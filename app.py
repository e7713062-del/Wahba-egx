import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval
import pandas as pd

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="Wahba EGX | Terminal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. تصميم الهوية البصرية (نفس الكود القديم والشكل القديم بالظبط)
# التغيير الوحيد هو رسمة الـ SVG لتعبر عن اللوجو الخاص بك
st.markdown("""
    <style>
    /* الحاوية الرئيسية */
    .terminal-header {
        text-align: center;
        padding: 40px 20px;
        margin-bottom: 30px;
    }

    .logo-container {
        display: inline-block;
        width: 140px;
        height: 140px;
        margin-bottom: 15px;
    }

    /* نص Wahba EGX - يتغير لونه تلقائياً */
    .brand-name {
        font-family: 'Inter', sans-serif;
        font-size: 50px;
        font-weight: 900;
        margin: 0;
        letter-spacing: -2px;
        text-transform: uppercase;
        line-height: 1;
        color: var(--text-color); /* يعتمد على ثيم الاستريميت */
    }

    .brand-tagline {
        font-size: 13px;
        letter-spacing: 4px;
        margin-top: 10px;
        text-transform: uppercase;
        font-weight: 700;
        opacity: 0.8;
        color: var(--text-color);
    }

    /* جعل اللوجو يأخذ لون النص الحالي للمتصفح */
    .dynamic-svg {
        stroke: currentColor;
    }

    /* تحسين شكل الأزرار */
    .stButton>button {
        border-radius: 4px;
        font-weight: 800;
        height: 3.8em;
        width: 100%;
        border: 1px solid currentColor;
    }
    </style>

    <div class="terminal-header">
        <div class="logo-container">
            <svg class="dynamic-svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <path d="M50,10 L85,25 V75 L50,90 L15,75 V25 Z" 
                      fill="none" stroke-width="5" stroke-linejoin="round"/>
                
                <path d="M25,65 L35,50 L45,60 L60,30 L75,35 M70,25 L75,35 L65,40" 
                      fill="none" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <div class="brand-name">Wahba EGX</div>
        <div class="brand-tagline">Institutional Market Terminal</div>
    </div>
    """, unsafe_allow_html=True)

# 3. باقي الكود القديم كما هو بالظبط (المنطق البرمجي وقائمة الأسهم)
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
    "NASR", "NBKE", "NCGC", "NDMC", "PACH", "PICO", "PRDC", "QNBA", "REAC", "SAUD", 
    "SBIB", "SCEM", "SDTI", "SGGW", "SIPC", "SPRE", "UEGC", "UNIP", "UPMS", "UTRE", 
    "VERT", "WARY"
]

def analyze_engine(symbol):
    try:
        handler = TA_Handler(
            symbol=symbol, screener="egypt", exchange="EGX",
            interval=Interval.INTERVAL_1_DAY, timeout=15
        )
        data = handler.get_analysis()
        ind = data.indicators
        signal = data.summary["RECOMMENDATION"]
        
        if ind["close"] > ind["SMA10"] and ind["RSI"] > 40 and "BUY" in signal:
            return {
                "Ticker": symbol, "Price": round(ind["close"], 2),
                "RSI": round(ind["RSI"], 2), "Signal": signal.replace("_", " ")
            }
    except: return None

# 4. الواجهة البرمجية (كما هي بالظبط)
st.write("Quantitative Parameters: Price Action > SMA(10) | RSI(14) > 40")

if st.button('START INSTITUTIONAL MARKET SCAN'):
    with st.spinner('Scanning Market Feed...'):
        with ThreadPoolExecutor(max_workers=35) as executor:
            raw_res = list(executor.map(analyze_engine, STOCKS))
        results = [r for r in raw_res if r is not None]
        if results:
            st.success(f"Protocol Complete: {len(results)} Bullish Opportunities Found")
            st.table(pd.DataFrame(results))
        else:
            st.warning("No securities currently match the criteria.")

st.divider()
st.caption("WAHBA EGX | QUANTITATIVE TERMINAL | © 2026")
