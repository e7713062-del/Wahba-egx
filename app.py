import streamlit as st
import yfinance as yf

# إعداد الصفحة
st.set_page_config(page_title="Wahba Pro: Market Hub", layout="wide")
st.title("📊 تحليل مؤشرات البورصة المصرية")

# رموز المؤشرات (الثلاثيني والسبعيني)
indices = {
    "EGX 30 (الثلاثيني)": "^CASE30",
    "EGX 70 (السبعيني)": "EGX70.CA"
}

def get_index_data(symbol):
    try:
        # جلب بيانات آخر 5 أيام لضمان وجود بيانات حتى لو السوق قافل
        idx = yf.Ticker(symbol)
        df = idx.history(period="5d") 
        
        if df.empty:
            return None
        
        # أخذ آخر سطر (أحدث بيانات)
        last_row = df.iloc[-1]
        last_price = float(last_row['Close'])
        high = float(last_row['High'])
        low = float(last_row['Low'])
        open_p = float(last_row['Open'])
        change = ((last_price - open_p) / open_p) * 100
        
        return last_price, high, low, change
    except:
        return None

# عرض المؤشرات
for name, symbol in indices.items():
    data = get_index_data(symbol)
    
    col1, col2, col3 = st.columns([2, 2, 4])
    
    with col1:
        st.subheader(name)
        
    if data:
        last, high, low, change = data
        with col2:
            color = "green" if change >= 0 else "red"
            st.metric("المستوى", f"{last:,.2f}", f"{change:+.2f}%")
            
        with col3:
            # شريط الأداء اليومي
            diff = high - low
            progress = ((last - low) / diff) if diff > 0 else 0.5
            st.write(f"المدى اليومي: {low:,.0f} - {high:,.0f}")
            st.progress(min(max(progress, 0.0), 1.0))
    else:
        with col2:
            st.error("فشل جلب البيانات")
            st.caption("تأكد من اتصال الإنترنت أو رمز المؤشر")
            
    st.divider()

st.info("ملاحظة: البيانات قد تتأخر حتى 15 دقيقة حسب مصدر Yahoo Finance.")
