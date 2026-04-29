import streamlit as st
from tradingview_ta import get_multiple_analysis, Interval

st.set_page_config(page_title="Wahba Pro | السريع", layout="wide")

st.title("⚡ Wahba Pro: الماسح السريع")
st.write("تم تسريع الفحص ليعمل على السوق بالكامل في ثوانٍ معدودة...")

# قائمة الـ 160 سهم (أهم الرموز كمثال وتقدر تكملهم)
egypt_symbols = [
    "COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "EGAL", "PHDC", 
    "HRHO", "ESRS", "ORWE", "SKPC", "BTEL", "EGCH", "AMOC", "MFOT", 
    "HELI", "ORAS", "EKHO", "JUFO", "CANA", "ESGI", "GBCO", "CCAP",
    "AUTO", "MNHD", "PORT", "TALA", "ETEL", "ISPH", "RMDA", "CIRA"
    # ضيف كل الرموز اللي ناقصاك هنا.. السعة بتستحمل كتير
]

# إضافة البادئة الخاصة ببورصة مصر عشان السرعة
formatted_symbols = [f"EGX:{s}" for s in egypt_symbols]

try:
    # الفحص الجماعي (هنا السرعة كلها)
    analysis_results = get_multiple_analysis(
        screener="egypt",
        interval=Interval.INTERVAL_1_DAY,
        symbols=formatted_symbols
    )

    found_bullish = 0
    cols = st.columns(4) # 4 أعمدة لشكل أشيك

    for sym_full, result in analysis_results.items():
        if result:
            status = result.summary['RECOMMENDATION']
            sym_name = sym_full.split(":")[1]
            
            # فلترة الصاعد فقط
            if "BUY" in status:
                with cols[found_bullish % 4]:
                    st.success(f"🟢 {sym_name}")
                    st.caption(f"الحالة: {status}")
                found_bullish += 1
    
    if found_bullish == 0:
        st.warning("لا توجد أسهم صاعدة حالياً.")
    else:
        st.sidebar.metric("إجمالي الفرص الصاعدة", found_bullish)

except Exception as e:
    st.error("حدث خطأ أثناء الفحص السريع، تأكد من اتصال الإنترنت.")

st.sidebar.info("هذا التحديث يستخدم تقنية الفحص الجماعي لضمان أعلى سرعة.")
