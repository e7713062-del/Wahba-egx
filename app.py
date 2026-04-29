import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Wahba MA50 Top 4", layout="wide")
st.markdown("<h1>Wahba Pro: أفضل 4 أسهم (MA50)</h1>", unsafe_allow_html=True)

tickers = ["COMI.CA", "SWDY.CA", "FWRY.CA", "TMGH.CA", "ORAS.CA", "ADIB.CA", "AMOC.CA", "ETEL.CA", "EFIH.CA", "HRHO.CA"]

@st.cache_data(ttl=3600)
def load_data():
    results = []
    for ticker in tickers:
        try:
            df = yf.download(ticker, period="1y", interval="1d", progress=False)
            if df.empty or len(df) < 50: continue
            
            last_price = float(df['Close'].iloc[-1])
            ma50 = float(df['Close'].rolling(window=50).mean().iloc[-1])
            
            # حساب نسبة البعد عن المتوسط
            diff_percent = ((last_price - ma50) / ma50) * 100
            
            if last_price > ma50:
                results.append({
                    "Symbol": ticker.replace(".CA", ""),
                    "Price": round(last_price, 2),
                    "MA50": round(ma50, 2),
                    "Diff%": round(diff_percent, 2)
                })
        except: continue
    
    # ترتيب النتائج واختيار أفضل 4 أسهم (أقربهم للمتوسط من الأعلى)
    return pd.DataFrame(results).sort_values(by="Diff%", ascending=True).head(4)

df = load_data()

if not df.empty:
    st.subheader("🚀 أفضل 4 أسهم فوق متوسط الـ 50 يوم")
    st.dataframe(df, use_container_width=True)
else:
    st.warning("لا توجد أسهم حالياً فوق متوسط الـ 50 يوم.")
  
