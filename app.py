import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime
import pytz

# --- 1. إعدادات الوقت (القاهرة أوتوماتيك) ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Intelligence", layout="wide")

# --- 2. التصميم المؤسسي (الأصلي كامل + ستايلات مباشر) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
* { font-family: 'Tajawal', sans-serif; }
.stApp { background-color: #000000; color: #ffffff; }
.nav-bar { text-align: center; padding: 30px; background: #000; border-bottom: 2px solid #d4af37; margin-bottom: 20px; }
.logo-text { font-size: 30px; font-weight: 900; color: #fff; letter-spacing: 2px; }
.logo-text span { color: #d4af37; }
.section-header { color: #d4af37; border-right: 5px solid #d4af37; padding-right: 15px; margin: 40px 0 20px 0; font-size: 24px; font-weight: bold; text-align: right; }
.stock-card { background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 15px; padding: 25px; margin-bottom: 20px; border-top: 3px solid #d4af37; }
.symbol-name { font-size: 28px; font-weight: 900; color: #d4af37; }
.price-val { font-size: 24px; font-weight: bold; color: #fff; }
.trade-tag { background: #1a1a1a; color: #d4af37; padding: 4px 12px; border-radius: 6px; font-size: 13px; border: 1px solid #d4af37; margin-right: 10px; font-weight: bold; }
.levels-grid { display: flex; justify-content: space-between; margin-top: 20px; background: #000; padding: 10px; border-radius: 8px; border: 1px solid #111; }
.level-item { text-align: center; flex: 1; }
.label { font-size: 10px; color: #555; display: block; }
.num { font-size: 14px; font-weight: bold; color: #d4af37; font-family: monospace; }
.stButton>button { background: #d4af37 !important; color: #000 !important; font-weight: 900 !important; border-radius: 10px !important; height: 60px !important; width: 100% !important; border: none !important; }
.footer-box { margin-top: 80px; padding: 40px; text-align: center; border-top: 1px solid #1a1a1a; color: #444; font-size: 12px; }

/* أداة مباشر اللحظية */
.live-indicator-container { margin: 15px 0; position: relative; width: 100%; }
.indicator-bar { height: 12px; border-radius: 6px; background: linear-gradient(to right, #ff4d4d 0%, #ff4d4d 35%, #333 45%, #333 55%, #2ecc71 65%, #2ecc71 100%); border: 1px solid #222; }
.blue-marker { position: absolute; top: -4px; width: 3px; height: 20px; background-color: #3498db; border-radius: 2px; box-shadow: 0 0 8px #3498db; z-index: 5; }
.indicator-label { font-size: 10px; color: #d4af37; margin-bottom: 5px; text-align: right; font-weight: bold; }
</style>
<div class="nav-bar">
<div class="logo-text">WAHBA <span>INTELLIGENCE</span></div>
<p style="color:#444; font-size:10px;">INSTITUTIONAL GRADE TERMINAL</p>
</div>
""", unsafe_allow_html=True)

# --- 3. محرك البيانات (نسخة طبق الأصل من كودك) ---
@st.cache_data(ttl=86400)
def fetch_egx_list(date_key):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK"]

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
            
            # معادلات السكور والـ RSI الأصلية
            score = 0
            if "STRONG_BUY" in rec: score += 5
            elif "BUY" in rec: score += 3
            if ind.get("RSI") and 50 <= ind.get("RSI") <= 68: score += 3
            if ind.get("close") > ind.get("Pivot.M.Classic.Middle"): score += 2
            
            # حسبة الـ Vol والـ Type الأصلية
            vol_ratio = (ind.get("volume") / ind.get("average_volume_10d")) if ind.get("average_volume_10d") else 1
            t_type = "⚡ DAY TRADING" if (vol_ratio > 1.5 or abs(ind.get("change", 0)) > 2.5) else "🌊 SWING"
            
            # طوبة مباشر اللحظية
            s2, r2 = ind.get("Pivot.M.Classic.S2"), ind.get("Pivot.M.Classic.R2")
            curr = ind.get("close")
            pos_pct = 50
            if s2 and r2 and r2 != s2:
                pos_pct = max(0, min(100, ((curr - s2) / (r2 - s2)) * 100))

            results.append({
                "Symbol": sym, "Price": round(curr, 2), "Score": score,
                "S1": round(ind.get("Pivot.M.Classic.S1"), 2), 
                "P": round(ind.get("Pivot.M.Classic.Middle"), 2),
                "R1": round(ind.get("Pivot.M.Classic.R1"), 2), 
                "R2": round(r2, 2) if r2 else 0,
                "S2": round(s2, 2) if s2 else 0,
                "PosPct": pos_pct, "Signal": rec, "Type": t_type
            })
        except: continue
        p_bar.progress((i + 1) / len(symbols))
    p_bar.empty()
    return pd.DataFrame(results)

# --- 4. واجهة التحكم والعرض (الأصلي) ---
st.write(f"توقيت التقرير: {now_egypt.strftime('%H:%M')} | {today_key}")

if st.button('🚀 إصدار التقرير الذهبي لليوم'):
    st.session_state.final_report = run_strategic_scan(today_key)

if 'final_report' not in st.session_state:
    st.session_state.final_report = None

data = st.session_state.final_report

if data is not None and not data.empty:
    # --- تصنيف 1: نخبة النخبة ---
    t1 = data[data['Score'] >= 9]
    if not t1.empty:
        st.markdown('<div class="section-header">⚜️ نخبة نخبة الصعود</div>', unsafe_allow_html=True)
        for _, row in t1.iterrows():
            status_text = "الدعم والمقاومة اللحظية"
            if row['Price'] > row['R2']: status_text = "السعر أعلى من المقاومة الثانية"
            
            # استخدام unsafe_allow_html=True لحل مشكلة 1000398890.jpg
            st.markdown(f"""
            <div class="stock-card">
                <div style="display:flex; justify-content:space-between; align-items:center; direction: rtl;">
                    <div><span class="symbol-name">{row['Symbol']}</span> <span class="trade-tag">{row['Type']}</span></div>
                    <span style="color:#d4af37; font-weight:bold;">{row['Signal']}</span>
                </div>
                <div class="price-val" style="text-align: right; margin-top:10px;">{row['Price']} <small style="font-size:12px; color:#444;">EGP</small></div>
                
                <div class="live-indicator-container">
                    <div class="indicator-label">{status_text}</div>
                    <div class="indicator-bar"></div>
                    <div class="blue-marker" style="left: {row['PosPct']}%;"></div>
                </div>

                <div class="levels-grid">
                    <div class="level-item"><span class="label">S1 (دعم)</span><span class="num">{row['S1']}</span></div>
                    <div class="level-item"><span class="label">PIVOT</span><span class="num">{row['P']}</span></div>
                    <div class="level-item"><span class="label">R1 (هدف 1)</span><span class="num">{row['R1']}</span></div>
                    <div class="level-item"><span class="label">R2 (هدف 2)</span><span class="num" style="color:#00ff00;">{row['R2']}</span></div>
                </div>
            </div>""", unsafe_allow_html=True)

    # --- تصنيف 2: النخبة الصاعدة ---
    t2 = data[(data['Score'] >= 6) & (data['Score'] < 9)]
    if not t2.empty:
        st.markdown('<div class="section-header">💎 نخبة الصعود</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for idx, row in t2.reset_index().iterrows():
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="stock-card" style="border-top: 1px solid #d4af37;">
                    <div style="display:flex; justify-content:space-between; direction: rtl;">
                        <div style="font-size:20px; font-weight:900;">{row['Symbol']}</div>
                        <div class="trade-tag" style="font-size:10px;">{row['Type']}</div>
                    </div>
                    <div style="color:#d4af37; font-size:18px; text-align: right; margin-top:5px;">{row['Price']} EGP</div>
                    <div style="font-size:11px; color:#444; margin-top:10px; text-align: center; border-top: 1px solid #111; padding-top:5px;">
                        R1: {row['R1']} | R2: {row['R2']} | S1: {row['S1']}
                    </div>
                </div>""", unsafe_allow_html=True)

st.markdown('<div class="footer-box"><p style="font-weight:bold; color:#d4af37;">WAHBA INTELLIGENCE • INSTITUTIONAL DIVISION</p><p>جميع الحقوق محفوظة 2026</p></div>', unsafe_allow_html=True)
            # --- طوبة مباشر (الحسابات) ---
            s2_val = ind.get("Pivot.M.Classic.S2")
            r2_val = ind.get("Pivot.M.Classic.R2")
            current_price = ind.get("close")
            
            # حساب النسبة المئوية للمؤشر الأزرق
            if s2_val and r2_val and r2_val != s2_val:
                pos_pct = max(0, min(100, ((current_price - s2_val) / (r2_val - s2_val)) * 100))
            else:
                pos_pct = 50

            # --- الجزء اللي هتزوده (كود العرض المصلح) ---
            # لاحظ استخدامنا لـ {{ }} عشان نهرب من مشكلة الـ f-string اللي ظهرت في الصورة
            card_html = f"""
            <div class="stock-card">
                <div style="display:flex; justify-content:space-between; align-items:center; direction: rtl;">
                    <div>
                        <span class="symbol-name">{sym}</span> 
                        <span class="trade-tag">{t_type}</span>
                    </div>
                    <span style="color:#d4af37; font-weight:bold;">{rec}</span>
                </div>
                <div class="price-val" style="text-align: right; margin-top:10px;">
                    {current_price:.2f} <small style="font-size:12px; color:#444;">EGP</small>
                </div>
                
                <div class="live-indicator-container">
                    <div class="indicator-text">الدعم والمقاومة اللحظية</div>
                    <div class="indicator-bar"></div>
                    <div class="blue-marker" style="left: {pos_pct}%;"></div>
                </div>

                <div class="levels-grid">
                    <div class="level-item"><span class="label">S1 (دعم)</span><span class="num">{ind.get("Pivot.M.Classic.S1"):.2f}</span></div>
                    <div class="level-item"><span class="label">PIVOT</span><span class="num">{ind.get("Pivot.M.Classic.Middle"):.2f}</span></div>
                    <div class="level-item"><span class="label">R1 (هدف 1)</span><span class="num">{ind.get("Pivot.M.Classic.R1"):.2f}</span></div>
                    <div class="level-item"><span class="label">R2 (هدف 2)</span><span class="num" style="color:#00ff00;">{r2_val:.2f}</span></div>
                </div>
            </div>
            """
            # دي أهم طوبة: بتعرض الكود كـ HTML حقيقي مش نص
            st.markdown(card_html, unsafe_allow_html=True)
