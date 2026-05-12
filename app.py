import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import google.generativeai as genai
import time

# ==========================================
# 1. إعدادات الـ AI (Gemini 1.5 Flash)
# ==========================================
API_KEY = "YOUR_API_KEY_HERE" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_pro_ai_analysis(stock):
    prompt = f"""
    بصفتك Swing Trader محترف، حلل سهم {stock['sym']}:
    السعر الحالي: {stock['price']}
    المقاومات: R1={stock['r1']}, R2={stock['r2']}
    الدعوم: S1={stock['s1']}, S2={stock['s2']}
    المطلوب: جملة واحدة تحدد أفضل نقطة جني أرباح ووقف خسارة نهائي.
    """
    try:
        response = model.generate_content(prompt, generation_config={"max_output_tokens": 70})
        return response.text.strip()
    except:
        return f"🎯 الهدف الأساسي: {stock['r1']} | 🛑 حماية الأرباح: {stock['s1']}"

# ==========================================
# 2. تصميم الواجهة الاحترافية
# ==========================================
st.set_page_config(page_title="Wahba S&R Scanner", layout="wide")
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #050505; color: #fff; direction: rtl; }
    .stProgress > div > div > div > div { background: linear-gradient(to right, #d4af37, #ffd700); }
    .stock-card { border: 1px solid #222; padding: 20px; margin-bottom: 15px; border-right: 5px solid #d4af37; background: #0c0c0c; border-radius: 5px; }
    .levels { display: flex; justify-content: space-around; margin-top: 10px; font-size: 13px; font-family: monospace; }
    .res { color: #ff4b4b; } /* المقاومة باللون الأحمر */
    .sup { color: #00ff41; } /* الدعم باللون الأخضر */
</style>
""", unsafe_allow_html=True)

st.title("🎯 رادار الدعوم والمقاومات | صفوة الأسهم")

# ==========================================
# 3. محرك المسح بنظام المستويات (S&R Engine)
# ==========================================
if st.button("🚀 ابدأ فلترة النخبة"):
    url = "https://scanner.tradingview.com/egypt/scan"
    res = requests.post(url, json={"markets": ["egypt"], "columns": ["name"]}, timeout=10)
    all_tickers = [item['s'].split(':')[1] for item in res.json()['data']]

    qualified = []
    st.subheader("🔍 جاري حساب المستويات واصطياد الفرص")
    p1 = st.progress(0)
    status = st.empty()
    
    for i, sym in enumerate(all_tickers):
        # حماية من التهنيج (Hedge protection)
        if i % 25 == 0 and i > 0: time.sleep(1.2)
            
        status.text(f"يتم الآن تحليل: {sym} ({i+1}/{len(all_tickers)})")
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=2)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            
            # --- الفلتر الصارم لتقليل العدد ---
            # 1. فوق المتوسطات (SMA 20 & 50)
            # 2. RSI في منطقة القوة (بين 55 و 70)
            # 3. لازم يكون السعر قريب من الـ Pivot أو مخترقه بقوة
            if (ind.get("close") > ind.get("SMA20")) and (55 < ind.get("RSI") < 72):
                qualified.append({
                    "sym": sym, "price": ind.get("close"), "rsi": ind.get("RSI"),
                    "s1": ind.get("Pivot.M.Classic.S1"), "s2": ind.get("Pivot.M.Classic.S2"),
                    "r1": ind.get("Pivot.M.Classic.R1"), "r2": ind.get("Pivot.M.Classic.R2")
                })
        except: continue
        p1.progress((i + 1) / len(all_tickers))

    if qualified:
        st.subheader(f"✨ وجدت {len(qualified)} أسهم في منطقة ذهبية")
        p2 = st.progress(0)
        for i, s in enumerate(qualified):
            status.markdown(f"🧠 AI يضع اللمسة الأخيرة لـ: **{s['sym']}**")
            report = get_pro_ai_analysis(s)
            
            st.markdown(f"""
            <div class="stock-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#d4af37; font-size:24px;">$ {s['sym']}</b>
                    <b style="font-size:20px;">{s['price']:.2f} EGP</b>
                </div>
                <div class="levels">
                    <span class="sup">دعم1: {s['s1']:.2f}</span>
                    <span class="sup">دعم2: {s['s2']:.2f}</span>
                    <span class="res">مقاومة1: {s['r1']:.2f}</span>
                    <span class="res">مقاومة2: {s['r2']:.2f}</span>
                </div>
                <div style="color:#fff; margin-top:12px; padding:10px; border-top:1px dashed #333; font-size:14px;">
                    🤖 <b>رؤية الـ AI:</b> {report}
                </div>
            </div>
            """, unsafe_allow_html=True)
            p2.progress((i + 1) / len(qualified))
            time.sleep(0.5)
        status.empty()
    else:
        st.warning("السوق حالياً هادئ، لا توجد أسهم تطابق 'شروط النخبة'.")
