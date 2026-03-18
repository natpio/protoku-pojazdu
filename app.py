import streamlit as st
import json
import requests
import base64
from PIL import Image
from datetime import datetime

# =========================================================
# 1. KONFIGURACJA DOSTĘPU
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
# 2. FUNKCJE SYSTEMOWE
# =========================================================
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except: return ""

def get_github_data():
    if not GITHUB_TOKEN: return None
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            decoded = base64.b64decode(content['content']).decode('utf-8')
            return json.loads(decoded)
        return None
    except: return None

# =========================================================
# 3. EKSTREMALNA CZYTELNOŚĆ (VORTEZA ULTRA CONTRAST)
# =========================================================
def apply_vorteza_theme():
    bin_str = get_base64_of_bin_file('bg_vorteza.png')
    if bin_str:
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{bin_str}");
                background-size: cover;
                background-attachment: fixed;
            }}
            </style>
        """, unsafe_allow_html=True)

    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;900&display=swap');

            /* 1. CAŁKOWITE ZASŁONIĘCIE TŁA POD TEKSTEM */
            .vorteza-section {
                background-color: #000000 !important; /* Zero przezroczystości - czysta czerń */
                padding: 35px;
                border-radius: 0px; /* Ostry, techniczny wygląd */
                border: 2px solid #B58863;
                margin-bottom: 30px;
                box-shadow: 0 20px 50px rgba(0,0,0,1);
            }

            /* 2. EKSTREMALNY TEKST */
            .stApp, p, span, label, div {
                color: #FFFFFF !important; /* Jaskrawa biel */
                font-family: 'Montserrat', sans-serif !important;
                font-weight: 700 !important;
                font-size: 1.1rem !important;
            }

            /* 3. NAGŁÓWKI (MIEDŹ) */
            h1, h2, h3, .stSubheader {
                color: #B58863 !important;
                font-weight: 900 !important;
                text-transform: uppercase;
                letter-spacing: 3px;
                background: #000000;
                padding: 5px 15px;
                display: inline-block;
            }

            /* 4. CHECKBOXY - DUŻE I WYRAŹNE */
            .stCheckbox label {
                background: #111111 !important;
                padding: 10px 20px !important;
                border-radius: 5px;
                border: 1px solid #333;
                width: 100%;
                display: block;
            }
            
            .stCheckbox label p {
                font-size: 1.2rem !important;
                color: #FFFFFF !important;
            }

            /* 5. INPUTY */
            input, textarea {
                background-color: #000000 !important;
                color: #FFFFFF !important;
                border: 2px solid #B58863 !important;
                font-size: 1.2rem !important;
            }

            /* 6. PRZYCISK */
            .stButton > button {
                background-color: #B58863 !important;
                color: #000000 !important;
                font-weight: 900 !important;
                font-size: 1.3rem !important;
                height: 4em;
                border: none !important;
            }
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 4. LOGIKA
# =========================================================
st.set_page_config(page_title="VORTEZA | SYSTEM", layout="wide")
apply_vorteza_theme()

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
        st.subheader("VORTEZA ACCESS")
        u = st.text_input("User")
        p = st.text_input("Pass", type="password")
        if st.button("LOGIN"):
            if u in USER_DB and USER_DB[u] == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
else:
    c1, c2, c3 = st.columns([1, 4, 1])
    with c1: 
        try: st.image('logo_vorteza.png', width=150)
        except: st.title("VORTEZA")
    with c3:
        if st.button("LOGOUT"):
            st.session_state.auth = False
            st.rerun()

    config = get_github_data()
    if config:
        with st.form("main_form"):
            st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
            st.subheader("POJAZD")
            r1, r2 = st.columns(2)
            nr = r1.text_input("REJESTRACJA")
            km = r2.number_input("PRZEBIEG", step=1)
            st.markdown('</div>', unsafe_allow_html=True)

            for kat, punkty in config["lista_kontrolna"].items():
                st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
                st.subheader(kat)
                for p in punkty:
                    st.checkbox(p, key=f"x_{p}")
                st.markdown('</div>', unsafe_allow_html=True)

            if st.form_submit_button("WYŚLIJ PROTOKÓŁ"):
                st.success("ZAPISANO")
                st.balloons()
    else:
        st.error("BŁĄD POŁĄCZENIA GITHUB")
