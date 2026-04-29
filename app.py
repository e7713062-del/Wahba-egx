import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval

# إعداد الصفحة
st.set_page_config(page_title="Wahba Pro", layout="wide")
st.title("🛡️ رادار Wahba Pro - الإغلاقات")

# قائمة الـ 220 سهم (تقدر تفتح القوس وتضيف كل اللي عندك بنفس التنسيق)
STOCKS = [
    "COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "EGAL", "PHDC", 
    "HRHO", "ESRS", "ORWE", "SKPC", "BTEL", "EGCH", "AMOC", "MFOT", 
    "HELI", "ORAS", "EKHO", "JUFO", "CANA", "ESGI", "GBCO", "CCAP",
    "AUTO", "MNHD", "PORT", "TALA", "ETEL", "ISPH", "RMDA", "CIRA"
    # ضيف باقي الأسهم هنا قبل القوس المربع
]

def check(s):
    try:
        h = TA_Handler(symbol=s, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=5)
        d = h.get_analysis().indicators
        # شرط الإغلاق: سعر أكبر من منتصف البولينجر و RSI أكبر من 50
        if d["close"] > d["BB.mavg"] and d["RSI"] > 50:
            return s
    except:
        return None

if st.button('🚀 فحص السوق بالكامل'):
    with st.spinner('جاري التحليل...'):
        # فحص سريع لـ 220 سهم
        with ThreadPoolExecutor(max_workers=20) as exe:
            res = list(exe.map(check, STOCKS))
        
        final = [r for r in res if r]
        
        if final:
            st.success(f"لقينا {len(final)} سهم صاعد")
            c = st.columns(5)
            for i, name in enumerate(final):
                with c[i % 5]:
                    st.success(f"**{name}**")
        else:
            st.warning("مفيش أسهم محققة الشروط")
