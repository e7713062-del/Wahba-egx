import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Wahba Pro Terminal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1a1a1a; font-family: 'Segoe UI', sans-serif; }
    .header { text-align: center; padding: 20px; border-bottom: 2px solid #333; }
    div.stButton > button { background-color: #333; color: white; width: 100%; border-radius: 4px; padding: 12px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'><h1>Wahba Pro Market Terminal</h1></div>", unsafe_allow_html=True)

# الرموز الرسمية لـ ياهو فاينانس للبورصة المصرية
tickers = ["COMI.CA", "SWDY.CA", "FWRY.CA", "TMGH.CA", "ORAS.CA", "ADIB.CA", "AMOC.CA", "ETEL.CA"]

if st.button("تحديث البيانات"):
    results = []
    # سحب البيانات ككتلة واحدة (أسرع وأضمن)
    data = yf.download(tickers, period="6mo", interval="1d", group_by='ticker', progress=False)
    
    for ticker in tickers:
        try:
            df = data[ticker]
            if not df.empty:
                last_price = df['Close'].iloc[-1]
                ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
                results.append({
                    "Symbol": ticker.replace(".CA", ""),
                    "Price": round(float(last_price), 2),
                    "MA50": round(float(ma50), 2)
                })
        except: continue
        
    if results:
        st.table(pd.DataFrame(results))
    else:
        st.error("لم يتم العثور على بيانات. تأكد من اتصال الإنترنت.")
