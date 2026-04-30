import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval

st.set_page_config(page_title="Wahba Pro | Sensitive", layout="wide")
st.title("🛡️ رادار Wahba Pro - اصطياد الفرص")

# قائمة الـ 220 سهم (تقدر تضيف الباقي هنا)
STOCKS = [
    "COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "EGAL", "PHDC", 
    "HRHO", "ESRS", "ORWE", "SKPC", "BTEL", "EGCH", "AMOC", "MFOT", 
    "HELI", "ORAS", "EKHO", "JUFO", "CANA", "ESGI", "GBCO", "CCAP",
    "AUTO", "MNHD", "PORT", "TALA", "ETEL", "ISPH", "RMDA", "CIRA",
    "ELSH", "OIH", "CCAP", "EMFD", "MTIE", "DSCW", "EHDR", "ASPI"
]

def check(s):
    try:
        h = TA_Handler(symbol=s, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=5)
        d = h.get_analysis().indicators
        
        # التعديل الجديد (إعدادات أكثر حساسية):
        # 1. السعر أكبر من متوسط 10 أيام (SMA10) بدل منتصف البولينجر
        # 2. RSI أكبر من 40 (بداية زخم صعودي)
        if d["close"] > d["SMA10"] and d["RSI"] > 40:
            return s
    except:
        return None

if st.button('🚀 إبدأ الفحص الشامل'):
    with st.spinner('جاري فحص 220 سهم...'):
        with ThreadPoolExecutor(max_workers=25) as exe:
            res = list(exe.map(check, STOCKS))
        
        final = [r for r in res if r]
        
        if final:
            st.success(f"✅ تم رصد {len(final)} سهم صاعد")
            c = st.columns(5)
            for i, name in enumerate(final):
                with c[i % 5]:
                    st.success(f"**{name}**")
        else:
            st.warning("حتى مع الإعدادات الحساسة، لا توجد أسهم محققة للشرط حالياً.")
