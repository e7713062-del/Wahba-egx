import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import base64

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="Wahba EGX | Terminal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# دالة لتحويل الصورة لكود يفهمه المتصفح
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

# محاولة تحميل الصورة
img_base64 = get_base64_of_bin_file('1000393267.png')

if img_base64:
    logo_html = f'<img src="data:image/png;base64,{img_base64}" class="logo-image">'
else:
    # شكل احتياطي لو الصورة مش موجودة
    logo_html = '<div style="height:140px; border:1px dashed #ccc; display:flex; align-items:center; justify-content:center;">Logo Not Found</div>'

# 2. تصميم الهوية البصرية (تم إصلاح أقواس الـ CSS هنا)
st.markdown(f"""
    <style>
    .terminal-header {{
        text-align: center;
        padding: 40px 20px;
        margin-bottom: 30px;
    }}
    .logo-container {{
        display: inline-block;
        width: 140px;
        height: 140px;
        margin-bottom: 15px;
    }}
    .logo-image {{
        width: 100%;
        height: auto;
    }}
    .brand-name {{
        font-family: 'Inter', sans-serif;
        font-size: 50px;
        font-weight: 900;
        margin: 0;
        letter-spacing: -2px;
        text-transform: uppercase;
        line-height: 1;
        color: var(--text-color);
    }}
    .brand-tagline {{
        font-size: 13px;
        letter-spacing: 4px;
        margin-top: 10px;
        text-transform: uppercase;
        font-weight: 700;
        opacity: 0.8;
        color: var(--text-color);
    }}
    .stButton>button {{
        border-radius: 4px;
        font-weight: 800;
        height: 3.8em;
        width: 100%;
        border: 1px solid currentColor;
    }}
    </style>

    <div class="terminal-header">
        <div class="logo-container">
            {logo_html}
        </div>
        <div class="brand-name">Wahba EGX</div>
        <div class="brand-tagline">Institutional Market Terminal</div>
    </div>
    """, unsafe_allow_html=True)

# 3. باقي الكود (بدون أي تغيير)
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
