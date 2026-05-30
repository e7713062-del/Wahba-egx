import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz
import os

# =========================================================================
# ⚙️ 1. تهيئة الصفحة والإعدادات الرئيسية
# =========================================================================
st.set_page_config(page_title="Wahba Intelligence", layout="wide", initial_sidebar_state="collapsed")

# نظام التوقيت والتواريخ
egy_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egy_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

# ملفات قاعدة البيانات والتقارير المخزنة
DB_USERS = "users_db.csv"
DB_FILE = f"report_{today_key}.csv"

# إنشاء ملف حسابات المشتركين لو مش موجود
if not os.path.exists(DB_USERS):
    df_init = pd.DataFrame(columns=["username", "password", "vodafone_number", "status", "join_date", "expiry_date"])
    df_init.to_csv(DB_USERS, index=False)

# إدارة جلسة المستخدم
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "expiry_display" not in st.session_state:
    st.session_state.expiry_display = ""

# =========================================================================
# 🧱 2. دوال الفحص الخوارزمي والمؤشرات
# =========================================================================
def fetch_egx_list(date_key):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {
            "filter": [{"left": "market_cap_basic", "operation": "nempty"}],
            "markets": ["egypt"],
            "columns": ["name", "description", "logoid", "update_mode", "type", "typespecs"],
            "sort": {"by": "market_cap_basic", "order": "desc"}
        }
        res = requests.post(url, json=payload, timeout=15).json()
        valid_symbols = []
        for item in res['data']:
            sym_raw = item['s'].split(':')[1]
            if not sym_raw.isdigit():
                valid_symbols.append(sym_raw)
        return sorted(list(set(valid_symbols)))
    except:
        return [
            "COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "ETEL", "AMOC", "HRHO", "ESRS",
            "MFOT", "ORAS", "JUFO", "EFID", "CIRA", "EAST", "ALCN", "HELI", "MNHD", "OCDI"
        ]

def run_strategic_scan(date_key):
    symbols = fetch_egx_list(date_key)
    results = []
    status_text = st.empty()
    p_bar = st.progress(0)
    for i, sym in enumerate(symbols):
        try:
            status_text.text(f"📊 فحص خوارزمي متقدم ونظام التوافق الزمني لـ: {sym}...")
            h_w = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_WEEK, timeout=10)
            w_analysis = h_w.get_analysis()
            w_rec = w_analysis.summary["RECOMMENDATION"]
            h_d = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=10)
            d_analysis = h_d.get_analysis()
            d_rec = d_analysis.summary["RECOMMENDATION"]
            h_h = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_HOUR, timeout=10)
            h_analysis = h_h.get_analysis()
            h_rec = h_analysis.summary["RECOMMENDATION"]
            if "BUY" in w_rec and "BUY" in d_rec and "BUY" in h_rec:
                ind = d_analysis.indicators
                score = 0
                if "STRONG_BUY" in d_rec: score += 5
                elif "BUY" in d_rec: score += 3
                rsi = ind.get("RSI")
                if rsi and 45 <= rsi <= 65: score += 3
                elif rsi and (rsi < 45 or rsi > 65): score += 1
                m_val = ind.get("MACD.macd")
                m_sig = ind.get("MACD.signal")
                if m_val is not None and m_sig is not None:
                    if m_val > m_sig: score += 2
                    else: score -= 4
                close = ind.get("close")
                pivot = ind.get("Pivot.M.Classic.Middle")
                if close and pivot and close > pivot: score += 2
                vol = ind.get("volume")
                avg_vol = ind.get("average_volume_10d")
                vol_ratio = (vol / avg_vol) if (vol and avg_vol) else 1
                change = ind.get("change") or 0
                
                results.append({
                    "Symbol": sym,
                    "Price": close,
                    "Score": score,
                    "S1": ind.get("Pivot.M.Classic.S1"),
                    "S2": ind.get("Pivot.M.Classic.S2"),
                    "P": pivot,
                    "R1": ind.get("Pivot.M.Classic.R1"),
                    "R2": ind.get("Pivot.M.Classic.R2"),
                    "Signal": d_rec.replace("_", " "),
                    "Volume_Ratio": round(vol_ratio, 2),
                    "Change_Pct": round(change, 2)
                })
        except:
            continue
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
                </div>
                <div style="text-align: left;">
                    <div style="color:#d4af37; font-weight:900; font-size:18px;">{row['Signal']}</div>
                    <div style="color:#666; font-size:12px;">SCORE: {row['Score']}/10 | التغيير: {row['Change_Pct']}%</div>
                </div>
            </div>
            <div class="price-val" style="text-align: right; margin-top:15px;">
                {row['Price']:.2f} <span style="font-size:14px; color:#666;">EGP</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if pd.notnull(row['S2']) and pd.notnull(row['R2']) and row['R2'] > row['S2']:
            val = max(0, min(100, ((row['Price'] - row['S2']) / (row['R2'] - row['S2'])) * 100))
            st.markdown(f"<div style='text-align:right; font-size:11px; color:#d4af37; margin-bottom:5px;'>القوة النسبية وموقع السعر الحالي داخل نطاق الدعم والمقاومة ({int(val)}%)</div>", unsafe_allow_html=True)
            st.progress(int(val))
        cols = st.columns(4)
        cols[0].metric("S1 (دعم أول)", f"{row['S1']:.2f}" if pd.notnull(row['S1']) else "N/A")
        cols[1].metric("Pivot (نقطة الارتكاز)", f"{row['P']:.2f}" if pd.notnull(row['P']) else "N/A")
        cols[2].metric("R1 (مقاومة أولى)", f"{row['R1']:.2f}" if pd.notnull(row['R1']) else "N/A")
        cols[3].metric("R2 (المستهدف الرئيسي)", f"{row['R2']:.2f}" if pd.notnull(row['R2']) else "N/A")
        st.markdown("<div style='margin-bottom:30px;'></div>", unsafe_allow_html=True)

