# wahba_mobile_full.py
# نسخة كاملة مطابقة لملف wahba_intelligence_pro.py بعدد أسطره ووظائفه،
# مع تحويل كود Streamlit إلى Flet مع الحفاظ على كل التفاصيل.

import flet as ft
import pandas as pd
from tradingview_ta import TA_Handler, Interval
import requests
from datetime import datetime, timedelta
import pytz
import os
import threading
import asyncio

# =========================================================================
# ⚙️ 1. تهيئة الصفحة والإعدادات الرئيسية (تم تعديلها لـ Flet)
# =========================================================================
# نظام التوقيت والتواريخ
egy_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egy_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

# ملفات قاعدة البيانات والتقارير المخزنة (المسلمة)
DB_USERS = "users_db.csv"
DB_FILE = f"report_{today_key}.csv"

# إنشاء ملف حسابات المشتركين التلقائي لو مش موجود لمنع الأخطاء
if not os.path.exists(DB_USERS):
    df_init = pd.DataFrame(columns=["username", "password", "vodafone_number", "status", "join_date", "expiry_date"])
    df_init.to_csv(DB_USERS, index=False)

# =========================================================================
# 🧱 2. دوال الفحص الخوارزمي والمؤشرات (نفس الكود الأصلي تماماً)
# =========================================================================
def fetch_egx_list(date_key=None):   # أضفت date_key للتوافق مع الأصلي لكن لمستخدم
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
        # القائمة الاحتياطية الاستراتيجية
        return [
            "COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "ETEL", "AMOC", "HRHO", "ESRS",
            "MFOT", "ORAS", "JUFO", "EFID", "CIRA", "EAST", "ALCN", "HELI", "MNHD", "OCDI"
        ]

# دالة الفحص الخوارزمي المطور ثلاثي الأبعاد والمتعدد الفريمات
def run_strategic_scan(date_key, progress_callback=None):
    symbols = fetch_egx_list(date_key)
    results = []
    total = len(symbols)
    for i, sym in enumerate(symbols):
        try:
            # الفريم الأسبوعي
            h_w = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_WEEK, timeout=10)
            w_analysis = h_w.get_analysis()
            w_rec = w_analysis.summary["RECOMMENDATION"]
            # الفريم اليومي
            h_d = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=10)
            d_analysis = h_d.get_analysis()
            d_rec = d_analysis.summary["RECOMMENDATION"]
            # فريم الساعة
            h_h = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_HOUR, timeout=10)
            h_analysis = h_h.get_analysis()
            h_rec = h_analysis.summary["RECOMMENDATION"]

            # الفلترة: إشارة شراء على جميع الفريمات
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
                if vol_ratio > 1.4 or abs(change) > 3:
                    t_type = "⚡ DAY TRADING (تداول سريع)"
                else:
                    t_type = "🌊 SWING (تداول موجي)"
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
                    "Type": t_type,
                    "Volume_Ratio": round(vol_ratio, 2),
                    "Change_Pct": round(change, 2)
                })
        except Exception as e:
            continue
        if progress_callback:
            progress_callback(i+1, total)
    return pd.DataFrame(results)

