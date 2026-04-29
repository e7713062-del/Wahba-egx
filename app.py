import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# إعدادات الصفحة
st.set_page_config(page_title="منصة الإغلاقات", layout="wide")
st.title("📈 مراقبة الإغلاقات اليومية")

# قائمة الأسهم
tickers = ["COMI.CA", "SWDY.CA", "FWRY.CA", "TMGH.CA", "ORAS.CA", "ADIB.CA"]

def get_stock_data(ticker):
    try:
        # تحميل بيانات آخر يوم تداول
        df = yf.download(ticker, period="1d", interval="1d", progress=False)
        
        if df.empty:
            return None
        
        # التأكد من استخراج القيم بشكل صحيح
        last_price = float(df['Close'].iloc[-1])
        high = float(df['High'].iloc[-1])
        low = float(df['Low'].iloc[-1])
        open_price = float(df['Open'].iloc[0])
        change_pct = ((last_price - open_price) / open_price) * 100
        
        return {
            "symbol": ticker.replace(".CA", ""),
            "price": last_price,
            "high": high,
            "low": low,
            "change": change_pct
        }
    except Exception:
        return None

# عرض البيانات
for ticker in tickers:
    data = get_stock_data(ticker)
    
    if data:
        # تحديد الألوان بناءً على الأداء
        color = "green" if data['change'] >= 0 else "red"
        
        c1, c2, c3 = st.columns([1, 1, 3])
        
        with c1:
            st.write(f"### {data['symbol']}")
        with c2:
            st.metric(label="السعر", value=f"{data['price']:.2f}", delta=f"{data['change']:.2f}%")
        
        with c3:
            # إنشاء الشريط الملون (Indicator)
            fig = go.Figure(go.Indicator(
                mode="gauge",
                value=data['price'],
                gauge={
                    'axis': {'range': [data['low'], data['high']], 'tickwidth': 0, 'tickvals': []},
                    'bar': {'color': color, 'thickness': 0.8},
                    'bgcolor': "#e0e0e0"
                }
            ))
            fig.update_layout(height=50, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)
            
        st.write("---")
