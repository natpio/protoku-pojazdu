import streamlit as st
import json
import requests
import base64
import gspread
import pandas as pd
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
    except: return False

def load_from_google_sheets():
    try:
        client = get_gspread_client()
        sheet = client.open_by_key(SHEET_ID).sheet1
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except: return pd.DataFrame()

# =========================================================
# 2. DESIGN VORTEZA 9.0
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
            color: #B58863 !important; text-align: center; font-size: 1.5rem !important;
            letter-spacing: 5px !important; text-transform: uppercase; margin-bottom: 25px;
        }}
        .vorteza-card {{
            background: rgba(20, 20, 20, 0.7);
            border: 1px solid rgba(181, 136, 99, 0.3);
            border-radius: 4px; padding: 20px; margin-bottom: 15px;
        }}
        .stButton > button {{
            background: #B58863 !important; color: white !important; font-family: 'Michroma', sans-serif !important;
            width: 100%; border-radius: 2px !important; padding: 15px !important;
        }}
        label, p, span, div {{ font-family: 'Montserrat', sans-serif !important; color: #FFFFFF !important; }}
        /* Styl tabeli dla dyspozytora */
        [data-testid="stDataFrame"] {{
            background: rgba(0,0,0,0.5);
            border: 1px solid #B58863;
        }}
        #MainMenu, footer, header {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. LOGIKA SYSTEMU
# =========================================================
st.set_page_config(page_title="VORTEZA-LOGISTICS", layout="wide")
apply_vorteza_design()

if "auth" not in st.session_state: st.session_state.auth = False

# --- LOGOWANIE ---
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<br><br>', unsafe_allow_html=True)
        try: st.image('logo_vorteza.png', use_container_width=True)
        except: pass
        st.markdown("<div class='vorteza-card' style='text-align:center;'><p class='logo-font'>SYSTEM ACCESS</p></div>", unsafe_allow_html=True)
        u = st.text_input("OPERATOR ID")
        p = st.text_input("SECURITY KEY", type="password")
        if st.button("AUTHORIZE"):
            users = st.secrets.get("USERS", {})
            if u in users and str(users[u]) == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("Access Denied")

# --- PANEL PO ZALOGOWANIU ---
else:
    # Górna belka
    c1, c2 = st.columns([5, 1])
    with c2:
        if st.button("LOGOUT"):
            st.session_state.auth = False
            st.rerun()
    with c1:
        st.markdown(f"<p style='color:#B58863'>ACTIVE OPERATOR: {st.session_state.user.upper()}</p>", unsafe_allow_html=True)

    # ROZDZIAŁ RÓL: Dyspozytor vs Kierowca
    if "dyspozytor" in st.session_state.user.lower() or st.session_state.user == "admin":
        st.markdown('<p class="logo-font">DISPATCHER CONTROL PANEL</p>', unsafe_allow_html=True)
        
        df = load_from_google_sheets()
        
        if not df.empty:
            # Filtry dla dyspozytora
            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                search_plate = st.selectbox("FILTER BY PLATE", ["ALL"] + list(df['Numer Rejestracyjny'].unique()))
            with col_f2:
                only_alerts = st.checkbox("SHOW ONLY ALERTS")
            
            # Aplikowanie filtrów
            if search_plate != "ALL":
                df = df[df['Numer Rejestracyjny'] == search_plate]
            if only_alerts:
                df = df[df['Wynik Kontroli'].str.contains("ALERT", na=False)]
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Wyświetlanie danych
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            if st.button("REFRESH DATA"):
                st.rerun()
        else:
            st.warning("No data found in the cloud.")

    else:
        # PANEL KIEROWCY (Formularz)
        st.markdown('<p class="logo-font">VEHICLE CHECKLIST</p>', unsafe_allow_html=True)
        data_gh, _ = get_remote_data()
        
        with st.form("main_form"):
            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            rej = st.text_input("LICENSE PLATE")
            km = st.number_input("MILEAGE (KM)", step=1, value=0)
            st.markdown('</div>', unsafe_allow_html=True)

            wyniki = {}
            if data_gh and "lista_kontrolna" in data_gh:
                for kat, punkty in data_gh["lista_kontrolna"].items():
                    with st.expander(f"► {kat.upper()}"):
                        for pt in punkty:
                            res = st.checkbox(pt, key=f"chk_{kat}_{pt}")
                            wyniki[pt] = "OK" if res else "BRAK/NIE"

            obs = st.text_area("Observations...", height=80)

            if st.form_submit_button("TRANSMIT PROTOCOL"):
                if not rej: st.error("Plate required!")
                else:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                    usterki = [k for k, v in wyniki.items() if v == "BRAK/NIE"]
                    wynik_tekst = "System Status: NOMINAL" if not usterki else f"ALERT: {', '.join(usterki)}"
                    
                    if save_to_google_sheets([timestamp, st.session_state.user, rej, km, wynik_tekst, obs]):
                        st.toast('DATA SECURED', icon='✅')
                        st.success("PROTOCOL SAVED.")
