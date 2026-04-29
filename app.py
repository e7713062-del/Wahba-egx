import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Wahba Pro", layout="wide")
st.title("📊 لوحة مراقبة الأسهم اليومية")

# قائمة الأسهم (تأكد أن الرموز صحيحة في Yahoo Finance)
tickers = ["EGX30.BO", "COMI.CA", "SWDY.CA", "FWRY.CA", "TMGH.CA"]

for ticker in tickers:
    try:
        # جلب بيانات آخر 5 أيام للتغلب على مشاكل بيانات اليوم الواحد
        stock = yf.Ticker(ticker)
        df = stock.history(period="5d")
        
        if not df.empty:
            curr = float(df['Close'].iloc[-1])
            high = float(df['High'].iloc[-1])
            low = float(df['Low'].iloc[-1])
            prev = float(df['Close'].iloc[-2]) # الإغلاق السابق
            change = ((curr - prev) / prev) * 100
            
            # حساب نسبة موقع السعر
            diff = high - low
            progress = ((curr - low) / diff) if diff > 0 else 0.5
            
            # التصميم
            cols = st.columns([1, 1, 3])
            cols[0].write(f"**{ticker.replace('.CA', '')}**")
            cols[1].write(f"{curr:.2f} ({change:+.2f}%)")
            cols[2].progress(min(max(progress, 0.0), 1.0))
            st.divider()
        else:
            st.warning(f"البيانات غير متوفرة حالياً لـ {ticker}")
    except Exception:
        continue
