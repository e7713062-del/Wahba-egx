import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Wahba MA50 Top 4", layout="wide")
st.markdown("<h1>Wahba Pro: أفضل 4 أسهم (MA50)</h1>", unsafe_allow_html=True)

# قائمة الأسهم
tickers = ["COMI.CA", "SWDY.CA", "FWRY.CA", "TMGH.CA", "OR
