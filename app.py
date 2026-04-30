import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests

# 1. الإعدادات الأساسية
st.set_page_config(page_title="Wahba EGX | Terminal", layout="wide")

# 2. تصميم الواجهة (في المنتصف وبدون لوجو كما طلبت)
st.markdown("""
    <style>
    .main-header { text-align: center; padding: 20px; }
    .brand-name {
        font-family: 'Inter', sans-serif;
        font-size: 50px;
        font-weight: 900;
        margin: 0;
        letter-spacing: -2px;
        text-transform: uppercase;
        color: var(--text-color);
    }
    .brand-tagline { font-size: 14px; letter-spacing: 3px; opacity: 0.8; }
    </style>
    <div class="main-header">
        <h1 class="brand-name">Wahba EGX</h1>
        <p class="brand-tagline">OFFICIAL LIVE AUTO-SCANNER | EGYPT STOCK EXCHANGE</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# 3. دالة جلب كل رموز مصر أوتوماتيكياً (تحديث تلقائي)
@st.cache_data(ttl=3600)
def get_live_symbols():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {"filter":[],"options":{"lang":"en"},"markets":["egypt"],"symbols":{"query":{"types":[]},"tickers":[]},"columns":["name"]}
        res = requests.post(url, json=payload, timeout=10).json()
        return [item['s'].split(':')[1] for item in res['data']]
    except:
        # قائمة احتياطية في حال تعطل السيرفر
        return ["COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "PHDC", "HRHO", "ESRS"]

def check_logic(symbol):
    try:
        handler = TA_Handler(
            symbol=symbol, screener="egypt", exchange="EGX",
            interval=Interval.INTERVAL_1_DAY, timeout=10
        )
        analysis = handler.get_analysis()
        d = analysis.indicators
        rec = analysis.summary["RECOMMENDATION"]
        
        # تعديل بسيط في الشرط ليكون أكثر مرونة ويظهر نتائج
        if d["close"] > d["SMA10"] and "BUY" in rec:
            return {
                "Ticker": symbol,
                "Price": round(d["close"], 2),
                "RSI": round(d["RSI"], 2) if d["RSI"] else 0,
                "Signal": rec.replace("_", " ")
            }
    except: return None

# 4. تنفيذ المسح
if st.button('START FULL MARKET AUTO-SCAN'):
    symbols = get_live_symbols()
    
    with st.spinner(f'Analyzing {len(symbols)} Live Assets...'):
        with ThreadPoolExecutor(max_workers=30) as executor:
            res = list(executor.map(check_logic, symbols))
        
        final = [item for item in res if item is not None]
        
        if final:
            st.success(f"Identification Complete: {len(final)} Bullish Assets Found")
            df = pd.DataFrame(final)
            st.table(df.sort_values(by="Signal", ascending=False)) # ترتيب حسب قوة الإشارة
            
            # قسم الـ STRONG BUY
            strong_buys = [item for item in final if "STRONG BUY" in item["Signal"]]
            if strong_buys:
                st.markdown("---")
                st.markdown("### 🔥 Top Priority: STRONG BUY Opportunities")
                st.table(pd.DataFrame(strong_buys))
        else:
            st.warning("No assets currently match the defined growth protocol. Try scanning again later.")

st.divider()
st.caption("WAHBA EGX | FULL AUTO-UPDATE SYSTEM | © 2026")
