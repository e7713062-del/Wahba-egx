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

def get_ai_final_verdict(stocks_list):
    """الـ AI يحلل القائمة النهائية كلها مرة واحدة ويعطي رأيه في 'نخبة النخبة'"""
    if not stocks_list: return "لا توجد فرص قوية حالياً."
    
    names = ", ".join([s['sym'] for s in stocks_list])
    prompt = f"بصفتك خبير في البورصة المصرية، هذه قائمة الأسهم الأقوى حالياً: {names}. أعطِ نصيحة استثمارية قصيرة جداً (سطرين) عن أفضلهم للتحرك القادم."
    
    try:
        time.sleep(1) # تأمين ضد الحظر
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return "تحليل الـ AI متاح عند استقرار الاتصال."

# ==========================================
# 2. إدارة البيانات (Cache System)
# ==========================================
DB_FILE = "wahba_pro_cache.csv"

def save_cache(data, ai_opinion):
    df = pd.DataFrame(data)
    df['ai_opinion'] = ai_opinion
    df['date'] = datetime.now().strftime("%Y-%m-%d")
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

def load_cache():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        if not df.empty and str(df['date'].iloc[0]) == datetime.now().strftime("%Y-%m-%d"):
            return df.to_dict('records'), df['ai_opinion'].iloc[0]
    return None, None

# ==========================================
# 3. الواجهة الاحترافية (Black & Gold)
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
        background: #0a0a0a; border-radius: 20px; padding: 25px; margin-bottom: 20px;
        border-right: 8px solid #d4af37; border-left: 1px solid #1a1a1a;
    }
    .ai-summary {
        background: linear-gradient(135deg, #0d1a0d 0%, #000 100%);
        color: #00ff00; padding: 25px; border-radius: 15px;
        border: 1px dashed #004400; margin-bottom: 30px; font-size: 20px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #d4af37, #b8860b) !important;
        color: #000 !important; font-weight: 900 !important; font-size: 24px !important;
        height: 70px !important; border-radius: 15px !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align:center; color:#d4af37;">WAHBA INTELLIGENCE | نخبة البورصة</h1>', unsafe_allow_html=True)

# ==========================================
# 4. محرك المسح (The 283 Engine)
# ==========================================
def get_all_symbols():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"markets": ["egypt"], "columns": ["name"]}, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data']]
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK"]

def run_wahba_core():
    symbols = get_all_symbols()
    nokhba = []
    
    st.info(f"🚀 جاري مسح كافة أسهم البورصة ({len(symbols)} سهم)...")
    progress = st.progress(0)
    status = st.empty()
    
    # الجزء الأول: المسح الفني الصامت والشامل
    for i, sym in enumerate(symbols):
        status.write(f"🔍 فحص راداري: {sym}")
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=2)
            analysis = handler.get_analysis()
            rec = analysis.summary["RECOMMENDATION"]
            
            # فلترة قاسية: نختار فقط الـ STRONG_BUY (نخبة النخبة)
            if "STRONG_BUY" in rec:
                ind = analysis.indicators
                nokhba.append({
                    "sym": sym, "price": ind.get("close"), "rsi": ind.get("RSI"),
                    "s1": ind.get("Pivot.M.Classic.S1"), "r1": ind.get("Pivot.M.Classic.R1")
                })
        except: continue
        progress.progress((i + 1) / len(symbols))

    # الجزء الثاني: رأي الـ AI في القائمة النهائية
    if nokhba:
        st.success(f"✅ تم العثور على {len(nokhba)} فرصة من ذهب.")
        with st.spinner("🧠 جاري استشارة Wahba AI في النتائج..."):
            ai_opinion = get_ai_final_verdict(nokhba)
            save_cache(nokhba, ai_opinion)
            st.rerun()
    else:
        st.warning("السوق حالياً في مرحلة تذبذب، لا توجد توصيات 'قوية جداً'.")

# ==========================================
# 5. منطق العرض والحفظ
# ==========================================
data, opinion = load_cache()

if data:
    st.markdown(f'<div class="ai-summary"><b>💡 رأي الذكاء الاصطناعي في جلسة اليوم:</b><br>{opinion}</div>', unsafe_allow_html=True)
    
    for s in data:
        st.markdown(f"""
        <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:35px; font-weight:900; color:#d4af37;">{s['sym']}</span>
                <span style="font-size:28px; font-family:monospace;">{float(s['price']):.2f} EGP</span>
            </div>
            <div style="color:#666; margin-top:10px;">RSI: {float(s['rsi']):.1f} | S1: {float(s['s1']):.2f} | R1: {float(s['r1']):.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 تحديث المسح (Scan All 283)"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.rerun()
else:
    if st.button("🚀 تفعيل المسح الشامل لنخبة النخبة"):
        run_wahba_core()

st.markdown('<div style="text-align:center; padding:50px; color:#333;">WAHBA PRO SYSTEM 2026</div>', unsafe_allow_html=True)
