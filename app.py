import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime
import pytz
import google.generativeai as genai
import time

# --- 1. إعدادات الوقت (توقيت القاهرة) ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

# --- 2. إعداد الـ AI (Gemini) ---
# تأكد من وضع المفتاح الجديد هنا
API_KEY = "ضع_مفتاحك_هنا" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_insight(symbol, recommendation, rsi, price, s1, r1):
    """وظيفة الـ AI مع إدارة ذكية لتجنب الحظر"""
    prompt = f"""
    أنت محلل فني خبير في البورصة المصرية. حلل سهم {symbol}:
    السعر {price}، التوصية {recommendation}، RSI {rsi}.
    أعطني سطر واحد فقط فيه: (الرؤية الفنية - الهدف القريب - وقف الخسارة).
    """
    for attempt in range(2):
        try:
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception:
            time.sleep(1)
            continue
    return None

st.set_page_config(page_title="Wahba Intelligence - Full Scanner", layout="wide")

# --- 3. التصميم الكامل (CSS) - النسخة الاحترافية ---
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
        background: #111; border-right: 4px solid #d4af37;
        padding: 15px; margin: 20px 0; font-size: 15px; 
        color: #00ff00; line-height: 1.6;
    }

    .levels-grid {
        display: flex; justify-content: space-around; margin-top: 20px;
        background: #000; padding: 10px; border-radius: 8px; border: 1px solid #111;
        direction: ltr;
    }
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
        <p style="color:#666; font-size:12px; letter-spacing: 3px;">المسح الشامل والتحليل الذكي لجميع أسهم EGX</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. محرك المسح (Full Market Scanner) ---
def fetch_all_egx_symbols():
    """سحب كافة الأسهم المدرجة في مصر أوتوماتيكياً"""
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {
            "filter": [{"left": "market_cap_basic", "operation": "nempty"}],
            "markets": ["egypt"],
            "columns": ["name"]
        }
        res = requests.post(url, json=payload, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data'] if ':' in item['s']]
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK"]

def run_full_scan():
    """تحليل كل سهم وحساب السكور الفني"""
    symbols = fetch_all_egx_symbols()
    results = []
    p_bar = st.progress(0)
    
    for i, sym in enumerate(symbols):
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=10)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            rec = analysis.summary["RECOMMENDATION"]
            
            # --- سكور وهبة (Mustafa's Score) ---
            score = 0
            if "STRONG_BUY" in rec: score += 5
            elif "BUY" in rec: score += 3
            
            rsi_val = ind.get("RSI")
            if rsi_val and 50 <= rsi_val <= 70: score += 3
            if ind.get("close") > ind.get("Pivot.M.Classic.Middle"): score += 2

            # تشغيل الـ AI فقط للأسهم ذات السكور العالي
            ai_text = ""
            if score >= 3:
                ai_text = get_ai_insight(sym, rec, rsi_val, ind.get("close"), ind.get("Pivot.M.Classic.S1"), ind.get("Pivot.get('Pivot.M.Classic.R1')"))
                time.sleep(0.5)

            results.append({
                "symbol": sym, "price": ind.get("close"), "score": score,
                "rec": rec, "ai": ai_text, "s1": ind.get("Pivot.M.Classic.S1"), "r1": ind.get("Pivot.M.Classic.R1")
            })
        except:
            continue
        p_bar.progress((i + 1) / len(symbols))
    return results

# --- 5. التشغيل والعرض ---
if st.button("بدء المسح الشامل للبورصة المصرية"):
    with st.spinner("جاري صيد الفرص في كامل السوق..."):
        data = run_full_scan()
        if data:
            # الترتيب حسب السكور الأعلى
            for stock in sorted(data, key=lambda x: x['score'], reverse=True):
                if stock['score'] >= 1:
                    # حل مشكلة الصورة 1000398575.jpg بتنسيق HTML سليم
                    card_html = f"""
                    <div class="stock-card">
                        <div class="symbol-name">{stock['symbol']} <span class="price-val">{stock['price']:.2f} EGP</span></div>
                        <div style="color:#888;">السكور: {stock['score']} | الحالة: {stock['rec']}</div>
                        {f'<div class="ai-insight-box"><b>🎯 Wahba AI:</b> {stock["ai"]}</div>' if stock['ai'] else ''}
                        <div class="levels-grid">
                            <div>S1: <span class="num">{stock['s1']:.2f}</span></div>
                            <div>R1: <span class="num">{stock['r1']:.2f}</span></div>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.error("فشل في جلب البيانات، تأكد من المفتاح الجديد.")

st.markdown('<div class="footer-box">WAHBA INTELLIGENCE © 2026</div>', unsafe_allow_html=True)
