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

# --- 2. التصميم المؤسسي (CSS Custom Styling) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    
    * { font-family: 'Tajawal', sans-serif; }
    .stApp { background-color: #000000; color: #ffffff; }
    
    /* الهيدر */
    .nav-bar { text-align: center; padding: 30px; background: #000; border-bottom: 2px solid #d4af37; margin-bottom: 20px; }
    .logo-text { font-size: 35px; font-weight: 900; color: #fff; letter-spacing: 2px; }
    .logo-text span { color: #d4af37; }
    
    /* التصنيفات */
    .section-header { color: #d4af37; border-right: 5px solid #d4af37; padding-right: 15px; margin: 40px 0 20px 0; font-size: 24px; font-weight: bold; text-align: right; }
    
    /* كروت الأسهم الذهبية */
    .stock-card { background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 15px; padding: 25px; margin-bottom: 20px; border-top: 3px solid #d4af37; transition: 0.3s; }
    .stock-card:hover { border-color: #d4af37; background: #111; }
    .symbol-name { font-size: 28px; font-weight: 900; color: #d4af37; }
    .price-val { font-size: 24px; font-weight: bold; color: #fff; }
    
    /* مستويات الدعم والمقاومة */
    .levels-grid { display: flex; justify-content: space-between; margin-top: 20px; background: #000; padding: 10px; border-radius: 8px; border: 1px solid #111; direction: ltr; }
    .level-item { text-align: center; flex: 1; }
    .label { font-size: 10px; color: #777; display: block; text-transform: uppercase; }
    .num { font-size: 14px; font-weight: bold; color: #d4af37; font-family: monospace; }
    
    /* زر التشغيل */
    .stButton>button { background: #d4af37 !important; color: #000 !important; font-weight: 900 !important; border-radius: 10px !important; height: 60px !important; width: 100% !important; border: none !important; font-size: 18px !important; }
    
    /* التذييل */
    .footer-box { margin-top: 80px; padding: 40px; text-align: center; border-top: 1px solid #1a1a1a; color: #444; font-size: 12px; }
</style>

<div class="nav-bar">
    <div class="logo-text">WAHBA <span>INTELLIGENCE</span></div>
    <p style="color:#666; font-size:12px; letter-spacing: 3px;">INSTITUTIONAL GRADE TERMINAL</p>
</div>
""", unsafe_allow_html=True)

# --- 3. محرك البيانات (Data Engine) ---
@st.cache_data(ttl=86400)
def fetch_egx_list(date_key):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "ETEL", "ORAS"]

@st.cache_data(ttl=3600, show_spinner=False) # تقليل الكاش لساعة واحدة لضمان دقة السعر
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
            
            # فلتر RSI (القوة النسبية)
            rsi = ind.get("RSI")
            if rsi and 45 <= rsi <= 65: score += 3 # منطقة تجميع مثالية
            
            # فلتر المتوسطات المتحركة (Pivot)
            close = ind.get("close")
            pivot = ind.get("Pivot.M.Classic.Middle")
            if close and pivot and close > pivot: score += 2
            
            results.append({
                "Symbol": sym,
                "Price": round(close, 2) if close else 0,
                "Score": score,
                "S1": round(ind.get("Pivot.M.Classic.S1"), 2) if ind.get("Pivot.M.Classic.S1") else 0,
                "P": round(pivot, 2) if pivot else 0,
                "R1": round(ind.get("Pivot.M.Classic.R1"), 2) if ind.get("Pivot.M.Classic.R1") else 0,
                "Signal": rec.replace("_", " ")
            })
        except:
            continue
        p_bar.progress((i + 1) / len(symbols))
    
    p_bar.empty()
    return pd.DataFrame(results)

# --- 4. واجهة التحكم والعرض ---
col_info1, col_info2 = st.columns([1, 1])
with col_info1:
    st.write(f"📅 التاريخ: **{today_key}**")
with col_info2:
    st.write(f"⏰ توقيت القاهرة: **{now_egypt.strftime('%H:%M')}**")

if st.button('🚀 إرسال المسح الاستراتيجي وإصدار التقرير الذهبي'):
    st.session_state.final_report = run_strategic_scan(today_key)

if 'final_report' not in st.session_state:
    st.session_state.final_report = None

data = st.session_state.final_report

if data is not None and not data.empty:
    # تصنيف 1: نخبة النخبة (Score >= 8)
    t1 = data[data['Score'] >= 8].sort_values(by="Score", ascending=False)
    if not t1.empty:
        st.markdown('<div class="section-header">🏆 نخبة النخبة (فرص ذهبية)</div>', unsafe_allow_html=True)
        for _, row in t1.iterrows():
            st.markdown(f"""
            <div class="stock-card">
                <div style="display:flex; justify-content:space-between; align-items:center; direction: rtl;">
                    <span class="symbol-name">{row['Symbol']}</span>
                    <span style="color:#d4af37; font-weight:bold; background: #1a1a1a; padding: 5px 15px; border-radius: 20px; font-size: 14px;">{row['Signal']}</span>
                </div>
                <div class="price-val" style="text-align: right; margin: 10px 0;">{row['Price']} <small style="font-size:12px; color:#666;">EGP</small></div>
                <div class="levels-grid">
                    <div class="level-item"><span class="label">S1 (دعم)</span><span class="num">{row['S1']}</span></div>
                    <div class="level-item"><span class="label">PIVOT (ارتكاز)</span><span class="num">{row['P']}</span></div>
                    <div class="level-item"><span class="label">R1 (مقاومة)</span><span class="num">{row['R1']}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # تصنيف 2: الأسهم الواعدة (Score 5-7)
    t2 = data[(data['Score'] >= 5) & (data['Score'] < 8)]
    if not t2.empty:
        st.markdown('<div class="section-header">💎 الأسهم الصاعدة والواعدة</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for idx, row in t2.reset_index().iterrows():
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="stock-card" style="border-top: 1px solid #d4af37; padding: 15px;">
                    <div style="display:flex; justify-content:space-between; direction: rtl;">
                        <div style="font-size:20px; font-weight:900;">{row['Symbol']}</div>
                        <div style="color:#d4af37; font-size:18px; font-weight:bold;">{row['Price']} <span style="font-size:10px;">EGP</span></div>
                    </div>
                    <div style="font-size:12px; color:#666; margin-top:10px; direction: ltr; text-align: center;">
                        R1: {row['R1']} | Pivot: {row['P']} | S1: {row['S1']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --- 5. التذييل الفاخر ---
st.markdown("""
<div class="footer-box">
    <p style="font-weight:bold; color:#d4af37; letter-spacing: 2px;">WAHBA INTELLIGENCE • ASSET MANAGEMENT DIVISION</p>
    <p>هذا التقرير تم إنشاؤه آلياً بناءً على مؤشرات فنية من TradingView. القرار الاستثماري مسؤوليتك الكاملة.</p>
    <p>© 2026 جميع الحقوق محفوظة لذكاء وهبة</p>
</div>
""", unsafe_allow_html=True)
