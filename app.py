import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval

st.set_page_config(page_title="Wahba Pro | Full Market", layout="wide")
st.title("🛡️ رادار Wahba Pro - فحص السوق الكامل")
st.write("الفحص يعتمد على **إغلاق اليوم** (بولينجر + RSI)")

# ضع هنا الـ 220 سهم بالكامل داخل القائمة
STOCKS = [
    "COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "EGAL", "PHDC", 
    "HRHO", "ESRS", "ORWE", "SKPC", "BTEL", "EGCH", "AMOC", "MFOT", 
    "HELI", "ORAS", "EKHO", "JUFO", "CANA", "ESGI", "GBCO", "CCAP",
    "AUTO", "MNHD", "PORT", "TALA", "ETEL", "ISPH", "RMDA", "CIRA",
    "POUL", "EDBM", "AFMC", "DOMT", "ARCC", "MAAL", "UNIT", "AJWA"
    # ... يمكنك إضافة باقي الـ 220 سهم هنا بنفس التنسيق
]

def check_stock(sym):
    try:
        h = TA_Handler(
            symbol=sym,
            screener="egypt",
            exchange="EGX",
            interval=Interval.INTERVAL_1_DAY,
            timeout=5
        )
        ind = h.get_analysis().indicators
        
        # شرط الإغلاق اليومي: السعر فوق منتصف البولينجر و RSI فوق 50
        if ind["close"] > ind["BB.mavg"] and ind["RSI"] > 50:
            return sym
    except:
        return None
    return None

if st.button('🚀 إبدأ فحص الـ 220 سهم الآن'):
    with st.
