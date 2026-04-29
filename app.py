import streamlit as st
import yfinance as yf
import pandas as pd

# 1. إعدادات الصفحة
st.set_page_config(page_title="Wahba Pro Terminal", layout="wide")

# 2. تعديل CSS لضمان ظهور الخط (اللون الأسود للخلفية البيضاء)
st.markdown("""
    <style>
    /* ضمان ظهور الخط في كل الأجهزة */
    .stApp { background-color: #ffffff !important; }
    h1, h2, h3, div, p, table { color: #000000 !important; font-family: 'Segoe UI', sans-serif !important; }
    
    /* تصميم الجدول ليظهر بوضوح */
    .stDataFrame { background-color: #ffffff; border: 1px solid #cccccc; }
    
    /* زرار التحديث */
    div.stButton > button { background-color: #333333; color: #ffffff !important; border-radius: 4px; padding: 10px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>Wahba Pro Market Terminal</h1>", unsafe_allow_html=True)

# القائمة (مختصرة للسرعة، ضيف الباقي براحتك)
tickers = ["COMI.CA", "SWDY.CA", "FWRY.CA", "TMGH.CA", "ORAS.CA", "ADIB.CA", "AMOC.CA", "ETEL.CA"]

@st.cache_data(ttl=600)
def load_data():
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
                    "MA50": round(float(ma50), 2),
                    "Trend": "Bullish" if df['Close'].iloc[-1] > ma50 else "Bearish"
                })
        except: continue
    return pd.DataFrame(results)

# عرض البيانات
df = load_data()
show_only_bullish = st.checkbox("إظهار الأسهم الصاعدة فقط")

if show_only_bullish:
    st.table(df[df['Trend'] == 'Bullish'])
else:
    st.table(df)
    
