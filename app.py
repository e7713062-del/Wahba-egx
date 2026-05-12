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
# 1. إعدادات المنطقة الزمنية والوقت
# ==========================================
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)

# ==========================================
# 2. إعدادات الذكاء الاصطناعي (Gemini)
# ==========================================
# استبدل YOUR_API_KEY بمفتاحك الحقيقي
API_KEY = "YOUR_API_KEY_HERE" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_insight(symbol, recommendation, rsi, price):
    """
    وظيفة مخصصة للتواصل مع Gemini AI لتحليل السهم تقنياً
    """
    prompt = f"حلل سهم {symbol}: السعر {price}، التوصية {recommendation}، RSI {rsi}. أعطني سطر واحد فقط فيه: (الرؤية الفنية - الهدف - وقف الخسارة)."
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
        else:
            return None
    except Exception:
        return None

# ==========================================
# 3. إعدادات واجهة المستخدم (التصميم الكامل)
# ==========================================
st.set_page_config(page_title="Wahba Intelligence - Pro Scanner", layout="wide")

# تصميم CSS كامل بدون أي اختصار
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
        padding: 45px;
        background: #000;
        border-bottom: 2px solid #d4af37;
        margin-bottom: 35px;
    }
    
    .logo-text {
        font-size: 45px;
        font-weight: 900;
        color: #ffffff;
        letter-spacing: 4px;
        margin: 0;
    }
    
    .logo-text span {
        color: #d4af37;
    }

    .status-sub {
        color: #666666;
        font-size: 14px;
        letter-spacing: 2px;
        margin-top: 10px;
    }

    .stock-card {
        background: #0a0a0a;
        border: 1px solid #1a1a1a;
        border-radius: 15px;
        padding: 30px;
        margin-bottom: 25px;
        border-top: 5px solid #d4af37;
        text-align: right;
        transition: 0.3s;
    }
    
    .stock-card:hover {
        border-top: 5px solid #ffffff;
        background: #0f0f0f;
    }
    
    .symbol-name {
        font-size: 35px;
        font-weight: 900;
        color: #d4af37;
    }
    
    .price-val {
        font-size: 28px;
        font-weight: bold;
        color: #ffffff;
        float: left;
    }
    
    .ai-insight-box {
        background: #0d1a0d;
        border-right: 6px solid #00ff00;
        padding: 20px;
        margin: 20px 0;
        font-size: 17px; 
        color: #00ff00;
        line-height: 1.8;
        border-radius: 10px;
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
        font-size: 20px;
        font-weight: bold;
        color: #d4af37;
        font-family: 'Courier New', monospace;
    }

    .stButton>button {
        background: #d4af37 !important;
        color: #000000 !important;
        font-weight: 900 !important;
        border-radius: 15px !important;
        height: 80px !important;
        width: 100% !important;
        border: none !important;
        font-size: 28px !important;
        box-shadow: 0 6px 20px rgba(212, 175, 55, 0.4) !important;
        cursor: pointer;
    }
    </style>
    
    <div class="nav-bar">
        <div class="logo-text">WAHBA <span>INTELLIGENCE</span></div>
        <div class="status-sub">وضع المسح العميق | تحليل كامل للسوق المصري (60 ثانية)</div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 4. محرك المسح (The Scanning Engine)
# ==========================================
def fetch_all_egx_symbols():
    """
    سحب قائمة الأسهم أوتوماتيكياً لضمان شمولية المسح
    """
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {
            "filter": [{"left": "market_cap_basic", "operation": "nempty"}],
            "markets": ["egypt"],
            "columns": ["name"]
        }
        res = requests.post(url, json=payload, timeout=25).json()
        return [item['s'].split(':')[1] for item in res['data'] if ':' in item['s']]
    except Exception:
        # قائمة الطوارئ إذا فشل السيرفر في الرد
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "ETEL", "AMOC"]

