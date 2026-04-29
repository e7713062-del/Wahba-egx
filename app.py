import streamlit as st
from tradingview_ta import TA_Handler, Interval

# إعدادات الصفحة
st.set_page_config(page_title="Wahba Pro", layout="wide")
st.title("🚀 رادار البورصة المصرية - Wahba Pro")

# قائمة الأسهم والرموز في تريدنج فيو
assets = {
    "مؤشر EGX 30": "EGX30",
    "مؤشر EGX 70": "EGX70",
    "البنك التجاري الدولي": "COMI",
    "فوري": "FWRY",
    "طلعت مصطفى": "TMGH",
    "السويدي الكتريك": "SWDY"
}

for name, sym in assets.items():
    try:
        # الربط مع تريدنج فيو (مصر)
        handler = TA_Handler(
            symbol=sym,
            screener="egypt",
            exchange="EGX",
            interval=Interval.INTERVAL_1_DAY
        )
        analysis = handler.get_analysis()
        status = analysis.summary['RECOMMENDATION']

        # الخلاصة: صاعد أو هابط
        if "BUY" in status:
            result = "صاعد 🟢"
            color = "#00c853"
        elif "SELL" in status:
            result = "هابط 🔴"
            color = "#ff1744"
        else:
            result = "عرضي / غير واضح 🟡"
            color = "#ffca28"

        st.subheader(f"{name}:")
        st.markdown(f"<h1 style='color:{color};'>{result}</h1>", unsafe_allow_html=True)
        st.divider()

    except Exception:
        st.error(f"عفواً.. تعذر جلب بيانات {name}")

st.info("💡 هذا التوقع مبني على التحليل الفني لآخر إغلاق.")
