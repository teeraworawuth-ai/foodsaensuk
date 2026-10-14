// =========================================================================
// ครัวแสนสุข - Food Cost Analysis & Kitchen Prep Board System
// With Real-Time Multi-Device Live Sync via WebSockets (MQTT over WSS)
// =========================================================================

let appData = null;
let currentTab = 'prep-board';
let currentCategory = 'all';
let searchQuery = '';
let viewMode = 'wall-sheet'; // 'wall-sheet' | 'cards' | 'table'
let selectedDishIds = new Set();
let deliveryMarkupPct = 30; // default +30% for Grab / Lineman
let showDeliveryPrices = false; // toggle delivery price view
let currentEditingDish = null; // active in-memory dish being edited
let currentEditingRawMaterials = {}; // map of { rmId: newDisplayPrice } for global sync

// Helper to count how many dishes use a specific raw material
function getRawMaterialUsageCount(rmId) {
    if (!appData || !appData.dishes) return 0;
    return appData.dishes.filter(d => d.items && d.items.some(i => i.rm_id === rmId)).length;
}

// Delivery Pricing Handlers
window.toggleDeliveryMode = function(enabled) {
    showDeliveryPrices = enabled;
    localStorage.setItem('saensuk_show_delivery_prices', enabled);
    const delToggle = document.getElementById('delivery-mode-toggle');
    if (delToggle) delToggle.checked = enabled;
    renderAll();
};

window.updateDeliveryMarkup = function(val) {
    const num = parseFloat(val);
    if (!isNaN(num) && num >= 0) {
        deliveryMarkupPct = num;
        localStorage.setItem('saensuk_delivery_markup_pct', num);
        const delMarkup = document.getElementById('delivery-markup-input');
        if (delMarkup) delMarkup.value = num;
        recalculateAllDishes();
        renderAll();
        showToast(`ปรับอัตราเปอร์เซ็นต์บวกเพิ่ม Grab/Lineman เป็น +${num}% แล้ว`);
    }
};

// Station classification helper
function getDishStation(dish) {
    const cat = dish.category || '';
    if (cat === 'cat_stir_fry' || cat === 'cat_fried_rice' || cat === 'cat_alacarte') {
        return { id: 'wok', name: 'เตาผัด', icon: '🔥', color: 'text-amber-800 bg-amber-50 border-amber-300' };
    }
    if (cat === 'cat_soup') {
        return { id: 'soup', name: 'เตาต้ม/แกง', icon: '🍲', color: 'text-sky-800 bg-sky-50 border-sky-300' };
    }
    if (cat === 'cat_bbq' || cat === 'cat_fried' || cat === 'cat_seabass') {
        return { id: 'grill', name: 'เตาย่าง/ทอด', icon: '🦐', color: 'text-rose-800 bg-rose-50 border-rose-300' };
    }
    if (cat === 'cat_fresh_yum' || cat === 'cat_thai_yum') {
        return { id: 'salad', name: 'สเตชันยำ', icon: '🥗', color: 'text-emerald-800 bg-emerald-50 border-emerald-300' };
    }
    if (cat === 'cat_omelet') {
        return { id: 'omelet', name: 'เตาไข่', icon: '🍳', color: 'text-yellow-800 bg-yellow-50 border-yellow-300' };
    }
    return { id: 'general', name: 'ครัวหลัก', icon: '🍽️', color: 'text-slate-800 bg-slate-100 border-slate-300' };
}

// Protein color indicator helper for visual glance
function getProteinColorInfo(itemName) {
    const n = (itemName || '').toLowerCase();
    if (n.includes('กุ้ง') || n.includes('ปู')) {
        return { border: 'border-l-rose-500', badge: 'bg-rose-50 text-rose-800 border-rose-200', dot: '🔴' };
    }
    if (n.includes('ปลา') || n.includes('หมึก') || n.includes('หอย') || n.includes('กะพง') || n.includes('คัง') || n.includes('ทะเล')) {
        return { border: 'border-l-blue-500', badge: 'bg-blue-50 text-blue-800 border-blue-200', dot: '🔵' };
    }
    if (n.includes('หมู') || n.includes('ไก่') || n.includes('เนื้อ')) {
        return { border: 'border-l-emerald-600', badge: 'bg-emerald-50 text-emerald-800 border-emerald-200', dot: '🟢' };
    }
    if (n.includes('ไข่') || n.includes('เต้าหู้')) {
        return { border: 'border-l-amber-500', badge: 'bg-amber-50 text-amber-800 border-amber-200', dot: '🟡' };
    }
    return { border: 'border-l-slate-400', badge: 'bg-slate-50 text-slate-700 border-slate-200', dot: '⚪' };
}

// Real-Time Multi-Device Sync Configuration
let mqttClient = null;
let syncRoomCode = 'saensuk-main';
const deviceId = 'chef-' + Math.random().toString(36).substring(2, 9);
let isRemoteUpdate = false;
let connectedPeersCount = 1;

// Initialize Application
document.addEventListener('DOMContentLoaded', async () => {
    // Check URL query parameters for custom room
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('room')) {
        syncRoomCode = urlParams.get('room');
    }

    await loadData();
    setupEventListeners();
    initRealtimeSync();
    renderAll();
});

// Load data from LocalStorage or data.json
async function loadData() {
    const savedMarkup = localStorage.getItem('saensuk_delivery_markup_pct');
    if (savedMarkup) deliveryMarkupPct = parseFloat(savedMarkup) || 30;
    const savedShowDel = localStorage.getItem('saensuk_show_delivery_prices');
    if (savedShowDel !== null) showDeliveryPrices = (savedShowDel === 'true');

    const saved = localStorage.getItem(`saensuk_food_cost_data_${syncRoomCode}`);
    if (saved) {
        try {
            appData = JSON.parse(saved);
            console.log('Loaded data from localStorage for room:', syncRoomCode);
            recalculateAllDishes();
            return;
        } catch (e) {
            console.error('Error parsing saved data:', e);
        }
    }

    try {
        const response = await fetch('./data.json');
        if (response.ok) {
            appData = await response.json();
            console.log('Loaded data from data.json');
            recalculateAllDishes();
            return;
        }
    } catch (e) {
        console.warn('Fetch data.json failed (possibly file:// protocol), using window.DEFAULT_DATA', e);
    }

    // Fallback if data.json fetch fails
    if (window.DEFAULT_DATA) {
        appData = JSON.parse(JSON.stringify(window.DEFAULT_DATA));
        recalculateAllDishes();
    }
}

// Save data to LocalStorage
function saveData(silent = false) {
    if (!appData) return;
    localStorage.setItem(`saensuk_food_cost_data_${syncRoomCode}`, JSON.stringify(appData));
    if (!silent) {
        showToast('💾 บันทึกข้อมูลในเครื่องเรียบร้อยแล้ว');
    }
}

// -------------------------------------------------------------------------
// REAL-TIME MULTI-DEVICE WEBSOCKET SYNC ENGINE (MQTT over WSS)
// -------------------------------------------------------------------------
function initRealtimeSync() {
    updateSyncStatus('connecting');

    // Use HiveMQ or EMQX public secure WebSockets broker
    const brokers = [
        'wss://broker.hivemq.com:8884/mqtt',
        'wss://broker.emqx.io:8084/mqtt'
    ];

    try {
        if (typeof mqtt === 'undefined') {
            console.warn('MQTT library not loaded, real-time sync disabled');
            updateSyncStatus('offline');
            return;
        }

        const brokerUrl = brokers[0];
        mqttClient = mqtt.connect(brokerUrl, {
            clientId: deviceId,
            clean: true,
            connectTimeout: 7000,
            reconnectPeriod: 3000
        });

        const topic = `saensuk/kitchen/v2/${syncRoomCode}`;
        const deltaTopic = `saensuk/kitchen/v2/${syncRoomCode}/retained_delta`;

        mqttClient.on('connect', () => {
            console.log('Connected to Cloud Realtime Live Sync:', brokerUrl);
            updateSyncStatus('online');

            // Subscribe to live broadcast events
            mqttClient.subscribe(topic, (err) => {
                if (!err) {
                    broadcastMessage({
                        type: 'PEER_PING',
                        senderId: deviceId,
                        timestamp: Date.now()
                    });
                }
            });

            // Subscribe to 24/7 cloud retained state (saved in cloud even when all PCs/phones were off)
            mqttClient.subscribe(deltaTopic, (err) => {
                if (!err) {
                    console.log('Subscribed to Cloud 24/7 Retained State');
                }
            });
        });

        mqttClient.on('message', (receivedTopic, message) => {
            try {
                const payload = JSON.parse(message.toString());
                if (receivedTopic.endsWith('/retained_delta')) {
                    applyCloudDelta(payload);
                    return;
                }
                handleIncomingSyncMessage(payload);
            } catch (err) {
                console.error('Error handling sync message:', err);
            }
        });

        mqttClient.on('error', (err) => {
            console.warn('MQTT Connection Error:', err);
            updateSyncStatus('offline');
        });

        mqttClient.on('close', () => {
            updateSyncStatus('connecting');
        });

    } catch (e) {
        console.error('Failed to initialize real-time sync:', e);
        updateSyncStatus('offline');
    }
}

// Broadcast an event to other phones / devices
function broadcastMessage(payload) {
    if (!mqttClient || !mqttClient.connected) return;
    payload.room = syncRoomCode;
    payload.senderId = deviceId;
    payload.timestamp = Date.now();
    const topic = `saensuk/kitchen/v2/${syncRoomCode}`;
    mqttClient.publish(topic, JSON.stringify(payload), { qos: 0 });
}

// Compile customized data into a compact cloud delta
function getCloudDelta() {
    if (!appData) return null;
    const customPrices = {};
    Object.values(appData.raw_materials || {}).forEach(rm => {
        if (rm.use_custom && rm.custom_price !== undefined) {
            customPrices[rm.id] = {
                use_custom: true,
                custom_price: rm.custom_price,
                custom_price_display: rm.custom_price_display
            };
        }
    });

    const modifiedDishes = {};
    (appData.dishes || []).forEach(dish => {
        if (dish.is_customized) {
            modifiedDishes[dish.id] = {
                items: dish.items,
                price: dish.price
            };
        }
    });

    return {
        type: 'RETAINED_DELTA_STATE',
        room: syncRoomCode,
        senderId: deviceId,
        updatedAt: Date.now(),
        last_sync: appData.restaurant_info.last_market_sync,
        customPrices,
        modifiedDishes
    };
}

// Publish retained delta to cloud broker (retained in cloud 24/7)
function publishCloudDelta() {
    if (!mqttClient || !mqttClient.connected) return;
    const delta = getCloudDelta();
    if (!delta) return;
    const deltaTopic = `saensuk/kitchen/v2/${syncRoomCode}/retained_delta`;
    mqttClient.publish(deltaTopic, JSON.stringify(delta), { qos: 1, retain: true });
    console.log('Saved state to 24/7 Cloud Broker');
}

// Apply retained delta from cloud broker
function applyCloudDelta(delta) {
    if (!delta || !appData || delta.senderId === deviceId) return;
    let changed = false;

    if (delta.customPrices) {
        Object.entries(delta.customPrices).forEach(([rmId, cData]) => {
            const rm = appData.raw_materials[rmId];
            if (rm) {
                rm.use_custom = true;
                rm.custom_price = cData.custom_price;
                rm.custom_price_display = cData.custom_price_display;
                changed = true;
            }
        });
    }

    if (delta.modifiedDishes) {
        Object.entries(delta.modifiedDishes).forEach(([dishId, dData]) => {
            const dish = appData.dishes.find(d => d.id === dishId);
            if (dish) {
                if (dData.items) dish.items = dData.items;
                if (dData.price) dish.price = dData.price;
                dish.is_customized = true;
                changed = true;
            }
        });
    }

    if (delta.last_sync && delta.last_sync > (appData.restaurant_info.last_market_sync || '')) {
        appData.restaurant_info.last_market_sync = delta.last_sync;
        changed = true;
    }

    if (changed) {
        recalculateAllDishes();
        saveData(true);
        renderAll();
        showToast('☁️ ซิงค์ข้อมูลล่าสุดจาก Cloud Server สำเร็จแล้ว (24 ชม.)', 'info');
    }
}

// Update Sync Status Badge on UI
function updateSyncStatus(status) {
    const el = document.getElementById('live-sync-indicator');
    const textEl = document.getElementById('live-sync-text');
    if (!el || !textEl) return;

    if (status === 'online') {
        el.className = 'w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse';
        textEl.textContent = '🟢 คลาวด์ออนไลน์ 24 ชม. (Live Sync)';
        textEl.className = 'text-[11px] font-bold text-emerald-700';
    } else if (status === 'connecting') {
        el.className = 'w-2.5 h-2.5 rounded-full bg-amber-500 animate-ping';
        textEl.textContent = '🟡 กำลังเชื่อมต่อคลาวด์ 24 ชม...';
        textEl.className = 'text-[11px] font-medium text-amber-700';
    } else {
        el.className = 'w-2.5 h-2.5 rounded-full bg-slate-400';
        textEl.textContent = '⚪ ออฟไลน์ (แคชในเครื่องพร้อมใช้)';
        textEl.className = 'text-[11px] font-medium text-slate-500';
    }
}

