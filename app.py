import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Wahba Pro: TradingView Style", layout="wide")

st.markdown("""
    <style>
    .trading-bar {
        height: 20px;
        width: 100%;
        background: linear-gradient(90deg, #ff4b4b 0%, #ffca28 50%, #2e7d32 100%);
        border-radius: 10px;
        position: relative;
    }
    .pointer {
        height: 30px;
        width: 4px;
        background-color: #2196f3;
        position: absolute;
        top: -5px;
        border-radius: 2px;
        box-shadow: 0 0 5px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Wahba Pro: تحليل الإغلاقات")

# قائمة المؤشرات والأسهم (تم اختيار رموز TradingView المتوافقة مع ياهو)
assets = {
    "EGX 30": "EGX30.CA",
    "EGX 70": "EGX70.CA",
    "المجموعة المالية هيرميس": "HRHO.CA",
    "فوري": "FWRY.CA",
    "السويدي الكتريك": "SWDY.CA"
}

def get_data(ticker):
    try:
        # جلب بيانات 5 أيام لضمان العمل في الإجازات
        df = yf.download(ticker, period="5d", interval="1d", progress=False)
        if df.empty: return None
        
        last = float(df['Close'].iloc[-1])
        high = float(df['High'].iloc[-1])
        low = float(df
        
