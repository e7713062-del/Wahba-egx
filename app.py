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
# استبدل بمفتاح الـ API الخاص بك
API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_insight(symbol, recommendation, rsi, price):
    """تحليل AI مع 'تهدئة' للطلبات لتجنب رسائل الخطأ"""
    prompt = f"حلل سهم {symbol}: سعر {price}، توصية {recommendation}، RSI {rsi}. سطر واحد فقط: هدف ووقف."
    try:
        # تأخير 1.5 ثانية عشان نتجنب الـ Rate Limit اللي ظهر في الصورة 1000398588.jpg
        time.sleep(1.5) 
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else "تحليل فني قيد التحديث"
    except Exception:
        return "الذكاء الاصطناعي يحتاج لراحة قصيرة.. جاري المحاولة"

# ==========================================
# 2. نظام التخزين المحلي (Wahba Database)
# ==========================================
DB_FILE = "wahba_market_data.csv"

def save_daily_data(data):
    """حفظ النتائج مع ختم تاريخ اليوم"""
    df = pd.DataFrame(data)
    df['scan_date'] = datetime.now().strftime("%Y-%m-%d")
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

def load_stored_data():
    """تحميل البيانات فقط لو كانت خاصة بجلسة اليوم"""
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
# 3. التصميم الخارجي (CSS) - الهوية البصرية
# ==========================================
st.set_page_config(page_title="Wahba Intelligence Pro", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Tajawal', sans-serif; direction: rtl;
        background-color: #000; color: #fff;
    }
    .card {
        background: #0a0a0a; border-radius: 20px; padding: 30px; margin-bottom: 30px;
        border-right: 10px solid #d4af37; box-shadow: 0 10px 40px rgba(0,0,0,0.6);
    }
    .card-header { display: flex; justify-content: space-between; align-items: center; }
    .symbol-name { font-size: 40px; font-weight: 900; color: #d4af37; }
    .price-tag { font-size: 30px; font-family: monospace; color: #fff; }
    .ai-box {
        background: #0d1a0d; color: #00ff00; padding: 20px; border-radius: 12px;
        margin: 20px 0; border: 1px solid #004400; font-size: 18px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #d4af37, #b8860b) !important;
        color: #000 !important; font-weight: 900 !important; font-size: 28px !important;
        height: 80px !important; width: 100% !important; border-radius: 20px !important;
        box-shadow: 0 10px 20px rgba(212, 175, 55, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align:center; color:#d4af37; font-size:50px;">WAHBA INTELLIGENCE PRO</h1>', unsafe_allow_html=True)

# ==========================================
# 4. محرك البحث والتحليل (Core Engine)
# ==========================================
def get_all_egx_symbols():
    """جلب قائمة كل الأسهم بلا استثناء من سيرفر البورصة"""
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"markets": ["egypt"], "columns": ["name"]}, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data']]
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "ETEL", "AMOC"]

def start_wahba_scan():
    all_symbols = get_all_egx_symbols()
    candidates = []
    
    # المرحلة الأولى: المسح الفني لكل السوق (سريع)
    st.subheader(f"🔍 المرحلة الأولى: مسح {len(all_symbols)} سهم بالبورصة المصرية...")
    fanni_progress = st.progress(0)
    status_text = st.empty()
    
    for i, sym in enumerate(all_symbols):
        status_text.write(f"يفحص فنياً: {sym}")
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
        fanni_progress.progress((i + 1) / len(all_symbols))

    # المرحلة الثانية: تحليل الـ AI للفرص القوية (أبطأ لتفادي التعليق)
    if candidates:
        st.subheader(f"🤖 المرحلة الثانية: تحليل {len(candidates)} فرصة بالذكاء الاصطناعي...")
        ai_progress = st.progress(0)
        final_results = []
        display_container = st.container()
        
        for i, stock in enumerate(candidates):
            status_text.write(f"ذكاء اصطناعي يحلل: {stock['sym']}")
            stock['ai'] = get_ai_insight(stock['sym'], stock['rec'], stock['rsi'], stock['price'])
            final_results.append(stock)
            
            with display_container:
                st.markdown(f"""
                <div class="card">
                    <div class="card-header">
                        <div class="symbol-name">{stock['sym']}</div>
                        <div class="price-tag">{stock['price']:.2f} EGP</div>
                    </div>
                    <div style="color:#888;">الحالة الفنية: {stock['rec']} | RSI: {stock['rsi']:.1f}</div>
                    <div class="ai-box"><b>🎯 Wahba AI Insight:</b> {stock['ai']}</div>
                    <div style="display:flex; justify-content:space-around; direction:ltr; background:#111; padding:15px; border-radius:10px; color:#d4af37;">
                        <span>S1: {stock['s1']:.2f}</span> | <span>R1: {stock['r1']:.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            ai_progress.progress((i + 1) / len(candidates))
        
        save_daily_data(final_results)
        status_text.success("✅ تم اكتمال المسح وحفظ البيانات للجلسة.")

# ==========================================
# 5. منطق التشغيل النهائي
# ==========================================
cached_data = load_stored_data()

if cached_data:
    st.info(f"📌 تم تحميل نتائج اليوم ({datetime.now().strftime('%Y-%m-%d')}) من قاعدة البيانات المحلية.")
    for s in cached_data:
        st.markdown(f"""
        <div class="card">
            <div class="card-header">
                <div class="symbol-name">{s['sym']}</div>
                <div class="price-tag">{float(s['price']):.2f} EGP</div>
            </div>
            <div class="ai-box"><b>🎯 Wahba AI Insight:</b> {s['ai']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("🔄 عمل مسح شامل جديد للبورصة"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.rerun()
else:
    if st.button("🚀 بدء نظام وهبة الذكي (تحليل كافة الأسهم)"):
        start_wahba_scan()

st.markdown('<br><div style="text-align:center; color:#444; border-top:1px solid #111; padding-top:20px;">WAHBA SYSTEM PRO © 2026 | تطوير مصطفى وهبة</div>', unsafe_allow_html=True)