// Handle messages from other devices
function handleIncomingSyncMessage(data) {
    if (!data || data.senderId === deviceId) return; // Ignore own messages

    console.log('Incoming real-time message:', data.type);

    if (data.type === 'PEER_PING') {
        // A new device joined! Send them our current active data state so they sync immediately
        broadcastMessage({
            type: 'STATE_RESPONSE',
            targetId: data.senderId,
            fullState: appData
        });
        showToast('📱 มีทีมงานเชื่อมต่อเข้ามาใหม่ในห้อง', 'info');
        return;
    }

    if (data.type === 'STATE_RESPONSE' && data.targetId === deviceId) {
        // Received latest state from a peer
        if (data.fullState && data.fullState.dishes) {
            appData = data.fullState;
            saveData(true);
            renderAll();
            showToast('🔄 ซิงค์ข้อมูลล่าสุดจากเครื่องทีมงานเรียบร้อยแล้ว', 'info');
        }
        return;
    }

    if (data.type === 'UPDATE_RM_PRICE') {
        const { rmId, customVal, useCustom, effectivePrice } = data;
        const rm = appData.raw_materials[rmId];
        if (rm) {
            rm.use_custom = useCustom;
            rm.custom_price_display = customVal;
            rm.custom_price = effectivePrice;
            recalculateAllDishes();
            saveData(true);
            renderAll();
            showToast(`⚡ ${rm.name} ถูกปรับราคาจากเครื่องทีมงาน (${customVal}.-)`, 'info');
        }
        return;
    }

    if (data.type === 'UPDATE_DISH_SPEC') {
        const { dishId, updatedDish } = data;
        const idx = appData.dishes.findIndex(d => d.id === dishId);
        if (idx !== -1) {
            appData.dishes[idx] = updatedDish;
            recalculateAllDishes();
            saveData(true);
            renderAll();
            showToast(`⚡ เมนู "${updatedDish.name}" ถูกปรับสเปกจากเครื่องทีมงาน`, 'info');
        }
        return;
    }

    if (data.type === 'SYNC_7DAY_MARKET') {
        appData.raw_materials = data.raw_materials;
        appData.restaurant_info.last_market_sync = data.last_sync;
        recalculateAllDishes();
        saveData(true);
        renderAll();
        showToast('⚡ อัปเดตราคาตลาดรอบ 7 วันจากเครื่องทีมงาน', 'info');
        return;
    }

    if (data.type === 'RESET_ALL_DATA') {
        appData = data.fullState;
        recalculateAllDishes();
        saveData(true);
        renderAll();
        showToast('⚠️ ข้อมูลถูกรีเซ็ตกลับสู่ค่าเริ่มต้นโดยเครื่องทีมงาน', 'warning');
        return;
    }
}

// Reset to Default Data
async function resetDefaults() {
    if (!confirm('คุณต้องการรีเซ็ตข้อมูลและราคาทั้งหมดกลับเป็นค่าเริ่มต้นใช่หรือไม่? (จะส่งผลต่อทุกเครื่องในห้อง)')) return;
    localStorage.removeItem(`saensuk_food_cost_data_${syncRoomCode}`);
    try {
        const response = await fetch('./data.json');
        appData = await response.json();
    } catch(e) {
        if (window.DEFAULT_DATA) appData = JSON.parse(JSON.stringify(window.DEFAULT_DATA));
    }
    recalculateAllDishes();
    saveData();
    renderAll();

    // Broadcast reset to peers
    broadcastMessage({
        type: 'RESET_ALL_DATA',
        fullState: appData
    });

    showToast('รีเซ็ตข้อมูลกลับสู่ค่ามาตรฐานแล้ว');
}

// Event Listeners Setup
function setupEventListeners() {
    // Navigation Tabs (Desktop & Mobile)
    document.querySelectorAll('.nav-tab').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.nav-tab').forEach(b => {
                b.classList.remove('active', 'border-blue-600', 'text-blue-600', 'bg-blue-50', 'text-blue-700');
                b.classList.add('text-slate-600', 'border-transparent');
            });
            btn.classList.add('active', 'border-blue-600', 'text-blue-600', 'bg-blue-50');
            currentTab = btn.dataset.tab;

            // Also highlight mobile bottom nav
            document.querySelectorAll('.mobile-nav-btn').forEach(mb => {
                mb.classList.toggle('text-blue-600', mb.dataset.tab === currentTab);
                mb.classList.toggle('text-slate-400', mb.dataset.tab !== currentTab);
            });

            renderAll();
        });
    });

    // Mobile Navigation Bottom Buttons
    document.querySelectorAll('.mobile-nav-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            currentTab = btn.dataset.tab;
            document.querySelectorAll('.mobile-nav-btn').forEach(b => {
                b.classList.remove('text-blue-600', 'font-bold');
                b.classList.add('text-slate-400');
            });
            btn.classList.add('text-blue-600', 'font-bold');
            btn.classList.remove('text-slate-400');

            document.querySelectorAll('.nav-tab').forEach(tb => {
                tb.classList.toggle('active', tb.dataset.tab === currentTab);
                tb.classList.toggle('border-blue-600', tb.dataset.tab === currentTab);
                tb.classList.toggle('text-blue-600', tb.dataset.tab === currentTab);
                tb.classList.toggle('bg-blue-50', tb.dataset.tab === currentTab);
            });

            renderAll();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    });

    // Search Input
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchQuery = e.target.value.trim().toLowerCase();
            renderCurrentTab();
        });
    }

    // 7-Day Market Sync Simulator Button
    const syncBtn = document.getElementById('sync-market-btn');
    if (syncBtn) {
        syncBtn.addEventListener('click', simulate7DayMarketSync);
    }

    // Save Button
    const saveBtn = document.getElementById('save-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', () => saveData(false));
    }

    // Reset Button
    const resetBtn = document.getElementById('reset-btn');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetDefaults);
    }

    // Print Button
    const printBtn = document.getElementById('print-btn');
    if (printBtn) {
        printBtn.addEventListener('click', () => {
            if (selectedDishIds && selectedDishIds.size > 0) {
                printSelectedBatch();
            } else {
                printAllDishes();
            }
        });
    }

    // Export JSON Button
    const exportBtn = document.getElementById('export-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportJSON);
    }

    // Share / QR Code Modal Button
    const shareBtn = document.getElementById('share-btn');
    if (shareBtn) {
        shareBtn.addEventListener('click', openShareModal);
    }

    // Delivery Controls Initial State
    const delToggle = document.getElementById('delivery-mode-toggle');
    if (delToggle) delToggle.checked = showDeliveryPrices;
    const delMarkup = document.getElementById('delivery-markup-input');
    if (delMarkup) delMarkup.value = deliveryMarkupPct;
}

// Recalculate costs for all dishes based on current raw material effective prices
function recalculateAllDishes() {
    if (!appData || !appData.dishes) return;
    
    appData.dishes.forEach(dish => {
        let psCost = 0;
        dish.items.forEach(item => {
            // If item is toggled off (disabled), exclude from cost calculation
            if (item.disabled) {
                item.item_cost = 0;
                item.cost_pct_of_sales = 0;
                return;
            }
            const rm = appData.raw_materials[item.rm_id];
            if (rm) {
                const effectivePrice = (rm.use_custom && rm.custom_price !== undefined) 
                    ? rm.custom_price 
                    : rm.market_price;
                
                const itemCost = Math.round(effectivePrice * item.portion * 100) / 100;
                item.unit_cost = effectivePrice;
                item.item_cost = itemCost;
                item.cost_pct_of_sales = Math.round((itemCost / (dish.price || 1)) * 1000) / 10;
                psCost += itemCost;
            }
        });

        dish.primary_secondary_cost = Math.round(psCost * 100) / 100;
        dish.minor_seasoning_cost = Math.round(dish.price * 0.025 * 100) / 100; // 2.5% minor allowance
        dish.total_cost = Math.round((dish.primary_secondary_cost + dish.minor_seasoning_cost) * 100) / 100;
        
        dish.ps_cost_pct = Math.round((dish.primary_secondary_cost / dish.price) * 1000) / 10;
        dish.total_cost_pct = Math.round((dish.total_cost / dish.price) * 1000) / 10;
        dish.gross_profit = Math.round((dish.price - dish.total_cost) * 100) / 100;
        dish.gross_margin_pct = Math.round((dish.gross_profit / dish.price) * 1000) / 10;
        dish.is_target_compliant = (dish.total_cost_pct <= 40.0 && dish.gross_margin_pct >= 60.0);

        // Delivery (Grab / Lineman) Pricing & Economics
        const markup = dish.delivery_markup_pct || deliveryMarkupPct || 30;
        dish.delivery_price = Math.round(dish.price * (1 + markup / 100));
        // Delivery Platform Fee is typically 30% GP
        const deliveryPlatformGP = 0.30;
        dish.delivery_net_revenue = Math.round(dish.delivery_price * (1 - deliveryPlatformGP) * 100) / 100;
        dish.delivery_gross_profit = Math.round((dish.delivery_net_revenue - dish.total_cost) * 100) / 100;
        dish.delivery_gross_margin_pct = Math.round((dish.delivery_gross_profit / (dish.delivery_net_revenue || 1)) * 1000) / 10;
    });
}

// 7-Day Market Sync Simulator (Simulates weekly price changes & broadcasts to all devices)
function simulate7DayMarketSync() {
    if (!appData || !appData.raw_materials) return;

    const rms = Object.values(appData.raw_materials);
    let changedCount = 0;

    const shuffled = [...rms].sort(() => 0.5 - Math.random());
    const toChange = shuffled.slice(0, 8);
    const today = new Date().toISOString().split('T')[0];

    toChange.forEach(rm => {
        const pctChange = (Math.floor(Math.random() * 25) - 12);
        if (pctChange !== 0) {
            rm.previous_price = rm.display_price;
            const newDisplay = Math.round(rm.display_price * (1 + pctChange / 100));
            rm.display_price = Math.max(1, newDisplay);
            rm.change_percent = pctChange;
            rm.last_updated = today;

            if (rm.unit === 'g') {
                rm.market_price = Math.round((rm.display_price / 1000) * 10000) / 10000;
                rm.market_price_per_kg = rm.display_price;
            } else if (rm.unit === 'ml') {
                rm.market_price = Math.round((rm.display_price / 1000) * 10000) / 10000;
            } else {
                rm.market_price = rm.display_price;
            }
            changedCount++;
        }
    });

    appData.restaurant_info.last_market_sync = today;
    recalculateAllDishes();
    saveData(true);
    renderAll();

    // Broadcast to all team devices
    broadcastMessage({
        type: 'SYNC_7DAY_MARKET',
        raw_materials: appData.raw_materials,
        last_sync: today
    });

    showToast(`🔄 อัปเดตราคาตลาด 7 วันแล้ว! ปรับราคา ${changedCount} รายการ และกระจายสู่เครื่องทีมงานแบบเรียลไทม์`, 'info');
}

// Toast notification
function showToast(msg, type = 'success') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = msg;
    toast.className = `fixed bottom-20 md:bottom-5 right-4 md:right-5 z-50 px-4 py-3 rounded-xl shadow-2xl text-white text-xs md:text-sm font-semibold transition-all duration-300 ${
        type === 'info' ? 'bg-indigo-600' : type === 'warning' ? 'bg-rose-600' : 'bg-emerald-600'
    }`;
    toast.classList.remove('opacity-0', 'pointer-events-none');
    setTimeout(() => {
        toast.classList.add('opacity-0', 'pointer-events-none');
    }, 3800);
}

// Render Summary KPIs
function renderKPIs() {
    if (!appData || !appData.dishes) return;

    const dishes = appData.dishes;
    const totalDishes = dishes.length;
    const compliantCount = dishes.filter(d => d.is_target_compliant).length;
    const avgCostPct = (dishes.reduce((acc, d) => acc + d.total_cost_pct, 0) / totalDishes).toFixed(1);
    const avgMarginPct = (dishes.reduce((acc, d) => acc + d.gross_margin_pct, 0) / totalDishes).toFixed(1);

    const totalEl = document.getElementById('kpi-total-dishes');
    if (totalEl) totalEl.textContent = totalDishes;
    const compEl = document.getElementById('kpi-compliant-pct');
    if (compEl) compEl.textContent = `${((compliantCount / totalDishes) * 100).toFixed(0)}% (${compliantCount}/${totalDishes})`;
    const costEl = document.getElementById('kpi-avg-cost');
    if (costEl) costEl.textContent = `${avgCostPct}%`;
    const marginEl = document.getElementById('kpi-avg-margin');
    if (marginEl) marginEl.textContent = `${avgMarginPct}%`;
    const syncDateEl = document.getElementById('last-sync-date');
    if (syncDateEl) syncDateEl.textContent = appData.restaurant_info.last_market_sync || 'ล่าสุด';
}

// Render Category Filter Pills
function renderCategoryPills() {
    const container = document.getElementById('category-pills');
    if (!container || !appData) return;

    let html = `
        <button onclick="setCategory('all')" class="cat-pill px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all ${
            currentCategory === 'all' 
                ? 'bg-blue-600 text-white shadow-sm' 
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-100'
        }">
            🍽️ ทั้งหมด (${appData.dishes.length})
        </button>
    `;

    appData.categories.forEach(cat => {
        const count = appData.dishes.filter(d => d.category === cat.id).length;
        const isActive = currentCategory === cat.id;
        html += `
            <button onclick="setCategory('${cat.id}')" class="cat-pill px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all ${
                isActive 
                    ? 'bg-blue-600 text-white shadow-sm' 
                    : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-100'
            }">
                ${cat.name.split('(')[0]} (${count})
            </button>
        `;
    });

    container.innerHTML = html;
}

