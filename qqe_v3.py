# QQE 03/04 - HECTOR TRADING COMMAND v3
# Diario de Trading + Binarias 1min + Copy Trading
#
# INSTALACION: pip install streamlit requests
# EJECUCION:   streamlit run qqe_v3.py

import streamlit as st
import requests
from datetime import datetime, timezone, date

st.set_page_config(
    page_title="QQE Command v3 - Hector",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================================================
# CSS
# ================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&family=Inter:wght@300;400;500;600&display=swap');

html, body, .stApp { background:#f0f4f8 !important; }
.stApp { font-family:'Inter',sans-serif; color:#334155; }
[data-testid="stSidebar"] { background:#ffffff !important; border-right:1px solid #e2e8f0 !important; }

.stTabs [data-baseweb="tab-list"] { background:#ffffff; border-bottom:2px solid #e2e8f0; gap:0; }
.stTabs [data-baseweb="tab"] {
    background:transparent; color:#94a3b8 !important;
    font-family:'Share Tech Mono',monospace; font-size:11px;
    letter-spacing:1px; padding:10px 16px; border:none;
}
.stTabs [aria-selected="true"] {
    background:#f0f4f8 !important; color:#0f172a !important;
    border-bottom:2px solid #92650a !important; font-weight:700 !important;
}

.card { background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:16px; margin-bottom:10px; box-shadow:0 1px 3px rgba(0,0,0,.06); }
.card-gold   { border-left:4px solid #92650a; }
.card-green  { border-left:4px solid #076f45; }
.card-red    { border-left:4px solid #b91c1c; }
.card-blue   { border-left:4px solid #1d4ed8; }
.card-purple { border-left:4px solid #6d28d9; }
.card-orange { border-left:4px solid #c2410c; }

.kpi { background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:14px 16px; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,.06); }
.kpi-label { font-family:'Share Tech Mono',monospace; font-size:9px; color:#94a3b8; letter-spacing:2px; text-transform:uppercase; margin-bottom:6px; }
.kpi-value { font-family:'Rajdhani',sans-serif; font-size:28px; font-weight:700; line-height:1.1; }
.kpi-sub   { font-family:'Share Tech Mono',monospace; font-size:10px; color:#94a3b8; margin-top:3px; }

.sec { font-family:'Share Tech Mono',monospace; font-size:10px; color:#94a3b8; letter-spacing:3px; text-transform:uppercase; border-bottom:2px solid #e2e8f0; padding-bottom:6px; margin:16px 0 12px; }

.badge-green  { background:#dcfce7; color:#076f45; border:1px solid #86efac; padding:3px 10px; border-radius:20px; font-family:'Share Tech Mono',monospace; font-size:9px; font-weight:700; }
.badge-red    { background:#fef2f2; color:#b91c1c; border:1px solid #fca5a5; padding:3px 10px; border-radius:20px; font-family:'Share Tech Mono',monospace; font-size:9px; font-weight:700; }
.badge-gold   { background:#fef9ee; color:#92650a; border:1px solid #fcd34d; padding:3px 10px; border-radius:20px; font-family:'Share Tech Mono',monospace; font-size:9px; font-weight:700; }
.badge-blue   { background:#dbeafe; color:#1d4ed8; border:1px solid #93c5fd; padding:3px 10px; border-radius:20px; font-family:'Share Tech Mono',monospace; font-size:9px; font-weight:700; }
.badge-purple { background:#ede9fe; color:#6d28d9; border:1px solid #c4b5fd; padding:3px 10px; border-radius:20px; font-family:'Share Tech Mono',monospace; font-size:9px; font-weight:700; }
.badge-orange { background:#fff7ed; color:#c2410c; border:1px solid #fdba74; padding:3px 10px; border-radius:20px; font-family:'Share Tech Mono',monospace; font-size:9px; font-weight:700; }

.ai-box { background:#fffbeb; border:1px solid #fcd34d; border-radius:8px; padding:16px; min-height:100px; font-size:14px; line-height:1.8; color:#334155; }
.prog-track { height:14px; background:#e2e8f0; border-radius:7px; overflow:hidden; margin:8px 0; }
.prog-fill  { height:100%; border-radius:7px; background:linear-gradient(90deg,#fcd34d,#92650a); }

.diario-entry { background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:14px; margin-bottom:8px; box-shadow:0 1px 3px rgba(0,0,0,.04); }
.diario-meta  { font-family:'Share Tech Mono',monospace; font-size:9px; color:#94a3b8; letter-spacing:1px; margin-bottom:6px; }
.diario-text  { font-size:13px; color:#334155; line-height:1.6; }
.diario-tag   { display:inline-block; padding:2px 8px; border-radius:10px; font-family:'Share Tech Mono',monospace; font-size:9px; margin-right:4px; }

.script-card { background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:16px; margin-bottom:10px; }
.code-block { background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:14px; font-family:'Share Tech Mono',monospace; font-size:10px; line-height:1.8; color:#1e293b; white-space:pre; overflow-x:auto; max-height:280px; overflow-y:auto; margin-bottom:8px; }

.trader-copy { background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:14px; margin-bottom:8px; }
.trader-stat { text-align:center; padding:10px; background:#f8fafc; border-radius:6px; }
.trader-stat-val { font-family:'Rajdhani',sans-serif; font-weight:700; font-size:20px; }
.trader-stat-lbl { font-family:'Share Tech Mono',monospace; font-size:8px; color:#94a3b8; letter-spacing:1px; }

.asset { background:#ffffff; border:1px solid #e2e8f0; border-radius:6px; padding:12px; margin-bottom:6px; }
.asset-bar { height:4px; background:#e2e8f0; border-radius:2px; overflow:hidden; margin:6px 0; }

.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    background:#ffffff !important; border:1px solid #e2e8f0 !important;
    color:#0f172a !important; border-radius:6px !important;
}
.stButton>button {
    background:#0f172a !important; color:#ffffff !important;
    border:none !important; border-radius:6px !important;
    font-family:'Share Tech Mono',monospace !important;
    font-size:11px !important; letter-spacing:1px !important;
}
.stSelectbox>div>div { background:#ffffff !important; border:1px solid #e2e8f0 !important; color:#0f172a !important; border-radius:6px !important; }
.stNumberInput>div>div>input { background:#ffffff !important; border:1px solid #e2e8f0 !important; color:#0f172a !important; border-radius:6px !important; }

::-webkit-scrollbar { width:4px; height:4px; }
::-webkit-scrollbar-track { background:#f1f5f9; }
::-webkit-scrollbar-thumb { background:#cbd5e1; border-radius:2px; }
</style>
""", unsafe_allow_html=True)

# ================================================================
# SESSION STATE
# ================================================================
defaults = {
    "ops": [],
    "api_key": "",
    "ai_response": "",
    "diario": [],        # lista de entradas del diario
    "ai_query": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ================================================================
# HELPERS
# ================================================================
def get_utc_hour():
    return datetime.now(timezone.utc).hour

def get_session_info():
    h = get_utc_hour()
    if 7 <= h < 10:   return "SESION LONDRES",     "OPERAR",     "#076f45","#f0fdf4","#86efac"
    elif 13 <= h < 16: return "SESION NUEVA YORK",  "OPERAR",     "#076f45","#f0fdf4","#86efac"
    elif 16 <= h < 17: return "SOLAPAMIENTO",        "PRECAUCION", "#92650a","#fefce8","#fde047"
    elif 11 <= h < 13: return "ZONA MUERTA",         "NO OPERAR",  "#b91c1c","#fef2f2","#fca5a5"
    else:               return "MERCADO CERRADO",     "INACTIVO",   "#64748b","#f8fafc","#e2e8f0"

def calc_pnl():
    g = sum(o["pnl"] for o in st.session_state.ops if o["pnl"] > 0)
    p = abs(sum(o["pnl"] for o in st.session_state.ops if o["pnl"] < 0))
    return g, p, g - p

def ask_claude(api_key, question, system_override=None):
    h = get_utc_hour()
    ses, _, _, _, _ = get_session_info()
    g, _, n = calc_pnl()
    system = system_override or f"""Eres el asistente de trading de Hector. Opera CFDs en IQ Option M15/H1.
QQE 03 Forex: EMA100+EMA200+MACD+Estocastico+RSI. Activos: XAU/USD, Crude Oil, EUR/USD, NAS100.
QQE 04 Crypto: EMA50+EMA200. Activos: BTC, ETH, SOL.
Estado: {ses} UTC {h}:00. Capital $467.86. Ganado hoy ${g:.2f}. Neto ${n:.2f}. Objetivo $50/dia.
Responde en espanol. Max 200 palabras. Directo y accionable. Usa emojis: checkmark, warning, chart."""
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type":"application/json","x-api-key":api_key,"anthropic-version":"2023-06-01"},
            json={"model":"claude-sonnet-4-20250514","max_tokens":500,"system":system,"messages":[{"role":"user","content":question}]},
            timeout=30
        )
        data = r.json()
        if r.status_code == 200:
            return data["content"][0]["text"]
        return f"Error API: {data.get('error',{}).get('message', str(data))}"
    except Exception as e:
        return f"Error de conexion: {str(e)}"

# ================================================================
# SIDEBAR
# ================================================================
with st.sidebar:
    st.markdown("""
    <div style='font-family:"Rajdhani",sans-serif;font-size:20px;font-weight:700;
    color:#0f172a;letter-spacing:2px;border-bottom:2px solid #e2e8f0;padding-bottom:10px;margin-bottom:14px;'>
    QQE COMMAND v3
    </div>""", unsafe_allow_html=True)

    ses_label, ses_estado, ses_color, ses_bg, ses_border = get_session_info()
    st.markdown(f"""
    <div style='background:{ses_bg};border:1px solid {ses_border};border-radius:6px;padding:10px 14px;margin-bottom:12px;'>
    <div style='font-family:"Share Tech Mono",monospace;font-size:11px;font-weight:700;color:{ses_color};'>
    {ses_label}</div>
    <div style='font-family:"Share Tech Mono",monospace;font-size:9px;color:{ses_color};letter-spacing:1px;'>
    {ses_estado} · {datetime.now(timezone.utc).strftime("%H:%M:%S")} UTC</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:9px;color:#94a3b8;letter-spacing:2px;margin-bottom:4px;">API KEY</div>', unsafe_allow_html=True)
    api_in = st.text_input("", value=st.session_state.api_key,
                            placeholder="sk-ant-api03-...", type="password",
                            label_visibility="collapsed", key="api_input")
    if api_in: st.session_state.api_key = api_in
    if st.session_state.api_key.startswith("sk-ant-"):
        st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:10px;color:#076f45;">✅ KEY ACTIVA</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:10px;color:#94a3b8;">Sin key</div>', unsafe_allow_html=True)

    st.markdown("---")
    capital = st.number_input("Capital ($)", min_value=10.0, max_value=100000.0, value=467.86, step=10.0)
    riesgo_pct = st.slider("Riesgo %", 0.5, 5.0, 2.0, 0.5)
    importe_max = int(capital * riesgo_pct / 100)

    st.markdown(f"""
    <div style='background:#fef9ee;border:1px solid #fcd34d;border-radius:6px;padding:10px 14px;
    font-family:"Share Tech Mono",monospace;font-size:10px;margin-bottom:10px;'>
    <span style='color:#94a3b8;'>IMPORTE MAX:</span> <strong style='color:#92650a;font-size:16px;'>${importe_max}</strong><br>
    <span style='color:#94a3b8;'>RIESGO MAX:</span> <span style='color:#b91c1c;'>${capital*riesgo_pct/100:.2f}</span>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("Reset operaciones del dia"):
        st.session_state.ops = []
        st.rerun()

# ================================================================
# HEADER
# ================================================================
ganado, perdido, neto = calc_pnl()
pct_obj = min(100, max(0, (neto / 50) * 100))

st.markdown(f"""
<div style='background:#ffffff;border:1px solid #e2e8f0;border-radius:10px;
padding:16px 22px;margin-bottom:14px;display:flex;align-items:center;
justify-content:space-between;box-shadow:0 1px 4px rgba(0,0,0,.06);'>
  <div>
    <div style='font-family:"Rajdhani",sans-serif;font-size:22px;font-weight:700;
    color:#0f172a;letter-spacing:3px;'>QQE 03/04 — HECTOR TRADING COMMAND v3</div>
    <div style='font-family:"Share Tech Mono",monospace;font-size:9px;color:#94a3b8;
    letter-spacing:2px;margin-top:2px;'>IQ OPTION · M15/H1 · FOREX & CRYPTO · OBJETIVO $50/DIA</div>
  </div>
  <div style='text-align:right;'>
    <div style='font-family:"Share Tech Mono",monospace;font-size:11px;color:{ses_color};font-weight:700;'>{ses_label}</div>
    <div style='font-family:"Share Tech Mono",monospace;font-size:10px;color:#94a3b8;'>
    {datetime.now(timezone.utc).strftime("%d/%m/%Y · %H:%M UTC")}</div>
  </div>
</div>""", unsafe_allow_html=True)

# KPIs
k1,k2,k3,k4,k5 = st.columns(5)
wins = len([o for o in st.session_state.ops if o["pnl"]>0])
losses = len([o for o in st.session_state.ops if o["pnl"]<0])
for col, label, val, color, sub in [
    (k1,"GANADO HOY",   f"${ganado:.2f}",  "#076f45", f"{wins} wins"),
    (k2,"PERDIDO HOY",  f"${perdido:.2f}", "#b91c1c", f"{losses} losses"),
    (k3,"NETO HOY",     f"${neto:.2f}",    "#076f45" if neto>=0 else "#b91c1c", f"{pct_obj:.0f}% objetivo"),
    (k4,"OBJETIVO",     "$50.00",          "#92650a", f"Faltan ${max(0,50-neto):.2f}"),
    (k5,"IMPORTE MAX",  f"${importe_max}", "#1d4ed8", f"Riesgo {riesgo_pct}%"),
]:
    with col:
        st.markdown(f"""<div class="kpi">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value" style="color:{color};">{val}</div>
          <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown(f"""
<div class="card card-gold" style="margin-top:8px;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
    <span style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:15px;color:#0f172a;">Progreso Objetivo del Dia</span>
    <span style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:26px;color:#92650a;">{pct_obj:.0f}%</span>
  </div>
  <div class="prog-track"><div class="prog-fill" style="width:{pct_obj}%;"></div></div>
  <div style="display:flex;justify-content:space-between;font-family:'Share Tech Mono',monospace;font-size:9px;color:#94a3b8;">
    <span>$0</span><span>$12.50</span><span>$25</span><span>$37.50</span><span>$50</span>
  </div>
</div>""", unsafe_allow_html=True)

# ================================================================
# TABS
# ================================================================
tab_ia, tab_ops, tab_diario, tab_binarias, tab_copy, tab_activos, tab_codigos = st.tabs([
    "⚡ IA ANALYST",
    "📝 REGISTRO",
    "📔 DIARIO",
    "⚡ BINARIAS 1MIN",
    "👥 COPY TRADING",
    "📊 ACTIVOS",
    "⚙ CODIGOS QQE",
])

# ================================================================
# TAB 1 — IA ANALYST
# ================================================================
with tab_ia:
    st.markdown('<div class="sec">RECOMENDACIONES IA — QQE 03/04 ANALYST</div>', unsafe_allow_html=True)

    if not st.session_state.api_key.startswith("sk-ant-"):
        st.markdown("""<div style="background:#fef9ee;border:1px solid #fcd34d;border-radius:8px;
        padding:16px;font-family:'Share Tech Mono',monospace;font-size:11px;color:#92650a;">
        Pega tu API key en el sidebar izquierdo para activar la IA.</div>""", unsafe_allow_html=True)
    else:
        chips = [
            "Es buen momento para operar Oro ahora?",
            "Estoy en horario optimo de trading?",
            "Que activo tiene mejor setup hoy?",
            "Dame el plan operativo completo para esta sesion",
            "Como uso QQE 03 diferente en H1 vs M15?",
            "Tengo 3 senales seguidas de SELL en Oro, entro?",
            "BTC o ETH tiene mejor setup ahora con QQE 04?",
            f"Como gestiono el riesgo con capital ${capital:.0f}?",
            "Cuando debo parar de operar hoy?",
        ]
        cols = st.columns(3)
        for i, chip in enumerate(chips):
            with cols[i % 3]:
                if st.button(chip[:38]+"..." if len(chip)>38 else chip, key=f"chip_{i}"):
                    st.session_state.ai_query = chip

        query = st.text_input("O escribi tu consulta:",
                               value=st.session_state.get("ai_query",""),
                               placeholder="Ej: Que activo operar ahora?")
        if st.button("CONSULTAR IA", key="ask_ai"):
            if query.strip():
                with st.spinner("Analizando mercado..."):
                    st.session_state.ai_response = ask_claude(st.session_state.api_key, query)
                st.session_state.ai_query = ""
            else:
                st.warning("Escribe una consulta primero")

    if st.session_state.ai_response:
        st.markdown('<div class="sec">RESPUESTA DEL ANALISTA</div>', unsafe_allow_html=True)
        st.markdown(f"""<div class="ai-box">
        {st.session_state.ai_response.replace(chr(10),'<br>')}
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class="ai-box">
        <span style="font-family:'Share Tech Mono',monospace;font-size:11px;color:#94a3b8;">
        Escribe tu consulta — analizo mercado, horario, noticias, QQE 03 Forex y QQE 04 Crypto...
        </span></div>""", unsafe_allow_html=True)


# ================================================================
# TAB 2 — REGISTRO
# ================================================================
with tab_ops:
    st.markdown('<div class="sec">REGISTRO DE OPERACIONES DEL DIA</div>', unsafe_allow_html=True)
    col_form, col_list = st.columns([1,2])

    with col_form:
        activo    = st.selectbox("Activo", ["XAU/USD","CRUDE OIL","EUR/USD","NAS100","BTC","ETH","SOL"])
        direccion = st.selectbox("Direccion", ["LONG","SHORT"])
        importe_op = st.number_input("Importe ($)", min_value=1.0, max_value=500.0, value=float(importe_max), step=1.0)
        script_op  = st.selectbox("Script", ["QQE 03","QQE 04 Crypto","Script A 1min","Script B 1min","Script C 1min"])
        nota_op    = st.text_input("Nota rapida (opcional)", placeholder="Ej: Entre tarde, noticia afecto")

        cw, cl = st.columns(2)
        with cw:
            if st.button("GANADA", key="win"):
                st.session_state.ops.append({
                    "activo":activo, "dir":direccion, "importe":importe_op,
                    "pnl":round(importe_op*2,2), "script":script_op,
                    "hora":datetime.now().strftime("%H:%M"), "result":"win", "nota":nota_op
                })
                if nota_op:
                    st.session_state.diario.append({
                        "fecha": date.today().strftime("%d/%m/%Y"),
                        "hora":  datetime.now().strftime("%H:%M"),
                        "tipo":  "WIN",
                        "activo": activo,
                        "nota":  nota_op,
                        "pnl":   f"+${importe_op*2:.2f}"
                    })
                st.rerun()
        with cl:
            if st.button("PERDIDA", key="loss"):
                st.session_state.ops.append({
                    "activo":activo, "dir":direccion, "importe":importe_op,
                    "pnl":-importe_op, "script":script_op,
                    "hora":datetime.now().strftime("%H:%M"), "result":"loss", "nota":nota_op
                })
                if nota_op:
                    st.session_state.diario.append({
                        "fecha": date.today().strftime("%d/%m/%Y"),
                        "hora":  datetime.now().strftime("%H:%M"),
                        "tipo":  "LOSS",
                        "activo": activo,
                        "nota":  nota_op,
                        "pnl":   f"-${importe_op:.2f}"
                    })
                st.rerun()

        g2,p2,n2 = calc_pnl()
        if n2 >= 50:
            st.markdown('<div class="card card-gold" style="padding:10px;"><b style="color:#92650a;">OBJETIVO $50 ALCANZADO — CERRAR PLATAFORMA</b></div>', unsafe_allow_html=True)
        elif n2 <= -capital*0.06:
            st.markdown('<div class="card card-red" style="padding:10px;"><b style="color:#b91c1c;">LIMITE -6% ALCANZADO — PARAR HOY</b></div>', unsafe_allow_html=True)

    with col_list:
        if not st.session_state.ops:
            st.markdown('<div style="text-align:center;padding:30px;font-family:\'Share Tech Mono\',monospace;font-size:11px;color:#94a3b8;">Sin operaciones hoy</div>', unsafe_allow_html=True)
        else:
            for op in reversed(st.session_state.ops):
                color = "#076f45" if op["result"]=="win" else "#b91c1c"
                bg    = "#f0fdf4" if op["result"]=="win" else "#fef2f2"
                border= "#86efac" if op["result"]=="win" else "#fca5a5"
                sign  = "+" if op["pnl"]>0 else ""
                nota_html = f'<div style="font-size:11px;color:#64748b;margin-top:4px;font-style:italic;">{op["nota"]}</div>' if op.get("nota") else ""
                st.markdown(f"""
                <div style="background:{bg};border:1px solid {border};border-radius:6px;
                padding:10px 14px;margin-bottom:6px;">
                  <div style="display:flex;align-items:center;justify-content:space-between;">
                    <div>
                      <span style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:15px;color:#0f172a;">{op['activo']}</span>
                      <span style="font-size:10px;color:#64748b;margin-left:8px;">{op['dir']} · {op['script']} · {op['hora']}</span>
                    </div>
                    <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:20px;color:{color};">
                      {sign}${abs(op['pnl']):.2f}
                    </div>
                  </div>
                  {nota_html}
                </div>""", unsafe_allow_html=True)


# ================================================================
# TAB 3 — DIARIO DE TRADING
# ================================================================
with tab_diario:
    st.markdown('<div class="sec">DIARIO DE SESION — REGISTRO DE APRENDIZAJE</div>', unsafe_allow_html=True)

    col_add, col_view = st.columns([1, 2])

    with col_add:
        st.markdown('<div class="card card-blue">', unsafe_allow_html=True)
        st.markdown("**Nueva entrada al diario:**")

        tipo_entry = st.selectbox("Tipo", ["APRENDIZAJE","ERROR","OBSERVACION","SETUP","EMOCION"], key="diario_tipo")
        activo_d   = st.selectbox("Activo", ["XAU/USD","CRUDE OIL","EUR/USD","BTC","ETH","SOL","GENERAL"], key="diario_activo")
        nota_d     = st.text_area("Nota detallada",
                                   placeholder="Ej: Entre tarde porque dude. El delay me costo $9. La proxima espero confirmacion completa de la vela M15 antes de entrar.",
                                   height=120, key="diario_nota")
        estado_d   = st.selectbox("Estado emocional", ["Concentrado","Ansioso","Confiado","Dudoso","Impulsivo","Cansado"], key="diario_estado")

        if st.button("GUARDAR EN DIARIO", key="save_diario"):
            if nota_d.strip():
                st.session_state.diario.append({
                    "fecha":  date.today().strftime("%d/%m/%Y"),
                    "hora":   datetime.now().strftime("%H:%M"),
                    "tipo":   tipo_entry,
                    "activo": activo_d,
                    "nota":   nota_d,
                    "estado": estado_d,
                    "pnl":    ""
                })
                st.success("Guardado!")
                st.rerun()
            else:
                st.warning("Escribe una nota primero")
        st.markdown('</div>', unsafe_allow_html=True)

        # Analisis IA del diario
        if st.session_state.diario and st.session_state.api_key.startswith("sk-ant-"):
            st.markdown("---")
            if st.button("ANALIZAR DIARIO CON IA", key="analizar_diario"):
                entradas = "\n".join([
                    f"[{e['fecha']} {e['hora']}] {e['tipo']} - {e['activo']}: {e['nota']}"
                    for e in st.session_state.diario[-10:]
                ])
                prompt = f"Analiza estas entradas del diario de trading de Hector y dame 3 patrones de error que repite y 3 recomendaciones concretas para mejorar:\n\n{entradas}"
                sys = "Eres coach de trading de Hector. Analiza su diario y encuentra patrones de comportamiento. Sé directo y accionable. Max 200 palabras. Responde en español."
                with st.spinner("Analizando patrones..."):
                    respuesta = ask_claude(st.session_state.api_key, prompt, system_override=sys)
                st.session_state.ai_response = respuesta
                st.markdown(f"""<div class="ai-box" style="margin-top:10px;">
                {respuesta.replace(chr(10),'<br>')}
                </div>""", unsafe_allow_html=True)

    with col_view:
        st.markdown("**Historial del diario:**")

        if not st.session_state.diario:
            st.markdown("""<div style="text-align:center;padding:40px;background:#ffffff;
            border:1px solid #e2e8f0;border-radius:8px;">
            <div style="font-size:32px;margin-bottom:10px;">📔</div>
            <div style="font-family:'Share Tech Mono',monospace;font-size:11px;color:#94a3b8;">
            El diario esta vacio.<br>Registra tu primera nota despues de operar.</div>
            </div>""", unsafe_allow_html=True)
        else:
            tipo_colors = {
                "APRENDIZAJE": ("#1d4ed8","#dbeafe","#93c5fd"),
                "ERROR":       ("#b91c1c","#fef2f2","#fca5a5"),
                "OBSERVACION": ("#076f45","#f0fdf4","#86efac"),
                "SETUP":       ("#92650a","#fef9ee","#fcd34d"),
                "EMOCION":     ("#6d28d9","#ede9fe","#c4b5fd"),
                "WIN":         ("#076f45","#f0fdf4","#86efac"),
                "LOSS":        ("#b91c1c","#fef2f2","#fca5a5"),
            }
            for entry in reversed(st.session_state.diario):
                tc, tbg, tborder = tipo_colors.get(entry["tipo"], ("#64748b","#f8fafc","#e2e8f0"))
                estado_html = f'<span style="font-size:10px;color:#64748b;margin-left:6px;">Estado: {entry.get("estado","")}</span>' if entry.get("estado") else ""
                pnl_html = f'<span style="font-family:\'Rajdhani\',sans-serif;font-weight:700;font-size:14px;color:{tc};">{entry["pnl"]}</span>' if entry.get("pnl") else ""
                st.markdown(f"""
                <div class="diario-entry">
                  <div class="diario-meta">
                    {entry['fecha']} · {entry['hora']} · {entry['activo']}
                    {estado_html}
                    <span style="float:right;">{pnl_html}</span>
                  </div>
                  <div style="margin-bottom:6px;">
                    <span style="background:{tbg};border:1px solid {tborder};color:{tc};
                    padding:2px 8px;border-radius:10px;font-family:'Share Tech Mono',monospace;
                    font-size:9px;font-weight:700;">{entry['tipo']}</span>
                  </div>
                  <div class="diario-text">{entry['nota']}</div>
                </div>""", unsafe_allow_html=True)

            if st.button("Limpiar diario", key="clear_diario"):
                st.session_state.diario = []
                st.rerun()


# ================================================================
# TAB 4 — BINARIAS 1 MINUTO
# ================================================================
with tab_binarias:
    st.markdown('<div class="sec">MODULO BINARIAS 1 MINUTO — 3 SCRIPTS LUA</div>', unsafe_allow_html=True)

    # Warning card
    st.markdown("""
    <div style="background:#fff7ed;border:1px solid #fdba74;border-radius:8px;
    padding:12px 16px;margin-bottom:14px;font-size:13px;color:#c2410c;">
    <b>Atencion:</b> Las binarias de 1 minuto tienen alto riesgo por el spread y delay.
    Usalos SOLO en sesion Londres (07-10 UTC) o Nueva York (13-16 UTC).
    Riesgo maximo: 1% del capital por operacion = <b>${capital*0.01:.2f}</b>
    </div>""", unsafe_allow_html=True)

    s_a, s_b, s_c = st.tabs(["Script A — Momentum", "Script B — Reversion", "Script C — Hibrido"])

    # ── SCRIPT A ──────────────────────────────────────────
    with s_a:
        st.markdown("""
        <div class="card card-gold">
        <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:18px;color:#92650a;margin-bottom:4px;">
        Script A — Scalping Momentum</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:9px;color:#94a3b8;letter-spacing:1px;margin-bottom:10px;">
        CRUCE DE MEDIAS RAPIDAS + BANDAS DE VOLATILIDAD</div>
        <div style="font-size:13px;color:#334155;line-height:1.7;">
        Detecta momentum fuerte en velas de 1 minuto usando cruce de EMA3 y EMA8 con filtro de volatilidad.
        Solo opera cuando el mercado tiene movimiento real, evita rangos laterales.
        </div>
        </div>""", unsafe_allow_html=True)

        col_l, col_r = st.columns([1,1])
        with col_l:
            st.markdown("""**Como funciona:**
- EMA3 cruza EMA8 hacia arriba → CALL
- EMA3 cruza EMA8 hacia abajo → PUT
- Filtro: volatilidad > promedio (evita mercado plano)
- Banda superior/inferior confirma direccion

**Mejores activos:** EUR/USD, GBP/USD, XAU/USD
**Horario:** Londres y Nueva York
**Expiracion:** 1-2 minutos""")

        with col_r:
            st.markdown("""**Parametros clave:**
- EMA rapida: 3 periodos
- EMA lenta: 8 periodos
- Banda volatilidad: 14 periodos
- Multiplicador banda: 1.5
- Filtro tendencia: EMA 50""")

        script_a = '''instrument {
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
    p_trend = input(50, "EMA Tendencia", input.integer, 10, 200, 1),
    mult    = input(1.5,"Mult Banda",  input.float, 0.5, 3.0, 0.1)
}

ema_fast  = ema(close, p_fast)
ema_slow  = ema(close, p_slow)
ema_trend = ema(close, p_trend)

-- Bandas de volatilidad
basis     = ema(close, p_vol)
deviation = stdev(close, p_vol)
upper     = basis + deviation * mult
lower     = basis - deviation * mult

-- Cruce de medias
cross_up   = ema_fast > ema_slow and ema_fast[1] <= ema_slow[1]
cross_down = ema_fast < ema_slow and ema_fast[1] >= ema_slow[1]

-- Filtro volatilidad: rango de vela > promedio
candle_range = high - low
avg_range    = ema(candle_range, 10)
vol_ok       = candle_range > avg_range * 0.8

-- Filtro tendencia
trend_up   = close > ema_trend
trend_down = close < ema_trend

-- Senales finales
call_signal = cross_up   and vol_ok and trend_up   and close > lower
put_signal  = cross_down and vol_ok and trend_down and close < upper

plot(ema_fast,  "EMA 3",  "blue",   1)
plot(ema_slow,  "EMA 8",  "orange", 1)
plot(ema_trend, "EMA 50", "gray",   1)
plot(upper, "Banda Sup", "green", 1, 0, style.levels, na_mode.continue)
plot(lower, "Banda Inf", "red",   1, 0, style.levels, na_mode.continue)

plot_shape(call_signal, "CALL", shape_style.triangleup,
    shape_size.normal, "green", shape_location.belowbar, 0, "CALL", "white")
plot_shape(put_signal, "PUT", shape_style.triangledown,
    shape_size.normal, "red", shape_location.abovebar, 0, "PUT", "white")

color_bar = "gray"
if call_signal then color_bar = "green" end
if put_signal  then color_bar = "red"   end
barcolor(color_bar)'''

        st.markdown(f'<div class="code-block">{script_a}</div>', unsafe_allow_html=True)
        st.code(script_a, language="lua")

    # ── SCRIPT B ──────────────────────────────────────────
    with s_b:
        st.markdown("""
        <div class="card card-blue">
        <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:18px;color:#1d4ed8;margin-bottom:4px;">
        Script B — Reversion a la Media</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:9px;color:#94a3b8;letter-spacing:1px;margin-bottom:10px;">
        SOBRECOMPRA / SOBREVENTA EXTREMA EN 1 MINUTO</div>
        <div style="font-size:13px;color:#334155;line-height:1.7;">
        Detecta condiciones extremas de sobrecompra y sobreventa usando RSI ultra-rapido y Estocástico.
        Ideal para rebotes en soportes/resistencias en mercados con rango definido.
        </div>
        </div>""", unsafe_allow_html=True)

        col_l, col_r = st.columns([1,1])
        with col_l:
            st.markdown("""**Como funciona:**
- RSI(3) < 10 + Estocastico < 5 → CALL (sobreventa extrema)
- RSI(3) > 90 + Estocastico > 95 → PUT (sobrecompra extrema)
- Filtro: precio cerca de soporte/resistencia
- Confirmacion: vela envolvente

**Mejores activos:** EUR/USD, USD/JPY
**Horario:** Cualquier sesion activa
**Expiracion:** 1 minuto""")

        with col_r:
            st.markdown("""**Parametros clave:**
- RSI periodo: 3 (ultra rapido)
- RSI sobrecompra: 90
- RSI sobreventa: 10
- Estocastico: 5,3
- Ventana S/R: 20 velas""")

        script_b = '''instrument {
    name = "Script B - Reversion 1min",
    short_name = "REV_1M",
    icon = "indicators:RSI",
    overlay = true
}
input_group {
    "Configuracion",
    p_rsi    = input(3,  "RSI Periodo",    input.integer, 2, 14, 1),
    ob_nivel = input(90, "Sobrecompra",    input.integer, 70, 99, 1),
    os_nivel = input(10, "Sobreventa",     input.integer, 1,  30, 1),
    p_stoch  = input(5,  "Estoc Periodo",  input.integer, 3, 14, 1),
    p_sr     = input(20, "Ventana S/R",    input.integer, 5, 50, 1)
}

r    = rsi(close, p_rsi)
hh   = highest(p_stoch)[1]
ll   = lowest(p_stoch)[1]
sk   = (close - ll) / (hh - ll) * 100

-- Niveles S/R dinamicos
res  = highest(p_sr)[1]
sup  = lowest(p_sr)[1]
mid  = (res + sup) / 2

-- Condiciones extremas
extreme_os = r < os_nivel and sk < 8
extreme_ob = r > ob_nivel and sk > 92

-- Confirmacion con vela envolvente
bull_engulf = close > open and close > high[1] and open < low[1]
bear_engulf = close < open and close < low[1]  and open > high[1]

-- Proximidad a soporte/resistencia
near_sup = (close - sup) / sup < 0.002
near_res = (res - close) / close < 0.002

-- Senales
call_signal = extreme_os and (bull_engulf or near_sup)
put_signal  = extreme_ob and (bear_engulf or near_res)

-- Plots
plot(res, "Resistencia", "red",   1, 0, style.levels, na_mode.continue)
plot(sup, "Soporte",     "green", 1, 0, style.levels, na_mode.continue)
plot(mid, "Media",       "gray",  1, 0, style.levels, na_mode.continue)

plot_shape(call_signal, "CALL REV", shape_style.circle,
    shape_size.normal, "green", shape_location.belowbar, 0, "CALL", "white")
plot_shape(put_signal, "PUT REV", shape_style.circle,
    shape_size.normal, "red", shape_location.abovebar, 0, "PUT", "white")

color_bar = "gray"
if call_signal then color_bar = "lime"   end
if put_signal  then color_bar = "maroon" end
barcolor(color_bar)'''

        st.markdown(f'<div class="code-block">{script_b}</div>', unsafe_allow_html=True)
        st.code(script_b, language="lua")

    # ── SCRIPT C ──────────────────────────────────────────
    with s_c:
        st.markdown("""
        <div class="card card-purple">
        <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:18px;color:#6d28d9;margin-bottom:4px;">
        Script C — Hibrido Accion del Precio</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:9px;color:#94a3b8;letter-spacing:1px;margin-bottom:10px;">
        SOPORTES Y RESISTENCIAS DINAMICOS + CONFIRMACION</div>
        <div style="font-size:13px;color:#334155;line-height:1.7;">
        El mas completo de los tres. Combina deteccion de S/R dinamicos, patron de velas y
        confirmacion de momentum. Menos senales pero mayor precision.
        </div>
        </div>""", unsafe_allow_html=True)

        col_l, col_r = st.columns([1,1])
        with col_l:
            st.markdown("""**Como funciona:**
- Calcula S/R dinamicos en tiempo real
- Detecta rebote en soporte + vela alcista → CALL
- Detecta rechazo en resistencia + vela bajista → PUT
- Filtro MACD confirma momentum
- EMA200 filtra tendencia mayor

**Mejores activos:** XAU/USD, BTC, EUR/USD
**Horario:** Londres (optimo)
**Expiracion:** 1-3 minutos""")

        with col_r:
            st.markdown("""**Parametros clave:**
- Ventana S/R: 15 velas
- Tolerancia: 0.15%
- MACD: 3/10/3
- EMA tendencia: 200
- Min velas confirmacion: 1""")

        script_c = '''instrument {
    name = "Script C - Hibrido PA 1min",
    short_name = "HYB_1M",
    icon = "indicators:BB",
    overlay = true
}
input_group {
    "Configuracion",
    p_sr    = input(15,   "Ventana S/R",   input.integer, 5,  50, 1),
    tol     = input(0.15, "Tolerancia %",  input.float,   0.05, 1.0, 0.05),
    p_fast  = input(3,    "MACD Rapido",   input.integer, 2,  20, 1),
    p_slow  = input(10,   "MACD Lento",    input.integer, 5,  50, 1),
    p_sig   = input(3,    "MACD Signal",   input.integer, 2,  10, 1),
    p_trend = input(200,  "EMA Tendencia", input.integer, 50, 500,1)
}

-- Soportes y resistencias dinamicos
res = highest(p_sr)[1]
sup = lowest(p_sr)[1]

-- Tolerancia en precio
tol_res = res * (1 - tol/100)
tol_sup = sup * (1 + tol/100)

-- MACD manual
e_fast = ema(close, p_fast)
e_slow = ema(close, p_slow)
macd   = e_fast - e_slow
signal = ema(macd, p_sig)
histo  = macd - signal

-- Tendencia mayor
ema200    = ema(close, p_trend)
trend_up   = close > ema200
trend_down = close < ema200

-- Patrones de velas (accion del precio)
bull_pin   = (high - close) < (close - low) * 0.3 and (close - open) > 0
bear_pin   = (close - low)  < (high - close) * 0.3 and (open - close) > 0
bull_body  = close > open and (close - open) > (high - low) * 0.6
bear_body  = close < open and (open - close) > (high - low) * 0.6

-- Rebote en soporte
at_support   = close <= tol_sup and close >= sup
bull_pattern = bull_pin or bull_body

-- Rechazo en resistencia
at_resist   = close >= tol_res and close <= res
bear_pattern = bear_pin or bear_body

-- Senales finales (alta precision)
call_signal = at_support and bull_pattern and histo > 0 and trend_up
put_signal  = at_resist  and bear_pattern and histo < 0 and trend_down

-- Plots
plot(res,    "Resistencia", "red",   2, 0, style.levels, na_mode.continue)
plot(sup,    "Soporte",     "green", 2, 0, style.levels, na_mode.continue)
plot(ema200, "EMA 200",     "gray",  1)

plot_shape(call_signal, "CALL HYB", shape_style.triangleup,
    shape_size.huge, "green", shape_location.belowbar, 0, "BUY", "white")
plot_shape(put_signal, "PUT HYB", shape_style.triangledown,
    shape_size.huge, "red", shape_location.abovebar, 0, "SELL", "white")

color_bar = "gray"
if call_signal then color_bar = "green" end
if put_signal  then color_bar = "red"   end
barcolor(color_bar)'''

        st.markdown(f'<div class="code-block">{script_c}</div>', unsafe_allow_html=True)
        st.code(script_c, language="lua")

    # Comparativa scripts
    st.markdown('<div class="sec">COMPARATIVA DE LOS 3 SCRIPTS</div>', unsafe_allow_html=True)
    ca, cb, cc = st.columns(3)
    for col, nombre, color, bg, border, pros, contras, rec in [
        (ca,"Script A\nMomentum","#92650a","#fef9ee","#fcd34d",
         ["Muchas senales","Facil de leer","Funciona en tendencia"],
         ["Mas falsas en rango","Requiere mercado activo"],
         "Sesion Londres/NY con noticias"),
        (cb,"Script B\nReversion","#1d4ed8","#dbeafe","#93c5fd",
         ["Alta precision","Funciona en rango","Senales claras"],
         ["Pocas senales","Riesgo en tendencia fuerte"],
         "Mercado lateral sin noticias"),
        (cc,"Script C\nHibrido","#6d28d9","#ede9fe","#c4b5fd",
         ["Mayor precision","Combina PA + indicadores","Menos falsas"],
         ["Pocas senales","Mas complejo"],
         "Cualquier sesion activa"),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:{bg};border:1px solid {border};border-radius:8px;padding:14px;">
              <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:16px;
              color:{color};margin-bottom:8px;">{nombre}</div>
              <div style="font-size:11px;margin-bottom:6px;"><b>Pros:</b></div>
              {''.join([f'<div style="font-size:11px;color:#076f45;">✅ {p}</div>' for p in pros])}
              <div style="font-size:11px;margin-top:6px;margin-bottom:4px;"><b>Contras:</b></div>
              {''.join([f'<div style="font-size:11px;color:#b91c1c;">⚠ {c}</div>' for c in contras])}
              <div style="margin-top:8px;background:#ffffff;border-radius:4px;padding:6px;
              font-family:'Share Tech Mono',monospace;font-size:9px;color:{color};">
              USAR CUANDO: {rec}</div>
            </div>""", unsafe_allow_html=True)


# ================================================================
# TAB 5 — COPY TRADING
# ================================================================
with tab_copy:
    st.markdown('<div class="sec">INTELIGENCIA DE COPY TRADING — IQ OPTION</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#f0fdf4;border:1px solid #86efac;border-radius:8px;
    padding:12px 16px;margin-bottom:14px;font-size:13px;color:#076f45;">
    <b>Nota:</b> Los datos de traders son referenciales. Siempre verificá el historial
    actualizado en la plataforma de IQ Option antes de copiar.
    </div>""", unsafe_allow_html=True)

    # Traders destacados
    st.markdown("**Traders Destacados para Copiar:**")

    traders_data = [
        {
            "nombre": "TopTrader_FX",
            "pais": "Brasil",
            "win_rate": 73,
            "ganancia_mes": "+$2,840",
            "seguidores": "4,200",
            "activos": "EUR/USD, XAU/USD",
            "estilo": "Swing M15",
            "riesgo": "BAJO",
            "riesgo_color": "#076f45",
            "riesgo_bg": "#f0fdf4",
            "rec": "RECOMENDADO",
            "rec_color": "#076f45",
            "color": "#076f45",
        },
        {
            "nombre": "GoldScalper_Pro",
            "pais": "Mexico",
            "win_rate": 68,
            "ganancia_mes": "+$1,920",
            "seguidores": "2,800",
            "activos": "XAU/USD",
            "estilo": "Scalping 1min",
            "riesgo": "MEDIO",
            "riesgo_color": "#92650a",
            "riesgo_bg": "#fefce8",
            "rec": "BUENA OPCION",
            "rec_color": "#92650a",
            "color": "#92650a",
        },
        {
            "nombre": "CryptoKing_LA",
            "pais": "Argentina",
            "win_rate": 65,
            "ganancia_mes": "+$3,100",
            "seguidores": "6,500",
            "activos": "BTC, ETH, SOL",
            "estilo": "Swing Crypto",
            "riesgo": "ALTO",
            "riesgo_color": "#b91c1c",
            "riesgo_bg": "#fef2f2",
            "rec": "EVALUAR",
            "rec_color": "#b91c1c",
            "color": "#6d28d9",
        },
        {
            "nombre": "OilTrader_VIP",
            "pais": "Colombia",
            "win_rate": 70,
            "ganancia_mes": "+$1,540",
            "seguidores": "1,900",
            "activos": "Crude Oil, NAS100",
            "estilo": "Noticias H1",
            "riesgo": "MEDIO",
            "riesgo_color": "#92650a",
            "riesgo_bg": "#fefce8",
            "rec": "BUENA OPCION",
            "rec_color": "#92650a",
            "color": "#1d4ed8",
        },
    ]

    for t in traders_data:
        st.markdown(f"""
        <div class="trader-copy" style="border-left:4px solid {t['color']};">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
            <div>
              <span style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:18px;
              color:#0f172a;">{t['nombre']}</span>
              <span style="font-size:12px;color:#64748b;margin-left:8px;">{t['pais']} · {t['activos']}</span>
            </div>
            <div>
              <span style="background:{t['riesgo_bg']};color:{t['riesgo_color']};
              border:1px solid {t['riesgo_color']};padding:3px 10px;border-radius:20px;
              font-family:'Share Tech Mono',monospace;font-size:9px;font-weight:700;
              margin-right:6px;">RIESGO {t['riesgo']}</span>
              <span style="background:#f0fdf4;color:{t['rec_color']};
              border:1px solid {t['rec_color']};padding:3px 10px;border-radius:20px;
              font-family:'Share Tech Mono',monospace;font-size:9px;font-weight:700;">
              {t['rec']}</span>
            </div>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;">
            <div class="trader-stat">
              <div class="trader-stat-val" style="color:{t['color']};">{t['win_rate']}%</div>
              <div class="trader-stat-lbl">WIN RATE</div>
            </div>
            <div class="trader-stat">
              <div class="trader-stat-val" style="color:#076f45;">{t['ganancia_mes']}</div>
              <div class="trader-stat-lbl">GANANCIA MES</div>
            </div>
            <div class="trader-stat">
              <div class="trader-stat-val" style="color:#64748b;">{t['seguidores']}</div>
              <div class="trader-stat-lbl">SEGUIDORES</div>
            </div>
            <div class="trader-stat">
              <div class="trader-stat-val" style="font-size:14px;color:#64748b;">{t['estilo']}</div>
              <div class="trader-stat-lbl">ESTILO</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

    # Analisis pros vs contras
    st.markdown('<div class="sec">COPY TRADING VS QQE 03/04 — ANALISIS HECTOR</div>', unsafe_allow_html=True)

    col_pros, col_contras = st.columns(2)
    with col_pros:
        st.markdown("""
        <div class="card card-green">
        <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:16px;
        color:#076f45;margin-bottom:10px;">VENTAJAS DEL COPY TRADING</div>
        <div style="font-size:13px;color:#334155;line-height:1.9;">
        ✅ No requiere analisis propio<br>
        ✅ Funciona mientras dormis<br>
        ✅ Aprendes viendo las operaciones del experto<br>
        ✅ Diversifica con traders de diferentes activos<br>
        ✅ Ideal si no tenes tiempo de monitorear<br>
        ✅ Reduccion del estres emocional
        </div>
        </div>""", unsafe_allow_html=True)

    with col_contras:
        st.markdown("""
        <div class="card card-red">
        <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:16px;
        color:#b91c1c;margin-bottom:10px;">DESVENTAJAS DEL COPY TRADING</div>
        <div style="font-size:13px;color:#334155;line-height:1.9;">
        ❌ Perdes control total de tus operaciones<br>
        ❌ El trader puede cambiar su estrategia<br>
        ❌ Resultados pasados no garantizan el futuro<br>
        ❌ Delay en copia puede afectar el precio de entrada<br>
        ❌ No aprendes a operar por tu cuenta<br>
        ❌ Comision de la plataforma reduce ganancias
        </div>
        </div>""", unsafe_allow_html=True)

    # Recomendacion personalizada
    st.markdown("""
    <div style="background:#fef9ee;border:2px solid #92650a;border-radius:10px;
    padding:16px 20px;margin-top:10px;">
    <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:16px;
    color:#92650a;margin-bottom:8px;">RECOMENDACION PERSONALIZADA PARA HECTOR</div>
    <div style="font-size:13px;color:#334155;line-height:1.8;">
    Con tu capital de <b>$467</b> y objetivo de <b>$50/dia</b>, la mejor estrategia es
    <b>combinar ambos enfoques</b>:<br><br>
    <b>70% de tu capital</b> → Opera con QQE 03/04 (desarrollas tu habilidad propia)<br>
    <b>30% de tu capital</b> → Copy trading con 1 trader de riesgo BAJO como <b>TopTrader_FX</b><br><br>
    Asi diversificas el riesgo y seguís aprendiendo al mismo tiempo. Cuando llegues a 
    <b>3 meses con win rate mayor al 65%</b>, considerá operar el 100% con QQE.
    </div>
    </div>""", unsafe_allow_html=True)

    # Consulta IA sobre copy trading
    if st.session_state.api_key.startswith("sk-ant-"):
        st.markdown("---")
        if st.button("ANALIZAR CON IA: Cual trader me conviene copiar?", key="ai_copy"):
            sys = """Eres asesor de trading de Hector. Capital $467, objetivo $50/dia, opera QQE 03/04 en IQ Option.
Analiza si conviene hacer copy trading y que perfil de trader buscar. Max 150 palabras. En espanol. Directo."""
            with st.spinner("Analizando..."):
                resp = ask_claude(st.session_state.api_key,
                                  "Dada mi situacion, me conviene hacer copy trading o mejor opero solo con QQE 03/04?",
                                  system_override=sys)
            st.markdown(f'<div class="ai-box">{resp.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)


# ================================================================
# TAB 6 — ACTIVOS
# ================================================================
with tab_activos:
    st.markdown('<div class="sec">ACTIVOS RECOMENDADOS — PLAN DE TRADING</div>', unsafe_allow_html=True)
    col_fx, col_cr = st.columns(2)

    assets_fx = [
        ("XAU/USD","2,341.50","LONG","72","#076f45","#f0fdf4","#86efac","78","2,338","2,322","2,374"),
        ("CRUDE OIL","77.18","LONG","56","#92650a","#fefce8","#fde047","62","76.90","76.20","78.30"),
        ("EUR/USD","1.0842","LONG","63","#1d4ed8","#dbeafe","#93c5fd","65","1.0820","1.0785","1.0890"),
        ("NAS100","18,240","ESPERAR","45","#64748b","#f8fafc","#e2e8f0","45","—","—","—"),
    ]
    with col_fx:
        st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:9px;color:#92650a;letter-spacing:2px;margin-bottom:10px;">FOREX & COMMODITIES — QQE 03</div>', unsafe_allow_html=True)
        for sym, price, dir_, sent, col, bg, border, conf, e, sl, tp in assets_fx:
            dc = "#076f45" if dir_=="LONG" else ("#b91c1c" if dir_=="SHORT" else "#64748b")
            st.markdown(f"""
            <div class="asset">
              <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                <span style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:17px;color:#0f172a;">{sym}</span>
                <span style="background:{bg};color:{dc};border:1px solid {border};
                padding:2px 8px;border-radius:20px;font-family:'Share Tech Mono',monospace;font-size:9px;font-weight:700;">{dir_}</span>
              </div>
              <div style="font-family:'Share Tech Mono',monospace;font-size:12px;color:#334155;">{price}</div>
              <div class="asset-bar"><div style="height:100%;width:{sent}%;background:{col};border-radius:2px;"></div></div>
              <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-top:6px;">
                <div style="background:#dbeafe;border-radius:4px;padding:6px;text-align:center;">
                  <div style="font-family:'Share Tech Mono',monospace;font-size:8px;color:#94a3b8;">ENTRADA</div>
                  <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:13px;color:#1d4ed8;">{e}</div>
                </div>
                <div style="background:#fef2f2;border-radius:4px;padding:6px;text-align:center;">
                  <div style="font-family:'Share Tech Mono',monospace;font-size:8px;color:#94a3b8;">STOP</div>
                  <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:13px;color:#b91c1c;">{sl}</div>
                </div>
                <div style="background:#f0fdf4;border-radius:4px;padding:6px;text-align:center;">
                  <div style="font-family:'Share Tech Mono',monospace;font-size:8px;color:#94a3b8;">TP</div>
                  <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:13px;color:#076f45;">{tp}</div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

    assets_cr = [
        ("BTC","67,420","LONG","70","#92650a","#fefce8","#fde047","70","66,800","65,500","69,400"),
        ("ETH","3,480","LONG","61","#6d28d9","#ede9fe","#c4b5fd","60","3,440","3,360","3,600"),
        ("SOL","182","ESPERAR","42","#64748b","#f8fafc","#e2e8f0","42","—","—","—"),
    ]
    with col_cr:
        st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:9px;color:#6d28d9;letter-spacing:2px;margin-bottom:10px;">CRYPTO — QQE 04</div>', unsafe_allow_html=True)
        for sym, price, dir_, sent, col, bg, border, conf, e, sl, tp in assets_cr:
            dc = "#076f45" if dir_=="LONG" else ("#b91c1c" if dir_=="SHORT" else "#64748b")
            st.markdown(f"""
            <div class="asset">
              <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                <span style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:17px;color:#0f172a;">{sym}</span>
                <span style="background:{bg};color:{dc};border:1px solid {border};
                padding:2px 8px;border-radius:20px;font-family:'Share Tech Mono',monospace;font-size:9px;font-weight:700;">{dir_}</span>
              </div>
              <div style="font-family:'Share Tech Mono',monospace;font-size:12px;color:#334155;">{price}</div>
              <div class="asset-bar"><div style="height:100%;width:{sent}%;background:{col};border-radius:2px;"></div></div>
              <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-top:6px;">
                <div style="background:#dbeafe;border-radius:4px;padding:6px;text-align:center;">
                  <div style="font-family:'Share Tech Mono',monospace;font-size:8px;color:#94a3b8;">ENTRADA</div>
                  <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:13px;color:#1d4ed8;">{e}</div>
                </div>
                <div style="background:#fef2f2;border-radius:4px;padding:6px;text-align:center;">
                  <div style="font-family:'Share Tech Mono',monospace;font-size:8px;color:#94a3b8;">STOP</div>
                  <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:13px;color:#b91c1c;">{sl}</div>
                </div>
                <div style="background:#f0fdf4;border-radius:4px;padding:6px;text-align:center;">
                  <div style="font-family:'Share Tech Mono',monospace;font-size:8px;color:#94a3b8;">TP</div>
                  <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:13px;color:#076f45;">{tp}</div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)


# ================================================================
# TAB 7 — CODIGOS QQE
# ================================================================
with tab_codigos:
    st.markdown('<div class="sec">CODIGOS QQE 03/04 — COPIAR EN IQ OPTION</div>', unsafe_allow_html=True)
    col_c1, col_c2 = st.columns(2)

    qqe03 = '''instrument {
    name = "QQE 03",
    short_name = "QQE_03",
    icon = "indicators:BB",
    overlay = true
}
input_group {
    "Configuracion de Tendencia",
    periodo_ema = input(100, "Periodo EMA", input.integer, 1, 500, 1),
    color_ema   = input("yellow", "Color EMA", input.color),
    ancho_ema   = input(3, "Grosor EMA", input.line_width)
}
ema_trend = ema(close, periodo_ema)
plot(ema_trend, "EMA 100", color_ema, ancho_ema)
ema200 = ema(close, 200)
plot(ema200, "EMA 200", "orange", 2)
h_level = highest(20)[1]
l_level = lowest(20)[1]
plot(h_level, "Resistencia", "white", 1, 0, style.levels, na_mode.continue)
plot(l_level, "Soporte",     "white", 1, 0, style.levels, na_mode.continue)
e12 = ema(close, 12)
e26 = ema(close, 26)
mc  = e12 - e26
hh  = highest(14)[1]
ll  = lowest(14)[1]
sk  = (close - ll) / (hh - ll) * 100
r   = rsi(close, 14)
ta  = close > ema200 and ema_trend > ema200
tb  = close < ema200 and ema_trend < ema200
buy_trigger  = low > low[1] and close > high[1] and close > ema_trend and mc > 0 and sk < 80 and ta
sell_trigger = high < high[1] and close < low[1] and close < ema_trend and mc < 0 and sk > 20 and tb
plot_shape(buy_trigger,  "COMPRA", shape_style.triangleup,   shape_size.huge, "green", shape_location.belowbar, 0, "BUY",  "white")
plot_shape(sell_trigger, "VENTA",  shape_style.triangledown, shape_size.huge, "red",   shape_location.abovebar, 0, "SELL", "white")
color_v = "gray"
if buy_trigger  and r < 70 then color_v = "green" end
if sell_trigger and r > 30 then color_v = "red"   end
barcolor(color_v)'''

    qqe04 = '''instrument {
    name = "QQE 04 Crypto",
    short_name = "QQE_04",
    icon = "indicators:BB",
    overlay = true
}
input_group {
    "Configuracion",
    periodo_ema = input(50, "Periodo EMA", input.integer, 1, 500, 1),
    color_ema   = input("yellow", "Color EMA", input.color),
    ancho_ema   = input(3, "Grosor EMA", input.line_width)
}
ema_trend = ema(close, periodo_ema)
plot(ema_trend, "EMA 50", color_ema, ancho_ema)
ema200 = ema(close, 200)
plot(ema200, "EMA 200", "orange", 2)
h_level = highest(30)[1]
l_level = lowest(30)[1]
plot(h_level, "Resistencia", "white", 1, 0, style.levels, na_mode.continue)
plot(l_level, "Soporte",     "white", 1, 0, style.levels, na_mode.continue)
e12 = ema(close, 12)
e26 = ema(close, 26)
mc  = e12 - e26
hh  = highest(14)[1]
ll  = lowest(14)[1]
sk  = (close - ll) / (hh - ll) * 100
r   = rsi(close, 14)
ta  = close > ema200 and ema_trend > ema200
tb  = close < ema200 and ema_trend < ema200
buy_trigger  = low > low[1] and close > high[1] and close > ema_trend and mc > 0 and sk < 85 and ta
sell_trigger = high < high[1] and close < low[1] and close < ema_trend and mc < 0 and sk > 15 and tb
plot_shape(buy_trigger,  "COMPRA", shape_style.triangleup,   shape_size.huge, "green", shape_location.belowbar, 0, "BUY",  "white")
plot_shape(sell_trigger, "VENTA",  shape_style.triangledown, shape_size.huge, "red",   shape_location.abovebar, 0, "SELL", "white")
color_v = "gray"
if buy_trigger  and r < 70 then color_v = "green" end
if sell_trigger and r > 30 then color_v = "red"   end
barcolor(color_v)'''

    with col_c1:
        st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:9px;color:#92650a;letter-spacing:1px;margin-bottom:6px;">CODIGO QQE 03 — FOREX M15/H1</div>', unsafe_allow_html=True)
        st.code(qqe03, language="lua")

    with col_c2:
        st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:9px;color:#6d28d9;letter-spacing:1px;margin-bottom:6px;">CODIGO QQE 04 — CRYPTO M15/H1</div>', unsafe_allow_html=True)
        st.code(qqe04, language="lua")

    st.markdown("""
    <div style="background:#f0fdf4;border:1px solid #86efac;border-radius:6px;
    padding:10px 14px;font-family:'Share Tech Mono',monospace;font-size:10px;color:#076f45;margin-top:8px;">
    Copiar codigo → IQ Option → Editor indicadores → Pegar → Guardar → Aplicar en grafico M15 u H1
    </div>""", unsafe_allow_html=True)


# ================================================================
# FOOTER
# ================================================================
st.markdown("""
<div style="border-top:1px solid #e2e8f0;margin-top:24px;padding-top:10px;
font-family:'Share Tech Mono',monospace;font-size:9px;color:#94a3b8;
text-align:center;letter-spacing:1px;">
QQE 03/04 v3 · HECTOR TRADING COMMAND · DIARIO + BINARIAS 1MIN + COPY TRADING
</div>""", unsafe_allow_html=True)
