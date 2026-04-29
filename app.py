import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Swing Trader Pro", layout="wide")
st.markdown("<h1>Wahba Swing Terminal</h1>", unsafe_allow_html=True)

tickers = ["COMI.CA", "SWDY.CA", "FWRY.CA", "TMGH.CA", "ORAS.CA", "ADIB.CA", "AMOC.CA", "ETEL.CA", "EFIH.CA", "HRHO.CA"]

@st.cache_data(ttl=3600) # زيادة الوقت لأن السيوينج مش محتاج تحديث كل دقيقة
def load_data():
    results = []
    for ticker in tickers:
        try:
            df = yf.download(ticker, period="1y", interval="1d", progress=False)
            if not df.empty:
                last_price = float(df['Close'].iloc[-1])
                ma50 = float(df['Close'].rolling(window=50).mean().iloc[-1])
                ma200 = float(df['Close'].rolling(window=200).mean().iloc[-1])
                
                # حساب RSI بسيط
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs.iloc[-1]))

                results.append({
                    "Symbol": ticker.replace(".CA", ""),
                    "Price": round(last_price, 2),
                    "Trend": "Bullish" if last_price > ma50 > ma200 else "Neutral/Bearish",
                    "RSI": round(float(rsi), 2)
                })
        except: continue
    return pd.DataFrame(results)

df = load_data()

# عرض الأسهم الجاهزة للسيوينج (اللي اتجاهها صاعد والـ RSI تحت 70)
swing_candidates = df[(df['Trend'] == 'Bullish') & (df['RSI'] < 70)]

st.subheader("🚀 فرص السيوينج الحالية (اتجاه صاعد + RSI صحي)")
st.table(swing_candidates)

st.subheader("📊 كل الأسهم")
st.table(df)
