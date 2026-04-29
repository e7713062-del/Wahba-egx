import streamlit as st
import yfinance as yf
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="Wahba Pro: Strong Trend", layout="wide")
st.markdown("<h1>Wahba Pro: تصفية الأسهم القوية (MA50 & MA200)</h1>", unsafe_allow_html=True)

# قائمة الأسهم
tickers = ["COMI.CA", "SWDY.CA", "FWRY.CA", "TMGH.CA", "ORAS.CA", "ADIB.CA", "AMOC.CA", "ETEL.CA", "EFIH.CA", "HRHO.CA"]

@st.cache_data(ttl=3600)
def load_data():
    results = []
    for ticker in tickers:
        try:
            # تحميل بيانات سنتين لضمان وجود بيانات كافية لـ MA200
            df = yf.download(ticker, period="2y", interval="1d", progress=False)
            
            # حاجز حماية: التأكد من أن السهم لديه بيانات كافية (أكثر من 200 يوم)
            if df.empty or len(df) < 200:
                continue
            
            # حساب المتوسطات
            last_price = float(df['Close'].iloc[-1])
            ma50 = float(df['Close'].rolling(window=50).mean().iloc[-1])
            ma200 = float(df['Close'].rolling(window=200).mean().iloc[-1])
            
            # شرط التصفية القوي: السعر فوق الـ 50 والـ 50 فوق الـ 200
            if last_price > ma50 > ma200:
                results.append({
                    "Symbol": ticker.replace(".CA", ""),
                    "Price": round(last_price, 2),
                    "MA50": round(ma50, 2),
                    "MA200": round(ma200, 2),
                    "Status": "Bullish Trend"
                })
        except Exception:
            # تجاهل أي سهم يسبب خطأ تقني دون توقيف البرنامج
            continue
            
    return pd.DataFrame(results)

# تنفيذ العملية وعرض النتائج
df = load_data()

if not df.empty:
    st.success(f"تم العثور على {len(df)} سهم في اتجاه صاعد قوي.")
    st.dataframe(df, use_container_width=True)
else:
    st.warning("لا توجد أسهم تحقق شروط الاتجاه الصاعد القوي حالياً (MA50 > MA200).")
