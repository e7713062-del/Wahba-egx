import streamlit as st
from tradingview_ta import TA_Handler, Interval

# إعداد الصفحة
st.set_page_config(page_title="Wahba Pro: TV Analysis", layout="wide")

# تصميم الشريط الملون (مثل تريدنج فيو)
st.markdown("""
    <style>
    .trading-bar {
        height: 18px; width: 100%;
        background: linear-gradient(90deg, #ff4b4b 0%, #ffca28 50%, #2e7d32 100%);
        border-radius: 9px; position: relative; margin: 10px 0;
    }
    .pointer {
        height: 26px; width: 4px; background-color: #2196f3;
        position: absolute; top: -4px; border-radius: 2px;
        box-shadow: 0 0 4px rgba(0,0,0,0.6);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Wahba Pro: رادار توقعات السوق")

# قائمة الأسهم والمؤشرات في بورصة مصر (رموز تريدنج فيو)
assets = {
    "EGX 30 (الثلاثيني)": "EGX30",
    "EGX 70 (السبعيني)": "EGX70",
    "البنك التجاري الدولي": "COMI",
    "فوري": "FWRY",
    "طلعت مصطفى": "TMGH",
    "السويدي الكتريك": "SWDY"
}

def get_tv_prediction(symbol):
    try:
        handler = TA_Handler(
            symbol=symbol,
            screener="egypt",
            exchange="EGX",
            interval=Interval.INTERVAL_1_DAY
        )
        analysis = handler.get_analysis()
        return analysis.summary, analysis.indicators
    except:
        return None, None

# عرض النتائج
for name, symbol in assets.items():
    summary, indicators = get_tv_prediction(symbol)
    
    if summary:
        col1, col2, col3 = st.columns([2, 2, 4])
        
        with col1:
            st.subheader(name)
            st.write(f"الرمز: **{symbol}**")
            
        with col2:
            rec = summary['RECOMMENDATION']
            # تحديد اللون بناءً على التوصية
            color = "#00c853" if "BUY" in rec else "#ff1744" if "SELL" in rec else "#ffca28"
            st.markdown(f"
            
