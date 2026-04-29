import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Wahba Pro: Predictor", layout="wide")
st.title("📊 توقعات حركة السوق بناءً على الإغلاق")

# رموز المؤشرات
indices = {
    "EGX 30 (الثلاثيني)": "^CASE30",
    "EGX 70 (السبعيني)": "EGX70.CA"
}

def analyze_closing(symbol):
    try:
        # جلب بيانات كافية لحساب المتوسط (آخر 20 يوم)
        df = yf.download(symbol, period="20d", interval="1d", progress=False)
        if df.empty: return None
        
        last_close = float(df['Close'].iloc[-1])
        prev_close = float(df['Close'].iloc[-2])
        high = float(df['High'].iloc[-1])
        low = float(df['Low'].iloc[-1])
        ma5 = float(df['Close'].rolling(5).mean().iloc[-1]) # متوسط 5 أيام
        
        change = ((last_close - prev_close) / prev_close) * 100
        
        # منطق التوقع:
        # 1. إذا السعر فوق المتوسط
        # 2. إذا الإغلاق في الثلث العلوي من شمعة اليوم
        position_in_range = (last_close - low) / (high - low) if (high - low) > 0 else 0.5
        
        prediction = "إيجابي (صاعد 🟢)" if (last_close > ma5 and position_in_range > 0.6) else "سلبي (حذر 🔴)"
        if 0.4 <= position_in_range <= 0.6: prediction = "عرضي (متذبذب 🟡)"
            
        return last_close, change, prediction, position_in_range
    except:
        return None

for name, symbol in indices.items():
    data = analyze_closing(symbol)
    
    if data:
        price, change, pred, pos = data
        col1, col2, col3 = st.columns([2, 2, 3])
        
        with col1:
            st.subheader(name)
            st.write(f"إغلاق اليوم: **{price:,.2f}**")
            
        with col2:
            st.metric("التغير اليومي", f"{change:+.2f}%")
            st.write(f"التوقع للغد: **{pred}**")
            
        with col3:
            st.write("موقع الإغلاق بالنسبة لليوم (قوة المشترين):")
            st.progress(min(max(pos, 0.0), 1.0))
            st.caption("اليمين = إغلاق عند القمة (قوي) | اليسار = إغلاق عند القاع (ضعيف)")
            
        st.divider()
    else:
        st.error(f"فشل جلب بيانات {name}")

st.warning("⚠️ هذا التوقع برمجي بناءً على الإغلاق فقط، ولا يعتبر نصيحة مالية. السوق دائماً متقلب!")
