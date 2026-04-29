import streamlit as st
import yfinance as yf
import pandas as pd

# 1. إعدادات الصفحة
st.set_page_config(page_title="Wahba Pro Terminal", layout="wide")

# 2. تصميم CSS احترافي (السرعة في العرض)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1a1a1a; font-family: 'Segoe UI', sans-serif; }
    .header { text-align: center; padding: 15px; border-bottom: 2px solid #333; }
    div.stButton > button { background-color: #333; color: white; width: 100%; padding: 10px; font-weight: bold; }
    /* تسريع عرض الجدول */
    .stDataFrame { animation: fadeIn 0.5s; }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'><h1>Wahba Pro Market Terminal</h1></div>", unsafe_allow_html=True)

# 3. محرك بيانات سريع جداً (Caching)
@st.cache_data(ttl=600) # البيانات هتتحدث كل 10 دقائق أوتوماتيكياً
def get_data(tickers):
    # تحميل جماعي
    data = yf.download(tickers, period="6mo", interval="1d", group_by='ticker', progress=False)
    results = []
    for ticker in tickers:
        try:
            df = data[ticker]
            if not df.empty:
                ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
                results.append({
                    "Symbol": ticker.replace(".CA", ""),
                    "Price": round(float(df['Close'].iloc[-1]), 2),
                    "MA50": round(float(ma50), 2)
                })
        except: continue
    return pd.DataFrame(results)

tickers = ["COMI.CA", "SWDY.CA", "FWRY.CA", "TMGH.CA", "ORAS.CA", "ADIB.CA", "AMOC.CA", "ETEL.CA"]

# 4. التنفيذ
if st.button("تحديث البيانات"):
    df = get_data(tickers)
    st.table(df)
else:
    st.info("اضغط على التحديث لعرض البيانات بسرعة فائقة.")
