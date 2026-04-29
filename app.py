import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Wahba Pro Terminal", layout="wide")

# تصميم احترافي
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1a1a1a; }
    div.stButton > button { background-color: #333; color: white; width: 100%; }
    </style>
""", unsafe_allow_html=True)

st.title("Wahba Pro Market Terminal")

tickers = [
    "ABUK.CA", "ACGC.CA", "ADCI.CA", "ADIB.CA", "AFMC.CA", "AIH.CA", "AIVC.CA", "AMER.CA", "AMOC.CA", "ANFI.CA", 
    "APME.CA", "ARAB.CA", "ASPI.CA", "ASRE.CA", "ASU.CA", "ATLC.CA", "ATWB.CA", "AUCC.CA", "AXPH.CA", "BINP.CA", 
    "BINV.CA", "BIOC.CA", "BLGN.CA", "BMOH.CA", "BTFH.CA", "CAED.CA", "CAFR.CA", "CAPW.CA", "CCAP.CA", "CERA.CA", 
    "CFGH.CA", "CHWP.CA", "CICH.CA", "CIRA.CA", "CLHO.CA", "CNCR.CA", "CNFR.CA", "COMI.CA", "COPR.CA", "CSAG.CA", 
    "CVLC.CA", "DAPH.CA", "DCRC.CA", "DCTL.CA", "DOMT.CA", "EALR.CA", "EATM.CA", "EBSC.CA", "ECAP.CA", "ECHG.CA", 
    "ECOS.CA", "EDAB.CA", "EDIN.CA", "EFID.CA", "EGAS.CA", "EGBE.CA", "EGCH.CA", "EGDC.CA", "EGDH.CA", "EGFI.CA", 
    "EGID.CA", "EGLI.CA", "EGSG.CA", "EGTB.CA", "EHDR.CA", "EIMC.CA", "EIPC.CA", "EKHO.CA", "ELKA.CA", "ELSH.CA", 
    "EMFD.CA", "ENGC.CA", "EPCO.CA", "ESIC.CA", "ESRS.CA", "ETEL.CA", "EXPA.CA", "FAHL.CA", "FAIT.CA", "FCIE.CA", 
    "FIIT.CA", "FWRY.CA", "GTHE.CA", "GZCC.CA", "HELI.CA", "HERO.CA", "HRHO.CA", "IFAP.CA", "IHCX.CA", "INFI.CA", 
    "IRGC.CA", "ISDI.CA", "ISPH.CA", "JUFO.CA", "KABO.CA", "KIMA.CA", "LREI.CA", "MACRO.CA", "MASR.CA", "MDWA.CA", 
    "MEPA.CA", "MFPC.CA", "MNHD.CA", "MPCO.CA", "MTIE.CA", "OBET.CA", "ODPD.CA", "ODIN.CA", "OIH.CA", "OPAT.CA", 
    "ORAS.CA", "ORHD.CA", "ORWE.CA", "PHDC.CA", "PIOH.CA", "PRDC.CA", "PSDC.CA", "QNBA.CA", "RAFT.CA", "RMDA.CA", 
    "RTVC.CA", "SAEI.CA", "SCFM.CA", "SEMO.CA", "SHAC.CA", "SIAG.CA", "SKPC.CA", "SPHT.CA", "SVCP.CA", "SWDY.CA", 
    "SYVI.CA", "TAQA.CA", "TMGH.CA", "TRGO.CA", "UEGC.CA", "UNTR.CA", "UPLD.CA", "UTOP.CA", "VIRA.CA", "ZEIRA.CA"
]

@st.cache_data(ttl=3600)
def load_all_data():
    # التحميل الجماعي
    data = yf.download(tickers, period="6mo", interval="1d", group_by='ticker', progress=False)
    results = []
    for ticker in tickers:
        try:
            df = data[ticker]
            if not df.empty and len(df) >= 50:
                ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
                results.append({
                    "Symbol": ticker.replace(".CA", ""),
                    "Price": round(float(df['Close'].iloc[-1]), 2),
                    "MA50": round(float(ma50), 2),
                    "Trend": "Bullish" if df['Close'].iloc[-1] > ma50 else "Bearish"
                })
        except: continue
    return pd.DataFrame(results)

df = load_all_data()

# إضافة زرار فلتر
show_only_bullish = st.checkbox("إظهار الأسهم الصاعدة فوق الـ 50 فقط")

if show_only_bullish:
    st.table(df[df['Trend'] == 'Bullish'])
else:
    st.table(df)
