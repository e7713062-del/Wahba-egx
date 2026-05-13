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

def get_balanced_analysis(stock):
    prompt = f"""
    بصفتك Swing Trader، حلل سهم {stock['sym']}:
    السعر الحالي: {stock['price']} | المقاومة القريبة: {stock['r1']} | الدعم: {stock['s1']}
    السهم أظهر سيولة جيدة. حدد نقطة دخول مثالية وهدف قريب باختصار.
    """
    try:
        response = model.generate_content(prompt, generation_config={"max_output_tokens": 80})
        return response.text.strip()
    except:
        return f"🎯 الهدف القادم: {stock['r1']} | 🛑 حماية الأرباح عند: {stock['s1']}"

# ==========================================
# 2. تصميم الواجهة (The Balanced Terminal)
# ==========================================
st.set_page_config(page_title="Wahba Growth Scanner", layout="wide")
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #050505; color: #e0e0e0; direction: rtl; }
    .stProgress > div > div > div > div { background: linear-gradient(to right, #1e90ff, #00ff41); }
    .stock-card { border: 1px solid #222; padding: 20px; margin-bottom: 15px; border-right: 5px solid #1e90ff; background: #0c0c0c; border-radius: 10px; }
    .metric-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 10px; }
    .tag { background: #1a1a1a; padding: 4px 8px; border-radius: 4px; font-size: 12px; border: 0.5px solid #333; }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ سكانر الفرص المتوازنة | Wahba Growth")

# ==========================================
# 3. المحرك المحدث (Balanced Engine)
# ==========================================
if st.button("🚀 فحص فرص النمو (توسيع النطاق)"):
    url = "https://scanner.tradingview.com/egypt/scan"
    res = requests.post(url, json={"markets": ["egypt"], "columns": ["name"]}, timeout=10)
    all_tickers = [item['s'].split(':')[1] for item in res.json()['data']]

    qualified = []
    st.subheader("🔍 جاري البحث عن أسهم السيولة الصاعدة")
    p1 = st.progress(0)
    status = st.empty()
    
    for i, sym in enumerate(all_tickers):
        # نظام الحماية من التهنيج (Hedge Protection)
        if i % 30 == 0 and i > 0: time.sleep(1.2)
            
        status.text(f"مراقبة $ {sym} ... ({i+1}/{len(all_tickers)})")
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=2)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            
            # --- تعديل الدقة (Balanced Criteria) ---
            # 1. السعر فوق الدعم المحوري (Pivot) بدلاً من S1 (شرط أسهل شوية)
            price_above_pivot = ind.get("close") > ind.get("Pivot.M.Classic.Pivot")
            
            # 2. الفوليوم أعلى من متوسط 5 أيام مش 10 (عشان يلقط الحركة أسرع)
            volume_spike = ind.get("volume") > ind.get("average_volume_10d") * 0.8 
            
            # 3. RSI فوق الـ 48 (بدل 55) - ده بيدي مساحة للأسهم اللي لسه بتبدأ تقوم
            momentum = ind.get("RSI") > 48
            
            if price_above_pivot and volume_spike and momentum:
                qualified.append({
                    "sym": sym, "price": ind.get("close"), "vol": ind.get("volume"),
                    "rsi": ind.get("RSI"), "s1": ind.get("Pivot.M.Classic.S1"),
                    "r1": ind.get("Pivot.M.Classic.R1"), "r2": ind.get("Pivot.M.Classic.R2")
                })
        except: continue
        p1.progress((i + 1) / len(all_tickers))

    if qualified:
        st.subheader(f"✅ تم العثور على {len(qualified)} فرصة محتملة")
        p2 = st.progress(0)
        for i, s in enumerate(qualified):
            status.markdown(f"🧠 تحليل الفرصة: **{s['sym']}**")
            report = get_balanced_analysis(s)
            
            st.markdown(f"""
            <div class="stock-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#1e90ff; font-size:22px;">$ {s['sym']}</b>
                    <b style="font-size:18px;">{s['price']:.2f} EGP</b>
                </div>
                <div class="metric-grid">
                    <span class="tag">RSI: {s['rsi']:.1f}</span>
                    <span class="tag">الفوليوم: {s['vol']:,}</span>
                    <span class="tag" style="color:#00ff41;">دعم: {s['s1']:.2f}</span>
                    <span class="tag" style="color:#ff4b4b;">مقاومة: {s['r1']:.2f}</span>
                </div>
                <div style="margin-top:15px; padding-top:10px; border-top:1px solid #222; font-size:14px; color:#bbb;">
                    🤖 <b>توصية الـ AI:</b> {report}
                </div>
            </div>
            """, unsafe_allow_html=True)
            p2.progress((i + 1) / len(qualified))
            time.sleep(0.3)
        status.empty()
    else:
        st.warning("السوق حالياً في حالة ركود تامة، لم يتم العثور على فرص مطابقة.")
