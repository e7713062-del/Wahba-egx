import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Wahba EGX | Terminal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Advanced Styling (CSS)
st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
    }
    .main-header {
        text-align: center;
        padding: 20px;
    }
    .logo-img {
        width: 100%;
        max-width: 800px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #1a1a1a;
        color: white;
        border-radius: 4px;
        font-weight: 600;
        border: none;
        width: 100%;
        height: 3.5em;
        font-size: 18px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #0052ff;
        box-shadow: 0 4px 12px rgba(0,82,255,0.3);
    }
    .metric-container {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #0052ff;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Logo and Branding Section
st.markdown('<div class="main-header">', unsafe_allow_html=True)
# عرض اللوجو الذي يحتوي على الشموع والعملات
st.image("https://r.jina.ai/i/6688d08595884964893796ec1c70e703", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# 4. Assets List
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

def analyze_security(ticker):
    try:
        handler = TA_Handler(
            symbol=ticker,
            screener="egypt",
            exchange="EGX",
            interval=Interval.INTERVAL_1_DAY,
            timeout=10
        )
        analysis = handler.get_analysis()
        ind = analysis.indicators
        signal = analysis.summary["RECOMMENDATION"]
        
        # التقاطع الإيجابي: السعر فوق متوسط 10 و RSI فوق 40
        if ind["close"] > ind["SMA10"] and ind["RSI"] > 40 and "BUY" in signal:
            return {
                "Ticker": ticker,
                "Price": round(ind["close"], 2),
                "RSI": round(ind["RSI"], 2),
                "Signal": signal.replace("_", " "),
                "Trend": "Bullish Momentum"
            }
    except:
        return None

# 5. Execution UI
st.markdown("### Market Intelligence Terminal")
st.info("System Protocol: Institutional Technical Scan | Timeframe: Daily | Market: Egypt")

if st.button('Execute Comprehensive Market Scan'):
    with st.spinner('Accessing Global Data Servers...'):
        with ThreadPoolExecutor(max_workers=30) as executor:
            raw_results = list(executor.map(analyze_security, STOCKS))
        
        results = [r for r in raw_results if r is not None]
        
        if results:
            st.success(f"Analysis Complete: {len(results)} Opportunities Identified")
            df = pd.DataFrame(results)
            st.table(df)
            
            st.divider()
            st.subheader("Asset Performance Matrix")
            cols = st.columns(5)
            for i, item in enumerate(results):
                with cols[i % 5]:
                    st.metric(
                        label=item["Ticker"], 
                        value=f"{item['Price']} EGP", 
                        delta=f"RSI: {item['RSI']}"
                    )
        else:
            st.warning("Scan finished. No bullish patterns detected under current criteria.")

st.divider()
st.caption("WAHBA EGX TERMINAL | PROPRIETARY QUANTITATIVE SYSTEM | © 2026")
