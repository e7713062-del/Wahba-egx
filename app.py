import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import google.generativeai as genai
import time

# ==========================================
# 1. إعدادات الـ AI
# ==========================================
API_KEY = "YOUR_API_KEY_HERE" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_analysis(stock):
    prompt = f"حلل سهم {stock['sym']} سعره {stock['price']} EGP، الأهداف والوقف بناءً على المقاومة {stock['r1']} والدعم {stock['s1']} باختصار شديد."
    try:
        # تقليل الـ tokens جداً عشان السرعة
        response = model.generate_content(prompt, generation_config={"max_output_tokens": 50})
        return response.text.strip()
    except:
        return f"🎯 هدف: {stock['r1']} | 🛑 وقف: {stock['s1']}"

# ==========================================
# 2. تصميم الواجهة (Terminal Style)
# ==========================================
st.set_page_config(page_title="Wahba Anti-Lag Scanner", layout="wide")
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #000; color: #0f0; direction: rtl; }
    .stProgress > div > div > div > div { background-color: #d4af37; }
    .card { border: 1px solid #222; padding: 15px; margin-bottom: 10px; border-right: 5px solid #d4af37; background: #050505; }
</style>
""", unsafe_allow_html=True)

st.title("📟 رادار وهبة (نسخة الحماية من التهنيج)")

# ==========================================
# 3. محرك المسح المجدول (Scheduled Scanner)
# ==========================================
if st.button("🚀 ابدأ المسح المجدول"):
    # جلب الأسهم
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"markets": ["egypt"], "columns": ["name"]}, timeout=10)
        all_tickers = [item['s'].split(':')[1] for item in res.json()['data']]
    except:
        all_tickers = ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK"]

    qualified = []
    
    # --- المرحلة 1: مسح فني بنظام المجموعات (Anti-Block) ---
    st.subheader("🔍 جاري الفحص الفني (نظام المجموعات لعدم التهنيج)")
    p1 = st.progress(0)
    status = st.empty()
    
    batch_size = 20  # كل 20 سهم هياخد راحة
    for i, sym in enumerate(all_tickers):
        if i % batch_size == 0 and i > 0:
            status.warning(f"⏳ راحة قصيرة لتجنب حظر السيرفر... (تم فحص {i} سهم)")
            time.sleep(2) # راحة ثانيتين كل 20 طلب
            
        status.text(f"📡 فحص إشارات: {sym} ({i+1}/{len(all_tickers)})")
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=2)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            
            # الفلتر بتاعك (وول ستريت)
            if (ind.get("close") > ind.get("SMA20")) and (ind.get("RSI") > 52):
                qualified.append({
                    "sym": sym, "price": ind.get("close"), "rsi": ind.get("RSI"),
                    "s1": ind.get("Pivot.M.Classic.S1"), "r1": ind.get("Pivot.M.Classic.R1")
                })
        except: continue
        p1.progress((i + 1) / len(all_tickers))

    # --- المرحلة 2: الـ AI (تحليل فوري للأهداف) ---
    if qualified:
        st.subheader(f"🎯 تحليل الأهداف لـ {len(qualified)} فرصة")
        p2 = st.progress(0)
        
        for i, s in enumerate(qualified):
            status.markdown(f"🧠 استخراج أهداف: **{s['sym']}**")
            report = get_ai_analysis(s)
            
            # عرض الكارت فوراً
            st.markdown(f"""
            <div class="card">
                <b style="color:#d4af37;">$ {s['sym']} | {s['price']:.2f} EGP</b><br>
                <span style="color:#fff; font-size:14px;">{report}</span>
            </div>
            """, unsafe_allow_html=True)
            
            p2.progress((i + 1) / len(qualified))
            time.sleep(0.5) # فاصل بسيط للـ AI برضه
            
        status.success("✅ تم المسح بنجاح دون أي تهنيج!")
    else:
        status.warning("لم نجد فرصاً تحقق الشروط حالياً.")
