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
    prompt = f"حلل سهم {stock['sym']} سعره {stock['price']} EGP. الأهداف بناءً على المقاومة {stock['r1']} والدعم {stock['s1']} باختصار."
    try:
        response = model.generate_content(prompt, generation_config={"max_output_tokens": 60})
        return response.text.strip()
    except:
        return f"🎯 الهدف: {stock['r1']} | 🛑 الوقف: {stock['s1']}"

# ==========================================
# 2. تصميم الواجهة (Wall Street Elite)
# ==========================================
st.set_page_config(page_title="Wahba Elite Scanner", layout="wide")
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #050505; color: #fff; direction: rtl; }
    .stProgress > div > div > div > div { background: linear-gradient(to right, #d4af37, #b8860b); }
    .elite-card { border: 1px solid #222; padding: 20px; margin-bottom: 15px; border-right: 6px solid #d4af37; background: #0c0c0c; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

st.title("🏆 سكانر النخبة | فلترة وول ستريت الصارمة")

# ==========================================
# 3. محرك الفلترة الصارمة (Strict Filtering)
# ==========================================
if st.button("🚀 تشغيل الفلترة الاحترافية"):
    url = "https://scanner.tradingview.com/egypt/scan"
    res = requests.post(url, json={"markets": ["egypt"], "columns": ["name"]}, timeout=10)
    all_tickers = [item['s'].split(':')[1] for item in res.json()['data']]

    qualified = []
    
    # شريط تحميل للمسح الفني
    st.subheader("🔍 جاري تصفية السوق (اختيار الأقوى فقط)")
    p1 = st.progress(0)
    status = st.empty()
    
    for i, sym in enumerate(all_tickers):
        # تقسيم المجموعات لتجنب التهنيج (Hedge protection)
        if i % 25 == 0 and i > 0: time.sleep(1.5)
            
        status.text(f"فحص المعايير لـ: {sym} ({i+1}/{len(all_tickers)})")
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=2)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            
            # --- معايير وول ستريت الصارمة لتقليل العدد ---
            # 1. الاتجاه: السعر فوق متوسط 20 و 50 و 200 (تريند صاعد حقيقي)
            is_trending = ind.get("close") > ind.get("SMA20") > ind.get("SMA50")
            # 2. الزخم: RSI لازم يكون بين 55 و 70 (قوي ومش متشبع زيادة)
            is_momentum = 55 < ind.get("RSI") < 70
            # 3. التوصية: لازم تكون "STRONG_BUY" حصراً
            is_strong = analysis.summary["RECOMMENDATION"] == "STRONG_BUY"
            
            if is_trending and is_momentum and is_strong:
                qualified.append({
                    "sym": sym, "price": ind.get("close"), "rsi": ind.get("RSI"),
                    "s1": ind.get("Pivot.M.Classic.S1"), "r1": ind.get("Pivot.M.Classic.R1")
                })
        except: continue
        p1.progress((i + 1) / len(all_tickers))

    # عرض النتائج النهائية
    if qualified:
        st.subheader(f"✅ تم العثور على {len(qualified)} فرصة ذهبية")
        p2 = st.progress(0)
        for i, s in enumerate(qualified):
            status.markdown(f"🧠 تحليل أهداف: **{s['sym']}**")
            report = get_ai_analysis(s)
            
            st.markdown(f"""
            <div class="elite-card">
                <div style="display:flex; justify-content:space-between;">
                    <b style="color:#d4af37; font-size:22px;">$ {s['sym']}</b>
                    <b style="font-size:18px;">{s['price']:.2f} EGP</b>
                </div>
                <div style="color:#00ff41; margin-top:10px; font-family:monospace;">{report}</div>
            </div>
            """, unsafe_allow_html=True)
            p2.progress((i + 1) / len(qualified))
            time.sleep(0.5)
        status.empty()
    else:
        st.warning("لا يوجد أسهم تطابق المعايير الصارمة اليوم. انتظر سيولة جديدة.")
