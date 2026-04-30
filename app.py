import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import time

# 1. الإعدادات
st.set_page_config(page_title="Wahba EGX | Terminal", layout="wide")

# 2. الواجهة
st.markdown("""
    <style>
    .main-header { text-align: center; padding: 20px; }
    .brand-name { font-family: 'Inter', sans-serif; font-size: 50px; font-weight: 900; color: var(--text-color); text-transform: uppercase; }
    </style>
    <div class="main-header">
        <h1 class="brand-name">Wahba EGX</h1>
        <p>OFFICIAL LIVE AUTO-SCANNER | EGYPT STOCK EXCHANGE</p>
    </div>
""", unsafe_allow_html=True)

# 3. دالة جلب الرموز مع معالجة الخطأ (عشان متوقفش)
def get_live_symbols():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter":[],"options":{"lang":"en"},"markets":["egypt"]}, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data']]
    except:
        # لو السيرفر معلق، بنرجع أهم أسهم البورصة عشان الأداة متوقفش خالص
        return ["COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "PHDC", "HRHO", "ESRS", "BTEL", "ORWE", "AMOC"]

def check_logic(symbol):
    try:
        # ضفنا تأخير بسيط (0.1 ثانية) بين كل سهم والثاني عشان السيرفر ميعملش Block
        time.sleep(0.1) 
        handler = TA_Handler(
            symbol=symbol, screener="egypt", exchange="EGX",
            interval=Interval.INTERVAL_1_DAY, timeout=10
        )
        analysis = handler.get_analysis()
        rec = analysis.summary["RECOMMENDATION"]
        ind = analysis.indicators
        
        # لو السهم واخد أي نوع من أنواع الشراء يظهر فوراً
        if "BUY" in rec:
            return {
                "Ticker": symbol,
                "Price": round(ind["close"], 2),
                "RSI": round(ind["RSI"], 2),
                "Signal": rec.replace("_", " ")
            }
    except: return None

# 4. زر التشغيل مع شريط تقدم (Progress Bar)
if st.button('START FULL MARKET AUTO-SCAN'):
    all_stocks = get_live_symbols()
    total = len(all_stocks)
    
    # هنا هتأكد إنها "بتحمل" قدام عينك
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = []
    with st.spinner(f'Checking {total} Live Securities...'):
        # قللنا الـ workers لـ 15 عشان نكون أهدى على السيرفر وميعلقش
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(check_logic, s) for s in all_stocks]
            for i, future in enumerate(futures):
                res = future.result()
                if res: results.append(res)
                # تحديث شريط التحميل
                progress_bar.progress((i + 1) / total)
                status_text.text(f"Processing: {all_stocks[i]} ({i+1}/{total})")

        if results:
            st.success(f"Identification Complete: {len(results)} Bullish Assets Found")
            df = pd.DataFrame(results)
            st.table(df.sort_values(by="Signal", ascending=False))
            
            # قسم الـ STRONG BUY
            strong_buys = [item for item in results if "STRONG BUY" in item["Signal"]]
            if strong_buys:
                st.markdown("---")
                st.markdown("### 🔥 Top Priority: STRONG BUY Opportunities")
                st.table(pd.DataFrame(strong_buys))
        else:
            st.warning("No assets currently match. Market might be in a correction phase.")

st.divider()
st.caption("WAHBA EGX | AUTO-SCANNER SYSTEM | © 2026")
