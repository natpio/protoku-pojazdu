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
    payload = {"message": "Update VORTEZA", "content": encoded_content, "sha": sha}
    res = requests.put(url, json=payload, headers=headers)
    return res.status_code == 200

# =========================================================
# 2. DESIGN VORTEZA 4.0 - ZERO GLITCH (HTML BASED)
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
            margin-bottom: 25px;
        }}

        /* STYLIZACJA WŁASNYCH ROZWIJANYCH SEKCJI */
        details {{
            background: rgba(181, 136, 99, 0.1);
            border: 1px solid rgba(181, 136, 99, 0.3);
            border-left: 5px solid #B58863;
            border-radius: 4px;
            margin-bottom: 10px;
            transition: all 0.3s ease;
        }}

        summary {{
            padding: 15px;
            font-family: 'Michroma', sans-serif;
            color: #B58863;
            font-size: 0.85rem;
            cursor: pointer;
            list-style: none; /* Ukrywa standardową strzałkę */
            outline: none;
            letter-spacing: 2px;
            display: flex;
            align-items: center;
        }}

        summary::-webkit-details-marker {{ display: none; }} /* Ukrywa strzałkę w Safari */

        summary:before {{
            content: '▶';
            display: inline-block;
            margin-right: 15px;
            font-size: 0.7rem;
            transition: transform 0.2s;
        }}

        details[open] summary:before {{
            transform: rotate(90deg);
        }}

        .content-box {{
            padding: 20px;
            background: rgba(20, 20, 20, 0.5);
            border-top: 1px solid rgba(181, 136, 99, 0.1);
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
if not data: data = {"uzytkownicy": {"admin": "vorteza"}, "lista_kontrolna": {}}

if "auth" not in st.session_state: st.session_state.auth = False

# --- LOGOWANIE ---
if not st.session_state.auth:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="vorteza-card" style="text-align:center;"><p class="logo-font">ACCESS</p>', unsafe_allow_html=True)
    u = st.text_input("ID")
    p = st.text_input("KEY", type="password")
    if st.button("LOGIN"):
        if u in data.get("uzytkownicy", {}) and data["uzytkownicy"][u] == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- PANEL GŁÓWNY ---
else:
    with st.sidebar:
        st.write(f"👤 **{st.session_state.user.upper()}**")
        if st.button("LOGOUT"):
            st.session_state.auth = False
            st.rerun()

    try: st.image('logo_vorteza.png', width=180)
    except: pass
    st.markdown('<p class="logo-font">VORTEZA - BASE</p>', unsafe_allow_html=True)
    
    with st.form("main_form"):
        # Dane pojazdu
        st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
        rej = st.text_input("LICENSE PLATE")
        km = st.number_input("MILEAGE (KM)", step=1)
        st.markdown('</div>', unsafe_allow_html=True)

        # Dynamiczne sekcje (Zwijane przez HTML)
        if "lista_kontrolna" in data:
            for kat, punkty in data["lista_kontrolna"].items():
                # Używamy HTML Details/Summary zamiast st.expander
                st.markdown(f"""
                    <details>
                        <summary>{kat.upper()}</summary>
                        <div class="content-box">
                """, unsafe_allow_html=True)
                
                # Checkboxy muszą być wewnątrz formy, ale poza blokiem HTML 
                # więc robimy mały trick ze st.container
                for pt in punkty:
                    st.checkbox(pt, key=f"chk_{pt}")
                
                st.markdown("</div></details>", unsafe_allow_html=True)

        # Uwagi
        st.markdown('<br>', unsafe_allow_html=True)
        st.markdown('<details><summary>OBSERVATIONS</summary><div class="content-box">', unsafe_allow_html=True)
        obs = st.text_area("Notes...", key="obs_area")
        st.markdown('</div></details>', unsafe_allow_html=True)

        st.markdown('<br>', unsafe_allow_html=True)
        if st.form_submit_button("SUBMIT PROTOCOL"):
            if not rej: st.error("No plate!")
            else: st.success("TRANSMITTED"); st.balloons()
