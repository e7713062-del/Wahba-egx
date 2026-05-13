import streamlit as st
from tradingview_ta import TA_Handler, Interval
import requests
import google.generativeai as genai
import time

# ==========================================
# 1. إعداد خبير التحليل (AI Strategy)
# ==========================================
API_KEY = "YOUR_API_KEY_HERE" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_final_verdict(stock):
    prompt = f"""
    بصفتك Swing Trader محترف، سهم {stock['sym']} سعره {stock['price']}.
    هو فوق المتوسطات (EMA 20 & 50) والـ RSI حالياً {stock['rsi']:.1f}.
    المقاومة {stock['r1']} والدعم {stock['s1']}.
    أعطِ قراراً نهائياً: هل السهم في منطقة انفجار سعري أم تجميع؟
    """
    try:
        response = model.generate_content(prompt, generation_config={"max_output_tokens": 70})
        return response.text.strip()
    except:
        return f"🎯 المستهدف: {stock['r1']} | 🛑 حماية الأرباح: {stock['s1']}"

# ==========================================
# 2. تصميم الواجهة (The Wahba Terminal)
# ==========================================
st.set_page_config(page_title="Wahba Final Filter", layout="wide")
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #050505; color: #fff; direction: rtl; }
    .stProgress > div > div > div > div { background: linear-gradient(to right, #00ff41, #008f11); }
    .final-card { border: 1px solid #1a1a1a; padding: 20px; margin-bottom: 15px; border-right: 5px solid #00ff41; background: #0c0c0c; border-radius: 8px; }
    .status-badge { background: #00ff41; color: #000; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 11px; }
</style>
""", unsafe_allow_html=True)

st.title("📊 المصفاة النهائية | تحليل شامل لفرص EGX")

# ==========================================
# 3. محرك الفحص العميق (Deep Scan)
# ==========================================
if st.button("🚀 ابدأ تحليل السوق وتصفية النخبة"):
    url = "https://scanner.tradingview.com/egypt/scan"
    res = requests.post(url, json={"markets": ["egypt"], "columns": ["name"]}, timeout=10)
    all_tickers = [item['s'].split(':')[1] for item in res.json()['data']]

    final_selection = []
    st.subheader(f"🔍 يتم الآن فحص {len(all_tickers)} سهم لاختيار الأقوى...")
    p1 = st.progress(0)
    status = st.empty()
    
    for i, sym in enumerate(all_tickers):
        if i % 30 == 0 and i > 0: time.sleep(1.2) # حماية من التهنيج
            
        status.text(f"تحليل تقني لـ: {sym} ({i+1}/{len(all_tickers)})")
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=2)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            
            # --- معايير التصفية لتقليل العدد (Focus Criteria) ---
            price = ind.get("close")
            ema20 = ind.get("EMA20")
            ema50 = ind.get("EMA50")
            rsi = ind.get("RSI")
            
            # 1. السعر فوق متوسط 20 و 50 يوم (اتجاه صاعد مؤكد).
            # 2. RSI في منطقة القوة (بين 52 و 65) - لسه مسخن مش طاير.
            # 3. السعر فوق نقطة الارتكاز (Pivot).
            
            if (price > ema20 > ema50) and (52 < rsi < 65) and (price > ind.get("Pivot.M.Classic.Pivot")):
                final_selection.append({
                    "sym": sym, "price": price, "rsi": rsi, 
                    "s1": ind.get("Pivot.M.Classic.S1"), "r1": ind.get("Pivot.M.Classic.R1")
                })
        except: continue
        p1.progress((i + 1) / len(all_tickers))

    if final_selection:
        st.subheader(f"✨ تم تصفية السوق إلى {len(final_selection)} فرصة ذهبية")
        for s in final_selection:
            verdict = get_final_verdict(s)
            st.markdown(f"""
            <div class="final-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span class="status-badge">INSTITUTIONAL MOMENTUM</span>
                        <h2 style="color:#00ff41; margin:5px 0;">$ {s['sym']}</h2>
                    </div>
                    <div style="text-align:left;">
                        <h3 style="margin:0;">{s['price']:.2f} EGP</h3>
                        <p style="color:#aaa; font-size:12px;">RSI: {s['rsi']:.1f}</p>
                    </div>
                </div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin:15px 0; border-top:1px solid #222; padding-top:10px;">
                    <span style="color:#00ff41;">🛡️ الدعم (S1): {s['s1']:.2f}</span>
                    <span style="color:#ff4b4b;">🚀 الهدف (R1): {s['r1']:.2f}</span>
                </div>
                <div style="background:#111; padding:12px; border-radius:6px; font-size:14px; border-right: 4px solid #00ff41;">
                    🤖 <b>قرار الـ AI:</b> {verdict}
                </div>
            </div>
            """, unsafe_allow_html=True)
        status.empty()
    else:
        st.warning("لم يتم العثور على أسهم تطابق 'معايير النخبة' حالياً.")