window.setCategory = function(catId) {
    currentCategory = catId;
    renderCategoryPills();
    renderCurrentTab();
};

window.setViewMode = function(mode) {
    viewMode = mode;
    renderCurrentTab();
};

// Filter Dishes based on search and category
function getFilteredDishes() {
    if (!appData || !appData.dishes) return [];
    return appData.dishes.filter(dish => {
        const matchCat = currentCategory === 'all' || dish.category === currentCategory;
        const matchSearch = !searchQuery || 
            dish.name.toLowerCase().includes(searchQuery) ||
            dish.items.some(i => i.rm_name && i.rm_name.toLowerCase().includes(searchQuery));
        return matchCat && matchSearch;
    });
}

// Render Content according to current tab
function renderCurrentTab() {
    const content = document.getElementById('main-content');
    if (!content) return;

    if (currentTab === 'prep-board') {
        renderKitchenPrepBoard(content);
    } else if (currentTab === 'cost-analysis') {
        renderCostAnalysis(content);
    } else if (currentTab === 'market-prices') {
        renderMarketPriceManager(content);
    } else if (currentTab === 'ref-gallery') {
        renderReferenceGallery(content);
    }
}

function renderAll() {
    renderKPIs();
    renderCategoryPills();
    renderCurrentTab();
}

// -------------------------------------------------------------------------
// TAB 1: Kitchen Prep Board (กระดานสเปกวัตถุดิบสำหรับครัว)
// -------------------------------------------------------------------------
// Selection & Batch Printing Handlers
window.toggleDishSelection = function(dishId, event) {
    if (event) event.stopPropagation();
    if (selectedDishIds.has(dishId)) {
        selectedDishIds.delete(dishId);
    } else {
        selectedDishIds.add(dishId);
    }
    updateSelectionUI();
};

window.selectAllDishes = function() {
    const dishes = getFilteredDishes();
    dishes.forEach(d => selectedDishIds.add(d.id));
    updateSelectionUI();
    showToast(`เลือกทั้งหมด ${selectedDishIds.size} เมนูสำหรับการพิมพ์แล้ว`);
};

window.deselectAllDishes = function() {
    selectedDishIds.clear();
    updateSelectionUI();
    showToast('ล้างการเลือกเมนูทั้งหมดแล้ว', 'info');
};

window.selectStationDishes = function(stationId, stationName) {
    selectedDishIds.clear();
    if (!appData || !appData.dishes) return;
    appData.dishes.forEach(dish => {
        const station = getDishStation(dish);
        if (station.id === stationId) {
            selectedDishIds.add(dish.id);
        }
    });
    updateSelectionUI();
    showToast(`เลือกเมนู "${stationName}" (${selectedDishIds.size} เมนู) พร้อมสั่งพิมพ์แล้ว!`);
};

function updateSelectionUI() {
    const count = selectedDishIds.size;
    document.querySelectorAll('.selected-count-badge').forEach(el => {
        el.textContent = count;
    });

    document.querySelectorAll('.print-selected-btn').forEach(btn => {
        if (count > 0) {
            btn.innerHTML = `🖨️ พิมพ์เฉพาะที่เลือก (${count} เมนู)`;
            btn.classList.remove('opacity-60', 'pointer-events-none');
        } else {
            btn.innerHTML = `🖨️ พิมพ์เฉพาะที่เลือก (0)`;
            btn.classList.add('opacity-60');
        }
    });

    document.querySelectorAll('.dish-checkbox').forEach(cb => {
        const dishId = cb.dataset.dishId;
        const isChecked = selectedDishIds.has(dishId);
        cb.checked = isChecked;
        const card = cb.closest('.dish-item');
        if (card) {
            card.classList.toggle('is-selected-for-print', isChecked);
            card.classList.toggle('ring-2', isChecked);
            card.classList.toggle('ring-blue-500', isChecked);
            card.classList.toggle('bg-blue-50/20', isChecked);
        }
    });
}

window.printSelectedBatch = function() {
    if (selectedDishIds.size === 0) {
        if (confirm('คุณยังไม่ได้เลือกเมนูใดๆ ต้องการเลือกเมนูทั้งหมดที่แสดงอยู่ตอนนี้เพื่อพิมพ์ใช่หรือไม่?')) {
            selectAllDishes();
        } else {
            return;
        }
    }

    const badge = document.getElementById('print-batch-badge');
    if (badge) {
        badge.textContent = `ชุดพิมพ์เฉพาะที่เลือก (${selectedDishIds.size} เมนู)`;
    }
    const dateEl = document.getElementById('print-current-date');
    if (dateEl) {
        dateEl.textContent = new Date().toLocaleDateString('th-TH', { 
            year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' 
        });
    }

    const mainContent = document.getElementById('main-content');
    if (mainContent) {
        mainContent.classList.add('printing-selected-only');
    }

    window.print();

    setTimeout(() => {
        if (mainContent) {
            mainContent.classList.remove('printing-selected-only');
        }
    }, 1500);
};

window.printAllDishes = function() {
    const badge = document.getElementById('print-batch-badge');
    if (badge) {
        badge.textContent = `ชุดพิมพ์: ทั้งหมด (${appData ? appData.dishes.length : 0} เมนู)`;
    }
    const dateEl = document.getElementById('print-current-date');
    if (dateEl) {
        dateEl.textContent = new Date().toLocaleDateString('th-TH', { 
            year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' 
        });
    }
    const mainContent = document.getElementById('main-content');
    if (mainContent) {
        mainContent.classList.remove('printing-selected-only');
    }
    window.print();
};

