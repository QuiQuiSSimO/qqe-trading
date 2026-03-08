# HECTOR PATTERN DETECTOR
# Sistema de Reconocimiento de Patrones — by Hector Trading
# Activos: XAU/USD, EUR/USD, GBP/USD, NAS100, BTC/USD, Crude Oil
# Patrones: 8 patrones profesionales en M15 con filtro H1
#
# INSTALACION: pip install streamlit requests pandas numpy yfinance
# EJECUCION:   streamlit run hector_pattern_detector.py

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
import requests
import time

st.set_page_config(
    page_title="Hector Pattern Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================================================
# CSS
# ================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=Share+Tech+Mono&family=Inter:wght@400;500;600&display=swap');

html, body, .stApp { background:#0a0f1e !important; }
.stApp { font-family:'Inter',sans-serif; color:#e2e8f0; }
[data-testid="stSidebar"] { background:#0f172a !important; border-right:1px solid #1e293b !important; }

.stTabs [data-baseweb="tab-list"] { background:#0f172a; border-bottom:2px solid #1e293b; }
.stTabs [data-baseweb="tab"] {
    background:transparent; color:#475569 !important;
    font-family:'Share Tech Mono',monospace; font-size:11px;
    letter-spacing:1px; padding:10px 16px; border:none;
}
.stTabs [aria-selected="true"] {
    background:#0a0f1e !important; color:#f1f5f9 !important;
    border-bottom:2px solid #c8920a !important; font-weight:700 !important;
}

.card { background:#0f172a; border:1px solid #1e293b; border-radius:10px; padding:16px; margin-bottom:10px; }
.card-gold   { border-left:4px solid #c8920a; }
.card-green  { border-left:4px solid #065f46; }
.card-red    { border-left:4px solid #991b1b; }
.card-blue   { border-left:4px solid #1e3a8a; }
.card-purple { border-left:4px solid #5b21b6; }

.kpi { background:#0f172a; border:1px solid #1e293b; border-radius:10px; padding:14px; text-align:center; }
.kpi-label { font-family:'Share Tech Mono',monospace; font-size:9px; color:#475569; letter-spacing:2px; margin-bottom:6px; }
.kpi-value { font-family:'Rajdhani',sans-serif; font-size:30px; font-weight:700; line-height:1.1; }
.kpi-sub   { font-family:'Share Tech Mono',monospace; font-size:9px; color:#475569; margin-top:3px; }

.sec { font-family:'Share Tech Mono',monospace; font-size:10px; color:#475569; letter-spacing:3px; border-bottom:1px solid #1e293b; padding-bottom:6px; margin:16px 0 12px; }

.pattern-card {
    background:#0f172a; border:1px solid #1e293b; border-radius:10px;
    padding:16px; margin-bottom:10px; transition:border-color 0.2s;
}
.pattern-card.bullish { border-left:4px solid #065f46; }
.pattern-card.bearish { border-left:4px solid #991b1b; }
.pattern-card.neutral { border-left:4px solid #c8920a; }

.conf-bar { height:8px; background:#1e293b; border-radius:4px; overflow:hidden; margin:6px 0; }
.conf-fill-green  { height:100%; border-radius:4px; background:linear-gradient(90deg,#065f46,#22c55e); }
.conf-fill-red    { height:100%; border-radius:4px; background:linear-gradient(90deg,#991b1b,#ef4444); }
.conf-fill-gold   { height:100%; border-radius:4px; background:linear-gradient(90deg,#92400e,#c8920a); }

.badge { display:inline-block; padding:3px 10px; border-radius:20px; font-family:'Share Tech Mono',monospace; font-size:9px; font-weight:700; }
.badge-green  { background:#064e3b; color:#34d399; border:1px solid #065f46; }
.badge-red    { background:#7f1d1d; color:#f87171; border:1px solid #991b1b; }
.badge-gold   { background:#451a03; color:#fbbf24; border:1px solid #92400e; }
.badge-blue   { background:#1e3a8a; color:#93c5fd; border:1px solid #1e40af; }
.badge-gray   { background:#1e293b; color:#94a3b8; border:1px solid #334155; }
.badge-purple { background:#2e1065; color:#c4b5fd; border:1px solid #5b21b6; }

.asset-row {
    background:#0f172a; border:1px solid #1e293b; border-radius:8px;
    padding:12px 16px; margin-bottom:8px; display:flex;
    align-items:center; justify-content:space-between;
}
.asset-name { font-family:'Rajdhani',sans-serif; font-weight:700; font-size:18px; color:#f1f5f9; }
.asset-price { font-family:'Share Tech Mono',monospace; font-size:12px; color:#94a3b8; }

.alert-card {
    border-radius:10px; padding:16px; margin-bottom:10px;
    border:1px solid; animation:pulse-border 2s infinite;
}
.alert-bull { background:#022c22; border-color:#065f46; }
.alert-bear { background:#2d0d0d; border-color:#991b1b; }

@keyframes pulse-border {
    0%,100% { box-shadow: 0 0 0 0 rgba(200,146,10,0); }
    50% { box-shadow: 0 0 0 4px rgba(200,146,10,0.15); }
}

.scan-status {
    display:flex; align-items:center; gap:8px;
    font-family:'Share Tech Mono',monospace; font-size:10px;
}
.scan-dot {
    width:8px; height:8px; border-radius:50%;
    animation:blink 1s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

.hector-brand {
    background:linear-gradient(135deg, #0f172a, #1e293b);
    border:1px solid #c8920a;
    border-radius:12px;
    padding:20px;
    text-align:center;
    margin-bottom:16px;
}

.stButton>button {
    background:#c8920a !important; color:#0a0f1e !important;
    border:none !important; border-radius:6px !important;
    font-family:'Share Tech Mono',monospace !important;
    font-size:11px !important; letter-spacing:1px !important;
    font-weight:700 !important;
}
.stButton>button:hover { background:#a37208 !important; }
.stSelectbox>div>div { background:#0f172a !important; border:1px solid #1e293b !important; color:#f1f5f9 !important; }
.stNumberInput>div>div>input { background:#0f172a !important; border:1px solid #1e293b !important; color:#f1f5f9 !important; }

::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-track { background:#0a0f1e; }
::-webkit-scrollbar-thumb { background:#1e293b; border-radius:2px; }
</style>
""", unsafe_allow_html=True)

# ================================================================
# SESSION STATE
# ================================================================
if "scan_results" not in st.session_state: st.session_state.scan_results = []
if "last_scan"    not in st.session_state: st.session_state.last_scan = None
if "alerts"       not in st.session_state: st.session_state.alerts = []
if "api_key"      not in st.session_state: st.session_state.api_key = ""
if "auto_scan"    not in st.session_state: st.session_state.auto_scan = False

# ================================================================
# ASSETS CONFIG
# ================================================================
ASSETS = {
    "XAU/USD":   {"yahoo": "GC=F",   "color": "#c8920a", "tipo": "Commodity", "spread": 0.30},
    "EUR/USD":   {"yahoo": "EURUSD=X","color": "#1d4ed8", "tipo": "Forex",     "spread": 0.0001},
    "GBP/USD":   {"yahoo": "GBPUSD=X","color": "#6d28d9", "tipo": "Forex",     "spread": 0.0002},
    "NAS100":    {"yahoo": "NQ=F",    "color": "#0891b2", "tipo": "Index",     "spread": 1.0},
    "BTC/USD":   {"yahoo": "BTC-USD", "color": "#f59e0b", "tipo": "Crypto",    "spread": 5.0},
    "CRUDE OIL": {"yahoo": "CL=F",   "color": "#16a34a", "tipo": "Commodity", "spread": 0.05},
}

PATTERNS = {
    "Engulfing + EMA":       {"efectividad": 72, "desc": "Vela envolvente en EMA100/200"},
    "Pin Bar en SR":         {"efectividad": 70, "desc": "Mecha larga en soporte/resistencia"},
    "Fakey":                 {"efectividad": 66, "desc": "Falsa ruptura con reversion"},
    "Divergencia RSI":       {"efectividad": 68, "desc": "Precio vs RSI divergen"},
    "Inside Bar Breakout":   {"efectividad": 67, "desc": "Compresion + ruptura de rango"},
    "Three Soldiers/Crows":  {"efectividad": 63, "desc": "3 velas consecutivas de momentum"},
    "Morning/Evening Star":  {"efectividad": 65, "desc": "Patron 3 velas de agotamiento"},
    "Consolidacion Ruptura": {"efectividad": 64, "desc": "Flag/Pennant post-impulso"},
}

# ================================================================
# DATA FETCHING
# ================================================================
@st.cache_data(ttl=300)
def fetch_data(symbol_yahoo, period="60d", interval="15m"):
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol_yahoo)
        df = ticker.history(period=period, interval=interval)
        if df.empty:
            return None
        df = df[["Open","High","Low","Close","Volume"]].copy()
        df.columns = ["open","high","low","close","volume"]
        df = df.dropna()
        return df
    except Exception as e:
        return None

def fetch_data_alpha(symbol, api_key_alpha):
    try:
        url = f"https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol={symbol[:3]}&to_symbol={symbol[4:]}&interval=15min&outputsize=full&apikey={api_key_alpha}"
        r = requests.get(url, timeout=10)
        data = r.json()
        ts = data.get("Time Series FX (15min)", {})
        if not ts:
            return None
        rows = []
        for dt, vals in ts.items():
            rows.append({
                "datetime": pd.to_datetime(dt),
                "open":  float(vals["1. open"]),
                "high":  float(vals["2. high"]),
                "low":   float(vals["3. low"]),
                "close": float(vals["4. close"]),
                "volume": 0
            })
        df = pd.DataFrame(rows).sort_values("datetime").reset_index(drop=True)
        return df
    except:
        return None

# ================================================================
# PATTERN DETECTION FUNCTIONS
# ================================================================
def calc_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def calc_rsi(series, period=14):
    delta = series.diff()
    gain  = delta.clip(lower=0)
    loss  = -delta.clip(upper=0)
    avg_g = gain.ewm(span=period, adjust=False).mean()
    avg_l = loss.ewm(span=period, adjust=False).mean()
    rs    = avg_g / (avg_l + 1e-10)
    return 100 - (100 / (1 + rs))

def calc_stoch(df, period=14):
    hh = df["high"].rolling(period).max()
    ll = df["low"].rolling(period).min()
    return (df["close"] - ll) / (hh - ll + 1e-10) * 100

def detect_engulfing_ema(df):
    results = []
    ema100 = calc_ema(df["close"], 100)
    ema200 = calc_ema(df["close"], 200)
    for i in range(1, len(df)):
        c, p = df.iloc[i], df.iloc[i-1]
        near_ema = abs(c["close"] - ema100.iloc[i]) / ema100.iloc[i] < 0.003
        # Bullish engulfing
        if (p["close"] < p["open"] and c["close"] > c["open"] and
            c["open"] < p["close"] and c["close"] > p["open"] and
            c["close"] > ema100.iloc[i] and near_ema):
            results.append({"idx": i, "dir": "BULL", "conf": 75, "pattern": "Engulfing + EMA"})
        # Bearish engulfing
        elif (p["close"] > p["open"] and c["close"] < c["open"] and
              c["open"] > p["close"] and c["close"] < p["open"] and
              c["close"] < ema100.iloc[i] and near_ema):
            results.append({"idx": i, "dir": "BEAR", "conf": 75, "pattern": "Engulfing + EMA"})
    return results[-3:] if results else []

def detect_pin_bar(df):
    results = []
    sr_high = df["high"].rolling(20).max().shift(1)
    sr_low  = df["low"].rolling(20).min().shift(1)
    for i in range(20, len(df)):
        c = df.iloc[i]
        body = abs(c["close"] - c["open"])
        total = c["high"] - c["low"]
        if total == 0: continue
        upper_wick = c["high"] - max(c["open"], c["close"])
        lower_wick = min(c["open"], c["close"]) - c["low"]
        near_res = abs(c["high"] - sr_high.iloc[i]) / (sr_high.iloc[i] + 1e-10) < 0.002
        near_sup = abs(c["low"]  - sr_low.iloc[i])  / (sr_low.iloc[i]  + 1e-10) < 0.002
        # Bull pin bar (long lower wick)
        if lower_wick > body * 2.5 and lower_wick > upper_wick * 2 and near_sup:
            results.append({"idx": i, "dir": "BULL", "conf": 70, "pattern": "Pin Bar en SR"})
        # Bear pin bar (long upper wick)
        elif upper_wick > body * 2.5 and upper_wick > lower_wick * 2 and near_res:
            results.append({"idx": i, "dir": "BEAR", "conf": 70, "pattern": "Pin Bar en SR"})
    return results[-3:] if results else []

def detect_fakey(df):
    results = []
    for i in range(3, len(df)):
        prev3 = df.iloc[i-3]
        prev2 = df.iloc[i-2]
        prev1 = df.iloc[i-1]
        curr  = df.iloc[i]
        # Inside bar
        inside = (prev2["high"] < prev3["high"] and prev2["low"] > prev3["low"])
        if not inside: continue
        # False breakout up then reversal
        if (prev1["high"] > prev3["high"] and
            curr["close"] < prev3["high"] and
            curr["close"] < prev1["close"]):
            results.append({"idx": i, "dir": "BEAR", "conf": 66, "pattern": "Fakey"})
        # False breakout down then reversal
        elif (prev1["low"] < prev3["low"] and
              curr["close"] > prev3["low"] and
              curr["close"] > prev1["close"]):
            results.append({"idx": i, "dir": "BULL", "conf": 66, "pattern": "Fakey"})
    return results[-3:] if results else []

def detect_rsi_divergence(df):
    results = []
    rsi = calc_rsi(df["close"])
    window = 20
    for i in range(window + 5, len(df)):
        price_window = df["close"].iloc[i-window:i]
        rsi_window   = rsi.iloc[i-window:i]
        price_max_idx = price_window.idxmax()
        price_min_idx = price_window.idxmin()
        # Bearish divergence
        if (df["close"].iloc[i] >= df["close"].loc[price_max_idx] and
            rsi.iloc[i] < rsi.loc[price_max_idx] - 5):
            results.append({"idx": i, "dir": "BEAR", "conf": 68, "pattern": "Divergencia RSI"})
        # Bullish divergence
        elif (df["close"].iloc[i] <= df["close"].loc[price_min_idx] and
              rsi.iloc[i] > rsi.loc[price_min_idx] + 5):
            results.append({"idx": i, "dir": "BULL", "conf": 68, "pattern": "Divergencia RSI"})
    return results[-3:] if results else []

def detect_inside_bar(df):
    results = []
    for i in range(2, len(df)):
        prev = df.iloc[i-1]
        curr = df.iloc[i]
        prev2 = df.iloc[i-2]
        # Inside bar: current inside previous
        inside = (prev["high"] < prev2["high"] and prev["low"] > prev2["low"])
        if not inside: continue
        # Breakout
        if curr["close"] > prev2["high"]:
            results.append({"idx": i, "dir": "BULL", "conf": 67, "pattern": "Inside Bar Breakout"})
        elif curr["close"] < prev2["low"]:
            results.append({"idx": i, "dir": "BEAR", "conf": 67, "pattern": "Inside Bar Breakout"})
    return results[-3:] if results else []

def detect_three_soldiers(df):
    results = []
    for i in range(2, len(df)):
        c0, c1, c2 = df.iloc[i-2], df.iloc[i-1], df.iloc[i]
        # Three white soldiers
        if (c0["close"] > c0["open"] and c1["close"] > c1["open"] and c2["close"] > c2["open"] and
            c1["close"] > c0["close"] and c2["close"] > c1["close"] and
            c1["open"] > c0["open"] and c2["open"] > c1["open"]):
            results.append({"idx": i, "dir": "BULL", "conf": 63, "pattern": "Three Soldiers/Crows"})
        # Three black crows
        elif (c0["close"] < c0["open"] and c1["close"] < c1["open"] and c2["close"] < c2["open"] and
              c1["close"] < c0["close"] and c2["close"] < c1["close"] and
              c1["open"] < c0["open"] and c2["open"] < c1["open"]):
            results.append({"idx": i, "dir": "BEAR", "conf": 63, "pattern": "Three Soldiers/Crows"})
    return results[-3:] if results else []

def detect_morning_star(df):
    results = []
    for i in range(2, len(df)):
        c0, c1, c2 = df.iloc[i-2], df.iloc[i-1], df.iloc[i]
        body0 = abs(c0["close"] - c0["open"])
        body1 = abs(c1["close"] - c1["open"])
        body2 = abs(c2["close"] - c2["open"])
        # Morning star
        if (c0["close"] < c0["open"] and body0 > body1 * 2 and
            c2["close"] > c2["open"] and body2 > body1 * 2 and
            c2["close"] > (c0["open"] + c0["close"]) / 2):
            results.append({"idx": i, "dir": "BULL", "conf": 65, "pattern": "Morning/Evening Star"})
        # Evening star
        elif (c0["close"] > c0["open"] and body0 > body1 * 2 and
              c2["close"] < c2["open"] and body2 > body1 * 2 and
              c2["close"] < (c0["open"] + c0["close"]) / 2):
            results.append({"idx": i, "dir": "BEAR", "conf": 65, "pattern": "Morning/Evening Star"})
    return results[-3:] if results else []

def detect_consolidation(df):
    results = []
    window = 10
    for i in range(window + 2, len(df)):
        segment = df.iloc[i-window:i]
        seg_range = segment["high"].max() - segment["low"].min()
        avg_range = (segment["high"] - segment["low"]).mean()
        # Consolidation: tight range
        if seg_range < avg_range * window * 0.5:
            curr = df.iloc[i]
            # Breakout
            if curr["close"] > segment["high"].max():
                results.append({"idx": i, "dir": "BULL", "conf": 64, "pattern": "Consolidacion Ruptura"})
            elif curr["close"] < segment["low"].min():
                results.append({"idx": i, "dir": "BEAR", "conf": 64, "pattern": "Consolidacion Ruptura"})
    return results[-3:] if results else []

def run_all_patterns(df):
    all_results = []
    detectors = [
        detect_engulfing_ema,
        detect_pin_bar,
        detect_fakey,
        detect_rsi_divergence,
        detect_inside_bar,
        detect_three_soldiers,
        detect_morning_star,
        detect_consolidation,
    ]
    for detector in detectors:
        try:
            results = detector(df)
            all_results.extend(results)
        except:
            pass
    # Filter recent (last 10 candles)
    recent = [r for r in all_results if r["idx"] >= len(df) - 10]
    # Sort by confidence
    recent.sort(key=lambda x: x["conf"], reverse=True)
    return recent

def get_trend_filter(df):
    ema200 = calc_ema(df["close"], 200)
    last_close = df["close"].iloc[-1]
    last_ema = ema200.iloc[-1]
    if last_close > last_ema * 1.001:
        return "ALCISTA", "#065f46"
    elif last_close < last_ema * 0.999:
        return "BAJISTA", "#991b1b"
    else:
        return "NEUTRAL", "#92400e"

def get_latest_price(df):
    return df["close"].iloc[-1]

def get_rsi_value(df):
    rsi = calc_rsi(df["close"])
    return rsi.iloc[-1]

# ================================================================
# SIDEBAR
# ================================================================
with st.sidebar:
    # BRAND
    st.markdown("""
    <div style='text-align:center;padding:14px 0 10px;border-bottom:1px solid #1e293b;margin-bottom:14px;'>
    <div style='font-family:"Rajdhani",sans-serif;font-size:22px;font-weight:700;
    color:#c8920a;letter-spacing:3px;'>HECTOR</div>
    <div style='font-family:"Share Tech Mono",monospace;font-size:9px;
    color:#475569;letter-spacing:2px;'>PATTERN DETECTOR</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:9px;color:#475569;letter-spacing:2px;margin-bottom:4px;">API KEY ANTHROPIC</div>', unsafe_allow_html=True)
    api_in = st.text_input("API Key", value=st.session_state.api_key,
                            placeholder="sk-ant-api03-...", type="password",
                            label_visibility="collapsed")
    if api_in: st.session_state.api_key = api_in
    if st.session_state.api_key.startswith("sk-ant-"):
        st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:10px;color:#34d399;margin-bottom:8px;">✅ IA ACTIVA</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:10px;color:#475569;margin-bottom:8px;">Sin key</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Activos seleccionados
    st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:9px;color:#475569;letter-spacing:2px;margin-bottom:8px;">ACTIVOS A ESCANEAR</div>', unsafe_allow_html=True)
    selected_assets = []
    for asset, info in ASSETS.items():
        checked = st.checkbox(asset, value=True, key=f"asset_{asset}")
        if checked:
            selected_assets.append(asset)

    st.markdown("---")

    # Confianza minima
    min_conf = st.slider("Confianza minima %", 50, 80, 63, 1)

    st.markdown("---")

    # Sesion actual
    h = datetime.now(timezone.utc).hour
    if 7 <= h < 10:
        ses, ses_col, ses_bg = "LONDRES", "#34d399", "#022c22"
    elif 13 <= h < 16:
        ses, ses_col, ses_bg = "NUEVA YORK", "#34d399", "#022c22"
    elif 16 <= h < 17:
        ses, ses_col, ses_bg = "SOLAPAMIENTO", "#fbbf24", "#451a03"
    else:
        ses, ses_col, ses_bg = "CERRADO", "#f87171", "#2d0d0d"

    st.markdown(f"""
    <div style='background:{ses_bg};border:1px solid {ses_col}33;border-radius:8px;
    padding:10px 12px;margin-bottom:10px;'>
    <div style='font-family:"Share Tech Mono",monospace;font-size:9px;color:{ses_col};
    letter-spacing:2px;'>{ses}</div>
    <div style='font-family:"Share Tech Mono",monospace;font-size:10px;color:#475569;'>
    {datetime.now(timezone.utc).strftime("%H:%M:%S UTC")}</div>
    </div>""", unsafe_allow_html=True)

# ================================================================
# HEADER
# ================================================================
st.markdown("""
<div class="hector-brand">
  <div style='font-family:"Share Tech Mono",monospace;font-size:9px;color:#475569;
  letter-spacing:3px;margin-bottom:6px;'>SISTEMA PROFESIONAL DE RECONOCIMIENTO</div>
  <div style='font-family:"Rajdhani",sans-serif;font-size:28px;font-weight:700;
  color:#c8920a;letter-spacing:4px;'>HECTOR PATTERN DETECTOR</div>
  <div style='font-family:"Share Tech Mono",monospace;font-size:10px;color:#64748b;
  margin-top:4px;letter-spacing:2px;'>
  8 PATRONES · 6 ACTIVOS · M15 + H1 FILTRO · IQ OPTION READY
  </div>
</div>""", unsafe_allow_html=True)

# ================================================================
# SCAN BUTTON
# ================================================================
col_btn, col_status = st.columns([1, 3])
with col_btn:
    scan_now = st.button("ESCANEAR AHORA", key="scan_btn")
with col_status:
    if st.session_state.last_scan:
        st.markdown(f"""
        <div class="scan-status" style="margin-top:8px;">
          <div class="scan-dot" style="background:#34d399;"></div>
          <span style="color:#475569;">Ultimo scan: {st.session_state.last_scan}</span>
          <span style="color:#c8920a;margin-left:8px;">
          {len(st.session_state.scan_results)} patrones detectados
          </span>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="scan-status" style="margin-top:8px;">
          <div class="scan-dot" style="background:#475569;"></div>
          <span style="color:#475569;">Presiona ESCANEAR para analizar el mercado</span>
        </div>""", unsafe_allow_html=True)

# ================================================================
# SCANNING
# ================================================================
if scan_now:
    all_results = []
    progress = st.progress(0)
    status_text = st.empty()

    for idx, asset in enumerate(selected_assets):
        info = ASSETS[asset]
        status_text.markdown(f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:10px;color:#c8920a;">Escaneando {asset}...</div>', unsafe_allow_html=True)
        progress.progress((idx + 1) / len(selected_assets))

        df = fetch_data(info["yahoo"], period="60d", interval="15m")

        if df is not None and len(df) > 200:
            patterns = run_all_patterns(df)
            trend, trend_col = get_trend_filter(df)
            price = get_latest_price(df)
            rsi_val = get_rsi_value(df)

            # Filter by min confidence
            patterns = [p for p in patterns if p["conf"] >= min_conf]

            # Filter by trend alignment
            aligned = []
            for p in patterns:
                if trend == "ALCISTA" and p["dir"] == "BULL":
                    p["trend_aligned"] = True
                    aligned.append(p)
                elif trend == "BAJISTA" and p["dir"] == "BEAR":
                    p["trend_aligned"] = True
                    aligned.append(p)
                else:
                    p["trend_aligned"] = False
                    aligned.append(p)

            all_results.append({
                "asset": asset,
                "info": info,
                "patterns": aligned,
                "trend": trend,
                "trend_col": trend_col,
                "price": price,
                "rsi": rsi_val,
                "df": df,
                "has_signal": len([p for p in aligned if p["trend_aligned"]]) > 0
            })
        else:
            all_results.append({
                "asset": asset,
                "info": info,
                "patterns": [],
                "trend": "SIN DATOS",
                "trend_col": "#475569",
                "price": 0,
                "rsi": 50,
                "df": None,
                "has_signal": False
            })

    progress.empty()
    status_text.empty()
    st.session_state.scan_results = all_results
    st.session_state.last_scan = datetime.now().strftime("%H:%M:%S")

    # Build alerts
    alerts = []
    for r in all_results:
        for p in r["patterns"]:
            if p["trend_aligned"] and p["conf"] >= 65:
                alerts.append({
                    "asset": r["asset"],
                    "pattern": p["pattern"],
                    "dir": p["dir"],
                    "conf": p["conf"],
                    "price": r["price"],
                    "hora": datetime.now().strftime("%H:%M"),
                })
    st.session_state.alerts = alerts
    st.rerun()

# ================================================================
# TABS
# ================================================================
tab_radar, tab_patrones, tab_alertas, tab_stats = st.tabs([
    "📡 RADAR",
    "🔍 PATRONES DETECTADOS",
    "🚨 ALERTAS ACTIVAS",
    "📊 ESTADISTICAS",
])

# ──────────────────────────────────────────────
# TAB 1 — RADAR
# ──────────────────────────────────────────────
with tab_radar:
    if not st.session_state.scan_results:
        st.markdown("""
        <div style='text-align:center;padding:60px 20px;'>
          <div style='font-size:48px;margin-bottom:16px;'>🔍</div>
          <div style='font-family:"Rajdhani",sans-serif;font-size:24px;color:#475569;'>
          Presiona ESCANEAR AHORA</div>
          <div style='font-family:"Share Tech Mono",monospace;font-size:11px;color:#334155;margin-top:8px;'>
          El sistema analizara los 6 activos en busca de los 8 patrones</div>
        </div>""", unsafe_allow_html=True)
    else:
        # KPIs
        total_patterns = sum(len(r["patterns"]) for r in st.session_state.scan_results)
        signals = sum(1 for r in st.session_state.scan_results if r["has_signal"])
        bull_count = sum(1 for r in st.session_state.scan_results for p in r["patterns"] if p["dir"]=="BULL" and p["trend_aligned"])
        bear_count = sum(1 for r in st.session_state.scan_results for p in r["patterns"] if p["dir"]=="BEAR" and p["trend_aligned"])

        k1,k2,k3,k4 = st.columns(4)
        for col, label, val, color, sub in [
            (k1, "PATRONES TOTALES", str(total_patterns), "#c8920a", "en todos los activos"),
            (k2, "SEÑALES VALIDAS",  str(signals),        "#34d399", "alineadas con tendencia"),
            (k3, "BULL SIGNALS",     str(bull_count),     "#34d399", "oportunidades LONG"),
            (k4, "BEAR SIGNALS",     str(bear_count),     "#f87171", "oportunidades SHORT"),
        ]:
            with col:
                st.markdown(f"""<div class="kpi">
                  <div class="kpi-label">{label}</div>
                  <div class="kpi-value" style="color:{color};">{val}</div>
                  <div class="kpi-sub">{sub}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown('<div class="sec" style="margin-top:16px;">ESTADO DE ACTIVOS</div>', unsafe_allow_html=True)

        for r in st.session_state.scan_results:
            has_bull = any(p["dir"]=="BULL" and p["trend_aligned"] for p in r["patterns"])
            has_bear = any(p["dir"]=="BEAR" and p["trend_aligned"] for p in r["patterns"])
            signal_color = "#34d399" if has_bull else ("#f87171" if has_bear else "#475569")
            signal_text  = "BULL SIGNAL" if has_bull else ("BEAR SIGNAL" if has_bear else "SIN SENAL")
            signal_bg    = "#022c22" if has_bull else ("#2d0d0d" if has_bear else "#0f172a")

            price_str = f"{r['price']:.2f}" if r["price"] > 0 else "Sin datos"
            rsi_color = "#f87171" if r["rsi"] > 70 else ("#34d399" if r["rsi"] < 30 else "#94a3b8")

            st.markdown(f"""
            <div class="asset-row" style="border-left:4px solid {r['info']['color']};">
              <div>
                <div class="asset-name">{r['asset']}</div>
                <div class="asset-price">{r['info']['tipo']} · {price_str}</div>
              </div>
              <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
                <span style="background:{signal_bg};color:{signal_color};border:1px solid {signal_color}33;
                padding:4px 12px;border-radius:20px;font-family:'Share Tech Mono',monospace;
                font-size:9px;font-weight:700;">{signal_text}</span>
                <span style="color:{r['trend_col']};font-family:'Share Tech Mono',monospace;font-size:9px;">
                {r['trend']}</span>
                <span style="color:{rsi_color};font-family:'Share Tech Mono',monospace;font-size:9px;">
                RSI {r['rsi']:.0f}</span>
                <span style="color:#475569;font-family:'Share Tech Mono',monospace;font-size:9px;">
                {len(r['patterns'])} patrones</span>
              </div>
            </div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# TAB 2 — PATRONES DETECTADOS
# ──────────────────────────────────────────────
with tab_patrones:
    if not st.session_state.scan_results:
        st.markdown('<div style="text-align:center;padding:40px;font-family:\'Share Tech Mono\',monospace;font-size:11px;color:#475569;">Ejecuta el scanner primero</div>', unsafe_allow_html=True)
    else:
        for r in st.session_state.scan_results:
            if not r["patterns"]: continue
            st.markdown(f'<div class="sec">{r["asset"]} — {len(r["patterns"])} PATRONES</div>', unsafe_allow_html=True)

            for p in r["patterns"]:
                dir_color = "#34d399" if p["dir"]=="BULL" else "#f87171"
                dir_bg    = "#022c22" if p["dir"]=="BULL" else "#2d0d0d"
                aligned_html = '<span style="color:#fbbf24;font-family:\'Share Tech Mono\',monospace;font-size:9px;"> ★ ALINEADO CON TENDENCIA</span>' if p.get("trend_aligned") else '<span style="color:#475569;font-family:\'Share Tech Mono\',monospace;font-size:9px;"> contra tendencia</span>'
                pat_info = PATTERNS.get(p["pattern"], {})
                fill_class = "conf-fill-green" if p["dir"]=="BULL" else "conf-fill-red"

                st.markdown(f"""
                <div class="pattern-card {'bullish' if p['dir']=='BULL' else 'bearish'}">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                    <div>
                      <span style="font-family:'Rajdhani',sans-serif;font-weight:700;
                      font-size:16px;color:#f1f5f9;">{p['pattern']}</span>
                      {aligned_html}
                    </div>
                    <span style="background:{dir_bg};color:{dir_color};border:1px solid {dir_color}44;
                    padding:4px 12px;border-radius:20px;font-family:'Share Tech Mono',monospace;
                    font-size:10px;font-weight:700;">{p['dir']}</span>
                  </div>
                  <div style="font-size:11px;color:#64748b;margin-bottom:8px;">
                  {pat_info.get('desc','')}</div>
                  <div class="conf-bar"><div class="{fill_class}" style="width:{p['conf']}%;"></div></div>
                  <div style="display:flex;justify-content:space-between;font-family:'Share Tech Mono',monospace;font-size:9px;color:#475569;">
                    <span>Confianza: <b style="color:{dir_color};">{p['conf']}%</b></span>
                    <span>Efectividad historica: {pat_info.get('efectividad',0)}%</span>
                  </div>
                </div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# TAB 3 — ALERTAS
# ──────────────────────────────────────────────
with tab_alertas:
    st.markdown('<div class="sec">ALERTAS ACTIVAS — SEÑALES DE ALTA CONFIANZA</div>', unsafe_allow_html=True)

    if not st.session_state.alerts:
        st.markdown("""
        <div style='text-align:center;padding:40px;background:#0f172a;border:1px solid #1e293b;border-radius:10px;'>
          <div style='font-size:32px;margin-bottom:10px;'>📡</div>
          <div style='font-family:"Share Tech Mono",monospace;font-size:11px;color:#475569;'>
          Sin alertas activas — ejecuta el scanner para detectar patrones</div>
        </div>""", unsafe_allow_html=True)
    else:
        for alert in st.session_state.alerts:
            is_bull = alert["dir"] == "BULL"
            card_class = "alert-bull" if is_bull else "alert-bear"
            icon = "▲" if is_bull else "▼"
            col = "#34d399" if is_bull else "#f87171"
            action = "CALL / LONG" if is_bull else "PUT / SHORT"

            st.markdown(f"""
            <div class="alert-card {card_class}">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <div>
                  <span style="font-family:'Rajdhani',sans-serif;font-weight:700;
                  font-size:22px;color:{col};">{icon} {alert['asset']}</span>
                  <span style="font-family:'Share Tech Mono',monospace;font-size:10px;
                  color:#64748b;margin-left:10px;">{alert['hora']} · ${alert['price']:.2f}</span>
                </div>
                <span style="font-family:'Rajdhani',sans-serif;font-weight:700;
                font-size:18px;color:{col};">{action}</span>
              </div>
              <div style="font-size:12px;color:#94a3b8;margin-bottom:6px;">
              Patron: <b style="color:{col};">{alert['pattern']}</b></div>
              <div style="display:flex;gap:8px;align-items:center;">
                <div style="flex:1;height:6px;background:#1e293b;border-radius:3px;overflow:hidden;">
                  <div style="height:100%;width:{alert['conf']}%;background:{col};border-radius:3px;"></div>
                </div>
                <span style="font-family:'Share Tech Mono',monospace;font-size:10px;color:{col};">
                {alert['conf']}%</span>
              </div>
            </div>""", unsafe_allow_html=True)

        # IA Analysis of alerts
        if st.session_state.api_key.startswith("sk-ant-") and st.session_state.alerts:
            st.markdown("---")
            if st.button("ANALIZAR ALERTAS CON IA", key="ai_alerts"):
                alerts_text = "\n".join([
                    f"{a['asset']} - {a['dir']} - {a['pattern']} - Confianza {a['conf']}%"
                    for a in st.session_state.alerts
                ])
                sys = """Eres el analista de patrones de Hector. Analiza estas alertas de patrones tecnicos
y dime cuales son las 2 mejores oportunidades para operar AHORA en IQ Option M15.
Considera confluencia de patrones, horario UTC actual, y riesgo. Max 150 palabras. En espanol."""
                with st.spinner("Analizando alertas..."):
                    resp = requests.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={"Content-Type":"application/json",
                                 "x-api-key":st.session_state.api_key,
                                 "anthropic-version":"2023-06-01"},
                        json={"model":"claude-sonnet-4-20250514","max_tokens":400,
                              "system":sys,
                              "messages":[{"role":"user","content":f"Alertas actuales:\n{alerts_text}"}]},
                        timeout=30
                    )
                    if resp.status_code == 200:
                        text = resp.json()["content"][0]["text"]
                        st.markdown(f"""
                        <div style="background:#1a1200;border:1px solid #c8920a;border-radius:8px;
                        padding:16px;font-size:13px;color:#e2e8f0;line-height:1.8;">
                        {text.replace(chr(10),'<br>')}
                        </div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# TAB 4 — ESTADISTICAS
# ──────────────────────────────────────────────
with tab_stats:
    st.markdown('<div class="sec">EFECTIVIDAD HISTORICA DE LOS 8 PATRONES</div>', unsafe_allow_html=True)

    for name, info in sorted(PATTERNS.items(), key=lambda x: x[1]["efectividad"], reverse=True):
        ef = info["efectividad"]
        color = "#34d399" if ef >= 68 else ("#fbbf24" if ef >= 64 else "#f87171")
        st.markdown(f"""
        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:8px;
        padding:12px 16px;margin-bottom:8px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
            <span style="font-family:'Rajdhani',sans-serif;font-weight:700;
            font-size:15px;color:#f1f5f9;">{name}</span>
            <span style="font-family:'Rajdhani',sans-serif;font-weight:700;
            font-size:20px;color:{color};">{ef}%</span>
          </div>
          <div style="height:6px;background:#1e293b;border-radius:3px;overflow:hidden;margin-bottom:6px;">
            <div style="height:100%;width:{ef}%;background:{color};border-radius:3px;"></div>
          </div>
          <div style="font-size:11px;color:#475569;">{info['desc']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec">ACTIVOS Y SPREADS</div>', unsafe_allow_html=True)
    for asset, info in ASSETS.items():
        st.markdown(f"""
        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:8px;
        padding:10px 14px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;">
          <div>
            <span style="font-family:'Rajdhani',sans-serif;font-weight:700;
            font-size:15px;color:{info['color']};">{asset}</span>
            <span style="font-family:'Share Tech Mono',monospace;font-size:9px;
            color:#475569;margin-left:8px;">{info['tipo']}</span>
          </div>
          <span style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#64748b;">
          Spread: {info['spread']}</span>
        </div>""", unsafe_allow_html=True)

# ================================================================
# FOOTER
# ================================================================
st.markdown("""
<div style="border-top:1px solid #1e293b;margin-top:24px;padding-top:10px;
text-align:center;font-family:'Share Tech Mono',monospace;font-size:9px;color:#334155;
letter-spacing:2px;">
HECTOR PATTERN DETECTOR · 8 PATRONES · 6 ACTIVOS · M15 · IQ OPTION READY
</div>""", unsafe_allow_html=True)
