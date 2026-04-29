import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Wahba Pro", layout="wide")
st.title("📊 لوحة مراقبة الأسهم اليومية")

tickers = ["COMI.CA", "SWDY.CA", "FWRY.CA", "TMGH.CA", "ORAS.CA", "ADIB.CA"]

def fetch_stock_data(ticker):
    # محاولة جلب البيانات
    try:
        stock = yf.Ticker(ticker)
        # جلب بيانات يوم واحد
        df = stock.history(period="1d")
        
        if df.empty:
            return None
        
        last = float(df['Close'].iloc[-1])
        high = float(df['High'].iloc[-1])
        low = float(df['Low'].iloc[-1])
        # استخدام Open اليوم كمرجع للتغير
        open_p = float(df['Open'].iloc[-1])
        change = ((last - open_p) / open_p) * 100
        
        return last, high, low, change
    except Exception:
        return None

# عرض البيانات
for ticker in tickers:
    data = fetch_stock_data(ticker)
    
    if data:
        last, high, low, change = data
        # حساب نسبة التقدم (0-100)
        rng = high - low
        progress = int(((last - low) / rng) * 100) if rng > 0 else 50
        
        c1, c2, c3 = st.columns([1, 1, 3])
        with c1:
            st.write(f"**{ticker.replace('.CA', '')}**")
        with c2:
            st.write(f"**{last:.2f}** | {change:+.2f}%")
        with c3:
            # شريط ملون بسيط يعبر عن مكان السعر
            st.progress(min(max(progress, 0), 100))
        st.divider()
    else:
        # رسالة في حال عدم توفر بيانات
        st.error(f"غير قادر على تحميل بيانات {ticker.replace('.CA', '')} حالياً")
