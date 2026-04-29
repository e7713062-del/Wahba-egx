import streamlit as st
import yfinance as yf
import pandas as pd

# إعداد الصفحة
st.set_page_config(page_title="Wahba Pro: MA50", layout="wide")
st.markdown("<h1>Wahba Pro: أفضل الأسهم فوق متوسط الـ 50 يوم</h1>", unsafe_allow_html=True)

tickers = ["COMI.CA", "SWDY.CA", "FWRY.CA", "TMGH.CA", "ORAS.CA", "ADIB.CA", "AMOC.CA", "ETEL.CA", "EFIH.CA", "HRHO.CA"]

@st.cache_data(ttl=3600)
def load_data():
    results = []
    for ticker in tickers:
        try:
            # تحميل البيانات
            df = yf.download(ticker, period="1y", interval="1d", progress=False)
            
            # التأكد من وجود بيانات كافية
            if df.empty or len(df) < 50: 
                continue
            
            last_price = float(df['Close'].iloc[-1])
            ma50 = float(df['Close'].rolling(window=50).mean().iloc[-1])
            
            # شرط: السعر فوق المتوسط
            if last_price > ma50:
                diff_percent = ((last_price - ma50) / ma50) * 100
                results.append({
                    "Symbol": ticker.replace(".CA", ""),
                    "Price": round(last_price, 2),
                    "MA50": round(ma50, 2),
                    "Diff%": round(diff_percent, 2)
                })
        except Exception:
            continue
            
    # إرجاع جدول فارغ إذا لم تتوفر نتائج لتجنب الخطأ
    if not results:
        return pd.DataFrame()
    
    return pd.DataFrame(results).sort_values(by="Diff%", ascending=True)

# تشغيل الدالة
df = load_data()

# عرض النتائج
if not df.empty:
    # عرض أفضل 4 أسهم كما طلبت
    st.subheader("🚀 أفضل 4 أسهم (الأقرب للمتوسط)")
    st.dataframe(df.head(4), use_container_width=True)
    
    st.subheader("📊 جميع الأسهم فوق المتوسط")
    st.dataframe(df, use_container_width=True)
else:
    st.warning("لا توجد أسهم حالياً تحقق شرط السعر فوق متوسط الـ 50 يوم.")
    
