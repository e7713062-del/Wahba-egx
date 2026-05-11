import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime
import pytz
import google.generativeai as genai
import json

# --- 1. إعدادات الذكاء الاصطناعي ---
GEMINI_API_KEY = "AIzaSyAHLshGDTIRhodR1CMAWGP_DH3622aADJQ" 
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# --- 2. إعدادات الوقت والهوية ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Elite Filter", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    .stApp { background-color: #000000; color: #ffffff; }
    .nav-bar { text-align: center; padding: 25px; border-bottom: 2px solid #d4af37; margin-bottom: 30px; }
    .logo-text { font-size: 32px; font-weight: 900; color: #fff; }
    .logo-text span { color: #d4af37; }
    .elite-card {
        background: #0d0d0d; border: 1px solid #d4af37; border-radius: 15px;
        padding: 25px; margin-bottom: 20px; position: relative;
        overflow: hidden; box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
    }
    .elite-tag {
        position: absolute; top: 0; left: 0; background: #d4af37;
        color: #000; padding: 5px 15px; font-weight: 900; font-size: 10px;
    }
    .ai-logic-box {
        background: rgba(212, 175, 55, 0.05); padding: 15px; border-radius: 10px;
        margin-top: 15px; border: 1px solid #222; color: #fff; line-height: 1.6;
    }
    </style>
    <div class="nav-bar">
        <div class="logo-text">WAHBA <span>ELITE OF ELITE</span></div>
        <p style="color:#666; font-size:12px;">نخبة النخبة - الأسهم المختارة بعناية فقط</p>
    </div>
""", unsafe_allow_html=True)

# --- 3. محرك الفلترة الذكي ---

def check_elite_status(sym, data):
    """الذكاء الاصطناعي يقرر: هل السهم يستحق الدخول في قائمة النخبة؟"""
    try:
        tech_context = (f"Stock: {sym}, Price: {data['Price']}, RSI: {data['RSI']}, "
                        f"Trend: {data['Signal']}, Support: {data['S1']}, Resistance: {data['R1']}")
        
        prompt = f"""
        Act as a strict Fund Manager. You only pick the top 5% of stocks.
        Data: {tech_context}.
        Rules for ELITE status:
        1. Must have a strong trend or be at a critical reversal point.
        2. RSI must not be overbought (>70) unless it's a massive breakout.
        3. Logic must be sound classical technical analysis.
        
        Task: 
        If the stock is EXCELLENT, return JSON: {{"status": "ELITE", "logic": "Explain why in 2 brief lines in Arabic"}}
        If the stock is average or weak, return JSON: {{"status": "REJECT"}}
        """
        
        response = ai_model.generate_content(prompt)
        # تنظيف النص لاستخراج الـ JSON
        cleaned_res = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(cleaned_res)
    except:
        return {"status": "REJECT"}

@st.cache_data(ttl=86400)
def fetch_egx_list(date_key):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except: return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "ISPH", "HELI"]

# --- 4. العرض النهائي المفلتر ---

if st.button("استخراج قائمة نخبة النخبة"):
    symbols = fetch_egx_list(today_key)
    p_bar = st.progress(0)
    elite_found = False
    
    # سنمر على الأسهم والذكاء الاصطناعي هو اللي هيفلتر
    for i, sym in enumerate(symbols[:30]): # فحص أول 30 سهم قوي
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=10)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            
            stock_data = {
                "Price": round(ind.get("close"), 2),
                "RSI": round(ind.get("RSI"), 2),
                "S1": round(ind.get("Pivot.M.Classic.S1"), 2),
                "R1": round(ind.get("Pivot.M.Classic.R1"), 2),
                "Signal": analysis.summary["RECOMMENDATION"]
            }

            # الفلترة عن طريق جيميناي
            decision = check_elite_status(sym, stock_data)
            
            if decision.get("status") == "ELITE":
                elite_found = True
                st.markdown(f"""
                    <div class="elite-card">
                        <div class="elite-tag">TOP TIER</div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 28px; font-weight: 900; color: #d4af37;">{sym}</span>
                            <span style="font-size: 24px; font-weight: bold; color: #fff;">{stock_data['Price']} EGP</span>
                        </div>
                        <div class="ai-logic-box">
                            <b style="color: #d4af37;">🦅 تحليل الصقر:</b><br>
                            {decision['logic']}
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 15px; font-size: 11px; color: #d4af37;">
                            <span>دعم: {stock_data['S1']}</span>
                            <span>مقاومة: {stock_data['R1']}</span>
                            <span>RSI: {stock_data['RSI']}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        except: continue
        p_bar.progress((i + 1) / 30)

    if not elite_found:
        st.warning("السوق حالياً لا يقدم فرص مطابقة لمعايير نخبة النخبة. انتظر سيولة جديدة.")

st.markdown('<div style="text-align:center; padding:40px; color:#222;">WAHBA ELITE MASTER © 2026</div>', unsafe_allow_html=True)
