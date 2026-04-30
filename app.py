import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Wahba EGX Terminal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Institutional Branding: SVG Logo & Custom Typography
# نص Wahba EGX بالأسود بالكامل، مع كود SVG للدرع الدقيق
st.markdown("""
    <style>
    /* Main Layout */
    .stApp {
        background-color: #ffffff;
    }
    
    /* Branded Header Container */
    .terminal-header {
        background-color: #fcfcfc;
        padding: 40px;
        border-radius: 4px;
        text-align: center;
        margin-bottom: 30px;
        border: 1px solid #eee;
    }
    
    /* Container for the Vector Logo */
    .logo-container {
        display: inline-block;
        width: 100px;
        height: 100px;
        margin-bottom: 20px;
    }
    
    /* Vector Logo (SVG) - Precise recreation of the shield and arrow from the image */
    .wahba-vector {
        width: 100%;
        height: 100%;
    }

    /* Main Title Text (Wahba EGX) - Absolute Black */
    .main-title {
        font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
        font-size: 52px;
        font-weight: 800;
        color: #1a1a1a; /* Black */
        margin: 0;
        letter-spacing: -2.5px;
        text-transform: uppercase;
        line-height: 1;
    }
    
    /* Sub-title Typography */
    .sub-title {
        color: #888888;
        font-size: 14px;
        letter-spacing: 5px;
        margin-top: 12px;
        text-transform: uppercase;
        font-weight: 500;
        line-height: 1.2;
    }
    
    /* Formal Button Styling */
    .stButton>button {
        background-color: #1a1a1a;
        color: white;
        border-radius: 4px;
        font-weight: 600;
        height: 3.8em;
        border: none;
        width: 100%;
        font-size: 15px;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #0052ff;
        color: white;
        box-shadow: 0 4px 12px rgba(0,82,255,0.3);
    }
    </style>
    
    <div class="terminal-header">
        <div class="logo-container">
            <svg class="wahba-vector" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <path d="M50,2.5 L97,16.5 L88,90 Q80,97.5 50,97.5 Q20,97.5 12,90 L3,16.5 Z" 
                      fill="none" stroke="#0052ff" stroke-width="5"/>
                <path d="M28,68 L36,45 L50,55 L64,45 L72,68" 
                      fill="none" stroke="#0052ff" stroke-width="5" stroke-linecap="round"/>
                <path d="M60,35 Q65,28 75,28 M75,28 L68,22 M75,28 L78,35 L68,22" 
                      fill="none" stroke="#0052ff" stroke-width="5" stroke-linecap="round"/>
            </svg>
        </div>
        <div class="main-title">Wahba EGX</div>
        <div class="sub-title">Algorithmic Market Terminal</div>
    </div>
    """, unsafe_allow_html=True)

# 3. Comprehensive EGX Asset List
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

def analyze_security(symbol):
    try:
        handler = TA_Handler(
            symbol=symbol,
            screener="egypt",
            exchange="EGX",
            interval=Interval.INTERVAL_1_DAY,
            timeout=12
        )
        data = handler.get_analysis()
        ind = data.indicators
        signal = data.summary["RECOMMENDATION"]
        
        # Fundamental Wahba EGX Logic
        if ind["close"] > ind["SMA10"] and ind["RSI"] > 40 and "BUY" in signal:
            return {
                "Ticker": symbol,
                "Price": round(ind["close"], 2),
                "RSI (14)": round(ind["RSI"], 2),
                "SMA (10)": round(ind["SMA10"], 2),
                "Signal Strength": signal.replace("_", " ")
            }
    except Exception:
        return None

# 4. Main Interface
st.divider()
st.write("Quantitative Parameters: Close > SMA(10) | RSI(14) > 40")

if st.button('INITIATE EGX MARKET SCAN'):
    with st.spinner('Synchronizing with Real-time EGX Feed...'):
        with ThreadPoolExecutor(max_workers=30) as executor:
            raw_res = list(executor.map(analyze_security, STOCKS))
        
        filtered_results = [r for r in raw_res if r is not None]
        
        if filtered_results:
            st.success(f"Scanning Complete: {len(filtered_results)} Opportunities Identified.")
            df = pd.DataFrame(filtered_results)
            st.dataframe(
                df.sort_values(by="RSI (14)", ascending=False),
                use_container_width=True,
                hide_index=True
            )
            
            # Metric Summary Grid
            st.markdown("---")
            st.subheader("Asset Metric Grid")
            metric_cols = st.columns(5)
            for idx, item in enumerate(filtered_results):
                with metric_cols[idx % 5]:
                    st.metric(
                        label=item["Ticker"],
                        value=f"{item['Price']} EGP",
                        delta=f"RSI {item['RSI (14)']}",
                        delta_color="normal"
                    )
        else:
            st.warning("No securities currently meet the quantitative bullish protocol.")

# 5. Formal Footer
st.divider()
st.caption("WAHBA EGX TERMINAL | INSTUTIONAL-GRADE ANALYSIS | © 2026 GLOBAL MARKETS")
