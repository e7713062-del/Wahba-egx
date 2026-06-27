import os
import re
import logging
from datetime import datetime, timedelta
import pytz
import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup
from tradingview_ta import TA_Handler, Interval
from streamlit_autorefresh import st_autorefresh

APP_NAME = "Wahba Intelligence"
CACHE_DIR = "cache"
EXPORT_DIR = "exports"
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("wahba")

egypt_tz = pytz.timezone("Africa/Cairo")

EGX_LISTED_URL = "https://www.egx.com.eg/en/listedstocks.aspx"
EGX_MARKET_URL = "https://www.egx.com.eg/en/MarketIndicator.aspx"
EGX_MAP_URL = "https://egx.com.eg/en/Maps_ListedCo.aspx"
EGX30_METHOD_URL = "https://www.egx.com.eg/getdoc/e824310c-884d-4700-9153-0f16526e839e/EGX30-Methodology_en-Jan-2025.aspx"

def egypt_now():
    return datetime.now(egypt_tz)

def http_get(url, timeout=25):
    headers = {"User-Agent": "Mozilla/5.0"}
    return requests.get(url, timeout=timeout, headers=headers)

def normalize_symbol(sym):
    return str(sym).strip().upper().replace(".CA", "")

def parse_number(x):
    if x is None:
        return None
    s = str(x).strip().replace(",", "")
    mult = 1
    if s.endswith(("K", "k")):
        mult = 1_000
        s = s[:-1]
    elif s.endswith(("M", "m")):
        mult = 1_000_000
        s = s[:-1]
    elif s.endswith(("B", "b")):
        mult = 1_000_000_000
        s = s[:-1]
    try:
        return float(s) * mult
    except:
        return None

