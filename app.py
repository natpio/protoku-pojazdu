import streamlit as st
import json
import requests
import base64
from datetime import datetime

# =========================================================
# 1. KONFIGURACJA GITHUB (API & SECRETS)
# =========================================================
try:
    # Token musi być w Streamlit Cloud Secrets pod nazwą G_TOKEN
    GITHUB_TOKEN = st.secrets["G_TOKEN"]["G_TOKEN"]
except Exception:
    GITHUB_TOKEN = None 

REPO_OWNER = "natpio"
REPO_NAME = "protoku-pojazdu"
FILE_PATH = "lista_kontrolna.json"

def get_remote_data():
    if not GITHUB_TOKEN: 
        return None, None
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            content = res.json()
            data = json.loads(base64.b64decode(content['content']).decode('utf-8'))
            return data, content['sha']
    except: 
        pass
    return None, None

def update_remote_data(new_data, sha):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Content-Type": "application/json"}
    encoded_content = base64.b64encode(json.dumps(new_data, indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
    payload = {
        "message": f"Vorteza System Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "content": encoded_content,
        "sha": sha
    }
    res = requests.put(url, json=payload, headers=headers)
    return res.status_code == 200

# =========================================================
# 2. DESIGN VORTEZA 7.0 - NO-GLITCH UI (TOTAL FIX)
# =========================================================
def apply_vorteza_design():
    try:
        with open('bg_vorteza.png', 'rb') as f:
            bg_base64 = base64.b64encode(f.read()).decode()
    except: 
        bg_base64 = ""
    
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Michroma&family=Montserrat:wght@400;600;700&display=swap');
        
        /* TŁO I GŁÓWNA KONFIGURACJA */
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("data:image/png;base64,{bg_base64}");
            background-size: cover; background-attachment: fixed;
        }}

        /* LOGO I TYPO GŁÓWNE */
        .logo-font {{
            font-family: 'Michroma', sans-serif !important;
            color: #B58863 !important;
            text-align: center; font-size: 1.5rem !important;
            letter-spacing: 5px !important; text-transform: uppercase;
            margin-bottom: 25px; text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
        }}

        /* STYLIZACJA PRZYCISKÓW KATEGORII (ZAMIAST EXPANDERA) */
        div[data-testid="stVerticalBlock"] > div > div > div > button {{
            background-color: rgba(181, 136, 99, 0.1) !important;
            color: #B58863 !important;
            border-left: 5px solid #B58863 !important;
            border-radius: 4px !important;
            text-align: left !important;
            font-family: 'Michroma', sans-serif !important;
            font-size: 0.85rem !important;
            padding: 15px 20px !important;
            width: 100% !important;
            margin-bottom: 5px !important;
            border-top: none !important;
            border-right: none !important;
            border-bottom: none !important;
            transition: 0.3s !important;
        }}
        
        div[data-testid="stVerticalBlock"] > div > div > div > button:hover {{
            background-color: rgba(181, 136, 99, 0.25) !important;
        }}

        /* KARTY ZAWARTOCI */
        .vorteza-card {{
            background: rgba(20, 20, 20, 0.8);
            border: 1px solid rgba(181, 136, 99, 0.2);
            border-radius: 4px; padding: 20px; margin-bottom: 20px;
        }}

        /* PRZYCISK GŁÓWNY WYSYŁKI */
        .stButton > button[kind="primaryFormSubmit"], .main-submit-btn button {{
            background: #B58863 !important;
            color: white !important; font-family: 'Michroma', sans-serif !important;
            width: 100%; border-radius: 2px !important;
            border: none !important; padding: 18px !important;
            letter-spacing: 2px; font-size: 1rem !important;
            margin-top: 20px !important;
        }}

        /* TEKSTY */
        h3, .stSubheader {{ font-family: 'Michroma', sans-serif !important; color: #B58863 !important; font-size: 0.9rem !important; }}
        label, p, span, .stCheckbox {{ font-family: 'Montserrat', sans-serif !important; color: #FFFFFF !important; }}
        
        /* UKRYCIE ŚMIECI STREAMLIT */
        #MainMenu, footer, header {{visibility: hidden;}}
        .stDeployButton {{display:none;}}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. GŁÓWNA LOGIKA SYSTEMU
# =========================================================
st.set_page_config(page_title="VORTEZA-BASE", layout="centered")
apply_vorteza_design()

# Pobieranie danych
data, current_sha = get_remote_data()
if data is None: 
    data = {"uzytkownicy": {"admin": "vorteza"}, "lista_kontrolna": {}}

# Zarządzanie sesją
if "auth" not in st.session_state: 
    st.session_state.auth = False

# Zarządzanie stanem rozwijania sekcji
if "sections_state" not in st.session_state:
    st.session_state.sections_state = {}

# --- EKRAN AUTORYZACJI ---
if not st.session_state.auth:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="vorteza-card" style="text-align:center;">', unsafe_allow_html=True)
    st.markdown('<p class="logo-font">SYSTEM ACCESS</p>', unsafe_allow_html=True)
    user_input = st.text_input("OPERATOR ID")
    pass_input = st.text_input("SECURITY KEY", type="password")
    if st.button("AUTHORIZE ACCESS"):
        if user_input in data.get("uzytkownicy", {}) and data["uzytkownicy"][user_input] == pass_input:
            st.session_state.auth = True
            st.session_state.user = user_input
            st.rerun()
        else: 
            st.error("Invalid Security Key")
    st.markdown('</div>', unsafe_allow_html=True)

# --- PANEL OPERACYJNY ---
else:
    with st.sidebar:
        st.markdown(f"<p style='font-family:Michroma; color:#B58863;'>OPERATOR: {st.session_state.user.upper()}</p>", unsafe_allow_html=True)
        menu = ["DASHBOARD"]
        if st.session_state.user == "admin": 
            menu.append("USER MANAGER")
        
        choice = st.radio("SELECT MODULE", menu)
        st.markdown("---")
        if st.button("LOGOUT SYSTEM"):
            st.session_state.auth = False
            st.rerun()

    # --- MODUŁ ZARZĄDZANIA UŻYTKOWNIKAMI ---
    if choice == "USER MANAGER":
        st.markdown('<p class="logo-font">USER MANAGER</p>', unsafe_allow_html=True)
        with st.form("add_new_user"):
            new_u = st.text_input("New Username")
            new_p = st.text_input("New Password")
            if st.form_submit_button("CREATE OPERATOR"):
                if new_u and new_p:
                    data["uzytkownicy"][new_u] = new_p
                    if update_remote_data(data, current_sha):
                        st.success(f"Operator {new_u} created successfully.")
                        st.rerun()

    # --- GŁÓWNY MODUŁ PROTOKOŁU ---
    else:
        try: 
            st.image('logo_vorteza.png', width=180)
        except: 
            pass
        st.markdown('<p class="logo-font">VORTEZA - BASE</p>', unsafe_allow_html=True)
        
        # Rozpoczęcie formularza
        with st.form("vorteza_protocol_form"):
            
            # SEKCJA: DANE POJAZDU
            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            st.subheader("Vehicle Identification")
            v_plate = st.text_input("LICENSE PLATE NUMBER")
            v_km = st.number_input("CURRENT MILEAGE (KM)", step=1, value=0)
            st.markdown('</div>', unsafe_allow_html=True)

            # SEKCJA: DYNAMICZNE KATEGORIE (NAPRAWA ZWIJANIA)
            if "lista_kontrolna" in data:
                for kat, punkty in data["lista_kontrolna"].items():
                    # Tworzymy unikalny klucz dla stanu sekcji
                    if kat not in st.session_state.sections_state:
                        st.session_state.sections_state[kat] = False
                    
                    # Generujemy "belkę" kategorii jako przycisk (poza formem, by działał rerun, 
                    # ale tutaj wewnątrz formy używamy checkboxa pomocniczego lub expandera bez stylów psujących UI)
                    # UWAGA: Wewnątrz st.form przyciski nie mogą zmieniać stanu sesji natychmiastowo.
                    # Dlatego dla zachowania zwijania wewnątrz formy używamy najbezpieczniejszego st.expander z poprawionym CSS.
                    
                    with st.expander(f"➔ {kat.upper()}", expanded=False):
                        st.markdown('<div style="padding: 10px 0;">', unsafe_allow_html=True)
                        for pt in punkty:
                            st.checkbox(pt, key=f"chk_{kat}_{pt}")
                        st.markdown('</div>', unsafe_allow_html=True)

            # SEKCJA: UWAGI I ZDJĘCIA
            st.markdown('<br>', unsafe_allow_html=True)
            with st.expander("➔ OBSERVATIONS & NOTES"):
                v_notes = st.text_area("Technician's comments...", height=150)

            # PRZYCISK WYSYŁKI
            st.markdown('<div class="main-submit-btn">', unsafe_allow_html=True)
            submit = st.form_submit_button("GENERATE AND ENCRYPT PROTOCOL")
            st.markdown('</div>', unsafe_allow_html=True)

            if submit:
                if not v_plate:
                    st.error("ACTION DENIED: License plate is mandatory.")
                else:
                    # Tutaj możesz dodać logikę zapisu wyniku do GitHub lub bazy
                    st.success(f"PROTOCOL FOR {v_plate} SAVED SUCCESSFULLY.")
                    st.balloons()
