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
# Zapobiega to blokowaniu kodu przez GitHub Secret Scanning
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
    """Konwertuje plik graficzny na base64 dla CSS."""
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

def get_data():
    """Pobiera checklistę z repozytorium GitHub."""
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
# 3. DESIGN: VORTEZA - BASE PREMIERE UI
# =========================================================
def apply_vorteza_design():
    bg_base64 = get_base64('bg_vorteza.png')
    
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Montserrat:wght@300;400;600;800&display=swap');
        
        /* GŁÓWNE TŁO APLIKACJI */
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.65), rgba(0,0,0,0.65)), url("data:image/png;base64,{bg_base64}");
            background-size: cover;
            background-attachment: fixed;
        }}

        /* FIX SIDEBAR ICON - Ukrywa błąd 'keyboard_double_arrow' */
        [data-testid="sidebar-button"] {{
            color: transparent !important;
            font-size: 0px !important;
        }}
        [data-testid="sidebar-button"]::before {{
            content: '◀'; 
            color: #B58863;
            font-size: 18px;
            visibility: visible;
            font-weight: bold;
        }}

        /* OGÓLNA TYPOGRAFIA */
        .stApp, p, label, span, div {{
            font-family: 'Montserrat', sans-serif !important;
            color: #FFFFFF !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
        }}

        /* NAGŁÓWKI TECHNOLOGICZNE */
        h1, h2, h3, .stSubheader {{
            font-family: 'Orbitron', sans-serif !important;
            color: #B58863 !important;
            text-transform: uppercase;
            letter-spacing: 2px !important;
            margin-bottom: 15px !important;
        }}

        /* KARTY KONTENEROWE (GLASSMORPHISM) */
        .vorteza-card {{
            background: rgba(15, 15, 15, 0.92);
            border: 1px solid rgba(181, 136, 99, 0.25);
            border-left: 5px solid #B58863;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 25px;
            backdrop-filter: blur(15px);
            box-shadow: 0 15px 45px rgba(0,0,0,0.9);
            transition: transform 0.3s ease, border-color 0.3s ease;
        }}

        .vorteza-card:hover {{
            transform: translateY(-5px);
            border-color: #B58863;
        }}

        /* EFEKT WIERSZY CHECKBOXA */
        div[data-testid="stCheckbox"] {{
            background: rgba(255,255,255,0.03);
            padding: 12px 18px;
            border-radius: 8px;
            margin-bottom: 8px;
            transition: all 0.3s ease;
            border: 1px solid transparent;
        }}

        div[data-testid="stCheckbox"]:hover {{
            background: rgba(181, 136, 99, 0.1);
            border: 1px solid rgba(181, 136, 99, 0.3);
            transform: translateX(10px);
        }}

        /* PRZYCISK GŁÓWNY (START/SUBMIT) */
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
            transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}
        
        .stButton > button:hover {{
            box-shadow: 0 0 50px rgba(181, 136, 99, 0.6);
            filter: brightness(1.2);
            transform: scale(1.02);
        }}

        /* STYLIZACJA ELEMENTÓW FORMULARZA */
        section[data-testid="stSidebar"] {{
            background-color: rgba(5, 5, 5, 0.98) !important;
            border-right: 1px solid rgba(181, 136, 99, 0.2);
        }}

        input, div[data-baseweb="input"] > div, textarea {{
            background: rgba(255,255,255,0.07) !important;
            border: 1px solid rgba(181, 136, 99, 0.3) !important;
            border-radius: 10px !important;
            color: white !important;
        }}

        div[data-testid="stForm"] {{
            border: none !important;
            padding: 0 !important;
        }}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 4. LOGIKA APLIKACJI
# =========================================================
st.set_page_config(page_title="VORTEZA - BASE | HUB", layout="wide")
apply_vorteza_design()

if "auth" not in st.session_state:
    st.session_state.auth = False

# --- EKRAN AUTORYZACJI ---
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown('<div class="vorteza-card" style="text-align:center;">', unsafe_allow_html=True)
        st.subheader("BASE SYSTEM ACCESS")
        u = st.text_input("Operator ID")
        p = st.text_input("Security Key", type="password")
        if st.button("AUTHORIZE"):
            if u in USER_DB and USER_DB[u] == p:
                st.session_state.auth = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("ACCESS DENIED: Invalid Security Credentials")
        st.markdown('</div>', unsafe_allow_html=True)

# --- GŁÓWNY PANEL OPERACYJNY ---
else:
    # PASEK BOCZNY (SIDEBAR)
    with st.sidebar:
        try:
            st.image('logo_vorteza.png', use_container_width=True)
        except:
            st.title("VORTEZA")
        
        st.markdown("---")
        st.write(f"👤 **OPERATOR:** {st.session_state.user}")
        st.write(f"📡 **STATUS:** VORTEZA-BASE ACTIVE")
        st.write(f"📅 **DATE:** {datetime.now().strftime('%d/%m/%Y')}")
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        if st.button("LOGOUT SYSTEM"):
            st.session_state.auth = False
            st.rerun()

    # TREŚĆ DASHBOARDU
    config = get_data()
    
    if config:
        st.markdown("<h1 style='text-align: center; margin-bottom: 40px;'>VORTEZA - BASE DASHBOARD</h1>", unsafe_allow_html=True)
        
        with st.form("vorteza_base_core"):
            # Sekcja 1: Dane Pojazdu
            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            st.subheader("Vehicle Identification")
            c1, c2 = st.columns(2)
            rej = c1.text_input("LICENSE PLATE NUMBER")
            km = c2.number_input("CURRENT MILEAGE (KM)", step=1, value=0)
            st.markdown('</div>', unsafe_allow_html=True)

            # Sekcja 2: Dynamiczna Checklista (Grid 2-kolumnowy)
            grid = st.columns(2)
            for i, (kat, punkty) in enumerate(config["lista_kontrolna"].items()):
                with grid[i % 2]:
                    # Każda kategoria w osobnej karcie
                    st.markdown(f'<div class="vorteza-card"><h3>{kat}</h3>', unsafe_allow_html=True)
                    for p_text in punkty:
                        st.checkbox(p_text, key=f"c_{p_text}")
                    st.markdown('</div>', unsafe_allow_html=True)

            # Sekcja 3: Raport Techniczny
            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            st.subheader("Technical Remarks & Observations")
            uwagi = st.text_area("Provide detailed report on any detected anomalies...", height=120)
            st.markdown('</div>', unsafe_allow_html=True)

            # Przycisk wysyłki
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("FINALIZE AND TRANSMIT PROTOCOL"):
                if not rej:
                    st.error("VALIDATION ERROR: Vehicle License Plate is mandatory.")
                else:
                    st.success(f"PROTOCOL SUCCESSFULLY TRANSMITTED TO HUB: {rej}")
                    st.balloons()
    else:
        st.error("DATABASE CONNECTION ERROR: Please check G_TOKEN in Streamlit Secrets.")
