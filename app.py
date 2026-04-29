import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from tvDatafeed import TvDatafeed, Interval
import base64

# 1. إعداد المنصة بالكامل
st.set_page_config(page_title="Wahba Holding Terminal", layout="wide")

# 2. تصميم CSS احترافي ومتطور (نمط المؤسسات)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1a1a1a; font-family: 'Helvetica Neue', sans-serif; }
    .header { text-align: center; padding: 25px; background: #f8f9fa; border-bottom: 2px solid #333333; margin-bottom: 30px; }
    .stTable { width: 100%; border: 1px solid #dee2e6; border-radius: 4px; }
    div.stButton > button { 
        background-color: #333; color: white; width: 100%; 
        border: none; border-radius: 4px; padding: 12px; font-weight: bold; 
    }
    div.stButton > button:hover { background-color: #000; }
    .logo-img { border-radius: 50%; vertical-align: middle; margin-right: 10px; }
    .symbol-name { font-weight: bold; font-size: 1.1em; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'><h1>Wahba Holding Financial Terminal</h1></div>", unsafe_allow_html=True)

# 3. محركات البيانات (التكامل بين الجمال والدقة)
tv = TvDatafeed()

@st.cache_data(ttl=600) # كاش لمدة 10 دقائق لصور الشركات
def get_company_logo(ticker_ca):
    try:
        ticker = yf.Ticker(ticker_ca)
        return ticker.info['logo_url']
    except:
        return None # في حال تعذر الحصول على اللوجو

def fetch_market_data(ticker):
    try:
        # بيانات TradingView (لسرعتها ودقتها)
        data = tv.get_hist(symbol=ticker, exchange='EGX', interval=Interval.in_daily, n_bars=60)
        ma50 = data['close'].rolling(window=50).mean().iloc[-1]
        
        # بيانات ياهو فاينانس (فقط للحصول على اللوجو)
        logo_url = get_company_logo(f"{ticker}.CA")
        
        return {
            "Logo": logo_url,
            "Symbol": ticker,
            "Price": round(float(data['close'].iloc[-1]), 2),
            "MA50": round(float(ma50), 2),
            "FullData": data # لحفظ البيانات للرسم البياني
        }
    except:
        return None

# قائمة الأسهم
tickers = ["COMI", "SWDY", "FWRY", "TMGH", "ORAS", "ADIB", "AMOC"]

# 4. التنفيذ والواجهة
if st.button("تحديث المنصة الاحترافية"):
    with st.spinner('جاري تحميل اللمسة الفنية للبيانات...'):
        market_results = []
        for t in tickers:
            res = fetch_market_data(t)
            if res: market_results.append(res)
        st.session_state.market_data = market_results

# عرض النتائج (الجدول المؤسسي)
if 'market_data' in st.session_state and st.session_state.market_data:
    results_df = pd.DataFrame(st.session_state.market_data)
    
    # تنسيق الجدول ليظهر اللوجو جمب الاسم
    st.write("### لوحة الأسعار اللحظية (EGX 30)")
    
    for _, row in results_df.iterrows():
        col1, col2, col3, col4 = st.columns([1, 4, 2, 2])
        
        with col1:
            if row['Logo']:
                st.markdown(f'<img src="{row["Logo"]}" class="logo-img" width="40" height="40">', unsafe_allow_html=True)
            else:
                st.markdown(f'<img src="https://via.placeholder.com/40" class="logo-img">', unsafe_allow_html=True) #Placeholder
        
        with col2:
            st.markdown(f'<span class="symbol-name">{row["Symbol"]}</span>', unsafe_allow_html=True)
            if st.button(f"تحليل {row['Symbol']}", key=row['Symbol']):
                # رسم الشموع اليابانية التفاعلي (Plotly)
                df_chart = row['FullData']
                fig = go.Figure(data=[go.Candlestick(x=df_chart.index,
                                                    open=df_chart['open'],
                                                    high=df_chart['high'],
                                                    low=df_chart['low'],
                                                    close=df_chart['close'])])
                fig.update_layout(title=f'رسم بياني للشموع اليابانية - {row["Symbol"]}', yaxis_title='السعر')
                st.plotly_chart(fig, use_container_width=True)

        with col3:
            st.metric("السعر الحالي", row['Price'])
        
        with col4:
            st.metric("متوسط 50", row['MA50'])
            
else:
    st.info("اضغط على تحديث المنصة الاحترافية لعرض اللمسة الفنية للبيانات.")
