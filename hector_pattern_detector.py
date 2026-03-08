# HECTOR PATTERN DETECTOR v5 - VERSIÓN BLINDADA
# Sistema Profesional de Reconocimiento de Patrones
# by Hector Trading — IQ Option M15

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
    initial_sidebar_state="collapsed"
)

# --- BLINDAJE DE SEGURIDAD (CONEXIÓN A LA CAJA FUERTE) ---
# Si las llaves no están en Secrets, el sistema usará un texto vacío para evitar errores
TELEGRAM_TOKEN = st.secrets.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "")
ANTHROPIC_KEY = st.secrets.get("ANTHROPIC_API_KEY", "")

# ================================================================
# CSS (Optimizado para iPhone y Desktop)
# ================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=Share+Tech+Mono&family=Inter:wght@400;500;600&display=swap');
html, body, .stApp { background:#e8f0f7 !important; }
.stApp { font-family:'Inter',sans-serif; color:#1a2940; }
[data-testid="stSidebar"] { background:#f0f6fc !important; border-right:1px solid #bdd4e8 !important; }
.stTabs [data-baseweb="tab-list"] { background:#f0f6fc; border-bottom:2px solid #bdd4e8; }
.stTabs [data-baseweb="tab"] { background:transparent; color:#5a7a99 !important; font-family:'Share Tech Mono',monospace; font-size:10px; letter-spacing:1px; padding:10px 12px; border:none; }
.stTabs [aria-selected="true"] { background:#ddeaf5 !important; color:#0f2035 !important; border-bottom:2px solid #c8920a !important; font-weight:700 !important; }
.kpi { background:#f0f6fc; border:1px solid #bdd4e8; border-radius:10px; padding:14px; text-align:center; }
.kpi-label { font-family:'Share Tech Mono',monospace; font-size:9px; color:#5a7a99; letter-spacing:2px; margin-bottom:6px; }
.kpi-value { font-family:'Rajdhani',sans-serif; font-size:30px; font-weight:700; line-height:1.1; }
.kpi-sub   { font-family:'Share Tech Mono',monospace; font-size:9px; color:#5a7a99; margin-top:3px; }
.sec { font-family:'Share Tech Mono',monospace; font-size:10px; color:#5a7a99; letter-spacing:3px; border-bottom:1px solid #bdd4e8; padding-bottom:6px; margin:16px 0 12px; }
.hector-brand { background:linear-gradient(135deg,#f0f6fc,#bdd4e8); border:1px solid #c8920a; border-radius:12px; padding:18px; text-align:center; margin-bottom:14px; }
.sesion-bar { border-radius:8px; padding:8px 16px; margin-bottom:14px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px; }
.stButton>button { background:#c8920a !important; color:#0f2035 !important; border:none !important; border-radius:12px !important; font-family:'Share Tech Mono',monospace !important; font-size:13px !important; letter-spacing:1px !important; font-weight:700 !important; padding:14px 20px !important; min-height:48px !important; width:100% !important; touch-action:manipulation !important; }
@media (max-width:768px) { [data-testid="stSidebar"] { display:none !important; } .kpi-value { font-size:24px !important; } .stButton>button { font-size:15px !important; min-height:52px !important; } }
</style>
""", unsafe_allow_html=True)

# ================================================================
# TELEGRAM (Blindado)
# ================================================================
def enviar_telegram(mensaje):
    """Envia mensaje a Telegram usando las llaves de la caja fuerte"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        r = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": mensaje,
            "parse_mode": "HTML"
        }, timeout=10)
        return r.status_code == 200
    except:
        return False

# ================================================================
# SESSION STATE Y CONFIGURACIÓN
# ================================================================
defaults = {
    "resultados_scan": [],
    "ultimo_scan": None,
    "alertas": [],
    "api_key": ANTHROPIC_KEY, # Usa la clave de la caja fuerte por defecto
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
    "telegram_on": True,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- (El resto de tus funciones de detección se mantienen igual) ---
# [Aquí sigue todo tu código de indicadores, patrones y lógica...]
