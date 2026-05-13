import streamlit as st
from tradingview_ta import TA_Handler, Interval
import requests
import google.generativeai as genai
import time

# ==========================================
# 1. إعدادات الـ AI
# ==========================================
API_KEY = "YOUR_API_KEY_HERE" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ma_analysis(stock):
    prompt = f"""
    بصفتك محلل فني، حلل سهم {stock['sym']}:
    السعر: {stock['price']} | متوسط 50 يوم: {stock['ema50']} | متوسط 200 يوم: {stock['ema200']}
    المقاومة: {stock['r1']} | الدعم: {stock['s1']}
    هل السعر فوق المتوسطات؟ وهل يقترب من مقاومة؟ جاوب باختصار كمتداول محترف.
    """
    try:
        response = model.generate_content(prompt, generation_config={"max_output_tokens": 80})
        return response.text.strip()
    except:
        return f"🚀 الاتجاه صاعد فوق المتوسطات | الهدف: {stock['r1']}"

# ==========================================
# 2. تصميم الواجهة (Trend Master Edition)
# ==========================================
st.set_page_config(page_title="Wahba Trend Scanner", layout="wide")
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #050505; color: #fff; direction: rtl; }
    .stProgress > div > div > div > div { background: linear-gradient(to right, #ffd700, #ff4500); }
    .ma-card { border: 1px solid #222; padding: 20px; margin-bottom: 15px; border-right: 5px solid #ffd700; background: #0c0c0c; border-radius: 12px; }
    .ma-badge { background: #1a1a1a; padding: 5px 12px; border-radius: 20px; font-size: 12px; border: 1px solid #333; color: #ffd700; }
</style>
""", unsafe_allow_html=True)

st.title("📈 رادار المتوسطات والدعوم | Moving Average Strategy")

# ==========================================
# 3. محرك البحث (MA & S/R Engine)
# ==========================================
if st.button("🔍 فحص اتجاهات الأسهم (EGX)"):
    url = "https://scanner.tradingview.com/egypt/scan"
    res = requests.post(url, json={"markets": ["egypt"], "columns": ["name"]}, timeout=10)
    all_tickers = [item['s'].split(':')[1] for item in res.json()['data']]

    qualified = []
    st.subheader("⚙️ جاري فحص المتوسطات المتحركة (EMA 50 & 200)")
    p1 = st.progress(0)
    status = st.empty()
    
    for i, sym in enumerate(all_tickers):
        if i % 30 == 0 and i > 0: time.sleep(1.2)
            
        status.text(f"تحليل اتجاه $ {sym} ... ({i+1}/{len(all_tickers)})")
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=2)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            
            # --- استراتيجية المتوسطات المتحركة ---
            # 1. السعر فوق متوسط 50 يوم (اتجاه متوسط المدى صاعد)
            # 2. السعر فوق متوسط 200 يوم (اتجاه طويل المدى صاعد)
            price = ind.get("close")
            ema50 = ind.get("EMA50")
            ema200 = ind.get("EMA200")
            
            if price > ema50 and price > ema200:
                qualified.append({
                    "sym": sym, "price": price, 
                    "ema50": ema50, "ema200": ema200,
                    "s1": ind.get("Pivot.M.Classic.S1"),
                    "r1": ind.get("Pivot.M.Classic.R1")
                })
        except: continue
        p1.progress((i + 1) / len(all_tickers))

    if qualified:
        st.subheader(f"✅ تم العثور على {len(qualified)} سهم في منطقة قوة")
        p2 = st.progress(0)
        for i, s in enumerate(qualified):
            status.markdown(f"🧠 تقييم الاتجاه لـ: **{s['sym']}**")
            report = get_ma_analysis(s)
            
            st.markdown(f"""
            <div class="ma-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#ffd700; font-size:22px;">$ {s['sym']}</b>
                    <b style="font-size:18px;">{s['price']:.2f} EGP</b>
                </div>
                <div style="margin: 15px 0; display: flex; gap: 10px; flex-wrap: wrap;">
                    <span class="ma-badge">EMA 50: {s['ema50']:.2f}</span>
                    <span class="ma-badge">EMA 200: {s['ema200']:.2f}</span>
                    <span class="ma-badge" style="color:#00ff41;">دعم (S1): {s['s1']:.2f}</span>
                    <span class="ma-badge" style="color:#ff4b4b;">مقاومة (R1): {s['r1']:.2f}</span>
                </div>
                <div style="background:#111; padding:10px; border-radius:5px; font-size:14px; border-right: 3px solid #ffd700;">
                    🤖 <b>رؤية الـ AI:</b> {report}
                </div>
            </div>
            """, unsafe_allow_html=True)
            p2.progress((i + 1) / len(qualified))
            time.sleep(0.3)
        status.empty()
    else:
        st.warning("لا توجد أسهم حالياً تتداول فوق متوسطات الـ 50 والـ 200.")
