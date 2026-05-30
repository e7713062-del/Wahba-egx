import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz
import os

# =========================================================================
# 🧱 1. طوبة جدار الحماية ونظام الاشتراكات التلقائي (فودافون كاش)
# =========================================================================
DB_USERS = "users_db.csv"
egy_tz = pytz.timezone('Africa/Cairo')
current_date = datetime.now(egy_tz).date()

# إنشاء ملف حسابات المشتركين لو مش موجود
if not os.path.exists(DB_USERS):
    df_init = pd.DataFrame(columns=["username", "password", "vodafone_number", "status", "join_date", "expiry_date"])
    df_init.to_csv(DB_USERS, index=False)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""

# شاشة الدخول وحجب المنصة عن غير المشتركين
if not st.session_state.logged_in:
    st.set_page_config(page_title="Wahba Intelligence - دخول المشتركين", layout="centered")
    
    st.markdown("""
    <div style="text-align: center; padding: 20px; border: 2px solid #d4af37; border-radius: 15px; background-color: #0a0a0a;">
        <h2 style="color: #d4af37; font-weight: 900;">👑 WAHBA INTELLIGENCE</h2>
        <p style="color: #fff; font-size: 14px;">منصة تحليل البورصة المصرية للنخبة والمشتركين</p>
    </div>
    <br>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 تسجيل الدخول", "📝 طلب اشتراك جديد"])
    
    with tab1:
        st.subheader("تسجيل الدخول للمشتركين")
        login_user = st.text_input("اسم المستخدم:", key="login_user_input")
        login_pass = st.text_input("كلمة المرور:", type="password", key="login_pass_input")
        
        if st.button("🚀 دخول المنصة", key="btn_login_click"):
            df_u = pd.read_csv(DB_USERS)
            user_row = df_u[(df_u["username"] == login_user) & (df_u["password"] == login_pass)]
            
            if not user_row.empty:
                status = user_row.iloc[0]["status"]
                expiry_str = user_row.iloc[0]["expiry_date"]
                
                if status == "مقبول":
                    expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                    if current_date <= expiry_date:
                        st.session_state.logged_in = True
                        st.session_state.current_user = login_user
                        st.session_state.expiry_display = expiry_str
                        st.success("✅ تم تسجيل الدخول بنجاح!")
                        st.rerun()
                    else:
                        st.error("❌ عذراً، تم انتهاء مدة اشتراكك الشهري! يرجى التواصل مع الإدارة للتجديد ودفع الاشتراك.")
                elif status == "في الانتظار":
                    st.warning("⏳ حسابك قيد المراجعة حالياً. سيقوم الأدمن بتفعيله بمجرد التأكد من تحويل فودافون كاش.")
                else:
                    st.error("❌ تم رفض هذا الحساب أو إلغاؤه من قبل الإدارة.")
            else:
                st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة.")
                
    with tab2:
        st.subheader("إنشاء حساب وطلب تفعيل (فودافون كاش)")
        st.info("💡 للاشتراك: قم بتحويل قيمة الاشتراك إلى رقم فودافون كاش الخاص بنا، ثم املأ البيانات بالأسفل لإنشاء حسابك وتفعيله لمدة شهر كامل.")
        
        new_user = st.text_input("اختر اسم مستخدم جديد:", key="reg_user")
        new_pass = st.text_input("اختر كلمة مرور:", type="password", key="reg_pass")
        voda_num = st.text_input("رقم المحفظة اللي حولت منها فودافون كاش:", key="reg_voda")
        
        if st.button("📤 إرسال الطلب للأدمن للتأكيد", key="btn_reg_click"):
            if new_user and new_pass and voda_num:
                df_u = pd.read_csv(DB_USERS)
                if new_user in df_u["username"].values:
                    st.error("❌ اسم المستخدم هذا محجوز مسبقاً، اختر اسماً آخر.")
                else:
                    join_str = current_date.strftime("%Y-%m-%d")
                    expiry_calc = (current_date + timedelta(days=30)).strftime("%Y-%m-%d")
                    
                    new_row = pd.DataFrame([{
                        "username": new_user, 
                        "password": new_pass, 
                        "vodafone_number": voda_num, 
                        "status": "في الانتظار", 
                        "join_date": join_str, 
                        "expiry_date": expiry_calc
                    }])
                    df_u = pd.concat([df_u, new_row], ignore_index=True)
                    df_u.to_csv(DB_USERS, index=False)
                    st.success("✅ تم إرسال طلبك بنجاح! سيقوم الأدمن بمراجعة التحويل وتفعيل حسابك خلال دقائق.")
            else:
                st.error("❌ يرجى ملء جميع الحقول لإرسال الطلب.")
    st.stop()

# شريط جانبي للمشترك يوضح بياناته
st.sidebar.markdown(f"👤 **المشترك الحالي:** `{st.session_state.current_user}`")
st.sidebar.markdown(f"📅 **ينتهي اشتراكك في:** `{st.session_state.expiry_display}`")


# =========================================================================
# 🔓 2. كود واهبا الأصلي والكامل للأسهم المصرية (تم إزالة الكاش ليعمل لايف فوراً)
# =========================================================================
now_egypt = datetime.now(egy_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

# ملف الماركتينج لحفظ البيانات لليوم التالي تلقائياً
DB_FILE = f"report_{today_key}.csv"

st.set_page_config(page_title="Wahba Intelligence", layout="wide", initial_sidebar_state="collapsed")

# التصميم المؤسسي المطور (CSS كاملاً)
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

# سحب قائمة الأسهم بدون كاش (لايف)
def fetch_egx_list(date_key):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}
        res = requests.post(url, json=payload, timeout=15).json()
        return sorted(list(set([item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()])))
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "ETEL", "AMOC", "HRHO", "ESRS"]

# الفحص الاستراتيجي الكامل بدون كاش (هيقوم بالفحص الفعلي سهم سهم كل مرة تضغط الزر)
def run_strategic_scan(date_key):
    symbols = fetch_egx_list(date_key)
    results = []
    status_text = st.empty()
    p_bar = st.progress(0)
    
    for i, sym in enumerate(symbols):
        try:
            status_text.text(f"تحليل متعدد الفريمات لـ: {sym}...")
            h_w = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_WEEK, timeout=10)
            w_rec = h_w.get_analysis().summary["RECOMMENDATION"]
            
            h_d = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=10)
            analysis = h_d.get_analysis()
            d_rec = analysis.summary["RECOMMENDATION"]
            
            h_h = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_HOUR, timeout=10)
            h_rec = h_h.get_analysis().summary["RECOMMENDATION"]

            if "BUY" in w_rec and "BUY" in d_rec and "BUY" in h_rec:
                ind = analysis.indicators
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

st.write(f"📅 **تاريخ التقرير:** {today_key} | 🕒 **توقيت القاهرة:** {now_egypt.strftime('%H:%M')}")

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    if st.button('🚀 تحديث وتحليل بيانات السوق الآن'):
        with st.spinner("جاري فحص التوافق الزمني (أسبوعي/يومي/ساعة)..."):
            st.session_state.final_report = run_strategic_scan(today_key)
            # [طوبة الماركتينج المباشرة]: حفظ التقرير في CSV لليوم التالي فوراً
            if not st.session_state.final_report.empty:
                st.session_state.final_report.to_csv(DB_FILE, index=False)

# [طوبة الماركتينج التلقائية]: قراءة تقرير الجلسة المحفوظ فوراً لزوار المنصة المشتركين
if 'final_report' not in st.session_state and os.path.exists(DB_FILE):
    st.session_state.final_report = pd.read_csv(DB_FILE)
    st.success("📊 تم تحميل تقرير الأسهم المصرية الجاهز تلقائياً بنجاح (وضع الماركتينج).")

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
# 🧱 3. لوحة تحكم الأدمن السرية (في نهاية الملف لإدارة التفعيل والتجديد لـ فودافون كاش)
# =========================================================================
st.markdown("<br><hr style='border-color: #1a1a1a;'>", unsafe_allow_html=True)
with st.expander("🛠️ لوحة تحكم الإدارة السرية (خاصة بـ مصطفى فقط)"):
    admin_password = st.text_input("أدخل كلمة مرور الأدمن لفتح التحكم:", type="password", key="admin_pass_field")
    
    if admin_password == "WAHBA-ADMIN-2026": 
        st.subheader("📋 إدارة المشتركين وتجديد الاشتراكات")
        df_u = pd.read_csv(DB_USERS)
        
        pending_users = df_u[df_u["status"] == "في الانتظار"]
        st.markdown("### ⏳ طلبات جديدة في انتظار التأكيد:")
        if pending_users.empty:
            st.info("👌 لا توجد طلبات جديدة معلقة حالياً.")
        else:
            for idx, row in pending_users.iterrows():
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                col1.write(f"👤 **الاسم:** {row['username']} | 🔑 **الباسورد:** {row['password']}")
                col2.write(f"📱 **رقم الكاش:** `{row['vodafone_number']}`")
                
                if col3.button("قبول وتفعيل ✅", key=f"accept_{row['username']}_{idx}"):
                    df_u.loc[df_u["username"] == row["username"], "status"] = "مقبول"
                    df_u.to_csv(DB_USERS, index=False)
                    st.success(f"تم تفعيل حساب {row['username']} بنجاح!")
                    st.rerun()
                
                if col4.button("رفض وحجب ❌", key=f"reject_{row['username']}_{idx}"):
                    df_u.loc[df_u["username"] == row["username"], "status"] = "مرفوض"
                    df_u.to_csv(DB_USERS, index=False)
                    st.error(f"تم رفض حساب {row['username']}.")
                    st.rerun()

        st.markdown("<hr style='border-color: #222;'>", unsafe_allow_html=True)
        
        st.markdown("### 🔄 تجديد الاشتراكات المنتهية:")
        active_and_expired = df_u[df_u["status"] == "مقبول"]
        if active_and_expired.empty:
            st.info("لا يوجد مستخدمين مقبولين حالياً.")
        else:
            for idx, row in active_and_expired.iterrows():
                user_expiry = datetime.strptime(row['expiry_date'], "%Y-%m-%d").date()
                is_expired = current_date > user_expiry
                
                col_u1, col_u2, col_u3 = st.columns([2, 2, 1])
                if is_expired:
                    col_u1.markdown(f"👤 **{row['username']}** | 🛑 <span style='color:red;font-weight:bold;'>انتهى اشتراكه</span>", unsafe_allow_html=True)
                else:
                    col_u1.markdown(f"👤 **{row['username']}** | ✅ <span style='color:green;'>شغال</span>", unsafe_allow_html=True)
                col_u2.write(f"📅 تاريخ الانتهاء: `{row['expiry_date']}`")
                
                if col_u3.button("تجديد 30 يوم 🔁", key=f"renew_{row['username']}_{idx}"):
                    new_expiry_calc = (current_date + timedelta(days=30)).strftime("%Y-%m-%d")
                    df_u.loc[df_u["username"] == row["username"], "expiry_date"] = new_expiry_calc
                    df_u.loc[df_u["username"] == row["username"], "status"] = "مقبول"
                    df_u.to_csv(DB_USERS, index=False)
                    st.success(f"🎉 تم تجديد اشتراك {row['username']} لشهر جديد!")
                    st.rerun()

        if st.checkbox("📊 استعراض قاعدة بيانات المشتركين بالكامل"):
            st.dataframe(df_u)
