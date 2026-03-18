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
# 2. NOWY, DOPRACOWANY DESIGN VORTEZA 2.0
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
            background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url("data:image/png;base64,{bg_base64}");
            background-size: cover; background-attachment: fixed;
        }}

        /* NAGŁÓWEK GŁÓWNY */
        .logo-font {{
            font-family: 'Michroma', sans-serif !important;
            color: #B58863 !important;
            text-align: center; font-size: 1.8rem !important;
            letter-spacing: 6px !important; text-transform: uppercase;
            text-shadow: 0px 0px 15px rgba(181, 136, 99, 0.4);
            margin: 20px 0 40px 0;
        }}

        /* STYLIZACJA KART (FORMULARZ I SEKCJE) */
        .vorteza-card {{
            background: rgba(15, 15, 15, 0.85);
            border: 1px solid rgba(181, 136, 99, 0.3);
            border-radius: 8px; padding: 20px; margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}

        /* NAPRAWA EXPANDERA (UKRYCIE STANDARDOWEGO WYGLĄDU) */
        .streamlit-expanderHeader {{
            background-color: transparent !important;
            border: none !important;
            color: #B58863 !important;
            font-family: 'Michroma', sans-serif !important;
            font-size: 0.9rem !important;
            padding: 15px 0 !important;
        }}
        
        .streamlit-expanderContent {{
            background-color: transparent !important;
            border-top: 1px solid rgba(181, 136, 99, 0.1) !important;
        }}

        /* PRZYCISKI */
        .stButton > button {{
            background: linear-gradient(90deg, #B58863, #8B6B4F) !important;
            color: white !important; font-family: 'Michroma', sans-serif !important;
            letter-spacing: 2px; width: 100%; border-radius: 4px !important;
            border: none !important; padding: 18px !important;
            box-shadow: 0 5px 15px rgba(181, 136, 99, 0.2);
        }}

        /* CHECKBOXY - CZYSTSZY WYGLĄD */
        div[data-testid="stCheckbox"] {{
            padding: 8px 12px;
            border-bottom: 1px solid rgba(255,255,255,0.03);
        }}

        h3 {{ font-family: 'Michroma', sans-serif !important; color: #B58863 !important; font-size: 1rem !important; }}
        label, p, span {{ font-family: 'Montserrat', sans-serif !important; color: #E0E0E0 !important; }}
        
        /* LOGO MOBILE FIX */
        .centered-logo {{ display: block; margin: 0 auto 10px auto; width: 140px; }}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. LOGIKA APLIKACJI
# =========================================================
st.set_page_config(page_title="VORTEZA-BASE", layout="wide")
apply_vorteza_design()

data, current_sha = get_remote_data()
if data is None: data = {"uzytkownicy": {"admin": "vorteza"}, "lista_kontrolna": {}}

if "auth" not in st.session_state: st.session_state.auth = False

# --- LOGOWANIE ---
if not st.session_state.auth:
    _, col, _ = st.columns([0.5, 2, 0.5])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<div class="vorteza-card" style="text-align:center;">', unsafe_allow_html=True)
        st.subheader("SYSTEM AUTHORIZATION")
        u = st.text_input("Operator")
        p = st.text_input("Security Key", type="password")
        if st.button("LOGIN"):
            if u in data.get("uzytkownicy", {}) and data["uzytkownicy"][u] == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("Access Denied")
        st.markdown('</div>', unsafe_allow_html=True)

# --- PANEL GŁÓWNY ---
else:
    with st.sidebar:
        st.write(f"👤 **{st.session_state.user.upper()}**")
        menu = ["DASHBOARD"]
        if st.session_state.user == "admin": menu.append("USER MANAGER")
        choice = st.radio("MENU", menu)
        if st.button("LOGOUT"):
            st.session_state.auth = False
            st.rerun()

    if choice == "USER MANAGER":
        st.markdown('<p class="logo-font">USER MANAGER</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="vorteza-card"><h3>NEW OPERATOR</h3>', unsafe_allow_html=True)
            nu, np = st.text_input("Login"), st.text_input("Pass")
            if st.button("ADD"):
                data["uzytkownicy"][nu] = np
                if update_remote_data(data, current_sha): st.success("Added"); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="vorteza-card"><h3>ACTIVE USERS</h3>', unsafe_allow_html=True)
            for usr in data.get("uzytkownicy", {}).keys(): st.write(f"• {usr}")
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        # Logo i Tytuł
        _, l_col, _ = st.columns([1, 0.8, 1])
        with l_col:
            try: st.image('logo_vorteza.png', width=160)
            except: pass
        st.markdown('<p class="logo-font">VORTEZA - BASE</p>', unsafe_allow_html=True)
        
        with st.form("main_vorteza"):
            # Dane Pojazdu w jednej karcie
            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            st.subheader("VEHICLE DATA")
            c1, c2 = st.columns(2)
            rej = c1.text_input("LICENSE PLATE")
            km = c2.number_input("MILEAGE (KM)", step=1)
            st.markdown('</div>', unsafe_allow_html=True)

            # Kategorie - Każda w osobnej, czystej karcie
            for kat, punkty in data.get("lista_kontrolna", {}).items():
                with st.expander(f"➔ {kat.upper()}"):
                    for pt in punkty:
                        st.checkbox(pt, key=f"chk_{pt}")

            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            st.subheader("OBSERVATIONS")
            st.text_area("Notes...", height=80)
            st.markdown('</div>', unsafe_allow_html=True)

            if st.form_submit_button("SUBMIT PROTOCOL"):
                if not rej: st.error("Plate number missing!")
                else: st.success("SUCCESS"); st.balloons()
