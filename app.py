import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval
import time

st.set_page_config(page_title="Wahba Pro | Sensitive", layout="wide")
st.title("🛡️ رادار Wahba Pro - اصطياد الفرص")

# قائمة الأسهم (يفضل التأكد من كتابتها كما هي في TradingView)
STOCKS = [
    "COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "EGAL", "PHDC", 
    "HRHO", "ESRS", "ORWE", "SKPC", "BTEL", "EGCH", "AMOC", "MFOT", 
    "HELI", "ORAS", "EKHO", "JUFO", "CANA", "ESGI", "GBCO", "CCAP",
    "AUTO", "MNHD", "PORT", "TALA", "ETEL", "ISPH", "RMDA", "CIRA",
    "ELSH", "OIH", "EMFD", "MTIE", "DSCW", "EHDR", "ASPI"
]

def check(s):
    # محاولة الفحص لـ 3 مرات في حال حدوث خطأ في الاتصال
    for attempt in range(2): 
        try:
            h = TA_Handler(
                symbol=s,
                screener="egypt",
                exchange="EGX",
                interval=Interval.INTERVAL_1_DAY,
                timeout=10 # زيادة وقت الانتظار قليلاً
            )
            analysis = h.get_analysis()
            d = analysis.indicators
            
            # الشروط الحساسة
            price = d["close"]
            sma10 = d["SMA10"]
            rsi = d["RSI"]
            
            if price > sma10 and rsi > 40:
                return {"symbol": s, "price": price, "rsi": rsi}
            return None
        except Exception:
            if attempt == 0: # محاولة مرة تانية لو فشل أول مرة
                time.sleep(0.5)
                continue
            return None

if st.button('🚀 إبدأ الفحص الشامل'):
    with st.spinner('جاري فحص الأسهم بدقة...'):
        # تقليل الـ workers لـ 15 لتجنب الـ Block من السيرفر
        with ThreadPoolExecutor(max_workers=15) as exe:
            results = list(exe.map(check, STOCKS))
        
        # تصفية النتائج
        final = [r for r in results if r is not None]
        
        if final:
            st.success(f"✅ تم رصد {len(final)} سهم صاعد")
            cols = st.columns(4)
            for i, data in enumerate(final):
                with cols[i % 4]:
                    # عرض السعر والـ RSI لزيادة التأكيد
                    st.metric(label=data["symbol"], value=f"{data['price']:.2f}", delta=f"RSI: {data['rsi']:.1f}")
        else:
            st.warning("لا توجد أسهم تطابق الشروط حالياً. جرب مرة أخرى بعد قليل.")
