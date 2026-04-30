import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval
import pandas as pd

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="Wahba EGX | Terminal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. تصميم الهوية البصرية (SVG Logo + Typography) - نص أسود ولوجو هندسي
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    
    .terminal-header {
        text-align: center;
        padding: 30px;
        margin-bottom: 20px;
        border-bottom: 1px solid #eee;
    }

    .logo-container {
        display: inline-block;
        width: 100px;
        height: 100px;
        margin-bottom: 15px;
    }

    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 45px;
        font-weight: 900;
        color: #000000; /* لون أسود تماماً */
        margin: 0;
        letter-spacing: -2px;
        text-transform: uppercase;
    }

    .sub-title {
        color: #000000; /* لون أسود تماماً */
        font-size:
