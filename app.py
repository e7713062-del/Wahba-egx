import streamlit as st
import time
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval

st.set_page_config(page_title="Wahba Pro | Turbo", layout="wide")
st.title("🛡️ رادار Wahba Pro السريع")

# القائمة الكاملة والجاهزة
STOCKS = [
    "COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "EGAL", "PHDC", 
    "HRHO", "ESRS", "ORWE", "SKPC", "BTEL", "EGCH", "AMOC", "MFOT", 
    "HELI", "ORAS", "EKHO", "JUFO", "CANA", "ESGI", "GBCO", "CCAP",
    "AUTO", "MNHD", "PORT", "TALA", "ETEL", "ISPH", "RMDA", "CIRA"
]

def check_stock(sym):
    """دالة فحص السهم الواحد - سريعة جداً"""
    try:
        h = TA_Handler(
            symbol=sym,
            screener="egypt",
            exchange="EGX",
            interval=Interval.INTERVAL_1_DAY,
            timeout=5
        )
        ind = h.get_analysis().indicators
        # شرط البولينجر و RSI
        if ind["close"] > ind["BB.mavg"] and ind["RSI"] > 50:
            return sym
    except:
        return None
    return None

if st.button('إبدأ فحص الصواريخ 🚀'):
    bullish_list = []
    progress_bar = st.progress(0)
    
    # استخدام ThreadPoolExecutor لتسريع الفحص (فحص 10 أسهم في نفس اللحظة)
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(check_stock, STOCKS))
    
    # تصفية النتائج
    bullish_list = [r for r in results if r is not None]

    if bullish_list:
        st.success(f"تم رصد {len(bullish_list)} سهم صاعد في ثوانٍ!")
        cols = st.columns(4)
        for i, name in enumerate(bullish_list):
            with cols[i % 4]:
                st.success(f"📈 **{name}**\n\n سهم صاعد")
    else:
        st.warning("مفيش أسهم محققة الشروط حالياً.")
