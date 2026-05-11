import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime
import pytz
import google.generativeai as genai
import json
import time

# --- 1. إعدادات الذكاء الاصطناعي (Sovereign AI) ---
GEMINI_API_KEY = "AIzaSyAHLshGDTIRhodR1CMAWGP_DH3622aADJQ" 
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# --- 2. إعدادات الوقت (توقيت القاهرة) ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Swing Intelligence", layout="wide")

# --- 3. التصميم المؤسسي الذهبي (Wahba UI) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    .stApp { background-color: #000000; color: #ffffff; }
    
    .nav-bar { text-align: center; padding: 30px; border-bottom: 2px solid #d4af37; margin-bottom: 30px; }
    .logo-text { font-size: 35px; font-weight: 900; color: #fff; letter-spacing: 1px; }
    .logo-text span { color: #d4af37; }

    .swing-card {
        background: linear-gradient(145deg, #0a0a0a, #111); border: 1px solid #d4af37;
        border-radius: 15px; padding: 25px; margin-bottom: 20px;
        border-right: 8px solid #d4af37; position: relative;
    }
    .explosive-card {
        background: linear-gradient(145deg, #0a0a0a, #111); border: 1px solid #ff4b4b;
        border-radius: 15px; padding: 25px; margin-bottom: 20px;
        border-right: 8px solid #ff4b4b; position: relative;
    }
    .badge {
        position: absolute; top: 0; left: 0; padding: 5px 15px;
        font-weight: 900; font-size: 10px; border-bottom-right-radius: 10px;
    }
    .logic-box {
        background: rgba(255,255,255,0.03); padding: 15px; border-radius: 8px;
        margin-top: 15px; border: 1px solid #222; font-size: 14px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #d4af37, #f2d06b) !important;
        color: #000 !important; font-weight: 900 !important; height: 60px !important;
        border-radius: 12px !important; width: 100% !important; border: none !important;
    }
    </style>
    <div class="nav-bar">
        <div class="logo-text">WAHBA <span>SWING INTELLIGENCE</span></div>
        <p style="color:#666; font-size:12px;">نخبة النخبة: نظام صيد موجات السوينج والانفجارات</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. محرك الفلترة والتصنيف الذكي ---

def classify_swing_elite(sym, data):
    """الذكاء الاصطناعي يقوم بدور مدير الصندوق لتحليل وايكوف وإليوت"""
    try:
        tech_context = (f"Stock: {sym}, Price: {data['Price']}, RSI: {data['RSI']}, "
                        f"Signal: {data['Signal']}, Support: {data['S1']}, Resistance: {data['R1']}")
        
        prompt = f"""
        Act as a Master Swing Trader (Wyckoff & Elliott Wave specialist).
        Data: {tech_context}.
        
        Rules:
        1. 'STEADY_SWING': Clear uptrend, safe entries, Wave 3 or 5.
        2. 'EXPLOSIVE_SWING': Wyckoff Spring, Squeeze, or imminent massive Breakout.
        3. 'REJECT': Weak structure or overbought.
        
        Return JSON ONLY:
        {{
            "status": "STEADY_SWING" or "EXPLOSIVE_SWING" or "REJECT",
            "logic": "Explain the swing setup in 2 brief lines in Arabic"
        }}
        """
        response = ai_model.generate_content(prompt)
        res = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
        return res
    except: return {"status": "REJECT"}

@st.cache_data(ttl=86400)
def fetch_egx_list(date_key):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except: return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK"]

# --- 5. التنفيذ والعرض ---

if st.button("🚀 بدء مسح نخبة السوينج (EGX SCAN)"):
    symbols = fetch_egx_list(today_key)
    p_bar = st.progress(0)
    
    col1, col2 = st.columns(2)
    with col1: st.markdown("### 🔥 أسهم الانفجار الوشيك")
    with col2: st.markdown("### 📈 أسهم الصعود المستمر")

    scan_limit = 30
    for i, sym in enumerate(symbols[:scan_limit]):
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=10)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            
            stock_data = {
                "Price": round(ind.get("close"), 2), "RSI": round(ind.get("RSI"), 2),
                "S1": round(ind.get("Pivot.M.Classic.S1"), 2), "R1": round(ind.get("Pivot.M.Classic.R1"), 2),
                "Signal": analysis.summary["RECOMMENDATION"]
            }

            decision = classify_swing_elite(sym, stock_data)

            if decision['status'] == "EXPLOSIVE_SWING":
                with col1:
                    st.markdown(f"""
                        <div class="explosive-card">
                            <div class="badge" style="background:#ff4b4b;">EXPLOSIVE SWING</div>
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-size:28px; font-weight:900; color:#ff4b4b;">{sym}</span>
                                <span style="font-size:22px; font-weight:bold;">{stock_data['Price']} EGP</span>
                            </div>
                            <div class="logic-box"><b>🦅 الرؤية:</b> {decision['logic']}</div>
                        </div>
                    """, unsafe_allow_html=True)
            
            elif decision['status'] == "STEADY_SWING":
                with col2:
                    st.markdown(f"""
                        <div class="swing-card">
                            <div class="badge" style="background:#d4af37;">STEADY SWING</div>
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-size:28px; font-weight:900; color:#d4af37;">{sym}</span>
                                <span style="font-size:22px; font-weight:bold;">{stock_data['Price']} EGP</span>
                            </div>
                            <div class="logic-box"><b>🦅 الرؤية:</b> {decision['logic']}</div>
                        </div>
                    """, unsafe_allow_html=True)
        except: continue
        p_bar.progress((i + 1) / scan_limit)

st.markdown('<div style="text-align:center; padding:50px; color:#333; font-size:10px;">WAHBA SWING TERMINAL © 2026</div>', unsafe_allow_html=True)
