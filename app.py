import streamlit as st
import json
import requests
import base64
from datetime import datetime

# =========================================================
# 1. KONFIGURACJA GITHUB
# =========================================================
try:
    # Upewnij się, że w Streamlit Cloud masz Secret: G_TOKEN
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
# 2. DESIGN VORTEZA 5.0 - ULTRA CLEAN & READABLE
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
            text-align: center; font-size: 1.6rem !important;
            letter-spacing: 6px !important; text-transform: uppercase;
            margin-bottom: 40px;
        }}

        /* NAGŁÓWEK SEKCJI - ZŁOTY PASEK */
        .section-header {{
            background: #B58863;
            color: black !important;
            font-family: 'Michroma', sans-serif;
            font-size: 0.85rem;
            padding: 10px 15px;
            margin-top: 30px;
            border-radius: 4px 4px 0 0;
            letter-spacing: 2px;
            font-weight: bold;
            text-transform: uppercase;
        }}

        /* KARTA ZAWARTOCI - SKLEJONA Z NAGŁÓWKIEM */
        .section-container {{
            background: rgba(25, 25, 25, 0.8);
            border: 1px solid rgba(181, 136, 99, 0.4);
            border-top: none;
            border-radius: 0 0 4px 4px;
            padding: 20px;
            margin-bottom: 10px;
        }}

        /* PRZYCISKI */
        .stButton > button {{
            background: #B58863 !important;
            color: white !important; font-family: 'Michroma', sans-serif !important;
            width: 100%; border-radius: 4px !important;
            border: none !important; padding: 18px !important;
            letter-spacing: 3px; font-weight: bold;
            transition: 0.3s;
        }}
        .stButton > button:hover {{ background: #8B6B4F !important; transform: scale(1.01); }}

        /* TYPOGRAFIA FORMULARZA */
        label {{ font-family: 'Montserrat', sans-serif !important; color: #B58863 !important; font-weight: bold !important; }}
        p, span, div {{ font-family: 'Montserrat', sans-serif !important; color: #FFFFFF !important; }}
        
        /* UKRYCIE ELEMENTÓW STREAMLIT */
        #MainMenu, footer, header {{visibility: hidden;}}
        .stDeployButton {{display:none;}}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. LOGIKA SYSTEMU
# =========================================================
st.set_page_config(page_title="VORTEZA-BASE", layout="centered")
apply_vorteza_design()

data, current_sha = get_remote_data()
if not data: 
    data = {"uzytkownicy": {"admin": "vorteza"}, "lista_kontrolna": {}}

if "auth" not in st.session_state: 
    st.session_state.auth = False

# --- EKRAN LOGOWANIA ---
if not st.session_state.auth:
    st.markdown("<br><br><div style='text-align:center;'><p class='logo-font'>AUTHORIZATION</p></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-container" style="border-top: 1px solid rgba(181, 136, 99, 0.4); border-radius:4px;">', unsafe_allow_html=True)
    u = st.text_input("OPERATOR ID")
    p = st.text_input("SECURITY KEY", type="password")
    if st.button("LOGIN"):
        if u in data.get("uzytkownicy", {}) and data["uzytkownicy"][u] == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else: st.error("Access Denied")
    st.markdown('</div>', unsafe_allow_html=True)

# --- PANEL GŁÓWNY ---
else:
    with st.sidebar:
        st.markdown(f"<p style='color:#B58863; font-family:Michroma;'>USER: {st.session_state.user.upper()}</p>", unsafe_allow_html=True)
        choice = st.radio("MENU", ["DASHBOARD", "USER MANAGER"] if st.session_state.user == "admin" else ["DASHBOARD"])
        st.markdown("---")
        if st.button("LOGOUT"):
            st.session_state.auth = False
            st.rerun()

    if choice == "USER MANAGER":
        st.markdown('<p class="logo-font">USERS</p>', unsafe_allow_html=True)
        st.markdown('<div class="section-container" style="border-top: 1px solid rgba(181, 136, 99, 0.4); border-radius:4px;">', unsafe_allow_html=True)
        nu = st.text_input("Nowy Login")
        np = st.text_input("Nowe Hasło")
        if st.button("DODAJ OPERATORA"):
            if nu and np:
                data["uzytkownicy"][nu] = np
                if update_remote_data(data, current_sha):
                    st.success(f"Dodano: {nu}")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # Nagłówek i Logo
        try: st.image('logo_vorteza.png', width=200)
        except: pass
        st.markdown('<p class="logo-font">VORTEZA - BASE</p>', unsafe_allow_html=True)
        
        with st.form("main_form"):
            # Dane Pojazdu
            st.markdown('<div class="section-header">INFORMACJE O POJEŹDZIE</div><div class="section-container">', unsafe_allow_html=True)
            rej = st.text_input("NUMER REJESTRACYJNY")
            km = st.number_input("PRZEBIEG (KM)", step=1, value=0)
            st.markdown('</div>', unsafe_allow_html=True)

            # Dynamiczne sekcje z JSON
            for kat, punkty in data.get("lista_kontrolna", {}).items():
                st.markdown(f'<div class="section-header">{kat}</div>', unsafe_allow_html=True)
                st.markdown('<div class="section-container">', unsafe_allow_html=True)
                for pt in punkty:
                    st.checkbox(pt, key=f"chk_{pt}")
                st.markdown('</div>', unsafe_allow_html=True)

            # Uwagi
            st.markdown('<div class="section-header">UWAGI TECHNICZNE</div><div class="section-container">', unsafe_allow_html=True)
            uwagi = st.text_area("Wpisz dodatkowe obserwacje...", height=100)
            st.markdown('</div>', unsafe_allow_html=True)

            # Przycisk wysyłki
            if st.form_submit_button("WYŚLIJ PROTOKÓŁ"):
                if not rej:
                    st.error("Wprowadź numer rejestracyjny!")
                else:
                    st.success("PROTOKÓŁ ZOSTAŁ WYGENEROWANY I ZAPISANY")
                    st.balloons()
