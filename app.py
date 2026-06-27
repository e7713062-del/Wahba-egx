import os
import re
from datetime import datetime
import pytz
import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup
from tradingview_ta import TA_Handler, Interval

APP_NAME = "Wahba Intelligence"
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

egypt_tz = pytz.timezone("Africa/Cairo")
now_egypt = datetime.now(egypt_tz)

st.set_page_config(
    page_title=APP_NAME,
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; }
.stApp { background: linear-gradient(180deg, #08111f 0%, #0d1728 100%); color: #f5f7fb; }
.hero {
    padding: 28px;
    border-radius: 22px;
    background: linear-gradient(135deg, rgba(12,20,36,.95), rgba(20,31,52,.92));
    border: 1px solid rgba(255,255,255,.08);
    box-shadow: 0 10px 30px rgba(0,0,0,.25);
    margin-bottom: 18px;
}
.hero h1 { margin: 0; font-size: 34px; font-weight: 900; color: #ffffff; }
.hero p { margin: 8px 0 0 0; color: #9fb2d0; font-size: 14px; }
.section-card {
    padding: 18px;
    border-radius: 18px;
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(255,255,255,.08);
    box-shadow: 0 8px 24px rgba(0,0,0,.16);
}
.small-label { color: #8ea3c6; font-size: 12px; margin-bottom: 4px; }
.big-value { color: #ffffff; font-size: 24px; font-weight: 900; margin: 0; }
div[data-testid="stMetric"] {
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(255,255,255,.08);
    padding: 16px;
    border-radius: 18px;
    box-shadow: 0 8px 24px rgba(0,0,0,.12);
}
div[data-testid="stMetricLabel"] { color: #9fb2d0 !important; }
div[data-testid="stMetricValue"] { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

if "scan_results" not in st.session_state:
    st.session_state.scan_results = []
if "news_items" not in st.session_state:
    st.session_state.news_items = []
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

@st.cache_data(ttl=86400)
def get_egx_listed_symbols():
    symbols = set()
    sources = [
        "https://egx.com.eg/en/Maps_ListedCo.aspx",
        "https://www.egx.com.eg/get_pdf.aspx?ID=3848&Lang=ENG",
    ]
    for url in sources:
        try:
            r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            found = re.findall(r"\b[A-Z]{2,6}.CA\b", r.text)
            for s in found:
                symbols.add(s.replace(".CA", ""))
        except:
            pass
    return sorted(list(symbols))

@st.cache_data(ttl=3600)
def get_egx_news():
    news = []
    sources = [
        "https://www.egx.com.eg",
        "https://www.alborsaanews.com/tag/%D8%A7%D9%84%D8%A8%D9%88%D8%B1%D8%B5%D8%A9-%D8%A7%D9%84%D9%85%D8%B5%D8%B1%D9%8A%D8%A9",
    ]
    for url in sources:
        try:
            r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.find_all("a", href=True):
                txt = a.get_text(" ", strip=True)
                href = a["href"]
                if len(txt) > 10:
                    news.append({"title": txt[:200], "url": href})
        except:
            pass
    seen = set()
    clean = []
    for n in news:
        key = (n["title"], n["url"])
        if key not in seen:
            seen.add(key)
            clean.append(n)
    return clean[:50]

def sentiment_score(text):
    pos = ["ربح", "ارتفاع", "زيادة", "نمو", "موافقة", "إيجابي", "تحسن", "توسع", "عقد", "قفزة"]
    neg = ["هبوط", "خسارة", "تراجع", "إيقاف", "عقوبة", "سلبية", "تعثر", "انخفاض", "نزاع"]
    t = text.lower()
    score = 0
    for w in pos:
        if w in t:
            score += 1
    for w in neg:
        if w in t:
            score -= 1
    return score

def analyze_symbol(symbol, interval):
    try:
        handler = TA_Handler(symbol=symbol, exchange="EGX", screener="egypt", interval=interval)
        return handler.get_analysis()
    except:
        return None

def extract_result(analysis):
    if analysis is None:
        return {}
    return {
        "RECOMMENDATION": analysis.summary.get("RECOMMENDATION"),
        "RSI": analysis.indicators.get("RSI"),
        "MACD": analysis.indicators.get("MACD.macd"),
        "MACD_SIGNAL": analysis.indicators.get("MACD.signal"),
        "CLOSE": analysis.indicators.get("close"),
        "S1": analysis.indicators.get("pivot.M.Classic.S1"),
        "P": analysis.indicators.get("pivot.M.Classic.P"),
        "R1": analysis.indicators.get("pivot.M.Classic.R1"),
        "EMA20": analysis.indicators.get("EMA20"),
        "EMA50": analysis.indicators.get("EMA50"),
        "SMA20": analysis.indicators.get("SMA20"),
        "SMA50": analysis.indicators.get("SMA50"),
    }

def score_snapshot(d):
    score = 0
    rec = str(d.get("RECOMMENDATION", "")).upper()
    if rec in ["BUY", "STRONG_BUY"]:
        score += 2
    elif rec in ["SELL", "STRONG_SELL"]:
        score -= 2
    rsi = d.get("RSI")
    if rsi is not None:
        if 50 <= rsi <= 70:
            score += 1
        elif rsi < 30:
            score += 1
        elif rsi > 75:
            score -= 1
    macd = d.get("MACD")
    sig = d.get("MACD_SIGNAL")
    if macd is not None and sig is not None:
        score += 1 if macd > sig else -1
    close = d.get("CLOSE")
    s1 = d.get("S1")
    r1 = d.get("R1")
    p = d.get("P")
    if close is not None and s1 is not None and r1 is not None:
        if s1 <= close <= r1:
            score += 1
        if p is not None and close > p:
            score += 1
    return score

def decide_from_score(total):
    if total >= 6:
        return "Strong Buy"
    if total >= 3:
        return "Buy"
    if total >= 1:
        return "Watch"
    return "Avoid"

def full_scan(symbol):
    weekly = extract_result(analyze_symbol(symbol, Interval.INTERVAL_1_WEEK))
    daily = extract_result(analyze_symbol(symbol, Interval.INTERVAL_1_DAY))
    w_score = score_snapshot(weekly)
    d_score = score_snapshot(daily)
    total = (w_score * 2) + d_score
    return {
        "symbol": symbol,
        "weekly": weekly,
        "daily": daily,
        "weekly_score": w_score,
        "daily_score": d_score,
        "total_score": total,
        "decision": decide_from_score(total),
    }

@st.cache_data(ttl=21600)
def scan_market(symbols, limit=50):
    return [full_scan(s) for s in symbols[:limit]]

def save_snapshot_df(df, filename_prefix="market_snapshot"):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(CACHE_DIR, f"{filename_prefix}_{ts}.csv")
    df.to_csv(path, index=False)
    return path

def build_top_df(results):
    rows = []
    for x in results:
        rows.append({
            "Symbol": x["symbol"],
            "Decision": x["decision"],
            "Score": x["total_score"],
            "Weekly Rec": x["weekly"].get("RECOMMENDATION") if x["weekly"] else None,
            "Daily Rec": x["daily"].get("RECOMMENDATION") if x["daily"] else None,
            "Weekly RSI": x["weekly"].get("RSI") if x["weekly"] else None,
            "Daily RSI": x["daily"].get("RSI") if x["daily"] else None,
            "Weekly MACD": x["weekly"].get("MACD") if x["weekly"] else None,
            "Daily MACD": x["daily"].get("MACD") if x["daily"] else None,
        })
    if not rows:
        return pd.DataFrame(columns=["Symbol", "Decision", "Score"])
    return pd.DataFrame(rows).sort_values("Score", ascending=False)

def build_news_df(items):
    rows = []
    for n in items:
        rows.append({
            "Title": n["title"],
            "URL": n["url"],
            "Sentiment": sentiment_score(n["title"]),
        })
    if not rows:
        return pd.DataFrame(columns=["Title", "URL", "Sentiment"])
    return pd.DataFrame(rows).sort_values("Sentiment", ascending=False)

symbols = get_egx_listed_symbols()
news_items = get_egx_news()

st.markdown(f"""
<div class="hero">
    <h1>Wahba Intelligence</h1>
    <p>Egyptian Exchange Intelligence Platform · Last update: {now_egypt.strftime("%Y-%m-%d %H:%M")} Cairo Time</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("Control Panel")
    view = st.radio("Navigation", ["Overview", "Screener", "News", "Indices", "Watchlist"])
    scan_limit = st.slider("Scan limit", 10, 200, 50, 10)
    show_only_signal = st.checkbox("Show only Buy / Strong Buy", value=False)
    run_scan = st.button("Run Full Scan")
    refresh_news = st.button("Refresh News")
    st.caption(f"Symbols loaded: {len(symbols)}")
    st.caption(f"News loaded: {len(news_items)}")

if run_scan and symbols:
    st.session_state.scan_results = scan_market(symbols, limit=scan_limit)
    top_df = build_top_df(st.session_state.scan_results)
    save_snapshot_df(top_df, "scan_results")
    st.success("Scan completed successfully.")

if refresh_news:
    st.session_state.news_items = get_egx_news()
    st.success("News refreshed successfully.")

results = st.session_state.scan_results
news = st.session_state.news_items if st.session_state.news_items else news_items

if view == "Overview":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Listed Symbols", len(symbols))
    c2.metric("News Items", len(news))
    c3.metric("Scanned", len(results))
    c4.metric("Top Opportunities", len([x for x in results if x["decision"] in ["Buy", "Strong Buy"]]))
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Market Snapshot")
    if results:
        df = build_top_df(results)
        if show_only_signal:
            df = df[df["Decision"].isin(["Buy", "Strong Buy", "Watch"])]
        st.dataframe(df, use_container_width=True)
        st.divider()
        if not df.empty:
            best = df.iloc[0]
            st.markdown(f"""
            <div class="small-label">Best Current Idea</div>
            <div class="big-value">{best['Symbol']} · {best['Decision']}</div>
            """, unsafe_allow_html=True)
    else:
        st.info("Run a scan to populate the dashboard.")
    st.markdown("</div>", unsafe_allow_html=True)

elif view == "Screener":
    st.subheader("Stock Screener")
    if results:
        df = build_top_df(results)
        if show_only_signal:
            df = df[df["Decision"].isin(["Buy", "Strong Buy"])]
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No results found. Run a scan first.")

elif view == "News":
    st.subheader("EGX News")
    df = build_news_df(news)
    st.dataframe(df, use_container_width=True)
    st.divider()
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.write("### Positive News Filter")
    st.dataframe(df[df["Sentiment"] > 0], use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif view == "Indices":
    st.subheader("EGX30 / EGX70")
    st.info("اربط رموز المؤشرات من مزود البيانات، ثم شغّل نفس الـ engine على المؤشرين بنفس منطق weekly ثم daily.")
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.write("### Implementation Notes")
    st.write("- Use the same technical engine.")
    st.write("- Store a daily snapshot after close.")
    st.write("- Show trend, RSI, MACD, and support/resistance for each index.")
    st.markdown("</div>", unsafe_allow_html=True)

elif view == "Watchlist":
    st.subheader("Watchlist")
    if not st.session_state.watchlist:
        st.info("Watchlist is empty.")
    else:
        st.dataframe(pd.DataFrame(st.session_state.watchlist), use_container_width=True)

st.caption("Built for Egyptian Exchange market intelligence with a corporate dashboard style.")
