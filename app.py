import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import time

# 1. الإعدادات الأساسية
st.set_page_config(page_title="Wahba EGX | Institutional Terminal", layout="wide")

# 2. الواجهة الاحترافية (بدون إيموجي، ألوان مؤسسية)
st.markdown("""
    <style>
    /* تنسيق العنوان الرئيسي */
    .main-header {
        text-align: center;
        padding: 30px 0;
        border-bottom: 1px solid #333;
        margin-bottom: 40px;
    }
    .brand-name {
        font-family: 'Inter', sans-serif;
        font-size: 45px;
        font-weight: 800;
        letter-spacing: -1px;
        color: var(--text-color);
        margin: 0;
    }
    .brand-tagline {
        font-size: 12px;
        letter-spacing: 5px;
        text-transform: uppercase;
        opacity: 0.6;
        margin-top: 10px;
    }
    /* علامة الحالة الخضراء */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        background-color: #00ff00;
        border-radius: 50%;
        margin-right: 10px;
        box-shadow: 0 0 8px #00ff00;
    }
    /* تنسيق الجداول */
    .stTable {
        border: 1px solid #222;
        border-radius: 8px;
    }
    </style>
    
    <div class="main-header">
        <h1 class="brand-name">WAHBA EGX</h1>
        <div class="brand-tagline">Institutional Market Terminal • Live Data Stream</div>
    </div>
""", unsafe_allow_html=True)

# 3. دالة جلب الرموز أوتوماتيكياً (لضمان إضافة أي سهم جديد)
@st.cache_data(ttl=3600)
def get_live_symbols():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter":[],"options":{"lang":"en"},"markets":["egypt"]}, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data']]
    except:
        # قائمة للطوارئ
        return ["COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "PHDC", "HRHO", "ESRS"]

def check_logic(symbol):
    try:
        # تأخير بسيط لتجنب الحظر
        time.sleep(0.05) 
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

# 4. التحكم في التشغيل والنتائج
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button('INITIALIZE FULL MARKET SCAN', use_container_width=True):
        all_stocks = get_live_symbols()
        total = len(all_stocks)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        results = []
        with st.spinner('Accessing Terminal Data...'):
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = [executor.submit(check_logic, s) for s in all_stocks]
                for i, future in enumerate(futures):
                    res = future.result()
                    if res: results.append(res)
                    progress_bar.progress((i + 1) / total)
                    status_text.markdown(f"**Scanning Asset:** `{all_stocks[i]}` ({i+1}/{total})")

            status_text.empty()
            progress_bar.empty()

            if results:
                st.markdown(f"### <div class='status-indicator'></div> Identified Opportunities", unsafe_allow_html=True)
                df = pd.DataFrame(results)
                st.table(df.sort_values(by="Signal", ascending=False))
                
                # قسم الـ STRONG BUY الاحترافي
                strong_buys = [item for item in results if "STRONG BUY" in item["Signal"]]
                if strong_buys:
                    st.divider()
                    st.markdown("### <div class='status-indicator'></div> High-Priority Momentum (Strong Buy)", unsafe_allow_html=True)
                    st.table(pd.DataFrame(strong_buys))
            else:
                st.warning("Analysis Complete: No assets currently meeting the criteria.")

# تذييل الصفحة الرسمي
st.divider()
st.caption("WAHBA EGX | INSTITUTIONAL TERMINAL | DATA SOURCE: TRADINGVIEW | © 2026")
