import streamlit as st
import yfinance as yf
import pandas as pd

# 1. إعدادات الصفحة
st.set_page_config(page_title="Wahba Pro Terminal", layout="wide")

# 2. تصميم CSS
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1a1a1a; font-family: 'Segoe UI', sans-serif; }
    .header-container { text-align: center; padding: 20px; border-bottom: 2px solid #333; margin-bottom: 20px; }
    .new-listing-box { background-color: #f8f9fa; border-left: 5px solid #333; padding: 15px; margin-bottom: 20px; }
    div.stButton > button { background-color: #333; color: white; width: 100%; border: none; border-radius: 4px; padding: 12px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='header-container'><h1>Wahba Pro Market Terminal</h1></div>", unsafe_allow_html=True)

tickers = ["COMI.CA", "SWDY.CA", "FWRY.CA", "TMGH.CA", "ORAS.CA", "ADIB.CA", "AMOC.CA", "ETEL.CA"]

col1, col2 = st.columns([1, 4])

# 3. معالجة البيانات (بشرط وجودها)
if 'data' not in st.session_state:
    st.session_state.data = None

with col1:
    if st.button("Run Market Terminal"):
        results = []
        for ticker in tickers:
            try:
                df = yf.download(ticker, period="6mo", interval="1d", progress=False)
                if not df.empty:
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
        st.rerun() # تحديث الصفحة لعرض البيانات فوراً

with col2:
    if st.session_state.data is not None:
        df = st.session_state.data
        if not df.empty:
            # فصل البيانات بأمان
            new = df[df['Status'] == 'NEW']
            stable = df[df['Status'] == 'STABLE']
            
            if not new.empty:
                st.markdown("<div class='new-listing-box'><h3>New Listings</h3></div>", unsafe_allow_html=True)
                st.table(new)
            
            st.subheader("Market Analysis (MA50)")
            st.table(stable)
    else:
        st.info("اضغط على Run Market Terminal لبدء تحليل السوق.")
