# -*- coding: utf-8 -*-
"""
Food Cost & Kitchen Prep Data Builder for ครัวแสนสุข
Generates data.json with full menu items, portion specs, market prices, and cost calculations.
"""
import json
import os
import datetime

# 1. Raw Materials Database (Baseline Market Price - Wholesale / Makro / Chonburi Seafood Market)
raw_materials = {
    # Seafood
    "RM_SHRIMP_WHITE": {
        "id": "RM_SHRIMP_WHITE",
        "name": "กุ้งขาวสด (40-50 ตัว/กก.)",
        "category": "อาหารทะเลสด",
        "unit": "g",
        "market_price_per_kg": 240.0,
        "market_price": 0.24, # THB/g
        "display_unit": "กก.",
        "display_price": 240,
        "previous_price": 230,
        "change_percent": 4.3,
        "last_updated": "2026-10-10"
    },
    "RM_SHRIMP_RIVER": {
        "id": "RM_SHRIMP_RIVER",
        "name": "กุ้งก้ามกราม/กุ้งแม่น้ำ (12-15 ตัว/กก.)",
        "category": "อาหารทะเลสด",
        "unit": "g",
        "market_price_per_kg": 260.0,
        "market_price": 0.26,
        "display_unit": "กก.",
        "display_price": 260,
        "previous_price": 260,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },
    "RM_SQUID_BANANA": {
        "id": "RM_SQUID_BANANA",
        "name": "ปลาหมึกกล้วยสด",
        "category": "อาหารทะเลสด",
        "unit": "g",
        "market_price_per_kg": 220.0,
        "market_price": 0.22,
        "display_unit": "กก.",
        "display_price": 220,
        "previous_price": 230,
        "change_percent": -4.3,
        "last_updated": "2026-10-10"
    },
    "RM_SQUID_ROE": {
        "id": "RM_SQUID_ROE",
        "name": "ปลาหมึกไข่สดคัดไซส์",
        "category": "อาหารทะเลสด",
        "unit": "g",
        "market_price_per_kg": 250.0,
        "market_price": 0.25,
        "display_unit": "กก.",
        "display_price": 250,
        "previous_price": 240,
        "change_percent": 4.2,
        "last_updated": "2026-10-10"
    },
    "RM_SQUID_BABY": {
        "id": "RM_SQUID_BABY",
        "name": "หมึกกระตอยสด",
        "category": "อาหารทะเลสด",
        "unit": "g",
        "market_price_per_kg": 240.0,
        "market_price": 0.24,
        "display_unit": "กก.",
        "display_price": 240,
        "previous_price": 240,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },
    "RM_SQUID_EGG": {
        "id": "RM_SQUID_EGG",
        "name": "ไข่หมึกแท้",
        "category": "อาหารทะเลสด",
        "unit": "g",
        "market_price_per_kg": 280.0,
        "market_price": 0.28,
        "display_unit": "กก.",
        "display_price": 280,
        "previous_price": 270,
        "change_percent": 3.7,
        "last_updated": "2026-10-10"
    },
    "RM_SEABASS": {
        "id": "RM_SEABASS",
        "name": "ปลากระพงขาวสด (ไซส์ 750-800g)",
        "category": "อาหารทะเลสด",
        "unit": "ตัว",
        "market_price_per_kg": 145.0,
        "market_price": 110.0, # ตัวละ 110 บาท
        "display_unit": "ตัว (~750g)",
        "display_price": 110,
        "previous_price": 115,
        "change_percent": -4.3,
        "last_updated": "2026-10-10"
    },
    "RM_SEABASS_FILLET": {
        "id": "RM_SEABASS_FILLET",
        "name": "เนื้อปลากระพงแล่ชิ้น",
        "category": "อาหารทะเลสด",
        "unit": "g",
        "market_price_per_kg": 230.0,
        "market_price": 0.23,
        "display_unit": "กก.",
        "display_price": 230,
        "previous_price": 230,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },
    "RM_CRAB_BLUE": {
        "id": "RM_CRAB_BLUE",
        "name": "ปูม้าสด (4-5 ตัว/กก.)",
        "category": "อาหารทะเลสด",
        "unit": "g",
        "market_price_per_kg": 240.0,
        "market_price": 0.24,
        "display_unit": "กก.",
        "display_price": 240,
        "previous_price": 250,
        "change_percent": -4.0,
        "last_updated": "2026-10-10"
    },
    "RM_CRAB_MEAT": {
        "id": "RM_CRAB_MEAT",
        "name": "เนื้อปูก้อน/ก้ามแกะสุกพร้อมทาน",
        "category": "อาหารทะเลสด",
        "unit": "g",
        "market_price_per_kg": 800.0,
        "market_price": 0.80,
        "display_unit": "กก.",
        "display_price": 800,
        "previous_price": 780,
        "change_percent": 2.6,
        "last_updated": "2026-10-10"
    },
    "RM_CRAB_EGG_ROE": {
        "id": "RM_CRAB_EGG_ROE",
        "name": "ปูทะเลไข่ดองคัดไซส์ (200g/ตัว)",
        "category": "อาหารทะเลสด",
        "unit": "ตัว",
        "market_price_per_kg": 420.0,
        "market_price": 84.0,
        "display_unit": "ตัว (200g)",
        "display_price": 84,
        "previous_price": 80,
        "change_percent": 5.0,
        "last_updated": "2026-10-10"
    },
    "RM_CATFISH_ROE": {
        "id": "RM_CATFISH_ROE",
        "name": "ไข่ปลาเรียวเซียวเม็ดสวย",
        "category": "อาหารทะเลสด",
        "unit": "g",
        "market_price_per_kg": 550.0,
        "market_price": 0.55,
        "display_unit": "กก.",
        "display_price": 550,
        "previous_price": 530,
        "change_percent": 3.8,
        "last_updated": "2026-10-10"
    },
    "RM_OYSTER": {
        "id": "RM_OYSTER",
        "name": "หอยนางรมสดคัดพิเศษ",
        "category": "อาหารทะเลสด",
        "unit": "g",
        "market_price_per_kg": 250.0,
        "market_price": 0.25,
        "display_unit": "กก.",
        "display_price": 250,
        "previous_price": 250,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },
    "RM_COCKLE": {
        "id": "RM_COCKLE",
        "name": "หอยแครงสด (ไซส์กลาง)",
        "category": "อาหารทะเลสด",
        "unit": "g",
        "market_price_per_kg": 130.0,
        "market_price": 0.13,
        "display_unit": "กก.",
        "display_price": 130,
        "previous_price": 120,
        "change_percent": 8.3,
        "last_updated": "2026-10-10"
    },
    "RM_CLAM": {
        "id": "RM_CLAM",
        "name": "หอยลายสดคัดไซส์",
        "category": "อาหารทะเลสด",
        "unit": "g",
        "market_price_per_kg": 90.0,
        "market_price": 0.09,
        "display_unit": "กก.",
        "display_price": 90,
        "previous_price": 90,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },
    "RM_HORSESHOE_CRAB_EGG": {
        "id": "RM_HORSESHOE_CRAB_EGG",
        "name": "ไข่แมงดาทะเลสุก",
        "category": "อาหารทะเลสด",
        "unit": "g",
        "market_price_per_kg": 320.0,
        "market_price": 0.32,
        "display_unit": "กก.",
        "display_price": 320,
        "previous_price": 320,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },
    "RM_SAND_FISH": {
        "id": "RM_SAND_FISH",
        "name": "ปลาเห็ดโคนสดล้างแต่ง",
        "category": "อาหารทะเลสด",
        "unit": "g",
        "market_price_per_kg": 200.0,
        "market_price": 0.20,
        "display_unit": "กก.",
        "display_price": 200,
        "previous_price": 190,
        "change_percent": 5.3,
        "last_updated": "2026-10-10"
    },
    "RM_MACKEREL_STEAK": {
        "id": "RM_MACKEREL_STEAK",
        "name": "ปลาอินทรีสเต็กสด",
        "category": "อาหารทะเลสด",
        "unit": "g",
        "market_price_per_kg": 320.0,
        "market_price": 0.32,
        "display_unit": "กก.",
        "display_price": 320,
        "previous_price": 330,
        "change_percent": -3.0,
        "last_updated": "2026-10-10"
    },
    "RM_GOURAMI": {
        "id": "RM_GOURAMI",
        "name": "ปลาสลิดแดดเดียวบางบ่อ",
        "category": "อาหารทะเลสด",
        "unit": "g",
        "market_price_per_kg": 200.0,
        "market_price": 0.20,
        "display_unit": "กก.",
        "display_price": 200,
        "previous_price": 200,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },
    "RM_MUSSEL": {
        "id": "RM_MUSSEL",
        "name": "หอยแมลงภู่สด/ชิลี",
        "category": "อาหารทะเลสด",
        "unit": "g",
        "market_price_per_kg": 100.0,
        "market_price": 0.10,
        "display_unit": "กก.",
        "display_price": 100,
        "previous_price": 100,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },

    # Pork & Poultry
    "RM_PORK_CRISPY": {
        "id": "RM_PORK_CRISPY",
        "name": "หมูกรอบสำเร็จรูปเกรดพรีเมียม",
        "category": "เนื้อสัตว์",
        "unit": "g",
        "market_price_per_kg": 300.0,
        "market_price": 0.30,
        "display_unit": "กก.",
        "display_price": 300,
        "previous_price": 290,
        "change_percent": 3.4,
        "last_updated": "2026-10-10"
    },
    "RM_PORK_BELLY": {
        "id": "RM_PORK_BELLY",
        "name": "หมูสามชั้นสดสไลด์",
        "category": "เนื้อสัตว์",
        "unit": "g",
        "market_price_per_kg": 180.0,
        "market_price": 0.18,
        "display_unit": "กก.",
        "display_price": 180,
        "previous_price": 175,
        "change_percent": 2.9,
        "last_updated": "2026-10-10"
    },
    "RM_PORK_MINCED": {
        "id": "RM_PORK_MINCED",
        "name": "หมูบด/หมูสับหมักนุ่ม",
        "category": "เนื้อสัตว์",
        "unit": "g",
        "market_price_per_kg": 150.0,
        "market_price": 0.15,
        "display_unit": "กก.",
        "display_price": 150,
        "previous_price": 150,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },
    "RM_PORK_SLICED": {
        "id": "RM_PORK_SLICED",
        "name": "เนื้อหมูสันนอกหมักนุ่ม",
        "category": "เนื้อสัตว์",
        "unit": "g",
        "market_price_per_kg": 150.0,
        "market_price": 0.15,
        "display_unit": "กก.",
        "display_price": 150,
        "previous_price": 150,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },
    "RM_PORK_CARTILAGE": {
        "id": "RM_PORK_CARTILAGE",
        "name": "ซี่โครงกระดูกอ่อนหมู",
        "category": "เนื้อสัตว์",
        "unit": "g",
        "market_price_per_kg": 170.0,
        "market_price": 0.17,
        "display_unit": "กก.",
        "display_price": 170,
        "previous_price": 165,
        "change_percent": 3.0,
        "last_updated": "2026-10-10"
    },
    "RM_CHICKEN_MEAT": {
        "id": "RM_CHICKEN_MEAT",
        "name": "เนื้อสะโพก/อกไก่หั่นชิ้น",
        "category": "เนื้อสัตว์",
        "unit": "g",
        "market_price_per_kg": 95.0,
        "market_price": 0.095,
        "display_unit": "กก.",
        "display_price": 95,
        "previous_price": 95,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },
    "RM_CHICKEN_WINGS": {
        "id": "RM_CHICKEN_WINGS",
        "name": "ปีกไก่กลาง",
        "category": "เนื้อสัตว์",
        "unit": "g",
        "market_price_per_kg": 120.0,
        "market_price": 0.12,
        "display_unit": "กก.",
        "display_price": 120,
        "previous_price": 115,
        "change_percent": 4.3,
        "last_updated": "2026-10-10"
    },
    "RM_CHICKEN_TENDON": {
        "id": "RM_CHICKEN_TENDON",
        "name": "เอ็นข้อไก่สด",
        "category": "เนื้อสัตว์",
        "unit": "g",
        "market_price_per_kg": 140.0,
        "market_price": 0.14,
        "display_unit": "กก.",
        "display_price": 140,
        "previous_price": 140,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },
    "RM_CHICKEN_FEET": {
        "id": "RM_CHICKEN_FEET",
        "name": "ตีนไก่สดคัดตัดเล็บ",
        "category": "เนื้อสัตว์",
        "unit": "g",
        "market_price_per_kg": 90.0,
        "market_price": 0.09,
        "display_unit": "กก.",
        "display_price": 90,
        "previous_price": 85,
        "change_percent": 5.9,
        "last_updated": "2026-10-10"
    },

    # Eggs & Tofu
    "RM_EGG_FRESH": {
        "id": "RM_EGG_FRESH",
        "name": "ไข่ไก่สด เบอร์ 2",
        "category": "ไข่และเต้าหู้",
        "unit": "ฟอง",
        "market_price_per_kg": 0,
        "market_price": 4.50, # ฟองละ 4.50 บาท
        "display_unit": "ฟอง",
        "display_price": 4.50,
        "previous_price": 4.20,
        "change_percent": 7.1,
        "last_updated": "2026-10-10"
    },
    "RM_EGG_CENTURY": {
        "id": "RM_EGG_CENTURY",
        "name": "ไข่เยี่ยวม้า",
        "category": "ไข่และเต้าหู้",
        "unit": "ฟอง",
        "market_price_per_kg": 0,
        "market_price": 11.0,
        "display_unit": "ฟอง",
        "display_price": 11.0,
        "previous_price": 11.0,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },
    "RM_TOFU_EGG": {
        "id": "RM_TOFU_EGG",
        "name": "เต้าหู้ไข่ไก่หลอด",
        "category": "ไข่และเต้าหู้",
        "unit": "หลอด",
        "market_price_per_kg": 0,
        "market_price": 10.0,
        "display_unit": "หลอด",
        "display_price": 10.0,
        "previous_price": 10.0,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },

    # Rice, Noodles & Dry Goods
    "RM_JASMINE_RICE": {
        "id": "RM_JASMINE_RICE",
        "name": "ข้าวสวยหอมมะลิสุกผึ่งแห้ง",
        "category": "ข้าวและเส้น",
        "unit": "g",
        "market_price_per_kg": 30.0,
        "market_price": 0.03,
        "display_unit": "กก.",
        "display_price": 30,
        "previous_price": 30,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },
    "RM_GLASS_NOODLES": {
        "id": "RM_GLASS_NOODLES",
        "name": "วุ้นเส้นสด/แช่น้ำพร้อมปรุง",
        "category": "ข้าวและเส้น",
        "unit": "g",
        "market_price_per_kg": 70.0,
        "market_price": 0.07,
        "display_unit": "กก.",
        "display_price": 70,
        "previous_price": 70,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },
    "RM_FLAT_NOODLES": {
        "id": "RM_FLAT_NOODLES",
        "name": "ก๋วยเตี๋ยวเส้นใหญ่สด",
        "category": "ข้าวและเส้น",
        "unit": "g",
        "market_price_per_kg": 28.0,
        "market_price": 0.028,
        "display_unit": "กก.",
        "display_price": 28,
        "previous_price": 28,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },
    "RM_INSTANT_NOODLES": {
        "id": "RM_INSTANT_NOODLES",
        "name": "บะหมี่กึ่งสำเร็จรูป (มาม่า)",
        "category": "ข้าวและเส้น",
        "unit": "ซอง",
        "market_price_per_kg": 0,
        "market_price": 7.0,
        "display_unit": "ซอง",
        "display_price": 7.0,
        "previous_price": 7.0,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },
    "RM_CASHEW_NUT": {
        "id": "RM_CASHEW_NUT",
        "name": "เม็ดมะม่วงหิมพานต์ทอดกรอบ",
        "category": "ของแห้ง",
        "unit": "g",
        "market_price_per_kg": 320.0,
        "market_price": 0.32,
        "display_unit": "กก.",
        "display_price": 320,
        "previous_price": 310,
        "change_percent": 3.2,
        "last_updated": "2026-10-10"
    },
    "RM_CHINESE_OLIVE": {
        "id": "RM_CHINESE_OLIVE",
        "name": "ลูกหนำเลี้ยบดองสับ",
        "category": "ของแห้ง",
        "unit": "g",
        "market_price_per_kg": 240.0,
        "market_price": 0.24,
        "display_unit": "กก.",
        "display_price": 240,
        "previous_price": 240,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },
    "RM_PICKLED_RADISH": {
        "id": "RM_PICKLED_RADISH",
        "name": "ไชโป๊หวานเส้นคัดล้างเค็ม",
        "category": "ของแห้ง",
        "unit": "g",
        "market_price_per_kg": 80.0,
        "market_price": 0.08,
        "display_unit": "กก.",
        "display_price": 80,
        "previous_price": 80,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },

    # Vegetables & Herbs
    "RM_LIME_JUICE": {
        "id": "RM_LIME_JUICE",
        "name": "มะนาวแป้นคั้นสดแท้ 100%",
        "category": "ผักและสมุนไพร",
        "unit": "ml",
        "market_price_per_kg": 200.0,
        "market_price": 0.20, # THB/ml
        "display_unit": "ลิตร",
        "display_price": 200,
        "previous_price": 180,
        "change_percent": 11.1,
        "last_updated": "2026-10-10"
    },
    "RM_GARLIC_CRISPY": {
        "id": "RM_GARLIC_CRISPY",
        "name": "กระเทียมไทยสับเจียวเหลืองกรอบ",
        "category": "ผักและสมุนไพร",
        "unit": "g",
        "market_price_per_kg": 120.0,
        "market_price": 0.12,
        "display_unit": "กก.",
        "display_price": 120,
        "previous_price": 120,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },
    "RM_CABBAGE": {
        "id": "RM_CABBAGE",
        "name": "กะหล่ำปลีหวานสด",
        "category": "ผักและสมุนไพร",
        "unit": "g",
        "market_price_per_kg": 35.0,
        "market_price": 0.035,
        "display_unit": "กก.",
        "display_price": 35,
        "previous_price": 30,
        "change_percent": 16.7,
        "last_updated": "2026-10-10"
    },
    "RM_KALE": {
        "id": "RM_KALE",
        "name": "คะน้าฮ่องกง/คะน้ายอดอ่อน",
        "category": "ผักและสมุนไพร",
        "unit": "g",
        "market_price_per_kg": 50.0,
        "market_price": 0.05,
        "display_unit": "กก.",
        "display_price": 50,
        "previous_price": 50,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },
    "RM_BRUSSELS": {
        "id": "RM_BRUSSELS",
        "name": "ผักแขนงกะหล่ำสด",
        "category": "ผักและสมุนไพร",
        "unit": "g",
        "market_price_per_kg": 60.0,
        "market_price": 0.06,
        "display_unit": "กก.",
        "display_price": 60,
        "previous_price": 55,
        "change_percent": 9.1,
        "last_updated": "2026-10-10"
    },
    "RM_WATER_MIMOSA": {
        "id": "RM_WATER_MIMOSA",
        "name": "ผักกระเฉดยอดอ่อนคัดข้อ",
        "category": "ผักและสมุนไพร",
        "unit": "g",
        "market_price_per_kg": 80.0,
        "market_price": 0.08,
        "display_unit": "กก.",
        "display_price": 80,
        "previous_price": 80,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },
    "RM_MORNING_GLORY": {
        "id": "RM_MORNING_GLORY",
        "name": "ผักบุ้งจีนคัดยอด",
        "category": "ผักและสมุนไพร",
        "unit": "g",
        "market_price_per_kg": 30.0,
        "market_price": 0.03,
        "display_unit": "กก.",
        "display_price": 30,
        "previous_price": 30,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },
    "RM_MIXED_VEG": {
        "id": "RM_MIXED_VEG",
        "name": "ผักรวมสด (บรอกโคลี แครอท ข้าวโพดอ่อน)",
        "category": "ผักและสมุนไพร",
        "unit": "g",
        "market_price_per_kg": 70.0,
        "market_price": 0.07,
        "display_unit": "กก.",
        "display_price": 70,
        "previous_price": 70,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },
    "RM_MANGO_SHREDDED": {
        "id": "RM_MANGO_SHREDDED",
        "name": "มะม่วงเปรี้ยวสับเส้นกรอบ",
        "category": "ผักและสมุนไพร",
        "unit": "g",
        "market_price_per_kg": 60.0,
        "market_price": 0.06,
        "display_unit": "กก.",
        "display_price": 60,
        "previous_price": 50,
        "change_percent": 20.0,
        "last_updated": "2026-10-10"
    },
    "RM_CHA_OM_EGG": {
        "id": "RM_CHA_OM_EGG",
        "name": "ไข่เจียวชะอมทอดหั่นเต๋า (ทำจากชะอม+ไข่)",
        "category": "ผักและสมุนไพร",
        "unit": "g",
        "market_price_per_kg": 150.0,
        "market_price": 0.15,
        "display_unit": "กก.",
        "display_price": 150,
        "previous_price": 140,
        "change_percent": 7.1,
        "last_updated": "2026-10-10"
    },
    "RM_MUSHROOM_STRAW": {
        "id": "RM_MUSHROOM_STRAW",
        "name": "เห็ดฟางสด/เห็ดออรินจิ",
        "category": "ผักและสมุนไพร",
        "unit": "g",
        "market_price_per_kg": 100.0,
        "market_price": 0.10,
        "display_unit": "กก.",
        "display_price": 100,
        "previous_price": 100,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },

    # Prepared Bases / Special Sauces (Major cost drivers)
    "RM_SAUCE_SEAFOOD": {
        "id": "RM_SAUCE_SEAFOOD",
        "name": "น้ำจิ้มซีฟู้ดมะนาวสดแท้สูตรแสนสุข",
        "category": "ซอสและน้ำแกง",
        "unit": "ml",
        "market_price_per_kg": 130.0,
        "market_price": 0.13,
        "display_unit": "ลิตร",
        "display_price": 130,
        "previous_price": 125,
        "change_percent": 4.0,
        "last_updated": "2026-10-10"
    },
    "RM_SAUCE_YUM": {
        "id": "RM_SAUCE_YUM",
        "name": "น้ำยำสามรสมะนาวสดเข้มข้น",
        "category": "ซอสและน้ำแกง",
        "unit": "ml",
        "market_price_per_kg": 140.0,
        "market_price": 0.14,
        "display_unit": "ลิตร",
        "display_price": 140,
        "previous_price": 135,
        "change_percent": 3.7,
        "last_updated": "2026-10-10"
    },
    "RM_CURRY_SOUP_BASE": {
        "id": "RM_CURRY_SOUP_BASE",
        "name": "น้ำแกงส้มสูตรเข้มข้นเนื้อปลาโขลก",
        "category": "ซอสและน้ำแกง",
        "unit": "ml",
        "market_price_per_kg": 40.0,
        "market_price": 0.04,
        "display_unit": "ลิตร",
        "display_price": 40,
        "previous_price": 40,
        "change_percent": 0.0,
        "last_updated": "2026-10-10"
    },
    "RM_CHILI_PASTE_EGG_BASE": {
        "id": "RM_CHILI_PASTE_EGG_BASE",
        "name": "เบสผัดผงกะหรี่ (ไข่ไก่ 2 ฟอง+นมข้นจืด+พริกเผา)",
        "category": "ซอสและน้ำแกง",
        "unit": "g",
        "market_price_per_kg": 150.0,
        "market_price": 0.15,
        "display_unit": "กก.",
        "display_price": 150,
        "previous_price": 145,
        "change_percent": 3.4,
        "last_updated": "2026-10-10"
    },
    "RM_FRYING_OIL_PORTION": {
        "id": "RM_FRYING_OIL_PORTION",
        "name": "น้ำมันพืชทอดฟูกรอบ (คำนวณการดูดซับ)",
        "category": "ซอสและน้ำแกง",
        "unit": "ml",
        "market_price_per_kg": 65.0,
        "market_price": 0.065,
        "display_unit": "ลิตร",
        "display_price": 65,
        "previous_price": 62,
        "change_percent": 4.8,
        "last_updated": "2026-10-10"
    }
}

