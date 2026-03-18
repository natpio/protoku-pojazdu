import streamlit as st
import json
import requests
import base64
from PIL import Image
from datetime import datetime

# =========================================================
# 1. KONFIGURACJA I DOSTĘP
# =========================================================
# Dane logowania użytkowników
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
# 2. FUNKCJE TECHNICZNE
# =========================================================
def get_base64_of_bin_file(bin_file):
    """Konwertuje grafikę na kod, aby użyć jej jako tła."""
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

def get_github_data():
    """Pobiera dane z pliku JSON na Twoim GitHubie."""
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
# 3. DESIGN PREMIUM (MODERN CARBON & COPPER)
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
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;800&display=swap');

            :root {
                --copper: #B58863;
                --dark-glass: rgba(10, 10, 10, 0.85);
            }

            /* Globalne ustawienia czcionki */
            .stApp, p, label, div, span {
                font-family: 'Montserrat', sans-serif !important;
                color: #FFFFFF !important;
            }

            /* PANELE - Nowoczesny Glassmorphism */
            .vorteza-section {
                background: linear-gradient(145deg, rgba(20,20,20,0.95) 0%, rgba(5,5,5,0.8) 100%);
                padding: 30px;
                border-radius: 15px;
                border: 1px solid rgba(181, 136, 99, 0.3);
                box-shadow: 0 10px 30px rgba(0,0,0,0.8), inset 0 0 15px rgba(181, 136, 99, 0.05);
                margin-bottom: 25px;
                backdrop-filter: blur(10px);
            }

            /* NAGŁÓWKI - Elegancka Miedź */
            h1, h2, h3, .stSubheader {
                color: var(--copper) !important;
                font-weight: 800 !important;
                text-transform: uppercase;
                letter-spacing: 3px;
                margin-bottom: 20px !important;
                border-bottom: 2px solid var(--copper);
                display: inline-block;
                padding-bottom: 5px;
            }

            /* CHECKBOXY - Stylizacja Premium */
            .stCheckbox label {
                transition: 0.3s;
                padding: 8px 12px;
                border-radius: 8px;
            }
            .stCheckbox label:hover {
                background: rgba(181, 136, 99, 0.1);
            }
            .stCheckbox label p {
                font-weight: 400 !important;
                font-size: 1.05rem !important;
                text-shadow: 1px 1px 4px rgba(0,0,0,0.8);
            }

            /* INPUTY - Ciemne i minimalistyczne */
            input, textarea, div[data-baseweb="input"] > div {
                background-color: rgba(0,0,0,0.6) !important;
                border: 1px solid rgba(181, 136, 99, 0.3) !important;
                color: white !important;
                border-radius: 8px !important;
            }
            input:focus {
                border-color: var(--copper) !important;
                box-shadow: 0 0 10px rgba(181, 136, 99, 0.4) !important;
            }

            /* PRZYCISK - VORTEZA SIGNATURE */
            .stButton > button {
                background: linear-gradient(90deg, #8B6B4F 0%, #B58863 50%, #8B6B4F 100%);
                color: white !important;
                font-weight: 700 !important;
                border: None !important;
                padding: 15px 30px !important;
                text-transform: uppercase;
                letter-spacing: 2px;
                border-radius: 50px !important;
                box-shadow: 0 5px 15px rgba(0,0,0,0.4);
                transition: 0.4s ease;
            }
            .stButton > button:hover {
                transform: scale(1.02);
                box-shadow: 0 8px 25px rgba(181, 136, 99, 0.5);
                filter: brightness(1.1);
            }

            div[data-testid="stForm"] {
                border: none !important;
                padding: 0 !important;
            }
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 4. GŁÓWNA LOGIKA APLIKACJI
# =========================================================
st.set_page_config(page_title="VORTEZA FLOW", layout="wide")
apply_vorteza_theme()

if "auth" not in st.session_state:
    st.session_state.auth = False

# --- EKRAN LOGOWANIA ---
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown('<div class="vorteza-section" style="text-align:center;">', unsafe_allow_html=True)
        st.subheader("SYSTEM LOGIN")
        u = st.text_input("Użytkownik")
        p = st.text_input("Hasło", type="password")
        if st.button("AUTORYZUJ"):
            if u in USER_DB and USER_DB[u] == p:
                st.session_state.auth = True
                st.session_state.username = u
                st.rerun()
            else:
                st.error("Dostęp zabroniony. Nieprawidłowe dane.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- PANEL GŁÓWNY PO LOGOWANIU ---
else:
    c1, c2, c3 = st.columns([1, 3, 1])
    with c1:
        try: st.image('logo_vorteza.png', width=140)
        except: st.title("VORTEZA")
    with c3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("WYLOGUJ"):
            st.session_state.auth = False
            st.rerun()

    config = get_github_data()
    
    if config:
        with st.form("main_form"):
            # Sekcja 1: Dane pojazdu
            st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
            st.subheader("DANE POJAZDU")
            col_a, col_b = st.columns(2)
            rej = col_a.text_input("NUMER REJESTRACYJNY")
            km = col_b.number_input("AKTUALNY PRZEBIEG", step=1, value=0)
            st.markdown('</div>', unsafe_allow_html=True)

            # Sekcje pytań generowane z pliku JSON
            for kat, punkty in config["lista_kontrolna"].items():
                st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
                st.subheader(kat)
                cols = st.columns(2)
                for idx, p_text in enumerate(punkty):
                    with cols[idx % 2]:
                        st.checkbox(p_text, key=f"chk_{p_text}")
                st.markdown('</div>', unsafe_allow_html=True)

            # Sekcja Uwagi
            st.markdown('<div class="vorteza-section">', unsafe_allow_html=True)
            st.subheader("UWAGI KOŃCOWE")
            uwagi = st.text_area("Uwagi do stanu technicznego / opis uszkodzeń...")
            st.markdown('</div>', unsafe_allow_html=True)

            # Przycisk wysyłki
            st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
            if st.form_submit_button("ZATWIERDŹ I WYŚLIJ PROTOKÓŁ"):
                if not rej:
                    st.error("BŁĄD: Podaj numer rejestracyjny!")
                else:
                    st.success(f"PROTOKÓŁ DLA POJAZDU {rej} ZOSTAŁ PRZESŁANY!")
                    st.balloons()
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("BŁĄD: Brak połączenia z bazą GitHub. Sprawdź TOKEN w Secrets.")
