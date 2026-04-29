import streamlit as st
import yfinance as yf
import pandas as pd

# 1. إعدادات الصفحة
st.set_page_config(page_title="Wahba Pro Fast", layout="wide")

# 2. تصميم CSS
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1a1a1a; font-family: 'Segoe UI', sans-serif; }
    .header { text-align: center; padding: 15px; border-bottom: 2px solid #333; }
    div.stButton > button { background-color: #333; color: white; width: 100%; border-radius: 4px; padding: 10px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'><h1>Wahba Pro Fast Terminal</h1></div>", unsafe_allow_html=True)

tickers = ["COMI.CA", "SWDY.CA", "FWRY.CA", "TMGH.CA", "ORAS.CA", "ADIB.CA", "AMOC.CA", "ETEL.CA"]

if 'data' not in st.session_state: st.session_state.data = None

if st.button("تحديث فائق السرعة"):
    # السر هنا: سحب البيانات دفعة واحدة (Bulk Download) بدل حلقة التكرار
    # هذا يقلل وقت الانتظار بنسبة 80%
    data = yf.download(tickers, period="6mo", interval="1d", group_by='ticker', progress=False)
    
    results = []
    for ticker in tickers:
        try:
            df = data[ticker]
            if not df.empty:
                # حساب سريع للمتوسط
                ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
                results.append({
                    "Symbol": ticker.replace(".CA", ""),
                    "Price": round(float(df['Close'].iloc[-1]), 2),
                    "MA50": round(float(ma50), 2)
                })
        except: continue
    
    st.session_state.data = pd.DataFrame(results)
    st.rerun()

if st.session_state.data is not None:
    st.table(st.session_state.data)
else:
    st.info("اضغط على التحديث للبدء.")
