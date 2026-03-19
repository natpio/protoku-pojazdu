import streamlit as st
import json
import requests
import base64
import gspread
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials

# =========================================================
# 1. KONFIGURACJA I ZASOBY
# =========================================================
try:
    GITHUB_TOKEN = st.secrets["G_TOKEN"]["G_TOKEN"]
except:
    GITHUB_TOKEN = None 

REPO_OWNER = "natpio"
REPO_NAME = "protoku-pojazdu"
SHEET_ID = "1UDehrxN8_j1CCrpq9FcXSory7FMA0LSdSk8PCIxIvPQ"

def get_github_file(file_path):
    if not GITHUB_TOKEN: return None
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.json()
    except: pass
    return None

def get_remote_data():
    content = get_github_file("lista_kontrolna.json")
    if content:
        data = json.loads(base64.b64decode(content['content']).decode('utf-8'))
        return data, content['sha']
    return None, None

def get_bg_base64():
    """Pobiera tło i czyści znaki nowej linii, które psują CSS."""
    content = get_github_file("bg_vorteza.png")
    if content and 'content' in content:
        # GitHub zwraca Base64 z \n, co uniemożliwia poprawne działanie url("data:...")
        return content['content'].replace("\n", "").replace("\r", "")
    return ""

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
# 2. DESIGN VORTEZA 15.2 - FIX TŁA
# =========================================================
def apply_vorteza_design():
    bg_data = get_bg_base64()
    
    # CSS dla tła - dodano !important i sprawdzanie danych
    if bg_data:
        bg_css = f"""
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
                        url("data:image/png;base64,{bg_data}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }}
        """
    else:
        bg_css = ".stApp { background-color: #050505 !important; }"

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Michroma&family=Montserrat:wght@400;700&display=swap');
        
        {bg_css}
        
        .vorteza-header {{
            font-family: 'Michroma', sans-serif;
            color: #B58863; text-align: center; letter-spacing: 4px; padding: 20px; text-transform: uppercase;
        }}
        
        section[data-testid="stSidebar"] {{
            background-color: rgba(5, 5, 5, 0.95) !important;
            border-right: 1px solid #B58863;
        }}

        .log-entry {{
            background-color: rgba(20, 20, 20, 0.85);
            border-left: 5px solid #B58863;
            border-radius: 4px;
            padding: 20px;
            margin-bottom: 25px;
            color: white;
            font-family: 'Montserrat', sans-serif;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }}

        .log-entry-alert {{ border-left: 5px solid #FF4B4B !important; }}

        .fault-list {{
            background: rgba(255, 75, 75, 0.15);
            border: 1px solid rgba(255, 75, 75, 0.4);
            border-radius: 4px; padding: 12px; margin-top: 10px;
        }}

        .fault-item {{ color: #FF4B4B; font-size: 0.85rem; display: block; margin-bottom: 3px; font-weight: 600; }}
        .status-ok {{ color: #B58863; font-weight: bold; font-size: 0.9rem; margin-top: 10px; display: block; }}
        
        #MainMenu, footer, header {{visibility: hidden;}}
        .stDeployButton {{display:none;}}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. LOGIKA APLIKACJI
# =========================================================
st.set_page_config(page_title="VORTEZA LOGISTICS", layout="wide")
apply_vorteza_design()

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        try: st.image('logo_vorteza.png', use_container_width=True)
        except: pass
        st.markdown("<h1 class='vorteza-header'>SYSTEM ACCESS</h1>", unsafe_allow_html=True)
        u = st.text_input("OPERATOR ID")
        p = st.text_input("SECURITY KEY", type="password")
        if st.button("AUTHORIZE"):
            users = st.secrets.get("USERS", {})
            if u in users and str(users[u]) == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("Access Denied")

else:
    is_dispatcher = "dyspozytor" in st.session_state.user.lower() or st.session_state.user == "admin"
    
    with st.sidebar:
        try: st.image('logo_vorteza.png', width=150)
        except: pass
        st.markdown(f"<p style='color:#B58863; font-family:Michroma; font-size:0.9rem; margin-top:10px;'>{st.session_state.user.upper()}</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        if is_dispatcher:
            st.markdown("<p style='color:#B58863; font-size:0.7rem; font-weight:bold;'>FILTRY</p>", unsafe_allow_html=True)
            df_full = load_from_google_sheets()
            if not df_full.empty:
                raw_plates = df_full['Numer Rejestracyjny'].astype(str).unique()
                plates = ["WSZYSTKIE"] + sorted([p for p in raw_plates if p.strip()])
                f_plate = st.selectbox("POJAZD", plates)
                f_alerts = st.checkbox("TYLKO ALERTY")
            if st.button("ODŚWIEŻ DANE"): st.rerun()
            st.markdown("---")
        
        if st.button("WYLOGUJ"):
            st.session_state.auth = False
            st.rerun()

    if is_dispatcher:
        st.markdown("<h2 class='vorteza-header'>CENTRUM DYSPOZYTORA</h2>", unsafe_allow_html=True)
        
        if not df_full.empty:
            df = df_full.copy()
            if f_plate != "WSZYSTKIE":
                df = df[df['Numer Rejestracyjny'].astype(str) == f_plate]
            if f_alerts:
                df = df[df['Wynik Kontroli'].str.contains("ALERT|USTERK|BRAK", na=False, case=False)]
            
            df['Data i Godzina'] = pd.to_datetime(df['Data i Godzina'])
            df = df.sort_values(by='Data i Godzina', ascending=False)

            for _, row in df.iterrows():
                status_raw = str(row.get('Wynik Kontroli', ''))
                is_alert = any(word in status_raw.upper() for word in ["ALERT", "USTERK", "BRAK"])
                entry_class = "log-entry log-entry-alert" if is_alert else "log-entry"
                
                fault_html = ""
                if is_alert:
                    msg = status_raw.split(":")[-1] if ":" in status_raw else status_raw
                    items = msg.split(",")
                    fault_html = '<div class="fault-list">'
                    for item in items:
                        fault_html += f'<span class="fault-item">⚠️ {item.strip()}</span>'
                    fault_html += '</div>'
                else:
                    fault_html = '<span class="status-ok">✅ SYSTEMY NOMINALNE</span>'

                st.markdown(f"""
                <div class="{entry_class}">
                    <div style="display:flex; justify-content:space-between; font-family:'Michroma'; border-bottom: 1px solid rgba(181,136,99,0.2); padding-bottom: 8px; margin-bottom: 10px;">
                        <span style="font-size:1.2rem; color:#B58863;">{row.get('Numer Rejestracyjny', 'N/A')}</span>
                        <span style="opacity:0.6; font-size:0.8rem;">{row.get('Data i Godzina').strftime('%Y-%m-%d | %H:%M')}</span>
                    </div>
                    <div style="font-size: 0.85rem; margin-bottom: 15px;">
                        OP: <b style="color:#B58863;">{row.get('Operator ID', 'N/A')}</b> | 
                        KM: <b style="color:#B58863;">{row.get('Przebieg (km)', 0)}</b>
                    </div>
                    {fault_html}
                    {f'<div style="margin-top:15px; font-size:0.8rem; border-top: 1px dotted rgba(255,255,255,0.1); padding-top:10px; opacity:0.8;"><i>Notatka: {row.get("Uwagi i Obserwacje", "")}</i></div>' if row.get("Uwagi i Obserwacje") else ""}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Brak danych w systemie.")

    else:
        # WIDOK KIEROWCY
        st.markdown("<h2 class='vorteza-header'>PROTOKÓŁ POJAZDU</h2>", unsafe_allow_html=True)
        data_gh, _ = get_remote_data()
        
        with st.form("driver_form", clear_on_submit=True):
            r = st.text_input("NUMER REJESTRACYJNY").upper()
            k = st.number_input("AKTUALNY PRZEBIEG (KM)", step=1)
            
            check_results = {}
            if data_gh and "lista_kontrolna" in data_gh:
                for kat, punkty in data_gh["lista_kontrolna"].items():
                    with st.expander(kat.upper()):
                        for pt in punkty:
                            res = st.checkbox(pt, key=f"f_{pt}")
                            check_results[pt] = "OK" if res else "BRAK"
            
            u = st.text_area("Uwagi i Obserwacje")
            
            if st.form_submit_button("WYŚLIJ PROTOKÓŁ"):
                if not r: st.error("Podaj numer rejestracyjny!")
                else:
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
                    errs = [pt for pt, v in check_results.items() if v == "BRAK"]
                    status = "System Status: NOMINAL" if not errs else f"ALERT: {', '.join(errs)}"
                    if save_to_google_sheets([ts, st.session_state.user, r, k, status, u]):
                        st.success("Dane przesłane do bazy.")
