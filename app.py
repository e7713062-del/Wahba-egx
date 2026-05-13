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

def get_macd_analysis(stock):
    prompt = f"""
    بصفتك محلل فني، حلل سهم {stock['sym']}:
    السعر: {stock['price']} | قيمة MACD: {stock['macd']} | خط الإشارة: {stock['signal']}
    المقاومة: {stock['r1']} | الدعم: {stock['s1']}
    بناءً على تقاطع MACD والمستويات، هل السهم في بداية موجة صعود؟ جاوب باختصار.
    """
    try:
        response = model.generate_content(prompt, generation_config={"max_output_tokens": 80})
        return response.text.strip()
    except:
        return f"🎯 الهدف: {stock['r1']} | 🛑 الدعم: {stock['s1']}"

# ==========================================
# 2. تصميم الواجهة (The MACD Strategy Edition)
# ==========================================
st.set_page_config(page_title="Wahba MACD Scanner", layout="wide")
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #050505; color: #fff; direction: rtl; }
    .stProgress > div > div > div > div { background: linear-gradient(to right, #8a2be2, #00ff41); }
    .macd-card { border: 1px solid #222; padding: 20px; margin-bottom: 15px; border-right: 5px solid #8a2be2; background: #0c0c0c; border-radius: 10px; }
    .status-up { color: #00ff41; font-weight: bold; }
    .level-info { font-size: 13px; color: #aaa; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

st.title("🔮 رادار الماكد والمستويات | MACD & Pivot Strategy")

# ==========================================
# 3. المحرك البديل (MACD Engine)
# ==========================================
if st.button("🚀 فحص تقاطعات الماكد (البورصة المصرية)"):
    url = "https://scanner.tradingview.com/egypt/scan"
    res = requests.post(url, json={"markets": ["egypt"], "columns": ["name"]}, timeout=10)
    all_tickers = [item['s'].split(':')[1] for item in res.json()['data']]

    qualified = []
    st.subheader("🔍 جاري تحليل الزخم واتجاه السعر")
    p1 = st.progress(0)
    status = st.empty()
    
    for i, sym in enumerate(all_tickers):
        if i % 30 == 0 and i > 0: time.sleep(1.2) # حماية من التهنيج
            
        status.text(f"تحليل مؤشرات $ {sym} ... ({i+1}/{len(all_tickers)})")
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=2)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            
            # --- استراتيجية البديل (MACD + RSI + Levels) ---
            # 1. تقاطع إيجابي: خط الـ MACD أعلى من خط الإشارة (Bullish Crossover)
            macd_bullish = ind.get("MACD.macd") > ind.get("MACD.signal")
            
            # 2. RSI مرن: فوق الـ 45 (بيدي مساحة للأسهم اللي لسه بتلف لفوق)
            rsi_ok = ind.get("RSI") > 45
            
            # 3. السعر فوق نقطة الارتكاز (Pivot) لضمان الأمان
            above_pivot = ind.get("close") > ind.get("Pivot.M.Classic.Pivot")
            
            if macd_bullish and rsi_ok and above_pivot:
                qualified.append({
                    "sym": sym, "price": ind.get("close"), 
                    "macd": ind.get("MACD.macd"), "signal": ind.get("MACD.signal"),
                    "rsi": ind.get("RSI"), "s1": ind.get("Pivot.M.Classic.S1"),
                    "r1": ind.get("Pivot.M.Classic.R1")
                })
        except: continue
        p1.progress((i + 1) / len(all_tickers))

    if qualified:
        st.subheader(f"✨ تم العثور على {len(qualified)} سهم بزخم صاعد")
        p2 = st.progress(0)
        for i, s in enumerate(qualified):
            status.markdown(f"🧠 AI يحلل الموجة لـ: **{s['sym']}**")
            report = get_macd_analysis(s)
            
            st.markdown(f"""
            <div class="macd-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#8a2be2; font-size:22px;">$ {s['sym']}</b>
                    <b style="font-size:18px;">{s['price']:.2f} EGP</b>
                </div>
                <div class="level-info">
                    <span>الهدف (R1): <b style="color:#ff4b4b;">{s['r1']:.2f}</b></span> | 
                    <span>الدعم (S1): <b style="color:#00ff41;">{s['s1']:.2f}</b></span> |
                    <span>RSI: <b>{s['rsi']:.1f}</b></span>
                </div>
                <div class="status-up">📈 إشارة MACD: تقاطع إيجابي (صعود)</div>
                <div style="margin-top:10px; border-top:1px solid #222; padding-top:10px; font-size:14px;">
                    🤖 <b>رؤية الـ AI:</b> {report}
                </div>
            </div>
            """, unsafe_allow_html=True)
            p2.progress((i + 1) / len(qualified))
            time.sleep(0.3)
        status.empty()
    else:
        st.warning("لا توجد أسهم حالياً تظهر تقاطعات إيجابية للماكد.")
