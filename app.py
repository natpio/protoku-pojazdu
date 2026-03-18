import streamlit as st
import json
import requests
import base64
from datetime import datetime

# =========================================================
# 1. KONFIGURACJA GITHUB
# =========================================================
try:
    GITHUB_TOKEN = st.secrets["G_TOKEN"]["G_TOKEN"]
except:
    GITHUB_TOKEN = None 

REPO_OWNER = "natpio"
REPO_NAME = "protoku-pojazdu"
FILE_PATH = "lista_kontrolna.json"

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

def update_remote_data(new_data, sha):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Content-Type": "application/json"}
    encoded_content = base64.b64encode(json.dumps(new_data, indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
    payload = {"message": "Update VORTEZA Users", "content": encoded_content, "sha": sha}
    res = requests.put(url, json=payload, headers=headers)
    return res.status_code == 200

# =========================================================
# 2. DESIGN VORTEZA 3.0 - CLEAN & READABLE
# =========================================================
def apply_vorteza_design():
    try:
        with open('bg_vorteza.png', 'rb') as f:
            bg_base64 = base64.b64encode(f.read()).decode()
    except: bg_base64 = ""
    
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Michroma&family=Montserrat:wght@300;400;700&display=swap');
        
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("data:image/png;base64,{bg_base64}");
            background-size: cover; background-attachment: fixed;
        }}

        .logo-font {{
            font-family: 'Michroma', sans-serif !important;
            color: #B58863 !important;
            text-align: center; font-size: 1.6rem !important;
            letter-spacing: 5px !important; text-transform: uppercase;
            margin-bottom: 30px;
        }}

        /* STYL KARTY KATEGORII (Zastępuje expander) */
        .category-header {{
            background: rgba(181, 136, 99, 0.15);
            border-left: 4px solid #B58863;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
            font-family: 'Michroma', sans-serif;
            color: #B58863;
            font-size: 0.9rem;
            letter-spacing: 2px;
        }}

        .vorteza-card {{
            background: rgba(20, 20, 20, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px; padding: 20px; margin-bottom: 20px;
        }}

        /* PRZYCISKI */
        .stButton > button {{
            background: #B58863 !important;
            color: white !important; font-family: 'Michroma', sans-serif !important;
            width: 100%; border-radius: 4px !important;
            border: none !important; padding: 15px !important;
            letter-spacing: 2px;
        }}

        h3 {{ font-family: 'Michroma', sans-serif !important; color: #B58863 !important; font-size: 1rem !important; margin-bottom: 15px; }}
        label, p, span {{ font-family: 'Montserrat', sans-serif !important; color: #FFFFFF !important; font-size: 1rem !important; }}
        
        /* UKRYCIE ŚMIECI STREAMLITA */
        #MainMenu, footer, header {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. LOGIKA APLIKACJI
# =========================================================
st.set_page_config(page_title="VORTEZA-BASE", layout="centered") # Zmieniono na centered dla lepszej czytelności
apply_vorteza_design()

data, current_sha = get_remote_data()
if data is None: data = {"uzytkownicy": {"admin": "vorteza"}, "lista_kontrolna": {}}

if "auth" not in st.session_state: st.session_state.auth = False

# --- LOGOWANIE ---
if not st.session_state.auth:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="vorteza-card" style="text-align:center;">', unsafe_allow_html=True)
    st.subheader("SYSTEM ACCESS")
    u = st.text_input("Operator")
    p = st.text_input("Security Key", type="password")
    if st.button("AUTHORIZE"):
        if u in data.get("uzytkownicy", {}) and data["uzytkownicy"][u] == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else: st.error("Access Denied")
    st.markdown('</div>', unsafe_allow_html=True)

# --- PANEL GŁÓWNY ---
else:
    with st.sidebar:
        st.write(f"👤 **{st.session_state.user.upper()}**")
        menu = ["DASHBOARD", "USER MANAGER"] if st.session_state.user == "admin" else ["DASHBOARD"]
        choice = st.radio("MENU", menu)
        if st.button("LOGOUT"):
            st.session_state.auth = False
            st.rerun()

    if choice == "USER MANAGER":
        st.markdown('<p class="logo-font">USER MANAGER</p>', unsafe_allow_html=True)
        nu, np = st.text_input("New Login"), st.text_input("New Pass")
        if st.button("ADD OPERATOR"):
            data["uzytkownicy"][nu] = np
            if update_remote_data(data, current_sha): st.success("Added"); st.rerun()

    else:
        # Logo
        try: st.image('logo_vorteza.png', width=180)
        except: pass
        st.markdown('<p class="logo-font">VORTEZA - BASE</p>', unsafe_allow_html=True)
        
        # FORMULARZ BEZ EXPANERÓW (Czytelna lista)
        with st.form("main_vorteza"):
            # Dane Pojazdu
            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            st.subheader("VEHICLE DATA")
            rej = st.text_input("LICENSE PLATE")
            km = st.number_input("MILEAGE (KM)", step=1)
            st.markdown('</div>', unsafe_allow_html=True)

            # Kategorie wyświetlane jako czytelne sekcje
            for kat, punkty in data.get("lista_kontrolna", {}).items():
                st.markdown(f'<div class="category-header">{kat.upper()}</div>', unsafe_allow_html=True)
                st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
                for pt in punkty:
                    st.checkbox(pt, key=f"chk_{pt}")
                st.markdown('</div>', unsafe_allow_html=True)

            st.subheader("OBSERVATIONS")
            obs = st.text_area("Notes...", height=100)

            if st.form_submit_button("SUBMIT PROTOCOL"):
                if not rej: st.error("Plate number missing!")
                else: st.success("SUCCESSFUL TRANSMISSION"); st.balloons()
