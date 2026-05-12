import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime
import pytz
import google.generativeai as genai
import time
import random

# --- 1. إعدادات الوقت (توقيت القاهرة) ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)

# --- 2. إعداد الـ AI (Gemini) ---
# حط مفتاحك هنا يا بطل
API_KEY = "YOUR_NEW_API_KEY" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_insight(symbol, recommendation, rsi, price):
    """تحليل AI مع نظام محاولات هادئ لتجنب الحظر"""
    prompt = f"حلل سهم {symbol}: سعر {price}، توصية {recommendation}، RSI {rsi}. سطر واحد: هدف ووقف."
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
    except:
        return None
    return None

st.set_page_config(page_title="Wahba Intelligence - Full Scanner", layout="wide")

# --- 3. التصميم الكامل (CSS) - لا يوجد حرف محذوف ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #000000; color: #ffffff; }
    
    .nav-bar {
        text-align: center; padding: 30px; background: #000;
        border-bottom: 2px solid #d4af37; margin-bottom: 20px;
    }
    .logo-text { font-size: 35px; font-weight: 900; color: #fff; letter-spacing: 2px; }
    .logo-text span { color: #d4af37; }

    .stock-card {
        background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 15px;
        padding: 25px; margin-bottom: 20px; border-top: 3px solid #d4af37;
        text-align: right;
    }
    .symbol-name { font-size: 28px; font-weight: 900; color: #d4af37; }
    .price-val { font-size: 24px; font-weight: bold; color: #fff; float: left; }
    
    .ai-insight-box {
        background: #111; border-right: 4px solid #00ff00;
        padding: 15px; margin: 20px 0; font-size: 15px; 
        color: #00ff00; line-height: 1.6; border-radius: 5px;
    }

    .levels-grid {
        display: flex; justify-content: space-around; margin-top: 20px;
        background: #000; padding: 12px; border-radius: 10px; border: 1px solid #222;
        direction: ltr;
    }
    .num { font-size: 16px; font-weight: bold; color: #d4af37; font-family: monospace; }

    .stButton>button {
        background: #d4af37 !important; color: #000 !important;
        font-weight: 900 !important; border-radius: 10px !important;
        height: 60px !important; width: 100% !important; border: none !important;
        font-size: 20px !important;
    }
    </style>
    
    <div class="nav-bar">
        <div class="logo-text">WAHBA <span>INTELLIGENCE</span></div>
        <p style="color:#666; font-size:12px; letter-spacing: 3px;">المسح الشامل والتحليل الذكي لجميع أسهم EGX</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. محرك البحث (Dynamic Scanner) ---
def fetch_all_egx_symbols():
    """جلب كل رموز الأسهم المدرجة في مصر أوتوماتيكياً"""
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {
            "filter": [{"left": "market_cap_basic", "operation": "nempty"}],
            "markets": ["egypt"],
            "columns": ["name"]
        }
        res = requests.post(url, json=payload, timeout=20).json()
        return [item['s'].split(':')[1] for item in res['data'] if ':' in item['s']]
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "ETEL", "AMOC"]

def run_market_scan():
    """تحليل السوق بالكامل طوبة طوبة"""
    symbols = fetch_all_egx_symbols()
    results = []
    p_bar = st.progress(0)
    status_msg = st.empty()
    
    for i, sym in enumerate(symbols):
        status_msg.text(f"جاري فحص: {sym} ({i+1}/{len(symbols)})")
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=10)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            rec = analysis.summary["RECOMMENDATION"]
            
            # --- سكور وهبة ---
            score = 0
            if "STRONG_BUY" in rec: score += 5
            elif "BUY" in rec: score += 3
            
            rsi_val = ind.get("RSI")
            if rsi_val and 50 <= rsi_val <= 70: score += 3
            if ind.get("close") > ind.get("Pivot.M.Classic.Middle"): score += 2

            # AI للفرص القوية فقط لتجنب الحظر
            ai_text = ""
            if score >= 3:
                ai_text = get_ai_insight(sym, rec, rsi_val, ind.get("close"))
                time.sleep(random.uniform(0.4, 0.7)) 

            results.append({
                "symbol": sym, "price": ind.get("close"), "score": score,
                "rec": rec, "ai": ai_text, 
                "s1": ind.get("Pivot.M.Classic.S1"), 
                "r1": ind.get("Pivot.M.Classic.R1")
            })
            
            # حماية السيرفر من الحظر (الرد على صورة 1000398580.jpg)
            if i % 8 == 0: time.sleep(1)
            
        except:
            continue
            
        p_bar.progress((i + 1) / len(symbols))
    
    status_msg.empty()
    return results

# --- 5. العرض النهائي ---
if st.button("بدء المسح الشامل والآمن للبورصة"):
    data = run_market_scan()
    if data:
        # ترتيب حسب السكور
        sorted_data = sorted(data, key=lambda x: x['score'], reverse=True)
        
        for stock in sorted_data:
            if stock['score'] >= 1:
                # حل مشكلة الـ HTML (الرد على صورة 1000398575.jpg)
                card_html = f"""
                <div class="stock-card">
                    <div class="symbol-name">{stock['symbol']} <span class="price-val">{stock['price']:.2f} EGP</span></div>
                    <div style="color:#888;">السكور الفني: {stock['score']} | الحالة: {stock['rec']}</div>
                    {f'<div class="ai-insight-box"><b>🎯 Wahba AI:</b> {stock["ai"]}</div>' if stock['ai'] else ''}
                    <div class="levels-grid">
                        <div>S1: <span class="num">{stock['s1']:.2f}</span></div>
                        <div>R1: <span class="num">{stock['r1']:.2f}</span></div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.error("السيرفر رفض الطلب حالياً، جرب كمان دقيقة.")

st.markdown('<div style="text-align:center; padding:50px; color:#444;">WAHBA INTELLIGENCE © 2026</div>', unsafe_allow_html=True)
