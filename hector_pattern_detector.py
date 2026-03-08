# HECTOR PATTERN DETECTOR v5
# Sistema Profesional de Reconocimiento de Patrones
# by Hector Trading — IQ Option M15
#
# v5 — Mejoras por pedido de Hector:
#   - Gestion de Capital y Riesgo (pestaña CAPITAL)
#   - Stop Loss diario automatico con bloqueo de radar
#   - Auto-Refresh configurable (1/5/15 min)
#   - Selector de horario de operacion
#   - Alertas sonoras cuando Score > 80%
#   - ATR extremo — aviso de volatilidad peligrosa
#   - Soportes y Resistencias dinamicos (ultimos 100 periodos)
#   - Score de confluencia aumenta si patron ocurre cerca de SR
#
# INSTALACION: pip install streamlit requests pandas numpy yfinance streamlit-autorefresh
# EJECUCION:   streamlit run hector_pattern_detector.py

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timezone, date
import requests
import streamlit.components.v1 as components_v1
import base64
try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_OK = True
except ImportError:
    AUTOREFRESH_OK = False

st.set_page_config(
    page_title="Hector Pattern Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"  # collapsed por defecto en iPhone
)

# ================================================================
# CSS
# ================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=Share+Tech+Mono&family=Inter:wght@400;500;600&display=swap');

