# QQE 03/04 - HECTOR TRADING COMMAND
# Dashboard completo con IA integrada
#
# INSTALACION (una sola vez):
#   pip install streamlit requests
#
# EJECUCION:
#   streamlit run qqe_trading.py

import streamlit as st
import requests
import json
from datetime import datetime, timezone

# ═══════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="QQE 03/04 — Hector Trading",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════
# CSS — TEMA CLARO PROFESIONAL
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&family=Inter:wght@300;400;500&display=swap');

html, body, .stApp { background: #f0f4f8 !important; }
.stApp { font-family: 'Inter', sans-serif; color: #334155; }

[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #ffffff;
    border-bottom: 2px solid #e2e8f0;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #94a3b8 !important;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    letter-spacing: 1px;
    padding: 10px 18px;
    border: none;
}
.stTabs [aria-selected="true"] {
    background: #f0f4f8 !important;
    color: #0f172a !important;
    border-bottom: 2px solid #92650a !important;
    font-weight: 700 !important;
}

/* Cards */
.card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 10px;
    box-shadow: 0 1px 3px rgba(0,0,0,.06);
}
.card-gold   { border-left: 4px solid #92650a; }
.card-green  { border-left: 4px solid #076f45; }
.card-red    { border-left: 4px solid #b91c1c; }
.card-blue   { border-left: 4px solid #1d4ed8; }
.card-purple { border-left: 4px solid #6d28d9; }
.card-gray   { border-left: 4px solid #94a3b8; }

/* KPI */
.kpi { background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:14px 16px; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,.06); }
.kpi-label { font-family:'Share Tech Mono',monospace; font-size:9px; color:#94a3b8; letter-spacing:2px; text-transform:uppercase; margin-bottom:6px; }
.kpi-value { font-family:'Rajdhani',sans-serif; font-size:28px; font-weight:700; line-height:1.1; }
.kpi-sub   { font-family:'Share Tech Mono',monospace; font-size:10px; color:#94a3b8; margin-top:3px; }

/* Section title */
.sec { font-family:'Share Tech Mono',monospace; font-size:10px; color:#94a3b8; letter-spacing:3px; text-transform:uppercase; border-bottom:2px solid #e2e8f0; padding-bottom:6px; margin:16px 0 12px; }

/* Semáforo */
.sem {
    border-radius:8px; padding:14px 16px; border:1px solid;
    display:flex; align-items:center; gap:12px;
    margin-bottom:6px; cursor:pointer;
}
.sem-verde  { background:#f0fdf4; border-color:#86efac; }
.sem-yellow { background:#fefce8; border-color:#fde047; }
.sem-red    { background:#fef2f2; border-color:#fca5a5; }
.sem-black  { background:#f8fafc; border-color:#cbd5e1; }

/* Badges */
.badge {
    display:inline-block; padding:3px 10px; border-radius:20px;
    font-family:'Share Tech Mono',monospace; font-size:9px; letter-spacing:1px;
    font-weight:700;
}
.badge-green  { background:#dcfce7; color:#076f45; border:1px solid #86efac; }
.badge-red    { background:#fef2f2; color:#b91c1c; border:1px solid #fca5a5; }
.badge-gold   { background:#fef9ee; color:#92650a; border:1px solid #fcd34d; }
.badge-blue   { background:#dbeafe; color:#1d4ed8; border:1px solid #93c5fd; }
.badge-purple { background:#ede9fe; color:#6d28d9; border:1px solid #c4b5fd; }
.badge-gray   { background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; }

/* IA Box */
.ai-box {
    background:#fffbeb; border:1px solid #fcd34d; border-radius:8px;
    padding:16px; min-height:100px; font-size:14px; line-height:1.8;
    color:#334155;
}
.ai-placeholder {
    font-family:'Share Tech Mono',monospace; font-size:11px;
    color:#94a3b8; letter-spacing:1px;
}

/* Chips */
.chip-row { display:flex; flex-wrap:wrap; gap:6px; margin-top:8px; }
.chip {
    background:#f1f5f9; border:1px solid #e2e8f0; color:#64748b;
    padding:5px 12px; border-radius:20px;
    font-family:'Share Tech Mono',monospace; font-size:9px; letter-spacing:1px;
    cursor:pointer;
}

/* Ticker */
.ticker-wrap { background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; overflow:hidden; padding:8px 0; margin-bottom:14px; }
.ticker-inner { display:inline-block; white-space:nowrap; animation:ticker 35s linear infinite; font-family:'Share Tech Mono',monospace; font-size:11px; }
@keyframes ticker { 0%{transform:translateX(100vw)} 100%{transform:translateX(-100%)} }
.t-up   { color:#076f45; margin:0 20px; }
.t-down { color:#b91c1c; margin:0 20px; }

/* Progress bar */
.prog-track { height:14px; background:#e2e8f0; border-radius:7px; overflow:hidden; margin:8px 0; }
.prog-fill  { height:100%; border-radius:7px; background:linear-gradient(90deg,#fcd34d,#92650a); transition:width .6s ease; }

/* Asset card */
.asset { background:#ffffff; border:1px solid #e2e8f0; border-radius:6px; padding:12px; cursor:pointer; transition:border-color .2s; margin-bottom:6px; }
.asset:hover { border-color:#92650a; }
.asset.active { border-color:#076f45; background:#f0fdf4; }
.asset-bar { height:4px; background:#e2e8f0; border-radius:2px; overflow:hidden; margin:6px 0; }
.asset-fill-green  { height:100%; border-radius:2px; background:linear-gradient(90deg,#86efac,#076f45); }
.asset-fill-gold   { height:100%; border-radius:2px; background:linear-gradient(90deg,#fcd34d,#92650a); }
.asset-fill-blue   { height:100%; border-radius:2px; background:linear-gradient(90deg,#93c5fd,#1d4ed8); }
.asset-fill-purple { height:100%; border-radius:2px; background:linear-gradient(90deg,#c4b5fd,#6d28d9); }
.asset-fill-gray   { height:100%; border-radius:2px; background:#cbd5e1; }

/* Code block */
.code-block {
    background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px;
    padding:14px; font-family:'Share Tech Mono',monospace; font-size:10px;
    line-height:1.8; color:#1e293b; white-space:pre; overflow-x:auto;
    margin-bottom:8px; max-height:260px; overflow-y:auto;
}

/* Horario row */
.h-row { display:flex; align-items:center; gap:10px; padding:10px 14px; border-radius:6px; border:1px solid #e2e8f0; margin-bottom:6px; font-size:12px; }

/* News item */
.news-item { padding:10px 0; border-bottom:1px solid #f1f5f9; }
.news-item:last-child { border-bottom:none; }

/* Trader card */
.trader { background:#ffffff; border-left:4px solid; border-radius:0 6px 6px 0; padding:12px 14px; margin-bottom:8px; box-shadow:0 1px 3px rgba(0,0,0,.04); }

/* Inputs */
.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    background:#ffffff !important; border:1px solid #e2e8f0 !important;
    color:#0f172a !important; font-family:'Inter',sans-serif !important;
    border-radius:6px !important;
}
.stTextInput>div>div>input:focus { border-color:#92650a !important; }

/* Buttons */
.stButton>button {
    background:#0f172a !important; color:#ffffff !important;
    border:none !important; border-radius:6px !important;
    font-family:'Share Tech Mono',monospace !important;
    font-size:11px !important; letter-spacing:1px !important;
    padding:8px 20px !important;
}
.stButton>button:hover { background:#1e293b !important; }

/* Select */
.stSelectbox>div>div { background:#ffffff !important; border:1px solid #e2e8f0 !important; color:#0f172a !important; border-radius:6px !important; }

/* Number input */
.stNumberInput>div>div>input { background:#ffffff !important; border:1px solid #e2e8f0 !important; color:#0f172a !important; border-radius:6px !important; }

::-webkit-scrollbar { width:4px; height:4px; }
::-webkit-scrollbar-track { background:#f1f5f9; }
::-webkit-scrollbar-thumb { background:#cbd5e1; border-radius:2px; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════
if "ops"         not in st.session_state: st.session_state.ops = []
if "semaforo"    not in st.session_state: st.session_state.semaforo = "verde"
if "ai_response" not in st.session_state: st.session_state.ai_response = ""
if "ai_loading"  not in st.session_state: st.session_state.ai_loading = False
if "api_key"     not in st.session_state: st.session_state.api_key = ""

# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════
def get_utc_hour():
    return datetime.now(timezone.utc).hour

def get_session_info():
    h = get_utc_hour()
    if 7 <= h < 10:
        return "🟢 SESIÓN LONDRES", "OPERAR", "#076f45", "#f0fdf4", "#86efac"
    elif 13 <= h < 16:
        return "🟢 SESIÓN NUEVA YORK", "OPERAR", "#076f45", "#f0fdf4", "#86efac"
    elif 16 <= h < 17:
        return "🟡 SOLAPAMIENTO", "PRECAUCIÓN", "#92650a", "#fefce8", "#fde047"
    elif 11 <= h < 13:
        return "🔴 ZONA MUERTA", "NO OPERAR", "#b91c1c", "#fef2f2", "#fca5a5"
    else:
        return "⚫ MERCADO CERRADO", "INACTIVO", "#64748b", "#f8fafc", "#e2e8f0"

def calc_pnl():
    ganado  = sum(o["pnl"] for o in st.session_state.ops if o["pnl"] > 0)
    perdido = abs(sum(o["pnl"] for o in st.session_state.ops if o["pnl"] < 0))
    neto    = ganado - perdido
    return ganado, perdido, neto

def ask_claude(api_key, question):
    h = get_utc_hour()
    ses_name, _, _, _, _ = get_session_info()
    ganado, _, neto = calc_pnl()
    system_prompt = f"""Eres el asistente de trading de Hector. Opera CFDs en IQ Option M15/H1 con dos scripts:
QQE 03 (Forex): EMA100+EMA200+MACD manual(e12-e26)+Estocástico manual(sk)+RSI. Activos: XAU/USD, Crude Oil, EUR/USD, NAS100.
QQE 04 Crypto: igual pero EMA50, ventana S/R 30, sk<85/sk>15. Activos: BTC, ETH, SOL.
Estado actual: Sesión UTC {ses_name}. Capital $467.86. Ganado hoy ${ganado:.2f}. Neto hoy ${neto:.2f}. Objetivo $50/día. Riesgo máx 2%=$9.36.
Contexto Marzo 2026: XAU/USD alcista, DXY débil, Fed dovish, BTC ~$67K, ETH subiendo.
Responde en español. Máx 180 palabras. Directo y accionable. Menciona horario UTC actual ({h}:00 UTC). Usá emojis: ✅ ⚠️ 📈 📉 🎯 🕐"""
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 400,
                "system": system_prompt,
                "messages": [{"role": "user", "content": question}]
            },
            timeout=30
        )
        data = r.json()
        if r.status_code == 200:
            return data["content"][0]["text"]
        else:
            err = data.get("error", {}).get("message", str(data))
            return f"⚠ Error API: {err}"
    except requests.exceptions.Timeout:
        return "⚠ Timeout — la API tardó demasiado. Intentá de nuevo."
    except Exception as e:
        return f"⚠ Error de conexión: {str(e)}"


# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='font-family:"Rajdhani",sans-serif;font-size:20px;font-weight:700;
    color:#0f172a;letter-spacing:2px;border-bottom:2px solid #e2e8f0;
    padding-bottom:10px;margin-bottom:14px;'>
    ⚡ QQE 03/04 COMMAND
    </div>""", unsafe_allow_html=True)

    # Sesión activa
    ses_label, ses_estado, ses_color, ses_bg, ses_border = get_session_info()
    st.markdown(f"""
    <div style='background:{ses_bg};border:1px solid {ses_border};border-radius:6px;
    padding:10px 14px;margin-bottom:12px;'>
    <div style='font-family:"Share Tech Mono",monospace;font-size:11px;font-weight:700;color:{ses_color};'>{ses_label}</div>
    <div style='font-family:"Share Tech Mono",monospace;font-size:9px;color:{ses_color};letter-spacing:1px;'>{ses_estado} · {datetime.now(timezone.utc).strftime("%H:%M:%S")} UTC</div>
    </div>""", unsafe_allow_html=True)

    # API Key
    st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:9px;color:#94a3b8;letter-spacing:2px;margin-bottom:4px;">🔑 ANTHROPIC API KEY</div>', unsafe_allow_html=True)
    api_key_input = st.text_input("", value=st.session_state.api_key,
                                   placeholder="sk-ant-api03-...",
                                   type="password", label_visibility="collapsed")
    if api_key_input:
        st.session_state.api_key = api_key_input
    if st.session_state.api_key.startswith("sk-ant-"):
        st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:10px;color:#076f45;">✅ KEY CARGADA — IA ACTIVA</div>', unsafe_allow_html=True)
    elif st.session_state.api_key:
        st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:10px;color:#b91c1c;">⚠ Formato incorrecto</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:10px;color:#94a3b8;">Sin key — IA desactivada</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Capital y riesgo
    st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:9px;color:#94a3b8;letter-spacing:2px;margin-bottom:4px;">💰 CAPITAL (USD)</div>', unsafe_allow_html=True)
    capital = st.number_input("", min_value=10.0, max_value=100000.0,
                               value=467.86, step=10.0, label_visibility="collapsed")
    riesgo_pct = st.slider("Riesgo %", 0.5, 5.0, 2.0, 0.5)
    importe_max = int(capital * riesgo_pct / 100)

    st.markdown(f"""
    <div style='background:#fef9ee;border:1px solid #fcd34d;border-radius:6px;
    padding:10px 14px;font-family:"Share Tech Mono",monospace;font-size:10px;'>
    <span style='color:#94a3b8;'>IMPORTE MÁX:</span> <strong style='color:#92650a;font-size:16px;'>${importe_max}</strong><br>
    <span style='color:#94a3b8;'>RIESGO MÁX:</span> <span style='color:#b91c1c;'>${capital*riesgo_pct/100:.2f}</span><br>
    <span style='color:#94a3b8;'>OPS P/$50:</span> <span style='color:#076f45;'>~{max(1,int(50/(importe_max*2+0.01)))}</span>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Semáforo
    st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:9px;color:#94a3b8;letter-spacing:2px;margin-bottom:6px;">🚦 SEMÁFORO</div>', unsafe_allow_html=True)
    sem_choice = st.radio("", ["🟢 VERDE — OPERAR", "🟡 AMARILLO — REDUCIR",
                                "🔴 ROJO — PARAR", "⚫ NEGRO — EMERGENCIA"],
                           index=0, label_visibility="collapsed")
    st.session_state.semaforo = sem_choice.split("—")[0].strip()

    st.markdown("---")
    if st.button("🗑 Reset operaciones"):
        st.session_state.ops = []
        st.rerun()


# ═══════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════
ganado, perdido, neto = calc_pnl()
pct_obj = min(100, max(0, (neto / 50) * 100))

st.markdown(f"""
<div style='background:#ffffff;border:1px solid #e2e8f0;border-radius:10px;
padding:16px 22px;margin-bottom:14px;display:flex;align-items:center;
justify-content:space-between;box-shadow:0 1px 4px rgba(0,0,0,.06);'>
  <div>
    <div style='font-family:"Rajdhani",sans-serif;font-size:22px;font-weight:700;
    color:#0f172a;letter-spacing:3px;'>⚡ QQE 03/04 — HECTOR TRADING COMMAND</div>
    <div style='font-family:"Share Tech Mono",monospace;font-size:9px;color:#94a3b8;
    letter-spacing:2px;margin-top:2px;'>IQ OPTION · M15 / H1 · FOREX & CRYPTO · OBJETIVO $50/DÍA</div>
  </div>
  <div style='text-align:right;'>
    <div style='font-family:"Share Tech Mono",monospace;font-size:11px;color:#0f172a;font-weight:700;'>{ses_label}</div>
    <div style='font-family:"Share Tech Mono",monospace;font-size:10px;color:#94a3b8;'>{datetime.now(timezone.utc).strftime("%d/%m/%Y · %H:%M UTC")}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Ticker
tickers = [
    ("XAU/USD","2,341.50","+0.42%",True), ("CRUDE OIL","77.18","-0.31%",False),
    ("EUR/USD","1.0842","+0.18%",True), ("BTC","67,420","+1.23%",True),
    ("ETH","3,480","+0.88%",True), ("NAS100","18,240","-0.22%",False),
    ("SOL","182","+2.1%",True), ("GBP/USD","1.2631","-0.09%",False),
]
ticker_html = '<div class="ticker-wrap"><div class="ticker-inner">'
for sym, price, chg, up in tickers * 2:
    cls = "t-up" if up else "t-down"
    ticker_html += f'<span class="{cls}">◆ {sym} {price} {chg}</span>'
ticker_html += '</div></div>'
st.markdown(ticker_html, unsafe_allow_html=True)

# KPIs
k1,k2,k3,k4,k5 = st.columns(5)
for col, label, val, color, sub in [
    (k1,"GANADO HOY",   f"${ganado:.2f}",  "#076f45", f"{len([o for o in st.session_state.ops if o['pnl']>0])} ops win"),
    (k2,"PERDIDO HOY",  f"${perdido:.2f}", "#b91c1c", f"{len([o for o in st.session_state.ops if o['pnl']<0])} ops loss"),
    (k3,"NETO HOY",     f"${neto:.2f}",    "#076f45" if neto>=0 else "#b91c1c", f"{pct_obj:.0f}% del objetivo"),
    (k4,"OBJETIVO",     "$50.00",          "#92650a", f"Faltan ${max(0,50-neto):.2f}"),
    (k5,"IMPORTE MÁX",  f"${importe_max}", "#1d4ed8", f"Riesgo {riesgo_pct}%"),
]:
    with col:
        st.markdown(f"""
        <div class="kpi">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value" style="color:{color};">{val}</div>
          <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

# Barra de progreso $50
st.markdown(f"""
<div class="card card-gold" style="margin-top:8px;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
    <span style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:16px;color:#0f172a;">Progreso — Objetivo del Día</span>
    <span style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:28px;color:#92650a;">{pct_obj:.0f}%</span>
  </div>
  <div class="prog-track"><div class="prog-fill" style="width:{pct_obj}%;"></div></div>
  <div style="display:flex;justify-content:space-between;font-family:'Share Tech Mono',monospace;font-size:9px;color:#94a3b8;">
    <span>$0</span><span>$12.50</span><span>$25</span><span>$37.50</span><span>$50</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════
tab_ia, tab_ops, tab_activos, tab_horarios, tab_noticias, tab_codigos = st.tabs([
    "⚡ IA ANALYST", "📝 REGISTRO", "📊 ACTIVOS", "🕐 SESIONES", "📡 NOTICIAS", "⚙ CÓDIGOS QQE"
])


# ══════════════════════════════════════════════
# TAB 1 — IA ANALYST
# ══════════════════════════════════════════════
with tab_ia:
    st.markdown('<div class="sec">⚡ RECOMENDACIONES IA — QQE 03/04 ANALYST · CLAUDE AI</div>', unsafe_allow_html=True)

    if not st.session_state.api_key.startswith("sk-ant-"):
        st.markdown("""
        <div style="background:#fef9ee;border:1px solid #fcd34d;border-radius:8px;
        padding:16px;font-family:'Share Tech Mono',monospace;font-size:11px;color:#92650a;">
        🔑 Pegá tu API key en el sidebar izquierdo para activar la IA.<br>
        La key empieza con <strong>sk-ant-api03-...</strong>
        </div>""", unsafe_allow_html=True)
    else:
        # Quick chips
        st.markdown("**Consultas rápidas:**")
        chips = [
            "¿Es buen momento para operar Oro ahora?",
            "¿Estoy en horario óptimo de trading?",
            "¿Qué activo tiene mejor setup hoy?",
            "Dame el plan operativo completo para esta sesión",
            "¿Cómo uso QQE 03 diferente en H1 vs M15?",
            "Tengo 3 señales seguidas de SELL en Oro, ¿entro?",
            "¿BTC o ETH tiene mejor setup ahora con QQE 04?",
            f"¿Cómo gestiono el riesgo si mi capital es ${capital:.0f}?",
            "¿Cuándo debo parar de operar hoy?",
        ]
        cols_chips = st.columns(3)
        for i, chip in enumerate(chips):
            with cols_chips[i % 3]:
                if st.button(chip[:35]+"…" if len(chip)>35 else chip, key=f"chip_{i}"):
                    st.session_state.ai_query = chip

        # Input manual
        query = st.text_input("O escribí tu consulta:",
                               value=st.session_state.get("ai_query",""),
                               placeholder="Ej: ¿Qué activo operar ahora? ¿BTC o Oro?")

        if st.button("▶ CONSULTAR IA", key="ask_ai_btn"):
            if query.strip():
                with st.spinner("⏳ Analizando mercado..."):
                    st.session_state.ai_response = ask_claude(st.session_state.api_key, query)
                if "ai_query" in st.session_state:
                    del st.session_state.ai_query
            else:
                st.warning("Escribí una consulta primero")

    # Respuesta
    if st.session_state.ai_response:
        st.markdown('<div class="sec">RESPUESTA DEL ANALISTA</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="ai-box">
        {st.session_state.ai_response.replace(chr(10), '<br>')}
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="ai-box">
        <span class="ai-placeholder">Escribí tu consulta — analizo mercado, horario, noticias, QQE 03 Forex y QQE 04 Crypto...</span>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 2 — REGISTRO DE OPERACIONES
# ══════════════════════════════════════════════
with tab_ops:
    st.markdown('<div class="sec">📝 REGISTRO DE OPERACIONES DEL DÍA</div>', unsafe_allow_html=True)

    col_form, col_list = st.columns([1, 2])

    with col_form:
        st.markdown("**Nueva operación:**")
        activo   = st.selectbox("Activo", ["XAU/USD","CRUDE OIL","EUR/USD","NAS100","BTC","ETH","SOL"])
        direccion = st.selectbox("Dirección", ["LONG ▲","SHORT ▼"])
        importe_op = st.number_input("Importe ($)", min_value=1.0, max_value=500.0,
                                      value=float(importe_max), step=1.0)
        script_op  = st.selectbox("Script", ["QQE 03","QQE 04 Crypto"])

        c_win, c_loss = st.columns(2)
        with c_win:
            if st.button("✅ GANADA", key="btn_win"):
                st.session_state.ops.append({
                    "activo": activo, "dir": direccion.split()[0],
                    "importe": importe_op, "pnl": round(importe_op * 2, 2),
                    "script": script_op,
                    "hora": datetime.now().strftime("%H:%M"),
                    "result": "win"
                })
                st.rerun()
        with c_loss:
            if st.button("❌ PERDIDA", key="btn_loss"):
                st.session_state.ops.append({
                    "activo": activo, "dir": direccion.split()[0],
                    "importe": importe_op, "pnl": -importe_op,
                    "script": script_op,
                    "hora": datetime.now().strftime("%H:%M"),
                    "result": "loss"
                })
                st.rerun()

        # Alerta semáforo
        g2, p2, n2 = calc_pnl()
        if n2 >= 50:
            st.markdown('<div class="card card-gold" style="padding:10px;margin-top:8px;"><b style="color:#92650a;">🎯 OBJETIVO $50 ALCANZADO — CERRAR PLATAFORMA</b></div>', unsafe_allow_html=True)
        elif n2 <= -capital * 0.06:
            st.markdown('<div class="card card-red" style="padding:10px;margin-top:8px;"><b style="color:#b91c1c;">🔴 LÍMITE -6% ALCANZADO — PARAR HOY</b></div>', unsafe_allow_html=True)

        # Tabla rápida riesgo
        st.markdown('<div class="sec">TABLA RÁPIDA</div>', unsafe_allow_html=True)
        for pct_r, mult in [(0.5,"x5"),(1.0,"x10"),(1.5,"x15"),(2.0,"x20")]:
            r = capital * pct_r / 100
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:5px 0;
            border-bottom:1px solid #f1f5f9;font-family:'Share Tech Mono',monospace;font-size:10px;">
            <span style="color:#94a3b8;">{mult}</span>
            <span>Riesgo: <b style="color:#b91c1c;">${r:.2f}</b></span>
            <span style="color:#92650a;">Imp: ${int(r)}</span>
            <span style="color:#076f45;">TP: ${int(r)*2}</span>
            </div>""", unsafe_allow_html=True)

    with col_list:
        st.markdown("**Historial del día:**")
        if not st.session_state.ops:
            st.markdown('<div style="text-align:center;padding:30px;font-family:\'Share Tech Mono\',monospace;font-size:11px;color:#94a3b8;">Sin operaciones hoy — registrá la primera</div>', unsafe_allow_html=True)
        else:
            for i, op in enumerate(reversed(st.session_state.ops)):
                color = "#076f45" if op["result"]=="win" else "#b91c1c"
                bg    = "#f0fdf4" if op["result"]=="win" else "#fef2f2"
                border= "#86efac" if op["result"]=="win" else "#fca5a5"
                sign  = "+" if op["pnl"] > 0 else ""
                st.markdown(f"""
                <div style="background:{bg};border:1px solid {border};border-radius:6px;
                padding:10px 14px;margin-bottom:6px;display:flex;align-items:center;
                justify-content:space-between;font-family:'Share Tech Mono',monospace;">
                  <div>
                    <span style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:15px;color:#0f172a;">{op['activo']}</span>
                    <span style="font-size:10px;color:#64748b;margin-left:8px;">{op['dir']} · {op['script']} · {op['hora']}</span>
                  </div>
                  <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:20px;color:{color};">
                    {sign}${abs(op['pnl']):.2f}
                  </div>
                </div>""", unsafe_allow_html=True)

            # Resumen
            g3, p3, n3 = calc_pnl()
            n_color = "#076f45" if n3 >= 0 else "#b91c1c"
            st.markdown(f"""
            <div class="card card-gold" style="margin-top:12px;">
              <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;text-align:center;">
                <div><div style="font-family:'Share Tech Mono',monospace;font-size:9px;color:#94a3b8;">GANADO</div>
                <div style="font-family:'Rajdhani',sans-serif;font-size:22px;font-weight:700;color:#076f45;">${g3:.2f}</div></div>
                <div><div style="font-family:'Share Tech Mono',monospace;font-size:9px;color:#94a3b8;">PERDIDO</div>
                <div style="font-family:'Rajdhani',sans-serif;font-size:22px;font-weight:700;color:#b91c1c;">${p3:.2f}</div></div>
                <div><div style="font-family:'Share Tech Mono',monospace;font-size:9px;color:#94a3b8;">NETO</div>
                <div style="font-family:'Rajdhani',sans-serif;font-size:22px;font-weight:700;color:{n_color};">${n3:.2f}</div></div>
              </div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 3 — ACTIVOS
# ══════════════════════════════════════════════
with tab_activos:
    st.markdown('<div class="sec">📊 ACTIVOS RECOMENDADOS — PLAN DE TRADING</div>', unsafe_allow_html=True)

    col_forex, col_crypto = st.columns(2)

    with col_forex:
        st.markdown("""
        <div style="font-family:'Share Tech Mono',monospace;font-size:9px;color:#92650a;
        letter-spacing:2px;margin-bottom:10px;padding-bottom:5px;border-bottom:2px solid #fcd34d;">
        FOREX & MATERIAS PRIMAS — QQE 03
        </div>""", unsafe_allow_html=True)

        assets_forex = [
            ("XAU/USD","2,341.50","LONG ▲","72","#076f45","asset-fill-green","78","EMA100 pullback","2,338","2,322","2,374"),
            ("CRUDE OIL","77.18","LONG ▲","56","#92650a","asset-fill-gold","62","Soporte WTI","76.90","76.20","78.30"),
            ("EUR/USD","1.0842","LONG ▲","63","#1d4ed8","asset-fill-blue","65","Zona demanda","1.0820","1.0785","1.0890"),
            ("NAS100","18,240","ESPERAR ⏸","45","#64748b","asset-fill-gray","45","Sin setup","—","—","—"),
        ]
        for sym, price, dir_, sent, col, fill, conf, nota, e, sl, tp in assets_forex:
            dir_color = "#076f45" if "LONG" in dir_ else ("#b91c1c" if "SHORT" in dir_ else "#64748b")
            dir_bg    = "#dcfce7" if "LONG" in dir_ else ("#fef2f2" if "SHORT" in dir_ else "#f1f5f9")
            st.markdown(f"""
            <div class="asset">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                <span style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:18px;color:#0f172a;">{sym}</span>
                <span style="background:{dir_bg};color:{dir_color};padding:3px 10px;border-radius:20px;
                font-family:'Share Tech Mono',monospace;font-size:9px;font-weight:700;">{dir_}</span>
              </div>
              <div style="font-family:'Share Tech Mono',monospace;font-size:13px;color:#334155;">{price}</div>
              <div class="asset-bar"><div class="{fill}" style="width:{sent}%;"></div></div>
              <div style="display:flex;justify-content:space-between;font-family:'Share Tech Mono',monospace;font-size:9px;color:#94a3b8;">
                <span style="color:{col};">▲ {sent}% LONG</span><span>Conf: {conf}%</span>
              </div>
              <div style="margin-top:8px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;">
                <div style="background:#dbeafe;border-radius:4px;padding:6px;text-align:center;">
                  <div style="font-family:'Share Tech Mono',monospace;font-size:8px;color:#94a3b8;">ENTRADA</div>
                  <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:14px;color:#1d4ed8;">{e}</div>
                </div>
                <div style="background:#fef2f2;border-radius:4px;padding:6px;text-align:center;">
                  <div style="font-family:'Share Tech Mono',monospace;font-size:8px;color:#94a3b8;">STOP</div>
                  <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:14px;color:#b91c1c;">{sl}</div>
                </div>
                <div style="background:#f0fdf4;border-radius:4px;padding:6px;text-align:center;">
                  <div style="font-family:'Share Tech Mono',monospace;font-size:8px;color:#94a3b8;">TP</div>
                  <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:14px;color:#076f45;">{tp}</div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

    with col_crypto:
        st.markdown("""
        <div style="font-family:'Share Tech Mono',monospace;font-size:9px;color:#6d28d9;
        letter-spacing:2px;margin-bottom:10px;padding-bottom:5px;border-bottom:2px solid #c4b5fd;">
        CRYPTO — QQE 04
        </div>""", unsafe_allow_html=True)

        assets_crypto = [
            ("BTC","67,420","LONG ▲","70","#92650a","asset-fill-gold","70","EMA50 QQE04","66,800","65,500","69,400"),
            ("ETH","3,480","LONG ▲","61","#6d28d9","asset-fill-purple","60","Soporte ETH","3,440","3,360","3,600"),
            ("SOL","182","ESPERAR ⏸","42","#64748b","asset-fill-gray","42","Sin setup","—","—","—"),
        ]
        for sym, price, dir_, sent, col, fill, conf, nota, e, sl, tp in assets_crypto:
            dir_color = "#076f45" if "LONG" in dir_ else ("#b91c1c" if "SHORT" in dir_ else "#64748b")
            dir_bg    = "#dcfce7" if "LONG" in dir_ else ("#fef2f2" if "SHORT" in dir_ else "#f1f5f9")
            st.markdown(f"""
            <div class="asset">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                <span style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:18px;color:#0f172a;">{sym}</span>
                <span style="background:{dir_bg};color:{dir_color};padding:3px 10px;border-radius:20px;
                font-family:'Share Tech Mono',monospace;font-size:9px;font-weight:700;">{dir_}</span>
              </div>
              <div style="font-family:'Share Tech Mono',monospace;font-size:13px;color:#334155;">{price}</div>
              <div class="asset-bar"><div class="{fill}" style="width:{sent}%;"></div></div>
              <div style="display:flex;justify-content:space-between;font-family:'Share Tech Mono',monospace;font-size:9px;color:#94a3b8;">
                <span style="color:{col};">▲ {sent}% LONG</span><span>Conf: {conf}%</span>
              </div>
              <div style="margin-top:8px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;">
                <div style="background:#dbeafe;border-radius:4px;padding:6px;text-align:center;">
                  <div style="font-family:'Share Tech Mono',monospace;font-size:8px;color:#94a3b8;">ENTRADA</div>
                  <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:14px;color:#1d4ed8;">{e}</div>
                </div>
                <div style="background:#fef2f2;border-radius:4px;padding:6px;text-align:center;">
                  <div style="font-family:'Share Tech Mono',monospace;font-size:8px;color:#94a3b8;">STOP</div>
                  <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:14px;color:#b91c1c;">{sl}</div>
                </div>
                <div style="background:#f0fdf4;border-radius:4px;padding:6px;text-align:center;">
                  <div style="font-family:'Share Tech Mono',monospace;font-size:8px;color:#94a3b8;">TP</div>
                  <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:14px;color:#076f45;">{tp}</div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 4 — SESIONES
# ══════════════════════════════════════════════
with tab_horarios:
    st.markdown('<div class="sec">🕐 SESIONES DE TRADING — HORARIOS UTC</div>', unsafe_allow_html=True)

    h_utc = get_utc_hour()
    sesiones = [
        ("Londres",     "07:00 – 10:00 UTC", 7,  10, "#076f45", "#f0fdf4", "#86efac", "PRIORITARIA", "Oro y EUR/USD · Mayor liquidez"),
        ("Nueva York",  "13:00 – 16:00 UTC", 13, 16, "#076f45", "#f0fdf4", "#86efac", "OPERAR",      "Crudo WTI y NAS100 · Alta volatilidad"),
        ("Solapamiento","16:00 – 17:00 UTC", 16, 17, "#92650a", "#fefce8", "#fde047", "PRECAUCIÓN",  "Solo señales muy claras con EMA200"),
        ("Zona Muerta", "11:00 – 13:00 UTC", 11, 13, "#b91c1c", "#fef2f2", "#fca5a5", "NO OPERAR",   "Baja liquidez · Señales falsas del QQE"),
        ("Nocturna",    "20:00 – 07:00 UTC", 20, 24, "#64748b", "#f8fafc", "#e2e8f0", "INACTIVO",    "Sin volumen institucional · Esperar"),
    ]

    for nombre, hora, h_start, h_end, color, bg, border, estado, nota in sesiones:
        activa = h_start <= h_utc < h_end
        activa_style = f"border:2px solid {border};" if activa else f"border:1px solid {border};"
        st.markdown(f"""
        <div style="background:{bg};{activa_style}border-radius:8px;padding:14px 18px;
        margin-bottom:8px;display:flex;align-items:center;gap:16px;">
          <div style="width:12px;height:12px;border-radius:50%;background:{color};
          {'animation:pulse 1s infinite' if activa else ''};flex-shrink:0;"></div>
          <div style="min-width:130px;font-family:'Rajdhani',sans-serif;font-weight:700;
          font-size:15px;color:{color};">{nombre}</div>
          <div style="font-family:'Share Tech Mono',monospace;font-size:11px;
          color:#64748b;min-width:160px;">{hora}</div>
          <div style="background:{bg};border:1px solid {border};border-radius:20px;
          padding:3px 10px;font-family:'Share Tech Mono',monospace;font-size:9px;
          color:{color};font-weight:700;flex-shrink:0;">{'● ' if activa else ''}{estado}</div>
          <div style="font-size:12px;color:#334155;">{nota}</div>
          {'<div style="margin-left:auto;font-family:\'Share Tech Mono\',monospace;font-size:10px;font-weight:700;color:'+color+';background:'+bg+';padding:3px 8px;border-radius:4px;">AHORA</div>' if activa else ''}
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card card-blue" style="margin-top:8px;text-align:center;">
      <div style="font-family:'Share Tech Mono',monospace;font-size:11px;color:#1d4ed8;letter-spacing:1px;">
        HORA UTC ACTUAL: <strong style="font-size:18px;">{datetime.now(timezone.utc).strftime("%H:%M:%S")}</strong>
        · Tu zona: {datetime.now().strftime("%H:%M")} local
      </div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 5 — NOTICIAS
# ══════════════════════════════════════════════
with tab_noticias:
    st.markdown('<div class="sec">📡 NOTICIAS DE IMPACTO — ANÁLISIS FUNDAMENTAL</div>', unsafe_allow_html=True)

    col_n1, col_n2 = st.columns(2)

    noticias = [
        ("Reuters",        "08:42","ALTO",  "#b91c1c","#fef2f2","#fca5a5",
         "Fed mantiene tasas — Powell insinúa recortes en H2 2026",
         "→ Bearish USD · Bullish XAU/USD · Oportunidad LONG Oro"),
        ("Bloomberg",      "07:15","ALTO",  "#b91c1c","#fef2f2","#fca5a5",
         "Inventarios Crudo EE.UU. caen 3.2M barriles — tercer dato consecutivo",
         "→ Bullish WTI · Soporte clave $76.50 confirmado"),
        ("Investing",      "06:30","MED",   "#92650a","#fefce8","#fde047",
         "PMI Manufactura Eurozona 47.6 — supera estimación 47.0",
         "→ Soporte EUR/USD · Confirma sesión Londres activa"),
        ("CoinDesk",       "05:50","BAJO",  "#64748b","#f8fafc","#e2e8f0",
         "ETF Bitcoin registra entradas netas $320M — tercer día",
         "→ BTC consolida sobre $65K · QQE 04 en modo LONG"),
        ("CryptoBriefing", "04:20","MED",   "#92650a","#fefce8","#fde047",
         "ETH actualiza red — reducción de fees confirma demanda",
         "→ Soporte ETH $3,400 · QQE 04 señal LONG activa"),
        ("Reuters",        "03:10","BAJO",  "#64748b","#f8fafc","#e2e8f0",
         "China PMI servicios 52.4 — expansión continúa",
         "→ Risk-on global · Favorece activos de riesgo"),
    ]

    with col_n1:
        st.markdown("**📰 Noticias Recientes**")
        for src, hora, imp, col, bg, border, titulo, efecto in noticias:
            st.markdown(f"""
            <div class="news-item">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
                <span style="font-family:'Share Tech Mono',monospace;font-size:10px;
                font-weight:700;color:{col};">{src}</span>
                <span style="font-family:'Share Tech Mono',monospace;font-size:9px;color:#94a3b8;">{hora}</span>
                <span style="background:{bg};border:1px solid {border};color:{col};
                padding:2px 7px;border-radius:3px;font-family:'Share Tech Mono',monospace;font-size:8px;
                font-weight:700;">{imp}</span>
              </div>
              <div style="font-size:13px;color:#0f172a;line-height:1.4;margin-bottom:3px;">{titulo}</div>
              <div style="font-size:11px;color:#64748b;">{efecto}</div>
            </div>""", unsafe_allow_html=True)

    with col_n2:
        st.markdown("**🧠 Sentimiento Institucional**")
        sentimientos = [
            ("XAU/USD", "Oro — Alcista",      72, "#076f45", "#86efac", "#f0fdf4"),
            ("CRUDE OIL","Crudo — Neutral+",   56, "#92650a", "#fde047", "#fefce8"),
            ("EUR/USD",  "Euro — Alcista",     63, "#1d4ed8", "#93c5fd", "#dbeafe"),
            ("NAS100",   "Nasdaq — Esperar",   45, "#64748b", "#e2e8f0", "#f8fafc"),
            ("BTC",      "Bitcoin — Prudente", 48, "#92650a", "#fde047", "#fefce8"),
            ("ETH",      "Ethereum — Alcista", 61, "#6d28d9", "#c4b5fd", "#ede9fe"),
        ]
        for sym, label, pct, col, bar_col, bg in sentimientos:
            st.markdown(f"""
            <div style="background:{bg};border:1px solid #e2e8f0;border-radius:6px;
            padding:10px 12px;margin-bottom:6px;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;">
                <span style="font-family:'Share Tech Mono',monospace;font-size:10px;
                color:#64748b;">{sym}</span>
                <span style="font-size:12px;font-weight:600;color:{col};">{label}</span>
              </div>
              <div style="height:5px;background:#e2e8f0;border-radius:3px;overflow:hidden;">
                <div style="height:100%;width:{pct}%;background:{bar_col};border-radius:3px;"></div>
              </div>
              <div style="display:flex;justify-content:space-between;font-family:'Share Tech Mono',monospace;
              font-size:9px;margin-top:3px;">
                <span style="color:{col};">▲ {pct}% LONG</span>
                <span style="color:#b91c1c;">{100-pct}% SHORT</span>
              </div>
            </div>""", unsafe_allow_html=True)

        # Traders community
        st.markdown("**👥 Experiencias de Traders**")
        traders = [
            ("Alex Ruiz",       "#92650a", "EMA STRATEGY",
             '"La EMA200 es el filtro más poderoso. Si el precio está por debajo, no compres. Jamás."',
             "→ QQE 03/04 integran esto con tend_alcista / tend_bajista"),
            ("Ezekiel Chew",    "#076f45", "PRICE ACTION",
             '"Low mayor que anterior y cierre sobre el máximo anterior — eso es fuerza real."',
             "→ Es el buy_trigger base del QQE"),
            ("Crypto Trader Pro","#6d28d9","CRYPTO M15",
             '"En crypto la EMA50 es más efectiva que la 100 por la reacción más rápida del precio."',
             "→ QQE 04 usa EMA50 exactamente por esto"),
        ]
        for nombre, color, badge, quote, insight in traders:
            st.markdown(f"""
            <div class="trader" style="border-color:{color};">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
                <span style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:13px;color:#0f172a;">{nombre}</span>
                <span style="background:#f1f5f9;border:1px solid #e2e8f0;color:#64748b;
                padding:2px 7px;border-radius:3px;font-family:'Share Tech Mono',monospace;font-size:8px;">{badge}</span>
              </div>
              <div style="font-size:12px;color:#334155;font-style:italic;line-height:1.5;">{quote}</div>
              <div style="font-size:11px;color:{color};margin-top:5px;">{insight}</div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 6 — CÓDIGOS QQE
# ══════════════════════════════════════════════
with tab_codigos:
    st.markdown('<div class="sec">⚙ EVOLUCIÓN DEL SISTEMA — QQE 01 → 02 → 03 → 04</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    versiones = [
        (c1,"QQE 01","BASE — REEMPLAZADO","#94a3b8","#f1f5f9",
         [("✅","EMA100 tendencia"),("✅","Patrón vela Ezekiel Chew"),("✅","MACD manual"),("✅","RSI"),("❌","Sin EMA200"),("❌","Sin filtro sobrecompra")]),
        (c2,"QQE 02","MEJORADO — REEMPLAZADO","#94a3b8","#f1f5f9",
         [("✅","Todo QQE 01"),("✅","Estocástico manual (sk)"),("✅","Filtro sobrecompra sk<80"),("✅","Filtro sobreventa sk>20"),("❌","Sin EMA200"),("❌","Sin tendencia mayor")]),
        (c3,"QQE 03 ★","FOREX · M15/H1 ACTIVO","#92650a","#fef9ee",
         [("✅","Todo QQE 02"),("✅","EMA200 filtro mayor"),("✅","tend_alcista / tend_bajista"),("✅","4 filtros simultáneos"),("✅","M15 y H1"),("⭐","~45% menos señales falsas")]),
        (c4,"QQE 04 ★","CRYPTO · M15/H1 ACTIVO","#6d28d9","#ede9fe",
         [("✅","Base QQE 03"),("🔷","EMA50 (vs EMA100)"),("🔷","Ventana S/R 30 velas"),("🔷","sk<85 / sk>15"),("🔷","BTC · ETH · SOL"),("🔷","Adaptado a crypto")]),
    ]
    for col, nombre, estado, color, bg, items in versiones:
        with col:
            st.markdown(f"""
            <div style="background:{bg};border:1px solid #e2e8f0;border-radius:8px;
            padding:14px;height:100%;">
              <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:18px;
              color:{color};">{nombre}</div>
              <div style="font-family:'Share Tech Mono',monospace;font-size:9px;
              color:{color};letter-spacing:1px;margin-bottom:10px;">{estado}</div>
              {''.join([f'<div style="font-size:11px;color:#334155;margin-bottom:4px;">{i} {t}</div>' for i,t in items])}
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec" style="margin-top:20px;">CÓDIGO FUENTE — COPIAR EN IQ OPTION</div>', unsafe_allow_html=True)

    col_code1, col_code2 = st.columns(2)

    qqe03_code = '''instrument {
    name = "QQE 03",
    short_name = "QQE_03",
    icon = "indicators:BB",
    overlay = true
}
input_group {
    "Configuracion de Tendencia",
    periodo_ema = input(100, "Periodo EMA (Tendencia)", input.integer, 1, 500, 1),
    color_ema = input("yellow", "Color EMA", input.color),
    ancho_ema = input(3, "Grosor EMA", input.line_width)
}
ema_trend = ema(close, periodo_ema)
plot(ema_trend, "EMA 100", color_ema, ancho_ema)
ema200 = ema(close, 200)
plot(ema200, "EMA 200", "orange", 2)
h_level = highest(20)[1]
l_level = lowest(20)[1]
plot(h_level, "Resistencia", "white", 1, 0, style.levels, na_mode.continue)
plot(l_level, "Soporte", "white", 1, 0, style.levels, na_mode.continue)
e12 = ema(close, 12)
e26 = ema(close, 26)
mc = e12 - e26
hh = highest(14)[1]
ll = lowest(14)[1]
sk = (close - ll) / (hh - ll) * 100
r = rsi(close, 14)
ta = close > ema200 and ema_trend > ema200
tb = close < ema200 and ema_trend < ema200
buy_trigger = low > low[1] and close > high[1] and close > ema_trend and mc > 0 and sk < 80 and ta
sell_trigger = high < high[1] and close < low[1] and close < ema_trend and mc < 0 and sk > 20 and tb
plot_shape(buy_trigger, "COMPRA", shape_style.triangleup, shape_size.huge, "green", shape_location.belowbar, 0, "BUY", "white")
plot_shape(sell_trigger, "VENTA", shape_style.triangledown, shape_size.huge, "red", shape_location.abovebar, 0, "SELL", "white")
color_v = "gray"
if buy_trigger and r < 70 then color_v = "green" end
if sell_trigger and r > 30 then color_v = "red" end
barcolor(color_v)'''

    qqe04_code = '''instrument {
    name = "QQE 04 Crypto",
    short_name = "QQE_04",
    icon = "indicators:BB",
    overlay = true
}
input_group {
    "Configuracion",
    periodo_ema = input(50, "Periodo EMA (Tendencia)", input.integer, 1, 500, 1),
    color_ema = input("yellow", "Color EMA", input.color),
    ancho_ema = input(3, "Grosor EMA", input.line_width)
}
ema_trend = ema(close, periodo_ema)
plot(ema_trend, "EMA 50", color_ema, ancho_ema)
ema200 = ema(close, 200)
plot(ema200, "EMA 200", "orange", 2)
h_level = highest(30)[1]
l_level = lowest(30)[1]
plot(h_level, "Resistencia", "white", 1, 0, style.levels, na_mode.continue)
plot(l_level, "Soporte", "white", 1, 0, style.levels, na_mode.continue)
e12 = ema(close, 12)
e26 = ema(close, 26)
mc = e12 - e26
hh = highest(14)[1]
ll = lowest(14)[1]
sk = (close - ll) / (hh - ll) * 100
r = rsi(close, 14)
ta = close > ema200 and ema_trend > ema200
tb = close < ema200 and ema_trend < ema200
buy_trigger = low > low[1] and close > high[1] and close > ema_trend and mc > 0 and sk < 85 and ta
sell_trigger = high < high[1] and close < low[1] and close < ema_trend and mc < 0 and sk > 15 and tb
plot_shape(buy_trigger, "COMPRA", shape_style.triangleup, shape_size.huge, "green", shape_location.belowbar, 0, "BUY", "white")
plot_shape(sell_trigger, "VENTA", shape_style.triangledown, shape_size.huge, "red", shape_location.abovebar, 0, "SELL", "white")
color_v = "gray"
if buy_trigger and r < 70 then color_v = "green" end
if sell_trigger and r > 30 then color_v = "red" end
barcolor(color_v)'''

    with col_code1:
        st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:9px;color:#92650a;letter-spacing:1px;margin-bottom:6px;">CÓDIGO QQE 03 — FOREX</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="code-block">{qqe03_code}</div>', unsafe_allow_html=True)
        st.code(qqe03_code, language="lua")

    with col_code2:
        st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:9px;color:#6d28d9;letter-spacing:1px;margin-bottom:6px;">CÓDIGO QQE 04 — CRYPTO</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="code-block">{qqe04_code}</div>', unsafe_allow_html=True)
        st.code(qqe04_code, language="lua")

    st.markdown("""
    <div style="background:#f0fdf4;border:1px solid #86efac;border-radius:6px;
    padding:10px 14px;font-family:'Share Tech Mono',monospace;font-size:10px;color:#076f45;margin-top:8px;">
    💡 Copiá el código → Abrí IQ Option → Editor de indicadores → Pegá → Guardá → Aplicá al gráfico M15 u H1
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════
st.markdown("""
<div style="border-top:1px solid #e2e8f0;margin-top:24px;padding-top:10px;
font-family:'Share Tech Mono',monospace;font-size:9px;color:#94a3b8;
text-align:center;letter-spacing:1px;">
QQE 03/04 · HECTOR TRADING COMMAND · IQ OPTION · M15/H1 · FOREX & CRYPTO
</div>
""", unsafe_allow_html=True)
