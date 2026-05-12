import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import google.generativeai as genai
import time
import random
from datetime import datetime
import os
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# ==========================================
# 1. إعدادات الـ AI (Gemini) - الاستقرار الأقصى
# ==========================================
API_KEY = "YOUR_API_KEY_HERE" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_analysis_stable(stock):
    """تحليل شامل وعميق للنخبة المختارة"""
    prompt = f"""
    أنت خبير مالي ومحلل فني محترف. حلل سهم {stock['sym']} بناءً على البيانات التالية:
    - السعر الحالي: {stock['price']} EGP
    - مؤشر القوة النسبية (RSI): {stock['rsi']:.1f}
    - التوصية الفنية الحالية: {stock['rec']}
    - مستويات الدعم: {stock['s1']} | المقاومة: {stock['r1']}
    
    المطلوب: تقديم تقرير فني "كامل" يتضمن (نقطة الدخول المثالية، الأهداف القريبة والبعيدة، مستوى وقف الخسارة الصارم، ورؤيتك لاتجاه السهم).
    """
    for attempt in range(3):
        try:
            time.sleep(2) 
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            time.sleep(attempt * 2)
    return "⚠️ الـ AI يراجع البيانات حاليًا، يرجى المحاولة لاحقًا."

# ==========================================
# 2. محرك فك الحظر والاتصال (Wahba Shield)
# ==========================================
def create_safe_session():
    session = requests.Session()
    retry = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36"
]

def fetch_egx_symbols():
    url = "https://scanner.tradingview.com/egypt/scan"
    session = create_safe_session()
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    try:
        res = session.post(url, json={"markets": ["egypt"], "columns": ["name"]}, headers=headers, timeout=20)
        res.raise_for_status()
        return [item['s'].split(':')[1] for item in res.json()['data']]
    except Exception as e:
        st.error(f"⚠️ فشل جلب رموز الأسهم: {e}")
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK"]

# ==========================================
# 3. واجهة التصميم (Luxury Black & Gold)
# ==========================================
st.set_page_config(page_title="Wahba AI | Full Analysis", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Tajawal', sans-serif; direction: rtl;
        background-color: #000; color: #fff;
    }
    .card {
        background: #080808; border-radius: 15px; padding: 25px; margin-bottom: 25px;
        border-right: 10px solid #d4af37; border-top: 1px solid #1a1a1a;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
    }
    .ai-report-box {
        background: #0d1a0d; color: #00ff00; padding: 20px; border-radius: 12px;
        border: 1px solid #004400; margin-top: 20px; font-size: 18px; line-height: 1.7;
        white-space: pre-wrap;
    }
    .stButton>button {
        background: linear-gradient(90deg, #d4af37, #b8860b) !important;
        color: #000 !important; font-weight: 900 !important; font-size: 24px !important;
        height: 80px !important; border-radius: 20px !important; width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align:center; color:#d4af37;">WAHBA AI | التحليل الشامل للنخبة</h1>', unsafe_allow_html=True)

# ==========================================
# 4. منطق التشغيل (مرحلة الأداة ثم مرحلة الـ AI)
# ==========================================
CACHE_FILE = "wahba_full_analysis.csv"

def run_master_workflow():
    # --- المرحلة الأولى: عمل الأداة بالكامل ---
    all_symbols = fetch_egx_symbols()
    nokhba_candidates = []
    
    st.info(f"⏳ المرحلة 1: الأداة تقوم بمسح {len(all_symbols)} سهم لتحديد النخبة...")
    p1 = st.progress(0)
    status_msg = st.empty()
    
    for i, sym in enumerate(all_symbols):
        if i % 10 == 0: status_msg.write(f"🔬 فحص فني شامل: {sym}")
        try:
            if i % 15 == 0: time.sleep(random.uniform(0.5, 1.0))
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=5)
            analysis = handler.get_analysis()
            rec = analysis.summary["RECOMMENDATION"]
            ind = analysis.indicators
            rsi_val = ind.get("RSI")
            
            # فلترة "فوق المتوسطة" (Buy/Strong Buy + RSI > 50)
            if ("BUY" in rec) and (rsi_val is not None and rsi_val > 50):
                nokhba_candidates.append({
                    "sym": sym, "price": ind.get("close"), "rec": rec,
                    "rsi": rsi_val, "s1": ind.get("Pivot.M.Classic.S1"), "r1": ind.get("Pivot.M.Classic.R1")
                })
        except: continue
        p1.progress((i + 1) / len(all_symbols))

    # --- المرحلة الثانية: عمل الـ AI بالكامل ---
    if nokhba_candidates:
        st.success(f"🎯 اكتملت مهمة الأداة بنجاح! تم حصر {len(nokhba_candidates)} سهم. يبدأ الـ AI الآن التحليل الكامل...")
        final_list = []
        p2 = st.progress(0)
        
        for i, s in enumerate(nokhba_candidates):
            status_msg.write(f"🧠 AI يحلل بعمق الآن: {s['sym']}")
            # الـ AI يمسك السهم يفرتكه تحليل
            s['ai_full_report'] = get_ai_analysis_stable(s)
            final_list.append(s)
            p2.progress((i + 1) / len(nokhba_candidates))
            
        # حفظ كل شيء
        df = pd.DataFrame(final_list)
        df['scan_date'] = datetime.now().strftime("%Y-%m-%d")
        df.to_csv(CACHE_FILE, index=False, encoding='utf-8-sig')
        st.rerun()
    else:
        st.warning("لم يتم العثور على أسهم مطابقة للمواصفات حالياً.")

# ==========================================
# 5. عرض النتائج النهائية
# ==========================================
if os.path.exists(CACHE_FILE):
    df = pd.read_csv(CACHE_FILE)
    if not df.empty and str(df['scan_date'].iloc[0]) == datetime.now().strftime("%Y-%m-%d"):
        st.write(f"📅 نتائج رادار النخبة - جلسة: {datetime.now().strftime('%Y-%m-%d')}")
        for _, s in df.iterrows():
            st.markdown(f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 1px solid #222; padding-bottom:10px;">
                    <span style="font-size:38px; font-weight:900; color:#d4af37;">{s['sym']}</span>
                    <span style="font-size:30px; font-family:monospace;">{float(s['price']):.2f} EGP</span>
                </div>
                <div class="ai-report-box">
                    <strong>📄 تقرير خبير Wahba AI الكامل:</strong><br>
                    {s['ai_full_report']}
                </div>
                <div style="margin-top:15px; color:#888; display:flex; justify-content:space-between; font-size:14px;">
                    <span>المؤشر التقني: {s['rec']} | RSI: {float(s['rsi']):.1f}</span>
                    <span>دعم: {float(s['s1']):.2f} | مقاومة: {float(s['r1']):.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("🔄 بدء مسح شامل جديد للسوق"):
            os.remove(CACHE_FILE)
            st.rerun()
    else:
        if st.button("🚀 تفعيل الرادار والتحليل الكامل"): run_master_workflow()
else:
    if st.button("🚀 تفعيل الرادار والتحليل الكامل"): run_master_workflow()
