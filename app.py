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
# 2. DESIGN VORTEZA 11.0 - CZYTELNOŚĆ I SEGMENTACJA
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
            background: linear-gradient(rgba(0,0,0,0.92), rgba(0,0,0,0.92)), url("data:image/png;base64,{bg_base64}");
            background-size: cover; background-attachment: fixed;
        }}

        .logo-font {{
            font-family: 'Michroma', sans-serif !important;
            color: #B58863 !important; text-align: center; font-size: 1.5rem !important;
            letter-spacing: 5px !important; text-transform: uppercase; margin-bottom: 25px;
        }}

        .vorteza-card {{
            background: rgba(15, 15, 15, 0.85);
            border: 1px solid rgba(181, 136, 99, 0.2);
            border-radius: 4px; padding: 20px; margin-bottom: 15px;
        }}

        /* Styl tagów usterek */
        .fault-tag {{
            display: inline-block;
            background: rgba(255, 75, 75, 0.2);
            color: #FF4B4B;
            border: 1px solid #FF4B4B;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.75rem;
            margin: 2px;
            font-weight: 600;
        }}

        .stButton > button {{
            background: #B58863 !important; color: white !important; font-family: 'Michroma', sans-serif !important;
            width: 100%; border-radius: 2px !important; padding: 15px !important;
        }}

        label, p, span, div {{ font-family: 'Montserrat', sans-serif !important; color: #FFFFFF !important; }}
        section[data-testid="stSidebar"] {{ background-color: rgba(5, 5, 5, 0.95) !important; border-right: 1px solid #B58863; }}
        #MainMenu, footer, header {{visibility: hidden;}}
        .stDeployButton {{display:none;}}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. LOGIKA SYSTEMU
# =========================================================
st.set_page_config(page_title="VORTEZA COMMAND", layout="wide")
apply_vorteza_design()

if "auth" not in st.session_state: st.session_state.auth = False

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

else:
    with st.sidebar:
        try: st.image('logo_vorteza.png', width=100)
        except: pass
        st.markdown(f"<p style='color:#B58863; font-size: 0.8rem;'>OPERATOR: {st.session_state.user.upper()}</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        is_dispatcher = "dyspozytor" in st.session_state.user.lower() or st.session_state.user == "admin"
        
        if is_dispatcher:
            st.markdown('<p style="font-family: Michroma; color: #B58863; font-size: 0.7rem;">CONTROL FILTERS</p>', unsafe_allow_html=True)
            df_full = load_from_google_sheets()
            if not df_full.empty:
                plates = ["ALL PLATES"] + list(df_full['Numer Rejestracyjny'].unique())
                f_plate = st.selectbox("SELECT VEHICLE", plates)
                f_alerts = st.checkbox("SHOW CRITICAL ONLY")
            if st.button("REFRESH COMMAND CENTER"): st.rerun()
        
        if st.button("LOGOUT"):
            st.session_state.auth = False
            st.rerun()

    if is_dispatcher:
        st.markdown('<p class="logo-font">DISPATCHER COMMAND CENTER</p>', unsafe_allow_html=True)
        
        if not df_full.empty:
            df = df_full.copy()
            if f_plate != "ALL PLATES": df = df[df['Numer Rejestracyjny'] == f_plate]
            if f_alerts: df = df[df['Wynik Kontroli'].str.contains("ALERT", na=False)]
            
            df['Data i Godzina'] = pd.to_datetime(df['Data i Godzina'])
            df = df.sort_values(by='Data i Godzina', ascending=False)

            for _, row in df.iterrows():
                val_wynik = str(row.get('Wynik Kontroli', ''))
                is_alert = "ALERT" in val_wynik.upper()
                
                # Przetwarzanie tekstu usterek na tagi
                faults_html = ""
                if is_alert:
                    # Wycinamy samą listę usterek po słowie ALERT:
                    content = val_wynik.split("ALERT: ")
                    if len(content) > 1:
                        faults_list = content[1].split(", ")
                        for f in faults_list:
                            faults_html += f'<span class="fault-tag">{f}</span>'
                    else:
                        faults_html = f'<span class="fault-tag">{val_wynik}</span>'
                else:
                    faults_html = '<span style="color:#B58863; font-size:0.9rem;">✅ ALL SYSTEMS OPERATIONAL</span>'

                accent = "#FF4B4B" if is_alert else "#B58863"
                bg = "rgba(255, 75, 75, 0.08)" if is_alert else "rgba(181, 136, 99, 0.05)"

                st.markdown(f"""
                    <div style="background: {bg}; border: 1px solid {accent}; border-radius: 4px; padding: 15px; margin-bottom: 12px; border-left: 5px solid {accent};">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 5px;">
                            <span style="font-family: 'Michroma'; color: {accent}; font-size: 1.1rem;">{row.get('Numer Rejestracyjny', 'N/A')}</span>
                            <span style="font-size: 0.8rem; opacity: 0.6;">{row.get('Data i Godzina').strftime('%Y-%m-%d | %H:%M')}</span>
                        </div>
                        
                        <div style="display: flex; gap: 30px; font-size: 0.85rem; margin-bottom: 12px; font-weight: 600;">
                            <div><span style="color:{accent}; opacity:0.7; font-weight:400;">OPERATOR:</span> {row.get('Operator ID', 'N/A')}</div>
                            <div><span style="color:{accent}; opacity:0.7; font-weight:400;">MILEAGE:</span> {row.get('Przebieg (km)', 0)} KM</div>
                        </div>

                        <div style="margin-bottom: 5px;">
                            <p style="font-size: 0.7rem; color: {accent}; margin-bottom: 5px; letter-spacing: 1px; font-weight: 600;">TECHNICAL STATUS / FAULTS</p>
                            <div style="line-height: 1.6;">
                                {faults_html}
                            </div>
                        </div>
                        
                        {f'<div style="margin-top:12px; padding-top:8px; border-top: 1px dotted rgba(255,255,255,0.1); font-size:0.85rem; color:#DDD;"><b>NOTE:</b> {row.get("Uwagi i Obserwacje", "")}</div>' if row.get("Uwagi i Obserwacje") else ""}
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No logs available in the system.")

    else:
        # WIDOK KIEROWCY
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
                            wyniki[pt] = "OK" if res else "BRAK"

            obs = st.text_area("Uwagi i Obserwacje")

            if st.form_submit_button("TRANSMIT PROTOCOL"):
                if not rej: st.error("Plate required!")
                else:
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    errs = [k for k, v in wyniki.items() if v == "BRAK"]
                    status = "System Status: NOMINAL" if not errs else f"ALERT: {', '.join(errs)}"
                    if save_to_google_sheets([ts, st.session_state.user, rej, km, status, obs]):
                        st.toast('PROTOCOL SECURED', icon='✅')
                        st.success("DATA TRANSMITTED TO COMMAND CENTER.")