function renderKitchenPrepBoard(container) {
    const dishes = getFilteredDishes();

    const wokCount = appData.dishes.filter(d => getDishStation(d).id === 'wok').length;
    const soupCount = appData.dishes.filter(d => getDishStation(d).id === 'soup').length;
    const grillCount = appData.dishes.filter(d => getDishStation(d).id === 'grill').length;
    const saladCount = appData.dishes.filter(d => getDishStation(d).id === 'salad').length;
    const omeletCount = appData.dishes.filter(d => getDishStation(d).id === 'omelet').length;

    const topControls = `
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4 print:hidden">
            <div>
                <h2 class="text-lg md:text-xl font-bold text-slate-800 flex items-center gap-2">
                    📋 กระดานสเปกวัตถุดิบสำหรับครัว (Kitchen Prep Board)
                </h2>
                <p class="text-xs text-slate-500 mt-0.5">
                    แสดงเฉพาะสิ่งที่คนครัวต้อง <strong>ชั่ง (กรัม) / ตวง (มล.) / นับชิ้น</strong> • ติ๊กเลือกเมนูเพื่อสั่งพิมพ์เฉพาะชุดที่ต้องการได้
                </p>
            </div>
            <div class="flex flex-wrap items-center gap-1.5 w-full sm:w-auto">
                <button onclick="setViewMode('wall-sheet')" class="flex-1 sm:flex-initial px-3 py-1.5 text-xs font-bold rounded-lg border transition-all ${
                    viewMode === 'wall-sheet' ? 'bg-blue-600 text-white border-blue-600 shadow-xs' : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
                }">
                    📌 ป้ายย่อติดผนัง (Wall Sheet)
                </button>
                <button onclick="setViewMode('cards')" class="flex-1 sm:flex-initial px-3 py-1.5 text-xs font-bold rounded-lg border transition-all ${
                    viewMode === 'cards' ? 'bg-blue-600 text-white border-blue-600 shadow-xs' : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
                }">
                    🗂️ การ์ดครัว
                </button>
                <button onclick="setViewMode('table')" class="flex-1 sm:flex-initial px-3 py-1.5 text-xs font-bold rounded-lg border transition-all ${
                    viewMode === 'table' ? 'bg-blue-600 text-white border-blue-600 shadow-xs' : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
                }">
                    📑 ตารางรวม
                </button>
            </div>
        </div>

        <!-- Custom Batch Selection Toolbar -->
        <div id="batch-toolbar" class="bg-white rounded-2xl border border-slate-200 p-3 mb-4 shadow-xs print:hidden">
            <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
                <!-- Station selection buttons -->
                <div class="flex flex-wrap items-center gap-1.5 text-xs">
                    <span class="font-bold text-slate-700 mr-1 flex items-center gap-1">
                        🏷️ ทางลัดเลือกตามเตา:
                    </span>
                    <button onclick="selectStationDishes('wok', 'เตาผัด')" class="px-2.5 py-1 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-200 font-semibold transition-all">
                        🔥 เตาผัด (${wokCount})
                    </button>
                    <button onclick="selectStationDishes('soup', 'เตาต้ม/แกง')" class="px-2.5 py-1 rounded-lg bg-sky-50 hover:bg-sky-100 text-sky-800 border border-sky-200 font-semibold transition-all">
                        🍲 เตาต้ม/แกง (${soupCount})
                    </button>
                    <button onclick="selectStationDishes('grill', 'เตาย่าง/ทอด')" class="px-2.5 py-1 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-800 border border-rose-200 font-semibold transition-all">
                        🦐 เตาเผา/ย่าง/ทอด (${grillCount})
                    </button>
                    <button onclick="selectStationDishes('salad', 'สเตชันยำ')" class="px-2.5 py-1 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200 font-semibold transition-all">
                        🥗 สเตชันยำ (${saladCount})
                    </button>
                    <button onclick="selectStationDishes('omelet', 'เตาไข่')" class="px-2.5 py-1 rounded-lg bg-yellow-50 hover:bg-yellow-100 text-yellow-800 border border-yellow-200 font-semibold transition-all">
                        🍳 เตาไข่ (${omeletCount})
                    </button>
                    <span class="text-slate-300">|</span>
                    <button onclick="selectAllDishes()" class="px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium">
                        ☑️ ทั้งหมด
                    </button>
                    <button onclick="deselectAllDishes()" class="px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-600 font-medium">
                        ⬜ ล้าง
                    </button>
                </div>

                <!-- Action / Print button -->
                <div class="flex items-center gap-2 self-end lg:self-auto">
                    <span class="text-xs font-bold px-2.5 py-1.5 rounded-lg bg-blue-50 text-blue-800 border border-blue-200 whitespace-nowrap">
                        เลือกแล้ว: <strong class="selected-count-badge font-black text-blue-900">${selectedDishIds.size}</strong> เมนู
                    </span>
                    <button onclick="printSelectedBatch()" class="print-selected-btn px-3.5 py-1.5 text-xs font-bold rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm flex items-center gap-1.5 transition-all whitespace-nowrap ${selectedDishIds.size === 0 ? 'opacity-60' : ''}">
                        🖨️ พิมพ์เฉพาะที่เลือก (<span class="selected-count-badge">${selectedDishIds.size}</span>)
                    </button>
                    <button onclick="printAllDishes()" class="px-2.5 py-1.5 text-xs font-semibold rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 transition-all whitespace-nowrap">
                        พิมพ์ทั้งหมด
                    </button>
                </div>
            </div>
        </div>
    `;

    if (dishes.length === 0) {
        container.innerHTML = topControls + `
            <div class="p-12 text-center bg-white rounded-2xl border border-slate-200 text-slate-400">
                <p class="text-base font-semibold">ไม่พบรายการเมนูที่ตรงกับคำค้นหา</p>
            </div>
        `;
        return;
    }

    if (viewMode === 'wall-sheet') {
        // High Density Compact Wall Sheet Mode (3-Columns Grid for Wall Mounting)
        let wallHtml = '<div class="wall-grid grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-2.5">';
        dishes.forEach((dish) => {
            const station = getDishStation(dish);
            const isSel = selectedDishIds.has(dish.id);
            const activeItems = (dish.items || []).filter(item => !item.disabled);

            wallHtml += `
                <div class="dish-item wall-card bg-white rounded-xl border border-slate-200 p-2.5 shadow-xs flex flex-col justify-between transition-all hover:border-blue-400 break-inside-avoid ${isSel ? 'is-selected-for-print ring-2 ring-blue-500 bg-blue-50/20' : ''}" data-dish-id="${dish.id}">
                    <div>
                        <!-- Header of Wall Card -->
                        <div class="flex items-center justify-between gap-1.5 border-b border-slate-100 pb-1.5 mb-1.5">
                            <div class="flex items-center gap-2 min-w-0">
                                <label class="cursor-pointer inline-flex items-center no-print" onclick="event.stopPropagation()">
                                    <input type="checkbox" data-dish-id="${dish.id}" onchange="toggleDishSelection('${dish.id}', event)" class="dish-checkbox w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-300 cursor-pointer" ${isSel ? 'checked' : ''}>
                                </label>
                                <h4 class="font-black text-slate-900 text-xs md:text-sm truncate">
                                    ${dish.name}
                                </h4>
                            </div>
                            <div class="flex items-center gap-1 shrink-0">
                                <span class="text-[10px] font-bold px-1.5 py-0.5 rounded border ${station.color}">
                                    ${station.icon} ${station.name}
                                </span>
                                <span class="text-xs font-black text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200" title="ราคาขายหน้าร้าน">
                                    ${dish.price}.-
                                </span>
                                ${showDeliveryPrices ? `
                                    <span class="text-[11px] font-black text-teal-800 bg-teal-50 px-1.5 py-0.5 rounded border border-teal-300" title="ราคา Grab / Lineman (+${deliveryMarkupPct}%)">
                                        🛵 ${dish.delivery_price}.-
                                    </span>
                                ` : ''}
                            </div>
                        </div>

                        <!-- Ingredients List with LARGE BOLD Numbers (Only Active Items) -->
                        <div class="space-y-1">
                            ${activeItems.length > 0 ? activeItems.map(item => {
                                const pInfo = getProteinColorInfo(item.rm_name);
                                const actionIcon = item.action === 'ชั่งน้ำหนัก' ? '⚖️' : item.action === 'นับชิ้น' ? '🔢' : '🧪';
                                return `
                                    <div class="flex items-center justify-between text-[11px] p-1 rounded bg-slate-50 border border-slate-100 border-l-2 ${pInfo.border}">
                                        <span class="truncate font-semibold text-slate-800 pr-1">
                                            ${item.rm_name}
                                            ${item.type === 'primary' ? '<span class="text-[9px] text-rose-600 font-bold ml-0.5">(หลัก)</span>' : ''}
                                        </span>
                                        <span class="font-black text-blue-900 shrink-0 text-xs bg-white px-1.5 py-0.2 rounded border border-slate-200">
                                            ${actionIcon} ${item.portion} <strong class="text-[10px] font-normal text-slate-600">${item.unit}</strong>
                                        </span>
                                    </div>
                                `;
                            }).join('') : '<div class="text-[11px] text-slate-400 py-1 text-center font-medium">ไม่มีวัตถุดิบที่เปิดใช้งาน</div>'}
                        </div>
                    </div>

                    <!-- Footer with Cost Summary & Quick Edit -->
                    <div class="mt-2 pt-1 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-500">
                        <span>ต้นทุน: <strong class="text-slate-700">${dish.primary_secondary_cost}.-</strong> (${dish.total_cost_pct}%)</span>
                        <button onclick="openDishEditor('${dish.id}')" class="text-blue-600 hover:text-blue-800 font-bold no-print">
                            ✏️ ปรับสเปก
                        </button>
                    </div>
                </div>
            `;
        });
        wallHtml += '</div>';
        container.innerHTML = topControls + wallHtml;
    } else if (viewMode === 'cards') {
        // Detailed Card View
        let cardsHtml = '<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 md:gap-5 print:grid-cols-2">';
        dishes.forEach((dish) => {
            const catObj = appData.categories.find(c => c.id === dish.category);
            const catName = catObj ? catObj.name.split('(')[0] : '';
            const station = getDishStation(dish);
            const isSel = selectedDishIds.has(dish.id);
            const activeItems = (dish.items || []).filter(item => !item.disabled);

            cardsHtml += `
                <div class="dish-item bg-white rounded-2xl border border-slate-200 shadow-xs hover:shadow-md transition-all overflow-hidden flex flex-col justify-between print:border-slate-400 print:shadow-none print:break-inside-avoid ${isSel ? 'is-selected-for-print ring-2 ring-blue-500 bg-blue-50/20' : ''}" data-dish-id="${dish.id}">
                    <div class="p-4 border-b border-slate-100 bg-slate-50/70">
                        <div class="flex items-center justify-between gap-2">
                            <div class="flex items-center gap-2">
                                <label class="cursor-pointer inline-flex items-center no-print" onclick="event.stopPropagation()">
                                    <input type="checkbox" data-dish-id="${dish.id}" onchange="toggleDishSelection('${dish.id}', event)" class="dish-checkbox w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-300 cursor-pointer" ${isSel ? 'checked' : ''}>
                                </label>
                                <span class="text-[11px] font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-800 uppercase tracking-wider">
                                    ${catName} | รูปที่ ${dish.image_ref}
                                </span>
                            </div>
                            <div class="text-right">
                                <span class="text-base font-black text-emerald-700" title="ราคาขายหน้าร้าน">
                                    ${dish.price.toLocaleString()}.-
                                </span>
                                ${showDeliveryPrices ? `
                                    <div class="text-[11px] font-black text-teal-700">🛵 Grab/LM: ${dish.delivery_price.toLocaleString()}.-</div>
                                ` : ''}
                            </div>
                        </div>
                        <h3 class="text-base md:text-lg font-bold text-slate-800 mt-1 leading-snug">
                            ${dish.name}
                        </h3>
                    </div>

                    <div class="p-4 flex-1">
                        <div class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2.5 flex items-center justify-between">
                            <span>สเปกวัตถุดิบ (ชั่ง/ตวง/นับ)</span>
                            <button onclick="openDishEditor('${dish.id}')" class="text-blue-600 hover:text-blue-800 font-bold text-xs no-print">
                                ✏️ ปรับสเปก
                            </button>
                        </div>

                        <div class="space-y-2">
                            ${activeItems.length > 0 ? activeItems.map(item => {
                                const actionBg = item.action === 'ชั่งน้ำหนัก' 
                                    ? 'bg-amber-50 text-amber-800 border-amber-200' 
                                    : item.action === 'นับชิ้น' 
                                        ? 'bg-purple-50 text-purple-800 border-purple-200' 
                                        : 'bg-sky-50 text-sky-800 border-sky-200';
                                
                                const actionIcon = item.action === 'ชั่งน้ำหนัก' ? '⚖️' : item.action === 'นับชิ้น' ? '🔢' : '🧪';

                                return `
                                    <div class="p-3 rounded-xl border border-slate-100 bg-slate-50/60 flex items-start justify-between gap-2">
                                        <div class="flex-1">
                                            <div class="flex items-center gap-1.5 flex-wrap">
                                                <span class="text-xs md:text-sm font-bold text-slate-800">${item.rm_name}</span>
                                                ${item.type === 'primary' 
                                                    ? '<span class="text-[10px] px-1.5 py-0.5 rounded bg-rose-100 text-rose-700 font-bold">หลัก</span>' 
                                                    : '<span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-200 text-slate-600 font-medium">รอง</span>'}
                                            </div>
                                            ${item.note ? `<p class="text-[11px] text-slate-500 mt-1 leading-snug">${item.note}</p>` : ''}
                                        </div>
                                        <div class="text-right shrink-0">
                                            <div class="text-base font-black text-blue-700">
                                                ${item.portion} <span class="text-xs font-normal text-slate-600">${item.unit}</span>
                                            </div>
                                            <span class="inline-block text-[10px] px-1.5 py-0.5 rounded border ${actionBg} font-bold mt-1">
                                                ${actionIcon} ${item.action}
                                            </span>
                                        </div>
                                    </div>
                                `;
                            }).join('') : '<div class="text-xs text-slate-400 p-3 text-center bg-slate-50 rounded-xl">ไม่มีวัตถุดิบที่เปิดใช้งาน</div>'}
                        </div>
                    </div>

                    <div class="p-3.5 bg-slate-50 border-t border-slate-100 text-[11px] text-slate-500 flex items-center justify-between">
                        <span>ต้นทุนหลัก-รอง: <strong class="text-slate-800 font-bold">${dish.primary_secondary_cost}.-</strong> (${dish.ps_cost_pct}%)</span>
                        <span class="font-bold ${dish.total_cost_pct <= 40 ? 'text-emerald-600' : 'text-rose-600'}">
                            Food Cost ${dish.total_cost_pct}%
                        </span>
                    </div>
                </div>
            `;
        });
        cardsHtml += '</div>';
        container.innerHTML = topControls + cardsHtml;
    } else {
        // Table View with Checkboxes
        let tableHtml = `
            <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-x-auto print:border-none print:shadow-none">
                <table class="w-full text-left text-xs text-slate-600 border-collapse">
                    <thead class="bg-slate-100 text-slate-700 uppercase font-bold text-[11px] border-b border-slate-200">
                        <tr>
                            <th class="p-3 w-8 text-center no-print">เลือก</th>
                            <th class="p-3">เมนู</th>
                            <th class="p-3">ราคาหน้าร้าน</th>
                            ${showDeliveryPrices ? '<th class="p-3 text-right bg-emerald-50/50 text-emerald-900 border-l border-emerald-200 whitespace-nowrap">🛵 Grab / Lineman</th>' : ''}
                            <th class="p-3">สเปกวัตถุดิบครัว (ชั่ง/ตวง/นับ)</th>
                            <th class="p-3 text-right">ต้นทุนหลัก-รอง</th>
                            <th class="p-3 text-right">Food Cost %</th>
                            <th class="p-3 text-center print:hidden">จัดการ</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100">
        `;

        dishes.forEach((dish) => {
            const isSel = selectedDishIds.has(dish.id);
            const activeItems = (dish.items || []).filter(item => !item.disabled);
            tableHtml += `
                <tr class="dish-item hover:bg-slate-50 transition-colors ${isSel ? 'is-selected-for-print bg-blue-50/30' : ''}" data-dish-id="${dish.id}">
                    <td class="p-3 text-center no-print">
                        <input type="checkbox" data-dish-id="${dish.id}" onchange="toggleDishSelection('${dish.id}', event)" class="dish-checkbox w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-300 cursor-pointer" ${isSel ? 'checked' : ''}>
                    </td>
                    <td class="p-3 font-bold text-slate-800 text-sm whitespace-nowrap">
                        ${dish.name}
                    </td>
                    <td class="p-3 font-bold text-emerald-700 whitespace-nowrap">${dish.price}.-</td>
                    ${showDeliveryPrices ? `<td class="p-3 text-right font-black text-teal-800 bg-teal-50/30 border-l border-teal-200 whitespace-nowrap">${dish.delivery_price}.-</td>` : ''}
                    <td class="p-3">
                        <div class="flex flex-wrap gap-1.5">
                            ${activeItems.length > 0 ? activeItems.map(item => `
                                <div class="px-2 py-1 rounded-lg bg-slate-100 border border-slate-200 text-[11px] leading-tight">
                                    <strong class="text-slate-800">${item.rm_name}</strong>: 
                                    <span class="text-blue-700 font-bold">${item.portion} ${item.unit}</span>
                                    <span class="text-slate-500">(${item.action})</span>
                                </div>
                            `).join('') : '<span class="text-slate-400">ไม่มีวัตถุดิบที่เปิดใช้งาน</span>'}
                        </div>
                    </td>
                    <td class="p-3 text-right font-bold text-slate-700 whitespace-nowrap">${dish.primary_secondary_cost}.-</td>
                    <td class="p-3 text-right font-black whitespace-nowrap ${dish.total_cost_pct <= 40 ? 'text-emerald-600' : 'text-rose-600'}">
                        ${dish.total_cost_pct}%
                    </td>
                    <td class="p-3 text-center print:hidden whitespace-nowrap">
                        <button onclick="openDishEditor('${dish.id}')" class="px-2.5 py-1 text-xs font-semibold rounded bg-blue-50 text-blue-600 hover:bg-blue-100">
                            ✏️ ปรับ
                        </button>
                    </td>
                </tr>
            `;
        });

        tableHtml += `
                    </tbody>
                </table>
            </div>
        `;
        container.innerHTML = topControls + tableHtml;
    }
}

