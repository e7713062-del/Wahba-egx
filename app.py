import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Wahba Pro", layout="wide")
st.title("📊 لوحة مراقبة الأسهم اليومية")

tickers = ["COMI.CA", "SWDY.CA", "FWRY.CA", "TMGH.CA", "ORAS.CA", "ADIB.CA"]

# إضافة مؤشر تحميل ليعرف المستخدم أن البرنامج يعمل
with st.spinner('جاري جلب بيانات السوق...'):
    for ticker in tickers:
        try:
            df = yf.download(ticker, period="1d", interval="1d", progress=False)
            
            if not df.empty:
                last = float(df['Close'].iloc[-1])
                high = float(df['High'].iloc[-1])
                low = float(df['Low'].iloc[-1])
                open_p = float(df['Open'].iloc[0])
                change = ((last - open_p) / open_p) * 100
                
                diff = high - low
                progress = int(((last - low) / diff) * 100) if diff > 0 else 50
                
                c1, c2, c3 = st.columns([1, 1, 3])
                with c1:
                    st.write(f"**{ticker.replace('.CA', '')}**")
                with c2:
                    color = "🟢" if change >= 0 else "🔴"
                    st.write(f"**{last:.2f}**")
                    st.write(f"{color} {change:+.2f}%")
                with c3:
                    st.progress(min(max(progress, 0), 100))
                st.divider()
            else:
                st.warning(f"لا توجد بيانات متاحة للسهم: {ticker}")
        except Exception as e:
            st.error(f"خطأ في تحميل {ticker}: {e}")
