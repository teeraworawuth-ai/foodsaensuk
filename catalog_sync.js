// =========================================================================
// catalog_sync.js — Shared ingredient catalog between this Cost/Spec app and
// the Smart-Stocks app (Firebase project restaurant-stock-81615, ครัวแสนสุข only).
//
// Data model (one Firestore document per ingredient, collection `catalog_saensuk`):
//   name, category (stock category), code (stock-only display), tag ('recipe'|'other')
//   stockUnit (กก./ลิตร/ตัว/ฟอง…), costUnit (g/ml/ตัว…), factor (costUnit per stockUnit)
//   priceMode ('market'|'custom'|'bill'), marketPrice, customPrice  (บาท / stockUnit)
//   billPrice, billDate, billVendor, billUpdatedAt                  (written by stock app)
//   nameUpdatedAt / priceUpdatedAt (+ *UpdatedBy)                   (conflict resolution)
//
// Rules of the road:
//   • Each write touches only its own fields of one ingredient (merge) → no app can
//     overwrite the other's data. The stock app's main document is only READ here.
//   • New bills never change dish costs silently: they appear as "รอยืนยัน" in 🧾 รายการซื้อ.
//   • Homemade items (sauces/bases) are not sent to stock.
// =========================================================================
(function () {
    const FB_CFG = {
        apiKey: 'AIzaSyCak5RHaVkjqN02MeWjvQ6HWA1EESEdeok',
        authDomain: 'restaurant-stock-81615.firebaseapp.com',
        projectId: 'restaurant-stock-81615'
    };
    const COL = 'catalog_saensuk';
    const STOCK_BRANCH = 'branch1';

    const HOMEMADE_IDS = new Set([
        'RM_SAUCE_SEAFOOD', 'RM_SAUCE_YUM', 'RM_CURRY_SOUP_BASE', 'RM_CHILI_PASTE_EGG_BASE', 'RM_CHA_OM_EGG'
    ]);
    // cost-app category -> stock category
    const CAT_MAP = {
        'อาหารทะเลสด': 'อาหารทะเล', 'เนื้อสัตว์': 'เนื้อสัตว์', 'ไข่และเต้าหู้': 'ไข่และเต้าหู้',
        'ข้าวและเส้น': 'ข้าวและเส้น', 'ของแห้ง': 'ของแห้ง', 'ผักและสมุนไพร': 'ผักสด', 'ซอสและน้ำแกง': 'เครื่องปรุง'
    };
    const CAT_BACK = {
        'อาหารทะเล': 'อาหารทะเลสด', 'ผักสด': 'ผักและสมุนไพร', 'เครื่องปรุง': 'ซอสและน้ำแกง'
    };
    // Must match the stock app
    const PREFIX = {
        'อาหารทะเล': 'S', 'เนื้อสัตว์': 'M', 'ไข่และเต้าหู้': 'E', 'ข้าวและเส้น': 'R', 'ของแห้ง': 'D',
        'ผักสด': 'V', 'เครื่องปรุง': 'C', 'เครื่องดื่ม': 'B', 'ขนม': 'K', 'อื่นๆ': 'O'
    };

    const S = {
        db: null, status: 'connecting', catalog: {}, catalogLoaded: false,
        stock: null, stockError: null, initialPushDone: false, billsShown: 30
    };

    const now = () => Date.now();
    const r2 = (n) => Math.round(Number(n) * 100) / 100;

    function isHomemade(rm) {
        return !!rm && (HOMEMADE_IDS.has(rm.id) || rm.homemade === true || !!rm.sub_recipe);
    }
    function unitInfo(rm) {
        const weighed = rm.unit === 'g' || rm.unit === 'ml';
        return {
            stockUnit: rm.unit === 'g' ? 'กก.' : rm.unit === 'ml' ? 'ลิตร' : rm.unit,
            factor: weighed ? 1000 : 1
        };
    }
    function stockCategory(rm) { return CAT_MAP[rm.category] || rm.category || 'อื่นๆ'; }
    function currentDisplayPrice(rm) {
        return (rm.use_custom && rm.custom_price_display !== undefined) ? Number(rm.custom_price_display) : Number(rm.display_price);
    }
    function nextCode(category, taken) {
        const p = PREFIX[category] || 'X';
        let max = 0;
        taken.forEach(code => {
            if (typeof code === 'string' && code.startsWith(p)) {
                const n = parseInt(code.slice(p.length), 10);
                if (!isNaN(n) && n > max) max = n;
            }
        });
        const code = p + String(max + 1).padStart(3, '0');
        taken.add(code);
        return code;
    }

    function priceFields(rm) {
        const custom = rm.use_custom && rm.custom_price_display !== undefined;
        return {
            marketPrice: r2(rm.display_price || 0),
            customPrice: custom ? r2(rm.custom_price_display) : null,
            priceMode: rm.price_source === 'bill' ? 'bill' : (custom ? 'custom' : 'market')
        };
    }

    function fullFields(rm, code) {
        const u = unitInfo(rm);
        const t = now();
        return Object.assign({
            name: rm.name, category: stockCategory(rm), code, tag: 'recipe',
            stockUnit: u.stockUnit, costUnit: rm.unit, factor: u.factor,
            createdBy: 'cost', createdAt: t,
            nameUpdatedAt: t, nameUpdatedBy: 'cost',
            priceUpdatedAt: t, priceUpdatedBy: 'cost'
        }, priceFields(rm));
    }

    function fsDoc(id) { return window.FirebaseAPI.doc(S.db, COL, id); }

    async function writeFields(id, fields) {
        if (!S.db) return false;
        try {
            await window.FirebaseAPI.setDoc(fsDoc(id), fields, { merge: true });
            return true;
        } catch (e) {
            console.error('Catalog write failed', id, e);
            showToast('⚠️ ส่งข้อมูลไประบบสต็อกไม่สำเร็จ (จะลองใหม่ครั้งถัดไป)', 'error');
            return false;
        }
    }

    // Push every non-homemade raw material that is not yet in the shared catalog
    async function pushMissing() {
        if (!S.db || !S.catalogLoaded || !appData) return 0;
        const taken = new Set(Object.values(S.catalog).map(c => c.code).filter(Boolean));
        const missing = Object.values(appData.raw_materials).filter(rm => !isHomemade(rm) && !S.catalog[rm.id]);
        if (missing.length === 0) return 0;
        const F = window.FirebaseAPI;
        let batch = F.writeBatch(S.db);
        let n = 0;
        for (const rm of missing) {
            const code = nextCode(stockCategory(rm), taken);
            const f = fullFields(rm, code);
            batch.set(fsDoc(rm.id), f, { merge: true });
            rm.name_synced_at = f.nameUpdatedAt;
            rm.price_synced_at = f.priceUpdatedAt;
            n++;
            if (n % 400 === 0) { await batch.commit(); batch = F.writeBatch(S.db); }
        }
        try {
            await batch.commit();
            saveData(true);
            showToast(`🔗 ส่งรายการวัตถุดิบ ${n} รายการไประบบสต็อกแล้ว`);
        } catch (e) {
            console.error('Catalog batch push failed', e);
            showToast('⚠️ ส่งรายการวัตถุดิบไประบบสต็อกไม่สำเร็จ', 'error');
        }
        return n;
    }

    // Called by app.js whenever a raw material's price (or name) changes in this app
    function pushRm(rmId, kind) {
        const rm = appData && appData.raw_materials[rmId];
        if (!rm || !S.db || isHomemade(rm)) return;
        if (!S.catalog[rmId]) { pushMissing(); return; }
        const t = now();
        if (kind === 'name') {
            rm.name_synced_at = t;
            writeFields(rmId, { name: rm.name, nameUpdatedAt: t, nameUpdatedBy: 'cost' });
        } else {
            rm.price_synced_at = t;
            writeFields(rmId, Object.assign(priceFields(rm), { priceUpdatedAt: t, priceUpdatedBy: 'cost' }));
        }
    }

    function createRmFromCatalog(id, c) {
        const weighed = c.stockUnit === 'กก.' || c.stockUnit === 'ลิตร';
        const unit = c.stockUnit === 'กก.' ? 'g' : c.stockUnit === 'ลิตร' ? 'ml' : (c.costUnit || c.stockUnit || 'ชิ้น');
        const factor = weighed ? 1000 : 1;
        const mp = Number(c.marketPrice) || 0;
        const price = c.priceMode === 'custom' || c.priceMode === 'bill' ? Number(c.customPrice ?? c.billPrice ?? mp) : mp;
        return {
            id, name: c.name, category: CAT_BACK[c.category] || c.category || 'อื่นๆ',
            unit, display_unit: c.stockUnit || unit, display_price: mp,
            market_price: Math.round((mp / factor) * 10000) / 10000,
            previous_price: mp, change_percent: 0,
            last_updated: new Date().toISOString().split('T')[0],
            use_custom: c.priceMode === 'custom' || c.priceMode === 'bill',
            custom_price_display: price,
            custom_price: Math.round((price / factor) * 10000) / 10000,
            price_source: c.priceMode === 'bill' ? 'bill' : undefined,
            from_stock: true,
            name_synced_at: c.nameUpdatedAt || 0,
            price_synced_at: c.priceUpdatedAt || 0
        };
    }

    function renameEverywhere(rmId, newName) {
        appData.raw_materials[rmId].name = newName;
        (appData.dishes || []).forEach(d => (d.items || []).forEach(it => { if (it.rm_id === rmId) it.rm_name = newName; }));
    }

    // Apply catalog changes made by the stock app (or other cost devices) to local data
    function applyCatalogToLocal() {
        if (!appData) return;
        let changed = false;
        const added = [];
        const renamed = [];
        Object.entries(S.catalog).forEach(([id, c]) => {
            const rm = appData.raw_materials[id];
            if (!rm) {
                if (c.tag === 'recipe' && c.name) {
                    appData.raw_materials[id] = createRmFromCatalog(id, c);
                    added.push(c.name);
                    changed = true;
                }
                return;
            }
            if ((c.nameUpdatedAt || 0) > (rm.name_synced_at || 0)) {
                if (c.name && c.name !== rm.name) { renamed.push(`${rm.name} → ${c.name}`); renameEverywhere(id, c.name); }
                rm.name_synced_at = c.nameUpdatedAt;
                changed = true;
            }
            if ((c.priceUpdatedAt || 0) > (rm.price_synced_at || 0)) {
                const u = unitInfo(rm);
                if (typeof c.marketPrice === 'number' && c.marketPrice !== Number(rm.display_price)) {
                    rm.display_price = c.marketPrice;
                    rm.market_price = Math.round((c.marketPrice / u.factor) * 10000) / 10000;
                }
                if (c.priceMode === 'market') {
                    rm.use_custom = false;
                    rm.price_source = 'market';
                } else if (c.customPrice != null) {
                    rm.use_custom = true;
                    rm.custom_price_display = c.customPrice;
                    rm.custom_price = Math.round((c.customPrice / u.factor) * 10000) / 10000;
                    rm.price_source = c.priceMode === 'bill' ? 'bill' : 'custom';
                }
                rm.price_synced_at = c.priceUpdatedAt;
                changed = true;
            }
        });
        if (changed) {
            recalculateAllDishes();
            saveData(true);
            renderAll();
            if (added.length) showToast(`🆕 รับวัตถุดิบใหม่จากระบบสต็อก ${added.length} รายการ: ${added.slice(0, 3).join(', ')}${added.length > 3 ? '…' : ''}`, 'info');
            if (renamed.length) showToast(`✏️ ชื่อวัตถุดิบถูกแก้จากระบบสต็อก: ${renamed.slice(0, 2).join(', ')}`, 'info');
        }
        updatePendingBadge();
    }

    // ---------------------------------------------------------------------
    // Pending bill prices (รอยืนยัน)
    // ---------------------------------------------------------------------
    function getPending() {
        if (!appData) return [];
        const out = [];
        Object.entries(S.catalog).forEach(([id, c]) => {
            const rm = appData.raw_materials[id];
            if (!rm || c.billPrice == null || isHomemade(rm)) return;
            if ((c.billUpdatedAt || 0) <= (rm.bill_ack_at || 0)) return;
            const current = currentDisplayPrice(rm);
            const bill = Number(c.billPrice);
            if (Math.abs(bill - current) < 0.005) return;
            const usedIn = (appData.dishes || []).filter(d => (d.items || []).some(it => it.rm_id === id && !it.disabled)).length;
            out.push({
                id, rm, c, current, bill, unit: rm.display_unit || c.stockUnit,
                pct: current > 0 ? Math.round(((bill - current) / current) * 1000) / 10 : null,
                usedIn
            });
        });
        return out.sort((a, b) => Math.abs(b.pct || 0) - Math.abs(a.pct || 0));
    }

    function applyBill(id) {
        const c = S.catalog[id];
        const rm = appData.raw_materials[id];
        if (!c || !rm || c.billPrice == null) return false;
        const u = unitInfo(rm);
        const bill = r2(c.billPrice);
        rm.use_custom = true;
        rm.custom_price_display = bill;
        rm.custom_price = Math.round((bill / u.factor) * 10000) / 10000;
        rm.price_source = 'bill';
        rm.bill_ack_at = c.billUpdatedAt || now();
        const t = now();
        rm.price_synced_at = t;
        writeFields(id, { priceMode: 'bill', customPrice: bill, priceUpdatedAt: t, priceUpdatedBy: 'cost' });
        broadcastMessage({ type: 'UPDATE_RM_PRICE', rmId: id, useCustom: true, customVal: bill, effectivePrice: rm.custom_price });
        return true;
    }

    function afterPriceChange(msg) {
        recalculateAllDishes();
        saveData(true);
        publishCloudDelta();
        renderAll();
        if (msg) showToast(msg);
    }

    function confirmBill(id) {
        if (applyBill(id)) afterPriceChange(`✅ ใช้ราคาบิลจริงของ "${appData.raw_materials[id].name}" แล้ว ต้นทุนทุกเมนูที่เกี่ยวข้องอัปเดตแล้ว`);
    }
    function confirmAllBills() {
        const list = getPending();
        if (list.length === 0) return;
        if (!confirm(`ใช้ราคาบิลจริงทั้งหมด ${list.length} รายการ?`)) return;
        list.forEach(p => applyBill(p.id));
        afterPriceChange(`✅ ใช้ราคาบิลจริง ${list.length} รายการแล้ว`);
    }
    function skipBill(id) {
        const c = S.catalog[id];
        const rm = appData.raw_materials[id];
        if (!c || !rm) return;
        rm.bill_ack_at = c.billUpdatedAt || now();
        saveData(true);
        renderAll();
        showToast(`ข้ามราคาบิลของ "${rm.name}" (ใช้ราคาเดิมต่อ)`, 'info');
    }

    function updatePendingBadge() {
        const n = getPending().length;
        document.querySelectorAll('.purchases-badge').forEach(el => {
            el.textContent = n > 0 ? String(n) : '';
            el.classList.toggle('hidden', n === 0);
        });
    }

    // ---------------------------------------------------------------------
    // 🧾 รายการซื้อ tab
    // ---------------------------------------------------------------------
    function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch])); }
    function modeLabel(rm) {
        if (rm.price_source === 'bill') return '<span class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800">บิลจริง</span>';
        if (rm.sub_recipe) return '<span class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-purple-100 text-purple-800">สูตรทำเอง</span>';
        if (rm.use_custom) return '<span class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-100 text-amber-800">ตั้งเอง</span>';
        return '<span class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-blue-100 text-blue-800">ตลาด</span>';
    }
    function statusPill() {
        const map = {
            connecting: ['bg-amber-100 text-amber-800', '⏳ กำลังเชื่อมต่อระบบสต็อก…'],
            online: ['bg-emerald-100 text-emerald-800', '🟢 เชื่อมต่อระบบสต็อกแล้ว'],
            error: ['bg-rose-100 text-rose-800', '🔴 เชื่อมต่อระบบสต็อกไม่ได้']
        };
        const [cls, txt] = map[S.status] || map.connecting;
        return `<span class="text-[11px] font-bold px-2 py-1 rounded-lg ${cls}">${txt}</span>`;
    }

    function renderPurchasesTab(container) {
        const pending = getPending();
        const linkedCount = Object.values(S.catalog).filter(c => c.tag === 'recipe').length;
        const receipts = (S.stock && Array.isArray(S.stock.receipts)) ? S.stock.receipts : [];

        let html = `
            <div class="bg-white rounded-2xl border border-slate-200 shadow-xs p-4 md:p-5 mb-4">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div>
                        <h2 class="text-lg md:text-xl font-bold text-slate-800">🧾 รายการซื้อ (ราคาจริงจากบิลในระบบสต็อก)</h2>
                        <p class="text-xs text-slate-500 mt-0.5">
                            บิลที่บันทึกใน "รับของ" ของระบบสต็อกจะแสดงที่นี่ — ราคาใหม่จะยังไม่ถูกใช้จนกว่าคุณกดยืนยัน
                        </p>
                    </div>
                    <div class="flex flex-wrap items-center gap-2">
                        ${statusPill()}
                        <span class="text-[11px] font-bold px-2 py-1 rounded-lg bg-slate-100 text-slate-700">🔗 วัตถุดิบเชื่อมกัน ${linkedCount} รายการ</span>
                    </div>
                </div>
                ${S.stockError ? `<div class="mt-2 text-xs text-rose-700 bg-rose-50 border border-rose-200 rounded-lg p-2">${esc(S.stockError)}</div>` : ''}
            </div>`;

        // Pending confirmations
        html += `
            <div class="bg-white rounded-2xl border ${pending.length ? 'border-amber-300' : 'border-slate-200'} shadow-xs p-4 mb-4">
                <div class="flex items-center justify-between gap-2 mb-2">
                    <h3 class="text-sm font-black text-slate-800">⏳ ราคาจากบิลใหม่ รอยืนยัน (${pending.length})</h3>
                    ${pending.length > 1 ? `<button onclick="CatalogSync.confirmAllBills()" class="px-3 py-1.5 text-xs font-bold rounded-xl bg-emerald-600 text-white">✅ ใช้ราคาบิลทั้งหมด</button>` : ''}
                </div>`;
        if (pending.length === 0) {
            html += `<div class="text-xs text-slate-400 p-3 text-center bg-slate-50 rounded-xl">ไม่มีราคาใหม่ที่ต้องยืนยัน</div>`;
        } else {
            html += '<div class="space-y-2">' + pending.map(p => `
                <div class="p-2.5 rounded-xl border border-slate-200 bg-slate-50/60 text-xs">
                    <div class="flex flex-wrap items-center gap-2">
                        <span class="font-black text-slate-900 text-sm">${esc(p.rm.name)}</span>
                        ${modeLabel(p.rm)}
                        <span class="text-slate-500">ใช้ใน ${p.usedIn} เมนู</span>
                    </div>
                    <div class="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1">
                        <span>ราคาที่ใช้อยู่: <strong>${r2(p.current)}.-</strong>/${esc(p.unit)}</span>
                        <span>→ บิลล่าสุด: <strong class="text-blue-800">${r2(p.bill)}.-</strong>/${esc(p.unit)}</span>
                        ${p.pct != null ? `<span class="font-black ${p.pct > 0 ? 'text-rose-600' : 'text-emerald-600'}">${p.pct > 0 ? '🔺 +' : '🔻 '}${p.pct}%</span>` : ''}
                        <span class="text-slate-500">(${esc(p.c.billDate || '')}${p.c.billVendor ? ' • ' + esc(p.c.billVendor) : ''})</span>
                    </div>
                    <div class="mt-2 flex gap-2">
                        <button onclick="CatalogSync.confirmBill('${p.id}')" class="px-3 py-1.5 rounded-lg bg-emerald-600 text-white font-bold">✅ ใช้ราคาบิล</button>
                        <button onclick="CatalogSync.skipBill('${p.id}')" class="px-3 py-1.5 rounded-lg bg-white border border-slate-300 text-slate-700 font-bold">ข้าม (ใช้ราคาเดิม)</button>
                    </div>
                </div>`).join('') + '</div>';
        }
        html += '</div>';

        // Bills list
        const sorted = [...receipts].sort((a, b) => (b.id || 0) - (a.id || 0));
        const shown = sorted.slice(0, S.billsShown);
        html += `
            <div class="bg-white rounded-2xl border border-slate-200 shadow-xs p-4">
                <h3 class="text-sm font-black text-slate-800 mb-2">📜 บิลซื้อล่าสุดจากระบบสต็อก (${receipts.length} บิล)</h3>`;
        if (!S.stock) {
            html += `<div class="text-xs text-slate-400 p-3 text-center bg-slate-50 rounded-xl">${S.status === 'error' ? 'ยังอ่านข้อมูลสต็อกไม่ได้' : 'กำลังโหลดบิล…'}</div>`;
        } else if (receipts.length === 0) {
            html += `<div class="text-xs text-slate-400 p-3 text-center bg-slate-50 rounded-xl">ยังไม่มีบิลซื้อในระบบสต็อก — เมื่อบันทึก "รับของ" ในระบบสต็อก บิลจะมาแสดงที่นี่</div>`;
        } else {
            html += '<div class="space-y-2">' + shown.map(b => `
                <details class="rounded-xl border border-slate-200 bg-slate-50/50">
                    <summary class="cursor-pointer p-2.5 text-xs flex flex-wrap items-center gap-2">
                        <span class="font-black text-slate-800">${esc(b.date)}</span>
                        <span class="text-slate-600">${esc(b.vendor || '-')}</span>
                        <span class="text-slate-400">${esc(b.method || '')}</span>
                        <span class="ml-auto font-black text-slate-900">${Number(b.total || 0).toLocaleString('th-TH')}.-</span>
                        <span class="text-slate-500">${(b.items || []).length} รายการ</span>
                    </summary>
                    <div class="px-2.5 pb-2.5 space-y-1">
                        ${(b.items || []).map(li => {
                            const it = li.item || {};
                            const conv = Number(it.conversionRate) || 1;
                            const perBase = r2(Number(li.price || 0) / conv);
                            const linked = it.catalogId && appData.raw_materials[it.catalogId];
                            return `
                            <div class="flex flex-wrap items-center gap-2 text-[11px] p-1.5 rounded bg-white border border-slate-100">
                                <span class="font-bold text-slate-800">${esc(it.name || '?')}</span>
                                ${linked ? '<span class="text-[10px] px-1 rounded bg-blue-50 text-blue-700 border border-blue-200">🔗 ใช้ในสูตร</span>' : '<span class="text-[10px] px-1 rounded bg-slate-100 text-slate-500">ไม่อยู่ในสูตร</span>'}
                                <span class="text-slate-600">${Number(li.qty || 0)} ${esc(it.purchaseUnit || it.unit || '')} × ${Number(li.price || 0)}.-</span>
                                ${conv !== 1 ? `<span class="text-slate-500">(= ${perBase}.-/${esc(it.unit || '')})</span>` : ''}
                                ${li.priceNote ? `<span class="font-bold ${String(li.priceNote).includes('แพง') ? 'text-rose-600' : 'text-emerald-600'}">${esc(li.priceNote)}</span>` : ''}
                                <span class="ml-auto font-black">${Number(li.total || 0).toLocaleString('th-TH')}.-</span>
                            </div>`;
                        }).join('')}
                    </div>
                </details>`).join('') + '</div>';
            if (sorted.length > shown.length) {
                html += `<button onclick="CatalogSync.showMoreBills()" class="mt-2 w-full py-2 text-xs font-bold rounded-xl bg-slate-100 text-slate-700">ดูบิลเพิ่ม</button>`;
            }
        }
        html += '</div>';
        container.innerHTML = html;
    }

    function rerenderIfPurchases() {
        updatePendingBadge();
        if (typeof currentTab !== 'undefined' && currentTab === 'purchases') renderCurrentTab();
    }

    function decompress(b64) {
        const bin = atob(b64);
        const bytes = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
        return JSON.parse(new TextDecoder().decode(window.pako.inflate(bytes)));
    }

    // ---------------------------------------------------------------------
    // Boot
    // ---------------------------------------------------------------------
    async function boot() {
        while (!window.FirebaseAPI || typeof appData === 'undefined' || !appData) {
            await new Promise(r => setTimeout(r, 150));
        }
        const F = window.FirebaseAPI;
        try {
            const app = F.initializeApp(FB_CFG, 'saensuk-cost');
            const auth = F.getAuth(app);
            S.db = F.initializeFirestore(app, { localCache: F.memoryLocalCache(), experimentalForceLongPolling: true });
            await new Promise((resolve, reject) => {
                const unsub = F.onAuthStateChanged(auth, async (u) => {
                    unsub();
                    if (u) return resolve(u);
                    try { resolve((await F.signInAnonymously(auth)).user); } catch (e) { reject(e); }
                });
            });

            F.onSnapshot(F.collection(S.db, COL), (snap) => {
                const map = {};
                snap.forEach(d => { map[d.id] = d.data(); });
                S.catalog = map;
                S.catalogLoaded = true;
                S.status = 'online';
                applyCatalogToLocal();
                if (!S.initialPushDone) {
                    S.initialPushDone = true;
                    pushMissing();
                }
                rerenderIfPurchases();
            }, (err) => {
                console.error('Catalog snapshot error', err);
                S.status = 'error';
                S.stockError = 'อ่านรายการวัตถุดิบกลางไม่ได้: ' + (err && err.message ? err.message : err);
                rerenderIfPurchases();
            });

            F.onSnapshot(F.doc(S.db, 'restaurant_data', STOCK_BRANCH), (snap) => {
                try {
                    if (!snap.exists()) { S.stock = { receipts: [], inventory: [] }; }
                    else {
                        const raw = snap.data();
                        S.stock = raw.compressedPayload ? decompress(raw.compressedPayload) : raw;
                    }
                    S.stockError = null;
                } catch (e) {
                    S.stockError = 'อ่านบิลจากระบบสต็อกไม่ได้: ' + e.message;
                }
                rerenderIfPurchases();
            }, (err) => {
                S.stockError = 'อ่านบิลจากระบบสต็อกไม่ได้: ' + (err && err.message ? err.message : err);
                rerenderIfPurchases();
            });
        } catch (e) {
            console.error('Catalog sync init failed', e);
            S.status = 'error';
            S.stockError = 'เชื่อมต่อระบบสต็อกไม่ได้: ' + (e && e.message ? e.message : e);
            rerenderIfPurchases();
        }
    }

    window.CatalogSync = {
        state: S, isHomemade, pushRm, pushMissing, getPending,
        confirmBill, confirmAllBills, skipBill, updatePendingBadge,
        showMoreBills() { S.billsShown += 30; rerenderIfPurchases(); },
        PREFIX, CAT_MAP
    };
    window.renderPurchasesTab = renderPurchasesTab;

    boot();
})();
