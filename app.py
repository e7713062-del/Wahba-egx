import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import google.generativeai as genai
from datetime import datetime
import os

# ==========================================
# 1. إعدادات الـ AI (Gemini 1.5 Flash - Speed Optimized)
# ==========================================
API_KEY = "YOUR_API_KEY_HERE" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_batch_ai_analysis(stocks_list):
    """تحليل كل الأسهم في طلب واحد لسرعة البرق"""
    if not stocks_list:
        return {}

    # بناء نص واحد يحتوي على بيانات كل الأسهم
    stocks_data_text = "\n".join([
        f"- {s['sym']}: السعر {s['price']}, RSI {s['rsi']:.1f}, فوق SMA20 و SMA50."
        for s in stocks_list
    ])

    prompt = f"""
    بصفتك خبير وول ستريت، حلل الأسهم التالية من البورصة المصرية بإيجاز شديد (نقطة دخول، هدف، وقف):
    {stocks_data_text}
    
    رد بصيغة:
    SYMBOL: التحليل باختصار.
    """
    
    try:
        response = model.generate_content(prompt)
        # تحويل الرد لقاموس لسهولة العرض
        lines = response.text.strip().split('\n')
        analysis_dict = {}
        for line in lines:
            if ':' in line:
                sym, report = line.split(':', 1)
                analysis_dict[sym.strip().replace('$','')] = report.strip()
        return analysis_dict
    except:
        return {s['sym']: "⚠️ فشل التحليل السريع، راجع الشارت." for s in stocks_list}

# ==========================================
# 2. الواجهة (Minimalist Wall Street)
# ==========================================
st.set_page_config(page_title="Wahba Ultra Fast Scanner", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono&family=Tajawal:wght@700;900&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #050505; color: #fff; font-family: 'Tajawal', sans-serif;
    }
    .stButton>button {
        background: #d4af37 !important; color: #000 !important; font-weight: 900 !important; font-size: 20px;
    }
    .stock-card {
        background: #0e0e0e; border: 1px solid #1a1a1a; padding: 20px; border-radius: 4px; margin-bottom: 15px;
    }
    .ai-flash { color: #00ff41; font-family: 'Roboto Mono', monospace; font-size: 15px; border-left: 2px solid #00ff41; padding-left: 10px; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align:center; color:#d4af37;">ULTRA FAST | WALL STREET SCANNER</h1>', unsafe_allow_html=True)

# ==========================================
# 3. محرك المسح السريع
# ==========================================
def fetch_all_tickers():
    url = "https://scanner.tradingview.com/egypt/scan"
    try:
        res = requests.post(url, json={"markets": ["egypt"], "columns": ["name"]}, timeout=10)
        return [item['s'].split(':')[1] for item in res.json()['data']]
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK"]

CACHE_FILE = "fast_wallstreet_results.csv"

if st.button("⚡ START FLASH SCAN"):
    tickers = fetch_all_tickers()
    qualified = []
    
    progress = st.progress(0)
    status = st.empty()
    
    # الفحص الفني (سريع جداً)
    for i, sym in enumerate(tickers):
        if i % 20 == 0: status.write(f"Scanning: `{sym}`")
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=5)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            
            if (ind.get("close") > ind.get("SMA20")) and (ind.get("RSI") > 55) and ("BUY" in analysis.summary["RECOMMENDATION"]):
                qualified.append({
                    "sym": sym, "price": ind.get("close"), "rsi": ind.get("RSI"),
                    "sma20": ind.get("SMA20"), "s1": ind.get("Pivot.M.Classic.S1")
                })
        except: continue
        progress.progress((i + 1) / len(tickers))

    # تحليل الـ AI (بسرعة البرق في طلب واحد)
    if qualified:
        status.write("🧠 AI Flash Analysis in progress...")
        ai_reports = get_batch_ai_analysis(qualified)
        
        for s in qualified:
            s['report'] = ai_reports.get(s['sym'], "⚠️ مراجعة يدوية")
            
        df = pd.DataFrame(qualified)
        df['date'] = datetime.now().strftime("%Y-%m-%d")
        df.to_csv(CACHE_FILE, index=False, encoding='utf-8-sig')
        st.rerun()
    else:
        st.warning("No High-Probability setups found.")

# ==========================================
# 4. العرض
# ==========================================
if os.path.exists(CACHE_FILE):
    df = pd.read_csv(CACHE_FILE)
    if not df.empty and str(df['date'].iloc[0]) == datetime.now().strftime("%Y-%m-%d"):
        for _, s in df.iterrows():
            st.markdown(f"""
            <div class="stock-card">
                <div style="display:flex; justify-content:space-between;">
                    <b style="font-size:25px; color:#d4af37;">$ {s['sym']}</b>
                    <b style="font-size:20px;">{s['price']:.2f} EGP</b>
                </div>
                <div class="ai-flash">
                    {s['report']}
                </div>
            </div>
            """, unsafe_allow_html=True)
