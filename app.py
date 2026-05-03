import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import time
from datetime import datetime
import pytz

# 1. إعدادات الوقت (إسكندرية) - يتوافق مع الصيفي والشتوي تلقائياً
egypt_tz = pytz.timezone('Africa/Cairo')
now_alex = datetime.now(egypt_tz)
today_key = now_alex.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba EGX | All-Market Terminal", layout="wide")

# 2. التنسيق والتحذير القانوني (الهروب من المسؤولية)
st.markdown(f"""
    <style>
    .main-header {{ text-align: center; padding: 10px; border-bottom: 2px solid #1e1e1e; }}
    .risk-banner {{ background: rgba(255,0,0,0.1); border-right: 5px solid #ff4b4b; padding: 15px; direction: rtl; text-align: right; font-size: 13px; color: #ddd; }}
    .opportunity-card {{ background: #0a0a0a; padding: 15px; border-radius: 10px; border: 1px solid #00ff00; margin-top: 20px; border-right: 5px solid #00ff00; }}
    </style>
    <div class="main-header">
        <h1 style="margin:0;">WAHBA EGX</h1>
        <div style="color: #888; font-size: 12px; letter-spacing: 2px;">INFINITY SCANNER • ALEXANDRIA SYNC</div>
    </div>
    <div class="risk-banner">
        <strong>⚠️ تحذير المخاطر:</strong> تداول الأوراق المالية يحتوي على مخاطر عالية. هذه الأداة تسحب البيانات آلياً من TradingView لغرض التحليل الفني فقط ولا تعتبر نصيحة مالية.
    </div>
""", unsafe_allow_html=True)

# 3. دالة جلب "كل" الأسهم المندرجة في مصر بلا استثناء (Infinity)
@st.cache_data(ttl=86400) # القائمة تتحدث مرة كل 24 ساعة لضمان التقاط الأسهم الجديدة
def get_absolute_all_symbols():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        # طلب "كل" البيانات المتاحة لماركت مصر بدون فلاتر
        payload = {
            "filter": [],
            "options": {"lang": "en"},
            "markets": ["egypt"],
            "symbols": {"query": {"types": []}, "tickers": []},
            "columns": ["name"]
        }
        res = requests.post(url, json=payload, timeout=15).json()
        # سحب الرموز (Tickers) وتصفيتها من التكرار
        all_found = [item['s'].split(':')[1] for item in res['data']]
        return sorted(list(set(all_found)))
    except:
        # في حالة فشل السيرفر، قائمة طوارئ
        return ["COMI", "FWRY", "TMGH", "SWDY", "EFIH"]

# 4. محرك التحليل وحفظ الإغلاق (5 أسهم + ثانية راحة للهروب من البلوك)
@st.cache_data(ttl=43200)
def run_infinity_scan(date_key):
    symbols = get_absolute_all_symbols()
    results = []
    
    total_market = len(symbols)
    progress_bar = st.progress(0)
    status_msg = st.empty()
    
    for i, symbol in enumerate(symbols):
        try:
            status_msg.markdown(f"🔍 فحص السهم `{symbol}` ({i+1} من {total_market})")
            
            handler = TA_Handler(
                symbol=symbol, 
                screener="egypt", 
                exchange="EGX",
                interval=Interval.INTERVAL_1_DAY, 
                timeout=5
            )
            analysis = handler.get_analysis()
            rec = analysis.summary["RECOMMENDATION"]
            
            if "BUY" in rec:
                results.append({
                    "السهم": symbol,
                    "إغلاق": round(analysis.indicators["close"], 2),
                    "RSI": round(analysis.indicators["RSI"], 2),
                    "الإشارة": rec.replace("_", " "),
                    "قوة الشراء": analysis.summary["BUY"]
                })
            
            # --- نظام الحماية (5 أسهم ثم ثانية راحة) ---
            if (i + 1) % 5 == 0:
                time.sleep(1.0)
            
            progress_bar.progress((i + 1) / total_market)
        except:
            continue
            
    status_msg.empty()
    progress_bar.empty()
    return results

# 5. العرض والتحكم
st.write(f"📅 **تاريخ الجلسة:** {today_key} | 🕒 **توقيت الإسكندرية:** {now_alex.strftime('%I:%M %p')}")

if st.button('🚀 تشغيل مسح السوق بالكامل (بما فيها الأسهم الجديدة)', use_container_width=True):
    # جلب القائمة أولاً لإظهار العدد للمستخدم
    all_symbols = get_absolute_all_symbols()
    st.info(f"📊 تم العثور على {len(all_symbols)} ورقة مالية مندرجة في البورصة المصرية حالياً.")
    
    with st.spinner("جاري تحليل الإغلاق وحفظ البيانات..."):
        report = run_infinity_scan(today_key)
        
        if report:
            df = pd.DataFrame(report)
            
            # قسم أفضل فرص الصعود
            st.markdown("<div class='opportunity-card'><h3 style='margin:0; color:#00ff00;'>🚀 أفضل فرص الصعود المكتشفة</h3></div>", unsafe_allow_html=True)
            top_picks = df[(df['الإشارة'] == "STRONG BUY") & (df['RSI'] < 65)].sort_values(by="قوة الشراء", ascending=False).head(5)
            if not top_picks.empty:
                st.table(top_picks[['السهم', 'إغلاق', 'RSI', 'الإشارة']])
            
            # جدول كافة الأسهم الإيجابية
            st.divider()
            st.markdown(f"### 📊 كافة فرص الشراء المتاحة ({len(df)} سهم)")
            st.table(df[['السهم', 'إغلاق', 'RSI', 'الإشارة']].sort_values(by="الإشارة", ascending=False))
        else:
            st.info("لم يتم العثور على إشارات شراء قوية في إغلاق اليوم.")

# 6. التذييل
st.divider()
st.caption("WAHBA EGX | Universal v7.0 | Alexandria Time Sync")
