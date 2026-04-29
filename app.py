import streamlit as st
from tradingview_ta import TA_Handler, Interval

st.set_page_config(page_title="Wahba Pro | فلتر الأسهم", layout="wide")

st.title("🔍 فلتر الأسهم الصاعدة (Wahba Pro)")
st.write("يتم الآن فحص أسهم البورصة المصرية لإظهار الفرص الصاعدة فقط...")

# قائمة بأهم رموز الأسهم المصرية (تقدر تضيف لحد 160 رمز بنفس الطريقة)
symbols = [
    "EGX30", "EGX70", "COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", 
    "EGAL", "PHDC", "HRHO", "ESRS", "ORWE", "SKPC", "BTEL", "EGCH",
    "AMOC", "MFOT", "HELI", "ORAS", "EKHO", "JUFO", "CANA", "ESGI",
    "GBCO", "CCAP", "AUTO", "MNHD", "PORT", "TALA", "ETEL"
    # ضيف باقي الرموز هنا داخل القائمة بنفس النمط
]

found_bullish = 0

# عرض النتائج في شكل أعمدة عشان الزحمة
cols = st.columns(3)

for i, sym in enumerate(symbols):
    try:
        handler = TA_Handler(
            symbol=sym,
            screener="egypt",
            exchange="EGX",
            interval=Interval.INTERVAL_1_DAY
        )
        analysis = handler.get_analysis()
        status = analysis.summary['RECOMMENDATION']

        # فلترة: إظهار الصاعد فقط (BUY أو STRONG_BUY)
        if "BUY" in status:
            found_bullish += 1
            # توزيع النتائج على الأعمدة
            with cols[found_bullish % 3]:
                st.success(f"✅ {sym}")
                st.caption(f"الحالة: {status}")
    except:
        continue

if found_bullish == 0:
    st.warning("لا توجد أسهم صاعدة حالياً بناءً على التحليل الفني.")
else:
    st.sidebar.metric("عدد الأسهم الصاعدة", found_bullish)

st.divider()
st.info("💡 تم الفحص بناءً على مؤشرات TradingView الفنية.")