st.set_page_config(
    page_title=APP_NAME,
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st_autorefresh(interval=15 * 60 * 1000, limit=None, key="market_autorefresh")

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
    margin-bottom: 18px;
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
if "last_auto_scan" not in st.session_state:
    st.session_state.last_auto_scan = None

@st.cache_data(ttl=86400)
def get_egx_listed_symbols():
    symbols = set()
    sources = [EGX_LISTED_URL, EGX_MAP_URL]
    for url in sources:
        try:
            r = http_get(url)
            found = re.findall(r"\b[A-Z]{2,6}.CA\b", r.text)
            for s in found:
                symbols.add(normalize_symbol(s))
        except Exception as e:
            logger.warning("symbol source failed %s %s", url, e)
    return sorted(symbols)

@st.cache_data(ttl=21600)
def get_egx_sector_liquidity():
    try:
        r = http_get(EGX_MARKET_URL)
        soup = BeautifulSoup(r.text, "html.parser")
        rows = []
        for tr in soup.find_all("tr"):
            cols = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
            if len(cols) >= 4:
                val = parse_number(cols[1])
                if val is not None:
                    rows.append({
                        "Sector": cols[0],
                        "Value": val,
                        "Change": cols[2],
                        "Pct": cols[3],
                    })
        df = pd.DataFrame(rows)
        if not df.empty:
            df = df.sort_values("Value", ascending=False).reset_index(drop=True)
            df["Liquidity Rank"] = df.index + 1
            return df
    except Exception as e:
        logger.warning("sector parse failed %s", e)

    fallback = [
        ("Trade & Distributors", 9959.47, "-112.22", "-1.11%"),
        ("Industrial Goods, Services and Automobiles", 9067.17, "-12.28", "-0.14%"),
        ("Building Materials", 4680.21, "8.20", "0.18%"),
        ("Education Services", 4379.93, "-30.73", "-0.70%"),
        ("Textile & Durables", 4464.29, "-16.02", "-0.36%"),
        ("Travel & Leisure", 4132.12, "1.92", "0.05%"),
        ("Contracting & Construction Engineering", 3782.76, "40.01", "1.07%"),
        ("Shipping & Transportation Services", 3704.75, "29.67", "0.81%"),
        ("Real Estate", 3399.28, "39.62", "1.18%"),
        ("IT, Media & Communication Services", 3023.25, "27.17", "0.91%"),
        ("Banks", 2817.09, "11.41", "0.41%"),
        ("Paper & Packaging", 2454.04, "-250.91", "-9.28%"),
        ("Food, Beverages and Tobacco", 2400.33, "6.14", "0.26%"),
        ("Non-bank financial services", 1636.33, "5.32", "0.33%"),
        ("Health Care & Pharmaceuticals", 1522.78, "7.65", "0.50%"),
        ("Energy & Support Services", 806.39, "7.36", "0.92%"),
    ]
    df = pd.DataFrame(fallback, columns=["Sector", "Value", "Change", "Pct"])
    df["Liquidity Rank"] = range(1, len(df) + 1)
    return df

@st.cache_data(ttl=3600)
def get_egx_news():
    news = []
    sources = [
        "https://www.egx.com.eg",
        "https://www.alborsaanews.com/tag/%D8%A7%D9%84%D8%A8%D9%88%D8%B1%D8%B5%D8%A9-%D8%A7%D9%84%D9%85%D8%B5%D8%B1%D9%8A%D8%A9",
    ]
    for url in sources:
        try:
            r = http_get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.find_all("a", href=True):
                txt = a.get_text(" ", strip=True)
                href = a["href"]
                if len(txt) > 15:
                    if href.startswith("/"):
                        href = requests.compat.urljoin(url, href)
                    news.append({"title": txt[:200], "url": href})
        except Exception as e:
            logger.warning("news failed %s %s", url, e)
    seen = set()
    out = []
    for n in news:
        key = (n["title"], n["url"])
        if key not in seen:
            seen.add(key)
            out.append(n)
    return out[:50]

def sentiment_score(text):
    pos = ["ربح", "ارتفاع", "زيادة", "نمو", "موافقة", "إيجابي", "تحسن", "توسع", "عقد", "قفزة"]
    neg = ["هبوط", "خسارة", "تراجع", "إيقاف", "عقوبة", "سلبية", "تعثر", "انخفاض", "نزاع"]
    t = str(text).lower()
    return sum(w in t for w in pos) - sum(w in t for w in neg)

def analyze_symbol(symbol, interval):
    try:
        handler = TA_Handler(symbol=symbol, exchange="EGX", screener="egypt", interval=interval)
        return handler.get_analysis()
    except Exception as e:
        logger.warning("analysis failed %s %s %s", symbol, interval, e)
        return None

def extract_result(analysis):
    if analysis is None:
        return {}
    ind = analysis.indicators or {}
    summ = analysis.summary or {}
    return {
        "RECOMMENDATION": summ.get("RECOMMENDATION"),
        "RSI": ind.get("RSI"),
        "MACD": ind.get("MACD.macd"),
        "MACD_SIGNAL": ind.get("MACD.signal"),
        "CLOSE": ind.get("close"),
        "S1": ind.get("pivot.M.Classic.S1"),
        "P": ind.get("pivot.M.Classic.P"),
        "R1": ind.get("pivot.M.Classic.R1"),
        "EMA20": ind.get("EMA20"),
        "EMA50": ind.get("EMA50"),
        "SMA20": ind.get("SMA20"),
        "SMA50": ind.get("SMA50"),
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
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=["Symbol", "Decision", "Score"])
    return df.sort_values("Score", ascending=False)

def build_news_df(items):
    rows = []
    for n in items:
        rows.append({
            "Title": n["title"],
            "URL": n["url"],
            "Sentiment": sentiment_score(n["title"]),
        })
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=["Title", "URL", "Sentiment"])
    return df.sort_values("Sentiment", ascending=False)

def save_snapshot_df(df, filename_prefix="market_snapshot"):
    ts = egypt_now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(EXPORT_DIR, f"{filename_prefix}_{ts}.csv")
    df.to_csv(path, index=False)
    return path

def normalize_symbol(x):
    return str(x).strip().upper().replace(".CA", "")

def refresh_data(scan_limit, symbols):
    st.session_state.scan_results = scan_market(symbols, limit=scan_limit)
    st.session_state.news_items = get_egx_news()
    st.session_state.last_auto_scan = egypt_now()

def build_watchlist_df(watchlist, results):
    rows = []
    for sym in watchlist:
        row = {"Symbol": sym}
        match = next((x for x in results if x["symbol"] == sym), None)
        if match:
            row["Decision"] = match["decision"]
            row["Score"] = match["total_score"]
            row["Daily Rec"] = match["daily"].get("RECOMMENDATION") if match["daily"] else None
            row["Weekly Rec"] = match["weekly"].get("RECOMMENDATION") if match["weekly"] else None
        rows.append(row)
    df = pd.DataFrame(rows)
    return df if not df.empty else pd.DataFrame(columns=["Symbol", "Decision", "Score"])

@st.cache_data(ttl=43200)
def get_index_analysis(symbol):
    try:
        handler = TA_Handler(symbol=symbol, exchange="EGX", screener="egypt", interval=Interval.INTERVAL_1_DAY)
        return extract_result(handler.get_analysis())
    except Exception:
        return {}

symbols = get_egx_listed_symbols()
news_items = get_egx_news()
sector_df = get_egx_sector_liquidity()

