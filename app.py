import streamlit as st
import json
import requests
import base64
from PIL import Image
from datetime import datetime

# =========================================================
# 1. KONFIGURACJA DOSTĘPU I SEKRETÓW
# =========================================================
# Dane logowania użytkowników
USER_DB = {
    "admin": "vorteza",
    "kierowca1": "CrystalBridge116"
}

# Bezpieczne pobieranie tokenu z Secrets (nie z kodu!)
try:
    GITHUB_TOKEN = st.secrets["G_TOKEN"]["G_TOKEN"]
except Exception:
    GITHUB_TOKEN = None

REPO_OWNER = "natpio"
REPO_NAME = "protoku-pojazdu"
FILE_PATH = "lista_kontrolna.json"

# =========================================================
# 2. FUNKCJE SYSTEMOWE (GITHUB & ASSETS)
# =========================================================
def get_base64_of_bin_file(bin_file):
    """Konwertuje obraz na base64 do wyświetlenia jako tło CSS."""
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

def get_github_data():
    """Pobiera checklistę JSON z Twojego repozytorium."""
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
# 3. STYLIZACJA VORTEZA (MAKSYMALNA CZYTELNOŚĆ)
# =========================================================
def apply_vorteza_theme():
    # Pobieranie tła z pliku bg_vorteza.png
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
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

            :root {
                --v-copper: #B58863;
                --v-panel: rgba(0, 0, 0, 0.88);
                --v-text: #FFFFFF;
            }

            .stApp {
                color: var(--v-text);
                font-family: 'Montserrat', sans-serif;
            }

            /* Ciemny panel pod tekstem dla kontrastu z tłem Carbon */
            .vorteza-section {
                background-color: var(--v-panel);
                padding: 30px;
                border-radius: 10px;
                border-left: 6px solid var(--v-copper);
                backdrop-filter: blur(12px);
                margin-bottom: 25px;
                box-shadow: 0 15px 40px rgba(0,0,0,0.9);
            }

            h1, h2, h3, .stSubheader {
                color: var(--v-copper) !important;
                font-weight: 700 !important;
                text-transform: uppercase;
                letter-spacing: 2px;
                text-shadow: 2px 2px 5px black;
            }

            /* Checkboxy - biały tekst i pogrubienie */
            .stCheckbox label {
                color: white !important;
                font-weight: 600 !important;
                font-size: 1.1rem !important;
                text-shadow: 1px 1px 2px black;
            }

            /* Etykiety pól */
            label[data-testid="stWidgetLabel"] {
                color: var(--v-copper) !important;
                font-weight: 700 !important;
                text-transform: uppercase;
                background: rgba(0,0,0,0.6);
                padding: 3px 10px;
                border-radius: 4px;
            }

            /* Inputy */
            input, div[data-baseweb="input"] > div {
                background-color: #000 !important;
                color: white !important;
                border: 1px solid var(--v-copper) !important;
            }

            /* Przycisk VORTEZA */
            .stButton > button {
                background-color: var(--v-copper) !important;
                color: black !important;
                font-weight: 800;
                border: none;
                padding: 18px;
                text-transform: uppercase;
                letter-spacing: 2px;
                width: 100%;
                transition: 0.3s ease;
            }
            .stButton > button:hover {
                box-shadow: 0 0 25px var(--v-copper);
                transform: translateY(-2px);
            }
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 4. LOGIKA APLIKACJI
# =========================================================
st.set_page_config(page_title="VORTEZA FLOW | PROTOKÓŁ", layout="wide")
apply_vorteza_theme()

if "auth" not in st.session_state:
    st.session_state.auth = False

# --- EKRAN LOGOWANIA ---
if not st.session_state.auth:
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
        st.subheader("VORTEZA | AUTORYZACJA")
        u = st.text_input("Użytkownik")
        p = st.text_input("Hasło", type="password")
        if st.button("ZALOGUJ DO SYSTEMU"):
            if u in USER_DB and USER_DB[u] == p:
                st.session_state.auth = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("BŁĄD: Nieprawidłowe dane logowania.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- EKRAN GŁÓWNY (PO LOGOWANIU) ---
else:
    c_l, c_m, c_r = st.columns([1, 4, 1])
    with c_l:
        try:
            logo = Image.open('logo_vorteza.png')
            st.image(logo, width=160)
        except:
            st.title("VORTEZA")
    with c_r:
        if st.button("WYLOGUJ"):
            st.session_state.auth = False
            st.rerun()

    # Próba pobrania checklisty
    config = get_github_data()
    
    if config:
        with st.form("protocol_form"):
            # Sekcja 1: Dane pojazdu
            st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
            st.subheader("1. Dane techniczne")
            c1, c2, c3 = st.columns(3)
            with c1: nr_rej = st.text_input("Numer Rejestracyjny")
            with c2: mileage = st.number_input("Stan Licznika (KM)", step=1)
            with c3: st.text_input("Kierowca", value=st.session_state.user, disabled=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Sekcje z JSON
            for kategoria, punkty in config["lista_kontrolna"].items():
                st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
                st.subheader(kategoria)
                cols = st.columns(2)
                for idx, punkt in enumerate(punkty):
                    with cols[idx % 2]:
                        st.checkbox(punkt, key=f"p_{punkt}")
                st.markdown('</div>', unsafe_allow_html=True)

            # Sekcja Uwagi
            st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
            st.subheader("Uwagi dodatkowe")
            uwagi = st.text_area("Opis ewentualnych uszkodzeń lub braków")
            st.markdown('</div>', unsafe_allow_html=True)

            # Przycisk wysyłki
            if st.form_submit_button("ZATWIERDŹ I WYŚLIJ PROTOKÓŁ"):
                if not nr_rej:
                    st.error("Proszę wpisać numer rejestracyjny!")
                else:
                    st.success(f"Protokół dla pojazdu {nr_rej} został pomyślnie wysłany!")
                    st.balloons()
    else:
        st.error("BŁĄD: System nie może połączyć się z bazą pytań na GitHub. Sprawdź TOKEN w Secrets.")
