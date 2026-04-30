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

# 2. تصميم الهوية البصرية (SVG Logo + Typography) - نص أسود ولوجو هندسي
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    
    .terminal-header {
        text-align: center;
        padding: 30px;
        margin-bottom: 20px;
        border-bottom: 1px solid #eee;
    }

    .logo-container {
        display: inline-block;
        width: 100px;
        height: 100px;
        margin-bottom: 15px;
    }

    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 45px;
        font-weight: 900;
        color: #000000; /* لون أسود تماماً */
        margin: 0;
        letter-spacing: -2px;
        text-transform: uppercase;
    }

    .sub-title {
        color: #000000; /* لون أسود تماماً */
        font-size: 11px;
        letter-spacing: 4px;
        margin-top: 5px;
        text-transform: uppercase;
        font-weight: 700;
        opacity: 0.8;
    }

    .stButton>button {
        background-color: #000000;
        color: white;
        border-radius: 4px;
        font-weight: 700;
        height: 3.5em;
        width: 100%;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #0052ff;
    }
    </style>

    <div class="terminal-header">
        <div class="logo-container">
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <path d="M50,5 L92,22 L84,85 Q82,95 50,95 Q18,95 16,85 L8,22 Z" 
                      fill="none" stroke="#0052ff" stroke-width="6"/>
                <path d="M30,65 L38,42 L50,55 L62,42 L75,18" 
                      fill="none" stroke="#0052ff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M65,18 L75,18 L75,28" 
                      fill="none" stroke="#0052ff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <div class="main-title">Wahba EGX</div>
        <div class="sub-title">Institutional Market Terminal</div>
    </div>
    """, unsafe_allow_html=True)

# 3. قائمة الـ 220 سهم (تغطي كافة قطاعات البورصة المصرية)
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
    "ARVA", "ASRE", "ATQA", "BINV", "BIOC", "CERA", "COPR", "DECO", "DGTW", "DOMT",
    "EDBM", "EDFM", "EGAL", "EGAS", "EGBE", "EGLF", "EGNA", "EGRP", "EGTW", "EKHO",
    "ELKA", "ELSA", "EMFD", "ENGC", "EPCO", "EPHL", "ESGI", "ETEL", "EXPA", "FAIT",
    "FIRT", "GGCC", "GIZA", "GTHE", "GTWR", "HDBK", "ICID", "IDRE", "IFAP", "IRAX",
    "ISMA", "KABO", "KTSP", "LCSW", "MAAL", "MCQE", "MENA", "MEPA", "MICH", "MIFT",
    "MIPH", "MOIL", "MOSC", "MPCI", "MPRC", "MTIE", "NASR", "NBKE", "NCGC", "NDMC",
    "ODIN", "ORAS", "ORHD", "ORWE", "PACH", "PHAR", "PICO", "PORT", "PRDC", "QNBA",
    "RAYA", "REAC", "RREI", "SAUD", "SBIB", "SCEM", "SDTI", "SGGW", "SIPC", "SKPC",
    "SPMD", "SPRE", "UEGC", "UNIP", "UNIT", "UPMS", "UTRE", "VERT", "WARY", "ZMID"
]

def analyze_security(symbol):
    try:
        handler = TA_Handler(
            symbol=symbol,
            screener="egypt",
            exchange="EGX",
            interval=Interval.INTERVAL_1_DAY,
            timeout=15
        )
        analysis = handler.get_analysis()
        ind = analysis.indicators
        rec = analysis.summary["RECOMMENDATION"]
        
        # استراتيجية وهبة: سعر > SMA10 و RSI > 40 مع إشارة شراء
        if ind["close"] > ind["SMA10"] and ind["RSI"] > 40 and "BUY" in rec:
            return {
                "Ticker": symbol,
                "Price": round(ind["close"], 2),
                "RSI": round(ind["RSI"], 2),
                "Signal": rec.replace("_", " "),
                "Trend": "Bullish"
            }
    except:
        return None

# 4. واجهة التشغيل والنتائج
st.info("System Protocol: Institutional Technical Scan | Assets: 200+ | Market: Egypt")

if st.button('EXECUTE FULL MARKET SCAN'):
    with st.spinner('Accessing Real-time EGX Data...'):
        with ThreadPoolExecutor(max_workers=30) as executor:
            raw_res = list(executor.map(analyze_security, STOCKS))
        
        results = [r for r in raw_res if r is not None]
        
        if results:
            st.success(f"Analysis Complete: {len(results)} Bullish Opportunities Found.")
            df = pd.DataFrame(results)
            st.table(df)
            
            st.divider()
            cols = st.columns(5)
            for idx, item in enumerate(results):
                with cols[idx % 5]:
                    st.metric(label=item["Ticker"], value=f"{item['Price']} EGP", delta=f"RSI: {item['RSI']}")
        else:
            st.warning("No securities currently meet the quantitative growth criteria.")

st.divider()
st.caption("WAHBA EGX TERMINAL | PROPRIETARY ALGORITHM | © 2026 GLOBAL MARKETS")
