import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# 1. إعدادات الصفحة - تصميم مؤسسي خفيف
st.set_page_config(page_title="Wahba Pro Terminal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000000; font-family: sans-serif; }
    .header { text-align: center; padding: 20px; border-bottom: 2px solid #000; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'><h1>Wahba Pro Market Terminal</h1></div>", unsafe_allow_html=True)

# 2. قائمة الأسهم
tickers = ["COMI.CA", "SWDY.CA", "FWRY.CA", "TMGH.CA", "ORAS.CA", "ADIB.CA", "AMOC.CA"]

# 3. سحب البيانات بطريقة مباشرة (بدون موديولات إضافية)
if st.button("تحديث السوق"):
    data = yf.download(tickers, period="6mo", interval="1d", group_by='ticker', progress=False)
    
    for t in tickers:
        try:
            df = data[t]
            if not df.empty:
                last_price = round(float(df['Close'].iloc[-1]), 2)
                ma50 = round(float(df['Close'].rolling(window=50).mean().iloc[-1]), 2)
                
                # عرض البيانات في أعمدة منظمة
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.write(f"### {t.replace('.CA', '')}")
                col2.write(f"السعر: {last_price}")
                col3.write(f"MA50: {ma50}")
                
                # زر لعرض الرسم البياني (بدون تعقيد)
                if st.button(f"رسم بياني {t}", key=t):
                    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                    st.plotly_chart(fig, use_container_width=True)
        except:
            continue
else:
    st.info("اضغط على تحديث السوق لعرض الأسعار.")
