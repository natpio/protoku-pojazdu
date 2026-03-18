import streamlit as st
import json
import requests
import base64
from PIL import Image
from datetime import datetime

# =========================================================
# 1. KONFIGURACJA I SEKRETY
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
    """Konwertuje grafikę na kod, aby użyć jej jako tła."""
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

def get_data():
    """Pobiera dane z pliku JSON na Twoim GitHubie."""
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
# 3. DESIGN: VORTEZA BLACK EDITION (MODERN & READABLE)
# =========================================================
def apply_vorteza_design():
    bg_base64 = get_base64('bg_vorteza.png')
    
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Montserrat:wght@300;400;600;800&display=swap');
        
        /* 1. TŁO I PODSTAWY */
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.55)), url("data:image/png;base64,{bg_base64}");
            background-size: cover;
            background-attachment: fixed;
        }}

        /* 2. FIX IKONY SIDEBARA (Usuwa błąd 'keyboard_double_arrow_left') */
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

        /* 3. STYLIZACJA TEKSTU - EKSTREMALNY KONTRAST */
        .stApp, p, label, span, div {{
            font-family: 'Montserrat', sans-serif !important;
            color: #FFFFFF !important;
            text-shadow: 1px 1px 3px rgba(0,0,0,1);
        }}

        h1, h2, h3, .stSubheader {{
            font-family: 'Orbitron', sans-serif !important;
            color: #B58863 !important;
            text-transform: uppercase;
            letter-spacing: 3px !important;
            margin-bottom: 15px !important;
        }}

        /* 4. KARTY Z EFEKTEM SZKŁA (GLASSMORPHISM) */
        .vorteza-card {{
            background: linear-gradient(135deg, rgba(20,20,20,0.98) 0%, rgba(5,5,5,0.9) 100%);
            border: 1px solid rgba(181, 136, 99, 0.3);
            border-left: 5px solid #B58863;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 25px;
            backdrop-filter: blur(15px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.9);
            transition: all 0.3s ease;
        }}
        .vorteza-card:hover {{
            transform: translateY(-5px);
            border-color: #B58863;
            box-shadow: 0 20px 50px rgba(181, 136, 99, 0.2);
        }}

        /* 5. SIDEBAR DESIGN */
        section[data-testid="stSidebar"] {{
            background-color: rgba(5, 5, 5, 0.98) !important;
            border-right: 2px solid rgba(181, 136, 99, 0.3);
        }}

        /* 6. PRZYCISK PREMIUM VORTEZA */
        .stButton > button {{
            background: linear-gradient(90deg, #8B6B4F 0%, #B58863 50%, #8B6B4F 100%);
            color: white !important;
            font-family: 'Orbitron', sans-serif !important;
            font-weight: 700 !important;
            border: none !important;
            padding: 20px !important;
            border-radius: 6px !important;
            text-transform: uppercase;
            letter-spacing: 2px;
            width: 100%;
            transition: 0.4s ease-in-out;
            box-shadow: 0 10px 25px rgba(0,0,0,0.6);
        }}
        .stButton > button:hover {{
            box-shadow: 0 0 30px rgba(181, 136, 99, 0.7);
            filter: brightness(1.2);
            transform: scale(1.01);
        }}

        /* 7. CZYSZCZENIE FORMULARZA */
        div[data-testid="stForm"] {{
            border: none !important;
            padding: 0 !important;
        }}

        /* Stylizacja checkboxów dla lepszej widoczności */
        .stCheckbox label p {{
            font-size: 1.1rem !important;
            font-weight: 600 !important;
        }}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 4. GŁÓWNA LOGIKA APLIKACJI
# =========================================================
st.set_page_config(page_title="VORTEZA FLOW | OPERATIONAL HUB", layout="wide")
apply_vorteza_design()

if "auth" not in st.session_state:
    st.session_state.auth = False

# --- EKRAN LOGOWANIA ---
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.3, 1])
    with col:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown('<div class="vorteza-card" style="text-align:center;">', unsafe_allow_html=True)
        st.subheader("SYSTEM ACCESS")
        u = st.text_input("Operator Username")
        p = st.text_input("Access Password", type="password")
        if st.button("AUTHORIZE SYSTEM"):
            if u in USER_DB and USER_DB[u] == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else:
                st.error("ACCESS DENIED: Invalid Credentials")
        st.markdown('</div>', unsafe_allow_html=True)

# --- PANEL OPERACYJNY PO LOGOWANIU ---
else:
    # --- PASEK BOCZNY (SIDEBAR) ---
    with st.sidebar:
        try:
            # Próba wczytania logo
            st.image('logo_vorteza.png', use_container_width=True)
        except:
            st.title("VORTEZA")
        
        st.markdown("---")
        st.write(f"👤 **OPERATOR:** {st.session_state.user}")
        st.write(f"📅 **DATE:** {datetime.now().strftime('%d/%m/%Y')}")
        st.write(f"📡 **STATUS:** ENCRYPTED CONNECTION")
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        if st.button("LOGOUT SYSTEM"):
            st.session_state.auth = False
            st.rerun()

    # --- TREŚĆ GŁÓWNA (DASHBOARD) ---
    config = get_data()
    
    if config:
        st.markdown("<h1 style='text-align: center; margin-bottom: 40px;'>OPERATIONAL DASHBOARD</h1>", unsafe_allow_html=True)
        
        with st.form("cockpit_form"):
            # Sekcja 1: Dane Pojazdu
            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            st.subheader("Vehicle Identification")
            c1, c2 = st.columns(2)
            rej = c1.text_input("LICENSE PLATE NUMBER")
            km = c2.number_input("CURRENT MILEAGE (KM)", step=1, value=0)
            st.markdown('</div>', unsafe_allow_html=True)

            # Sekcja 2: Checklista (Układ 2-kolumnowy typu Grid)
            grid_cols = st.columns(2)
            for i, (kat, punkty) in enumerate(config["lista_kontrolna"].items()):
                with grid_cols[i % 2]:
                    st.markdown(f'<div class="vorteza-card"><h3>{kat}</h3>', unsafe_allow_html=True)
                    for p_text in punkty:
                        st.checkbox(p_text, key=f"check_{p_text}")
                    st.markdown('</div>', unsafe_allow_html=True)

            # Sekcja 3: Raport Techniczny
            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            st.subheader("Technical Remarks & Observations")
            uwagi = st.text_area("Provide details on any damages or technical issues...", height=120)
            st.markdown('</div>', unsafe_allow_html=True)

            # Przycisk Finałowy
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("SUBMIT AND ENCRYPT PROTOCOL"):
                if not rej:
                    st.error("CRITICAL ERROR: Vehicle plate number is required.")
                else:
                    st.success(f"PROTOCOL SUCCESSFULLY TRANSMITTED FOR: {rej}")
                    st.balloons()
    else:
        st.error("CRITICAL ERROR: Database Connection Failed. Please verify GitHub Secrets.")
