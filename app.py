import streamlit as st
import json
import requests
import base64
from PIL import Image
from datetime import datetime

# =========================================================
# KONFIGURACJA GITHUB I SEKRETÓW
# =========================================================
# Pobieranie danych z Streamlit Cloud Secrets
try:
    # Twoja struktura: [G_TOKEN] -> G_TOKEN = "..."
    GITHUB_TOKEN = st.secrets["G_TOKEN"]["G_TOKEN"]
    # Twoja struktura: [credentials.usernames] -> admin = "..."
    USER_DB = st.secrets["credentials"]["usernames"]
except Exception as e:
    st.warning("⚠️ Brak konfiguracji Secrets. Używam trybu demo.")
    GITHUB_TOKEN = "BRAK"
    USER_DB = {"admin": "vorteza"} 

REPO_OWNER = "natpio"
REPO_NAME = "protoku-pojazdu"
FILE_PATH = "lista_kontrolna.json"

# =========================================================
# FUNKCJE POMOCNICZE (GITHUB & ASSETS)
# =========================================================
def get_base64_of_bin_file(bin_file):
    """Konwertuje obraz na base64, aby użyć go jako tło CSS."""
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

def get_github_data():
    """Pobiera plik JSON z checklistą z Twojego repozytorium."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            decoded = base64.b64decode(content['content']).decode('utf-8')
            return json.loads(decoded)
        else:
            st.error(f"❌ Błąd GitHub API: {response.status_code}. Sprawdź Token w Secrets.")
            return None
    except Exception as e:
        st.error(f"❌ Błąd połączenia: {e}")
        return None

# =========================================================
# STYLIZACJA VORTEZA FLOW (SQM STYLE)
# =========================================================
def apply_vorteza_theme():
    # Tło aplikacji
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
    else:
        st.markdown("<style>.stApp { background-color: #0E0E0E; }</style>", unsafe_allow_html=True)

    # Stylizacja interfejsu (Czcionki, Kolory, Panele)
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&display=swap');

            :root {
                --v-copper: #B58863;
                --v-panel: rgba(20, 20, 20, 0.9);
                --v-text: #E0E0E0;
            }

            .stApp {
                color: var(--v-text);
                font-family: 'Montserrat', sans-serif;
            }

            h1, h2, h3, .stSubheader {
                color: var(--v-copper) !important;
                font-weight: 700 !important;
                text-transform: uppercase;
                letter-spacing: 2px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }

            /* Styl kontenerów (sekcji) */
            .vorteza-section {
                background-color: var(--v-panel);
                padding: 25px;
                border-radius: 5px;
                border-left: 5px solid var(--v-copper);
                box-shadow: 0 10px 40px rgba(0,0,0,0.8);
                backdrop-filter: blur(15px);
                margin-bottom: 25px;
            }

            /* Styl przycisków */
            .stButton > button {
                background-color: rgba(0, 0, 0, 0.7);
                color: var(--v-copper);
                border: 1px solid var(--v-copper);
                padding: 15px;
                width: 100%;
                font-weight: 700;
                text-transform: uppercase;
                transition: 0.3s;
            }
            .stButton > button:hover {
                background-color: var(--v-copper);
                color: black;
            }

            /* Checkboxy i Inputy */
            input, div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
                background-color: rgba(15, 15, 15, 0.9) !important;
                color: white !important;
                border: 1px solid #444 !important;
            }
            
            label[data-testid="stWidgetLabel"] {
                color: var(--v-copper) !important;
                font-weight: 700 !important;
                text-transform: uppercase;
            }
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# LOGIKA LOGOWANIA
# =========================================================
def check_password():
    if "auth" not in st.session_state:
        st.session_state.auth = False

    if not st.session_state.auth:
        _, col2, _ = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
            st.subheader("VORTEZA | SECURE ACCESS")
            u = st.text_input("Użytkownik")
            p = st.text_input("Hasło", type="password")
            if st.button("AUTORYZUJ"):
                if u in USER_DB and USER_DB[u] == p:
                    st.session_state.auth = True
                    st.session_state.username = u
                    st.rerun()
                else:
                    st.error("Nieprawidłowe dane logowania.")
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

# =========================================================
# GŁÓWNA APLIKACJA
# =========================================================
st.set_page_config(page_title="VORTEZA FLOW | PROTOKÓŁ", layout="wide")
apply_vorteza_theme()

if check_password():
    # --- Nagłówek ---
    col_logo, col_title, col_logout = st.columns([1, 4, 1])
    with col_logo:
        try:
            logo = Image.open('logo_vorteza.png')
            st.image(logo, use_container_width=True)
        except:
            st.title("VORTEZA")

    with col_title:
        st.markdown("<br>", unsafe_allow_html=True)
        st.title("Protokół Przekazania Pojazdu")
    
    with col_logout:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("WYLOGUJ"):
            st.session_state.auth = False
            st.rerun()

    # --- Pobieranie Checklisty ---
    config = get_github_data()

    if config:
        with st.form("formularz_protokolu"):
            # 1. Dane podstawowe
            st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
            st.subheader("Informacje o pojeździe")
            c1, c2, c3 = st.columns(3)
            with c1:
                nr_rej = st.text_input("Numer Rejestracyjny")
            with c2:
                kierowca = st.text_input("Kierowca", value=st.session_state.username)
            with c3:
                mileage = st.number_input("Przebieg (KM)", step=1)
            st.markdown('</div>', unsafe_allow_html=True)

            # 2. Dynamiczne sekcje z JSON
            for kategoria, punkty in config["lista_kontrolna"].items():
                st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
                st.subheader(kategoria)
                cols = st.columns(2)
                for i, punkt in enumerate(punkty):
                    with cols[i % 2]:
                        st.checkbox(punkt, key=punkt)
                st.markdown('</div>', unsafe_allow_html=True)

            # 3. Uwagi końcowe
            st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
            st.subheader("Uwagi i Stan Systemu")
            uwagi = st.text_area("Opisz ewentualne usterki...")
            st.markdown('</div>', unsafe_allow_html=True)

            # Przycisk wysyłki
            if st.form_submit_button("ZATWIERDŹ I WYŚLIJ PROTOKÓŁ"):
                # Tutaj w przyszłości dodamy logikę zapisu do bazy SQL
                st.success("PROTOKÓŁ ZOSTAŁ POMYŚLNIE ZAPISANY W SYSTEMIE VORTEZA.")
    else:
        st.error("Błąd krytyczny: Nie udało się pobrać konfiguracji protokołu.")
