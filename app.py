import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime
import pytz
import google.generativeai as genai
import time
import random

# ==========================================
# 1. الإعدادات والذكاء الاصطناعي (Gemini)
# ==========================================
# ضع مفتاح الـ API الخاص بك هنا
API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_insight(symbol, recommendation, rsi, price):
    """تحليل AI مع حماية كاملة من توقف البرنامج"""
    prompt = f"حلل سهم {symbol}: سعر {price}، توصية {recommendation}، RSI {rsi}. سطر واحد فقط: هدف ووقف."
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
        return "تحليل فني قيد التحديث"
    except Exception:
        return "جاري محاولة التحليل مرة أخرى..."

# ==========================================
# 2. تصميم الواجهة بالكامل (CSS) - طوبة طوبة
# ==========================================
st.set_page_config(page_title="Wahba Intelligence Pro", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        background-color: #000000 !important;
        color: #ffffff;
    }
    
    .nav-header {
        text-align: center;
        padding: 40px;
        border-bottom: 2px solid #d4af37;
        margin-bottom: 40px;
    }
    
    .logo { font-size: 45px; font-weight: 900; color: #fff; }
    .logo span { color: #d4af37; }

    .card {
        background: #0a0a0a;
        border: 1px solid #1a1a1a;
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 30px;
        border-right: 8px solid #d4af37;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    .card-title {
        display: flex;
        justify-content: space-between;
        font-size: 35px;
        font-weight: 900;
        color: #d4af37;
        margin-bottom: 15px;
    }
    
    .price { color: #ffffff; font-family: monospace; font-size: 30px; }
    
    .ai-box {
        background: #0d1a0d;
        color: #00ff00;
        padding: 20px;
        border-radius: 12px;
        margin: 20px 0;
        font-size: 18px;
        border: 1px solid #004400;
        line-height: 1.6;
    }
    
    .levels {
        display: flex;
        justify-content: space-around;
        background: #111;
        padding: 15px;
        border-radius: 10px;
        direction: ltr;
        font-family: monospace;
        color: #d4af37;
        font-size: 20px;
    }

    .stButton>button {
        background: linear-gradient(90deg, #d4af37, #b8860b) !important;
        color: #000 !important;
        font-weight: 900 !important;
        font-size: 28px !important;
        height: 80px !important;
        border-radius: 20px !important;
        border: none !important;
        box-shadow: 0 10px 25px rgba(212, 175, 55, 0.4) !important;
        transition: 0.4s;
    }
    .stButton>button:hover {
        transform: translateY(-5px);
        background: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="nav-header"><div class="logo">WAHBA <span>INTELLIGENCE</span></div></div>', unsafe_allow_html=True)

# ==========================================
# 3. محرك المسح المستمر (The Non-Stop Engine)
# ==========================================
# تهيئة الذاكرة لحفظ الأسهم المكتشفة
if 'found_stocks' not in st.session_state:
    st.session_state.found_stocks = []

def get_symbols():
    """جلب كل رموز الأسهم المصرية"""
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data']]
    except Exception:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "ETEL", "AMOC"]

def run_scan():
    """تنفيذ المسح وحفظ النتائج في الذاكرة"""
    symbols = get_symbols()
    st.session_state.found_stocks = [] # تصفير القائمة لبدء مسح جديد
    
    progress_bar = st.progress(0)
    status_msg = st.empty()
    results_area = st.container() # حاوية العرض الحي
    
    for i, sym in enumerate(symbols):
        status_msg.markdown(f"📡 **جاري فحص السوق المصري:** {sym} ({i+1}/{len(symbols)})")
        
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=10)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            rec = analysis.summary["RECOMMENDATION"]
            
            # سكور وهبة (مصمم لعام 2026)
            score = 0
            if "BUY" in rec: score += 5
            rsi = ind.get("RSI", 50)
            if 45 <= rsi <= 65: score += 3
            if ind.get("close") > ind.get("Pivot.M.Classic.Middle"): score += 2
            
            # لو السهم عليه فرصة قوية (سكور 5 فأعلى)
            if score >= 5:
                ai_text = get_ai_insight(sym, rec, rsi, ind.get("close"))
                
                stock_data = {
                    "sym": sym, "price": ind.get("close"), "score": score,
                    "rec": rec, "ai": ai_text, 
                    "s1": ind.get("Pivot.M.Classic.S1"), "r1": ind.get("Pivot.M.Classic.R1")
                }
                st.session_state.found_stocks.append(stock_data)
                
                # عرض فوري داخل الحاوية
                with results_area:
                    st.markdown(f"""
                    <div class="card">
                        <div class="card-title">
                            <span>{sym}</span>
                            <span class="price">{ind.get("close"):.2f} EGP</span>
                        </div>
                        <div style="color: #888; font-size: 20px;">سكور: {score} | التوصية: {rec}</div>
                        <div class="ai-box"><b>🎯 رؤية وهبة AI:</b> {ai_text}</div>
                        <div class="levels">
                            <span>S1 (دعم): {ind.get("Pivot.M.Classic.S1"):.2f}</span>
                            <span>R1 (مقاومة): {ind.get("Pivot.M.Classic.R1"):.2f}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                time.sleep(1.2) # انتظار هادئ لمنع الحظر
            else:
                time.sleep(0.4)
                
        except Exception:
            continue
            
        progress_bar.progress((i + 1) / len(symbols))
    
    status_msg.success("✅ تم الانتهاء من المسح الشامل 10/10!")

# ==========================================
# 4. منطقة التشغيل والعرض الدائم
# ==========================================
if st.button("تفعيل المسح الشامل (10/10) - ابدأ الآن"):
    run_scan()

# ضمان بقاء النتائج حتى لو المسح خلص أو الصفحة عملت ريفريش
if st.session_state.found_stocks and not st.empty():
    st.write("---")
    st.info(f"تم العثور على {len(st.session_state.found_stocks)} فرص قوية في السوق المصري.")

st.markdown('<div style="text-align:center; padding:100px; color:#444; font-size:14px; border-top:1px solid #111;">WAHBA INTELLIGENCE SYSTEM © 2026 | تطوير مصطفى وهبة</div>', unsafe_allow_html=True)
