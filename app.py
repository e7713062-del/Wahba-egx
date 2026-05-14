import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime
import pytz

# --- 1. إعدادات الوقت (القاهرة) ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Intelligence", layout="wide")

# --- 2. التصميم المؤسسي الكامل ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
* { font-family: 'Tajawal', sans-serif; }
.stApp { background-color: #000000; color: #ffffff; }
.nav-bar { text-align: center; padding: 30px; background: #000; border-bottom: 2px solid #d4af37; margin-bottom: 20px; }
.logo-text { font-size: 30px; font-weight: 900; color: #fff; letter-spacing: 2px; }
.logo-text span { color: #d4af37; }
.section-header { color: #d4af37; border-right: 5px solid #d4af37; padding-right: 15px; margin: 40px 0 20px 0; font-size: 24px; font-weight: bold; text-align: right; }
.stock-card { background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 15px; padding: 25px; margin-bottom: 10px; border-top: 3px solid #d4af37; }
.symbol-name { font-size: 28px; font-weight: 900; color: #d4af37; }
.price-val { font-size: 24px; font-weight: bold; color: #fff; }
.trade-tag { background: #1a1a1a; color: #d4af37; padding: 4px 12px; border-radius: 6px; font-size: 13px; border: 1px solid #d4af37; margin-right: 10px; font-weight: bold; }
.stButton>button { background: #d4af37 !important; color: #000 !important; font-weight: 900 !important; border-radius: 10px !important; height: 60px !important; width: 100% !important; border: none !important; }
.footer-box { margin-top: 80px; padding: 40px; text-align: center; border-top: 1px solid #1a1a1a; color: #444; font-size: 12px; }
</style>
<div class="nav-bar">
<div class="logo-text">WAHBA <span>INTELLIGENCE</span></div>
<p style="color:#444; font-size:10px;">INSTITUTIONAL GRADE TERMINAL</p>
</div>
""", unsafe_allow_html=True)

# --- 3. محرك البيانات ---
@st.cache_data(ttl=86400)
def fetch_egx_list(date_key):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "ETEL", "AMOC"]

@st.cache_data(ttl=3600, show_spinner=False)
def run_strategic_scan(date_key):
    symbols = fetch_egx_list(date_key)
    results = []
    p_bar = st.progress(0)
    for i, sym in enumerate(symbols):
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=10)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            rec = analysis.summary["RECOMMENDATION"]
            
            score = 0
            if "STRONG_BUY" in rec: score += 5
            elif "BUY" in rec: score += 3
            if ind.get("RSI") and 50 <= ind.get("RSI") <= 68: score += 3
            if ind.get("close") > ind.get("Pivot.M.Classic.Middle"): score += 2
            
            vol_ratio = (ind.get("volume") / ind.get("average_volume_10d")) if ind.get("average_volume_10d") else 1
            t_type = "⚡ DAY TRADING" if (vol_ratio > 1.5 or abs(ind.get("change", 0)) > 2.5) else "🌊 SWING"
            
            results.append({
                "Symbol": sym, "Price": ind.get("close"), "Score": score,
                "S1": ind.get("Pivot.M.Classic.S1"), "S2": ind.get("Pivot.M.Classic.S2"),
                "P": ind.get("Pivot.M.Classic.Middle"), "R1": ind.get("Pivot.M.Classic.R1"),
                "R2": ind.get("Pivot.M.Classic.R2"), "Signal": rec, "Type": t_type
            })
        except: continue
        p_bar.progress((i + 1) / len(symbols))
    p_bar.empty()
    return pd.DataFrame(results)

# --- 4. دالة العرض ---
def display_stock_card(row):
    st.markdown(f"""
    <div class="stock-card">
        <div style="display:flex; justify-content:space-between; align-items:center; direction: rtl;">
            <div><span class="symbol-name">{row['Symbol']}</span> <span class="trade-tag">{row['Type']}</span></div>
            <span style="color:#d4af37; font-weight:bold;">{row['Signal']}</span>
        </div>
        <div class="price-val" style="text-align: right; margin-top:10px;">{row['Price']:.2f} <small style="font-size:12px; color:#444;">EGP</small></div>
    </div>
    """, unsafe_allow_html=True)
    
    if row['S2'] and row['R2'] and row['R2'] != row['S2']:
        pos = max(0, min(100, ((row['Price'] - row['S2']) / (row['R2'] - row['S2'])) * 100))
        st.caption(f"📍 موقع السعر الحالي (S2 ↔ R2)")
        st.progress(int(pos))
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("S1", f"{row['S1']:.2f}")
    c2.metric("Pivot", f"{row['P']:.2f}")
    c3.metric("R1", f"{row['R1']:.2f}")
    c4.metric("R2", f"{row['R2']:.2f}")
    st.markdown("<br>", unsafe_allow_html=True)

# --- 5. التنفيذ ---
st.write(f"توقيت التقرير: {now_egypt.strftime('%H:%M')} | {today_key}")

if st.button('🚀 إصدار التقرير الذهبي لليوم'):
    st.session_state.final_report = run_strategic_scan(today_key)

if 'final_report' in st.session_state and st.session_state.final_report is not None:
    df = st.session_state.final_report
    
    # 1. نخبة النخبة (Score >= 9)
    t1 = df[df['Score'] >= 9]
    if not t1.empty:
        st.markdown('<div class="section-header">⚜️ نخبة نخبة الصعود</div>', unsafe_allow_html=True)
        for _, row in t1.iterrows(): display_stock_card(row)

    # 2. نخبة الصعود (Score 6-8)
    t2 = df[(df['Score'] >= 6) & (df['Score'] < 9)]
    if not t2.empty:
        st.markdown('<div class="section-header">💎 نخبة الصعود</div>', unsafe_allow_html=True)
        for _, row in t2.iterrows(): display_stock_card(row)

    # 3. تحركات السوق العادية (باقي الأسهم)
    t3 = df[df['Score'] < 6]
    if not t3.empty:
        st.markdown('<div class="section-header">📊 تحركات السوق العامة</div>', unsafe_allow_html=True)
        for _, row in t3.iterrows(): display_stock_card(row)

st.markdown('<div class="footer-box"><p style="font-weight:bold; color:#d4af37;">WAHBA INTELLIGENCE • INSTITUTIONAL DIVISION</p><p>جميع الحقوق محفوظة 2026</p></div>', unsafe_allow_html=True)
