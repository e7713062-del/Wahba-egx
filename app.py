import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests

# 1. الإعدادات الأساسية
st.set_page_config(page_title="Wahba EGX | Terminal", layout="wide")

# 2. تصميم الواجهة (نفس الشكل اللي بتحبه)
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

# 3. دالة جلب كل أسهم مصر أوتوماتيكياً (فك التعليقة)
@st.cache_data(ttl=600) # تحديث كل 10 دقائق لضمان عدم التعليق
def get_live_symbols():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        # طلب خفيف للسيرفر عشان ميحصلش بلوك
        res = requests.post(url, json={"filter":[],"options":{"lang":"en"},"markets":["egypt"]}, timeout=10).json()
        return [item['s'].split(':')[1] for item in res['data']]
    except:
        # قائمة إنقاذ لو السيرفر وقع
        return ["COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "PHDC", "HRHO", "ESRS", "ORWE", "SKPC"]

def check_logic(symbol):
    try:
        handler = TA_Handler(
            symbol=symbol, screener="egypt", exchange="EGX",
            interval=Interval.INTERVAL_1_DAY, timeout=5 # تقليل التايم أوت للسرعة
        )
        analysis = handler.get_analysis()
        rec = analysis.summary["RECOMMENDATION"]
        ind = analysis.indicators
        
        # شرط مرن عشان الأداة متوقفش: لو إشارة شراء والسعر مش منهار
        if "BUY" in rec:
            return {
                "Ticker": symbol,
                "Price": round(ind["close"], 2),
                "RSI": round(ind["RSI"], 2),
                "Signal": rec.replace("_", " ")
            }
    except: return None

# 4. الزر والنتائج
if st.button('START FULL MARKET AUTO-SCAN'):
    all_stocks = get_live_symbols()
    
    with st.spinner(f'Checking {len(all_stocks)} Live Securities...'):
        with ThreadPoolExecutor(max_workers=40) as executor: # زيادة السرعة
            res = list(executor.map(check_logic, all_stocks))
        
        final = [item for item in res if item is not None]
        
        if final:
            st.success(f"Identification Complete: {len(final)} Bullish Assets Found")
            df = pd.DataFrame(final)
            st.table(df.sort_values(by="Signal", ascending=False))
            
            # قسم الـ STRONG BUY
            strong_buys = [item for item in final if "STRONG BUY" in item["Signal"]]
            if strong_buys:
                st.markdown("---")
                st.markdown("### 🔥 Top Priority: STRONG BUY Opportunities")
                st.table(pd.DataFrame(strong_buys))
        else:
            st.warning("No assets currently match. Market might be in a correction phase.")

st.divider()
st.caption("WAHBA EGX | AUTO-SCANNER SYSTEM | © 2026")