// -------------------------------------------------------------------------
// TAB 2: Cost Analysis & Margin Controller
// -------------------------------------------------------------------------
function renderCostAnalysis(container) {
    const dishes = getFilteredDishes();

    let html = `
        <div class="bg-white rounded-2xl border border-slate-200 shadow-xs p-4 md:p-5 mb-5">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                <div>
                    <h2 class="text-lg md:text-xl font-bold text-slate-800 flex items-center gap-2">
                        📊 โครงสร้างต้นทุนอาหารและกำไรขั้นต้น (Cost & Margin Controller)
                    </h2>
                    <p class="text-xs text-slate-500 mt-0.5">
                        เป้าหมาย: ต้นทุนรวม &le; 40% | กำไรขั้นต้น &ge; 60% | ต้นทุนวัตถุดิบหลัก-รอง 35% - 40%
                    </p>
                </div>
                <div class="flex items-center gap-2 flex-wrap text-xs">
                    <span class="text-slate-600 bg-blue-50 px-3 py-1.5 rounded-lg border border-blue-200">
                        💡 คลิกปุ่ม <strong class="text-blue-700">"ปรับสเปก"</strong> เพื่อแก้ไขสูตร เปิด/ปิดวัตถุดิบ หรือปรับราคาซื้อสด
                    </span>
                    ${!showDeliveryPrices ? `
                        <button onclick="toggleDeliveryMode(true)" class="px-2.5 py-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-300 rounded-lg font-bold transition-all">
                            🛵 แสดงราคา Grab/Lineman
                        </button>
                    ` : ''}
                </div>
            </div>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-x-auto">
            <table class="w-full text-left text-xs text-slate-600 border-collapse">
                <thead class="bg-slate-100 text-slate-700 uppercase font-bold text-[11px] border-b border-slate-200">
                    <tr>
                        <th class="p-3">เมนูอาหาร</th>
                        <th class="p-3 text-right">ราคาขายหน้าร้าน</th>
                        ${showDeliveryPrices ? `
                            <th class="p-3 text-right bg-emerald-50/70 text-emerald-900 border-l border-emerald-200 whitespace-nowrap">🛵 Grab/LM (+${deliveryMarkupPct}%)</th>
                            <th class="p-3 text-right bg-emerald-50/70 text-emerald-900 whitespace-nowrap">GP เดลิเวอรีสุทธิ (หัก GP 30%)</th>
                        ` : ''}
                        <th class="p-3 text-right">ต้นทุนหลัก+รอง</th>
                        <th class="p-3 text-right">% หลัก-รอง</th>
                        <th class="p-3 text-right">เครื่องปรุง (~2.5%)</th>
                        <th class="p-3 text-right">ต้นทุนรวม</th>
                        <th class="p-3 text-right">Food Cost %</th>
                        <th class="p-3 text-right">กำไรขั้นต้น (GP หน้าร้าน)</th>
                        <th class="p-3 text-center">สถานะ</th>
                        <th class="p-3 text-center">จัดการ</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
    `;

    dishes.forEach((dish) => {
        const isCompliant = dish.is_target_compliant;
        html += `
            <tr class="hover:bg-slate-50 transition-colors">
                <td class="p-3 font-bold text-slate-800 text-sm whitespace-nowrap">
                    ${dish.name}
                    <div class="text-[10px] text-slate-400 font-normal">รูปภาพชุดที่ ${dish.image_ref}</div>
                </td>
                <td class="p-3 text-right font-black text-slate-800 whitespace-nowrap">${dish.price}.-</td>
                ${showDeliveryPrices ? `
                    <td class="p-3 text-right font-black text-teal-800 bg-teal-50/40 border-l border-teal-200 whitespace-nowrap">
                        ${dish.delivery_price}.-
                    </td>
                    <td class="p-3 text-right font-bold text-teal-900 bg-teal-50/40 whitespace-nowrap">
                        ${dish.delivery_gross_profit}.- 
                        <span class="text-[10px] font-black ${dish.delivery_gross_margin_pct >= 60 ? 'text-emerald-700' : 'text-amber-700'}">(${dish.delivery_gross_margin_pct}%)</span>
                    </td>
                ` : ''}
                <td class="p-3 text-right font-bold text-blue-700 whitespace-nowrap">${dish.primary_secondary_cost}.-</td>
                <td class="p-3 text-right font-semibold text-blue-600 whitespace-nowrap">${dish.ps_cost_pct}%</td>
                <td class="p-3 text-right text-slate-400 whitespace-nowrap">${dish.minor_seasoning_cost}.-</td>
                <td class="p-3 text-right font-bold text-slate-800 whitespace-nowrap">${dish.total_cost}.-</td>
                <td class="p-3 text-right font-black whitespace-nowrap ${dish.total_cost_pct <= 40 ? 'text-emerald-600' : 'text-rose-600'}">
                    ${dish.total_cost_pct}%
                </td>
                <td class="p-3 text-right font-black text-emerald-700 whitespace-nowrap">
                    ${dish.gross_profit}.- <span class="text-[10px] text-emerald-600">(${dish.gross_margin_pct}%)</span>
                </td>
                <td class="p-3 text-center whitespace-nowrap">
                    ${isCompliant 
                        ? '<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800">✅ ผ่านเกณฑ์</span>' 
                        : '<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-rose-100 text-rose-800">⚠️ เกิน 40%</span>'}
                </td>
                <td class="p-3 text-center whitespace-nowrap">
                    <button onclick="openDishEditor('${dish.id}')" class="px-2.5 py-1 text-xs font-semibold rounded-lg bg-blue-50 text-blue-600 border border-blue-200 hover:bg-blue-100 transition-all">
                        ✏️ ปรับสเปก
                    </button>
                </td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = html;
}

// -------------------------------------------------------------------------
// INTERACTIVE RECIPE & COST CUSTOMIZATION MODAL (GLOBAL PRICE SYNC & REAL-TIME)
// -------------------------------------------------------------------------

// Helper to render Raw Materials in dropdown grouped by category
function renderRawMaterialOptions() {
    if (!appData || !appData.raw_materials) return '';
    const rms = Object.values(appData.raw_materials);
    const groups = {};
    rms.forEach(rm => {
        if (!groups[rm.category]) groups[rm.category] = [];
        groups[rm.category].push(rm);
    });

    let html = '';
    Object.entries(groups).forEach(([cat, list]) => {
        html += `<optgroup label="${cat}">`;
        list.forEach(rm => {
            const price = rm.use_custom && rm.custom_price_display !== undefined ? rm.custom_price_display : rm.display_price;
            html += `<option value="${rm.id}">${rm.name} (${price} บ./${rm.display_unit})</option>`;
        });
        html += `</optgroup>`;
    });
    return html;
}

// Recalculate preview in memory for currentEditingDish
function calculateModalPreview() {
    if (!currentEditingDish) return;
    let psCost = 0;
    currentEditingDish.items.forEach(item => {
        if (item.disabled) {
            item.item_cost = 0;
            item.cost_pct_of_sales = 0;
            return;
        }
        const rm = appData.raw_materials[item.rm_id];
        let effectivePrice = 0;
        if (currentEditingRawMaterials[item.rm_id]) {
            effectivePrice = currentEditingRawMaterials[item.rm_id].effectivePrice;
        } else if (rm) {
            effectivePrice = (rm.use_custom && rm.custom_price !== undefined) 
                ? rm.custom_price 
                : (rm.market_price || 0);
        }
        const itemCost = Math.round(effectivePrice * (item.portion || 0) * 100) / 100;
        item.unit_cost = effectivePrice;
        item.item_cost = itemCost;
        item.cost_pct_of_sales = Math.round((itemCost / (currentEditingDish.price || 1)) * 1000) / 10;
        psCost += itemCost;
    });

    currentEditingDish.primary_secondary_cost = Math.round(psCost * 100) / 100;
    currentEditingDish.minor_seasoning_cost = Math.round(currentEditingDish.price * 0.025 * 100) / 100;
    currentEditingDish.total_cost = Math.round((currentEditingDish.primary_secondary_cost + currentEditingDish.minor_seasoning_cost) * 100) / 100;
    currentEditingDish.ps_cost_pct = Math.round((currentEditingDish.primary_secondary_cost / (currentEditingDish.price || 1)) * 1000) / 10;
    currentEditingDish.total_cost_pct = Math.round((currentEditingDish.total_cost / (currentEditingDish.price || 1)) * 1000) / 10;
    currentEditingDish.gross_profit = Math.round((currentEditingDish.price - currentEditingDish.total_cost) * 100) / 100;
    currentEditingDish.gross_margin_pct = Math.round((currentEditingDish.gross_profit / (currentEditingDish.price || 1)) * 1000) / 10;
    currentEditingDish.is_target_compliant = (currentEditingDish.total_cost_pct <= 40.0 && currentEditingDish.gross_margin_pct >= 60.0);

    // Delivery Preview
    const markup = currentEditingDish.delivery_markup_pct || deliveryMarkupPct || 30;
    currentEditingDish.delivery_price = Math.round(currentEditingDish.price * (1 + markup / 100));
    const deliveryPlatformGP = 0.30;
    currentEditingDish.delivery_net_revenue = Math.round(currentEditingDish.delivery_price * (1 - deliveryPlatformGP) * 100) / 100;
    currentEditingDish.delivery_gross_profit = Math.round((currentEditingDish.delivery_net_revenue - currentEditingDish.total_cost) * 100) / 100;
    currentEditingDish.delivery_gross_margin_pct = Math.round((currentEditingDish.delivery_gross_profit / (currentEditingDish.delivery_net_revenue || 1)) * 1000) / 10;
}

// Update the top KPI summary banner in the modal
function updateModalKPIBanner() {
    if (!currentEditingDish) return;

    const psCostEl = document.getElementById('modal-ps-cost');
    if (psCostEl) psCostEl.textContent = `${currentEditingDish.primary_secondary_cost}.-`;
    const psPctEl = document.getElementById('modal-ps-cost-pct');
    if (psPctEl) psPctEl.textContent = `(${currentEditingDish.ps_cost_pct}%)`;

    const totalCostEl = document.getElementById('modal-total-cost');
    if (totalCostEl) totalCostEl.textContent = `${currentEditingDish.total_cost}.-`;
    const totalPctEl = document.getElementById('modal-total-cost-pct');
    if (totalPctEl) {
        totalPctEl.textContent = `(${currentEditingDish.total_cost_pct}%)`;
        totalPctEl.className = `text-[10px] font-bold block ${currentEditingDish.total_cost_pct <= 40 ? 'text-emerald-600' : 'text-rose-600'}`;
    }

    const gpEl = document.getElementById('modal-gross-profit');
    if (gpEl) gpEl.textContent = `${currentEditingDish.gross_profit}.-`;
    const gmEl = document.getElementById('modal-gross-margin');
    if (gmEl) gmEl.textContent = `(${currentEditingDish.gross_margin_pct}%)`;

    const delPriceEl = document.getElementById('modal-delivery-price');
    if (delPriceEl) delPriceEl.textContent = `${currentEditingDish.delivery_price}.-`;
    const delGpEl = document.getElementById('modal-delivery-gp');
    if (delGpEl) delGpEl.textContent = `GP สุทธิ ${currentEditingDish.delivery_gross_profit}.-`;

    const badgeEl = document.getElementById('modal-compliance-badge');
    if (badgeEl) {
        badgeEl.textContent = currentEditingDish.is_target_compliant ? '✅ ผ่านเกณฑ์ (≤ 40%)' : '⚠️ เกินเกณฑ์เป้าหมาย (> 40%)';
        badgeEl.className = `px-2.5 py-0.5 rounded-full text-xs font-black ${currentEditingDish.is_target_compliant ? 'bg-emerald-600 text-white shadow-xs' : 'bg-rose-600 text-white shadow-xs'}`;
    }

    const bannerEl = document.getElementById('modal-kpi-banner');
    if (bannerEl) {
        bannerEl.className = `p-3.5 rounded-2xl border transition-all ${currentEditingDish.is_target_compliant ? 'bg-emerald-50/70 border-emerald-300' : 'bg-rose-50/70 border-rose-300'}`;
    }
}

// Update single row cost display without replacing input DOM (preserves keyboard focus)
function updateRowCostDisplay(idx) {
    const rowEl = document.querySelector(`.dish-modal-item-row[data-item-idx="${idx}"]`);
    if (!rowEl || !currentEditingDish || !currentEditingDish.items[idx]) return;
    const item = currentEditingDish.items[idx];
    const costEl = rowEl.querySelector('.modal-row-cost-val');
    if (costEl) costEl.textContent = item.disabled ? '0.00 บาท' : `${(item.item_cost || 0).toFixed(2)} บาท`;
    const pctEl = rowEl.querySelector('.modal-row-pct-val');
    if (pctEl) pctEl.textContent = item.disabled ? '0.0% ของราคาขายหน้าร้าน' : `${item.cost_pct_of_sales}% ของราคาขายหน้าร้าน`;
}

// Render HTML for the modal items list
function renderModalItemsListHtml() {
    if (!currentEditingDish || !currentEditingDish.items || currentEditingDish.items.length === 0) {
        return `<div class="p-6 text-center text-slate-400 bg-slate-50 rounded-xl border border-dashed border-slate-200 text-xs">ยังไม่มีวัตถุดิบในเมนูนี้ คลิก "➕ เพิ่มวัตถุดิบ" เพื่อเพิ่ม</div>`;
    }

    return currentEditingDish.items.map((item, idx) => {
        const rm = appData.raw_materials[item.rm_id];
        const isCustomPriceEdited = currentEditingRawMaterials[item.rm_id] !== undefined;
        const currentDisplayPrice = isCustomPriceEdited 
            ? currentEditingRawMaterials[item.rm_id].display_price 
            : (rm ? (rm.use_custom && rm.custom_price_display !== undefined ? rm.custom_price_display : rm.display_price) : 0);
        const displayUnit = rm ? rm.display_unit : (item.unit === 'g' ? 'กก.' : item.unit === 'ml' ? 'ลิตร' : item.unit);
        const usageCount = getRawMaterialUsageCount(item.rm_id);
        const isDisabled = item.disabled === true;

        const actionIcon = item.action === 'ชั่งน้ำหนัก' ? '⚖️' : item.action === 'นับชิ้น' ? '🔢' : '🧪';

        return `
            <div class="dish-modal-item-row p-3 rounded-2xl border transition-all ${
                isDisabled 
                    ? 'bg-slate-100/80 border-slate-200 opacity-60' 
                    : 'bg-white border-slate-200 shadow-2xs hover:border-blue-300'
            }" data-item-idx="${idx}">
                <!-- Row Top Bar: Checkbox + Name + Type Toggle + Action + Trash -->
                <div class="flex items-center justify-between gap-2 pb-2 border-b border-slate-100">
                    <div class="flex items-center gap-2 min-w-0">
                        <label class="cursor-pointer inline-flex items-center" title="${isDisabled ? 'คลิกเพื่อเปิดใช้งานวัตถุดิบนี้' : 'คลิกเพื่อปิดใช้งาน (ตัดออกจากต้นทุน)'}">
                            <input type="checkbox" ${!isDisabled ? 'checked' : ''} 
                                onchange="toggleModalItem(${idx}, this.checked)" 
                                class="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-300 cursor-pointer" />
                        </label>
                        <span class="text-xs sm:text-sm font-black text-slate-800 truncate ${isDisabled ? 'line-through text-slate-400' : ''}">
                            ${item.rm_name}
                        </span>
                        ${isDisabled ? '<span class="text-[10px] font-bold px-1.5 py-0.2 rounded bg-slate-200 text-slate-600">ปิดใช้งาน</span>' : ''}
                    </div>

                    <div class="flex items-center gap-1.5 shrink-0">
                        <!-- Switch Primary / Secondary -->
                        <button type="button" onclick="toggleModalItemType(${idx})" 
                            class="text-[10px] font-black px-2 py-0.5 rounded-full border transition-all ${
                                item.type === 'primary' 
                                    ? 'bg-rose-50 text-rose-700 border-rose-200 hover:bg-rose-100' 
                                    : 'bg-slate-100 text-slate-600 border-slate-200 hover:bg-slate-200'
                            }" title="คลิกเพื่อสลับระหว่างวัตถุดิบหลัก / วัตถุดิบรอง">
                            ${item.type === 'primary' ? '⭐ วัตถุดิบหลัก' : '⚪ วัตถุดิบรอง'}
                        </button>

                        <!-- Action Badge -->
                        <span class="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-slate-50 text-slate-500 border border-slate-200">
                            ${actionIcon} ${item.action}
                        </span>

                        <!-- Delete Button -->
                        <button type="button" onclick="removeModalItem(${idx})" 
                            class="w-6 h-6 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 flex items-center justify-center text-xs transition-colors" 
                            title="ลบวัตถุดิบนี้ออกจากเมนู">
                            🗑️
                        </button>
                    </div>
                </div>

                <!-- Row Controls Grid: Inline Portion Edit & Inline RM Purchase Price Edit -->
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-2">
                    <!-- Column 1: Portion in dish -->
                    <div class="bg-slate-50/80 p-2 rounded-xl border border-slate-100">
                        <div class="flex items-center justify-between text-[11px] font-semibold text-slate-600 mb-1">
                            <span>ปริมาณที่ใช้ในจาน:</span>
                            <span class="text-blue-700 font-bold">${item.action}</span>
                        </div>
                        <div class="flex items-center gap-1.5">
                            <input type="number" step="any" min="0" value="${item.portion}" 
                                oninput="onModalPortionChange(${idx}, this.value)" 
                                ${isDisabled ? 'disabled' : ''}
                                class="w-full text-xs font-black p-1.5 border border-slate-300 rounded-lg bg-white focus:ring-1 focus:ring-blue-500 focus:outline-none" />
                            <span class="text-xs font-bold text-slate-600 shrink-0 w-8">${item.unit}</span>
                        </div>
                    </div>

                    <!-- Column 2: Purchase Price per Unit (Global Sync) -->
                    <div class="bg-slate-50/80 p-2 rounded-xl border border-slate-100">
                        <div class="flex items-center justify-between text-[11px] font-semibold text-slate-600 mb-1">
                            <span>ราคาซื้อหน้าร้าน:</span>
                            <span class="text-[10px] font-bold text-blue-700 bg-blue-100/70 px-1 py-0.2 rounded" title="ราคาซื้อนี้จะเชื่อมโยงและคำนวณใหม่กับทุกเมนูที่ใช้วัตถุดิบนี้">
                                💡 ซิงค์ ${usageCount} เมนู
                            </span>
                        </div>
                        <div class="flex items-center gap-1.5">
                            <input type="number" step="any" min="0" value="${currentDisplayPrice}" 
                                oninput="onModalRmPriceChange('${item.rm_id}', this.value)" 
                                class="w-full text-xs font-black p-1.5 border border-slate-300 rounded-lg bg-white focus:ring-1 focus:ring-blue-500 focus:outline-none" />
                            <span class="text-xs font-bold text-slate-600 shrink-0">บ./${displayUnit}</span>
                        </div>
                    </div>
                </div>

                <!-- Row Bottom: Real-Time Calculated Cost & % of Dine-in Sales! -->
                <div class="mt-2 p-2 rounded-xl bg-blue-50/50 border border-blue-100 flex flex-wrap items-center justify-between gap-1 text-xs">
                    <div class="flex items-center gap-2">
                        <span class="text-[11px] font-semibold text-slate-600">ต้นทุนต่อจาน:</span>
                        <strong class="modal-row-cost-val text-xs sm:text-sm font-black text-blue-800">
                            ${isDisabled ? '0.00 บาท' : ((item.item_cost || 0).toFixed(2) + ' บาท')}
                        </strong>
                    </div>

                    <div class="flex items-center gap-1">
                        <span class="text-[10px] text-slate-500">คิดเป็น</span>
                        <span class="modal-row-pct-val text-[11px] font-black px-2 py-0.5 rounded-md ${
                            isDisabled ? 'bg-slate-200 text-slate-600' : 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                        }">
                            ${isDisabled ? '0.0% ของราคาขายหน้าร้าน' : ((item.cost_pct_of_sales || 0) + '% ของราคาขายหน้าร้าน')}
                        </span>
                    </div>
                </div>

                <!-- Prep Note Input -->
                <div class="mt-2">
                    <input type="text" placeholder="📝 บันทึกคำแนะนำเตรียมวัตถุดิบ (เช่น ลอกเปลือก, หั่นเต๋า, ต้มน้ำสต็อก)" 
                        value="${item.note || ''}" 
                        oninput="onModalNoteChange(${idx}, this.value)" 
                        class="w-full text-[11px] p-1.5 border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:ring-1 focus:ring-blue-500 focus:outline-none placeholder:text-slate-400" />
                </div>
            </div>
        `;
    }).join('');
}

// Open Recipe & Cost Customization Modal
window.openDishEditor = function(dishId) {
    const dish = appData.dishes.find(d => d.id === dishId);
    if (!dish) return;

    // Deep copy dish for editing
    currentEditingDish = JSON.parse(JSON.stringify(dish));
    currentEditingDish.items = currentEditingDish.items || [];
    currentEditingDish.items.forEach(it => {
        if (it.disabled === undefined) it.disabled = false;
    });
    currentEditingRawMaterials = {}; // reset pending rm price changes

    calculateModalPreview();

    const catObj = appData.categories.find(c => c.id === currentEditingDish.category);
    const catName = catObj ? catObj.name.split('(')[0] : '';

    const modalHtml = `
        <div id="dish-modal" class="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/60 backdrop-blur-xs p-0 sm:p-4">
            <div class="bg-white rounded-t-3xl sm:rounded-2xl max-w-2xl w-full max-h-[94vh] flex flex-col shadow-2xl animate-in slide-in-from-bottom duration-200">
                <!-- Modal Header -->
                <div class="p-4 sm:p-5 border-b border-slate-200 flex justify-between items-center shrink-0 bg-slate-50/80 rounded-t-2xl">
                    <div class="min-w-0 pr-2">
                        <div class="flex items-center gap-2">
                            <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-800 uppercase tracking-wider">
                                ${catName} | รูปที่ ${currentEditingDish.image_ref}
                            </span>
                            <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-100 text-amber-800">
                                ⚡ แก้ไขสดซิงค์ทั่วระบบ
                            </span>
                        </div>
                        <h3 class="text-base sm:text-lg font-black text-slate-800 truncate mt-1">
                            ปรับแต่งสูตร & ต้นทุน: ${currentEditingDish.name}
                        </h3>
                    </div>
                    <button onclick="closeDishEditor()" class="w-8 h-8 rounded-full bg-slate-200/80 hover:bg-slate-300 flex items-center justify-center text-slate-600 text-lg font-bold transition-all shrink-0">&times;</button>
                </div>

                <!-- Modal Body (Scrollable) -->
                <div class="p-4 sm:p-5 overflow-y-auto space-y-4 flex-1">
                    <!-- Live Cost & Margin KPI Summary Card -->
                    <div id="modal-kpi-banner" class="p-3.5 rounded-2xl border transition-all ${currentEditingDish.is_target_compliant ? 'bg-emerald-50/70 border-emerald-300' : 'bg-rose-50/70 border-rose-300'}">
                        <div class="flex items-center justify-between gap-2 border-b border-slate-200/60 pb-2 mb-2">
                            <div class="flex items-center gap-1.5">
                                <span class="text-sm font-black text-slate-800">📊 ผลคำนวณต้นทุนเรียลไทม์ (Live Margin)</span>
                            </div>
                            <span id="modal-compliance-badge" class="px-2.5 py-0.5 rounded-full text-xs font-black ${currentEditingDish.is_target_compliant ? 'bg-emerald-600 text-white shadow-xs' : 'bg-rose-600 text-white shadow-xs'}">
                                ${currentEditingDish.is_target_compliant ? '✅ ผ่านเกณฑ์ (≤ 40%)' : '⚠️ เกินเกณฑ์เป้าหมาย (> 40%)'}
                            </span>
                        </div>

                        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-xs">
                            <div class="p-2 rounded-xl bg-white border border-slate-200/80 shadow-2xs">
                                <span class="text-slate-500 block text-[10px] font-medium">ต้นทุนหลัก-รอง</span>
                                <strong id="modal-ps-cost" class="text-xs sm:text-sm font-black text-blue-700">${currentEditingDish.primary_secondary_cost}.-</strong>
                                <span id="modal-ps-cost-pct" class="text-[10px] text-slate-400 block">(${currentEditingDish.ps_cost_pct}%)</span>
                            </div>
                            <div class="p-2 rounded-xl bg-white border border-slate-200/80 shadow-2xs">
                                <span class="text-slate-500 block text-[10px] font-medium">ต้นทุนรวม (+2.5%)</span>
                                <strong id="modal-total-cost" class="text-xs sm:text-sm font-black text-slate-800">${currentEditingDish.total_cost}.-</strong>
                                <span id="modal-total-cost-pct" class="text-[10px] font-bold block ${currentEditingDish.total_cost_pct <= 40 ? 'text-emerald-600' : 'text-rose-600'}">(${currentEditingDish.total_cost_pct}%)</span>
                            </div>
                            <div class="p-2 rounded-xl bg-white border border-slate-200/80 shadow-2xs">
                                <span class="text-slate-500 block text-[10px] font-medium">กำไรขั้นต้น (GP)</span>
                                <strong id="modal-gross-profit" class="text-xs sm:text-sm font-black text-emerald-700">${currentEditingDish.gross_profit}.-</strong>
                                <span id="modal-gross-margin" class="text-[10px] text-emerald-600 font-bold block">(${currentEditingDish.gross_margin_pct}%)</span>
                            </div>
                            <div class="p-2 rounded-xl bg-white border border-slate-200/80 shadow-2xs">
                                <span class="text-slate-500 block text-[10px] font-medium">ราคา Grab/LM (+${deliveryMarkupPct}%)</span>
                                <strong id="modal-delivery-price" class="text-xs sm:text-sm font-black text-teal-800">${currentEditingDish.delivery_price}.-</strong>
                                <span id="modal-delivery-gp" class="text-[10px] text-teal-600 font-semibold block">GP สุทธิ ${currentEditingDish.delivery_gross_profit}.-</span>
                            </div>
                        </div>
                    </div>

                    <!-- Selling Price Setting -->
                    <div class="bg-slate-50 p-3.5 rounded-2xl border border-slate-200">
                        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
                            <div>
                                <label for="modal-dish-price" class="text-xs font-black text-slate-800 flex items-center gap-1">
                                    💵 ราคาขายหน้าร้านปกติ (บาท)
                                    <span class="text-[10px] font-normal text-slate-500">(ใช้เป็นฐานคำนวณ % ต้นทุนของวัตถุดิบแต่ละตัว)</span>
                                </label>
                            </div>
                            <div class="flex items-center gap-2 w-full sm:w-auto">
                                <input type="number" id="modal-dish-price" value="${currentEditingDish.price}" min="1" step="1" 
                                    oninput="onModalPriceChange(this.value)" 
                                    class="w-full sm:w-36 text-base font-black text-right p-2 border border-slate-300 rounded-xl bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none" />
                                <span class="text-xs font-bold text-slate-700">บาท</span>
                            </div>
                        </div>
                    </div>

                    <!-- Ingredients List Header & Helper -->
                    <div>
                        <div class="flex items-center justify-between gap-2 mb-1.5">
                            <div>
                                <h4 class="text-xs font-black text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                                    🥬 วัตถุดิบในสูตร (Main & Secondary Ingredients)
                                </h4>
                                <p class="text-[11px] text-slate-500">
                                    เปิด/ปิดรายการ • แก้ไขปริมาณ/ราคาซื้อ • ดู % ต้นทุนเทียบราคาขายหน้าร้านได้ทันที
                                </p>
                            </div>
                            <button type="button" onclick="showAddIngredientDropdown()" class="px-2.5 py-1 text-xs font-bold rounded-lg bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 transition-all shrink-0">
                                ➕ เพิ่มวัตถุดิบ
                            </button>
                        </div>

                        <!-- Add Ingredient Dropdown / Card -->
                        <div id="modal-add-box" class="hidden mb-3 p-3 bg-blue-50/70 border border-blue-200 rounded-2xl space-y-2.5 transition-all">
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold text-blue-900">➕ เลือกวัตถุดิบที่จะเพิ่มเข้าสู่สูตรเมนูนี้:</span>
                                <button type="button" onclick="hideAddIngredientDropdown()" class="text-xs font-bold text-slate-500 hover:text-slate-800">&times; ปิด</button>
                            </div>
                            <div class="flex flex-col sm:flex-row gap-2">
                                <select id="modal-select-existing-rm" class="flex-1 text-xs p-2 rounded-xl border border-blue-300 bg-white font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500">
                                    <option value="">-- เลือกวัตถุดิบจากคลัง (${Object.keys(appData.raw_materials).length} รายการ) --</option>
                                    ${renderRawMaterialOptions()}
                                </select>
                                <button type="button" onclick="addSelectedExistingRm()" class="px-3 py-2 text-xs font-bold rounded-xl bg-blue-600 text-white hover:bg-blue-700 shadow-xs shrink-0">
                                    เพิ่มลงสูตร
                                </button>
                            </div>
                            <div class="text-center pt-1 border-t border-blue-200/60">
                                <button type="button" onclick="toggleCustomRmSubForm()" class="text-xs font-bold text-blue-700 hover:text-blue-900 underline">
                                    ✨ หรือคลิกที่นี่ เพื่อสร้างวัตถุดิบใหม่นอกคลัง
                                </button>
                            </div>
                            <!-- Custom RM Creation Sub-form -->
                            <div id="modal-custom-rm-form" class="hidden pt-2 border-t border-blue-200 space-y-2">
                                <span class="text-[11px] font-bold text-slate-700 block">สร้างวัตถุดิบใหม่เข้าระบบ:</span>
                                <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                                    <input type="text" id="new-rm-name" placeholder="ชื่อวัตถุดิบ (เช่น ปลาหมึกสายสด)" class="p-2 border border-slate-300 rounded-lg bg-white" />
                                    <select id="new-rm-category" class="p-2 border border-slate-300 rounded-lg bg-white">
                                        <option value="อาหารทะเลสด">อาหารทะเลสด</option>
                                        <option value="เนื้อสัตว์และไข่">เนื้อสัตว์และไข่</option>
                                        <option value="ผักสดและสมุนไพร">ผักสดและสมุนไพร</option>
                                        <option value="เครื่องปรุงและซอส">เครื่องปรุงและซอส</option>
                                        <option value="ของแห้งและอื่นๆ">ของแห้งและอื่นๆ</option>
                                    </select>
                                    <div class="flex items-center gap-1">
                                        <input type="number" id="new-rm-price" placeholder="ราคาซื้อ (บ.)" class="w-full p-2 border border-slate-300 rounded-lg bg-white" />
                                        <select id="new-rm-unit" class="p-2 border border-slate-300 rounded-lg bg-white">
                                            <option value="g">บ./กก. (ชั่งกรัม)</option>
                                            <option value="ml">บ./ลิตร (ตวงมล.)</option>
                                            <option value="ฟอง">บ./ฟอง (นับชิ้น)</option>
                                            <option value="ตัว">บ./ตัว (นับชิ้น)</option>
                                            <option value="ชิ้น">บ./ชิ้น (นับชิ้น)</option>
                                        </select>
                                    </div>
                                    <div class="flex items-center gap-1">
                                        <input type="number" id="new-rm-portion" placeholder="ปริมาณที่ใส่ในจานนี้" class="w-full p-2 border border-slate-300 rounded-lg bg-white" />
                                        <select id="new-rm-type" class="p-2 border border-slate-300 rounded-lg bg-white">
                                            <option value="primary">วัตถุดิบหลัก</option>
                                            <option value="secondary" selected>วัตถุดิบรอง</option>
                                        </select>
                                    </div>
                                </div>
                                <button type="button" onclick="submitCreateCustomRm()" class="w-full py-1.5 text-xs font-bold rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 shadow-xs">
                                    💾 สร้างวัตถุดิบและใส่ในเมนูนี้
                                </button>
                            </div>
                        </div>

                        <!-- Items Container -->
                        <div id="modal-items-list" class="space-y-2.5">
                            ${renderModalItemsListHtml()}
                        </div>
                    </div>
                </div>

                <!-- Modal Footer -->
                <div class="p-4 sm:p-5 border-t border-slate-200 flex flex-col sm:flex-row gap-2 shrink-0 bg-slate-50/80 rounded-b-2xl">
                    <button type="button" onclick="closeDishEditor()" class="w-full sm:w-auto px-5 py-2.5 text-xs font-bold rounded-xl bg-white border border-slate-300 text-slate-700 hover:bg-slate-100 transition-all">
                        ยกเลิก
                    </button>
                    <button type="button" onclick="saveDishEditor('${currentEditingDish.id}')" class="flex-1 py-2.5 text-xs font-bold rounded-xl bg-blue-600 hover:bg-blue-700 text-white shadow-md flex items-center justify-center gap-2 transition-all">
                        💾 บันทึก & อัปเดตซิงค์ทั่วระบบ (Global Sync)
                    </button>
                </div>
            </div>
        </div>
    `;

    const existing = document.getElementById('dish-modal');
    if (existing) existing.remove();
    document.body.insertAdjacentHTML('beforeend', modalHtml);
};

// Close modal editor
window.closeDishEditor = function() {
    const modal = document.getElementById('dish-modal');
    if (modal) modal.remove();
    currentEditingDish = null;
    currentEditingRawMaterials = {};
};

// Toggle enable/disable raw material in dish
window.toggleModalItem = function(idx, checked) {
    if (!currentEditingDish || !currentEditingDish.items[idx]) return;
    currentEditingDish.items[idx].disabled = !checked;
    calculateModalPreview();
    updateModalKPIBanner();
    const list = document.getElementById('modal-items-list');
    if (list) list.innerHTML = renderModalItemsListHtml();
};

// Toggle Primary / Secondary ingredient type
window.toggleModalItemType = function(idx) {
    if (!currentEditingDish || !currentEditingDish.items[idx]) return;
    const current = currentEditingDish.items[idx].type;
    currentEditingDish.items[idx].type = current === 'primary' ? 'secondary' : 'primary';
    const list = document.getElementById('modal-items-list');
    if (list) list.innerHTML = renderModalItemsListHtml();
};

// Handle Portion changes inline
window.onModalPortionChange = function(idx, val) {
    if (!currentEditingDish || !currentEditingDish.items[idx]) return;
    const p = parseFloat(val);
    currentEditingDish.items[idx].portion = isNaN(p) ? 0 : p;
    calculateModalPreview();
    updateModalKPIBanner();
    updateRowCostDisplay(idx);
};

// Handle Raw Material Purchase Price changes inline (Global Sync Cascade)
window.onModalRmPriceChange = function(rmId, val) {
    const num = parseFloat(val);
    if (isNaN(num) || num < 0) return;
    const rm = appData.raw_materials[rmId];
    if (!rm) return;

    let effectivePrice = num;
    if (rm.unit === 'g' || rm.unit === 'ml') {
        effectivePrice = Math.round((num / 1000) * 10000) / 10000;
    }

    currentEditingRawMaterials[rmId] = {
        display_price: num,
        effectivePrice: effectivePrice
    };

    calculateModalPreview();
    updateModalKPIBanner();
    currentEditingDish.items.forEach((it, idx) => {
        if (it.rm_id === rmId) {
            updateRowCostDisplay(idx);
        }
    });
};

// Handle Dish Selling Price changes
window.onModalPriceChange = function(val) {
    if (!currentEditingDish) return;
    const p = parseFloat(val);
    if (!isNaN(p) && p > 0) {
        currentEditingDish.price = p;
        calculateModalPreview();
        updateModalKPIBanner();
        currentEditingDish.items.forEach((it, idx) => {
            updateRowCostDisplay(idx);
        });
    }
};

// Handle Dish Item Prep Note changes
window.onModalNoteChange = function(idx, val) {
    if (!currentEditingDish || !currentEditingDish.items[idx]) return;
    currentEditingDish.items[idx].note = val;
};

// Remove raw material from dish
window.removeModalItem = function(idx) {
    if (!currentEditingDish || !currentEditingDish.items[idx]) return;
    const item = currentEditingDish.items[idx];
    if (confirm(`คุณต้องการลบ "${item.rm_name}" ออกจากสูตรอาหารนี้ใช่หรือไม่?`)) {
        currentEditingDish.items.splice(idx, 1);
        calculateModalPreview();
        updateModalKPIBanner();
        const list = document.getElementById('modal-items-list');
        if (list) list.innerHTML = renderModalItemsListHtml();
    }
};

// Add Ingredient Dropdown Controls
window.showAddIngredientDropdown = function() {
    const box = document.getElementById('modal-add-box');
    if (box) box.classList.remove('hidden');
};

window.hideAddIngredientDropdown = function() {
    const box = document.getElementById('modal-add-box');
    if (box) box.classList.add('hidden');
};

window.toggleCustomRmSubForm = function() {
    const form = document.getElementById('modal-custom-rm-form');
    if (form) form.classList.toggle('hidden');
};

// Add existing raw material from catalog
window.addSelectedExistingRm = function() {
    const select = document.getElementById('modal-select-existing-rm');
    if (!select || !select.value) {
        alert('กรุณาเลือกวัตถุดิบจากรายการ');
        return;
    }
    const rmId = select.value;
    const rm = appData.raw_materials[rmId];
    if (!rm) return;

    const action = (rm.unit === 'g') ? 'ชั่งน้ำหนัก' : (rm.unit === 'ml') ? 'ตวงปริมาตร' : 'นับชิ้น';
    const defaultPortion = (rm.unit === 'g') ? 100 : (rm.unit === 'ml') ? 50 : 1;

    currentEditingDish.items.push({
        rm_id: rm.id,
        rm_name: rm.name,
        type: 'secondary',
        action: action,
        portion: defaultPortion,
        unit: rm.unit,
        disabled: false,
        note: ''
    });

    calculateModalPreview();
    updateModalKPIBanner();
    const list = document.getElementById('modal-items-list');
    if (list) list.innerHTML = renderModalItemsListHtml();
    hideAddIngredientDropdown();
    showToast(`เพิ่ม "${rm.name}" ในสูตรแล้ว`);
};

// Create new custom raw material on the fly
window.submitCreateCustomRm = function() {
    const nameInput = document.getElementById('new-rm-name');
    const catInput = document.getElementById('new-rm-category');
    const priceInput = document.getElementById('new-rm-price');
    const unitSelect = document.getElementById('new-rm-unit');
    const portionInput = document.getElementById('new-rm-portion');
    const typeSelect = document.getElementById('new-rm-type');

    if (!nameInput || !nameInput.value.trim()) {
        alert('กรุณากรอกชื่อวัตถุดิบ');
        return;
    }
    const name = nameInput.value.trim();
    const cat = catInput ? catInput.value : 'อาหารทะเลสด';
    const displayPrice = parseFloat(priceInput ? priceInput.value : '0') || 0;
    const unit = unitSelect ? unitSelect.value : 'g';
    const portion = parseFloat(portionInput ? portionInput.value : '1') || 1;
    const type = typeSelect ? typeSelect.value : 'secondary';

    const rmId = 'RM_CUSTOM_' + Date.now();
    const action = (unit === 'g') ? 'ชั่งน้ำหนัก' : (unit === 'ml') ? 'ตวงปริมาตร' : 'นับชิ้น';
    const displayUnit = (unit === 'g') ? 'กก.' : (unit === 'ml') ? 'ลิตร' : unit;

    let marketPrice = displayPrice;
    if (unit === 'g' || unit === 'ml') {
        marketPrice = Math.round((displayPrice / 1000) * 10000) / 10000;
    }

    const newRm = {
        id: rmId,
        name: name,
        category: cat,
        unit: unit,
        display_unit: displayUnit,
        display_price: displayPrice,
        market_price: marketPrice,
        market_price_per_kg: unit === 'g' ? displayPrice : undefined,
        previous_price: displayPrice,
        change_percent: 0,
        last_updated: new Date().toISOString().split('T')[0],
        use_custom: true,
        custom_price_display: displayPrice,
        custom_price: marketPrice
    };

    appData.raw_materials[rmId] = newRm;

    currentEditingDish.items.push({
        rm_id: rmId,
        rm_name: name,
        type: type,
        action: action,
        portion: portion,
        unit: unit,
        disabled: false,
        note: ''
    });

    calculateModalPreview();
    updateModalKPIBanner();
    const list = document.getElementById('modal-items-list');
    if (list) list.innerHTML = renderModalItemsListHtml();
    hideAddIngredientDropdown();
    showToast(`สร้างวัตถุดิบใหม่ "${name}" และเพิ่มเข้าสูตรสำเร็จ!`);
};

// Save dish changes and synchronize globally across all dishes & devices
window.saveDishEditor = function(dishId) {
    if (!currentEditingDish || currentEditingDish.id !== dishId) return;

    // 1. Commit any raw material custom price changes to global master
    const updatedRmList = [];
    Object.entries(currentEditingRawMaterials).forEach(([rmId, pData]) => {
        const rm = appData.raw_materials[rmId];
        if (rm) {
            rm.use_custom = true;
            rm.custom_price_display = pData.display_price;
            rm.custom_price = pData.effectivePrice;
            updatedRmList.push(rm);

            // Broadcast raw material price update to all devices
            broadcastMessage({
                type: 'UPDATE_RM_PRICE',
                rmId: rm.id,
                useCustom: true,
                customVal: pData.display_price,
                effectivePrice: pData.effectivePrice
            });
        }
    });

    // 2. Commit current editing dish to master dish list
    const dishIndex = appData.dishes.findIndex(d => d.id === dishId);
    if (dishIndex !== -1) {
        currentEditingDish.is_customized = true;
        appData.dishes[dishIndex] = JSON.parse(JSON.stringify(currentEditingDish));
    }

    // 3. Recalculate all dishes globally (so other dishes using same updated RM will reflect immediately!)
    recalculateAllDishes();

    // 4. Save to localStorage
    saveData(true);

    // 5. Broadcast dish update to peers
    broadcastMessage({
        type: 'UPDATE_DISH_SPEC',
        dishId: currentEditingDish.id,
        updatedDish: appData.dishes[dishIndex]
    });

    // 6. Save retained delta state in cloud 24/7 broker
    publishCloudDelta();

    // 7. Close modal and render all views
    closeDishEditor();
    renderAll();

    const syncMsg = updatedRmList.length > 0 
        ? `บันทึกสูตร "${currentEditingDish.name}" พร้อมซิงค์ราคา ${updatedRmList.length} วัตถุดิบไปยังทุกเมนูที่เกี่ยวข้องแล้ว!`
        : `บันทึกสูตร "${currentEditingDish.name}" สำเร็จและซิงค์ข้อมูลเรียลไทม์แล้ว!`;
    showToast(syncMsg);
};

// -------------------------------------------------------------------------
// TAB 3: Market Price Manager & 7-Day Auto Sync
// -------------------------------------------------------------------------
function renderMarketPriceManager(container) {
    const rms = Object.values(appData.raw_materials);

    let html = `
        <div class="bg-white rounded-2xl border border-slate-200 shadow-xs p-4 md:p-5 mb-5">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                <div>
                    <h2 class="text-lg md:text-xl font-bold text-slate-800 flex items-center gap-2">
                        🏷️ ฐานข้อมูลราคาตลาด 7 วัน & ปรับต้นทุนหน้าร้าน (Market Prices)
                    </h2>
                    <p class="text-xs text-slate-500 mt-0.5">
                        ทีมงานสามารถแก้ไขราคาซื้อจริงตามตลาดในพื้นที่ หรือเลือกใช้ราคาตลาดอัตโนมัติได้อิสระ
                    </p>
                </div>
                <div class="flex items-center gap-2 w-full sm:w-auto">
                    <button onclick="simulate7DayMarketSync()" class="w-full sm:w-auto px-4 py-2 text-xs font-bold rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white shadow-md flex items-center justify-center gap-1.5 transition-all">
                        🔄 อัปเดตราคาตลาดรอบ 7 วัน
                    </button>
                </div>
            </div>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-x-auto">
            <table class="w-full text-left text-xs text-slate-600 border-collapse">
                <thead class="bg-slate-100 text-slate-700 uppercase font-bold text-[11px] border-b border-slate-200">
                    <tr>
                        <th class="p-3">วัตถุดิบ</th>
                        <th class="p-3">หมวด</th>
                        <th class="p-3 text-right">ราคาตลาดอ้างอิง</th>
                        <th class="p-3 text-center">แนวโน้ม 7 วัน</th>
                        <th class="p-3 text-right">ราคาตั้งเอง (หน้าร้าน)</th>
                        <th class="p-3 text-center">ตัวเลือกที่ใช้</th>
                        <th class="p-3 text-right">ราคาที่ใช้คำนวณ</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
    `;

    rms.forEach(rm => {
        const changeBadge = rm.change_percent > 0 
            ? `<span class="inline-flex items-center text-rose-600 font-bold bg-rose-50 px-2 py-0.5 rounded text-[11px]">🔺 +${rm.change_percent}%</span>`
            : rm.change_percent < 0 
                ? `<span class="inline-flex items-center text-emerald-600 font-bold bg-emerald-50 px-2 py-0.5 rounded text-[11px]">🔻 ${rm.change_percent}%</span>`
                : `<span class="text-slate-400 font-medium text-[11px]">➖ คงที่</span>`;

        const useCustom = rm.use_custom === true;
        const customVal = rm.custom_price_display !== undefined ? rm.custom_price_display : rm.display_price;
        const effectiveDisplay = useCustom ? customVal : rm.display_price;

        html += `
            <tr class="hover:bg-slate-50 transition-colors">
                <td class="p-3 font-bold text-slate-800 text-sm whitespace-nowrap">
                    ${rm.name}
                </td>
                <td class="p-3 text-slate-500 whitespace-nowrap">${rm.category}</td>
                <td class="p-3 text-right font-black text-slate-800 whitespace-nowrap">
                    ${rm.display_price}.- <span class="text-[10px] font-normal text-slate-500">/ ${rm.display_unit}</span>
                </td>
                <td class="p-3 text-center whitespace-nowrap">
                    ${changeBadge}
                </td>
                <td class="p-3 text-right whitespace-nowrap">
                    <input type="number" step="any" value="${customVal}" 
                        onchange="updateCustomPrice('${rm.id}', this.value)"
                        class="w-24 text-right p-1.5 text-xs font-bold border border-slate-300 rounded-lg focus:border-blue-500 focus:outline-none bg-slate-50" />
                </td>
                <td class="p-3 text-center whitespace-nowrap">
                    <div class="inline-flex rounded-lg border border-slate-200 p-0.5 bg-slate-100 text-[10px]">
                        <button onclick="togglePriceMode('${rm.id}', false)" class="px-2 py-1 rounded-md font-bold transition-all ${
                            !useCustom ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-800'
                        }">
                            ตลาด
                        </button>
                        <button onclick="togglePriceMode('${rm.id}', true)" class="px-2 py-1 rounded-md font-bold transition-all ${
                            useCustom ? 'bg-amber-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-800'
                        }">
                            ตั้งเอง
                        </button>
                    </div>
                </td>
                <td class="p-3 text-right font-black text-blue-700 whitespace-nowrap">
                    ${effectiveDisplay}.- <span class="text-[10px] font-normal text-slate-500">/ ${rm.display_unit}</span>
                </td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = html;
}

