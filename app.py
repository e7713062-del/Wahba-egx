import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Wahba Pro", layout="centered")

st.title("Wahba Pro Market")

# تعريف الأسهم
tickers = ["COMI.CA", "SWDY.CA", "FWRY.CA", "AMOC.CA"]

# زر التحديث
if st.button("تحديث الأسعار"):
    for t in tickers:
        try:
            # تحميل السهم الواحد مباشرة (أكثر استقراراً)
            df = yf.Ticker(t).history(period="3mo")
            if not df.empty:
                price = round(df['Close'].iloc[-1], 2)
                ma50 = round(df['Close'].rolling(window=50).mean().iloc[-1], 2)
                
                # عرض البيانات
                st.write(f"---")
                st.write(f"**السهم:** {t.replace('.CA', '')}")
                st.write(f"السعر: {price} | المتوسط (MA50): {ma50}")
        except Exception as e:
            st.error(f"مشكلة في سحب بيانات {t}")

else:
    st.info("اضغط الزر للبدء.")
