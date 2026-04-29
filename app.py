import streamlit as st
import pandas as pd
import time

# محاولة استيراد المكتبة مع معالجة الخطأ في حال لم تثبت بعد
try:
    from tradingview_ta import TA_Handler, Interval
except ImportError:
    st.error("المكتبة 'tradingview-ta' غير مثبتة. تأكد من وجود ملف requirements.txt وعمل Reboot للتطبيق.")
    st.stop()

st.set_page_config(page_title="Wahba Pro | SMA 50", layout="wide")

st.title("🛡️ Wahba Pro: رادار البورصة المصرية")
st.write("الفحص يعتمد على **الإغلاق اليومي** واختراق السعر لمتوسط 50 يوم.")

# قائمة الأسهم المصرية (تحديث يدوي لضمان الاستقرار)
STOCKS = [
    "COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "EGAL", "PHDC", 
    "HRHO", "ESRS", "ORWE", "SKPC", "BTEL", "EGCH", "AMOC", "MFOT", 
    "HELI", "ORAS", "EKHO", "JUFO", "CANA", "ESGI", "
