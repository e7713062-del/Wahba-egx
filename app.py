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

def get_pro_analysis(stock):
    prompt = f"""
    بصفتك Swing Trader، حلل سهم {stock['sym']}:
    السعر: {stock['price']} | الفوليوم: {stock['vol']} | مؤشر OBV: {stock['obv']}
    المقاومات: {stock['r1']}, {stock['r2']} | الدعوم: {stock['s1']}, {stock['s2']}
    المطلوب: هل السيولة (OBV) تدعم اختراق المقاومة؟ جاوب باختصار شديد جداً.
    """
    try:
        response = model.generate_content(prompt, generation_config={"max_output_tokens": 80})
        return response.text.strip()
    except:
        return f"🎯 الهدف: {stock['r1']} | 🛑 الدعم: {stock['s1']}"

# ==========================================
# 2. تصميم الواجهة (The Wahba Terminal)
# ==========================================
st.set_page_config(page_title="Wahba Pro Scanner", layout="wide")
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #050505; color: #fff; direction: rtl; }
    .stProgress > div > div > div > div { background: linear-gradient(to right, #00ff41, #008f11); }
    .stock-card { border: 1px solid #1a1a1a; padding: 20px; margin-bottom: 15px; border-right: 5px solid #d4af37; background: #0c0c0c; border-radius: 8px; }
    .level-tag { background: #111; padding: 5px 10px; border-radius: 4px; font-family: monospace; font-size: 12px; }
    .obv-signal { color: #00ff41; font-weight: bold; font-family: 'Courier New', monospace; }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ سكانر وهبة المتكامل | فوليوم + مستويات + OBV")

# ==========================================
# 3. المحرك الذكي (The Engine)
# ==========================================
if st.button("🚀 تشغيل المسح الاحترافي"):
    url = "https://scanner.tradingview.com/egypt/scan"
    res = requests.post(url, json={"markets": ["egypt"], "columns": ["name"]}, timeout=10)
    all_tickers = [item['s'].split(':')[1] for item in res.json()['data']]

    qualified = []
    st.subheader("🔍 فحص السيولة الذكية (OBV) واختراقات الحيتان")
    p1 = st.progress(0)
    status = st.empty()
    
    for i, sym in enumerate(all_tickers):
        # منع التهنيج (Hedge Protection)
        if i % 30 == 0 and i > 0: time.sleep(1.5)
            
        status.text(f"جاري فحص $ {sym} ... ({i+1}/{len(all_tickers)})")
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=2)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            
            # --- شروط النخبة (وول ستريت) ---
            # 1. السعر فوق الدعم (S1)
            # 2. الفوليوم أعلى من متوسط 10 أيام (دخول سيولة)
            # 3. مؤشر OBV في صعود (تجميع حقيقي)
            if (ind.get("close") > ind.get("Pivot.M.Classic.S1")) and \
               (ind.get("volume") > ind.get("average_volume_10d")) and \
               (ind.get("OBV") > ind.get("OBV[1]")): # OBV النهاردة أعلى من امبارح
                
                qualified.append({
                    "sym": sym, "price": ind.get("close"), "vol": ind.get("volume"),
                    "obv": ind.get("OBV"), "s1": ind.get("Pivot.M.Classic.S1"),
                    "r1": ind.get("Pivot.M.Classic.R1"), "r2": ind.get("Pivot.M.Classic.R2")
                })
        except: continue
        p1.progress((i + 1) / len(all_tickers))

    if qualified:
        st.subheader(f"✅ تم تصفية {len(qualified)} فرصة قوية")
        p2 = st.progress(0)
        for i, s in enumerate(qualified):
            status.markdown(f"🧠 AI يحلل تدفق السيولة لـ: **{s['sym']}**")
            report = get_pro_analysis(s)
            
            st.markdown(f"""
            <div class="stock-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#d4af37; font-size:24px;">$ {s['sym']}</b>
                    <b style="font-size:20px;">{s['price']:.2f} EGP</b>
                </div>
                <div style="margin: 15px 0; display: flex; gap: 10px;">
                    <span class="level-tag">الدعم: {s['s1']:.2f}</span>
                    <span class="level-tag" style="color:#ff4b4b;">المقاومة: {s['r1']:.2f}</span>
                    <span class="level-tag" style="color:#00ff41;">OBV صاعد 📈</span>
                </div>
                <div class="obv-signal">
                    💬 رؤية المحلل الذكي: {report}
                </div>
            </div>
            """, unsafe_allow_html=True)
            p2.progress((i + 1) / len(qualified))
            time.sleep(0.4)
        status.empty()
    else:
        st.warning("لا توجد فرص تجميع واضحة حالياً. راقب السوق لاحقاً.")