window.togglePriceMode = function(rmId, useCustom) {
    const rm = appData.raw_materials[rmId];
    if (!rm) return;
    rm.use_custom = useCustom;
    recalculateAllDishes();
    saveData(true);
    renderAll();

    // Broadcast to team devices
    broadcastMessage({
        type: 'UPDATE_RM_PRICE',
        rmId: rm.id,
        useCustom: useCustom,
        customVal: rm.custom_price_display || rm.display_price,
        effectivePrice: rm.custom_price || rm.market_price
    });

    // Save to 24/7 cloud broker
    publishCloudDelta();

    showToast(`เปลี่ยนโหมดราคา "${rm.name}" เป็น ${useCustom ? 'ราคาตั้งเอง' : 'ราคาตลาดอัตโนมัติ'}`);
};

window.updateCustomPrice = function(rmId, val) {
    const rm = appData.raw_materials[rmId];
    if (!rm) return;
    const num = parseFloat(val);
    if (isNaN(num) || num <= 0) return;

    rm.custom_price_display = num;
    if (rm.unit === 'g') {
        rm.custom_price = Math.round((num / 1000) * 10000) / 10000;
    } else if (rm.unit === 'ml') {
        rm.custom_price = Math.round((num / 1000) * 10000) / 10000;
    } else {
        rm.custom_price = num;
    }
    rm.use_custom = true;

    recalculateAllDishes();
    saveData(true);
    renderAll();

    // Broadcast update to team
    broadcastMessage({
        type: 'UPDATE_RM_PRICE',
        rmId: rm.id,
        useCustom: true,
        customVal: num,
        effectivePrice: rm.custom_price
    });

    // Save to 24/7 cloud broker
    publishCloudDelta();

    showToast(`อัปเดตราคาตั้งเองสำหรับ "${rm.name}" เป็น ${num} บาทแล้ว`);
};

