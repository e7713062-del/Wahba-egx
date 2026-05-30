import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime
import pytz
import os

# --- 1. إعدادات الوقت والهوية ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Intelligence", layout="wide", initial_sidebar_state="collapsed")

# =========================================================================
# 🔐 بوابه الأمان ونظام الاشتراكات التلقائي (30 يوم) - مضاف في البداية لحماية كودك 🔐
# =========================================================================
USER_DB_FILE = "users_db.csv"

def load_users():
    if os.path.exists(USER_DB_FILE):
        try:
            df = pd.read_csv(USER_DB_FILE)
            return df.to_dict(orient="records")
        except:
            pass
    # 📝 هنا تم تعديل الباسورد الافتراضي الجديد لحساباتك
    return [
        {"username": "admin", "password": "012700", "role": "admin", "status": "active", "start_date": today_key},
        {"username": "مصطفى تامر", "password": "012700", "role": "user", "status": "active", "start_date": today_key}
    ]

def save_users(users_list):
    pd.DataFrame(users_list).to_csv(USER_DB_FILE, index=False)

if 'users' not in st.session_state:
    st.session_state.users = load_users()

# فحص الـ 30 يوم التلقائي - تم استخدام .get لمنع KeyError نهائياً إذا كانت الداتا قديمة
for u in st.session_state.users:
    if u.get('role', 'user') != 'admin' and u.get('status', 'pending') == 'active':
        try:
            start_dt = datetime.strptime(u.get('start_date', today_key), "%Y-%m-%d")
            days_passed = (datetime.now().date() - start_dt.date()).days
            if days_passed >= 30:
                u['status'] = 'expired'
        except:
            pass
