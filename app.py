import streamlit as st
import json
import requests
import base64
from datetime import datetime

# =========================================================
# 1. KONFIGURACJA SYSTEMU VORTEZA - BASE
# =========================================================
USER_DB = {
    "admin": "vorteza",
    "kierowca1": "CrystalBridge116"
}

# Pobieranie tokenu z bezpiecznych ustawień Streamlit (Secrets)
try:
    GITHUB_TOKEN = st.secrets["G_TOKEN"]["G_TOKEN"]
except Exception:
    GITHUB_TOKEN = None 

REPO_OWNER = "natpio"
REPO_NAME = "protoku-pojazdu"
FILE_PATH = "lista_kontrolna.json"

# =========================================================
# 2. FUNKCJE POMOCNICZE
# =========================================================
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

def get_data():
    if not GITHUB_TOKEN:
        return None
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            content = res.json()
            return json.loads(base64.b64decode(content['content']).decode('utf-8'))
        return None
    except:
        return None

# =========================================================
# 3. DESIGN: VORTEZA - BASE "ORBITRON EDITION"
# =========================================================
def apply_vorteza_design():
    bg_base64 = get_base64('bg_vorteza.png')
    
    st.markdown(f"""
        <style>
        /* IMPORT CZCIONKI ORBITRON I MONTSERRAT */
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Montserrat:wght@300;400;700&display=swap');
        
        /* GŁÓWNE TŁO */
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url("data:image/png;base64,{bg_base64}");
            background-size: cover;
            background-attachment: fixed;
        }}

        /* FIX SIDEBAR ICON - Ukrywa błąd tekstowy 'keyboard_double_arrow' */
        [data-testid="sidebar-button"] {{
            color: transparent !important;
            font-size: 0px !important;
        }}
        [data-testid="sidebar-button"]::before {{
            content: '◀'; 
            color: #B58863;
            font-size: 18px;
            visibility: visible;
        }}

        /* TYPOGRAFIA MONTSERRAT DLA TREŚCI */
        .stApp, p, label, span, div {{
            font-family: 'Montserrat', sans-serif !important;
            color: #FFFFFF !important;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.9);
        }}

        /* NAGŁÓWKI ORBITRON (Powrót do poprzedniego stylu) */
        h1, h2, h3, .stSubheader {{
            font-family: 'Orbitron', sans-serif !important;
            color: #B58863 !important;
            text-transform: uppercase;
            letter-spacing: 3px !important;
            font-weight: 700 !important;
        }}

        /* KARTY DASHBOARDU */
        .vorteza-card {{
            background: rgba(10, 10, 10, 0.93);
            border: 1px solid rgba(181, 136, 99, 0.25);
            border-left: 5px solid #B58863;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 25px;
            backdrop-filter: blur(15px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.8);
            transition: 0.3s ease;
        }}

        .vorteza-card:hover {{
            border-color: #B58863;
            box-shadow: 0 15px 45px rgba(181, 136, 99, 0.15);
        }}

        /* INTERAKTYWNE WIERSZE CHECKBOXA */
        div[data-testid="stCheckbox"] {{
            background: rgba(255,255,255,0.03);
            padding: 12px 18px;
            border-radius: 6px;
            margin-bottom: 6px;
            transition: all 0.3s ease;
        }}

        div[data-testid="stCheckbox"]:hover {{
            background: rgba(181, 136, 99, 0.1);
            transform: translateX(10px);
        }}

        /* PRZYCISK SIGNATURE (ORBITRON) */
        .stButton > button {{
            background: linear-gradient(90deg, #8B6B4F 0%, #B58863 50%, #8B6B4F 100%);
            color: white !important;
            font-family: 'Orbitron', sans-serif !important;
            font-weight: 700 !important;
            border: none !important;
            padding: 22px !important;
            border-radius: 8px !important;
            text-transform: uppercase;
            letter-spacing: 2px;
            width: 100%;
            transition: 0.4s;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}
        
        .stButton > button:hover {{
            box-shadow: 0 0 40px rgba(181, 136, 99, 0.5);
            filter: brightness(1.2);
            transform: scale(1.01);
        }}

        /* ELEMENTY INPUT */
        input, div[data-baseweb="input"] > div, textarea {{
            background: rgba(255,255,255,0.05) !important;
            border: 1px solid rgba(181, 136, 99, 0.3) !important;
            border-radius: 8px !important;
            color: white !important;
        }}

        /* SIDEBAR */
        section[data-testid="stSidebar"] {{
            background-color: rgba(5, 5, 5, 0.98) !important;
            border-right: 1px solid rgba(181, 136, 99, 0.2);
        }}

        div[data-testid="stForm"] {{ border: none !important; padding: 0 !important; }}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 4. GŁÓWNA LOGIKA VORTEZA - BASE
# =========================================================
st.set_page_config(page_title="VORTEZA-BASE", layout="wide")
apply_vorteza_design()

if "auth" not in st.session_state:
    st.session_state.auth = False

# --- LOGOWANIE ---
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.3, 1])
    with col:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown('<div class="vorteza-card" style="text-align:center;">', unsafe_allow_html=True)
        st.subheader("BASE ACCESS")
        u = st.text_input("Operator")
        p = st.text_input("Password", type="password")
        if st.button("AUTHORIZE SYSTEM"):
            if u in USER_DB and USER_DB[u] == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("Access Denied")
        st.markdown('</div>', unsafe_allow_html=True)

# --- PANEL OPERACYJNY ---
else:
    with st.sidebar:
        try: st.image('logo_vorteza.png', use_container_width=True)
        except: st.title("VORTEZA")
        st.markdown("---")
        st.write(f"👤 **OPERATOR:** {st.session_state.user}")
        st.write(f"📅 **DATE:** {datetime.now().strftime('%d/%m/%Y')}")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("LOGOUT"):
            st.session_state.auth = False
            st.rerun()

    config = get_data()
    if config:
        st.markdown("<h1 style='text-align: center; margin-bottom: 40px;'>VORTEZA - BASE DASHBOARD</h1>", unsafe_allow_html=True)
        
        with st.form("base_hub"):
            # IDENTYFIKACJA
            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            st.subheader("Vehicle Data")
            c1, c2 = st.columns(2)
            rej = c1.text_input("LICENSE PLATE")
            km = c2.number_input("MILEAGE (KM)", step=1, value=0)
            st.markdown('</div>', unsafe_allow_html=True)

            # LISTA (GRID)
            grid = st.columns(2)
            for i, (kat, punkty) in enumerate(config["lista_kontrolna"].items()):
                with grid[i % 2]:
                    st.markdown(f'<div class="vorteza-card"><h3>{kat}</h3>', unsafe_allow_html=True)
                    for p_text in punkty:
                        st.checkbox(p_text, key=f"p_{p_text}")
                    st.markdown('</div>', unsafe_allow_html=True)

            # UWAGI
            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            st.subheader("Technical Remarks")
            st.text_area("Observations...", height=100)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("SUBMIT PROTOCOL"):
                if not rej: st.error("Plate required")
                else: st.success("SUCCESSFUL TRANSMISSION"); st.balloons()
