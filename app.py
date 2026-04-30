import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval
import pandas as pd

# 1. الاعدادات الاساسية
st.set_page_config(page_title="Wahba Pro Terminal", layout="wide")

# 2. تصميم الواجهة (لوجو وهيبة برو)
st.markdown("<h1 style='text-align: left; color: #1a1a1a;'>WAHBA<span style='color: #0066ff;'>PRO</span></h1>", unsafe_allow_html=True)
st.write("OFFICIAL MARKET TERMINAL | EGYPT STOCK EXCHANGE")
st.markdown("---")

# 3. قائمة الاسهم
STOCKS = [
    "COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "EGAL", "PHDC", "HRHO", "ESRS",
    "ORWE", "SKPC", "BTEL", "EGCH", "AMOC", "MFOT", "HELI", "ORAS", "EKHO", "JUFO",
    "CANA", "ESGI", "GBCO", "CCAP", "AUTO", "MNHD", "PORT", "TALA", "ETEL", "ISPH",
    "RMDA", "CIRA", "ELSH", "OIH", "EMFD", "MTIE", "DSCW", "EHDR", "ASPI", "ADIB",
    "ACTF", "KRDI", "ATLC", "ALCN", "AFMC", "AMER", "ARAB", "AMIA", "AIDC", "AIHC",
    "ARCC", "ASCM", "BTFH", "COSG", "POUL", "CSAG", "PRCL", "CNFN", "CIEB", "DAPH",
    "EAST", "EFID", "EGTS", "PHAR", "MPRC", "ETRS", "AFDI", "ECAP", "KABO", "OBRI",
    "RAYA", "MCQE", "ORHD", "UNIT", "MBSC", "MPCI", "ZMID", "SPMD", "BINV",
    "MOIL", "AALR", "WKOL", "EALR", "CPME", "IFAP", "SMPP", "ELWA", "GPPL",
    "ALUM", "BIOC", "EDBM", "MICH", "DCRC", "ODIN", "ICMI", "RACC", "REAC"
]

def check_logic(symbol):
    try:
        handler = TA_Handler(
            symbol=symbol,
            screener="egypt",
            exchange="EGX",
            interval=Interval.INTERVAL_1_DAY,
            timeout=10
        )
        analysis = handler.get_analysis()
        d = analysis.indicators
        rec = analysis.summary["RECOMMENDATION"]
        
        # الشرط: السعر فوق متوسط 10 و RSI فوق 40 وتوصية شراء
        if d["close"] > d["SMA10"] and d["RSI"] > 40 and "BUY" in rec:
            return {
                "Ticker": symbol,
                "Price": round(d["close"], 2),
                "RSI": round(d["RSI"], 2),
                "Signal": rec.replace("_", " ")
            }
    except:
        return None

# 4. زر التشغيل والنتائج
if st.button('RUN SYSTEM SCAN'):
    with st.spinner('Accessing Real-time Market Data...'):
        with ThreadPoolExecutor(max_workers=30) as executor:
            res = list(executor.map(check_logic, STOCKS))
        
        final = [item for item in res if item is not None]
        
        if final:
            st.success(f"Identification Complete: {len(final)} Bullish Assets Found")
            df = pd.DataFrame(final)
            st.table(df) # استخدام table بدلاً من dataframe لضمان استقرار العرض
        else:
            st.warning("No assets currently match the defined growth protocol.")

st.markdown("---")
st.caption("WAHBA PRO | DATA PROVIDED BY TRADINGVIEW | © 2026")