# =========================================================================
# 🔐 3. شاشة تسجيل الدخول المستقلة
# =========================================================================
def show_login_screen():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    .stApp { background-color: #000000; color: #ffffff; }
    div[data-testid="stVerticalBlock"] { gap: 0rem; }
    </style>
    <div style="text-align: center; padding: 25px; border: 2px solid #d4af37; border-radius: 15px; background-color: #0a0a0a; margin-bottom: 25px;">
        <h1 style="color: #d4af37; font-weight: 900; margin: 0; font-size: 38px;">WAHBA INTELLIGENCE</h1>
        <p style="color: #fff; font-size: 15px; margin-top: 5px;">نظام الفحص الرقمي المؤسسي للنخبة والمشتركين</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 تسجيل الدخول الفوري", "📝 طلب اشتراك جديد (فودافون كاش)"])
    
    with tab1:
        st.markdown("<div style='text-align: right; font-weight: bold;'>يرجى إدخال بيانات حسابك المعتمد لفتح النظام:</div>", unsafe_allow_html=True)
        login_user = st.text_input("اسم المستخدم (Username):", key="login_user_input", placeholder="أدخل اسمك هنا")
        login_pass = st.text_input("كلمة المرور (Password):", type="password", key="login_pass_input", placeholder="أدخل كلمة السر")
        
        if st.button("🚀 دخول المنصة والاطلاع على التحليلات", key="btn_login_click"):
            u_clean = login_user.strip()
            p_clean = login_pass.strip()
            
            if u_clean == "admin" and p_clean == "1234":
                st.session_state.logged_in = True
                st.session_state.current_user = "المهندس مصطفى"
                st.session_state.expiry_display = "حساب إدارة دائم"
                st.success("أهلاً بك يا باشمهندس مصطفى! جاري فتح المنصة...")
                st.rerun()
            else:
                df_u = pd.read_csv(DB_USERS)
                user_row = df_u[(df_u["username"] == u_clean) & (df_u["password"] == p_clean)]
                if not user_row.empty:
                    status = user_row.iloc[0]["status"]
                    expiry_str = user_row.iloc[0]["expiry_date"]
                    if status == "مقبول":
                        expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                        if now_egypt.date() <= expiry_date:
                            st.session_state.logged_in = True
                            st.session_state.current_user = u_clean
                            st.session_state.expiry_display = expiry_str
                            st.success("✅ تم التحقق بنجاح.. جاري تفعيل اللوحة!")
                            st.rerun()
                        else:
                            st.error("❌ عذراً، انتهت صلاحية اشتراكك الشهري!")
                    elif status == "في الانتظار":
                        st.warning("⏳ حسابك قيد المراجعة حالياً من قبل الإدارة.")
                    else:
                        st.error("❌ هذا الحساب غير مصرح له بالدخول.")
                else:
                    st.error("❌ اسم المستخدم أو كلمة المرور التي أدخلتها غير صحيحة.")
    
    with tab2:
        st.subheader("إنشاء حساب جديد وطلب تفعيل")
        st.info("💡 للاشتراك: قم بتحويل قيمة الاشتراك إلى رقم فودافون كاش الخاص بنا، ثم املأ البيانات بالأسفل لإنشاء حسابك وتفعيله.")
        new_user = st.text_input("اختر اسم مستخدم جديد:", key="reg_user")
        new_pass = st.text_input("اختر كلمة مرور قوية:", type="password", key="reg_pass")
        voda_num = st.text_input("رقم المحفظة التي قمت بالتحويل منها:", key="reg_voda")
        if st.button("📤 إرسال طلب الاشتراك للأدمن", key="btn_reg_click"):
            if new_user and new_pass and voda_num:
                df_u = pd.read_csv(DB_USERS)
                if new_user in df_u["username"].values:
                    st.error("❌ اسم المستخدم هذا مسجل مسبقاً، يرجى اختيار اسم آخر.")
                else:
                    join_str = now_egypt.strftime("%Y-%m-%d")
                    expiry_calc = (now_egypt + timedelta(days=30)).strftime("%Y-%m-%d")
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
                    st.success("✅ تم حفظ البيانات وإرسال الإشعار للأدمن! سيتم التفعيل فور مراجعة التحويل.")
            else:
                st.error("❌ برجاء إدخال كافة البيانات المطلوبة لإرسال الطلب بشكل صحيح.")

# =========================================================================
# 🚀 4. المنصة الأساسية (تظهر فقط بعد تسجيل الدخول)
# =========================================================================
def show_platform():
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
    
    st.sidebar.markdown(f"👤 **المشترك:** `{st.session_state.current_user}`")
    st.sidebar.markdown(f"📅 **نهاية الاشتراك:** `{st.session_state.expiry_display}`")
    
    st.write(f"📅 **تاريخ تقرير الجلسة:** {today_key} | 🕒 **توقيت القاهرة الفوري:** {now_egypt.strftime('%H:%M')}")
    
    # 🔄 التحديث التلقائي الذكي بعد انتهاء الجلسة (بعد الساعة 3 عصراً بتوقيت القاهرة)
    if now_egypt.hour >= 15:
        if not os.path.exists(DB_FILE):
            with st.spinner("🔄 نهاية الجلسة المعتادة.. جاري تشغيل الفحص التلقائي لحفظ بيانات اليوم..."):
                auto_report = run_strategic_scan(today_key)
                if not auto_report.empty:
                    auto_report.to_csv(DB_FILE, index=False)
                    st.session_state.final_report = auto_report
                    st.rerun()

    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button('🚀 تشغيل وتحديث الفحص الفوري للسوق الآن'):
            with st.spinner("جاري الاتصال بخوادم الفحص الفني وتحليل الفريمات الثلاثة..."):
                st.session_state.final_report = run_strategic_scan(today_key)
                if not st.session_state.final_report.empty:
                    st.session_state.final_report.to_csv(DB_FILE, index=False)
    
    # محاولة تحميل ملف اليوم، وإذا لم يوجد، يتم تحميل آخر ملف متاح لليوم السابق
    if 'final_report' not in st.session_state:
        if os.path.exists(DB_FILE):
            st.session_state.final_report = pd.read_csv(DB_FILE)
            st.success("📊 تم تحميل تقرير الأسهم الجاهز تلقائياً بنجاح.")
        else:
            all_files = sorted([f for f in os.listdir('.') if f.startswith("report_") and f.endswith(".csv")], reverse=True)
            if all_files:
                st.session_state.final_report = pd.read_csv(all_files[0])
                st.info(f"📁 تم عرض آخر بيانات محفوظة من جلسة: {all_files[0].replace('report_', '').replace('.csv', '')}")
            else:
                st.warning("⚠️ لا توجد بيانات محفوظة حالياً، يرجى تشغيل الفحص أول مرة.")

    if 'final_report' in st.session_state:
        df = st.session_state.final_report
        if not df.empty:
            df = df.sort_values(by="Score", ascending=False)
            t1 = df[df['Score'] >= 8]
            if not t1.empty:
                st.markdown('<div class="section-header">⚜️ أسهم النخبة والمؤسسات (إشارات شرائية قوية جداً)</div>', unsafe_allow_html=True)
                for _, row in t1.iterrows():
                    display_stock_card(row)
            t2 = df[(df['Score'] >= 5) & (df['Score'] < 8)]
            if not t2.empty:
                st.markdown('<div class="section-header">💎 أسهم تحت المراقبة اللصيقة (إشارات إيجابية صاعدة)</div>', unsafe_allow_html=True)
                for _, row in t2.iterrows():
                    display_stock_card(row)
            t3 = df[df['Score'] < 5]
            if not t3.empty:
                with st.expander("📊 استعراض باقي الأسهم ومخرجات الفحص الرقمي"):
                    for _, row in t3.iterrows():
                        display_stock_card(row)
        else:
            st.warning("لم يتم العثور على أسهم تتطابق شروطها الفنية تماماً على الفريمات الثلاثة في هذه اللحظة.")
    
    st.markdown("""
    <div class="footer-box">
        <p style="font-weight:bold; color:#d4af37; letter-spacing:1px;">WAHBA INTELLIGENCE • INSTITUTIONAL DIVISION</p>
        <p>تحذير مخاطر: كافة التحليلات والمخرجات الرقمية الناتجة عن الخوارزمية هي لأغراض تعليمية وإرشادية ولا تعد توصية مباشرة بالشراء أو البيع.</p>
        <p>© 2026 جميع الحقوق محفوظة لشركة واهبا القابضة</p>
    </div>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # 🛠️ 5. لوحة تحكم الأدمن
    # =========================================================================
    st.markdown("<br><hr style='border-color: #1a1a1a;'>", unsafe_allow_html=True)
    with st.expander("🛠️ لوحة تحكم الإدارة العليا (خاصة بالمهندس مصطفى فقط)"):
        admin_password = st.text_input("أدخل كلمة مرور الأدمن السرية لفتح التحكم الحصري:", type="password", key="admin_pass_field")
        if admin_password == "WAHBA-ADMIN-2026" or admin_password == "WahbaAdmin2026":
            st.subheader("📋 كشوفات حسابات المشتركين وطلبات فودافون كاش المعلقة")
            df_u = pd.read_csv(DB_USERS)
            pending_users = df_u[df_u["status"] == "في الانتظار"]
            st.markdown("### ⏳ طلبات جديدة في انتظار التأكيد والمراجعة المالية:")
            if pending_users.empty:
                st.info("👌 لا توجد طلبات اشتراك معلقة حالياً في الانتظار.")
            else:
                for idx, row in pending_users.iterrows():
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                    col1.write(f"👤 **الاسم المطلوب:** {row['username']} | 🔑 **كلمة المرور:** {row['password']}")
                    col2.write(f"📱 **رقم التحويل المرسل منها:** `{row['vodafone_number']}`")
                    if col3.button("قبول وتفعيل الاشتراك ✅", key=f"accept_{row['username']}_{idx}"):
                        df_u.loc[df_u["username"] == row["username"], "status"] = "مقبول"
                        df_u.to_csv(DB_USERS, index=False)
                        st.success(f"تم تفعيل وتوثيق حساب {row['username']} لمدة شهر!")
                        st.rerun()
                    if col4.button("رفض وإلغاء الطلب ❌", key=f"reject_{row['username']}_{idx}"):
                        df_u.loc[df_u["username"] == row["username"], "status"] = "مرفوض"
                        df_u.to_csv(DB_USERS, index=False)
                        st.error(f"تم رفض حساب {row['username']} بنجاح.")
                        st.rerun()
            
            st.markdown("<hr style='border-color: #222;'>", unsafe_allow_html=True)
            st.markdown("### 🔄 تجديد وصلاحيات الحسابات النشطة والمنتهية:")
            active_and_expired = df_u[df_u["status"] == "مقبول"]
            if active_and_expired.empty:
                st.info("لا توجد حسابات نشطة حالياً في النظام.")
            else:
                for idx, row in active_and_expired.iterrows():
                    user_expiry = datetime.strptime(row['expiry_date'], "%Y-%m-%d").date()
                    current_date_egy = now_egypt.date()
                    is_expired = current_date_egy > user_expiry
                    col_u1, col_u2, col_u3 = st.columns([2, 2, 1])
                    if is_expired:
                        col_u1.markdown(f"👤 **{row['username']}** | 🛑 <span style='color:red;font-weight:bold;'>انتهى اشتراكه الشهري</span>", unsafe_allow_html=True)
                    else:
                        col_u1.markdown(f"👤 **{row['username']}** | ✅ <span style='color:green;'>نشط وشغال حالياً</span>", unsafe_allow_html=True)
                    col_u2.write(f"📅 تاريخ الصلاحية الحالي: `{row['expiry_date']}`")
                    if col_u3.button("تجديد 30 يوم إضافي 🔄", key=f"renew_{row['username']}_{idx}"):
                        new_expiry = (datetime.strptime(row['expiry_date'], "%Y-%m-%d") + timedelta(days=30)).strftime("%Y-%m-%d")
                        df_u.loc[df_u["username"] == row["username"], "expiry_date"] = new_expiry
                        df_u.to_csv(DB_USERS, index=False)
                        st.success(f"تم تجديد صلاحية {row['username']} بنجاح!")
                        st.rerun()

# =========================================================================
# 🎮 6. التحكم في توجيه العرض
# =========================================================================
if st.session_state.logged_in:
    show_platform()
else:
    show_login_screen()
