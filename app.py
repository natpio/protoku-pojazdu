import streamlit as st
import json
import requests
import base64
from PIL import Image
from datetime import datetime

# =========================================================
# 1. KONFIGURACJA I BEZPIECZEŃSTWO
# =========================================================
USER_DB = {
    "admin": "vorteza",
    "kierowca1": "CrystalBridge116"
}

# Pobieranie tokenu z Secrets Streamlit
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
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except: return ""

def get_data():
    if not GITHUB_TOKEN: return None
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            content = res.json()
            return json.loads(base64.b64decode(content['content']).decode('utf-8'))
    except: return None

# =========================================================
# 3. DESIGN: VORTEZA COCKPIT UI
# =========================================================
def apply_vorteza_design():
    bg_base64 = get_base64('bg_vorteza.png')
    
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Montserrat:wght@300;400;600&display=swap');
        
        /* TŁO GŁÓWNE */
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("data:image/png;base64,{bg_base64}");
            background-size: cover;
            background-attachment: fixed;
        }}

        /* OGÓLNE TEKSTY */
        .stApp, p, label, span, div {{
            font-family: 'Montserrat', sans-serif !important;
            color: #FFFFFF !important;
        }}

        /* NAGŁÓWKI TYPU COCKPIT */
        h1, h2, h3, .stSubheader {{
            font-family: 'Orbitron', sans-serif !important;
            color: #B58863 !important;
            text-transform: uppercase;
            letter-spacing: 3px !important;
            text-shadow: 2px 2px 10px rgba(0,0,0,0.8);
        }}

        /* KARTY DASHBOARDU */
        .vorteza-card {{
            background: linear-gradient(135deg, rgba(20,20,20,0.95) 0%, rgba(5,5,5,0.85) 100%);
            border: 1px solid rgba(181, 136, 99, 0.2);
            border-left: 5px solid #B58863;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            backdrop-filter: blur(15px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.7);
            transition: 0.3s ease;
        }}
        .vorteza-card:hover {{
            border-color: #B58863;
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(181, 136, 99, 0.2);
        }}

        /* INPUTY I POLA TEKSTOWE */
        input, div[data-baseweb="input"] > div, textarea {{
            background: rgba(255,255,255,0.05) !important;
            border: 1px solid rgba(181, 136, 99, 0.3) !important;
            color: white !important;
            border-radius: 8px !important;
        }}
        
        /* CHECKBOXY - CZYTELNE I ELEGANCKIE */
        .stCheckbox label p {{
            font-size: 1.1rem !important;
            font-weight: 400 !important;
            padding-left: 10px;
        }}

        /* PRZYCISK START/SUBMIT */
        .stButton > button {{
            background: linear-gradient(90deg, #8B6B4F 0%, #B58863 50%, #8B6B4F 100%);
            color: white !important;
            font-family: 'Orbitron', sans-serif !important;
            font-weight: 700 !important;
            border: none !important;
            padding: 20px !important;
            border-radius: 50px !important;
            text-transform: uppercase;
            letter-spacing: 2px;
            width: 100%;
            transition: 0.5s;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        }}
        .stButton > button:hover {{
            box-shadow: 0 0 35px rgba(181, 136, 99, 0.6);
            filter: brightness(1.2);
        }}

        /* SIDEBAR DESIGN */
        section[data-testid="stSidebar"] {{
            background-color: rgba(10, 10, 10, 0.9) !important;
            border-right: 1px solid rgba(181, 136, 99, 0.2);
        }}

        /* UKRYCIE RAMKI FORMULARZA */
        div[data-testid="stForm"] {{
            border: none !important;
            padding: 0 !important;
        }}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 4. LOGIKA APLIKACJI
# =========================================================
st.set_page_config(page_title="VORTEZA FLOW | HUB", layout="wide")
apply_vorteza_design()

if "auth" not in st.session_state:
    st.session_state.auth = False

# --- EKRAN LOGOWANIA ---
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown('<div class="vorteza-card" style="text-align:center;">', unsafe_allow_html=True)
        st.subheader("SYSTEM ACCESS")
        u = st.text_input("User")
        p = st.text_input("Pass", type="password")
        if st.button("AUTHORIZE"):
            if u in USER_DB and USER_DB[u] == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("Access Denied")
        st.markdown('</div>', unsafe_allow_html=True)

# --- PANEL OPERACYJNY ---
else:
    # --- PASEK BOCZNY ---
    with st.sidebar:
        try: st.image('logo_vorteza.png', use_container_width=True)
        except: st.title("VORTEZA")
        st.markdown("---")
        st.write(f"👤 **OPERATOR:** {st.session_state.user}")
        st.write(f"📅 **DATA:** {datetime.now().strftime('%d/%m/%Y')}")
        st.write(f"📡 **STATUS:** SYSTEM ONLINE")
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("LOGOUT SYSTEM"):
            st.session_state.auth = False
            st.rerun()

    # --- TREŚĆ GŁÓWNA ---
    config = get_data()
    if config:
        st.markdown("<h1 style='text-align: center; margin-bottom: 40px;'>OPERATIONAL DASHBOARD</h1>", unsafe_allow_html=True)
        
        with st.form("cockpit_form"):
            # Sekcja 1: Dane Pojazdu
            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            st.subheader("Vehicle Identification")
            c1, c2 = st.columns(2)
            rej = c1.text_input("NUMER REJESTRACYJNY")
            km = c2.number_input("AKTUALNY PRZEBIEG (KM)", step=1, value=0)
            st.markdown('</div>', unsafe_allow_html=True)

            # Sekcja 2: Checklista (Układ 2-kolumnowy)
            grid_cols = st.columns(2)
            for i, (kat, punkty) in enumerate(config["lista_kontrolna"].items()):
                with grid_cols[i % 2]:
                    st.markdown(f'<div class="vorteza-card"><h3>{kat}</h3>', unsafe_allow_html=True)
                    for p in punkty:
                        st.checkbox(p, key=f"check_{p}")
                    st.markdown('</div>', unsafe_allow_html=True)

            # Sekcja 3: Raport i Uwagi
            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            st.subheader("Technical Remarks")
            uwagi = st.text_area("Wpisz dodatkowe spostrzeżenia lub opisz usterki...", height=100)
            st.markdown('</div>', unsafe_allow_html=True)

            # Przycisk Finałowy
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("SUBMIT AND CLOSE PROTOCOL"):
                if not rej:
                    st.error("BŁĄD: Podaj numer rejestracyjny!")
                else:
                    st.success(f"PROTOCOL GENERATED: {rej} - DATA SENT TO HUB")
                    st.balloons()
    else:
        st.error("ERROR: GitHub Connection Failed. Check Secrets.")
