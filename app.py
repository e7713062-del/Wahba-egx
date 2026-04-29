import streamlit as st
import yfinance as yf
import pandas as pd

# 1. إعدادات الصفحة
st.set_page_config(page_title="Wahba Pro Terminal", layout="wide")

# 2. تصميم CSS احترافي (مؤسسي)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1a1a1a; font-family: 'Segoe UI', sans-serif; }
    .header-container { text-align: center; padding: 20px; border-bottom: 2px solid #333; margin-bottom: 20px; }
    .new-listing-box { background-color: #f8f9fa; border-left: 5px solid #333; padding: 15px; margin-bottom: 20px; }
    .stDataFrame { border: 1px solid #dee2e6; border-radius: 4px; }
    div.stButton > button { background-color: #333; color: white; width: 100%; border: none; border-radius: 4px; padding: 12px; font-weight: bold; }
    div.stButton > button:hover { background-color: #000000; }
    </style>
""", unsafe_allow_html=True)

# 3. الهيكل
st.markdown("<div class='header-container'><h1>Wahba Pro Market Terminal</h1></div>", unsafe_allow_html=True)

# 4. قائمة الأسهم
tickers = ["COMI.CA", "SWDY.CA", "FWRY.CA", "TMGH.CA", "ORAS.CA", "ADIB.CA", "AMOC.CA", "ETEL.CA"]

# 5. منطقة العمليات
col1, col2 = st.columns([1, 4])

with col1:
    if st.button("Run Market Terminal"):
        results = []
        for ticker in tickers:
            try:
                df = yf.download(ticker, period="6mo", interval="1d", progress=False)
                if not df.empty:
                    # اكتشاف الأسهم الجديدة (بيانات أقل من 50 يوم)
                    is_new = len(df) < 50
                    ma50 = df['Close'].rolling(window=50).mean().iloc[-1] if not is_new else 0
                    
                    results.append({
                        "Symbol": ticker.replace(".CA", ""),
                        "Price": round(float(df['Close'].iloc[-1]), 2),
                        "Status": "NEW" if is_new else "STABLE",
                        "MA50": round(float(ma50), 2)
                    })
            except: continue
        st.session_state.data = pd.DataFrame(results)

with col2:
    if 'data' in st.session_state:
        df = st.session_state.data
        
        # عرض الأسهم الجديدة في صندوق خاص
        new = df[df['Status'] == 'NEW']
        if not new.empty:
            st.markdown("<div class='new-listing-box'><h3>New Listings</h3></div>", unsafe_allow_html=True)
            st.table(new)
            
        st.subheader("Market Analysis (MA50)")
        st.table(df[df['Status'] == 'STABLE'])
