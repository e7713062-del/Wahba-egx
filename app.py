import streamlit as st
from tradingview_ta import TA_Handler, Interval
import time

st.set_page_config(page_title="Wahba Pro | رادار شامل", layout="wide")

st.title("🛡️ Wahba Pro: رادار البورصة المصرية الذكي")
st.write("فحص آلي وتلقائي لأسهم البورصة المصرية.")

# قائمة الأسهم (يفضل وضعها خارج الدالة لسهولة التعديل)
STOCKS = [
    "COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "EGAL", "PHDC", 
    "HRHO", "ESRS", "ORWE", "SKPC", "BTEL", "EGCH", "AMOC", "MFOT", 
    "HELI", "ORAS", "EKHO", "JUFO", "CANA", "ESGI", "GBCO", "CCAP",
    "AUTO", "MNHD", "PORT", "TALA", "ETEL", "ISPH", "RMDA", "CIRA"
]

if st.button('إبدأ فحص السوق الآن'):
    bullish_stocks = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_area = st.container() # مكان مخصص لعرض النتائج فور ظهورها

    for idx, sym in enumerate(STOCKS):
        try:
            # تحديث شريط التقدم
            progress = (idx + 1) / len(STOCKS)
            progress_bar.progress(progress)
            status_text.text(f"جاري فحص: {sym}")

            handler = TA_Handler(
                symbol=sym,
                screener="egypt",
                exchange="EGX",
                interval=Interval.INTERVAL_1_DAY,
                timeout=10 # إضافة وقت انتظار أطول قليلاً لمنع التعليق
            )
            
            analysis = handler.get_analysis()
            rec = analysis.summary['RECOMMENDATION']
            
            if "BUY" in rec:
                bullish_stocks.append({"symbol": sym, "status": rec})
            
            # إضافة فاصل زمني صغير جداً لتجنب الحظر (0.1 ثانية)
            time.sleep(0.1)

        except Exception as e:
            continue

    status_text.empty()
    progress_bar.empty()

    if bullish_stocks:
        st.success(f"تم العثور على {len(bullish_stocks)} سهم بإشارة صعود")
        cols = st.columns(4)
        for idx, s in enumerate(bullish_stocks):
            with cols[idx % 4]:
                color = "chartreuse" if "STRONG" in s['status'] else "white"
                st.markdown(f"""
                <div style="border:1px solid #ccc; padding:10px; border-radius:10px; text-align:center;">
                    <h3 style="color:{color};">{s['symbol']}</h3>
                    <p>{s['status']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("لا توجد إشارات صعود قوية حالياً. حاول مرة أخرى لاحقاً.")
