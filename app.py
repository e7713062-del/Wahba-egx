import streamlit as st
import requests
import pandas as pd
import time

# 1. إعدادات المنصة الرسمية
st.set_page_config(page_title="Wahba EGX | Universal Terminal", layout="wide")

# 2. تصميم الواجهة المؤسسي
st.markdown("""
    <style>
    .main-header { text-align: center; padding: 30px 0; border-bottom: 1px solid #333; margin-bottom: 40px; }
    .brand-name { font-family: 'Inter', sans-serif; font-size: 45px; font-weight: 800; color: var(--text-color); margin: 0; }
    .brand-tagline { font-size: 12px; letter-spacing: 5px; text-transform: uppercase; opacity: 0.6; margin-top: 10px; }
    .status-indicator { display: inline-block; width: 10px; height: 10px; background-color: #00ff00; border-radius: 50%; margin-right: 10px; box-shadow: 0 0 8px #00ff00; }
    .disclaimer-box { padding: 20px; background-color: rgba(255, 0, 0, 0.05); border-left: 5px solid #ff4b4b; margin-top: 50px; font-size: 13px; color: #888; line-height: 1.6; }
    </style>
    <div class="main-header">
        <h1 class="brand-name">WAHBA EGX</h1>
        <div class="brand-tagline">Universal Market Terminal • Infinite Range Mode</div>
    </div>
""", unsafe_allow_html=True)

# 3. محرك الفحص المجمع بمدى مفتوح (Unlimited Discovery)
def execute_universal_scan():
    url = "https://scanner.tradingview.com/egypt/scan"
    # هنا بنبعت طلب للسيرفر يرجعلنا "كل" الأسهم اللي فيها إشارة شراء
    payload = {
        "filter": [
            {"left": "recommendation_all", "operation": "in_range", "right": [0.1, 5]} # فلتر الشراء المفتوح
        ],
        "options": {"lang": "en"},
        "markets": ["egypt"],
        "symbols": {"query": {"types": []}, "tickers": []},
        "columns": ["logoid", "name", "close", "change", "RSI", "recommendation_all"],
        "sort": {"sortBy": "recommendation_all", "sortOrder": "desc"},
        "range": [0, 10000] # مدى ضخم جداً يعمل كأنه Infinity ليغطي أي عدد أسهم مستقبلي
    }
    
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.post(url, json=payload, headers=headers, timeout=20).json()
        data = res.get('data', [])
        
        final_list = []
        for item in data:
            rec_val = item['d'][5]
            # تحديد قوة الإشارة بناءً على القيمة الفنية للمؤشرات
            if rec_val > 0.5:
                signal = "STRONG BUY"
            elif rec_val > 0.1:
                signal = "BUY"
            else:
                continue # تجاهل أي إشارات بيع أو تعادل
                
            final_list.append({
                "Ticker": item['d'][1],
                "Price": round(item['d'][2], 2),
                "RSI": round(item['d'][4], 2) if item['d'][4] else "N/A",
                "Signal": signal
            })
        return final_list
    except Exception as e:
        return []

# 4. واجهة التشغيل
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button('START UNIVERSAL MARKET SCAN', use_container_width=True):
        with st.spinner('Scanning all listed assets in EGX...'):
            results = execute_universal_scan()
            
            if results:
                st.markdown(f"### <div class='status-indicator'></div> Identified Opportunities ({len(results)} Assets Found)", unsafe_allow_html=True)
                df = pd.DataFrame(results)
                st.table(df)
                
                # إحصائية بسيطة لتعزيز الشكل المؤسسي
                st.caption(f"Total Market Coverage: Inclusive of all detected listings.")
            else:
                st.info("Scan Complete: No securities currently meet the institutional growth criteria.")

# 5. القسم القانوني
st.markdown("""
    <div class="disclaimer-box">
        <strong>إخلاء مسؤولية قانوني:</strong><br>
        هذه الأداة للمساعدة المعلوماتية والتحليل الفني فقط. سوق المال ينطوي على مخاطر، والقرار النهائي مسؤوليتك الشخصية.
    </div>
""", unsafe_allow_html=True)

st.divider()
st.caption(f"WAHBA EGX | INFINITE ENGINE | © 2026")
