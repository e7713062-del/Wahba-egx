import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# 1. إعداد المنصة
st.set_page_config(page_title="Wahba Pro Terminal", layout="wide")

# 2. تصميم CSS احترافي (السرعة في العرض)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1a1a1a; font-family: 'Segoe UI', sans-serif; }
    .header { text-align: center; padding: 20px; background: #f8f9fa; border-bottom: 2px solid #333; }
    div.stButton > button { background-color: #333; color: white; width: 100%; border: none; border-radius: 4px; padding: 12px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'><h1>Wahba Pro Market Terminal</h1></div>", unsafe_allow_html=True)

# 3. محرك بيانات سريع (يعتمد على ياهو فقط لتجنب مشاكل الموديول)
def get_data(tickers):
    # تحميل جماعي سريع
    data = yf.download(tickers, period="6mo", interval="1d", group_by='ticker', progress=False)
    return data

tickers = ["COMI.CA", "SWDY.CA", "FWRY.CA", "TMGH.CA", "ORAS.CA", "ADIB.CA", "AMOC.CA"]

# 4. واجهة العرض
if st.button("تحديث المنصة بسرعة البرق"):
    market_data = get_data(tickers)
    
    for t in tickers:
        try:
            df = market_data[t]
            if not df.empty:
                price = round(float(df['Close'].iloc[-1]), 2)
                ma50 = round(float(df['Close'].rolling(window=50).mean().iloc[-1]), 2)
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    if st.button(f"رسم بياني {t.replace('.CA', '')}", key=t):
                        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                        st.plotly_chart(fig, use_container_width=True)
                with col2:
                    st.write(f"**السعر:** {price}")
                with col3:
                    st.write(f"**MA50:** {ma50}")
        except: continue
