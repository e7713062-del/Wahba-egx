import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests

# 1. الإعدادات الأساسية
st.set_page_config(page_title="Wahba EGX | Terminal", layout="wide")

# 2. تصميم الواجهة (العنوان في المنتصف)
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

# 3. دالة جلب كل أسهم مصر أوتوماتيكياً من سيرفرات TradingView مباشرة
@st.cache_data(ttl=3600) # بيحدث القائمة كل ساعة عشان لو سهم نزل في نص اليوم يظهر
def get_live_egx_symbols():
    try:
        # بننادي على الـ API الخاص بـ TradingView اللي فيه كل رموز مصر
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {"filter":[],"options":{"lang":"en"},"markets":["egypt"],"symbols":{"query":{"types":[]},"tickers":[]},"columns":["logoid","name"]}
        res = requests.post(url, json=payload).json()
        # بنستخرج الرموز (الـ Tickers) فقط
        tickers = [item['s'].split(':')[1] for item in res['data']]
        return tickers
    except:
        # لو السيرفر مهنج، بيستخدم القائمة الأساسية اللي إنت عارفها كاحتياط
        return ["COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "PHDC", "HRHO", "BTEL"]

def check_logic(symbol):
    try:
        handler = TA_Handler(
            symbol=symbol, screener="egypt", exchange="EGX",
            interval=Interval.INTERVAL_1_DAY, timeout=7
        )
        analysis = handler.get_analysis()
        d = analysis.indicators
        rec = analysis.summary["RECOMMENDATION"]
        
        # فلترة الأسهم الصاعدة
        if d["close"] > d["SMA10"] and d["RSI"] > 40 and "BUY" in rec:
            return {
                "Ticker": symbol,
                "Price": round(d["close"], 2),
                "RSI": round(d["RSI"], 2),
                "Signal": rec.replace("_", " ")
            }
    except: return None

# 4. زر التشغيل والنتائج
if st.button('START FULL MARKET AUTO-SCAN'):
    all_current_stocks = get_live_egx_symbols()
    
    with st.spinner(f'Scanning {len(all_current_stocks)} Live EGX Securities...'):
        with ThreadPoolExecutor(max_workers=35) as executor:
            res = list(executor.map(check_logic, all_current_stocks))
        
        final = [item for item in res if item is not None]
        
        if final:
            st.success(f"Identification Complete: {len(final)} Assets Found")
            st.table(pd.DataFrame(final))
            
            # قسم الـ STRONG BUY في الأسفل
            strong_buys = [item for item in final if "STRONG BUY" in item["Signal"]]
            if strong_buys:
                st.markdown("---")
                st.markdown("### 🔥 Top Priority: STRONG BUY Opportunities")
                st.table(pd.DataFrame(strong_buys))
        else:
            st.warning("No assets currently match the defined growth protocol.")

st.divider()
st.caption("WAHBA EGX | FULL AUTO-UPDATE SYSTEM | © 2026")
