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
# 3. DESIGN: VORTEZA - BASE "EXECUTIVE DARK"
# =========================================================
def apply_vorteza_design():
    bg_base64 = get_base64('bg_vorteza.png')
    
    st.markdown(f"""
        <style>
        /* IMPORT NOWOCZESNYCH CZCIONEK PREMIUM */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Space+Grotesk:wght@300;500;700&display=swap');
        
        /* GŁÓWNE TŁO */
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("data:image/png;base64,{bg_base64}");
            background-size: cover;
            background-attachment: fixed;
        }}

        /* FIX SIDEBAR ICON - Czyszczenie błędu wizualnego */
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

        /* TYPOGRAFIA INTER (Bardzo czytelna) */
        .stApp, p, label, span, div {{
            font-family: 'Inter', sans-serif !important;
            color: #F5F5F5 !important;
            font-weight: 400;
        }}

        /* NAGŁÓWKI SPACE GROTESK (Elegancki Tech) */
        h1, h2, h3, .stSubheader {{
            font-family: 'Space Grotesk', sans-serif !important;
            color: #B58863 !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 1px !important;
        }}

        /* KARTY DASHBOARDU - Ostre kąty dla profesjonalnego wyglądu */
        .vorteza-card {{
            background: rgba(12, 12, 12, 0.96);
            border: 1px solid rgba(181, 136, 99, 0.2);
            border-left: 4px solid #B58863;
            border-radius: 4px;
            padding: 30px;
            margin-bottom: 20px;
            backdrop-filter: blur(20px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.7);
        }}

        /* LISTA KONTROLNA - INTERAKTYWNE WIERSZE */
        div[data-testid="stCheckbox"] {{
            background: rgba(255,255,255,0.02);
            padding: 14px 20px;
            border-radius: 4px;
            margin-bottom: 8px;
            transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid transparent;
        }}

        div[data-testid="stCheckbox"]:hover {{
            background: rgba(181, 136, 99, 0.12);
            border: 1px solid rgba(181, 136, 99, 0.3);
            transform: translateX(8px);
        }}

        /* PRZYCISK - MATOWA MIEDŹ (Luxury Look) */
        .stButton > button {{
            background-color: #B58863 !important;
            color: white !important;
            font-family: 'Space Grotesk', sans-serif !important;
            font-weight: 700 !important;
            border: none !important;
            padding: 22px !important;
            border-radius: 4px !important;
            text-transform: uppercase;
            letter-spacing: 2px;
            width: 100%;
            transition: 0.3s;
            box-shadow: 0 10px 25px rgba(0,0,0,0.4);
        }}
        
        .stButton > button:hover {{
            background-color: #8B6B4F !important;
            box-shadow: 0 0 35px rgba(181, 136, 99, 0.45);
            transform: translateY(-2px);
        }}

        /* SIDEBAR I ELEMENTY INPUT */
        section[data-testid="stSidebar"] {{
            background-color: rgba(5, 5, 5, 0.98) !important;
            border-right: 1px solid rgba(181, 136, 99, 0.1);
        }}

        input, div[data-baseweb="input"] > div, textarea {{
            background: rgba(255,255,255,0.05) !important;
            border: 1px solid rgba(181, 136, 99, 0.2) !important;
            border-radius: 4px !important;
            color: white !important;
        }}

        /* Usunięcie domyślnych obramowań Streamlit */
        div[data-testid="stForm"] {{ border: none !important; padding: 0 !important; }}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 4. GŁÓWNA LOGIKA VORTEZA - BASE
# =========================================================
st.set_page_config(page_title="VORTEZA - BASE", layout="wide")
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
        u = st.text_input("Operator ID")
        p = st.text_input("Security Key", type="password")
        if st.button("AUTHORIZE"):
            if u in USER_DB and USER_DB[u] == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("Access Denied")
        st.markdown('</div>', unsafe_allow_html=True)

# --- PANEL GŁÓWNY ---
else:
    with st.sidebar:
        try: st.image('logo_vorteza.png', use_container_width=True)
        except: st.title("VORTEZA")
        st.markdown("---")
        st.write(f"👤 **OPERATOR:** {st.session_state.user}")
        st.write(f"📅 **DATE:** {datetime.now().strftime('%d/%m/%Y')}")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("LOGOUT SYSTEM"):
            st.session_state.auth = False
            st.rerun()

    config = get_data()
    if config:
        st.markdown("<h1 style='text-align: center; margin-bottom: 40px;'>VORTEZA - BASE DASHBOARD</h1>", unsafe_allow_html=True)
        
        with st.form("main_hub"):
            # Sekcja Dane Pojazdu
            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            st.subheader("Vehicle Data")
            c1, c2 = st.columns(2)
            rej = c1.text_input("LICENSE PLATE")
            km = c2.number_input("CURRENT MILEAGE (KM)", step=1, value=0)
            st.markdown('</div>', unsafe_allow_html=True)

            # Checklista (Grid 2-kolumnowy)
            grid = st.columns(2)
            for i, (kat, punkty) in enumerate(config["lista_kontrolna"].items()):
                with grid[i % 2]:
                    st.markdown(f'<div class="vorteza-card"><h3>{kat}</h3>', unsafe_allow_html=True)
                    for p_text in punkty:
                        st.checkbox(p_text, key=f"p_{p_text}")
                    st.markdown('</div>', unsafe_allow_html=True)

            # Uwagi
            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            st.subheader("Technical Remarks")
            st.text_area("Observations or damage descriptions...", height=120)
            st.markdown('</div>', unsafe_allow_html=True)

            # Submit
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("SUBMIT AND ENCRYPT PROTOCOL"):
                if not rej: st.error("Plate number is required.")
                else: 
                    st.success(f"PROTOCOL FOR {rej} TRANSMITTED")
                    st.balloons()
    else:
        st.error("Connection Error: Check G_TOKEN in Secrets.")
