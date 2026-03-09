# HECTOR PATTERN DETECTOR v5
# Sistema Profesional de Reconocimiento de Patrones
# by Hector Trading — IQ Option M15
#
# v4 — Correcciones y mejoras autonomas:
#   - MACD integrado como confirmacion de tendencia
#   - calcular_score_activo() simplificado, sin desincronizacion
#   - Historial sin duplicados (deduplicacion por activo+hora)
#   - Confluencia solo cuenta patrones en la MISMA direccion
#   - Expiracion de confluencia = la mayor de los patrones involucrados
#   - Tracker WIN/LOSS robusto con key unico por alerta
#   - Indicador de sesion activa en header (Londres / Nueva York)
#
# INSTALACION: pip install streamlit requests pandas numpy yfinance
# EJECUCION:   streamlit run hector_pattern_detector.py

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timezone, date
import requests
import base64
import streamlit.components.v1 as components_v1
try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_OK = True
except ImportError:
    AUTOREFRESH_OK = False

st.set_page_config(
    page_title="Hector Pattern Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
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

@media (max-width:480px) {
    .kpi-value { font-size:22px; }
    .alert-card,.confluencia-card { padding:14px; }
    .asset-row { flex-direction:column; align-items:flex-start; }
    .rank-card { flex-direction:column; }
}

.stButton>button {
    background:#c8920a !important; color:#0f2035 !important;
    border:none !important; border-radius:8px !important;
    font-family:'Share Tech Mono',monospace !important;
    font-size:11px !important; letter-spacing:1px !important; font-weight:700 !important;
}
.stCheckbox label { color:#4a6080 !important; font-family:'Share Tech Mono',monospace !important; font-size:11px !important; }

::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-track { background:#ddeaf5; }
::-webkit-scrollbar-thumb { background:#7aaac8; border-radius:2px; }
</style>
""", unsafe_allow_html=True)


# ================================================================
# TELEGRAM
# ================================================================
def enviar_telegram(token, chat_id, mensaje):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        r = requests.post(url, json={"chat_id": chat_id, "text": mensaje, "parse_mode": "HTML"}, timeout=10)
        return r.status_code == 200
    except:
        return False


# ================================================================
# SECRETS — carga automatica desde Streamlit Cloud
# ================================================================
def cargar_secrets():
    """Carga API key, Telegram y capital desde st.secrets si existen"""
    try:
        if "anthropic_api_key" in st.secrets:
            st.session_state.api_key = st.secrets["anthropic_api_key"]
    except: pass
    try:
        if "telegram_token" in st.secrets:
            st.session_state.telegram_token = st.secrets["telegram_token"]
    except: pass
    try:
        if "telegram_chat_id" in st.secrets:
            st.session_state.telegram_chat_id = str(st.secrets["telegram_chat_id"])
    except: pass
    try:
        if "capital_dia" in st.secrets:
            st.session_state.capital_dia = float(st.secrets["capital_dia"])
    except: pass

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
    "telegram_token": "",
    "telegram_chat_id": "",
    "telegram_on": False,  # se activa automaticamente si hay secrets
    "tg_enviadas": set(),
    "ultima_alerta_sonido": "",
    "autorefresh_on": False,
    "autorefresh_min": 5,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Cargar secrets de Streamlit Cloud (si existen)
cargar_secrets()
# Auto-activar Telegram si hay token y chat_id cargados
if st.session_state.get("telegram_token") and st.session_state.get("telegram_chat_id"):
    st.session_state.telegram_on = True


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
    if   pct >= 90: return "FUERTE", pct, "Volatilidad optima — OPERAR",           "#34d399","atr-ok"
    elif pct >= 60: return "NORMAL", pct, "Volatilidad aceptable — Con precaucion", "#fbbf24","atr-low"
    else:           return "PLANO",  pct, "Mercado sin fuerza — NO OPERAR",         "#f87171","atr-flat"


def calcular_soportes_resistencias(df, periodos=100):
    datos = df.tail(periodos)
    maximos = datos["maximo"].values
    minimos = datos["minimo"].values
    resistencias, soportes = [], []
    for i in range(2, len(maximos)-2):
        if maximos[i] > maximos[i-1] and maximos[i] > maximos[i-2] and maximos[i] > maximos[i+1] and maximos[i] > maximos[i+2]:
            resistencias.append(maximos[i])
        if minimos[i] < minimos[i-1] and minimos[i] < minimos[i-2] and minimos[i] < minimos[i+1] and minimos[i] < minimos[i+2]:
            soportes.append(minimos[i])
    return sorted(set([round(s,4) for s in soportes]))[:3], sorted(set([round(r,4) for r in resistencias]))[-3:]

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

def calcular_score_activo(patrones_validos, vol_est, tendencia):
    """FIX v4: recibe parametros directos, sin riesgo de desincronizacion."""
    pat_alineados = [p for p in patrones_validos if p.get("alineado")]
    if not pat_alineados: return 0
    score, _, _, _ = calcular_confluencia(pat_alineados)
    vol_bonus  = {"FUERTE":20,"NORMAL":10,"PLANO":0}.get(vol_est, 0)
    tend_bonus = 0 if "LATERAL" in tendencia else 10
    return score + vol_bonus + tend_bonus

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
    ia_ok = st.session_state.api_key.startswith("sk-ant-")
    st.markdown(f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:10px;color:{"#34d399" if ia_ok else "#475569"};margin-bottom:8px;">{"IA ACTIVA" if ia_ok else "Sin clave"}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:9px;color:#5a7a99;letter-spacing:2px;margin-bottom:8px;">ACTIVOS</div>', unsafe_allow_html=True)
    activos_sel = [a for a in ACTIVOS if st.checkbox(a, value=True, key=f"chk_{a}")]

    st.markdown("---")
    confianza_min = st.slider("Confianza minima %", 50, 80, 63, 1)
    solo_confluencia = st.checkbox("Solo mostrar confluencias", value=False)

    # ── AUTO-SCAN ──
    st.markdown("---")
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#5a7a99;letter-spacing:2px;margin-bottom:6px;">AUTO-SCAN</div>', unsafe_allow_html=True)
    ar_on = st.checkbox("Escaneo automatico", value=st.session_state.get("autorefresh_on", False), key="ar_on_chk")
    st.session_state.autorefresh_on = ar_on
    if ar_on:
        ar_min = st.selectbox("Frecuencia", [1, 5, 10, 15], index=1, key="ar_min_sel", format_func=lambda x: f"Cada {x} minutos")
        st.session_state.autorefresh_min = ar_min
        if AUTOREFRESH_OK:
            st_autorefresh(interval=ar_min * 60 * 1000, key="autorefresh_main")
        else:
            # Fallback: meta-refresh via HTML
            import time as _time
            ms = ar_min * 60 * 1000
            components_v1.html(f"<script>setTimeout(function(){{window.location.reload();}},{ms});</script>", height=0)
        st.markdown(f'<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#34d399;margin-top:4px;">● SCAN ACTIVO — cada {ar_min} min</div>', unsafe_allow_html=True)

    # ── TELEGRAM ──
    st.markdown("---")
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#5a7a99;letter-spacing:2px;margin-bottom:6px;">NOTIFICACIONES TELEGRAM</div>', unsafe_allow_html=True)
    tg_on = st.checkbox("Alertas Telegram", value=st.session_state.telegram_on, key="tg_on_chk")
    st.session_state.telegram_on = tg_on
    if tg_on:
        tg_tok = st.text_input("Token bot", value=st.session_state.telegram_token, placeholder="8310236833:AAG...", type="password", key="tg_tok_inp", label_visibility="collapsed")
        tg_cid = st.text_input("Chat ID",   value=st.session_state.telegram_chat_id, placeholder="1495197167", key="tg_cid_inp", label_visibility="collapsed")
        if tg_tok: st.session_state.telegram_token   = tg_tok
        if tg_cid: st.session_state.telegram_chat_id = tg_cid
        tg_ok = bool(st.session_state.telegram_token and st.session_state.telegram_chat_id)
        st.markdown(f'<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:{"#34d399" if tg_ok else "#f87171"};margin-bottom:4px;">{"TELEGRAM ACTIVO ✓" if tg_ok else "Completa token y chat ID"}</div>', unsafe_allow_html=True)
        if tg_ok and st.button("Enviar prueba", key="tg_prueba_btn"):
            ok = enviar_telegram(st.session_state.telegram_token, st.session_state.telegram_chat_id,
                "✅ <b>Hector Pattern Detector v5</b> conectado!\n\nLas alertas con Score mayor a 80% llegaran aqui.")
            if ok:
                st.success("✅ Enviado! Revisá Telegram.")
            else:
                st.error("Error al enviar — verificá token y chat ID")

    # ── CAPITAL ──
    st.markdown("---")
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#5a7a99;letter-spacing:2px;margin-bottom:6px;">CAPITAL Y RIESGO</div>', unsafe_allow_html=True)
    cap_val = st.number_input("Capital dia USD", min_value=10.0, max_value=100000.0, value=float(st.session_state.capital_dia), step=10.0, key="cap_sb", label_visibility="collapsed")
    st.session_state.capital_dia = cap_val
    sl_val = st.slider("Stop Loss diario %", 5, 30, int(st.session_state.stop_loss_pct), 1, key="sl_sb")
    st.session_state.stop_loss_pct = sl_val
    sl_monto = cap_val * sl_val / 100
    perdida  = st.session_state.perdida_dia
    pct_used = min(100, int(perdida / sl_monto * 100)) if sl_monto > 0 else 0
    bar_col  = "#34d399" if pct_used < 50 else ("#fbbf24" if pct_used < 80 else "#f87171")
    st.markdown(f"""
    <div style="background:#f0f6fc;border:1px solid #bdd4e8;border-radius:8px;padding:8px;margin-bottom:4px;">
      <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
        <span style="font-family:Share Tech Mono,monospace;font-size:9px;color:#5a7a99;">ENTRADA 1%</span>
        <span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:14px;color:#16a34a;">${cap_val*0.01:.2f}</span>
      </div>
      <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
        <span style="font-family:Share Tech Mono,monospace;font-size:9px;color:#5a7a99;">ENTRADA 2%</span>
        <span style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:14px;color:#c8920a;">${cap_val*0.02:.2f}</span>
      </div>
      <div style="height:5px;background:#bdd4e8;border-radius:3px;overflow:hidden;">
        <div style="height:100%;width:{pct_used}%;background:{bar_col};border-radius:3px;"></div>
      </div>
      <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:{bar_col};margin-top:2px;">Perdida: ${perdida:.2f} / ${sl_monto:.2f}</div>
    </div>""", unsafe_allow_html=True)
    if perdida >= sl_monto and sl_monto > 0:
        st.session_state.radar_bloqueado = True
        st.markdown('<div style="background:#fff0f0;border:2px solid #dc2626;border-radius:6px;padding:6px;text-align:center;font-family:Share Tech Mono,monospace;font-size:10px;color:#dc2626;font-weight:700;">🛑 STOP LOSS — RADAR BLOQUEADO</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("+ Loss", key="add_loss_sb"):
            st.session_state.perdida_dia += cap_val * 0.02
            st.rerun()
    with c2:
        if st.button("Reset", key="reset_sb"):
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
  <div style='font-family:"Rajdhani",sans-serif;font-size:26px;font-weight:700;color:#c8920a;letter-spacing:4px;'>HECTOR PATTERN DETECTOR</div>
  <div style='font-family:"Share Tech Mono",monospace;font-size:9px;color:#3a5570;margin-top:4px;letter-spacing:2px;'>
  8 PATRONES · 6 ACTIVOS · M15 · ATR · MACD · CONFLUENCIA · RANKING · HISTORIAL
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

# ── AUTO-SCAN EN PANTALLA PRINCIPAL ──
with st.container():
    c_scan1, c_scan2, c_scan3 = st.columns([2, 2, 3])
    with c_scan1:
        escanear = st.button("⚡ ESCANEAR AHORA", key="btn_scan", use_container_width=True)
    with c_scan2:
        ar_on_main = st.toggle("Auto-scan", value=st.session_state.get("autorefresh_on", False), key="ar_toggle_main")
        st.session_state.autorefresh_on = ar_on_main
    with c_scan3:
        if ar_on_main:
            ar_min_main = st.select_slider("", options=[1, 5, 10, 15], value=st.session_state.get("autorefresh_min", 5), key="ar_slider_main", format_func=lambda x: f"Cada {x} min")
            st.session_state.autorefresh_min = ar_min_main
            if AUTOREFRESH_OK:
                st_autorefresh(interval=ar_min_main * 60 * 1000, key="autorefresh_main")
            st.markdown(f'<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#34d399;">● ACTIVO — cada {ar_min_main} min</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#5a7a99;margin-top:8px;">Auto-scan desactivado</div>', unsafe_allow_html=True)

# Estado del ultimo scan
if st.session_state.ultimo_scan:
    n_conf = len([a for a in st.session_state.alertas if a.get("n_patrones",1)>=2])
    nc = "#34d399" if st.session_state.alertas else "#475569"
    st.markdown(f"""<div style="display:flex;align-items:center;gap:8px;margin-top:4px;flex-wrap:wrap;">
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

            patrones = [p for p in patrones if p["conf"] >= confianza_min]
            for p in patrones:
                # Alineacion: consideramos ALCISTA(deb) como alcista para no perder señales
                es_alc_tend = "ALCISTA" in tend
                es_baj_tend = "BAJISTA" in tend
                p["alineado"] = (es_alc_tend and p["dir"]=="ALCISTA") or (es_baj_tend and p["dir"]=="BAJISTA")
                p["min_exp"]  = PATRONES.get(p["patron"],{}).get("min_exp", 15)

            patrones_validos = [] if vol_est == "PLANO" else patrones
            pat_alineados    = [p for p in patrones_validos if p.get("alineado")]
            conf_score, conf_label, max_exp, dir_dom = calcular_confluencia(pat_alineados)
            score = calcular_score_activo(patrones_validos, vol_est, tend)

            todos_res.append({
                "activo":activo,"info":info,"patrones":patrones_validos,
                "tendencia":tend,"tend_col":tend_col,
                "vol_est":vol_est,"vol_pct":vol_pct,"vol_msg":vol_msg,"vol_col":vol_col,"vol_cls":vol_cls,
                "precio":precio,"rsi":rsi_v,"sin_datos":False,
                "mercado_plano":vol_est=="PLANO",
                "tiene_senal":len(pat_alineados)>0,
                "n_alineados":len(pat_alineados),
                "conf_score":conf_score,"conf_label":conf_label,
                "dir_dom":dir_dom,"max_exp":max_exp,
                "score":score,
            })
        else:
            todos_res.append({
                "activo":activo,"info":info,"patrones":[],"tendencia":"SIN DATOS",
                "tend_col":"#475569","vol_est":"SIN DATOS","vol_pct":0,
                "vol_msg":"Sin datos","vol_col":"#475569","vol_cls":"atr-flat",
                "precio":0,"rsi":50,"sin_datos":True,"mercado_plano":False,
                "tiene_senal":False,"n_alineados":0,"conf_score":0,
                "conf_label":"SIN SEÑAL","dir_dom":"ALCISTA","max_exp":15,"score":0,
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

    # ── TELEGRAM ──
    if st.session_state.get("telegram_on") and st.session_state.get("telegram_token") and st.session_state.get("telegram_chat_id"):
        for al in [a for a in alertas if a["conf"] >= 80]:
            key_tg = f"tg_{al['activo']}_{al['hora']}"
            enviadas = st.session_state.get("tg_enviadas", set())
            if key_tg not in enviadas:
                acc = "CALL ▲" if al["dir"] == "ALCISTA" else "PUT ▼"
                ic  = "📈" if al["dir"] == "ALCISTA" else "📉"
                cap = st.session_state.get("capital_dia", 467.86)
                msg = (f"{ic} <b>ALERTA — {al['activo']}</b>\n"
                       f"━━━━━━━━━━━━━━\n"
                       f"📊 {acc}\n"
                       f"🎯 Score: {al['conf']}% — {al['conf_label']}\n"
                       f"📌 {al['patrones_nombres']}\n"
                       f"⏱ Expiracion: {al['expiracion']}\n"
                       f"💰 Precio: ${al['precio']:.2f}\n"
                       f"💵 Entrada 2%: <b>${cap*0.02:.2f}</b>\n"
                       f"🕐 {al['hora']} UTC\n"
                       f"<i>Hector Pattern Detector v5</i>")
                ok = enviar_telegram(st.session_state.telegram_token, st.session_state.telegram_chat_id, msg)
                if ok:
                    enviadas.add(key_tg)
                    st.session_state.tg_enviadas = enviadas

    # ── SONIDO ──
    alertas_fuertes = [a for a in alertas if a["conf"] >= 80]
    if alertas_fuertes:
        mejor = alertas_fuertes[0]
        key_s = f"{mejor['activo']}_{mejor['hora']}"
        if key_s != st.session_state.get("ultima_alerta_sonido", ""):
            st.session_state.ultima_alerta_sonido = key_s
            audio_html = """<script>
try {
  var ctx = new (window.AudioContext || window.webkitAudioContext)();
  [880,660,880].forEach(function(f,i){
    var o=ctx.createOscillator(), g=ctx.createGain();
    o.connect(g); g.connect(ctx.destination);
    o.frequency.value=f;
    g.gain.setValueAtTime(0.3, ctx.currentTime+i*0.18);
    g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime+i*0.18+0.15);
    o.start(ctx.currentTime+i*0.18); o.stop(ctx.currentTime+i*0.18+0.15);
  });
} catch(e) {}
</script>"""
            components_v1.html(audio_html, height=0)

    st.rerun()

# ================================================================
# TABS
# ================================================================
tab_radar, tab_ranking, tab_alert, tab_hist, tab_tracker, tab_atr, tab_stats, tab_confirmar = st.tabs([
    "RADAR","RANKING","ALERTAS","HISTORIAL","TRACKER","VOLATILIDAD ATR","ESTADISTICAS","📷 CONFIRMAR"
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

                # Boton IA individual con escaneo en vivo
                if ia_ok:
                    ia_key = f"ia_individual_{i}"
                    ia_resp_key = f"ia_resp_{i}"
                    if ia_resp_key not in st.session_state:
                        st.session_state[ia_resp_key] = ""

                    st.markdown("---")
                    if st.button(f"ANALIZAR ESTA SEÑAL CON IA", key=ia_key):
                        with st.spinner(f"Escaneando {al['activo']} en vivo..."):
                            try:
                                # Descargar datos frescos del activo
                                info_ia = ACTIVOS.get(al["activo"], {})
                                df_ia   = obtener_datos(info_ia.get("yahoo",""))

                                # Construir contexto tecnico detallado
                                checks_txt = "\n".join([f"{'OK' if v else 'FALLA'}: {l}" for l,v in checks])

                                datos_tecnicos = ""
                                if df_ia is not None and len(df_ia) > 50:
                                    rsi_ia   = calc_rsi(df_ia["cierre"]).iloc[-1]
                                    atr_ia   = calc_atr(df_ia).iloc[-1]
                                    atr_avg  = calc_atr(df_ia).iloc[-20:].mean()
                                    ema20_ia = calc_ema(df_ia["cierre"], 20).iloc[-1]
                                    ema50_ia = calc_ema(df_ia["cierre"], 50).iloc[-1]
                                    precio_ia = df_ia["cierre"].iloc[-1]
                                    vela_ant1 = df_ia["cierre"].iloc[-2]
                                    vela_ant2 = df_ia["cierre"].iloc[-3]
                                    _, _, macd_hist = calc_macd(df_ia["cierre"])
                                    macd_v   = macd_hist.iloc[-1]
                                    tend_ia, _ = filtro_tendencia(df_ia)
                                    vol_ia, vol_pct_ia, _, _, _ = analizar_volatilidad(df_ia)
                                    sop_ia, res_ia = calcular_soportes_resistencias(df_ia)

                                    # Ultimas 5 velas
                                    ultimas = df_ia.tail(5)
                                    velas_txt = ""
                                    for _, row in ultimas.iterrows():
                                        color_v = "VERDE" if row["cierre"] > row["apertura"] else "ROJA"
                                        velas_txt += f"  {color_v} O:{row['apertura']:.4f} C:{row['cierre']:.4f} H:{row['maximo']:.4f} L:{row['minimo']:.4f}\n"

                                    datos_tecnicos = f"""
DATOS EN VIVO M15 — {al['activo']}:
Precio actual: {precio_ia:.4f}
Tendencia: {tend_ia}
RSI: {rsi_ia:.1f} {'(SOBRECOMPRA)' if rsi_ia>70 else '(SOBREVENTA)' if rsi_ia<30 else '(NEUTRO)'}
MACD histograma: {macd_v:.4f} {'(POSITIVO - alcista)' if macd_v>0 else '(NEGATIVO - bajista)'}
EMA20: {ema20_ia:.4f} | EMA50: {ema50_ia:.4f}
ATR actual: {atr_ia:.4f} | ATR promedio: {atr_avg:.4f} | Volatilidad: {vol_ia} ({vol_pct_ia:.0f}%)
Soportes cercanos: {[f"{s:.4f}" for s in sop_ia]}
Resistencias cercanas: {[f"{r:.4f}" for r in res_ia]}

Ultimas 5 velas M15:
{velas_txt}"""

                                sys_p = """Eres el analista personal de Hector, trader profesional de IQ Option con opciones binarias M15.
Tu trabajo es analizar la señal y los datos tecnicos en vivo y decirle con claridad si debe ENTRAR AHORA, ESPERAR o NO ENTRAR.
Se muy directo. Maximo 100 palabras. Responde en espanol.
Formato: empieza siempre con la decision en mayusculas (ENTRAR / ESPERAR / NO ENTRAR), luego el por que en 2-3 lineas."""

                                prompt = f"""SEÑAL DETECTADA:
Activo: {al['activo']}
Direccion: {al['dir']} ({'CALL' if al['dir']=='ALCISTA' else 'PUT'})
Patrones: {al['patrones_nombres']}
Score: {al['conf']}% — {al['conf_label']}
Expiracion recomendada: {al['expiracion']}
Precio al detectar: ${al['precio']:.4f}
Hora: {al['hora']} UTC

CHECKLIST AUTOMATICO ({aprobados}/4 OK):
{checks_txt}
{datos_tecnicos}
Capital de Hector: ${st.session_state.get('capital_dia', 467.86):.2f} | Entrada 2%: ${st.session_state.get('capital_dia', 467.86)*0.02:.2f}

Dime: ¿Entra ahora o espera?"""

                                r = requests.post("https://api.anthropic.com/v1/messages",
                                    headers={"Content-Type":"application/json","x-api-key":st.session_state.api_key,"anthropic-version":"2023-06-01"},
                                    json={"model":"claude-sonnet-4-20250514","max_tokens":250,"system":sys_p,
                                          "messages":[{"role":"user","content":prompt}]}, timeout=30)

                                if r.status_code == 200:
                                    st.session_state[ia_resp_key] = r.json()["content"][0]["text"]
                                    st.rerun()
                                else:
                                    st.error(f"Error API: {r.status_code}")
                            except Exception as e:
                                st.error(f"Error: {e}")

                    if st.session_state.get(ia_resp_key):
                        resp_txt = st.session_state[ia_resp_key]
                        if "NO ENTRAR" in resp_txt.upper():
                            rc,rb,rbr = "#dc2626","#fff0f0","#991b1b"
                            ri = "🔴"
                        elif "ESPERAR" in resp_txt.upper():
                            rc,rb,rbr = "#c8920a","#fff8e7","#c8920a"
                            ri = "🟡"
                        else:
                            rc,rb,rbr = "#16a34a","#e8f9f0","#065f46"
                            ri = "🟢"
                        st.markdown(f'''<div style="background:{rb};border:2px solid {rbr};border-radius:10px;padding:14px;margin-top:8px;">
                          <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:22px;color:{rc};margin-bottom:6px;">{ri} ANALISIS IA EN VIVO</div>
                          <div style="font-size:13px;color:#1a2940;line-height:1.8;">{resp_txt.replace(chr(10),"<br>")}</div>
                          <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#5a7a99;margin-top:8px;">Datos frescos M15 · {al["activo"]} · {datetime.now().strftime("%H:%M")}</div>
                        </div>''', unsafe_allow_html=True)

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

# ── CONFIRMAR CON IMAGEN ─────────────────────────
with tab_confirmar:
    st.markdown('<div class="sec">📷 CONFIRMAR ENTRADA — ANALIZADOR DE GRAFICO</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#fff8e7;border:1px solid #c8920a;border-radius:10px;padding:12px 16px;margin-bottom:12px;">
      <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:15px;color:#c8920a;margin-bottom:4px;">Como usar</div>
      <div style="font-size:13px;color:#4a6080;line-height:1.8;">
      1. Llega alerta → ir a IQ Option → abrir grafico M15<br>
      2. Sacar captura de pantalla<br>
      3. Subir la imagen aca<br>
      4. La IA confirma ENTRAR / ESPERAR / NO ENTRAR
      </div>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.api_key.startswith("sk-ant-"):
        st.markdown('<div class="atr-flat"><b style="color:#dc2626;">Necesitas la clave API de Anthropic (sidebar)</b></div>', unsafe_allow_html=True)
    else:
        c1, c2 = st.columns(2)
        with c1:
            activo_conf = st.selectbox("Activo", list(ACTIVOS.keys()), key="act_conf_sel")
        with c2:
            dir_conf = st.selectbox("Direccion esperada", ["ALCISTA (CALL)", "BAJISTA (PUT)"], key="dir_conf_sel")

        img_file = st.file_uploader("Captura del grafico M15", type=["png","jpg","jpeg","webp"], key="img_up", label_visibility="collapsed")

        if img_file:
            st.image(img_file, use_column_width=True)
            if st.button("ANALIZAR CON IA", key="btn_analizar_img"):
                with st.spinner("Analizando grafico..."):
                    try:
                        img_b64 = base64.b64encode(img_file.read()).decode()
                        ext = img_file.name.split(".")[-1].lower()
                        mtype = "image/jpeg" if ext in ("jpg","jpeg") else f"image/{ext}"
                        dir_limpia = "CALL (alcista)" if "ALCISTA" in dir_conf else "PUT (bajista)"
                        ctx = ""
                        if st.session_state.alertas:
                            al = next((a for a in st.session_state.alertas if a["activo"]==activo_conf), None)
                            if al: ctx = f"El detector encontro: {al['patrones_nombres']} con score {al['conf']}%."
                        sys_p = f"""Eres el analista personal de Hector, trader de IQ Option en M15.
Hector considera entrar {dir_limpia} en {activo_conf}. {ctx}
Analiza el grafico y responde:
1. DECISION: ENTRAR / ESPERAR / NO ENTRAR (en grande)
2. Por que — maximo 2 lineas
3. Que debe ver para confirmar
Directo, sin rodeos. Maximo 80 palabras. En espanol."""
                        resp = requests.post("https://api.anthropic.com/v1/messages",
                            headers={"Content-Type":"application/json","x-api-key":st.session_state.api_key,"anthropic-version":"2023-06-01"},
                            json={"model":"claude-sonnet-4-20250514","max_tokens":300,"system":sys_p,
                                  "messages":[{"role":"user","content":[
                                      {"type":"image","source":{"type":"base64","media_type":mtype,"data":img_b64}},
                                      {"type":"text","text":f"Analiza este grafico M15 de {activo_conf} — entro {dir_limpia}?"}
                                  ]}]}, timeout=45)
                        if resp.status_code == 200:
                            txt_resp = resp.json()["content"][0]["text"]
                            if "ENTRAR" in txt_resp.upper() and "NO ENTRAR" not in txt_resp.upper():
                                dc,db,dbr,di = "#16a34a","#e8f9f0","#065f46","🟢"
                            elif "ESPERAR" in txt_resp.upper():
                                dc,db,dbr,di = "#c8920a","#fff8e7","#c8920a","🟡"
                            else:
                                dc,db,dbr,di = "#dc2626","#fff0f0","#991b1b","🔴"
                            st.markdown(f"""<div style="background:{db};border:2px solid {dbr};border-radius:12px;padding:16px;margin-top:10px;">
                              <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:26px;color:{dc};margin-bottom:8px;">{di} ANALISIS IA</div>
                              <div style="font-size:14px;color:#1a2940;line-height:1.8;">{txt_resp.replace(chr(10),"<br>")}</div>
                              <div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#5a7a99;margin-top:8px;">{activo_conf} · {dir_conf} · {datetime.now().strftime("%H:%M")}</div>
                            </div>""", unsafe_allow_html=True)
                        else:
                            st.error(f"Error API {resp.status_code}")
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.markdown("""<div style="text-align:center;padding:40px 20px;background:#f0f6fc;border:2px dashed #bdd4e8;border-radius:12px;margin-top:10px;">
              <div style="font-size:48px;margin-bottom:10px;">📱</div>
              <div style="font-family:Rajdhani,sans-serif;font-size:18px;color:#4a6080;">Subi la captura de IQ Option</div>
              <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#5a7a99;margin-top:6px;">iPhone: screenshot → subir aca</div>
            </div>""", unsafe_allow_html=True)

# FOOTER
# ================================================================
st.markdown("""
<div style="border-top:1px solid #bdd4e8;margin-top:24px;padding-top:10px;
text-align:center;font-family:'Share Tech Mono',monospace;font-size:9px;color:#6a8aaa;letter-spacing:2px;">
HECTOR PATTERN DETECTOR v4 · ATR · MACD · CONFLUENCIA · RANKING · HISTORIAL · TRACKER · 8 PATRONES · 6 ACTIVOS
</div>""", unsafe_allow_html=True)
