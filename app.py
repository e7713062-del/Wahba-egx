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
# 1. إعدادات الـ AI والـ API
# ==========================================
API_KEY = "YOUR_API_KEY_HERE" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_daily_report(stock):
    """تحليل استراتيجي للإغلاق اليومي"""
    prompt = f"""
    بناءً على إغلاق اليوم لسهم {stock['sym']}:
    السعر: {stock['price']} EGP | RSI: {stock['rsi']:.1f}
    المتوسط المتحرك 20: {stock['sma20']:.2f}
    الطلب: حلل الشمعة اليومية وحدد هل السهم للشراء مع بداية جلسة الغد؟ 
    حدد (نقطة الدخول، الهدف الأول، وقف الخسارة الصارم).
    """
    try:
        time.sleep(2) # حماية الـ API من الحظر
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return "⚠️ التحليل الفني اليدوي مطلوب لهذا السهم."

# ==========================================
# 2. الواجهة الاحترافية (Black & Gold)
# ==========================================
st.set_page_config(page_title="Wahba EGX Daily Scanner", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Tajawal', sans-serif; direction: rtl;
        background-color: #000; color: #fff;
    }
    .main-header { color: #d4af37; text-align: center; font-weight: 900; font-size: 40px; margin-bottom: 20px; }
    .status-box { background: #111; border: 1px solid #d4af37; padding: 15px; border-radius: 10px; margin-bottom: 20px; text-align: center; }
    .card { background: #080808; border: 1px solid #222; padding: 25px; border-radius: 15px; border-right: 10px solid #d4af37; margin-bottom: 30px; }
    .ai-insight { background: #001a00; color: #00ff00; padding: 15px; border-radius: 10px; border: 1px solid #004400; margin-top: 20px; font-size: 18px; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">WAHBA EGX | سكانر الإغلاق اليومي</div>', unsafe_allow_html=True)

# ==========================================
# 3. محرك المسح (Daily Close Engine)
# ==========================================
def fetch_symbols():
    url = "https://scanner.tradingview.com/egypt/scan"
    try:
        res = requests.post(url, json={"markets": ["egypt"], "columns": ["name"]}, timeout=15)
        return [item['s'].split(':')[1] for item in res.json()['data']]
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "ESRS"]

CACHE_FILE = "daily_close_results.csv"

if st.button("🔍 تشغيل سكانر الإغلاق (Daily Close Scan)"):
    all_syms = fetch_symbols()
    nokhba = []
    
    status_area = st.empty()
    progress_bar = st.progress(0)
    
    # فحص الـ 283 سهم بناءً على شمعة اليوم المنتهية
    for i, sym in enumerate(all_syms):
        status_area.markdown(f"🔬 جاري تحليل إغلاق سهم: **{sym}**")
        try:
            handler = TA_Handler(
                symbol=sym,
                screener="egypt",
                exchange="EGX",
                interval=Interval.INTERVAL_1_DAY, # إغلاق يومي
                timeout=5
            )
            analysis = handler.get_analysis()
            ind = analysis.indicators
            rec = analysis.summary["RECOMMENDATION"]
            
            # فلترة "النخبة فوق المتوسطة":
            # 1. إشارة شراء واضحة عند الإغلاق
            # 2. RSI فوق 50 (عزم قوي)
            # 3. السعر فوق متوسط 20 يوم (تريند صاعد)
            if ("BUY" in rec) and (ind.get("RSI") > 52) and (ind.get("close") > ind.get("SMA20")):
                nokhba.append({
                    "sym": sym,
                    "price": ind.get("close"),
                    "rsi": ind.get("RSI"),
                    "sma20": ind.get("SMA20"),
                    "rec": rec,
                    "s1": ind.get("Pivot.M.Classic.S1"),
                    "r1": ind.get("Pivot.M.Classic.R1")
                })
        except: continue
        progress_bar.progress((i + 1) / len(all_syms))

    if nokhba:
        st.success(f"🎯 تم العثور على {len(nokhba)} سهم بإغلاق إيجابي جداً. جاري تحليل الـ AI...")
        final_list = []
        for s in nokhba:
            status_area.markdown(f"🧠 AI يضع استراتيجية الغد لسهم: **{s['sym']}**")
            s['ai_report'] = get_ai_daily_report(s)
            final_list.append(s)
            
        df = pd.DataFrame(final_list)
        df['scan_date'] = datetime.now().strftime("%Y-%m-%d")
        df.to_csv(CACHE_FILE, index=False, encoding='utf-8-sig')
        st.rerun()
    else:
        st.warning("السوق أغلق اليوم بدون فرص واضحة تحقق شروطنا الصارمة.")

# ==========================================
# 4. عرض التقرير اليومي
# ==========================================
if os.path.exists(CACHE_FILE):
    df = pd.read_csv(CACHE_FILE)
    if not df.empty and str(df['scan_date'].iloc[0]) == datetime.now().strftime("%Y-%m-%d"):
        st.markdown(f'<div class="status-box">📅 تقرير جاهزية التداول ليوم: {datetime.now().strftime("%d-%m-%Y")}</div>', unsafe_allow_html=True)
        
        for _, s in df.iterrows():
            st.markdown(f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:35px; font-weight:900; color:#d4af37;">{s['sym']}</span>
                    <span style="font-size:25px;">الإغلاق: {float(s['price']):.2f} EGP</span>
                </div>
                <div class="ai-insight">
                    <b>🤖 خطة تداول Wahba AI (لجلسة الغد):</b><br>{s['ai_report']}
                </div>
                <div style="margin-top:15px; color:#777; font-size:14px; display:flex; justify-content:space-between;">
                    <span>قوة العزم (RSI): {float(s['rsi']):.1f}</span>
                    <span>متوسط 20 يوم: {float(s['sma20']):.2f}</span>
                    <span>أهم دعم: {float(s['s1']):.2f} | أهم مقاومة: {float(s['r1']):.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
