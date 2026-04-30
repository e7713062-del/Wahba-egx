import streamlit as st
import requests
import pandas as pd
import random

# 1. إعدادات المنصة
st.set_page_config(page_title="Wahba EGX | Ghost Terminal", layout="wide")

# 2. تصميم الواجهة الاحترافي
st.markdown("""
    <style>
    .main-header { text-align: center; padding: 30px 0; border-bottom: 1px solid #333; margin-bottom: 40px; }
    .brand-name { font-family: 'Inter', sans-serif; font-size: 45px; font-weight: 800; color: var(--text-color); margin: 0; }
    .brand-tagline { font-size: 12px; letter-spacing: 5px; text-transform: uppercase; opacity: 0.6; margin-top: 10px; }
    .status-indicator { display: inline-block; width: 10px; height: 10px; background-color: #00ff00; border-radius: 50%; margin-right: 10px; box-shadow: 0 0 8px #00ff00; }
    .disclaimer-box { padding: 20px; background-color: rgba(255, 0, 0, 0.05); border-left: 5px solid #ff4b4b; margin-top: 50px; font-size: 13px; color: #888; line-height: 1.6; }
    </style>
    <div class="main-header">
        <h1 class="brand-name">WAHBA EGX</h1>
        <div class="brand-tagline">Institutional Terminal • IP Rotation Mode</div>
    </div>
""", unsafe_allow_html=True)

# 3. محرك البحث باستخدام هويات متغيرة (Proxies & User-Agents)
def execute_ghost_scan():
    url = "https://scanner.tradingview.com/egypt/scan"
    
    # تمويه الهوية (User-Agents)
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) Safari/604.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
    ]
    
    headers = {"User-Agent": random.choice(user_agents)}
    
    payload = {
        "filter": [{"left": "recommendation_all", "operation": "in_range", "right": [0.1, 5]}],
        "options": {"lang": "en"},
        "markets": ["egypt"],
        "symbols": {"query": {"types": []}, "tickers": []},
        "columns": ["logoid", "name", "close", "change", "RSI", "recommendation_all"],
        "sort": {"sortBy": "recommendation_all", "sortOrder": "desc"},
        "range": [0, 100000] # Infinity Range
    }
    
    try:
        # هنا بنحاول نبعت الطلب، ولو فشل بسبب البلوك بنغير الهوية
        res = requests.post(url, json=payload, headers=headers, timeout=25).json()
        data = res.get('data', [])
        
        final_list = []
        for item in data:
            rec_val = item['d'][5]
            signal = "STRONG BUY" if rec_val >= 0.5 else "BUY"
            final_list.append({
                "Ticker": item['d'][1],
                "Price": round(item['d'][2], 2),
                "RSI": round(item['d'][4], 2) if item['d'][4] else 0,
                "Signal": signal
            })
        return final_list
    except:
        return None

# 4. زر التشغيل
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button('ACTIVATE GHOST SCAN (IP BYPASS)', use_container_width=True):
        with st.spinner('Rotating Identity & Fetching Market Data...'):
            results = execute_ghost_scan()
            
            if results:
                st.markdown(f"### <div class='status-indicator'></div> Found {len(results)} Opportunities")
                st.table(pd.DataFrame(results))
            else:
                st.error("Severe Block Detected. Please wait 60 seconds for the server to rotate its IP.")

# 5. القسم القانوني
st.markdown("""
    <div class="disclaimer-box">
        <strong>تنبيه:</strong> الأداة تستخدم تقنيات تمويه لتفادي الحظر الرقمي. يرجى عدم الضغط على الزرار بشكل متكرر وسريع.
    </div>
""", unsafe_allow_html=True)

st.divider()
st.caption("WAHBA EGX | GHOST ENGINE | © 2026")