// -------------------------------------------------------------------------
// TAB 4: Reference Gallery (19 Images from ref/)
// -------------------------------------------------------------------------
function renderReferenceGallery(container) {
    let html = `
        <div class="bg-white rounded-2xl border border-slate-200 shadow-xs p-4 md:p-5 mb-5">
            <h2 class="text-lg md:text-xl font-bold text-slate-800 flex items-center gap-2">
                🖼️ แกลเลอรีรูปภาพเมนูอ้างอิงสำหรับการโฆษณา (19 รูป)
            </h2>
            <p class="text-xs text-slate-500 mt-0.5">
                รูปภาพทั้งหมดจากโฟลเดอร์ ref ใช้เป็นแนวทางโฆษณา โดยระบบได้วิเคราะห์ถอดสเปกวัตถุดิบและ portion control ทุกเมนู
            </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-5">
    `;

    for (let i = 1; i <= 19; i++) {
        const dishesInRef = appData.dishes.filter(d => d.image_ref === i);
        const imgSrc = `./ref/menu_${i}.jpg`;

        html += `
            <div class="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden flex flex-col justify-between">
                <div class="relative bg-slate-100 aspect-3/4 overflow-hidden border-b border-slate-200">
                    <img src="${imgSrc}" alt="Menu Sheet ${i}" class="w-full h-full object-cover object-top hover:scale-105 transition-transform duration-300"
                        onerror="this.src='https://placehold.co/400x500?text=Menu+Image+${i}';" />
                    <span class="absolute top-2 left-2 bg-black/70 text-white font-bold text-xs px-2.5 py-1 rounded-md backdrop-blur-xs">
                        ไฟล์รูปที่ ${i}
                    </span>
                </div>
                <div class="p-3 bg-slate-50">
                    <h4 class="text-xs font-bold text-slate-800 mb-1">เมนูที่วิเคราะห์ในรูปนี้ (${dishesInRef.length} เมนู):</h4>
                    <div class="text-[11px] text-slate-600 line-clamp-3">
                        ${dishesInRef.map(d => `<span class="inline-block bg-white px-1.5 py-0.5 rounded border border-slate-200 mr-1 mb-1 font-medium">${d.name}</span>`).join('') || '<span class="text-slate-400">ภาพหน้าปก / เครื่องดื่ม</span>'}
                    </div>
                </div>
            </div>
        `;
    }

    html += `</div>`;
    container.innerHTML = html;
}

