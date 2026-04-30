import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval

st.set_page_config(page_title="Wahba Pro", layout="wide")
st.title("🛡️ رادار Wahba Pro")

# قائمة الأسهم في سطر واحد لتفادي أخطاء النسخ
STOCKS = ["COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "EGAL", "PHDC", "HRHO", "ESRS", "ORWE", "SKPC", "AMOC", "HELI", "JUFO", "ETEL", "MNHD"]

def check(s):
    try:
        h = TA_Handler(symbol=s, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=7)
        d = h.get_analysis().indicators
        if d["close"] > d["SMA10"] and d["RSI"] > 35:
            return {"s": s, "p": d["close"], "r": d["RSI"]}
    except: return None

if st.button('🚀 ابدأ الفحص'):
    with st.spinner('جاري التحميل...'):
        with ThreadPoolExecutor(max_workers=10) as exe:
            res = list(exe.map(check, STOCKS))
        final = [r for r in res if r]
        if final:
            st.success(f"وجدنا {len(final)} سهم")
            cols = st.columns(4)
            for i, item in enumerate(final):
                with cols[i % 4]:
                    st.metric(item["s"], f"{item['p']:.2f}", f"RSI: {item['r']:.1f}")
        else:
            st.warning("لا توجد نتائج حالياً.")
