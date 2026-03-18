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

# Bezpieczne pobieranie tokenu z Secrets (G_TOKEN -> G_TOKEN)
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
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;800&display=swap');

            :root {
                --v-copper: #B58863;
                --v-text: #FFFFFF;
                --v-panel: rgba(0, 0, 0, 0.9); /* Bardzo ciemny panel pod tekstem */
            }

            /* Globalny kolor tekstu - wymuszamy czystą biel i Montserrat */
            .stApp, p, div, span, label {
                color: var(--v-text) !important;
                font-family: 'Montserrat', sans-serif !important;
            }

            /* Panel sekcji - silny kontrast dla czytelności */
            .vorteza-section {
                background-color: var(--v-panel);
                padding: 30px;
                border-radius: 12px;
                border: 1px solid rgba(181, 136, 99, 0.4);
                border-left: 8px solid var(--v-copper);
                backdrop-filter: blur(15px);
                margin-bottom: 25px;
                box-shadow: 0 15px 45px rgba(0,0,0,0.9);
            }

            /* Nagłówki sekcji (Miedź) */
            h1, h2, h3, .stSubheader {
                color: var(--v-copper) !important;
                font-weight: 800 !important;
                text-transform: uppercase;
                letter-spacing: 2.5px;
                text-shadow: 3px 3px 6px rgba(0,0,0,1) !important;
                margin-bottom: 20px !important;
            }

            /* Checkboxy - biały, bardzo wyraźny tekst */
            .stCheckbox label p {
                color: #FFFFFF !important;
                font-weight: 700 !important;
                font-size: 1.15rem !important;
                text-shadow: 2px 2px 4px rgba(0,0,0,1) !important;
            }

            /* Pola wpisywania - etykiety */
            label[data-testid="stWidgetLabel"] p {
                color: var(--v-copper) !important;
                font-weight: 800 !important;
                text-transform: uppercase;
                font-size: 0.9rem !important;
                background: rgba(0,0,0,0.7);
                padding: 2px 10px;
                border-radius: 4px;
                display: inline-block;
            }

            /* Inputy (Tło czarne, obramowanie miedziane) */
            input, div[data-baseweb="input"] > div, textarea {
                background-color: #000000 !important;
                color: #FFFFFF !important;
                border: 1px solid var(--v-copper) !important;
                font-weight: 600 !important;
            }

            /* Przycisk VORTEZA */
            .stButton > button {
                background-color: var(--v-copper) !important;
                color: #000000 !important;
                font-weight: 800 !important;
                border: none !important;
                padding: 18px !important;
                text-transform: uppercase;
                letter-spacing: 2px;
                width: 100%;
                border-radius: 6px !important;
                transition: 0.3s ease;
            }
            .stButton > button:hover {
                box-shadow: 0 0 30px var(--v-copper);
                transform: translateY(-3px);
            }
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 4. GŁÓWNA LOGIKA APLIKACJI
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
            st.image(logo, width=180)
        except:
            st.title("VORTEZA")
    with c_r:
        st.write("") # Spacer
        if st.button("WYLOGUJ SYSTEM"):
            st.session_state.auth = False
            st.rerun()

    # Próba pobrania checklisty z GitHub
    config = get_github_data()
    
    if config:
        with st.form("protocol_form"):
            # Sekcja 1: Dane pojazdu
            st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
            st.subheader("1. IDENTYFIKACJA OPERACYJNA")
            c1, c2, c3 = st.columns(3)
            with c1: nr_rej = st.text_input("Numer Rejestracyjny")
            with c2: mileage = st.number_input("Stan Licznika (KM)", step=1, value=0)
            with c3: st.text_input("Kierowca", value=st.session_state.user, disabled=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Sekcje dynamiczne z pliku JSON
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
            st.subheader("UWAGI I STAN TECHNICZNY")
            uwagi = st.text_area("Opisz ewentualne usterki, braki lub uwagi do pojazdu...")
            st.markdown('</div>', unsafe_allow_html=True)

            # Przycisk wysyłki
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("ZATWIERDŹ I WYŚLIJ PROTOKÓŁ DO BAZY"):
                if not nr_rej:
                    st.error("BŁĄD: Podaj numer rejestracyjny pojazdu!")
                else:
                    st.success(f"PROTOKÓŁ DLA {nr_rej} ZOSTAŁ POMYŚLNIE WYGENEROWANY!")
                    st.balloons()
    else:
        st.error("BŁĄD KRYTYCZNY: Brak połączenia z GitHub (Sprawdź Token w Secrets).")
