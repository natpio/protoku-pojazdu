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
    content = get_github_file("bg_vorteza.png")
    if content and 'content' in content:
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
# 2. DESIGN VORTEZA 15.5 - EKSTREMALNY KONTRAST
# =========================================================
def apply_vorteza_design():
    bg_data = get_bg_base64()
    bg_style = f"""
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.9), rgba(0,0,0,0.9)), 
                        url("data:image/png;base64,{bg_data}") !important;
            background-size: cover !important;
            background-attachment: fixed !important;
        }}
    """ if bg_data else ".stApp { background-color: #050505 !important; }"

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Michroma&family=Montserrat:wght@400;700&display=swap');
        
        {bg_style}
        
        /* WYMUSZENIE KOLORU MIEDZIANEGO NA WSZYSTKIM CO TEKSTOWE */
        html, body, [data-testid="stWidgetLabel"], .stMarkdown, p, span, label, .st-ae {{
            color: #B58863 !important;
            font-family: 'Montserrat', sans-serif !important;
        }}

        .vorteza-header {{
            font-family: 'Michroma', sans-serif !important;
            color: #B58863 !important;
            text-align: center; letter-spacing: 4px; padding: 20px; text-transform: uppercase;
        }}
        
        /* Sidebar Fix */
        section[data-testid="stSidebar"] {{
            background-color: rgba(5, 5, 5, 0.98) !important;
            border-right: 1px solid #B58863;
        }}
        
        /* Karty Dyspozytora - Całkowite przeprojektowanie dla czytelności */
        .log-entry {{
            background-color: rgba(15, 15, 15, 0.95) !important;
            border: 1px solid rgba(181, 136, 99, 0.4) !important;
            border-left: 8px solid #B58863 !important;
            border-radius: 4px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.6);
        }}

        .log-entry-alert {{ 
            border-left: 8px solid #FF4B4B !important;
            border-color: rgba(255, 75, 75, 0.3) !important;
        }}

        .card-plate {{
            font-family: 'Michroma', sans-serif !important;
            font-size: 1.5rem !important;
            color: #B58863 !important;
            margin-bottom: 5px;
        }}

        /* Fix dla Expanderów (widoczne na image_e2ba46.png) */
        .stExpander {{
            background-color: rgba(255,255,255,0.03) !important;
            border: 1px solid rgba(181, 136, 99, 0.2) !important;
            margin-bottom: 10px !important;
        }}
        
        .stExpander p {{
            color: #B58863 !important;
            font-weight: 500 !important;
        }}

        /* Ukrywanie elementów systemowych */
        #MainMenu, footer, header {{visibility: hidden;}}
        .stDeployButton {{display:none;}}
        
        /* Przyciski */
        .stButton>button {{
            width: 100%;
            background-color: transparent !important;
            color: #B58863 !important;
            border: 1px solid #B58863 !important;
            font-family: 'Michroma', sans-serif !important;
            transition: 0.3s;
        }}
        .stButton>button:hover {{
            background-color: #B58863 !important;
            color: black !important;
        }}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. GŁÓWNA LOGIKA
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
        st.write(f"USER: **{st.session_state.user.upper()}**")
        st.markdown("---")
        
        if is_dispatcher:
            df_full = load_from_google_sheets()
            if not df_full.empty:
                raw_plates = df_full['Numer Rejestracyjny'].astype(str).unique()
                plates = ["WSZYSTKIE"] + sorted([p for p in raw_plates if p.strip()])
                f_plate = st.selectbox("POJAZD", plates)
                f_alerts = st.checkbox("POKAŻ TYLKO ALERTY")
            if st.button("ODŚWIEŻ BAZĘ"): st.rerun()
            st.markdown("---")
        
        if st.button("WYLOGUJ"):
            st.session_state.auth = False
            st.rerun()

    if is_dispatcher:
        st.markdown("<h2 class='vorteza-header'>COMMAND CENTER</h2>", unsafe_allow_html=True)
        
        if not df_full.empty:
            df = df_full.copy()
            df['Data i Godzina'] = pd.to_datetime(df['Data i Godzina'], errors='coerce')
            df = df.dropna(subset=['Data i Godzina'])
            
            if f_plate != "WSZYSTKIE":
                df = df[df['Numer Rejestracyjny'].astype(str) == f_plate]
            if f_alerts:
                df = df[df['Wynik Kontroli'].str.contains("ALERT|USTERK|BRAK", na=False, case=False)]
            
            df = df.sort_values(by='Data i Godzina', ascending=False)

            for _, row in df.iterrows():
                status_raw = str(row.get('Wynik Kontroli', ''))
                is_alert = any(word in status_raw.upper() for word in ["ALERT", "USTERK", "BRAK"])
                entry_class = "log-entry log-entry-alert" if is_alert else "log-entry"
                
                fault_html = ""
                if is_alert:
                    msg = status_raw.split(":")[-1] if ":" in status_raw else status_raw
                    items = msg.split(",")
                    fault_html = '<div style="background:rgba(255,75,75,0.1); border:1px solid rgba(255,75,75,0.3); padding:10px; margin-top:10px;">'
                    for item in items:
                        fault_html += f'<span style="color:#FF4B4B !important; display:block; font-weight:700;">⚠️ {item.strip()}</span>'
                    fault_html += '</div>'
                else:
                    fault_html = '<div style="color:#B58863; font-weight:bold; margin-top:10px;">✅ WSZYSTKIE SYSTEMY SPRAWNE</div>'

                st.markdown(f"""
                <div class="{entry_class}">
                    <div style="display:flex; justify-content:space-between;">
                        <span class="card-plate">{row.get('Numer Rejestracyjny', 'N/A')}</span>
                        <span style="opacity:0.7; font-size:0.8rem;">{row.get('Data i Godzina').strftime('%Y-%m-%d | %H:%M')}</span>
                    </div>
                    <div style="margin: 10px 0;">
                        OPERATOR: <b style="color:#B58863;">{row.get('Operator ID', 'N/A')}</b> | 
                        PRZEBIEG: <b style="color:#B58863;">{row.get('Przebieg (km)', 0)} KM</b>
                    </div>
                    {fault_html}
                    {f'<div style="margin-top:10px; opacity:0.6; font-style:italic; border-top:1px solid rgba(181,136,99,0.1); padding-top:5px;">Notatki: {row.get("Uwagi i Obserwacje", "")}</div>' if row.get("Uwagi i Obserwacje") else ""}
                </div>
                """, unsafe_allow_html=True)
        else: st.info("Brak danych.")

    else:
        # WIDOK KIEROWCY
        st.markdown("<h2 class='vorteza-header'>KARTA KONTROLNA</h2>", unsafe_allow_html=True)
        data_gh, _ = get_remote_data()
        
        with st.form("driver_form", clear_on_submit=True):
            r = st.text_input("NUMER REJESTRACYJNY").upper()
            k = st.number_input("PRZEBIEG POJAZDU (KM)", step=1)
            
            check_results = {}
            if data_gh and "lista_kontrolna" in data_gh:
                for kat, punkty in data_gh["lista_kontrolna"].items():
                    with st.expander(kat.upper()):
                        for pt in punkty:
                            res = st.checkbox(pt, key=f"f_{pt}")
                            check_results[pt] = "OK" if res else "BRAK"
            
            u = st.text_area("DODATKOWE UWAGI")
            
            if st.form_submit_button("ZATWIERDŹ I WYŚLIJ PROTOKÓŁ"):
                if not r: st.error("Wpisz numer rejestracyjny!")
                else:
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
                    errs = [pt for pt, v in check_results.items() if v == "BRAK"]
                    status = "OK" if not errs else f"ALERT: {', '.join(errs)}"
                    if save_to_google_sheets([ts, st.session_state.user, r, k, status, u]):
                        st.success("Protokół został zapisany pomyślnie.")
