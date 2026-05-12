import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import google.generativeai as genai
import time
from datetime import datetime

# ==========================================
# 1. إعدادات الـ AI (Gemini 1.5 Flash)
# ==========================================
API_KEY = "YOUR_API_KEY_HERE" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_precise_targets(stock):
    """توليد أهداف دقيقة بناءً على مستويات الدعم والمقاومة والـ AI"""
    # حساب أهداف تقنية أولية بناءً على مستويات الـ Pivot
    t1 = stock['r1']
    t2 = stock['r1'] + (stock['r1'] - stock['s1']) * 0.5
    
    prompt = f"""
    بصفتك محلل صناديق استثمار، حلل سهم {stock['sym']} بناءً على:
    - السعر الحالي: {stock['price']} EGP
    - المقاومة القريبة: {stock['r1']}
    - الدعم الأساسي: {stock['s1']}
    - مؤشر RSI: {stock['rsi']:.1f}
    
    المطلوب "بدقة":
    1. تحديد الهدف الأول (T1) والهدف الثاني (T2) والهدف التاريخي (T3).
    2. تحديد "وقف خسارة" رقمي صارم.
    3. كتابة نصيحة قصيرة جداً (Hold/Buy/Sell).
    رد بصيغة نقاط واضحة.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        # نظام محاكاة الأهداف الدقيقة في حال فشل الـ AI
        return f"🎯 T1: {t1:.2f} | 🎯 T2: {t2:.2f} | 🛑 SL: {stock['s1']:.2f}\n(تحليل رقمي تلقائي)"

# ==========================================
# 2. تصميم الواجهة (Professional Scanner UI)
# ==========================================
st.set_page_config(page_title="Wahba Precision Scanner", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Tajawal', sans-serif; background-color: #000; color: #fff; direction: rtl;
    }
    .stProgress > div > div > div > div { background-color: #d4af37; }
    .card {
        background: #0a0a0a; border: 1px solid #1a1a1a; padding: 20px;
        border-radius: 8px; border-right: 5px solid #d4af37; margin-bottom: 20px;
    }
    .target-box { background: #001a00; color: #00ff41; padding: 15px; border-radius: 5px; border: 1px solid #003311; margin-top: 10px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🏹 رادار النخبة | أهداف دقيقة & تحليل مباشر")

# ==========================================
# 3. محرك المسح مع شريط التحميل (Scanner with Progress Bar)
# ==========================================
if st.button("🚀 بدء المسح الشامل (283 سهم)"):
    # جلب الرموز
    url = "https://scanner.tradingview.com/egypt/scan"
    res = requests.post(url, json={"markets": ["egypt"], "columns": ["name"]}, timeout=10)
    all_tickers = [item['s'].split(':')[1] for item in res.json()['data']]
    
    qualified = []
    
    # --- شريط تحميل المرحلة الأولى (المسح الفني) ---
    st.subheader("🔍 المرحلة 1: المسح الفني الفوري")
    p1 = st.progress(0)
    status_text = st.empty()
    
    for i, sym in enumerate(all_tickers):
        status_text.text(f"فحص السهم {i+1}/{len(all_tickers)}: {sym}")
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=2)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            
            # فلتر وول ستريت: (شراء + تريند صاعد + عزم)
            if (ind.get("close") > ind.get("SMA20")) and (ind.get("RSI") > 50) and ("BUY" in analysis.summary["RECOMMENDATION"]):
                qualified.append({
                    "sym": sym, "price": ind.get("close"), "rsi": ind.get("RSI"),
                    "s1": ind.get("Pivot.M.Classic.S1"), "r1": ind.get("Pivot.M.Classic.R1")
                })
        except: continue
        p1.progress((i + 1) / len(all_tickers))
    
    # --- شريط تحميل المرحلة الثانية (تحليل الـ AI) ---
    if qualified:
        st.subheader(f"🧠 المرحلة 2: تحديد الأهداف الدقيقة لـ {len(qualified)} سهم")
        p2 = st.progress(0)
        
        for i, stock in enumerate(qualified):
            status_text.markdown(f"جاري استخراج أهداف سهم: **{stock['sym']}**")
            
            # استدعاء التحليل
            report = get_precise_targets(stock)
            
            # عرض الكارت فوراً (Live Update)
            with st.container():
                st.markdown(f"""
                <div class="card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:28px; font-weight:900; color:#d4af37;">{stock['sym']}</span>
                        <span style="font-size:22px;">السعر: {stock['price']:.2f} EGP</span>
                    </div>
                    <div class="target-box">
                        {report.replace('\n', '<br>')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            p2.progress((i + 1) / len(qualified))
            time.sleep(1) # لضمان عدم حظر الـ API وظهور شريط التحميل بوضوح
            
        status_text.success("✅ اكتمل التحليل بنجاح!")
    else:
        status_text.warning("لم يتم العثور على أسهم مطابقة للشروط حالياً.")
