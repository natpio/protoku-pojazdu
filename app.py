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
except Exception:
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
    payload = {"message": "Vorteza Update", "content": encoded_content, "sha": sha}
    res = requests.put(url, json=payload, headers=headers)
    return res.status_code == 200

# =========================================================
# 2. DESIGN VORTEZA 4.0 - FIX EMPTY BARS
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
            margin-bottom: 30px;
        }}

        /* NAGŁÓWEK SEKCJI - ZINTEGROWANY */
        .vorteza-section-title {{
            background: #B58863;
            color: black !important;
            font-family: 'Michroma', sans-serif;
            font-size: 0.8rem;
            padding: 8px 15px;
            margin-top: 20px;
            border-radius: 4px 4px 0 0;
            letter-spacing: 2px;
            font-weight: bold;
        }}

        /* KARTA ZAWARTOCI - PODPIĘTA POD TYTUŁ */
        .vorteza-section-content {{
            background: rgba(30, 30, 30, 0.6);
            border: 1px solid rgba(181, 136, 99, 0.3);
            border-top: none;
            border-radius: 0 0 4px 4px;
            padding: 20px;
            margin-bottom: 20px;
        }}

        .stButton > button {{
            background: #B58863 !important;
            color: white !important; font-family: 'Michroma', sans-serif !important;
            width: 100%; border-radius: 4px !important;
            border: none !important; padding: 18px !important;
            letter-spacing: 2px;
        }}

        h3 {{ font-family: 'Michroma', sans-serif !important; color: #B58863 !important; font-size: 1rem !important; }}
        label, p, span {{ font-family: 'Montserrat', sans-serif !important; color: #FFFFFF !important; }}
        
        #MainMenu, footer, header {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. LOGIKA SYSTEMU
# =========================================================
st.set_page_config(page_title="VORTEZA-BASE", layout="centered")
apply_vorteza_design()

data, current_sha = get_remote_data()
if not data: data = {"uzytkownicy": {"admin": "vorteza"}, "lista_kontrolna": {}}

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<br><br><div style='text-align:center;'><p class='logo-font'>SYSTEM LOGIN</p></div>", unsafe_allow_html=True)
    u = st.text_input("Operator")
    p = st.text_input("Key", type="password")
    if st.button("AUTHORIZE"):
        if u in data.get("uzytkownicy", {}) and data["uzytkownicy"][u] == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else: st.error("Access Denied")
else:
    with st.sidebar:
        st.write(f"👤 **{st.session_state.user.upper()}**")
        choice = st.radio("MENU", ["DASHBOARD", "USER MANAGER"] if st.session_state.user == "admin" else ["DASHBOARD"])
        if st.button("LOGOUT"):
            st.session_state.auth = False
            st.rerun()

    if choice == "USER MANAGER":
        st.markdown('<p class="logo-font">USERS</p>', unsafe_allow_html=True)
        nu, np = st.text_input("Login"), st.text_input("Pass")
        if st.button("ADD"):
            data["uzytkownicy"][nu] = np
            if update_remote_data(data, current_sha): st.success("Added"); st.rerun()
    else:
        try: st.image('logo_vorteza.png', width=180)
        except: pass
        st.markdown('<p class="logo-font">VORTEZA - BASE</p>', unsafe_allow_html=True)
        
        with st.form("protocol"):
            # Dane podstawowe
            st.markdown('<div class="vorteza-section-title">PODSTAWOWE INFORMACJE</div><div class="vorteza-section-content">', unsafe_allow_html=True)
            rej = st.text_input("LICENSE PLATE")
            km = st.number_input("MILEAGE (KM)", step=1)
            st.markdown('</div>', unsafe_allow_html=True)

            # Sekcje z pliku JSON
            for kat, punkty in data.get("lista_kontrolna", {}).items():
                st.markdown(f'<div class="vorteza-section-title">{kat.upper()}</div>', unsafe_allow_html=True)
                st.markdown('<div class="vorteza-section-content">', unsafe_allow_html=True)
                for pt in punkty:
                    st.checkbox(pt, key=f"chk_{pt}")
                st.markdown('</div>', unsafe_allow_html=True)

            # Uwagi
            st.markdown('<div class="vorteza-section-title">OBSERWACJE</div><div class="vorteza-section-content">', unsafe_allow_html=True)
            st.text_area("Notatki technika...", height=80)
            st.markdown('</div>', unsafe_allow_html=True)

            if st.form_submit_button("SUBMIT PROTOCOL"):
                if not rej: st.error("Plate missing!")
                else: st.success("SENT"); st.balloons()
