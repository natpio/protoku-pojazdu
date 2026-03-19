import streamlit as st
import json
import requests
import base64
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials

# =========================================================
# 1. KONFIGURACJA ZASOBÓW (GITHUB & GOOGLE SHEETS)
# =========================================================
try:
    GITHUB_TOKEN = st.secrets["G_TOKEN"]["G_TOKEN"]
except:
    GITHUB_TOKEN = None 

# Dane repozytorium GitHub
REPO_OWNER = "natpio"
REPO_NAME = "protoku-pojazdu"
FILE_PATH = "lista_kontrolna.json"

# ID Twojego arkusza Google (wyciągnięte z Twojego linku)
SHEET_ID = "1UDehrxN8_j1CCrpq9FcXSory7FMA0LSdSk8PCIxIvPQ"

def get_remote_data():
    """Pobiera listę kontrolną i dane użytkowników z GitHub."""
    if not GITHUB_TOKEN: 
        return None, None
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            content = res.json()
            data = json.loads(base64.b64decode(content['content']).decode('utf-8'))
            return data, content['sha']
    except: 
        pass
    return None, None

def get_gspread_client():
    """Autoryzacja w Google Sheets przy użyciu konta serwisowego."""
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_info = st.secrets["GCP_SERVICE_ACCOUNT"]
    credentials = Credentials.from_service_account_info(creds_info, scopes=scope)
    return gspread.authorize(credentials)

def save_to_google_sheets(row_data):
    """Zapisuje jeden wiersz danych do arkusza Google."""
    try:
        client = get_gspread_client()
        sheet = client.open_by_key(SHEET_ID).sheet1
        sheet.append_row(row_data)
        return True
    except Exception as e:
        st.error(f"Błąd zapisu do Google Sheets: {e}")
        return False

# =========================================================
# 2. DESIGN VORTEZA 8.0 - INTERFEJS I STYLE
# =========================================================
def apply_vorteza_design():
    try:
        with open('bg_vorteza.png', 'rb') as f:
            bg_base64 = base64.b64encode(f.read()).decode()
    except: 
        bg_base64 = ""
    
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Michroma&family=Montserrat:wght@400;600&display=swap');
        
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("data:image/png;base64,{bg_base64}");
            background-size: cover; background-attachment: fixed;
        }}

        .logo-font {{
            font-family: 'Michroma', sans-serif !important;
            color: #B58863 !important;
            text-align: center; font-size: 1.5rem !important;
            letter-spacing: 5px !important; text-transform: uppercase;
            margin-bottom: 25px;
        }}

        /* Fix dla ikon expandera */
        div[data-testid="stExpander"] svg {{
            display: none !important;
        }}
        
        div[data-testid="stExpander"] summary span {{
            color: transparent !important;
            font-size: 0px !important;
        }}

        .streamlit-expanderHeader {{
            background-color: rgba(181, 136, 99, 0.1) !important;
            border: 1px solid rgba(181, 136, 99, 0.3) !important;
            border-left: 5px solid #B58863 !important;
            border-radius: 4px !important;
            padding: 12px !important;
        }}

        div[data-testid="stExpander"] p {{
            font-family: 'Michroma', sans-serif !important;
            color: #B58863 !important;
            font-size: 0.8rem !important;
            letter-spacing: 2px !important;
            visibility: visible !important;
            display: block !important;
            margin: 0 !important;
        }}

        .vorteza-card {{
            background: rgba(20, 20, 20, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 4px; padding: 20px; margin-bottom: 15px;
        }}

        .stButton > button {{
            background: #B58863 !important;
            color: white !important; font-family: 'Michroma', sans-serif !important;
            width: 100%; border-radius: 2px !important;
            border: none !important; padding: 18px !important;
            letter-spacing: 2px;
        }}

        label, p, span {{ font-family: 'Montserrat', sans-serif !important; color: #FFFFFF !important; }}
        
        #MainMenu, footer, header {{visibility: hidden;}}
        .stDeployButton {{display:none;}}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. LOGIKA GŁÓWNA APLIKACJI
# =========================================================
st.set_page_config(page_title="VORTEZA-BASE", layout="centered")
apply_vorteza_design()

# Pobranie danych startowych
data, current_sha = get_remote_data()
if not data: 
    data = {"uzytkownicy": {"admin": "vorteza"}, "lista_kontrolna": {}}

# Zarządzanie sesją (logowanie)
if "auth" not in st.session_state: 
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<br><br><div class='vorteza-card' style='text-align:center;'><p class='logo-font'>SYSTEM ACCESS</p></div>", unsafe_allow_html=True)
    u = st.text_input("OPERATOR ID")
    p = st.text_input("SECURITY KEY", type="password")
    if st.button("AUTHORIZE"):
        if u in data.get("uzytkownicy", {}) and data["uzytkownicy"][u] == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
else:
    # Ekran po zalogowaniu
    try: 
        st.image('logo_vorteza.png', width=180)
    except: 
        pass
    st.markdown('<p class="logo-font">VORTEZA - BASE</p>', unsafe_allow_html=True)
    
    with st.form("main_form"):
        # Dane pojazdu
        st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
        rej = st.text_input("LICENSE PLATE (NUMERY REJESTRACYJNE)")
        km = st.number_input("MILEAGE (PRZEBIEG KM)", step=1, value=0)
        st.markdown('</div>', unsafe_allow_html=True)

        # Dynamiczne sekcje kontrolne
        wyniki_kontroli = {}
        if "lista_kontrolna" in data:
            for kat, punkty in data["lista_kontrolna"].items():
                with st.expander(f"► {kat.upper()}"):
                    for pt in punkty:
                        # Klucz musi być unikalny dla każdego checkboxa
                        stan = st.checkbox(pt, key=f"chk_{kat}_{pt}")
                        wyniki_kontroli[pt] = "OK" if stan else "BRAK/NIE"

        st.markdown('<br>', unsafe_allow_html=True)
        with st.expander("► OBSERVATIONS & NOTES (UWAGI)"):
            obs = st.text_area("Wpisz dodatkowe informacje...", height=100)

        st.markdown('<br>', unsafe_allow_html=True)
        if st.form_submit_button("GENERATE AND ENCRYPT PROTOCOL"):
            if not rej:
                st.error("Plate required! (Wymagana rejestracja)")
            else:
                # Przygotowanie danych do wysyłki
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Zbieramy tylko usterki (to co nie zostało zaznaczone)
                usterki = [k for k, v in wyniki_kontroli.items() if v == "BRAK/NIE"]
                wynik_finalny = "Wszystko sprawne" if not usterki else f"USTERKI: {', '.join(usterki)}"
                
                # Układ kolumn: Data, Operator, Rejestracja, Przebieg, Usterki, Uwagi
                row_to_save = [timestamp, st.session_state.user, rej, km, wynik_finalny, obs]
                
                with st.spinner("TRANSMITTING TO GOOGLE SHEETS..."):
                    if save_to_google_sheets(row_to_save):
                        st.success("PROTOCOL TRANSMITTED AND SAVED")
                        st.balloons()
                    else:
                        st.error("TRANSMISSION FAILED. CHECK LOGS.")
