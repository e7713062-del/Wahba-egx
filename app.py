import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import time
import random

# 1. إعدادات المنصة الرسمية
st.set_page_config(page_title="Wahba EGX | Professional Terminal", layout="wide")

# 2. تصميم الواجهة المؤسسي
st.markdown("""
    <style>
    .main-header { text-align: center; padding: 30px 0; border-bottom: 1px solid #333; margin-bottom: 40px; }
    .brand-name { font-family: 'Inter', sans-serif; font-size: 45px; font-weight: 800; color: var(--text-color); margin: 0; }
    .brand-tagline { font-size: 12px; letter-spacing: 5px; text-transform: uppercase; opacity: 0.6; margin-top: 10px; }
    .status-indicator { display: inline-block; width: 10px; height: 10px; background-color: #00ff00; border-radius: 50%; margin-right: 10px; box-shadow: 0 0 8px #00ff00; }
    .disclaimer-box { padding: 20px; background-color: rgba(255, 0, 0, 0.05); border-left: 5px solid #ff4b4b; margin-top: 50px; font-size: 13px; color: #888; line-height: 1.6; }
    </style>
    <div class="main-header">
        <h1 class="brand-name">WAHBA EGX</h1>
        <div class="brand-tagline">Institutional Market Terminal • Stealth Batch Mode</div>
    </div>
""", unsafe_allow_html=True)

# 3. سحب الأسهم (283 سهم حالياً وأي جديد مستقبلاً)
@st.cache_data(ttl=1800)
def get_live_symbols():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.post(url, json={"filter":[],"options":{"lang":"en"},"markets":["egypt"]}, headers=headers, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data']]
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY"]

# 4. زر التشغيل بنظام "5-5"
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button('START SECURE BATCH SCAN (5 per step)', use_container_width=True):
        stocks = get_live_symbols()
        total = len(stocks)
        
        results = []
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        
        with st.spinner('Accessing Market Data in Stealth Mode...'):
            for i in range(0, total):
                symbol = stocks[i]
                try:
                    # تحديث الحالة لكل سهم
                    status_placeholder.markdown(f"📡 **Batch Syncing:** `{symbol}` ({i+1}/{total})")
                    progress_bar.progress((i + 1) / total)
                    
                    handler = TA_Handler(
                        symbol=symbol, screener="egypt", exchange="EGX",
                        interval=Interval.INTERVAL_1_DAY, timeout=10
                    )
                    analysis = handler.get_analysis()
                    rec = analysis.summary["RECOMMENDATION"]
                    
                    if "BUY" in rec:
                        results.append({
                            "Ticker": symbol,
                            "Price": round(analysis.indicators["close"], 2),
                            "RSI": round(analysis.indicators["RSI"], 2),
                            "Signal": rec.replace("_", " ")
                        })
                    
                    # نظام الـ "خمسة خمسة"
                    # بعد كل 5 أسهم، نصبر ثانية كاملة لراحة السيرفر
                    if (i + 1) % 5 == 0:
                        time.sleep(1.0 + random.uniform(0.1, 0.5))
                    else:
                        # بين كل سهم وسهم في نفس المجموعة، انتظار بسيط جداً
                        time.sleep(0.2)
                        
                except:
                    continue

            status_placeholder.empty()
            progress_bar.empty()

            if results:
                st.markdown(f"### <div class='status-indicator'></div> Identified Opportunities", unsafe_allow_html=True)
                st.table(pd.DataFrame(results).sort_values(by="Signal", ascending=False))
                
                strong_buys = [item for item in results if "STRONG BUY" in item["Signal"]]
                if strong_buys:
                    st.divider()
                    st.markdown("### <div class='status-indicator'></div> High-Priority Momentum", unsafe_allow_html=True)
                    st.table(pd.DataFrame(strong_buys))
            else:
                st.info("Scan Complete: No assets currently match the defined protocol.")

# 5. القسم القانوني
st.markdown("""
    <div class="disclaimer-box">
        <strong>إخلاء مسؤولية قانوني:</strong><br>
        هذه الأداة معلوماتية فقط. سوق المال متقلب والقرارات الاستثمارية مسؤولية المستخدم.
    </div>
""", unsafe_allow_html=True)

st.divider()
st.caption("WAHBA EGX | BATCH VERSION | © 2026")
