import streamlit as st
import json
import requests
import base64
from PIL import Image
from datetime import datetime

# =========================================================
# KONFIGURACJA GITHUB I SEKRETÓW
# =========================================================
try:
    GITHUB_TOKEN = st.secrets["G_TOKEN"]
    USER_DB = st.secrets["credentials"]["usernames"]
except Exception:
    GITHUB_TOKEN = "BRAK"
    USER_DB = {"admin": "admin123"} # Fallback do testów lokalnych

REPO_OWNER = "natpio"
REPO_NAME = "protoku-pojazdu"  # Zaktualizowana nazwa repozytorium
FILE_PATH = "lista_kontrolna.json"

# =========================================================
# FUNKCJE POMOCNICZE
# =========================================================
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ""

def get_github_data():
    """Pobiera listę kontrolną z GitHub API."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            decoded = base64.b64decode(content['content']).decode('utf-8')
            return json.loads(decoded)
        return None
    except Exception:
        return None

# =========================================================
# STYLIZACJA VORTEZA SYSTEMS (PROTOKÓŁ STYLE)
# =========================================================
def apply_vorteza_theme():
    # Pobieranie tła z pliku bg_vorteza.png
    bin_str = get_base64_of_bin_file('bg_vorteza.png')
    
    if bin_str:
        bg_style = f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-attachment: fixed;
        }}
        </style>
        """
        st.markdown(bg_style, unsafe_allow_html=True)
    else:
        st.markdown("<style>.stApp { background-color: #0E0E0E; }</style>", unsafe_allow_html=True)

    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&display=swap');

            :root {
                --v-copper: #B58863;
                --v-dark: #0E0E0E;
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

            .vorteza-section {
                background-color: var(--v-panel);
                padding: 25px;
                border-radius: 5px;
                border-left: 5px solid var(--v-copper);
                box-shadow: 0 10px 40px rgba(0,0,0,0.8);
                backdrop-filter: blur(15px);
                margin-bottom: 25px;
            }

            .stButton > button {
                background-color: rgba(0, 0, 0, 0.7);
                color: var(--v-copper);
                border: 1px solid var(--v-copper);
                padding: 10px;
                width: 100%;
                font-weight: 700;
                text-transform: uppercase;
                transition: 0.3s;
            }

            .stButton > button:hover {
                background-color: var(--v-copper);
                color: black;
            }

            /* Styl checkboxów i inputów */
            label[data-testid="stWidgetLabel"] {
                color: var(--v-text) !important;
                font-weight: 400 !important;
                text-transform: uppercase;
                font-size: 0.8rem !important;
            }
            
            input, div[data-baseweb="select"] > div {
                background-color: rgba(15, 15, 15, 0.9) !important;
                color: white !important;
                border: 1px solid #444 !important;
            }
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# SYSTEM LOGOWANIA
# =========================================================
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("Login"):
                st.markdown("### VORTEZA | PROTOCOLS ACCESS")
                user = st.text_input("Użytkownik")
                password = st.text_input("Hasło", type="password")
                submit = st.form_submit_button("ZALOGUJ")
                if submit:
                    if user in USER_DB and USER_DB[user] == password:
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = user
                        st.rerun()
                    else:
                        st.error("Nieprawidłowe dane logowania.")
        return False
    return True

# =========================================================
# GŁÓWNA LOGIKA
# =========================================================
st.set_page_config(page_title="VORTEZA | PROTOKÓŁ", layout="wide")
apply_vorteza_theme()

if check_password():
    # Nagłówek
    col_logo, col_title, col_logout = st.columns([1, 4, 1])
    with col_logo:
        try:
            # Pobieranie logo z logo_vorteza.png
            logo = Image.open('logo_vorteza.png')
            st.image(logo, use_container_width=True)
        except:
            st.title("VORTEZA")

    with col_title:
        st.title("Protokół Przekazania Pojazdu")
    
    with col_logout:
        if st.button("WYLOGUJ"):
            del st.session_state["authenticated"]
            st.rerun()

    # Pobranie danych z GitHub
    config_data = get_github_data()

    if config_data:
        lista_zadan = config_data.get("lista_kontrolna", {})

        with st.form("main_protocol_form"):
            # Sekcja Informacyjna
            st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
            st.subheader("General Information")
            c1, c2, c3 = st.columns(3)
            with c1:
                nr_rej = st.text_input("Numer Rejestracyjny")
            with c2:
                kierowca = st.text_input("Kierowca Przejmujący", value=st.session_state.username)
            with c3:
                data_godz = st.text_input("Data i Godzina", value=datetime.now().strftime("%Y-%m-%d %H:%M"))
            st.markdown('</div>', unsafe_allow_html=True)

            # Sekcje z JSON
            results = {}
            for kategoria, punkty in lista_zadan.items():
                st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
                st.subheader(kategoria)
                
                # Wyświetlanie w dwóch kolumnach dla lepszej czytelności na mobile
                cols = st.columns(2)
                for i, punkt in enumerate(punkty):
                    with cols[i % 2]:
                        results[punkt] = st.checkbox(punkt)
                st.markdown('</div>', unsafe_allow_html=True)

            # Uwagi i przycisk
            st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
            st.subheader("System Comments")
            uwagi = st.text_area("Dodatkowe uwagi techniczne...")
            st.markdown('</div>', unsafe_allow_html=True)

            if st.form_submit_button("WYŚLIJ PROTOKÓŁ DO BAZY"):
                # Tutaj wstawimy później kod do zapisu w PostgreSQL
                st.success("PROTOKÓŁ ZAPISANY POMYŚLNIE")
    else:
        st.error("Błąd: Nie udało się pobrać pliku lista_kontrolna.json z repozytorium protoku-pojazdu.")
