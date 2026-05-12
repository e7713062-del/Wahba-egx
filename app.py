import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime
import pytz
import google.generativeai as genai  # طوبة الذكاء الاصطناعي[span_2](start_span)[span_2](end_span)[span_3](start_span)[span_3](end_span)

# --- 1. إعدادات الوقت (كما هي في كودك) ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

# --- طوبة إعداد Gemini (المحرك) ---[span_4](start_span)[span_4](end_span)[span_5](start_span)[span_5](end_span)
# ضع مفتاح الـ API الخاص بك هنا
GENAI_API_KEY = "ضـع_مفتاحك_هنا" 
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def get_ai_insight(symbol, recommendation, rsi, price, s1, r1):
    """وظيفة الـ AI لحساب الأهداف ووقف الخسارة"""
    prompt = f"""
    أنت محلل خبير. حلل سهم {symbol}: السعر {price}، التوصية {recommendation}، RSI {rsi}، دعم {s1}، مقاومة {r1}.
    المطلوب رد سطر واحد: (رؤية السهم - هدف أول - وقف خسارة).
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return "جاري تحليل الأهداف الفنية..."

st.set_page_config(page_title="Wahba Intelligence", layout="wide")

# --- 2. التصميم (CSS) - كما هو بدون أي حذف ---
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

    .section-header {
        color: #d4af37; border-right: 5px solid #d4af37;
        padding-right: 15px; margin: 40px 0 20px 0; font-size: 24px; font-weight: bold;
        text-align: right;
    }

    .stock-card {
        background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 15px;
        padding: 25px; margin-bottom: 20px; border-top: 3px solid #d4af37;
        text-align: right;
    }
    .symbol-name { font-size: 28px; font-weight: 900; color: #d4af37; }
    .price-val { font-size: 24px; font-weight: bold; color: #fff; }
    
    /* طوبة تصميم صندوق الـ AI */
    .ai-insight-box {
        background: #111; border-right: 4px solid #d4af37;
        padding: 15px; margin: 20px 0; font-size: 15px; 
        color: #e0e0e0; line-height: 1.6;
    }

    .levels-grid {
        display: flex; justify-content: space-around; margin-top: 20px;
        background: #000; padding: 10px; border-radius: 8px; border: 1px solid #111;
        direction: ltr;
    }
    .level-item { text-align: center; }
    .label { font-size: 12px; color: #777; display: block; margin-bottom: 5px; }
    .num { font-size: 16px; font-weight: bold; color: #d4af37; font-family: monospace; }

    .stButton>button {
        background: #d4af37 !important; color: #000 !important;
        font-weight: 900 !important; border-radius: 10px !important;
        height: 60px !important; width: 100% !important; border: none !important;
        font-size: 20px !important;
    }
    
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

# --- 3. محرك البيانات (Data Engine) - كما هو حرفياً ---
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
    
    # طوبة: فحص عدد معقول لضمان التحميل السريع مع الـ AI[span_6](start_span)[span_6](end_span)[span_7](start_span)[span_7](end_span)
    active_symbols = symbols[:20] 
    
    p_bar = st.progress(0)
    for i, sym in enumerate(active_symbols):
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=10)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            rec = analysis.summary["RECOMMENDATION"]
            
            # منطق السكور (كما هو في كودك)
            score = 0
            if "STRONG_BUY" in rec: score += 5
            elif "BUY" in rec: score += 3
            
            rsi_val = ind.get("RSI")
            if rsi_val and 50 <= rsi_val <= 70: score += 3
            
            if ind.get("close") > ind.get("Pivot.M.Classic.Middle"): score += 2

            # طوبة: جلب بيانات الـ AI[span_8](start_span)[span_8](end_span)[span_9](start_span)[span_9](end_span)
            s1 = ind.get("Pivot.M.Classic.S1")
            r1 = ind.get("Pivot.M.Classic.R1")
            price = ind.get("close")
            ai_insight = get_ai_insight(sym, rec, rsi_val, price, s1, r1)

            results.append({
                "symbol": sym, "price": price, "rec": rec, "rsi": rsi_val,
                "score": score, "ai": ai_insight, "s1": s1, "r1": r1
            })
            p_bar.progress((i + 1) / len(active_symbols))
        except: continue
    return results

# --- 4. عرض النتائج (UI) ---
if st.button("تشغيل المسح الاستراتيجي"):
    all_data = run_strategic_scan(today_key)
    sorted_data = sorted(all_data, key=lambda x: x['score'], reverse=True)
    
    for stock in sorted_data:
        # الكارت الذهبي (كما هو بدون حذف أي تفصيلة)
        st.markdown(f"""
            <div class="stock-card">
                <div class="symbol-name">{stock['symbol']} <span class="price-val">{stock['price']:.2f} EGP</span></div>
                <div style="color:#888;">التقييم: {stock['score']} | التوصية: {stock['rec']} | RSI: {stock['rsi']:.1f}</div>
                
                <div class="ai-insight-box">
                    <b style="color:#d4af37;">🎯 استراتيجية Wahba AI:</b><br>
                    {stock['ai']}
                </div>

                <div class="levels-grid">
                    <div class="level-item"><span class="label">دعم (S1)</span><span class="num">{stock['s1']:.2f}</span></div>
                    <div class="level-item"><span class="label">مقاومة (R1)</span><span class="num">{stock['r1']:.2f}</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="footer-box">WAHBA INTELLIGENCE © 2026</div>', unsafe_allow_html=True)