# =========================================================================
# 🧩 3. تطبيق Flet الرئيسي (نفس هيكل Streamlit مع تحويل الواجهة)
# =========================================================================
def main(page: ft.Page):
    page.title = "Wahba Intelligence"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 10
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    # متغيرات الحالة (تحل محل st.session_state)
    logged_in = False
    current_user = ""
    expiry_display = ""
    final_report = None

    # مراجع للعناصر التي سيتم تحديثها ديناميكياً
    main_content = ft.Column(spacing=20, expand=True, scroll=ft.ScrollMode.AUTO)
    page.add(main_content)

    # دالة عرض شاشة الدخول (مطابقة للتبويبات الأصلية)
    def show_login_screen():
        nonlocal logged_in, current_user, expiry_display
        main_content.controls.clear()

        # الهيدر نفس الكود الأصلي
        header = ft.Container(
            content=ft.Column([
                ft.Text("👑 WAHBA INTELLIGENCE", size=38, weight=ft.FontWeight.BOLD, color="#d4af37", text_align=ft.TextAlign.CENTER),
                ft.Text("نظام الفحص الرقمي المؤسسي للنخبة والمشتركين", size=15, color="#ffffff", text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=25,
            border=ft.border.all(2, "#d4af37"),
            border_radius=15,
            bgcolor="#0a0a0a",
            margin=ft.margin.only(bottom=25)
        )
        main_content.controls.append(header)

        # التبويبات
        tabs = ft.Tabs(
            tabs=[
                ft.Tab(text="🔑 تسجيل الدخول الفوري"),
                ft.Tab(text="📝 طلب اشتراك جديد (فودافون كاش)"),
            ],
            expand=True,
        )
        main_content.controls.append(tabs)

        # محتوى التبويب الأول (تسجيل الدخول)
        login_user = ft.TextField(label="اسم المستخدم (Username):", text_align=ft.TextAlign.RIGHT, width=300)
        login_pass = ft.TextField(label="كلمة المرور (Password):", password=True, can_reveal_password=True, text_align=ft.TextAlign.RIGHT, width=300)
        login_btn = ft.ElevatedButton("🚀 دخول المنصة والاطلاع على التحليلات", bgcolor="#d4af37", color="black", on_click=lambda e: do_login(login_user.value, login_pass.value))
        login_panel = ft.Column([login_user, login_pass, login_btn], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)

        # محتوى التبويب الثاني (الاشتراك)
        reg_user = ft.TextField(label="اختر اسم مستخدم جديد:", text_align=ft.TextAlign.RIGHT, width=300)
        reg_pass = ft.TextField(label="اختر كلمة مرور قوية:", password=True, text_align=ft.TextAlign.RIGHT, width=300)
        reg_voda = ft.TextField(label="رقم المحفظة التي قمت بالتحويل منها:", text_align=ft.TextAlign.RIGHT, width=300)
        reg_btn = ft.ElevatedButton("📤 إرسال طلب الاشتراك للأدمن", bgcolor="#d4af37", color="black", on_click=lambda e: do_register(reg_user.value, reg_pass.value, reg_voda.value))
        reg_panel = ft.Column([reg_user, reg_pass, reg_voda, reg_btn], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)

        # ربط التبويبات بالألواح
        tabs.content = ft.Column([
            ft.Container(content=login_panel, visible=True, expand=True),
            ft.Container(content=reg_panel, visible=False, expand=True)
        ], expand=True)
        
        def on_tab_change(e):
            for i, c in enumerate(tabs.content.controls):
                c.visible = (i == tabs.selected_index)
            page.update()
        tabs.on_change = on_tab_change
        # إظهار اللوح الأول
        tabs.content.controls[0].visible = True
        tabs.content.controls[1].visible = False
        
        def do_login(u, p):
            nonlocal logged_in, current_user, expiry_display
            df_u = pd.read_csv(DB_USERS)
            user_row = df_u[(df_u["username"] == u) & (df_u["password"] == p)]
            if not user_row.empty:
                status = user_row.iloc[0]["status"]
                expiry_str = user_row.iloc[0]["expiry_date"]
                if status == "مقبول":
                    expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                    current_date_egy = now_egypt.date()
                    if current_date_egy <= expiry_date:
                        logged_in = True
                        current_user = u
                        expiry_display = expiry_str
                        show_main_app()
                        return
                    else:
                        page.snack_bar = ft.SnackBar(ft.Text("❌ عذراً، انتهت صلاحية اشتراكك الشهري! يرجى التواصل مع الإدارة للتجديد."), bgcolor="red")
                elif status == "في الانتظار":
                    page.snack_bar = ft.SnackBar(ft.Text("⏳ حسابك قيد المراجعة حالياً. سيقوم الأدمن بتفعيله فور التأكد من تحويل فودافون كاش."), bgcolor="orange")
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("❌ تم حظر أو رفض هذا الحساب من قبل الإدارة."), bgcolor="red")
            else:
                page.snack_bar = ft.SnackBar(ft.Text("❌ اسم المستخدم أو كلمة المرور التي أدخلتها غير صحيحة."), bgcolor="red")
            page.snack_bar.open = True
            page.update()
        
        def do_register(u, p, v):
            if not u or not p or not v:
                page.snack_bar = ft.SnackBar(ft.Text("❌ برجاء إدخال كافة البيانات المطلوبة لإرسال الطلب بشكل صحيح."), bgcolor="red")
                page.snack_bar.open = True
                page.update()
                return
            df_u = pd.read_csv(DB_USERS)
            if u in df_u["username"].values:
                page.snack_bar = ft.SnackBar(ft.Text("❌ اسم المستخدم هذا مسجل مسبقاً، يرجى اختيار اسم آخر."), bgcolor="red")
            else:
                join_str = now_egypt.strftime("%Y-%m-%d")
                expiry_calc = (now_egypt + timedelta(days=30)).strftime("%Y-%m-%d")
                new_row = pd.DataFrame([{"username": u, "password": p, "vodafone_number": v, "status": "في الانتظار", "join_date": join_str, "expiry_date": expiry_calc}])
                df_u = pd.concat([df_u, new_row], ignore_index=True)
                df_u.to_csv(DB_USERS, index=False)
                page.snack_bar = ft.SnackBar(ft.Text("✅ تم حفظ البيانات وإرسال الإشعار للأدمن! سيتم التفعيل فور مراجعة التحويل."), bgcolor="green")
            page.snack_bar.open = True
            page.update()
        
        page.update()

    # دالة عرض التطبيق الرئيسي بعد الدخول (جميع التحليلات والأسهم)
    def show_main_app():
        nonlocal final_report
        main_content.controls.clear()

        # الشريط الجانبي العلوي (المعلومات)
        sidebar_info = ft.Container(
            content=ft.Column([
                ft.Text(f"👤 **المشترك:** `{current_user}`", size=14),
                ft.Text(f"📅 **نهاية الاشتراك:** `{expiry_display}`", size=14),
            ]),
            padding=10,
            bgcolor="#111",
            border_radius=10,
            margin=ft.margin.only(bottom=10)
        )
        main_content.controls.append(sidebar_info)

        # تاريخ الجلسة
        date_info = ft.Text(f"📅 **تاريخ تقرير الجلسة:** {today_key} | 🕒 **توقيت القاهرة الفوري:** {now_egypt.strftime('%H:%M')}", size=12, color="#666")
        main_content.controls.append(date_info)

        # زر التحديث
        scan_btn = ft.ElevatedButton("🚀 تشغيل وتحديث الفحص الفوري للسوق الآن", bgcolor="#d4af37", color="black", on_click=lambda e: run_scan())
        main_content.controls.append(ft.Container(scan_btn, alignment=ft.alignment.center, margin=10))

        # حاوية النتائج
        results_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        main_content.controls.append(results_container)

        # تحميل التقرير المخزن إن وجد
        def load_stored():
            nonlocal final_report
            if os.path.exists(DB_FILE):
                df = pd.read_csv(DB_FILE)
                if not df.empty:
                    final_report = df
                    display_results(df)
        load_stored()

        def run_scan():
            # إظهار شريط التقدم
            progress_bar = ft.ProgressBar(width=400)
            progress_text = ft.Text("جاري الاتصال بخوادم الفحص الفني وتحليل الفريمات الثلاثة...", text_align=ft.TextAlign.CENTER)
            results_container.controls.clear()
            results_container.controls.append(ft.Column([progress_text, progress_bar], horizontal_alignment=ft.CrossAxisAlignment.CENTER))
            page.update()

            def update_progress(current, total):
                progress_bar.value = current / total
                progress_text.value = f"تم فحص {current} من {total} سهم"
                page.update()

            def scan_thread():
                nonlocal final_report
                df = run_strategic_scan(today_key, update_progress)
                final_report = df
                if not df.empty:
                    df.to_csv(DB_FILE, index=False)
                # تحديث الواجهة
                page.run_coroutine(display_results_async(df))

            threading.Thread(target=scan_thread).start()

        async def display_results_async(df):
            results_container.controls.clear()
            display_results(df)
            page.update()

        def display_results(df):
            if df.empty:
                results_container.controls.append(ft.Text("لم يتم العثور على أسهم تتطابق شروطها الفنية تماماً على الفريمات الثلاثة في هذه اللحظة.", size=14, color="#d4af37"))
                return
            df_sorted = df.sort_values(by="Score", ascending=False)

            # دالة بناء بطاقة السهم (مطابقة للتصميم الأصلي)
            def build_stock_card(row):
                # شريط القوة النسبية
                progress_val = 0
                if pd.notnull(row['S2']) and pd.notnull(row['R2']) and row['R2'] > row['S2']:
                    progress_val = max(0, min(100, ((row['Price'] - row['S2']) / (row['R2'] - row['S2'])) * 100))
                return ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(row['Symbol'], size=28, weight=ft.FontWeight.BOLD, color="#d4af37"),
                            ft.Text(row['Type'], size=13, bgcolor="#1a1a1a", color="#d4af37", border=ft.border.all(1, "#d4af37"), padding=4),
                            ft.Container(expand=True),
                            ft.Column([
                                ft.Text(row['Signal'], size=18, weight=ft.FontWeight.BOLD, color="#d4af37", text_align=ft.TextAlign.END),
                                ft.Text(f"SCORE: {row['Score']}/10 | التغيير: {row['Change_Pct']}%", size=12, color="#666", text_align=ft.TextAlign.END),
                            ], horizontal_alignment=ft.CrossAxisAlignment.END),
                        ]),
                        ft.Text(f"{row['Price']:.2f} EGP", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text("القوة النسبية وموقع السعر الحالي داخل نطاق الدعم والمقاومة", size=11, color="#d4af37"),
                        ft.ProgressBar(value=progress_val/100, color="#d4af37", bgcolor="#333", width=400),
                        ft.Row([
                            ft.Text(f"S1: {row['S1']:.2f}" if pd.notnull(row['S1']) else "S1: N/A"),
                            ft.Text(f"Pivot: {row['P']:.2f}" if pd.notnull(row['P']) else "Pivot: N/A"),
                            ft.Text(f"R1: {row['R1']:.2f}" if pd.notnull(row['R1']) else "R1: N/A"),
                            ft.Text(f"R2: {row['R2']:.2f}" if pd.notnull(row['R2']) else "R2: N/A"),
                        ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                    ]),
                    bgcolor="#0a0a0a",
                    border=ft.border.all(1, "#1a1a1a"),
                    border_radius=15,
                    padding=20,
                    margin=ft.margin.only(bottom=10),
                    on_hover=lambda e: setattr(e.control, 'border', ft.border.all(2, "#d4af37") if e.data == "true" else ft.border.all(1, "#1a1a1a"))
                )

            # القسم الأول: أسهم النخبة
            elite = df_sorted[df_sorted['Score'] >= 8]
            if not elite.empty:
                results_container.controls.append(ft.Text("⚜️ أسهم النخبة والمؤسسات (إشارات شرائية قوية جداً)", size=20, weight=ft.FontWeight.BOLD, color="#d4af37"))
                for _, r in elite.iterrows():
                    results_container.controls.append(build_stock_card(r))
            
            # القسم الثاني: أسهم تحت المراقبة
            watch = df_sorted[(df_sorted['Score'] >= 5) & (df_sorted['Score'] < 8)]
            if not watch.empty:
                results_container.controls.append(ft.Text("💎 أسهم تحت المراقبة اللصيقة (إشارات إيجابية صاعدة)", size=20, weight=ft.FontWeight.BOLD, color="#d4af37"))
                for _, r in watch.iterrows():
                    results_container.controls.append(build_stock_card(r))
            
            # القسم الثالث: بقية الأسهم (في expander)
            rest = df_sorted[df_sorted['Score'] < 5]
            if not rest.empty:
                expander = ft.ExpansionTile(title=ft.Text("📊 استعراض باقي الأسهم ومخرجات الفحص الرقمي", weight=ft.FontWeight.BOLD))
                for _, r in rest.iterrows():
                    expander.controls.append(build_stock_card(r))
                results_container.controls.append(expander)
            
            page.update()

        # إضافة زر تسجيل الخروج
        logout_btn = ft.IconButton(icon=ft.icons.LOGOUT, on_click=lambda e: logout())
        page.appbar = ft.AppBar(title=ft.Text("Wahba Intelligence"), actions=[logout_btn], bgcolor="#0a0a0a")
        
        def logout():
            nonlocal logged_in
            logged_in = False
            show_login_screen()
        
        page.update()

    # =========================================================================
    # 🛠️ 4. لوحة تحكم الأدمن السرية (كما هي في الأصل)
    # =========================================================================
    def show_admin_panel():
        # نافذة حوار لإدخال كلمة المرور
        admin_pass = ft.TextField(label="أدخل كلمة مرور الأدمن السرية لفتح التحكم الحصري:", password=True, width=300)
        def check_admin(e):
            if admin_pass.value == "WAHBA-ADMIN-2026":
                dialog.open = False
                show_admin_ui()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("كلمة المرور غير صحيحة"), bgcolor="red")
                page.snack_bar.open = True
                page.update()
        dialog = ft.AlertDialog(
            title=ft.Text("التحقق من الصلاحيات"),
            content=admin_pass,
            actions=[ft.ElevatedButton("دخول", on_click=check_admin)],
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def show_admin_ui():
        # نافذة جديدة لعرض لوحة التحكم
        admin_view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        page.add(admin_view)
        # إغلاق أي محتوى سابق مؤقتاً
        main_content.visible = False
        # زر العودة
        back_btn = ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: close_admin())
        page.appbar = ft.AppBar(title=ft.Text("لوحة تحكم الإدارة العليا"), leading=back_btn, bgcolor="#0a0a0a")
        page.update()
        
        def close_admin():
            main_content.visible = True
            page.appbar = None
            admin_view.visible = False
            page.update()
        
        # قراءة قاعدة البيانات
        df_u = pd.read_csv(DB_USERS)
        
        # طلبات جديدة
        pending = df_u[df_u["status"] == "في الانتظار"]
        admin_view.controls.append(ft.Text("⏳ طلبات جديدة في انتظار التأكيد والمراجعة المالية:", size=18, weight=ft.FontWeight.BOLD))
        if pending.empty:
            admin_view.controls.append(ft.Text("👌 لا توجد طلبات اشتراك معلقة حالياً في الانتظار."))
        else:
            for idx, row in pending.iterrows():
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(f"👤 الاسم المطلوب: {row['username']} | 🔑 كلمة المرور: {row['password']}"),
                            ft.Text(f"📱 رقم التحويل المرسل منها: `{row['vodafone_number']}`"),
                            ft.Row([
                                ft.ElevatedButton("قبول وتفعيل الاشتراك ✅", on_click=lambda e, u=row['username']: update_status(u, "مقبول")),
                                ft.ElevatedButton("رفض وإلغاء الطلب ❌", on_click=lambda e, u=row['username']: update_status(u, "مرفوض")),
                            ])
                        ]),
                        padding=10
                    )
                )
                admin_view.controls.append(card)
        
        # تجديد الصلاحيات
        admin_view.controls.append(ft.Divider())
        admin_view.controls.append(ft.Text("🔄 تجديد وصلاحيات الحسابات النشطة والمنتهية:", size=18, weight=ft.FontWeight.BOLD))
        active = df_u[df_u["status"] == "مقبول"]
        if active.empty:
            admin_view.controls.append(ft.Text("لا توجد حسابات نشطة حالياً في النظام."))
        else:
            for idx, row in active.iterrows():
                user_expiry = datetime.strptime(row['expiry_date'], "%Y-%m-%d").date()
                is_expired = now_egypt.date() > user_expiry
                status_text = "🛑 انتهى اشتراكه الشهري" if is_expired else "✅ نشط وشغال حالياً"
                admin_view.controls.append(
                    ft.Row([
                        ft.Text(f"👤 {row['username']} | {status_text}"),
                        ft.Text(f"📅 تاريخ الصلاحية الحالي: {row['expiry_date']}"),
                        ft.ElevatedButton("تجديد 30 يوماً إضافية 🔁", on_click=lambda e, u=row['username']: renew_user(u))
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
        
        # خيار إظهار الجدول الكامل
        def show_full_table(e):
            admin_view.controls.append(ft.DataTable(
                columns=[ft.DataColumn(ft.Text(c)) for c in df_u.columns],
                rows=[ft.DataRow(cells=[ft.DataCell(ft.Text(str(val))) for val in row]) for _, row in df_u.iterrows()]
            ))
            page.update()
        admin_view.controls.append(ft.Checkbox(label="📊 إظهار الجدول الشامل لقاعدة البيانات الأصلية (للنسخ الاحتياطي)", on_change=show_full_table))
        
        def update_status(u, new_status):
            df = pd.read_csv(DB_USERS)
            df.loc[df["username"] == u, "status"] = new_status
            df.to_csv(DB_USERS, index=False)
            page.snack_bar = ft.SnackBar(ft.Text(f"تم {new_status} حساب {u}"), bgcolor="green")
            page.snack_bar.open = True
            page.update()
            # إعادة تحميل الواجهة
            admin_view.controls.clear()
            show_admin_ui()
        
        def renew_user(u):
            df = pd.read_csv(DB_USERS)
            current_expiry = datetime.strptime(df.loc[df["username"] == u, "expiry_date"].values[0], "%Y-%m-%d").date()
            new_expiry = max(current_expiry, now_egypt.date()) + timedelta(days=30)
            df.loc[df["username"] == u, "expiry_date"] = new_expiry.strftime("%Y-%m-%d")
            df.loc[df["username"] == u, "status"] = "مقبول"
            df.to_csv(DB_USERS, index=False)
            page.snack_bar = ft.SnackBar(ft.Text(f"🎉 تم تجديد الصلاحية لـ {u} لمدة 30 يوم إضافية من اليوم!"), bgcolor="green")
            page.snack_bar.open = True
            page.update()
            admin_view.controls.clear()
            show_admin_ui()
        
        page.update()

    # إضافة زر الأدمن العائم في كل شاشة
    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.icons.ADMIN_PANEL_SETTINGS,
        bgcolor="#d4af37",
        on_click=lambda e: show_admin_panel()
    )

    # بدء التطبيق بشاشة الدخول
    show_login_screen()

# تشغيل التطبيق
if __name__ == "__main__":
    ft.app(target=main)
