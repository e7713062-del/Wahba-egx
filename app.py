import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import base64

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="Wahba EGX | Terminal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# دالة لتحويل الصورة لكود يفهمه المتصفح
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# تأكد من وضع ملف الصورة في نفس مجلد الكود وتسميته logo.png أو تغيير الاسم هنا
try:
    img_base64 = get_base64_of_bin_file('1000393267.png')
    logo_html = f'<img src="data:image/png;base64,{img_base64}" class="logo-image">'
except:
    # في حال لم يجد ملف الصورة، سيضع مساحة فارغة أو يمكنك وضع الشعار القديم هنا
    logo_html = '<div style="height:140px"></div>'

# 2. تصميم الهوية البصرية
st.markdown(f"""
    <style>
    .terminal-header {{
        text-align: center;
        padding: 40px 20px;
        margin-bottom: 30
