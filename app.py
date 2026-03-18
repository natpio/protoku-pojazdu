import streamlit as st
import json
import requests
import base64
from PIL import Image
from datetime import datetime

# =========================================================
# 1. KONFIGURACJA DOSTĘPU I UŻYTKOWNIKÓW
# =========================================================
USER_DB = {
    "admin": "vorteza",
    "kierowca1": "CrystalBridge116"
}

# Pobieranie TOKENU z Streamlit Secrets
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
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

def get_github_data():
    if not GITHUB_TOKEN:
        return None
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            decoded = base64.b64decode(content['content']).decode('utf-8')
            return json.loads(decoded)
        return None
    except:
        return None

# =========================================================
# 3. STYLIZACJA VORTEZA ULTRA-CONTRAST (SOLID BLACK)
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

            /* 1. SOLIDNE CZARNE PANELE - ZERO PRZEŚWITÓW */
            .vorteza-section {
                background-color: #000000 !important; 
                padding: 30px;
                border-radius: 4px;
                border: 2px solid #B58863;
                margin-bottom: 25px;
                box-shadow: 0 20px 60px rgba(0,0,0,1);
            }

            /* 2. WYMUSZENIE BIAŁEGO KOLORU DLA WSZYSTKIEGO */
            .stApp, p, span, label, div {
                color: #FFFFFF !important;
                font-family: 'Montserrat', sans-serif !important;
                font-weight: 700 !important;
            }

            /* 3. NAGŁÓWKI (MIEDŹ NA CZARNYM TLE) */
            h1, h2, h3, .stSubheader {
                color: #B58863 !important;
                font-weight: 900 !important;
                text-transform: uppercase;
                letter-spacing: 3px;
                text-shadow: none !important;
                background: #000000;
                padding: 5px 10px;
            }

            /* 4. CHECKBOXY - CZYTELNOŚĆ 100% */
            .stCheckbox label p {
                color: #FFFFFF !important;
                font-size: 1.2rem !important;
                font-weight: 700 !important;
                background-color: rgba(255,255,255,0.05);
                padding: 5px 15px;
                border-radius: 3px;
            }

            /* 5. POLA INPUT */
            input, textarea, div[data-baseweb="input"] > div {
                background-color: #111111 !important;
                color: #FFFFFF !important;
                border: 1px solid #B58863 !important;
                font-size: 1.1rem !important;
            }

            label[data-testid="stWidgetLabel"] p {
                color: #B58863 !important;
                font-size: 1rem !important;
                font-weight: 900 !important;
            }

            /* 6. PRZYCISK ZATWIERDZENIA */
            .stButton > button {
                background-color: #B58863 !important;
                color: #000000 !important;
                font-weight: 900 !important;
                font-size: 1.2rem !important;
                height: 3.5em;
                border-radius: 2px !important;
                text-transform: uppercase;
                width: 100%;
            }
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 4. LOGIKA APLIKACJI
# =========================================================
st.set_page_config(page_title="VORTEZA | PROTOKÓŁ", layout="wide")
apply_vorteza_theme()

if "auth" not in st.session_state:
    st.session_state.auth = False

# --- LOGOWANIE ---
if not st.session_state.auth:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
        st.subheader("VORTEZA | LOGIN")
        u = st.text_input("Użytkownik")
        p = st.text_input("Hasło", type="password")
        if st.button("AUTORYZUJ"):
            if u in USER_DB and USER_DB[u] == p:
                st.session_state.auth = True
                st.session_state.username = u
                st.rerun()
            else:
                st.error("Odmowa dostępu.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- PANEL GŁÓWNY ---
else:
    c1, c2, c3 = st.columns([1, 4, 1])
    with c1:
        try:
            logo = Image.open('logo_vorteza.png')
            st.image(logo, width=150)
        except:
            st.title("VORTEZA")
    with c3:
        if st.button("WYLOGUJ"):
            st.session_state.auth = False
            st.rerun()

    # Pobieranie listy kontrolnej
    data = get_github_data()
    
    if data:
        with st.form("main_form"):
            # Sekcja 1: Dane
            st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
            st.subheader("Pojazd i Przebieg")
            r1, r2 = st.columns(2)
            rej = r1.text_input("Numer Rejestracyjny")
            km = r2.number_input("Aktualny Przebieg", step=1, value=0)
            st.markdown('</div>', unsafe_allow_html=True)

            # Sekcje pytań z JSON
            for kat, punkty in data["lista_kontrolna"].items():
                st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
                st.subheader(kat)
                # Dwie kolumny dla wygody
                cols = st.columns(2)
                for idx, p in enumerate(punkty):
                    with cols[idx % 2]:
                        st.checkbox(p, key=f"c_{p}")
                st.markdown('</div>', unsafe_allow_html=True)

            # Sekcja Uwagi
            st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
            st.subheader("Dodatkowe Uwagi")
            uwagi = st.text_area("Opisz usterki lub uwagi...")
            st.markdown('</div>', unsafe_allow_html=True)

            # Finał
            if st.form_submit_button("ZATWIERDŹ PROTOKÓŁ"):
                if not rej:
                    st.error("Brak numeru rejestracyjnego!")
                else:
                    st.success(f"Protokół dla {rej} gotowy!")
                    st.balloons()
    else:
        st.error("Błąd połączenia z bazą danych (GitHub).")
