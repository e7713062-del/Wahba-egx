import streamlit as st
from tradingview_ta import TA_Handler, Interval
import requests
import google.generativeai as genai
import time

# ==========================================
# 1. إعدادات الـ AI (محلل صفقات سريعة)
# ==========================================
API_KEY = "YOUR_API_KEY_HERE" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_smart_analysis(stock):
    prompt = f"""
    بصفتك Swing Trader محترف، حلل سهم {stock['sym']}:
    السعر {stock['price']} فوق المتوسط (EMA 50) بمسافة جيدة. 
    RSI حالياً {stock['rsi']:.1f}. المقاومة القادمة {stock['r1']}.
    بناءً على السلوك السعري، هل تنصح بالدخول الآن أم انتظار تصحيح؟
    """
    try:
        response = model.generate_content(prompt, generation_config={"max_output_tokens": 80})
        return response.text.strip()
    except:
        return f"🚀 الاتجاه صاعد بقوة. الهدف: {stock['r1']} | الوقف: {stock['s1']}"

# ==========================================
# 2. الواجهة (Modern Elite Interface)
# ==========================================
st.set_page_config(page_title="Wahba Elite Flex", layout="wide")
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #080a0c; color: #f0f2f6; direction: rtl; }
    .stProgress > div > div > div > div { background: linear-gradient(to right, #00d2ff, #3a7bd5); }
    .elite-flex-card { border: 1px solid #1e3a5f; padding: 20px; margin-bottom: 15px; background: #111b27; border-radius: 12px; border-right: 6px solid #00d2ff; }
    .metric-box { background: #0d1117; padding: 8px; border-radius: 6px; border: 0.5px solid #30363d; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.title("💎 رادار نخبة النخبة (الإصدار المرن)")

# ==========================================
# 3. محرك الفلترة الذكي (Smart Elite Engine)
# ==========================================
if st.button("🔍 استخراج الأسهم القيادية (نمو سريع)"):
    url = "https://scanner.tradingview.com/egypt/scan"
    res = requests.post(url, json={"markets": ["egypt"], "columns": ["name"]}, timeout=10)
    all_tickers = [item['s'].split(':')[1] for item in res.json()['data']]

    qualified = []
    st.subheader("📡 جاري مسح السوق المصري بحثاً عن القوة الشرائية")
    p1 = st.progress(0)
    status = st.empty()
    
    for i, sym in enumerate(all_tickers):
        if i % 30 == 0 and i > 0: time.sleep(1)
            
        status.text(f"تحليل $ {sym} ... ({i+1}/{len(all_tickers)})")
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=2)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            
            # --- فلاتر النخبة المرنة ---
            price = ind.get("close")
            ema50 = ind.get("EMA50")
            rsi = ind.get("RSI")
            
            # 1. الاتجاه: السعر فوق متوسط 50 يوم (ده لوحده بيضمن إن السهم "شغال").
            # 2. الزخم: RSI فوق 53 (عشان نضمن إن فيه مشتري) بس تحت 75 (عشان ما نشتريش في القمة).
            # 3. الترتيب: السعر فوق نقطة الارتكاز (Pivot) وفوق الدعم الأول (S1).
            
            if price > ema50 and 53 < rsi < 75 and price > ind.get("Pivot.M.Classic.Pivot"):
                qualified.append({
                    "sym": sym, "price": price, "rsi": rsi, "ema50": ema50,
                    "s1": ind.get("Pivot.M.Classic.S1"), "r1": ind.get("Pivot.M.Classic.R1")
                })
        except: continue
        p1.progress((i + 1) / len(all_tickers))

    if qualified:
        st.subheader(f"✨ تم اختيار {len(qualified)} أسهم قيادية")
        for s in qualified:
            report = get_smart_analysis(s)
            st.markdown(f"""
            <div class="elite-flex-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#00d2ff; font-size:24px;">$ {s['sym']}</b>
                    <b style="font-size:20px;">{s['price']:.2f} EGP</b>
                </div>
                <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:10px; margin-top:15px;">
                    <div class="metric-box"><small>RSI</small><br><b>{s['rsi']:.1f}</b></div>
                    <div class="metric-box"><small>دعم EMA50</small><br><b>{s['ema50']:.2f}</b></div>
                    <div class="metric-box" style="color:#00ff41;"><small>دعم قريب</small><br><b>{s['s1']:.2f}</b></div>
                    <div class="metric-box" style="color:#ff4b4b;"><small>هدف قريب</small><br><b>{s['r1']:.2f}</b></div>
                </div>
                <div style="margin-top:15px; border-top:1px solid #1e3a5f; padding-top:10px; font-style: italic; color:#bdc3c7;">
                    🤖 <b>تحليل AI:</b> {report}
                </div>
            </div>
            """, unsafe_allow_html=True)
        status.empty()
    else:
        st.warning("السوق حالياً في مرحلة انتظار، لا توجد أسهم مطابقة للمواصفات النخبوية.")
