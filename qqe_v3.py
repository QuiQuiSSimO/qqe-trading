# QQE COMMAND V4 — HECTOR TRADING SYSTEM
# Binarias 1min + Swing Trading H1/H4 + Scanner en Vivo + IA Grafico
#
# INSTALACION: pip install streamlit requests yfinance pandas numpy streamlit-autorefresh
# EJECUCION:   streamlit run qqe_v4.py

import streamlit as st
import requests
import base64
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timezone, date, timedelta

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
    page_title="QQE Command v4 — Hector",
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
.stApp { font-family:'Inter',sans-serif; color:#c8d8e8; }
[data-testid="stSidebar"] { background:#0d1525 !important; border-right:1px solid #1e3050 !important; }

.stTabs [data-baseweb="tab-list"] { background:#0d1525; border-bottom:2px solid #1e3050; gap:0; }
.stTabs [data-baseweb="tab"] {
    background:transparent; color:#4a7a99 !important;
    font-family:'Share Tech Mono',monospace; font-size:10px;
    letter-spacing:1px; padding:10px 14px; border:none;
}
.stTabs [aria-selected="true"] {
    background:#0a0f1a !important; color:#c8920a !important;
    border-bottom:2px solid #c8920a !important; font-weight:700 !important;
}

.card { background:#0d1525; border:1px solid #1e3050; border-radius:10px; padding:16px; margin-bottom:10px; }
.card-gold   { border-left:4px solid #c8920a; }
.card-green  { border-left:4px solid #16a34a; }
.card-red    { border-left:4px solid #dc2626; }
.card-blue   { border-left:4px solid #2563eb; }
.card-purple { border-left:4px solid #7c3aed; }

.kpi { background:#0d1525; border:1px solid #1e3050; border-radius:10px; padding:14px 16px; text-align:center; }
.kpi-label { font-family:'Share Tech Mono',monospace; font-size:9px; color:#4a7a99; letter-spacing:2px; margin-bottom:6px; }
.kpi-value { font-family:'Rajdhani',sans-serif; font-size:30px; font-weight:700; line-height:1.1; }
.kpi-sub   { font-family:'Share Tech Mono',monospace; font-size:10px; color:#4a7a99; margin-top:3px; }

.sec { font-family:'Share Tech Mono',monospace; font-size:10px; color:#4a7a99; letter-spacing:3px;
       text-transform:uppercase; border-bottom:2px solid #1e3050; padding-bottom:6px; margin:16px 0 12px; }

.signal-call { background:linear-gradient(135deg,#0a2010,#0d3520); border:1px solid #16a34a;
               border-radius:10px; padding:14px; margin-bottom:8px; }
.signal-put  { background:linear-gradient(135deg,#200a0a,#350d0d); border:1px solid #dc2626;
               border-radius:10px; padding:14px; margin-bottom:8px; }
.signal-wait { background:#0d1525; border:1px solid #1e3050; border-radius:10px; padding:14px; margin-bottom:8px; }

.badge { padding:3px 10px; border-radius:20px; font-family:'Share Tech Mono',monospace; font-size:9px; font-weight:700; }
.badge-green  { background:#0a3020; color:#4ade80; border:1px solid #16a34a; }
.badge-red    { background:#3a0a0a; color:#f87171; border:1px solid #dc2626; }
.badge-gold   { background:#2a1a00; color:#fbbf24; border:1px solid #c8920a; }
.badge-blue   { background:#0a1a3a; color:#60a5fa; border:1px solid #2563eb; }
.badge-gray   { background:#1a2535; color:#94a3b8; border:1px solid #2a3a55; }

.ia-box { background:#0d1525; border:1px solid #c8920a; border-radius:10px; padding:16px;
          font-size:13px; line-height:1.8; color:#c8d8e8; }

.asset-row { background:#0d1525; border:1px solid #1e3050; border-radius:8px; padding:12px; margin-bottom:6px; }

.scan-dot { display:inline-block; width:8px; height:8px; border-radius:50%; animation:pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:.4;} }

.prog-track { height:6px; background:#1e3050; border-radius:3px; overflow:hidden; margin:4px 0; }
.prog-fill  { height:100%; border-radius:3px; }

.diario-entry { background:#0d1525; border:1px solid #1e3050; border-radius:8px; padding:14px; margin-bottom:8px; }
.diario-meta  { font-family:'Share Tech Mono',monospace; font-size:9px; color:#4a7a99; letter-spacing:1px; margin-bottom:6px; }

.script-card { background:#0d1525; border:1px solid #1e3050; border-radius:8px; padding:16px; margin-bottom:10px; }
.code-block { background:#060c18; border:1px solid #1e3050; border-radius:6px; padding:14px;
              font-family:'Share Tech Mono',monospace; font-size:10px; line-height:1.8; color:#7dd3fc;
              white-space:pre; overflow-x:auto; max-height:280px; overflow-y:auto; margin-bottom:8px; }

.swing-result { border-radius:12px; padding:18px; margin-top:10px; }

/* Mobile */
@media (max-width:768px) {
    .stTabs [data-baseweb="tab"] { font-size:9px; padding:8px 8px; letter-spacing:0; }
    .stButton>button { min-height:48px !important; font-size:12px !important; }
    .kpi-value { font-size:22px; }
}

.stButton>button {
    background:#1e3050 !important; color:#c8d8e8 !important;
    border:1px solid #2a4570 !important; border-radius:8px !important;
    font-family:'Share Tech Mono',monospace !important; font-size:11px !important; letter-spacing:1px !important;
    transition:all .2s;
}
.stButton>button:hover { background:#c8920a !important; color:#000 !important; border-color:#c8920a !important; }

.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    background:#0d1525 !important; border:1px solid #1e3050 !important;
    color:#c8d8e8 !important; border-radius:8px !important;
}
.stSelectbox>div>div, .stNumberInput>div>div>input {
    background:#0d1525 !important; border:1px solid #1e3050 !important; color:#c8d8e8 !important; border-radius:8px !important;
}
[data-testid="stSlider"] { color:#c8920a; }
::-webkit-scrollbar { width:4px; height:4px; }
::-webkit-scrollbar-track { background:#0a0f1a; }
::-webkit-scrollbar-thumb { background:#1e3050; border-radius:2px; }
</style>
""", unsafe_allow_html=True)

# ================================================================
# SECRETS / SESSION STATE
# ================================================================
def cargar_secrets():
    try:
        if "anthropic_api_key" in st.secrets:
            st.session_state.api_key = st.secrets["anthropic_api_key"]
    except: pass
    try:
        if "telegram_token" in st.secrets:
            st.session_state.tg_token = st.secrets["telegram_token"]
    except: pass
    try:
        if "telegram_chat_id" in st.secrets:
            st.session_state.tg_chat = str(st.secrets["telegram_chat_id"])
    except: pass
    try:
        if "capital_dia" in st.secrets:
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
    "XAU/USD":   {"yahoo": "GC=F",      "tipo": "commodity"},
    "EUR/USD":   {"yahoo": "EURUSD=X",  "tipo": "forex"},
    "GBP/USD":   {"yahoo": "GBPUSD=X",  "tipo": "forex"},
    "NAS100":    {"yahoo": "NQ=F",      "tipo": "index"},
    "BTC/USD":   {"yahoo": "BTC-USD",   "tipo": "crypto"},
    "CRUDE OIL": {"yahoo": "CL=F",      "tipo": "commodity"},
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

def analizar_activo_swing(symbol, tf="1h"):
    """Analiza activo para swing trading H1/H4"""
    interval = "1h" if tf == "H1" else "4h" if tf == "H4" else "1d"
    period   = "30d" if tf in ("H1","H4") else "90d"
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
    st.markdown('<div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:20px;color:#c8920a;letter-spacing:2px;margin-bottom:16px;">QQE CMD v4</div>', unsafe_allow_html=True)

    # API
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;letter-spacing:2px;margin-bottom:4px;">CLAVE API ANTHROPIC</div>', unsafe_allow_html=True)
    api_in = st.text_input("API", value=st.session_state.api_key, type="password", label_visibility="collapsed", key="api_sb")
    if api_in: st.session_state.api_key = api_in
    ia_status = "IA ACTIVA ✓" if get_ia_ok() else "Sin clave API"
    ia_col = "#4ade80" if get_ia_ok() else "#f87171"
    st.markdown(f'<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:{ia_col};margin-bottom:12px;">{ia_status}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Capital
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;letter-spacing:2px;margin-bottom:4px;">CAPITAL Y RIESGO</div>', unsafe_allow_html=True)
    cap = st.number_input("Capital", min_value=10.0, max_value=100000.0, value=float(st.session_state.capital), step=10.0, label_visibility="collapsed", key="cap_sb")
    st.session_state.capital = cap
    sl_pct = st.slider("Stop Loss diario %", 5, 30, int(st.session_state.stop_loss_dia), 1, key="sl_sb")
    st.session_state.stop_loss_dia = sl_pct
    sl_monto = cap * sl_pct / 100
    perdida  = st.session_state.perdida_dia
    pct_used = min(100, int(perdida / sl_monto * 100)) if sl_monto > 0 else 0
    bar_col  = "#4ade80" if pct_used < 50 else ("#fbbf24" if pct_used < 80 else "#f87171")
    st.markdown(f"""
    <div style="background:#0d1525;border:1px solid #1e3050;border-radius:8px;padding:10px;margin-bottom:8px;">
      <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
        <span style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">ENTRADA 1%</span>
        <span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;color:#4ade80;">${cap*0.01:.2f}</span>
      </div>
      <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
        <span style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">ENTRADA 2%</span>
        <span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;color:#c8920a;">${cap*0.02:.2f}</span>
      </div>
      <div class="prog-track"><div class="prog-fill" style="width:{pct_used}%;background:{bar_col};"></div></div>
      <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:{bar_col};margin-top:3px;">Perdida: ${perdida:.2f} / SL: ${sl_monto:.2f}</div>
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
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;letter-spacing:2px;margin-bottom:4px;">TELEGRAM</div>', unsafe_allow_html=True)
    tg_chk = st.checkbox("Alertas activas", value=st.session_state.tg_on, key="tg_chk_sb")
    st.session_state.tg_on = tg_chk
    if tg_chk:
        tg_tok = st.text_input("Token", value=st.session_state.tg_token, type="password", placeholder="Token bot...", label_visibility="collapsed", key="tg_tok_sb")
        tg_cid = st.text_input("Chat ID", value=st.session_state.tg_chat, placeholder="Chat ID...", label_visibility="collapsed", key="tg_cid_sb")
        if tg_tok: st.session_state.tg_token = tg_tok
        if tg_cid: st.session_state.tg_chat  = tg_cid
        tg_ok = bool(st.session_state.tg_token and st.session_state.tg_chat)
        col_tg = "#4ade80" if tg_ok else "#f87171"
        st.markdown(f'<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:{col_tg};margin-bottom:6px;">{"CONECTADO ✓" if tg_ok else "Completa token y chat ID"}</div>', unsafe_allow_html=True)
        if tg_ok and st.button("Enviar prueba", key="tg_prueba"):
            ok = enviar_telegram(st.session_state.tg_token, st.session_state.tg_chat,
                "✅ <b>QQE Command v4</b> conectado!\n\nRecibirás alertas de binarias 1min y swing trading.")
            if ok: st.success("✅ Enviado!")
            else: st.error("Error al enviar")

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
tab_scan1, tab_swing, tab_swing_ia, tab_ops, tab_diario, tab_binarias, tab_copy, tab_codigos = st.tabs([
    "⚡ SCANNER 1MIN", "📈 SWING SCANNER", "🖼 SWING IA GRAFICO",
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
# TAB 2 — SWING SCANNER
# ================================================================
with tab_swing:
    st.markdown('<div class="sec">SWING TRADING SCANNER — H1 / H4</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2,2,2])
    with c1:
        swing_btn = st.button("📈 ESCANEAR SWING", key="swing_scan_btn", use_container_width=True)
    with c2:
        tf_sel = st.selectbox("Temporalidad", ["H1","H4","D1"], key="swing_tf")
    with c3:
        activos_swing = st.multiselect("Activos", list(ACTIVOS.keys()), default=list(ACTIVOS.keys()), key="act_swing", label_visibility="collapsed")

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
                        msg = (f"{ic} <b>SWING {tf_sel} — {activo}</b>\n"
                               f"━━━━━━━━━━━━━━\n"
                               f"📊 {r['direccion']} — {r['tendencia']}\n"
                               f"🎯 Score: {r['score']}%\n"
                               f"💰 Precio: {r['precio']:.4f}\n"
                               f"🛑 Stop Loss: {r['sl']:.4f}\n"
                               f"🎯 Take Profit: {r['tp']:.4f}\n"
                               f"📊 RSI: {r['rsi']:.1f}\n"
                               f"💵 Capital 2%: <b>${st.session_state.capital*0.02:.2f}</b>\n"
                               f"<i>QQE Command v4 · {tf_sel}</i>")
                        ok = enviar_telegram(st.session_state.tg_token, st.session_state.tg_chat, msg)
                        if ok:
                            enviadas.add(key_sw)
                            st.session_state.tg_enviadas = enviadas
        st.rerun()

    # Mostrar swing
    if hasattr(st.session_state, "swing_resultados") and st.session_state.swing_resultados:
        res_list = sorted(st.session_state.swing_resultados.values(), key=lambda x: x["score"], reverse=True)
        for r in res_list:
            es_long = "LONG" in r["direccion"]
            es_short = "SHORT" in r["direccion"]
            card_cls = "signal-call" if es_long else "signal-put" if es_short else "signal-wait"
            ic = "▲" if es_long else "▼" if es_short else "—"
            col_dir = "#4ade80" if es_long else "#f87171" if es_short else "#c8920a"
            score = r["score"]

            st.markdown(f"""
            <div class="{card_cls}">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-wrap:wrap;gap:6px;">
                <div>
                  <span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:20px;color:#c8d8e8;">{r['activo']}</span>
                  <span style="margin-left:8px;" class="badge {'badge-green' if es_long else 'badge-red' if es_short else 'badge-gold'}">{ic} {r['direccion']}</span>
                  <span style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;margin-left:8px;">{r['tf']}</span>
                </div>
                <div style="text-align:right;">
                  <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:22px;color:{col_dir};">{score}%</div>
                  <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">SCORE</div>
                </div>
              </div>
              <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:8px;">
                <div style="background:#060c18;border-radius:6px;padding:10px;text-align:center;">
                  <div style="font-family:Share Tech Mono,monospace;font-size:8px;color:#4a7a99;">PRECIO</div>
                  <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;color:#c8d8e8;">{r['precio']:.4f}</div>
                </div>
                <div style="background:#3a0a0a;border:1px solid #dc2626;border-radius:6px;padding:10px;text-align:center;">
                  <div style="font-family:Share Tech Mono,monospace;font-size:8px;color:#f87171;">STOP LOSS</div>
                  <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;color:#f87171;">{r['sl']:.4f}</div>
                </div>
                <div style="background:#0a3020;border:1px solid #16a34a;border-radius:6px;padding:10px;text-align:center;">
                  <div style="font-family:Share Tech Mono,monospace;font-size:8px;color:#4ade80;">TAKE PROFIT</div>
                  <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;color:#4ade80;">{r['tp']:.4f}</div>
                </div>
              </div>
              <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:6px;">
                <div style="text-align:center;"><span style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">RSI: </span><span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:13px;color:#c8d8e8;">{r['rsi']:.1f}</span></div>
                <div style="text-align:center;"><span style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">EMA20: </span><span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:13px;color:#c8d8e8;">{r['ema20']:.4f}</span></div>
                <div style="text-align:center;"><span style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">ATR: </span><span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:13px;color:#c8d8e8;">{r['atr']:.4f}</span></div>
              </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;background:#0d1525;border:2px dashed #1e3050;border-radius:12px;margin-top:10px;">
          <div style="font-size:48px;margin-bottom:10px;">📈</div>
          <div style="font-family:Rajdhani,sans-serif;font-size:20px;color:#4a7a99;">Presiona ESCANEAR SWING</div>
          <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#2a3a55;margin-top:6px;">Analiza H1/H4 con SL y TP calculados por ATR</div>
        </div>""", unsafe_allow_html=True)

# ================================================================
# TAB 3 — SWING IA GRAFICO
# ================================================================
with tab_swing_ia:
    st.markdown('<div class="sec">ANALIZADOR IA — CAPTURA DE GRAFICO IQ OPTION</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#0d1525;border:1px solid #c8920a;border-radius:12px;padding:14px 18px;margin-bottom:16px;">
      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:16px;color:#c8920a;margin-bottom:8px;">Como usar</div>
      <div style="font-size:13px;color:#94a3b8;line-height:1.9;">
        1. Abrí IQ Option → seleccioná el activo → temporalidad H1 o H4<br>
        2. Sacá captura de pantalla del grafico (iPhone: lateral + subir volumen)<br>
        3. Completá los datos del trade abajo<br>
        4. Subí la imagen → la IA analiza y te dice la probabilidad, SL y TP recomendados
      </div>
    </div>""", unsafe_allow_html=True)

    if not get_ia_ok():
        st.markdown('<div style="background:#3a0a0a;border:1px solid #dc2626;border-radius:8px;padding:12px;color:#f87171;font-family:Share Tech Mono,monospace;font-size:11px;">Necesitas la clave API de Anthropic en el sidebar para usar el analizador.</div>', unsafe_allow_html=True)
    else:
        # FORMULARIO DE CONTEXTO
        st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;letter-spacing:2px;margin-bottom:8px;">DATOS DEL TRADE</div>', unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            activo_ia = st.selectbox("Activo", list(ACTIVOS.keys()) + ["Otro"], key="ia_activo")
        with col_b:
            tf_ia = st.selectbox("Temporalidad", ["H1 (1 hora)","H4 (4 horas)","D1 (diario)"], key="ia_tf")
        with col_c:
            dir_ia = st.selectbox("Direccion que analizas", ["Sin preferencia","CALL / LONG (sube)","PUT / SHORT (baja)"], key="ia_dir")

        col_d, col_e = st.columns(2)
        with col_d:
            precio_ia = st.text_input("Precio actual (opcional)", placeholder="1.0842", key="ia_precio")
        with col_e:
            notas_ia = st.text_input("Notas adicionales (opcional)", placeholder="Rompio resistencia, noticias hoy...", key="ia_notas")

        st.markdown("---")

        # MULTIPLES IMAGENES
        st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;letter-spacing:2px;margin-bottom:8px;">CAPTURA DEL GRAFICO — podes subir hasta 3 imagenes (H1 + H4 + M15)</div>', unsafe_allow_html=True)

        imgs = st.file_uploader("", type=["png","jpg","jpeg","webp"], accept_multiple_files=True, key="ia_imgs", label_visibility="collapsed")

        if imgs:
            # Preview
            cols_prev = st.columns(min(len(imgs), 3))
            for i, img in enumerate(imgs[:3]):
                with cols_prev[i]:
                    st.image(img, use_column_width=True)
                    st.markdown(f'<div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;text-align:center;">{img.name}</div>', unsafe_allow_html=True)

            st.markdown("---")

            if st.button("🧠 ANALIZAR CON IA — SWING TRADING", key="ia_analizar_swing", use_container_width=True):
                with st.spinner("La IA está analizando el grafico..."):
                    try:
                        # Construir contenido con todas las imagenes
                        content = []
                        for img in imgs[:3]:
                            ext = img.name.split(".")[-1].lower()
                            mtype = "image/jpeg" if ext in ("jpg","jpeg") else f"image/{ext}"
                            b64 = base64.b64encode(img.read()).decode()
                            content.append({"type":"image","source":{"type":"base64","media_type":mtype,"data":b64}})

                        # Contexto adicional
                        ctx_dir = dir_ia if dir_ia != "Sin preferencia" else "sin direccion previa"
                        ctx_precio = f"Precio actual: {precio_ia}." if precio_ia else ""
                        ctx_notas = f"Contexto adicional: {notas_ia}." if notas_ia else ""
                        ctx_capital = f"Capital de Hector: ${st.session_state.capital:.2f}. Entrada 2%: ${st.session_state.capital*0.02:.2f}."

                        content.append({"type":"text","text":f"""Analiza este grafico de {activo_ia} en {tf_ia}.
El trader considera: {ctx_dir}. {ctx_precio} {ctx_notas} {ctx_capital}

Dame un analisis COMPLETO de swing trading."""})

                        sys_swing = f"""Eres el analista de swing trading personal de Hector. Opera en IQ Option con opciones H1 y H4.
Tu objetivo: analizar el grafico y dar una recomendacion CLARA y ACCIONABLE.

ESTRUCTURA OBLIGATORIA de tu respuesta:
1. DECISION: ENTRAR CALL / ENTRAR PUT / ESPERAR (en grande)
2. PROBABILIDAD DE EXITO: X% (estimacion honesta)
3. POR QUE: 2-3 lineas del razonamiento tecnico
4. STOP LOSS recomendado: precio exacto o distancia en pips/puntos
5. TAKE PROFIT: precio exacto o distancia (minimo ratio 1:2)
6. TIEMPO ESTIMADO: cuanto puede tardar el movimiento
7. QUE INVALIDARIA la señal: una linea

Maximo 200 palabras. En espanol. Directo. Sin rodeos.
Si el grafico no es claro o hay riesgo alto, decilo sin dudar."""

                        resp = requests.post("https://api.anthropic.com/v1/messages",
                            headers={"Content-Type":"application/json",
                                     "x-api-key": st.session_state.get("api_key",""),
                                     "anthropic-version":"2023-06-01"},
                            json={"model":"claude-sonnet-4-20250514","max_tokens":600,
                                  "system":sys_swing,
                                  "messages":[{"role":"user","content":content}]},
                            timeout=60)

                        if resp.status_code == 200:
                            texto = resp.json()["content"][0]["text"]
                            st.session_state[f"swing_ia_resp_{activo_ia}"] = {
                                "texto": texto, "hora": datetime.now().strftime("%H:%M"),
                                "activo": activo_ia, "tf": tf_ia
                            }
                            st.rerun()
                        else:
                            st.error(f"Error API: {resp.status_code} — {resp.text[:200]}")
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.markdown("""
            <div style="text-align:center;padding:50px 20px;background:#0d1525;border:2px dashed #1e3050;border-radius:12px;margin-top:10px;">
              <div style="font-size:52px;margin-bottom:12px;">📱</div>
              <div style="font-family:Rajdhani,sans-serif;font-size:20px;color:#4a7a99;">Subi la captura de IQ Option</div>
              <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#2a3a55;margin-top:8px;">Podes subir hasta 3 graficos — H1 + H4 + M15</div>
            </div>""", unsafe_allow_html=True)

        # Mostrar resultado IA
        resp_key = f"swing_ia_resp_{activo_ia if 'activo_ia' in dir() else 'XAU/USD'}"
        if resp_key in st.session_state and st.session_state[resp_key]:
            res_ia = st.session_state[resp_key]
            texto = res_ia["texto"]

            # Color segun decision
            if "ENTRAR CALL" in texto.upper() or "CALL" in texto.upper()[:50]:
                rc,rb,rbr,ri = "#4ade80","#0a3020","#16a34a","🟢"
            elif "ENTRAR PUT" in texto.upper() or "PUT" in texto.upper()[:50]:
                rc,rb,rbr,ri = "#f87171","#200a0a","#dc2626","🔴"
            elif "ESPERAR" in texto.upper()[:80]:
                rc,rb,rbr,ri = "#fbbf24","#2a1a00","#c8920a","🟡"
            else:
                rc,rb,rbr,ri = "#c8d8e8","#0d1525","#1e3050","⚪"

            st.markdown(f"""
            <div style="background:{rb};border:2px solid {rbr};border-radius:14px;padding:20px;margin-top:16px;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:24px;color:{rc};">{ri} ANALISIS IA — {res_ia['activo']}</div>
                <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">{res_ia['tf']} · {res_ia['hora']}</div>
              </div>
              <div style="font-size:14px;color:#c8d8e8;line-height:2.0;">{texto.replace(chr(10),"<br>")}</div>
              <div style="margin-top:12px;padding-top:10px;border-top:1px solid {rbr};font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">
                Capital: ${st.session_state.capital:.2f} · Entrada 2%: ${st.session_state.capital*0.02:.2f} · QQE Command v4
              </div>
            </div>""", unsafe_allow_html=True)

            # Guardar en diario
            if st.button("📓 Guardar en Diario", key="guardar_diario_ia"):
                st.session_state.diario.append({
                    "fecha": date.today().strftime("%d/%m/%Y"),
                    "hora": res_ia["hora"],
                    "tipo": "ANALISIS IA",
                    "activo": res_ia["activo"],
                    "texto": texto,
                    "tf": res_ia["tf"],
                })
                st.success("Guardado en el diario!")

# ================================================================
# TAB 4 — REGISTRO DE OPERACIONES
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
  <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#2a3a55;letter-spacing:2px;">
    QQE COMMAND V4 · HECTOR TRADING SYSTEM · Capital: ${st.session_state.capital:.2f} · Objetivo: $50/dia
  </div>
</div>""", unsafe_allow_html=True)