# 2. Categories
categories = [
    {"id": "cat_recom", "name": "เมนูแนะนำยอดฮิต (Recommended)", "image_refs": [1, 2]},
    {"id": "cat_soup", "name": "เมนูต้ม / แกง (Soup & Curry)", "image_refs": [3]},
    {"id": "cat_omelet", "name": "เมนูไข่เจียว (Omelet)", "image_refs": [4]},
    {"id": "cat_fresh_yum", "name": "เมนูยำทะเลสด (Fresh Seafood Salad)", "image_refs": [5]},
    {"id": "cat_thai_yum", "name": "เมนูยำทะเลไทยๆ (Thai Seafood Salad)", "image_refs": [6]},
    {"id": "cat_bbq", "name": "อาหารทะเลเผา / ย่าง / นึ่ง (BBQ Seafood)", "image_refs": [7]},
    {"id": "cat_fried", "name": "เมนูทอด (Deep Fried)", "image_refs": [8]},
    {"id": "cat_stir_fry", "name": "เมนูผัดรสเด็ด (Stir-Fried)", "image_refs": [9, 10, 11]},
    {"id": "cat_seabass", "name": "เมนูปลากระพง & ปลาอื่นๆ (Sea Bass & Fish)", "image_refs": [14, 15]},
    {"id": "cat_fried_rice", "name": "เมนูข้าวผัดกระทะทอง (Fried Rice)", "image_refs": [13]},
    {"id": "cat_sets", "name": "เซ็ตเมนูสุดคุ้ม (Value Sets 1-4)", "image_refs": [16, 17]},
    {"id": "cat_alacarte", "name": "อาหารตามสั่งจานเดี่ยว (A La Carte)", "image_refs": [18]},
    {"id": "cat_drinks", "name": "เครื่องดื่มและของหวาน (Beverages)", "image_refs": [12]}
]

# 3. Complete Dishes List with Primary & Secondary Ingredients (strictly 4-5 items per dish for kitchen prep board)
# Each dish controls food cost strictly around 35% - 40% (Total Food Cost <= 40%, Gross Profit >= 60%)

