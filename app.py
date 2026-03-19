import streamlit as st
import json
import requests
import base64
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials

# =========================================================
# 1. KONFIGURACJA ZASOBÓW
# =========================================================
try:
    GITHUB_TOKEN = st.secrets["G_TOKEN"]["G_TOKEN"]
except:
    GITHUB_TOKEN = None 

REPO_OWNER = "natpio"
REPO_NAME = "protoku-pojazdu"
FILE_PATH = "lista_kontrolna.json"
SHEET_ID = "1UDehrxN8_j1CCrpq9FcXSory7FMA0LSdSk8PCIxIvPQ"

def get_remote_data():
    if not GITHUB_TOKEN: return None, None
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            content = res.json()
            data = json.loads(base64.b64decode(content['content']).decode('utf-8'))
            return data, content['sha']
    except: pass
    return None, None

def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_info = st.secrets["GCP_SERVICE_ACCOUNT"]
    credentials = Credentials.from_service_account_info(creds_info, scopes=scope)
    return gspread.authorize(credentials)

def save_to_google_sheets(row_data):
    try:
        client = get_gspread_client()
        sheet = client.open_by_key(SHEET_ID).sheet1
        sheet.append_row(row_data)
        return True
    except Exception as e:
        st.error(f"Błąd zapisu: {e}")
        return False

# =========================================================
# 2. DESIGN VORTEZA 8.0
# =========================================================
def apply_vorteza_design():
    try:
        with open('bg_vorteza.png', 'rb') as f:
            bg_base64 = base64.b64encode(f.read()).decode()
    except: bg_base64 = ""
    
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

        .login-logo-container {{
            display: flex;
            justify-content: center;
            margin-bottom: 30px;
        }}

        div[data-testid="stExpander"] svg {{ display: none !important; }}
        div[data-testid="stExpander"] summary span {{ color: transparent !important; font-size: 0px !important; }}

        .streamlit-expanderHeader {{
            background-color: rgba(181, 136, 99, 0.1) !important;
            border: 1px solid rgba(181, 136, 99, 0.3) !important;
            border-left: 5px solid #B58863 !important;
            border-radius: 4px !important; padding: 12px !important;
        }}

        div[data-testid="stExpander"] p {{
            font-family: 'Michroma', sans-serif !important;
            color: #B58863 !important; font-size: 0.8rem !important;
            letter-spacing: 2px !important; visibility: visible !important; display: block !important;
        }}

        .vorteza-card {{
            background: rgba(20, 20, 20, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 4px; padding: 20px; margin-bottom: 15px;
        }}

        .stButton > button {{
            background: #B58863 !important;
            color: white !important; font-family: 'Michroma', sans-serif !important;
            width: 100%; border-radius: 2px !important; padding: 18px !important;
        }}

        label, p, span {{ font-family: 'Montserrat', sans-serif !important; color: #FFFFFF !important; }}
        #MainMenu, footer, header {{visibility: hidden;}}
        .stDeployButton {{display:none;}}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. LOGIKA APLIKACJI
# =========================================================
st.set_page_config(page_title="VORTEZA-BASE", layout="centered")
apply_vorteza_design()

data, current_sha = get_remote_data()

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    # Strona logowania z dużym logo
    st.markdown('<br><br>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image('logo_vorteza.png', use_container_width=True)
        except:
            pass
        st.markdown("<div class='vorteza-card' style='text-align:center;'><p class='logo-font'>SYSTEM ACCESS</p></div>", unsafe_allow_html=True)
        
        u = st.text_input("OPERATOR ID")
        p = st.text_input("SECURITY KEY", type="password")
        
        if st.button("AUTHORIZE"):
            # Pobieranie użytkowników bezpośrednio z secrets
            users_db = st.secrets.get("USERS", {})
            if u in users_db and str(users_db[u]) == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else:
                st.error("Invalid Credentials")
else:
    # Formularz główny
    try: st.image('logo_vorteza.png', width=150)
    except: pass
    st.markdown('<p class="logo-font">VORTEZA - BASE</p>', unsafe_allow_html=True)
    
    with st.form("main_form"):
        st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
        rej = st.text_input("LICENSE PLATE")
        km = st.number_input("MILEAGE (KM)", step=1, value=0)
        st.markdown('</div>', unsafe_allow_html=True)

        wyniki_kontroli = {}
        if data and "lista_kontrolna" in data:
            for kat, punkty in data["lista_kontrolna"].items():
                with st.expander(f"► {kat.upper()}"):
                    for pt in punkty:
                        res = st.checkbox(pt, key=f"chk_{kat}_{pt}")
                        wyniki_kontroli[pt] = "OK" if res else "BRAK/NIE"

        st.markdown('<br>', unsafe_allow_html=True)
        with st.expander("► OBSERVATIONS & NOTES"):
            obs = st.text_area("Notes...", height=100)

        if st.form_submit_button("GENERATE AND ENCRYPT PROTOCOL"):
            if not rej:
                st.error("Plate required!")
            else:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                usterki = [k for k, v in wyniki_kontroli.items() if v == "BRAK/NIE"]
                wynik_tekst = "Wszystko sprawne" if not usterki else f"USTERKI: {', '.join(usterki)}"
                
                row = [timestamp, st.session_state.user, rej, km, wynik_tekst, obs]
                
                if save_to_google_sheets(row):
                    st.success("PROTOCOL TRANSMITTED")
                    st.balloons()
