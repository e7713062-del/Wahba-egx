import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import google.generativeai as genai
from datetime import datetime
import os

# ==========================================
# 1. إعدادات الـ AI والـ API
# ==========================================
API_KEY = "YOUR_API_KEY_HERE" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_hybrid_analysis(stock):
    """نظام هجين: يحاول مع الـ AI، وإذا فشل، يقوم بالمحاكاة برمجياً"""
    
    # 1. محاكاة التحليل برمجياً (الخطة ب)
    logic_analysis = f"نقطة الدخول: {stock['price']} EGP | "
    if stock['rsi'] > 70:
        logic_analysis += "الحالة: تشبع شرائي (احذر) | الهدف: {stock['r1']}"
    elif stock['rsi'] < 40:
        logic_analysis += "الحالة: تجميع | الهدف: {stock['sma20']}"
    else:
        logic_analysis += f"الحالة: عزم صاعد | الهدف: {stock['r1']}"
    logic_analysis += f" | الوقف: {stock['s1']}"

    # 2. محاولة جلب تحليل الـ AI
    prompt = f"بصفتك خبير وول ستريت، حلل سهم {stock['sym']} سعره {stock['price']} ورسيه {stock['rsi']:.1f} بإيجاز (دخول، هدف، وقف)."
    
    try:
        # تقليل وقت الانتظار لسرعة الاستجابة
        response = model.generate_content(prompt, generation_config={"max_output_tokens": 100})
        return response.text.strip()
    except:
        # لو الـ AI فشل (زي ما حصل في الصورة 1000398601.jpg)، نرجع التحليل البرمجي
        return f"🤖 [نظام محاكاة]: {logic_analysis}"

# ==========================================
# 2. واجهة الـ Terminal المتطورة
# ==========================================
st.set_page_config(page_title="Wahba AI Hybrid Scanner", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #000; color: #00ff41; font-family: 'Roboto Mono', monospace;
    }
    .stock-card {
        border: 1px solid #1a1a1a; padding: 15px; border-radius: 2px; margin-bottom: 10px;
        background: #050505; border-right: 4px solid #d4af37;
    }
    .ai-response { color: #fff; font-size: 14px; margin-top: 8px; border-top: 1px solid #111; padding-top: 8px; }
</style>
""", unsafe_allow_html=True)

st.title("📟 WAHBA HYBRID SCANNER")

# ==========================================
# 3. محرك المسح
# ==========================================
if st.button("RUN SYSTEM SCAN"):
    # (نفس كود جلب الأسهم السابق لضمان السرعة)
    url = "https://scanner.tradingview.com/egypt/scan"
    res = requests.post(url, json={"markets": ["egypt"], "columns": ["name"]}, timeout=10)
    tickers = [item['s'].split(':')[1] for item in res.json()['data']]
    
    qualified = []
    status = st.empty()
    
    for i, sym in enumerate(tickers[:100]): # فحص أول 100 سهم لسرعة التجربة
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=2)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            
            # فلتر وول ستريت
            if (ind.get("close") > ind.get("SMA20")) and (ind.get("RSI") > 50):
                qualified.append({
                    "sym": sym, "price": ind.get("close"), "rsi": ind.get("RSI"),
                    "s1": ind.get("Pivot.M.Classic.S1"), "r1": ind.get("Pivot.M.Classic.R1"),
                    "sma20": ind.get("SMA20")
                })
        except: continue

    if qualified:
        for s in qualified:
            # هنا السحر: الكود بينادي الـ Hybrid Analysis
            report = get_hybrid_analysis(s)
            st.markdown(f"""
            <div class="stock-card">
                <div style="display:flex; justify-content:space-between;">
                    <span style="color:#d4af37; font-weight:bold;">$ {s['sym']}</span>
                    <span>{s['price']:.2f} EGP</span>
                </div>
                <div class="ai-response">{report}</div>
            </div>
            """, unsafe_allow_html=True)
