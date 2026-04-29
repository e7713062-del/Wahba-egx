import streamlit as st
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# 1. إعدادات الصفحة
st.set_page_config(page_title="Wahba Pro Terminal", layout="wide")

# 2. تصميم CSS احترافي (أبيض ومؤسسي)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1a1a1a; font-family: 'Segoe UI', sans-serif; }
    .header { text-align: center; padding: 20px; border-bottom: 2px solid #333; margin-bottom: 20px; }
    .stTable { width: 100%; border: 1px solid #dee2e6; }
    div.stButton > button { 
        background-color: #333; color: white; width: 100%; 
        border: none; border-radius: 4px; padding: 12px; font-weight: bold; 
    }
    div.stButton > button:hover { background-color: #000000; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'><h1>Wahba Pro Market Terminal</h1></div>", unsafe_allow_html=True)

# قائمة الأسهم المحدثة (ممكن تضيف أي سهم هنا)
tickers = ["COMI.CA", "SWDY.CA", "FWRY.CA", "TMGH.CA", "ORAS.CA", "ADIB.CA", "AMOC.CA", "ETEL.CA"]

# دالة سحب سهم واحد (خلفية)
def fetch_stock(ticker):
    try:
        # فترة زمنية كافية لحساب المتوسط الخمسيني
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
        if not df.empty:
            ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
            return {
                "Symbol": ticker.replace(".CA", ""),
                "Price": round(float(df['Close'].iloc[-1]), 2),
                "MA50": round(float(ma50), 2)
            }
    except: return None

# 3. التشغيل السريع
if st.button("تحديث البيانات (توازي)"):
    with st.spinner('جاري سحب البيانات...'):
        # المعالجة المتوازية لسحب الأسهم في وقت واحد
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(fetch_stock, tickers))
        
        final_data = [res for res in results if res is not None]
        st.table(pd.DataFrame(final_data))
else:
    st.info("اضغط على زر التحديث لعرض البيانات.")
