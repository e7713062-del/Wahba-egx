import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import google.generativeai as genai
import time
from datetime import datetime
import os

# ==========================================
# 1. إعدادات الـ AI (Gemini)
# ==========================================
API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_analysis(stock):
    """تحليل مركّز لنخبة النخبة فقط"""
    prompt = f"حلل سهم {stock['sym']} سعره الحالي {stock['price']}. الـ RSI هو {stock['rsi']}. اعطِ تحليل فني سريع (سطر واحد) يشمل نقطة دخول وهدف."
    try:
        time.sleep(1.5) # تهدئة الطلبات لضمان عدم التعليق
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return "جاري تحديث الرؤية الفنية..."

# ==========================================
# 2. نظام حفظ البيانات (Database)
# ==========================================
DB_FILE = "wahba_nokhba_exclusive.csv"

def save_to_db(data):
    df = pd.DataFrame(data)
    df['date'] = datetime.now().strftime("%Y-%m-%d")
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

def load_from_db():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        if not df.empty and str(df['date'].iloc[0]) == datetime.now().strftime("%Y-%m-%d"):
            return df.to_dict('records')
    return None

# ==========================================
# 3. الواجهة (Black & Gold Professional)
# ==========================================
st.set_page_config(page_title="Wahba AI | Nokhba Only", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Tajawal', sans-serif; direction: rtl;
        background-color: #000; color: #fff;
    }
    .card {
        background: #0a0a0a; border-radius: 15px; padding: 25px; margin-bottom: 20px;
        border-right: 8px solid #d4af37; border-left: 1px solid #1a1a1a;
    }
    .ai-insight {
        background: #0d1a0d; color: #00ff00; padding: 15px; border-radius: 10px;
        border: 1px solid #004400; margin-top: 15px; font-size: 16px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #d4af37, #b8860b) !important;
        color: #000 !important; font-weight: 900 !important; font-size: 24px !important;
        height: 70px !important; border-radius: 15px !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align:center; color:#d4af37;">WAHBA AI | تحليل النخبة فقط</h1>', unsafe_allow_html=True)

# ==========================================
# 4. محرك المسح (Scanning 283 Stocks)
# ==========================================
def fetch_symbols():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"markets": ["egypt"], "columns": ["name"]}, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data']]
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK"]

def run_nokhba_system():
    all_stocks = fetch_symbols()
    nokhba_candidates = []
    
    st.info(f"🚀 جاري فحص الـ {len(all_stocks)} سهم لتحديد نخبة النخبة...")
    p1 = st.progress(0)
    status = st.empty()
    
    # الخطوة 1: الفلترة الفنية (Strong Buy فقط)
    for i, sym in enumerate(all_stocks):
        status.write(f"🔍 فحص راداري: {sym}")
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=2)
            analysis = handler.get_analysis()
            if "STRONG_BUY" in analysis.summary["RECOMMENDATION"]:
                nokhba_candidates.append({
                    "sym": sym, "price": analysis.indicators["close"],
                    "rsi": analysis.indicators["RSI"], "s1": analysis.indicators["Pivot.M.Classic.S1"],
                    "r1": analysis.indicators["Pivot.M.Classic.R1"]
                })
        except: continue
        p1.progress((i + 1) / len(all_stocks))
    
    # الخطوة 2: تحليل الـ AI للحالات المختارة فقط
    if nokhba_candidates:
        st.success(f"🎯 تم العثور على {len(nokhba_candidates)} سهم نخبة. جاري تفعيل الـ AI لتحليلهم...")
        final_list = []
        p2 = st.progress(0)
        for i, s in enumerate(nokhba_candidates):
            status.write(f"🧠 AI يحلل النخبة: {s['sym']}")
            s['ai_insight'] = get_ai_analysis(s)
            final_list.append(s)
            p2.progress((i + 1) / len(nokhba_candidates))
            
        save_to_db(final_list)
        st.rerun()
    else:
        st.warning("السوق هادئ اليوم، لا توجد أسهم 'Strong Buy'.")

# ==========================================
# 5. العرض
# ==========================================
history = load_from_db()

if history:
    st.write(f"✅ نتائج نخبة الجلسة ({datetime.now().strftime('%Y-%m-%d')})")
    for s in history:
        st.markdown(f"""
        <div class="card">
            <div style="display:flex; justify-content:space-between;">
                <span style="font-size:30px; font-weight:900; color:#d4af37;">{s['sym']}</span>
                <span style="font-size:25px;">{float(s['price']):.2f} EGP</span>
            </div>
            <div class="ai-insight">
                <b>🤖 رؤية Wahba AI:</b><br>{s['ai_insight']}
            </div>
            <div style="color:#555; font-size:13px; margin-top:10px;">
                RSI: {float(s['rsi']):.1f} | دعم: {float(s['s1']):.2f} | مقاومة: {float(s['r1']):.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("🔄 تحديث المسح الشامل (283 سهم)"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.rerun()
else:
    if st.button("🚀 ابدأ استخراج وتحليل النخبة"):
        run_nokhba_system()