dishes_data = [
    # IMAGE 1: เมนูแนะนำ
    {
        "id": "D01",
        "name": "หมึกไข่นึ่งมะนาว",
        "category": "cat_recom",
        "image_ref": 1,
        "price": 300,
        "target_cost_pct": 36.5,
        "items": [
            {"rm_id": "RM_SQUID_ROE", "portion": 350, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมึกไข่ตัวโต 2-3 ตัว ล้างสะอาดบั้งถี่สวยงาม"},
            {"rm_id": "RM_LIME_JUICE", "portion": 45, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมะนาวแท้คั้นสด รสเปรี้ยวจัดจ้าน"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 30, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กระเทียมจีนสับหยาบโรยพูน"},
            {"rm_id": "RM_SAUCE_SEAFOOD", "portion": 50, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำยำนึ่งมะนาวสูตรเข้มข้นพร้อมพริกสดขี้หนูสวน"}
        ]
    },
    {
        "id": "D02",
        "name": "แกงส้มไข่ปลาเรียวเซียว",
        "category": "cat_recom",
        "image_ref": 1,
        "price": 350,
        "target_cost_pct": 35.8,
        "items": [
            {"rm_id": "RM_CATFISH_ROE", "portion": 180, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ไข่ปลาเรียวเซียวคัดเม็ดโตสดเต่งตึง ลวกสะดุ้งน้ำเดือดพักไว้"},
            {"rm_id": "RM_CURRY_SOUP_BASE", "portion": 450, "unit": "ml", "action": "ตวงปริมาตร", "type": "primary", "note": "น้ำแกงส้มสูตรปลาโขลกเข้มข้นรสเปรี้ยวอมหวาน"},
            {"rm_id": "RM_CABBAGE", "portion": 150, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ยอดมะพร้าวอ่อนหรือผักรวมแกงส้มหั่นพอดีคำ"}
        ]
    },
    {
        "id": "D03",
        "name": "ทะเลกระทะร้อน",
        "category": "cat_recom",
        "image_ref": 1,
        "price": 250,
        "target_cost_pct": 35.5,
        "items": [
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 100, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวแกะเปลือกผ่าหลังไว้หาง 4 ตัว"},
            {"rm_id": "RM_SQUID_BANANA", "portion": 100, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ปลาหมึกกล้วยบั้งตารางหั่นชิ้นพอดีคำ"},
            {"rm_id": "RM_MUSSEL", "portion": 80, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หอยแมลงภู่ชิลี/หอยลายแกะฝา"},
            {"rm_id": "RM_EGG_FRESH", "portion": 1, "unit": "ฟอง", "action": "นับชิ้น", "type": "secondary", "note": "ไข่ไก่สด 1 ฟอง ตอกลงกระทะร้อนตอนเสิร์ฟฉ่า"}
        ]
    },
    {
        "id": "D04",
        "name": "หมึกผัดไข่หมึก",
        "category": "cat_recom",
        "image_ref": 1,
        "price": 200,
        "target_cost_pct": 35.0,
        "items": [
            {"rm_id": "RM_SQUID_EGG", "portion": 120, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ไข่หมึกแท้ลวกสะดุ้งน้ำมันพอสุกเด้ง"},
            {"rm_id": "RM_SQUID_BANANA", "portion": 120, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "เนื้อหมึกกล้วยสดบั้งชิ้น"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 25, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กระเทียมสับผัดหอมพริกสด"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 30, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันผัดคั่วแห้งหอมกระทะ"}
        ]
    },
    {
        "id": "D05",
        "name": "กุ้งอบวุ้นเส้น",
        "category": "cat_recom",
        "image_ref": 1,
        "price": 250,
        "target_cost_pct": 35.8,
        "items": [
            {"rm_id": "RM_SHRIMP_RIVER", "portion": 200, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งแม่น้ำหรือกุ้งขาวตัวโต 4-5 ตัว วางเรียงบนหม้อ"},
            {"rm_id": "RM_GLASS_NOODLES", "portion": 130, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "วุ้นเส้นแช่น้ำคลุกน้ำซอสปรุงรสเข้มข้น"},
            {"rm_id": "RM_PORK_BELLY", "portion": 40, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "หมูสามชั้นสไลด์รองก้นหม้อดินกันไหม้และดึงความหอม"},
            {"rm_id": "RM_SAUCE_SEAFOOD", "portion": 40, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำจิ้มซีฟู้ดมะนาวสดเสิร์ฟเคียงหม้ออบ"}
        ]
    },
    {
        "id": "D06",
        "name": "ปูผัดผงหญิงงามเมือง (ผงกะหรี่)",
        "category": "cat_recom",
        "image_ref": 1,
        "price": 370,
        "target_cost_pct": 35.4,
        "items": [
            {"rm_id": "RM_CRAB_BLUE", "portion": 350, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ปูม้าสดตัดแต่งก้ามทุบพอแตก ผ่า 4 ชิ้น"},
            {"rm_id": "RM_CHILI_PASTE_EGG_BASE", "portion": 160, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ซอสผงกะหรี่สูตรหญิงงามเมือง (ไข่ไก่ 2 ฟอง+นมข้นจืด+ผงกะหรี่+พริกเผา)"},
            {"rm_id": "RM_KALE", "portion": 60, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ต้นหอม คื่นช่าย และหอมใหญ่ซอย"}
        ]
    },

    # IMAGE 2: เมนูแนะนำ 2
    {
        "id": "D07_1",
        "name": "ปูไข่ดอง (1 ตัว)",
        "category": "cat_recom",
        "image_ref": 2,
        "price": 279,
        "target_cost_pct": 36.2,
        "items": [
            {"rm_id": "RM_CRAB_EGG_ROE", "portion": 1, "unit": "ตัว", "action": "นับชิ้น", "type": "primary", "note": "ปูทะเลไข่แน่นคัดไซส์พิเศษ 1 ตัว (200g) แกะกระดองตัดแต่ง"},
            {"rm_id": "RM_SAUCE_SEAFOOD", "portion": 60, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำจิ้มซีฟู้ดพริกสดมะนาวแท้ราดฉ่ำบนไข่ปู"},
            {"rm_id": "RM_LIME_JUICE", "portion": 20, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำดองน้ำปลาปรุงรสสูตรกลมกล่อม"}
        ]
    },
    {
        "id": "D07_2",
        "name": "ปูไข่ดอง (2 ตัวสุดคุ้ม)",
        "category": "cat_recom",
        "image_ref": 2,
        "price": 490,
        "target_cost_pct": 37.6,
        "items": [
            {"rm_id": "RM_CRAB_EGG_ROE", "portion": 2, "unit": "ตัว", "action": "นับชิ้น", "type": "primary", "note": "ปูทะเลไข่แน่นคัดไซส์พิเศษ 2 ตัวเต็มจาน (รวม ~400g)"},
            {"rm_id": "RM_SAUCE_SEAFOOD", "portion": 100, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำจิ้มซีฟู้ดมะนาวสดแท้ 2 ถ้วย"},
            {"rm_id": "RM_LIME_JUICE", "portion": 30, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำดองน้ำปลาสูตรพิเศษแสนสุข"}
        ]
    },
    {
        "id": "D08",
        "name": "หมึกกระตอยน้ำดำ",
        "category": "cat_recom",
        "image_ref": 2,
        "price": 200,
        "target_cost_pct": 35.0,
        "items": [
            {"rm_id": "RM_SQUID_BABY", "portion": 260, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมึกกระตอยสดไม่เอาดีออก เพื่อให้น้ำหมึกดำหวานธรรมชาติ"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 30, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กระเทียมไทยบุบ+รากผักชีคั่วต้ม"},
            {"rm_id": "RM_LIME_JUICE", "portion": 25, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมะนาวแท้แตะรสกลมกล่อม"}
        ]
    },
    {
        "id": "D09",
        "name": "กะหล่ำปลีไข่ข้นปู",
        "category": "cat_recom",
        "image_ref": 2,
        "price": 200,
        "target_cost_pct": 35.8,
        "items": [
            {"rm_id": "RM_CRAB_MEAT", "portion": 65, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "เนื้อปูก้อน/ก้ามปูแกะโรยหน้าและผัดในไข่ข้น"},
            {"rm_id": "RM_EGG_FRESH", "portion": 3, "unit": "ฟอง", "action": "นับชิ้น", "type": "primary", "note": "ไข่ไก่สด 3 ฟอง ตีพอแตกทำไข่ข้นเยิ้ม"},
            {"rm_id": "RM_CABBAGE", "portion": 130, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กะหล่ำปลีฉีกชิ้นผัดน้ำปลาหอมกระทะรองจาน"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 25, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันเนยสำหรับทอดไข่ข้นเนียนนุ่ม"}
        ]
    },
    {
        "id": "D10",
        "name": "ยำเนื้อปู",
        "category": "cat_recom",
        "image_ref": 2,
        "price": 200,
        "target_cost_pct": 36.5,
        "items": [
            {"rm_id": "RM_CRAB_MEAT", "portion": 75, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "เนื้อปูก้อน+ก้ามสดนึ่งสุกใหม่หวานฉ่ำ"},
            {"rm_id": "RM_MANGO_SHREDDED", "portion": 70, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "มะม่วงเปรี้ยวสับเส้นกรอบ"},
            {"rm_id": "RM_SAUCE_YUM", "portion": 50, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำยำมะนาวสดแท้สูตรพริกสดหอมแดง"}
        ]
    },
    {
        "id": "D11",
        "name": "กุ้งผัดพริกเกลือกระเทียม",
        "category": "cat_recom",
        "image_ref": 2,
        "price": 200,
        "target_cost_pct": 36.0,
        "items": [
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 240, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาว 7-8 ตัว ตัดหนวดผ่าหลังทอดสะดุ้งกรอบ"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 55, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กระเทียมไทยสับเจียวกรอบเหลืองทองโรยพูน"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 35, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันทอดและคั่วพริกเกลือหอมฟุ้ง"}
        ]
    },
    {
        "id": "D12",
        "name": "ไข่ตุ๋นทะเลหม้อไฟ",
        "category": "cat_recom",
        "image_ref": 2,
        "price": 200,
        "target_cost_pct": 36.8,
        "items": [
            {"rm_id": "RM_EGG_FRESH", "portion": 4, "unit": "ฟอง", "action": "นับชิ้น", "type": "primary", "note": "ไข่ไก่สด 4 ฟอง ตีผสมน้ำซุปกรองเนียน"},
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 80, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวสด 3-4 ตัว วางบนหน้าไข่ตุ๋น"},
            {"rm_id": "RM_SQUID_BANANA", "portion": 80, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ปลาหมึกกล้วยบั้งลวกสุกแต่งหน้าหม้อไฟ"},
            {"rm_id": "RM_CRAB_MEAT", "portion": 20, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "เนื้อปูก้อนฉีกโรยหน้าเพิ่มความพรีเมียม"}
        ]
    },

    # IMAGE 3: เมนูต้ม / แกง
    {
        "id": "D13",
        "name": "ต้มยำโป๊ะแตก",
        "category": "cat_soup",
        "image_ref": 3,
        "price": 250,
        "target_cost_pct": 36.0,
        "items": [
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 80, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวสด 3 ตัว แกะเปลือกไว้หาง"},
            {"rm_id": "RM_SQUID_BANANA", "portion": 90, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมึกกล้วยหั่นแว่นบั้งสวย"},
            {"rm_id": "RM_SEABASS_FILLET", "portion": 80, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "เนื้อปลากระพงแล่ชิ้นสดหวาน"},
            {"rm_id": "RM_MUSHROOM_STRAW", "portion": 60, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "เห็ดฟางสดผ่าครึ่ง"},
            {"rm_id": "RM_LIME_JUICE", "portion": 40, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมะนาวแท้คั้นสดปรุงรสเปรี้ยวแซ่บหอมกะเพรา"}
        ]
    },
    {
        "id": "D14",
        "name": "ต้มยำทะเลข้น / ใส",
        "category": "cat_soup",
        "image_ref": 3,
        "price": 200,
        "target_cost_pct": 36.2,
        "items": [
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 80, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวสด 3 ตัว"},
            {"rm_id": "RM_SQUID_BANANA", "portion": 90, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมึกกล้วยหั่นแว่น"},
            {"rm_id": "RM_MUSSEL", "portion": 70, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หอยแมลงภู่ชิลี"},
            {"rm_id": "RM_MUSHROOM_STRAW", "portion": 60, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "เห็ดฟางสดต้มในหม้อไฟ"},
            {"rm_id": "RM_LIME_JUICE", "portion": 40, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมะนาวสดแท้คั้นสด (เติมน้ำพริกเผา+นมข้นจืดกรณีน้ำข้น)"}
        ]
    },
    {
        "id": "D15",
        "name": "แกงป่าทะเล",
        "category": "cat_soup",
        "image_ref": 3,
        "price": 200,
        "target_cost_pct": 35.8,
        "items": [
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 70, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวสดแกะเปลือก"},
            {"rm_id": "RM_SQUID_BANANA", "portion": 80, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ปลาหมึกสดบั้ง"},
            {"rm_id": "RM_SEABASS_FILLET", "portion": 70, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "เนื้อปลากระพงแล่ชิ้น"},
            {"rm_id": "RM_MIXED_VEG", "portion": 100, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "มะเขือเปราะ มะเขือพวง ถั่วฝักยาว พริกไทยอ่อน กระชายซอย"}
        ]
    },
    {
        "id": "D16",
        "name": "แกงส้มผักรวมกุ้ง",
        "category": "cat_soup",
        "image_ref": 3,
        "price": 300,
        "target_cost_pct": 35.5,
        "items": [
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 240, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวตัวโตแกะไว้หาง 8 ตัว (น้ำหนัก 240g)"},
            {"rm_id": "RM_CURRY_SOUP_BASE", "portion": 450, "unit": "ml", "action": "ตวงปริมาตร", "type": "primary", "note": "น้ำแกงส้มปลาโขลกเข้มข้น"},
            {"rm_id": "RM_CABBAGE", "portion": 180, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ผักรวม (ผักกาดขาว ถั่วฝักยาว กะหล่ำปลี แครอท)"}
        ]
    },
    {
        "id": "D17",
        "name": "แกงส้มชะอมกุ้ง",
        "category": "cat_soup",
        "image_ref": 3,
        "price": 300,
        "target_cost_pct": 35.8,
        "items": [
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 200, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวสด 6-7 ตัว"},
            {"rm_id": "RM_CHA_OM_EGG", "portion": 160, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ไข่ทอดชะอมหั่นเต๋าหนานุ่ม 8-10 ชิ้น"},
            {"rm_id": "RM_CURRY_SOUP_BASE", "portion": 450, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำแกงส้มสูตรปลาโขลกร้อนฉ่าเสิร์ฟหม้อไฟ"}
        ]
    },
    {
        "id": "D18",
        "name": "แกงจืดเต้าหู้หมูสับ",
        "category": "cat_soup",
        "image_ref": 3,
        "price": 200,
        "target_cost_pct": 35.2,
        "items": [
            {"rm_id": "RM_PORK_MINCED", "portion": 180, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมูสับหมักปรุงรสนุ่มปั้นก้อน 8-10 ก้อน"},
            {"rm_id": "RM_TOFU_EGG", "portion": 2, "unit": "หลอด", "action": "นับชิ้น", "type": "primary", "note": "เต้าหู้ไข่ไก่ 2 หลอด หั่นแว่นพอดีคำ"},
            {"rm_id": "RM_CABBAGE", "portion": 120, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ผักกาดขาวหวาน สาหร่ายวากาเมะ และขึ้นฉ่าย"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 20, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กระเทียมเจียวหอมโรยหน้าชาม"}
        ]
    },
    {
        "id": "D19",
        "name": "ต้มแซ่บกระดูกอ่อน",
        "category": "cat_soup",
        "image_ref": 3,
        "price": 180,
        "target_cost_pct": 36.5,
        "items": [
            {"rm_id": "RM_PORK_CARTILAGE", "portion": 260, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กระดูกอ่อนหมูเคี่ยวตุ๋นจนนุ่มเคี้ยวกรุบ"},
            {"rm_id": "RM_MUSHROOM_STRAW", "portion": 60, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "เห็ดฟางสดต้มในหม้อ"},
            {"rm_id": "RM_LIME_JUICE", "portion": 40, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมะนาวแท้ ข้าวคั่ว และพริกป่นคั่วหอม"}
        ]
    },
    {
        "id": "D20",
        "name": "ซุปเปอร์ตีนไก่",
        "category": "cat_soup",
        "image_ref": 3,
        "price": 180,
        "target_cost_pct": 35.8,
        "items": [
            {"rm_id": "RM_CHICKEN_FEET", "portion": 380, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ตีนไก่คัดพิเศษตุ๋นพะโล้/ยาจีนจนเปื่อยร่อนเต็มชาม"},
            {"rm_id": "RM_LIME_JUICE", "portion": 50, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมะนาวแท้คั้นสดรสจี๊ดจ๊าด"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 25, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "พริกขี้หนูสวนบุบหยาบ ผักชีฝรั่งซอยหอม"}
        ]
    },

    # IMAGE 4: เมนูไข่เจียว (Omelet)
    {
        "id": "D21",
        "name": "ไข่เจียวหอยนางรม",
        "category": "cat_omelet",
        "image_ref": 4,
        "price": 180,
        "target_cost_pct": 36.8,
        "items": [
            {"rm_id": "RM_OYSTER", "portion": 160, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หอยนางรมสดคัดตัวอวบลวกสะดุ้งน้ำก่อนเจียว"},
            {"rm_id": "RM_EGG_FRESH", "portion": 3, "unit": "ฟอง", "action": "นับชิ้น", "type": "primary", "note": "ไข่ไก่สด 3 ฟอง ตีฟู"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 100, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันพืชสำหรับทอดไข่เจียวฟูกรอบไม่อมน้ำมัน"}
        ]
    },
    {
        "id": "D22",
        "name": "ไข่เจียวปู",
        "category": "cat_omelet",
        "image_ref": 4,
        "price": 180,
        "target_cost_pct": 38.8,
        "items": [
            {"rm_id": "RM_CRAB_MEAT", "portion": 65, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "เนื้อปูก้อนสดแกะแน่นๆ โรยหน้าและแทรกในเนื้อไข่"},
            {"rm_id": "RM_EGG_FRESH", "portion": 3, "unit": "ฟอง", "action": "นับชิ้น", "type": "primary", "note": "ไข่ไก่สด 3 ฟอง"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 90, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันทอดไข่ปูกรอบนอกนุ่มใน"}
        ]
    },
    {
        "id": "D23",
        "name": "ไข่เจียวหมูสับ",
        "category": "cat_omelet",
        "image_ref": 4,
        "price": 150,
        "target_cost_pct": 35.5,
        "items": [
            {"rm_id": "RM_PORK_MINCED", "portion": 170, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมูสับปรุงรสหมักนุ่ม"},
            {"rm_id": "RM_EGG_FRESH", "portion": 3, "unit": "ฟอง", "action": "นับชิ้น", "type": "primary", "note": "ไข่ไก่สด 3 ฟอง"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 90, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันสำหรับเจียวฟูกรอบ"}
        ]
    },
    {
        "id": "D24",
        "name": "ไข่เจียวกุ้ง",
        "category": "cat_omelet",
        "image_ref": 4,
        "price": 180,
        "target_cost_pct": 36.2,
        "items": [
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 170, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวสดหั่นเต๋าชิ้นโตแน่นๆ"},
            {"rm_id": "RM_EGG_FRESH", "portion": 3, "unit": "ฟอง", "action": "นับชิ้น", "type": "primary", "note": "ไข่ไก่สด 3 ฟอง"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 90, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันทอดไข่เจียวฟูกรอบ"}
        ]
    },
    {
        "id": "D25",
        "name": "ไข่เจียวธรรมดา",
        "category": "cat_omelet",
        "image_ref": 4,
        "price": 100,
        "target_cost_pct": 35.0,
        "items": [
            {"rm_id": "RM_EGG_FRESH", "portion": 4, "unit": "ฟอง", "action": "นับชิ้น", "type": "primary", "note": "ไข่ไก่สด 4 ฟองเต็มจานฟูหนานุ่ม"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 110, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันทอดฟูกรอบสีทองไม่อมน้ำมัน"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 15, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ต้นหอมซอยโรยในเนื้อไข่"}
        ]
    },

    # IMAGE 5: เมนูยำทะเลสด
    {
        "id": "D26",
        "name": "หอยนางรมทรงเครื่อง",
        "category": "cat_fresh_yum",
        "image_ref": 5,
        "price": 180,
        "target_cost_pct": 36.2,
        "items": [
            {"rm_id": "RM_OYSTER", "portion": 190, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หอยนางรมสดคัดตัวอวบแช่น้ำแข็งเย็นเจี๊ยบ"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 35, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "หอมเจียวทอดกรอบแท้สีทองพูนถ้วย"},
            {"rm_id": "RM_SAUCE_SEAFOOD", "portion": 60, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำจิ้มซีฟู้ดมะนาวสดแท้รสจัด"},
            {"rm_id": "RM_KALE", "portion": 50, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ยอดกระถินสดและน้ำพริกเผาเคียงจาน"}
        ]
    },
    {
        "id": "D27",
        "name": "กุ้งแช่น้ำปลา",
        "category": "cat_fresh_yum",
        "image_ref": 5,
        "price": 180,
        "target_cost_pct": 36.0,
        "items": [
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 190, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวสด 8-9 ตัว แกะเปลือกผ่าหลังแช่น้ำปลาแช่เย็นจัด"},
            {"rm_id": "RM_CABBAGE", "portion": 80, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "มะระจีนฝานบางแช่น้ำแข็งกรอบและกะหล่ำฝอยรองจาน"},
            {"rm_id": "RM_SAUCE_SEAFOOD", "portion": 65, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำจิ้มซีฟู้ดมะนาวสดราดตัวกุ้งพร้อมกระเทียมสดซอย"}
        ]
    },
    {
        "id": "D28",
        "name": "ยำหอยนางรม",
        "category": "cat_fresh_yum",
        "image_ref": 5,
        "price": 180,
        "target_cost_pct": 35.8,
        "items": [
            {"rm_id": "RM_OYSTER", "portion": 170, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หอยนางรมสดเต่งตึงล้างสะอาด"},
            {"rm_id": "RM_SAUCE_YUM", "portion": 60, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำยำสามรสน้ำพริกเผามะนาวแท้"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 25, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "หอมเจียวทอดกรอบโรยหน้าและยอดกระถิน"}
        ]
    },
    {
        "id": "D29",
        "name": "ลาบทะเล",
        "category": "cat_fresh_yum",
        "image_ref": 5,
        "price": 200,
        "target_cost_pct": 36.5,
        "items": [
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 80, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวสดลวกสะดุ้ง"},
            {"rm_id": "RM_SQUID_BANANA", "portion": 90, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมึกกล้วยบั้งลวกเด้ง"},
            {"rm_id": "RM_SEABASS_FILLET", "portion": 70, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "เนื้อปลากระพงลวกชิ้นพอดีคำ"},
            {"rm_id": "RM_LIME_JUICE", "portion": 40, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมะนาวสดแท้ ข้าวคั่วหอม และผักชีฝรั่ง"}
        ]
    },
    {
        "id": "D30",
        "name": "หอยแครงลวก",
        "category": "cat_fresh_yum",
        "image_ref": 5,
        "price": 180,
        "target_cost_pct": 36.0,
        "items": [
            {"rm_id": "RM_COCKLE", "portion": 420, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หอยแครงสดไซส์กลาง-ใหญ่ ล้างขัดสะอาด ลวกความสุกตามลูกค้าสั่ง"},
            {"rm_id": "RM_SAUCE_SEAFOOD", "portion": 80, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำจิ้มซีฟู้ดรสเด็ดมะนาวสด 2 ถ้วย (ซีฟู้ดพริกสด+หวานถั่วตัด)"}
        ]
    },
    {
        "id": "D31",
        "name": "ยำมะม่วงปูม้า",
        "category": "cat_fresh_yum",
        "image_ref": 5,
        "price": 200,
        "target_cost_pct": 36.2,
        "items": [
            {"rm_id": "RM_CRAB_BLUE", "portion": 230, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ปูม้าสดคัดไข่/เนื้อตัดแต่งพร้อมทาน 1.5 ตัว"},
            {"rm_id": "RM_MANGO_SHREDDED", "portion": 110, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "มะม่วงเปรี้ยวสับเส้นกรอบฉ่ำ"},
            {"rm_id": "RM_SAUCE_YUM", "portion": 55, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำยำมะนาวสดพริกแดงจินดาตำ"}
        ]
    },

    # IMAGE 6: เมนูยำทะเลไทยๆ
    {
        "id": "D32",
        "name": "ยำหอยแครง",
        "category": "cat_thai_yum",
        "image_ref": 6,
        "price": 180,
        "target_cost_pct": 36.5,
        "items": [
            {"rm_id": "RM_COCKLE", "portion": 450, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หอยแครงสด 450g ลวกแกะฝาเหลือเนื้อฉ่ำๆ"},
            {"rm_id": "RM_SAUCE_YUM", "portion": 60, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำยำมะนาวสดแท้ตะไคร้ซอยสะระแหน่"}
        ]
    },
    {
        "id": "D33",
        "name": "ยำปลาหมึก",
        "category": "cat_thai_yum",
        "image_ref": 6,
        "price": 180,
        "target_cost_pct": 36.0,
        "items": [
            {"rm_id": "RM_SQUID_BANANA", "portion": 230, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ปลาหมึกกล้วยบั้งถี่ลวกสะดุ้ง 15 วินาที กรอบเด้ง"},
            {"rm_id": "RM_SAUCE_YUM", "portion": 55, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำยำสามรสมะนาวสด พริกชี้ฟ้า และขึ้นฉ่าย"}
        ]
    },
    {
        "id": "D34",
        "name": "ยำทะเลรวมมิตร",
        "category": "cat_thai_yum",
        "image_ref": 6,
        "price": 180,
        "target_cost_pct": 36.2,
        "items": [
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 70, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวสด 3 ตัว"},
            {"rm_id": "RM_SQUID_BANANA", "portion": 80, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมึกกล้วยบั้งลวกเด้ง"},
            {"rm_id": "RM_PORK_MINCED", "portion": 40, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "หมูสับลวกสุกเพิ่มความนัว"},
            {"rm_id": "RM_SAUCE_YUM", "portion": 55, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำยำมะนาวแท้ ขึ้นฉ่าย หอมใหญ่ มะเขือเทศ"}
        ]
    },
    {
        "id": "D35",
        "name": "ยำมาม่าทะเลรวม",
        "category": "cat_thai_yum",
        "image_ref": 6,
        "price": 180,
        "target_cost_pct": 35.8,
        "items": [
            {"rm_id": "RM_INSTANT_NOODLES", "portion": 1, "unit": "ซอง", "action": "นับชิ้น", "type": "primary", "note": "บะหมี่กึ่งสำเร็จรูป ลวกเส้นพอเหนียวนุ่ม"},
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 70, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวสด 3 ตัว"},
            {"rm_id": "RM_SQUID_BANANA", "portion": 80, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมึกกล้วยบั้งลวก"},
            {"rm_id": "RM_PORK_MINCED", "portion": 40, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "หมูสับลวกสุก"},
            {"rm_id": "RM_SAUCE_YUM", "portion": 55, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำยำมะนาวสดปรุงผสมเครื่องปรุงมาม่า"}
        ]
    },
    {
        "id": "D36",
        "name": "ยำไข่แมงดา",
        "category": "cat_thai_yum",
        "image_ref": 6,
        "price": 180,
        "target_cost_pct": 35.5,
        "items": [
            {"rm_id": "RM_HORSESHOE_CRAB_EGG", "portion": 150, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ไข่แมงดาทะเลสุกนึ่ง/ย่างหอมมัน"},
            {"rm_id": "RM_MANGO_SHREDDED", "portion": 90, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "มะม่วงเปรี้ยวสับเส้นกรอบ"},
            {"rm_id": "RM_SAUCE_YUM", "portion": 55, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำยำสามรสมะนาวสดพริกขี้หนูสวน"}
        ]
    },
    {
        "id": "D37",
        "name": "ยำวุ้นเส้นทะเล",
        "category": "cat_thai_yum",
        "image_ref": 6,
        "price": 180,
        "target_cost_pct": 35.8,
        "items": [
            {"rm_id": "RM_GLASS_NOODLES", "portion": 110, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "วุ้นเส้นสดลวกนุ่มใส"},
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 70, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวสด 3 ตัว"},
            {"rm_id": "RM_SQUID_BANANA", "portion": 80, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมึกกล้วยบั้งลวกเด้ง"},
            {"rm_id": "RM_PORK_MINCED", "portion": 40, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "หมูสับลวกสุก"},
            {"rm_id": "RM_SAUCE_YUM", "portion": 55, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำยำมะนาวสดแท้โรยถั่วลิสงคั่ว"}
        ]
    },

    # IMAGE 7: อาหารทะเลเผา / ย่าง / นึ่ง (BBQ Seafood)
    {
        "id": "D38",
        "name": "ทะเลเผารวมมิตรชุดใหญ่",
        "category": "cat_bbq",
        "image_ref": 7,
        "price": 600,
        "target_cost_pct": 37.8,
        "items": [
            {"rm_id": "RM_SHRIMP_RIVER", "portion": 250, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งแม่น้ำเผามันเยิ้ม 3-4 ตัว (250g)"},
            {"rm_id": "RM_SQUID_ROE", "portion": 200, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมึกไข่ย่างหอมกรุ่น 1 ตัวใหญ่ (200g)"},
            {"rm_id": "RM_CRAB_BLUE", "portion": 200, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ปูม้านึ่ง 1 ตัวเต็มกระดอง (200g)"},
            {"rm_id": "RM_COCKLE", "portion": 200, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หอยแครงลวก/เผา (200g) + หอยแมลงภู่"},
            {"rm_id": "RM_SAUCE_SEAFOOD", "portion": 120, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำจิ้มซีฟู้ดมะนาวสด 2 ถ้วยใหญ่"}
        ]
    },
    {
        "id": "D39",
        "name": "หอยแครงเผา",
        "category": "cat_bbq",
        "image_ref": 7,
        "price": 180,
        "target_cost_pct": 36.0,
        "items": [
            {"rm_id": "RM_COCKLE", "portion": 420, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หอยแครงสดตัวใหญ่ล้างสะอาด ย่างเตาถ่านหอมหวาน"},
            {"rm_id": "RM_SAUCE_SEAFOOD", "portion": 80, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำจิ้มซีฟู้ดรสจัดจ้านมะนาวแท้ 2 ถ้วย"}
        ]
    },
    {
        "id": "D40",
        "name": "หมึกไข่ย่าง",
        "category": "cat_bbq",
        "image_ref": 7,
        "price": 300,
        "target_cost_pct": 36.5,
        "items": [
            {"rm_id": "RM_SQUID_ROE", "portion": 380, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมึกไข่ตัวโต 2 ตัวเต็มจาน ย่างไฟเตาถ่านหอมฟุ้ง"},
            {"rm_id": "RM_SAUCE_SEAFOOD", "portion": 80, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำจิ้มซีฟู้ดพริกสดมะนาวแท้ถ้วยใหญ่"}
        ]
    },
    {
        "id": "D41_S",
        "name": "กุ้งเผา (จานเล็ก)",
        "category": "cat_bbq",
        "image_ref": 7,
        "price": 350,
        "target_cost_pct": 36.5,
        "items": [
            {"rm_id": "RM_SHRIMP_RIVER", "portion": 450, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งก้ามกรามเผามันเยิ้ม 5-6 ตัว (450g)"},
            {"rm_id": "RM_SAUCE_SEAFOOD", "portion": 65, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำจิ้มซีฟู้ดมะนาวสดแท้สูตรแสนสุข"}
        ]
    },
    {
        "id": "D41_L",
        "name": "กุ้งเผา (จานใหญ่ 1 กก.)",
        "category": "cat_bbq",
        "image_ref": 7,
        "price": 600,
        "target_cost_pct": 38.0,
        "items": [
            {"rm_id": "RM_SHRIMP_RIVER", "portion": 850, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งก้ามกรามสดเผา 10-12 ตัว มันหัวเยิ้มๆ (850g สด)"},
            {"rm_id": "RM_SAUCE_SEAFOOD", "portion": 120, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำจิ้มซีฟู้ดมะนาวสด 2 ถ้วยใหญ่"}
        ]
    },
    {
        "id": "D42_S",
        "name": "ปูม้านึ่ง (จานเล็ก)",
        "category": "cat_bbq",
        "image_ref": 7,
        "price": 370,
        "target_cost_pct": 35.5,
        "items": [
            {"rm_id": "RM_CRAB_BLUE", "portion": 500, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ปูม้าสดเนื้อแน่น 2-3 ตัว นึ่งแกะกระดองพร้อมทาน"},
            {"rm_id": "RM_SAUCE_SEAFOOD", "portion": 65, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำจิ้มซีฟู้ดพริกสดมะนาวแท้"}
        ]
    },
    {
        "id": "D42_L",
        "name": "ปูม้านึ่ง (จานใหญ่ 1 กก.)",
        "category": "cat_bbq",
        "image_ref": 7,
        "price": 700,
        "target_cost_pct": 36.8,
        "items": [
            {"rm_id": "RM_CRAB_BLUE", "portion": 1000, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ปูม้าสด 4-5 ตัวเต็มกิโลกรัม แกะจัดเรียงสวยงาม"},
            {"rm_id": "RM_SAUCE_SEAFOOD", "portion": 120, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำจิ้มซีฟู้ดมะนาวสด 2 ถ้วยใหญ่"}
        ]
    },

    # IMAGE 8: เมนูทอด (Deep Fried)
    {
        "id": "D43_S",
        "name": "กุ้งทอดกระเทียม (ขนาดปกติ)",
        "category": "cat_fried",
        "image_ref": 8,
        "price": 200,
        "target_cost_pct": 35.2,
        "items": [
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 230, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวสดแกะเปลือกไว้หาง 7 ตัว ทอดสะดุ้ง"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 50, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กระเทียมเจียวกรอบหอมสีทองพูนจาน"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 50, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันทอดและคั่วพริกไทยกระเทียม"}
        ]
    },
    {
        "id": "D43_L",
        "name": "กุ้งทอดกระเทียม (จานใหญ่)",
        "category": "cat_fried",
        "image_ref": 8,
        "price": 300,
        "target_cost_pct": 36.0,
        "items": [
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 360, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวสดตัวโต 11-12 ตัว"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 70, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กระเทียมเจียวสีทองกรอบหอม"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 70, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันทอดและคั่วซอส"}
        ]
    },
    {
        "id": "D44",
        "name": "ทอดมันกุ้ง",
        "category": "cat_fried",
        "image_ref": 8,
        "price": 200,
        "target_cost_pct": 35.5,
        "items": [
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 220, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "เนื้อกุ้งสดบดเด้งผสมมันหมูเล็กน้อย ปั้นโดนัท 5 ชิ้นโต"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 80, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันทอดเกล็ดขนมปังฟูกรอบสีทอง"},
            {"rm_id": "RM_SAUCE_YUM", "portion": 40, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำจิ้มบ๊วยเจี่ยหวานหอมเสิร์ฟเคียง"}
        ]
    },
    {
        "id": "D45",
        "name": "หมึกไข่ทอดกระเทียม",
        "category": "cat_fried",
        "image_ref": 8,
        "price": 300,
        "target_cost_pct": 36.5,
        "items": [
            {"rm_id": "RM_SQUID_ROE", "portion": 360, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมึกไข่สดคัดไซส์ 2-3 ตัว ทอดแห้งผิวตึง"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 60, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กระเทียมเจียวกรอบหอมโรยทั่วจาน"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 60, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันทอดและคลุกซอสกระเทียมพริกไทย"}
        ]
    },
    {
        "id": "D46",
        "name": "ปีกไก่ทอดน้ำปลา",
        "category": "cat_fried",
        "image_ref": 8,
        "price": 150,
        "target_cost_pct": 35.2,
        "items": [
            {"rm_id": "RM_CHICKEN_WINGS", "portion": 350, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ปีกไก่กลางหมักน้ำปลาแท้ 6 ชิ้นใหญ่ (350g)"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 80, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันทอดหนังกรอบเนื้อในฉ่ำ"},
            {"rm_id": "RM_SAUCE_YUM", "portion": 40, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำจิ้มไก่หวานสูตรเด็ด"}
        ]
    },
    {
        "id": "D47",
        "name": "เอ็นไก่ทอด",
        "category": "cat_fried",
        "image_ref": 8,
        "price": 150,
        "target_cost_pct": 36.5,
        "items": [
            {"rm_id": "RM_CHICKEN_TENDON", "portion": 280, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "เอ็นข้อไก่สดหมักงาขาวชุบแป้งทอดกรอบบาง"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 70, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันทอดกรุบกรอบไม่อมน้ำมัน"},
            {"rm_id": "RM_SAUCE_YUM", "portion": 40, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "ซอสพริกศรีราชาเสิร์ฟเคียง"}
        ]
    },
    {
        "id": "D48",
        "name": "หมูสามชั้นทอดน้ำปลา",
        "category": "cat_fried",
        "image_ref": 8,
        "price": 180,
        "target_cost_pct": 35.8,
        "items": [
            {"rm_id": "RM_PORK_BELLY", "portion": 280, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมูสามชั้นเส้นสวยหมักน้ำปลาแท้ ทอดหั่นชิ้นเรียงเต็มจาน"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 75, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันทอดกรอบนอกนุ่มฉ่ำ"},
            {"rm_id": "RM_SAUCE_SEAFOOD", "portion": 45, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำจิ้มแจ่วรสแซ่บข้าวคั่วหอม"}
        ]
    },

    # IMAGE 9: เมนูผัด 1
    {
        "id": "D49",
        "name": "ทะเลผัดฉ่า",
        "category": "cat_stir_fry",
        "image_ref": 9,
        "price": 200,
        "target_cost_pct": 35.5,
        "items": [
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 80, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาว 3 ตัว"},
            {"rm_id": "RM_SQUID_BANANA", "portion": 90, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมึกกล้วยบั้งชิ้นสวย"},
            {"rm_id": "RM_SEABASS_FILLET", "portion": 70, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "เนื้อปลากระพงทอดสะดุ้ง"},
            {"rm_id": "RM_MIXED_VEG", "portion": 50, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กระชายซอย พริกไทยอ่อนสด ใบมะกรูด ใบโหระพา"}
        ]
    },
    {
        "id": "D50",
        "name": "กะหล่ำปลีผัดน้ำปลา",
        "category": "cat_stir_fry",
        "image_ref": 9,
        "price": 100,
        "target_cost_pct": 35.0,
        "items": [
            {"rm_id": "RM_CABBAGE", "portion": 380, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กะหล่ำปลีคัดใบหวานกรอบฉีกชิ้นพอดีคำ"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 35, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กระเทียมไทยบุบผัดกระทะคั่วหอมและโรยหน้า"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 35, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันหมู/พืชคั่วกระทะไฟแรงกับน้ำปลาแท้"}
        ]
    },
    {
        "id": "D51",
        "name": "ผัดคะน้าหมูกรอบ",
        "category": "cat_stir_fry",
        "image_ref": 9,
        "price": 180,
        "target_cost_pct": 36.5,
        "items": [
            {"rm_id": "RM_PORK_CRISPY", "portion": 160, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมูกรอบหั่นชิ้นเต๋าหนา 160g หนังกรอบฟู"},
            {"rm_id": "RM_KALE", "portion": 200, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "คะน้าฮ่องกงยอดอ่อนลอกก้านกรอบ"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 25, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กระเทียมสับผัดพริกสดไฟแดง"}
        ]
    },
    {
        "id": "D52",
        "name": "ผัดหนำเลี้ยบหมูสับ",
        "category": "cat_stir_fry",
        "image_ref": 9,
        "price": 150,
        "target_cost_pct": 35.8,
        "items": [
            {"rm_id": "RM_PORK_MINCED", "portion": 190, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมูสับติดมันเล็กน้อยคั่วแห้งหอม"},
            {"rm_id": "RM_CHINESE_OLIVE", "portion": 50, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หนำเลี้ยบสับละเอียดผัดเข้าเนื้อ"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 30, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กระเทียมสับเจียวหอม พริกซอย มะนาวหั่นเต๋าเคียง"}
        ]
    },
    {
        "id": "D53",
        "name": "ผัดแขนงหมูกรอบ",
        "category": "cat_stir_fry",
        "image_ref": 9,
        "price": 180,
        "target_cost_pct": 36.2,
        "items": [
            {"rm_id": "RM_PORK_CRISPY", "portion": 155, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมูกรอบชิ้นหนา 155g"},
            {"rm_id": "RM_BRUSSELS", "portion": 200, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ผักแขนงสดคัดหวานกรอบผัดไฟแดง"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 25, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "พริกกระเทียมบุบสดไฟแดง"}
        ]
    },
    {
        "id": "D54",
        "name": "ไชโป๊ผัดไข่",
        "category": "cat_stir_fry",
        "image_ref": 9,
        "price": 150,
        "target_cost_pct": 35.0,
        "items": [
            {"rm_id": "RM_PICKLED_RADISH", "portion": 200, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ไชโป๊หวานเส้นอย่างดีล้างสะเด็ดน้ำ คั่วหอม"},
            {"rm_id": "RM_EGG_FRESH", "portion": 4, "unit": "ฟอง", "action": "นับชิ้น", "type": "primary", "note": "ไข่ไก่สด 4 ฟอง ผัดเคลือบเส้นสีทอง"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 25, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กระเทียมสับเจียวผัดหอมกระทะ"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 35, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันหมูหรือน้ำมันพืชสำหรับคั่วแห้ง"}
        ]
    },

    # IMAGE 10: เมนูผัด 2
    {
        "id": "D55",
        "name": "ทะเลผัดพริกเผา",
        "category": "cat_stir_fry",
        "image_ref": 10,
        "price": 200,
        "target_cost_pct": 35.5,
        "items": [
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 80, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวสด 3-4 ตัว"},
            {"rm_id": "RM_SQUID_BANANA", "portion": 90, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมึกกล้วยบั้งชิ้น"},
            {"rm_id": "RM_MUSSEL", "portion": 70, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หอยแมลงภู่สด"},
            {"rm_id": "RM_SAUCE_YUM", "portion": 45, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำพริกเผาปรุงรสผัดขลุกขลิกพร้อมใบโหระพาและหอมใหญ่"}
        ]
    },
    {
        "id": "D56",
        "name": "ทะเลผัดผงหญิงงามเมือง (ผงกะหรี่)",
        "category": "cat_stir_fry",
        "image_ref": 10,
        "price": 200,
        "target_cost_pct": 35.8,
        "items": [
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 80, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาว 3-4 ตัว"},
            {"rm_id": "RM_SQUID_BANANA", "portion": 90, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมึกกล้วยบั้งสวย"},
            {"rm_id": "RM_CHILI_PASTE_EGG_BASE", "portion": 140, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "เบสผงกะหรี่เข้มข้น (ไข่ไก่ 2 ฟอง+นมข้นจืด+ผงกะหรี่)"},
            {"rm_id": "RM_KALE", "portion": 50, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ต้นหอม คื่นช่าย และพริกชี้ฟ้า"}
        ]
    },
    {
        "id": "D57",
        "name": "หอยลายผัดโหระพา",
        "category": "cat_stir_fry",
        "image_ref": 10,
        "price": 150,
        "target_cost_pct": 36.5,
        "items": [
            {"rm_id": "RM_CLAM", "portion": 450, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หอยลายสดคัดตัวใหญ่ไม่มีโคลน 450g พูนจาน"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 25, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กระเทียม พริกสดตำผัดหอม"},
            {"rm_id": "RM_KALE", "portion": 40, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ใบโหระพาสดยอดงามและน้ำพริกเผา"}
        ]
    },
    {
        "id": "D58",
        "name": "ไก่ผัดเม็ดมะม่วง",
        "category": "cat_stir_fry",
        "image_ref": 10,
        "price": 200,
        "target_cost_pct": 36.0,
        "items": [
            {"rm_id": "RM_CHICKEN_MEAT", "portion": 220, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "เนื้อสะโพกไก่ชุบแป้งทอดกรอบนอกนุ่มใน 220g"},
            {"rm_id": "RM_CASHEW_NUT", "portion": 65, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "เม็ดมะม่วงหิมพานต์ทอดกรอบมัน 65g พูนจาน"},
            {"rm_id": "RM_MIXED_VEG", "portion": 60, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "พริกหวาน 3 สี หอมใหญ่ พริกแห้งทอด"}
        ]
    },
    {
        "id": "D59",
        "name": "ผัดผักรวมมิตรหมู",
        "category": "cat_stir_fry",
        "image_ref": 10,
        "price": 120,
        "target_cost_pct": 35.0,
        "items": [
            {"rm_id": "RM_MIXED_VEG", "portion": 260, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ผักรวม (บรอกโคลี แครอท กะหล่ำ ข้าวโพดอ่อน) สดกรอบ"},
            {"rm_id": "RM_PORK_SLICED", "portion": 80, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมูสันนอกหมักนุ่ม 80g"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 20, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กระเทียมสับผัดซอสน้ำมันหอยเคลือบเงา"}
        ]
    },
    {
        "id": "D60",
        "name": "กระเฉดหมูกรอบ",
        "category": "cat_stir_fry",
        "image_ref": 10,
        "price": 180,
        "target_cost_pct": 36.2,
        "items": [
            {"rm_id": "RM_PORK_CRISPY", "portion": 155, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมูกรอบสับชิ้นหนา 155g"},
            {"rm_id": "RM_WATER_MIMOSA", "portion": 160, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ผักกระเฉดยอดอ่อนเด็ดข้อกรอบหวาน"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 25, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "พริกขี้หนูตำกระเทียมสดผัดไฟแดงแรงเร็ว"}
        ]
    },

    # IMAGE 11: เมนูผัด 3
    {
        "id": "D61",
        "name": "ออส่วนหอยนางรม (กระทะร้อน)",
        "category": "cat_stir_fry",
        "image_ref": 11,
        "price": 200,
        "target_cost_pct": 36.8,
        "items": [
            {"rm_id": "RM_OYSTER", "portion": 180, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หอยนางรมสดตัวเต่งตึง 180g แน่นเต็มจาน"},
            {"rm_id": "RM_EGG_FRESH", "portion": 2, "unit": "ฟอง", "action": "นับชิ้น", "type": "primary", "note": "ไข่ไก่สด 2 ฟอง ผัดกับแป้งท้าวยายม่อมนุ่มเหนียว"},
            {"rm_id": "RM_CABBAGE", "portion": 100, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ถั่วงอกสดผัดสะดุ้งไฟรองจานกระทะร้อน"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 35, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันหมูหรือเนยผัดหอม พร้อมซอสพริกศรีราชาเคียง"}
        ]
    },
    {
        "id": "D62",
        "name": "ปูผัดน้ำพริกเผา",
        "category": "cat_stir_fry",
        "image_ref": 11,
        "price": 370,
        "target_cost_pct": 35.8,
        "items": [
            {"rm_id": "RM_CRAB_BLUE", "portion": 370, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ปูม้าสดตัดแต่งก้ามทุบพร้อมทาน 370g"},
            {"rm_id": "RM_SAUCE_YUM", "portion": 60, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำพริกเผาปรุงรสผัดขลุกขลิกพร้อมนมข้นจืด"},
            {"rm_id": "RM_KALE", "portion": 60, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "โหระพา พริกชี้ฟ้า และหอมใหญ่"}
        ]
    },
    {
        "id": "D63",
        "name": "หอยลายน้ำพริกเผา",
        "category": "cat_stir_fry",
        "image_ref": 11,
        "price": 150,
        "target_cost_pct": 36.5,
        "items": [
            {"rm_id": "RM_CLAM", "portion": 450, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หอยลายสด 450g ล้างทรายสะอาด"},
            {"rm_id": "RM_SAUCE_YUM", "portion": 45, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำพริกเผาปรุงรสเข้มข้น"},
            {"rm_id": "RM_KALE", "portion": 35, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ใบโหระพาสดและพริกชี้ฟ้า"}
        ]
    },
    {
        "id": "D64",
        "name": "ผัดผักบุ้งไฟแดง",
        "category": "cat_stir_fry",
        "image_ref": 11,
        "price": 100,
        "target_cost_pct": 35.0,
        "items": [
            {"rm_id": "RM_MORNING_GLORY", "portion": 320, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ผักบุ้งจีนคัดยอดอ่อนกรอบ 320g"},
            {"rm_id": "RM_PORK_CRISPY", "portion": 50, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "หมูกรอบสไลด์บางโรยเพิ่มความคุ้มค่า"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 25, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กระเทียมไทยบุบ พริกขี้หนูสด เต้าเจี้ยวโมฬี"}
        ]
    },
    {
        "id": "D65",
        "name": "กุ้งผัดผงหญิงงามเมือง (ผงกะหรี่)",
        "category": "cat_stir_fry",
        "image_ref": 11,
        "price": 200,
        "target_cost_pct": 35.5,
        "items": [
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 200, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวสดแกะเปลือกผ่าหลัง 6-7 ตัว (200g)"},
            {"rm_id": "RM_CHILI_PASTE_EGG_BASE", "portion": 140, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "เบสผงกะหรี่ไข่ไก่ 2 ฟอง นมข้นจืด น้ำพริกเผา"},
            {"rm_id": "RM_KALE", "portion": 50, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ต้นหอม คื่นช่าย และหอมใหญ่ซอย"}
        ]
    },
    {
        "id": "D66",
        "name": "กุ้งผัดเม็ดมะม่วง",
        "category": "cat_stir_fry",
        "image_ref": 11,
        "price": 200,
        "target_cost_pct": 36.2,
        "items": [
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 190, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวสด 6 ตัว ชุบแป้งทอดกรอบเบาๆ"},
            {"rm_id": "RM_CASHEW_NUT", "portion": 60, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "เม็ดมะม่วงหิมพานต์ทอดกรอบ 60g"},
            {"rm_id": "RM_MIXED_VEG", "portion": 60, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "พริกหวาน หอมใหญ่ พริกแห้งทอดกรอบ"}
        ]
    },

    # IMAGE 13: เมนูข้าวผัดกระทะทอง (Fried Rice S / M / L)
    # L = 200.-, M = 160.-, S = 70-80.-
    {
        "id": "D67_L",
        "name": "ข้าวผัดปู (จานใหญ่ L)",
        "category": "cat_fried_rice",
        "image_ref": 13,
        "price": 200,
        "target_cost_pct": 38.8,
        "items": [
            {"rm_id": "RM_JASMINE_RICE", "portion": 400, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ข้าวสวยหอมมะลิสุกผึ่งแห้ง 400g เมล็ดร่วนสวย"},
            {"rm_id": "RM_CRAB_MEAT", "portion": 60, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "เนื้อปูก้อนและก้ามปูแกะ 60g โรยพูนหน้าจาน"},
            {"rm_id": "RM_EGG_FRESH", "portion": 3, "unit": "ฟอง", "action": "นับชิ้น", "type": "primary", "note": "ไข่ไก่สด 3 ฟอง ผัดเคลือบเม็ดข้าวสีทอง"},
            {"rm_id": "RM_KALE", "portion": 50, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ต้นหอมซอย แตงกวา และมะนาวผ่าซีกเคียง"}
        ]
    },
    {
        "id": "D68_L",
        "name": "ข้าวผัดกุ้ง (จานใหญ่ L)",
        "category": "cat_fried_rice",
        "image_ref": 13,
        "price": 200,
        "target_cost_pct": 36.5,
        "items": [
            {"rm_id": "RM_JASMINE_RICE", "portion": 400, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ข้าวสวยหอมมะลิผึ่งแห้ง 400g"},
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 200, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวแกะไว้หางตัวโต 8-9 ตัว (200g)"},
            {"rm_id": "RM_EGG_FRESH", "portion": 2, "unit": "ฟอง", "action": "นับชิ้น", "type": "secondary", "note": "ไข่ไก่สด 2 ฟอง ผัดคั่วหอมกระทะ"},
            {"rm_id": "RM_KALE", "portion": 50, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ต้นหอมซอย แตงกวา และมะนาวเคียง"}
        ]
    },
    {
        "id": "D69_L",
        "name": "ข้าวผัดทะเล (จานใหญ่ L)",
        "category": "cat_fried_rice",
        "image_ref": 13,
        "price": 200,
        "target_cost_pct": 37.0,
        "items": [
            {"rm_id": "RM_JASMINE_RICE", "portion": 400, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ข้าวสวยหอมมะลิ 400g"},
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 80, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวสด 3-4 ตัว"},
            {"rm_id": "RM_SQUID_BANANA", "portion": 90, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ปลาหมึกกล้วยบั้งชิ้นสวย"},
            {"rm_id": "RM_EGG_FRESH", "portion": 2, "unit": "ฟอง", "action": "นับชิ้น", "type": "secondary", "note": "ไข่ไก่สด 2 ฟอง"}
        ]
    },
    {
        "id": "D70_L",
        "name": "ข้าวผัดไก่ (จานใหญ่ L)",
        "category": "cat_fried_rice",
        "image_ref": 13,
        "price": 200,
        "target_cost_pct": 35.5,
        "items": [
            {"rm_id": "RM_JASMINE_RICE", "portion": 420, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ข้าวหอมมะลิ 420g"},
            {"rm_id": "RM_CHICKEN_MEAT", "portion": 300, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "เนื้อสะโพกไก่หมักนุ่ม 300g"},
            {"rm_id": "RM_EGG_FRESH", "portion": 3, "unit": "ฟอง", "action": "นับชิ้น", "type": "secondary", "note": "ไข่ไก่สด 3 ฟอง"}
        ]
    },
    {
        "id": "D71_L",
        "name": "ข้าวผัดหมู (จานใหญ่ L)",
        "category": "cat_fried_rice",
        "image_ref": 13,
        "price": 200,
        "target_cost_pct": 36.0,
        "items": [
            {"rm_id": "RM_JASMINE_RICE", "portion": 420, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ข้าวหอมมะลิ 420g"},
            {"rm_id": "RM_PORK_SLICED", "portion": 240, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "เนื้อหมูหมักนุ่มสไลด์ 240g"},
            {"rm_id": "RM_EGG_FRESH", "portion": 3, "unit": "ฟอง", "action": "นับชิ้น", "type": "secondary", "note": "ไข่ไก่สด 3 ฟอง"}
        ]
    },
    {
        "id": "D72_L",
        "name": "ข้าวผัดไข่ (จานใหญ่ L)",
        "category": "cat_fried_rice",
        "image_ref": 13,
        "price": 200,
        "target_cost_pct": 35.5,
        "items": [
            {"rm_id": "RM_JASMINE_RICE", "portion": 450, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ข้าวหอมมะลิ 450g เม็ดสวย"},
            {"rm_id": "RM_EGG_FRESH", "portion": 7, "unit": "ฟอง", "action": "นับชิ้น", "type": "primary", "note": "ไข่ไก่สด 7 ฟอง คั่วไข่สีทองหอมฟุ้งทั้งจาน"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 50, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "เนยสดผสมน้ำมันผัดข้าวหอมกรุ่น"}
        ]
    },

    # IMAGE 14: เมนูปลากระพง (ทุกเมนู 400.- ปลากระพงขาวสด 1 ตัว 750-800g)
    {
        "id": "D73",
        "name": "01 ปลากระพงทอดน้ำปลา",
        "category": "cat_seabass",
        "image_ref": 14,
        "price": 400,
        "target_cost_pct": 36.5,
        "items": [
            {"rm_id": "RM_SEABASS", "portion": 1, "unit": "ตัว", "action": "นับชิ้น", "type": "primary", "note": "ปลากระพงขาวสด 1 ตัว (750-800g) ผ่าผีเสื้อบั้งทอดกรอบฟู"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 180, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันทอดปลาให้สีทองกรอบไม่อมน้ำมัน"},
            {"rm_id": "RM_MANGO_SHREDDED", "portion": 70, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ยำมะม่วงสับเคียงจาน (มะม่วงสับ หอมแดง ถั่วลิสง)"},
            {"rm_id": "RM_SAUCE_YUM", "portion": 40, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำปลาหอมเคี่ยวหวานราดบนตัวปลา"}
        ]
    },
    {
        "id": "D74",
        "name": "02 ปลากระพงแกงส้มแป๊ะซะ",
        "category": "cat_seabass",
        "image_ref": 14,
        "price": 400,
        "target_cost_pct": 37.8,
        "items": [
            {"rm_id": "RM_SEABASS", "portion": 1, "unit": "ตัว", "action": "นับชิ้น", "type": "primary", "note": "ปลากระพงสดทอดกรอบทั้งตัว 1 ตัว (750g)"},
            {"rm_id": "RM_CURRY_SOUP_BASE", "portion": 600, "unit": "ml", "action": "ตวงปริมาตร", "type": "primary", "note": "น้ำแกงส้มสูตรปลาโขลกเข้มข้นเสิร์ฟในหม้อแป๊ะซะรูปปลา"},
            {"rm_id": "RM_WATER_MIMOSA", "portion": 120, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ผักกระเฉดยอดอ่อนและผักกาดขาวรองหม้อแป๊ะซะ"}
        ]
    },
    {
        "id": "D75",
        "name": "03 ปลากระพงทอดกระเทียม",
        "category": "cat_seabass",
        "image_ref": 14,
        "price": 400,
        "target_cost_pct": 36.8,
        "items": [
            {"rm_id": "RM_SEABASS", "portion": 1, "unit": "ตัว", "action": "นับชิ้น", "type": "primary", "note": "ปลากระพงสด 1 ตัว บั้งถี่ทอดกรอบสีทอง"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 100, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กระเทียมไทยเจียวเหลืองกรอบพูนคลุมทั้งตัวปลา"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 180, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันทอดปลาให้กรอบทั่วถึง"}
        ]
    },
    {
        "id": "D76",
        "name": "04 ปลากระพงทอดสามรส",
        "category": "cat_seabass",
        "image_ref": 14,
        "price": 400,
        "target_cost_pct": 36.2,
        "items": [
            {"rm_id": "RM_SEABASS", "portion": 1, "unit": "ตัว", "action": "นับชิ้น", "type": "primary", "note": "ปลากระพงทอดกรอบทั้งตัว 1 ตัว"},
            {"rm_id": "RM_MIXED_VEG", "portion": 120, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ซอสสามรสสับปะรดเต๋า พริกชี้ฟ้า และหอมใหญ่เคี่ยวเข้มข้นราดปลา"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 180, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันทอดปลา"}
        ]
    },
    {
        "id": "D77",
        "name": "05 ปลากระพงนึ่งมะนาว",
        "category": "cat_seabass",
        "image_ref": 14,
        "price": 400,
        "target_cost_pct": 36.5,
        "items": [
            {"rm_id": "RM_SEABASS", "portion": 1, "unit": "ตัว", "action": "นับชิ้น", "type": "primary", "note": "ปลากระพงขาวสด 1 ตัว (750-800g) บั้งนึ่งในจานแป๊ะซะ"},
            {"rm_id": "RM_LIME_JUICE", "portion": 80, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมะนาวคั้นสดแท้ 100% รสเปรี้ยวจัดจ้าน"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 60, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กระเทียมจีนสับหยาบ พริกขี้หนูสวนตำ และคื่นช่าย"}
        ]
    },
    {
        "id": "D78",
        "name": "06 ปลากระพงลวกจิ้ม",
        "category": "cat_seabass",
        "image_ref": 14,
        "price": 400,
        "target_cost_pct": 36.5,
        "items": [
            {"rm_id": "RM_SEABASS", "portion": 1, "unit": "ตัว", "action": "นับชิ้น", "type": "primary", "note": "ปลากระพงสด 1 ตัว แล่เนื้อชิ้นหนาไร้ก้าง ลวกน้ำเดือดสมุนไพร"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 50, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กระเทียมเจียวหอมโรยหน้าเนื้อปลา"},
            {"rm_id": "RM_SAUCE_SEAFOOD", "portion": 100, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำจิ้มซีฟู้ดมะนาวสดแท้ + น้ำจิ้มเต้าเจี้ยว 2 ถ้วย"}
        ]
    },
    {
        "id": "D79",
        "name": "07 ปลากระพงผัดฉ่า",
        "category": "cat_seabass",
        "image_ref": 14,
        "price": 400,
        "target_cost_pct": 36.8,
        "items": [
            {"rm_id": "RM_SEABASS", "portion": 1, "unit": "ตัว", "action": "นับชิ้น", "type": "primary", "note": "เนื้อปลากระพงสด 1 ตัว แล่หั่นชิ้นหนาทอดสะดุ้งน้ำมัน"},
            {"rm_id": "RM_MIXED_VEG", "portion": 80, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กระชายซอย พริกไทยอ่อน ใบมะกรูด โหระพา"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 35, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "พริกขี้หนูตำกระเทียมผัดฉ่าร้อนแรง"}
        ]
    },
    {
        "id": "D80",
        "name": "08 ปลากระพงผัดคื่นช่าย",
        "category": "cat_seabass",
        "image_ref": 14,
        "price": 400,
        "target_cost_pct": 36.5,
        "items": [
            {"rm_id": "RM_SEABASS", "portion": 1, "unit": "ตัว", "action": "นับชิ้น", "type": "primary", "note": "เนื้อปลากระพงสด 1 ตัว แล่ชิ้นทอดพอตึงผิว"},
            {"rm_id": "RM_KALE", "portion": 110, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ผักคื่นช่ายสดคัดต้นอวบกรอบ 110g"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 30, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "เต้าเจี้ยวอย่างดี ขิงแก่ซอย และกระเทียมผัดหอม"}
        ]
    },

    # IMAGE 15: ปลากระพง & ปลาอื่นๆ
    {
        "id": "D81",
        "name": "ต้มยำปลากระพงน้ำใสหม้อไฟ",
        "category": "cat_seabass",
        "image_ref": 15,
        "price": 400,
        "target_cost_pct": 38.0,
        "items": [
            {"rm_id": "RM_SEABASS", "portion": 1, "unit": "ตัว", "action": "นับชิ้น", "type": "primary", "note": "ปลากระพงสด 1 ตัว หั่นท่อนต้มในหม้อไฟน้ำใส"},
            {"rm_id": "RM_MUSHROOM_STRAW", "portion": 80, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "เห็ดฟางสดผ่าครึ่ง"},
            {"rm_id": "RM_LIME_JUICE", "portion": 70, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมะนาวแท้คั้นสด พริกขี้หนูบุบ และกะเพรา"}
        ]
    },
    {
        "id": "D82",
        "name": "ปลากระพงนึ่งซีอิ๊ว",
        "category": "cat_seabass",
        "image_ref": 15,
        "price": 400,
        "target_cost_pct": 36.2,
        "items": [
            {"rm_id": "RM_SEABASS", "portion": 1, "unit": "ตัว", "action": "นับชิ้น", "type": "primary", "note": "ปลากระพงขาวสด 1 ตัว นึ่งซีอิ๊วสไตล์เหลา"},
            {"rm_id": "RM_KALE", "portion": 90, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ต้นหอมซอยเส้น คื่นช่าย และขิงแก่ซอยเส้น"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 40, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันงาคั่วราดหน้าปลาให้หอมฉ่า"}
        ]
    },
    {
        "id": "D83",
        "name": "ปลาเห็ดโคนทอดกระเทียม",
        "category": "cat_seabass",
        "image_ref": 15,
        "price": 200,
        "target_cost_pct": 36.5,
        "items": [
            {"rm_id": "RM_SAND_FISH", "portion": 270, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ปลาเห็ดโคนสดล้างขอดเกล็ด 270g ทอดกรอบเคี้ยวได้ทั้งก้าง"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 55, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กระเทียมเจียวสีทองกรอบหอมโรยพูนตัวปลา"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 70, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันทอดปลาให้กรอบสะเด็ดน้ำมัน"}
        ]
    },
    {
        "id": "D84",
        "name": "ปลาเห็ดโคนทอดราดน้ำปลา",
        "category": "cat_seabass",
        "image_ref": 15,
        "price": 200,
        "target_cost_pct": 36.0,
        "items": [
            {"rm_id": "RM_SAND_FISH", "portion": 270, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ปลาเห็ดโคนสดทอดกรอบสีทอง"},
            {"rm_id": "RM_MANGO_SHREDDED", "portion": 60, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ยำมะม่วงสับเคียงจาน"},
            {"rm_id": "RM_SAUCE_YUM", "portion": 35, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำปลาหอมหวานเคี่ยวราดปลา"}
        ]
    },
    {
        "id": "D85",
        "name": "ปลาอินทรีทอดน้ำปลา",
        "category": "cat_seabass",
        "image_ref": 15,
        "price": 250,
        "target_cost_pct": 36.0,
        "items": [
            {"rm_id": "RM_MACKEREL_STEAK", "portion": 230, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "สเต็กปลาอินทรีสดชิ้นหนา 1 ชิ้นใหญ่ (230g) ทอดสีทองเนื้อฉ่ำ"},
            {"rm_id": "RM_MANGO_SHREDDED", "portion": 70, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ยำมะม่วงเปรี้ยวสับเคียงจาน"},
            {"rm_id": "RM_SAUCE_YUM", "portion": 35, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำปลาแท้เคี่ยวหวานหอมราดปลา"}
        ]
    },
    {
        "id": "D86",
        "name": "ปลาสลิดทอด",
        "category": "cat_seabass",
        "image_ref": 15,
        "price": 200,
        "target_cost_pct": 36.5,
        "items": [
            {"rm_id": "RM_GOURAMI", "portion": 310, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ปลาสลิดแดดเดียวบางบ่อทอดกรอบตัวโต 3 ตัว (310g)"},
            {"rm_id": "RM_MANGO_SHREDDED", "portion": 70, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ยำมะม่วงสับเคียงจาน"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 60, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันทอดปลาสลิดให้กรอบนอกนุ่มใน"}
        ]
    },
    {
        "id": "D87",
        "name": "แกงป่าปลาเห็ดโคน",
        "category": "cat_seabass",
        "image_ref": 15,
        "price": 250,
        "target_cost_pct": 36.8,
        "items": [
            {"rm_id": "RM_SAND_FISH", "portion": 320, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "เนื้อปลาเห็ดโคนสดแล่สะอาด 320g แน่นชาม"},
            {"rm_id": "RM_MIXED_VEG", "portion": 110, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กระชายซอย พริกไทยอ่อน มะเขือเปราะ ถั่วฝักยาว ใบกะเพรา"}
        ]
    },
    {
        "id": "D88",
        "name": "ต้มยำปลากระพงน้ำข้นหม้อไฟ",
        "category": "cat_seabass",
        "image_ref": 15,
        "price": 400,
        "target_cost_pct": 38.8,
        "items": [
            {"rm_id": "RM_SEABASS", "portion": 1, "unit": "ตัว", "action": "นับชิ้น", "type": "primary", "note": "ปลากระพงขาวสด 1 ตัว หั่นท่อนเสิร์ฟหม้อไฟ"},
            {"rm_id": "RM_MUSHROOM_STRAW", "portion": 80, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "เห็ดฟางสดต้มหม้อไฟ"},
            {"rm_id": "RM_LIME_JUICE", "portion": 70, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมะนาวแท้คั้นสด น้ำพริกเผา และนมข้นจืดต้มยำข้น"}
        ]
    },

    # IMAGE 16 & 17: เซ็ตเมนูสุดคุ้ม (Set 1 - 4)
    {
        "id": "D89_SET1",
        "name": "Set 1: เซ็ตคู่ขวัญ (ข้าวผัดใหญ่ + ต้มยำหม้อไฟ)",
        "category": "cat_sets",
        "image_ref": 16,
        "price": 400,
        "target_cost_pct": 36.2,
        "items": [
            {"rm_id": "RM_JASMINE_RICE", "portion": 400, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ข้าวผัดจานใหญ่ (กุ้ง/ปู/ทะเล)"},
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 180, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ซีฟู้ดรวมใส่ข้าวผัดและต้มยำ"},
            {"rm_id": "RM_SQUID_BANANA", "portion": 160, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมึกสดสำหรับต้มยำหม้อไฟและข้าวผัด"},
            {"rm_id": "RM_LIME_JUICE", "portion": 45, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "มะนาวสดปรุงรสต้มยำหม้อไฟ"}
        ]
    },
    {
        "id": "D90_SET2",
        "name": "Set 2: เซ็ต 3 สหายแสนสุข (ข้าวผัดใหญ่ + ปลากระพง + ต้มยำ)",
        "category": "cat_sets",
        "image_ref": 16,
        "price": 750,
        "target_cost_pct": 36.8,
        "items": [
            {"rm_id": "RM_SEABASS", "portion": 1, "unit": "ตัว", "action": "นับชิ้น", "type": "primary", "note": "ปลากระพงขาวสด 1 ตัว (ทอดน้ำปลา/สามรส/นึ่งมะนาว/แป๊ะซะ)"},
            {"rm_id": "RM_JASMINE_RICE", "portion": 400, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ข้าวผัดจานใหญ่ (ทะเล/ปู/กุ้ง)"},
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 180, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งสดสำหรับต้มยำและข้าวผัด"},
            {"rm_id": "RM_SQUID_BANANA", "portion": 160, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมึกกล้วยสด"}
        ]
    },
    {
        "id": "D91_SET3",
        "name": "Set 3: เซ็ต 4 อร่อยครบเครื่อง (+ ยำ 1 จาน)",
        "category": "cat_sets",
        "image_ref": 17,
        "price": 900,
        "target_cost_pct": 37.0,
        "items": [
            {"rm_id": "RM_SEABASS", "portion": 1, "unit": "ตัว", "action": "นับชิ้น", "type": "primary", "note": "ปลากระพงขาวสด 1 ตัว"},
            {"rm_id": "RM_JASMINE_RICE", "portion": 400, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ข้าวผัดจานใหญ่"},
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 220, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งสดรวมในต้มยำ ข้าวผัด และยำ"},
            {"rm_id": "RM_SQUID_BANANA", "portion": 220, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมึกสดรวมใน 3 เมนู"},
            {"rm_id": "RM_SAUCE_YUM", "portion": 60, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำยำรสเด็ดสำหรับจานยำที่ลูกค้าเลือก"}
        ]
    },
    {
        "id": "D92_SET4",
        "name": "Set 4: เซ็ตอภิมหาคุ้ม 5 รายการ (+ ทะเลย่าง/กุ้งย่าง)",
        "category": "cat_sets",
        "image_ref": 17,
        "price": 1200,
        "target_cost_pct": 37.5,
        "items": [
            {"rm_id": "RM_SEABASS", "portion": 1, "unit": "ตัว", "action": "นับชิ้น", "type": "primary", "note": "ปลากระพงสด 1 ตัว"},
            {"rm_id": "RM_SHRIMP_RIVER", "portion": 350, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งแม่น้ำเผา 4-5 ตัว หรือซีฟู้ดย่าง"},
            {"rm_id": "RM_JASMINE_RICE", "portion": 400, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ข้าวผัดจานใหญ่"},
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 220, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวสดสำหรับต้มยำและยำ"},
            {"rm_id": "RM_SQUID_ROE", "portion": 200, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมึกไข่ย่างหรือหมึกต้มยำ"}
        ]
    },

    # IMAGE 18: อาหารตามสั่ง (A La Carte Single Dishes)
    {
        "id": "D93",
        "name": "ข้าวกะเพราไก่ / หมู",
        "category": "cat_alacarte",
        "image_ref": 18,
        "price": 70,
        "target_cost_pct": 35.0,
        "items": [
            {"rm_id": "RM_JASMINE_RICE", "portion": 200, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ข้าวสวยหอมมะลิสุก 200g (1 ทัพพีพูน)"},
            {"rm_id": "RM_PORK_MINCED", "portion": 105, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมูสับหรือเนื้อไก่สับ 105g"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 30, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ใบกะเพราสด พริกแดงจินดาตำกระเทียมไทย"}
        ]
    },
    {
        "id": "D94",
        "name": "ข้าวกะเพรากุ้ง / หมึก / ทะเล",
        "category": "cat_alacarte",
        "image_ref": 18,
        "price": 80,
        "target_cost_pct": 36.5,
        "items": [
            {"rm_id": "RM_JASMINE_RICE", "portion": 200, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ข้าวสวยหอมมะลิ 200g"},
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 50, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวสด 2 ตัว"},
            {"rm_id": "RM_SQUID_BANANA", "portion": 50, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมึกกล้วยบั้ง 4 ชิ้น (รวมซีฟู้ด 100g)"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 30, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ใบกะเพราสด พริกกระเทียมผัดหอมฉุน"}
        ]
    },
    {
        "id": "D95",
        "name": "ข้าวกะเพราไข่เยี่ยวม้าหมูสับ",
        "category": "cat_alacarte",
        "image_ref": 18,
        "price": 80,
        "target_cost_pct": 38.5,
        "items": [
            {"rm_id": "RM_JASMINE_RICE", "portion": 200, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ข้าวสวย 200g"},
            {"rm_id": "RM_EGG_CENTURY", "portion": 1, "unit": "ฟอง", "action": "นับชิ้น", "type": "primary", "note": "ไข่เยี่ยวม้า 1 ฟอง ทอดผิวด้านนอกตึงหั่น 4 ซีก"},
            {"rm_id": "RM_PORK_MINCED", "portion": 65, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมูสับหมัก 65g ผัดกะเพรากรอบราด"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 25, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ใบกะเพราทอดกรอบโรยหน้า"}
        ]
    },
    {
        "id": "D96",
        "name": "ข้าวกะเพราหมูกรอบ",
        "category": "cat_alacarte",
        "image_ref": 18,
        "price": 80,
        "target_cost_pct": 36.8,
        "items": [
            {"rm_id": "RM_JASMINE_RICE", "portion": 200, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ข้าวสวย 200g"},
            {"rm_id": "RM_PORK_CRISPY", "portion": 70, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมูกรอบสับชิ้นเต๋า 70g หนังกรอบฟู"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 30, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ใบกะเพรา พริกกระเทียมผัดคั่วแห้ง"}
        ]
    },
    {
        "id": "D97",
        "name": "ข้าวผัดไก่ / หมู (จานเดียว S)",
        "category": "cat_alacarte",
        "image_ref": 18,
        "price": 70,
        "target_cost_pct": 35.0,
        "items": [
            {"rm_id": "RM_JASMINE_RICE", "portion": 200, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ข้าวสวยหอมมะลิ 200g"},
            {"rm_id": "RM_PORK_SLICED", "portion": 80, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "เนื้อหมู/ไก่หมักนุ่ม 80g"},
            {"rm_id": "RM_EGG_FRESH", "portion": 1, "unit": "ฟอง", "action": "นับชิ้น", "type": "primary", "note": "ไข่ไก่สด 1 ฟอง"},
            {"rm_id": "RM_KALE", "portion": 30, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "แตงกวา มะนาว ต้นหอมเคียง"}
        ]
    },
    {
        "id": "D98",
        "name": "ข้าวผัดกุ้ง / หมึก / ทะเล (จานเดียว S)",
        "category": "cat_alacarte",
        "image_ref": 18,
        "price": 80,
        "target_cost_pct": 37.0,
        "items": [
            {"rm_id": "RM_JASMINE_RICE", "portion": 200, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ข้าวสวยหอมมะลิ 200g"},
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 45, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวสด 2 ตัว"},
            {"rm_id": "RM_SQUID_BANANA", "portion": 45, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมึกสดบั้งสวย"},
            {"rm_id": "RM_EGG_FRESH", "portion": 1, "unit": "ฟอง", "action": "นับชิ้น", "type": "secondary", "note": "ไข่ไก่สด 1 ฟอง"}
        ]
    },
    {
        "id": "D99",
        "name": "ผัดซีอิ๊วไก่ / หมู",
        "category": "cat_alacarte",
        "image_ref": 18,
        "price": 70,
        "target_cost_pct": 35.8,
        "items": [
            {"rm_id": "RM_FLAT_NOODLES", "portion": 160, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ก๋วยเตี๋ยวเส้นใหญ่สด 160g คั่วหอมไหม้กระทะ"},
            {"rm_id": "RM_PORK_SLICED", "portion": 85, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมู/ไก่หมักนุ่ม 85g"},
            {"rm_id": "RM_EGG_FRESH", "portion": 1, "unit": "ฟอง", "action": "นับชิ้น", "type": "primary", "note": "ไข่ไก่สด 1 ฟอง"},
            {"rm_id": "RM_KALE", "portion": 70, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ยอดคะน้ากรอบลอกก้าน"}
        ]
    },
    {
        "id": "D100",
        "name": "ผัดซีอิ๊วกุ้ง / หมึก / ทะเล",
        "category": "cat_alacarte",
        "image_ref": 18,
        "price": 80,
        "target_cost_pct": 37.5,
        "items": [
            {"rm_id": "RM_FLAT_NOODLES", "portion": 160, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ก๋วยเตี๋ยวเส้นใหญ่สด 160g"},
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 45, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวสด 2 ตัว"},
            {"rm_id": "RM_SQUID_BANANA", "portion": 45, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมึกสดบั้ง"},
            {"rm_id": "RM_EGG_FRESH", "portion": 1, "unit": "ฟอง", "action": "นับชิ้น", "type": "secondary", "note": "ไข่ไก่ 1 ฟอง"},
            {"rm_id": "RM_KALE", "portion": 70, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ยอดคะน้ากรอบ"}
        ]
    },
    {
        "id": "D101",
        "name": "ข้าวกระเทียมหมู / ไก่",
        "category": "cat_alacarte",
        "image_ref": 18,
        "price": 70,
        "target_cost_pct": 36.0,
        "items": [
            {"rm_id": "RM_JASMINE_RICE", "portion": 200, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ข้าวสวยหอมมะลิ 200g"},
            {"rm_id": "RM_PORK_SLICED", "portion": 105, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมู/ไก่หมักนุ่ม 105g"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 30, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กระเทียมสับเจียวกรอบหอมโรยพูน"}
        ]
    },
    {
        "id": "D102",
        "name": "ข้าวกระเทียมกุ้ง / หมึก / ทะเล",
        "category": "cat_alacarte",
        "image_ref": 18,
        "price": 80,
        "target_cost_pct": 37.5,
        "items": [
            {"rm_id": "RM_JASMINE_RICE", "portion": 200, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ข้าวสวยหอมมะลิ 200g"},
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 50, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวสด 2 ตัว"},
            {"rm_id": "RM_SQUID_BANANA", "portion": 50, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมึกสดบั้ง"},
            {"rm_id": "RM_GARLIC_CRISPY", "portion": 30, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "กระเทียมเจียวกรอบสีทอง"}
        ]
    },
    {
        "id": "D103",
        "name": "ข้าวคะน้าหมูกรอบ",
        "category": "cat_alacarte",
        "image_ref": 18,
        "price": 80,
        "target_cost_pct": 37.0,
        "items": [
            {"rm_id": "RM_JASMINE_RICE", "portion": 200, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ข้าวสวย 200g"},
            {"rm_id": "RM_PORK_CRISPY", "portion": 70, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมูกรอบชิ้นหนา 70g"},
            {"rm_id": "RM_KALE", "portion": 80, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ยอดคะน้ากรอบลอกก้าน"}
        ]
    },
    {
        "id": "D104",
        "name": "สุกี้น้ำ / แห้ง หมู / ไก่",
        "category": "cat_alacarte",
        "image_ref": 18,
        "price": 70,
        "target_cost_pct": 36.5,
        "items": [
            {"rm_id": "RM_GLASS_NOODLES", "portion": 90, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "วุ้นเส้นสด 90g"},
            {"rm_id": "RM_PORK_SLICED", "portion": 85, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมู/ไก่หมักนุ่ม 85g"},
            {"rm_id": "RM_EGG_FRESH", "portion": 1, "unit": "ฟอง", "action": "นับชิ้น", "type": "primary", "note": "ไข่ไก่สด 1 ฟอง"},
            {"rm_id": "RM_MORNING_GLORY", "portion": 90, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ผักบุ้ง ผักกาดขาว ขึ้นฉ่าย และน้ำจิ้มสุกี้เต้าหู้ยี้"}
        ]
    },
    {
        "id": "D105",
        "name": "สุกี้น้ำ / แห้ง กุ้ง / หมึก / ทะเล",
        "category": "cat_alacarte",
        "image_ref": 18,
        "price": 80,
        "target_cost_pct": 37.8,
        "items": [
            {"rm_id": "RM_GLASS_NOODLES", "portion": 90, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "วุ้นเส้นสด 90g"},
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 45, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวสด 2 ตัว"},
            {"rm_id": "RM_SQUID_BANANA", "portion": 45, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมึกสดบั้ง"},
            {"rm_id": "RM_EGG_FRESH", "portion": 1, "unit": "ฟอง", "action": "นับชิ้น", "type": "secondary", "note": "ไข่ไก่สด 1 ฟอง"},
            {"rm_id": "RM_MORNING_GLORY", "portion": 90, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ผักบุ้งและผักกาดขาว"}
        ]
    },
    {
        "id": "D106",
        "name": "ราดหน้าหมู / ไก่",
        "category": "cat_alacarte",
        "image_ref": 18,
        "price": 70,
        "target_cost_pct": 35.0,
        "items": [
            {"rm_id": "RM_FLAT_NOODLES", "portion": 160, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "เส้นใหญ่ผัดคั่วกระทะหอม 160g"},
            {"rm_id": "RM_PORK_SLICED", "portion": 85, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมู/ไก่หมักเต้าเจี้ยวนุ่ม 85g"},
            {"rm_id": "RM_KALE", "portion": 80, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ยอดคะน้ากรอบในน้ำราดหน้าน้ำซุปกระดูก"}
        ]
    },
    {
        "id": "D107",
        "name": "ราดหน้ากุ้ง / หมึก / ทะเล",
        "category": "cat_alacarte",
        "image_ref": 18,
        "price": 80,
        "target_cost_pct": 37.0,
        "items": [
            {"rm_id": "RM_FLAT_NOODLES", "portion": 160, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "เส้นใหญ่ผัดซีอิ๊วหอมกระทะ"},
            {"rm_id": "RM_SHRIMP_WHITE", "portion": 45, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "กุ้งขาวสด 2 ตัว"},
            {"rm_id": "RM_SQUID_BANANA", "portion": 45, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมึกสดบั้ง"},
            {"rm_id": "RM_KALE", "portion": 80, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "secondary", "note": "ยอดคะน้าฮ่องกงกรอบ"}
        ]
    },
    {
        "id": "D108",
        "name": "ข้าวไข่เจียวหมูสับ (จานด่วน)",
        "category": "cat_alacarte",
        "image_ref": 18,
        "price": 70,
        "target_cost_pct": 36.0,
        "items": [
            {"rm_id": "RM_JASMINE_RICE", "portion": 200, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "ข้าวสวยหอมมะลิ 200g"},
            {"rm_id": "RM_EGG_FRESH", "portion": 2, "unit": "ฟอง", "action": "นับชิ้น", "type": "primary", "note": "ไข่ไก่สด 2 ฟอง"},
            {"rm_id": "RM_PORK_MINCED", "portion": 55, "unit": "g", "action": "ชั่งน้ำหนัก", "type": "primary", "note": "หมูสับหมัก 55g"},
            {"rm_id": "RM_FRYING_OIL_PORTION", "portion": 50, "unit": "ml", "action": "ตวงปริมาตร", "type": "secondary", "note": "น้ำมันทอดไข่ฟูกรอบ"}
        ]
    }
]

# 4. Beverage & Extras Database (Buy-and-sell items from Image 12 & 18 toppings)
beverages_data = [
    {"name": "เบียร์สิงห์ (ขวดใหญ่)", "price": 90, "cost": 58, "margin": 35.6, "unit": "ขวด"},
    {"name": "เบียร์ช้าง (ขวดใหญ่)", "price": 75, "cost": 50, "margin": 33.3, "unit": "ขวด"},
    {"name": "เบียร์ลีโอ (ขวดใหญ่)", "price": 80, "cost": 52, "margin": 35.0, "unit": "ขวด"},
    {"name": "เบียร์ไฮเนเก้น (ขวดใหญ่)", "price": 100, "cost": 68, "margin": 32.0, "unit": "ขวด"},
    {"name": "เบียร์โฮกาเด้น (กระป๋อง)", "price": 140, "cost": 92, "margin": 34.3, "unit": "กระป๋อง"},
    {"name": "รีเจนซี่ (แบน)", "price": 480, "cost": 310, "margin": 35.4, "unit": "แบน"},
    {"name": "รีเจนซี่ (กลม)", "price": 680, "cost": 480, "margin": 29.4, "unit": "กลม"},
    {"name": "285 ดำ (กลม)", "price": 380, "cost": 255, "margin": 32.9, "unit": "กลม"},
    {"name": "285 ทอง (กลม)", "price": 380, "cost": 265, "margin": 30.3, "unit": "กลม"},
    {"name": "แสงโสม (แบน)", "price": 190, "cost": 130, "margin": 31.6, "unit": "แบน"},
    {"name": "แสงโสม (กลม)", "price": 380, "cost": 250, "margin": 34.2, "unit": "กลม"},
    {"name": "หงส์ทอง (แบน)", "price": 190, "cost": 130, "margin": 31.6, "unit": "แบน"},
    {"name": "หงส์ทอง (กลม)", "price": 380, "cost": 240, "margin": 36.8, "unit": "กลม"},
    {"name": "meridian (แบน)", "price": 380, "cost": 260, "margin": 31.6, "unit": "แบน"},
    {"name": "meridian (กลม)", "price": 680, "cost": 480, "margin": 29.4, "unit": "กลม"},
    {"name": "น้ำเปล่า (ขวดเล็ก)", "price": 15, "cost": 5, "margin": 66.7, "unit": "ขวด"},
    {"name": "น้ำเปล่า (ขวดใหญ่)", "price": 25, "cost": 8, "margin": 68.0, "unit": "ขวด"},
    {"name": "โซดาสิงห์", "price": 15, "cost": 7.5, "margin": 50.0, "unit": "ขวด"},
    {"name": "โค้ก / แฟนต้า (ขวดใหญ่)", "price": 45, "cost": 27, "margin": 40.0, "unit": "ขวด"},
    {"name": "โค้ก / แฟนต้า (ขวดเล็ก)", "price": 25, "cost": 12, "margin": 52.0, "unit": "ขวด"},
    {"name": "น้ำแข็ง (ถังเล็ก)", "price": 25, "cost": 6, "margin": 76.0, "unit": "ถัง"},
    {"name": "น้ำแข็ง (ถังใหญ่)", "price": 30, "cost": 10, "margin": 66.7, "unit": "ถัง"},
    {"name": "+ไข่ดาว (ท็อปปิ้ง)", "price": 10, "cost": 4.5 + 1.2, "margin": 43.0, "unit": "ฟอง"},
    {"name": "+ไข่เจียว (ท็อปปิ้ง)", "price": 15, "cost": 4.5 + 1.8, "margin": 58.0, "unit": "ฟอง"}
]

# Calculate costs and margins for dishes
for dish in dishes_data:
    primary_secondary_cost = 0.0
    for item in dish["items"]:
        rm = raw_materials.get(item["rm_id"])
        if rm:
            unit_cost = rm["market_price"]
            item_cost = round(unit_cost * item["portion"], 2)
            item["unit_cost"] = unit_cost
            item["item_cost"] = item_cost
            item["rm_name"] = rm["name"]
            item["display_unit"] = rm["display_unit"]
            primary_secondary_cost += item_cost
    
    # Seasoning & Minor aromatics allowance (e.g. fish sauce, sugar, salt, MSG) ~ 2-3% of dish
    # The requirement specifically mentions:
    # "ต้นทุนรวม (Total Food Cost): บังคับควบคุมให้ไม่เกิน 40% ของราคาขายหน้าป้าย"
    # "ต้นทุนหลักและต้นทุนรอง (ส่วนที่ต้องแสดงผล): กำหนดเป้าหมายที่ 35% (ยืดหยุ่น 35% - 40%)"
    minor_seasoning_cost = round(dish["price"] * 0.025, 2) # 2.5% minor allowance
    total_cost = round(primary_secondary_cost + minor_seasoning_cost, 2)
    
    ps_cost_pct = round((primary_secondary_cost / dish["price"]) * 100, 1)
    total_cost_pct = round((total_cost / dish["price"]) * 100, 1)
    gross_profit = round(dish["price"] - total_cost, 2)
    gross_margin_pct = round((gross_profit / dish["price"]) * 100, 1)
    
    dish["primary_secondary_cost"] = round(primary_secondary_cost, 2)
    dish["minor_seasoning_cost"] = minor_seasoning_cost
    dish["total_cost"] = total_cost
    dish["ps_cost_pct"] = ps_cost_pct
    dish["total_cost_pct"] = total_cost_pct
    dish["gross_profit"] = gross_profit
    dish["gross_margin_pct"] = gross_margin_pct
    dish["is_target_compliant"] = (total_cost_pct <= 40.0 and gross_margin_pct >= 60.0)

# Save to data.json
database = {
    "restaurant_info": {
        "name": "ครัวแสนสุข",
        "concept": "อาหารทะเล สด สะอาด รสจัดจ้าน | บ้านพักเป็นหลัง 24 ชม.",
        "phone": "080-143-2563",
        "last_market_sync": "2026-10-10",
        "next_market_sync": "2026-10-17",
        "target_max_food_cost": 40.0,
        "target_min_gross_margin": 60.0,
        "target_ps_cost_min": 35.0,
        "target_ps_cost_max": 40.0
    },
    "raw_materials": raw_materials,
    "categories": categories,
    "dishes": dishes_data,
    "beverages": beverages_data
}

output_path = os.path.join(os.path.dirname(__file__), "data.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(database, f, ensure_ascii=False, indent=2)

print(f"Successfully generated data.json with {len(dishes_data)} dishes and {len(raw_materials)} raw materials!")
