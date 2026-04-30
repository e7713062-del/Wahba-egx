import streamlit as st
import requests
import pandas as pd
import time

# 1. الإعدادات العامة للمنصة
st.set_page_config(page_title="Wahba EGX | Terminal", layout="wide")

# 2. تصميم الواجهة (مظهر احترافي ومبسط)
st.markdown("""
    <style>
    .main-header { text-align: center; padding: 20px 0; border-bottom: 1px solid #333; }
    .brand-name { font-size: 40px; font-weight: 800; color: #ffffff; }
    .status-indicator { display: inline-block; width: 10px; height: 10px; background-color: #00ff00; border-radius: 50%; margin-right: 10px; }
    .disclaimer { padding: 15px; background: #1e1e1e; border-radius: 5px; margin-top: 30px; font-size: 12px; color: #888; }
    </style>
    <div class="main-header">
        <div class="brand-name">WAHBA EGX TERMINAL</div>
        <div style="opacity: 0.6; letter-spacing: 2px;">INFINITE ASSET SCANNER • LOCAL MODE</div>
    </div>
""", unsafe_allow_html=True)

# 3. محرك الفحص المجمع (بيجيب أي عدد أسهم أوتوماتيك)
def run_master_scan():
    url = "https://scanner.tradingview.com/egypt/scan"
    # الفلتر ده بيجيب الأسهم اللي عليها إشارات شراء فقط
    payload = {
        "filter": [{"left": "recommendation_all", "operation": "in_range", "right": [0.1, 5]}],
        "options": {"lang": "en"},
        "markets": ["egypt"],
        "symbols": {"query": {"types": []}, "tickers": []},
        "columns": ["name", "close", "change", "RSI", "recommendation_all", "description"],
        "sort": {"sortBy": "recommendation_all", "sortOrder": "desc"},
        "range": [0, 100000] # نطاق مفتوح لأي عدد أسهم
    }
    
    try:
        response = requests.post(url, json=payload, timeout=20).json()
        rows = response.get('data', [])
        
        results = []
        for row in rows:
            d = row['d']
            rec_val = d[4]
            # تصنيف الإشارة
            signal = "STRONG BUY" if rec_val >= 0.5 else "BUY"
            
            results.append({
                "Ticker": d[0],
                "Company": d[5],
                "Price": round(d[1], 2),
                "Change %": f"{round(d[2], 2)}%",
                "RSI": round(d[3], 2) if d[3] else 0,
                "Signal": signal
            })
        return results
    except Exception as e:
        st.error(f"Error connecting to EGX Data: {e}")
        return []

# 4. التحكم في التشغيل
st.write("")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button('EXECUTE MARKET SCAN', use_container_width=True):
        with st.spinner('Synchronizing with EGX Live Data...'):
            data = run_master_scan()
            
            if data:
                st.success(f"Successfully analyzed all assets. Found {len(data)} opportunities.")
                df = pd.DataFrame(data)
                
                # عرض النتائج في جدول
                st.markdown("### <div class='status-indicator'></div> Identified Growth Opportunities", unsafe_allow_html=True)
                st.table(df)
                
                # قسم خاص للأسهم القوية جداً
                strong = df[df['Signal'] == "STRONG BUY"]
                if not strong.empty:
                    st.divider()
                    st.markdown("### 🚀 Institutional Priority (Strong Buy)")
                    st.table(strong)
            else:
                st.warning("No buying signals detected at this moment.")

# 5. القسم القانوني
st.markdown("""
    <div class="disclaimer">
        <strong>إخلاء مسؤولية:</strong> هذا الكود للأغراض التعليمية والفنية فقط. 
        الاستثمار في البورصة ينطوي على مخاطر، والقرار النهائي مسؤوليتك الشخصية.
    </div>
""", unsafe_allow_html=True)

st.divider()
st.caption(f"WAHBA EGX | LOCAL TERMINAL | {time.strftime('%Y')} | STABLE VERSION")
