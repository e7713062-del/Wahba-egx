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
# 1. إعدادات الوقت والمنطقة الزمنية
# ==========================================
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)

# ==========================================
# 2. إعدادات الذكاء الاصطناعي (Gemini)
# ==========================================
# ضع مفتاح الـ API الخاص بك هنا
API_KEY = "YOUR_API_KEY_HERE" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_insight(symbol, recommendation, rsi, price):
    """
    تحليل السهم بواسطة الذكاء الاصطناعي مع معالجة الأخطاء
    """
    prompt = f"حلل سهم {symbol}: السعر {price}، التوصية {recommendation}، RSI {rsi}. أعطني سطر واحد: (الرؤية - الهدف - الوقف)."
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
    except Exception:
        return None
    return None

# ==========================================
# 3. واجهة المستخدم والتصميم (Full CSS)
# ==========================================
st.set_page_config(page_title="Wahba Intelligence - Deep Scan 10/10", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    
    * {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
    }
    
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    .nav-bar {
        text-align: center;
        padding: 50px;
        background: #000;
        border-bottom: 2px solid #d4af37;
        margin-bottom: 40px;
    }
    
    .logo-text {
        font-size: 45px;
        font-weight: 900;
        color: #ffffff;
        letter-spacing: 3px;
    }
    
    .logo-text span {
        color: #d4af37;
    }

    .stock-card {
        background: #0a0a0a;
        border: 1px solid #1a1a1a;
        border-radius: 20px;
        padding: 35px;
        margin-bottom: 30px;
        border-top: 5px solid #d4af37;
        text-align: right;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    .symbol-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }

    .symbol-name {
        font-size: 38px;
        font-weight: 900;
        color: #d4af37;
    }
    
    .price-val {
        font-size: 30px;
        font-weight: bold;
        color: #ffffff;
    }
    
    .ai-box {
        background: #0a1f0a;
        border-right: 6px solid #00ff00;
        padding: 20px;
        margin: 25px 0;
        font-size: 18px; 
        color: #00ff00;
        line-height: 1.8;
        border-radius: 12px;
    }

    .levels-container {
        display: flex;
        justify-content: space-around;
        margin-top: 30px;
        background: #000000;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #222222;
        direction: ltr;
    }
    
    .num-label { color: #888; font-size: 14px; }
    .num-val { font-size: 22px; font-weight: bold; color: #d4af37; font-family: 'Courier New', monospace; }

    .stButton>button {
        background: #d4af37 !important;
        color: #000000 !important;
        font-weight: 900 !important;
        border-radius: 15px !important;
        height: 80px !important;
        width: 100% !important;
        border: none !important;
        font-size: 28px !important;
        box-shadow: 0 10px 25px rgba(212, 175, 55, 0.4) !important;
        transition: 0.4s;
    }
    .stButton>button:hover {
        background: #ffffff !important;
        transform: translateY(-5px);
    }
    </style>
    
    <div class="nav-bar">
        <div class="logo-text">WAHBA <span>INTELLIGENCE</span></div>
        <p style="color:#666; font-size:16px; margin-top:10px;">نظام المسح العميق والمطوّر - تحليل 10 على 10</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 4. محرك المسح العميق (Deep Scan Engine)
# ==========================================
def fetch_egx_symbols():
    """جلب كل رموز الأسهم من البورصة المصرية"""
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=30).json()
        return [item['s'].split(':')[1] for item in res['data']]
    except Exception:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "ETEL", "AMOC"]

def run_full_deep_scan():
    """تنفيذ المسح ببطء شديد ودقة (براحتك خالص)"""
    symbols = fetch_egx_symbols()
    results = []
    
    p_bar = st.progress(0)
    status = st.empty()
    
    for i, sym in enumerate(symbols):
        status.markdown(f"🔬 **جاري التحليل المتأني:** {sym}... ({i+1}/{len(symbols)})")
        
        try:
            handler = TA_Handler(
                symbol=sym, 
                screener="egypt", 
                exchange="EGX", 
                interval=Interval.INTERVAL_1_DAY, 
                timeout=20
            )
            analysis = handler.get_analysis()
            ind = analysis.indicators
            rec = analysis.summary["RECOMMENDATION"]
            
            # حساب سكور وهبة (Logic 10/10)
            score = 0
            if "STRONG_BUY" in rec: score += 5
            elif "BUY" in rec: score += 3
            
            rsi_val = ind.get("RSI")
            if rsi_val and 45 <= rsi_val <= 65: score += 3
            if ind.get("close") > ind.get("Pivot.M.Classic.Middle"): score += 2

            # استدعاء AI للفرص القوية فقط
            ai_txt = ""
            if score >= 3:
                ai_txt = get_ai_insight(sym, rec, rsi_val, ind.get("close"))
                # وقت إضافي للذكاء الاصطناعي لتجنب الحظر
                time.sleep(random.uniform(1.5, 2.5))

            results.append({
                "symbol": sym, "price": ind.get("close"), "score": score,
                "rec": rec, "ai": ai_txt, 
                "s1": ind.get("Pivot.M.Classic.S1"), "r1": ind.get("Pivot.M.Classic.R1")
            })
            
            # أهم فاص زمني عشان السيرفر يشتغل "براحته"
            time.sleep(1.5)
            
        except Exception:
            continue
            
        p_bar.progress((i + 1) / len(symbols))
    
    status.empty()
    return results

# ==========================================
# 5. منطقة التشغيل والعرض
# ==========================================
if st.button("بدء المسح العميق (شغل 10 على 10 وبراحتك)"):
    with st.spinner("جاري فحص كامل السوق المصري بعناية..."):
        all_stocks = run_full_deep_scan()
        
        if all_stocks:
            # ترتيب النتائج من الأعلى سكور للأقل
            sorted_stocks = sorted(all_stocks, key=lambda x: x['score'], reverse=True)
            
            for s in sorted_stocks:
                if s['score'] >= 1:
                    st.markdown(f"""
                    <div class="stock-card">
                        <div class="symbol-header">
                            <span class="symbol-name">{s['symbol']}</span>
                            <span class="price-val">{s['price']:.2f} EGP</span>
                        </div>
                        <div style="color:#888; font-size:18px;">الحالة: {s['rec']} | سكور وهبة: {s['score']}</div>
                        
                        {f'<div class="ai-box"><b>🎯 رؤية وهبة AI:</b> {s["ai"]}</div>' if s['ai'] else ''}
                        
                        <div class="levels-container">
                            <div style="text-align:center;">
                                <div class="num-label">دعم (S1)</div>
                                <div class="num-val">{s['s1']:.2f}</div>
                            </div>
                            <div style="text-align:center;">
                                <div class="num-label">مقاومة (R1)</div>
                                <div class="num-val">{s['r1']:.2f}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("السيرفر مشغول حالياً، يرجى المحاولة بعد قليل.")

st.markdown('<div style="text-align:center; padding:100px; color:#444; font-size:14px; border-top:1px solid #111;">WAHBA INTELLIGENCE © 2026 | تطوير مصطفى وهبة</div>', unsafe_allow_html=True)
