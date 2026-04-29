import streamlit as st
import yfinance as yf
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="Wahba Pro", layout="wide")
st.title("📊 لوحة مراقبة الأسهم اليومية")

# قائمة الأسهم
tickers = ["COMI.CA", "SWDY.CA", "FWRY.CA", "TMGH.CA", "ORAS.CA", "ADIB.CA"]

def get_data(ticker):
    try:
        # تحميل بيانات آخر يوم
        df = yf.download(ticker, period="1d", interval="1d", progress=False)
        if df.empty: return None
        
        last = float(df['Close'].iloc[-1])
        high = float(df['High'].iloc[-1])
        low = float(df['Low'].iloc[-1])
        open_p = float(df['Open'].iloc[0])
        change = ((last - open_p) / open_p) * 100
        
        return last, high, low, change
    except:
        return None

# عرض البيانات
for ticker in tickers:
    data = get_data(ticker)
    if data:
        last, high, low, change = data
        
        # حساب نسبة مكان السعر في الشمعة (0 إلى 100)
        # إذا كان السعر يساوي القاع، النسبة 0. إذا كان القمة، النسبة 100
        diff = high - low
        progress = int(((last - low) / diff) * 100) if diff > 0 else 50
        
        # تنسيق الأعمدة
        c1, c2, c3 = st.columns([1, 1, 3])
        
        with c1:
            st.write(f"### {ticker.replace('.CA', '')}")
        with c2:
            color = "🟢" if change >= 0 else "🔴"
            st.write(f"**{last:.2f}**")
            st.write(f"{color} {change:+.2f}%")
        with c3:
            # شريط تحميل يوضح موقع السعر الحالي
            st.progress(min(max(progress, 0), 100))
            
        st.divider()
