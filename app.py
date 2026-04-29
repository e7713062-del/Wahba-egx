import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Wahba Pro: Market Scan", layout="wide")
st.markdown("<h1>Wahba Pro: كاشف حالة الأسهم</h1>", unsafe_allow_html=True)

tickers = ["COMI.CA", "SWDY.CA", "FWRY.CA", "TMGH.CA", "ORAS.CA", "ADIB.CA", "AMOC.CA", "ETEL.CA", "EFIH.CA", "HRHO.CA"]

@st.cache_data(ttl=3600)
def load_data():
    data_list = []
    for ticker in tickers:
        try:
            # تحميل بيانات أطول (سنتين)
            df = yf.download(ticker, period="2y", interval="1d", progress=False)
            if df.empty or len(df) < 50: continue
            
            last_price = float(df['Close'].iloc[-1])
            ma50 = float(df['Close'].rolling(window=50).mean().iloc[-1])
            
            # حساب نسبة السعر من المتوسط
            # إذا كانت النسبة موجبة يعني السعر فوق المتوسط
            status = ((last_price - ma50) / ma50) * 100
            
            data_list.append({
                "Symbol": ticker.replace(".CA", ""),
                "Price": round(last_price, 2),
                "MA50": round(ma50, 2),
                "Status%": round(status, 2)
            })
        except: continue
    return pd.DataFrame(data_list)

df = load_data()

if not df.empty:
    st.write("جدول حالة الأسهم (النسبة الموجبة تعني فوق الـ 50 يوم):")
    # الترتيب من الأقوى للأضعف
    df = df.sort_values(by="Status%", ascending=False)
    st.dataframe(df, use_container_width=True)
else:
    st.warning("لم يتم تحميل بيانات.")
