import streamlit as st
import yfinance as yf

# إعداد الصفحة
st.set_page_config(page_title="Wahba Pro", layout="wide")
st.title("📊 لوحة مراقبة الأسهم اليومية")

# قائمة الأسهم
tickers = ["COMI.CA", "SWDY.CA", "FWRY.CA", "TMGH.CA", "ORAS.CA", "ADIB.CA"]

def get_market_data(ticker):
    try:
        # جلب البيانات
        stock = yf.Ticker(ticker)
        df = stock.history(period="1d")
        
        if df.empty:
            return None
        
        last = float(df['Close'].iloc[-1])
        high = float(df['High'].iloc[-1])
        low = float(df['Low'].iloc[-1])
        open_p = float(df['Open'].iloc[-1])
        change = ((last - open_p) / open_p) * 100
        
        return last, high, low, change
    except:
        return None

# عرض البيانات بتصميم مشابه للصورة
for ticker in tickers:
    data = get_market_data(ticker)
    
    # تصميم الصف
    cols = st.columns([1, 1, 3])
    
    with cols[0]:
        st.write(f"**{ticker.replace('.CA', '')}**")
        
    if data:
        last, high, low, change = data
        
        with cols[1]:
            color = "🟢" if change >= 0 else "🔴"
            st.write(f"{last:.2f} ({change:+.2f}%)")
            
        with cols[2]:
            # شريط الأداء: يمثل مكان السعر بين الـ low والـ high
            rng = high - low
            progress = ((last - low) / rng) if rng > 0 else 0.5
            st.progress(min(max(progress, 0.0), 1.0))
    else:
        with cols[1]:
            st.caption("بيانات غير متاحة")
            
    st.divider()
