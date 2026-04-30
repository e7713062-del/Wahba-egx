import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import time

# 1. إعدادات المنصة المؤسسية
st.set_page_config(page_title="Wahba EGX | Institutional Terminal", layout="wide")

# 2. تصميم الواجهة الرسمي (بدون إيموجي)
st.markdown("""
    <style>
    .main-header { text-align: center; padding: 30px 0; border-bottom: 1px solid #333; margin-bottom: 40px; }
    .brand-name { font-family: 'Inter', sans-serif; font-size: 45px; font-weight: 800; color: var(--text-color); margin: 0; }
    .brand-tagline { font-size: 12px; letter-spacing: 5px; text-transform: uppercase; opacity: 0.6; margin-top: 10px; }
    .status-indicator { display: inline-block; width: 10px; height: 10px; background-color: #00ff00; border-radius: 50%; margin-right: 10px; box-shadow: 0 0 8px #00ff00; }
    .disclaimer-box {
        padding: 20px;
        background-color: rgba(255, 0, 0, 0.05);
        border-left: 5px solid #ff4b4b;
        margin-top: 50px;
        font-size: 13px;
        color: #888;
        line-height: 1.6;
    }
    </style>
    <div class="main-header">
        <h1 class="brand-name">WAHBA EGX</h1>
        <div class="brand-tagline">Institutional Market Terminal • High-Speed Engine</div>
    </div>
""", unsafe_allow_html=True)

# 3. دالة سحب كل الأسهم (تحديث تلقائي لأي سهم جديد)
@st.cache_data(ttl=1800)
def get_live_symbols():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter":[],"options":{"lang":"en"},"markets":["egypt"]}, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data']]
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EFIH"]

# 4. زر التشغيل والمسح
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button('EXECUTE SECURE MARKET SCAN', use_container_width=True):
        stocks = get_live_symbols()
        total = len(stocks)
        
        if total > 0:
            results = []
            progress_bar = st.progress(0)
            status_placeholder = st.empty()
            
            with st.spinner(f'Analyzing {total} securities...'):
                for i, symbol in enumerate(stocks):
                    try:
                        status_placeholder.markdown(f"🔍 **Scanning:** `{symbol}` ({i+1}/{total})")
                        progress_bar.progress((i + 1) / total)
                        
                        handler = TA_Handler(
                            symbol=symbol, screener="egypt", exchange="EGX",
                            interval=Interval.INTERVAL_1_DAY, timeout=5
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
                        
                        if i % 8 == 0: time.sleep(0.1) # فاصل لفك البلوك
                    except: continue

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
                st.info("Analysis Complete: No assets currently match the protocol.")

# 5. قسم إخلاء المسؤولية القانوني (Disclaimer)
st.markdown("""
    <div class="disclaimer-box">
        <strong>إخلاء مسؤولية قانوني:</strong><br>
        هذه الأداة مخصصة للأغراض المعلوماتية والتعليمية فقط، ولا تشكل دعوة للشراء أو البيع أو نصيحة استثمارية مباشرة. 
        سوق الأوراق المالية ينطوي على مخاطر عالية، والقرارات المالية تقع على عاتق المستثمر بالكامل. 
        البيانات يتم سحبها من مصادر خارجية (TradingView)، وقد يحدث تأخير بسيط في الأسعار أو الإشارات الفنية. 
        يُنصح دائماً باستشارة مستشار مالي معتمد قبل اتخاذ أي قرار استثماري.
    </div>
""", unsafe_allow_html=True)

st.divider()
st.caption(f"WAHBA EGX | INSTITUTIONAL VERSION | © 2026")
