import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime
import pytz
import google.generativeai as genai

# --- 1. إعدادات الوقت (توقيت القاهرة) ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

# --- 2. إعداد الـ AI (بمفتاحك الجديد والشرط الصارم) ---
API_KEY = "AIzaSyBlT4KWYOj58RE-cfHE_YNpwR1cfHW1pY0"
genai.configure(api_key=API_KEY)
# استخدام gemini-1.5-flash لضمان استجابة سريعة جداً وتجنب الـ Timeout
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_insight(symbol, recommendation, rsi, price, s1, r1):
    """وظيفة الـ AI: تعيد النص فقط إذا نجحت، وإلا تعيد None لمنع عرض السهم"""
    prompt = f"""
    أنت محلل فني خبير في البورصة المصرية. حلل سهم {symbol}:
    - السعر الحالي: {price}
    - التوصية الفنية: {recommendation}
    - مؤشر RSI: {rsi}
    - الدعم الأول (S1): {s1}
    - المقاومة الأولى (R1): {r1}
    المطلوب رد احترافي في سطر واحد يتضمن: (رؤية السهم - هدف البيع الأول - نقطة وقف الخسارة).
    """
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
        return None
    except Exception:
        return None

st.set_page_config(page_title="Wahba Intelligence", layout="wide")

# --- 3. التصميم المؤسسي (كامل بدون حذف أي سطر CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #000000; color: #ffffff; }
    
    /* الهيدر */
    .nav-bar {
        text-align: center; padding: 30px; background: #000;
        border-bottom: 2px solid #d4af37; margin-bottom: 20px;
    }
    .logo-text { font-size: 35px; font-weight: 900; color: #fff; letter-spacing: 2px; }
    .logo-text span { color: #d4af37; }

    /* كروت الأسهم الذهبية */
    .stock-card {
        background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 15px;
        padding: 25px; margin-bottom: 20px; border-top: 3px solid #d4af37;
        text-align: right;
    }
    .symbol-name { font-size: 28px; font-weight: 900; color: #d4af37; }
    .price-val { font-size: 24px; font-weight: bold; color: #fff; float: left; }
    
    /* صندوق الـ AI */
    .ai-insight-box {
        background: #111; border-right: 4px solid #d4af37;
        padding: 15px; margin: 20px 0; font-size: 15px; 
        color: #e0e0e0; line-height: 1.6;
    }

    /* مستويات الدعم والمقاومة */
    .levels-grid {
        display: flex; justify-content: space-around; margin-top: 20px;
        background: #000; padding: 10px; border-radius: 8px; border: 1px solid #111;
        direction: ltr;
    }
    .level-item { text-align: center; }
    .label { font-size: 12px; color: #777; display: block; margin-bottom: 5px; }
    .num { font-size: 16px; font-weight: bold; color: #d4af37; font-family: monospace; }

    /* زر التشغيل */
    .stButton>button {
        background: #d4af37 !important; color: #000 !important;
        font-weight: 900 !important; border-radius: 10px !important;
        height: 60px !important; width: 100% !important; border: none !important;
        font-size: 20px !important;
    }
    
    /* التذييل */
    .footer-box {
        margin-top: 80px; padding: 40px; text-align: center;
        border-top: 1px solid #1a1a1a; color: #666; font-size: 14px;
    }
    </style>
    
    <div class="nav-bar">
        <div class="logo-text">WAHBA <span>INTELLIGENCE</span></div>
        <p style="color:#666; font-size:12px; letter-spacing: 3px;">المنصة الذكية لتحليل البورصة المصرية</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. محرك البيانات (Data Engine) ---

@st.cache_data(ttl=86400)
def fetch_egx_list(date_key):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except: 
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "ETEL", "AMOC"]

@st.cache_data(ttl=3600, show_spinner=False)
def run_strategic_scan(date_key):
    symbols = fetch_egx_list(date_key)
    results = []
    
    # فحص أكبر 15 سهم لضمان اقتناص الفرص وسرعة الرد
    active_symbols = symbols[:15] 
    
    p_bar = st.progress(0)
    for i, sym in enumerate(active_symbols):
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=10)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            rec = analysis.summary["RECOMMENDATION"]
            
            # حساب سكور وهبة (كامل)
            score = 0
            if "STRONG_BUY" in rec: score += 5
            elif "BUY" in rec: score += 3
            
            rsi_val = ind.get("RSI")
            if rsi_val and 50 <= rsi_val <= 70: score += 3
            # الربط بنقطة البيفوت المركزية
            if ind.get("close") > ind.get("Pivot.M.Classic.Middle"): score += 2

            # بيانات الدعم والمقاومة والسعر
            s1 = ind.get("Pivot.M.Classic.S1")
            r1 = ind.get("Pivot.M.Classic.R1")
            price = ind.get("close")

            # --- الشرط الصارم: استدعاء الـ AI أولاً ---
            ai_insight = get_ai_insight(sym, rec, rsi_val, price, s1, r1)

            # إذا نجح الـ AI فقط، يتم إضافة السهم للنتائج النهائية
            if ai_insight:
                results.append({
                    "symbol": sym, "price": price, "rec": rec, "rsi": rsi_val,
                    "score": score, "ai": ai_insight, "s1": s1, "r1": r1
                })
            p_bar.progress((i + 1) / len(active_symbols))
        except: continue
    return results

# --- 5. العرض النهائي (UI) ---
if st.button("تشغيل المسح الاستراتيجي"):
    with st.spinner("جاري صيد الفرص وتحليل الذكاء الاصطناعي..."):
        data = run_strategic_scan(today_key)
        
        if data:
            # ترتيب حسب الأعلى سكور (الأقوى فنياً)
            sorted_data = sorted(data, key=lambda x: x['score'], reverse=True)
            
            for stock in sorted_data:
                st.markdown(f"""
                    <div class="stock-card">
                        <div class="symbol-name">{stock['symbol']} <span class="price-val">{stock['price']:.2f} EGP</span></div>
                        <div style="color:#888;">التقييم: {stock['rec']} | سكور: {stock['score']} | RSI: {stock['rsi']:.1f}</div>
                        
                        <div class="ai-insight-box">
                            <b style="color:#d4af37;">🎯 استراتيجية وهبة AI:</b><br>
                            {stock['ai']}
                        </div>

                        <div class="levels-grid">
                            <div class="level-item"><span class="label">دعم (S1)</span><span class="num">{stock['s1']:.2f}</span></div>
                            <div class="level-item"><span class="label">مقاومة (R1)</span><span class="num">{stock['r1']:.2f}</span></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.error("⚠️ لم نتمكن من جلب ردود الـ AI حالياً. تأكد من ثبات الاتصال بالإنترنت وصلاحية مفتاح الـ API الخاص بك.")

st.markdown('<div class="footer-box">WAHBA INTELLIGENCE © 2026</div>', unsafe_allow_html=True)
