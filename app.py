import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import google.generativeai as genai
import time
from datetime import datetime

# ==========================================
# 1. نظام الـ AI الهجين (أهداف دقيقة + سرعة)
# ==========================================
API_KEY = "YOUR_API_KEY_HERE" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_pro_targets(stock):
    """تحديد أهداف SMC دقيقة جداً"""
    # حسابات رياضية سريعة كـ (Back-up) عشان لو المنصة هنجت
    t1 = stock['r1']
    t2 = stock['r1'] + (stock['r1'] - stock['s1']) * 0.5
    sl = stock['s1'] * 0.98 # وقف خسارة تحت الدعم بـ 2%
    
    prompt = f"""
    بصفتك Senior Trader، سهم {stock['sym']} سعره {stock['price']}.
    المقاومة {stock['r1']}، الدعم {stock['s1']}، RSI {stock['rsi']:.1f}.
    حدد بدقة: Entry, T1, T2, SL. 
    اجعل الرد في 4 سطر فقط.
    """
    try:
        # تقليل الـ Tokens لزيادة السرعة ومنع التهنيج
        response = model.generate_content(prompt, generation_config={"max_output_tokens": 80})
        return response.text.strip()
    except:
        return f"🎯 T1: {t1:.2f} | 🎯 T2: {t2:.2f} | 🛑 SL: {sl:.2f} (Calculated Mode)"

# ==========================================
# 2. واجهة مستخدم Wall Street (Ultra-Scannable)
# ==========================================
st.set_page_config(page_title="Wahba Pro Scanner", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #050505; color: #fff; direction: rtl;
    }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #d4af37, #f1c40f); }
    .terminal-card {
        background: #0a0a0a; border: 1px solid #1a1a1a; padding: 15px;
        margin-bottom: 10px; border-right: 5px solid #d4af37;
    }
    .ai-flash { color: #00ff41; font-family: 'Roboto Mono', monospace; font-size: 14px; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

st.title("🏹 WAHBA PRO | رادار الأهداف الذكي")

# ==========================================
# 3. المحرك (Scanner Engine)
# ==========================================
if st.button("🚀 تشغيل نظام المسح الشامل (EGX 283)"):
    # 1. جلب كل الأسهم
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"markets": ["egypt"], "columns": ["name"]}, timeout=10)
        all_tickers = [item['s'].split(':')[1] for item in res.json()['data']]
    except:
        all_tickers = ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK"] # Backup list

    qualified = []
    
    # المرحلة الأولى: المسح الفني (Progress Bar 1)
    st.subheader("🔍 المرحلة 1: تصفية السيولة والاتجاه")
    p1 = st.progress(0)
    status = st.empty()
    
    for i, sym in enumerate(all_tickers):
        status.text(f"فحص سيولة: {sym} ({i+1}/{len(all_tickers)})")
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=2)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            
            # فلتر النخبة (إغلاق يومي صاعد + عزم)
            if (ind.get("close") > ind.get("SMA20")) and (ind.get("RSI") > 52) and ("BUY" in analysis.summary["RECOMMENDATION"]):
                qualified.append({
                    "sym": sym, "price": ind.get("close"), "rsi": ind.get("RSI"),
                    "s1": ind.get("Pivot.M.Classic.S1"), "r1": ind.get("Pivot.M.Classic.R1")
                })
        except: continue
        p1.progress((i + 1) / len(all_tickers))

    # المرحلة الثانية: تحليل الأهداف (Progress Bar 2 + Live Display)
    if qualified:
        st.subheader(f"🎯 المرحلة 2: استخراج الأهداف لـ {len(qualified)} فرصة")
        p2 = st.progress(0)
        
        for i, s in enumerate(qualified):
            status.markdown(f"🧠 AI يحلل أهداف: **{s['sym']}**")
            
            report = get_pro_targets(s)
            
            # عرض الكارت فوراً عشان ما تزهقش من الانتظار
            st.markdown(f"""
            <div class="terminal-card">
                <div style="display:flex; justify-content:space-between; font-weight:bold;">
                    <span style="color:#d4af37; font-size:20px;">$ {s['sym']}</span>
                    <span>{s['price']:.2f} EGP</span>
                </div>
                <div class="ai-flash">{report.replace('\n', '<br>')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            p2.progress((i + 1) / len(qualified))
            time.sleep(0.5) # فاصل بسيط لمنع تهنيج الـ API
            
        status.success(f"✅ اكتمل المسح. تم إيجاد {len(qualified)} فرصة جاهزة.")
    else:
        status.warning("لا توجد فرص تحقق شروط 'وول ستريت' حالياً.")
