import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import time
import random

# 1. الإعدادات المؤسسية
st.set_page_config(page_title="Wahba EGX | Terminal", layout="wide")

# 2. تصميم الواجهة الاحترافي
st.markdown("""
    <style>
    .main-header { text-align: center; padding: 30px 0; border-bottom: 1px solid #333; margin-bottom: 40px; }
    .brand-name { font-family: 'Inter', sans-serif; font-size: 45px; font-weight: 800; letter-spacing: -1px; color: var(--text-color); margin: 0; }
    .brand-tagline { font-size: 12px; letter-spacing: 5px; text-transform: uppercase; opacity: 0.6; margin-top: 10px; }
    .status-indicator { display: inline-block; width: 10px; height: 10px; background-color: #00ff00; border-radius: 50%; margin-right: 10px; box-shadow: 0 0 8px #00ff00; }
    </style>
    <div class="main-header">
        <h1 class="brand-name">WAHBA EGX</h1>
        <div class="brand-tagline">Institutional Market Terminal • Live Data Stream</div>
    </div>
""", unsafe_allow_html=True)

# 3. جلب الرموز أوتوماتيكياً (لضمان إضافة أي سهم جديد)
@st.cache_data(ttl=3600)
def get_live_symbols():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.post(url, json={"filter":[],"options":{"lang":"en"},"markets":["egypt"]}, headers=headers, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data']]
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "PHDC", "HRHO", "ESRS"]

def check_logic(symbol):
    try:
        # فاصل زمني لتجنب البلوك
        time.sleep(random.uniform(0.1, 0.3)) 
        handler = TA_Handler(
            symbol=symbol, screener="egypt", exchange="EGX",
            interval=Interval.INTERVAL_1_DAY, timeout=10
        )
        analysis = handler.get_analysis()
        rec = analysis.summary["RECOMMENDATION"]
        ind = analysis.indicators
        
        if "BUY" in rec:
            return {
                "Ticker": symbol,
                "Price": round(ind["close"], 2),
                "RSI": round(ind["RSI"], 2),
                "Signal": rec.replace("_", " ")
            }
    except: return None

# 4. التحكم والتشغيل مع إظهار السهم الجاري تحميله
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button('ESTABLISH FULL MARKET SCAN', use_container_width=True):
        all_stocks = get_live_symbols()
        total = len(all_stocks)
        
        # عناصر التحميل
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        
        results = []
        # استخدام عدد متوازن من الـ workers لتجنب البلوك مع الحفاظ على السرعة
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(check_logic, s) for s in all_stocks]
            for i, future in enumerate(futures):
                res = future.result()
                if res: results.append(res)
                
                # تحديث الشريط واسم السهم فوراً قدامك
                progress_bar.progress((i + 1) / total)
                status_placeholder.markdown(f"🔍 **Processing:** `{all_stocks[i]}` ({i+1}/{total})")

        status_placeholder.empty()
        progress_bar.empty()

        if results:
            st.markdown(f"### <div class='status-indicator'></div> Identified Opportunities", unsafe_allow_html=True)
            df = pd.DataFrame(results)
            st.table(df.sort_values(by="Signal", ascending=False))
            
            strong_buys = [item for item in results if "STRONG BUY" in item["Signal"]]
            if strong_buys:
                st.divider()
                st.markdown("### <div class='status-indicator'></div> Institutional Priority (Strong Buy)", unsafe_allow_html=True)
                st.table(pd.DataFrame(strong_buys))
        else:
            st.info("Analysis Complete: No assets currently match the defined growth protocol.")

st.divider()
st.caption("WAHBA EGX | INSTITUTIONAL TERMINAL | © 2026")