// -------------------------------------------------------------------------
// SHARE & QR CODE MODAL FOR MOBILE TEAMS
// -------------------------------------------------------------------------
function openShareModal() {
    const currentUrl = window.location.href;

    const modalHtml = `
        <div id="share-modal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
            <div class="bg-white rounded-3xl max-w-md w-full shadow-2xl p-6 text-center animate-in zoom-in-95 duration-200">
                <div class="w-12 h-12 rounded-2xl bg-blue-100 text-blue-600 flex items-center justify-center mx-auto text-2xl mb-3">
                    📱
                </div>
                <h3 class="text-lg font-bold text-slate-800">แชร์ให้ทีมงานใช้งานบนมือถือ</h3>
                <p class="text-xs text-slate-500 mt-1">
                    สแกน QR Code หรือคัดลอกลิงก์ส่งเข้า LINE เพื่อให้ทีมงานร่วมตรวจสอบและแก้ไขราคาแบบเรียลไทม์
                </p>

                <div class="my-5 p-4 bg-slate-50 border border-slate-200 rounded-2xl flex flex-col items-center justify-center">
                    <div id="qrcode-container" class="bg-white p-3 rounded-xl shadow-xs"></div>
                    <span class="text-[11px] text-slate-400 mt-2">ห้องเชื่อมต่อสด: <strong class="text-blue-600">${syncRoomCode}</strong></span>
                </div>

                <div class="space-y-2">
                    <div class="flex items-center gap-1.5 p-2 bg-slate-100 rounded-xl border border-slate-200 text-xs">
                        <input type="text" id="share-url-input" value="${currentUrl}" readonly class="w-full bg-transparent border-none text-slate-700 font-mono text-[11px] focus:outline-none" />
                        <button onclick="copyShareUrl()" class="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold shrink-0">
                            คัดลอก
                        </button>
                    </div>
                    <button onclick="closeShareModal()" class="w-full py-2.5 text-xs font-bold text-slate-500 hover:text-slate-800">
                        ปิดหน้าต่าง
                    </button>
                </div>
            </div>
        </div>
    `;

    const existing = document.getElementById('share-modal');
    if (existing) existing.remove();
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // Generate QR Code
    if (typeof QRCode !== 'undefined') {
        new QRCode(document.getElementById('qrcode-container'), {
            text: currentUrl,
            width: 160,
            height: 160,
            colorDark: '#0f172a',
            colorLight: '#ffffff',
            correctLevel: QRCode.CorrectLevel.M
        });
    } else {
        document.getElementById('qrcode-container').innerHTML = `<p class="text-xs text-slate-400 p-4">คัดลอกลิงก์เพื่อแชร์</p>`;
    }
}

window.closeShareModal = function() {
    const modal = document.getElementById('share-modal');
    if (modal) modal.remove();
};

window.copyShareUrl = function() {
    const input = document.getElementById('share-url-input');
    if (!input) return;
    input.select();
    document.execCommand('copy');
    showToast('📋 คัดลอกลิงก์แล้ว! ส่งให้ทีมงานเปิดบนมือถือได้เลย');
};

// Export JSON
function exportJSON() {
    if (!appData) return;
    const blob = new Blob([JSON.stringify(appData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `saensuk_food_cost_backup_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('ดาวน์โหลดไฟล์สำรองข้อมูล JSON แล้ว');
}
