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
# 3. DESIGN: VORTEZA - BASE "LOGO-MATCH EDITION"
# =========================================================
def apply_vorteza_design():
    bg_base64 = get_base64('bg_vorteza.png')
    
    st.markdown(f"""
        <style>
        /* IMPORT CZCIONEK: MICHROMA (Szeroka jak w logo) i MONTSERRAT */
        @import url('https://fonts.googleapis.com/css2?family=Michroma&family=Montserrat:wght@400;700;900&display=swap');
        
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.65), rgba(0,0,0,0.65)), url("data:image/png;base64,{bg_base64}");
            background-size: cover;
            background-attachment: fixed;
        }}

        /* FIX SIDEBAR ICON */
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

        /* GŁÓWNY NAGŁÓWEK - STYLIZOWANY NA LOGO */
        .logo-font {{
            font-family: 'Michroma', sans-serif !important;
            color: #B58863 !important;
            text-align: center;
            font-size: 2.2rem !important;
            letter-spacing: 8px !important; /* Szerokie rozstawienie jak w logo */
            text-transform: uppercase;
            font-weight: bold;
            margin-bottom: 40px;
            text-shadow: 2px 2px 10px rgba(0,0,0,0.8);
        }}

        /* POZOSTAŁE NAGŁÓWKI (Kategorie) */
        h2, h3, .stSubheader {{
            font-family: 'Michroma', sans-serif !important;
            color: #B58863 !important;
            font-size: 1.1rem !important;
            letter-spacing: 3px !important;
            text-transform: uppercase;
        }}

        /* TREŚĆ I CHECKBOXY */
        .stApp, p, label, span, div {{
            font-family: 'Montserrat', sans-serif !important;
            color: #FFFFFF !important;
        }}

        /* KARTY */
        .vorteza-card {{
            background: rgba(10, 10, 10, 0.94);
            border: 1px solid rgba(181, 136, 99, 0.2);
            border-left: 5px solid #B58863;
            border-radius: 4px;
            padding: 25px;
            margin-bottom: 25px;
            backdrop-filter: blur(15px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.8);
        }}

        /* WIERSZE CHECKBOXA */
        div[data-testid="stCheckbox"] {{
            background: rgba(255,255,255,0.03);
            padding: 12px 18px;
            border-radius: 2px;
            margin-bottom: 6px;
            transition: 0.3s;
        }}

        div[data-testid="stCheckbox"]:hover {{
            background: rgba(181, 136, 99, 0.1);
            transform: translateX(10px);
        }}

        /* PRZYCISK */
        .stButton > button {{
            background-color: #B58863 !important;
            color: white !important;
            font-family: 'Michroma', sans-serif !important;
            font-size: 0.9rem !important;
            border: none !important;
            padding: 20px !important;
            border-radius: 2px !important;
            text-transform: uppercase;
            letter-spacing: 4px;
            width: 100%;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}
        
        .stButton > button:hover {{
            background-color: #8B6B4F !important;
            box-shadow: 0 0 40px rgba(181, 136, 99, 0.4);
        }}

        section[data-testid="stSidebar"] {{
            background-color: rgba(5, 5, 5, 0.98) !important;
            border-right: 1px solid rgba(181, 136, 99, 0.15);
        }}

        div[data-testid="stForm"] {{ border: none !important; padding: 0 !important; }}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 4. LOGIKA APLIKACJI
# =========================================================
st.set_page_config(page_title="VORTEZA-BASE", layout="wide")
apply_vorteza_design()

if "auth" not in st.session_state:
    st.session_state.auth = False

# --- LOGOWANIE ---
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown('<div class="vorteza-card" style="text-align:center;">', unsafe_allow_html=True)
        st.subheader("BASE ACCESS")
        u = st.text_input("Operator")
        p = st.text_input("Security Key", type="password")
        if st.button("AUTHORIZE"):
            if u in USER_DB and USER_DB[u] == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- PANEL OPERACYJNY ---
else:
    with st.sidebar:
        try: st.image('logo_vorteza.png', use_container_width=True)
        except: st.title("VORTEZA")
        st.markdown("---")
        st.write(f"👤 **OPERATOR:** {st.session_state.user}")
        st.write(f"📅 **DATE:** {datetime.now().strftime('%d/%m/%Y')}")
        if st.button("LOGOUT SYSTEM"):
            st.session_state.auth = False
            st.rerun()

    config = get_data()
    if config:
        # GŁÓWNY NAGŁÓWEK STYLIZOWANY NA LOGO
        st.markdown('<p class="logo-font">VORTEZA - BASE</p>', unsafe_allow_html=True)
        
        with st.form("main_form"):
            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            st.subheader("Vehicle Data")
            c1, c2 = st.columns(2)
            rej = c1.text_input("LICENSE PLATE")
            km = c2.number_input("MILEAGE (KM)", step=1, value=0)
            st.markdown('</div>', unsafe_allow_html=True)

            grid = st.columns(2)
            for i, (kat, punkty) in enumerate(config["lista_kontrolna"].items()):
                with grid[i % 2]:
                    st.markdown(f'<div class="vorteza-card"><h3>{kat}</h3>', unsafe_allow_html=True)
                    for p_text in punkty:
                        st.checkbox(p_text, key=f"p_{p_text}")
                    st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            st.subheader("Technical Notes")
            st.text_area("Observations...", height=100)
            st.markdown('</div>', unsafe_allow_html=True)

            if st.form_submit_button("SUBMIT AND ENCRYPT PROTOCOL"):
                if not rej: st.error("Plate number required!")
                else: st.success("TRANSMISSION SUCCESSFUL"); st.balloons()
