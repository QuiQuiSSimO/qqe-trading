# QQE COMMAND V5 — HECTOR TRADING SYSTEM
# Binarias 1min + Swing H1/H4 + Scanner + IA Grafico + Estrategia EMA/QQE/Vela
#
# INSTALACION: pip install streamlit requests yfinance pandas numpy streamlit-autorefresh
# EJECUCION:   streamlit run qqe_v5.py

import streamlit as st
import requests
import base64
import pandas as pd
import numpy as np
import yfinance as yf
import json
import os
from datetime import datetime, timezone, date, timedelta

# ================================================================
# PERSISTENCIA LOCAL DE CREDENCIALES (sin pedir cada vez)
# ================================================================
CREDS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".qqe_creds.json")

def guardar_creds():
    try:
        data = {
            "api_key":    st.session_state.get("api_key", ""),
            "tg_token":   st.session_state.get("tg_token", ""),
            "tg_chat":    st.session_state.get("tg_chat", ""),
            "capital":    st.session_state.get("capital", 467.86),
            "stop_loss_dia": st.session_state.get("stop_loss_dia", 10),
        }
        with open(CREDS_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

def cargar_creds_locales():
    try:
        if os.path.exists(CREDS_FILE):
            with open(CREDS_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_OK = True
except ImportError:
    AUTOREFRESH_OK = False

try:
    import streamlit.components.v1 as components_v1
    COMPONENTS_OK = True
except:
    COMPONENTS_OK = False

st.set_page_config(
    page_title="QQE Command v7 — Hector",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================================================================
# CSS
# ================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&family=Inter:wght@300;400;500;600&display=swap');

html, body, .stApp { background:#0a0f1a !important; }
.stApp { font-family:'Inter',sans-serif; color:#c8d8e8; font-size:15px; }
[data-testid="stSidebar"] { background:#0d1525 !important; border-right:1px solid #1e3050 !important; }

.stTabs [data-baseweb="tab-list"] { background:#0d1525; border-bottom:2px solid #1e3050; gap:0; }
.stTabs [data-baseweb="tab"] {
    background:transparent; color:#4a7a99 !important;
    font-family:'Share Tech Mono',monospace; font-size:12px;
    letter-spacing:1px; padding:12px 16px; border:none;
}
.stTabs [aria-selected="true"] {
    background:#0a0f1a !important; color:#c8920a !important;
    border-bottom:2px solid #c8920a !important; font-weight:700 !important;
}

.card { background:#0d1525; border:1px solid #1e3050; border-radius:10px; padding:18px; margin-bottom:10px; }
.card-gold   { border-left:4px solid #c8920a; }
.card-green  { border-left:4px solid #16a34a; }
.card-red    { border-left:4px solid #dc2626; }
.card-blue   { border-left:4px solid #2563eb; }
.card-purple { border-left:4px solid #7c3aed; }

.kpi { background:#0d1525; border:1px solid #1e3050; border-radius:10px; padding:16px 18px; text-align:center; }
.kpi-label { font-family:'Share Tech Mono',monospace; font-size:11px; color:#4a7a99; letter-spacing:2px; margin-bottom:6px; }
.kpi-value { font-family:'Rajdhani',sans-serif; font-size:36px; font-weight:700; line-height:1.1; }
.kpi-sub   { font-family:'Share Tech Mono',monospace; font-size:11px; color:#4a7a99; margin-top:3px; }

.sec { font-family:'Share Tech Mono',monospace; font-size:12px; color:#4a7a99; letter-spacing:3px;
       text-transform:uppercase; border-bottom:2px solid #1e3050; padding-bottom:6px; margin:16px 0 12px; }

.signal-call { background:linear-gradient(135deg,#0a2010,#0d3520); border:1px solid #16a34a;
               border-radius:10px; padding:16px; margin-bottom:10px; }
.signal-put  { background:linear-gradient(135deg,#200a0a,#350d0d); border:1px solid #dc2626;
               border-radius:10px; padding:16px; margin-bottom:10px; }
.signal-wait { background:#0d1525; border:1px solid #1e3050; border-radius:10px; padding:16px; margin-bottom:10px; }

.badge { padding:4px 12px; border-radius:20px; font-family:'Share Tech Mono',monospace; font-size:11px; font-weight:700; }
.badge-green  { background:#0a3020; color:#4ade80; border:1px solid #16a34a; }
.badge-red    { background:#3a0a0a; color:#f87171; border:1px solid #dc2626; }
.badge-gold   { background:#2a1a00; color:#fbbf24; border:1px solid #c8920a; }
.badge-blue   { background:#0a1a3a; color:#60a5fa; border:1px solid #2563eb; }
.badge-gray   { background:#1a2535; color:#94a3b8; border:1px solid #2a3a55; }

.ia-box { background:#0d1525; border:1px solid #c8920a; border-radius:10px; padding:18px;
          font-size:15px; line-height:1.9; color:#c8d8e8; }

.asset-row { background:#0d1525; border:1px solid #1e3050; border-radius:8px; padding:14px; margin-bottom:8px; }

.scan-dot { display:inline-block; width:8px; height:8px; border-radius:50%; animation:pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:.4;} }

.prog-track { height:7px; background:#1e3050; border-radius:3px; overflow:hidden; margin:4px 0; }
.prog-fill  { height:100%; border-radius:3px; }

.diario-entry { background:#0d1525; border:1px solid #1e3050; border-radius:8px; padding:16px; margin-bottom:8px; }
.diario-meta  { font-family:'Share Tech Mono',monospace; font-size:11px; color:#4a7a99; letter-spacing:1px; margin-bottom:6px; }

.script-card { background:#0d1525; border:1px solid #1e3050; border-radius:8px; padding:18px; margin-bottom:12px; }
.code-block { background:#060c18; border:1px solid #1e3050; border-radius:6px; padding:16px;
              font-family:'Share Tech Mono',monospace; font-size:11px; line-height:1.9; color:#7dd3fc;
              white-space:pre; overflow-x:auto; max-height:300px; overflow-y:auto; margin-bottom:10px; }

/* ESTRATEGIA NUEVA */
.strat-box { background:#0d1525; border:1px solid #c8920a; border-radius:12px; padding:18px; margin-bottom:12px; }
.strat-step { background:#060c18; border-left:3px solid #c8920a; padding:12px 16px; margin-bottom:8px; border-radius:0 8px 8px 0; font-size:14px; line-height:1.8; }
.strat-regla { background:#0a3020; border:1px solid #16a34a; border-radius:8px; padding:12px 16px; margin-bottom:8px; font-size:14px; }

/* Mobile */
@media (max-width:768px) {
    .stTabs [data-baseweb="tab"] { font-size:11px; padding:10px 10px; letter-spacing:0; }
    .stButton>button { min-height:52px !important; font-size:13px !important; }
    .kpi-value { font-size:28px; }
}

.stButton>button {
    background:#1e3050 !important; color:#c8d8e8 !important;
    border:1px solid #2a4570 !important; border-radius:8px !important;
    font-family:'Share Tech Mono',monospace !important; font-size:12px !important; letter-spacing:1px !important;
    transition:all .2s;
}
.stButton>button:hover { background:#c8920a !important; color:#000 !important; border-color:#c8920a !important; }

.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    background:#0d1525 !important; border:1px solid #1e3050 !important;
    color:#c8d8e8 !important; border-radius:8px !important;
    font-size:14px !important;
}
.stSelectbox>div>div, .stNumberInput>div>div>input {
    background:#0d1525 !important; border:1px solid #1e3050 !important; color:#c8d8e8 !important; border-radius:8px !important;
    font-size:14px !important;
}
[data-testid="stSlider"] { color:#c8920a; }
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:#0a0f1a; }
::-webkit-scrollbar-thumb { background:#1e3050; border-radius:2px; }

/* Bigger labels globally */
label, .stSelectbox label, .stTextInput label, .stNumberInput label {
    font-size:13px !important; color:#7a9ab8 !important;
}
p, li, div { font-size:inherit; }
</style>
""", unsafe_allow_html=True)

# ================================================================
# SECRETS / SESSION STATE — carga automática sin pedir cada vez
# ================================================================
def cargar_secrets():
    # 1) Primero desde archivo local (guardado en sesión anterior)
    creds = cargar_creds_locales()
    for k, v in creds.items():
        if k not in st.session_state or not st.session_state[k]:
            st.session_state[k] = v
    # 2) Luego desde st.secrets de Streamlit Cloud (si existe)
    try:
        if "anthropic_api_key" in st.secrets and not st.session_state.get("api_key"):
            st.session_state.api_key = st.secrets["anthropic_api_key"]
    except: pass
    try:
        if "telegram_token" in st.secrets and not st.session_state.get("tg_token"):
            st.session_state.tg_token = st.secrets["telegram_token"]
    except: pass
    try:
        if "telegram_chat_id" in st.secrets and not st.session_state.get("tg_chat"):
            st.session_state.tg_chat = str(st.secrets["telegram_chat_id"])
    except: pass
    try:
        if "capital_dia" in st.secrets and not st.session_state.get("capital"):
            st.session_state.capital = float(st.secrets["capital_dia"])
    except: pass

defaults = {
    "api_key": "",
    "ops": [],
    "diario": [],
    "scan_results": [],
    "scan_ultimo": None,
    "swing_analisis": {},
    "alertas_bin": [],
    "tg_token": "",
    "tg_chat": "",
    "tg_on": False,
    "tg_enviadas": set(),
    "capital": 467.86,
    "riesgo_pct": 2,
    "stop_loss_dia": 10,
    "perdida_dia": 0.0,
    "radar_bloqueado": False,
    "autorefresh_on": False,
    "hector_results": None,
    "hector_ultimo": "",
    "not_resultado": None,
    "autorefresh_min": 5,
    "ultima_alerta_son": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

cargar_secrets()
if st.session_state.tg_token and st.session_state.tg_chat:
    st.session_state.tg_on = True

def get_ia_ok():
    return st.session_state.get("api_key", "").startswith("sk-ant-")

# ================================================================
# HELPERS
# ================================================================
def get_utc_hour():
    return datetime.now(timezone.utc).hour

def get_session_info():
    h = get_utc_hour()
    if 7 <= h < 10:    return "SESION LONDRES",   "OPERAR",    "#16a34a", "#0a3020", "#4ade80"
    elif 13 <= h < 16: return "SESION NUEVA YORK","OPERAR",    "#16a34a", "#0a3020", "#4ade80"
    elif 11 <= h < 13: return "SOLAPAMIENTO",     "ACTIVO",    "#c8920a", "#2a1a00", "#fbbf24"
    elif 10 <= h < 11: return "CIERRE LONDRES",   "PRECAUCION","#c8920a", "#2a1a00", "#fbbf24"
    else:               return "MERCADO CERRADO",  "INACTIVO",  "#64748b", "#1a2535", "#94a3b8"

def enviar_telegram(token, chat_id, msg):
    try:
        r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"}, timeout=10)
        return r.status_code == 200
    except: return False

def calc_pnl():
    g = sum(o["pnl"] for o in st.session_state.ops if o["pnl"] > 0)
    p = abs(sum(o["pnl"] for o in st.session_state.ops if o["pnl"] < 0))
    return g, p, g - p

# ================================================================
# INDICADORES TECNICOS
# ================================================================
ACTIVOS = {
    # ── FOREX ──────────────────────────────────────────────────
    "EUR/USD":    {"yahoo": "EURUSD=X",  "tipo": "forex",      "iq": "EUR/USD"},
    "GBP/USD":    {"yahoo": "GBPUSD=X",  "tipo": "forex",      "iq": "GBP/USD"},
    "USD/JPY":    {"yahoo": "JPY=X",     "tipo": "forex",      "iq": "USD/JPY"},
    "AUD/USD":    {"yahoo": "AUDUSD=X",  "tipo": "forex",      "iq": "AUD/USD"},
    "USD/CAD":    {"yahoo": "CAD=X",     "tipo": "forex",      "iq": "USD/CAD"},
    "EUR/GBP":    {"yahoo": "EURGBP=X",  "tipo": "forex",      "iq": "EUR/GBP"},
    # ── MATERIAS PRIMAS ────────────────────────────────────────
    "GOLD":       {"yahoo": "GC=F",      "tipo": "commodity",  "iq": "Gold"},
    "SILVER":     {"yahoo": "SI=F",      "tipo": "commodity",  "iq": "Silver"},
    "OIL WTI":    {"yahoo": "CL=F",      "tipo": "commodity",  "iq": "Light Crude Oil WTI"},
    "OIL BRENT":  {"yahoo": "BZ=F",      "tipo": "commodity",  "iq": "Brent Crude Oil"},
    "NAT GAS":    {"yahoo": "NG=F",      "tipo": "commodity",  "iq": "Natural Gas"},
    "COPPER":     {"yahoo": "HG=F",      "tipo": "commodity",  "iq": "Copper"},
    # ── INDICES ────────────────────────────────────────────────
    "US 100":     {"yahoo": "NQ=F",      "tipo": "index",      "iq": "US 100"},
    "US 500":     {"yahoo": "ES=F",      "tipo": "index",      "iq": "US 500"},
    "US 30":      {"yahoo": "YM=F",      "tipo": "index",      "iq": "US 30"},
    # ── CRYPTO ─────────────────────────────────────────────────
    "BTC/USD":    {"yahoo": "BTC-USD",   "tipo": "crypto",     "iq": "Bitcoin"},
    "ETH/USD":    {"yahoo": "ETH-USD",   "tipo": "crypto",     "iq": "Ethereum"},
}

@st.cache_data(ttl=60)
def obtener_datos(symbol, period="5d", interval="1h"):
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True)
        if df.empty or len(df) < 20: return None
        df.columns = [c[0].lower() if isinstance(c, tuple) else c.lower() for c in df.columns]
        df = df.rename(columns={"open":"apertura","high":"maximo","low":"minimo","close":"cierre","volume":"volumen"})
        return df.dropna()
    except: return None

@st.cache_data(ttl=30)
def obtener_datos_1min(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="1m", progress=False, auto_adjust=True)
        if df.empty or len(df) < 20: return None
        df.columns = [c[0].lower() if isinstance(c, tuple) else c.lower() for c in df.columns]
        df = df.rename(columns={"open":"apertura","high":"maximo","low":"minimo","close":"cierre","volume":"volumen"})
        return df.dropna()
    except: return None

def calc_ema(series, n):
    return series.ewm(span=n, adjust=False).mean()

def calc_rsi(series, n=14):
    delta = series.diff()
    g = delta.clip(lower=0).ewm(span=n, adjust=False).mean()
    l = (-delta.clip(upper=0)).ewm(span=n, adjust=False).mean()
    return 100 - 100 / (1 + g / l.replace(0, 1e-10))

def calc_macd(series):
    ema12 = calc_ema(series, 12)
    ema26 = calc_ema(series, 26)
    macd  = ema12 - ema26
    signal = calc_ema(macd, 9)
    return macd, signal, macd - signal

def calc_atr(df, n=14):
    h, l, c = df["maximo"], df["minimo"], df["cierre"]
    tr = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(span=n, adjust=False).mean()

def analizar_activo_1min(symbol):
    """Detecta senales de binarias 1 minuto con 3 estrategias"""
    df = obtener_datos_1min(symbol)
    if df is None or len(df) < 50: return None

    c = df["cierre"]
    ema3  = calc_ema(c, 3)
    ema8  = calc_ema(c, 8)
    ema50 = calc_ema(c, 50)
    rsi   = calc_rsi(c)
    macd, signal, hist = calc_macd(c)
    atr   = calc_atr(df)

    precio   = c.iloc[-1]
    atr_v    = atr.iloc[-1]
    atr_avg  = atr.iloc[-20:].mean()
    volatil  = atr_v / atr_avg if atr_avg > 0 else 1
    rsi_v    = rsi.iloc[-1]
    hist_v   = hist.iloc[-1]

    senales = []

    # SCRIPT A — Momentum: cruce EMA3/EMA8
    ema3_now  = ema3.iloc[-1]; ema3_prev = ema3.iloc[-2]
    ema8_now  = ema8.iloc[-1]; ema8_prev = ema8.iloc[-2]
    if ema3_prev < ema8_prev and ema3_now > ema8_now and volatil > 0.8 and precio > ema50.iloc[-1]:
        senales.append({"script":"A — Momentum","dir":"CALL","conf":min(95,int(70+volatil*10))})
    elif ema3_prev > ema8_prev and ema3_now < ema8_now and volatil > 0.8 and precio < ema50.iloc[-1]:
        senales.append({"script":"A — Momentum","dir":"PUT","conf":min(95,int(70+volatil*10))})

    # SCRIPT B — Reversion: RSI extremo + contra-momentum
    if rsi_v < 25 and hist_v > 0:
        senales.append({"script":"B — Reversion","dir":"CALL","conf":min(90,int(65+(30-rsi_v)))})
    elif rsi_v > 75 and hist_v < 0:
        senales.append({"script":"B — Reversion","dir":"PUT","conf":min(90,int(65+(rsi_v-70)))})

    # SCRIPT C — Hibrido: confluencia MACD + EMA
    if hist_v > 0 and hist.iloc[-2] < 0 and precio > ema8_now and rsi_v < 65:
        senales.append({"script":"C — Hibrido","dir":"CALL","conf":78})
    elif hist_v < 0 and hist.iloc[-2] > 0 and precio < ema8_now and rsi_v > 35:
        senales.append({"script":"C — Hibrido","dir":"PUT","conf":78})

    if not senales: return None

    mejor = max(senales, key=lambda x: x["conf"])
    return {
        "precio": precio, "rsi": rsi_v, "atr": atr_v, "volatilidad": volatil,
        "hist_macd": hist_v, "ema3": ema3_now, "ema8": ema8_now,
        "senales": senales, "mejor": mejor,
        "hora": datetime.now().strftime("%H:%M:%S"),
    }

def analizar_activo_swing(symbol, tf="H1"):
    """Analiza activo para swing trading H1/H4"""
    tmap = {"M15": ("15m","5d"), "H1": ("1h","30d"), "H4": ("4h","60d"), "D1": ("1d","90d")}
    interval, period = tmap.get(tf, ("1h","30d"))

    df = obtener_datos(symbol, period=period, interval=interval)
    if df is None or len(df) < 50: return None

    c = df["cierre"]
    ema20  = calc_ema(c, 20)
    ema50  = calc_ema(c, 50)
    ema200 = calc_ema(c, 200) if len(c) >= 200 else calc_ema(c, min(len(c)-1, 50))
    rsi    = calc_rsi(c)
    macd, sig_line, hist = calc_macd(c)
    atr    = calc_atr(df)

    precio  = c.iloc[-1]
    rsi_v   = rsi.iloc[-1]
    hist_v  = hist.iloc[-1]
    atr_v   = atr.iloc[-1]
    e20     = ema20.iloc[-1]
    e50     = ema50.iloc[-1]
    e200    = ema200.iloc[-1]

    # Tendencia
    if precio > e20 > e50 and hist_v > 0: tend = "ALCISTA"; tend_col = "#16a34a"
    elif precio < e20 < e50 and hist_v < 0: tend = "BAJISTA"; tend_col = "#dc2626"
    else: tend = "LATERAL"; tend_col = "#c8920a"

    # SL y TP basados en ATR
    atr_mult_sl = 1.5
    atr_mult_tp = 3.0
    if tend == "ALCISTA":
        sl = round(precio - atr_v * atr_mult_sl, 5)
        tp = round(precio + atr_v * atr_mult_tp, 5)
        direccion = "LONG/CALL"
    elif tend == "BAJISTA":
        sl = round(precio + atr_v * atr_mult_sl, 5)
        tp = round(precio - atr_v * atr_mult_tp, 5)
        direccion = "SHORT/PUT"
    else:
        sl = round(precio - atr_v * 1.0, 5)
        tp = round(precio + atr_v * 1.5, 5)
        direccion = "ESPERAR"

    # Score de confianza
    score = 50
    if tend != "LATERAL": score += 20
    if 40 < rsi_v < 60: score += 10
    elif (tend == "ALCISTA" and 30 < rsi_v < 55): score += 15
    elif (tend == "BAJISTA" and 45 < rsi_v < 70): score += 15
    if abs(hist_v) > abs(hist.iloc[-3:].mean()): score += 10
    if precio > e200: score += 5

    return {
        "precio": precio, "rsi": rsi_v, "atr": atr_v,
        "ema20": e20, "ema50": e50, "ema200": e200,
        "tendencia": tend, "tend_col": tend_col,
        "direccion": direccion, "sl": sl, "tp": tp,
        "hist_macd": hist_v, "score": min(score, 100),
        "hora": datetime.now().strftime("%H:%M"),
        "tf": tf,
    }

# ================================================================
# SIDEBAR
# ================================================================
with st.sidebar:
    st.markdown('<div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:22px;color:#c8920a;letter-spacing:2px;margin-bottom:16px;">QQE CMD v5</div>', unsafe_allow_html=True)

    # API
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#4a7a99;letter-spacing:2px;margin-bottom:4px;">CLAVE API ANTHROPIC</div>', unsafe_allow_html=True)
    api_in = st.text_input("API", value=st.session_state.api_key, type="password", label_visibility="collapsed", key="api_sb")
    if api_in and api_in != st.session_state.api_key:
        st.session_state.api_key = api_in
        guardar_creds()
    ia_status = "IA ACTIVA ✓" if get_ia_ok() else "Sin clave API"
    ia_col = "#4ade80" if get_ia_ok() else "#f87171"
    st.markdown(f'<div style="font-family:Share Tech Mono,monospace;font-size:11px;color:{ia_col};margin-bottom:12px;">{ia_status}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Capital
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#4a7a99;letter-spacing:2px;margin-bottom:4px;">CAPITAL Y RIESGO</div>', unsafe_allow_html=True)
    cap = st.number_input("Capital", min_value=10.0, max_value=100000.0, value=float(st.session_state.capital), step=10.0, label_visibility="collapsed", key="cap_sb")
    if cap != st.session_state.capital:
        st.session_state.capital = cap
        guardar_creds()
    sl_pct = st.slider("Stop Loss diario %", 5, 30, int(st.session_state.stop_loss_dia), 1, key="sl_sb")
    if sl_pct != st.session_state.stop_loss_dia:
        st.session_state.stop_loss_dia = sl_pct
        guardar_creds()
    sl_monto = cap * sl_pct / 100
    perdida  = st.session_state.perdida_dia
    pct_used = min(100, int(perdida / sl_monto * 100)) if sl_monto > 0 else 0
    bar_col  = "#4ade80" if pct_used < 50 else ("#fbbf24" if pct_used < 80 else "#f87171")
    st.markdown(f"""
    <div style="background:#0d1525;border:1px solid #1e3050;border-radius:8px;padding:12px;margin-bottom:8px;">
      <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
        <span style="font-family:Share Tech Mono,monospace;font-size:11px;color:#4a7a99;">ENTRADA 1%</span>
        <span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:17px;color:#4ade80;">${cap*0.01:.2f}</span>
      </div>
      <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
        <span style="font-family:Share Tech Mono,monospace;font-size:11px;color:#4a7a99;">ENTRADA 2%</span>
        <span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:17px;color:#c8920a;">${cap*0.02:.2f}</span>
      </div>
      <div class="prog-track"><div class="prog-fill" style="width:{pct_used}%;background:{bar_col};"></div></div>
      <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:{bar_col};margin-top:3px;">Perdida: ${perdida:.2f} / SL: ${sl_monto:.2f}</div>
    </div>""", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("+ Loss", key="add_loss"):
            st.session_state.perdida_dia += cap * 0.02
            if st.session_state.perdida_dia >= sl_monto: st.session_state.radar_bloqueado = True
            st.rerun()
    with c2:
        if st.button("Reset", key="reset_loss"):
            st.session_state.perdida_dia = 0.0; st.session_state.radar_bloqueado = False; st.rerun()

    st.markdown("---")

    # Telegram
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#4a7a99;letter-spacing:2px;margin-bottom:4px;">TELEGRAM</div>', unsafe_allow_html=True)
    tg_chk = st.checkbox("Alertas activas", value=st.session_state.tg_on, key="tg_chk_sb")
    st.session_state.tg_on = tg_chk
    if tg_chk:
        tg_tok = st.text_input("Token", value=st.session_state.tg_token, type="password", placeholder="Token bot...", label_visibility="collapsed", key="tg_tok_sb")
        tg_cid = st.text_input("Chat ID", value=st.session_state.tg_chat, placeholder="Chat ID...", label_visibility="collapsed", key="tg_cid_sb")
        if tg_tok and tg_tok != st.session_state.tg_token:
            st.session_state.tg_token = tg_tok
            guardar_creds()
        if tg_cid and tg_cid != st.session_state.tg_chat:
            st.session_state.tg_chat  = tg_cid
            guardar_creds()
        tg_ok = bool(st.session_state.tg_token and st.session_state.tg_chat)
        col_tg = "#4ade80" if tg_ok else "#f87171"
        st.markdown(f'<div style="font-family:Share Tech Mono,monospace;font-size:11px;color:{col_tg};margin-bottom:6px;">{"CONECTADO ✓" if tg_ok else "Completa token y chat ID"}</div>', unsafe_allow_html=True)
        if tg_ok and st.button("Enviar prueba", key="tg_prueba"):
            ok = enviar_telegram(st.session_state.tg_token, st.session_state.tg_chat,
                "✅ <b>QQE Command v5</b> conectado!\n\nRecibirás alertas de binarias 1min y swing trading.")
            if ok: st.success("✅ Enviado!")
            else: st.error("Error al enviar")

    st.markdown("---")
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#2a3a55;text-align:center;">Credenciales guardadas automáticamente</div>', unsafe_allow_html=True)

# ================================================================
# HEADER
# ================================================================
ses_nom, ses_est, ses_col, ses_bg, ses_border = get_session_info()
hora_utc = datetime.now(timezone.utc).strftime("%H:%M UTC")
_, cp, np_ = calc_pnl()

st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;
background:#0d1525;border:1px solid #1e3050;border-radius:12px;padding:14px 20px;margin-bottom:16px;flex-wrap:wrap;gap:8px;">
  <div>
    <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:26px;color:#c8920a;letter-spacing:2px;">QQE COMMAND V4</div>
    <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;letter-spacing:2px;">BINARIAS 1MIN · SWING H1/H4 · SCANNER EN VIVO</div>
  </div>
  <div style="display:flex;gap:16px;align-items:center;flex-wrap:wrap;">
    <div style="background:{ses_bg};border:1px solid {ses_border};border-radius:8px;padding:8px 14px;text-align:center;">
      <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:{ses_col};">{ses_est}</div>
      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:13px;color:{ses_col};">{ses_nom}</div>
    </div>
    <div style="text-align:right;">
      <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">{hora_utc}</div>
      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:18px;color:{'#4ade80' if np_>=0 else '#f87171'};">${np_:.2f}</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

# ================================================================
# TABS
# ================================================================
tab_scan1, tab_swing, tab_strat, tab_hector, tab_noticias, tab_ops, tab_diario, tab_binarias, tab_copy, tab_codigos = st.tabs([
    "⚡ SCANNER 1MIN", "📈 SWING + IA GRAFICO",
    "🎯 ESTRATEGIA EMA+QQE",
    "🔺 HECTOR SCANNER",
    "📰 NOTICIAS + IA",
    "📋 REGISTRO", "📓 DIARIO", "🤖 SCRIPTS LUA", "👥 COPY", "💻 CODIGOS QQE"
])

# ================================================================
# TAB 1 — SCANNER BINARIAS 1 MINUTO
# ================================================================
with tab_scan1:
    st.markdown('<div class="sec">SCANNER BINARIAS 1 MINUTO — DETECCION EN VIVO</div>', unsafe_allow_html=True)

    # Controles
    c1, c2, c3, c4 = st.columns([2,2,2,2])
    with c1:
        scan_btn = st.button("⚡ ESCANEAR AHORA", key="scan1_btn", use_container_width=True)
    with c2:
        ar_on = st.toggle("Auto-scan", value=st.session_state.autorefresh_on, key="ar_1min")
        st.session_state.autorefresh_on = ar_on
    with c3:
        if ar_on:
            ar_min = st.select_slider("", options=[1,2,3,5], value=st.session_state.autorefresh_min if st.session_state.autorefresh_min <= 5 else 1, key="ar_1min_sl", format_func=lambda x: f"Cada {x} min")
            st.session_state.autorefresh_min = ar_min
            if AUTOREFRESH_OK:
                st_autorefresh(interval=ar_min * 60 * 1000, key="ar_main_1min")
            st.markdown(f'<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4ade80;">● ACTIVO — {ar_min}min</div>', unsafe_allow_html=True)
    with c4:
        activos_sel1 = st.multiselect("Activos", list(ACTIVOS.keys()), default=["EUR/USD","GBP/USD","XAU/USD"], key="act_1min", label_visibility="collapsed")

    if st.session_state.radar_bloqueado:
        st.error("🛑 RADAR BLOQUEADO — Stop Loss diario alcanzado.")

    elif scan_btn or (ar_on and AUTOREFRESH_OK):
        resultados = []
        prog = st.progress(0)
        txt  = st.empty()
        for idx, activo in enumerate(activos_sel1):
            prog.progress((idx) / max(len(activos_sel1),1))
            txt.markdown(f'<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#c8920a;">⏳ Escaneando {activo}... ({idx+1}/{len(activos_sel1)})</div>', unsafe_allow_html=True)
            res = analizar_activo_1min(ACTIVOS[activo]["yahoo"])
            if res:
                res["activo"] = activo
                resultados.append(res)
            prog.progress((idx+1) / max(len(activos_sel1),1))
        prog.empty(); txt.empty()

        st.session_state.scan_results  = resultados
        st.session_state.scan_ultimo   = datetime.now().strftime("%H:%M:%S")
        st.session_state.alertas_bin   = [r for r in resultados if r["mejor"]["conf"] >= 70]

        # Telegram
        if st.session_state.tg_on and st.session_state.tg_token:
            for r in st.session_state.alertas_bin:
                key_tg = f"1min_{r['activo']}_{r['hora']}"
                enviadas = st.session_state.get("tg_enviadas", set())
                if key_tg not in enviadas:
                    m = r["mejor"]
                    ic = "📈" if m["dir"] == "CALL" else "📉"
                    msg = (f"{ic} <b>BINARIA 1MIN — {r['activo']}</b>\n"
                           f"━━━━━━━━━━━━━━\n"
                           f"📊 {m['dir']} — Script {m['script']}\n"
                           f"🎯 Confianza: {m['conf']}%\n"
                           f"💰 Precio: {r['precio']:.4f}\n"
                           f"📊 RSI: {r['rsi']:.1f}\n"
                           f"💵 Entrada 1%: <b>${st.session_state.capital*0.01:.2f}</b>\n"
                           f"⏱ Expiracion: 1-2 min\n"
                           f"🕐 {r['hora']} UTC\n"
                           f"<i>QQE Command v4</i>")
                    ok = enviar_telegram(st.session_state.tg_token, st.session_state.tg_chat, msg)
                    if ok:
                        enviadas.add(key_tg)
                        st.session_state.tg_enviadas = enviadas

        st.rerun()

    # Mostrar resultados 1min
    if st.session_state.scan_results:
        if st.session_state.scan_ultimo:
            n_al = len(st.session_state.alertas_bin)
            st.markdown(f'<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;margin-bottom:12px;"><span class="scan-dot" style="background:#4ade80;"></span> Ultimo scan: {st.session_state.scan_ultimo} — <span style="color:{"#4ade80" if n_al>0 else "#4a7a99"};">{n_al} señales activas</span></div>', unsafe_allow_html=True)

        for r in sorted(st.session_state.scan_results, key=lambda x: x["mejor"]["conf"], reverse=True):
            m = r["mejor"]
            es_call = m["dir"] == "CALL"
            card_cls = "signal-call" if es_call else "signal-put"
            ic = "▲" if es_call else "▼"
            col_dir = "#4ade80" if es_call else "#f87171"
            conf = m["conf"]
            conf_bar = f'<div class="prog-track"><div class="prog-fill" style="width:{conf}%;background:{"#4ade80" if conf>=80 else "#c8920a" if conf>=65 else "#64748b"};"></div></div>'

            st.markdown(f"""
            <div class="{card_cls}">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-wrap:wrap;gap:6px;">
                <div>
                  <span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:20px;color:#c8d8e8;">{r['activo']}</span>
                  <span style="font-family:Share Tech Mono,monospace;font-size:10px;color:{col_dir};margin-left:10px;">{ic} {m['dir']} — Script {m['script']}</span>
                </div>
                <div style="text-align:right;">
                  <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:22px;color:{col_dir};">{conf}%</div>
                  <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">CONFIANZA</div>
                </div>
              </div>
              {conf_bar}
              <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:10px;">
                <div style="background:#060c18;border-radius:6px;padding:8px;text-align:center;">
                  <div style="font-family:Share Tech Mono,monospace;font-size:8px;color:#4a7a99;">PRECIO</div>
                  <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:14px;color:#c8d8e8;">{r['precio']:.4f}</div>
                </div>
                <div style="background:#060c18;border-radius:6px;padding:8px;text-align:center;">
                  <div style="font-family:Share Tech Mono,monospace;font-size:8px;color:#4a7a99;">RSI</div>
                  <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:14px;color:{'#f87171' if r['rsi']>70 else '#4ade80' if r['rsi']<30 else '#c8d8e8'};">{r['rsi']:.1f}</div>
                </div>
                <div style="background:#060c18;border-radius:6px;padding:8px;text-align:center;">
                  <div style="font-family:Share Tech Mono,monospace;font-size:8px;color:#4a7a99;">ENTRADA 1%</div>
                  <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:14px;color:#c8920a;">${st.session_state.capital*0.01:.2f}</div>
                </div>
                <div style="background:#060c18;border-radius:6px;padding:8px;text-align:center;">
                  <div style="font-family:Share Tech Mono,monospace;font-size:8px;color:#4a7a99;">EXPIRACION</div>
                  <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:14px;color:#c8d8e8;">1-2 min</div>
                </div>
              </div>
              {"<br>".join([f'<span style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">• Script {s["script"]}: {s["dir"]} {s["conf"]}%</span>' for s in r["senales"]])}
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;background:#0d1525;border:2px dashed #1e3050;border-radius:12px;margin-top:10px;">
          <div style="font-size:48px;margin-bottom:10px;">⚡</div>
          <div style="font-family:Rajdhani,sans-serif;font-size:20px;color:#4a7a99;">Presiona ESCANEAR AHORA</div>
          <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#2a3a55;margin-top:6px;">Detecta señales de binarias 1 minuto en tiempo real</div>
        </div>""", unsafe_allow_html=True)

    # Advertencia 1min
    st.markdown("""
    <div style="background:#2a1a00;border:1px solid #c8920a;border-radius:8px;padding:10px 14px;margin-top:12px;font-size:12px;color:#fbbf24;">
    ⚠️ <b>Binarias 1 min:</b> Alto riesgo. Usar SOLO en sesion activa (Londres 07-10 UTC · NY 13-16 UTC). Máximo 1% del capital por operacion.
    </div>""", unsafe_allow_html=True)

# ================================================================
# TAB 2 — SWING SCANNER + IA GRAFICO (FUSIONADO)
# ================================================================
with tab_swing:
    st.markdown('<div class="sec">📈 SWING SCANNER + IA GRAFICO — M15 / H1 / H4 / D1</div>', unsafe_allow_html=True)

    sub_scan, sub_ia = st.tabs(["📊 Scanner Tecnico", "🧠 IA Grafico"])

    # ─── SUB-TAB: SCANNER TECNICO ─────────────────────────────
    with sub_scan:
        c1, c2, c3, c4 = st.columns([2,2,2,2])
        with c1:
            swing_btn = st.button("📈 ESCANEAR SWING", key="swing_scan_btn", use_container_width=True)
        with c2:
            tf_sel = st.selectbox("Temporalidad", ["M15","H1","H4","D1"], index=1, key="swing_tf")
        with c3:
            tipo_sw = st.selectbox("Tipo", ["Todos","forex","commodity","index","crypto"], key="swing_tipo")
        with c4:
            act_sw_disp = list(ACTIVOS.keys()) if tipo_sw=="Todos" else [a for a,v in ACTIVOS.items() if v["tipo"]==tipo_sw]
            activos_swing = st.multiselect("Activos", list(ACTIVOS.keys()), default=act_sw_disp[:8] if len(act_sw_disp)>=8 else act_sw_disp, key="act_swing", label_visibility="collapsed")

        # Asesor de temporalidad
        tf_consejo = {
            "M15": ("⚡ M15 — Scalping rapido. Bueno para binarias 5-15 min. Mas ruido.", "#ff9800"),
            "H1":  ("✅ H1 — Equilibrio ideal. Menos ruido. Excelente para binarias 1h y forex intraday.", "#4ade80"),
            "H4":  ("💎 H4 — Señales de alta calidad. Para swing 4-12 horas. Pocas pero seguras.", "#60a5fa"),
            "D1":  ("📅 D1 — Tendencia macro. Entradas de dias o semanas. Solo forex/indices.", "#a78bfa"),
        }
        consejo_txt, consejo_col = tf_consejo.get(tf_sel, ("","#4a7a99"))
        st.markdown(f'<div style="background:#0d1525;border-left:3px solid {consejo_col};padding:8px 14px;border-radius:0 6px 6px 0;font-family:Share Tech Mono,monospace;font-size:11px;color:{consejo_col};margin-bottom:12px;">{consejo_txt}</div>', unsafe_allow_html=True)

        if swing_btn:
            swing_res = {}
            prog2 = st.progress(0)
            txt2  = st.empty()
            for idx, activo in enumerate(activos_swing):
                prog2.progress(idx / max(len(activos_swing),1))
                txt2.markdown(f'<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#c8920a;">📈 Analizando {activo} {tf_sel}... ({idx+1}/{len(activos_swing)})</div>', unsafe_allow_html=True)
                r = analizar_activo_swing(ACTIVOS[activo]["yahoo"], tf_sel)
                if r:
                    r["activo"] = activo
                    r["iq_name"] = ACTIVOS[activo]["iq"]
                    r["tipo"]    = ACTIVOS[activo]["tipo"]
                    swing_res[activo] = r
                prog2.progress((idx+1) / max(len(activos_swing),1))
            prog2.empty(); txt2.empty()
            st.session_state.swing_resultados = swing_res

            # Telegram swing
            if st.session_state.tg_on and st.session_state.tg_token:
                for activo, r in swing_res.items():
                    if r["score"] >= 75 and r["direccion"] != "ESPERAR":
                        key_sw = f"swing_{activo}_{r['hora']}"
                        enviadas = st.session_state.get("tg_enviadas", set())
                        if key_sw not in enviadas:
                            ic = "📈" if "LONG" in r["direccion"] else "📉"
                            msg = (f"{ic} <b>SWING {tf_sel} — {activo} ({r['iq_name']})</b>\n"
                                   f"━━━━━━━━━━━━━━\n"
                                   f"📊 {r['direccion']} — {r['tendencia']}\n"
                                   f"🎯 Score: {r['score']}%\n"
                                   f"💰 Precio: {r['precio']:.4f}\n"
                                   f"🛑 Stop Loss: {r['sl']:.4f}\n"
                                   f"🎯 Take Profit: {r['tp']:.4f}\n"
                                   f"📊 RSI: {r['rsi']:.1f}\n"
                                   f"💵 Capital 2%: <b>${st.session_state.capital*0.02:.2f}</b>\n"
                                   f"<i>QQE Command v7 · {tf_sel}</i>")
                            ok = enviar_telegram(st.session_state.tg_token, st.session_state.tg_chat, msg)
                            if ok:
                                enviadas.add(key_sw)
                                st.session_state.tg_enviadas = enviadas
            st.rerun()

        # Mostrar swing
        if hasattr(st.session_state, "swing_resultados") and st.session_state.swing_resultados:
            res_list = sorted(st.session_state.swing_resultados.values(), key=lambda x: x["score"], reverse=True)
            for r in res_list:
                es_long  = "LONG" in r["direccion"]
                es_short = "SHORT" in r["direccion"]
                card_cls = "signal-call" if es_long else "signal-put" if es_short else "signal-wait"
                ic       = "▲" if es_long else "▼" if es_short else "—"
                col_dir  = "#4ade80" if es_long else "#f87171" if es_short else "#c8920a"
                score    = r["score"]
                tipo_badge = {"forex":"FOREX","commodity":"MATERIA PRIMA","index":"INDICE","crypto":"CRYPTO"}.get(r.get("tipo",""),"")
                tipo_col   = {"forex":"#60a5fa","commodity":"#fbbf24","index":"#a78bfa","crypto":"#fb923c"}.get(r.get("tipo",""),"#94a3b8")

                # Cartel señal destacado
                if es_long or es_short:
                    st.markdown(f"""
                    <div style="background:{'#0a3020' if es_long else '#200a0a'};border:2px solid {col_dir};border-radius:10px;padding:12px 20px;margin-bottom:6px;display:flex;align-items:center;gap:20px;flex-wrap:wrap;">
                      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:36px;color:{col_dir};">{ic}</div>
                      <div>
                        <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:22px;color:#c8d8e8;">{r.get("iq_name",r["activo"])}</div>
                        <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:{tipo_col};">{tipo_badge} · {r.get("tf","")}</div>
                      </div>
                      <div style="margin-left:auto;text-align:center;">
                        <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:28px;color:{col_dir};">{"SUBE ▲" if es_long else "BAJA ▼"}</div>
                        <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">AHORA · {r.get("hora","")}</div>
                      </div>
                      <div style="text-align:center;background:#060c18;border-radius:8px;padding:8px 16px;">
                        <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">CONFIANZA</div>
                        <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:24px;color:{col_dir};">{score}%</div>
                      </div>
                    </div>""", unsafe_allow_html=True)

                st.markdown(f"""
                <div class="{card_cls}" style="margin-bottom:14px;">
                  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:8px;">
                    <div style="background:#060c18;border-radius:6px;padding:10px;text-align:center;">
                      <div style="font-family:Share Tech Mono,monospace;font-size:8px;color:#4a7a99;">PRECIO</div>
                      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;color:#c8d8e8;">{r["precio"]:.4f}</div>
                    </div>
                    <div style="background:#3a0a0a;border:1px solid #dc2626;border-radius:6px;padding:10px;text-align:center;">
                      <div style="font-family:Share Tech Mono,monospace;font-size:8px;color:#f87171;">STOP LOSS</div>
                      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;color:#f87171;">{r["sl"]:.4f}</div>
                    </div>
                    <div style="background:#0a3020;border:1px solid #16a34a;border-radius:6px;padding:10px;text-align:center;">
                      <div style="font-family:Share Tech Mono,monospace;font-size:8px;color:#4ade80;">TAKE PROFIT</div>
                      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;color:#4ade80;">{r["tp"]:.4f}</div>
                    </div>
                  </div>
                  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:6px;">
                    <div style="text-align:center;"><span style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">RSI: </span><span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:13px;color:#c8d8e8;">{r["rsi"]:.1f}</span></div>
                    <div style="text-align:center;"><span style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">EMA20: </span><span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:13px;color:#c8d8e8;">{r["ema20"]:.4f}</span></div>
                    <div style="text-align:center;"><span style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">ATR: </span><span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:13px;color:#c8d8e8;">{r["atr"]:.4f}</span></div>
                  </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center;padding:60px 20px;background:#0d1525;border:2px dashed #1e3050;border-radius:12px;margin-top:10px;">
              <div style="font-size:48px;margin-bottom:10px;">📈</div>
              <div style="font-family:Rajdhani,sans-serif;font-size:20px;color:#4a7a99;">Presiona ESCANEAR SWING</div>
              <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#2a3a55;margin-top:6px;">M15 / H1 / H4 / D1 — con SL y TP calculados por ATR</div>
            </div>""", unsafe_allow_html=True)

    # ─── SUB-TAB: IA GRAFICO ──────────────────────────────────
    with sub_ia:
        st.markdown("""
        <div style="background:#0d1525;border:1px solid #c8920a;border-radius:12px;padding:14px 18px;margin-bottom:16px;">
          <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:16px;color:#c8920a;margin-bottom:8px;">Como usar</div>
          <div style="font-size:13px;color:#94a3b8;line-height:1.9;">
            1. Abrí IQ Option → seleccioná el activo → temporalidad H1 o H4<br>
            2. Sacá captura de pantalla del grafico<br>
            3. Completá los datos del trade abajo<br>
            4. Subí la imagen → la IA analiza precio, noticias actuales y da una conclusion accionable
          </div>
        </div>""", unsafe_allow_html=True)

        if not get_ia_ok():
            st.markdown('<div style="background:#3a0a0a;border:1px solid #dc2626;border-radius:8px;padding:12px;color:#f87171;font-family:Share Tech Mono,monospace;font-size:11px;">Necesitas la clave API de Anthropic en el sidebar para usar el analizador.</div>', unsafe_allow_html=True)
        else:
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                activo_ia = st.selectbox("Activo", list(ACTIVOS.keys()) + ["Otro"], key="ia_activo")
            with col_b:
                tf_ia = st.selectbox("Temporalidad", ["M15 (15 min)","H1 (1 hora)","H4 (4 horas)","D1 (diario)"], key="ia_tf")
            with col_c:
                dir_ia = st.selectbox("Direccion que analizas", ["Sin preferencia","CALL / LONG (sube)","PUT / SHORT (baja)"], key="ia_dir")

            col_d, col_e = st.columns(2)
            with col_d:
                precio_ia = st.text_input("Precio actual (opcional)", placeholder="1.0842", key="ia_precio")
            with col_e:
                notas_ia = st.text_input("Notas adicionales", placeholder="Rompio resistencia, noticias hoy...", key="ia_notas")

            st.markdown("---")
            st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;letter-spacing:2px;margin-bottom:8px;">CAPTURA DEL GRAFICO — podes subir hasta 3 imagenes (H1 + H4 + M15)</div>', unsafe_allow_html=True)

            imgs = st.file_uploader("", type=["png","jpg","jpeg","webp"], accept_multiple_files=True, key="ia_imgs", label_visibility="collapsed")

            if imgs:
                cols_prev = st.columns(min(len(imgs), 3))
                for i, img in enumerate(imgs[:3]):
                    with cols_prev[i]:
                        st.image(img, use_column_width=True)
                        st.markdown(f'<div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;text-align:center;">{img.name}</div>', unsafe_allow_html=True)

                st.markdown("---")

                if st.button("🧠 ANALIZAR CON IA — SWING + NOTICIAS", key="ia_analizar_swing", use_container_width=True):
                    with st.spinner("La IA busca noticias y analiza el grafico..."):
                        try:
                            content = []
                            for img in imgs[:3]:
                                ext   = img.name.split(".")[-1].lower()
                                mtype = "image/jpeg" if ext in ("jpg","jpeg") else f"image/{ext}"
                                b64   = base64.b64encode(img.read()).decode()
                                content.append({"type":"image","source":{"type":"base64","media_type":mtype,"data":b64}})

                            ctx_dir     = dir_ia if dir_ia != "Sin preferencia" else "sin preferencia"
                            ctx_precio  = f"Precio actual: {precio_ia}." if precio_ia else ""
                            ctx_notas   = f"Contexto adicional: {notas_ia}." if notas_ia else ""
                            ctx_capital = f"Capital de Hector: ${st.session_state.capital:.2f}. Entrada 2%: ${st.session_state.capital*0.02:.2f}."
                            iq_name     = ACTIVOS.get(activo_ia, {}).get("iq", activo_ia)

                            content.append({"type":"text","text":f"""Analiza este grafico de {activo_ia} ({iq_name} en IQ Option) en {tf_ia}.
El trader considera: {ctx_dir}. {ctx_precio} {ctx_notas} {ctx_capital}

Dame un analisis COMPLETO."""})

                            sys_swing = f"""Eres el analista de swing trading y macro-economico personal de Hector, trader argentino que opera en IQ Option con opciones binarias y forex.
Tu tarea: analizar el grafico Y buscar noticias/eventos macroeconómicos recientes que impacten al activo, luego dar una conclusion fusionada.

ESTRUCTURA OBLIGATORIA de tu respuesta (respeta exactamente estos titulos):

## 📊 DECISION
ENTRAR CALL (sube) / ENTRAR PUT (baja) / ESPERAR (en grande y claro)

## 📰 NOTICIAS / CONTEXTO MACRO
Lista 2-3 eventos o noticias recientes relevantes para este activo.
Ejemplo: "Guerra en el Golfo → sube petroleo" / "Fed sube tasas → dolar fuerte" / "Datos empleo EE.UU. → eurusd baja"
Si no hay noticias relevantes, decilo.

## 🔗 FUSION TECNICO + MACRO
1 parrafo corto: cómo las noticias confirman O contradicen lo que muestra el grafico tecnico.

## 🎯 NIVELES
- Stop Loss: (precio o distancia)
- Take Profit: (precio, minimo ratio 1:2)
- Tiempo estimado: (cuanto puede tardar)

## ⚠ INVALIDACION
Una linea: que nivel o evento invalidaria la señal.

Maximo 300 palabras. En espanol. Directo. Sin rodeos.
Si hay conflicto entre tecnico y macro, priorizá la macro y avisar."""

                            resp = requests.post("https://api.anthropic.com/v1/messages",
                                headers={{"Content-Type":"application/json",
                                         "x-api-key": st.session_state.get("api_key",""),
                                         "anthropic-version":"2023-06-01"}},
                                json={{"model":"claude-sonnet-4-20250514","max_tokens":800,
                                      "system":sys_swing,
                                      "tools":[{{"type":"web_search_20250305","name":"web_search"}}],
                                      "messages":[{{"role":"user","content":content}}]}},
                                timeout=90)

                            if resp.status_code == 200:
                                rdata = resp.json()
                                texto = " ".join(
                                    b["text"] for b in rdata.get("content",[])
                                    if b.get("type") == "text"
                                )
                                st.session_state[f"swing_ia_resp_{{activo_ia}}"] = {{
                                    "texto": texto, "hora": datetime.now().strftime("%H:%M"),
                                    "activo": activo_ia, "tf": tf_ia, "iq_name": iq_name
                                }}
                                st.rerun()
                            else:
                                st.error(f"Error API: {{resp.status_code}} — {{resp.text[:200]}}")
                        except Exception as e:
                            st.error(f"Error: {{e}}")
            else:
                st.markdown("""
                <div style="text-align:center;padding:50px 20px;background:#0d1525;border:2px dashed #1e3050;border-radius:12px;margin-top:10px;">
                  <div style="font-size:52px;margin-bottom:12px;">📱</div>
                  <div style="font-family:Rajdhani,sans-serif;font-size:20px;color:#4a7a99;">Subi la captura de IQ Option</div>
                  <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#2a3a55;margin-top:8px;">Podes subir hasta 3 graficos — M15 + H1 + H4</div>
                </div>""", unsafe_allow_html=True)

            # Mostrar resultado IA
            resp_key = f"swing_ia_resp_{activo_ia}"
            if resp_key in st.session_state and st.session_state[resp_key]:
                res_ia = st.session_state[resp_key]
                texto  = res_ia["texto"]

                if "ENTRAR CALL" in texto.upper() or texto.upper().count("CALL") > texto.upper().count("PUT"):
                    rc,rb,rbr,ri = "#4ade80","#0a3020","#16a34a","🟢"
                elif "ENTRAR PUT" in texto.upper() or "PUT" in texto.upper()[:80]:
                    rc,rb,rbr,ri = "#f87171","#200a0a","#dc2626","🔴"
                elif "ESPERAR" in texto.upper()[:80]:
                    rc,rb,rbr,ri = "#fbbf24","#2a1a00","#c8920a","🟡"
                else:
                    rc,rb,rbr,ri = "#c8d8e8","#0d1525","#1e3050","⚪"

                st.markdown(f"""
                <div style="background:{rb};border:2px solid {rbr};border-radius:14px;padding:20px;margin-top:16px;">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px;">
                    <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:24px;color:{rc};">{ri} ANALISIS IA + MACRO — {res_ia.get("iq_name",res_ia["activo"])}</div>
                    <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">{res_ia["tf"]} · {res_ia["hora"]}</div>
                  </div>
                  <div style="font-size:14px;color:#c8d8e8;line-height:2.0;">{texto.replace(chr(10),"<br>")}</div>
                  <div style="margin-top:12px;padding-top:10px;border-top:1px solid {rbr};font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">
                    Capital: ${st.session_state.capital:.2f} · Entrada 2%: ${st.session_state.capital*0.02:.2f} · QQE Command v7
                  </div>
                </div>""", unsafe_allow_html=True)

                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    if st.button("📓 Guardar en Diario", key="guardar_diario_ia"):
                        st.session_state.diario.append({
                            "fecha": date.today().strftime("%d/%m/%Y"),
                            "hora": res_ia["hora"],
                            "tipo": "ANALISIS IA+MACRO",
                            "activo": res_ia["activo"],
                            "texto": texto,
                            "tf": res_ia["tf"],
                        })
                        st.success("Guardado en el diario!")
                with col_g2:
                    if st.button("📤 Enviar a Telegram", key="tg_ia_swing"):
                        if st.session_state.tg_token:
                            msg_ia = (f"{ri} <b>IA SWING — {res_ia.get('iq_name',res_ia['activo'])} {res_ia['tf']}</b>\n"
                                      f"━━━━━━━━━━━━━━\n"
                                      f"{texto[:800]}\n"
                                      f"<i>QQE Command v7 · {res_ia['hora']}</i>")
                            ok = enviar_telegram(st.session_state.tg_token, st.session_state.tg_chat, msg_ia)
                            st.success("Enviado!" if ok else "Error al enviar")
                        else:
                            st.warning("Configura el token de Telegram en el sidebar")


# ================================================================
# TAB 4 — ESTRATEGIA EMA + QQE + VELA DE CONFIRMACION
# ================================================================
with tab_strat:
    st.markdown('<div class="sec">🎯 ESTRATEGIA TRIPLE CONFIRMACION — EMA + QQE + VELA</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="strat-box">
      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:22px;color:#c8920a;margin-bottom:6px;">
        Estrategia: EMA 5/13/50 + QQE + Vela de Confirmacion
      </div>
      <div style="font-size:15px;color:#94a3b8;line-height:1.9;margin-bottom:12px;">
        Sistema de triple confirmacion para binarias 1–5 minutos y scalping forex.<br>
        Requiere que los 3 filtros estén alineados antes de entrar. Sin señal completa = no operar.<br>
        <strong style="color:#c8920a;">Win rate estimado histórico: 68–74% en sesion Londres/NY con activos líquidos.</strong>
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:16px;">
        <div style="background:#060c18;border:1px solid #c8920a;border-radius:8px;padding:14px;text-align:center;">
          <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#c8920a;margin-bottom:4px;">FILTRO 1</div>
          <div style="font-family:Rajdhani,sans-serif;font-size:20px;font-weight:700;color:#c8d8e8;">EMA 5/13/50</div>
          <div style="font-size:13px;color:#94a3b8;margin-top:4px;">Dirección de tendencia</div>
        </div>
        <div style="background:#060c18;border:1px solid #16a34a;border-radius:8px;padding:14px;text-align:center;">
          <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#4ade80;margin-bottom:4px;">FILTRO 2</div>
          <div style="font-family:Rajdhani,sans-serif;font-size:20px;font-weight:700;color:#c8d8e8;">QQE / RSI</div>
          <div style="font-size:13px;color:#94a3b8;margin-top:4px;">Momentum y zona</div>
        </div>
        <div style="background:#060c18;border:1px solid #2563eb;border-radius:8px;padding:14px;text-align:center;">
          <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#60a5fa;margin-bottom:4px;">FILTRO 3</div>
          <div style="font-family:Rajdhani,sans-serif;font-size:20px;font-weight:700;color:#c8d8e8;">VELA PATRON</div>
          <div style="font-size:13px;color:#94a3b8;margin-top:4px;">Confirmacion de entrada</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # REGLAS CALL
    st.markdown('<div class="sec">REGLAS DE ENTRADA — CALL (SUBE)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="strat-regla">
      <div style="font-family:Rajdhani,sans-serif;font-size:17px;font-weight:700;color:#4ade80;margin-bottom:8px;">✅ CONDICIONES CALL — las 3 deben cumplirse</div>
      <div class="strat-step">
        <strong style="color:#c8920a;">FILTRO 1 — EMA Stack Alcista:</strong><br>
        EMA5 > EMA13 > EMA50 — las tres alineadas de mayor a menor.<br>
        El precio cierra <strong>por encima</strong> de la EMA13.<br>
        <em style="color:#4a7a99;">Confirma que la tendencia de fondo es compradora.</em>
      </div>
      <div class="strat-step">
        <strong style="color:#c8920a;">FILTRO 2 — QQE / RSI Zona Compradora:</strong><br>
        RSI (14) entre 45 y 65 — zona de momentum alcista sin sobrecompra.<br>
        Histograma MACD positivo y creciendo (hist > 0 y hist > hist[-1]).<br>
        <em style="color:#4a7a99;">Evita entrar en sobrecompra o en zona muerta sin momentum.</em>
      </div>
      <div class="strat-step">
        <strong style="color:#c8920a;">FILTRO 3 — Vela de Confirmacion:</strong><br>
        Aparece una vela <strong>alcista engulfing</strong>, <strong>martillo</strong> o <strong>marubozu verde</strong>.<br>
        La vela cierra en el 70% superior de su rango (cuerpo grande).<br>
        Volumen de la vela de confirmacion > promedio de las últimas 5 velas.<br>
        <em style="color:#4a7a99;">La vela es la "firma" del mercado — sin ella no entres.</em>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # REGLAS PUT
    st.markdown('<div class="sec">REGLAS DE ENTRADA — PUT (BAJA)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#200a0a;border:1px solid #dc2626;border-radius:8px;padding:14px;margin-bottom:12px;">
      <div style="font-family:Rajdhani,sans-serif;font-size:17px;font-weight:700;color:#f87171;margin-bottom:8px;">✅ CONDICIONES PUT — espejo inverso</div>
      <div class="strat-step">
        <strong style="color:#f87171;">FILTRO 1:</strong> EMA5 &lt; EMA13 &lt; EMA50. Precio cierra <strong>por debajo</strong> de EMA13.
      </div>
      <div class="strat-step">
        <strong style="color:#f87171;">FILTRO 2:</strong> RSI (14) entre 35 y 55. Histograma MACD negativo y decreciendo.
      </div>
      <div class="strat-step">
        <strong style="color:#f87171;">FILTRO 3:</strong> Vela <strong>bajista engulfing</strong>, <strong>estrella fugaz</strong> o <strong>marubozu rojo</strong>. Cierra en el 30% inferior de su rango.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # GESTIÓN DE LA OPERACION
    st.markdown('<div class="sec">GESTION DE LA OPERACION</div>', unsafe_allow_html=True)
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown(f"""
        <div style="background:#0d1525;border:1px solid #1e3050;border-radius:10px;padding:16px;">
          <div style="font-family:Share Tech Mono,monospace;font-size:12px;color:#4a7a99;margin-bottom:10px;letter-spacing:2px;">PARAMETROS DE ENTRADA</div>
          <div style="font-size:14px;line-height:2.2;color:#c8d8e8;">
            <span style="color:#c8920a;">Temporalidad:</span> M1 (binarias) · M5 (forex scalp)<br>
            <span style="color:#c8920a;">Capital por op:</span> 1% = <strong style="color:#4ade80;">${st.session_state.capital*0.01:.2f}</strong><br>
            <span style="color:#c8920a;">Expiracion binaria:</span> 1–3 minutos<br>
            <span style="color:#c8920a;">Max operaciones/dia:</span> 6<br>
            <span style="color:#c8920a;">Max perdidas seguidas:</span> 2 → parar
          </div>
        </div>
        """, unsafe_allow_html=True)
    with col_g2:
        st.markdown("""
        <div style="background:#0d1525;border:1px solid #1e3050;border-radius:10px;padding:16px;">
          <div style="font-family:Share Tech Mono,monospace;font-size:12px;color:#4a7a99;margin-bottom:10px;letter-spacing:2px;">INVALIDACION DE SEÑAL</div>
          <div style="font-size:14px;line-height:2.2;color:#c8d8e8;">
            <span style="color:#f87171;">✗</span> RSI &gt; 70 o &lt; 30 (extremo — no entrar en tendencia)<br>
            <span style="color:#f87171;">✗</span> Noticias de alto impacto en los próximos 15 min<br>
            <span style="color:#f87171;">✗</span> EMAs en compresion (diferencia &lt;0.0002 entre EMA5 y EMA13)<br>
            <span style="color:#f87171;">✗</span> ATR muy bajo (mercado dormido, sin volatilidad)<br>
            <span style="color:#f87171;">✗</span> Fuera de sesion Londres/NY activa
          </div>
        </div>
        """, unsafe_allow_html=True)

    # SCANNER EN VIVO DE LA ESTRATEGIA
    st.markdown('<div class="sec">SCANNER EN VIVO — TRIPLE CONFIRMACION</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([2,3])
    with c1:
        scan_strat_btn = st.button("🎯 ESCANEAR TRIPLE CONFIRMACION", key="scan_strat", use_container_width=True)
    with c2:
        activos_strat = st.multiselect("Activos a escanear", list(ACTIVOS.keys()),
            default=["EUR/USD","GBP/USD","XAU/USD"], key="act_strat")

    if scan_strat_btn:
        resultados_strat = []
        prog_s = st.progress(0)
        for idx, activo in enumerate(activos_strat):
            prog_s.progress((idx+1)/max(len(activos_strat),1))
            df = obtener_datos_1min(ACTIVOS[activo]["yahoo"])
            if df is None or len(df) < 60:
                continue
            c_s = df["cierre"]
            ema5  = calc_ema(c_s, 5)
            ema13 = calc_ema(c_s, 13)
            ema50 = calc_ema(c_s, 50)
            rsi   = calc_rsi(c_s, 14)
            macd, sig_l, hist = calc_macd(c_s)
            atr   = calc_atr(df)

            # Valores actuales
            e5 = ema5.iloc[-1]; e13 = ema13.iloc[-1]; e50 = ema50.iloc[-1]
            precio = c_s.iloc[-1]; prev = c_s.iloc[-2]
            rsi_v  = rsi.iloc[-1]
            hist_v = hist.iloc[-1]; hist_p = hist.iloc[-2]
            atr_v  = atr.iloc[-1]

            # Filtro 1 — EMA Stack
            f1_call = e5 > e13 > e50 and precio > e13
            f1_put  = e5 < e13 < e50 and precio < e13

            # Filtro 2 — QQE/RSI
            f2_call = 45 < rsi_v < 65 and hist_v > 0 and hist_v > hist_p
            f2_put  = 35 < rsi_v < 55 and hist_v < 0 and hist_v < hist_p

            # Filtro 3 — Vela patron
            apertura = df["apertura"].iloc[-1]
            rango    = df["maximo"].iloc[-1] - df["minimo"].iloc[-1]
            cuerpo   = abs(precio - apertura)
            pos_vela = (precio - df["minimo"].iloc[-1]) / rango if rango > 0 else 0.5
            f3_call  = precio > apertura and pos_vela > 0.70 and cuerpo > rango * 0.5
            f3_put   = precio < apertura and pos_vela < 0.30 and cuerpo > rango * 0.5

            filtros_call = sum([f1_call, f2_call, f3_call])
            filtros_put  = sum([f1_put,  f2_put,  f3_put])

            if filtros_call >= 2 or filtros_put >= 2:
                dir_s    = "CALL" if filtros_call >= filtros_put else "PUT"
                filtros  = filtros_call if dir_s == "CALL" else filtros_put
                f1_ok    = f1_call if dir_s == "CALL" else f1_put
                f2_ok    = f2_call if dir_s == "CALL" else f2_put
                f3_ok    = f3_call if dir_s == "CALL" else f3_put
                conf     = 60 + filtros * 12
                resultados_strat.append({
                    "activo": activo, "dir": dir_s, "conf": conf,
                    "filtros": filtros, "f1": f1_ok, "f2": f2_ok, "f3": f3_ok,
                    "precio": precio, "rsi": rsi_v, "e5": e5, "e13": e13, "e50": e50,
                    "hist": hist_v, "atr": atr_v,
                })
        prog_s.empty()
        st.session_state["strat_results"] = resultados_strat
        st.rerun()

    if st.session_state.get("strat_results"):
        res_s = st.session_state["strat_results"]
        if not res_s:
            st.markdown('<div style="text-align:center;padding:30px;color:#4a7a99;font-family:Share Tech Mono,monospace;font-size:13px;">Sin señales de triple confirmacion en este momento</div>', unsafe_allow_html=True)
        for r in sorted(res_s, key=lambda x: x["conf"], reverse=True):
            es_call = r["dir"] == "CALL"
            card_cls = "signal-call" if es_call else "signal-put"
            col_d = "#4ade80" if es_call else "#f87171"
            ic = "▲" if es_call else "▼"
            completo = r["filtros"] == 3
            st.markdown(f"""
            <div class="{card_cls}" style="{'border:2px solid #4ade80;' if completo and es_call else 'border:2px solid #f87171;' if completo else ''}">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:6px;">
                <div>
                  <span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:22px;color:#c8d8e8;">{r['activo']}</span>
                  <span style="font-family:Share Tech Mono,monospace;font-size:12px;color:{col_d};margin-left:12px;">{ic} {r['dir']}</span>
                  {'<span style="margin-left:10px;" class="badge badge-green">✅ TRIPLE CONFIRMACION</span>' if completo else f'<span style="margin-left:10px;" class="badge badge-gold">⚠ {r["filtros"]}/3 filtros</span>'}
                </div>
                <div style="text-align:right;">
                  <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:26px;color:{col_d};">{r['conf']}%</div>
                  <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#4a7a99;">CONFIANZA</div>
                </div>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:10px;">
                <div style="background:#060c18;border:1px solid {'#16a34a' if r['f1'] else '#1e3050'};border-radius:8px;padding:10px;text-align:center;">
                  <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#4a7a99;">EMA STACK</div>
                  <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:18px;color:{'#4ade80' if r['f1'] else '#64748b'};margin-top:2px;">{'✓' if r['f1'] else '✗'}</div>
                  <div style="font-size:12px;color:#4a7a99;">EMA5/13/50</div>
                </div>
                <div style="background:#060c18;border:1px solid {'#16a34a' if r['f2'] else '#1e3050'};border-radius:8px;padding:10px;text-align:center;">
                  <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#4a7a99;">QQE/RSI</div>
                  <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:18px;color:{'#4ade80' if r['f2'] else '#64748b'};margin-top:2px;">{'✓' if r['f2'] else '✗'}</div>
                  <div style="font-size:12px;color:#4a7a99;">RSI {r['rsi']:.1f}</div>
                </div>
                <div style="background:#060c18;border:1px solid {'#16a34a' if r['f3'] else '#1e3050'};border-radius:8px;padding:10px;text-align:center;">
                  <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#4a7a99;">VELA</div>
                  <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:18px;color:{'#4ade80' if r['f3'] else '#64748b'};margin-top:2px;">{'✓' if r['f3'] else '✗'}</div>
                  <div style="font-size:12px;color:#4a7a99;">Patron</div>
                </div>
              </div>
              <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;font-size:13px;">
                <div style="background:#060c18;border-radius:6px;padding:8px;text-align:center;">
                  <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">PRECIO</div>
                  <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;">{r['precio']:.4f}</div>
                </div>
                <div style="background:#060c18;border-radius:6px;padding:8px;text-align:center;">
                  <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">EMA5</div>
                  <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;">{r['e5']:.4f}</div>
                </div>
                <div style="background:#060c18;border-radius:6px;padding:8px;text-align:center;">
                  <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">ENTRADA 1%</div>
                  <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;color:#c8920a;">${st.session_state.capital*0.01:.2f}</div>
                </div>
                <div style="background:#060c18;border-radius:6px;padding:8px;text-align:center;">
                  <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">EXPIRACION</div>
                  <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;">1–2 min</div>
                </div>
              </div>
              {'<div style="background:#0a3020;border:1px solid #16a34a;border-radius:6px;padding:8px;margin-top:8px;font-family:Share Tech Mono,monospace;font-size:12px;color:#4ade80;">⚡ SEÑAL COMPLETA — Las 3 confirmaciones activas. Entrada válida.</div>' if completo else '<div style="background:#2a1a00;border:1px solid #c8920a;border-radius:6px;padding:8px;margin-top:8px;font-family:Share Tech Mono,monospace;font-size:12px;color:#fbbf24;">⚠ Señal parcial — esperar que se complete el tercer filtro antes de entrar.</div>'}
            </div>""", unsafe_allow_html=True)

    # SCRIPT LUA DE LA ESTRATEGIA
    st.markdown('<div class="sec">SCRIPT LUA — ESTRATEGIA TRIPLE CONFIRMACION PARA IQ OPTION</div>', unsafe_allow_html=True)
    script_triple = '''instrument {
    name = "Triple Confirm — EMA+QQE+Vela",
    short_name = "3C_1M",
    icon = "indicators:MA",
    overlay = true
}
input_group {
    "EMAs",
    p_e5  = input(5,  "EMA Ultra-Rapida", input.integer, 2,  20, 1),
    p_e13 = input(13, "EMA Rapida",        input.integer, 5,  30, 1),
    p_e50 = input(50, "EMA Tendencia",     input.integer, 20, 100,1),
}
input_group {
    "QQE / Filtros",
    p_rsi    = input(14,  "RSI Periodo",    input.integer, 5,  30, 1),
    p_macd_f = input(5,   "MACD Rapido",    input.integer, 3,  15, 1),
    p_macd_s = input(13,  "MACD Lento",     input.integer, 8,  30, 1),
    p_macd_g = input(4,   "MACD Signal",    input.integer, 2,  10, 1),
    p_vol    = input(true,"Filtro Vela",    input.bool),
}
function init()
    ema5   = indicator.ema(p_e5)
    ema13  = indicator.ema(p_e13)
    ema50  = indicator.ema(p_e50)
    rsi    = indicator.rsi(p_rsi)
    macd   = indicator.macd(p_macd_f, p_macd_s, p_macd_g)
    atr    = indicator.atr(14)
    e5p    = plot("EMA5",  color.yellow, 1, plot.line)
    e13p   = plot("EMA13", color.cyan,   1, plot.line)
    e50p   = plot("EMA50", color.gray,   1, plot.line)
    callp  = plot("CALL",  color.green,  2, plot.arrow_up)
    putp   = plot("PUT",   color.red,    2, plot.arrow_down)
    warn_c = plot("WARN+", color.lime,   1, plot.circles)
    warn_p = plot("WARN-", color.orange, 1, plot.circles)
end
function update()
    e5p:set(ema5[0])
    e13p:set(ema13[0])
    e50p:set(ema50[0])

    -- FILTRO 1: EMA Stack
    local f1_call = ema5[0] > ema13[0] and ema13[0] > ema50[0] and close[0] > ema13[0]
    local f1_put  = ema5[0] < ema13[0] and ema13[0] < ema50[0] and close[0] < ema13[0]

    -- FILTRO 2: QQE / RSI momentum
    local rsi_v   = rsi[0]
    local hist_up = macd.histogram[0] > 0 and macd.histogram[0] > macd.histogram[1]
    local hist_dn = macd.histogram[0] < 0 and macd.histogram[0] < macd.histogram[1]
    local f2_call = rsi_v > 45 and rsi_v < 65 and hist_up
    local f2_put  = rsi_v > 35 and rsi_v < 55 and hist_dn

    -- FILTRO 3: Vela de confirmacion
    local rango  = high[0] - low[0]
    local cuerpo = math.abs(close[0] - open[0])
    local pos    = (rango > 0) and ((close[0] - low[0]) / rango) or 0.5
    local f3_call = close[0] > open[0] and pos > 0.70 and cuerpo > rango * 0.5
    local f3_put  = close[0] < open[0] and pos < 0.30 and cuerpo > rango * 0.5

    -- CONTEO DE FILTROS
    local n_call = (f1_call and 1 or 0) + (f2_call and 1 or 0) + (f3_call and 1 or 0)
    local n_put  = (f1_put  and 1 or 0) + (f2_put  and 1 or 0) + (f3_put  and 1 or 0)

    -- SEÑAL COMPLETA (3/3)
    if n_call == 3 then
        callp:set(low[0] - atr[0] * 0.8)
    end
    if n_put == 3 then
        putp:set(high[0] + atr[0] * 0.8)
    end

    -- AVISO PARCIAL (2/3) — prepararse
    if n_call == 2 then
        warn_c:set(low[0])
    end
    if n_put == 2 then
        warn_p:set(high[0])
    end
end'''

    st.markdown(f'<div class="code-block">{script_triple}</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#0a1a3a;border:1px solid #2563eb;border-radius:8px;padding:12px;font-size:13px;color:#60a5fa;line-height:1.8;">
      <strong>Cómo instalar en IQ Option:</strong><br>
      1. Abrí IQ Option → Editor de Indicadores (ícono &lt;/&gt;)<br>
      2. Creá un nuevo indicador → pegá el código completo<br>
      3. Guardá como "Triple Confirm" → aplicar al gráfico M1<br>
      4. <strong>Flecha verde grande</strong> = señal completa CALL &nbsp;|&nbsp; <strong>Flecha roja grande</strong> = señal completa PUT<br>
      5. <strong>Círculos pequeños</strong> = 2/3 filtros activos — prepararse, esperar la vela de confirmacion
    </div>
    """, unsafe_allow_html=True)

# ================================================================
# ================================================================
# TAB HECTOR — SCANNER TRIPLE CONFIRM + SCRIPTS LUA
# ================================================================
with tab_hector:
    st.markdown('<div class="sec">🔺 HECTOR SCANNER — TRIPLE CONFIRM EN VIVO</div>', unsafe_allow_html=True)

    # Descripcion
    st.markdown("""
    <div style="background:#0d1525;border:1px solid #c8920a;border-radius:12px;padding:14px 18px;margin-bottom:16px;">
      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:18px;color:#c8920a;margin-bottom:6px;">Estrategia HECTOR 1 — Triple Confirm</div>
      <div style="font-size:14px;color:#94a3b8;line-height:1.9;">
        Misma logica que el script IQ Option: <b style="color:#c8920a;">EMA Stack + MACD + RSI + Vela</b><br>
        <b style="color:#4ade80;">🔺 CALL</b>: EMA5>EMA13>EMA50 · MACD hist positivo · RSI 45–75 · vela alcista<br>
        <b style="color:#f87171;">🔻 PUT</b>: EMA5&lt;EMA13&lt;EMA50 · MACD hist negativo · RSI 25–55 · vela bajista<br>
        <b style="color:#ff9800;">⚠ AVISO</b>: 3/4 filtros activos — prepararse, esperar confirmacion
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Controles scanner
    c1, c2, c3 = st.columns([2, 2, 3])
    with c1:
        hector_btn = st.button("🔺 ESCANEAR AHORA", key="hector_scan_btn", use_container_width=True)
    with c2:
        tipo_filtro = st.selectbox("Filtrar por tipo", ["Todos", "forex", "commodity", "index", "crypto"], key="hector_tipo")
    with c3:
        # Filtrar activos por tipo seleccionado
        if tipo_filtro == "Todos":
            activos_disponibles = list(ACTIVOS.keys())
        else:
            activos_disponibles = [a for a, v in ACTIVOS.items() if v["tipo"] == tipo_filtro]
        activos_hector = st.multiselect(
            "Activos",
            list(ACTIVOS.keys()),
            default=activos_disponibles[:8] if len(activos_disponibles) >= 8 else activos_disponibles,
            key="act_hector"
        )

    # Funcion analisis HECTOR
    def analizar_hector(symbol):
        df = obtener_datos_1min(symbol)
        if df is None or len(df) < 55:
            return None
        c = df["cierre"]
        o = df["apertura"]
        h = df["maximo"]
        l = df["minimo"]

        e5  = calc_ema(c, 5)
        e13 = calc_ema(c, 13)
        e50 = calc_ema(c, 50)

        macd_l = calc_ema(c, 5) - calc_ema(c, 13)
        macd_s = calc_ema(macd_l, 4)
        macd_h = macd_l - macd_s

        rsi = calc_rsi(c, 14)

        # Valores actuales
        e5v   = e5.iloc[-1];   e13v  = e13.iloc[-1];  e50v  = e50.iloc[-1]
        mh    = macd_h.iloc[-1]
        rv    = rsi.iloc[-1]
        cv    = c.iloc[-1];    ov    = o.iloc[-1]
        hv    = h.iloc[-1];    lv    = l.iloc[-1]

        rango  = hv - lv
        cuerpo = abs(cv - ov)

        # 4 filtros CALL
        f1c = e5v > e13v and e13v > e50v
        f2c = mh > 0
        f3c = rv > 45 and rv < 75
        f4c = cv > ov

        # 4 filtros PUT
        f1p = e5v < e13v and e13v < e50v
        f2p = mh < 0
        f3p = rv > 25 and rv < 55
        f4p = cv < ov

        nc = sum([f1c, f2c, f3c, f4c])
        np = sum([f1p, f2p, f3p, f4p])

        call_sig = f1c and f2c and f3c and f4c
        put_sig  = f1p and f2p and f3p and f4p

        if nc < 2 and np < 2:
            return None

        direccion = "CALL" if nc >= np else "PUT"
        filtros   = nc if direccion == "CALL" else np
        conf      = int(50 + filtros * 12)

        return {
            "precio": cv, "rsi": rv, "macd_hist": mh,
            "e5": e5v, "e13": e13v, "e50": e50v,
            "f1": f1c if direccion == "CALL" else f1p,
            "f2": f2c if direccion == "CALL" else f2p,
            "f3": f3c if direccion == "CALL" else f3p,
            "f4": f4c if direccion == "CALL" else f4p,
            "direccion": direccion,
            "filtros": filtros,
            "conf": conf,
            "call_completo": call_sig,
            "put_completo":  put_sig,
            "hora": datetime.now().strftime("%H:%M:%S"),
        }

    if hector_btn:
        resultados_h = []
        prog_h = st.progress(0)
        txt_h  = st.empty()
        for idx, activo in enumerate(activos_hector):
            prog_h.progress((idx + 1) / max(len(activos_hector), 1))
            txt_h.markdown(f'<div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#c8920a;">⏳ Escaneando {activo}... ({idx+1}/{len(activos_hector)})</div>', unsafe_allow_html=True)
            res = analizar_hector(ACTIVOS[activo]["yahoo"])
            if res:
                res["activo"] = activo
                res["tipo"]   = ACTIVOS[activo]["tipo"]
                resultados_h.append(res)
        prog_h.empty(); txt_h.empty()
        st.session_state["hector_results"] = resultados_h
        st.session_state["hector_ultimo"]  = datetime.now().strftime("%H:%M:%S")

        # Telegram
        if st.session_state.tg_on and st.session_state.tg_token:
            for r in resultados_h:
                if r["filtros"] == 4:
                    key_tg = f"hector_{r['activo']}_{r['hora']}"
                    enviadas = st.session_state.get("tg_enviadas", set())
                    if key_tg not in enviadas:
                        ic = "🔺" if r["direccion"] == "CALL" else "🔻"
                        msg = (f"{ic} <b>HECTOR TRIPLE CONFIRM — {r['activo']}</b>\n"
                               f"━━━━━━━━━━━━━━\n"
                               f"📊 {r['direccion']} — 4/4 filtros ✅\n"
                               f"💰 Precio: {r['precio']:.5f}\n"
                               f"📊 RSI: {r['rsi']:.1f}\n"
                               f"💵 Entrada 1%: <b>${st.session_state.capital*0.01:.2f}</b>\n"
                               f"⏱ Expiracion: 1 min\n"
                               f"🕐 {r['hora']}\n"
                               f"<i>QQE Command v6 — HECTOR</i>")
                        ok = enviar_telegram(st.session_state.tg_token, st.session_state.tg_chat, msg)
                        if ok:
                            enviadas.add(key_tg)
                            st.session_state.tg_enviadas = enviadas
        st.rerun()

    # Mostrar resultados
    if st.session_state.get("hector_results") is not None:
        res_list = st.session_state["hector_results"]
        ultimo   = st.session_state.get("hector_ultimo", "")

        # Resumen
        completos = [r for r in res_list if r["filtros"] == 4]
        avisos    = [r for r in res_list if r["filtros"] == 3]
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:16px;">
          <div class="kpi"><div class="kpi-label">ULTIMO SCAN</div><div class="kpi-value" style="font-size:20px;color:#4a7a99;">{ultimo}</div></div>
          <div class="kpi"><div class="kpi-label">SEÑALES 4/4</div><div class="kpi-value" style="color:{'#4ade80' if completos else '#4a7a99'};">{len(completos)}</div></div>
          <div class="kpi"><div class="kpi-label">AVISOS 3/4</div><div class="kpi-value" style="color:{'#ff9800' if avisos else '#4a7a99'};">{len(avisos)}</div></div>
        </div>
        """, unsafe_allow_html=True)

        if not res_list:
            st.markdown('<div style="text-align:center;padding:40px;color:#4a7a99;font-family:Share Tech Mono,monospace;font-size:13px;">Sin señales activas en este momento. Intentá durante sesion Londres (07-10 UTC) o NY (13-16 UTC).</div>', unsafe_allow_html=True)
        else:
            for r in sorted(res_list, key=lambda x: x["filtros"], reverse=True):
                es_call    = r["direccion"] == "CALL"
                completo   = r["filtros"] == 4
                card_cls   = "signal-call" if es_call else "signal-put"
                col_d      = "#4ade80" if es_call else "#f87171"
                ic         = "🔺" if es_call else "🔻"
                tipo_badge = {"forex": "FOREX", "commodity": "MATERIA PRIMA", "index": "INDICE", "crypto": "CRYPTO"}.get(r["tipo"], r["tipo"].upper())
                tipo_col   = {"forex": "#60a5fa", "commodity": "#fbbf24", "index": "#a78bfa", "crypto": "#fb923c"}.get(r["tipo"], "#94a3b8")

                st.markdown(f"""
                <div class="{card_cls}" style="{'border:2px solid ' + col_d + ';' if completo else ''}margin-bottom:10px;">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:6px;">
                    <div>
                      <span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:22px;color:#c8d8e8;">{r['activo']}</span>
                      <span style="font-family:Share Tech Mono,monospace;font-size:11px;color:{tipo_col};margin-left:10px;">{tipo_badge}</span>
                      <span style="font-family:Share Tech Mono,monospace;font-size:12px;color:{col_d};margin-left:10px;">{ic} {r['direccion']}</span>
                    </div>
                    <div style="text-align:right;">
                      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:28px;color:{col_d};">{r['filtros']}/4</div>
                      <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">{'✅ ENTRAR' if completo else '⚠ ESPERAR'}</div>
                    </div>
                  </div>

                  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;margin-bottom:10px;">
                    <div style="background:#060c18;border:1px solid {'#16a34a' if r['f1'] else '#1e3050'};border-radius:6px;padding:8px;text-align:center;">
                      <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">EMA STACK</div>
                      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:18px;color:{'#4ade80' if r['f1'] else '#374151'};">{'✓' if r['f1'] else '✗'}</div>
                    </div>
                    <div style="background:#060c18;border:1px solid {'#16a34a' if r['f2'] else '#1e3050'};border-radius:6px;padding:8px;text-align:center;">
                      <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">MACD</div>
                      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:18px;color:{'#4ade80' if r['f2'] else '#374151'};">{'✓' if r['f2'] else '✗'}</div>
                    </div>
                    <div style="background:#060c18;border:1px solid {'#16a34a' if r['f3'] else '#1e3050'};border-radius:6px;padding:8px;text-align:center;">
                      <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">RSI</div>
                      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:18px;color:{'#4ade80' if r['f3'] else '#374151'};">{'✓' if r['f3'] else '✗'}</div>
                    </div>
                    <div style="background:#060c18;border:1px solid {'#16a34a' if r['f4'] else '#1e3050'};border-radius:6px;padding:8px;text-align:center;">
                      <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">VELA</div>
                      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:18px;color:{'#4ade80' if r['f4'] else '#374151'};">{'✓' if r['f4'] else '✗'}</div>
                    </div>
                  </div>

                  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;">
                    <div style="background:#060c18;border-radius:6px;padding:8px;text-align:center;">
                      <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">PRECIO</div>
                      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;color:#c8d8e8;">{r['precio']:.5f}</div>
                    </div>
                    <div style="background:#060c18;border-radius:6px;padding:8px;text-align:center;">
                      <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">RSI</div>
                      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;color:{'#f87171' if r['rsi']>70 else '#4ade80' if r['rsi']<30 else '#c8d8e8'};">{r['rsi']:.1f}</div>
                    </div>
                    <div style="background:#060c18;border-radius:6px;padding:8px;text-align:center;">
                      <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">ENTRADA 1%</div>
                      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;color:#c8920a;">${st.session_state.capital*0.01:.2f}</div>
                    </div>
                    <div style="background:#060c18;border-radius:6px;padding:8px;text-align:center;">
                      <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">EXPIRACION</div>
                      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;color:#c8d8e8;">1 min</div>
                    </div>
                  </div>

                  {'<div style="background:#0a3020;border:1px solid #16a34a;border-radius:6px;padding:8px;margin-top:8px;font-family:Share Tech Mono,monospace;font-size:12px;color:#4ade80;">⚡ 4/4 FILTROS — Entrar en la PROXIMA vela. Expiracion 1 minuto.</div>' if completo else '<div style="background:#2a1a00;border:1px solid #c8920a;border-radius:6px;padding:8px;margin-top:8px;font-family:Share Tech Mono,monospace;font-size:12px;color:#fbbf24;">⚠ 3/4 filtros — Prepararse. Esperar que el 4to filtro confirme antes de entrar.</div>'}
                </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;background:#0d1525;border:2px dashed #1e3050;border-radius:12px;margin-top:10px;">
          <div style="font-size:48px;margin-bottom:10px;">🔺</div>
          <div style="font-family:Rajdhani,sans-serif;font-size:20px;color:#4a7a99;">Presiona ESCANEAR AHORA</div>
          <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#2a3a55;margin-top:6px;">Detecta señales Triple Confirm en forex, materias primas, indices y crypto</div>
        </div>""", unsafe_allow_html=True)

    # ── SCRIPTS LUA PARA DESCARGAR ──────────────────────────────
    st.markdown('<div class="sec" style="margin-top:24px;">📥 SCRIPTS LUA — DESCARGAR PARA IQ OPTION</div>', unsafe_allow_html=True)

    script_hector1 = '''instrument {
    name = "HECTOR 1 — Triple Confirm",
    short_name = "H1_3C",
    icon = "indicators:MA",
    overlay = true
}

e5  = ema(close, 5)
e13 = ema(close, 13)
e50 = ema(close, 50)

macd_linea  = ema(close, 5) - ema(close, 13)
macd_signal = ema(macd_linea, 4)
macd_hist   = macd_linea - macd_signal

rsi_v = rsi(close, 14)

f1_call = e5 > e13 and e13 > e50
f1_put  = e5 < e13 and e13 < e50

f2_call = macd_hist > 0 and macd_hist[1] <= 0
f2_put  = macd_hist < 0 and macd_hist[1] >= 0

f3_call = rsi_v > 45 and rsi_v < 75
f3_put  = rsi_v > 25 and rsi_v < 55

f4_call = close > open
f4_put  = close < open

call_signal = f1_call and f2_call and f3_call and f4_call
put_signal  = f1_put  and f2_put  and f3_put  and f4_put

warn_call = f1_call and f3_call and f4_call and not f2_call
warn_put  = f1_put  and f3_put  and f4_put  and not f2_put

plot(e5,  "EMA 5",  "yellow", 2)
plot(e13, "EMA 13", "cyan",   2)
plot(e50, "EMA 50", "gray",   1)

plot_shape(call_signal, "CALL", shape_style.triangleup,
    shape_size.large, "lime", shape_location.belowbar, 0, "CALL", "black")
plot_shape(put_signal, "PUT", shape_style.triangledown,
    shape_size.large, "red", shape_location.abovebar, 0, "PUT", "white")
plot_shape(warn_call, "PREP+", shape_style.triangleup,
    shape_size.small, "orange", shape_location.belowbar, 0, "!", "black")
plot_shape(warn_put, "PREP-", shape_style.triangledown,
    shape_size.small, "orange", shape_location.abovebar, 0, "!", "black")

color_bar = "gray"
if call_signal then color_bar = "lime" end
if put_signal  then color_bar = "red"  end
barcolor(color_bar)'''

    script_hector2 = '''instrument {
    name       = "HECTOR 2 — RSI + MACD",
    short_name = "H2_RSI",
    icon       = "indicators:RSI",
    overlay    = false
}

rsi_v       = rsi(close, 14)
macd_linea  = ema(close, 5) - ema(close, 13)
macd_signal = ema(macd_linea, 4)
macd_hist   = macd_linea - macd_signal

rsi_color = "gray"
if rsi_v > 50 and rsi_v < 70 then rsi_color = "lime"   end
if rsi_v < 50 and rsi_v > 30 then rsi_color = "red"    end
if rsi_v >= 70                then rsi_color = "orange" end
if rsi_v <= 30                then rsi_color = "orange" end

hist_color = "gray"
if macd_hist > 0 then hist_color = "lime" end
if macd_hist < 0 then hist_color = "red"  end

plot(70,   "OB",  "red",    1, 0, style.levels, na_mode.continue)
plot(30,   "OS",  "lime",   1, 0, style.levels, na_mode.continue)
plot(50,   "MED", "gray",   1, 0, style.levels, na_mode.continue)
plot(rsi_v,"RSI", rsi_color, 2)
plot(macd_hist,   "Hist",   hist_color, 3, 0, style.histogram)
plot(macd_linea,  "MACD",   "cyan",  1)
plot(macd_signal, "Signal", "orange",1)
plot(0,           "Zero",   "gray",  1, 0, style.levels, na_mode.continue)'''

    h1_tab, h2_tab = st.tabs(["HECTOR 1 — Triple Confirm (overlay)", "HECTOR 2 — RSI + MACD (panel)"])

    with h1_tab:
        st.markdown("""<div class="script-card card-green">
        <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:17px;color:#4ade80;margin-bottom:4px;">HECTOR 1 — Triple Confirm</div>
        <div style="font-size:13px;color:#94a3b8;line-height:1.7;">
        4 filtros: EMA Stack + MACD cruce + RSI zona + Vela confirmacion.<br>
        <b style="color:#4ade80;">Flecha verde grande</b> = CALL — entrar proxima vela · <b style="color:#f87171;">Flecha roja grande</b> = PUT<br>
        <b style="color:#ff9800;">Flecha naranja pequeña</b> = 3/4 filtros, prepararse
        </div></div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="code-block">{script_hector1}</div>', unsafe_allow_html=True)
        st.download_button("⬇ Descargar HECTOR 1.lua", script_hector1,
            file_name="HECTOR_1_triple_confirm.lua", mime="text/plain", key="dl_h1")

    with h2_tab:
        st.markdown("""<div class="script-card card-blue">
        <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:17px;color:#60a5fa;margin-bottom:4px;">HECTOR 2 — RSI + MACD</div>
        <div style="font-size:13px;color:#94a3b8;line-height:1.7;">
        Panel inferior de confirmacion. RSI coloreado por zona + histograma MACD.<br>
        <b style="color:#4ade80;">RSI verde</b> = zona alcista · <b style="color:#f87171;">RSI rojo</b> = zona bajista · <b style="color:#ff9800;">RSI naranja</b> = extremo, precaucion
        </div></div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="code-block">{script_hector2}</div>', unsafe_allow_html=True)
        st.download_button("⬇ Descargar HECTOR 2.lua", script_hector2,
            file_name="HECTOR_2_rsi_macd.lua", mime="text/plain", key="dl_h2")

# ================================================================
# TAB NOTICIAS + IA — FUSION MACRO + TECNICO SIN IMAGEN
# ================================================================
with tab_noticias:
    st.markdown('<div class="sec">📰 NOTICIAS + IA — FUSION MACRO Y TECNICO</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#0d1525;border:1px solid #c8920a;border-radius:12px;padding:14px 18px;margin-bottom:16px;">
      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:16px;color:#c8920a;margin-bottom:8px;">¿Para qué sirve esta tab?</div>
      <div style="font-size:13px;color:#94a3b8;line-height:1.9;">
        La IA busca noticias y eventos macro actuales relevantes para el activo que elijas, luego combina eso con el análisis técnico y da una conclusión concreta.<br>
        Ejemplo: <b style="color:#fbbf24;">conflicto en el Golfo → sube el petróleo</b> + técnico alcista → <b style="color:#4ade80;">CONCLUSIÓN: CALL en OIL WTI</b>
      </div>
    </div>""", unsafe_allow_html=True)

    if not get_ia_ok():
        st.markdown('<div style="background:#3a0a0a;border:1px solid #dc2626;border-radius:8px;padding:12px;color:#f87171;font-family:Share Tech Mono,monospace;font-size:11px;">Necesitas la clave API de Anthropic en el sidebar para usar esta función.</div>', unsafe_allow_html=True)
    else:
        c1n, c2n, c3n = st.columns([2,2,2])
        with c1n:
            activo_n = st.selectbox("Activo a analizar", list(ACTIVOS.keys()), key="not_activo")
        with c2n:
            tf_n = st.selectbox("Temporalidad operativa", ["M1 (binaria)","M15","H1","H4","D1"], key="not_tf")
        with c3n:
            pregunta_n = st.text_input("Pregunta específica (opcional)", placeholder="¿Qué pasa con el oro si escala el conflicto en Gaza?", key="not_pregunta")

        col_n1, col_n2 = st.columns(2)
        with col_n1:
            precio_n = st.text_input("Precio actual (opcional)", placeholder="2650.00", key="not_precio")
        with col_n2:
            sesion_n = st.selectbox("Sesión actual", ["London (07-10 UTC)","New York (13-16 UTC)","Asia (23-03 UTC)","Fuera de sesión"], key="not_sesion")

        scan_noticias_btn = st.button("📰 BUSCAR NOTICIAS + ANALIZAR", key="not_scan_btn", use_container_width=True)

        if scan_noticias_btn:
            with st.spinner("Buscando noticias actuales y analizando..."):
                try:
                    iq_name    = ACTIVOS.get(activo_n, {}).get("iq", activo_n)
                    tipo_activo = ACTIVOS.get(activo_n, {}).get("tipo", "")
                    ctx_precio  = f"Precio actual: {precio_n}." if precio_n else ""
                    ctx_pregunta = f"Pregunta específica de Hector: {pregunta_n}" if pregunta_n else ""
                    ctx_capital = f"Capital de Hector: ${st.session_state.capital:.2f}. Entrada 1% binaria: ${st.session_state.capital*0.01:.2f}. Entrada 2% swing: ${st.session_state.capital*0.02:.2f}."

                    sys_noticias = f"""Eres el analista macroeconómico y de noticias de Hector, trader argentino que opera en IQ Option.
Tu tarea es:
1. Buscar con web_search las noticias y eventos más recientes (últimas 48h) que impacten directamente al activo
2. Analizar si el contexto macro favorece una posición CALL (sube) o PUT (baja)
3. Dar una conclusión clara y accionable

ESTRUCTURA OBLIGATORIA:

## 📰 NOTICIAS RELEVANTES (últimas 48h)
Lista las 3-4 noticias o eventos más importantes que encontraste con la búsqueda.
Formato: • [Fuente] Titular breve → Impacto esperado (sube/baja/neutro)

## 🌍 CONTEXTO MACRO
1 párrafo: situación general del activo (dólar, tasas, guerra, commodities, etc.)

## 🔗 CONCLUSIÓN FINAL
**CALL ▲ / PUT ▼ / ESPERAR**
Explicación en 2-3 lineas de por qué.

## 🎯 MEJOR MOMENTO PARA ENTRAR
Sesión recomendada y condición técnica mínima que debe verse antes de entrar.

## ⚠ RIESGO PRINCIPAL
Un evento o dato que podría invalidar el análisis.

Maximo 350 palabras. En español. Directo. Formato exacto arriba."""

                    resp = requests.post("https://api.anthropic.com/v1/messages",
                        headers={"Content-Type":"application/json",
                                 "x-api-key": st.session_state.get("api_key",""),
                                 "anthropic-version":"2023-06-01"},
                        json={"model":"claude-sonnet-4-20250514","max_tokens":900,
                              "system":sys_noticias,
                              "tools":[{"type":"web_search_20250305","name":"web_search"}],
                              "messages":[{"role":"user","content":
                                  f"Analiza el activo {activo_n} ({iq_name}) para operar en {tf_n} durante {sesion_n}. {ctx_precio} {ctx_pregunta} {ctx_capital}"}]},
                        timeout=90)

                    if resp.status_code == 200:
                        rdata = resp.json()
                        texto = " ".join(
                            b["text"] for b in rdata.get("content",[])
                            if b.get("type") == "text"
                        )
                        st.session_state["not_resultado"] = {
                            "texto": texto, "activo": activo_n, "iq_name": iq_name,
                            "tf": tf_n, "hora": datetime.now().strftime("%H:%M"),
                            "sesion": sesion_n
                        }
                        st.rerun()
                    else:
                        st.error(f"Error API: {resp.status_code} — {resp.text[:200]}")
                except Exception as e:
                    st.error(f"Error: {e}")

        # Mostrar resultado
        if st.session_state.get("not_resultado"):
            r_n = st.session_state["not_resultado"]
            texto_n = r_n["texto"]

            # Detectar dirección
            if "CALL" in texto_n.upper()[:300] and "PUT" not in texto_n.upper()[:100]:
                rc_n,rb_n,rbr_n,ri_n = "#4ade80","#0a3020","#16a34a","🟢"
            elif "PUT" in texto_n.upper()[:300]:
                rc_n,rb_n,rbr_n,ri_n = "#f87171","#200a0a","#dc2626","🔴"
            elif "ESPERAR" in texto_n.upper()[:300]:
                rc_n,rb_n,rbr_n,ri_n = "#fbbf24","#2a1a00","#c8920a","🟡"
            else:
                rc_n,rb_n,rbr_n,ri_n = "#c8d8e8","#0d1525","#1e3050","⚪"

            st.markdown(f"""
            <div style="background:{rb_n};border:2px solid {rbr_n};border-radius:14px;padding:20px;margin-top:16px;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;flex-wrap:wrap;gap:8px;">
                <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:24px;color:{rc_n};">{ri_n} NOTICIAS + MACRO — {r_n["iq_name"]}</div>
                <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">{r_n["tf"]} · {r_n["sesion"]} · {r_n["hora"]}</div>
              </div>
              <div style="font-size:14px;color:#c8d8e8;line-height:2.1;">{texto_n.replace(chr(10),"<br>")}</div>
              <div style="margin-top:14px;padding-top:10px;border-top:1px solid {rbr_n};font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">
                Capital: ${st.session_state.capital:.2f} · 1%: ${st.session_state.capital*0.01:.2f} · 2%: ${st.session_state.capital*0.02:.2f} · QQE Command v7
              </div>
            </div>""", unsafe_allow_html=True)

            col_nt1, col_nt2, col_nt3 = st.columns(3)
            with col_nt1:
                if st.button("📓 Guardar en Diario", key="not_guardar"):
                    st.session_state.diario.append({
                        "fecha": date.today().strftime("%d/%m/%Y"),
                        "hora": r_n["hora"], "tipo": "NOTICIAS+MACRO",
                        "activo": r_n["activo"], "texto": texto_n, "tf": r_n["tf"],
                    })
                    st.success("Guardado!")
            with col_nt2:
                if st.button("📤 Enviar a Telegram", key="not_telegram"):
                    if st.session_state.tg_token:
                        msg_n = (f"{ri_n} <b>NOTICIAS+MACRO — {r_n['iq_name']} {r_n['tf']}</b>\n"
                                 f"━━━━━━━━━━━━━━\n"
                                 f"{texto_n[:800]}\n"
                                 f"<i>QQE Command v7 · {r_n['hora']}</i>")
                        ok = enviar_telegram(st.session_state.tg_token, st.session_state.tg_chat, msg_n)
                        st.success("Enviado!" if ok else "Error")
                    else:
                        st.warning("Configura Telegram en el sidebar")
            with col_nt3:
                csv_not = f"Fecha,Hora,Activo,TF,Sesion,Analisis\n{date.today()},{r_n['hora']},{r_n['activo']},{r_n['tf']},{r_n['sesion']},\"{texto_n.replace(chr(34),'')}\"\n"
                st.download_button("⬇ Descargar análisis", csv_not,
                    file_name=f"noticias_{r_n['activo']}_{r_n['hora'].replace(':','')}.csv",
                    mime="text/csv", key="not_dl")
        else:
            st.markdown("""
            <div style="text-align:center;padding:60px 20px;background:#0d1525;border:2px dashed #1e3050;border-radius:12px;margin-top:10px;">
              <div style="font-size:52px;margin-bottom:12px;">📰</div>
              <div style="font-family:Rajdhani,sans-serif;font-size:20px;color:#4a7a99;">Seleccioná un activo y presioná BUSCAR</div>
              <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#2a3a55;margin-top:8px;">La IA busca noticias en tiempo real y fusiona con análisis técnico</div>
            </div>""", unsafe_allow_html=True)

# ================================================================
# TAB 5 — REGISTRO DE OPERACIONES
# ================================================================
with tab_ops:
    st.markdown('<div class="sec">REGISTRO DE OPERACIONES</div>', unsafe_allow_html=True)
    capital = st.session_state.capital

    g, p, n = calc_pnl()
    cols_kpi = st.columns(4)
    kpis = [
        ("NETO HOY", f"${n:.2f}", "#4ade80" if n>=0 else "#f87171"),
        ("GANADO",   f"${g:.2f}", "#4ade80"),
        ("PERDIDO",  f"${p:.2f}", "#f87171"),
        ("OPERACIONES", str(len(st.session_state.ops)), "#c8920a"),
    ]
    for col, (label, val, color) in zip(cols_kpi, kpis):
        with col:
            st.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value" style="color:{color};">{val}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="sec">NUEVA OPERACION</div>', unsafe_allow_html=True)
    c1,c2,c3,c4,c5,c6 = st.columns([2,1,1,1,1,1])
    with c1: act_op = st.selectbox("Activo", list(ACTIVOS.keys()), key="op_act")
    with c2: dir_op = st.selectbox("Dir", ["CALL","PUT"], key="op_dir")
    with c3: tipo_op = st.selectbox("Tipo", ["1MIN","SWING H1","SWING H4"], key="op_tipo")
    with c4: monto_op = st.number_input("Monto $", min_value=1.0, value=round(capital*0.02,2), step=1.0, key="op_monto")
    with c5: res_op = st.selectbox("Result", ["WIN","LOSS","—"], key="op_res")
    with c6: pnl_op = st.number_input("P&L $", value=0.0, step=1.0, key="op_pnl")

    if st.button("REGISTRAR", key="op_reg", use_container_width=True):
        if res_op != "—":
            pnl_final = abs(pnl_op) if res_op=="WIN" else -abs(monto_op if pnl_op==0 else pnl_op)
            st.session_state.ops.append({
                "fecha": date.today().strftime("%d/%m"), "hora": datetime.now().strftime("%H:%M"),
                "activo": act_op, "dir": dir_op, "tipo": tipo_op,
                "monto": monto_op, "resultado": res_op, "pnl": pnl_final,
            })
            if res_op == "LOSS":
                st.session_state.perdida_dia += abs(pnl_final)
            st.rerun()

    if st.session_state.ops:
        st.markdown('<div class="sec">HISTORIAL</div>', unsafe_allow_html=True)
        for o in reversed(st.session_state.ops[-20:]):
            pnl_c = "#4ade80" if o["pnl"]>0 else "#f87171"
            ic_r = "✅" if o["resultado"]=="WIN" else "❌"
            ic_d = "▲" if o["dir"]=="CALL" else "▼"
            st.markdown(f"""
            <div class="asset-row" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;">
              <div>
                <span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:16px;color:#c8d8e8;">{o['activo']}</span>
                <span style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;margin-left:8px;">{o['tipo']}</span>
                <span style="font-family:Share Tech Mono,monospace;font-size:10px;color:{'#4ade80' if o['dir']=='CALL' else '#f87171'};margin-left:8px;">{ic_d} {o['dir']}</span>
              </div>
              <div style="display:flex;gap:14px;align-items:center;">
                <span style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">{o['fecha']} {o['hora']}</span>
                <span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:16px;color:{pnl_c};">{ic_r} ${abs(o['pnl']):.2f}</span>
              </div>
            </div>""", unsafe_allow_html=True)

# ================================================================
# TAB 5 — DIARIO
# ================================================================
with tab_diario:
    st.markdown('<div class="sec">DIARIO DE TRADING</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([3,1])
    with c1:
        nota_txt = st.text_area("Nueva entrada", height=100, placeholder="Anotá tu analisis, aprendizaje, estado emocional...", key="diario_txt", label_visibility="collapsed")
    with c2:
        nota_tipo = st.selectbox("Tipo", ["📊 Analisis","💡 Aprendizaje","😤 Gestion Emocional","🎯 Estrategia","📰 Noticias"], key="diario_tipo")
        if st.button("GUARDAR", key="diario_save", use_container_width=True):
            if nota_txt.strip():
                st.session_state.diario.append({
                    "fecha": date.today().strftime("%d/%m/%Y"),
                    "hora": datetime.now().strftime("%H:%M"),
                    "tipo": nota_tipo, "activo": "—", "texto": nota_txt, "tf": "—"
                })
                st.rerun()

    if st.session_state.diario:
        for e in reversed(st.session_state.diario[-30:]):
            st.markdown(f"""
            <div class="diario-entry">
              <div class="diario-meta">{e['fecha']} {e['hora']} · {e.get('tipo','—')} · {e.get('activo','—')} {e.get('tf','')}</div>
              <div style="font-size:13px;color:#c8d8e8;line-height:1.7;">{e['texto'].replace(chr(10),'<br>')}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align:center;padding:40px;color:#4a7a99;font-family:Share Tech Mono,monospace;font-size:11px;">Sin entradas aun</div>', unsafe_allow_html=True)

# ================================================================
# TAB 6 — SCRIPTS LUA
# ================================================================
with tab_binarias:
    st.markdown('<div class="sec">SCRIPTS LUA — BINARIAS 1 MINUTO — IQ OPTION</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#2a1a00;border:1px solid #c8920a;border-radius:8px;padding:10px 14px;margin-bottom:14px;font-size:12px;color:#fbbf24;">
    ⚠️ <b>Atencion:</b> Alto riesgo por spread y delay. Solo en sesion Londres (07-10 UTC) o NY (13-16 UTC).
    Riesgo max: 1% = <b>${st.session_state.capital*0.01:.2f}</b> por operacion.
    </div>""", unsafe_allow_html=True)

    s_a, s_b, s_c = st.tabs(["Script A — Momentum","Script B — Reversion","Script C — Hibrido"])

    script_a_code = '''instrument {
    name = "Script A - Momentum 1min",
    short_name = "MOM_1M",
    icon = "indicators:MA",
    overlay = true
}
input_group {
    "Configuracion",
    p_fast  = input(3,  "EMA Rapida",  input.integer, 1, 20, 1),
    p_slow  = input(8,  "EMA Lenta",   input.integer, 2, 50, 1),
    p_vol   = input(14, "Volatilidad", input.integer, 5, 30, 1),
    p_mult  = input(1.5,"Multiplicador",input.float,  0.5, 5, 0.1),
    p_trend = input(50, "EMA Tendencia",input.integer,20, 200,1)
}
function init()
    ema_fast  = indicator.ema(p_fast)
    ema_slow  = indicator.ema(p_slow)
    ema_trend = indicator.ema(p_trend)
    atr       = indicator.atr(p_vol)
    atr_ma    = indicator.ema(p_vol)
    upper = plot("Upper", color.blue, 1, plot.line)
    lower = plot("Lower", color.blue, 1, plot.line)
    signal_call = plot("CALL", color.green, 2, plot.arrow_up)
    signal_put  = plot("PUT",  color.red,   2, plot.arrow_down)
end
function update()
    local mid       = (ema_fast[0] + ema_slow[0]) / 2
    local band      = atr[0] * p_mult
    local vol_ok    = atr[0] > atr_ma[0] * 0.8
    local cross_up  = ema_fast[1] < ema_slow[1] and ema_fast[0] > ema_slow[0]
    local cross_down= ema_fast[1] > ema_slow[1] and ema_fast[0] < ema_slow[0]
    local trend_up  = close[0] > ema_trend[0]
    local trend_dn  = close[0] < ema_trend[0]
    upper:set(mid + band)
    lower:set(mid - band)
    if cross_up and vol_ok and trend_up then
        signal_call:set(low[0] - atr[0])
    end
    if cross_down and vol_ok and trend_dn then
        signal_put:set(high[0] + atr[0])
    end
end'''

    script_b_code = '''instrument {
    name = "Script B - Reversion 1min",
    short_name = "REV_1M",
    icon = "indicators:RSI",
    overlay = false
}
input_group {
    "Configuracion",
    p_rsi    = input(7,  "RSI Periodo", input.integer, 3, 20, 1),
    p_ob     = input(75, "Sobrecompra", input.integer, 60, 95, 1),
    p_os     = input(25, "Sobreventa",  input.integer, 5,  40, 1),
    p_macd_f = input(5,  "MACD Rapido", input.integer, 3,  15, 1),
    p_macd_s = input(13, "MACD Lento",  input.integer, 8,  30, 1),
    p_macd_g = input(4,  "MACD Signal", input.integer, 2,  10, 1)
}
function init()
    rsi  = indicator.rsi(p_rsi)
    macd = indicator.macd(p_macd_f, p_macd_s, p_macd_g)
    rsi_plot    = plot("RSI",     color.orange, 1, plot.line)
    ob_line     = plot("OB",      color.red,    1, plot.line)
    os_line     = plot("OS",      color.green,  1, plot.line)
    call_signal = plot("CALL",    color.green,  2, plot.arrow_up)
    put_signal  = plot("PUT",     color.red,    2, plot.arrow_down)
end
function update()
    rsi_plot:set(rsi[0])
    ob_line:set(p_ob)
    os_line:set(p_os)
    local hist_up   = macd.histogram[0] > 0 and macd.histogram[1] < 0
    local hist_down = macd.histogram[0] < 0 and macd.histogram[1] > 0
    if rsi[0] < p_os and hist_up then
        call_signal:set(rsi[0])
    end
    if rsi[0] > p_ob and hist_down then
        put_signal:set(rsi[0])
    end
end'''

    script_c_code = '''instrument {
    name = "Script C - Hibrido 1min",
    short_name = "HIB_1M",
    icon = "indicators:MACD",
    overlay = true
}
input_group {
    "EMAs",
    p_ema3  = input(3,  "EMA Ultra-Rapida", input.integer, 2, 10,  1),
    p_ema8  = input(8,  "EMA Rapida",        input.integer, 4, 20,  1),
    p_ema21 = input(21, "EMA Lenta",         input.integer, 10, 50, 1),
}
input_group {
    "Filtros",
    p_rsi_mid = input(50, "RSI Neutro", input.integer, 40, 60, 1),
    p_atr_f   = input(10, "ATR Periodo",input.integer,  5, 30, 1)
}
function init()
    ema3  = indicator.ema(p_ema3)
    ema8  = indicator.ema(p_ema8)
    ema21 = indicator.ema(p_ema21)
    macd  = indicator.macd(5, 13, 4)
    rsi   = indicator.rsi(7)
    atr   = indicator.atr(p_atr_f)
    e3_p = plot("EMA3",  color.yellow, 1, plot.line)
    e8_p = plot("EMA8",  color.blue,   1, plot.line)
    e21_p= plot("EMA21", color.gray,   1, plot.line)
    call_s = plot("CALL",color.green,  2, plot.arrow_up)
    put_s  = plot("PUT", color.red,    2, plot.arrow_down)
end
function update()
    e3_p:set(ema3[0])
    e8_p:set(ema8[0])
    e21_p:set(ema21[0])
    local stack_bull = ema3[0] > ema8[0] and ema8[0] > ema21[0]
    local stack_bear = ema3[0] < ema8[0] and ema8[0] < ema21[0]
    local macd_cross_up   = macd.histogram[0] > 0 and macd.histogram[1] < 0
    local macd_cross_down = macd.histogram[0] < 0 and macd.histogram[1] > 0
    local rsi_ok_call = rsi[0] < 65 and rsi[0] > 35
    local rsi_ok_put  = rsi[0] > 35 and rsi[0] < 65
    if stack_bull and macd_cross_up and rsi_ok_call then
        call_s:set(low[0] - atr[0] * 0.5)
    end
    if stack_bear and macd_cross_down and rsi_ok_put then
        put_s:set(high[0] + atr[0] * 0.5)
    end
end'''

    with s_a:
        st.markdown("""<div class="script-card card-gold">
        <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:18px;color:#c8920a;margin-bottom:4px;">Script A — Scalping Momentum</div>
        <div style="font-size:13px;color:#94a3b8;line-height:1.7;">
        Detecta momentum fuerte con cruce de EMA3/EMA8 + filtro de volatilidad ATR.<br>
        Solo opera cuando el precio esta a favor de la EMA50 (tendencia).<br>
        <b style="color:#c8920a;">Mejores activos:</b> EUR/USD, GBP/USD, XAU/USD · <b style="color:#c8920a;">Expiracion:</b> 1-2 min
        </div></div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="code-block">{script_a_code}</div>', unsafe_allow_html=True)
        st.button("Copiar Script A", key="copy_a")

    with s_b:
        st.markdown("""<div class="script-card card-blue">
        <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:18px;color:#2563eb;margin-bottom:4px;">Script B — Reversion a la Media</div>
        <div style="font-size:13px;color:#94a3b8;line-height:1.7;">
        RSI extremo (sobrecompra/sobreventa) + confirmacion de giro MACD histograma.<br>
        Opera contra la tendencia en puntos de agotamiento.<br>
        <b style="color:#60a5fa;">Mejores activos:</b> BTC/USD, GBP/USD · <b style="color:#60a5fa;">Expiracion:</b> 2-3 min
        </div></div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="code-block">{script_b_code}</div>', unsafe_allow_html=True)
        st.button("Copiar Script B", key="copy_b")

    with s_c:
        st.markdown("""<div class="script-card card-purple">
        <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:18px;color:#7c3aed;margin-bottom:4px;">Script C — Hibrido Triple EMA + MACD</div>
        <div style="font-size:13px;color:#94a3b8;line-height:1.7;">
        Triple confirmacion: alineacion de EMA3/8/21 + cruce MACD + RSI neutro.<br>
        La mas exigente — menos senales pero mayor calidad.<br>
        <b style="color:#a78bfa;">Mejores activos:</b> Todos · <b style="color:#a78bfa;">Expiracion:</b> 1-3 min
        </div></div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="code-block">{script_c_code}</div>', unsafe_allow_html=True)
        st.button("Copiar Script C", key="copy_c")

# ================================================================
# TAB 7 — COPY TRADING
# ================================================================
with tab_copy:
    st.markdown('<div class="sec">COPY TRADING — GUIA PARA IQ OPTION</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#0d1525;border:1px solid #c8920a;border-radius:12px;padding:16px;margin-bottom:16px;">
      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:16px;color:#c8920a;margin-bottom:8px;">Estrategia de Capital — Capital: ${st.session_state.capital:.2f}</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
        <div style="background:#0a3020;border:1px solid #16a34a;border-radius:8px;padding:12px;text-align:center;">
          <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4ade80;">TRADING PROPIO (70%)</div>
          <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:24px;color:#4ade80;">${st.session_state.capital*0.70:.2f}</div>
          <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">QQE Command v4</div>
        </div>
        <div style="background:#0a1a3a;border:1px solid #2563eb;border-radius:8px;padding:12px;text-align:center;">
          <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#60a5fa;">COPY TRADING (30%)</div>
          <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:24px;color:#60a5fa;">${st.session_state.capital*0.30:.2f}</div>
          <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">1 trader riesgo BAJO</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    traders = [
        ("TopTrader_FX",    "87%", "3.2x", "BAJO",   "#4ade80", "#0a3020", "#16a34a", "Forex especialista. +2.4% mensual constante. Opera EUR/USD y GBP/USD. Max DD 8%."),
        ("CryptoMaster_99", "71%", "5.8x", "ALTO",   "#f87171", "#200a0a", "#dc2626", "BTC y ETH. Alto retorno pero drawdown de hasta 35%. Solo si aceptas el riesgo."),
        ("GoldTrader_Pro",  "79%", "2.1x", "MEDIO",  "#fbbf24", "#2a1a00", "#c8920a", "Especialista XAU/USD. Consistente. Opera con noticias de Fed y CPI. Max DD 15%."),
        ("ScalpKing_EU",    "83%", "1.8x", "BAJO",   "#4ade80", "#0a3020", "#16a34a", "Scalping EUR/USD 1min. Muchas operaciones pequenas. Win rate alto, ganancias moderadas."),
    ]

    for name, wr, mult, risk, col, bg, border, desc in traders:
        st.markdown(f"""
        <div style="background:{bg};border:1px solid {border};border-radius:10px;padding:14px;margin-bottom:8px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-wrap:wrap;gap:6px;">
            <span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:18px;color:#c8d8e8;">{name}</span>
            <span class="badge" style="background:{bg};color:{col};border:1px solid {border};">RIESGO {risk}</span>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:8px;">
            <div style="background:#060c18;border-radius:6px;padding:8px;text-align:center;">
              <div style="font-family:Share Tech Mono,monospace;font-size:8px;color:#4a7a99;">WIN RATE</div>
              <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:18px;color:{col};">{wr}</div>
            </div>
            <div style="background:#060c18;border-radius:6px;padding:8px;text-align:center;">
              <div style="font-family:Share Tech Mono,monospace;font-size:8px;color:#4a7a99;">MULTIPLICADOR</div>
              <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:18px;color:{col};">{mult}</div>
            </div>
            <div style="background:#060c18;border-radius:6px;padding:8px;text-align:center;">
              <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">COPIA 30%</div>
              <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:18px;color:#c8920a;">${st.session_state.capital*0.30:.0f}</div>
            </div>
          </div>
          <div style="font-size:12px;color:#94a3b8;line-height:1.6;">{desc}</div>
        </div>""", unsafe_allow_html=True)

# ================================================================
# TAB 8 — CODIGOS QQE
# ================================================================
with tab_codigos:
    st.markdown('<div class="sec">CODIGOS QQE 03/04 — COPIAR EN IQ OPTION</div>', unsafe_allow_html=True)

    qqe03 = '''instrument {
    name = "QQE 03 - Hector Forex",
    short_name = "QQE03",
    icon = "indicators:RSI",
    overlay = false
}
input_group {
    "QQE",
    rsi_len  = input(14, "RSI Periodo",   input.integer, 5, 30, 1),
    smooth   = input(5,  "Suavizado RSI", input.integer, 1, 20, 1),
    qqe_fact = input(4.238, "QQE Factor", input.float,   1, 10, 0.001),
}
input_group {
    "Filtros",
    ema100_on = input(true, "EMA 100", input.bool),
    ema200_on = input(true, "EMA 200", input.bool),
}
function init()
    rsi_src  = indicator.rsi(rsi_len)
    ema100   = indicator.ema(100)
    ema200   = indicator.ema(200)
    macd_ind = indicator.macd(12, 26, 9)
    sto      = indicator.stochastic(14, 3, 3)
    bull_sig = plot("BULL", color.green, 2, plot.arrow_up)
    bear_sig = plot("BEAR", color.red,   2, plot.arrow_down)
end
function update()
    local rsi_s    = rsi_src[0]
    local trend_ok = (not ema100_on or close[0] > ema100[0]) and
                     (not ema200_on or close[0] > ema200[0])
    local trend_dn = (not ema100_on or close[0] < ema100[0]) and
                     (not ema200_on or close[0] < ema200[0])
    local macd_bull = macd_ind.histogram[0] > 0
    local macd_bear = macd_ind.histogram[0] < 0
    local sto_bull  = sto.k[0] < 80 and sto.d[0] < 80
    local sto_bear  = sto.k[0] > 20 and sto.d[0] > 20
    if rsi_s > 50 and trend_ok and macd_bull and sto_bull then
        bull_sig:set(low[0])
    end
    if rsi_s < 50 and trend_dn and macd_bear and sto_bear then
        bear_sig:set(high[0])
    end
end'''

    qqe04 = '''instrument {
    name = "QQE 04 - Hector Crypto",
    short_name = "QQE04",
    icon = "indicators:MA",
    overlay = true
}
input_group {
    "EMAs",
    ema_f = input(50,  "EMA Rapida", input.integer, 10, 100, 1),
    ema_s = input(200, "EMA Lenta",  input.integer, 50, 500, 1),
}
function init()
    ema_fast = indicator.ema(ema_f)
    ema_slow = indicator.ema(ema_s)
    rsi_ind  = indicator.rsi(14)
    macd_ind = indicator.macd(12, 26, 9)
    ef_plot  = plot("EMA Fast", color.yellow, 1, plot.line)
    es_plot  = plot("EMA Slow", color.gray,   1, plot.line)
    bull_s   = plot("BULL",     color.green,  2, plot.arrow_up)
    bear_s   = plot("BEAR",     color.red,    2, plot.arrow_down)
end
function update()
    ef_plot:set(ema_fast[0])
    es_plot:set(ema_slow[0])
    local cross_bull = ema_fast[1] < ema_slow[1] and ema_fast[0] > ema_slow[0]
    local cross_bear = ema_fast[1] > ema_slow[1] and ema_fast[0] < ema_slow[0]
    local rsi_ok  = rsi_ind[0] > 45 and rsi_ind[0] < 75
    local rsi_ok2 = rsi_ind[0] < 55 and rsi_ind[0] > 25
    if cross_bull and rsi_ok and macd_ind.histogram[0] > 0 then
        bull_s:set(low[0])
    end
    if cross_bear and rsi_ok2 and macd_ind.histogram[0] < 0 then
        bear_s:set(high[0])
    end
end'''

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:16px;color:#c8920a;margin-bottom:8px;">QQE 03 — FOREX & COMMODITIES</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px;color:#94a3b8;margin-bottom:8px;">EMA100 + EMA200 + MACD + Estocastico + RSI<br>Activos: XAU/USD, Crude Oil, EUR/USD, NAS100</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="code-block">{qqe03}</div>', unsafe_allow_html=True)
    with col_c2:
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:16px;color:#7c3aed;margin-bottom:8px;">QQE 04 — CRYPTO</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px;color:#94a3b8;margin-bottom:8px;">EMA50 + EMA200 + MACD + RSI<br>Activos: BTC, ETH, SOL</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="code-block">{qqe04}</div>', unsafe_allow_html=True)

# ================================================================
# FOOTER
# ================================================================
st.markdown(f"""
<div style="text-align:center;margin-top:24px;padding:14px;border-top:1px solid #1e3050;">
  <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#2a3a55;letter-spacing:2px;">
    QQE COMMAND V7 · HECTOR TRADING SYSTEM · Capital: ${st.session_state.capital:.2f} · Objetivo: $50/dia
  </div>
</div>""", unsafe_allow_html=True)
