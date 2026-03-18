import streamlit as st
import json
import requests
import base64
from PIL import Image
from datetime import datetime

# =========================================================
# 1. KONFIGURACJA DOSTĘPU I UŻYTKOWNIKÓW
# =========================================================
# Dane logowania wpisane bezpośrednio w kod (skoro Secrets sprawiały problem)
USER_DB = {
    "admin": "vorteza",
    "kierowca1": "CrystalBridge116"
}

# Próba pobrania TOKENU z Secrets - upewnij się, że w Secrets masz:
# [G_TOKEN]
# G_TOKEN = "ghp_..."
try:
    GITHUB_TOKEN = st.secrets["G_TOKEN"]["G_TOKEN"]
except Exception:
    GITHUB_TOKEN = "BRAK_TOKENU"

REPO_OWNER = "natpio"
REPO_NAME = "protoku-pojazdu"
FILE_PATH = "lista_kontrolna.json"

# =========================================================
# 2. FUNKCJE SYSTEMOWE (GITHUB & ASSETS)
# =========================================================
def get_base64_of_bin_file(bin_file):
    """Konwertuje plik graficzny na format base64 dla CSS."""
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

def get_github_data():
    """Pobiera plik JSON z checklistą bezpośrednio z GitHub API."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            decoded = base64.b64decode(content['content']).decode('utf-8')
            return json.loads(decoded)
        else:
            return None
    except:
        return None

# =========================================================
# 3. STYLIZACJA VORTEZA SYSTEMS (Pełny Design)
# =========================================================
def apply_vorteza_theme():
    # Tło z pliku bg_vorteza.png
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

    # Stylizacja elementów UI
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&display=swap');

            :root {
                --v-copper: #B58863;
                --v-panel: rgba(15, 15, 15, 0.92);
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
                padding: 30px;
                border-radius: 4px;
                border-left: 5px solid var(--v-copper);
                box-shadow: 0 10px 40px rgba(0,0,0,0.7);
                backdrop-filter: blur(15px);
                margin-bottom: 25px;
            }

            .stButton > button {
                background-color: rgba(0, 0, 0, 0.5);
                color: var(--v-copper);
                border: 1px solid var(--v-copper);
                padding: 15px;
                width: 100%;
                font-weight: 700;
                text-transform: uppercase;
                transition: 0.3s ease;
            }

            .stButton > button:hover {
                background-color: var(--v-copper);
                color: black;
                box-shadow: 0 0 15px var(--v-copper);
            }

            /* Styl inputów i selectboxów */
            input, div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
                background-color: #000 !important;
                color: white !important;
                border: 1px solid #333 !important;
            }

            label[data-testid="stWidgetLabel"] {
                color: var(--v-copper) !important;
                font-weight: 700 !important;
                text-transform: uppercase;
                font-size: 0.85rem !important;
            }

            /* Custom checkbox style */
            .stCheckbox > label {
                color: #FFF !important;
            }
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 4. LOGIKA LOGOWANIA
# =========================================================
def check_password():
    if "auth" not in st.session_state:
        st.session_state.auth = False

    if not st.session_state.auth:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
            st.subheader("VORTEZA | SECURE ACCESS")
            u = st.text_input("Użytkownik")
            p = st.text_input("Hasło", type="password")
            if st.button("AUTORYZUJ WEJŚCIE"):
                if u in USER_DB and USER_DB[u] == p:
                    st.session_state.auth = True
                    st.session_state.username = u
                    st.rerun()
                else:
                    st.error("ODMOWA DOSTĘPU: Nieprawidłowe dane.")
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

# =========================================================
# 5. GŁÓWNA LOGIKA APLIKACJI (Główny ekran)
# =========================================================
st.set_page_config(page_title="VORTEZA | SYSTEM PROTOKOŁÓW", layout="wide")
apply_vorteza_theme()

if check_password():
    # --- Nagłówek i Nawigacja ---
    col_logo, col_title, col_logout = st.columns([1, 4, 1])
    with col_logo:
        try:
            logo = Image.open('logo_vorteza.png')
            st.image(logo, use_container_width=True)
        except:
            st.title("VORTEZA")

    with col_title:
        st.markdown("<br>", unsafe_allow_html=True)
        st.title("VORTEZA FLOW | Protokół Pojazdu")
    
    with col_logout:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("WYLOGUJ"):
            st.session_state.auth = False
            st.rerun()

    # --- Pobieranie Danych z GitHub ---
    config = get_github_data()

    if config:
        with st.form("main_protocol_form"):
            # 1. Dane Operacyjne
            st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
            st.subheader("1. Identyfikacja i Przebieg")
            c1, c2, c3 = st.columns(3)
            with c1:
                nr_rej = st.text_input("Numer Rejestracyjny")
            with c2:
                kierowca = st.text_input("Kierowca Przejmujący", value=st.session_state.username)
            with c3:
                mileage = st.number_input("Aktualny Przebieg (KM)", value=0, step=1)
            st.markdown('</div>', unsafe_allow_html=True)

            # 2. Dynamiczne Generowanie Checklisty z JSON
            for kategoria, punkty in config["lista_kontrolna"].items():
                st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
                st.subheader(kategoria)
                
                # Wyświetlanie punktów w 2 kolumnach dla lepszej czytelności
                cols = st.columns(2)
                for idx, punkt in enumerate(punkty):
                    with cols[idx % 2]:
                        st.checkbox(punkt, key=f"chk_{punkt}")
                st.markdown('</div>', unsafe_allow_html=True)

            # 3. Uwagi i Zdjęcia (Opcjonalne)
            st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
            st.subheader("3. Uwagi Techniczne")
            st.text_area("Opisz zauważone uszkodzenia lub uwagi do stanu technicznego...", height=150)
            st.file_uploader("Dodaj zdjęcia (opcjonalnie)", accept_multiple_files=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # 4. Zatwierdzenie
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("ZATWIERDŹ I WYŚLIJ PROTOKÓŁ")
            
            if submit:
                # Tu w przyszłości podepniemy bazę PostgreSQL
                st.success(f"PROTOKÓŁ DLA POJAZDU {nr_rej} ZOSTAŁ WYGENEROWANY I PRZESŁANY DO SYSTEMU.")
                st.balloons()
    else:
        st.error("BŁĄD SYSTEMU: Nie można pobrać listy kontrolnej z GitHub. Sprawdź TOKEN w Secrets.")
