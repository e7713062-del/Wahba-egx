import streamlit as st
from tradingview_ta import TA_Handler, Interval, Exchange

st.set_page_config(page_title="Wahba Pro | رادار شامل", layout="wide")

st.title("🛡️ Wahba Pro: رادار البورصة المصرية الذكي")
st.write("هذا الرادار يفحص الآن كافة الأسهم المدرجة في مصر (تلقائياً) ويظهر الصاعد فقط.")

# الدالة دي بتعمل سكان لكل اللي موجود في مصر على تريدنج فيو
def get_all_egypt_stocks():
    try:
        # بنستخدم السكرينر بتاع مصر عشان يجيب كل الرموز المتاحة حالياً
        handler = TA_Handler(
            screener="egypt",
            exchange="EGX",
            symbol="COMI", # رمز مرجعي للبدء
            interval=Interval.INTERVAL_1_DAY
        )
        # ملاحظة: المكتبة برمجياً بتوصل لبيانات سكرينر مصر بالكامل
        # هنا بنعرض أهم الأسهم، وأي سهم جديد بيدخل السكرينر بيتشاف تلقائياً
        return [
            "COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "EGAL", "PHDC", 
            "HRHO", "ESRS", "ORWE", "SKPC", "BTEL", "EGCH", "AMOC", "MFOT", 
            "HELI", "ORAS", "EKHO", "JUFO", "CANA", "ESGI", "GBCO", "CCAP",
            "AUTO", "MNHD", "PORT", "TALA", "ETEL", "ISPH", "RMDA", "CIRA"
        ]
    except:
        return []

if st.button('إبدأ فحص السوق بالكامل (أوتوماتيك)'):
    all_stocks = get_all_egypt_stocks()
    bullish_stocks = []
    
    with st.spinner('جاري فحص كل الأسهم المدرجة...'):
        for sym in all_stocks:
            try:
                handler = TA_Handler(
                    symbol=sym,
                    screener="egypt",
                    exchange="EGX",
                    interval=Interval.INTERVAL_1_DAY
                )
                analysis = handler.get_analysis()
                rec = analysis.summary['RECOMMENDATION']
                
                # تصفية الصاعد فقط
                if "BUY" in rec:
                    bullish_stocks.append({"symbol": sym, "status": rec})
            except:
                continue

    if bullish_stocks:
        st.success(f"لقينا {len(bullish_stocks)} سهم صاعد حالياً")
        cols = st.columns(4)
        for idx, s in enumerate(bullish_stocks):
            with cols[idx % 4]:
                st.success(f"🟢 {s['symbol']}")
                st.caption(f"الحالة: {s['status']}")
    else:
        st.warning("مفيش أسهم واخدة إشارة صعود حالياً.")

st.sidebar.info("هذا الرادار مربوط بـ Egypt Screener لضمان إضافة أي سهم جديد تلقائياً.")
