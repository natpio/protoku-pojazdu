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
# 2. DESIGN VORTEZA 9.5 - COMMAND CENTER
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
            background: linear-gradient(rgba(0,0,0,0.9), rgba(0,0,0,0.9)), url("data:image/png;base64,{bg_base64}");
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
            width: 100%; border-radius: 2px !important; padding: 15px !important; transition: 0.3s;
        }}
        
        .stButton > button:hover {{ background: #966b4a !important; box-shadow: 0px 0px 15px rgba(181, 136, 99, 0.4); }}

        label, p, span, div {{ font-family: 'Montserrat', sans-serif !important; color: #FFFFFF !important; }}
        
        /* Stylistyka Sidebar */
        section[data-testid="stSidebar"] {{ background-color: rgba(10, 10, 10, 0.9) !important; border-right: 1px solid #B58863; }}
        
        /* Ukrycie elementów Streamlit */
        #MainMenu, footer, header {{visibility: hidden;}}
        .stDeployButton {{display:none;}}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. LOGIKA SYSTEMU
# =========================================================
st.set_page_config(page_title="VORTEZA LOGISTICS", layout="wide")
apply_vorteza_design()

if "auth" not in st.session_state: st.session_state.auth = False

# --- EKRAN LOGOWANIA ---
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

# --- PANEL GŁÓWNY ---
else:
    # Sidebar - Nawigacja i Filtry
    with st.sidebar:
        try: st.image('logo_vorteza.png', width=100)
        except: pass
        st.markdown(f"<p style='color:#B58863; font-size: 0.8rem;'>ACTIVE: {st.session_state.user.upper()}</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Jeśli dyspozytor/admin - pokaż filtry
        is_dispatcher = "dyspozytor" in st.session_state.user.lower() or st.session_state.user == "admin"
        
        if is_dispatcher:
            st.markdown('<p style="font-family: Michroma; color: #B58863; font-size: 0.7rem;">FILTERS</p>', unsafe_allow_html=True)
            df_full = load_from_google_sheets()
            if not df_full.empty:
                f_plate = st.selectbox("PLATE", ["ALL"] + list(df_full['Numer Rejestracyjny'].unique()))
                f_alerts = st.checkbox("ONLY ALERTS")
            if st.button("REFRESH DATA"): st.rerun()
        
        if st.button("LOGOUT"):
            st.session_state.auth = False
            st.rerun()

    # --- WIDOK DYSPOZYTORA (KARTY) ---
    if is_dispatcher:
        st.markdown('<p class="logo-font">DISPATCHER COMMAND CENTER</p>', unsafe_allow_html=True)
        
        if not df_full.empty:
            # Filtrowanie
            df = df_full.copy()
            if f_plate != "ALL": df = df[df['Numer Rejestracyjny'] == f_plate]
            if f_alerts: df = df[df['Wynik Kontroli'].str.contains("ALERT", na=False)]
            
            # Sortowanie po dacie (najnowsze u góry)
            df['Data i Godzina'] = pd.to_datetime(df['Data i Godzina'])
            df = df.sort_values(by='Data i Godzina', ascending=False)

            for _, row in df.iterrows():
                is_alert = "ALERT" in str(row['Wynik Kontroli']).upper()
                accent = "#FF4B4B" if is_alert else "#B58863"
                bg = "rgba(255, 75, 75, 0.15)" if is_alert else "rgba(181, 136, 99, 0.05)"
                glow = "0px 0px 15px rgba(255, 75, 75, 0.3)" if is_alert else "none"

                st.markdown(f"""
                    <div style="background: {bg}; border: 1px solid {accent}; box-shadow: {glow}; border-radius: 4px; padding: 15px; margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px;">
                            <span style="font-family: 'Michroma'; color: {accent};">{row['Numer Rejestracyjny']}</span>
                            <span style="font-size: 0.8rem; opacity: 0.6;">{row['Data i Godzina'].strftime('%Y-%m-%d %H:%M')}</span>
                        </div>
                        <div style="display: flex; gap: 20px; font-size: 0.8rem; margin-bottom: 10px;">
                            <div><span style="color:{accent};">OP:</span> {row['Operator ID']}</div>
                            <div><span style="color:{accent};">KM:</span> {row['Przebieg (km)']}</div>
                        </div>
                        <div style="background: rgba(0,0,0,0.4); padding: 8px; border-radius: 2px; border-left: 3px solid {accent}; font-size: 0.9rem;">
                            {row['Wynik Kontroli']}
                        </div>
                        {f'<div style="margin-top:8px; font-size:0.8rem; opacity:0.7;">Note: {row["Uwagi"]}</div>' if row["Uwagi"] else ""}
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No data available.")

    # --- WIDOK KIEROWCY (FORMULARZ) ---
    else:
        st.markdown('<p class="logo-font">VEHICLE CHECKLIST</p>', unsafe_allow_html=True)
        data_gh, _ = get_remote_data()
        
        with st.form("main_form", clear_on_submit=True):
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

            obs = st.text_area("Observations...")

            if st.form_submit_button("TRANSMIT PROTOCOL"):
                if not rej: st.error("Plate required!")
                else:
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    errs = [k for k, v in wyniki.items() if v == "BRAK/NIE"]
                    status = "System Status: NOMINAL" if not errs else f"ALERT: {', '.join(errs)}"
                    
                    if save_to_google_sheets([ts, st.session_state.user, rej, km, status, obs]):
                        st.toast('DATA SECURED', icon='✅')
                        st.success("PROTOCOL SAVED TO CLOUD.")
