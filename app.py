import streamlit as st
import yfinance as yf
import pandas as pd

# إعداد الصفحة
st.set_page_config(page_title="Wahba Pro: TradingView Style", layout="wide")

# تصميم CSS للشريط الملون (مثل تريند فيو)
st.markdown("""
    <style>
    .trading-bar {
        height: 18px;
        width: 100%;
        background: linear-gradient(90deg, #ff4b4b 0%, #ffca28 50%, #2e7d32 100%);
        border-radius: 9px;
        position: relative;
        margin: 10px 0;
    }
    .pointer {
        height: 26px;
        width: 4px;
        background-color: #2196f3;
        position: absolute;
        top: -4px;
        border-radius: 2px;
        box-shadow: 0 0 4px rgba(0,0,0,0.6);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Wahba Pro: توقعات الإغلاق")

# القائمة المستهدفة (المؤشرات والأسهم القيادية)
assets = {
    "EGX 30 (الثلاثيني)": "EGX30.CA",
    "EGX 70 (السبعيني)": "EGX70.CA",
    "البنك التجاري الدولي": "COMI.CA",
    "فوري": "FWRY.CA",
    "طلعت مصطفى": "TMGH.CA",
    "السويدي الكتريك": "SWDY.CA"
}

def get_market_data(ticker):
    try:
        # جلب بيانات 5 أيام لضمان وجود داتا حتى في الإجازات
        df = yf.download(ticker, period="5d", interval="1d", progress=False)
        if df.empty or len(df) < 2:
            return None
        
        last = float(df['Close'].iloc[-1])
        high = float(df['High'].iloc[-1])
        low = float(df['Low'].iloc[-1])
        prev_close = float(df['Close'].iloc[-2])
        change = ((last - prev_close) / prev_close) * 100
        
        # حساب مكان الإغلاق في شمعة اليوم (0-100)
        score = ((last - low) / (high - low) * 100) if (high - low) > 0 else 50
        return last, change, score, high, low
    except:
        return None

# عرض البيانات
for name, symbol in assets.items():
    data = get_market_data(symbol)
    
    if data:
        last, change, score, h, l = data
        col1, col2, col3 = st.columns([2, 2, 4])
        
        with col1:
            st.markdown(f"### {name}")
            st.caption(f"السعر الحالي: {last:,.2f}")
            
        with col2:
            color = "#00c853" if change >= 0 else "#ff1744"
            st.markdown(f"<h2 style='color:{color}; margin:0;'>{change:+.2f}%</h2>", unsafe_allow_html=True)
            
            # منطق التوقع للغد بناءً على قوة الإغلاق
            if score > 75: pred = "🚀 إغلاق قوي (متوقع صعود)"
            elif score < 25: pred = "⚠️ إغلاق ضعيف (متوقع هبوط)"
            else: pred = "🔄 إغلاق متذبذب (عرضي)"
            st.write(f"**التوقع:** {pred}")
            
        with col3:
            st.write(f"المدى اليومي: {l:,.1f} — {h:,.1f}")
            # رسم الشريط الملون الاحترافي
            st.markdown(f"""
                <div class="trading-bar">
                    <div class="pointer" style="left: {min(max(score, 0), 98)}%;"></div>
                </div>
                """, unsafe_allow_html=True)
            st.caption("الشريط يوضح مكان الإغلاق: يمين (إيجابي) | يسار (سلبي)")
            
        st.divider()
    else:
        st.error(f"تعذر جلب بيانات {name} حالياً")

st.info("💡 ملاحظة: هذا التحليل يعتمد على مكان إغلاق السعر بالنسبة لأعلى وأقل سعر في الجلسة.")
