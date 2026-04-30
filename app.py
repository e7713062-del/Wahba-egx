import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from tradingview_ta import TA_Handler, Interval
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="Wahba Pro | Full Market", layout="wide")

st.title("🛡️ رادار Wahba Pro - المسح الشامل للبورصة المصرية")
st.write("يتم الآن فحص أكثر من 100 سهم من السوق المصري بناءً على التحليل الفني اللحظي.")

# القائمة الموسعة للأسهم (EGX 100 + الأكثر نشاطاً)
STOCKS = [
    "COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "EGAL", "PHDC", "HRHO", "ESRS",
    "ORWE", "SKPC", "BTEL", "EGCH", "AMOC", "MFOT", "HELI", "ORAS", "EKHO", "JUFO",
    "CANA", "ESGI", "GBCO", "CCAP", "AUTO", "MNHD", "PORT", "TALA", "ETEL", "ISPH",
    "RMDA", "CIRA", "ELSH", "OIH", "EMFD", "MTIE", "DSCW", "EHDR", "ASPI", "ADIB",
    "ACTF", "KRDI", "ATLC", "ALCN", "AFMC", "AMER", "ARAB", "AMIA", "AIDC", "AIHC",
    "ARCC", "ASCM", "BTFH", "COSG", "POUL", "CSAG", "PRCL", "CNFN", "CIEB", "DAPH",
    "EAST", "EFID", "EGTS", "PHAR", "MPRC", "ETRS", "AFDI", "ECAP", "KABO", "OBRI",
    "RAYA", "MCQE", "ORHD", "EGTS", "UNIT", "MBSC", "MPCI", "ZMID", "SPMD", "BINV",
    "MOIL", "AALR", "WKOL", "EALR", "CPME", "IFAP", "SMPP", "AMIA", "ELWA", "GPPL",
    "ALUM", "BIOC", "EDBM", "MICH", "DCRC", "ODIN", "ICMI", "RACC", "BINV", "REAC"
]

def check_stock(symbol):
    try:
        handler = TA_Handler(
            symbol=symbol,
            screener="egypt",
            exchange="EGX",
            interval=Interval.INTERVAL_1_DAY,
            timeout=10
        )
        analysis = handler.get_analysis()
        d = analysis.indicators
        rec = analysis.summary["RECOMMENDATION"]
        
        # الفلتر الحساس الخاص بك
        if d["close"] > d["SMA10"] and d["RSI"] > 40 and "BUY" in rec:
            return {
                "السهم": symbol,
                "السعر": round(d["close"], 2),
                "RSI": round(d["RSI"], 2),
                "قوة الإشارة": rec.replace("_", " ")
            }
    except:
        return None

if st.button('🚀 إبدأ الفحص الشامل (100+ سهم)'):
    with st.spinner('جاري تحليل كافة أسهم السوق المصري...'):
        # رفعنا max_workers لسرعة الفحص
        with ThreadPoolExecutor(max_workers=30) as executor:
            results = list(executor.map(check_stock, STOCKS))
        
        final_list = [res for res in results if res is not None]
        
        if final_list:
            st.success(f"✅ تم رصد {len(final_list)} سهم في منطقة شراء")
            df = pd.DataFrame(final_list)
            st.dataframe(df, use_container_width=True)
            
            st.divider()
            st.subheader("💡 ملخص الفرص المتاحة:")
            cols = st.columns(5)
            for i, item in enumerate(final_list):
                with cols[i % 5]:
                    st.metric(label=item["السهم"], value=item["السعر"], delta=item["RSI"])
        else:
            st.warning("لا توجد فرص مطابقة للشروط حالياً في السوق بالكامل.")

st.divider()
st.caption("Wahba Pro Terminal © 2026 - البيانات مستمدة من TradingView")