if not st.session_state.scan_results:
    refresh_data(50, symbols)

st.markdown(f"""
<div class="hero">
    <h1>Wahba Intelligence</h1>
    <p>Egyptian Exchange Intelligence Platform · Auto-updated every 15 minutes · Last update: {egypt_now().strftime("%Y-%m-%d %H:%M")} Cairo Time</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("Control Panel")
    view = st.radio("Navigation", ["Overview", "Screener", "News", "Indices", "Watchlist", "Sectors"])
    scan_limit = st.slider("Max symbols in auto scan", 10, 200, 50, 10)
    show_only_signal = st.checkbox("Show only Buy / Strong Buy", value=False)
    force_refresh = st.button("Force Refresh Now")
    export_now = st.button("Export CSV")
    add_symbol = st.text_input("Add to watchlist")
    add_btn = st.button("Add Symbol")
    remove_symbol = st.text_input("Remove from watchlist")
    remove_btn = st.button("Remove Symbol")
    st.caption(f"Symbols loaded: {len(symbols)}")
    st.caption(f"News loaded: {len(news_items)}")
    if st.session_state.last_auto_scan:
        st.caption(f"Last auto scan: {st.session_state.last_auto_scan.strftime('%Y-%m-%d %H:%M')}")

if force_refresh:
    refresh_data(scan_limit, symbols)
    st.success("Refreshed successfully.")

if export_now:
    save_snapshot_df(build_top_df(st.session_state.scan_results), "scan_results")
    save_snapshot_df(build_news_df(st.session_state.news_items), "news")
    save_snapshot_df(sector_df, "sectors")
    save_snapshot_df(build_watchlist_df(st.session_state.watchlist, st.session_state.scan_results), "watchlist")
    st.success("Exported CSV files.")

if add_btn and add_symbol:
    sym = normalize_symbol(add_symbol)
    if sym not in st.session_state.watchlist:
        st.session_state.watchlist.append(sym)

if remove_btn and remove_symbol:
    sym = normalize_symbol(remove_symbol)
    st.session_state.watchlist = [x for x in st.session_state.watchlist if x != sym]

if symbols and egypt_now().minute % 15 == 0:
    if st.session_state.last_auto_scan is None or (egypt_now() - st.session_state.last_auto_scan) >= timedelta(minutes=15):
        refresh_data(scan_limit, symbols)

results = st.session_state.scan_results
news = st.session_state.news_items if st.session_state.news_items else news_items
best_sector = sector_df.iloc[0] if not sector_df.empty else None

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
        if not df.empty:
            best = df.iloc[0]
            st.markdown(f"""
            <div class="small-label">Best Current Idea</div>
            <div class="big-value">{best['Symbol']} · {best['Decision']}</div>
            """, unsafe_allow_html=True)
    else:
        st.info("Data is loading automatically.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Most Liquid Sector")
    if best_sector is not None:
        st.metric("Highest liquidity", best_sector["Sector"])
        st.metric("Sector value", f"{best_sector['Value']:.2f}")
        st.dataframe(sector_df, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif view == "Screener":
    st.subheader("Stock Screener")
    if results:
        df = build_top_df(results)
        if show_only_signal:
            df = df[df["Decision"].isin(["Buy", "Strong Buy"])]
        st.dataframe(df, use_container_width=True)

elif view == "News":
    st.subheader("EGX News")
    df = build_news_df(news)
    st.dataframe(df, use_container_width=True)
    st.divider()
    st.subheader("Positive News Filter")
    st.dataframe(df[df["Sentiment"] > 0], use_container_width=True)

elif view == "Indices":
    st.subheader("EGX30 / EGX70")
    egx30 = get_index_analysis("EGX30")
    egx70 = get_index_analysis("EGX70")
    col1, col2 = st.columns(2)
    with col1:
        st.write("EGX30")
        st.json(egx30)
    with col2:
        st.write("EGX70")
        st.json(egx70)

elif view == "Watchlist":
    st.subheader("Watchlist")
    if not st.session_state.watchlist:
        st.info("Watchlist is empty.")
    else:
        wl_df = build_watchlist_df(st.session_state.watchlist, results)
        st.dataframe(wl_df, use_container_width=True)

elif view == "Sectors":
    st.subheader("Sector Liquidity")
    st.dataframe(sector_df, use_container_width=True)
    if best_sector is not None:
        st.success(f"أعلى قطاع سيولة حاليًا: {best_sector['Sector']} — {best_sector['Value']:.2f}")

st.caption("Built for Egyptian Exchange market intelligence with a corporate dashboard style.")
