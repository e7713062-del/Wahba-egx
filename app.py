import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval
import time

st.set_page_config(page_title="Wahba Pro | Scanner", layout="wide")
st.title("🛡️ رادار Wahba Pro - اصطياد الفرص")

# القائمة مع إضافة "EGX:" لضمان عملها 100%
RAW_STOCKS = [
    "COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "EGAL", "PHDC", 
    "HRHO", "ESRS", "ORWE", "SKPC", "BTEL", "EGCH", "AMOC", "MFOT", 
    "HELI", "ORAS", "EKHO", "JUFO", "CANA", "ESGI", "GBCO", "CCAP",
    "AUTO", "MNHD", "PORT", "TALA", "ETEL", "ISPH", "RMDA", "CIRA",
    "ELSH", "OIH", "EMFD", "MTIE", "DSCW", "EHDR", "ASPI"
]

STOCKS = [f"{s}" for s in RAW_STOCKS]

def check(s):
    try:
        # محاولة الاتصال بزيادة الـ timeout
        h = TA_Handler(
            symbol=s,
            screener="egypt",
            exchange="EGX",
            interval=Interval.INTERVAL_1_DAY,
            timeout=15 
        )
        analysis = h.get_analysis()
        d = analysis.indicators
        
        close_price = d.get("close")
        sma10 = d.get("SMA10")
        rsi = d.get("RSI")

        # التحقق من وجود القيم لتجنب الـ Errors
        if close_price and sma10 and rsi:
            # شرط مرن شوية للتأكد من ظهور نتائج
            if close_price > sma10 and rsi > 35: 
                return {"symbol": s, "price": close_price, "rsi": rsi}
    except Exception as e:
        return None
    return None

if st.button('🚀 إبدأ الفحص الآن'):
    with st.spinner('جاري فحص السوق المصري...'):
        # تقليل عدد العمليات المتوازية لـ 10 لضمان استقرار الاستجابة
        with ThreadPoolExecutor(max_workers=10) as exe:
            results = list(exe.map(check, STOCKS))
        
        final = [r for r in results if r is not None]
        
        if final:
            st.success(f"✅ تم رصد {len(final)} سهم تنطبق عليه الشروط")
            # عرض النتائج في مربعات
            rows = [final[i:i + 4] for i in range(0, len(final), 4)]
            for row in rows:
                cols = st.columns(4)
                for i, data in enumerate(row):
                    with
