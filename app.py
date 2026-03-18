import streamlit as st
import json
import requests
import base64
from datetime import datetime

# =========================================================
# 1. KONFIGURACJA GITHUB (API & SECRETS)
# =========================================================
try:
    # Upewnij się, że w Streamlit Cloud -> Settings -> Secrets masz:
    # [G_TOKEN]
    # G_TOKEN = "twój_token_github"
    GITHUB_TOKEN = st.secrets["G_TOKEN"]["G_TOKEN"]
except Exception:
    GITHUB_TOKEN = None 

REPO_OWNER = "natpio"
REPO_NAME = "protoku-pojazdu"
FILE_PATH = "lista_kontrolna.json"

# --- FUNKCJE SYNCHRONIZACJI Z GITHUB ---
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
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    # Indent=2 sprawia, że plik JSON na GitHubie jest czytelny dla oka
    encoded_content = base64.b64encode(json.dumps(new_data, indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
    payload = {
        "message": f"Vorteza System Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "content": encoded_content,
        "sha": sha
    }
    res = requests.put(url, json=payload, headers=headers)
    return res.status_code == 200

# =========================================================
# 2. DESIGN VORTEZA - LOGO MATCH & PREMIUM DARK
# =========================================================
def apply_vorteza_design():
    try:
        with open('bg_vorteza.png', 'rb') as f:
            bg_base64 = base64.b64encode(f.read()).decode()
    except: bg_base64 = ""
    
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Michroma&family=Montserrat:wght@400;700;900&display=swap');
        
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("data:image/png;base64,{bg_base64}");
            background-size: cover; background-attachment: fixed;
        }}

        /* LOGO FONT (Nagłówki) */
        .logo-font {{
            font-family: 'Michroma', sans-serif !important;
            color: #B58863 !important;
            text-align: center; font-size: 2.2rem !important;
            letter-spacing: 8px !important; text-transform: uppercase;
            font-weight: bold; text-shadow: 2px 2px 10px rgba(0,0,0,0.8);
            margin-bottom: 30px; margin-top: 10px;
        }}

        /* KARTY INTERFEJSU */
        .vorteza-card {{
            background: rgba(10, 10, 10, 0.95);
            border: 1px solid rgba(181, 136, 99, 0.2);
            border-left: 5px solid #B58863;
            border-radius: 4px; padding: 25px; margin-bottom: 20px;
            backdrop-filter: blur(15px);
        }}

        /* PRZYCISKI */
        .stButton > button {{
            background-color: #B58863 !important; color: white !important;
            font-family: 'Michroma', sans-serif !important;
            letter-spacing: 2px; width: 100%; border-radius: 2px !important;
            padding: 15px !important; border: none !important; transition: 0.3s;
        }}
        .stButton > button:hover {{ transform: scale(1.02); background-color: #8B6B4F !important; }}

        /* TYPOGRAFIA OGÓLNA */
        h2, h3, .stSubheader {{ font-family: 'Michroma', sans-serif !important; color: #B58863 !important; text-transform: uppercase; }}
        p, label, span, li {{ font-family: 'Montserrat', sans-serif !important; color: #FFFFFF !important; }}
        
        /* INPUTY */
        input {{ background: rgba(255,255,255,0.05) !important; color: white !important; }}
        
        /* SIDEBAR FIX */
        [data-testid="sidebar-button"] {{ color: transparent !important; font-size: 0px !important; }}
        [data-testid="sidebar-button"]::before {{ content: '◀'; color: #B58863; font-size: 18px; visibility: visible; }}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. GŁÓWNA LOGIKA SYSTEMU
# =========================================================
st.set_page_config(page_title="VORTEZA-BASE", layout="wide")
apply_vorteza_design()

# Inicjalizacja danych
data, current_sha = get_remote_data()

if "auth" not in st.session_state:
    st.session_state.auth = False

# --- EKRAN LOGOWANIA ---
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<div class="vorteza-card" style="text-align:center;">', unsafe_allow_html=True)
        st.subheader("BASE ACCESS")
        u = st.text_input("Operator ID")
        p = st.text_input("Security Key", type="password")
        if st.button("AUTHORIZE"):
            if data and u in data.get("uzytkownicy", {}) and data["uzytkownicy"][u] == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else:
                st.error("Błąd autoryzacji. Sprawdź dane.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- PANEL OPERACYJNY (PO ZALOGOWANIU) ---
else:
    with st.sidebar:
        st.write(f"👤 **OPERATOR:** {st.session_state.user}")
        st.markdown("---")
        
        # Wybór modułu (Tylko admin widzi User Managera)
        menu_options = ["DASHBOARD"]
        if st.session_state.user == "admin":
            menu_options.append("USER MANAGER")
        
        choice = st.radio("NAVIGATE", menu_options)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("LOGOUT"):
            st.session_state.auth = False
            st.rerun()

    # --- MODUŁ: USER MANAGER (Tylko Admin) ---
    if choice == "USER MANAGER":
        st.markdown('<p class="logo-font">USER MANAGER</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="vorteza-card"><h3>Dodaj Operatora</h3>', unsafe_allow_html=True)
            new_user = st.text_input("Login")
            new_pass = st.text_input("Hasło")
            if st.button("DODAJ DO SYSTEMU"):
                if new_user and new_pass:
                    data["uzytkownicy"][new_user] = new_pass
                    if update_remote_data(data, current_sha):
                        st.success(f"Dodano: {new_user}. Zmiany zapisane na GitHub.")
                        st.balloons()
                    else: st.error("Błąd zapisu na GitHub (sprawdź Token).")
                else: st.warning("Wypełnij dane.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="vorteza-card"><h3>Lista Użytkowników</h3>', unsafe_allow_html=True)
            for usr in data.get("uzytkownicy", {}).keys():
                st.write(f"• **{usr}**")
            st.markdown('</div>', unsafe_allow_html=True)

    # --- MODUŁ: DASHBOARD (Standardowy protokół) ---
    else:
        # Logo na środku (widoczne na telefonie)
        _, logo_col, _ = st.columns([1, 0.7, 1])
        with logo_col:
            try: st.image('logo_vorteza.png', use_container_width=True)
            except: pass
        
        st.markdown('<p class="logo-font">VORTEZA - BASE</p>', unsafe_allow_html=True)
        
        if data:
            with st.form("protocol_form"):
                st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
                st.subheader("Vehicle Data")
                c1, c2 = st.columns(2)
                rej = c1.text_input("LICENSE PLATE")
                km = c2.number_input("MILEAGE (KM)", step=1, value=0)
                st.markdown('</div>', unsafe_allow_html=True)

                grid = st.columns(2)
                for i, (kat, punkty) in enumerate(data.get("lista_kontrolna", {}).items()):
                    with grid[i % 2]:
                        st.markdown(f'<div class="vorteza-card"><h3>{kat}</h3>', unsafe_allow_html=True)
                        for pt in punkty:
                            st.checkbox(pt, key=f"chk_{pt}")
                        st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
                st.subheader("Observations")
                st.text_area("Technician's Notes...", height=100)
                st.markdown('</div>', unsafe_allow_html=True)

                if st.form_submit_button("SUBMIT AND ENCRYPT PROTOCOL"):
                    if not rej: st.error("Plate number required!")
                    else: st.success("SUCCESS"); st.balloons()
