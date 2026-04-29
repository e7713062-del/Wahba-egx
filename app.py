import streamlit as st
from tradingview_ta import TA_Handler, Interval

st.set_page_config(page_title="Wahba Pro | الأسهم الصاعدة", layout="wide")

st.title("🚀 فلتر الأسهم الصاعدة لبكرة")
st.write("الأسهم اللي ظاهرة تحت هي فقط اللي واخدة إشارة 'صعود' من تريدنج فيو")

# قائمة موسعة لأهم أسهم البورصة المصرية
egypt_stocks = {
    "المؤشر الثلاثيني": "EGX30",
    "المؤشر السبعيني": "EGX70",
    "البنك التجاري الدولي": "COMI",
    "فوري": "FWRY",
    "طلعت مصطفى": "TMGH",
    "السويدي الكتريك": "SWDY",
    "إي فاينانس": "EFIH",
    "أبو قير للأسمدة": "ABUK",
    "مصر للألومنيوم": "EGAL",
    "بالم هيلز": "PHDC",
    "هيرميس": "HRHO",
    "حديد عز": "ESRS",
    "النساجون الشرقيون": "ORWE",
    "سيدي كرير": "SKPC",
    "بلتون": "BTEL",
    "كيما": "EGCH"
}

# عداد للأسهم الصاعدة
found_bullish = 0

for name, sym in egypt_stocks.items():
    try:
        handler = TA_Handler(
            symbol=sym,
            screener="egypt",
            exchange="EGX",
            interval=Interval.INTERVAL_1_DAY
        )
        analysis = handler.get_analysis()
        status = analysis.summary['RECOMMENDATION']

        # الفلتر: إظهار الصاعد فقط (BUY أو STRONG_BUY)
        if "BUY" in status:
            found_bullish += 1
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(f"{name} ({sym})")
                with col2:
                    st.markdown(f"<h2 style='color:#00c853;'>صاعد 🟢</h2>", unsafe_allow_html=True)
                st.divider()
    except:
        continue

if found_bullish == 0:
    st.warning("مفيش أسهم واخدة إشارة صعود حالياً بناءً على إغلاق اليوم.")

st.info(f"تم فحص {len(egypt_stocks)} سهم، ولقينا {found_bullish} سهم في حالة صعود.")
