import streamlit as st
from tradingview_ta import TA_Handler, Interval

st.set_page_config(page_title="Wahba Pro", layout="wide")

# تصميم الشريط الملون بتاع تريدنج فيو
st.markdown("""
    <style>
    .t-bar { height: 18px; width: 100%; background: linear-gradient(90deg, #ff4b4b 0%, #ffca28 50%, #2e7d32 100%); border-radius: 9px; position: relative; margin: 10px 0; }
    .t-pointer { height: 26px; width: 4px; background-color: #2196f3; position: absolute; top: -4px; border-radius: 2px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Wahba Pro: رادار البورصة المصرية")

# المؤشرات والأسهم اللي تهمك
assets = {
    "EGX 30 (الثلاثيني)": "EGX30",
    "EGX 70 (السبعيني)": "EGX70",
    "CIB (التجاري الدولي)": "COMI",
    "Fawry (فوري)": "FWRY",
    "TMG (طلعت مصطفى)": "TMGH"
}

for name, sym in assets.items():
    try:
        handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY)
        analysis = handler.get_analysis()
        summary = analysis.summary
        ind = analysis.indicators

        col1, col2, col3 = st.columns([2, 2, 4])
        with col1:
            st.subheader(name)
        with col2:
            rec = summary['RECOMMENDATION']
            color = "#00c853" if "BUY" in rec else "#ff1744" if "SELL" in rec else "#ffca28"
            st.markdown(f"<h3 style='color:{color};'>{rec}</h3>", unsafe_allow_html=True)
        with col3:
            # حساب مكان السعر في الشريط الملون
            h, l, c = ind['high'], ind['low'], ind['close']
            pos = ((c - l)
            