save_users(st.session_state.users)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# واجهة الدخول الفخمة للماركتينج
if not st.session_state.logged_in:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    .stApp { background-color: #000000; color: #ffffff; }
    .marketing-login-box { max-width: 450px; margin: 60px auto 10px auto; padding: 35px; background: #0a0a0a; border: 1px solid #1a1a1a; border-top: 4px solid #d4af37; border-radius: 15px; text-align: center; box-shadow: 0px 10px 30px rgba(212, 175, 55, 0.05); }
    .m-logo { font-size: 32px; font-weight: 900; color: #fff; letter-spacing: 2px; margin-bottom: 5px; }
    .m-logo span { color: #d4af37; }
    .m-subtitle { color: #666; font-size: 12px; margin-bottom: 25px; letter-spacing: 1px; }
    .stButton>button { background: #d4af37 !important; color: #000 !important; font-weight: 900 !important; border-radius: 10px !important; height: 45px !important; width: 100% !important; border: none !important; transition: 0.3s; }
    .stButton>button:hover { background: #fff !important; transform: scale(1.02); }
    </style>
    <div class="marketing-login-box">
        <div class="m-logo">WAHBA <span>INTELLIGENCE</span></div>
        <div class="m-subtitle">PREMIUM ALGORITHMIC TRADING TERMINAL</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐 تسجيل دخول المشتركين", "✨ طلب اشتراك جديد"])
    with tab1:
        u_clean = st.text_input("اسم المستخدم", placeholder="أدخل اسم الحساب", key="login_user").strip()
        p_clean = st.text_input("كلمة المرور", type="password", placeholder="••••••", key="login_pass").strip()
        # استبدل الجزء الخاص بالدخول في الكود بـ:

if st.button("دخول المنصة 🚀"):
    user_found = next((u for u in st.session_state.users if u.get('username') == u_clean and str(u.get('password')) == p_clean), None)
    if user_found:
        if user_found.get('status') == 'active':
            # تنظيف أي بيانات دخول قديمة قبل تعيين الجديدة
            st.session_state.logged_in = True
            st.session_state.current_user = user_found.get('username')
            st.session_state.user_role = user_found.get('role')
            st.rerun() # تحديث الصفحة فوراً بعد تسجيل الدخول
        else:
            st.error("❌ حسابك غير نشط.")
    else:
        st.error("❌ بيانات الدخول غير صحيحة.")

                st.error("❌ بيانات الدخول خاطئة.")
    with tab2:
        new_user = st.text_input("اختر اسم مستخدم", placeholder="الاسم ثلاثي", key="reg_user").strip()
        new_pass = st.text_input("اختر كلمة مرور", type="password", placeholder="••••••", key="reg_pass").strip()
        if st.button("إرسال طلب التفعيل 📨", key="reg_btn"):
            if new_user and new_pass:
                if any(u for u in st.session_state.users if u.get('username') == new_user):
                    st.error("❌ الاسم موجود بالفعل.")
                else:
                    st.session_state.users.append({"username": new_user, "password": new_pass, "role": "user", "status": "pending", "start_date": today_key})
                    save_users(st.session_state.users)
                    st.success("✅ تم إرسال طلبك! تفضل بتحويل الاشتراك لتفعيل الحساب.")
            else:
                st.error("❌ يرجى ملء الحقول.")
    st.stop()

# لوحة تفعيل وتجديد الاشتراكات للـ Admin بضغطة زر
if st.session_state.user_role == "admin":
    st.markdown("<div style='background:#111; padding:15px; border-radius:10px; border:1px solid #d4af37; margin-bottom:20px;'>", unsafe_allow_html=True)
    st.subheader("💼 لوحة تحكم الإدارة والاشتراكات الشهرية")
    for idx, row in pd.DataFrame(st.session_state.users).iterrows():
        if row.get('username') != 'admin':
            col_u1, col_u2, col_u3 = st.columns([2, 1, 1])
            col_u1.write(f"👤 **المستخدم:** {row.get('username')} | 📅 **بدء الاشتراك:** {row.get('start_date', today_key)}")
            col_u2.write(f"الحالة: {'🟢 نشط' if row.get('status')=='active' else '❌ منتهي' if row.get('status')=='expired' else '🔴 قيد الانتظار'}")
            if row.get('status', 'pending') == 'pending':
                if col_u3.button("✅ قبول وتفعيل", key=f"acc_{idx}"):
                    st.session_state.users[idx]['status'] = 'active'
                    st.session_state.users[idx]['start_date'] = today_key
                    save_users(st.session_state.users)
                    st.rerun()
            elif row.get('status', 'pending') == 'expired':
                if col_u3.button("🔄 تجديد 30 يوم", key=f"ren_{idx}"):
                    st.session_state.users[idx]['status'] = 'active'
                    st.session_state.users[idx]['start_date'] = today_key 
                    save_users(st.session_state.users)
                    st.rerun()
            else:
                if col_u3.button("🚫 إلغاء التفعيل", key=f"susp_{idx}"):
                    st.session_state.users[idx]['status'] = 'pending'
                    save_users(st.session_state.users)
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================================
# ⚜️ كودك الأصلي بالملي وبنفس الترتيب دون تغيير حرف واحد فني ⚜️
# =========================================================================

# --- 2. التصميم المؤسسي المطور (CSS كاملاً بدون حذف) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
* { font-family: 'Tajawal', sans-serif; }
.stApp { background-color: #000000; color: #ffffff; }
.nav-bar { text-align: center; padding: 25px; background: linear-gradient(180deg, #111 0%, #000 100%); border-bottom: 2px solid #d4af37; margin-bottom: 30px; }
.logo-text { font-size: 35px; font-weight: 900; color: #fff; letter-spacing: 2px; }
.logo-text span { color: #d4af37; }
.section-header { color: #d4af37; border-right: 5px solid #d4af37; padding-right: 15px; margin: 40px 0 20px 0; font-size: 24px; font-weight: bold; text-align: right; background: rgba(212, 175, 55, 0.05); padding: 10px; }
.stock-card { background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 15px; padding: 25px; margin-bottom: 10px; border-top: 3px solid #d4af37; transition: 0.3s; }
.stock-card:hover { border-color: #fff; background: #111; }
.symbol-name { font-size: 28px; font-weight: 900; color: #d4af37; }
.price-val { font-size: 24px; font-weight: bold; color: #fff; }
.trade-tag { background: #1a1a1a; color: #d4af37; padding: 4px 12px; border-radius: 6px; font-size: 13px; border: 1px solid #d4af37; margin-right: 10px; font-weight: bold; }
.stButton>button { background: #d4af37 !important; color: #000 !important; font-weight: 900 !important; border-radius: 10px !important; height: 50px !important; width: 100% !important; border: none !important; transition: 0.3s; }
.stButton>button:hover { background: #fff !important; transform: scale(1.02); }
.footer-box { margin-top: 80px; padding: 40px; text-align: center; border-top: 1px solid #1a1a1a; color: #666; font-size: 13px; }
[data-testid="stMetricValue"] { color: #fff !important; font-size: 18px !important; }
[data-testid="stMetricLabel"] { color: #d4af37 !important; }
</style>

<div class="nav-bar">
    <div class="logo-text">WAHBA <span>INTELLIGENCE</span></div>
    <p style="color:#666; font-size:12px; margin-top:5px;">PREMIUM ALGORITHMIC TRADING TERMINAL</p>
</div>
""", unsafe_allow_html=True)

# --- 3. محرك البيانات الاستراتيجي (Multi-Timeframe Logic) ---
@st.cache_data(ttl=86400)
def fetch_egx_list(date_key):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}
        res = requests.post(url, json=payload, timeout=15).json()
        return sorted(list(set([item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()])))
    except:
        # 📝 هنا تم تعديل قائمة الأسهم الاحتياطية التي تظهر لو السيرفر علّق
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "ETEL", "AMOC", "HRHO", "ESRS"]

@st.cache_data(ttl=3600, show_spinner=False)
def run_strategic_scan(date_key):
    symbols = fetch_egx_list(date_key)
    results = []
    
    status_text = st.empty()
    p_bar = st.progress(0)
    
    for i, sym in enumerate(symbols):
        try:
            status_text.text(f"تحليل متعدد الفريمات لـ: {sym}...")
            
            # 1. تحليل الفريم الأسبوعي (Weekly)
            h_w = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_WEEK, timeout=10)
            w_rec = h_w.get_analysis().summary["RECOMMENDATION"]
            
            # 2. تحليل الفريم اليومي (Daily) - الأساسي
            h_d = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=10)
            analysis = h_d.get_analysis()
            d_rec = analysis.summary["RECOMMENDATION"]
            
            # 3. تحليل فريم الساعة (Hourly)
            h_h = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_HOUR, timeout=10)
            h_rec = h_h.get_analysis().summary["RECOMMENDATION"]

            # تطبيق نظام تعدد الفريمات: صعود على الكل
            if "BUY" in w_rec and "BUY" in d_rec and "BUY" in h_rec:
                ind = analysis.indicators
                
                # خوارزمية تسجيل النقاط الأصلية
                score = 0
                if "STRONG_BUY" in d_rec: score += 5
                elif "BUY" in d_rec: score += 3
                
                rsi = ind.get("RSI")
                if rsi and 45 <= rsi <= 65: score += 3 
                
                m_val = ind.get("MACD.macd")
                m_sig = ind.get("MACD.signal")
                if m_val is not None and m_sig is not None:
                    if m_val > m_sig: score += 2
                    else: score -= 5 

                close = ind.get("close")
                pivot = ind.get("Pivot.M.Classic.Middle")
                if close and pivot and close > pivot: score += 2
                
                vol = ind.get("volume")
                avg_vol = ind.get("average_volume_10d")
                vol_ratio = (vol / avg_vol) if (vol and avg_vol) else 1
                change = ind.get("change") or 0
                
                t_type = "⚡ DAY TRADING" if (vol_ratio > 1.4 or abs(change) > 3) else "🌊 SWING"
                
                results.append({
                    "Symbol": sym, "Price": close, "Score": score,
                    "S1": ind.get("Pivot.M.Classic.S1"), "S2": ind.get("Pivot.M.Classic.S2"),
                    "P": pivot, "R1": ind.get("Pivot.M.Classic.R1"),
                    "R2": ind.get("Pivot.M.Classic.R2"), "Signal": d_rec.replace("_", " "), "Type": t_type
                })
        except: continue
        p_bar.progress((i + 1) / len(symbols))
        
    p_bar.empty()
    status_text.empty()
    return pd.DataFrame(results)

# --- 4. وظائف العرض (كما هي في كودك الأصلي) ---
def display_stock_card(row):
    with st.container():
        st.markdown(f"""
        <div class="stock-card">
            <div style="display:flex; justify-content:space-between; align-items:center; direction: rtl;">
                <div>
                    <span class="symbol-name">{row['Symbol']}</span> 
                    <span class="trade-tag">{row['Type']}</span>
                </div>
                <div style="text-align: left;">
                    <div style="color:#d4af37; font-weight:900; font-size:18px;">{row['Signal']}</div>
                    <div style="color:#666; font-size:12px;">SCORE: {row['Score']}/10</div>
                </div>
            </div>
            <div class="price-val" style="text-align: right; margin-top:15px;">
                {row['Price']:.2f} <span style="font-size:14px; color:#666;">EGP</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if pd.notnull(row['S2']) and pd.notnull(row['R2']) and row['R2'] > row['S2']:
            val = max(0, min(100, ((row['Price'] - row['S2']) / (row['R2'] - row['S2'])) * 100))
            st.markdown(f"<div style='text-align:right; font-size:11px; color:#d4af37; margin-bottom:5px;'>القوة الشرائية داخل النطاق</div>", unsafe_allow_html=True)
            st.progress(int(val))
        
        cols = st.columns(4)
        cols[0].metric("S1 (دعم)", f"{row['S1']:.2f}" if pd.notnull(row['S1']) else "N/A")
        cols[1].metric("Pivot (ارتكاز)", f"{row['P']:.2f}" if pd.notnull(row['P']) else "N/A")
        cols[2].metric("R1 (مقاومة)", f"{row['R1']:.2f}" if pd.notnull(row['R1']) else "N/A")
        cols[3].metric("R2 (هدف)", f"{row['R2']:.2f}" if pd.notnull(row['R2']) else "N/A")
        st.markdown("<div style='margin-bottom:30px;'></div>", unsafe_allow_html=True)

# --- 5. منطق التشغيل ---
st.write(f"📅 **تاريخ التقرير:** {today_key} | 🕒 **توقيت القاهرة:** {now_egypt.strftime('%H:%M')} | 👤 **المشترك:** {st.session_state.current_user}")

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    if st.button('🚀 تحديث وتحليل بيانات السوق الآن'):
        with st.spinner("جاري فحص التوافق الزمني (أسبوعي/يومي/ساعة)..."):
            st.session_state.final_report = run_strategic_scan(today_key)

if 'final_report' in st.session_state:
    df = st.session_state.final_report
    if not df.empty:
        df = df.sort_values(by="Score", ascending=False)
        
        t1 = df[df['Score'] >= 8]
        if not t1.empty:
            st.markdown('<div class="section-header">⚜️ أسهم النخبة (إشارات قوية)</div>', unsafe_allow_html=True)
            for _, row in t1.iterrows(): display_stock_card(row)

        t2 = df[(df['Score'] >= 5) & (df['Score'] < 8)]
        if not t2.empty:
            st.markdown('<div class="section-header">💎 أسهم تحت المراقبة (إشارات إيجابية)</div>', unsafe_allow_html=True)
            for _, row in t2.iterrows(): display_stock_card(row)

        t3 = df[df['Score'] < 5]
        if not t3.empty:
            with st.expander("📊 استعراض باقي تحركات السوق"):
                for _, row in t3.iterrows(): display_stock_card(row)
    else:
        st.warning("لا توجد أسهم حالياً تتوافق على الفريمات الثلاثة.")

st.markdown("""
<div class="footer-box">
    <p style="font-weight:bold; color:#d4af37; letter-spacing:1px;">WAHBA INTELLIGENCE • INSTITUTIONAL DIVISION</p>
    <p>تحذير مخاطر: المعلومات المقدمة هي تحليل رقمي فني ولا تعتبر توصية مباشرة بالشراء أو البيع.</p>
    <p>© 2026 جميع الحقوق محفوظة</p>
</div>
""", unsafe_allow_html=True)

# =========================================================================
# 🧱 طوبة التسويق والأتمتة: مضافة بالكامل في نهاية الملف بدون لمس ما سبق 🧱
# =========================================================================
DB_FILE = f"report_{today_key}.csv"

if 'final_report' in st.session_state and not st.session_state.final_report.empty:
    st.session_state.final_report.to_csv(DB_FILE, index=False)

if 'final_report' not in st.session_state and os.path.exists(DB_FILE):
    st.session_state.final_report = pd.read_csv(DB_FILE)
    st.rerun()
