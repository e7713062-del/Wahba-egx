import streamlit as st
from tradingview_ta import TA_Handler, Interval
import requests
import google.generativeai as genai
import time

# ==========================================
# 1. إعدادات الـ AI (محلل صفقات النخبة)
# ==========================================
API_KEY = "YOUR_API_KEY_HERE" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_final_selection(stock):
    prompt = f"""
    بصفتك Senior Trader، سهم {stock['sym']} سعره {stock['price']}.
    هو فوق EMA 50 و EMA 100، والـ RSI حالياً {stock['rsi']:.1f}.
    المقاومة {stock['r1']} والدعم {stock['s1']}.
    حدد بدقة: هل السهم في منطقة دخول آمنة؟ وما هو العائد المتوقع (RR Ratio)؟
    """
    try:
        response = model.generate_content(prompt, generation_config={"max_output_tokens": 80})
        return response.text.strip()
    except:
        return f"🎯 الهدف الرئيسي: {stock['r1']} | 🛑 وقف الخسارة: {stock['s1']}"

# ==========================================
# 2. الواجهة (Professional Terminal)
# ==========================================
st.set_page_config(page_title="Wahba Pro Filter", layout="wide")
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #050505; color: #fff; direction: rtl; }
    .stProgress > div > div > div > div { background: linear-gradient(to right, #f1c40f, #e67e22); }
    .gold-card { border: 1px solid #d4af37; padding: 20px; margin-bottom: 15px; background: #0a0a0a; border-radius: 12px; border-right: 8px solid #d4af37; }
    .badge { background: #d4af37; color: #000; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 11px; }
</style>
""", unsafe_allow_html=True)

st.title("🏆 تصفية النخبة | من 114 إلى أقوى 10 فرص")

# ==========================================
# 3. محرك التصفية النهائية (Final Filter)
# ==========================================
if st.button("🔱 ابدأ التصفية النهائية"):
    url = "https://scanner.tradingview.com/egypt/scan"
    res = requests.post(url, json={"markets": ["egypt"], "columns": ["name"]}, timeout=10)
    all_tickers = [item['s'].split(':')[1] for item in res.json()['data']]

    qualified = []
    st.subheader("🔍 جاري تطبيق معايير السيولة الصارمة")
    p1 = st.progress(0)
    status = st.empty()
    
    for i, sym in enumerate(all_tickers):
        # نظام الحماية من التهنيج (Hedge Protection)
        if i % 30 == 0 and i > 0: time.sleep(1.2) 
            
        status.text(f"فحص جودة السهم: {sym} ({i+1}/{len(all_tickers)})")
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=2)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            
            # --- فلاتر تصفية الـ 114 سهم (Elite Strategy) ---
            price = ind.get("close")
            ema50 = ind.get("EMA50")
            ema100 = ind.get("EMA100")
            rsi = ind.get("RSI")
            
            # 1. الاتجاه القوي: السعر فوق EMA 50 و EMA 100 معاً (تأكيد مؤسسي).
            # 2. الزخم المثالي: RSI بين 55 و 65 (بداية انفجار، مش متشبع).
            # 3. الأمان: السعر فوق الـ Pivot وفوق الدعم الأول S1.
            
            if (price > ema50 > ema100) and (55 < rsi < 65) and (price > ind.get("Pivot.M.Classic.S1")):
                qualified.append({
                    "sym": sym, "price": price, "rsi": rsi, "ema50": ema50,
                    "s1": ind.get("Pivot.M.Classic.S1"), "r1": ind.get("Pivot.M.Classic.R1")
                })
        except: continue
        p1.progress((i + 1) / len(all_tickers))

    if qualified:
        st.subheader(f"✨ تم تصفية الـ 114 سهم إلى {len(qualified)} فرصة من ذهب")
        for s in qualified:
            report = get_final_selection(s)
            st.markdown(f"""
            <div class="gold-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span class="badge">INSTITUTIONAL BUY</span>
                        <h2 style="color:#d4af37; margin:5px 0;">$ {s['sym']}</h2>
                    </div>
                    <div style="text-align:left;">
                        <h3 style="margin:0;">{s['price']:.2f} EGP</h3>
                        <p style="color:#2ecc71; font-size:12px;">RSI: {s['rsi']:.1f} (زخم مثالي)</p>
                    </div>
                </div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin:15px 0; border-top:1px solid #222; padding-top:10px;">
                    <span style="color:#00ff41;">🛡️ الدعم (S1): {s['s1']:.2f}</span>
                    <span style="color:#ff4b4b;">🚀 الهدف (R1): {s['r1']:.2f}</span>
                </div>
                <div style="background:#111; padding:12px; border-radius:6px; font-size:14px; line-height:1.5;">
                    🤖 <b>رؤية المحلل:</b> {report}
                </div>
            </div>
            """, unsafe_allow_html=True)
        status.empty()
    else:
        st.warning("لم يتم العثور على أسهم تحقق شروط النخبة حالياً. حاول مرة أخرى لاحقاً.")
