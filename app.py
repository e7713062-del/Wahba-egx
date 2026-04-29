import streamlit as st
from tradingview_ta import TA_Handler, Interval

st.set_page_config(page_title="Wahba Pro: Predictor")

st.title("🚀 توقعات البورصة المصرية لبكرة")

# قائمة الأسهم والرموز
assets = {
    "مؤشر EGX 30": "EGX30",
    "مؤشر EGX 70": "EGX70",
    "البنك التجاري الدولي": "COMI",
    "فوري": "FWRY",
    "طلعت مصطفى": "TMGH"
}

for name, sym in assets.items():
    try:
        # الربط مع تريدنج فيو
        handler = TA_Handler(
            symbol=sym,
            screener="egypt",
            exchange="EGX",
            interval=Interval.INTERVAL_1_DAY
        )
        analysis = handler.get_analysis()
        status = analysis.summary['RECOMMENDATION']

        # تحديد النتيجة صاعد أو هابط
        if "BUY" in status:
            result = "صاعد 🟢"
            color = "#00c853"
        elif "SELL" in status:
            result = "هابط 🔴"
            color = "#ff1744"
        else:
            result = "متذبذب 🟡"
            color = "#ffca28"

        # عرض النتيجة بشكل واضح
        st.subheader(f"{name}:")
        st.markdown(f"<h1 style='color:{color};'>{result}</h1>", unsafe_allow_html=True)
        st.divider()

    except:
        st.error(f"مشكلة في جلب بيانات {name}")

st.info("💡 التوقعات دي بناءً على التحليل الفني لتريدنج فيو.")