def run_deep_scan_60s():
    """
    تنفيذ المسح وتوزيع الوقت لضمان استغراق دقيقة كاملة لمنع الحظر
    """
    symbols = fetch_all_egx_symbols()
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # توزيع الـ 60 ثانية بدقة على عدد الأسهم
    total_duration = 60 
    sleep_interval = total_duration / len(symbols) if len(symbols) > 0 else 1
    
    for i, sym in enumerate(symbols):
        status_text.markdown(f"📉 **جاري تحليل السهم:** {sym}... ({i+1} / {len(symbols)})")
        
        try:
            # إعداد محلل TradingView
            handler = TA_Handler(
                symbol=sym,
                screener="egypt",
                exchange="EGX",
                interval=Interval.INTERVAL_1_DAY,
                timeout=15
            )
            analysis = handler.get_analysis()
            indicators = analysis.indicators
            summary_rec = analysis.summary["RECOMMENDATION"]
            
            # منطق سكور وهبة (Score Calculation)
            score = 0
            if "STRONG_BUY" in summary_rec: 
                score += 5
            elif "BUY" in summary_rec: 
                score += 3
            
            rsi = indicators.get("RSI")
            if rsi and 45 <= rsi <= 65: 
                score += 3
                
            close_price = indicators.get("close")
            pivot_middle = indicators.get("Pivot.M.Classic.Middle")
            if close_price and pivot_middle and close_price > pivot_middle:
                score += 2

            # جلب رؤية الذكاء الاصطناعي للفرص المتميزة
            ai_commentary = ""
            if score >= 4:
                ai_commentary = get_ai_insight(sym, summary_rec, rsi, close_price)
                # فاص حماية للـ API
                time.sleep(1)

            # تجميع البيانات
            results.append({
                "symbol": sym,
                "price": close_price,
                "score": score,
                "rec": summary_rec,
                "ai": ai_commentary, 
                "s1": indicators.get("Pivot.M.Classic.S1"), 
                "r1": indicators.get("Pivot.M.Classic.R1")
            })
            
            # الالتزام بجدول الـ 60 ثانية
            time.sleep(sleep_interval)
            
        except Exception:
            continue
            
        progress_bar.progress((i + 1) / len(symbols))
    
    status_text.empty()
    return results

# ==========================================
# 5. منطقة التحكم والعرض (UI Logic)
# ==========================================
if st.button("تفعيل المسح العميق (60 ثانية)"):
    with st.spinner("جاري بناء التقرير طوبة طوبة..."):
        all_data = run_deep_scan_60s()
        
        if all_data:
            # ترتيب النتائج من الأقوى للأضعف
            final_list = sorted(all_data, key=lambda x: x['score'], reverse=True)
            
            for stock in final_list:
                if stock['score'] >= 1:
                    # بناء الكارت بصيغة HTML كاملة
                    card_markup = f"""
                    <div class="stock-card">
                        <div class="symbol-name">{stock['symbol']} <span class="price-val">{stock['price']:.2f} EGP</span></div>
                        <div style="color:#888888; margin-top:10px;">سكور وهبة: {stock['score']} | التوصية الفنية: {stock['rec']}</div>
                        {f'<div class="ai-insight-box"><b>🎯 Wahba AI:</b> {stock["ai"]}</div>' if stock['ai'] else ''}
                        <div class="levels-grid">
                            <div>الدعم (S1): <span class="num">{stock['s1']:.2f}</span></div>
                            <div>المقاومة (R1): <span class="num">{stock['r1']:.2f}</span></div>
                        </div>
                    </div>
                    """
                    st.markdown(card_markup, unsafe_allow_html=True)
        else:
            st.error("فشل في استلام البيانات. يرجى مراجعة الاتصال أو الـ API Key.")

# تذييل الصفحة
st.markdown("""
    <div style="text-align:center; padding:80px; color:#333333; font-size:13px; border-top:1px solid #111; margin-top:50px;">
        WAHBA INTELLIGENCE SYSTEM © 2026<br>تم التطوير بواسطة مصطفى وهبة - جميع الحقوق محفوظة
    </div>
""", unsafe_allow_html=True)
