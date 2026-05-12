import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import google.generativeai as genai
import time
import random
from datetime import datetime
import os

# ==========================================
# 1. إعدادات الـ AI (Gemini)
# ==========================================
API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ultra_ai_analysis(stock):
    """تحليل عميق وشامل لنخبة النخبة فقط"""
    prompt = f"""
    أنت كبير محللي البورصة المصرية. حلل سهم {stock['sym']} بناءً على:
    - السعر: {stock['price']} EGP
    - مؤشر RSI: {stock['rsi']}
    - الدعم الأساسي: {stock['s1']}
    - المقاومة القادمة: {stock['r1']}
    
    المطلوب تقرير فني احترافي في سطرين يحدد: (أفضل منطقة شراء، الهدف الأول، ومستوى حماية الأرباح).
    """
    try:
        time.sleep(2) # تأمين لمنع ضغط الطلبات
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return "⚠️ الرؤية الفنية جاري تحديثها حالياً..."

# ==========================================
# 2. نظام التمويه وفك البلوك (Anti-Block)
# ==========================================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

def get_egx_symbols_safe():
    url = "https://scanner.tradingview.com/egypt/scan"
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    try:
        res = requests.post(url, json={"markets": ["egypt"], "columns": ["name"]}, headers=headers, timeout=15)
        if res.status_code == 200:
            return [item['s'].split(':')[1] for item in res.json()['data']]
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "ORAS", "ESRS"]
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO"]

# ==========================================
# 3. واجهة Wahba Intelligence (Black & Gold)
# ==========================================
st.set_page_config(page_title="Wahba Ultra AI", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Tajawal', sans-serif; direction: rtl;
        background-color: #000; color: #fff;
    }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #d4af37 , #8a6d3b); }
    .card {
        background: #080808; border-radius: 15px; padding: 25px; margin-bottom: 20px;
        border-right: 10px solid #d4af37; border-top: 1px solid #1a1a1a;
    }
    .ai-box {
        background: #0d1a0d; color: #00ff00; padding: 15px; border-radius: 10px;
        border: 1px solid #004400; margin-top: 15px; font-size: 18px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #d4af37, #b8860b) !important;
        color: #000 !important; font-weight: 900 !important; font-size: 24px !important;
        height: 75px !important; border-radius: 15px !important; width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align:center; color:#d4af37;">WAHBA AI | محلل النخبة الشامل</h1>', unsafe_allow_html=True)

# ==========================================
# 4. محرك المسح الاستراتيجي (Anti-Detection)
# ==========================================
def run_wahba_ultra_scan():
    symbols = get_egx_symbols_safe()
    nokhba_candidates = []
    
    st.info(f"🚀 جاري فحص الـ {len(symbols)} سهم بنظام التمويه...")
    p_bar = st.progress(0)
    status = st.empty()
    
    for i, sym in enumerate(symbols):
        status.write(f"🔬 رادار Wahba يفحص: {sym}")
        try:
            # إضافة تأخير عشوائي بسيط كل 15 سهم لفك البلوك
            if i % 15 == 0: time.sleep(random.uniform(1, 2))
            
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=5)
            analysis = handler.get_analysis()
            rec = analysis.summary["RECOMMENDATION"]
            
            # فلترة مرنة: نخبة النخبة (Strong Buy) والفرص القوية (Buy)
            if "BUY" in rec:
                ind = analysis.indicators
                nokhba_candidates.append({
                    "sym": sym, "price": ind.get("close"), "rec": rec,
                    "rsi": ind.get("RSI"), "s1": ind.get("Pivot.M.Classic.S1"), "r1": ind.get("Pivot.M.Classic.R1")
                })
        except: continue
        p_bar.progress((i + 1) / len(symbols))

    if nokhba_candidates:
        st.success(f"🎯 تم العثور على {len(nokhba_candidates)} فرصة. جاري التحليل التفصيلي بالـ AI...")
        final_list = []
        p2 = st.progress(0)
        for i, s in enumerate(nokhba_candidates):
            status.write(f"🧠 AI يحلل بعمق: {s['sym']}")
            s['ai_report'] = get_ultra_ai_analysis(s)
            final_list.append(s)
            p2.progress((i + 1) / len(nokhba_candidates))
            
        # حفظ النتائج
        df = pd.DataFrame(final_list)
        df['date'] = datetime.now().strftime("%Y-%m-%d")
        df.to_csv("wahba_ultra_data.csv", index=False, encoding='utf-8-sig')
        st.rerun()
    else:
        st.warning("السوق في حالة ترقب، لا توجد فرص نخبة حالياً.")

# ==========================================
# 5. عرض النتائج النهائية
# ==========================================
if os.path.exists("wahba_ultra_data.csv"):
    res_df = pd.read_csv("wahba_ultra_data.csv")
    if not res_df.empty and str(res_df['date'].iloc[0]) == datetime.now().strftime("%Y-%m-%d"):
        st.write(f"📅 جلسة اليوم: {datetime.now().strftime('%Y-%m-%d')}")
        for _, s in res_df.iterrows():
            rec_color = "#00ff00" if "STRONG" in s['rec'] else "#d4af37"
            st.markdown(f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:35px; font-weight:900; color:#d4af37;">{s['sym']}</span>
                    <span style="color:{rec_color}; font-weight:bold;">{s['rec']}</span>
                    <span style="font-size:28px;">{float(s['price']):.2f} EGP</span>
                </div>
                <div class="ai-box">
                    <b>🤖 تقرير Wahba AI المفصل:</b><br>{s['ai_report']}
                </div>
                <div style="color:#666; font-size:14px; margin-top:10px; display:flex; justify-content:space-between;">
                    <span>RSI: {float(s['rsi']):.1f}</span>
                    <span>الدعم: {float(s['s1']):.2f} | المقاومة: {float(s['r1']):.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("🔄 تحديث المسح الشامل (283 سهم)"):
            os.remove("wahba_ultra_data.csv")
            st.rerun()
    else:
        if st.button("🚀 ابدأ استخراج وتحليل النخبة"):
            run_wahba_ultra_scan()
else:
    if st.button("🚀 ابدأ استخراج وتحليل النخبة"):
        run_wahba_ultra_scan()
