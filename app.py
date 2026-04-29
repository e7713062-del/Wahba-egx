import streamlit as st
import yfinance as yf
import pandas as pd

# 1. إعدادات الصفحة
st.set_page_config(page_title="Wahba Trading Pro", layout="wide")

# 2. تصميم CSS احترافي (ستايل TradingView)
st.markdown("""
    <style>
    .stApp { background-color: #131722; color: #d1d4dc; }
    .header-style { 
        text-align: center; padding: 15px; 
        background: #1e222d; border-bottom: 2px solid #2962ff;
        margin-bottom: 20px; color: #ffffff;
    }
    .ad-banner { 
        background: #1e222d; border: 1px dashed #2962ff; 
        padding: 10px; text-align: center; margin-bottom: 20px;
        color: #888; font-size: 0.9em;
    }
    .buy-signal { color: #00ff88; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 3. العنوان والمساحة الإعلانية
st.markdown("<div class='header-style'><h1>📈 Wahba EGX - Swing Trading Scanner</h1></div>", unsafe_allow_html=True)
st.markdown("<div class='ad-banner'>📢 مساحة إعلانية - للإعلان تواصل معنا عبر تليجرام/إيميل</div>", unsafe_allow_html=True)

# 4. قائمة الأسهم
tickers = [
    "ABUK", "ACGC", "ADCI", "ADIB", "AFMC", "AIH", "AIVC", "AMER", "AMOC", "ANFI", "APME", 
    "ARAB", "ASPI", "ASRE", "ASU", "ATLC", "ATWB", "AUCC", "AXPH", "BINP", "BINV", "BIOC", 
    "BLGN", "BMOH", "BTFH", "CAED", "CAFR", "CAPW", "CCAP", "CERA", "CFGH", "CHWP", "CICH", 
    "CIRA", "CLHO", "CNCR", "CNFR", "COMI", "COPR", "CSAG", "CVLC", "DAPH", "DCRC", "DCTL", 
    "DOMT", "EALR", "EATM", "EBSC", "ECAP", "ECHG", "ECOS", "EDAB", "EDIN", "EFID", "EGAS", 
    "EGBE", "EGCH", "EGDC", "EGDH", "EGFI", "EGID", "EGLI", "EGSG", "EGTB", "EHDR", "EIMC", 
    "EIPC", "EKHO", "ELKA", "ELSH", "EMFD", "ENGC", "EPCO", "ESIC", "ESRS", "ETEL", "EXPA", 
    "FAHL", "FAIT", "FCIE", "FIIT", "FWRY", "GTHE", "GZCC", "HELI", "HERO", "HRHO", "IFAP", 
    "IHCX", "INFI", "IRGC", "ISDI", "ISPH", "JUFO", "KABO", "KIMA", "LREI", "MACRO", "MASR", 
    "MDWA", "MEPA", "MFPC", "MNHD", "MPCO", "MTIE", "OBET", "ODPD", "ODIN", "OIH", "OPAT", 
    "ORAS", "ORHD", "ORWE", "PHDC", "PIOH", "PRDC", "PSDC", "QNBA", "RAFT", "RMDA", "RTVC", 
    "SAEI", "SCFM", "SEMO", "SHAC", "SIAG", "SKPC", "SPHT", "SVCP", "SWDY", "SYVI", "TAQA", 
    "TMGH", "TRGO", "UEGC", "UNTR", "UPLD", "UTOP", "VIRA", "ZEIRA"
]
tickers_ca = [f"{t}.CA" for t in tickers]

# 5. زر المسح
if st.button("🚀 تصفية الفرص القوية (سويـنج)"):
    opportunities = []
    with st.spinner('جاري فحص إغلاقات السوق...'):
        for ticker in tickers_ca:
            try:
                # الاعتماد على إغلاق اليوم (Daily Close)
                df = yf.download(ticker, period="6mo", interval="1d", progress=False)
                if len(df) >= 50:
                    df['MA20'] = df['Close'].rolling(window=20).mean()
                    df['MA50'] = df['Close'].rolling(window=50).mean()
                    
                    # شرط السوينج: إغلاق فوق المتوسطات
                    if df['Close'].iloc[-1] > df['MA50'].iloc[-1] and df['MA20'].iloc[-1] > df['MA50'].iloc[-1]:
                        opportunities.append({
                            "السهم": ticker.replace(".CA", ""),
                            "الاتجاه": "صاعد",
                            "الإشارة": "✅ شراء (قوية)"
                        })
            except: continue
    
    # 6. عرض النتائج
    if opportunities:
        results_df = pd.DataFrame(opportunities)
        st.table(results_df)
    else:
        st.warning("لا توجد فرص شراء قوية بناءً على إغلاق اليوم، السوق في مرحلة تجميع.")
