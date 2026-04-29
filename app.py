import streamlit as st
import time
from tradingview_ta import TA_Handler, Interval

st.set_page_config(page_title="Wahba Pro | RSI & BB", layout="wide")

st.title("🛡️ Wahba Pro: رادار البولينجر و RSI")
st.write("الشرط: السعر فوق خط المنتصف للبولينجر + مؤشر RSI فوق 50.")

STOCKS = [
    "COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "EGAL", "PHDC", 
    "HRHO", "ESRS", "ORWE", "SKPC", "BTEL", "EGCH", "AMOC", "MFOT", 
    "HELI", "ORAS", "EKHO", "JUFO", "CANA", "ESGI", "GBCO", "CCAP",
    "AUTO", "MNHD", "PORT", "TALA", "ETEL", "ISPH", "RMDA", "CIRA"
]

if st.button('إبدأ فحص الاستراتيجية الآن 🔄'):
    bullish_list = []
    progress_bar = st.progress(0)
    
    for idx, sym in enumerate(STOCKS):
        try:
            progress_bar.progress((idx + 1) / len(STOCKS))
            handler = TA_Handler(
                symbol=sym,
                screener="egypt",
                exchange="EGX",
                interval=Interval.INTERVAL_
