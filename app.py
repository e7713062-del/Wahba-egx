import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import google.generativeai as genai
import time
from datetime import datetime
import os

# ==========================================
# 1. إعدادات الذكاء الاصطناعي (Gemini)
# ==========================================
# استبدل YOUR_API_KEY_HERE بمفتاحك الخاص من Gemini
API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_insight(symbol, recommendation, rsi, price):
    """تحليل AI مركز للأسهم المختارة فقط"""
    prompt = f"حلل سهم {symbol}: سعر {price}، توصية {recommendation}، RSI {rsi}. سطر واحد فقط: هدف ووقف."
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
        return "تحليل AI قيد المراجعة"
    except Exception:
        return "عذراً، الـ AI مشغول حالياً"

# ==========================================
# 2. نظام حفظ البيانات (Wahba Database System)
# ==========================================
DB_FILE = "wahba_market_cache.csv"

def save_daily_data(data):
    """حفظ نتائج المسح في ملف CSV مع تاريخ اليوم"""
    df = pd.DataFrame(data)
    df['scan_date'] = datetime.now().strftime("%Y-%m-%d")
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

def load_stored_data():
    """تحميل البيانات المحفوظة إذا كانت مطابقة لتاريخ اليوم"""
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            today = datetime.now().strftime("%Y-%m-%d")
            if not df.empty and str(df['scan_date'].iloc[0]) == today:
                return df.to_dict('records')
        except:
            return None
    return None

# ==========================================
# 3. تصميم الواجهة الاحترافية (CSS)
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

    .stButton>button {
        background: linear-gradient(90deg, #d4af37, #b8860b) !important;
        color: #000 !important;
        font-weight: 900 !important;
        font-size: 28px !important;
        height: 80px !important;
        border-radius: 20px !important;
        border: none !important;
        box-shadow: 0 10px 25px rgba(212, 175, 55, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="nav-header"><div class="logo">WAHBA <span>INTELLIGENCE</span></div></div>', unsafe_allow_html=True)

# ==========================================
# 4. وظائف المسح والجلب (Core Engine)
# ==========================================
def get_egypt_symbols():
    """جلب كل رموز الأسهم المدرجة لضمان رؤية أي سهم جديد"""
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data']]
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "ETEL", "AMOC"]

def run_full_scan():
    symbols = get_egypt_symbols()
    candidates = []
    
    st.info("⚡ جاري المسح الشامل لكل الأسهم المدرجة (أول مرة اليوم)...")
    p1 = st.progress(0)
    s1 = st.empty()
    
    for i, sym in enumerate(symbols):
        s1.write(f"🔍 فحص فني: {sym}")
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=5)
            analysis = handler.get_analysis()
            rec = analysis.summary["RECOMMENDATION"]
            ind = analysis.indicators
            
            if "BUY" in rec:
                candidates.append({
                    "sym": sym, "price": ind.get("close"), "rec": rec,
                    "rsi": ind.get("RSI", 50), "s1": ind.get("Pivot.M.Classic.S1"), "r1": ind.get("Pivot.M.Classic.R1")
                })
        except: continue
        p1.progress((i + 1) / len(symbols))
        time.sleep(0.05)

    if candidates:
        st.subheader("🤖 تفعيل Wahba AI للتحليل...")
        p2 = st.progress(0)
        s2 = st.empty()
        final_list = []
        
        for i, stock in enumerate(candidates):
            s2.write(f"🧠 AI يحلل: {stock['sym']}")
            stock['ai'] = get_ai_insight(stock['sym'], stock['rec'], stock['rsi'], stock['price'])
            final_list.append(stock)
            p2.progress((i + 1) / len(candidates))
            time.sleep(1.2)
        
        save_daily_data(final_list)
        st.success("✅ تم حفظ نتائج اليوم بنجاح!")
        st.rerun()

# ==========================================
# 5. تشغيل البرنامج (المنطق النهائي)
# ==========================================
stored_results = load_stored_data()

if stored_results:
    st.success(f"📌 تم استعادة نتائج جلسة اليوم من الذاكرة ({datetime.now().strftime('%Y-%m-%d')})")
    for stock in stored_results:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">
                <span>{stock['sym']}</span>
                <span class="price">{float(stock['price']):.2f} EGP</span>
            </div>
            <div class="ai-box"><b>🎯 Wahba AI Insight:</b> {stock['ai']}</div>
            <div style="display:flex; justify-content:space-around; direction:ltr; color:#d4af37; background:#111; padding:15px; border-radius:10px;">
                <span>S1: {float(stock['s1']):.2f}</span> | <span>R1: {float(stock['r1']):.2f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("🔄 عمل Scan جديد الآن"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.rerun()
else:
    if st.button("🚀 بدء المسح الشامل للبورصة المصرية"):
        run_full_scan()

st.markdown('<div style="text-align:center; padding:100px; color:#444;">WAHBA INTELLIGENCE PRO © 2026 | تطوير مصطفى وهبة</div>', unsafe_allow_html=True)
