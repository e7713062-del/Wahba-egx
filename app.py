import streamlit as st
import time
from tradingview_ta import TA_Handler, Interval

st.set_page_config(page_title="Wahba Pro", layout="wide")

st.title("🛡️ Wahba Pro: رادار الأسهم الصاعدة")

STOCKS = [
    "COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "EGAL", "PHDC", 
    "HRHO", "ESRS", "ORWE", "SKPC", "BTEL", "EGCH", "AMOC", "MFOT", 
    "HELI", "ORAS", "EKHO", "JUFO", "CANA", "ESGI", "GBCO", "CCAP",
    "AUTO", "MNHD", "PORT", "TALA", "ETEL", "ISPH", "RMDA", "CIRA"
]

if st.button('إبدأ فحص السوق الآن 🔄'):
    bullish_list = []
    progress_bar = st.progress(0)
    
    for idx, sym in enumerate(STOCKS):
        try:
            progress_bar.progress((idx + 1) / len(STOCKS))
            handler = TA_Handler(
                symbol=sym,
                screener="egypt",
                exchange="EGX",
                interval=Interval.INTERVAL_1_DAY,
                timeout=7
            )
            analysis = handler.get_analysis()
            
            # التعديل هنا: إذا كانت التوصية العامة هي شراء
            # ده هيخلي الرادار يجيب لك الأسهم الصاعدة فعلياً
            rec = analysis.summary['RECOMMENDATION']
            
            if "BUY" in rec:
                bullish_list.append(sym)
            
            time.sleep(0.05)
        except:
            continue

    progress_bar.empty()

    if bullish_list:
        st.success(f"تم رصد {len(bullish_list)} سهم صاعد")
        cols = st.columns(3)
        for i, stock_name in enumerate(bullish_list):
            with cols[i % 3]:
                st.success(f"📈 **{stock_name}**\n\n سهم صاعد")
    else:
        st.warning("لا توجد أسهم صاعدة حالياً في البورصة المصرية حسب التحليل الفني.")
