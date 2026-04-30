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

# 2. تصميم اللوجو البرمجي الاحترافي (بدون إيموجي)
st.markdown("""
    <style>
    /* تصميم اللوجو الهيكلي */
    .terminal-header {
        background-color: #1a1a1a;
        padding: 40px;
        border-radius: 4px;
        text-align: center;
        border-left: 10px solid #0052ff;
        margin-bottom: 30px;
    }
    .main-title {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 50px;
        font-weight: 900;
        color: #ffffff;
        margin: 0;
        letter-spacing: -2px;
        text-transform: uppercase;
    }
    .accent-color {
        color: #0052ff;
    }
    .chart-icon {
        display: inline-block;
        width: 40px;
        height: 4px;
        background-color: #0052ff;
        margin-bottom: 10px;
    }
    .sub-title {
        color: #888888;
        font-size: 14px;
        letter-spacing: 5px;
        margin-top: 10px;
        text-transform: uppercase;
    }
    /* تحسين شكل الأزرار والجداول */
    .stButton>button {
        background-color: #1a1a1a;
        color: white;
        border-radius: 0px;
        font-weight: bold;
        height: 3.5em;
        border: 1px solid #333;
    }
    .stButton>button:hover {
        background-color: #0052ff;
        border-color: #0052ff;
    }
    </style>
    
    <div class="terminal-header">
        <div class="chart-icon"></div>
        <div class="main-title">Wahba <span class="accent-color">EGX</span></div>
        <div class="sub-title">Algorithmic Trading Terminal</div>
    </div>
    """, unsafe_allow_html=True)

# 3. قائمة الأسهم الكاملة
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

def analyze_asset(symbol):
    try:
        handler = TA_Handler(
            symbol=symbol,
            screener="egypt",
            exchange="EGX",
            interval=Interval.INTERVAL_1_DAY,
            timeout=12
        )
        data = handler.get_analysis()
        i = data.indicators
        s = data.summary["RECOMMENDATION"]
        
        # استراتيجية Wahba EGX
        if i["close"] > i["SMA10"] and i["RSI"] > 40 and "BUY" in s:
            return {
                "Ticker": symbol,
                "Price": round(i["close"], 2),
                "RSI": round(i["RSI"], 2),
                "Signal": s.replace("_", " "),
                "Status": "Bullish"
            }
    except:
        return None

# 4. واجهة التشغيل
st.write("Quantitative Strategy: Price > SMA10 + RSI > 40")

if st.button('INITIALIZE MARKET SCAN'):
    with st.spinner('Accessing Real-Time Market Feed...'):
        with ThreadPoolExecutor(max_workers=30) as executor:
            raw_res = list(executor.map(analyze_asset, STOCKS))
        
        results = [r for r in raw_res if r is not None]
        
        if results:
            st.success(f"Scanning Complete: {len(results)} Bullish Patterns Identified")
            df = pd.DataFrame(results)
            st.table(df)
            
            st.divider()
            st.subheader("Market Summary Matrix")
            cols = st.columns(5)
            for idx, item in enumerate(results):
                with cols[idx % 5]:
                    st.metric(label=item["Ticker"], value=f"{item['Price']} EGP", delta=f"RSI {item['RSI']}")
        else:
            st.warning("No bullish configurations detected in current market cycle.")

st.divider()
st.caption("WAHBA EGX TERMINAL | INSTITUTIONAL GRADE ANALYSIS | © 2026")
