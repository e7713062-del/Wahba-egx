import streamlit as st
import pandas as pd
import time

# محاولة استيراد المكتبة
try:
    from tradingview_ta import TA_Handler, Interval
except ImportError:
    st.error("المكتبة غير مثبتة. يرجى التأكد من ملف requirements.txt")
    st.stop()

st.set_page_config(page_title="Wahba Pro | Radar", layout="wide")

st.title("🛡️ Wahba Pro: رادار البورصة المصرية")
st.write("الفحص يعتمد على الإغلاق اليومي واختراق السعر لمتوسط 50 يوم.")

# قائمة الأسهم المحدثة (تأكد من عدم مسح أي علامة تنصيص)
STOCKS = [
    "COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "EGAL", "PHDC", 
    "HRHO", "ESRS", "ORWE", "SKPC", "BTEL", "EGCH", "AMOC", "MFOT", 
    "HELI", "ORAS", "EKHO", "JUFO", "CANA", "ESGI", "GBCO", "CCAP",
    "AUTO", "MNHD", "PORT", "TALA", "ETEL", "ISPH", "RMDA", "CIRA"
]

if st.button('إبدأ فحص السوق الآن 🔄'):
    bullish_stocks = []
    progress_bar = st.progress(0)
    
    for idx, sym in enumerate(STOCKS):
        try:
            progress_bar.progress((idx + 1) / len(STOCKS))
            
            handler = TA_Handler(
                symbol=sym,
                screener="egypt",
                exchange="EGX",
                interval=Interval.INTERVAL_1_DAY,
                timeout=10
            )
            
            analysis = handler.get_analysis()
            close_price = analysis.indicators["close"]
            sma
