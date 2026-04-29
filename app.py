import streamlit as st
from tradingview_ta import TA_Handler, Interval
import time

st.set_page_config(page_title="Wahba Pro | SMA 50", layout="wide")

st.title("🛡️ Wahba Pro: رادار المتوسطات المتحركة")
st.write("الفحص الآن يعتمد فقط على اختراق السعر لمتوسط 50 يوم (SMA50)")

STOCKS = [
    "COMI", "FWRY", "TMGH", "SWDY", "EFIH", "ABUK", "EGAL", "PHDC", 
    "HRHO", "ESRS", "ORWE", "SKPC", "BTEL", "EGCH", "AMOC", "MFOT", 
    "HELI", "ORAS", "EKHO", "JUFO", "CANA", "ESGI", "GBCO", "CCAP",
    "AUTO", "MNHD", "PORT", "TALA", "ETEL", "ISPH", "RMDA", "CIRA"
]

if st.button('إبدأ فحص اختراق متوسط 50'):
    bullish_stocks = []
    progress_bar = st.progress(0)
    
    for idx, sym in enumerate(STOCKS):
        try:
            progress_bar.progress((idx + 1) / len(STOCKS))
            
            handler = TA_Handler(
                symbol=sym,
                screener="egypt",
                exchange="EGX",
                interval=Interval.INTERVAL_1_DAY,
                timeout=10
            )
            
            analysis = handler.get_analysis()
            
            # هنا بنسحب سعر الإغلاق الحالي وقيمة المتوسط 50
            current_price = analysis.indicators["close"]
            sma50 = analysis.indicators["SMA50"]
            
            # الشرط: السعر الحالي أكبر من متوسط 50 (اتجاه صاعد)
            if current_price > sma50:
                bullish_stocks.append({
                    "symbol": sym, 
                    "price": current_price, 
                    "sma50": sma50
                })
            
            time.sleep(0.1)
        except:
            continue

    if bullish_stocks:
        st.success(f"لقينا {len(bullish_stocks)} سهم فوق متوسط 50 يوم")
        cols = st.columns(4)
        for idx, s in enumerate(bullish_stocks):
            with cols[idx % 4]:
                st.info(f"🟢 **{s['symbol']}**")
                st.write(f"السعر: {s['price']:.2f}")
                st.caption(f"SMA50: {s['sma50']:.2f}")
    else:
        st.warning("مفيش أسهم فوق المتوسط حالياً.")
