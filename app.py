import streamlit as st
import yfinance as yf
import pandas as pd

# 1. إعدادات الصفحة
st.set_page_config(page_title="Wahba Pro Terminal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    h1, h2, h3, div, p, table { color: #000000 !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>Wahba Pro Market Terminal (EGX 30 + 70)</h1>", unsafe_allow_html=True)

# قائمة شاملة لأسهم المؤشرين
# قمت بتجميع الرموز الرئيسية للمؤشرين
tickers = [
    "COMI.CA", "SWDY.CA", "FWRY.CA", "TMGH.CA", "ORAS.CA", "ADIB.CA", "AMOC.CA", 
    "ETEL.CA", "EFIH.CA", "HRHO.CA", "JUFO.CA", "PHDC.CA", "SKPC.CA", "QNBA.CA",
    "IRON.CA", "ELEC.CA", "DAPH.CA", "RAYA.CA", "CCAP.CA", "CIRA.CA", "SPMD.CA",
    "ABUK.CA", "ASCM.CA", "MFPC.CA", "ORWE.CA", "ZMID.CA", "CANA.CA", "EKHOA.CA"
]

@st.cache_data(ttl=600)
def load_data():
    # تحميل البيانات
    data = yf.download(tickers, period="6mo", interval="1d", group_by='ticker', progress=False)
    results = []
    
    for ticker in tickers:
        try:
            # التأكد من هيكل البيانات
            df = data[ticker] if len(tickers) > 1 else data
            if not df.empty:
                current_price = float(df['Close'].iloc[-1])
                ma50 = float(df['Close'].rolling(window=50).mean().iloc[-1])
                
                # حساب القوة
                strength = (current_price - ma50) / ma50
                
                results.append({
                    "Symbol": ticker.replace(".CA", ""),
                    "Price": round(current_price, 2),
                    "MA50": round(ma50, 2),
                    "Trend": "Bullish" if current_price > ma50 else "Bearish",
                    "Strength": strength
                })
        except: continue
    return pd.DataFrame(results)

df = load_data()

# تصفية وإيجاد الأقوى
bullish_stocks = df[df['Trend'] == 'Bullish'].sort_values(by="Strength", ascending=False)

# عرض النتيجة
st.subheader("🚀 أقوى سهمين صاعدين حالياً (EGX 30 & 70)")
if not bullish_stocks.empty:
    st.table(bullish_stocks.head(2)[["Symbol", "Price", "MA50"]])
else:
    st.write("لا توجد أسهم فوق المتوسط حالياً.")

st.subheader("📊 قائمة الأسهم المتابعة")
show_only_bullish = st.checkbox("إظهار الأسهم الصاعدة فقط")

if show_only_bullish:
    st.table(bullish_stocks[["Symbol", "Price", "MA50", "Trend"]])
else:
    st.table(df[["Symbol", "Price", "MA50", "Trend"]])
