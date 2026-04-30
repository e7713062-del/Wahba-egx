import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval
import pandas as pd

# 1. إعدادات الصفحة الاحترافية
st.set_page_config(
    page_title="Wahba EGX | Terminal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. تصميم الهوية البصرية (SVG Brand Identity)
# تم بناء الشعار برمجياً ليتطابق مع "براند وهبة" (الدرع والسهم وحرف W الهندسي)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    
    .terminal-header {
        text-align: center;
        padding: 40px 20px;
        margin-bottom: 30px;
        border-bottom: 2px solid #f0f0f0;
    }

    .logo-container {
        display: inline-block;
        width: 120px;
        height: 120px;
        margin-bottom: 20px;
    }

    /* نص الهوية باللون الأسود بالكامل */
    .brand-name {
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 52px;
        font-weight: 900;
        color: #000000;
        margin: 0;
        letter-spacing: -3px;
        text-transform: uppercase;
        line-height: 1;
    }

    .brand-tagline {
        color: #000000;
        font-size: 13px;
        letter-spacing: 5px;
        margin-top: 10px;
        text-transform: uppercase;
        font-weight: 700;
        opacity: 0.7;
    }

    /* تصميم زر المسح السوقي */
    .stButton>button {
        background-color: #000000;
        color: white;
        border-radius: 4px;
        font-weight: 800;
        height: 4em;
        width: 100%;
        border: none;
        font-size: 16px;
        transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .stButton>button:hover {
        background-color: #0052ff;
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(0,82,255,0.2);
    }
    </style>

    <div class="terminal-header">
        <div class="logo-container">
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <path d="M50,5 L95,22 L85,88 Q82,97 50,97 Q18,97 15,88 L5,22 Z" 
                      fill="none" stroke="#0052ff" stroke-width="7" stroke-linejoin="round"/>
                <rect x="35" y="45" width="4" height="15" fill="#0052ff" opacity="0.3"/>
                <rect x="45" y="35" width="4" height="25" fill="#0052ff" opacity="0.3"/>
                <rect x="55" y="40" width="4" height="20" fill="#0052ff" opacity="0.3"/>
                <path d="M25,70 L35,45 L50,60 L65,45 L80,15" 
                      fill="none" stroke="#0052ff" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M68,15 L80,15 L80,27" 
                      fill="none" stroke="#0052ff" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <div class="brand-name">Wahba EGX</div>
        <div class="brand-tagline">Institutional Market Terminal</div>
    </div>
    """, unsafe_allow_html=True)

# 3. القائمة الكاملة (220 سهم)
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

def analyze_engine(symbol):
    try:
        handler = TA_Handler(
            symbol=symbol,
            screener="egypt",
            exchange="EGX",
            interval=Interval.INTERVAL_1_DAY,
            timeout=15
        )
        data = handler.get_analysis()
        ind = data.indicators
        signal = data.summary["RECOMMENDATION"]
        
        # استراتيجية وهبة الذكية
        if ind["close"] > ind["SMA10"] and ind["RSI"] > 40 and "BUY" in signal:
            return {
                "Ticker": symbol,
                "Price": round(ind["close"], 2),
                "RSI": round(ind["RSI"], 2),
                "Signal": signal.replace("_", " "),
                "Status": "Bullish"
            }
    except:
        return None

# 4. واجهة المستخدم
st.write("Quantitative Parameters: Price Action > SMA(10) | RSI(14) > 40")

if st.button('START INSTITUTIONAL MARKET SCAN'):
    with st.spinner('Scanning 200+ Assets in Real-Time...'):
        with ThreadPoolExecutor(max_workers=35) as executor:
            raw_res = list(executor.map(analyze_engine, STOCKS))
        
        results = [r for r in raw_res if r is not None]
        
        if results:
            st.success(f"Protocol Complete: {len(results)} Bullish Opportunities Identified")
            st.table(pd.DataFrame(results))
            
            st.divider()
            cols = st.columns(5)
            for idx, item in enumerate(results):
                with cols[idx % 5]:
                    st.metric(label=item["Ticker"], value=f"{item['Price']} EGP", delta=f"RSI: {item['RSI']}")
        else:
            st.warning("No securities currently match the institutional bullish criteria.")

st.divider()
st.caption("WAHBA EGX | QUANTITATIVE TERMINAL | © 2026")
