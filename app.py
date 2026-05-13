import streamlit as st
from tradingview_ta import TA_Handler, Interval
import requests
import google.generativeai as genai
import time

# ==========================================
# 1. إعدادات الـ AI (محلل الفرص المتاحة)
# ==========================================
API_KEY = "YOUR_API_KEY_HERE" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_opportunity_analysis(stock):
    prompt = f"""
    كمحلل أسواق، سهم {stock['sym']} سعره {stock['price']} فوق متوسط 20 يوم. 
    RSI حالياً {stock['rsi']:.1f} والمقاومة {stock['r1']}.
    حدد باختصار: هل السهم مناسب للشراء الآن وما هو الهدف المتوقع؟
    """
    try:
        response = model.generate_content(prompt, generation_config={"max_output_tokens": 60})
        return response.text.strip()
    except:
        return f"🎯 الهدف القادم: {stock['r1']} | 🛑 الدعم: {stock['s1']}"

# ==========================================
# 2. الواجهة (Clean & Professional Interface)
# ==========================================
st.set_page_config(page_title="Wahba Opportunity Scanner", layout="wide")
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #0c0f12; color: #ffffff; direction: rtl; }
    .stProgress > div > div > div > div { background: #3498db; }
    .opp-card { border: 1px solid #2c3e50; padding: 15px; margin-bottom: 12px; background: #1a1e23; border-radius: 8px; border-right: 4px solid #3498db; }
    .label { color: #95a5a6; font-size: 12px; }
    .value { color: #ecf0f1; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🏹 رادار الفرص المتاحة | Wahba Scan")

# ==========================================
# 3. محرك البحث (Opportunity Engine)
# ==========================================
if st.button("🚀 فحص فرص السوق الحالية"):
    url = "https://scanner.tradingview.com/egypt/scan"
    res = requests.post(url, json={"markets": ["egypt"], "columns": ["name"]}, timeout=10)
    all_tickers = [item['s'].split(':')[1] for item in res.json()['data']]

    qualified = []
    st.subheader("🔍 جاري جرد الأسهم بحثاً عن زخم صاعد")
    p1 = st.progress(0)
    status = st.empty()
    
    for i, sym in enumerate(all_tickers):
        if i % 35 == 0 and i > 0: time.sleep(1) # حماية من التهنيج (Hedge Protection)
            
        status.text(f"مراقبة $ {sym} ... ({i+1}/{len(all_tickers)})")
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=2)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            
            # --- فلاتر الفرص (أقل صرامة) ---
            price = ind.get("close")
            ema20 = ind.get("EMA20") # متوسط قصير المدى
            rsi = ind.get("RSI")
            
            # 1. السعر فوق متوسط 20 يوم (يعني السهم في حالة "صعود لحظي")
            # 2. RSI فوق 45 (بيدي فرصة للأسهم اللي لسه بتلف من تحت)
            # 3. السعر فوق الدعم الأول (S1) لضمان عدم الانهيار
            
            if price > ema20 and rsi > 45 and price > ind.get("Pivot.M.Classic.S1"):
                qualified.append({
                    "sym": sym, "price": price, "rsi": rsi, "ema20": ema20,
                    "s1": ind.get("Pivot.M.Classic.S1"), "r1": ind.get("Pivot.M.Classic.R1")
                })
        except: continue
        p1.progress((i + 1) / len(all_tickers))

    if qualified:
        st.subheader(f"✅ تم العثور على {len(qualified)} فرصة نشطة")
        for s in qualified:
            report = get_opportunity_analysis(s)
            st.markdown(f"""
            <div class="opp-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#3498db; font-size:22px;">$ {s['sym']}</b>
                    <b style="font-size:18px;">{s['price']:.2f} EGP</b>
                </div>
                <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:10px; margin-top:10px;">
                    <div><span class="label">RSI:</span> <span class="value">{s['rsi']:.1f}</span></div>
                    <div><span class="label">دعم (S1):</span> <span class="value" style="color:#2ecc71;">{s['s1']:.2f}</span></div>
                    <div><span class="label">هدف (R1):</span> <span class="value" style="color:#e74c3c;">{s['r1']:.2f}</span></div>
                </div>
                <div style="margin-top:10px; border-top:1px solid #2c3e50; padding-top:8px; font-size:14px; color:#bdc3c7;">
                    🤖 {report}
                </div>
            </div>
            """, unsafe_allow_html=True)
        status.empty()
    else:
        st.warning("لا توجد فرص واضحة حالياً، يرجى إعادة المحاولة مع افتتاح الجلسة القادمة.")
