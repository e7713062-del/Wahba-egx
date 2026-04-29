import streamlit as st
import pandas as pd
import time
from tradingview_ta import TA_Handler, Interval

st.set_page_config(page_title="Wahba Pro", layout="wide")

st.title("🛡️ Wahba Pro: رادار البورصة المصرية")

STOCKS = [
    "COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "EGAL", "PHDC", 
    "HRHO", "ESRS", "ORWE", "SKPC", "BTEL", "EGCH", "AMOC", "MFOT", 
    "HELI", "ORAS", "EKHO", "JUFO", "CANA", "ESGI", "GBCO", "CCAP",
    "AUTO", "MNHD", "PORT", "TALA", "ETEL", "ISPH", "RMDA", "CIRA"
]

if st.button('إبدأ فحص السوق الآن'):
    bullish_stocks = []
    bar = st.progress(0)
    
    for idx, sym in enumerate(STOCKS):
        try:
            bar.progress((idx + 1) / len(STOCKS))
            handler = TA_Handler(
                symbol=sym,
                screener="egypt",
                exchange="EGX",
                interval=Interval.INTERVAL_1_DAY,
                timeout=10
            )
            analysis = handler.get_analysis()
            price = analysis.indicators["close"]
            sma50 = analysis.indicators.get("SMA50")

            if sma50 and price >= sma50:
                bullish_stocks.append({"الرمز": sym, "السعر": price, "SMA50": sma50})
            time.sleep(0.05)
        except:
            continue

    if bullish_stocks:
        st.table(pd.DataFrame(bullish_stocks))
    else:
        st.warning("لا توجد فرص حالياً")
        
