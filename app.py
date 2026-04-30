import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import time
import random

# 1. الإعدادات المؤسسية
st.set_page_config(page_title="Wahba EGX | Terminal", layout="wide")

# 2. تصميم الواجهة الاحترافي (بدون إيموجي)
st.markdown("""
    <style>
    .main-header { text-align: center; padding: 30px 0; border-bottom: 1px solid #333; margin-bottom: 40px; }
    .brand-name { font-family: 'Inter', sans-serif; font-size: 45px; font-weight: 800; color: var(--text-color); margin: 0; }
    .brand-tagline { font-size: 12px; letter-spacing: 5px; text-transform: uppercase; opacity: 0.6; margin-top: 10px; }
    .status-indicator { display: inline-block; width: 10px; height: 10px; background-color: #00ff00; border-radius: 50%; margin-right: 10px; box-shadow: 0 0 8px #00ff00; }
    </style>
    <div class="main-header">
        <h1 class="brand-name">WAHBA EGX</h1>
        <div class="brand-tagline">Institutional Market Terminal • Stable Connection</div>
    </div>
""", unsafe_allow_html=True)

# 3. جلب الرموز أوتوماتيكياً (لضمان إضافة أي سهم جديد)
@st.cache_data(ttl=3600)
def get_live_symbols():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        res = requests.post(url, json={"filter":[],"options":{"lang":"en"},"markets":["egypt"]}, headers=headers, timeout=20).json()
        return [item['s'].split(':')[1] for item in res['data']]
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "ABUK", "HRHO", "PHDC"]

def check_logic(symbol):
    try:
        # فاصل زمني عشوائي لفك البلوك وتجنب التعليق
        time.sleep(random.uniform(0.3, 0.7)) 
        
        handler = TA_Handler(
            symbol=symbol, screener="egypt", exchange="EGX",
            interval=Interval.INTERVAL_1_DAY, timeout=15 # زيادة المهلة
        )
        analysis = handler.get_analysis()
        rec = analysis.summary["RECOMMENDATION"]
        ind = analysis.indicators
        
        # شرط مرن وشامل للاستقرار
        if "BUY" in rec:
            return {
                "Ticker": symbol,
                "Price": round(ind["close"], 2),
                "RSI": round(ind["RSI"], 2) if ind["RSI"] else 0,
                "Signal": rec.replace("_", " ")
            }
    except: return None

# 4. التحكم والتشغيل
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button('ESTABLISH SECURE MARKET SCAN', use_container_width=True):
        all_stocks = get_live_symbols()
        total = len(all_stocks)
        
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        
        results = []
        # تقليل الـ workers لـ 4 لضمان استقرار الاتصال وعدم التعليق
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(check_logic, s) for s in all_stocks]
            for i, future in enumerate(futures):
                res = future.result()
                if res: results.append(res)
                
                # إظهار السهم الجاري تحميله كما طلبت
                progress_bar.progress((i + 1) / total)
                status_placeholder.markdown(f"**Synchronizing Data:** `{all_stocks[i]}` ({i+1}/{total})")

        status_placeholder.empty()
        progress_bar.empty()

        if results:
            st.markdown(f"### <div class='status-indicator'></div> Identified Opportunities", unsafe_allow_html=True)
            df = pd.DataFrame(results)
            st.table(df.sort_values(by="Signal", ascending=False))
            
            strong_buys = [item for item in results if "STRONG BUY" in item["Signal"]]
            if strong_buys:
                st.divider()
                st.markdown("### <div class='status-indicator'></div> High-Priority Assets (Strong Buy)", unsafe_allow_html=True)
                st.table(pd.DataFrame(strong_buys))
        else:
            st.info("Analysis Complete: No assets currently match the defined growth protocol.")

st.divider()
st.caption("WAHBA EGX | INSTITUTIONAL TERMINAL | © 2026")
