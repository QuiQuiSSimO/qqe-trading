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
# Zona horaria Argentina = UTC-3 (no cambia con horario de verano)
TZ_ARG = timezone(timedelta(hours=-3))

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
    page_title="QQE Command v10 — Hector",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================================================================
# CSS
# ================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700;900&family=Share+Tech+Mono&family=Exo+2:wght@300;400;700;900&display=swap');

/* ── BASE ── */
html, body, .stApp { background:#050a14 !important; }
.stApp { font-family:'Exo 2',sans-serif; color:#c8d8e8; font-size:15px; }
[data-testid="stSidebar"] { background:#080e1c !important; border-right:1px solid #1a2a45 !important; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background:linear-gradient(90deg,#050a14,#0a1020,#050a14);
    border-bottom:2px solid #1a2a45; gap:0; flex-wrap:nowrap; overflow-x:auto;
}
.stTabs [data-baseweb="tab"] {
    background:transparent; color:#4a7a99 !important;
    font-family:'Share Tech Mono',monospace; font-size:11px;
    letter-spacing:1px; padding:13px 14px; border:none; white-space:nowrap;
    transition: all 0.25s;
}
.stTabs [aria-selected="true"] {
    background:linear-gradient(180deg,#0d1e3a,#050a14) !important;
    color:#f0b429 !important;
    border-bottom:3px solid #f0b429 !important; font-weight:700 !important;
    text-shadow: 0 0 12px rgba(240,180,41,0.5);
}

/* ── CARDS ── */
.card { background:#0a1020; border:1px solid #1a2a45; border-radius:12px; padding:18px; margin-bottom:10px; }
.card-gold   { border-left:4px solid #f0b429; background:linear-gradient(135deg,#150e00,#0a1020); }
.card-green  { border-left:4px solid #22c55e; background:linear-gradient(135deg,#001508,#0a1020); }
.card-red    { border-left:4px solid #ef4444; background:linear-gradient(135deg,#150000,#0a1020); }
.card-blue   { border-left:4px solid #3b82f6; background:linear-gradient(135deg,#000d20,#0a1020); }
.card-purple { border-left:4px solid #a855f7; background:linear-gradient(135deg,#0d0020,#0a1020); }

/* ── KPIs ── */
.kpi { background:linear-gradient(135deg,#0a1020,#0d1830); border:1px solid #1a2a45;
       border-radius:12px; padding:16px 18px; text-align:center;
       transition: transform 0.2s, border-color 0.2s; }
.kpi:hover { transform:translateY(-2px); border-color:#f0b429; }
.kpi-label { font-family:'Share Tech Mono',monospace; font-size:10px; color:#4a7a99; letter-spacing:2px; margin-bottom:6px; }
.kpi-value { font-family:'Rajdhani',sans-serif; font-size:36px; font-weight:700; line-height:1.1; }
.kpi-sub   { font-family:'Share Tech Mono',monospace; font-size:11px; color:#4a7a99; margin-top:3px; }

/* ── SECCIÓN HEADER ── */
.sec { font-family:'Share Tech Mono',monospace; font-size:11px; color:#f0b429; letter-spacing:4px;
       text-transform:uppercase; border-bottom:1px solid #1a2a45; padding-bottom:8px; margin:18px 0 14px;
       display:flex; align-items:center; gap:8px; }
.sec::before { content:''; display:inline-block; width:3px; height:14px;
               background:linear-gradient(#f0b429,#c8920a); border-radius:2px; }

/* ── SIGNALS ── */
.signal-call {
    background:linear-gradient(135deg,#001a08,#002010,#001508);
    border:1px solid #22c55e; border-radius:12px; padding:18px; margin-bottom:12px;
    box-shadow: 0 0 20px rgba(34,197,94,0.15), inset 0 1px 0 rgba(34,197,94,0.1);
    animation: glow-call 3s ease-in-out infinite;
}
.signal-put {
    background:linear-gradient(135deg,#1a0000,#200000,#150000);
    border:1px solid #ef4444; border-radius:12px; padding:18px; margin-bottom:12px;
    box-shadow: 0 0 20px rgba(239,68,68,0.15), inset 0 1px 0 rgba(239,68,68,0.1);
    animation: glow-put 3s ease-in-out infinite;
}
.signal-wait { background:#0a1020; border:1px solid #1a2a45; border-radius:12px; padding:16px; margin-bottom:10px; }

@keyframes glow-call {
    0%,100% { box-shadow: 0 0 15px rgba(34,197,94,0.1); }
    50%      { box-shadow: 0 0 35px rgba(34,197,94,0.35), 0 0 60px rgba(34,197,94,0.1); }
}
@keyframes glow-put {
    0%,100% { box-shadow: 0 0 15px rgba(239,68,68,0.1); }
    50%      { box-shadow: 0 0 35px rgba(239,68,68,0.35), 0 0 60px rgba(239,68,68,0.1); }
}

/* ── ENTRADA RÁPIDA BUTTON ── */
.btn-entrada {
    display:inline-block; background:linear-gradient(135deg,#22c55e,#16a34a);
    color:#000 !important; font-family:'Rajdhani',sans-serif; font-weight:900;
    font-size:15px; letter-spacing:2px; padding:12px 24px; border-radius:10px;
    border:none; cursor:pointer; width:100%; text-align:center;
    box-shadow: 0 4px 20px rgba(34,197,94,0.4);
    animation: pulse-btn 2s infinite;
}
.btn-entrada-put {
    background:linear-gradient(135deg,#ef4444,#dc2626) !important;
    box-shadow: 0 4px 20px rgba(239,68,68,0.4) !important;
}
@keyframes pulse-btn {
    0%,100% { transform:scale(1); }
    50%      { transform:scale(1.02); }
}

/* ── PANEL SESIÓN STICKY ── */
.sesion-bar {
    position:sticky; top:0; z-index:999;
    background:rgba(5,10,20,0.95); backdrop-filter:blur(12px);
    border-bottom:1px solid #1a2a45; padding:8px 16px;
    display:flex; align-items:center; justify-content:space-between;
    flex-wrap:wrap; gap:8px; margin-bottom:16px;
    border-radius:0 0 10px 10px;
}

/* ── BADGES ── */
.badge { padding:4px 12px; border-radius:20px; font-family:'Share Tech Mono',monospace; font-size:11px; font-weight:700; }
.badge-green  { background:rgba(34,197,94,0.15); color:#4ade80; border:1px solid #22c55e; }
.badge-red    { background:rgba(239,68,68,0.15); color:#f87171; border:1px solid #ef4444; }
.badge-gold   { background:rgba(240,180,41,0.15); color:#fbbf24; border:1px solid #f0b429; }
.badge-blue   { background:rgba(59,130,246,0.15); color:#60a5fa; border:1px solid #3b82f6; }
.badge-purple { background:rgba(168,85,247,0.15); color:#c084fc; border:1px solid #a855f7; }
.badge-gray   { background:#1a2535; color:#94a3b8; border:1px solid #2a3a55; }

/* ── MISCELÁNEOS ── */
.ia-box { background:#0a1020; border:1px solid #f0b429; border-radius:12px; padding:18px;
          font-size:15px; line-height:1.9; color:#c8d8e8; }
.asset-row { background:#0a1020; border:1px solid #1a2a45; border-radius:10px; padding:14px; margin-bottom:8px;
             transition: border-color 0.2s; }
.asset-row:hover { border-color:#f0b429; }
.scan-dot { display:inline-block; width:9px; height:9px; border-radius:50%; animation:blink 1.5s infinite; }
@keyframes blink { 0%,100%{opacity:1; transform:scale(1);} 50%{opacity:.3; transform:scale(0.7);} }
.prog-track { height:8px; background:#1a2a45; border-radius:4px; overflow:hidden; margin:4px 0; }
.prog-fill  { height:100%; border-radius:4px; transition: width 0.8s ease; }
.diario-entry { background:#0a1020; border:1px solid #1a2a45; border-radius:10px; padding:16px; margin-bottom:8px; }
.diario-meta  { font-family:'Share Tech Mono',monospace; font-size:11px; color:#4a7a99; letter-spacing:1px; margin-bottom:6px; }
.script-card { background:#0a1020; border:1px solid #1a2a45; border-radius:10px; padding:18px; margin-bottom:12px; }
.code-block { background:#030710; border:1px solid #1a2a45; border-radius:8px; padding:16px;
              font-family:'Share Tech Mono',monospace; font-size:11px; line-height:1.9; color:#7dd3fc;
              white-space:pre; overflow-x:auto; max-height:300px; overflow-y:auto; margin-bottom:10px; }
.strat-box { background:#0a1020; border:1px solid #f0b429; border-radius:14px; padding:18px; margin-bottom:12px; }
.strat-step { background:#030710; border-left:3px solid #f0b429; padding:12px 16px; margin-bottom:8px;
              border-radius:0 10px 10px 0; font-size:14px; line-height:1.8; }
.strat-regla { background:rgba(34,197,94,0.05); border:1px solid #22c55e; border-radius:10px;
               padding:12px 16px; margin-bottom:8px; font-size:14px; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width:4px; height:4px; }
::-webkit-scrollbar-track { background:#050a14; }
::-webkit-scrollbar-thumb { background:linear-gradient(#f0b429,#c8920a); border-radius:2px; }

/* ── BOTONES STREAMLIT ── */
.stButton>button {
    background:linear-gradient(135deg,#0d1830,#1a2a45) !important;
    color:#c8d8e8 !important; border:1px solid #2a4060 !important;
    border-radius:10px !important; font-family:'Share Tech Mono',monospace !important;
    font-size:12px !important; letter-spacing:1px !important;
    transition:all .25s; min-height:44px !important;
}
.stButton>button:hover {
    background:linear-gradient(135deg,#f0b429,#c8920a) !important;
    color:#000 !important; border-color:#f0b429 !important;
    box-shadow: 0 4px 16px rgba(240,180,41,0.4) !important;
    transform: translateY(-1px);
}
.stButton>button:active { transform: translateY(0); }

/* ── INPUTS ── */
.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    background:#0a1020 !important; border:1px solid #1a2a45 !important;
    color:#c8d8e8 !important; border-radius:10px !important; font-size:14px !important;
}
.stSelectbox>div>div, .stNumberInput>div>div>input {
    background:#0a1020 !important; border:1px solid #1a2a45 !important;
    color:#c8d8e8 !important; border-radius:10px !important; font-size:14px !important;
}
[data-testid="stSlider"] .stSlider { accent-color:#f0b429; }

/* ── MOBILE / iPHONE ── */
@media (max-width:768px) {
    .stApp { font-size:14px !important; }
    .stTabs [data-baseweb="tab"] { font-size:10px !important; padding:10px 8px !important; letter-spacing:0 !important; }
    .stTabs [data-baseweb="tab-list"] { overflow-x:auto !important; -webkit-overflow-scrolling:touch; }
    .stButton>button { min-height:52px !important; font-size:14px !important; border-radius:12px !important; }
    .kpi-value { font-size:26px !important; }
    .kpi { padding:12px !important; }
    .signal-call, .signal-put { padding:14px !important; }
    h1,h2,h3 { font-size:1.1em !important; }
    /* Hacer grids de 1 columna en mobile */
    [style*="grid-template-columns: repeat(4"] { grid-template-columns: 1fr 1fr !important; }
    [style*="grid-template-columns: repeat(5"] { grid-template-columns: 1fr 1fr !important; }
    [style*="grid-template-columns:1fr 1fr 1fr 1fr"] { grid-template-columns: 1fr 1fr !important; }
}
@media (max-width:480px) {
    .stTabs [data-baseweb="tab"] { font-size:9px !important; padding:9px 6px !important; }
    .btn-entrada { font-size:16px !important; padding:16px !important; min-height:56px; }
}

/* ── LABELS ── */
label, .stSelectbox label, .stTextInput label, .stNumberInput label {
    font-size:12px !important; color:#7a9ab8 !important; letter-spacing:1px;
}
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
    "racha_losses": 0,        # pérdidas consecutivas
    "max_racha_dia": 0,       # máxima racha del día
    "autorefresh_on": False,
    "hector_results": None,
    "hector_ultimo": "",
    "triple_results": None,
    "triple_ultimo": "",
    "noticias_analisis": None,
    "noticias_activo_sel": "",
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

def get_hora_arg():
    """Hora local Argentina (UTC-3)"""
    return datetime.now(TZ_ARG)

def get_hora_arg_str():
    return datetime.now(TZ_ARG).strftime("%H:%M")

def get_fecha_arg():
    return datetime.now(TZ_ARG).date()

def get_session_info():
    h = get_utc_hour()
    if 7 <= h < 10:    return "SESION LONDRES",   "OPERAR",    "#16a34a", "#0a3020", "#4ade80"
    elif 13 <= h < 16: return "SESION NUEVA YORK","OPERAR",    "#16a34a", "#0a3020", "#4ade80"
    elif 11 <= h < 13: return "SOLAPAMIENTO",     "ACTIVO",    "#c8920a", "#2a1a00", "#fbbf24"
    elif 10 <= h < 11: return "CIERRE LONDRES",   "PRECAUCION","#c8920a", "#2a1a00", "#fbbf24"
    else:               return "MERCADO CERRADO",  "INACTIVO",  "#64748b", "#1a2535", "#94a3b8"

def es_horario_operable():
    """True solo en ventanas de alta probabilidad de profit"""
    h = get_utc_hour()
    return (7 <= h < 10) or (13 <= h < 16)

def es_horario_aceptable():
    """True incluye solapamiento"""
    h = get_utc_hour()
    return (7 <= h < 16)

def _build_filtros_html(r):
    """5 filtros grandes — sin f-strings anidados."""
    labels = ["EMA 5/13/50", "MACD HIST", "RSI ZONA", "VELA", "VOLUMEN"]
    parts = []
    for i, lbl in enumerate(labels):
        ok     = r.get(f"f{i+1}", False)
        bc     = "#16a34a" if ok else "#dc2626"
        col    = "#4ade80" if ok else "#dc2626"
        sym    = "✓" if ok else "✗"
        parts.append(
            f'<div style="background:#060c18;border:1px solid {bc};border-radius:8px;'
            f'padding:10px;text-align:center;">'
            f'<div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">{lbl}</div>'
            f'<div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:20px;color:{col};">{sym}</div>'
            f'</div>'
        )
    return "".join(parts)

def _build_filtros_mini(r):
    """4 filtros compactos para avisos."""
    parts = []
    for j in range(4):
        ok  = r.get(f"f{j+1}", False)
        bc  = "#16a34a" if ok else "#374151"
        col = "#4ade80" if ok else "#64748b"
        sym = "✓" if ok else "✗"
        parts.append(
            f'<div style="background:#060c18;border:1px solid {bc};border-radius:4px;'
            f'padding:5px;text-align:center;font-family:Rajdhani,sans-serif;'
            f'font-weight:700;font-size:14px;color:{col};">{sym}</div>'
        )
    return "".join(parts)

def _play_audio(sound_type, audio_on):
    """Reproduce audio via components_v1.html — unico metodo que ejecuta JS en Streamlit."""
    if not COMPONENTS_OK or not audio_on or sound_type == "none":
        return
    ao = "true" if audio_on else "false"
    html_audio = f"""<script>
(function() {{
  var _on = {ao};
  var _t  = "{sound_type}";
  if (!_on || !_t || _t === 'none') return;
  try {{
    var ctx = new (window.AudioContext || window.webkitAudioContext)();
    if (ctx.state === 'suspended') ctx.resume();
    var now = ctx.currentTime;
    function nota(f, w, d, tp, v) {{
      var o = ctx.createOscillator(), g = ctx.createGain();
      o.connect(g); g.connect(ctx.destination);
      o.type = tp || 'sine'; o.frequency.setValueAtTime(f, now+w);
      g.gain.setValueAtTime(v||0.3, now+w);
      g.gain.exponentialRampToValueAtTime(0.001, now+w+d);
      o.start(now+w); o.stop(now+w+d+0.05);
    }}
    if (_t==='signal_call')  {{ nota(440,.00,.12,'sine',.35); nota(554,.13,.12,'sine',.35); nota(659,.26,.20,'sine',.40); nota(880,.48,.18,'sine',.25); }}
    else if (_t==='signal_put')   {{ nota(659,.00,.12,'sine',.35); nota(554,.13,.12,'sine',.35); nota(440,.26,.20,'sine',.40); nota(330,.48,.18,'sine',.25); }}
    else if (_t==='signal')       {{ nota(880,.00,.10,'sine',.30); nota(1047,.12,.15,'sine',.30); }}
    else if (_t==='loss_warning') {{ nota(200,.00,.18,'square',.28); nota(150,.20,.18,'square',.28); nota(200,.40,.18,'square',.28); }}
    else if (_t==='session_open') {{ nota(523,.00,.10,'triangle',.30); nota(659,.12,.10,'triangle',.30); nota(784,.24,.10,'triangle',.30); nota(1047,.36,.22,'triangle',.35); }}
    else if (_t==='stop_hit')     {{ nota(300,.00,.10,'sawtooth',.38); nota(150,.12,.10,'sawtooth',.38); nota(300,.25,.10,'sawtooth',.38); nota(150,.37,.10,'sawtooth',.38); nota(100,.50,.30,'sawtooth',.30); }}
    else {{ nota(880,.00,.12,'sine',.28); }}
  }} catch(e) {{ console.warn('QQE audio:', e); }}
}})();
</script>"""
    components_v1.html(html_audio, height=0, scrolling=False)

@st.cache_data(ttl=300)
def get_tendencia_h1(symbol):
    """Devuelve tendencia en H1 para confirmar señales 1min (confluencia)"""
    try:
        df = yf.download(symbol, period="5d", interval="1h", progress=False, auto_adjust=True)
        if df.empty or len(df) < 20: return "LATERAL"
        df.columns = [c[0].lower() if isinstance(c, tuple) else c.lower() for c in df.columns]
        c = df["close"].dropna()
        e20 = c.ewm(span=20, adjust=False).mean()
        e50 = c.ewm(span=50, adjust=False).mean()
        precio = c.iloc[-1]
        if precio > e20.iloc[-1] > e50.iloc[-1]: return "ALCISTA"
        if precio < e20.iloc[-1] < e50.iloc[-1]: return "BAJISTA"
        return "LATERAL"
    except: return "LATERAL"

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
    # FOREX
    "EUR/USD":    {"yahoo": "EURUSD=X",  "tipo": "forex",     "iqopt": "EUR/USD"},
    "GBP/USD":    {"yahoo": "GBPUSD=X",  "tipo": "forex",     "iqopt": "GBP/USD"},
    "USD/JPY":    {"yahoo": "JPY=X",     "tipo": "forex",     "iqopt": "USD/JPY"},
    "AUD/USD":    {"yahoo": "AUDUSD=X",  "tipo": "forex",     "iqopt": "AUD/USD"},
    "USD/CAD":    {"yahoo": "CAD=X",     "tipo": "forex",     "iqopt": "USD/CAD"},
    "EUR/GBP":    {"yahoo": "EURGBP=X",  "tipo": "forex",     "iqopt": "EUR/GBP"},
    # MATERIAS PRIMAS
    "XAU/USD":    {"yahoo": "GC=F",      "tipo": "commodity", "iqopt": "Gold"},
    "XAG/USD":    {"yahoo": "SI=F",      "tipo": "commodity", "iqopt": "Silver"},
    "WTI":        {"yahoo": "CL=F",      "tipo": "commodity", "iqopt": "WTI Crude Oil"},
    "BRENT":      {"yahoo": "BZ=F",      "tipo": "commodity", "iqopt": "Brent Crude Oil"},
    "NAT GAS":    {"yahoo": "NG=F",      "tipo": "commodity", "iqopt": "Natural Gas"},
    "COPPER":     {"yahoo": "HG=F",      "tipo": "commodity", "iqopt": "Copper"},
    # INDICES
    "US 100":     {"yahoo": "NQ=F",      "tipo": "index",     "iqopt": "US 100"},
    "US 500":     {"yahoo": "ES=F",      "tipo": "index",     "iqopt": "US 500"},
    "US 30":      {"yahoo": "YM=F",      "tipo": "index",     "iqopt": "US 30"},
    "GER 40":     {"yahoo": "^GDAXI",    "tipo": "index",     "iqopt": "GER 40"},
    # CRYPTO
    "BTC/USD":    {"yahoo": "BTC-USD",   "tipo": "crypto",    "iqopt": "Bitcoin"},
    "ETH/USD":    {"yahoo": "ETH-USD",   "tipo": "crypto",    "iqopt": "Ethereum"},
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

# ================================================================
# QQE ENGINE — MOTOR DE SEÑALES (integrado v11)
# ================================================================
def calc_qqe_engine(df_raw, rsi_period=14, sf=5, qqe_factor=4.238, thresh=3.0):
    """
    QQE real sobre el dataframe del v10 (columnas en español).
    Devuelve df con columnas: rsi_smooth, trend, signal, signal_quality
    """
    close = df_raw["cierre"].copy()
    # RSI
    delta = close.diff()
    g = delta.clip(lower=0).ewm(span=rsi_period, adjust=False).mean()
    l = (-delta.clip(upper=0)).ewm(span=rsi_period, adjust=False).mean()
    rsi = 100 - 100 / (1 + g / l.replace(0, 1e-10))
    # Suavizado
    rsi_smooth = rsi.ewm(span=sf, adjust=False).mean()
    # ATR del RSI suavizado (Wilders)
    delta_rsi = rsi_smooth.diff().abs()
    atr_rsi   = delta_rsi.ewm(alpha=1/(rsi_period*2-1), adjust=False).mean()
    dar        = atr_rsi.ewm(alpha=1/(rsi_period*2-1), adjust=False).mean() * qqe_factor
    # Bandas dinámicas
    rs_arr = rsi_smooth.values
    d_arr  = dar.values
    lb_arr = np.full(len(df_raw), np.nan)
    sb_arr = np.full(len(df_raw), np.nan)
    tr_arr = np.zeros(len(df_raw))
    for i in range(1, len(df_raw)):
        if np.isnan(rs_arr[i]) or np.isnan(d_arr[i]):
            lb_arr[i] = lb_arr[i-1] if not np.isnan(lb_arr[i-1]) else 0
            sb_arr[i] = sb_arr[i-1] if not np.isnan(sb_arr[i-1]) else 100
            tr_arr[i] = tr_arr[i-1]; continue
        nlb = rs_arr[i] - d_arr[i]
        nsb = rs_arr[i] + d_arr[i]
        plb = lb_arr[i-1] if not np.isnan(lb_arr[i-1]) else nlb
        psb = sb_arr[i-1] if not np.isnan(sb_arr[i-1]) else nsb
        lb_arr[i] = max(nlb, plb) if rs_arr[i-1] > plb else nlb
        sb_arr[i] = min(nsb, psb) if rs_arr[i-1] < psb else nsb
        if tr_arr[i-1] == 1:
            tr_arr[i] = -1 if rs_arr[i] < lb_arr[i] else 1
        else:
            tr_arr[i] =  1 if rs_arr[i] > sb_arr[i] else -1
    result = df_raw.copy()
    result["rsi_q"]      = rsi.values
    result["rsi_smooth"] = rs_arr
    result["dar"]        = d_arr
    result["trend_q"]    = tr_arr
    result["signal"]     = "WAIT"
    buy_m  = (result["trend_q"] ==  1) & (result["trend_q"].shift(1) == -1)
    sell_m = (result["trend_q"] == -1) & (result["trend_q"].shift(1) ==  1)
    result.loc[buy_m,  "signal"] = "BUY"
    result.loc[sell_m, "signal"] = "SELL"
    result["signal_quality"] = "NORMAL"
    result.loc[(result["signal"]=="BUY")  & (result["rsi_smooth"] < 50+thresh), "signal_quality"] = "ALTA"
    result.loc[(result["signal"]=="SELL") & (result["rsi_smooth"] > 50-thresh), "signal_quality"] = "ALTA"
    return result

def run_backtest_v11(df_qqe, capital=500.0, riesgo_pct=1.0):
    """Backtest sobre señales QQE. Entrada en cierre señal, salida en siguiente cierre."""
    monto  = capital * riesgo_pct / 100
    trades = []
    sig_idx = df_qqe.index[df_qqe["signal"].isin(["BUY","SELL"])].tolist()
    for i, idx in enumerate(sig_idx):
        pos   = df_qqe.index.get_loc(idx)
        if pos + 1 >= len(df_qqe): continue
        entry = float(df_qqe["cierre"].iloc[pos])
        exit_ = float(df_qqe["cierre"].iloc[pos + 1])
        row   = df_qqe.loc[idx]
        if row["signal"] == "BUY":
            pnl = (exit_ - entry) / entry
        else:
            pnl = (entry - exit_) / entry
        ganancia = monto * pnl
        trades.append({
            "fecha":    idx.strftime("%m/%d %H:%M") if hasattr(idx, "strftime") else str(idx),
            "senal":    row["signal"],
            "calidad":  row["signal_quality"],
            "entrada":  round(entry, 5),
            "salida":   round(exit_, 5),
            "pnl_pct":  round(pnl*100, 2),
            "ganancia": round(ganancia, 2),
            "resultado": "WIN" if pnl > 0 else "LOSS",
            "rsi":      round(float(row["rsi_smooth"]), 1),
        })
    if not trades:
        return {"trades": [], "stats": {}}
    tdf   = pd.DataFrame(trades)
    wins  = tdf[tdf["resultado"]=="WIN"]
    loss  = tdf[tdf["resultado"]=="LOSS"]
    wr    = len(wins)/len(tdf)*100
    total_g = tdf["ganancia"].sum()
    gw    = wins["ganancia"].sum()
    gl    = abs(loss["ganancia"].sum()) if len(loss) else 0.0001
    cum   = tdf["ganancia"].cumsum()
    dd    = (cum - cum.cummax()).min()
    avg_w = wins["ganancia"].mean() if len(wins) else 0
    avg_l = abs(loss["ganancia"].mean()) if len(loss) else 0.0001
    racha = lambda tipo: max((sum(1 for _ in g) for k,g in __import__("itertools").groupby(tdf["resultado"]) if k==tipo), default=0)
    stats = {
        "total_trades": len(tdf), "wins": len(wins), "losses": len(loss),
        "win_rate": round(wr,1), "total_ganancia": round(total_g,2),
        "profit_factor": round(gw/gl,2), "max_drawdown": round(dd,2),
        "rr_ratio": round(avg_w/avg_l,2), "capital_final": round(capital+total_g,2),
        "avg_win": round(avg_w,2), "avg_loss": round(avg_l,2),
        "racha_win": racha("WIN"), "racha_loss": racha("LOSS"),
    }
    return {"trades": trades, "stats": stats}

def _kpi_v11(label, value, sub="", color="#c8d8e8"):
    st.markdown(f"""<div style="background:linear-gradient(135deg,#0a1020,#0d1830);border:1px solid #1a2a45;
        border-radius:12px;padding:16px;text-align:center;">
        <div style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#4a7a99;letter-spacing:2px;margin-bottom:6px;">{label}</div>
        <div style="font-family:'Rajdhani',sans-serif;font-size:34px;font-weight:700;color:{color};line-height:1.1;">{value}</div>
        {"<div style='font-family:Share Tech Mono,monospace;font-size:11px;color:#4a7a99;margin-top:3px;'>"+sub+"</div>" if sub else ""}
    </div>""", unsafe_allow_html=True)

def _progbar(pct, color="#f0b429"):
    st.markdown(f"""<div style="height:8px;background:#1a2a45;border-radius:4px;overflow:hidden;margin:4px 0;">
        <div style="height:100%;width:{min(100,max(0,pct))}%;background:{color};border-radius:4px;transition:width .6s;"></div>
    </div>""", unsafe_allow_html=True)

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
        "hora": datetime.now(TZ_ARG).strftime("%H:%M:%S"),
    }

def analizar_activo_swing(symbol, tf="H1"):
    """Analiza activo para swing trading M15/H1/H4/D1"""
    if tf == "M15":   interval, period = "15m", "5d"
    elif tf == "H1":  interval, period = "1h",  "30d"
    elif tf == "H4":  interval, period = "4h",  "30d"
    else:             interval, period = "1d",  "90d"
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
        "hora": datetime.now(TZ_ARG).strftime("%H:%M"),
        "tf": tf,
    }

# ================================================================
# SIDEBAR
# ================================================================
with st.sidebar:
    st.markdown('<div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:22px;color:#c8920a;letter-spacing:2px;margin-bottom:16px;">QQE CMD v10</div>', unsafe_allow_html=True)

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
    racha    = st.session_state.get("racha_losses", 0)
    _racha_txt = "🟢 0" if racha==0 else ("🟡 1 - CUIDADO" if racha==1 else f"🔴 {racha} - PARAR")
    racha_col = "#4ade80" if racha == 0 else ("#fbbf24" if racha == 1 else "#f87171")
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
      <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:{bar_col};margin-top:3px;">Pérdida: ${perdida:.2f} / SL: ${sl_monto:.2f}</div>
      <div style="display:flex;justify-content:space-between;margin-top:8px;padding-top:8px;border-top:1px solid #1e3050;">
        <span style="font-family:Share Tech Mono,monospace;font-size:11px;color:#4a7a99;">RACHA LOSSES</span>
        <span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:17px;color:{racha_col};">{_racha_txt}</span>
      </div>
    </div>""", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("+ Loss", key="add_loss"):
            st.session_state.perdida_dia += cap * 0.02
            st.session_state.racha_losses = st.session_state.get("racha_losses", 0) + 1
            if st.session_state.perdida_dia >= sl_monto or st.session_state.racha_losses >= 2:
                st.session_state.radar_bloqueado = True
            st.rerun()
    with c2:
        if st.button("Reset", key="reset_loss"):
            st.session_state.perdida_dia = 0.0
            st.session_state.radar_bloqueado = False
            st.session_state.racha_losses = 0
            st.rerun()

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
# HEADER v10
# ================================================================
ses_nom, ses_est, ses_col, ses_bg, ses_border = get_session_info()
hora_arg_now = datetime.now(TZ_ARG).strftime("%H:%M")
_, cp, np_ = calc_pnl()
racha_actual = st.session_state.get("racha_losses", 0)
_racha_hdr = "✓ 0" if racha_actual==0 else (f"⚠ {racha_actual}" if racha_actual==1 else f"🛑 {racha_actual}")
capital_hoy  = st.session_state.capital

if ses_est == "OPERAR":
    sem_color = "#22c55e"; sem_bg = "rgba(34,197,94,0.12)"; sem_icon = "🟢"
elif ses_est in ("ACTIVO","PRECAUCION"):
    sem_color = "#f0b429"; sem_bg = "rgba(240,180,41,0.12)"; sem_icon = "🟡"
else:
    sem_color = "#64748b"; sem_bg = "rgba(100,116,139,0.12)"; sem_icon = "🔴"

pnl_col  = "#22c55e" if np_ >= 0 else "#ef4444"
racha_col = "#22c55e" if racha_actual == 0 else ("#f0b429" if racha_actual == 1 else "#ef4444")
if "audio_on" not in st.session_state:
    st.session_state.audio_on = True

st.markdown(f"""
<div style="background:linear-gradient(135deg,#080e1c,#0d1830);border:1px solid #1a2a45;border-radius:14px;
     padding:12px 18px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;
     flex-wrap:wrap;gap:10px;box-shadow:0 4px 30px rgba(0,0,0,0.5);">
  <div>
    <div style="font-family:'Exo 2',sans-serif;font-weight:900;font-size:22px;letter-spacing:3px;
         background:linear-gradient(90deg,#f0b429,#ff8c00,#f0b429);background-size:200%;
         -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
      QQE COMMAND v10
    </div>
    <div style="font-family:'Share Tech Mono',monospace;font-size:9px;color:#4a7a99;letter-spacing:2px;">
      HECTOR · GOYA, CTES · TRIPLE CONFIRM SYSTEM
    </div>
  </div>
  <div style="background:{sem_bg};border:1px solid {sem_color};border-radius:10px;padding:8px 14px;text-align:center;min-width:120px;">
    <div style="font-family:'Share Tech Mono',monospace;font-size:9px;color:{sem_color};letter-spacing:2px;">{sem_icon} SESION</div>
    <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:14px;color:{sem_color};">{ses_nom}</div>
    <div style="font-family:'Share Tech Mono',monospace;font-size:9px;color:{sem_color};opacity:0.8;">{ses_est}</div>
  </div>
  <div style="text-align:center;">
    <div style="font-family:'Share Tech Mono',monospace;font-size:9px;color:#4a7a99;letter-spacing:2px;">🕐 ARG</div>
    <div id="reloj-arg" style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:28px;color:#c8d8e8;line-height:1;">{hora_arg_now}</div>
  </div>
  <div style="text-align:center;">
    <div style="font-family:'Share Tech Mono',monospace;font-size:9px;color:#4a7a99;letter-spacing:2px;">P&L HOY</div>
    <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:28px;color:{pnl_col};">${{np_:+.2f}}</div>
  </div>
  <div style="text-align:center;">
    <div style="font-family:'Share Tech Mono',monospace;font-size:9px;color:#4a7a99;letter-spacing:2px;">RACHA</div>
    <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:26px;color:{racha_col};">{_racha_hdr}</div>
  </div>
  <div style="text-align:center;">
    <div style="font-family:'Share Tech Mono',monospace;font-size:9px;color:#4a7a99;letter-spacing:2px;">ENTRADA 1%</div>
    <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:24px;color:#f0b429;">${{capital_hoy*0.01:.2f}}</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<script>
(function() {
  function updateClock() {
    var el = document.getElementById('reloj-arg');
    if (!el) return;
    var now = new Date();
    var utcMs = now.getTime() + (now.getTimezoneOffset()*60000);
    var argMs = utcMs - (3*3600000);
    var argDate = new Date(argMs);
    var h = argDate.getHours().toString().padStart(2,'0');
    var m = argDate.getMinutes().toString().padStart(2,'0');
    var s = argDate.getSeconds().toString().padStart(2,'0');
    el.textContent = h + ':' + m + ':' + s;
  }
  updateClock();
  setInterval(updateClock, 1000);
})();
</script>
""", unsafe_allow_html=True)

# Botón silenciar y test sonido
_c1, _c2, _c3 = st.columns([1,1,8])
with _c1:
    if st.button("🔔 ON" if st.session_state.audio_on else "🔕 OFF", key="btn_snd_toggle"):
        st.session_state.audio_on = not st.session_state.audio_on
        st.rerun()
with _c2:
    if st.button("🔊 Test", key="btn_snd_test"):
        st.session_state["_play_sound"] = "signal"

_snd = st.session_state.pop("_play_sound", "none")
if racha_actual >= 2 and st.session_state.get("_racha_alerted",0) != racha_actual:
    _snd = "stop_hit"; st.session_state["_racha_alerted"] = racha_actual
_h_utc = get_utc_hour(); _min_utc = datetime.now(timezone.utc).minute
if _h_utc in (7,13) and _min_utc == 0:
    _ses_key = f"_ses_alerted_{_h_utc}"
    if not st.session_state.get(_ses_key,False):
        _snd = "session_open"; st.session_state[_ses_key] = True
_play_audio(_snd, st.session_state.audio_on)



# ================================================================
# TABS
# ================================================================

# ================================================================
# TABS — v10
# ================================================================
tab_triple, tab_noticias, tab_swing, tab_ops, tab_diario, tab_binarias, tab_copy, tab_codigos, tab_scan1, tab_backtest, tab_sim, tab_educativo, tab_mejoras = st.tabs([
    "🎯 TRIPLE EN VIVO", "📰 NOTICIAS+IA",
    "📈 SWING+IA", "📋 REGISTRO", "📓 DIARIO",
    "🤖 SCRIPTS LUA", "👥 COPY", "💻 CODIGOS QQE",
    "⚡ SCANNER",
    "📊 BACKTEST", "🔮 SIMULACIÓN", "📚 EDUCATIVO", "🔧 MEJORAS"
])

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
        st.session_state.scan_ultimo   = datetime.now(TZ_ARG).strftime("%H:%M:%S")
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
            _rsi_col = "#f87171" if r["rsi"] > 70 else ("#4ade80" if r["rsi"] < 30 else "#c8d8e8")

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
                  <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:14px;color:{_rsi_col};">{r['rsi']:.1f}</div>
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
# TAB 2 — SWING SCANNER + IA (FUSIONADO)
# ================================================================
with tab_swing:
    st.markdown('<div class="sec">📈 SWING SCANNER + ANALIZADOR IA — M15 / H1 / H4 / D1</div>', unsafe_allow_html=True)

    # ── ASESORAMIENTO DE TEMPORALIDAD ────────────────────────────
    hora_utc = datetime.now(timezone.utc).hour
    hora_arg_disp = datetime.now(TZ_ARG).strftime("%H:%M")
    if 7 <= hora_utc < 10:
        sesion_activa = "LONDRES"
        ses_col = "#4ade80"
        tf_recom = "M15 o H1"
        ses_desc = "Sesion Londres activa — alta liquidez en EUR/GBP/XAU. Ideal M15-H1."
    elif 13 <= hora_utc < 17:
        sesion_activa = "NUEVA YORK"
        ses_col = "#60a5fa"
        tf_recom = "H1 o H4"
        ses_desc = "Sesion NY activa — alta liquidez en USD. Tendencias fuertes. Ideal H1-H4."
    elif 0 <= hora_utc < 5:
        sesion_activa = "TOKYO"
        ses_col = "#f472b6"
        tf_recom = "H4 o D1"
        ses_desc = "Sesion Tokyo — movimientos moderados en JPY/AUD. Mejor H4 o D1."
    else:
        sesion_activa = "MERCADO TRANQUILO"
        ses_col = "#c8920a"
        tf_recom = "H4 o D1"
        ses_desc = "Mercado entre sesiones. Rango reducido. Mejor H4/D1 o esperar."

    st.markdown(f"""
    <div style="background:#0d1525;border:2px solid {ses_col};border-radius:12px;padding:12px 18px;margin-bottom:14px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
      <div>
        <span style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;letter-spacing:2px;">SESION ACTIVA</span>
        <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:22px;color:{ses_col};">🌐 {sesion_activa}</div>
        <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#94a3b8;">{ses_desc}</div>
      </div>
      <div style="text-align:right;">
        <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">TEMPORALIDAD OPTIMA</div>
        <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:28px;color:{ses_col};">{tf_recom}</div>
        <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">{hora_arg_disp} ARG · {hora_utc:02d}:xx UTC</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── CONTROLES ───────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns([2, 2, 2, 3])
    with c1:
        swing_btn = st.button("📈 ESCANEAR SWING", key="swing_scan_btn", use_container_width=True)
    with c2:
        tf_sel = st.selectbox("Temporalidad", ["M15","H1","H4","D1"], key="swing_tf",
                              index=["M15","H1","H4","D1"].index(
                                  "M15" if "M15" in tf_recom else "H4" if "H4" in tf_recom else "H1"))
    with c3:
        tipo_sw = st.selectbox("Tipo", ["Todos","forex","commodity","index","crypto"], key="swing_tipo")
    with c4:
        act_pool = list(ACTIVOS.keys()) if tipo_sw == "Todos" else [a for a,v in ACTIVOS.items() if v["tipo"]==tipo_sw]
        activos_swing = st.multiselect("Activos", list(ACTIVOS.keys()), default=act_pool[:8] if len(act_pool)>=8 else act_pool, key="act_swing", label_visibility="collapsed")

    # ── BADGE DE TEMPORALIDAD ───────────────────────────────────
    tf_badges = {
        "M15": ("⚡ M15 — Alta frecuencia", "#f87171", "#3a0a0a",
                "Señales rapidas. Solo durante sesion activa. Ruido elevado fuera de sesion.", "RIESGO ALTO"),
        "H1":  ("📊 H1 — Tendencias cortas", "#4ade80", "#0a3020",
                "Balance ideal entre señal y ruido. Funciona bien en Londres y NY.", "RECOMENDADO"),
        "H4":  ("📈 H4 — Tendencias medias", "#60a5fa", "#0a1a3a",
                "Señales mas confiables, menos frecuentes. Puede operar en cualquier sesion.", "MUY CONFIABLE"),
        "D1":  ("🌙 D1 — Tendencias largas", "#a78bfa", "#1a0a3a",
                "Minimo ruido, maximo contexto. Ideal para definir sesgo del dia.", "CONTEXTO DIARIO"),
    }
    badge = tf_badges.get(tf_sel, tf_badges["H1"])
    st.markdown(f"""
    <div style="background:{badge[2]};border:1px solid {badge[1]};border-radius:8px;padding:8px 14px;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;">
      <div>
        <span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:16px;color:{badge[1]};">{badge[0]}</span>
        <span style="font-family:Share Tech Mono,monospace;font-size:11px;color:#94a3b8;margin-left:12px;">{badge[3]}</span>
      </div>
      <span style="font-family:Share Tech Mono,monospace;font-size:10px;color:{badge[1]};border:1px solid {badge[1]};border-radius:4px;padding:2px 8px;">{badge[4]}</span>
    </div>""", unsafe_allow_html=True)

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
                r["iqopt"]  = ACTIVOS[activo]["iqopt"]
                r["tipo"]   = ACTIVOS[activo]["tipo"]
                swing_res[activo] = r
            prog2.progress((idx+1) / max(len(activos_swing),1))
        prog2.empty(); txt2.empty()
        st.session_state.swing_resultados = swing_res

        if st.session_state.tg_on and st.session_state.tg_token:
            for activo, r in swing_res.items():
                if r["score"] >= 75 and r["direccion"] != "ESPERAR":
                    key_sw = f"swing_{activo}_{r['hora']}"
                    enviadas = st.session_state.get("tg_enviadas", set())
                    if key_sw not in enviadas:
                        ic = "📈" if "LONG" in r["direccion"] else "📉"
                        iqn = r.get("iqopt", activo)
                        msg = (f"{ic} <b>SWING {tf_sel} — {iqn}</b>\n"
                               f"━━━━━━━━━━━━━━\n"
                               f"📊 {r['direccion']} — {r['tendencia']}\n"
                               f"🎯 Score: {r['score']}%\n"
                               f"💰 Precio: {r['precio']:.5f}\n"
                               f"🛑 Stop Loss: {r['sl']:.5f}\n"
                               f"🎯 Take Profit: {r['tp']:.5f}\n"
                               f"📊 RSI: {r['rsi']:.1f}\n"
                               f"⏱ Temporalidad: {tf_sel}\n"
                               f"💵 Capital 2%: <b>${st.session_state.capital*0.02:.2f}</b>\n"
                               f"<i>QQE Command v10 · {sesion_activa}</i>")
                        ok = enviar_telegram(st.session_state.tg_token, st.session_state.tg_chat, msg)
                        if ok:
                            enviadas.add(key_sw)
                            st.session_state.tg_enviadas = enviadas
        st.rerun()

    # ── RESULTADOS SCANNER ──────────────────────────────────────
    if hasattr(st.session_state, "swing_resultados") and st.session_state.swing_resultados:
        res_list = sorted(st.session_state.swing_resultados.values(), key=lambda x: x["score"], reverse=True)

        # Señales destacadas en cartel grande
        top_signals = [r for r in res_list if r["score"] >= 70 and r["direccion"] != "ESPERAR"]
        if top_signals:
            st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#c8920a;letter-spacing:2px;margin:8px 0 6px;">SEÑALES ACTIVAS</div>', unsafe_allow_html=True)
            cols_sig = st.columns(min(len(top_signals), 3))
            for i, r in enumerate(top_signals[:3]):
                es_long = "LONG" in r["direccion"]
                c_bg    = "#0a3020" if es_long else "#200a0a"
                c_bo    = "#16a34a" if es_long else "#dc2626"
                c_tx    = "#4ade80" if es_long else "#f87171"
                ic_dir  = "▲ SUBE" if es_long else "▼ BAJA"
                tipo_lbl= {"forex":"Forex","commodity":"Mat. Prima","index":"Indice","crypto":"Crypto"}.get(r["tipo"], r["tipo"])
                with cols_sig[i]:
                    st.markdown(f"""
                    <div style="background:{c_bg};border:2px solid {c_bo};border-radius:14px;padding:16px;text-align:center;">
                      <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;letter-spacing:2px;">{tipo_lbl} · {r["tf"]}</div>
                      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:26px;color:#c8d8e8;margin:4px 0;">{r["iqopt"]}</div>
                      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:36px;color:{c_tx};">{ic_dir}</div>
                      <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:{c_tx};">AHORA · {r["hora"]}</div>
                      <div style="margin-top:10px;display:grid;grid-template-columns:1fr 1fr;gap:6px;">
                        <div style="background:#060c18;border-radius:6px;padding:6px;">
                          <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">SCORE</div>
                          <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:20px;color:{c_tx};">{r["score"]}%</div>
                        </div>
                        <div style="background:#060c18;border-radius:6px;padding:6px;">
                          <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">ENTRADA</div>
                          <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:14px;color:#c8d8e8;">{r["precio"]:.4f}</div>
                        </div>
                      </div>
                      <div style="margin-top:6px;display:grid;grid-template-columns:1fr 1fr;gap:6px;">
                        <div style="background:#3a0a0a;border-radius:6px;padding:5px;">
                          <div style="font-family:Share Tech Mono,monospace;font-size:8px;color:#f87171;">STOP</div>
                          <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:13px;color:#f87171;">{r["sl"]:.4f}</div>
                        </div>
                        <div style="background:#0a3020;border-radius:6px;padding:5px;">
                          <div style="font-family:Share Tech Mono,monospace;font-size:8px;color:#4ade80;">TARGET</div>
                          <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:13px;color:#4ade80;">{r["tp"]:.4f}</div>
                        </div>
                      </div>
                    </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # Lista completa
        st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;letter-spacing:2px;margin:4px 0 8px;">TODOS LOS ACTIVOS ESCANEADOS</div>', unsafe_allow_html=True)
        for r in res_list:
            es_long  = "LONG" in r["direccion"]
            es_short = "SHORT" in r["direccion"]
            card_cls = "signal-call" if es_long else "signal-put" if es_short else "signal-wait"
            ic       = "▲" if es_long else "▼" if es_short else "—"
            col_dir  = "#4ade80" if es_long else "#f87171" if es_short else "#c8920a"
            score    = r["score"]
            tipo_lbl = {"forex":"FOREX","commodity":"MAT. PRIMA","index":"INDICE","crypto":"CRYPTO"}.get(r["tipo"], r["tipo"].upper())
            tipo_col = {"forex":"#60a5fa","commodity":"#fbbf24","index":"#a78bfa","crypto":"#fb923c"}.get(r["tipo"],"#94a3b8")

            st.markdown(f"""
            <div class="{card_cls}">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-wrap:wrap;gap:6px;">
                <div>
                  <span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:22px;color:#c8d8e8;">{r["iqopt"]}</span>
                  <span style="font-family:Share Tech Mono,monospace;font-size:10px;color:{tipo_col};margin-left:8px;">{tipo_lbl}</span>
                  <span style="font-family:Share Tech Mono,monospace;font-size:11px;color:{col_dir};margin-left:8px;">{ic} {r["direccion"]}</span>
                  <span style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;margin-left:8px;">{r.get("tf","")}</span>
                </div>
                <div style="text-align:right;">
                  <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:24px;color:{col_dir};">{score}%</div>
                  <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">SCORE</div>
                </div>
              </div>
              <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;">
                <div style="background:#060c18;border-radius:6px;padding:10px;text-align:center;">
                  <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">PRECIO</div>
                  <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;color:#c8d8e8;">{r["precio"]:.5f}</div>
                </div>
                <div style="background:#3a0a0a;border:1px solid #dc2626;border-radius:6px;padding:10px;text-align:center;">
                  <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#f87171;">STOP LOSS</div>
                  <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;color:#f87171;">{r["sl"]:.5f}</div>
                </div>
                <div style="background:#0a3020;border:1px solid #16a34a;border-radius:6px;padding:10px;text-align:center;">
                  <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4ade80;">TAKE PROFIT</div>
                  <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;color:#4ade80;">{r["tp"]:.5f}</div>
                </div>
              </div>
              <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:6px;">
                <div style="text-align:center;"><span style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">RSI: </span><span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:13px;color:#c8d8e8;">{r["rsi"]:.1f}</span></div>
                <div style="text-align:center;"><span style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">EMA20: </span><span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:13px;color:#c8d8e8;">{r["ema20"]:.5f}</span></div>
                <div style="text-align:center;"><span style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">ATR: </span><span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:13px;color:#c8d8e8;">{r["atr"]:.5f}</span></div>
              </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;background:#0d1525;border:2px dashed #1e3050;border-radius:12px;margin-top:10px;">
          <div style="font-size:48px;margin-bottom:10px;">📈</div>
          <div style="font-family:Rajdhani,sans-serif;font-size:20px;color:#4a7a99;">Presiona ESCANEAR SWING</div>
          <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#2a3a55;margin-top:6px;">Analiza M15/H1/H4/D1 con SL y TP calculados por ATR</div>
        </div>""", unsafe_allow_html=True)

    # ── ANALIZADOR IA (integrado en misma tab) ───────────────────
    st.markdown("---")
    st.markdown('<div class="sec" style="margin-top:8px;">🧠 ANALIZADOR IA — CAPTURA DE GRAFICO IQ OPTION</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#0d1525;border:1px solid #c8920a;border-radius:12px;padding:12px 18px;margin-bottom:14px;">
      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;color:#c8920a;margin-bottom:6px;">Como usar</div>
      <div style="font-size:13px;color:#94a3b8;line-height:1.9;">
        1. IQ Option → elegir activo → temporalidad → captura de pantalla<br>
        2. Completar datos del trade abajo<br>
        3. Subir imagen → IA analiza y da decision clara con SL/TP<br>
        <b style="color:#c8920a;">Podes subir hasta 3 imagenes</b> — ej: M15 + H1 + H4 para multitemporal
      </div>
    </div>""", unsafe_allow_html=True)

    if not get_ia_ok():
        st.markdown('<div style="background:#3a0a0a;border:1px solid #dc2626;border-radius:8px;padding:12px;color:#f87171;font-family:Share Tech Mono,monospace;font-size:11px;">⚠ Necesitas la clave API de Anthropic en el sidebar para usar el analizador.</div>', unsafe_allow_html=True)
    else:
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            activo_ia = st.selectbox("Activo (IQ Option)", list(ACTIVOS.keys()), key="ia_activo")
        with col_b:
            tf_ia = st.selectbox("Temporalidad", ["M15 (15 min)","H1 (1 hora)","H4 (4 horas)","D1 (diario)"], key="ia_tf")
        with col_c:
            dir_ia = st.selectbox("Direccion que analizas", ["Sin preferencia","CALL / LONG (sube)","PUT / SHORT (baja)"], key="ia_dir")

        col_d, col_e = st.columns(2)
        with col_d:
            precio_ia = st.text_input("Precio actual (opcional)", placeholder="1.0842", key="ia_precio")
        with col_e:
            notas_ia = st.text_input("Notas (opcional)", placeholder="Rompio resistencia, noticias hoy...", key="ia_notas")

        iqopt_name = ACTIVOS[activo_ia]["iqopt"]
        st.markdown(f'<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#c8920a;margin:4px 0;">📋 Nombre en IQ Option: <b>{iqopt_name}</b></div>', unsafe_allow_html=True)

        st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;letter-spacing:2px;margin:8px 0 4px;">CAPTURA DEL GRAFICO (hasta 3) · 📱 iPhone: capturá → Archivos → subí</div>', unsafe_allow_html=True)
        imgs = st.file_uploader("", type=["png","jpg","jpeg","webp"], accept_multiple_files=True, key="ia_imgs", label_visibility="collapsed")

        if imgs:
            cols_prev = st.columns(min(len(imgs), 3))
            for i, img in enumerate(imgs[:3]):
                with cols_prev[i]:
                    st.image(img, use_column_width=True)
                    st.markdown(f'<div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;text-align:center;">{img.name}</div>', unsafe_allow_html=True)

            if st.button("🧠 ANALIZAR CON IA", key="ia_analizar_swing", use_container_width=True):
                with st.spinner("La IA está analizando el grafico..."):
                    try:
                        content = []
                        for img in imgs[:3]:
                            ext = img.name.split(".")[-1].lower()
                            mtype = "image/jpeg" if ext in ("jpg","jpeg") else f"image/{ext}"
                            b64 = base64.b64encode(img.read()).decode()
                            content.append({"type":"image","source":{"type":"base64","media_type":mtype,"data":b64}})

                        ctx_dir    = dir_ia if dir_ia != "Sin preferencia" else "sin direccion previa"
                        ctx_precio = f"Precio actual: {precio_ia}." if precio_ia else ""
                        ctx_notas  = f"Contexto adicional: {notas_ia}." if notas_ia else ""
                        ctx_cap    = f"Capital de Hector: ${st.session_state.capital:.2f}. Entrada 2%: ${st.session_state.capital*0.02:.2f}."

                        content.append({"type":"text","text":f"Analiza este grafico de {iqopt_name} ({activo_ia}) en {tf_ia}.\nEl trader considera: {ctx_dir}. {ctx_precio} {ctx_notas} {ctx_cap}\n\nDame un analisis COMPLETO de swing trading."})

                        sys_swing = f"""Eres el analista de swing trading personal de Hector. Opera en IQ Option.
El activo en IQ Option se llama: {iqopt_name}.

ESTRUCTURA OBLIGATORIA (no cambiar el orden):
1. DECISION: ENTRAR CALL / ENTRAR PUT / ESPERAR (en mayusculas, primera linea)
2. PROBABILIDAD DE EXITO: X%
3. POR QUE: 2-3 lineas del razonamiento tecnico clave
4. STOP LOSS: precio exacto o distancia en pips
5. TAKE PROFIT: precio exacto (ratio minimo 1:2)
6. TIEMPO ESTIMADO: cuanto puede tardar el movimiento
7. INVALIDA LA SEÑAL SI: una linea concisa

Maximo 220 palabras. En espanol rioplatense. Directo. Sin rodeos.
Si el grafico es poco claro, decilo sin dudar."""

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
                                "texto": texto, "hora": datetime.now(TZ_ARG).strftime("%H:%M"),
                                "activo": activo_ia, "iqopt": iqopt_name, "tf": tf_ia
                            }
                            st.rerun()
                        else:
                            st.error(f"Error API: {resp.status_code} — {resp.text[:200]}")
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.markdown("""
            <div style="text-align:center;padding:40px 20px;background:#0d1525;border:2px dashed #1e3050;border-radius:12px;margin-top:10px;">
              <div style="font-size:48px;margin-bottom:10px;">📱</div>
              <div style="font-family:Rajdhani,sans-serif;font-size:18px;color:#4a7a99;">Subi la captura de IQ Option</div>
              <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#2a3a55;margin-top:6px;">Hasta 3 graficos — M15 + H1 + H4</div>
            </div>""", unsafe_allow_html=True)

        resp_key = f"swing_ia_resp_{activo_ia}"
        if resp_key in st.session_state and st.session_state[resp_key]:
            res_ia = st.session_state[resp_key]
            texto  = res_ia["texto"]

            if "ENTRAR CALL" in texto.upper()[:80]:
                rc,rb,rbr,ri = "#4ade80","#0a3020","#16a34a","🟢"
            elif "ENTRAR PUT" in texto.upper()[:80]:
                rc,rb,rbr,ri = "#f87171","#200a0a","#dc2626","🔴"
            elif "ESPERAR" in texto.upper()[:80]:
                rc,rb,rbr,ri = "#fbbf24","#2a1a00","#c8920a","🟡"
            else:
                rc,rb,rbr,ri = "#c8d8e8","#0d1525","#1e3050","⚪"

            st.markdown(f"""
            <div style="background:{rb};border:2px solid {rbr};border-radius:14px;padding:20px;margin-top:16px;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:22px;color:{rc};">{ri} ANALISIS IA — {res_ia["iqopt"]}</div>
                <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">{res_ia["tf"]} · {res_ia["hora"]}</div>
              </div>
              <div style="font-size:14px;color:#c8d8e8;line-height:2.1;">{texto.replace(chr(10),"<br>")}</div>
              <div style="margin-top:12px;padding-top:10px;border-top:1px solid {rbr};font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;">
                Capital: ${st.session_state.capital:.2f} · Entrada 2%: ${st.session_state.capital*0.02:.2f} · QQE Command v10
              </div>
            </div>""", unsafe_allow_html=True)

            col_g1, col_g2 = st.columns(2)
            with col_g1:
                if st.button("📓 Guardar en Diario", key="guardar_diario_ia"):
                    st.session_state.diario.append({
                        "fecha": get_fecha_arg().strftime("%d/%m/%Y"),
                        "hora":  res_ia["hora"],
                        "tipo":  "ANALISIS IA",
                        "activo": res_ia["iqopt"],
                        "texto": texto,
                        "tf":    res_ia["tf"],
                    })
                    st.success("Guardado en el diario!")
            with col_g2:
                if st.button("📤 Enviar a Telegram", key="enviar_ia_tg"):
                    if st.session_state.tg_token:
                        ic_tg = "🟢" if "CALL" in texto.upper()[:80] else "🔴" if "PUT" in texto.upper()[:80] else "🟡"
                        msg_tg = (f"{ic_tg} <b>ANALISIS IA — {res_ia['iqopt']}</b>\n"
                                  f"━━━━━━━━━━━━━━\n"
                                  f"⏱ {res_ia['tf']} · {res_ia['hora']}\n\n"
                                  + texto[:800] +
                                  f"\n\n<i>QQE Command v10</i>")
                        ok = enviar_telegram(st.session_state.tg_token, st.session_state.tg_chat, msg_tg)
                        if ok: st.success("Enviado a Telegram!")
                        else: st.error("Error enviando a Telegram")
                    else:
                        st.warning("Configurar Telegram en el sidebar")
# ================================================================

# ================================================================
# TAB 3 — TRIPLE EN VIVO (fusión ESTRATEGIA + HECTOR SCANNER)
# ================================================================
with tab_triple:

    # ── HEADER GRANDE CON DECISION RÁPIDA ──────────────────────
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0d1525 0%,#0a1e0a 100%);border:1px solid #c8920a;border-radius:14px;padding:18px 22px;margin-bottom:18px;">
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
        <div>
          <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:26px;color:#c8920a;letter-spacing:1px;">🎯 ESTRATEGIA TRIPLE EN VIVO</div>
          <div style="font-family:Share Tech Mono,monospace;font-size:12px;color:#4a7a99;margin-top:4px;">4 FILTROS · HECTOR 1 · EMA + MACD + RSI + VELA</div>
        </div>
        <div style="display:flex;gap:16px;flex-wrap:wrap;">
          <div style="text-align:center;background:#060c18;border:1px solid #16a34a;border-radius:8px;padding:10px 18px;">
            <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:28px;color:#4ade80;">4/4</div>
            <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">= ENTRAR</div>
          </div>
          <div style="text-align:center;background:#060c18;border:1px solid #ff9800;border-radius:8px;padding:10px 18px;">
            <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:28px;color:#ff9800;">3/4</div>
            <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">= ESPERAR</div>
          </div>
          <div style="text-align:center;background:#060c18;border:1px solid #dc2626;border-radius:8px;padding:10px 18px;">
            <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:28px;color:#64748b;">≤2/4</div>
            <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">= NO OPERAR</div>
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── REGLAS COMPACTAS EN ACORDEÓN ───────────────────────────
    with st.expander("📖 Ver reglas de los 4 filtros", expanded=False):
        col_rc, col_rp = st.columns(2)
        with col_rc:
            st.markdown("""
            <div style="background:#0a2010;border:1px solid #16a34a;border-radius:10px;padding:14px;">
              <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:16px;color:#4ade80;margin-bottom:10px;">🔺 CALL — las 4 condiciones</div>
              <div style="font-size:13px;color:#94a3b8;line-height:2.1;">
                <span style="color:#c8920a;">F1 EMA Stack:</span> EMA5 &gt; EMA13 &gt; EMA50<br>
                <span style="color:#c8920a;">F2 MACD:</span> Histograma positivo<br>
                <span style="color:#c8920a;">F3 RSI:</span> Entre 45 y 75<br>
                <span style="color:#c8920a;">F4 Vela:</span> Cierre &gt; Apertura (vela verde)
              </div>
            </div>
            """, unsafe_allow_html=True)
        with col_rp:
            st.markdown("""
            <div style="background:#200a0a;border:1px solid #dc2626;border-radius:10px;padding:14px;">
              <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:16px;color:#f87171;margin-bottom:10px;">🔻 PUT — espejo inverso</div>
              <div style="font-size:13px;color:#94a3b8;line-height:2.1;">
                <span style="color:#f87171;">F1 EMA Stack:</span> EMA5 &lt; EMA13 &lt; EMA50<br>
                <span style="color:#f87171;">F2 MACD:</span> Histograma negativo<br>
                <span style="color:#f87171;">F3 RSI:</span> Entre 25 y 55<br>
                <span style="color:#f87171;">F4 Vela:</span> Cierre &lt; Apertura (vela roja)
              </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#0d1525;border:1px solid #1e3050;border-radius:8px;padding:12px;margin-top:10px;font-size:13px;color:#94a3b8;line-height:1.8;">
          <strong style="color:#c8920a;">Gestión:</strong>
          Capital 1% por operación · Expiración 1–2 min · Máx 6 ops/día · 2 pérdidas seguidas = PARAR<br>
          <strong style="color:#f87171;">Invalidación:</strong>
          RSI &gt;70 o &lt;30 · Noticias de alto impacto próximos 15min · EMAs comprimidas · Fuera de sesión Londres/NY
        </div>
        """, unsafe_allow_html=True)

    # ── CONTROLES SCANNER ───────────────────────────────────────
    st.markdown('<div class="sec">⚡ SCANNER EN VIVO</div>', unsafe_allow_html=True)
    cv1, cv2, cv3 = st.columns([2, 2, 3])
    with cv1:
        triple_btn = st.button("🔺 ESCANEAR AHORA", key="triple_scan_btn", use_container_width=True)
    with cv2:
        tipo_filtro_t = st.selectbox("Filtrar por tipo", ["Todos", "forex", "commodity", "index", "crypto"], key="triple_tipo")
    with cv3:
        if tipo_filtro_t == "Todos":
            act_disp_t = list(ACTIVOS.keys())
        else:
            act_disp_t = [a for a, v in ACTIVOS.items() if v["tipo"] == tipo_filtro_t]
        activos_triple = st.multiselect(
            "Activos", list(ACTIVOS.keys()),
            default=act_disp_t[:8] if len(act_disp_t) >= 8 else act_disp_t,
            key="act_triple"
        )

    # ── FUNCIÓN ANÁLISIS (4 filtros HECTOR) ────────────────────
    def analizar_triple(symbol):
        df = obtener_datos_1min(symbol)
        if df is None or len(df) < 55:
            return None
        c = df["cierre"]; o = df["apertura"]
        h = df["maximo"]; l = df["minimo"]

        e5  = calc_ema(c, 5)
        e13 = calc_ema(c, 13)
        e50 = calc_ema(c, 50)
        # MACD consistente con script Lua: EMA(5) - EMA(13), signal EMA(4)
        macd_l = e5 - e13
        macd_s = calc_ema(macd_l, 4)
        macd_h = macd_l - macd_s
        rsi    = calc_rsi(c, 14)
        # Filtro volumen: vela actual debe tener volumen > promedio últimas 10
        vol_actual = df["volumen"].iloc[-1] if "volumen" in df.columns else 1
        vol_avg    = df["volumen"].iloc[-11:-1].mean() if "volumen" in df.columns else 1
        vol_ok     = vol_actual >= vol_avg * 0.8  # al menos 80% del promedio

        e5v = e5.iloc[-1]; e13v = e13.iloc[-1]; e50v = e50.iloc[-1]
        mh  = macd_h.iloc[-1]
        rv  = rsi.iloc[-1]
        cv_ = c.iloc[-1];  ov_ = o.iloc[-1]

        f1c = e5v > e13v and e13v > e50v
        f2c = mh > 0
        f3c = 45 < rv < 75
        f4c = cv_ > ov_
        f5c = vol_ok  # volumen activo

        f1p = e5v < e13v and e13v < e50v
        f2p = mh < 0
        f3p = 25 < rv < 55
        f4p = cv_ < ov_
        f5p = vol_ok

        nc = sum([f1c, f2c, f3c, f4c, f5c])
        np_ = sum([f1p, f2p, f3p, f4p, f5p])

        if nc < 3 and np_ < 3:
            return None

        dir_ = "CALL" if nc >= np_ else "PUT"
        filt = nc if dir_ == "CALL" else np_
        return {
            "precio": cv_, "rsi": rv, "macd_hist": mh,
            "e5": e5v, "e13": e13v, "e50": e50v,
            "f1": f1c if dir_ == "CALL" else f1p,
            "f2": f2c if dir_ == "CALL" else f2p,
            "f3": f3c if dir_ == "CALL" else f3p,
            "f4": f4c if dir_ == "CALL" else f4p,
            "f5": f5c if dir_ == "CALL" else f5p,
            "vol_ok": vol_ok,
            "direccion": dir_, "filtros": filt,
            "conf": int(50 + filt * 10),
            "hora": datetime.now(TZ_ARG).strftime("%H:%M:%S"),
        }

    # ── SCAN ────────────────────────────────────────────────────
    if triple_btn:
        resultados_t = []
        prog_t = st.progress(0)
        txt_t  = st.empty()

        # ── ADVERTENCIA DE SESIÓN ──────────────────────────────
        if not es_horario_operable():
            h_utc = get_utc_hour()
            if es_horario_aceptable():
                st.warning(f"⚠️ Horario {h_utc}:xx UTC — Fuera de ventana óptima. Señales menos confiables. Ventanas profit: 07-10 UTC y 13-16 UTC.")
            else:
                st.error(f"🛑 Horario {h_utc}:xx UTC — Mercado tranquilo. Alta tasa de falsas señales. Recomendado NO operar.")

        for idx, activo in enumerate(activos_triple):
            prog_t.progress((idx + 1) / max(len(activos_triple), 1))
            txt_t.markdown(f'<div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#c8920a;">⏳ Escaneando {activo}... ({idx+1}/{len(activos_triple)})</div>', unsafe_allow_html=True)
            res = analizar_triple(ACTIVOS[activo]["yahoo"])
            if res:
                res["activo"] = activo
                res["tipo"]   = ACTIVOS[activo]["tipo"]
                # ── CONFLUENCIA H1 ─────────────────────────────
                tend_h1 = get_tendencia_h1(ACTIVOS[activo]["yahoo"])
                res["tend_h1"] = tend_h1
                # Señal alineada con H1 = mayor confianza
                alineado = (res["direccion"] == "CALL" and tend_h1 == "ALCISTA") or \
                           (res["direccion"] == "PUT"  and tend_h1 == "BAJISTA")
                res["h1_alineado"] = alineado
                if alineado:
                    res["conf"] = min(res["conf"] + 10, 100)
                # Señal contra H1 = reducir confianza y marcar
                elif tend_h1 != "LATERAL":
                    res["conf"] = max(res["conf"] - 15, 30)
                    res["contra_tendencia"] = True
                else:
                    res["contra_tendencia"] = False
                # Sesión operativa suma confianza
                if es_horario_operable():
                    res["conf"] = min(res["conf"] + 5, 100)
                resultados_t.append(res)
        prog_t.empty(); txt_t.empty()
        st.session_state["triple_results"] = resultados_t
        st.session_state["triple_ultimo"]  = datetime.now(TZ_ARG).strftime("%H:%M:%S")
        st.session_state["triple_sesion_ok"] = es_horario_operable()

        # Telegram — solo 5/5 o 4/5 alineado con H1 en horario operativo
        if st.session_state.tg_on and st.session_state.tg_token:
            enviadas = st.session_state.get("tg_enviadas", set())
            for r in resultados_t:
                calidad = r["filtros"] >= 4 and r.get("h1_alineado", False) and es_horario_operable()
                if calidad:
                    key_tg = f"triple_{r['activo']}_{r['hora']}"
                    if key_tg not in enviadas:
                        ic = "🔺" if r["direccion"] == "CALL" else "🔻"
                        ses_nom = get_session_info()[0]
                        alin_txt = "✅ H1 ALINEADO" if r.get("h1_alineado") else "⚠ H1 LATERAL"
                        msg = (f"{ic} <b>TRIPLE CONFIRM — {r['activo']}</b>\n"
                               f"━━━━━━━━━━━━━━\n"
                               f"📊 {r['direccion']} — {r['filtros']}/5 · {alin_txt}\n"
                               f"📈 Tendencia H1: {r.get('tend_h1','?')}\n"
                               f"💰 Precio: {r['precio']:.5f}\n"
                               f"📊 RSI: {r['rsi']:.1f} · Confianza: {r['conf']}%\n"
                               f"💵 Entrada 1%: <b>${st.session_state.capital*0.01:.2f}</b>\n"
                               f"⏱ Exp: 1 min · 🕐 {r['hora']} · {ses_nom}\n"
                               f"<i>QQE Command v10</i>")
                        ok = enviar_telegram(st.session_state.tg_token, st.session_state.tg_chat, msg)
                        if ok:
                            enviadas.add(key_tg)
                            st.session_state.tg_enviadas = enviadas

        # ── Sonido según señales encontradas ─────────────────────
        completos_snd = [r for r in resultados_t if r["filtros"] >= 4]
        if completos_snd:
            # Determinar dirección dominante para el sonido
            n_call = sum(1 for r in completos_snd if r["direccion"]=="CALL")
            n_put  = sum(1 for r in completos_snd if r["direccion"]=="PUT")
            st.session_state["_play_sound"] = "signal_call" if n_call >= n_put else "signal_put"
        st.rerun()

    # ── RESULTADOS ──────────────────────────────────────────────
    if st.session_state.get("triple_results") is not None:
        res_t    = st.session_state["triple_results"]
        ultimo_t = st.session_state.get("triple_ultimo", "")
        completos_t = [r for r in res_t if r["filtros"] == 4]
        avisos_t    = [r for r in res_t if r["filtros"] == 3]
        _kc1 = "#4ade80" if completos_t else "#4a7a99"
        _kc2 = "#ff9800" if avisos_t else "#4a7a99"

        # KPIs
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px;margin-bottom:16px;">
          <div class="kpi"><div class="kpi-label">ÚLTIMO SCAN</div><div class="kpi-value" style="font-size:20px;color:#4a7a99;">{ultimo_t}</div></div>
          <div class="kpi"><div class="kpi-label">ACTIVOS</div><div class="kpi-value" style="color:#60a5fa;">{len(res_t)}</div></div>
          <div class="kpi"><div class="kpi-label">ENTRAR 4/4</div><div class="kpi-value" style="color:{_kc1};">{len(completos_t)}</div></div>
          <div class="kpi"><div class="kpi-label">ESPERAR 3/4</div><div class="kpi-value" style="color:{_kc2};">{len(avisos_t)}</div></div>
        </div>
        """, unsafe_allow_html=True)

        # SEÑALES ≥4 — destacadas arriba en grande
        if completos_t:
            st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#4ade80;letter-spacing:2px;margin-bottom:8px;">⚡ SEÑALES COMPLETAS — ENTRAR AHORA</div>', unsafe_allow_html=True)
            for r in completos_t:
                es_call = r["direccion"] == "CALL"
                col_d   = "#4ade80" if es_call else "#f87171"
                ic      = "🔺" if es_call else "🔻"
                tipo_col = {"forex":"#60a5fa","commodity":"#fbbf24","index":"#a78bfa","crypto":"#fb923c"}.get(r["tipo"],"#94a3b8")
                tipo_lbl = {"forex":"FOREX","commodity":"MATERIA PRIMA","index":"INDICE","crypto":"CRYPTO"}.get(r["tipo"],r["tipo"].upper())
                alineado = r.get("h1_alineado", False)
                tend_h1  = r.get("tend_h1", "?")
                contra   = r.get("contra_tendencia", False)
                vol_ok   = r.get("vol_ok", True)
                # Color borde: verde brillante si alineado, naranja si contra
                borde_col = col_d if not contra else "#ff9800"
                # Etiqueta de calidad
                if alineado and es_horario_operable():
                    calidad_label = '<span style="background:#16a34a;color:#fff;padding:3px 10px;border-radius:6px;font-family:Share Tech Mono,monospace;font-size:10px;margin-left:8px;">⭐ ALTA CALIDAD</span>'
                elif contra:
                    calidad_label = '<span style="background:#c8920a;color:#000;padding:3px 10px;border-radius:6px;font-family:Share Tech Mono,monospace;font-size:10px;margin-left:8px;">⚠ CONTRA H1</span>'
                else:
                    calidad_label = ''
                # Pre-calcular todo — sin ternarios dentro del HTML
                _bg        = "#041a0c" if es_call else "#1a0404"
                _txt_ent   = "&#9889; ENTRAR AHORA" if not contra else "&#9888; REVISAR — CONTRA H1"
                _h1_border = "#16a34a" if alineado else ("#c8920a" if contra else "#1e3050")
                _h1_color  = "#4ade80" if alineado else ("#ff9800" if contra else "#94a3b8")
                _h1_check  = "&#10003; " if alineado else "&#10007; "
                _ent_1pct  = round(st.session_state.capital * 0.01, 2)
                _filt_html = _build_filtros_html(r)
                if alineado and not contra:
                    _banner = '<div style="background:#0a3020;border:1px solid #16a34a;border-radius:6px;padding:8px;margin-top:8px;font-family:Share Tech Mono,monospace;font-size:12px;color:#4ade80;">&#9889; SEÑAL COMPLETA + H1 ALINEADO — Maxima calidad.</div>'
                elif contra:
                    _banner = '<div style="background:#2a1a00;border:1px solid #ff9800;border-radius:6px;padding:8px;margin-top:8px;font-family:Share Tech Mono,monospace;font-size:12px;color:#fbbf24;">&#9888; Señal OK pero contra H1. Reducir monto a 0.5%.</div>'
                else:
                    _banner = '<div style="background:#0a2030;border:1px solid #60a5fa;border-radius:6px;padding:8px;margin-top:8px;font-family:Share Tech Mono,monospace;font-size:12px;color:#60a5fa;">Señal completa. H1 lateral.</div>'
                st.markdown(f"""<div style="background:linear-gradient(135deg,{_bg} 0%,#0d1525 100%);border:2px solid {borde_col};border-radius:14px;padding:18px 22px;margin-bottom:12px;">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:14px;">
    <div><span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:32px;color:#c8d8e8;">{r['activo']}</span>
    <span style="font-family:Share Tech Mono,monospace;font-size:11px;color:{tipo_col};margin-left:12px;">{tipo_lbl}</span>
    {calidad_label}</div>
    <div style="display:flex;align-items:center;gap:16px;">
      <div style="text-align:center;">
        <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:42px;color:{col_d};line-height:1;">{ic} {r['direccion']}</div>
        <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:{col_d};">{_txt_ent}</div>
      </div>
      <div style="text-align:center;background:#060c18;border:1px solid {borde_col};border-radius:10px;padding:10px 16px;">
        <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:32px;color:{col_d};">{r['filtros']}/5</div>
        <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">FILTROS</div>
      </div>
    </div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr 1fr;gap:8px;margin-bottom:12px;">{_filt_html}</div>
  <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:8px;">
    <div style="background:#060c18;border-radius:6px;padding:8px;text-align:center;">
      <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">PRECIO</div>
      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;color:#c8d8e8;">{r['precio']:.5f}</div>
    </div>
    <div style="background:#060c18;border-radius:6px;padding:8px;text-align:center;">
      <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">RSI</div>
      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;color:{col_d};">{r['rsi']:.1f}</div>
    </div>
    <div style="background:#060c18;border:1px solid {_h1_border};border-radius:6px;padding:8px;text-align:center;">
      <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">H1 TREND</div>
      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:13px;color:{_h1_color};">{_h1_check}{tend_h1}</div>
    </div>
    <div style="background:#060c18;border-radius:6px;padding:8px;text-align:center;">
      <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">CONFIANZA</div>
      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;color:{col_d};">{r['conf']}%</div>
    </div>
    <div style="background:#060c18;border-radius:6px;padding:8px;text-align:center;">
      <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">ENTRADA 1%</div>
      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;color:#c8920a;">${_ent_1pct:.2f}</div>
    </div>
  </div>
  {_banner}
</div>""", unsafe_allow_html=True)

                # ── BOTÓN ENTRADA RÁPIDA ─────────────────────────────
                _btn_col = "#22c55e" if es_call else "#ef4444"
                _btn_dir = r["direccion"]
                _btn_act = r["activo"]
                _monto_ent = round(st.session_state.capital * 0.01, 2)
                _btn_key   = f"entrada_rapida_{r['activo']}_{r.get('hora','')}"

                st.markdown(f"""
                <div style="margin-top:12px;">
                  <div style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#4a7a99;
                       letter-spacing:2px;margin-bottom:6px;text-align:center;">
                    REGISTRAR ENTRADA · MONTO 1% = ${_monto_ent}
                  </div>
                </div>""", unsafe_allow_html=True)

                _c_btn1, _c_btn2 = st.columns([3,1])
                with _c_btn1:
                    if st.button(
                        f"{'🔺 CALL' if es_call else '🔻 PUT'} — ENTRAR {_btn_act} ${_monto_ent}",
                        key=_btn_key,
                        use_container_width=True
                    ):
                        # Registrar operación automáticamente
                        st.session_state.ops.append({
                            "fecha": get_fecha_arg().strftime("%d/%m"),
                            "hora":  datetime.now(TZ_ARG).strftime("%H:%M"),
                            "activo": _btn_act,
                            "dir":    _btn_dir,
                            "tipo":   "TRIPLE 1MIN",
                            "monto":  _monto_ent,
                            "resultado": "—",   # pendiente — se actualiza después
                            "pnl":    0.0,
                        })
                        # Sonido entrada
                        st.session_state["_play_sound"] = "signal_call" if es_call else "signal_put"
                        st.success(f"✅ Operación registrada — {_btn_dir} {_btn_act} ${_monto_ent} · Completar resultado en REGISTRO")
                with _c_btn2:
                    if st.button("WIN ✅", key=f"win_{_btn_key}"):
                        # Buscar última op sin resultado y marcarla WIN
                        for _op in reversed(st.session_state.ops):
                            if _op["activo"] == _btn_act and _op["resultado"] == "—":
                                _op["resultado"] = "WIN"
                                _op["pnl"]       = _monto_ent * 0.85  # pago IQ Option ~85%
                                st.session_state.racha_losses = 0
                                st.session_state["_play_sound"] = "signal_call"
                                break
                        st.rerun()

        # SEÑALES 3/4 — más pequeñas
        if avisos_t:
            st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#ff9800;letter-spacing:2px;margin:14px 0 8px;">⚠ PREPARARSE — 3/4 FILTROS</div>', unsafe_allow_html=True)
            cols_av = st.columns(min(len(avisos_t), 3))
            for i, r in enumerate(avisos_t):
                es_call = r["direccion"] == "CALL"
                col_d   = "#4ade80" if es_call else "#f87171"
                ic      = "🔺" if es_call else "🔻"
                with cols_av[i % 3]:
                    _fm   = _build_filtros_mini(r)
                    _e1p  = round(st.session_state.capital * 0.01, 2)
                    st.markdown(f'<div style="background:#0d1525;border:1px solid #ff9800;border-radius:10px;padding:14px;margin-bottom:10px;"><div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:20px;color:#c8d8e8;">{r["activo"]}</div><div style="font-family:Rajdhani,sans-serif;font-size:22px;color:{col_d};font-weight:700;">{ic} {r["direccion"]}</div><div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:4px;margin:8px 0;">{_fm}</div><div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#94a3b8;">RSI {r["rsi"]:.1f} &#183; ${_e1p:.2f}</div><div style="background:#2a1a00;border-radius:4px;padding:6px;margin-top:6px;font-family:Share Tech Mono,monospace;font-size:11px;color:#fbbf24;">&#9888; Esperar 4to filtro</div></div>', unsafe_allow_html=True)

        if not res_t:
            st.markdown('<div style="text-align:center;padding:40px;color:#4a7a99;font-family:Share Tech Mono,monospace;font-size:13px;">Sin señales. Mejor horario: 07-10 UTC (Londres) o 13-16 UTC (NY)</div>', unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;background:#0d1525;border:2px dashed #1e3050;border-radius:14px;margin-top:10px;">
          <div style="font-size:52px;margin-bottom:12px;">🎯</div>
          <div style="font-family:Rajdhani,sans-serif;font-size:22px;color:#4a7a99;">Presioná ESCANEAR AHORA</div>
          <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#2a3a55;margin-top:6px;">4 filtros · todos los activos · señal clara en segundos</div>
        </div>""", unsafe_allow_html=True)

    # ── SCRIPT LUA (colapsado) ──────────────────────────────────
    with st.expander("📥 Script Lua HECTOR 1 para IQ Option", expanded=False):
        st.markdown('<div class="sec">HECTOR 1 — TRIPLE CONFIRM (overlay)</div>', unsafe_allow_html=True)
        script_h1_inline = '''instrument {
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

rsi14 = rsi(close, 14)

p_e5   = plot("EMA5",  "yellow", 1, "line")
p_e13  = plot("EMA13", "cyan",   1, "line")
p_e50  = plot("EMA50", "gray",   1, "line")
p_call = plot("CALL",  "lime",   3, "arrow_up")
p_put  = plot("PUT",   "red",    3, "arrow_down")
p_warn_c = plot("PREP+", "orange", 1, "circles")
p_warn_p = plot("PREP-", "orange", 1, "circles")

f1c = e5[0] > e13[0] and e13[0] > e50[0]
f2c = macd_hist[0] > 0
f3c = rsi14[0] > 45 and rsi14[0] < 75
f4c = close[0] > open[0]

f1p = e5[0] < e13[0] and e13[0] < e50[0]
f2p = macd_hist[0] < 0
f3p = rsi14[0] > 25 and rsi14[0] < 55
f4p = close[0] < open[0]

nc = (f1c and 1 or 0) + (f2c and 1 or 0) + (f3c and 1 or 0) + (f4c and 1 or 0)
np = (f1p and 1 or 0) + (f2p and 1 or 0) + (f3p and 1 or 0) + (f4p and 1 or 0)

p_e5:set(e5[0])
p_e13:set(e13[0])
p_e50:set(e50[0])

if nc == 4 then p_call:set(low[0]) end
if np == 4 then p_put:set(high[0]) end
if nc == 3 then p_warn_c:set(low[0]) end
if np == 3 then p_warn_p:set(high[0]) end'''
        st.markdown(f'<div class="code-block">{script_h1_inline}</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#0a1a3a;border:1px solid #2563eb;border-radius:8px;padding:12px;font-size:13px;color:#60a5fa;line-height:1.8;">
          <strong>Instalar en IQ Option:</strong> Editor de indicadores → Nuevo → Pegar código → Guardar → Aplicar en M1<br>
          <strong>Flecha grande:</strong> 4/4 filtros = entrar · <strong>Círculo naranja:</strong> 3/4 = prepararse
        </div>
        """, unsafe_allow_html=True)


# ================================================================
# TAB 4 — NOTICIAS DE MERCADO CON IA
# ================================================================
with tab_noticias:

    st.markdown("""
    <div style="background:linear-gradient(135deg,#0d1525 0%,#1a0d25 100%);border:1px solid #7c3aed;border-radius:14px;padding:18px 22px;margin-bottom:18px;">
      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:26px;color:#a78bfa;letter-spacing:1px;">📰 NOTICIAS &amp; IMPACTO EN MERCADO</div>
      <div style="font-family:Share Tech Mono,monospace;font-size:12px;color:#4a7a99;margin-top:4px;">
        IA analiza noticias → probabilidad de suba/baja → CALL/PUT sugerido
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SELECTOR DE CATEGORIA ───────────────────────────────────
    cat_col1, cat_col2, cat_col3 = st.columns(3)
    with cat_col1:
        noticias_activo = st.selectbox("Activo a analizar", [
            "XAU/USD (Oro)", "WTI Crude Oil (Petróleo)", "Natural Gas",
            "BTC/USD (Bitcoin)", "ETH/USD (Ethereum)",
            "EUR/USD", "GBP/USD",
            "Mercado general"
        ], key="not_activo")
    with cat_col2:
        noticias_periodo = st.selectbox("Período de noticias", [
            "Últimas 24 horas", "Últimas 48 horas", "Esta semana"
        ], key="not_periodo")
    with cat_col3:
        noticias_idioma = st.selectbox("Idioma análisis IA", ["Español", "English"], key="not_idioma")

    # ── BOTÓN ANALIZAR ──────────────────────────────────────────
    # ── IMAGEN DESDE PORTAPAPELES ──────────────────────────────
    with st.expander("📸 Pegar imagen del gráfico (portapapeles / captura)", expanded=False):
        st.markdown("""
        <div style="background:rgba(168,85,247,0.08);border:1px solid #a855f7;border-radius:10px;
             padding:12px 16px;margin-bottom:10px;font-family:'Share Tech Mono',monospace;font-size:11px;color:#c084fc;">
          📱 <b>iPhone/Android:</b> Capturá el gráfico → guardá → cargá desde Archivos<br>
          💻 <b>Desktop:</b> Capturá con Win+Shift+S → guardá → subí acá
        </div>
        """, unsafe_allow_html=True)
        img_uploaded = st.file_uploader(
            "Subir imagen del gráfico para análisis IA",
            type=["png","jpg","jpeg","webp"],
            key="img_grafico_noticias",
            label_visibility="collapsed"
        )
        if img_uploaded:
            import base64 as b64mod
            st.image(img_uploaded, caption="Gráfico cargado — la IA lo analizará junto con las noticias", use_column_width=True)
            st.session_state["img_grafico_b64"] = b64mod.b64encode(img_uploaded.read()).decode()
            st.session_state["img_grafico_type"] = img_uploaded.type
            st.success("✅ Imagen lista — hacé clic en ANALIZAR CON IA")
        elif st.session_state.get("img_grafico_b64"):
            st.info("📊 Imagen del scan anterior cargada. Subí una nueva o continuá.")
            if st.button("🗑 Borrar imagen", key="del_img_not"):
                st.session_state.pop("img_grafico_b64", None)
                st.rerun()

    not_btn = st.button("🤖 ANALIZAR CON IA", key="noticias_btn", use_container_width=True)

    # ── CALENDARIO ECONÓMICO ESTÁTICO ──────────────────────────
    st.markdown('<div class="sec">📅 PRÓXIMOS EVENTOS DE ALTO IMPACTO</div>', unsafe_allow_html=True)

    hoy = get_fecha_arg()

    calendario_eventos = [
        {"dia": "Lunes", "evento": "PMI Manufacturero EE.UU.", "impacto": "ALTO", "activos": "EUR/USD, US 500, US 30", "color": "#dc2626"},
        {"dia": "Miércoles", "evento": "Inventarios de Crudo EIA", "impacto": "ALTO", "activos": "WTI Crude Oil, Brent", "color": "#dc2626"},
        {"dia": "Miércoles", "evento": "Actas Fed (FOMC)", "impacto": "MUY ALTO", "activos": "EUR/USD, GBP/USD, Oro, Indices", "color": "#7f1d1d"},
        {"dia": "Jueves", "evento": "Solicitudes de desempleo EE.UU.", "impacto": "MEDIO", "activos": "EUR/USD, US 100", "color": "#c8920a"},
        {"dia": "Viernes", "evento": "NFP — Nóminas no agrícolas", "impacto": "MUY ALTO", "activos": "TODOS LOS ACTIVOS", "color": "#7f1d1d"},
        {"dia": "Variable", "evento": "Reunión OPEP / Producción", "impacto": "ALTO", "activos": "WTI, Brent, USD", "color": "#dc2626"},
        {"dia": "Variable", "evento": "CPI Inflación EE.UU.", "impacto": "MUY ALTO", "activos": "Oro, EUR/USD, Indices", "color": "#7f1d1d"},
    ]

    cal_html = '<div style="display:grid;gap:8px;">'
    for ev in calendario_eventos:
        cal_html += f"""
        <div style="background:#0d1525;border-left:4px solid {ev['color']};border-radius:0 8px 8px 0;padding:10px 14px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;">
          <div>
            <span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:16px;color:#c8d8e8;">{ev['evento']}</span>
            <span style="font-family:Share Tech Mono,monospace;font-size:10px;color:{ev['color']};margin-left:10px;">{ev['impacto']}</span>
          </div>
          <div style="text-align:right;">
            <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#4a7a99;">{ev['dia']}</div>
            <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#60a5fa;">{ev['activos']}</div>
          </div>
        </div>"""
    cal_html += "</div>"
    st.markdown(cal_html, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#1a0a0a;border:1px solid #dc2626;border-radius:8px;padding:10px 14px;margin:10px 0;font-family:Share Tech Mono,monospace;font-size:12px;color:#f87171;">
      ⛔ REGLA: No operar 15 minutos ANTES ni 15 minutos DESPUÉS de un evento de ALTO impacto.
      El precio puede moverse erráticamente en ambas direcciones.
    </div>
    """, unsafe_allow_html=True)

    # ── ANÁLISIS IA ─────────────────────────────────────────────
    st.markdown('<div class="sec">🤖 ANÁLISIS IA — IMPACTO EN PRECIO</div>', unsafe_allow_html=True)

    if not_btn:
        if not st.session_state.get("ia_ok", False) and not get_ia_ok():
            st.warning("⚠ Configurá tu API Key de Anthropic en la barra lateral para usar análisis IA.")
        else:
            idioma_prompt = "spanish" if noticias_idioma == "Español" else "english"
            prompt_noticias = f"""You are an expert financial market analyst specializing in commodities, forex, crypto and macroeconomics.

The user wants to analyze: {noticias_activo} — news impact for {noticias_periodo}.

Respond ONLY in {idioma_prompt}.

Your response must be structured EXACTLY as JSON (no markdown, no extra text):
{{
  "activo": "name of asset",
  "tendencia": "ALCISTA" or "BAJISTA" or "NEUTRAL",
  "probabilidad_suba": number 0-100,
  "probabilidad_baja": number 0-100,
  "señal": "CALL" or "PUT" or "NO OPERAR",
  "confianza": number 0-100,
  "resumen": "2-3 sentence summary of key news drivers in {idioma_prompt}",
  "noticias": [
    {{
      "titulo": "news headline",
      "impacto": "ALCISTA" or "BAJISTA" or "NEUTRO",
      "descripcion": "1-2 sentence explanation of why this moves the price",
      "fuente": "Reuters/Bloomberg/Fed/OPEP/etc"
    }}
  ],
  "drivers": [
    "key driver 1",
    "key driver 2", 
    "key driver 3"
  ],
  "riesgo": "LOW" or "MEDIUM" or "HIGH",
  "invalidacion": "What would invalidate this analysis",
  "horizonte": "timeframe of this analysis"
}}

For {noticias_activo}, consider these specific factors:
- If Gold/XAU: geopolitical tensions, Fed rates, USD strength, inflation data, war/conflict news
- If Oil/WTI/Brent: OPEP decisions, US inventories EIA, Middle East conflicts, demand from China
- If Bitcoin/ETH: whale movements (large wallet transfers), exchange flows, regulatory news, ETF flows
- If EUR/USD GBP/USD: ECB/Fed policy divergence, economic data, political events
- Natural Gas: weather forecasts, storage levels, LNG exports
- General: use current macro environment

Be specific and realistic. Base analysis on what typically moves {noticias_activo} in {noticias_periodo}.
"""

            with st.spinner("🤖 Analizando noticias con IA..."):
                try:
                    import requests as req_not
                    resp_not = req_not.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={
                            "Content-Type": "application/json",
                            "x-api-key": st.session_state.api_key,
                            "anthropic-version": "2023-06-01"
                        },
                        json={
                            "model": "claude-sonnet-4-20250514",
                            "max_tokens": 1500,
                            "messages": [{
                                "role": "user",
                                "content": (
                                    [
                                        {"type": "image", "source": {
                                            "type": "base64",
                                            "media_type": st.session_state.get("img_grafico_type","image/png"),
                                            "data": st.session_state["img_grafico_b64"]
                                        }},
                                        {"type": "text", "text": prompt_noticias + "\n\nAdemás analiza el gráfico adjunto e incorpora lo que ves (tendencia, niveles clave, patrones) en tu análisis."}
                                    ] if st.session_state.get("img_grafico_b64") else prompt_noticias
                                )
                            }]
                        },
                        timeout=30
                    )
                    if resp_not.status_code != 200:
                        st.error(f"Error API ({resp_not.status_code}): {resp_not.text[:200]}")
                        st.session_state["noticias_analisis"] = None
                    else:
                        data_not = resp_not.json()
                        raw_not  = data_not["content"][0]["text"].strip()
                        raw_not  = raw_not.replace("```json", "").replace("```", "").strip()
                        import json as json_mod
                        an       = json_mod.loads(raw_not)
                        st.session_state["noticias_analisis"] = an
                        st.session_state["noticias_activo_sel"] = noticias_activo
                except Exception as e_not:
                    st.error(f"Error en análisis IA: {e_not}")
                    st.session_state["noticias_analisis"] = None

        st.rerun()

    # ── MOSTRAR ANÁLISIS ─────────────────────────────────────────
    if st.session_state.get("noticias_analisis"):
        an = st.session_state["noticias_analisis"]
        activo_sel = st.session_state.get("noticias_activo_sel", "")

        tend_color = {"ALCISTA": "#4ade80", "BAJISTA": "#f87171", "NEUTRAL": "#94a3b8"}.get(an.get("tendencia",""), "#94a3b8")
        senal_color = {"CALL": "#4ade80", "PUT": "#f87171", "NO OPERAR": "#94a3b8"}.get(an.get("señal",""), "#94a3b8")
        _ic_ia = '🔺' if an.get('señal')=='CALL' else ('🔻' if an.get('señal')=='PUT' else '⏸')
        senal_bg = {"CALL": "#041a0c", "PUT": "#1a0404", "NO OPERAR": "#0d1525"}.get(an.get("señal",""), "#0d1525")
        riesgo_color = {"LOW": "#4ade80", "MEDIUM": "#ff9800", "HIGH": "#f87171"}.get(an.get("riesgo",""), "#94a3b8")

        prob_suba = an.get("probabilidad_suba", 50)
        prob_baja = an.get("probabilidad_baja", 50)
        conf      = an.get("confianza", 50)

        # TARJETA PRINCIPAL — DECISIÓN RÁPIDA
        st.markdown(f"""
        <div style="background:{senal_bg};border:2px solid {senal_color};border-radius:14px;padding:22px;margin-bottom:16px;">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:16px;">
            <div>
              <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:28px;color:#c8d8e8;">{activo_sel}</div>
              <div style="font-family:Share Tech Mono,monospace;font-size:12px;color:{tend_color};margin-top:4px;">TENDENCIA: {an.get('tendencia','')}</div>
            </div>
            <div style="display:flex;gap:14px;align-items:center;flex-wrap:wrap;">
              <div style="text-align:center;background:#060c18;border:2px solid {senal_color};border-radius:12px;padding:14px 24px;">
                <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:36px;color:{senal_color};">{_ic_ia} {an.get('señal','')}</div>
                <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#4a7a99;">SEÑAL IA</div>
              </div>
              <div style="text-align:center;background:#060c18;border:1px solid #1e3050;border-radius:10px;padding:10px 16px;">
                <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:28px;color:{senal_color};">{conf}%</div>
                <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;">CONFIANZA</div>
              </div>
            </div>
          </div>

          <!-- BARRAS DE PROBABILIDAD -->
          <div style="margin-bottom:14px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
              <span style="font-family:Share Tech Mono,monospace;font-size:12px;color:#4ade80;">🔺 SUBE {prob_suba}%</span>
              <span style="font-family:Share Tech Mono,monospace;font-size:12px;color:#f87171;">🔻 BAJA {prob_baja}%</span>
            </div>
            <div style="background:#060c18;border-radius:6px;overflow:hidden;height:14px;position:relative;">
              <div style="position:absolute;left:0;top:0;height:100%;width:{prob_suba}%;background:linear-gradient(90deg,#16a34a,#4ade80);border-radius:6px;"></div>
            </div>
            <div style="background:#060c18;border-radius:6px;overflow:hidden;height:14px;margin-top:4px;position:relative;">
              <div style="position:absolute;left:0;top:0;height:100%;width:{prob_baja}%;background:linear-gradient(90deg,#dc2626,#f87171);border-radius:6px;"></div>
            </div>
          </div>

          <div style="font-size:14px;color:#94a3b8;line-height:1.7;border-top:1px solid #1e3050;padding-top:12px;">{an.get('resumen','')}</div>
        </div>
        """, unsafe_allow_html=True)

        # NOTICIAS INDIVIDUALES
        noticias_list = an.get("noticias", [])
        if noticias_list:
            st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#7c3aed;letter-spacing:2px;margin-bottom:8px;">📰 NOTICIAS ANALIZADAS</div>', unsafe_allow_html=True)
            for noticia in noticias_list:
                imp = noticia.get("impacto", "NEUTRO")
                imp_col = {"ALCISTA": "#4ade80", "BAJISTA": "#f87171", "NEUTRO": "#94a3b8"}.get(imp, "#94a3b8")
                imp_bg  = {"ALCISTA": "#041a0c", "BAJISTA": "#1a0404", "NEUTRO": "#0d1525"}.get(imp, "#0d1525")
                imp_ic  = {"ALCISTA": "🔺", "BAJISTA": "🔻", "NEUTRO": "➡"}.get(imp, "")
                st.markdown(f"""
                <div style="background:{imp_bg};border:1px solid {imp_col};border-radius:10px;padding:12px 16px;margin-bottom:8px;">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:6px;">
                    <div style="flex:1;">
                      <span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:16px;color:#c8d8e8;">{noticia.get('titulo','')}</span>
                      <span style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;margin-left:10px;">{noticia.get('fuente','')}</span>
                    </div>
                    <span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:14px;color:{imp_col};">{imp_ic} {imp}</span>
                  </div>
                  <div style="font-size:13px;color:#94a3b8;margin-top:6px;line-height:1.6;">{noticia.get('descripcion','')}</div>
                </div>""", unsafe_allow_html=True)

        # DRIVERS + RIESGO + INVALIDACION
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            drivers = an.get("drivers", [])
            if drivers:
                st.markdown(f"""
                <div style="background:#0d1525;border:1px solid #7c3aed;border-radius:10px;padding:14px;">
                  <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#7c3aed;margin-bottom:8px;letter-spacing:1px;">🎯 DRIVERS CLAVE</div>
                  {''.join([f'<div style="font-size:13px;color:#c8d8e8;padding:4px 0;border-bottom:1px solid #1e3050;">▸ {d}</div>' for d in drivers])}
                </div>""", unsafe_allow_html=True)
        with col_d2:
            st.markdown(f"""
            <div style="background:#0d1525;border:1px solid {riesgo_color};border-radius:10px;padding:14px;">
              <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#4a7a99;margin-bottom:8px;letter-spacing:1px;">⚠ RIESGO &amp; INVALIDACIÓN</div>
              <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:20px;color:{riesgo_color};margin-bottom:8px;">RIESGO {an.get('riesgo','')}</div>
              <div style="font-size:13px;color:#94a3b8;line-height:1.6;">{an.get('invalidacion','')}</div>
              <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#4a7a99;margin-top:8px;">Horizonte: {an.get('horizonte','')}</div>
            </div>""", unsafe_allow_html=True)

        # ENVIAR A TELEGRAM
        if st.session_state.tg_on and st.session_state.tg_token:
            if st.button("📱 Enviar análisis a Telegram", key="not_tg_btn"):
                senal_ic = "🔺" if an.get("señal") == "CALL" else "🔻" if an.get("señal") == "PUT" else "⏸"
                msg_not = (f"📰 <b>ANÁLISIS IA — {activo_sel}</b>\n"
                           f"━━━━━━━━━━━━━━\n"
                           f"{senal_ic} <b>{an.get('señal','')} — {an.get('tendencia','')}</b>\n"
                           f"🎯 Confianza: {conf}%\n"
                           f"🔺 Prob. suba: {prob_suba}% | 🔻 Prob. baja: {prob_baja}%\n"
                           f"⚠ Riesgo: {an.get('riesgo','')}\n\n"
                           f"📝 {an.get('resumen','')}\n\n"
                           f"<i>QQE Command v10 — Noticias IA</i>")
                ok_not = enviar_telegram(st.session_state.tg_token, st.session_state.tg_chat, msg_not)
                if ok_not:
                    st.success("✅ Enviado a Telegram")

    else:
        # Estado inicial
        st.markdown("""
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-top:16px;">
          <div style="background:#0d1525;border:1px solid #fbbf24;border-radius:12px;padding:18px;text-align:center;">
            <div style="font-size:32px;margin-bottom:8px;">🥇</div>
            <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:16px;color:#fbbf24;">ORO (XAU/USD)</div>
            <div style="font-size:12px;color:#94a3b8;margin-top:6px;line-height:1.6;">
              Se mueve con: tensiones geopolíticas, decisiones Fed, inflación, fortaleza del USD, conflictos armados
            </div>
          </div>
          <div style="background:#0d1525;border:1px solid #60a5fa;border-radius:12px;padding:18px;text-align:center;">
            <div style="font-size:32px;margin-bottom:8px;">🛢️</div>
            <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:16px;color:#60a5fa;">PETRÓLEO (WTI)</div>
            <div style="font-size:12px;color:#94a3b8;margin-top:6px;line-height:1.6;">
              Se mueve con: inventarios EIA (miércoles), reuniones OPEP, conflictos Golfo Pérsico, demanda China
            </div>
          </div>
          <div style="background:#0d1525;border:1px solid #fb923c;border-radius:12px;padding:18px;text-align:center;">
            <div style="font-size:32px;margin-bottom:8px;">🐋</div>
            <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:16px;color:#fb923c;">CRYPTO BALLENAS</div>
            <div style="font-size:12px;color:#94a3b8;margin-top:6px;line-height:1.6;">
              Se mueve con: transferencias masivas a exchanges (presión venta), ETF flows, regulaciones, noticias de adoptción
            </div>
          </div>
        </div>
        <div style="text-align:center;padding:24px;margin-top:10px;">
          <div style="font-family:Share Tech Mono,monospace;font-size:12px;color:#4a7a99;">Seleccioná un activo y hacé clic en 🤖 ANALIZAR CON IA</div>
        </div>
        """, unsafe_allow_html=True)

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
    _monto_default = max(1.0, round(capital*0.02, 2))
    with c4: monto_op = st.number_input("Monto $", min_value=1.0, value=_monto_default, step=1.0, key="op_monto")
    with c5: res_op = st.selectbox("Result", ["WIN","LOSS","—"], key="op_res")
    with c6: pnl_op = st.number_input("P&L $", value=0.0, step=1.0, key="op_pnl")

    if st.button("REGISTRAR", key="op_reg", use_container_width=True):
        if res_op != "—":
            pnl_final = abs(pnl_op) if res_op=="WIN" else -abs(monto_op if pnl_op==0 else pnl_op)
            st.session_state.ops.append({
                "fecha": get_fecha_arg().strftime("%d/%m"), "hora": datetime.now(TZ_ARG).strftime("%H:%M"),
                "activo": act_op, "dir": dir_op, "tipo": tipo_op,
                "monto": monto_op, "resultado": res_op, "pnl": pnl_final,
            })
            if res_op == "LOSS":
                st.session_state.perdida_dia += abs(pnl_final)
                st.session_state.racha_losses += 1
                st.session_state.max_racha_dia = max(
                    st.session_state.max_racha_dia,
                    st.session_state.racha_losses
                )
                # REGLA: 2 pérdidas consecutivas = bloqueo automático
                if st.session_state.racha_losses >= 2:
                    st.session_state.radar_bloqueado = True
                    if st.session_state.tg_on and st.session_state.tg_token:
                        enviar_telegram(st.session_state.tg_token, st.session_state.tg_chat,
                            f"🛑 <b>STOP — 2 PÉRDIDAS CONSECUTIVAS</b>\n"
                            f"Regla HECTOR: detener operaciones por hoy.\n"
                            f"Pérdida del día: ${st.session_state.perdida_dia:.2f}\n"
                            f"<i>QQE Command v10</i>")
            else:
                # WIN resetea racha
                st.session_state.racha_losses = 0
            # Stop loss diario
            sl_monto_check = st.session_state.capital * (st.session_state.stop_loss_dia / 100)
            if st.session_state.perdida_dia >= sl_monto_check:
                st.session_state.radar_bloqueado = True
            st.rerun()

    if st.session_state.ops:
        st.markdown('<div class="sec">HISTORIAL</div>', unsafe_allow_html=True)
        for o in reversed(st.session_state.ops[-20:]):
            pnl_c = "#4ade80" if o["pnl"]>0 else "#f87171"
            ic_r = "✅" if o["resultado"]=="WIN" else "❌"
            ic_d = "▲" if o["dir"]=="CALL" else "▼"
            _col_dir = "#4ade80" if o["dir"]=="CALL" else "#f87171"
            st.markdown(f"""
            <div class="asset-row" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;">
              <div>
                <span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:16px;color:#c8d8e8;">{o['activo']}</span>
                <span style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;margin-left:8px;">{o['tipo']}</span>
                <span style="font-family:Share Tech Mono,monospace;font-size:10px;color:{_col_dir};margin-left:8px;">{ic_d} {o['dir']}</span>
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
    st.markdown('<div class="sec">📓 BITACORA DE TRADING — DESCARGA Y TELEGRAM</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([3,1])
    with c1:
        nota_txt = st.text_area("Nueva entrada", height=100, placeholder="Anotá tu analisis, aprendizaje, estado emocional...", key="diario_txt", label_visibility="collapsed")
    with c2:
        nota_tipo = st.selectbox("Tipo", ["📊 Analisis","💡 Aprendizaje","😤 Gestion Emocional","🎯 Estrategia","📰 Noticias"], key="diario_tipo")
        if st.button("GUARDAR", key="diario_save", use_container_width=True):
            if nota_txt.strip():
                st.session_state.diario.append({
                    "fecha": get_fecha_arg().strftime("%d/%m/%Y"),
                    "hora":  datetime.now(TZ_ARG).strftime("%H:%M"),
                    "tipo":  nota_tipo, "activo": "—", "texto": nota_txt, "tf": "—"
                })
                st.rerun()

    # ── EXPORTAR BITACORA ────────────────────────────────────────
    if st.session_state.diario:
        df_diario = pd.DataFrame(st.session_state.diario)
        csv_diario = df_diario.to_csv(index=False).encode("utf-8")

        st.markdown("---")
        st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#c8920a;letter-spacing:2px;margin-bottom:8px;">EXPORTAR BITACORA</div>', unsafe_allow_html=True)
        col_exp1, col_exp2, col_exp3 = st.columns(3)
        with col_exp1:
            st.download_button(
                "⬇ Descargar CSV",
                csv_diario,
                file_name=f"bitacora_hector_{get_fecha_arg().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
                key="dl_bitacora_csv"
            )
        with col_exp2:
            # Descargar como TXT legible
            txt_lines = [f"BITACORA HECTOR — {get_fecha_arg().strftime('%d/%m/%Y')}", "="*40]
            for e in st.session_state.diario:
                txt_lines.append(f"\n{e.get('fecha','?')} {e.get('hora','?')} | {e.get('tipo','?')} | {e.get('activo','?')} {e.get('tf','')}")
                txt_lines.append(e.get('texto',''))
                txt_lines.append("-"*30)
            txt_export = "\n".join(txt_lines).encode("utf-8")
            st.download_button(
                "⬇ Descargar TXT",
                txt_export,
                file_name=f"bitacora_hector_{get_fecha_arg().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True,
                key="dl_bitacora_txt"
            )
        with col_exp3:
            if st.button("📤 Enviar a Telegram", key="diario_tg_export", use_container_width=True):
                if st.session_state.tg_token:
                    # Enviar las últimas 5 entradas
                    ultimas = st.session_state.diario[-5:]
                    msg_tg = f"📓 <b>BITACORA HECTOR — {get_fecha_arg().strftime('%d/%m/%Y')}</b>\n"
                    msg_tg += f"━━━━━━━━━━━━━━\n"
                    msg_tg += f"Total registros: {len(st.session_state.diario)}\n\n"
                    msg_tg += "<b>Ultimas 5 entradas:</b>\n"
                    for e in reversed(ultimas):
                        msg_tg += f"\n🕐 {e.get('hora','?')} | {e.get('tipo','?')} | {e.get('activo','?')}\n"
                        msg_tg += e.get('texto','')[:200] + ("..." if len(e.get('texto','')) > 200 else "") + "\n"
                    msg_tg += f"\n<i>QQE Command v10 — Goya, Corrientes</i>"
                    ok = enviar_telegram(st.session_state.tg_token, st.session_state.tg_chat, msg_tg[:4000])
                    if ok: st.success("Bitacora enviada a Telegram!")
                    else:  st.error("Error — verificar token y chat ID en sidebar")
                else:
                    st.warning("Configurar Telegram en el sidebar primero")
        st.markdown("---")

        # ── ENTRADAS ─────────────────────────────────────────────
        st.markdown(f'<div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a7a99;letter-spacing:2px;margin-bottom:8px;">REGISTROS ({len(st.session_state.diario)} total)</div>', unsafe_allow_html=True)
        for e in reversed(st.session_state.diario[-30:]):
            st.markdown(f"""
            <div class="diario-entry">
              <div class="diario-meta">{e.get('fecha','?')} {e.get('hora','?')} · {e.get('tipo','—')} · {e.get('activo','—')} {e.get('tf','')}</div>
              <div style="font-size:14px;color:#c8d8e8;line-height:1.8;">{e.get('texto','').replace(chr(10),'<br>')}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align:center;padding:40px;color:#4a7a99;font-family:Share Tech Mono,monospace;font-size:11px;">Sin entradas aun. Guardá tu primera nota arriba.</div>', unsafe_allow_html=True)

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
# TAB: BACKTEST
# ================================================================
with tab_backtest:
    st.markdown('<div class="sec">📊 BACKTESTING QQE — ESTADÍSTICAS AVANZADAS</div>', unsafe_allow_html=True)

    bt_c1, bt_c2 = st.columns([1, 2])
    with bt_c1:
        st.markdown('<div style="background:#0a1020;border:1px solid #1a2a45;border-left:4px solid #f0b429;border-radius:12px;padding:18px;margin-bottom:12px;">', unsafe_allow_html=True)
        bt_act_key = st.selectbox("Activo", list(ACTIVOS.keys()), key="bt_act")
        bt_iv      = st.selectbox("Intervalo", ["5m","15m","1h","4h","1d"], index=2, key="bt_iv")
        bt_cap     = st.number_input("Capital $", 50.0, 100000.0, value=float(st.session_state.capital), step=10.0, key="bt_cap")
        bt_rsk     = st.slider("Riesgo por trade %", 0.5, 5.0, 1.0, step=0.5, key="bt_rsk")
        st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#f0b429;letter-spacing:2px;margin:12px 0 8px;">PARÁMETROS QQE</div>', unsafe_allow_html=True)
        bt_rsi_p = st.slider("RSI Period",    5,  30, 14, step=1,   key="bt_rsi_p")
        bt_sf    = st.slider("Smooth Factor", 2,  20,  5, step=1,   key="bt_sf")
        bt_qf    = st.slider("QQE Factor",    1.0, 10.0, 4.238, step=0.1, key="bt_qf", format="%.2f")
        bt_thr   = st.slider("RSI Threshold", 0.5, 10.0, 3.0, step=0.5, key="bt_thr")
        btn_bt   = st.button("▶ CORRER BACKTEST", key="bt_run", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with bt_c2:
        if btn_bt:
            with st.spinner("Calculando señales QQE..."):
                _ticker = ACTIVOS[bt_act_key]["yahoo"]
                _df_raw = obtener_datos(_ticker, period="60d", interval=bt_iv)
                if _df_raw is None or len(_df_raw) < 40:
                    st.error("Sin datos suficientes. Probá otro intervalo o activo.")
                else:
                    _df_q  = calc_qqe_engine(_df_raw, bt_rsi_p, bt_sf, bt_qf, bt_thr)
                    _bt    = run_backtest_v11(_df_q, bt_cap, bt_rsk)
                    st.session_state["bt_result_v11"] = _bt
                    st.session_state["bt_act_used"]   = bt_act_key

        if "bt_result_v11" in st.session_state:
            _r = st.session_state["bt_result_v11"]
            _s = _r.get("stats", {})
            if _s:
                _wr_col  = "#22c55e" if _s["win_rate"]>=55 else ("#f0b429" if _s["win_rate"]>=45 else "#ef4444")
                _pf_col  = "#22c55e" if _s["profit_factor"]>=1.5 else ("#f0b429" if _s["profit_factor"]>=1.0 else "#ef4444")
                _gan_col = "#22c55e" if _s["total_ganancia"]>=0 else "#ef4444"

                k1,k2,k3,k4 = st.columns(4)
                with k1: _kpi_v11("WIN RATE", f"{_s['win_rate']}%", f"{_s['wins']}W / {_s['losses']}L", _wr_col)
                with k2: _kpi_v11("PROFIT FACTOR", str(_s["profit_factor"]), "bruto/pérdida", _pf_col)
                with k3: _kpi_v11("GANANCIA TOTAL", f"${_s['total_ganancia']:+.2f}", f"cap: ${_s['capital_final']:.2f}", _gan_col)
                with k4: _kpi_v11("MAX DRAWDOWN", f"${_s['max_drawdown']:.2f}", "peor racha", "#ef4444")

                k5,k6,k7,k8 = st.columns(4)
                with k5: _kpi_v11("RR RATIO", f"{_s['rr_ratio']:.2f}x", "win/loss prom", "#60a5fa")
                with k6: _kpi_v11("TOTAL TRADES", str(_s["total_trades"]), bt_iv, "#c8d8e8")
                with k7: _kpi_v11("RACHA WIN", str(_s["racha_win"]), "seguidas ganadas", "#22c55e")
                with k8: _kpi_v11("RACHA LOSS", str(_s["racha_loss"]), "seguidas perdidas", "#ef4444")

                # Barras visuales
                _bc1, _bc2 = st.columns(2)
                with _bc1:
                    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;margin:12px 0 4px;">WIN RATE</div>', unsafe_allow_html=True)
                    _progbar(_s["win_rate"], "#22c55e")
                    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;margin:8px 0 4px;">PROFIT FACTOR (escala x10)</div>', unsafe_allow_html=True)
                    _progbar(min(100, _s["profit_factor"]*10), "#f0b429")
                with _bc2:
                    _tot_wr = (_s["avg_win"] + _s["avg_loss"]) or 1
                    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;margin:12px 0 4px;">WIN PROM vs LOSS PROM</div>', unsafe_allow_html=True)
                    _progbar(_s["avg_win"]/_tot_wr*100, "#22c55e")
                    st.caption(f"WIN prom: ${_s['avg_win']:.2f}  |  LOSS prom: ${_s['avg_loss']:.2f}")

                # Curva de capital
                _trades = _r.get("trades", [])
                if _trades:
                    st.markdown('<div class="sec">CURVA DE CAPITAL</div>', unsafe_allow_html=True)
                    _cap_curve = [bt_cap]
                    for _t in _trades:
                        _cap_curve.append(_cap_curve[-1] + _t["ganancia"])
                    st.line_chart(pd.DataFrame({"Capital": _cap_curve}), color="#f0b429")

                    # Tabla de trades
                    st.markdown('<div class="sec">TABLA DE OPERACIONES (últimas 30)</div>', unsafe_allow_html=True)
                    _tbl = pd.DataFrame(_trades[-30:]).copy()
                    _tbl["ganancia"] = _tbl["ganancia"].apply(lambda x: f"${x:+.2f}")
                    _tbl["pnl_pct"]  = _tbl["pnl_pct"].apply(lambda x: f"{x:+.2f}%")
                    st.dataframe(_tbl[["fecha","senal","calidad","entrada","salida","pnl_pct","ganancia","resultado"]],
                                 use_container_width=True, hide_index=True)
            else:
                st.warning("Sin señales en el período. Probá un intervalo mayor o ajustá los parámetros QQE.")
        else:
            st.markdown("""<div style="text-align:center;padding:60px;background:#0a1020;border:2px dashed #1a2a45;border-radius:14px;">
              <div style="font-size:48px;margin-bottom:12px;">📊</div>
              <div style="font-family:Rajdhani,sans-serif;font-size:22px;color:#4a7a99;">Ajustá los parámetros y presioná ▶ CORRER BACKTEST</div>
              <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#2a3a55;margin-top:6px;">Win Rate · Profit Factor · Drawdown · RR Ratio · Curva de capital</div>
            </div>""", unsafe_allow_html=True)

# ================================================================
# TAB: SIMULACIÓN
# ================================================================
with tab_sim:
    st.markdown('<div class="sec">🔮 SIMULACIÓN DE ESCENARIOS — ÚLTIMAS N SEÑALES</div>', unsafe_allow_html=True)

    sim_c1, sim_c2 = st.columns([1, 2])
    with sim_c1:
        sim_act = st.selectbox("Activo", list(ACTIVOS.keys()), key="sim_act")
        sim_iv  = st.selectbox("Intervalo", ["5m","15m","1h","4h"], index=2, key="sim_iv")
        sim_n   = st.slider("Últimas N señales a simular", 5, 30, 15, key="sim_n")
        sim_cap = st.number_input("Capital simulado $", 50.0, 10000.0, value=float(st.session_state.capital), step=10.0, key="sim_cap")
        sim_rsk = st.slider("Riesgo %", 0.5, 5.0, 1.0, step=0.5, key="sim_rsk")
        btn_sim = st.button("🔮 SIMULAR AHORA", key="sim_run", use_container_width=True)

    with sim_c2:
        if btn_sim:
            with st.spinner("Simulando..."):
                _t_sim = ACTIVOS[sim_act]["yahoo"]
                _d_sim = obtener_datos(_t_sim, period="60d", interval=sim_iv)
                if _d_sim is None or len(_d_sim) < 40:
                    st.error("Sin datos para simular.")
                else:
                    _dq_sim = calc_qqe_engine(_d_sim)
                    _sr     = run_backtest_v11(_dq_sim, sim_cap, sim_rsk)
                    st.session_state["sim_result_v11"] = _sr
                    st.session_state["sim_n_v11"]      = sim_n
                    st.session_state["sim_cap_v11"]    = sim_cap

        if "sim_result_v11" in st.session_state:
            _sr2     = st.session_state["sim_result_v11"]
            _n2      = st.session_state.get("sim_n_v11", 15)
            _cap2    = st.session_state.get("sim_cap_v11", sim_cap)
            _all_t   = _sr2.get("trades", [])
            _trades2 = _all_t[-_n2:] if len(_all_t) >= _n2 else _all_t

            if not _trades2:
                st.warning("Sin señales en el período seleccionado.")
            else:
                _sw2   = [t for t in _trades2 if t["resultado"]=="WIN"]
                _sl2   = [t for t in _trades2 if t["resultado"]=="LOSS"]
                _sg2   = sum(t["ganancia"] for t in _trades2)
                _swr2  = len(_sw2)/len(_trades2)*100
                _swr_c = "#22c55e" if _swr2>=55 else ("#f0b429" if _swr2>=45 else "#ef4444")
                _sg_c  = "#22c55e" if _sg2>=0 else "#ef4444"

                sa,sb,sc2,sd = st.columns(4)
                with sa: _kpi_v11("TRADES SIM", str(len(_trades2)), f"últimas {_n2}", "#c8d8e8")
                with sb: _kpi_v11("WIN RATE", f"{_swr2:.1f}%", f"{len(_sw2)}W/{len(_sl2)}L", _swr_c)
                with sc2: _kpi_v11("GANANCIA", f"${_sg2:+.2f}", f"desde ${_cap2:.0f}", _sg_c)
                with sd: _kpi_v11("CAPITAL FINAL", f"${_cap2+_sg2:.2f}", "hipotético", _sg_c)

                st.markdown('<div class="sec">OPERACIONES DE LA SIMULACIÓN</div>', unsafe_allow_html=True)
                for _t2 in reversed(_trades2):
                    _ct2 = "#22c55e" if _t2["resultado"]=="WIN" else "#ef4444"
                    _it2 = "🔺" if _t2["senal"]=="BUY" else "🔻"
                    st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center;
                         background:#0a1020;border-left:3px solid {_ct2};border-radius:6px;
                         padding:10px 14px;margin-bottom:6px;flex-wrap:wrap;gap:8px;">
                      <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#4a7a99;">{_t2['fecha']}</div>
                      <div style="font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;color:{_ct2};">{_it2} {_t2['senal']}</div>
                      <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#c8d8e8;">RSI {_t2['rsi']}</div>
                      <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#c8d8e8;">{_t2['entrada']:.5f} → {_t2['salida']:.5f}</div>
                      <div style="font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;color:{_ct2};">{_t2['ganancia']:+.2f}$</div>
                      <div style="font-family:Share Tech Mono,monospace;font-size:11px;font-weight:700;
                           background:{'rgba(34,197,94,0.15)' if _t2['resultado']=='WIN' else 'rgba(239,68,68,0.15)'};
                           color:{_ct2};padding:3px 10px;border-radius:10px;">{_t2['resultado']}</div>
                    </div>""", unsafe_allow_html=True)

                _cap_c2 = [_cap2]
                for _t2 in _trades2:
                    _cap_c2.append(_cap_c2[-1] + _t2["ganancia"])
                st.markdown('<div class="sec">CURVA DE CAPITAL SIMULADA</div>', unsafe_allow_html=True)
                st.line_chart(pd.DataFrame({"Capital": _cap_c2}), color="#f0b429")
        else:
            st.markdown("""<div style="text-align:center;padding:60px;background:#0a1020;border:2px dashed #1a2a45;border-radius:14px;">
              <div style="font-size:48px;margin-bottom:12px;">🔮</div>
              <div style="font-family:Rajdhani,sans-serif;font-size:22px;color:#4a7a99;">Configurá el escenario y presioná SIMULAR</div>
            </div>""", unsafe_allow_html=True)

# ================================================================
# TAB: EDUCATIVO
# ================================================================
with tab_educativo:
    st.markdown('<div class="sec">📚 PANEL EDUCATIVO — QQE Y ESTRATEGIA</div>', unsafe_allow_html=True)
    edu_t = st.tabs(["QQE", "SEÑALES", "GESTIÓN", "PSICOLOGÍA", "SESIONES ARG"])

    with edu_t[0]:
        st.markdown("""<div style="background:#0a1020;border:1px solid #1a2a45;border-left:4px solid #f0b429;border-radius:12px;padding:18px;margin-bottom:12px;">
          <div style="font-family:'Share Tech Mono',monospace;font-size:11px;color:#f0b429;letter-spacing:2px;margin-bottom:12px;">QUE ES EL QQE</div>
          <div style="font-size:14px;line-height:1.9;color:#c8d8e8;">
            El <b style="color:#f0b429;">QQE (Quantitative Qualitative Estimation)</b> es un indicador de momentum
            derivado del RSI. Aplica suavizado exponencial y calcula bandas dinámicas basadas en el ATR del propio RSI.<br><br>
            <b style="color:#22c55e;">PROCESO:</b><br>
            1. RSI(close, N) — RSI base<br>
            2. EMA(RSI, SF) — RSI suavizado<br>
            3. ATR del RSI suavizado × QQE Factor — Banda dinámica<br>
            4. Cruce del RSI suavizado con la banda — SEÑAL<br><br>
            <b style="color:#60a5fa;">VENTAJA vs RSI clásico:</b> Las señales son menos ruidosas
            porque la banda se ajusta a la volatilidad actual del indicador, no a un valor fijo.
          </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
          <div style="background:#030710;border:1px solid #1a2a45;border-radius:10px;padding:14px;">
            <div style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#f0b429;margin-bottom:8px;">RSI PERIOD (14)</div>
            <div style="font-size:13px;color:#c8d8e8;line-height:1.7;">Período base del RSI. Menor = más señales pero más ruido. Para scalping M1 usar 9-14.</div>
          </div>
          <div style="background:#030710;border:1px solid #1a2a45;border-radius:10px;padding:14px;">
            <div style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#f0b429;margin-bottom:8px;">SMOOTHING FACTOR (5)</div>
            <div style="font-size:13px;color:#c8d8e8;line-height:1.7;">Suaviza el RSI. Mayor SF = señales más tardías pero más limpias. Scalping: 3-5.</div>
          </div>
          <div style="background:#030710;border:1px solid #1a2a45;border-radius:10px;padding:14px;">
            <div style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#f0b429;margin-bottom:8px;">QQE FACTOR (4.238)</div>
            <div style="font-size:13px;color:#c8d8e8;line-height:1.7;">Multiplica el ATR de la banda. Mayor = bandas más anchas, menos señales, mayor calidad.</div>
          </div>
          <div style="background:#030710;border:1px solid #1a2a45;border-radius:10px;padding:14px;">
            <div style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#f0b429;margin-bottom:8px;">RSI THRESHOLD (3.0)</div>
            <div style="font-size:13px;color:#c8d8e8;line-height:1.7;">Define zona de alta calidad. Señales alejadas del 50 se marcan como ALTA.</div>
          </div>
        </div>""", unsafe_allow_html=True)

    with edu_t[1]:
        st.markdown("""<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
          <div style="background:linear-gradient(135deg,#001508,#0a1020);border:1px solid #22c55e;border-radius:12px;padding:18px;">
            <div style="font-family:'Share Tech Mono',monospace;font-size:11px;color:#22c55e;margin-bottom:10px;">SEÑAL CALL (BUY)</div>
            <div style="font-size:13px;color:#c8d8e8;line-height:1.8;">
              RSI suavizado cruza ARRIBA la banda inferior<br>
              Tendencia QQE cambia de -1 a +1<br>
              RSI suavizado supera los 50 puntos<br><br>
              <b style="color:#22c55e;">ALTA CALIDAD:</b> RSI estaba debajo de 50 y cruza con momentum creciente.
            </div>
          </div>
          <div style="background:linear-gradient(135deg,#150000,#0a1020);border:1px solid #ef4444;border-radius:12px;padding:18px;">
            <div style="font-family:'Share Tech Mono',monospace;font-size:11px;color:#ef4444;margin-bottom:10px;">SEÑAL PUT (SELL)</div>
            <div style="font-size:13px;color:#c8d8e8;line-height:1.8;">
              RSI suavizado cruza ABAJO la banda superior<br>
              Tendencia QQE cambia de +1 a -1<br>
              RSI suavizado cae debajo de 50 puntos<br><br>
              <b style="color:#ef4444;">FILTRO EXTRA:</b> Confirmar vela bajista y volumen no anormalmente bajo.
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

    with edu_t[2]:
        st.markdown("""<div style="background:#0a1020;border:1px solid #1a2a45;border-left:4px solid #f0b429;border-radius:12px;padding:18px;">
          <div style="font-family:'Share Tech Mono',monospace;font-size:11px;color:#f0b429;margin-bottom:12px;">GESTIÓN DE CAPITAL</div>
          <div style="font-size:13px;line-height:1.9;color:#c8d8e8;">
            <b style="color:#f0b429;">Regla del 1%:</b> No arriesgar más del 1% del capital por operación.<br>
            Con $500 → máximo $5 por operación.<br><br>
            <b style="color:#f0b429;">Stop diario:</b> 2 pérdidas seguidas = parar el día.<br><br>
            <b style="color:#f0b429;">Profit Factor mínimo:</b> Solo operar sistemas con PF &gt; 1.3<br><br>
            <b style="color:#22c55e;">Fórmula posición:</b><br>
            <code style="background:#030710;padding:4px 10px;border-radius:4px;color:#60a5fa;font-size:12px;">
            monto = capital × riesgo% / 100
            </code>
          </div>
        </div>""", unsafe_allow_html=True)

    with edu_t[3]:
        st.markdown("""<div style="background:#0a1020;border:1px solid #1a2a45;border-left:4px solid #60a5fa;border-radius:12px;padding:18px;">
          <div style="font-family:'Share Tech Mono',monospace;font-size:11px;color:#60a5fa;margin-bottom:12px;">PSICOLOGÍA DEL TRADING</div>
          <div style="font-size:13px;line-height:1.9;color:#c8d8e8;">
            <b style="color:#ef4444;">Revenge trading:</b> Doblar apuesta tras perder para recuperar.<br>
            El sistema no cambia porque vos perdiste.<br><br>
            <b style="color:#ef4444;">FOMO:</b> Entrar tarde a una señal que ya corrió.<br>
            Si perdiste la entrada, esperar la próxima.<br><br>
            <b style="color:#ef4444;">Over-trading:</b> Operar sin señal clara por aburrimiento.<br>
            WAIT en el semáforo = esperar, sin excepciones.<br><br>
            <b style="color:#22c55e;">Regla mental:</b> Cada operación es independiente. El edge está en el volumen, no en cada trade individual.
          </div>
        </div>""", unsafe_allow_html=True)

    with edu_t[4]:
        st.markdown("""<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
          <div style="background:#030710;border-left:3px solid #22c55e;border-radius:8px;padding:14px;">
            <b style="color:#22c55e;">LONDRÉS 04:00–07:00 ARG</b><br>
            <div style="font-size:13px;color:#c8d8e8;margin-top:6px;">Mayor liquidez EUR/GBP. Movimientos limpios.<br><span style="color:#4a7a99;">Mejor: EUR/USD, GBP/USD</span></div>
          </div>
          <div style="background:#030710;border-left:3px solid #22c55e;border-radius:8px;padding:14px;">
            <b style="color:#22c55e;">NUEVA YORK 10:00–13:00 ARG</b><br>
            <div style="font-size:13px;color:#c8d8e8;margin-top:6px;">Alta volatilidad. Solapamiento con Londres.<br><span style="color:#4a7a99;">Mejor: todos los pares mayores</span></div>
          </div>
          <div style="background:#030710;border-left:3px solid #f0b429;border-radius:8px;padding:14px;">
            <b style="color:#f0b429;">SOLAPAMIENTO 07:00–10:00 ARG</b><br>
            <div style="font-size:13px;color:#c8d8e8;margin-top:6px;">Máxima actividad y spreads bajos.<br><span style="color:#4a7a99;">Optimo para scalping</span></div>
          </div>
          <div style="background:#030710;border-left:3px solid #ef4444;border-radius:8px;padding:14px;">
            <b style="color:#ef4444;">ASIÁTICA 21:00–04:00 ARG</b><br>
            <div style="font-size:13px;color:#c8d8e8;margin-top:6px;">Baja volatilidad. Muchas señales falsas.<br><span style="color:#4a7a99;">EVITAR operaciones</span></div>
          </div>
        </div>""", unsafe_allow_html=True)

# ================================================================
# TAB: MEJORAS
# ================================================================
with tab_mejoras:
    st.markdown('<div class="sec">🔧 10 MEJORAS — IMPLEMENTADAS EN TIEMPO REAL</div>', unsafe_allow_html=True)

    mej_tabs = st.tabs([
        "①MTF","②ATR","③KELLY","④ALERTAS","⑤PAYOUT",
        "⑥HORARIO","⑦IQ AUTO","⑧IA SEÑAL","⑨OPTIMIZAR","⑩DIARIO+"
    ])

    # ── MEJORA 01: CONFIRMACIÓN MULTI-TIMEFRAME ──────────────────
    with mej_tabs[0]:
        st.markdown('<div class="sec">① CONFIRMACIÓN MULTI-TIMEFRAME — EN VIVO</div>', unsafe_allow_html=True)
        st.markdown("""<div style="background:#030710;border-left:4px solid #22c55e;border-radius:8px;padding:12px;margin-bottom:14px;font-size:13px;color:#c8d8e8;line-height:1.8;">
        Solo operar cuando M1, H1 y H4 coinciden en dirección. Reduce señales pero aumenta win rate al 60-70%.
        </div>""", unsafe_allow_html=True)

        m1_col1, m1_col2 = st.columns([1,2])
        with m1_col1:
            m1_act = st.selectbox("Activo", list(ACTIVOS.keys()), key="m1_act")
            btn_m1 = st.button("🔍 ANALIZAR MTF AHORA", key="m1_run", use_container_width=True)

        with m1_col2:
            if btn_m1:
                _ticker_m1 = ACTIVOS[m1_act]["yahoo"]
                with st.spinner("Consultando 3 timeframes..."):
                    def _tend_tf(sym, iv, period):
                        try:
                            _d = yf.download(sym, period=period, interval=iv, progress=False, auto_adjust=True)
                            if _d.empty or len(_d) < 20: return "LATERAL", 50.0
                            _d.columns = [c[0].lower() if isinstance(c,tuple) else c.lower() for c in _d.columns]
                            _c = _d["close"].dropna()
                            _e20 = _c.ewm(span=20, adjust=False).mean()
                            _e50 = _c.ewm(span=50, adjust=False).mean()
                            _rsi_v = float(calc_rsi(_c).iloc[-1])
                            _p = float(_c.iloc[-1])
                            if _p > float(_e20.iloc[-1]) > float(_e50.iloc[-1]): return "ALCISTA", _rsi_v
                            if _p < float(_e20.iloc[-1]) < float(_e50.iloc[-1]): return "BAJISTA", _rsi_v
                            return "LATERAL", _rsi_v
                        except: return "LATERAL", 50.0

                    _t1m,  _r1m  = _tend_tf(_ticker_m1, "1m",  "1d")
                    _t1h,  _r1h  = _tend_tf(_ticker_m1, "1h",  "10d")
                    _t4h,  _r4h  = _tend_tf(_ticker_m1, "4h",  "30d") if "4h" in ["4h"] else _tend_tf(_ticker_m1,"1h","30d")

                    _tfs = [("M1", _t1m, _r1m), ("H1", _t1h, _r1h), ("H4", _t4h, _r4h)]
                    _alcistas = sum(1 for _,t,_ in _tfs if t=="ALCISTA")
                    _bajistas = sum(1 for _,t,_ in _tfs if t=="BAJISTA")

                    if _alcistas == 3:
                        _mtf_sig = "🔺 CALL CONFIRMADO"
                        _mtf_col = "#22c55e"
                        _mtf_bg  = "linear-gradient(135deg,#001508,#0a1020)"
                    elif _bajistas == 3:
                        _mtf_sig = "🔻 PUT CONFIRMADO"
                        _mtf_col = "#ef4444"
                        _mtf_bg  = "linear-gradient(135deg,#150000,#0a1020)"
                    elif _alcistas == 2:
                        _mtf_sig = "⚠ POSIBLE CALL (2/3)"
                        _mtf_col = "#f0b429"
                        _mtf_bg  = "#0a1020"
                    elif _bajistas == 2:
                        _mtf_sig = "⚠ POSIBLE PUT (2/3)"
                        _mtf_col = "#f0b429"
                        _mtf_bg  = "#0a1020"
                    else:
                        _mtf_sig = "⏸ SIN CONFLUENCIA"
                        _mtf_col = "#64748b"
                        _mtf_bg  = "#0a1020"

                    st.markdown(f"""<div style="background:{_mtf_bg};border:2px solid {_mtf_col};border-radius:12px;padding:16px;margin-bottom:12px;text-align:center;">
                      <div style="font-family:'Rajdhani',sans-serif;font-weight:900;font-size:40px;color:{_mtf_col};">{_mtf_sig}</div>
                      <div style="font-family:'Share Tech Mono',monospace;font-size:11px;color:#4a7a99;margin-top:6px;">{m1_act} · Confluencia Multi-Timeframe</div>
                    </div>""", unsafe_allow_html=True)

                    _gc1,_gc2,_gc3 = st.columns(3)
                    for _col_w, (_lbl, _tend, _rsi_v) in zip([_gc1,_gc2,_gc3], _tfs):
                        _cc = "#22c55e" if _tend=="ALCISTA" else ("#ef4444" if _tend=="BAJISTA" else "#64748b")
                        _ic = "🔺" if _tend=="ALCISTA" else ("🔻" if _tend=="BAJISTA" else "⏸")
                        with _col_w:
                            _kpi_v11(_lbl, f"{_ic} {_tend}", f"RSI {_rsi_v:.1f}", _cc)

    # ── MEJORA 02: FILTRO ATR ────────────────────────────────────
    with mej_tabs[1]:
        st.markdown('<div class="sec">② FILTRO DE VOLATILIDAD ATR — OPERAR SOLO EN ZONA VÁLIDA</div>', unsafe_allow_html=True)
        st.markdown("""<div style="background:#030710;border-left:4px solid #f0b429;border-radius:8px;padding:12px;margin-bottom:14px;font-size:13px;color:#c8d8e8;line-height:1.8;">
        Calcula el ATR actual y lo compara con rangos históricos. Solo señal verde si el mercado tiene volatilidad operable (ni dormido ni explosivo por noticias).
        </div>""", unsafe_allow_html=True)

        m2c1, m2c2 = st.columns([1,2])
        with m2c1:
            m2_act  = st.selectbox("Activo", list(ACTIVOS.keys()), key="m2_act")
            m2_iv   = st.selectbox("Intervalo", ["1m","5m","15m","1h"], index=1, key="m2_iv")
            m2_atr_min = st.number_input("ATR mínimo", value=0.0002, step=0.0001, format="%.4f", key="m2_amin")
            m2_atr_max = st.number_input("ATR máximo", value=0.0015, step=0.0001, format="%.4f", key="m2_amax")
            btn_m2 = st.button("📡 ANALIZAR VOLATILIDAD", key="m2_run", use_container_width=True)

        with m2c2:
            if btn_m2:
                _t_m2 = ACTIVOS[m2_act]["yahoo"]
                _d_m2_raw = obtener_datos(_t_m2, period="5d", interval=m2_iv) if m2_iv not in ["1m"] else obtener_datos_1min(_t_m2)
                if _d_m2_raw is not None and len(_d_m2_raw) >= 14:
                    _atr_series = calc_atr(_d_m2_raw)
                    _atr_actual = float(_atr_series.iloc[-1])
                    _atr_prom   = float(_atr_series.tail(20).mean())
                    _atr_max_h  = float(_atr_series.tail(50).max())
                    _atr_min_h  = float(_atr_series.tail(50).min())

                    if _atr_actual < m2_atr_min:
                        _vol_estado = "🔴 MERCADO DORMIDO"
                        _vol_col    = "#ef4444"
                        _vol_desc   = "ATR muy bajo — spread consume la ganancia. No operar."
                    elif _atr_actual > m2_atr_max:
                        _vol_estado = "🟡 ALTA VOLATILIDAD"
                        _vol_col    = "#f0b429"
                        _vol_desc   = "ATR muy alto — posible noticia. Esperar estabilización."
                    else:
                        _vol_estado = "🟢 VOLATILIDAD NORMAL"
                        _vol_col    = "#22c55e"
                        _vol_desc   = "ATR en zona operable. Las señales QQE son válidas."

                    st.markdown(f"""<div style="background:#0a1020;border:2px solid {_vol_col};border-radius:12px;padding:16px;margin-bottom:12px;text-align:center;">
                      <div style="font-family:'Rajdhani',sans-serif;font-weight:900;font-size:34px;color:{_vol_col};">{_vol_estado}</div>
                      <div style="font-size:13px;color:#c8d8e8;margin-top:8px;">{_vol_desc}</div>
                    </div>""", unsafe_allow_html=True)

                    _ac1,_ac2,_ac3,_ac4 = st.columns(4)
                    with _ac1: _kpi_v11("ATR ACTUAL",  f"{_atr_actual:.5f}", m2_iv, _vol_col)
                    with _ac2: _kpi_v11("ATR PROM 20", f"{_atr_prom:.5f}",  "historial", "#c8d8e8")
                    with _ac3: _kpi_v11("ATR MÍN 50",  f"{_atr_min_h:.5f}", "50 velas", "#60a5fa")
                    with _ac4: _kpi_v11("ATR MÁX 50",  f"{_atr_max_h:.5f}", "50 velas", "#f0b429")

                    # Barra de posición del ATR actual
                    _rango = _atr_max_h - _atr_min_h if _atr_max_h > _atr_min_h else 1
                    _pos_pct = (_atr_actual - _atr_min_h) / _rango * 100
                    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a7a99;margin:10px 0 4px;">POSICIÓN DEL ATR EN RANGO HISTÓRICO</div>', unsafe_allow_html=True)
                    _progbar(_pos_pct, _vol_col)
                    st.caption(f"Zona operable: {m2_atr_min:.4f} — {m2_atr_max:.4f}")
                else:
                    st.error("Sin datos suficientes.")

    # ── MEJORA 03: KELLY DINÁMICO ────────────────────────────────
    with mej_tabs[2]:
        st.markdown('<div class="sec">③ GESTIÓN DINÁMICA DEL CAPITAL — KELLY MODIFICADO</div>', unsafe_allow_html=True)
        st.markdown("""<div style="background:#030710;border-left:4px solid #60a5fa;border-radius:8px;padding:12px;margin-bottom:14px;font-size:13px;color:#c8d8e8;line-height:1.8;">
        Ajusta el tamaño de la posición automáticamente según tu racha de pérdidas/ganancias del día. Factor: 0.5x tras 2 pérdidas · 1.0x normal · 1.5x tras 3 ganancias.
        </div>""", unsafe_allow_html=True)

        _racha_actual = st.session_state.get("racha_losses", 0)
        _ops_hoy = st.session_state.get("ops", [])
        _racha_wins = 0
        for _op in reversed(_ops_hoy):
            if _op.get("pnl", 0) > 0: _racha_wins += 1
            else: break

        # Factor Kelly
        if _racha_actual >= 2:
            _kelly_f = 0.5
            _kelly_color = "#ef4444"
            _kelly_txt   = "⚠ REDUCIDO — racha de pérdidas"
        elif _racha_wins >= 3:
            _kelly_f = 1.5
            _kelly_color = "#22c55e"
            _kelly_txt   = "🚀 AUMENTADO — racha ganadora"
        elif _racha_actual == 1:
            _kelly_f = 0.75
            _kelly_color = "#f0b429"
            _kelly_txt   = "⚡ PRECAUCIÓN — 1 pérdida"
        else:
            _kelly_f = 1.0
            _kelly_color = "#60a5fa"
            _kelly_txt   = "✅ NORMAL"

        _monto_base   = st.session_state.capital * st.session_state.riesgo_pct / 100
        _monto_kelly  = _monto_base * _kelly_f

        m3c1, m3c2, m3c3, m3c4 = st.columns(4)
        with m3c1: _kpi_v11("FACTOR KELLY",   f"{_kelly_f}x",          _kelly_txt, _kelly_color)
        with m3c2: _kpi_v11("MONTO BASE",      f"${_monto_base:.2f}",   f"{st.session_state.riesgo_pct}% capital", "#c8d8e8")
        with m3c3: _kpi_v11("MONTO AJUSTADO",  f"${_monto_kelly:.2f}",  "usar ahora", _kelly_color)
        with m3c4: _kpi_v11("RACHA PÉRDIDAS",  str(_racha_actual),       "consecutivas", "#ef4444" if _racha_actual>0 else "#22c55e")

        st.markdown(f"""<div style="background:#0a1020;border:2px solid {_kelly_color};border-radius:12px;padding:16px;text-align:center;margin-top:12px;">
          <div style="font-family:'Rajdhani',sans-serif;font-weight:900;font-size:42px;color:{_kelly_color};">PRÓXIMA ENTRADA: ${_monto_kelly:.2f}</div>
          <div style="font-family:'Share Tech Mono',monospace;font-size:11px;color:#4a7a99;margin-top:6px;">{_kelly_txt} · Racha pérdidas: {_racha_actual} · Racha ganancias: {_racha_wins}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="sec">SIMULADOR KELLY</div>', unsafe_allow_html=True)
        _sk_c1, _sk_c2 = st.columns(2)
        with _sk_c1:
            _sim_cap_k = st.number_input("Capital", 50.0, 10000.0, value=float(st.session_state.capital), key="sk_cap")
            _sim_rsk_k = st.slider("Riesgo base %", 0.5, 5.0, float(st.session_state.riesgo_pct), step=0.5, key="sk_rsk")
        with _sk_c2:
            _sim_seq_k = st.text_input("Secuencia W/L (ej: W,W,L,L,W)", value="W,W,L,L,L,W,W,W,W", key="sk_seq")
            if st.button("▶ SIMULAR SECUENCIA KELLY", key="sk_run", use_container_width=True):
                _seq_k = [s.strip().upper() for s in _sim_seq_k.split(",")]
                _cap_k = _sim_cap_k
                _hist_k = [_cap_k]
                _racha_l_k = 0
                _racha_w_k = 0
                for _res_k in _seq_k:
                    _base_k = _cap_k * _sim_rsk_k / 100
                    if _racha_l_k >= 2: _f_k = 0.5
                    elif _racha_w_k >= 3: _f_k = 1.5
                    elif _racha_l_k == 1: _f_k = 0.75
                    else: _f_k = 1.0
                    _monto_k = _base_k * _f_k
                    if _res_k == "W":
                        _cap_k += _monto_k * 0.85  # payout 85%
                        _racha_l_k = 0; _racha_w_k += 1
                    else:
                        _cap_k -= _monto_k
                        _racha_w_k = 0; _racha_l_k += 1
                    _hist_k.append(round(_cap_k, 2))
                st.line_chart(pd.DataFrame({"Capital Kelly": _hist_k}), color="#60a5fa")
                _kpi_v11("RESULTADO", f"${_hist_k[-1]:.2f}", f"desde ${_sim_cap_k:.2f}", "#22c55e" if _hist_k[-1]>_sim_cap_k else "#ef4444")

    # ── MEJORA 04: ALERTAS TELEGRAM CON CONTEXTO COMPLETO ───────
    with mej_tabs[3]:
        st.markdown('<div class="sec">④ ALERTAS TELEGRAM CON CONTEXTO COMPLETO</div>', unsafe_allow_html=True)
        st.markdown("""<div style="background:#030710;border-left:4px solid #a78bfa;border-radius:8px;padding:12px;margin-bottom:14px;font-size:13px;color:#c8d8e8;line-height:1.8;">
        Genera y envía una alerta Telegram con: señal, par, timeframe, RSI, ATR, fuerza, sesión activa, tendencia H1, capital y monto de entrada.
        </div>""", unsafe_allow_html=True)

        m4c1, m4c2 = st.columns([1,2])
        with m4c1:
            m4_act  = st.selectbox("Activo", list(ACTIVOS.keys()), key="m4_act")
            m4_iv   = st.selectbox("Intervalo", ["1m","5m","15m","1h"], index=1, key="m4_iv")
            m4_sig  = st.radio("Señal", ["BUY (CALL)","SELL (PUT)","WAIT"], horizontal=True, key="m4_sig")
            m4_rsi  = st.slider("RSI Suavizado", 20.0, 80.0, 58.0, step=0.5, key="m4_rsi")
            m4_fz   = st.slider("Fuerza %", 0, 100, 74, key="m4_fz")
            btn_m4  = st.button("📱 GENERAR Y ENVIAR ALERTA", key="m4_run", use_container_width=True)

        with m4c2:
            _sesion_m4, _estado_m4, *_ = get_session_info()
            _tend_m4 = get_tendencia_h1(ACTIVOS[m4_act]["yahoo"])
            _kelly_m4 = st.session_state.capital * st.session_state.riesgo_pct / 100
            _sig_m4 = "BUY" if "BUY" in m4_sig else ("SELL" if "SELL" in m4_sig else "WAIT")
            _ic_m4  = "🟢" if _sig_m4 == "BUY" else ("🔴" if _sig_m4 == "SELL" else "⏸")
            _dir_m4 = "CALL" if _sig_m4 == "BUY" else ("PUT" if _sig_m4 == "SELL" else "ESPERAR")

            _msg_m4 = f"""{_ic_m4} <b>QQE SIGNAL — {_dir_m4}</b>

📊 <b>Par:</b> {m4_act} | <b>TF:</b> {m4_iv.upper()}
📈 <b>RSI:</b> {m4_rsi:.1f} | <b>Fuerza:</b> {m4_fz}%
📉 <b>ATR:</b> Zona normal
🕐 <b>Sesión:</b> {_sesion_m4} ({_estado_m4})
📐 <b>H1 tendencia:</b> {_tend_m4}
💰 <b>Capital:</b> ${st.session_state.capital:.2f} | <b>Entrada:</b> ${_kelly_m4:.2f}
🎯 <b>Resultado esperado:</b> Win Rate hist ~60%

<i>QQE Command v11 · Goya, Corrientes</i>"""

            st.markdown(f"""<div style="background:#0a1020;border:1px solid #a78bfa;border-radius:12px;padding:16px;margin-bottom:12px;font-family:'Share Tech Mono',monospace;font-size:12px;color:#c8d8e8;line-height:1.9;white-space:pre-wrap;">{_msg_m4}</div>""", unsafe_allow_html=True)

            if btn_m4:
                if st.session_state.tg_on:
                    _ok_m4 = enviar_telegram(st.session_state.tg_token, st.session_state.tg_chat, _msg_m4)
                    if _ok_m4:
                        st.success("✅ Alerta enviada a Telegram con contexto completo!")
                    else:
                        st.error("❌ Error al enviar. Verificá token y chat ID en config.")
                else:
                    st.warning("⚠ Telegram no configurado. Ir al tab TRIPLE EN VIVO → configuración.")

    # ── MEJORA 05: BACKTEST CON PAYOUT REAL (BINARIAS) ──────────
    with mej_tabs[4]:
        st.markdown('<div class="sec">⑤ BACKTEST CON COSTOS REALES DE IQ OPTION</div>', unsafe_allow_html=True)
        st.markdown("""<div style="background:#030710;border-left:4px solid #fb923c;border-radius:8px;padding:12px;margin-bottom:14px;font-size:13px;color:#c8d8e8;line-height:1.8;">
        En binarias el payout es fijo. WIN = +monto×payout%. LOSS = -monto×100%. Esto cambia completamente las estadísticas vs backtest de forex libre.
        </div>""", unsafe_allow_html=True)

        m5c1, m5c2 = st.columns([1,2])
        with m5c1:
            m5_act    = st.selectbox("Activo", list(ACTIVOS.keys()), key="m5_act")
            m5_iv     = st.selectbox("Intervalo", ["1m","5m","15m","1h"], index=1, key="m5_iv")
            m5_cap    = st.number_input("Capital $", 50.0, 10000.0, value=float(st.session_state.capital), step=10.0, key="m5_cap")
            m5_rsk    = st.slider("Riesgo %", 0.5, 5.0, float(st.session_state.riesgo_pct), step=0.5, key="m5_rsk")
            m5_payout = st.slider("Payout IQ Option %", 70, 95, 85, step=1, key="m5_payout")
            btn_m5    = st.button("▶ BACKTEST BINARIAS REAL", key="m5_run", use_container_width=True)

        with m5c2:
            if btn_m5:
                with st.spinner("Calculando backtest con payout real..."):
                    _t5    = ACTIVOS[m5_act]["yahoo"]
                    _d5    = obtener_datos(_t5, period="30d", interval=m5_iv)
                    if _d5 is None or len(_d5) < 40:
                        st.error("Sin datos suficientes.")
                    else:
                        _dq5 = calc_qqe_engine(_d5)
                        # Backtest con payout fijo
                        _monto5  = m5_cap * m5_rsk / 100
                        _payout5 = m5_payout / 100
                        _trades5 = []
                        _sig5_idx = _dq5.index[_dq5["signal"].isin(["BUY","SELL"])].tolist()
                        for _i5, _idx5 in enumerate(_sig5_idx):
                            _pos5   = _dq5.index.get_loc(_idx5)
                            if _pos5 + 1 >= len(_dq5): continue
                            _entry5 = float(_dq5["cierre"].iloc[_pos5])
                            _exit5  = float(_dq5["cierre"].iloc[_pos5+1])
                            _row5   = _dq5.loc[_idx5]
                            _es_win5 = (_exit5 > _entry5 and _row5["signal"]=="BUY") or (_exit5 < _entry5 and _row5["signal"]=="SELL")
                            _gan5    = _monto5 * _payout5 if _es_win5 else -_monto5
                            _trades5.append({
                                "fecha":    _idx5.strftime("%m/%d %H:%M") if hasattr(_idx5,"strftime") else str(_idx5),
                                "senal":    _row5["signal"],
                                "resultado": "WIN" if _es_win5 else "LOSS",
                                "ganancia": round(_gan5, 2),
                                "payout_aplicado": f"{m5_payout}%",
                            })
                        if _trades5:
                            _tdf5   = pd.DataFrame(_trades5)
                            _w5     = _tdf5[_tdf5["resultado"]=="WIN"]
                            _l5     = _tdf5[_tdf5["resultado"]=="LOSS"]
                            _wr5    = len(_w5)/len(_tdf5)*100
                            _gan5t  = _tdf5["ganancia"].sum()
                            _wr5_c  = "#22c55e" if _wr5>=55 else ("#f0b429" if _wr5>=45 else "#ef4444")
                            _g5_c   = "#22c55e" if _gan5t>=0 else "#ef4444"
                            # Breakeven con payout real
                            _be5    = 1 / (1 + _payout5) * 100

                            _bc1,_bc2,_bc3,_bc4 = st.columns(4)
                            with _bc1: _kpi_v11("WIN RATE", f"{_wr5:.1f}%", f"{len(_w5)}W/{len(_l5)}L", _wr5_c)
                            with _bc2: _kpi_v11("BREAKEVEN REAL", f"{_be5:.1f}%", f"payout {m5_payout}%", "#f0b429")
                            with _bc3: _kpi_v11("GANANCIA TOTAL", f"${_gan5t:+.2f}", f"${m5_cap:.0f}→${m5_cap+_gan5t:.2f}", _g5_c)
                            with _bc4: _kpi_v11("TRADES", str(len(_tdf5)), m5_iv, "#c8d8e8")

                            if _wr5 >= _be5:
                                st.success(f"✅ Sistema rentable con payout {m5_payout}%. WR {_wr5:.1f}% > breakeven {_be5:.1f}%")
                            else:
                                st.error(f"⚠ Sistema NO rentable con payout {m5_payout}%. WR {_wr5:.1f}% < breakeven {_be5:.1f}%")

                            _cap5_c = [m5_cap]
                            for _t5r in _trades5: _cap5_c.append(_cap5_c[-1]+_t5r["ganancia"])
                            st.line_chart(pd.DataFrame({"Capital Binarias": _cap5_c}), color="#fb923c")
                            st.dataframe(_tdf5.tail(20), use_container_width=True, hide_index=True)

    # ── MEJORA 06: ESTADÍSTICAS POR HORARIO ─────────────────────
    with mej_tabs[5]:
        st.markdown('<div class="sec">⑥ ESTADÍSTICAS POR SESIÓN DE MERCADO</div>', unsafe_allow_html=True)
        st.markdown("""<div style="background:#030710;border-left:4px solid #34d399;border-radius:8px;padding:12px;margin-bottom:14px;font-size:13px;color:#c8d8e8;line-height:1.8;">
        Segmenta las señales QQE por sesión (Londres / Nueva York / Solapamiento / Asia) y calcula el Win Rate de cada una para encontrar el horario óptimo.
        </div>""", unsafe_allow_html=True)

        m6c1, m6c2 = st.columns([1,2])
        with m6c1:
            m6_act = st.selectbox("Activo", list(ACTIVOS.keys()), key="m6_act")
            m6_iv  = st.selectbox("Intervalo", ["1h","4h","1d"], index=0, key="m6_iv")
            btn_m6 = st.button("📊 ANALIZAR POR HORARIO", key="m6_run", use_container_width=True)

        with m6c2:
            if btn_m6:
                with st.spinner("Analizando señales por sesión..."):
                    _t6  = ACTIVOS[m6_act]["yahoo"]
                    _d6  = obtener_datos(_t6, period="60d", interval=m6_iv)
                    if _d6 is None or len(_d6) < 40:
                        st.error("Sin datos.")
                    else:
                        _dq6 = calc_qqe_engine(_d6)
                        _sig6 = _dq6[_dq6["signal"].isin(["BUY","SELL"])].copy()

                        def _get_sesion_utc(idx):
                            try:
                                _h = idx.hour
                                if 7 <= _h < 10:   return "LONDRÉS"
                                if 11 <= _h < 13:  return "SOLAPAMIENTO"
                                if 13 <= _h < 16:  return "NUEVA YORK"
                                return "ASIA/CERRADO"
                            except: return "DESCONOCIDO"

                        _sig6["sesion"] = _sig6.index.map(_get_sesion_utc)
                        _monto6 = st.session_state.capital * st.session_state.riesgo_pct / 100

                        # Calcular win por sesión (siguiente cierre)
                        _wins6 = {"LONDRÉS":0,"SOLAPAMIENTO":0,"NUEVA YORK":0,"ASIA/CERRADO":0}
                        _tots6 = {"LONDRÉS":0,"SOLAPAMIENTO":0,"NUEVA YORK":0,"ASIA/CERRADO":0}
                        for _i6, _idx6 in enumerate(_sig6.index):
                            _pos6 = _dq6.index.get_loc(_idx6)
                            if _pos6+1 >= len(_dq6): continue
                            _e6 = float(_dq6["cierre"].iloc[_pos6])
                            _x6 = float(_dq6["cierre"].iloc[_pos6+1])
                            _s6 = _sig6.loc[_idx6,"sesion"]
                            _tots6[_s6] = _tots6.get(_s6,0) + 1
                            _es_w6 = (_x6>_e6 and _sig6.loc[_idx6,"signal"]=="BUY") or (_x6<_e6 and _sig6.loc[_idx6,"signal"]=="SELL")
                            if _es_w6: _wins6[_s6] = _wins6.get(_s6,0)+1

                        for _ses6, _col6 in [("LONDRÉS","#22c55e"),("SOLAPAMIENTO","#f0b429"),("NUEVA YORK","#22c55e"),("ASIA/CERRADO","#ef4444")]:
                            _t6v = _tots6[_ses6]
                            _w6v = _wins6[_ses6]
                            _wr6 = _w6v/_t6v*100 if _t6v > 0 else 0
                            _wr6_c = "#22c55e" if _wr6>=55 else ("#f0b429" if _wr6>=40 else "#ef4444")
                            st.markdown(f"""<div style="background:#0a1020;border-left:4px solid {_col6};border-radius:8px;padding:12px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
                              <div style="font-family:'Share Tech Mono',monospace;font-size:12px;color:{_col6};">{_ses6}</div>
                              <div style="font-family:'Rajdhani',sans-serif;font-size:24px;font-weight:700;color:{_wr6_c};">{_wr6:.1f}% WR</div>
                              <div style="font-family:'Share Tech Mono',monospace;font-size:11px;color:#4a7a99;">{_w6v}W / {_t6v-_w6v}L de {_t6v} señales</div>
                            </div>""", unsafe_allow_html=True)
                            _progbar(_wr6, _wr6_c)

    # ── MEJORA 07: MONITOR IQ OPTION (sin iqoptionapi) ──────────
    with mej_tabs[6]:
        st.markdown('<div class="sec">⑦ MONITOR PARA IQ OPTION — SEÑAL LISTA PARA OPERAR</div>', unsafe_allow_html=True)
        st.markdown("""<div style="background:#030710;border-left:4px solid #f472b6;border-radius:8px;padding:12px;margin-bottom:14px;font-size:13px;color:#c8d8e8;line-height:1.8;">
        Panel operativo completo: señal QQE + filtro ATR + confirmación H1 + Kelly + sesión activa. Todo en una pantalla para ejecutar rápido en IQ Option.
        </div>""", unsafe_allow_html=True)

        m7c1, m7c2 = st.columns([1,2])
        with m7c1:
            m7_act = st.selectbox("Par a operar", list(ACTIVOS.keys()), key="m7_act")
            m7_exp = st.selectbox("Expiración", ["1 min","2 min","3 min","5 min"], key="m7_exp")
            btn_m7 = st.button("⚡ PANEL DE ENTRADA RÁPIDA", key="m7_run", use_container_width=True)

        with m7c2:
            if btn_m7:
                with st.spinner("Preparando panel operativo..."):
                    _t7    = ACTIVOS[m7_act]["yahoo"]
                    _d7_1m = obtener_datos_1min(_t7)
                    _tend7 = get_tendencia_h1(_t7)
                    _ses7, _est7, _ses7_col, *_ = get_session_info()

                    _sig7  = "WAIT"
                    _rsi7  = 50.0
                    _fz7   = 0
                    _atr7  = 0.0

                    if _d7_1m is not None and len(_d7_1m) >= 30:
                        _dq7 = calc_qqe_engine(_d7_1m)
                        _last7 = _dq7.iloc[-1]
                        _rsi7  = round(float(_last7["rsi_smooth"]), 1)
                        _sig7  = "BUY" if _last7["trend_q"]==1 else ("SELL" if _last7["trend_q"]==-1 else "WAIT")
                        _fz7   = min(100, int(abs(_rsi7-50)*2))
                        _atr7  = float(calc_atr(_d7_1m).iloc[-1])

                    # Semáforo de 5 condiciones
                    _chk_sig   = _sig7 != "WAIT"
                    _chk_tend  = (_sig7=="BUY" and _tend7=="ALCISTA") or (_sig7=="SELL" and _tend7=="BAJISTA") or _sig7=="WAIT"
                    _chk_ses   = es_horario_operable()
                    _chk_atr   = 0.0001 < _atr7 < 0.005
                    _chk_kelly = st.session_state.get("racha_losses",0) < 2

                    _checks = [
                        ("Señal QQE activa",    _chk_sig,   "M1 trend ≠ WAIT"),
                        ("Confluencia H1",      _chk_tend,  f"H1: {_tend7}"),
                        ("Sesión operable",     _chk_ses,   f"{_ses7}"),
                        ("ATR en zona",         _chk_atr,   f"ATR: {_atr7:.5f}"),
                        ("Kelly sin bloqueo",   _chk_kelly, f"Racha pérd: {st.session_state.get('racha_losses',0)}"),
                    ]
                    _ok_count = sum(1 for _,v,_ in _checks if v)

                    _panel_col = "#22c55e" if _ok_count==5 else ("#f0b429" if _ok_count>=3 else "#ef4444")
                    _panel_txt = "🟢 ENTRAR AHORA" if _ok_count==5 else ("🟡 PRECAUCIÓN" if _ok_count>=3 else "🔴 NO OPERAR")
                    _dir7  = "CALL" if _sig7=="BUY" else ("PUT" if _sig7=="SELL" else "—")
                    _monto7 = st.session_state.capital * st.session_state.riesgo_pct / 100

                    st.markdown(f"""<div style="background:#0a1020;border:3px solid {_panel_col};border-radius:14px;padding:20px;text-align:center;margin-bottom:14px;">
                      <div style="font-family:'Rajdhani',sans-serif;font-weight:900;font-size:48px;color:{_panel_col};">{_panel_txt}</div>
                      <div style="font-family:'Share Tech Mono',monospace;font-size:12px;color:#4a7a99;margin-top:6px;">{_ok_count}/5 condiciones OK · {m7_act} · {_dir7} · ${_monto7:.2f} · {m7_exp}</div>
                    </div>""", unsafe_allow_html=True)

                    for _lbl7, _ok7, _det7 in _checks:
                        _c7 = "#22c55e" if _ok7 else "#ef4444"
                        _ic7 = "✅" if _ok7 else "❌"
                        st.markdown(f"""<div style="background:#030710;border-radius:6px;padding:10px 14px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;">
                          <div style="font-family:'Share Tech Mono',monospace;font-size:12px;color:#c8d8e8;">{_ic7} {_lbl7}</div>
                          <div style="font-family:'Share Tech Mono',monospace;font-size:11px;color:{_c7};">{_det7}</div>
                        </div>""", unsafe_allow_html=True)

    # ── MEJORA 08: IA EXPLICA CADA SEÑAL ────────────────────────
    with mej_tabs[7]:
        st.markdown('<div class="sec">⑧ IA EXPLICA TU SEÑAL — ANÁLISIS CONTEXTUAL</div>', unsafe_allow_html=True)
        st.markdown("""<div style="background:#030710;border-left:4px solid #38bdf8;border-radius:8px;padding:12px;margin-bottom:14px;font-size:13px;color:#c8d8e8;line-height:1.8;">
        Usa la API de Anthropic (ya configurada en tu dashboard) para explicar en lenguaje natural por qué se generó la señal, qué factores la respaldan y el riesgo.
        </div>""", unsafe_allow_html=True)

        m8c1, m8c2 = st.columns([1,2])
        with m8c1:
            m8_act = st.selectbox("Activo", list(ACTIVOS.keys()), key="m8_act")
            m8_sig = st.radio("Señal", ["BUY (CALL)","SELL (PUT)"], horizontal=True, key="m8_sig")
            m8_rsi = st.slider("RSI Suavizado", 20.0, 80.0, 62.0, step=0.5, key="m8_rsi")
            m8_tend = st.radio("Tendencia H1", ["ALCISTA","BAJISTA","LATERAL"], horizontal=True, key="m8_tend")
            m8_ses, *_ = get_session_info()
            btn_m8 = st.button("🤖 PEDIR ANÁLISIS A LA IA", key="m8_run", use_container_width=True)

        with m8c2:
            if btn_m8:
                if not get_ia_ok():
                    st.warning("⚠ API key de Anthropic no configurada. Ingresala en el tab TRIPLE EN VIVO → Config IA.")
                else:
                    _sig_m8 = "BUY/CALL" if "BUY" in m8_sig else "SELL/PUT"
                    _prompt_m8 = f"""Sos un analista de trading experto en forex y opciones binarias. Explicá esta señal de forma clara y concisa:

Par: {m8_act}
Señal QQE: {_sig_m8}
RSI suavizado: {m8_rsi:.1f}
Tendencia H1: {m8_tend}
Sesión activa: {m8_ses}
Capital: ${st.session_state.capital:.2f}
Monto de entrada: ${st.session_state.capital * st.session_state.riesgo_pct / 100:.2f}

Respondé con: 1) Por qué se generó esta señal 2) Factores que la respaldan 3) Riesgos a considerar 4) Recomendación final. Máximo 200 palabras. En español."""

                    with st.spinner("Consultando IA..."):
                        try:
                            import anthropic as _anth
                            _client_m8 = _anth.Anthropic(api_key=st.session_state.api_key)
                            _resp_m8   = _client_m8.messages.create(
                                model="claude-opus-4-6",
                                max_tokens=400,
                                messages=[{"role":"user","content":_prompt_m8}]
                            )
                            _txt_m8 = _resp_m8.content[0].text
                            st.markdown(f"""<div style="background:#0a1020;border:1px solid #38bdf8;border-radius:12px;padding:18px;font-size:14px;color:#c8d8e8;line-height:1.9;">{_txt_m8}</div>""", unsafe_allow_html=True)
                        except Exception as _e_m8:
                            st.error(f"Error IA: {_e_m8}")

    # ── MEJORA 09: GRID SEARCH OPTIMIZACIÓN ─────────────────────
    with mej_tabs[8]:
        st.markdown('<div class="sec">⑨ OPTIMIZACIÓN AUTOMÁTICA DE PARÁMETROS QQE</div>', unsafe_allow_html=True)
        st.markdown("""<div style="background:#030710;border-left:4px solid #fbbf24;border-radius:8px;padding:12px;margin-bottom:14px;font-size:13px;color:#c8d8e8;line-height:1.8;">
        Grid search sobre combinaciones de RSI Period × SF × QQE Factor. Encuentra los parámetros con mayor Profit Factor para tu par y timeframe.
        </div>""", unsafe_allow_html=True)

        m9c1, m9c2 = st.columns([1,2])
        with m9c1:
            m9_act = st.selectbox("Activo", list(ACTIVOS.keys()), key="m9_act")
            m9_iv  = st.selectbox("Intervalo", ["5m","15m","1h","4h"], index=2, key="m9_iv")
            m9_cap = st.number_input("Capital $", 50.0, 10000.0, value=float(st.session_state.capital), key="m9_cap")
            m9_rsk = st.slider("Riesgo %", 0.5, 5.0, float(st.session_state.riesgo_pct), step=0.5, key="m9_rsk")
            st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#fbbf24;margin:10px 0 6px;">GRILLA DE BÚSQUEDA</div>', unsafe_allow_html=True)
            m9_rsi_vals = st.multiselect("RSI Period", [7,9,11,14,18,21], default=[9,14,21], key="m9_rsi_v")
            m9_sf_vals  = st.multiselect("SF (smooth)", [3,4,5,6,8,10], default=[3,5,8], key="m9_sf_v")
            m9_qf_vals  = st.multiselect("QQE Factor", [2.618,3.0,4.238,5.0,6.0], default=[3.0,4.238,6.0], key="m9_qf_v")
            btn_m9 = st.button("🔍 INICIAR GRID SEARCH", key="m9_run", use_container_width=True)

        with m9c2:
            if btn_m9:
                _t9  = ACTIVOS[m9_act]["yahoo"]
                _d9  = obtener_datos(_t9, period="60d", interval=m9_iv)
                if _d9 is None or len(_d9) < 50:
                    st.error("Sin datos suficientes.")
                elif not m9_rsi_vals or not m9_sf_vals or not m9_qf_vals:
                    st.warning("Seleccioná al menos 1 valor por parámetro.")
                else:
                    _combos = [(r,s,q) for r in m9_rsi_vals for s in m9_sf_vals for q in m9_qf_vals]
                    _resultados9 = []
                    _prog9 = st.progress(0)
                    for _ci9, (_r9,_s9,_q9) in enumerate(_combos):
                        _prog9.progress((_ci9+1)/len(_combos))
                        try:
                            _dq9 = calc_qqe_engine(_d9, _r9, _s9, _q9)
                            _bt9 = run_backtest_v11(_dq9, m9_cap, m9_rsk)
                            _st9 = _bt9.get("stats",{})
                            if _st9 and _st9["total_trades"] >= 5:
                                _resultados9.append({
                                    "RSI": _r9, "SF": _s9, "QQE_F": _q9,
                                    "WR%": _st9["win_rate"],
                                    "PF":  _st9["profit_factor"],
                                    "Trades": _st9["total_trades"],
                                    "Ganancia": _st9["total_ganancia"],
                                })
                        except: pass
                    _prog9.empty()

                    if _resultados9:
                        _df9 = pd.DataFrame(_resultados9).sort_values("PF", ascending=False)
                        _mejor9 = _df9.iloc[0]
                        st.markdown(f"""<div style="background:linear-gradient(135deg,#0a1a00,#0a1020);border:2px solid #fbbf24;border-radius:12px;padding:16px;margin-bottom:12px;text-align:center;">
                          <div style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#fbbf24;margin-bottom:6px;">MEJORES PARÁMETROS ENCONTRADOS</div>
                          <div style="font-family:'Rajdhani',sans-serif;font-weight:900;font-size:28px;color:#fbbf24;">
                            RSI {int(_mejor9['RSI'])} · SF {int(_mejor9['SF'])} · QQE {_mejor9['QQE_F']:.3f}
                          </div>
                          <div style="font-family:'Share Tech Mono',monospace;font-size:12px;color:#c8d8e8;margin-top:8px;">
                            WR {_mejor9['WR%']:.1f}% · PF {_mejor9['PF']:.2f} · {int(_mejor9['Trades'])} trades · ${_mejor9['Ganancia']:+.2f}
                          </div>
                        </div>""", unsafe_allow_html=True)
                        st.dataframe(_df9.head(15).reset_index(drop=True), use_container_width=True, hide_index=True)
                    else:
                        st.warning("Sin resultados válidos. Probá más combinaciones o un período mayor.")

    # ── MEJORA 10: DIARIO+ CON ANÁLISIS EMOCIONAL ───────────────
    with mej_tabs[9]:
        st.markdown('<div class="sec">⑩ DIARIO+ — REGISTRO CON ESTADO EMOCIONAL</div>', unsafe_allow_html=True)
        st.markdown("""<div style="background:#030710;border-left:4px solid #c084fc;border-radius:8px;padding:12px;margin-bottom:14px;font-size:13px;color:#c8d8e8;line-height:1.8;">
        Registra cada operación con tu estado emocional. Al final de la semana analizá si las pérdidas correlacionan con revenge trading, FOMO o aburrimiento.
        </div>""", unsafe_allow_html=True)

        if "diario_plus" not in st.session_state:
            st.session_state["diario_plus"] = []

        m10c1, m10c2 = st.columns([1,2])
        with m10c1:
            st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#c084fc;margin-bottom:10px;letter-spacing:2px;">NUEVA ENTRADA</div>', unsafe_allow_html=True)
            m10_par   = st.selectbox("Par",          list(ACTIVOS.keys()), key="m10_par")
            m10_dir   = st.radio("Dirección",        ["CALL","PUT"], horizontal=True, key="m10_dir")
            m10_res   = st.radio("Resultado",        ["WIN","LOSS","BREAK EVEN"], horizontal=True, key="m10_res")
            m10_monto = st.number_input("Monto $", 1.0, 1000.0, value=st.session_state.capital*st.session_state.riesgo_pct/100, step=0.5, key="m10_monto")
            m10_emo   = st.selectbox("Estado emocional", [
                "😊 Tranquilo/Concentrado",
                "😤 Frustrado (tras pérdida)",
                "😨 Ansioso/Apurado",
                "🤑 Eufórico (tras ganancia)",
                "😴 Aburrido/Sin señal",
                "😅 FOMO (señal que ya corrió)",
            ], key="m10_emo")
            m10_nota  = st.text_input("Nota rápida", placeholder="ej: entré tarde, seguí el plan...", key="m10_nota")
            btn_m10   = st.button("💾 GUARDAR ENTRADA", key="m10_save", use_container_width=True)

            if btn_m10:
                _pnl10 = m10_monto * 0.85 if m10_res=="WIN" else (-m10_monto if m10_res=="LOSS" else 0)
                st.session_state["diario_plus"].append({
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "par":   m10_par,
                    "dir":   m10_dir,
                    "result": m10_res,
                    "monto": m10_monto,
                    "pnl":   round(_pnl10,2),
                    "emocion": m10_emo,
                    "nota":  m10_nota,
                })
                st.success("✅ Registrado!")

        with m10c2:
            _dp = st.session_state["diario_plus"]
            if _dp:
                _dp_df = pd.DataFrame(_dp)

                # Estadísticas por emoción
                st.markdown('<div class="sec">WIN RATE POR ESTADO EMOCIONAL</div>', unsafe_allow_html=True)
                for _emo in _dp_df["emocion"].unique():
                    _emo_df = _dp_df[_dp_df["emocion"]==_emo]
                    _emo_wr = len(_emo_df[_emo_df["result"]=="WIN"]) / len(_emo_df) * 100 if len(_emo_df) > 0 else 0
                    _emo_col = "#22c55e" if _emo_wr>=55 else ("#f0b429" if _emo_wr>=40 else "#ef4444")
                    st.markdown(f"""<div style="background:#030710;border-radius:6px;padding:10px 14px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;">
                      <div style="font-size:13px;color:#c8d8e8;">{_emo}</div>
                      <div style="font-family:'Rajdhani',sans-serif;font-size:22px;font-weight:700;color:{_emo_col};">{_emo_wr:.0f}% WR</div>
                      <div style="font-family:'Share Tech Mono',monospace;font-size:11px;color:#4a7a99;">{len(_emo_df)} trades</div>
                    </div>""", unsafe_allow_html=True)
                    _progbar(_emo_wr, _emo_col)

                # Tabla completa
                st.markdown('<div class="sec">HISTORIAL DIARIO+</div>', unsafe_allow_html=True)
                st.dataframe(_dp_df[["fecha","par","dir","result","monto","pnl","emocion","nota"]].iloc[::-1].reset_index(drop=True),
                             use_container_width=True, hide_index=True)

                # KPI resumen
                _tot10 = len(_dp_df)
                _w10   = len(_dp_df[_dp_df["result"]=="WIN"])
                _gan10 = _dp_df["pnl"].sum()
                _r10a, _r10b, _r10c = st.columns(3)
                with _r10a: _kpi_v11("TOTAL TRADES", str(_tot10), "diario+", "#c8d8e8")
                _wr10_val = f"{_w10/_tot10*100:.1f}%" if _tot10>0 else "—"
                _wr10_col = ("#22c55e" if (_w10/_tot10>=0.55) else "#ef4444") if _tot10>0 else "#c8d8e8"
                with _r10b: _kpi_v11("WIN RATE", _wr10_val, f"{_w10}W", _wr10_col)
                with _r10c: _kpi_v11("P&L TOTAL", f"${_gan10:+.2f}", "con payout 85%", "#22c55e" if _gan10>=0 else "#ef4444")

                if st.button("🗑 Limpiar Diario+", key="m10_clear"):
                    st.session_state["diario_plus"] = []
                    st.rerun()
            else:
                st.markdown("""<div style="text-align:center;padding:40px;background:#0a1020;border:2px dashed #1a2a45;border-radius:12px;">
                  <div style="font-size:36px;margin-bottom:10px;">📓</div>
                  <div style="font-family:'Rajdhani',sans-serif;font-size:20px;color:#4a7a99;">Registrá tu primera operación con estado emocional</div>
                </div>""", unsafe_allow_html=True)

# ================================================================
# FOOTER
# ================================================================
st.markdown(f"""
<div style="text-align:center;margin-top:24px;padding:14px;border-top:1px solid #1e3050;">
  <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#2a3a55;letter-spacing:2px;">
    QQE COMMAND V7 · HECTOR TRADING SYSTEM · Capital: ${st.session_state.capital:.2f} · Objetivo: $50/dia
  </div>
</div>""", unsafe_allow_html=True)