html, body, .stApp { background:#e8f0f7 !important; }
.stApp { font-family:'Inter',sans-serif; color:#1a2940; }
[data-testid="stSidebar"] { background:#f0f6fc !important; border-right:1px solid #bdd4e8 !important; }

.stTabs [data-baseweb="tab-list"] { background:#f0f6fc; border-bottom:2px solid #bdd4e8; }
.stTabs [data-baseweb="tab"] {
    background:transparent; color:#5a7a99 !important;
    font-family:'Share Tech Mono',monospace; font-size:10px;
    letter-spacing:1px; padding:10px 12px; border:none;
}
.stTabs [aria-selected="true"] {
    background:#ddeaf5 !important; color:#0f2035 !important;
    border-bottom:2px solid #c8920a !important; font-weight:700 !important;
}

.kpi { background:#f0f6fc; border:1px solid #bdd4e8; border-radius:10px; padding:14px; text-align:center; }
.kpi-label { font-family:'Share Tech Mono',monospace; font-size:9px; color:#5a7a99; letter-spacing:2px; margin-bottom:6px; }
.kpi-value { font-family:'Rajdhani',sans-serif; font-size:30px; font-weight:700; line-height:1.1; }
.kpi-sub   { font-family:'Share Tech Mono',monospace; font-size:9px; color:#5a7a99; margin-top:3px; }

.sec { font-family:'Share Tech Mono',monospace; font-size:10px; color:#5a7a99; letter-spacing:3px;
       border-bottom:1px solid #bdd4e8; padding-bottom:6px; margin:16px 0 12px; }

.hector-brand { background:linear-gradient(135deg,#f0f6fc,#bdd4e8); border:1px solid #c8920a;
    border-radius:12px; padding:18px; text-align:center; margin-bottom:14px; }

.sesion-bar { border-radius:8px; padding:8px 16px; margin-bottom:14px;
    display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px; }

.atr-ok   { background:#e8f9f0; border:1px solid #065f46; border-radius:8px; padding:10px 14px; margin-bottom:6px; }
.atr-low  { background:#fffbf0; border:1px solid #c8920a; border-radius:8px; padding:10px 14px; margin-bottom:6px; }
.atr-flat { background:#fff0f0; border:1px solid #991b1b; border-radius:8px; padding:10px 14px; margin-bottom:6px; }

.pattern-card { background:#f0f6fc; border:1px solid #bdd4e8; border-radius:10px; padding:16px; margin-bottom:10px; }
.pattern-card.alcista { border-left:4px solid #065f46; }
.pattern-card.bajista { border-left:4px solid #991b1b; }

.alert-card { border-radius:12px; padding:18px; margin-bottom:14px; border:1px solid; }
.alert-alcista { background:#e8f9f0; border-color:#065f46; }
.alert-bajista { background:#fff0f0; border-color:#991b1b; }

.confluencia-card { border-radius:12px; padding:18px; margin-bottom:14px;
    background:linear-gradient(135deg,#fff8e7,#eaf3fa);
    border:2px solid #c8920a; box-shadow:0 0 20px rgba(200,146,10,0.2); }

.exp-badge { display:inline-block; background:#fff8e7; border:1px solid #c8920a;
    color:#fbbf24; padding:4px 10px; border-radius:20px;
    font-family:'Share Tech Mono',monospace; font-size:9px; font-weight:700; letter-spacing:1px; }

.conf-multi-badge { display:inline-block; background:#451a03; border:1px solid #c8920a;
    color:#fbbf24; padding:4px 10px; border-radius:20px;
    font-family:'Share Tech Mono',monospace; font-size:9px; font-weight:700; letter-spacing:1px; }

.vol-track { height:8px; background:#bdd4e8; border-radius:4px; overflow:hidden; margin:6px 0; }
.vol-fill-green { height:100%; border-radius:4px; background:linear-gradient(90deg,#065f46,#22c55e); }
.vol-fill-gold  { height:100%; border-radius:4px; background:linear-gradient(90deg,#92400e,#fbbf24); }
.vol-fill-red   { height:100%; border-radius:4px; background:linear-gradient(90deg,#991b1b,#ef4444); }

.asset-row { background:#f0f6fc; border:1px solid #bdd4e8; border-radius:8px;
    padding:14px 16px; margin-bottom:8px; display:flex; align-items:center;
    justify-content:space-between; flex-wrap:wrap; gap:8px; }

.rank-card { background:#f0f6fc; border:1px solid #bdd4e8; border-radius:10px;
    padding:14px; margin-bottom:8px; display:flex; align-items:center; gap:14px; }
.rank-num { font-family:'Rajdhani',sans-serif; font-size:32px; font-weight:700;
    color:#c8920a; min-width:36px; }

.hist-item { background:#f0f6fc; border:1px solid #bdd4e8; border-radius:8px;
    padding:10px 14px; margin-bottom:6px; display:flex; align-items:center;
    justify-content:space-between; flex-wrap:wrap; gap:6px; }

.conf-bar { height:6px; background:#bdd4e8; border-radius:3px; overflow:hidden; margin:6px 0; }
.conf-fill-green { height:100%; border-radius:3px; background:linear-gradient(90deg,#065f46,#22c55e); }
.conf-fill-red   { height:100%; border-radius:3px; background:linear-gradient(90deg,#991b1b,#ef4444); }
.conf-fill-gold  { height:100%; border-radius:3px; background:linear-gradient(90deg,#92400e,#fbbf24); }

.scan-dot { width:8px; height:8px; border-radius:50%; animation:blink 1s infinite; display:inline-block; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ── BOTONES GLOBALES ── */
.stButton>button {
    background:#c8920a !important; color:#0f2035 !important;
    border:none !important; border-radius:12px !important;
    font-family:'Share Tech Mono',monospace !important;
    font-size:13px !important; letter-spacing:1px !important; font-weight:700 !important;
    padding:14px 20px !important; min-height:48px !important;
    width:100% !important; touch-action:manipulation !important;
}
.stCheckbox label { color:#4a6080 !important; font-family:'Share Tech Mono',monospace !important; font-size:13px !important; }
.stRadio label { color:#4a6080 !important; font-family:'Share Tech Mono',monospace !important; font-size:13px !important; }
.stSelectbox label { color:#4a6080 !important; font-family:'Share Tech Mono',monospace !important; font-size:12px !important; }

::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-track { background:#ddeaf5; }
::-webkit-scrollbar-thumb { background:#7aaac8; border-radius:2px; }

/* ── IPHONE / MOBILE OPTIMIZATION ── */
@media (max-width:768px) {
    /* Layout base */
    html, body, .stApp { font-size:16px !important; }
    [data-testid="stSidebar"] { display:none !important; }

    /* Header compacto */
    .hector-brand { padding:12px 10px !important; margin-bottom:8px !important; }
    .hector-brand div:first-child { font-size:8px !important; }
    .hector-brand div:nth-child(2) { font-size:20px !important; letter-spacing:2px !important; }
    .hector-brand div:nth-child(3) { font-size:8px !important; }

    /* Sesion bar */
    .sesion-bar { padding:6px 10px !important; margin-bottom:8px !important; }

    /* KPIs — 2 columnas en mobile */
    .kpi { padding:10px 8px !important; }
    .kpi-value { font-size:24px !important; }
    .kpi-label { font-size:8px !important; letter-spacing:1px !important; }

    /* Tabs — mas grandes para touch */
    .stTabs [data-baseweb="tab"] {
        font-size:9px !important; padding:12px 8px !important;
        letter-spacing:0 !important;
    }

    /* Cards */
    .alert-card, .confluencia-card { padding:12px !important; margin-bottom:10px !important; }
    .asset-row { flex-direction:column !important; align-items:flex-start !important; padding:12px !important; }
    .rank-card { flex-direction:row !important; padding:12px !important; }
    .rank-num { font-size:24px !important; min-width:28px !important; }
    .hist-item { flex-direction:column !important; align-items:flex-start !important; }

    /* Botones touch-friendly */
    .stButton>button {
        font-size:15px !important; padding:16px 20px !important;
        min-height:52px !important; border-radius:14px !important;
        margin-bottom:6px !important;
    }

    /* Texto mas legible */
    .sec { font-size:9px !important; letter-spacing:1px !important; }
    .exp-badge { font-size:10px !important; padding:5px 12px !important; }
    .conf-multi-badge { font-size:10px !important; padding:5px 12px !important; }

    /* Inputs mas grandes */
    input, select, textarea { font-size:16px !important; min-height:44px !important; }

    /* Ocultar elementos no esenciales en mobile */
    .rank-num { display:none !important; }
}

/* iPhone SE y pantallas muy pequenas */
@media (max-width:380px) {
    .kpi-value { font-size:20px !important; }
    .stTabs [data-baseweb="tab"] { font-size:8px !important; padding:10px 5px !important; }
}

/* iPhone landscape */
@media (max-width:768px) and (orientation:landscape) {
    .hector-brand { padding:6px !important; }
    .kpi { padding:6px !important; }
    .kpi-value { font-size:18px !important; }
}

/* Botones de alerta — extra grandes en mobile */
@media (max-width:768px) {
    .btn-iphone {
        display:block; width:100%; padding:18px;
        font-size:16px; font-weight:700; border-radius:14px;
        text-align:center; margin:6px 0; cursor:pointer;
        touch-action:manipulation; -webkit-tap-highlight-color:transparent;
        border:none; font-family:'Share Tech Mono',monospace;
    }
    .btn-call { background:#16a34a; color:white; }
    .btn-put  { background:#dc2626; color:white; }
}
</style>
""", unsafe_allow_html=True)

# ================================================================
# SESSION STATE
# ================================================================
defaults = {
    "resultados_scan": [],
    "ultimo_scan": None,
    "alertas": [],
    "api_key": "",
    "confirmadas": set(),
    "historial": [],
    "tracker": [],
    "ia_analisis": "",
    "capital_dia": 467.86,
    "stop_loss_pct": 10,
    "perdida_dia": 0.0,
    "radar_bloqueado": False,
    "autorefresh_on": False,
    "autorefresh_min": 5,
    "hora_inicio_op": "07:00",
    "hora_fin_op": "16:00",
    "ultima_alerta_sonido": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ================================================================
# ACTIVOS
# ================================================================
ACTIVOS = {
    "XAU/USD":   {"yahoo":"GC=F",    "color":"#c8920a","tipo":"Commodity"},
    "EUR/USD":   {"yahoo":"EURUSD=X","color":"#1d4ed8","tipo":"Forex"},
    "GBP/USD":   {"yahoo":"GBPUSD=X","color":"#6d28d9","tipo":"Forex"},
    "NAS100":    {"yahoo":"NQ=F",    "color":"#0891b2","tipo":"Indice"},
    "BTC/USD":   {"yahoo":"BTC-USD", "color":"#f59e0b","tipo":"Crypto"},
    "CRUDE OIL": {"yahoo":"CL=F",   "color":"#16a34a","tipo":"Commodity"},
}

# peso: importancia en el score de confluencia (3=mayor, 1=menor)
# min_exp: minutos de expiracion recomendada
PATRONES = {
    "Engulfing + EMA":       {"efectividad":72,"desc":"Vela envolvente en EMA100/200","min_exp":15,"tf":"M15","peso":3},
    "Pin Bar en SR":         {"efectividad":70,"desc":"Mecha larga en soporte/resistencia","min_exp":30,"tf":"M15","peso":3},
    "Divergencia RSI":       {"efectividad":68,"desc":"Precio vs RSI divergen","min_exp":30,"tf":"M15","peso":2},
    "Fakey":                 {"efectividad":66,"desc":"Falsa ruptura con reversion","min_exp":15,"tf":"M15","peso":2},
    "Inside Bar Ruptura":    {"efectividad":67,"desc":"Compresion + ruptura de rango","min_exp":15,"tf":"M15","peso":2},
    "Tres Soldados/Cuervos": {"efectividad":63,"desc":"3 velas consecutivas de momentum","min_exp":15,"tf":"M15","peso":1},
    "Estrella Manana/Tarde": {"efectividad":65,"desc":"Patron 3 velas de agotamiento","min_exp":30,"tf":"M15","peso":2},
    "Consolidacion Ruptura": {"efectividad":64,"desc":"Flag/Pennant post-impulso","min_exp":15,"tf":"M15","peso":1},
}

def expiracion_str(min_exp):
    return f"{min_exp} min"

# ================================================================
# SESION DE MERCADO
# ================================================================
def get_sesion():
    h = datetime.now(timezone.utc).hour
    if   7 <= h < 10:  return "LONDRES",       "#34d399","#e8f9f0","Activa — mejor momento"
    elif 13 <= h < 16: return "NUEVA YORK",    "#34d399","#e8f9f0","Activa — alta liquidez"
    elif 16 <= h < 17: return "SOLAPAMIENTO",  "#fbbf24","#451a03","Alta volatilidad, cuidado"
    elif 10 <= h < 13: return "INTERBANCARIA", "#fbbf24","#451a03","Liquidez moderada"
    else:              return "CERRADA",        "#f87171","#fff0f0","No operar binarias"

# ================================================================
# DATOS
# ================================================================
@st.cache_data(ttl=300)
def obtener_datos(simbolo, periodo="60d", intervalo="15m"):
    try:
        import yfinance as yf
        df = yf.Ticker(simbolo).history(period=periodo, interval=intervalo)
        if df.empty: return None
        df = df[["Open","High","Low","Close","Volume"]].copy()
        df.columns = ["apertura","maximo","minimo","cierre","volumen"]
        return df.dropna()
    except:
        return None

# ================================================================
# INDICADORES
# ================================================================
def calc_ema(serie, p):
    return serie.ewm(span=p, adjust=False).mean()

def calc_rsi(serie, p=14):
    d = serie.diff()
    g = d.clip(lower=0).ewm(span=p, adjust=False).mean()
    l = (-d.clip(upper=0)).ewm(span=p, adjust=False).mean()
    return 100 - (100 / (1 + g / (l + 1e-10)))

def calc_atr(df, p=14):
    cp = df["cierre"].shift(1)
    tr = pd.concat([
        df["maximo"] - df["minimo"],
        (df["maximo"] - cp).abs(),
        (df["minimo"] - cp).abs()
    ], axis=1).max(axis=1)
    return tr.ewm(span=p, adjust=False).mean()

def calc_macd(serie, rapido=12, lento=26, señal=9):
    linea = calc_ema(serie, rapido) - calc_ema(serie, lento)
    sig   = calc_ema(linea, señal)
    hist  = linea - sig
    return linea, sig, hist

def analizar_volatilidad(df):
    atr  = calc_atr(df)
    act  = atr.iloc[-1]
    prom = atr.iloc[-50:].mean()
    pct  = (act / prom) * 100 if prom > 0 else 100
    if   pct >= 180: return "EXTREMA", pct, "⚠️ Volatilidad extrema — PELIGRO",       "#f97316","atr-flat"
    elif pct >= 90:  return "FUERTE",  pct, "Volatilidad optima — OPERAR",             "#34d399","atr-ok"
    elif pct >= 60:  return "NORMAL",  pct, "Volatilidad aceptable — Con precaucion",  "#fbbf24","atr-low"
    else:            return "PLANO",   pct, "Mercado sin fuerza — NO OPERAR",          "#f87171","atr-flat"

def calcular_soportes_resistencias(df, periodos=100):
    """Calcula niveles S/R basados en pivots de los ultimos N periodos"""
    datos = df.tail(periodos)
    precios = datos["cierre"].values
    maximos = datos["maximo"].values
    minimos = datos["minimo"].values

    # Pivots: puntos donde el precio cambia de direccion
    resistencias = []
    soportes     = []
    for i in range(2, len(maximos)-2):
        if maximos[i] > maximos[i-1] and maximos[i] > maximos[i-2] and maximos[i] > maximos[i+1] and maximos[i] > maximos[i+2]:
            resistencias.append(maximos[i])
        if minimos[i] < minimos[i-1] and minimos[i] < minimos[i-2] and minimos[i] < minimos[i+1] and minimos[i] < minimos[i+2]:
            soportes.append(minimos[i])

    # Tomar los 3 mas recientes/relevantes
    resistencias = sorted(set([round(r, 4) for r in resistencias]))[-3:]
    soportes     = sorted(set([round(s, 4) for s in soportes]))[:3]
    return soportes, resistencias

def patron_cerca_sr(precio_actual, soportes, resistencias, tolerancia_pct=0.003):
    """Devuelve True y tipo si el patron ocurre cerca de un nivel S/R"""
    for s in soportes:
        if abs(precio_actual - s) / s < tolerancia_pct:
            return True, "SOPORTE"
    for r in resistencias:
        if abs(precio_actual - r) / r < tolerancia_pct:
            return True, "RESISTENCIA"
    return False, ""

def filtro_tendencia(df):
    """Tendencia usando EMA200 + confirmacion MACD"""
    ema200 = calc_ema(df["cierre"], 200)
    _, _, macd_hist = calc_macd(df["cierre"])
    u = df["cierre"].iloc[-1]
    e = ema200.iloc[-1]
    mh = macd_hist.iloc[-1]
    precio_arriba = u > e * 1.001
    precio_abajo  = u < e * 0.999
    # Tendencia confirmada: precio + MACD en misma direccion
    if precio_arriba and mh > 0:   return "ALCISTA",       "#34d399"
    elif precio_abajo and mh < 0:  return "BAJISTA",       "#f87171"
    elif precio_arriba or mh > 0:  return "ALCISTA (deb)", "#6ee7b7"  # señal debil
    elif precio_abajo  or mh < 0:  return "BAJISTA (deb)", "#fca5a5"
    else:                          return "LATERAL",        "#fbbf24"

# ================================================================
# DETECTORES DE PATRONES
# ================================================================
def detectar_engulfing(df):
    res = []; e = calc_ema(df["cierre"], 100)
    for i in range(1, len(df)):
        c, p = df.iloc[i], df.iloc[i-1]
        cerca = abs(c["cierre"] - e.iloc[i]) / e.iloc[i] < 0.003
        if (p["cierre"] < p["apertura"] and c["cierre"] > c["apertura"] and
            c["apertura"] < p["cierre"] and c["cierre"] > p["apertura"] and
            c["cierre"] > e.iloc[i] and cerca):
            res.append({"idx":i,"dir":"ALCISTA","conf":75,"patron":"Engulfing + EMA"})
        elif (p["cierre"] > p["apertura"] and c["cierre"] < c["apertura"] and
              c["apertura"] > p["cierre"] and c["cierre"] < p["apertura"] and
              c["cierre"] < e.iloc[i] and cerca):
            res.append({"idx":i,"dir":"BAJISTA","conf":75,"patron":"Engulfing + EMA"})
    return res[-3:] if res else []

def detectar_pin_bar(df):
    res = []; sm = df["maximo"].rolling(20).max().shift(1); si = df["minimo"].rolling(20).min().shift(1)
    for i in range(20, len(df)):
        c = df.iloc[i]; cu = abs(c["cierre"]-c["apertura"]); to = c["maximo"]-c["minimo"]
        if to == 0: continue
        ms = c["maximo"] - max(c["apertura"], c["cierre"])
        mi = min(c["apertura"], c["cierre"]) - c["minimo"]
        if mi > cu*2.5 and mi > ms*2 and abs(c["minimo"] - si.iloc[i])/(si.iloc[i]+1e-10) < 0.002:
            res.append({"idx":i,"dir":"ALCISTA","conf":70,"patron":"Pin Bar en SR"})
        elif ms > cu*2.5 and ms > mi*2 and abs(c["maximo"] - sm.iloc[i])/(sm.iloc[i]+1e-10) < 0.002:
            res.append({"idx":i,"dir":"BAJISTA","conf":70,"patron":"Pin Bar en SR"})
    return res[-3:] if res else []

def detectar_fakey(df):
    res = []
    for i in range(3, len(df)):
        p3,p2,p1,c = df.iloc[i-3],df.iloc[i-2],df.iloc[i-1],df.iloc[i]
        if not (p2["maximo"] < p3["maximo"] and p2["minimo"] > p3["minimo"]): continue
        if p1["maximo"] > p3["maximo"] and c["cierre"] < p3["maximo"] and c["cierre"] < p1["cierre"]:
            res.append({"idx":i,"dir":"BAJISTA","conf":66,"patron":"Fakey"})
        elif p1["minimo"] < p3["minimo"] and c["cierre"] > p3["minimo"] and c["cierre"] > p1["cierre"]:
            res.append({"idx":i,"dir":"ALCISTA","conf":66,"patron":"Fakey"})
    return res[-3:] if res else []

def detectar_div_rsi(df):
    res = []; rsi = calc_rsi(df["cierre"]); v = 20
    for i in range(v+5, len(df)):
        pw = df["cierre"].iloc[i-v:i]; rw = rsi.iloc[i-v:i]
        im = pw.idxmax(); ii = pw.idxmin()
        if df["cierre"].iloc[i] >= df["cierre"].loc[im] and rsi.iloc[i] < rsi.loc[im] - 5:
            res.append({"idx":i,"dir":"BAJISTA","conf":68,"patron":"Divergencia RSI"})
        elif df["cierre"].iloc[i] <= df["cierre"].loc[ii] and rsi.iloc[i] > rsi.loc[ii] + 5:
            res.append({"idx":i,"dir":"ALCISTA","conf":68,"patron":"Divergencia RSI"})
    return res[-3:] if res else []

def detectar_inside(df):
    res = []
    for i in range(2, len(df)):
        p2,p1,c = df.iloc[i-2],df.iloc[i-1],df.iloc[i]
        if p1["maximo"] < p2["maximo"] and p1["minimo"] > p2["minimo"]:
            if c["cierre"] > p2["maximo"]:   res.append({"idx":i,"dir":"ALCISTA","conf":67,"patron":"Inside Bar Ruptura"})
            elif c["cierre"] < p2["minimo"]: res.append({"idx":i,"dir":"BAJISTA","conf":67,"patron":"Inside Bar Ruptura"})
    return res[-3:] if res else []

def detectar_tres(df):
    res = []
    for i in range(2, len(df)):
        c0,c1,c2 = df.iloc[i-2],df.iloc[i-1],df.iloc[i]
        if (c0["cierre"]>c0["apertura"] and c1["cierre"]>c1["apertura"] and c2["cierre"]>c2["apertura"] and
            c1["cierre"]>c0["cierre"] and c2["cierre"]>c1["cierre"]):
            res.append({"idx":i,"dir":"ALCISTA","conf":63,"patron":"Tres Soldados/Cuervos"})
        elif (c0["cierre"]<c0["apertura"] and c1["cierre"]<c1["apertura"] and c2["cierre"]<c2["apertura"] and
              c1["cierre"]<c0["cierre"] and c2["cierre"]<c1["cierre"]):
            res.append({"idx":i,"dir":"BAJISTA","conf":63,"patron":"Tres Soldados/Cuervos"})
    return res[-3:] if res else []

def detectar_estrella(df):
    res = []
    for i in range(2, len(df)):
        c0,c1,c2 = df.iloc[i-2],df.iloc[i-1],df.iloc[i]
        b0 = abs(c0["cierre"]-c0["apertura"]); b1 = abs(c1["cierre"]-c1["apertura"]); b2 = abs(c2["cierre"]-c2["apertura"])
        if (c0["cierre"]<c0["apertura"] and b0>b1*2 and c2["cierre"]>c2["apertura"] and
            b2>b1*2 and c2["cierre"]>(c0["apertura"]+c0["cierre"])/2):
            res.append({"idx":i,"dir":"ALCISTA","conf":65,"patron":"Estrella Manana/Tarde"})
        elif (c0["cierre"]>c0["apertura"] and b0>b1*2 and c2["cierre"]<c2["apertura"] and
              b2>b1*2 and c2["cierre"]<(c0["apertura"]+c0["cierre"])/2):
            res.append({"idx":i,"dir":"BAJISTA","conf":65,"patron":"Estrella Manana/Tarde"})
    return res[-3:] if res else []

def detectar_consolidacion(df):
    res = []; v = 10
    for i in range(v+2, len(df)):
        seg  = df.iloc[i-v:i]
        rango = seg["maximo"].max() - seg["minimo"].min()
        prom  = (seg["maximo"] - seg["minimo"]).mean()
        if rango < prom * v * 0.5:
            c = df.iloc[i]
            if c["cierre"] > seg["maximo"].max():   res.append({"idx":i,"dir":"ALCISTA","conf":64,"patron":"Consolidacion Ruptura"})
            elif c["cierre"] < seg["minimo"].min(): res.append({"idx":i,"dir":"BAJISTA","conf":64,"patron":"Consolidacion Ruptura"})
    return res[-3:] if res else []

def ejecutar_patrones(df):
    todos = []
    for det in [detectar_engulfing, detectar_pin_bar, detectar_fakey, detectar_div_rsi,
                detectar_inside, detectar_tres, detectar_estrella, detectar_consolidacion]:
        try: todos.extend(det(df))
        except: pass
    recientes = [r for r in todos if r["idx"] >= len(df)-10]
    recientes.sort(key=lambda x: x["conf"], reverse=True)
    return recientes

def calcular_confluencia(patrones_alineados):
    """
    FIX v4: solo considera patrones en la MISMA direccion dominante.
    Expiracion = la mayor de los patrones involucrados.
    """
    if not patrones_alineados: return 0, "SIN SEÑAL", 15, "ALCISTA"

    # Determinar direccion dominante
    n_alc = sum(1 for p in patrones_alineados if p["dir"] == "ALCISTA")
    n_baj = sum(1 for p in patrones_alineados if p["dir"] == "BAJISTA")
    dir_dom = "ALCISTA" if n_alc >= n_baj else "BAJISTA"

    # Filtrar solo patrones de la direccion dominante
    patrones_dom = [p for p in patrones_alineados if p["dir"] == dir_dom]
    n = len(patrones_dom)

    peso_total = sum(PATRONES.get(p["patron"],{}).get("peso",1) for p in patrones_dom)
    conf_prom  = sum(p["conf"] for p in patrones_dom) / n
    score = min(100, peso_total * 10 + conf_prom * 0.5)

    # Expiracion: la mayor de los patrones involucrados
    max_exp = max(PATRONES.get(p["patron"],{}).get("min_exp", 15) for p in patrones_dom)

    if n >= 3: label = "CONFLUENCIA MAXIMA"
    elif n == 2: label = "DOBLE CONFLUENCIA"
    else: label = "SEÑAL SIMPLE"

    return score, label, max_exp, dir_dom

def calcular_score_activo(patrones_validos, vol_est, tendencia, sr_bonus=0):
    """v5: incluye bonus por patron cerca de S/R"""
    pat_alineados = [p for p in patrones_validos if p.get("alineado")]
    if not pat_alineados: return 0
    score, _, _, _ = calcular_confluencia(pat_alineados)
    vol_bonus  = {"FUERTE":20,"NORMAL":10,"PLANO":0,"EXTREMA":0}.get(vol_est, 0)
    tend_bonus = 0 if "LATERAL" in tendencia else 10
    return score + vol_bonus + tend_bonus + sr_bonus

# ================================================================
# SIDEBAR
# ================================================================
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:14px 0 10px;border-bottom:1px solid #bdd4e8;margin-bottom:14px;'>
    <div style='font-family:"Rajdhani",sans-serif;font-size:22px;font-weight:700;color:#c8920a;letter-spacing:3px;'>HECTOR</div>
    <div style='font-family:"Share Tech Mono",monospace;font-size:9px;color:#5a7a99;letter-spacing:2px;'>PATTERN DETECTOR v4</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:9px;color:#5a7a99;letter-spacing:2px;margin-bottom:4px;">CLAVE API ANTHROPIC</div>', unsafe_allow_html=True)
    api_in = st.text_input("Clave API", value=st.session_state.api_key,
                           placeholder="sk-ant-api03-...", type="password", label_visibility="collapsed")
    if api_in: st.session_state.api_key = api_in
    ia_ok_sb = st.session_state.api_key.startswith("sk-ant-")
    st.markdown(f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:10px;color:{"#34d399" if ia_ok else "#475569"};margin-bottom:8px;">{"IA ACTIVA" if ia_ok_sb else "Sin clave"}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:9px;color:#5a7a99;letter-spacing:2px;margin-bottom:8px;">ACTIVOS</div>', unsafe_allow_html=True)
    activos_sel = [a for a in ACTIVOS if st.checkbox(a, value=True, key=f"chk_{a}")]

    st.markdown("---")
    confianza_min = st.slider("Confianza minima %", 50, 80, 63, 1)
    solo_confluencia = st.checkbox("Solo mostrar confluencias", value=False)

    # ── AUTO-REFRESH ──
    st.markdown("---")
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#5a7a99;letter-spacing:2px;margin-bottom:6px;">AUTO-SCAN</div>', unsafe_allow_html=True)
    ar_on = st.checkbox("Activar escaneo automatico", value=st.session_state.autorefresh_on, key="ar_chk")
    st.session_state.autorefresh_on = ar_on
    if ar_on:
        ar_min = st.selectbox("Frecuencia", [1, 5, 15], index=[1,5,15].index(st.session_state.autorefresh_min) if st.session_state.autorefresh_min in [1,5,15] else 1, key="ar_sel", format_func=lambda x: f"Cada {x} min")
        st.session_state.autorefresh_min = ar_min
        if AUTOREFRESH_OK:
            st_autorefresh(interval=ar_min * 60 * 1000, key="autoref")
        else:
            st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#f87171;">Instalar: pip install streamlit-autorefresh</div>', unsafe_allow_html=True)
        # Horario de operacion
        st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#5a7a99;margin-top:6px;margin-bottom:4px;">HORARIO ACTIVO</div>', unsafe_allow_html=True)
        hi = st.text_input("Desde (HH:MM)", value=st.session_state.hora_inicio_op, key="hi", label_visibility="collapsed", placeholder="09:00")
        hf = st.text_input("Hasta (HH:MM)", value=st.session_state.hora_fin_op,    key="hf", label_visibility="collapsed", placeholder="16:00")
        if hi: st.session_state.hora_inicio_op = hi
        if hf: st.session_state.hora_fin_op    = hf

    # ── CAPITAL Y RIESGO ──
    st.markdown("---")
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#5a7a99;letter-spacing:2px;margin-bottom:6px;">CAPITAL Y RIESGO</div>', unsafe_allow_html=True)
    capital_in = st.number_input("Capital del dia USD", min_value=10.0, max_value=100000.0,
        value=float(st.session_state.capital_dia), step=10.0, key="cap_input", label_visibility="collapsed")
    st.session_state.capital_dia = capital_in
    sl_pct = st.slider("Stop Loss diario %", 5, 30, int(st.session_state.stop_loss_pct), 1, key="sl_slider")
    st.session_state.stop_loss_pct = sl_pct
    entrada_1pct = capital_in * 0.01
    entrada_2pct = capital_in * 0.02
    sl_monto     = capital_in * sl_pct / 100
    perdida = st.session_state.perdida_dia
    radar_ok = perdida < sl_monto
    st.session_state.radar_bloqueado = not radar_ok
    pct_usado = min(100, int(perdida / sl_monto * 100)) if sl_monto > 0 else 0
    barra_col = "#34d399" if pct_usado < 50 else ("#fbbf24" if pct_usado < 80 else "#f87171")
    st.markdown(f"""
    <div style="background:#f0f6fc;border:1px solid #bdd4e8;border-radius:8px;padding:10px;margin-bottom:6px;">
      <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
        <span style="font-family:Share Tech Mono,monospace;font-size:9px;color:#5a7a99;">ENTRADA 1%</span>
        <span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;color:#1a2940;">${entrada_1pct:.2f}</span>
      </div>
      <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
        <span style="font-family:Share Tech Mono,monospace;font-size:9px;color:#5a7a99;">ENTRADA 2%</span>
        <span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;color:#c8920a;">${entrada_2pct:.2f}</span>
      </div>
      <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#5a7a99;margin-bottom:3px;">STOP LOSS: ${sl_monto:.2f} ({sl_pct}%)</div>
      <div style="height:6px;background:#bdd4e8;border-radius:3px;overflow:hidden;">
        <div style="height:100%;width:{pct_usado}%;background:{barra_col};border-radius:3px;transition:width 0.3s;"></div>
      </div>
      <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:{barra_col};margin-top:3px;">Perdida: ${perdida:.2f} / ${sl_monto:.2f}</div>
    </div>""", unsafe_allow_html=True)
    if not radar_ok:
        st.markdown('<div style="background:#fff0f0;border:2px solid #dc2626;border-radius:8px;padding:8px;text-align:center;font-family:Share Tech Mono,monospace;font-size:10px;color:#dc2626;font-weight:700;">🛑 STOP LOSS ALCANZADO<br>RADAR BLOQUEADO</div>', unsafe_allow_html=True)
    c_p1, c_p2 = st.columns(2)
    with c_p1:
        if st.button(f"+ Perdida", key="add_loss"):
            st.session_state.perdida_dia += entrada_2pct
            st.rerun()
    with c_p2:
        if st.button("Reset dia", key="reset_perdida"):
            st.session_state.perdida_dia = 0.0
            st.session_state.radar_bloqueado = False
            st.rerun()

    st.markdown("---")
    # Tracker rapido en sidebar
    wins   = len([t for t in st.session_state.tracker if t["resultado"]=="WIN"])
    losses = len([t for t in st.session_state.tracker if t["resultado"]=="LOSS"])
    total  = wins + losses
    wr     = int(wins/total*100) if total > 0 else 0
    col_wr = "#34d399" if wr >= 60 else ("#fbbf24" if wr >= 50 else "#f87171")
    st.markdown(f"""
    <div style='background:#e8f0f7;border:1px solid #bdd4e8;border-radius:8px;padding:10px;text-align:center;'>
    <div style='font-family:"Share Tech Mono",monospace;font-size:9px;color:#5a7a99;letter-spacing:2px;margin-bottom:6px;'>TRACKER DEL DIA</div>
    <div style='display:flex;justify-content:space-around;'>
    <div><div style='font-family:"Rajdhani",sans-serif;font-size:20px;font-weight:700;color:#34d399;'>{wins}</div>
    <div style='font-family:"Share Tech Mono",monospace;font-size:8px;color:#5a7a99;'>WINS</div></div>
    <div><div style='font-family:"Rajdhani",sans-serif;font-size:20px;font-weight:700;color:#f87171;'>{losses}</div>
    <div style='font-family:"Share Tech Mono",monospace;font-size:8px;color:#5a7a99;'>LOSS</div></div>
    <div><div style='font-family:"Rajdhani",sans-serif;font-size:20px;font-weight:700;color:{col_wr};'>{wr}%</div>
    <div style='font-family:"Share Tech Mono",monospace;font-size:8px;color:#5a7a99;'>WIN%</div></div>
    </div></div>""", unsafe_allow_html=True)

# ================================================================
# HEADER + BARRA DE SESION
# ================================================================
st.markdown("""
<div class="hector-brand">
  <div style='font-family:"Share Tech Mono",monospace;font-size:9px;color:#5a7a99;letter-spacing:3px;margin-bottom:6px;'>SISTEMA PROFESIONAL DE RECONOCIMIENTO DE PATRONES</div>
  <div style='font-family:"Rajdhani",sans-serif;font-size:26px;font-weight:700;color:#c8920a;letter-spacing:4px;'>HECTOR PATTERN DETECTOR v5</div>
  <div style='font-family:"Share Tech Mono",monospace;font-size:9px;color:#3a5570;margin-top:4px;letter-spacing:2px;'>
  8 PATRONES · 6 ACTIVOS · M15 · ATR · SR · CAPITAL · AUTO-SCAN · SONIDO
  </div>
</div>""", unsafe_allow_html=True)

# Barra de sesion
ses_nom, ses_col, ses_bg, ses_desc = get_sesion()
hora_utc = datetime.now(timezone.utc).strftime("%H:%M UTC")
st.markdown(f"""
<div class="sesion-bar" style="background:{ses_bg};border:1px solid {ses_col}44;">
  <div style="display:flex;align-items:center;gap:10px;">
    <span class="scan-dot" style="background:{ses_col};"></span>
    <span style="font-family:'Share Tech Mono',monospace;font-size:11px;font-weight:700;color:{ses_col};">SESION {ses_nom}</span>
    <span style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#3a5570;">{ses_desc}</span>
  </div>
  <span style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#5a7a99;">{hora_utc}</span>
</div>""", unsafe_allow_html=True)

# API Key visible en mobile — arriba del boton escanear
ia_ok = st.session_state.api_key.startswith("sk-ant-")
if not ia_ok:
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#c8920a;margin-bottom:4px;">CLAVE API ANTHROPIC</div>', unsafe_allow_html=True)
    api_mobile = st.text_input("API Key", value=st.session_state.api_key,
        placeholder="sk-ant-api03-...", type="password",
        label_visibility="collapsed", key="api_mobile")
    if api_mobile:
        st.session_state.api_key = api_mobile
        ia_ok = api_mobile.startswith("sk-ant-")
        st.rerun()
else:
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#16a34a;margin-bottom:6px;">IA ACTIVA</div>', unsafe_allow_html=True)

# Boton escanear
col_btn, col_est = st.columns([1,3])
with col_btn:
    escanear = st.button("ESCANEAR MERCADO", key="btn_scan")
with col_est:
    if st.session_state.ultimo_scan:
        n_conf = len([a for a in st.session_state.alertas if a.get("n_patrones",1)>=2])
        nc = "#34d399" if st.session_state.alertas else "#475569"
        st.markdown(f"""<div style="display:flex;align-items:center;gap:8px;margin-top:8px;flex-wrap:wrap;">
          <span class="scan-dot" style="background:#34d399;"></span>
          <span style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#5a7a99;">Ultimo: {st.session_state.ultimo_scan}</span>
          <span style="font-family:'Share Tech Mono',monospace;font-size:10px;color:{nc};">{len(st.session_state.alertas)} alertas</span>
          {f'<span style="font-family:\'Share Tech Mono\',monospace;font-size:10px;color:#c8920a;">{n_conf} confluencias</span>' if n_conf>0 else ''}
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="margin-top:8px;font-family:\'Share Tech Mono\',monospace;font-size:10px;color:#5a7a99;">Presiona ESCANEAR para analizar el mercado</div>', unsafe_allow_html=True)

# ================================================================
# ESCANEO
# ================================================================
if escanear:
    # Verificar horario de operacion
    hora_actual = datetime.now(timezone.utc).strftime("%H:%M")
    en_horario = True
    if st.session_state.get("autorefresh_on") and st.session_state.get("hora_inicio_op") and st.session_state.get("hora_fin_op"):
        hi = st.session_state.hora_inicio_op
        hf = st.session_state.hora_fin_op
        en_horario = hi <= hora_actual <= hf

    if st.session_state.get("radar_bloqueado"):
        st.error("🛑 RADAR BLOQUEADO — Stop Loss diario alcanzado. Reseteá el contador para continuar.")
    elif not en_horario:
        st.warning(f"⏰ Fuera del horario de operacion configurado ({st.session_state.hora_inicio_op} - {st.session_state.hora_fin_op} UTC)")
    else:
        todos_res = []; prog = st.progress(0); txt = st.empty()

        for idx, activo in enumerate(activos_sel):
            info = ACTIVOS[activo]
            txt.markdown(f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:10px;color:#c8920a;">Escaneando {activo}...</div>', unsafe_allow_html=True)
            prog.progress((idx+1) / max(len(activos_sel), 1))

            df = obtener_datos(info["yahoo"])
            if df is not None and len(df) > 200:
                patrones  = ejecutar_patrones(df)
                tend, tend_col = filtro_tendencia(df)
                vol_est, vol_pct, vol_msg, vol_col, vol_cls = analizar_volatilidad(df)
                precio = df["cierre"].iloc[-1]
                rsi_v  = calc_rsi(df["cierre"]).iloc[-1]
                soportes, resistencias = calcular_soportes_resistencias(df)
                cerca_sr, tipo_sr = patron_cerca_sr(precio, soportes, resistencias)
                sr_bonus = 15 if cerca_sr else 0

                patrones = [p for p in patrones if p["conf"] >= confianza_min]
                for p in patrones:
                    es_alc_tend = "ALCISTA" in tend
                    es_baj_tend = "BAJISTA" in tend
                    p["alineado"] = (es_alc_tend and p["dir"]=="ALCISTA") or (es_baj_tend and p["dir"]=="BAJISTA")
                    p["min_exp"]  = PATRONES.get(p["patron"],{}).get("min_exp", 15)

                patrones_validos = [] if vol_est in ("PLANO","EXTREMA") else patrones
                pat_alineados    = [p for p in patrones_validos if p.get("alineado")]
                conf_score, conf_label, max_exp, dir_dom = calcular_confluencia(pat_alineados)
                score = calcular_score_activo(patrones_validos, vol_est, tend, sr_bonus)

                todos_res.append({
                    "activo":activo,"info":info,"patrones":patrones_validos,
                    "tendencia":tend,"tend_col":tend_col,
                    "vol_est":vol_est,"vol_pct":vol_pct,"vol_msg":vol_msg,"vol_col":vol_col,"vol_cls":vol_cls,
                    "precio":precio,"rsi":rsi_v,"sin_datos":False,
                    "mercado_plano":vol_est in ("PLANO","EXTREMA"),
                    "tiene_senal":len(pat_alineados)>0,
                    "n_alineados":len(pat_alineados),
                    "conf_score":conf_score,"conf_label":conf_label,
                    "dir_dom":dir_dom,"max_exp":max_exp,
                    "score":score,
                    "soportes":soportes,"resistencias":resistencias,
                    "cerca_sr":cerca_sr,"tipo_sr":tipo_sr,
                })
            else:
                todos_res.append({
                    "activo":activo,"info":info,"patrones":[],"tendencia":"SIN DATOS",
                    "tend_col":"#475569","vol_est":"SIN DATOS","vol_pct":0,
                    "vol_msg":"Sin datos","vol_col":"#475569","vol_cls":"atr-flat",
                    "precio":0,"rsi":50,"sin_datos":True,"mercado_plano":False,
                    "tiene_senal":False,"n_alineados":0,"conf_score":0,
                    "conf_label":"SIN SEÑAL","dir_dom":"ALCISTA","max_exp":15,"score":0,
                    "soportes":[],"resistencias":[],"cerca_sr":False,"tipo_sr":"",
                })

        prog.empty(); txt.empty()
    todos_res.sort(key=lambda x: x["score"], reverse=True)
    st.session_state.resultados_scan = todos_res

    # Construir alertas
    alertas = []
    hora_scan = datetime.now().strftime("%H:%M")
    for r in todos_res:
        pat_al = [p for p in r["patrones"] if p.get("alineado") and p["conf"] >= 65]
        if not pat_al or r["mercado_plano"]: continue
        conf_score, conf_label, max_exp, dir_dom = calcular_confluencia(pat_al)
        nombres = ", ".join(list(dict.fromkeys([p["patron"] for p in pat_al]))[:3])
        alerta_id = f"{r['activo']}_{hora_scan}"

        alertas.append({
            "id":alerta_id,
            "activo":r["activo"],"dir":dir_dom,
            "conf":int(conf_score),"precio":r["precio"],
            "expiracion":expiracion_str(max_exp),
            "vol_est":r["vol_est"],"hora":hora_scan,
            "n_patrones":len(pat_al),"conf_label":conf_label,
            "patrones_nombres":nombres,
        })

        # FIX: evitar duplicados en historial por activo+hora
        historial_actual = st.session_state.get("historial", [])
        ya_existe = any(h["activo"]==r["activo"] and h["hora"]==hora_scan for h in historial_actual)
        if not ya_existe:
            st.session_state.historial.append({
                "fecha":date.today().strftime("%d/%m"),"hora":hora_scan,
                "activo":r["activo"],"dir":dir_dom,
                "conf":int(conf_score),"conf_label":conf_label,
                "n_patrones":len(pat_al),"expiracion":expiracion_str(max_exp),
                "resultado":None,
            })

        alertas.sort(key=lambda x: x["conf"], reverse=True)
        st.session_state.alertas  = alertas
        st.session_state.ultimo_scan = datetime.now().strftime("%H:%M:%S")
        st.session_state.confirmadas = set()
        st.session_state.ia_analisis = ""

        # Alerta sonora si hay señal con Score > 80
        alertas_fuertes = [a for a in alertas if a["conf"] >= 80]
        if alertas_fuertes:
            mejor = alertas_fuertes[0]
            alerta_key = f"{mejor['activo']}_{mejor['hora']}"
            if alerta_key != st.session_state.get("ultima_alerta_sonido",""):
                st.session_state.ultima_alerta_sonido = alerta_key
                # Audio embebido HTML — beep de alerta
                audio_html = """
                <audio autoplay>
                  <source src="data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAA
EAAQARAAIAIgACABAAZGF0YVAGAACBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGB
gcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwf//////////AQIDBAUGB
wgJCgsM" type="audio/wav">
                </audio>
                <script>
                try {
                  var ctx = new (window.AudioContext || window.webkitAudioContext)();
                  var osc = ctx.createOscillator();
                  var gain = ctx.createGain();
                  osc.connect(gain);
                  gain.connect(ctx.destination);
                  osc.frequency.setValueAtTime(880, ctx.currentTime);
                  osc.frequency.setValueAtTime(660, ctx.currentTime + 0.15);
                  osc.frequency.setValueAtTime(880, ctx.currentTime + 0.3);
                  gain.gain.setValueAtTime(0.3, ctx.currentTime);
                  gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.5);
                  osc.start(ctx.currentTime);
                  osc.stop(ctx.currentTime + 0.5);
                } catch(e) {}
                </script>
                """
                components_v1.html(audio_html, height=0)
        st.rerun()

# ================================================================
# TABS
# ================================================================
tab_radar, tab_ranking, tab_alert, tab_hist, tab_tracker, tab_atr, tab_stats, tab_capital, tab_confirmar = st.tabs([
    "RADAR","RANKING","ALERTAS","HISTORIAL","TRACKER","VOLATILIDAD ATR","ESTADISTICAS","CAPITAL","📷 CONFIRMAR"
])

# ── RADAR ──────────────────────────────────────
with tab_radar:
    if not st.session_state.resultados_scan:
        st.markdown("<div style='text-align:center;padding:60px;'><div style='font-size:48px;'>🔍</div><div style='font-family:\"Rajdhani\",sans-serif;font-size:24px;color:#5a7a99;margin-top:12px;'>Presiona ESCANEAR MERCADO</div><div style='font-family:\"Share Tech Mono\",monospace;font-size:11px;color:#6a8aaa;margin-top:6px;'>8 patrones · 6 activos · ATR · MACD · Confluencia · Ranking</div></div>", unsafe_allow_html=True)
    else:
        t_pat  = sum(len(r["patrones"]) for r in st.session_state.resultados_scan)
        n_sig  = sum(1 for r in st.session_state.resultados_scan if r["tiene_senal"])
        n_conf = sum(1 for r in st.session_state.resultados_scan if r["n_alineados"]>=2)
        n_alc  = sum(1 for r in st.session_state.resultados_scan for p in r["patrones"] if p["dir"]=="ALCISTA" and p.get("alineado"))
        for col, lbl, val, color, sub in zip(st.columns(4),
            ["PATRONES TOTALES","SEÑALES VALIDAS","CONFLUENCIAS","SEÑALES ALCISTAS"],
            [str(t_pat),str(n_sig),str(n_conf),str(n_alc)],
            ["#c8920a","#34d399","#fbbf24","#34d399"],
            ["detectados","alineadas","doble+ patron","oportunidad CALL"]):
            with col:
                st.markdown(f'<div class="kpi"><div class="kpi-label">{lbl}</div><div class="kpi-value" style="color:{color};">{val}</div><div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="sec" style="margin-top:14px;">ESTADO DE ACTIVOS</div>', unsafe_allow_html=True)
        for r in st.session_state.resultados_scan:
            alc = any(p["dir"]=="ALCISTA" and p.get("alineado") for p in r["patrones"])
            baj = any(p["dir"]=="BAJISTA" and p.get("alineado") for p in r["patrones"])
            es_conf = r["n_alineados"] >= 2
            if r["mercado_plano"]:       sc,st_,sb = "#f87171","SIN FUERZA — NO OPERAR","#fff0f0"
            elif es_conf and alc:        sc,st_,sb = "#c8920a","CONFLUENCIA ALCISTA","#fff8e7"
            elif es_conf and baj:        sc,st_,sb = "#c8920a","CONFLUENCIA BAJISTA","#fff8e7"
            elif alc:                    sc,st_,sb = "#34d399","SEÑAL ALCISTA","#e8f9f0"
            elif baj:                    sc,st_,sb = "#f87171","SEÑAL BAJISTA","#fff0f0"
            else:                        sc,st_,sb = "#475569","SIN SEÑAL","#f0f6fc"
            precio_s = f"{r['precio']:.2f}" if r["precio"] > 0 else "Sin datos"
            rc = "#f87171" if r["rsi"]>70 else ("#34d399" if r["rsi"]<30 else "#94a3b8")
            st.markdown(f"""
            <div class="asset-row" style="border-left:4px solid {r['info']['color']};">
              <div>
                <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:18px;color:#0f2035;">{r['activo']}</div>
                <div style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#5a7a99;">{r['info']['tipo']} · {precio_s}</div>
              </div>
              <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;">
                <span style="background:{sb};color:{sc};border:1px solid {sc}44;padding:4px 12px;border-radius:20px;font-family:'Share Tech Mono',monospace;font-size:9px;font-weight:700;">{st_}</span>
                <span style="color:{r['tend_col']};font-family:'Share Tech Mono',monospace;font-size:9px;">{r['tendencia']}</span>
                <span style="color:{r['vol_col']};font-family:'Share Tech Mono',monospace;font-size:9px;">ATR:{r['vol_est']}</span>
                <span style="color:{rc};font-family:'Share Tech Mono',monospace;font-size:9px;">RSI:{r['rsi']:.0f}</span>
              </div>
            </div>""", unsafe_allow_html=True)

# ── RANKING ─────────────────────────────────────
with tab_ranking:
    st.markdown('<div class="sec">RANKING — MEJOR OPORTUNIDAD AHORA</div>', unsafe_allow_html=True)
    if not st.session_state.resultados_scan:
        st.markdown('<div style="text-align:center;padding:40px;font-family:\'Share Tech Mono\',monospace;font-size:11px;color:#5a7a99;">Ejecuta el escaneo para ver el ranking</div>', unsafe_allow_html=True)
    else:
        ranking = [r for r in st.session_state.resultados_scan if r["score"] > 0]
        if not ranking:
            st.markdown('<div style="text-align:center;padding:30px;background:#f0f6fc;border:1px solid #bdd4e8;border-radius:10px;font-family:\'Share Tech Mono\',monospace;font-size:11px;color:#5a7a99;">El mercado no presenta buenas oportunidades ahora mismo</div>', unsafe_allow_html=True)
        else:
            medallas = ["🥇","🥈","🥉"]
            for i, r in enumerate(ranking):
                dir_col = "#34d399" if r["dir_dom"]=="ALCISTA" else "#f87171"
                accion  = "CALL / LONG" if r["dir_dom"]=="ALCISTA" else "PUT / SHORT"
                es_conf = r["n_alineados"] >= 2
                borde   = "border:2px solid #c8920a;" if es_conf else "border:1px solid #bdd4e8;"
                conf_badge = f'<span class="conf-multi-badge">{r["conf_label"]}</span>' if es_conf else ""
                score_pct  = min(100, r["score"])
                exp_str    = expiracion_str(r["max_exp"])
                med = medallas[i] if i < 3 else str(i+1)
                st.markdown(f"""
                <div class="rank-card" style="{borde}">
                  <div class="rank-num">{med}</div>
                  <div style="flex:1;">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;flex-wrap:wrap;">
                      <span style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:20px;color:#0f2035;">{r['activo']}</span>
                      <span style="background:#e8f0f7;color:{dir_col};border:1px solid {dir_col}44;padding:3px 10px;border-radius:20px;font-family:'Share Tech Mono',monospace;font-size:9px;font-weight:700;">{r['dir_dom']}</span>
                      {conf_badge}
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;flex-wrap:wrap;">
                      <span style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#5a7a99;">{accion}</span>
                      <span class="exp-badge">EXPIRACION: {exp_str}</span>
                      <span style="font-family:'Share Tech Mono',monospace;font-size:9px;color:#c8920a;">{r['n_alineados']} patron(es)</span>
                    </div>
                    <div style="height:6px;background:#bdd4e8;border-radius:3px;overflow:hidden;">
                      <div style="height:100%;width:{score_pct}%;background:linear-gradient(90deg,#92400e,#c8920a);border-radius:3px;"></div>
                    </div>
                    <div style="font-family:'Share Tech Mono',monospace;font-size:9px;color:#5a7a99;margin-top:3px;">Score: {r['score']:.0f}/100 · ATR:{r['vol_est']} · {r['tendencia']}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

# ── ALERTAS ─────────────────────────────────────
# ================================================================
# IMAGENES SVG DE PATRONES
# ================================================================
def svg_patron(nombre, direccion):
    """Mini diagrama SVG de cada patron — visual rapido en iPhone"""
    col_alc = "#16a34a"; col_baj = "#dc2626"; col_neu = "#92400e"
    c = col_alc if direccion == "ALCISTA" else col_baj

    svgs = {
        "Engulfing + EMA": f"""<svg width="80" height="50" viewBox="0 0 80 50">
            <rect x="20" y="15" width="12" height="25" fill="{col_baj}" rx="1"/>
            <line x1="26" y1="8" x2="26" y2="15" stroke="{col_baj}" stroke-width="1.5"/>
            <line x1="26" y1="40" x2="26" y2="46" stroke="{col_baj}" stroke-width="1.5"/>
            <rect x="42" y="8" width="16" height="34" fill="{c}" rx="1"/>
            <line x1="50" y1="2" x2="50" y2="8" stroke="{c}" stroke-width="1.5"/>
            <line x1="50" y1="42" x2="50" y2="48" stroke="{c}" stroke-width="1.5"/>
            <line x1="5" y1="30" x2="75" y2="22" stroke="#c8920a" stroke-width="1" stroke-dasharray="3,2"/>
        </svg>""",
        "Pin Bar en SR": f"""<svg width="80" height="50" viewBox="0 0 80 50">
            <line x1="40" y1="2" x2="40" y2="42" stroke="{c}" stroke-width="1.5"/>
            <rect x="33" y="30" width="14" height="10" fill="{c}" rx="1"/>
            <line x1="40" y1="42" x2="40" y2="48" stroke="{c}" stroke-width="1.5"/>
            <line x1="5" y1="32" x2="75" y2="32" stroke="#c8920a" stroke-width="1.5" stroke-dasharray="4,2"/>
        </svg>""",
        "Fakey": f"""<svg width="80" height="50" viewBox="0 0 80 50">
            <rect x="8" y="12" width="14" height="26" fill="#94a3b8" rx="1"/>
            <rect x="28" y="16" width="10" height="18" fill="#94a3b8" rx="1"/>
            <line x1="56" y1="4" x2="56" y2="46" stroke="{col_baj}" stroke-width="1.5"/>
            <rect x="50" y="28" width="12" height="8" fill="{col_baj}" rx="1"/>
            <line x1="62" y1="10" x2="75" y2="20" stroke="{c}" stroke-width="2"/>
        </svg>""",
        "Divergencia RSI": f"""<svg width="80" height="50" viewBox="0 0 80 50">
            <polyline points="5,35 20,25 35,15 50,18 65,12" fill="none" stroke="#1d4ed8" stroke-width="1.5"/>
            <polyline points="5,38 20,32 35,30 50,34 65,38" fill="none" stroke="#c8920a" stroke-width="1.5" stroke-dasharray="3,2"/>
            <text x="3" y="48" font-size="7" fill="#4a6080">Precio</text>
            <text x="3" y="44" font-size="7" fill="#c8920a" dy="0">RSI</text>
            <line x1="50" y1="10" x2="68" y2="10" stroke="{c}" stroke-width="2"/>
        </svg>""",
        "Inside Bar Ruptura": f"""<svg width="80" height="50" viewBox="0 0 80 50">
            <rect x="10" y="10" width="14" height="30" fill="#94a3b8" rx="1"/>
            <rect x="30" y="16" width="10" height="18" fill="#64748b" rx="1"/>
            <rect x="50" y="{'5' if direccion=='ALCISTA' else '30'}" width="14" height="{'28' if direccion=='ALCISTA' else '15'}" fill="{c}" rx="1"/>
            <line x1="10" y1="10" x2="64" y2="10" stroke="{col_baj}" stroke-width="1" stroke-dasharray="3,2"/>
            <line x1="10" y1="40" x2="64" y2="40" stroke="#16a34a" stroke-width="1" stroke-dasharray="3,2"/>
        </svg>""",
        "Tres Soldados/Cuervos": f"""<svg width="80" height="50" viewBox="0 0 80 50">
            <rect x="8" y="{'28' if direccion=='ALCISTA' else '8'}" width="14" height="{'18' if direccion=='ALCISTA' else '18'}" fill="{c}" rx="1"/>
            <rect x="28" y="{'20' if direccion=='ALCISTA' else '16'}" width="14" height="{'22' if direccion=='ALCISTA' else '22'}" fill="{c}" rx="1"/>
            <rect x="48" y="{'10' if direccion=='ALCISTA' else '24'}" width="14" height="{'28' if direccion=='ALCISTA' else '18'}" fill="{c}" rx="1"/>
        </svg>""",
        "Estrella Manana/Tarde": f"""<svg width="80" height="50" viewBox="0 0 80 50">
            <rect x="5" y="{'8' if direccion=='BAJISTA' else '25'}" width="16" height="{'22' if direccion=='BAJISTA' else '18'}" fill="{'#dc2626' if direccion=='BAJISTA' else '#16a34a'}" rx="1"/>
            <rect x="28" y="20" width="10" height="10" fill="#fbbf24" rx="1"/>
            <line x1="33" y1="15" x2="33" y2="20" stroke="#fbbf24" stroke-width="1.5"/>
            <line x1="33" y1="30" x2="33" y2="36" stroke="#fbbf24" stroke-width="1.5"/>
            <rect x="48" y="{'25' if direccion=='BAJISTA' else '8'}" width="16" height="{'18' if direccion=='BAJISTA' else '22'}" fill="{c}" rx="1"/>
        </svg>""",
        "Consolidacion Ruptura": f"""<svg width="80" height="50" viewBox="0 0 80 50">
            <rect x="5" y="18" width="8" height="14" fill="#94a3b8" rx="1"/>
            <rect x="16" y="20" width="8" height="10" fill="#94a3b8" rx="1"/>
            <rect x="27" y="17" width="8" height="16" fill="#94a3b8" rx="1"/>
            <rect x="38" y="19" width="8" height="12" fill="#94a3b8" rx="1"/>
            <line x1="5" y1="17" x2="46" y2="17" stroke="{col_baj}" stroke-width="1" stroke-dasharray="2,2"/>
            <line x1="5" y1="32" x2="46" y2="32" stroke="#16a34a" stroke-width="1" stroke-dasharray="2,2"/>
            <rect x="52" y="{'5' if direccion=='ALCISTA' else '28'}" width="14" height="{'28' if direccion=='ALCISTA' else '18'}" fill="{c}" rx="1"/>
            <line x1="52" y1="17" x2="66" y2="17" stroke="{col_baj}" stroke-width="1" stroke-dasharray="2,2"/>
        </svg>""",
    }
    svg = svgs.get(nombre, f"""<svg width="80" height="50" viewBox="0 0 80 50">
        <text x="10" y="28" font-size="9" fill="#4a6080">{nombre[:10]}</text>
    </svg>""")
    return svg

def checklist_confirmacion(df, direccion):
    """Checklist automatico de confirmacion antes de entrar"""
    checks = []
    rsi = calc_rsi(df["cierre"]).iloc[-1]
    ultima = df["cierre"].iloc[-1]
    ante   = df["cierre"].iloc[-2]
    ante2  = df["cierre"].iloc[-3]

    # Velas anteriores
    vela_favor = (direccion=="ALCISTA" and ultima > ante) or (direccion=="BAJISTA" and ultima < ante)
    checks.append(("Vela actual a favor", vela_favor))

    # RSI no extremo
    rsi_ok = (direccion=="ALCISTA" and rsi < 70) or (direccion=="BAJISTA" and rsi > 30)
    checks.append((f"RSI no extremo ({rsi:.0f})", rsi_ok))

    # Momentum — 2 velas previas
    if direccion == "ALCISTA":
        momentum = ultima > ante2
    else:
        momentum = ultima < ante2
    checks.append(("Momentum de 2 velas", momentum))

    # ATR — ya viene del resultado del scan, usamos RSI como proxy
    vol_ok = 30 < rsi < 75
    checks.append(("Volatilidad aceptable", vol_ok))

    aprobados = sum(1 for _, v in checks if v)
    return checks, aprobados

# ================================================================
# TAB ALERTAS
# ================================================================
with tab_alert:
    st.markdown('<div class="sec">ALERTAS ACTIVAS — ALTA CONFIANZA</div>', unsafe_allow_html=True)
    if not st.session_state.alertas:
        st.markdown("<div style='text-align:center;padding:50px;background:#f0f6fc;border:1px solid #bdd4e8;border-radius:12px;'><div style='font-size:40px;margin-bottom:12px;'>📡</div><div style='font-family:\"Rajdhani\",sans-serif;font-size:20px;color:#5a7a99;'>Sin alertas activas</div><div style='font-family:\"Share Tech Mono\",monospace;font-size:11px;color:#6a8aaa;margin-top:8px;'>Ejecuta el escaneo para detectar oportunidades</div></div>", unsafe_allow_html=True)
    else:
        for i, al in enumerate(st.session_state.alertas):
            if solo_confluencia and al.get("n_patrones",1) < 2: continue
            es_alc  = al["dir"] == "ALCISTA"
            es_conf = al.get("n_patrones",1) >= 2
            cc      = "confluencia-card" if es_conf else ("alert-alcista" if es_alc else "alert-bajista")
            ic      = "▲" if es_alc else "▼"
            col     = "#34d399" if es_alc else "#f87171"
            acc     = "CALL / LONG" if es_alc else "PUT / SHORT"
            conf_i  = i in st.session_state.confirmadas
            conf_badge = f'<span class="conf-multi-badge">{al["conf_label"]}</span>' if es_conf else ""

            # Obtener datos para checklist y SVG
            info_activo = ACTIVOS.get(al["activo"], {})
            df_al = obtener_datos(info_activo.get("yahoo",""))
            checks, aprobados = checklist_confirmacion(df_al, al["dir"]) if df_al is not None else ([], 0)
            semaforo = "🟢 ENTRAR" if aprobados >= 3 else ("🟡 ESPERAR" if aprobados == 2 else "🔴 NO ENTRAR")
            sem_col  = "#16a34a" if aprobados >= 3 else ("#c8920a" if aprobados == 2 else "#dc2626")

            # Patrones individuales para SVGs
            patrones_lista = [p.strip() for p in al["patrones_nombres"].split(",")]

            # Build card avoiding single-quote conflicts in f-strings
            opacidad  = "opacity:0.5;" if conf_i else ""
            sem_bg    = "#e8f9f0" if aprobados >= 3 else ("#fffbf0" if aprobados == 2 else "#fff0f0")
            precio_s  = f"{al['precio']:.2f}"
            card_html = (
                f'<div class="{cc}" style="{opacidad}">' +
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">' +
                f'<div><div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">' +
                f'<div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:26px;color:{col};">{ic} {al["activo"]}</div>' +
                conf_badge +
                f'</div><div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#3a5570;">{al["hora"]} &middot; ${precio_s} &middot; Vol:{al["vol_est"]}</div></div>' +
                f'<div style="text-align:right;"><div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:20px;color:{col};">{acc}</div>' +
                f'<span class="exp-badge">EXPIRACION: {al["expiracion"]}</span></div></div>' +
                f'<div style="font-size:12px;color:#4a6080;margin-bottom:8px;">Patrones: <b style="color:{col};">{al["patrones_nombres"]}</b></div>' +
                f'<div style="display:flex;gap:8px;align-items:center;margin-bottom:10px;">' +
                f'<div style="flex:1;height:8px;background:#bdd4e8;border-radius:4px;overflow:hidden;">' +
                f'<div style="height:100%;width:{al["conf"]}%;background:{col};border-radius:4px;"></div></div>' +
                f'<span style="font-family:Share Tech Mono,monospace;font-size:11px;color:{col};font-weight:700;">{al["conf"]}%</span></div>' +
                f'<div style="display:flex;align-items:center;gap:10px;padding:10px;background:{sem_bg};border-radius:8px;margin-bottom:8px;">' +
                f'<span style="font-family:Rajdhani,sans-serif;font-size:20px;font-weight:700;color:{sem_col};">{semaforo}</span>' +
                f'<span style="font-family:Share Tech Mono,monospace;font-size:9px;color:#4a6080;">{aprobados}/4 checks OK</span></div></div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)

            # Checklist de confirmacion expandible
            with st.expander(f"Ver checklist de confirmacion — {al['activo']}"):
                for label, ok in checks:
                    icono = "✅" if ok else "❌"
                    st.markdown(f"{icono} **{label}**")

                # Mini SVGs de los patrones detectados
                st.markdown("**Patrones detectados — referencia visual:**")
                svg_cols = st.columns(min(len(patrones_lista), 4))
                for j, pat in enumerate(patrones_lista[:4]):
                    with svg_cols[j]:
                        svg_html = svg_patron(pat.strip(), al["dir"])
                        st.markdown(f"""
                        <div style="text-align:center;background:#f0f6fc;border:1px solid #bdd4e8;border-radius:8px;padding:8px;">
                          {svg_html}
                          <div style="font-family:'Share Tech Mono',monospace;font-size:8px;color:#4a6080;margin-top:4px;">{pat.strip()[:18]}</div>
                        </div>""", unsafe_allow_html=True)

                # Boton IA individual
                if ia_ok:
                    ia_key = f"ia_individual_{i}"
                    ia_resp_key = f"ia_resp_{i}"
                    if ia_resp_key not in st.session_state:
                        st.session_state[ia_resp_key] = ""
                    if st.button(f"ANALIZAR ESTA SEÑAL CON IA", key=ia_key):
                        checks_txt = "\n".join([f"{'OK' if v else 'FALLA'}: {l}" for l,v in checks])
                        sys_p = f"Eres analista de Hector. Capital $467, objetivo $50/dia, IQ Option M15. Analiza esta señal especifica y di si debe entrar AHORA o esperar. Se directo. Max 80 palabras. Espanol."
                        prompt = f"Activo: {al['activo']}\nDireccion: {al['dir']}\nPatrones: {al['patrones_nombres']}\nScore: {al['conf']}%\nExpiracion: {al['expiracion']}\n\nChecklist:\n{checks_txt}"
                        with st.spinner("Analizando..."):
                            try:
                                r = requests.post("https://api.anthropic.com/v1/messages",
                                    headers={"Content-Type":"application/json","x-api-key":st.session_state.api_key,"anthropic-version":"2023-06-01"},
                                    json={"model":"claude-sonnet-4-20250514","max_tokens":200,"system":sys_p,
                                          "messages":[{"role":"user","content":prompt}]}, timeout=30)
                                if r.status_code == 200:
                                    st.session_state[ia_resp_key] = r.json()["content"][0]["text"]
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                    if st.session_state.get(ia_resp_key):
                        st.markdown(f'<div style="background:#fff8e7;border:1px solid #c8920a;border-radius:8px;padding:12px;font-size:13px;color:#1a2940;line-height:1.7;margin-top:8px;">{st.session_state[ia_resp_key].replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

            _, c2, c3 = st.columns([2,1,1])
            with c2:
                if not conf_i and st.button("OK LEIDA", key=f"ok_{i}"):
                    st.session_state.confirmadas.add(i)
                    st.rerun()
            with c3:
                tracker_key = f"tracker_{al.get('id','')}"
                ya_trackeada = any(t.get("alerta_id")==al.get("id") for t in st.session_state.tracker)
                if conf_i and not ya_trackeada:
                    res = st.selectbox("Resultado", ["—","WIN","LOSS"], key=tracker_key, label_visibility="collapsed")
                    if res in ("WIN","LOSS"):
                        st.session_state.tracker.append({
                            "alerta_id":al.get("id",""),
                            "activo":al["activo"],"dir":al["dir"],
                            "resultado":res,"hora":al["hora"],
                            "conf":al["conf"],"patron":al["patrones_nombres"],
                        })
                        st.rerun()

        # Analisis IA general
        if ia_ok:
            st.markdown("---")
            if st.button("ANALIZAR TODAS LAS ALERTAS CON IA", key="ia_al"):
                txt_al = "\n".join([
                    f"{a['activo']} - {a['dir']} - {a['patrones_nombres']} - Score:{a['conf']}% - {a['conf_label']} - Exp:{a['expiracion']}"
                    for a in st.session_state.alertas
                ])
                sys_p = "Eres analista de Hector. Capital $467, objetivo $50/dia, IQ Option M15. Analiza estas alertas y dime las 2 MEJORES oportunidades ahora mismo. Prioriza las dobles confluencias. Indica activo, CALL o PUT, expiracion y razon. Max 150 palabras. Espanol."
                with st.spinner("Analizando con IA..."):
                    try:
                        r = requests.post("https://api.anthropic.com/v1/messages",
                            headers={"Content-Type":"application/json","x-api-key":st.session_state.api_key,"anthropic-version":"2023-06-01"},
                            json={"model":"claude-sonnet-4-20250514","max_tokens":400,"system":sys_p,
                                  "messages":[{"role":"user","content":f"Alertas:\n{txt_al}"}]}, timeout=30)
                        if r.status_code == 200:
                            st.session_state.ia_analisis = r.json()["content"][0]["text"]
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            if st.session_state.ia_analisis:
                st.markdown(f'<div style="background:#fff8e7;border:1px solid #c8920a;border-radius:10px;padding:16px;font-size:13px;color:#1a2940;line-height:1.8;margin-top:10px;">{st.session_state.ia_analisis.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

# ── HISTORIAL ───────────────────────────────────
with tab_hist:
    st.markdown('<div class="sec">HISTORIAL DEL DIA — SEÑALES DETECTADAS</div>', unsafe_allow_html=True)
    if not st.session_state.historial:
        st.markdown("<div style='text-align:center;padding:40px;background:#f0f6fc;border:1px solid #bdd4e8;border-radius:10px;'><div style='font-size:32px;margin-bottom:10px;'>📋</div><div style='font-family:\"Share Tech Mono\",monospace;font-size:11px;color:#5a7a99;'>Sin señales en el historial de hoy.</div></div>", unsafe_allow_html=True)
    else:
        n_unicas = len(set(h["activo"] for h in st.session_state.historial))
        st.markdown(f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:10px;color:#5a7a99;margin-bottom:10px;">{len(st.session_state.historial)} señales registradas · {n_unicas} activos distintos</div>', unsafe_allow_html=True)
        for h in reversed(st.session_state.historial):
            dc = "#34d399" if h["dir"]=="ALCISTA" else "#f87171"
            es_conf = h.get("n_patrones",1) >= 2
            borde = f"border-left:3px solid #c8920a;" if es_conf else f"border-left:3px solid {dc};"
            st.markdown(f"""
            <div class="hist-item" style="{borde}">
              <div>
                <span style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:16px;color:#0f2035;">{h['activo']}</span>
                <span style="font-family:'Share Tech Mono',monospace;font-size:9px;color:#5a7a99;margin-left:8px;">{h['fecha']} {h['hora']}</span>
              </div>
              <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;">
                <span style="color:{dc};font-family:'Share Tech Mono',monospace;font-size:10px;font-weight:700;">{h['dir']}</span>
                <span class="exp-badge">{h['expiracion']}</span>
                {f'<span class="conf-multi-badge">{h["conf_label"]}</span>' if es_conf else ''}
                <span style="font-family:'Share Tech Mono',monospace;font-size:9px;color:#c8920a;">{h['conf']}%</span>
              </div>
            </div>""", unsafe_allow_html=True)
        _, col_d = st.columns([3,1])
        with col_d:
            if st.button("Limpiar historial", key="clear_hist"):
                st.session_state.historial = []
                st.rerun()

# ── TRACKER ─────────────────────────────────────
with tab_tracker:
    st.markdown('<div class="sec">TRACKER WIN/LOSS — RENDIMIENTO DEL DETECTOR</div>', unsafe_allow_html=True)
    wins   = [t for t in st.session_state.tracker if t["resultado"]=="WIN"]
    losses = [t for t in st.session_state.tracker if t["resultado"]=="LOSS"]
    total  = len(wins) + len(losses)
    wr     = int(len(wins)/total*100) if total > 0 else 0
    col_wr = "#34d399" if wr>=60 else ("#fbbf24" if wr>=50 else "#f87171")

    for col, lbl, val, color in zip(st.columns(4),
        ["WINS","LOSSES","WIN RATE","OPERACIONES"],
        [str(len(wins)),str(len(losses)),f"{wr}%",str(total)],
        ["#34d399","#f87171",col_wr,"#c8920a"]):
        with col:
            st.markdown(f'<div class="kpi"><div class="kpi-label">{lbl}</div><div class="kpi-value" style="color:{color};">{val}</div></div>', unsafe_allow_html=True)

    if total > 0:
        st.markdown('<div class="sec" style="margin-top:14px;">OPERACIONES TRACKEADAS</div>', unsafe_allow_html=True)
        for t in reversed(st.session_state.tracker):
            rc = "#34d399" if t["resultado"]=="WIN" else "#f87171"
            st.markdown(f"""
            <div class="hist-item" style="border-left:3px solid {rc};">
              <div>
                <span style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:15px;color:#0f2035;">{t['activo']}</span>
                <span style="font-family:'Share Tech Mono',monospace;font-size:9px;color:#5a7a99;margin-left:8px;">{t['hora']} · {t['dir']}</span>
              </div>
              <div style="display:flex;gap:6px;align-items:center;">
                <span style="font-size:11px;color:#3a5570;">{t['patron'][:35]}</span>
                <span style="color:{rc};border:1px solid {rc}44;padding:3px 10px;border-radius:20px;font-family:'Share Tech Mono',monospace;font-size:10px;font-weight:700;">{t['resultado']}</span>
              </div>
            </div>""", unsafe_allow_html=True)

        if wr < 50 and total >= 5:
            st.markdown('<div class="atr-flat" style="margin-top:10px;"><b style="color:#f87171;">Win rate bajo 50% — Subir confianza minima a 68% o activar "Solo confluencias"</b></div>', unsafe_allow_html=True)
        elif wr >= 65 and total >= 5:
            st.markdown('<div class="atr-ok" style="margin-top:10px;"><b style="color:#34d399;">Excelente win rate — El detector esta calibrado correctamente</b></div>', unsafe_allow_html=True)

        if st.button("Reset tracker", key="reset_tracker"):
            st.session_state.tracker = []
            st.rerun()
    else:
        st.markdown("<div style='text-align:center;padding:40px;background:#f0f6fc;border:1px solid #bdd4e8;border-radius:10px;'><div style='font-family:\"Share Tech Mono\",monospace;font-size:11px;color:#5a7a99;'>Confirma alertas como leidas y luego registra WIN o LOSS para trackear el rendimiento del detector.</div></div>", unsafe_allow_html=True)

# ── VOLATILIDAD ATR ─────────────────────────────
with tab_atr:
    st.markdown('<div class="sec">VOLATILIDAD ATR — FILTRO DE MERCADO</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#f0f6fc;border:1px solid #bdd4e8;border-radius:10px;padding:14px 16px;margin-bottom:14px;">
      <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:16px;color:#c8920a;margin-bottom:8px;">Por que el ATR protege tu capital</div>
      <div style="font-size:13px;color:#4a6080;line-height:1.8;">
      El <b style="color:#0f2035;">ATR</b> mide la fuerza real del mercado en 14 velas. Mercado plano = el spread te come la ganancia antes de que el patron se desarrolle.<br><br>
      <b style="color:#34d399;">FUERTE (mayor 90%):</b> Operar con confianza<br>
      <b style="color:#fbbf24;">NORMAL (60-90%):</b> Operar con precaucion<br>
      <b style="color:#f87171;">PLANO (menor 60%):</b> NO OPERAR — señales bloqueadas automaticamente
      </div>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.resultados_scan:
        st.markdown('<div style="text-align:center;padding:30px;font-family:\'Share Tech Mono\',monospace;font-size:11px;color:#5a7a99;">Ejecuta el escaneo primero</div>', unsafe_allow_html=True)
    else:
        for r in st.session_state.resultados_scan:
            if r["sin_datos"]: continue
            vp = min(100, r["vol_pct"])
            fc = "vol-fill-green" if r["vol_est"]=="FUERTE" else ("vol-fill-gold" if r["vol_est"]=="NORMAL" else "vol-fill-red")
            st.markdown(f"""
            <div class="{r['vol_cls']}" style="margin-bottom:10px;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <div>
                  <span style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:18px;color:#0f2035;">{r['activo']}</span>
                  <span style="font-family:'Share Tech Mono',monospace;font-size:10px;color:{r['vol_col']};margin-left:10px;">{r['vol_est']}</span>
                </div>
                <span style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:22px;color:{r['vol_col']};">{vp:.0f}%</span>
              </div>
              <div class="vol-track"><div class="{fc}" style="width:{vp}%;"></div></div>
              <div style="font-family:'Share Tech Mono',monospace;font-size:10px;color:{r['vol_col']};margin-top:4px;">{r['vol_msg']}</div>
            </div>""", unsafe_allow_html=True)

# ── ESTADISTICAS ────────────────────────────────
with tab_stats:
    st.markdown('<div class="sec">EFECTIVIDAD HISTORICA — 8 PATRONES</div>', unsafe_allow_html=True)
    for nombre, ip in sorted(PATRONES.items(), key=lambda x: x[1]["efectividad"], reverse=True):
        ef = ip["efectividad"]; color = "#34d399" if ef>=68 else ("#fbbf24" if ef>=64 else "#f87171")
        peso_s = "★" * ip["peso"]
        st.markdown(f"""
        <div style="background:#f0f6fc;border:1px solid #bdd4e8;border-radius:8px;padding:12px 16px;margin-bottom:8px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
            <div>
              <span style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:15px;color:#0f2035;">{nombre}</span>
              <span style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#c8920a;margin-left:8px;">{peso_s}</span>
            </div>
            <div style="display:flex;align-items:center;gap:10px;">
              <span class="exp-badge">EXP: {expiracion_str(ip['min_exp'])}</span>
              <span style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:20px;color:{color};">{ef}%</span>
            </div>
          </div>
          <div style="height:5px;background:#bdd4e8;border-radius:3px;overflow:hidden;margin-bottom:5px;">
            <div style="height:100%;width:{ef}%;background:{color};border-radius:3px;"></div>
          </div>
          <div style="font-size:11px;color:#5a7a99;">{ip['desc']} · Peso en confluencia: {ip['peso']}/3</div>
        </div>""", unsafe_allow_html=True)

# ================================================================

# ── CAPITAL ─────────────────────────────────────
with tab_capital:
    st.markdown('<div class="sec">GESTION DE CAPITAL Y RIESGO</div>', unsafe_allow_html=True)

    capital = st.session_state.capital_dia
    sl_pct  = st.session_state.stop_loss_pct
    perdida = st.session_state.perdida_dia
    sl_monto = capital * sl_pct / 100
    pct_usado = min(100, int(perdida / sl_monto * 100)) if sl_monto > 0 else 0
    barra_col = "#34d399" if pct_usado < 50 else ("#fbbf24" if pct_usado < 80 else "#f87171")

    # KPIs principales
    k1,k2,k3,k4 = st.columns(4)
    for col, lbl, val, color in [
        (k1, "CAPITAL DEL DIA",  f"${capital:.2f}",          "#1a2940"),
        (k2, "ENTRADA 1%",       f"${capital*0.01:.2f}",     "#16a34a"),
        (k3, "ENTRADA 2%",       f"${capital*0.02:.2f}",     "#c8920a"),
        (k4, "STOP LOSS DIARIO", f"${sl_monto:.2f} ({sl_pct}%)", "#dc2626"),
    ]:
        with col:
            st.markdown(f'<div class="kpi"><div class="kpi-label">{lbl}</div><div class="kpi-value" style="color:{color};">{val}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="sec" style="margin-top:14px;">ESTADO DEL DIA</div>', unsafe_allow_html=True)

    estado_txt = "🛑 STOP LOSS ALCANZADO — NO OPERAR" if perdida >= sl_monto else ("⚠️ RIESGO ALTO" if pct_usado >= 70 else "✅ CAPITAL OK — OPERAR")
    estado_col = "#dc2626" if perdida >= sl_monto else ("#f97316" if pct_usado >= 70 else "#16a34a")
    estado_bg  = "#fff0f0" if perdida >= sl_monto else ("#fffbf0" if pct_usado >= 70 else "#e8f9f0")

    st.markdown(f"""
    <div style="background:{estado_bg};border:2px solid {estado_col};border-radius:10px;padding:16px;margin-bottom:14px;">
      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:22px;color:{estado_col};margin-bottom:8px;">{estado_txt}</div>
      <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a6080;margin-bottom:8px;">Perdida acumulada: ${perdida:.2f} de ${sl_monto:.2f} permitidos</div>
      <div style="height:12px;background:#bdd4e8;border-radius:6px;overflow:hidden;">
        <div style="height:100%;width:{pct_usado}%;background:{barra_col};border-radius:6px;transition:width 0.5s;"></div>
      </div>
      <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:{barra_col};margin-top:4px;">{pct_usado}% del stop loss usado</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec">REGISTRAR RESULTADO DE OPERACION</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        monto_op = st.number_input("Monto operado $", min_value=1.0, max_value=float(capital), value=float(capital*0.02), step=1.0, key="monto_op_cap")
    with c2:
        resultado_op = st.selectbox("Resultado", ["—","WIN","LOSS"], key="res_op_cap")
    with c3:
        payout_pct = st.number_input("Payout %", min_value=50, max_value=100, value=80, step=1, key="payout_cap")

    if resultado_op == "WIN":
        ganancia = monto_op * payout_pct / 100
        st.markdown(f'<div class="atr-ok"><b style="color:#16a34a;">GANANCIA: +${ganancia:.2f}</b></div>', unsafe_allow_html=True)
        if st.button("Registrar WIN", key="reg_win_cap"):
            # En wins reducimos la perdida acumulada si habia
            if st.session_state.perdida_dia > 0:
                st.session_state.perdida_dia = max(0, st.session_state.perdida_dia - ganancia)
            st.rerun()
    elif resultado_op == "LOSS":
        st.markdown(f'<div class="atr-flat"><b style="color:#dc2626;">PERDIDA: -${monto_op:.2f}</b></div>', unsafe_allow_html=True)
        if st.button("Registrar LOSS", key="reg_loss_cap"):
            st.session_state.perdida_dia += monto_op
            if st.session_state.perdida_dia >= sl_monto:
                st.session_state.radar_bloqueado = True
            st.rerun()

    st.markdown('<div class="sec" style="margin-top:14px;">CALCULADORA DE ENTRADAS</div>', unsafe_allow_html=True)
    cap_calc = st.number_input("Capital a calcular", min_value=10.0, value=float(capital), step=10.0, key="cap_calc")
    for pct, label, color in [(1,"Entrada conservadora (1%)","#16a34a"),(2,"Entrada estandar (2%)","#c8920a"),(3,"Entrada agresiva (3%)","#dc2626"),(5,"Entrada max (5%)","#7c3aed")]:
        monto = cap_calc * pct / 100
        st.markdown(f'<div style="display:flex;justify-content:space-between;padding:8px 14px;background:#f0f6fc;border:1px solid #bdd4e8;border-radius:6px;margin-bottom:4px;"><span style="font-family:Share Tech Mono,monospace;font-size:10px;color:#4a6080;">{label}</span><span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:16px;color:{color};">${monto:.2f}</span></div>', unsafe_allow_html=True)

    if st.button("Reset dia completo", key="reset_dia_cap"):
        st.session_state.perdida_dia = 0.0
        st.session_state.radar_bloqueado = False
        st.rerun()


# ── CONFIRMAR CON IMAGEN ────────────────────────
with tab_confirmar:
    st.markdown('<div class="sec">📷 CONFIRMAR ENTRADA — ANALIZADOR DE GRAFICO</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#fff8e7;border:1px solid #c8920a;border-radius:10px;padding:14px 16px;margin-bottom:14px;">
      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:16px;color:#c8920a;margin-bottom:6px;">Como usar</div>
      <div style="font-size:13px;color:#4a6080;line-height:1.8;">
      1. El detector encontro una alerta → ir a IQ Option<br>
      2. Sacar captura de pantalla del grafico M15<br>
      3. Subir la imagen aca<br>
      4. La IA analiza el grafico y confirma ENTRAR o ESPERAR
      </div>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.api_key.startswith("sk-ant-"):
        st.markdown('<div class="atr-flat"><b style="color:#dc2626;">Necesitas la clave API de Anthropic para usar esta funcion</b></div>', unsafe_allow_html=True)
    else:
        # Selector de activo y direccion esperada
        c1, c2 = st.columns(2)
        with c1:
            activo_conf = st.selectbox("Activo de la alerta", list(ACTIVOS.keys()), key="act_conf")
        with c2:
            dir_conf = st.selectbox("Direccion esperada", ["ALCISTA (CALL)", "BAJISTA (PUT)"], key="dir_conf")

        # Subir imagen
        st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#5a7a99;margin:10px 0 4px;">SUBE LA CAPTURA DEL GRAFICO</div>', unsafe_allow_html=True)
        img_file = st.file_uploader("Captura del grafico", type=["png","jpg","jpeg","webp"], key="img_upload", label_visibility="collapsed")

        if img_file is not None:
            # Mostrar imagen subida
            st.image(img_file, caption="Grafico subido", use_column_width=True)

            if st.button("ANALIZAR GRAFICO CON IA", key="btn_analizar_img"):
                with st.spinner("La IA esta analizando el grafico..."):
                    try:
                        # Convertir imagen a base64
                        img_bytes = img_file.read()
                        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
                        ext = img_file.name.split(".")[-1].lower()
                        media_type = "image/jpeg" if ext in ("jpg","jpeg") else f"image/{ext}"

                        # Obtener alertas activas para contexto
                        alertas_ctx = ""
                        if st.session_state.alertas:
                            al_act = [a for a in st.session_state.alertas if a["activo"] == activo_conf]
                            if al_act:
                                a = al_act[0]
                                alertas_ctx = f"El detector encontro: {a['patrones_nombres']} con score {a['conf']}% - {a['conf_label']}."

                        dir_limpia = "CALL (alcista)" if "ALCISTA" in dir_conf else "PUT (bajista)"
                        sys_p = f"""Eres el analista personal de Hector, trader de IQ Option en temporalidad M15.
Hector esta considerando entrar {dir_limpia} en {activo_conf}.
{alertas_ctx}
Analiza el grafico que te mando y respondele:
1. DECISION: ENTRAR / ESPERAR / NO ENTRAR (en grande, claro)
2. Por que en 2-3 lineas maximo
3. Que debe ver en el grafico para confirmar
Se directo, sin rodeos. Maximo 100 palabras. En espanol."""

                        response = requests.post(
                            "https://api.anthropic.com/v1/messages",
                            headers={
                                "Content-Type": "application/json",
                                "x-api-key": st.session_state.api_key,
                                "anthropic-version": "2023-06-01"
                            },
                            json={
                                "model": "claude-sonnet-4-20250514",
                                "max_tokens": 300,
                                "system": sys_p,
                                "messages": [{
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "image",
                                            "source": {
                                                "type": "base64",
                                                "media_type": media_type,
                                                "data": img_b64
                                            }
                                        },
                                        {
                                            "type": "text",
                                            "text": f"Analiza este grafico M15 de {activo_conf} y dime si entro {dir_limpia} ahora."
                                        }
                                    ]
                                }]
                            },
                            timeout=45
                        )

                        if response.status_code == 200:
                            resp_txt = response.json()["content"][0]["text"]

                            # Determinar color segun decision
                            if "ENTRAR" in resp_txt.upper() and "NO ENTRAR" not in resp_txt.upper():
                                dec_col = "#16a34a"; dec_bg = "#e8f9f0"; dec_border = "#065f46"
                                dec_icon = "🟢"
                            elif "ESPERAR" in resp_txt.upper():
                                dec_col = "#c8920a"; dec_bg = "#fff8e7"; dec_border = "#c8920a"
                                dec_icon = "🟡"
                            else:
                                dec_col = "#dc2626"; dec_bg = "#fff0f0"; dec_border = "#991b1b"
                                dec_icon = "🔴"

                            st.markdown(f"""
                            <div style="background:{dec_bg};border:2px solid {dec_border};border-radius:12px;padding:18px;margin-top:12px;">
                              <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:28px;color:{dec_col};margin-bottom:10px;">{dec_icon} ANALISIS IA</div>
                              <div style="font-size:14px;color:#1a2940;line-height:1.8;">{resp_txt.replace(chr(10),"<br>")}</div>
                              <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#5a7a99;margin-top:10px;">{activo_conf} · {dir_conf} · {datetime.now().strftime("%H:%M")}</div>
                            </div>""", unsafe_allow_html=True)
                        else:
                            st.error(f"Error API: {response.status_code} — {response.text[:200]}")

                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        else:
            # Instruccion visual cuando no hay imagen
            st.markdown("""
            <div style="text-align:center;padding:40px 20px;background:#f0f6fc;border:2px dashed #bdd4e8;border-radius:12px;margin-top:10px;">
              <div style="font-size:48px;margin-bottom:12px;">📱</div>
              <div style="font-family:Rajdhani,sans-serif;font-size:18px;color:#4a6080;margin-bottom:8px;">Subi la captura de IQ Option</div>
              <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#5a7a99;line-height:1.8;">
              iPhone: screenshot → compartir → subir aca<br>
              Android: captura → galeria → subir aca
              </div>
            </div>""", unsafe_allow_html=True)


# FOOTER
# ================================================================
st.markdown("""
<div style="border-top:1px solid #bdd4e8;margin-top:24px;padding-top:10px;
text-align:center;font-family:'Share Tech Mono',monospace;font-size:9px;color:#6a8aaa;letter-spacing:2px;">
HECTOR PATTERN DETECTOR v5 · CAPITAL · AUTO-SCAN · SONIDO · SR · ATR · MACD · CONFLUENCIA · RANKING · 8 PATRONES · 6 ACTIVOS
</div>""", unsafe_allow_html=True)
