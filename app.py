import streamlit as st
import yfinance as yf
import pandas as pd

# 1. إعدادات الصفحة
st.set_page_config(page_title="Wahba Pro Scanner", layout="wide")

# 2. تصميم CSS احترافي (أبيض ومريح للعين)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1a1a1a; font-family: 'Segoe UI', sans-serif; }
    .header-style { 
        text-align: center; padding: 25px; 
        background: #f8f9fa; border-bottom: 2px solid #333333;
        margin-bottom: 30px; 
    }
    div.stButton > button { 
        background-color: #333333; color: white; width: 100%;
        border: none; border-radius: 4px; font-weight: bold; padding: 12px;
    }
    div.stButton > button:hover { background-color: #000000; }
    .ad-slot { 
        background: #f8f9fa; border: 1px solid #dee2e6; 
        padding: 15px; text-align: center; color: #666;
        border-radius: 4px; margin-top: 20px; font-size: 0.8em;
    }
    </style>
""", unsafe_allow_html=True)

# 3. العنوان
st.markdown("<div class='header-style'><h1>Wahba Pro Market Scanner</h1></div>", unsafe_allow_html=True)

# 4. قائمة الأسهم (شاملة الـ 30 والـ 70)
tickers = [
    "ABUK", "ACGC", "ADIB", "AMOC", "COMI", "EKHO", "ETEL", "FWRY", "HELI", "HRHO", 
    "MNHD", "ORAS", "ORWE", "PHDC", "RMDA", "SWDY", "TAQA", "TMGH", "CIRA", "QNBA",
    "ESRS", "SKPC", "MFPC", "EGCH", "KIMA", "JUFO", "DOMT", "CCAP", "OIH", "BTFH",
    "ADCI", "AIH", "AIVC", "AMER", "ANFI", "APME", "ARAB", "ASPI", "ASRE", "ASU"
]
tickers_ca = [f"{t}.CA" for t in tickers]

# 5. منطقة التحكم والتحليل
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("Control Panel")
    if st.button("Run Daily Swing Scan"):
        results = []
        progress = st.progress(0)
        for i, ticker in enumerate(tickers_ca):
            try:
                # الاعتماد على الإغلاق اليومي (Daily Close)
                df = yf.download(ticker, period="6mo", interval="1d", progress=False)
                if not df.empty and len(df) >= 50:
                    df['MA50'] = df['Close'].rolling(window=50).mean()
                    
                    # الفلتر: الإغلاق الحالي فوق الـ MA50
                    if df['Close'].iloc[-1] > df['MA50'].iloc[-1]:
                        results.append({
                            "Ticker": ticker.replace(".CA", ""),
                            "Close Price": round(float(df['Close'].iloc[-1]), 2),
                            "MA50": round(float(df['MA50'].iloc[-1]), 2)
                        })
                progress.progress((i + 1) / len(tickers_ca))
            except: continue
        
        st.session_state.results = pd.DataFrame(results)
    
    st.markdown("<div class='ad-slot'>Advertising Space Available</div>", unsafe_allow_html=True)

with col2:
    st.subheader("Market Analysis Results")
    if 'results' in st.session_state and not st.session_state.results.empty:
        st.table(st.session_state.results)
        st.write("Scan complete. Please provide this table for further MA20 analysis.")
    else:
        st.info("Scanner is ready. Click 'Run Daily Swing Scan' to start.")
