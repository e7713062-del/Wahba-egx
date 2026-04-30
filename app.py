import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval

st.set_page_config(page_title="Wahba Pro", layout="wide")
st.title("🛡️ رادار Wahba Pro")

# القائمة الكاملة اللي كنت عايزها
STOCKS = [
    "COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "EGAL", "PHDC", 
    "HRHO", "ESRS", "ORWE", "SKPC", "BTEL", "EGCH", "AMOC", "MFOT", 
    "HELI", "ORAS", "EKHO", "JUFO", "CANA", "ESGI", "GBCO", "CCAP",
    "AUTO", "MNHD", "PORT", "TALA", "ETEL", "ISPH", "RMDA", "CIRA",
    "ELSH", "OIH", "EMFD", "MTIE", "DSCW", "EHDR", "ASPI"
]

def check(s):
    try:
        h = TA_Handler(symbol=s, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=10)
        d = h.get_analysis().indicators
        
        # شروط "أقل حدة" للتأكد من عمل الرادار
        # السعر فوق المتوسط 10 أيام (أو قريب منه جداً) والـ RSI فوق 30
        if d["close"] > (d["SMA10"] * 0.98) and d["RSI"] > 30:
            return {"s": s, "p": d["close"], "r": d["RSI"]}
    except:
        return None

if st.button('🚀 ابدأ الفحص الشامل'):
    with st.spinner('جاري فحص 40 سهم الآن...'):
        with ThreadPoolExecutor(max_workers=10) as exe:
            res = list(exe.map(check, STOCKS))
        
        final = [r for r in res if r]
        
        if final:
            st.success(f"✅ تم رصد {len(final)} فرص محتملة")
            cols = st.columns(4)
            for i, item
