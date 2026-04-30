import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval
import pandas as pd

# 1. إعدادات الصفحة الاحترافية
st.set_page_config(
    page_title="Wahba EGX | Terminal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. تصميم الواجهة واللوجو الهندسي (CSS + HTML) - مستوحى من صورة WAHBA PRO
st.markdown("""
    <style>
    /* تصميم الواجهة الجاد */
    .stApp {
        background-color: #ffffff;
    }
    
    /* تصميم اللوجو البرمجي الاحترافي */
    .terminal-header {
        background-color: #fcfcfc;
        padding: 40px;
        border-radius: 4px;
        text-align: center;
        margin-bottom: 30px;
        border: 1px solid #eee;
    }
    
    /* أيقونة اللوجو الهندسي (الدرع والسهم) */
    .wahba-shield-icon {
        display: inline-block;
        width: 100px;
        height: 100px;
        position: relative;
        margin-bottom: 15px;
    }
    
    /* الدرع الهيكلي (استخدام CSS لرسم مضلع) */
    .shield-body {
        position: absolute;
        top: 0; left: 0;
        width: 100px;
        height: 100px;
        background-color: transparent;
        border: 5px solid #0052ff;
        border-bottom-left-radius: 10px;
        border-bottom-right-radius: 10px;
        clip-path: polygon(50% 0%, 100% 15%, 90% 100%, 10% 100%, 0% 15%);
        opacity: 0.2; /* خفيف ليعطي انطباع مائي */
    }
    
    /* حرف W الهندسي الداخلي */
    .internal-w {
        position: absolute;
        bottom: 25px;
        left: 30px;
        width: 40px;
        height: 3px;
        background-color: #0052ff;
        transform: rotate(45deg);
    }
    .internal-w::after {
        content: '';
        position: absolute;
        bottom: 0px;
        left: 0px;
        width: 40px;
        height: 3px;
        background-color: #0052ff;
        transform: rotate(90deg);
    }
    
    /* السهم الصاعد المدمج */
    .up-arrow {
        position: absolute;
        top: 15px;
        right: 15px;
        width: 40px;
        height: 4px;
        background-color: #0052ff;
        transform: rotate(-45deg);
    }
    .up-arrow::after {
        content: '';
        position: absolute;
        top: -8px;
        right: -8px;
        border-left: 10px solid transparent;
        border-right: 10px solid transparent;
        border-bottom: 20px solid #0052ff;
    }

    /* نص الشعار (Wahba EGX) - أسود بالكامل */
    .main-title {
        font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
        font-size: 50px;
        font-weight: 800;
        color: #1a1a1a; /* أسود تماماً */
        margin: 0;
        letter-spacing: -2px;
        text-transform: uppercase;
    }
    
    /* الشعار الفرعي الاحترافي (بدون "Pro") */
    .sub-title {
        color: #888888;
        font-size: 14px;
        letter-spacing: 5px;
        margin-top: 10px;
        text-transform: uppercase;
        font-weight: 500;
    }
    
    /* تعديل شكل الأزرار */
    .stButton>button {
        background-color: #1a1a1a;
        color: white;
        border-radius: 4px;
        font-weight: bold;
        height: 3.8em;
        border: none;
        width: 100%;
        transition: background 0.2s;
    }
    .stButton>button:hover {
        background-color: #0052ff;
        color: white;
    }
    </style>
    
    <div class="terminal-header">
        <div class="wahba-shield-icon">
            <div class="shield-body"></div>
            <div class="internal-w"></div>
            <div class="up-arrow"></div>
        </div>
        <div class="main-title">Wahba EGX</div>
        <div class="sub-title">Algorithmic Market Terminal</div>
    </div>
    """, unsafe_allow_html=True)

# 3. قائمة الأسهم الكاملة والمحدثة للبورصة المصرية
STOCKS = [
    "COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "EGAL", "PHDC", "HRHO", "ESRS",
    "ORWE", "SKPC", "BTEL", "EGCH", "AMOC", "MFOT", "HELI", "ORAS", "EKHO", "JUFO",
    "CANA", "ESGI", "GBCO", "CCAP", "AUTO", "MNHD", "PORT", "TALA", "ETEL", "ISPH",
    "RMDA", "CIRA", "ELSH", "OIH", "EMFD", "MTIE", "DSCW", "EHDR", "ASPI", "ADIB",
    "ACTF", "KRDI", "ATLC", "ALCN", "AFMC", "AMER", "ARAB", "AMIA", "AIDC", "AIHC",
    "ARCC", "ASCM", "BTFH", "COSG", "POUL", "CSAG", "PRCL", "CNFN", "CIEB", "DAPH",
    "EAST", "EFID", "EGTS", "PHAR", "MPRC", "ETRS", "AFDI", "ECAP", "KABO", "OBRI",
    "RAYA", "MCQE", "ORHD", "UNIT", "MBSC", "MPCI", "ZMID", "SPMD", "BINV",
    "MOIL", "AALR", "WKOL", "EALR", "CPME", "IFAP", "SMPP", "ELWA", "GPPL",
    "ALUM", "BIOC", "EDBM", "MICH", "DCRC", "ODIN", "ICMI", "RACC", "REAC"
]

def analyze_security(symbol):
    try:
        # إعداد الاتصال بالبيانات
        handler = TA_Handler(
            symbol=symbol,
            screener="egypt",
            exchange="EGX",
            interval=Interval.INTERVAL_1_DAY,
            timeout=12
        )
        data = handler.get_analysis()
        ind = data.indicators
        signal = data.summary["RECOMMENDATION"]
        
        # استراتيجية الفحص (منطق "Wahba EGX")
        if ind["close"] > ind["SMA10"] and ind["RSI"] > 40 and "BUY" in signal:
            return {
                "Ticker": symbol,
                "Last Price": round(ind["close"], 2),
                "RSI (14)": round(ind["RSI"], 2),
                "SMA (10)": round(ind["SMA10"], 2),
                "Signal Strength": signal.replace("_", " ")
            }
    except:
        return None

# 4. واجهة التشغيل والنتائج
st.divider()
st.write("Quantitative Parameters: Close > SMA(10) | RSI(14) > 40")

# زر البدء الاحترافي
if st.button('INITIATE COMPREHENSIVE MARKET SCAN'):
    with st.spinner('Accessing EGX Market Feed...'):
        with ThreadPoolExecutor(max_workers=30) as executor:
            raw_res = list(executor.map(analyze_security, STOCKS))
        
        # تصفية النتائج
        filtered_results = [r for r in raw_res if r is not None]
        
        if filtered_results:
            st.success(f"Scanning Protocol Complete: {len(filtered_results)} bullish assets identified.")
            
            # عرض البيانات في جدول احترافي
            df = pd.DataFrame(filtered_results)
            st.dataframe(
                df.sort_values(by="RSI (14)", ascending=False),
                use_container_width=True,
                hide_index=True
            )
            
            # ملخص سريع تفاعلي
            st.markdown("---")
            st.subheader("Performance Summary Matrix")
            metrics_cols = st.columns(5)
            for idx, item in enumerate(filtered_results):
                with metrics_cols[idx % 5]:
                    st.metric(
                        label=item["Ticker"],
                        value=f"{item['Last Price']} EGP",
                        delta=f"RSI {item['RSI (14)']}",
                        delta_color="normal"
                    )
        else:
            st.warning("Analysis finished. No securities currently meet the quantitative protocol.")

# 5. تذييل الصفحة الرسمي
st.divider()
st.caption("WAHBA EGX TERMINAL | INSTUTIONAL-GRADE ANALYSIS | © 2026 GLOBAL MARKETS")
