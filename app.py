import streamlit as st
import time
from tradingview_ta import TA_Handler, Interval

st.set_page_config(page_title="Wahba Pro | Radar", layout="wide")

st.title("🛡️ Wahba Pro: رادار الأسهم الصاعدة")
st.write("الفحص يعتمد على اختراق متوسط 50 يوم (إغلاق يومي).")

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
            close_price = analysis.indicators["close"]
            sma50 = analysis.indicators.get("SMA50")

            # الشرط: السعر فوق المتوسط 50
            if sma50 and close_price >= sma50:
                bullish_list.append(sym)
            
            time.sleep(0.05)
        except:
            continue

    progress_bar.empty()

    if bullish_list:
        st.success(f"تم رصد {len(bullish_list)} فرصة صاعدة")
        
        # عرض النتائج في أعمدة بشكل أنيق
        cols = st.columns(4)
        for i, stock_name in enumerate(bullish_list):
            with cols[i % 4]:
                st.info(f"📈 **{stock_name}**\n\n سهم صاعد")
    else:
        st.warning("لا توجد أسهم صاعدة حالياً.")
        
