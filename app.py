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
# استبدل بمفتاح الـ API الخاص بك
API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_detailed_ai_analysis(stock):
    """تحليل احترافي مفصل لكل سهم من نخبة النخبة"""
    prompt = f"""
    أنت خبير مالي في البورصة المصرية. حلل سهم {stock['sym']} تحليل كامل بناءً على المعطيات التالية:
    - السعر الحالي: {stock['price']} EGP
    - مؤشر RSI: {stock['rsi']}
    - التوصية الفنية: {stock['rec']}
    - مستويات الدعم (S1): {stock['s1']}
    - مستويات المقاومة (R1): {stock['r1']}
    
    المطلوب: تقرير من سطرين يوضح (أفضل سعر دخول، الأهداف القادمة، ووقف الخسارة) بلهجة احترافية.
    """
    try:
        # تأخير 2 ثانية لضمان أقصى استقرار للـ API وتجنب أخطاء الاتصال
        time.sleep(2) 
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return "⚠️ حدث خطأ أثناء التحليل التفصيلي، يرجى المحاولة مرة أخرى."

# ==========================================
# 2. نظام حفظ البيانات (Wahba DB)
# ==========================================
DB_FILE = "wahba_ultra_nokhba.csv"

def save_to_wahba_db(data):
    df = pd.DataFrame(data)
    df['scan_date'] = datetime.now().strftime("%Y-%m-%d")
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

def load_wahba_db():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            if not df.empty and str(df['scan_date'].iloc[0]) == datetime.now().strftime("%Y-%m-%d"):
                return df.to_dict('records')
        except: return None
    return None

# ==========================================
# 3. الواجهة الاحترافية (Design)
# ==========================================
st.set_page_config(page_title="Wahba AI Ultra", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Tajawal', sans-serif; direction: rtl;
        background-color: #000; color: #fff;
    }
    .card {
        background: #080808; border-radius: 20px; padding: 30px; margin-bottom: 25px;
        border-right: 12px solid #d4af37; border-top: 1px solid #222;
        box-shadow: 0 15px 35px rgba(0,0,0,0.8);
    }
    .ai-report {
        background: #0d1a0d; color: #00ff00; padding: 20px; border-radius: 12px;
        border: 1px solid #004400; margin-top: 20px; line-height: 1.6; font-size: 18px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #d4af37, #b8860b) !important;
        color: #000 !important; font-weight: 900 !important; font-size: 26px !important;
        height: 75px !important; border-radius: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align:center; color:#d4af37; font-size:45px;">WAHBA AI | تحليل النخبة الشامل</h1>', unsafe_allow_html=True)

# ==========================================
# 4. محرك المسح الاستراتيجي
# ==========================================
def get_all_egx():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"markets": ["egypt"], "columns": ["name"]}, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data']]
    except: return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK"]

def start_ultra_scan():
    all_symbols = get_all_egx()
    nokhba = []
    
    st.info(f"🚀 جاري فحص الـ {len(all_symbols)} سهم لتحديد الأقوى...")
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # المرحلة 1: تصفية الـ 283 سهم (بحثاً عن الـ Strong Buy والـ Buy القوي)
    for i, sym in enumerate(all_symbols):
        status_text.write(f"🔍 فحص تقني: {sym}")
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=2)
            analysis = handler.get_analysis()
            rec = analysis.summary["RECOMMENDATION"]
            
            if "BUY" in rec: # بياخد الـ Buy والـ Strong Buy عشان ميفوتش فرص
                ind = analysis.indicators
                nokhba.append({
                    "sym": sym, "price": ind.get("close"), "rec": rec,
                    "rsi": ind.get("RSI"), "s1": ind.get("Pivot.M.Classic.S1"), "r1": ind.get("Pivot.M.Classic.R1")
                })
        except: continue
        progress_bar.progress((i + 1) / len(all_symbols))

    # المرحلة 2: تحليل الـ AI التفصيلي للنخبة
    if nokhba:
        st.success(f"🎯 تم اختيار {len(nokhba)} سهم. جاري كتابة التقارير بواسطة Wahba AI...")
        final_results = []
        p2 = st.progress(0)
        
        for i, stock in enumerate(nokhba):
            status_text.write(f"🧠 AI يحلل بعمق: {stock['sym']}")
            stock['ai_report'] = get_detailed_ai_analysis(stock)
            final_results.append(stock)
            p2.progress((i + 1) / len(nokhba))
            
        save_to_wahba_db(final_results)
        st.rerun()
    else:
        st.error("السوق هادئ جداً، لا توجد فرص شراء واضحة حالياً.")

# ==========================================
# 5. عرض النتائج النهائية
# ==========================================
results = load_wahba_db()

if results:
    for s in results:
        st.markdown(f"""
        <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:35px; font-weight:900; color:#d4af37;">{s['sym']}</span>
                <span style="font-size:28px; font-family:monospace;">{float(s['price']):.2f} EGP</span>
            </div>
            <div style="color:#888; margin-top:5px;">الحالة: {s['rec']} | RSI: {float(s['rsi']):.1f}</div>
            <div class="ai-report">
                <b>📝 تقرير خبير Wahba AI:</b><br>{s['ai_report']}
            </div>
            <div style="display:flex; justify-content:space-around; margin-top:15px; color:#d4af37; font-weight:bold;">
                <span>الدعم: {float(s['s1']):.2f}</span>
                <span>المقاومة: {float(s['r1']):.2f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("🔄 عمل مسح شامل جديد للسوق"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.rerun()
else:
    if st.button("🚀 تفعيل رادار النخبة والتحليل الشامل"):
        start_ultra_scan()
