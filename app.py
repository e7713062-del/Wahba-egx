import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval
import pandas as pd

# إعدادات الصفحة الاحترافية
st.set_page_config(
    page_title="Wahba Pro | Terminal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# تصميم اللوجو والواجهة باستخدام CSS
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .logo-text {
        font-weight: 800;
        font-size: 35px;
        color: #1E1E1E;
        letter-spacing: -1px;
        margin-bottom: 0px;
    }
    .logo-subtext {
        color: #007BFF;
        font-size: 14px;
        font-weight: 500;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #1E1E1E;
        color: white;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #007BFF;
        color: white;
    }
    </style>
