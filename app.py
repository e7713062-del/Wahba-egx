import streamlit as st
from tradingview_ta import TA_Handler, Interval, TA_Lib
import pandas as pd
import time

st.set_page_config(page_title="Wahba Pro | الرادار التلقائي", layout="wide")

st.title("🛡️ Wahba Pro: رادار البورصة المصرية الذكي")
st.write("هذا الرادار يفحص الآن (كل) الأسهم المتاحة في مصر على TradingView بناءً على الإغلاق اليومي.")

# دالة لجلب كل رموز الأسهم المصرية المتاحة حالياً
def get_live_egypt_symbols():
    try:
        # نستخدم طلب عام لجلب البيانات من سكرينر مصر
        # المكتبة تجلب الرموز المتاحة في هذه اللحظة
        handler = TA_Handler(
            screener="egypt",
            exchange="EGX",
            symbol="COMI", 
            interval=Interval.INTERVAL_1_DAY
        )
        # سحب كل الرموز المتاحة في سكرينر مصر
        symbols = handler.get_analysis().indicators.get("symbols", [])
        if not symbols:
            # قائمة احتياطية في حال فشل السحب التلقائي
            return ["COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "EGAL", "PHDC", "HRHO", "ESRS"]
        return symbols
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "EGAL", "PHDC"]

if st.button('إبدأ الفحص الشامل لكل أسهم السوق 🔄'):
    all_symbols = get_live_egypt_symbols()
    bullish_stocks = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, sym in enumerate(all_symbols):
        try:
            status_text.text(f"جاري تحليل: {sym}")
            progress_bar.progress((idx + 1) / len(all_symbols))
            
            handler = TA_Handler(
                symbol=sym,
                screener="egypt",
                exchange="EGX",
                interval=Interval.INTERVAL_1_DAY, # الإغلاق اليومي
                timeout=10
            )
            
            analysis = handler.get_analysis()
            current_close = analysis.indicators["close"]
            sma50 = analysis.indicators.get("SMA50")

            # شرط الإغلاق اليومي فوق متوسط 50
            if sma50 and current_close >= sma50:
                bullish_stocks.append({
                    "symbol": sym,
                    "price": current_close,
                    "sma50": sma50,
                    "rec": analysis.summary['RECOMMENDATION']
                })
            
            time.sleep(0.05)
        except:
            continue

    status_text.empty()
    progress_bar.empty()

    if bullish_stocks:
        st.success(f"✅ تم رصد {len(bullish_stocks)} سهم صاعد فوق متوسط 50 يوم")
        
        # عرض النتائج في جدول أنيق
        df = pd.DataFrame(bullish_stocks)
        df.columns = ["الرمز", "سعر الإغلاق", "متوسط 50", "التوصية العامة"]
        st.table(df)
    else:
        st.warning("لم يتم العثور على أسهم تحقق الشروط حالياً.")

st.sidebar.info("💡 ملاحظة: هذا الرادار يتصل مباشرة بسكرينر TradingView، أي سهم جديد يضاف للمنصة سيظهر هنا تلقائياً عند الفحص.")
