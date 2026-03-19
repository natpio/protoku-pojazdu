import streamlit as st
import json
import requests
import base64
import gspread
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials

# =========================================================
# 1. KONFIGURACJA I POBIERANIE DANYCH
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

def load_from_google_sheets():
    try:
        client = get_gspread_client()
        sheet = client.open_by_key(SHEET_ID).sheet1
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except: return pd.DataFrame()

def save_to_google_sheets(row_data):
    try:
        client = get_gspread_client()
        sheet = client.open_by_key(SHEET_ID).sheet1
        sheet.append_row(row_data)
        return True
    except: return False

# =========================================================
# 2. DESIGN VORTEZA 12.0 - FIX WYŚWIETLANIA
# =========================================================
def apply_vorteza_design():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Michroma&family=Montserrat:wght@400;700&display=swap');
        
        .stApp { background-color: #050505; }
        
        .vorteza-header {
            font-family: 'Michroma', sans-serif;
            color: #B58863;
            text-align: center;
            letter-spacing: 4px;
            padding: 20px;
        }

        .card-container {
            background-color: #111111;
            border-left: 5px solid #B58863;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 20px;
            color: white;
        }

        .card-alert { border-left: 5px solid #FF4B4B !important; }

        .tag {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            margin: 3px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
        }

        .tag-fault {
            background: rgba(255, 75, 75, 0.2);
            border: 1px solid #FF4B4B;
            color: #FF4B4B;
        }

        h3, p, span { font-family: 'Montserrat', sans-serif; }
        #MainMenu, footer, header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. LOGIKA APLIKACJI
# =========================================================
st.set_page_config(page_title="VORTEZA COMMAND", layout="wide")
apply_vorteza_design()

if "auth" not in st.session_state: st.session_state.auth = False

# LOGOWANIE
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h1 class='vorteza-header'>VORTEZA ACCESS</h1>", unsafe_allow_html=True)
        u = st.text_input("OPERATOR")
        p = st.text_input("KEY", type="password")
        if st.button("AUTHORIZE"):
            users = st.secrets.get("USERS", {})
            if u in users and str(users[u]) == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("Access Denied")

# PANEL GŁÓWNY
else:
    is_dispatcher = "dyspozytor" in st.session_state.user.lower() or st.session_state.user == "admin"
    
    with st.sidebar:
        st.markdown(f"<p style='color:#B58863'>OPERATOR: {st.session_state.user.upper()}</p>", unsafe_allow_html=True)
        if st.button("LOGOUT"):
            st.session_state.auth = False
            st.rerun()

    if is_dispatcher:
        st.markdown("<h2 class='vorteza-header'>COMMAND CENTER</h2>", unsafe_allow_html=True)
        df_full = load_from_google_sheets()
        
        if not df_full.empty:
            # Szybkie statystyki na górze
            total = len(df_full)
            alerts = len(df_full[df_full['Wynik Kontroli'].str.contains("ALERT|USTERK", na=False, case=False)])
            
            c1, c2 = st.columns(2)
            c1.metric("TOTAL PROTOCOLS", total)
            c2.metric("ACTIVE ALERTS", alerts, delta_color="inverse")
            
            st.markdown("---")

            # Wyświetlanie kart
            for _, row in df_full.iloc[::-1].iterrows(): # Najnowsze u góry
                status_raw = str(row.get('Wynik Kontroli', ''))
                is_alert = any(word in status_raw.upper() for word in ["ALERT", "USTERK", "BRAK"])
                card_class = "card-container card-alert" if is_alert else "card-container"
                
                # Renderowanie karty jako czysty markdown + małe wstawki HTML dla stabilności
                with st.container():
                    st.markdown(f"""
                    <div class="{card_class}">
                        <div style="display:flex; justify-content:space-between; font-family:'Michroma';">
                            <span style="font-size:1.2rem; color:#B58863;">{row.get('Numer Rejestracyjny', 'N/A')}</span>
                            <span style="opacity:0.5;">{row.get('Data i Godzina', '')}</span>
                        </div>
                        <div style="margin: 10px 0; font-size: 0.8rem; opacity:0.8;">
                            OPERATOR: <b>{row.get('Operator ID', 'N/A')}</b> | MILEAGE: <b>{row.get('Przebieg (km)', 0)} KM</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Szczegóły usterek (osobno, aby Streamlit ich nie "uciął")
                    if is_alert:
                        st.error("⚠️ WYKRYTO USTERKI / BRAKI:")
                        # Próba wyciągnięcia listy po słowie ALERT: lub USTERKI:
                        parts = status_raw.split(":")
                        msg = parts[1] if len(parts) > 1 else status_raw
                        items = msg.split(",")
                        
                        # Wyświetlamy jako tagi przy użyciu st.button (trik na czytelność) lub kolumn
                        cols = st.columns(3)
                        for i, item in enumerate(items):
                            cols[i % 3].markdown(f"❌ `{item.strip()}`")
                    else:
                        st.success("✅ WSZYSTKIE SYSTEMY SPRAWNE")
                    
                    if row.get('Uwagi i Obserwacje'):
                        st.info(f"**Notatka:** {row.get('Uwagi i Obserwacje')}")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.warning("Brak danych w arkuszu.")

    else:
        # WIDOK KIEROWCY
        st.markdown("<h2 class='vorteza-header'>VEHICLE CHECKLIST</h2>", unsafe_allow_html=True)
        data_gh, _ = get_remote_data()
        
        with st.form("driver_form", clear_on_submit=True):
            r = st.text_input("NR REJESTRACYJNY")
            k = st.number_input("PRZEBIEG (KM)", step=1)
            
            check_results = {}
            if data_gh and "lista_kontrolna" in data_gh:
                for kat, punkty in data_gh["lista_kontrolna"].items():
                    with st.expander(kat.upper()):
                        for pt in punkty:
                            res = st.checkbox(pt, key=f"f_{pt}")
                            check_results[pt] = "OK" if res else "BRAK"
            
            u = st.text_area("Uwagi i Obserwacje")
            
            if st.form_submit_button("WYŚLIJ PROTOKÓŁ"):
                errs = [pt for pt, v in check_results.items() if v == "BRAK"]
                status = "System Status: NOMINAL" if not errs else f"ALERT: {', '.join(errs)}"
                if save_to_google_sheets([datetime.now().strftime("%Y-%m-%d %H:%M"), st.session_state.user, r, k, status, u]):
                    st.toast("Wysłano!")
                    st.success("Protokół zapisany.")
