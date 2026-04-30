import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import time

# 1. إعدادات المنصة المؤسسية
st.set_page_config(page_title="Wahba EGX | Institutional Terminal", layout="wide")

# 2. تصميم الواجهة الرسمي
st.markdown("""
    <style>
    .main-header { text-align: center; padding: 30px 0; border-bottom: 1px solid #333; margin-bottom: 40px; }
    .brand-name { font-family: 'Inter', sans-serif; font-size: 45px; font-weight: 800; color: var(--text-color); margin: 0; }
    .brand-tagline { font-size: 12px; letter-spacing: 5px; text-transform: uppercase; opacity: 0.6; margin-top: 10px; }
    .status-indicator { display: inline-block; width: 10px; height: 10px; background-color: #00ff00; border-radius: 50%; margin-right: 10px; box-shadow: 0 0 8px #00ff00; }
    </style>
    <div class="main-header">
        <h1 class="brand-name">WAHBA EGX</h1>
        <div class="brand-tagline">Institutional Market Terminal • 283 Assets Detected</div>
    </div>
""", unsafe_allow_html=True)

# 3. دالة سحب كل الأسهم (الـ 283 سهم الحاليين وأي سهم جديد مستقبلاً)
@st.cache_data(ttl=1800) # تحديث القائمة كل نص ساعة
def get_live_symbols():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        # بنطلب من السيرفر يبعت لنا كل الرموز المتاحة في مصر حالياً
        res = requests.post(url, json={"filter":[],"options":{"lang":"en"},"markets":["egypt"]}, timeout=15).json()
        tickers = [item['s'].split(':')[1] for item in res['data']]
        return tickers
    except:
        return []

# 4. زر التشغيل والمسح الذكي
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button('EXECUTE MASTER SCAN (ALL ASSETS)', use_container_width=True):
        stocks = get_live_symbols()
        total = len(stocks)
        
        if total == 0:
            st.error("Connection Error: Unable to fetch EGX symbols.")
        else:
            results = []
            progress_bar = st.progress(0)
            status_placeholder = st.empty()
            
            with st.spinner(f'Processing {total} assets...'):
                for i, symbol in enumerate(stocks):
                    try:
                        # تحديث اسم السهم والتحميل فوراً قدامك
                        status_placeholder.markdown(f"🔍 **Analyzing:** `{symbol}` ({i+1}/{total})")
                        progress_bar.progress((i + 1) / total)
                        
                        handler = TA_Handler(
                            symbol=symbol,
                            screener="egypt",
                            exchange="EGX",
                            interval=Interval.INTERVAL_1_DAY,
                            timeout=5
                        )
                        analysis = handler.get_analysis()
                        rec = analysis.summary["RECOMMENDATION"]
                        
                        # لو الإشارة شراء بأي درجة، ضيفه للجدول
                        if "BUY" in rec:
                            results.append({
                                "Ticker": symbol,
                                "Price": round(analysis.indicators["close"], 2),
                                "RSI": round(analysis.indicators["RSI"], 2),
                                "Signal": rec.replace("_", " ")
                            })
                        
                        # فاصل زمني "ميكرو" عشان السيرفر ميحسش بالهجوم
                        if i % 10 == 0:
                            time.sleep(0.1)
                            
                    except:
                        continue

            status_placeholder.empty()
            progress_bar.empty()

            if results:
                st.markdown(f"### <div class='status-indicator'></div> Identified Opportunities", unsafe_allow_html=True)
                df = pd.DataFrame(results)
                st.table(df.sort_values(by="Signal", ascending=False))
                
                # قسم الـ Strong Buy
                strong_buys = [item for item in results if "STRONG BUY" in item["Signal"]]
                if strong_buys:
                    st.divider()
                    st.markdown("### <div class='status-indicator'></div> Institutional Priority (Strong Buy)", unsafe_allow_html=True)
                    st.table(pd.DataFrame(strong_buys))
            else:
                st.info("Analysis Complete: No assets currently match the defined protocol.")

st.divider()
st.caption(f"WAHBA EGX | LIVE DATA STREAM | {time.strftime('%Y-%m-%d %H:%M:%S')} | © 2026")
