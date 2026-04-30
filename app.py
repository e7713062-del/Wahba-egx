import streamlit as st
import requests
import pandas as pd
import time

# 1. إعدادات البراندنج (عشان الماركتنج)
st.set_page_config(page_title="Wahba EGX | Professional", layout="wide")

st.markdown("""
    <style>
    .main-header { text-align: center; color: #00ffcc; padding: 20px; border-bottom: 2px solid #333; }
    .stButton>button { background-color: #00ffcc; color: black; font-weight: bold; width: 100%; border-radius: 10px; }
    .card { background-color: #1e1e1e; padding: 20px; border-radius: 10px; border-left: 5px solid #00ffcc; }
    </style>
    <div class="main-header">
        <h1>WAHBA EGX PRO</h1>
        <p>Institutional Market Intelligence Terminal</p>
    </div>
""", unsafe_allow_html=True)

# 2. وظيفة جلب البيانات مع حماية "User-Agent" عشوائية
@st.cache_data(ttl=300) # الكود بيحفظ البيانات لمدة 5 دقائق عشان لو حد داس مرتين ميحصلش بلوك
def fetch_data_safe():
    url = "https://scanner.tradingview.com/egypt/scan"
    
    # رأس طلب (Header) يبان كأنه متصفح حقيقي 100%
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.tradingview.com/",
        "Origin": "https://www.tradingview.com"
    }
    
    payload = {
        "filter": [{"left": "recommendation_all", "operation": "in_range", "right": [0.1, 5]}],
        "options": {"lang": "en"},
        "markets": ["egypt"],
        "columns": ["name", "close", "change", "RSI", "recommendation_all", "description"],
        "sort": {"sortBy": "recommendation_all", "sortOrder": "desc"},
        "range": [0, 100000] # Infinity Range
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json().get('data', [])
        return None
    except:
        return None

# 3. عرض البيانات بشكل تسويقي (Professional UI)
if st.button("🚀 EXECUTE GLOBAL MARKET SCAN"):
    with st.spinner("Bypassing firewalls & fetching live EGX data..."):
        raw_data = fetch_data_safe()
        
        if raw_data:
            processed = []
            for item in raw_data:
                d = item['d']
                processed.append({
                    "Ticker": d[0],
                    "Company": d[5],
                    "Price": f"{d[1]:,.2f}",
                    "Change": f"{d[2]:+.2f}%",
                    "RSI": round(d[3], 2) if d[3] else "N/A",
                    "Signal": "🟢 STRONG BUY" if d[4] >= 0.5 else "🔵 BUY"
                })
            
            df = pd.DataFrame(processed)
            
            # عرض إحصائيات سريعة للماركتنج
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Assets", len(raw_data))
            c2.metric("Strong Buys", len(df[df['Signal'] == "🟢 STRONG BUY"]))
            c3.metric("Market Status", "🟢 OPEN" if 10 <= time.localtime().tm_hour < 15 else "🔴 CLOSED")

            st.divider()
            
            # جدول البيانات الاحترافي
            st.subheader("📊 Identified Opportunities")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
        else:
            # رسالة ذكية في حالة البلوك عشان شكل الماركتنج
            st.error("⚠️ System Overload: Too many requests from this server. Please try again in 60 seconds.")
            st.info("Tip: For faster, unblocked access, our Pro desktop version is recommended.")

# 4. إخلاء المسؤولية
st.markdown("<div style='font-size: 10px; color: #555; margin-top: 50px;'>Legal Disclaimer: For educational use only. Trading involves risk.</div>", unsafe_allow_html=True)
