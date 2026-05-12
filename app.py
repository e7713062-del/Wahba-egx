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
# تأكد من وضع الـ API Key الخاص بك هنا
API_KEY = "YOUR_NEW_API_KEY" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_insight(symbol, recommendation, rsi, price):
    """
    وظيفة مخصصة لجلب تحليل AI مع معالجة الأخطاء
    """
    prompt = f"حلل سهم {symbol}: السعر الحالي {price}، التوصية {recommendation}، مؤشر RSI {rsi}. أعطني سطر واحد فقط فيه: (الرؤية الفنية - الهدف - وقف الخسارة)."
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
    except Exception:
        return None
    return None

# ==========================================
# 3. إعدادات الصفحة والتصميم (CSS)
# ==========================================
st.set_page_config(page_title="Wahba Intelligence - Full Scanner", layout="wide")

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
        padding: 40px;
        background: #000;
        border-bottom: 2px solid #d4af37;
        margin-bottom: 30px;
    }
    
    .logo-text {
        font-size: 40px;
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
        border-radius: 15px;
        padding: 30px;
        margin-bottom: 25px;
        border-top: 4px solid #d4af37;
        text-align: right;
    }
    
    .symbol-name {
        font-size: 32px;
        font-weight: 900;
        color: #d4af37;
    }
    
    .price-val {
        font-size: 26px;
        font-weight: bold;
        color: #ffffff;
        float: left;
    }
    
    .ai-insight-box {
        background: #111111;
        border-right: 5px solid #00ff00;
        padding: 18px;
        margin: 20px 0;
        font-size: 16px; 
        color: #00ff00;
        line-height: 1.8;
        border-radius: 8px;
    }

    .levels-grid {
        display: flex;
        justify-content: space-around;
        margin-top: 25px;
        background: #000000;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #222222;
        direction: ltr;
    }
    
    .num {
        font-size: 18px;
        font-weight: bold;
        color: #d4af37;
        font-family: 'Courier New', monospace;
    }

    .stButton>button {
        background: #d4af37 !important;
        color: #000000 !important;
        font-weight: 900 !important;
        border-radius: 12px !important;
        height: 70px !important;
        width: 100% !important;
        border: none !important;
        font-size: 24px !important;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3) !important;
    }
    </style>
    
    <div class="nav-bar">
        <div class="logo-text">WAHBA <span>INTELLIGENCE</span></div>
        <p style="color:#888888; font-size:14px; letter-spacing: 2px;">المسح الشامل والتحليل الاحترافي لجميع أسهم البورصة المصرية</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 4. دوال المسح والبيانات (Scanner Logic)
# ==========================================
def fetch_all_egx_symbols():
    """جلب قائمة الأسهم كاملة من TradingView"""
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {
            "filter": [{"left": "market_cap_basic", "operation": "nempty"}],
            "markets": ["egypt"],
            "columns": ["name"]
        }
        res = requests.post(url, json=payload, timeout=20).json()
        return [item['s'].split(':')[1] for item in res['data'] if ':' in item['s']]
    except Exception:
        # قائمة احتياطية في حال فشل السيرفر
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "ETEL", "AMOC"]

def run_full_scan():
    """تنفيذ المسح العميق الموزع على دقيقة كاملة"""
    symbols = fetch_all_egx_symbols()
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # حساب وقت الانتظار لضمان استغراق دقيقة كاملة (60 ثانية) لتجنب الحظر
    wait_time = 60 / len(symbols) if len(symbols) > 0 else 1
    
    for i, sym in enumerate(symbols):
        status_text.markdown(f"🔍 **فحص جاري:** {sym}... ({i+1} من {len(symbols)})")
        
        try:
            handler = TA_Handler(
                symbol=sym,
                screener="egypt",
                exchange="EGX",
                interval=Interval.INTERVAL_1_DAY,
                timeout=15
            )
            analysis = handler.get_analysis()
            ind = analysis.indicators
            rec = analysis.summary["RECOMMENDATION"]
            
            # حساب سكور وهبة (Mustafa's Proprietary Logic)
            score = 0
            if "STRONG_BUY" in rec: score += 5
            elif "BUY" in rec: score += 3
            
            rsi_val = ind.get("RSI")
            if rsi_val and 50 <= rsi_val <= 70: score += 3
            if ind.get("close") > ind.get("Pivot.M.Classic.Middle"): score += 2

            # استدعاء الـ AI للفرص الواعدة فقط
            ai_insight = ""
            if score >= 3:
                ai_insight = get_ai_insight(sym, rec, rsi_val, ind.get("close"))
                time.sleep(random.uniform(0.6, 1.2)) # حماية إضافية للـ API

            results.append({
                "symbol": sym,
                "price": ind.get("close"),
                "score": score,
                "rec": rec,
                "ai": ai_insight, 
                "s1": ind.get("Pivot.M.Classic.S1"), 
                "r1": ind.get("Pivot.M.Classic.R1")
            })
            
            # التوقف لضمان المسح الهادئ (دقيقة كاملة)
            time.sleep(wait_time)
            
        except Exception:
            continue
            
        progress_bar.progress((i + 1) / len(symbols))
    
    status_text.empty()
    return results

# ==========================================
# 5. منطقة التشغيل والعرض (UI)
# ==========================================
if st.button("بدء المسح العميق للبورصة المصرية (دقيقة كاملة)"):
    with st.spinner("جاري تحليل البيانات طوبة طوبة..."):
        scan_data = run_full_scan()
        
        if scan_data:
            # ترتيب النتائج حسب السكور (الأفضل أولاً)
            sorted_results = sorted(scan_data, key=lambda x: x['score'], reverse=True)
            
            for stock in sorted_results:
                if stock['score'] >= 1:
                    # بناء عرض السهم بتنسيق HTML سليم (حل مشكلة صورة 1000398575.jpg)
                    html_card = f"""
                    <div class="stock-card">
                        <div class="symbol-name">{stock['symbol']} <span class="price-val">{stock['price']:.2f} EGP</span></div>
                        <div style="color:#aaaaaa; margin-top:5px;">السكور الفني: {stock['score']} | التوصية: {stock['rec']}</div>
                        {f'<div class="ai-insight-box"><b>🎯 Wahba AI:</b> {stock["ai"]}</div>' if stock['ai'] else ''}
                        <div class="levels-grid">
                            <div>الدعم (S1): <span class="num">{stock['s1']:.2f}</span></div>
                            <div>المقاومة (R1): <span class="num">{stock['r1']:.2f}</span></div>
                        </div>
                    </div>
                    """
                    st.markdown(html_card, unsafe_allow_html=True)
        else:
            st.error("فشل في الوصول لمزود البيانات حالياً. يرجى الانتظار دقيقة والمحاولة مجدداً.")

st.markdown('<div style="text-align:center; padding:60px; color:#444444; font-size:12px;">WAHBA INTELLIGENCE © 2026 | تطوير مصطفى وهبة</div>', unsafe_allow_html=True)
