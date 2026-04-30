import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval
import pandas as pd

# 1. الاعدادات الاساسية
st.set_page_config(page_title="Wahba EGX | Terminal", layout="wide")

# 2. تصميم الواجهة (الاسم في المنتصف وتعديل المسمى لـ Wahba EGX)
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 20px;
    }
    .brand-name {
        font-family: 'Inter', sans-serif;
        font-size: 50px;
        font-weight: 900;
        margin: 0;
        letter-spacing: -2px;
        text-transform: uppercase;
        color: var(--text-color);
    }
    .brand-tagline {
        font-size: 14px;
        letter-spacing: 3px;
        opacity: 0.8;
        text-transform: uppercase;
    }
    </style>
    <div class="main-header">
        <h1 class="brand-name">Wahba EGX</h1>
        <p class="brand-tagline">OFFICIAL MARKET TERMINAL | EGYPT STOCK EXCHANGE</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# 3. قائمة الأسهم الكاملة (220 سهم)
STOCKS = [
    "COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "EGAL", "PHDC", "HRHO", "ESRS",
    "ORWE", "SKPC", "BTEL", "EGCH", "AMOC", "MFOT", "HELI", "ORAS", "EKHO", "JUFO",
    "CANA", "ESGI", "GBCO", "CCAP", "AUTO", "MNHD", "PORT", "TALA", "ETEL", "ISPH",
    "RMDA", "CIRA", "ELSH", "OIH", "EMFD", "MTIE", "DSCW", "EHDR", "ASPI", "ADIB",
    "ACTF", "KRDI", "ATLC", "ALCN", "AFMC", "AMER", "ARAB", "AMIA", "AIDC", "AIHC",
    "ARCC", "ASCM", "BTFH", "COSG", "POUL", "CSAG", "PRCL", "CNFN", "CIEB", "DAPH",
    "EAST", "EFID", "EGTS", "PHAR", "MPRC", "ETRS", "AFDI", "ECAP", "KABO", "OBRI",
    "RAYA", "MCQE", "ORHD", "UNIT", "MBSC", "MPCI", "ZMID", "SPMD", "BINV", "MOIL",
    "AALR", "WKOL", "EALR", "CPME", "IFAP", "SMPP", "ELWA", "GPPL", "ALUM", "BIOC",
    "EDBM", "MICH", "DCRC", "ODIN", "ICMI", "RACC", "REAC", "EFTG", "ALRE", "ANBK",
    "ARVA", "ASRE", "ATQA", "CERA", "COPR", "DECO", "DGTW", "DOMT", "EDFM", "EGAS", 
    "EGBE", "EGLF", "EGNA", "EGRP", "EGTW", "ELKA", "ELSA", "ENGC", "EPCO", "EPHL", 
    "EXPA", "FAIT", "FIRT", "GGCC", "GIZA", "GTHE", "GTWR", "HDBK", "ICID", "IDRE", 
    "IRAX", "ISMA", "KTSP", "LCSW", "MAAL", "MENA", "MEPA", "MIFT", "MIPH", "MOSC",
    "NASR", "NBKE", "NCGC", "NDMC", "PACH", "PICO", "PRDC", "QNBA", "RREI", "SAUD", 
    "SBIB", "SCEM", "SDTI", "SGGW", "SIPC", "SPRE", "UEGC", "UNIP", "UPMS", "UTRE", 
    "VERT", "WARY"
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
        with ThreadPoolExecutor(max_workers=35) as executor:
            res = list(executor.map(check_logic, STOCKS))
        
        final = [item for item in res if item is not None]
        
        if final:
            st.success(f"Identification Complete: {len(final)} Bullish Assets Found")
            df = pd.DataFrame(final)
            st.table(df)
        else:
            st.warning("No assets currently match the defined growth protocol.")

st.markdown("---")
st.caption("WAHBA EGX | DATA PROVIDED BY TRADINGVIEW | © 2026")
