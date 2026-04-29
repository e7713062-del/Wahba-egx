import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Wahba Pro: Analysis", layout="wide")
st.title("📊 توقعات حركة السوق بناءً على الإغلاق")

# رموز المؤشرات اللي شغالة كويس في مصر
indices = {
    "EGX 30 (الثلاثيني)": "EGX30.CA",
    "EGX 70 (السبعيني)": "EGX70.CA"
}

def get_market_prediction(symbol):
    try:
        # بنجيب بيانات أسبوع عشان نضمن إننا نلاقي إغلاقات حتى لو في إجازة
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="7d")
        
        if df.empty or len(df) < 2:
            return None
        
        # بيانات آخر جلسة
        last_close = float(df['Close'].iloc[-1])
        prev_close = float(df['Close'].iloc[-2])
        high = float(df['High'].iloc[-1])
        low = float(df['Low'].iloc[-1])
        
        change = ((last_close - prev_close) / prev_close) * 100
        
        # حساب مكان الإغلاق (زي الشريط اللي في الصورة)
        # لو الإغلاق قمة = 100%، لو قاع = 0%
        range_day = high - low
        score = ((last_close - low) / range_day) if range_day > 0 else 0.5
        
        # منطق التوقع للغد
        if score > 0.7:
            pred = "إيجابي جداً (صعود محتمل 🟢)"
        elif score < 0.3:
            pred = "سلبي (هبوط محتمل 🔴)"
        else:
            pred = "متذبذب (حيرة 🟡)"
            
        return last_close, change, pred, score, high, low
    except:
        return None

# العرض
for name, symbol in indices.items():
    data = get_market_prediction(symbol)
    
    if data:
        price, change, pred, score, h, l = data
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            st.subheader(name)
            st.write(f"الإغلاق: **{price:,.2f}**")
            
        with col2:
            st.metric("التغير", f"{change:+.2f}%")
            st.write(f"التوقع: **{pred}**")
            
        with col3:
            st.write("قوة الإغلاق (مكانه في شمعة اليوم):")
            # شريط زي اللي في الصورة
            st.progress(min(max(score, 0.0), 1.0))
            st.caption(f"أقل: {l:,.0f} | أعلى: {h:,.0f}")
        st.divider()
    else:
        st.error(f"فشل جلب بيانات {name} - جرب تحديث الصفحة")

st.info("💡 نصيحة: إذا أغلق السوق عند القمة (الشريط ممتلئ)، فهذا يعني أن المشتري مسيطر وقد يكمل الصعود غداً.")
