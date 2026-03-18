import streamlit as st
import json
import requests
import base64
from datetime import datetime

# =========================================================
# 1. KONFIGURACJA GITHUB (API & SECRETS)
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
    payload = {
        "message": f"Vorteza Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "content": encoded_content,
        "sha": sha
    }
    res = requests.put(url, json=payload, headers=headers)
    return res.status_code == 200

# =========================================================
# 2. DESIGN VORTEZA 3.6 - FIX OVERLAP GLITCH
# =========================================================
def apply_vorteza_design():
    try:
        with open('bg_vorteza.png', 'rb') as f:
            bg_base64 = base64.b64encode(f.read()).decode()
    except: bg_base64 = ""
    
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Michroma&family=Montserrat:wght@400;600;700&display=swap');
        
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

        /* --- NAPRAWA EXPANDERA (ZAPOBIEGA NACHODZENIU) --- */
        .streamlit-expanderHeader {{
            background-color: rgba(181, 136, 99, 0.1) !important;
            border: 1px solid rgba(181, 136, 99, 0.2) !important;
            border-left: 5px solid #B58863 !important;
            border-radius: 4px !important;
            padding: 10px !important;
        }}
        
        /* Kluczowa poprawka: odsuwamy tekst od ikony strzałki */
        .streamlit-expanderHeader div[data-testid="stMarkdownContainer"] p {{
            font-family: 'Michroma', sans-serif !important;
            color: #B58863 !important;
            font-size: 0.8rem !important;
            letter-spacing: 1px !important;
            margin: 0 !important;
            padding-left: 35px !important; /* TO TWORZY MIEJSCE NA STRZAŁKĘ */
        }}

        .vorteza-card {{
            background: rgba(20, 20, 20, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 4px; padding: 20px; margin-bottom: 15px;
        }}

        .stButton > button {{
            background: #B58863 !important;
            color: white !important; font-family: 'Michroma', sans-serif !important;
            width: 100%; border-radius: 2px !important;
            border: none !important; padding: 18px !important;
            letter-spacing: 2px;
        }}

        label, p, span {{ font-family: 'Montserrat', sans-serif !important; color: #FFFFFF !important; }}
        h3, .stSubheader {{ font-family: 'Michroma', sans-serif !important; color: #B58863 !important; }}
        
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
if data is None: 
    data = {"uzytkownicy": {"admin": "vorteza"}, "lista_kontrolna": {}}

if "auth" not in st.session_state: st.session_state.auth = False

# --- LOGOWANIE ---
if not st.session_state.auth:
    st.markdown("<br><br><div class='vorteza-card' style='text-align:center;'><p style='font-family:Michroma; color:#B58863;'>SYSTEM ACCESS</p></div>", unsafe_allow_html=True)
    u = st.text_input("OPERATOR ID")
    p = st.text_input("SECURITY KEY", type="password")
    if st.button("AUTHORIZE"):
        if u in data.get("uzytkownicy", {}) and data["uzytkownicy"][u] == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else: st.error("Access Denied")

# --- PANEL GŁÓWNY ---
else:
    with st.sidebar:
        st.write(f"👤 **{st.session_state.user.upper()}**")
        menu = ["DASHBOARD"]
        if st.session_state.user == "admin": menu.append("USER MANAGER")
        choice = st.radio("NAVIGATE", menu)
        if st.button("LOGOUT"):
            st.session_state.auth = False
            st.rerun()

    if choice == "USER MANAGER":
        st.markdown('<p class="logo-font">USER MANAGER</p>', unsafe_allow_html=True)
        with st.form("add_user"):
            nu, np = st.text_input("Login"), st.text_input("Hasło")
            if st.form_submit_button("DODAJ OPERATORA"):
                data["uzytkownicy"][nu] = np
                if update_remote_data(data, current_sha):
                    st.success(f"Dodano: {nu}"); st.rerun()

    else:
        try: st.image('logo_vorteza.png', width=180)
        except: pass
        st.markdown('<p class="logo-font">VORTEZA - BASE</p>', unsafe_allow_html=True)
        
        with st.form("protocol_form"):
            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            st.subheader("Vehicle Data")
            rej = st.text_input("LICENSE PLATE")
            km = st.number_input("MILEAGE (KM)", step=1)
            st.markdown('</div>', unsafe_allow_html=True)

            # --- LISTY ROZWIJALNE ---
            if "lista_kontrolna" in data:
                for kat, punkty in data["lista_kontrolna"].items():
                    # Tutaj tworzymy expander
                    with st.expander(kat.upper()):
                        for pt in punkty:
                            st.checkbox(pt, key=f"chk_{pt}")

            st.markdown('<br>', unsafe_allow_html=True)
            with st.expander("OBSERVATIONS"):
                obs = st.text_area("Technician's Notes...", height=100)

            st.markdown('<br>', unsafe_allow_html=True)
            if st.form_submit_button("SUBMIT AND ENCRYPT PROTOCOL"):
                if not rej: st.error("Plate number required!")
                else: st.success("PROTOCOL TRANSMITTED"); st.balloons()
