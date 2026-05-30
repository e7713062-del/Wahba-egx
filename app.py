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

# --- 2. قاعدة بيانات المشتركين والأتمتة المالية والزمنية ---
USER_DB_FILE = "users_db.csv"

def load_users():
    if os.path.exists(USER_DB_FILE):
        df = pd.read_csv(USER_DB_FILE)
        return df.to_dict(orient="records")
    else:
        # الحسابات الافتراضية الثابتة
        return [
            {"username": "admin", "password": "012700", "role": "admin", "status": "active", "start_date": today_key},
            {"username": "مصطفى تامر", "password": "012700", "role": "user", "status": "active", "start_date": today_key}
        ]

def save_users(users_list):
    pd.DataFrame(users_list).to_csv(USER_DB_FILE, index=False)

if 'users' not in st.session_state:
    st.session_state.users = load_users()

# الفحص التلقائي لمرور 30 يوم (دون المساس بكود السوق)
for u in st.session_state.users:
    if u['role'] != 'admin' and u['status'] == 'active':
        try:
            start_dt = datetime.strptime(u['start_date'], "%Y-%m-%d")
            days_passed = (datetime.now().date() - start_dt.date()).days
            if days_passed >= 30:
                u['status'] = 'expired'
        except:
            pass
save_users(st.session_state.users)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- 3. واجهة تسجيل الدخول والتسجيل الجديد (تصميم صندوقي فخم للماركتينج) ---
if not st.session_state.logged_in:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    .stApp { background-color: #000000; color: #ffffff; }
    
    .marketing-login-box {
        max-width: 450px;
        margin: 60px auto 10px auto;
        padding: 35px;
        background: #0a0a0a;
        border: 1px solid #1a1a1a;
        border-top: 4px solid #d4af37;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0px 10px 30px rgba(212, 175, 55, 0.05);
    }
    .m-logo { font-size: 32px; font-weight: 900; color: #fff; letter-spacing: 2px; margin-bottom: 5px; }
    .m-logo span { color: #d4af37; }
    .m-subtitle { color: #666; font-size: 12px; margin-bottom: 25px; letter-spacing: 1px; }
    
    .stButton>button { 
        background: #d4af37 !important; 
        color: #000 !important; 
        font-weight: 900 !important; 
        border-radius: 10px !important; 
        height: 45px !important; 
        width: 100% !important; 
        border: none !important; 
        transition: 0.3s;
    }
    .stButton>button:hover { 
        background: #fff !important; 
        transform: scale(1.02); 
    }
    </style>
    
    <div class="marketing-login-box">
        <div class="m-logo">WAHBA <span>INTELLIGENCE</span></div>
        <div class="m-subtitle">PREMIUM ALGORITHMIC TRADING TERMINAL</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐 تسجيل دخول المشتركين", "✨ طلب اشتراك جديد"])
    
    with tab1:
        col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
        with col_l2:
            u_clean = st.text_input("اسم المستخدم", placeholder="أدخل اسم الحساب", key="login_user").strip()
            p_clean = st.text_input("كلمة المرور", type="password", placeholder="••••••", key="login_pass").strip()
            
            if st.button("دخول المنصة 🚀", key="login_btn"):
                user_found = next((u for u in st.session_state.users if u['username'] == u_clean and u['password'] == p_clean), None)
                
                if user_found:
                    if user_found['status'] == 'active':
                        st.session_state.logged_in = True
                        st.session_state.current_user = user_found['username']
                        st.session_state.user_role = user_found['role']
                        st.success("👑 تم التحقق من الاشتراك بنجاح! جاري التوجيه...")
                        st.rerun()
                    elif user_found['status'] == 'expired':
                        st.error("❌ انتهت صلاحية اشتراكك الشهري (30 يوم). يرجى تحويل قيمة الاشتراك للإدارة لإعادة تفعيل الحساب فوراً.")
                    else:
                        st.warning("⚠️ حسابك قيد الانتظار. يرجى التواصل مع الإدارة لتفعيل الاشتراك الشهري وتأكيد الدفع.")
                else:
                    st.error("❌ بيانات الدخول غير صحيحة.")
                    
    with tab2:
        col_r1, col_r2, col_r3 = st.columns([1, 2, 1])
        with col_r2:
            st.markdown("<p style='color:#666; font-size:13px; text-align:center;'>أنشئ حسابك الجديد وتواصل مع الإدارة لتفعيل الاشتراك</p>", unsafe_allow_html=True)
            new_user = st.text_input("اختر اسم مستخدم", placeholder="الاسم ثلاثي", key="reg_user").strip()
            new_pass = st.text_input("اختر كلمة مرور", type="password", placeholder="••••••", key="reg_pass").strip()
            
            if st.button("إرسال طلب التفعيل 📨", key="reg_btn"):
                if new_user and new_pass:
                    exists = any(u for u in st.session_state.users if u['username'] == new_user)
                    if exists:
                        st.error("❌ اسم المستخدم هذا موجود بالفعل.")
                    else:
                        st.session_state.users.append({
                            "username": new_user, "password": new_pass, "role": "user", "status": "pending", "start_date": today_key
                        })
                        save_users(st.session_state.users)
                        st.success("✅ تم تسجيل طلبك! حسابك الآن قيد الانتظار لحين مراجعة الدفع وتفعيله من الإدارة.")
                else:
                    st.error("❌ يرجى ملء كافة الحقول لإرسال الطلب.")
    st.stop()

# --- 4. لوحة تحكم الإدارة (التحكم الذكي وقبول/تجديد الاشتراكات الشهري) ---
if st.session_state.user_role == "admin":
    st.markdown("<div style='background:#111; padding:15px; border-radius:10px; border:1px solid #d4af37; margin-bottom:20px;'>", unsafe_allow_html=True)
    st.subheader("💼 لوحة تحكم الإدارة المالية والتحكم بالاشتراكات")
    
    users_df = pd.DataFrame(st.session_state.users)
    
    for idx, row in users_df.iterrows():
        if row['username'] != 'admin':
            col_u1, col_u2, col_u3 = st.columns([2, 1, 1])
            col_u1.write(f"👤 **المستخدم:** {row['username']} | 📅 **تاريخ البدء:** {row['start_date']}")
            
            if row['status'] == 'active':
                status_color = "🟢 نشط (ضمن الـ 30 يوم)"
            elif row['status'] == 'expired':
                status_color = "❌ منتهي الصلاحية تلقائياً"
            else:
                status_color = "🔴 قيد الانتظار (جديد)"
                
            col_u2.write(f"الحالة: {status_color}")
            
            if row['status'] == 'pending':
                if col_u3.button("✅ قبول وتفعيل", key=f"acc_{idx}"):
                    st.session_state.users[idx]['status'] = 'active'
                    st.session_state.users[idx]['start_date'] = today_key
                    save_users(st.session_state.users)
                    st.rerun()
            elif row['status'] == 'expired':
                if col_u3.button("🔄 تجديد لـ 30 يوم", key=f"ren_{idx}"):
                    st.session_state.users[idx]['status'] = 'active'
                    st.session_state.users[idx]['start_date'] = today_key
                    save_users(st.session_state.users)
                    st.rerun()
            else:
                if col_u3.button("🚫 إلغاء الاشتراك", key=f"susp_{idx}"):
                    st.session_state.users[idx]['status'] = 'pending'
                    save_users(st.session_state.users)
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- 5. التصميم المؤسسي للمنصة (كما هو بالملي) ---
st.markdown("""
<style>
.nav-bar { text-align: center; padding: 25px; background: linear-gradient(180deg, #111 0%, #000 100%); border-bottom: 2px solid #d4af37; margin-bottom: 30px; }
.logo-text { font-size: 35px; font-weight: 900; color: #fff; letter-spacing: 2px; }
.logo-text span { color: #d4af37; }
.section-header { color: #d4af37; border-right: 5px solid #d4af37; padding-right: 15px; margin: 40px 0 20px 0; font-size: 24px; font-weight: bold; text-align: right; background: rgba(212, 175, 55, 0.05); padding: 10px; }
.stock-card { background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 15px; padding: 25px; margin-bottom: 10px; border-top: 3px solid #d4af37; transition: 0.3s; }
.stock-card:hover { border-color: #fff; background: #111; }
.symbol-name { font-size: 28px; font-weight: 900; color: #d4af37; }
.price-val { font-size: 24px; font-weight: bold; color: #fff; }
.trade-tag { background: #1a1a1a; color: #d4af37; padding: 4px 12px; border-radius: 6px; font-size: 13px; border: 1px solid #d4af37; margin-right: 10px; font-weight: bold; }
.footer-box { margin-top: 80px; padding: 40px; text-align: center; border-top: 1px solid #1a1a1a; color: #666; font-size: 13px; }
[data-testid="stMetricValue"] { color: #fff !important; font-size: 18px !important; }
[data-testid="stMetricLabel"] { color: #d4af37 !important; }
</style>

<div class="nav-bar">
    <div class="logo-text">WAHBA <span>INTELLIGENCE</span></div>
    <p style="color:#666; font-size:12px; margin-top:5px;">PREMIUM ALGORITHMIC TRADING TERMINAL</p>
</div>
""", unsafe_allow_html=True)

# --- 6. محرك البيانات الاستراتيجي (لم يتم تعديل حرف واحد منه) ---
@st.cache_data(ttl=86400)
def fetch_egx_list(date_key):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}
        res = requests.post(url, json=payload, timeout=15).json()
        return sorted(list(set([item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()])))
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "ETEL", "AMOC", "HRHO", "ESRS"]

@st.cache_data(ttl=3600, show_spinner=False)
def run_strategic_scan(date_key):
    symbols = fetch_egx_list(date_key)
    results = []
    
    status_text = st.empty()
    p_bar = st.progress(0)
    
    for i, sym in enumerate(symbols
