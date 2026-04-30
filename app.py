import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval
import pandas as pd

# --- 1. Configuration & Layout ---
st.set_page_config(
    page_title="Wahba Pro | Market Terminal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. Advanced Professional Styling (CSS) ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #ffffff;
    }
    /* Logo Styling */
    .logo-container {
        padding: 10px 0px;
        border-bottom: 2px solid #1a1a1a;
        margin-bottom: 20px;
    }
    .logo-text {
        font-family
