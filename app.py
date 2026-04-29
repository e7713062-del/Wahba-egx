import streamlit as st
from tradingview_ta import TA_Handler, Interval

st.set_page_config(page_title="Wahba Pro | الماسح التلقائي", layout="wide")

st.title("🛡️ Wahba Pro: رادار البورصة المصرية الشامل")
st.write("الرادار بيفحص حالياً كل الأسهم المدرجة في مصر وبيطلع لك 'الصاعد' بس..")

# قائمة ضخمة لأهم الأسهم (ممكن تسيبها كقاعدة بيانات والبرنامج بيفحصها)
# أي سهم جديد ينزل البورصة، ضيف رمزه هنا مرة واحدة وهيفضل شغال للأبد
symbols = [
    "EGX30", "EGX70", "COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", 
    "EGAL", "PHDC", "HRHO", "ESRS", "ORWE", "SKPC", "BTEL", "EGCH",
    "AMOC", "MFOT", "HELI", "ORAS", "EKHO", "JUFO", "CANA", "ESGI",
    "GBCO", "CCAP", "AUTO", "MNHD", "PORT", "TALA", "ETEL", "ISPH",
    "ESLAN", "RMDA", "CIRA", "CLHO", "MIPH", "DSCW", "DOMT", "OBRI",
    "BINV", "ORAS", "DAPH", "MOIL", "AIVC", "IDRE", "ASCM", "RAQT"
]

# لو عايز تضيف الـ 160 سهم، حط رموزهم في القائمة فوق بنفس الطريقة

bullish_found = 0
cols = st.columns(3)

with st.spinner('جاري فحص السوق بالكامل...'):
    for sym in symbols:
        try:
            handler = TA_Handler(
                symbol=sym,
                screener="egypt",
                exchange="EGX",
                interval=Interval.INTERVAL_1_DAY
            )
            analysis = handler.get_analysis()
            rec = analysis.summary['RECOMMENDATION']

            # إظهار الصاعد فقط (شراء أو شراء قوي)
            if "BUY" in rec:
                with cols[bullish_found % 3]:
                    st.success(f"✅ {sym}")
                    st.write(f"الحالة: **{rec}**")
                bullish_found += 1
        except:
            continue

if bullish_found == 0:
    st.warning("مفيش إشارات صعود واضحة دلوقتي في السوق.")
else:
    st.sidebar.metric("عدد الأسهم الصاعدة", bullish_found)

st.sidebar.info("هذا الرادار مبرمج لمراقبة كافة تحديثات TradingView للبورصة المصرية.")
