import streamlit as st
from tradingview_ta import TA_Handler, Interval
import requests
import google.generativeai as genai
import time

# ==========================================
# 1. إعدادات الـ AI (الخبير الاستراتيجي)
# ==========================================
API_KEY = "YOUR_API_KEY_HERE" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_elite_analysis(stock):
    prompt = f"""
    بصفتك كبير محللي وول ستريت، حلل سهم {stock['sym']}:
    - السعر فوق EMA 50 ({stock['ema50']:.2f}) و EMA 200 ({stock['ema200']:.2f}).
    - المقاومة القادمة (R1): {stock['r1']:.2f}.
    - الدعم الأساسي (S1): {stock['s1']:.2f}.
    المطلوب: تقييم سريع جداً، هل السهم في منطقة "انفجار سعري"؟ حدد الهدف والوقف.
    """
    try:
        response = model.generate_content(prompt, generation_config={"max_output_tokens": 80})
        return response.text.strip()
    except:
        return f"🚀 سهم في اتجاه صاعد قوي. الهدف: {stock['r1']} | الوقف: {stock['s1']}"

# ==========================================
# 2. واجهة المستخدم (Elite Dark Terminal)
# ==========================================
st.set_page_config(page_title="Wahba Elite Terminal", layout="wide")
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #000; color: #fff; direction: rtl; }
    .stProgress > div > div > div > div { background: linear-gradient(to right, #d4af37, #ffffff); }
    .elite-card { border: 2px solid #d4af37; padding: 25px; margin-bottom: 20px; background: #080808; border-radius: 15px; box-shadow: 0 4px 15px rgba(212, 175, 55, 0.2); }
    .status-tag { background: #d4af37; color: #000; padding: 3px 12px; border-radius: 5px; font-weight: bold; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

st.title("💎 سكانر نخبة النخبة | THE ELITE TERMINAL")

# ==========================================
# 3. محرك الفلترة القصوى (Maximum Filter Engine)
# ==========================================
if st.button("🔱 استخراج صفوة الأسهم"):
    url = "https://scanner.tradingview.com/egypt/scan"
    res = requests.post(url, json={"markets": ["egypt"], "columns": ["name"]}, timeout=10)
    all_tickers = [item['s'].split(':')[1] for item in res.json()['data']]

    qualified = []
    st.subheader("🛡️ جاري تطبيق فلاتر المؤسسات المالية")
    p1 = st.progress(0)
    status = st.empty()
    
    for i, sym in enumerate(all_tickers):
        if i % 25 == 0 and i > 0: time.sleep(1.5)
            
        status.text(f"فحص جودة الاتجاه: {sym} ({i+1}/{len(all_tickers)})")
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=2)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            
            # --- معايير نخبة النخبة ---
            price = ind.get("close")
            ema50 = ind.get("EMA50")
            ema200 = ind.get("EMA200")
            rsi = ind.get("RSI")
            
            # 1. السعر فوق المتوسطين (EMA 50 & 200) -> تريند صاعد تاريخي.
            # 2. متوسط 50 فوق متوسط 200 (Golden Cross) -> تأكيد قوة الاتجاه.
            # 3. السعر فوق نقطة الارتكاز (Pivot).
            # 4. RSI بين 52 و 68 (قوة شرائية بدون تشبع خطر).
            
            if (price > ema50 > ema200) and (price > ind.get("Pivot.M.Classic.Pivot")) and (52 < rsi < 68):
                qualified.append({
                    "sym": sym, "price": price, "ema50": ema50, "ema200": ema200,
                    "s1": ind.get("Pivot.M.Classic.S1"), "r1": ind.get("Pivot.M.Classic.R1")
                })
        except: continue
        p1.progress((i + 1) / len(all_tickers))

    if qualified:
        st.subheader(f"✅ تم العثور على {len(qualified)} فرص ذهبية فقط")
        p2 = st.progress(0)
        for i, s in enumerate(qualified):
            status.markdown(f"🧠 تحليل استراتيجي لـ: **{s['sym']}**")
            report = get_elite_analysis(s)
            
            st.markdown(f"""
            <div class="elite-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span class="status-tag">HIGH PROBABILITY</span>
                        <h2 style="color:#d4af37; margin:10px 0;">$ {s['sym']}</h2>
                    </div>
                    <div style="text-align:left;">
                        <h3 style="margin:0;">{s['price']:.2f} EGP</h3>
                        <p style="color:#888; font-size:12px;">فوق EMA 50 & 200</p>
                    </div>
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin:15px 0; border-top:1px solid #222; padding-top:15px;">
                    <span style="color:#00ff41;">🎯 الهدف (R1): {s['r1']:.2f}</span>
                    <span style="color:#ff4b4b;">🛑 الوقف (S1): {s['s1']:.2f}</span>
                </div>
                <div style="background:#111; padding:15px; border-radius:8px; border-right:4px solid #d4af37;">
                    <b style="color:#d4af37;">📝 تقرير النخبة:</b><br>
                    <p style="margin-top:5px; font-size:14px; line-height:1.6;">{report}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            p2.progress((i + 1) / len(qualified))
            time.sleep(0.4)
        status.empty()
    else:
        st.warning("لا توجد أسهم حالياً تحقق معايير 'نخبة النخبة'. انتظر دورة سيولة جديدة.")
