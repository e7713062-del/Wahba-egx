import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval
import pandas as pd

# إعدادات الصفحة لظهورها بشكل احترافي
st.set_page_config(page_title="Wahba Pro | Sensitive", layout="wide", initial_sidebar_state="collapsed")

# تصميم الواجهة
st.title("🛡️ رادار Wahba Pro - اصطياد الفرص")
st.write("فحص لحظي للبورصة المصرية بناءً على إغلاق الشموع اليومية.")

# قائمة الأسهم (رموز البورصة المصرية على TradingView)
STOCKS = [
    "COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "EGAL", "PHDC", 
    "HRHO", "ESRS", "ORWE", "SKPC", "BTEL", "EGCH", "AMOC", "MFOT", 
    "HELI", "ORAS", "EKHO", "JUFO", "CANA", "ESGI", "GBCO", "CCAP",
    "AUTO", "MNHD", "PORT", "TALA", "ETEL", "ISPH", "RMDA", "CIRA",
    "ELSH", "OIH", "EMFD", "MTIE", "DSCW", "EHDR", "ASPI"
]

def check_stock(symbol):
    try:
        # جلب البيانات من TradingView
        handler = TA_Handler(
            symbol=symbol,
            screener="egypt",
            exchange="EGX",
            interval=Interval.INTERVAL_1_DAY,
            timeout=10
        )
        
        analysis = handler.get_analysis()
        d = analysis.indicators
        rec = analysis.summary["RECOMMENDATION"]
        
        # الشروط: السعر فوق متوسط 10، RSI فوق 40، وتوصية شراء
        if d["close"] > d["SMA10"] and d["RSI"] > 40 and "BUY" in rec:
            return {
                "السهم": symbol,
                "السعر": round(d["close"], 2),
                "RSI": round(d["RSI"], 2),
                "الحالة": rec.replace("_", " ")
            }
    except:
        return None

# زر بدء التشغيل
if st.button('🚀 إبدأ الفحص الشامل للأسهم'):
    with st.spinner('جاري فحص السوق المصري...'):
        with ThreadPoolExecutor(max_workers=25) as executor:
            results = list(executor.map(check_stock, STOCKS))
        
        # تصفية النتائج
        final_list = [res for res in results if res is not None]
        
        if final_list:
            st.success(f"✅ تم العثور على {len(final_list)} فرصة صاعدة")
            
            # عرض البيانات في جدول
            df = pd.DataFrame(final_list)
            st.dataframe(df, use_container_width=True)
            
            # عرض بطاقات سريعة
            st.divider()
            cols = st.columns(4)
            for i, item in enumerate(final_list):
                with cols[i % 4]:
                    st.metric(label=item["السهم"], value=item["السعر"], delta=f"RSI: {item['RSI']}")
        else:
            st.warning("لا توجد أسهم تحقق الشروط حالياً.")

st.divider()
st.caption("تم البرمجة بواسطة Wahba Pro - البيانات تتحدث تلقائياً")
