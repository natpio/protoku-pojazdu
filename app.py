import streamlit as st
import json
import requests
import base64
from datetime import datetime

# =========================================================
# 1. KONFIGURACJA (BEZPIECZEŃSTWO)
# =========================================================
USER_DB = {"admin": "vorteza", "kierowca1": "CrystalBridge116"}

# POBIERAJ TOKEN TYLKO Z SECRETS! 
# Nie wklejaj go tutaj, bo GitHub zawsze będzie blokował commit.
try:
    GITHUB_TOKEN = st.secrets["G_TOKEN"]["G_TOKEN"]
except Exception:
    GITHUB_TOKEN = None 

REPO_OWNER = "natpio"
REPO_NAME = "protoku-pojazdu"
FILE_PATH = "lista_kontrolna.json"

# =========================================================
# 2. FUNKCJE SYSTEMOWE
# =========================================================
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f: return base64.b64encode(f.read()).decode()
    except: return ""

def get_data():
    if not GITHUB_TOKEN: return None
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return json.loads(base64.b64decode(res.json()['content']).decode('utf-8'))
    except: return None

# =========================================================
# 3. DESIGN: VORTEZA NEON-CARBON EDITION
# =========================================================
def apply_vorteza_design():
    bg_base64 = get_base64('bg_vorteza.png')
    
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Montserrat:wght@300;400;600;800&display=swap');
        
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url("data:image/png;base64,{bg_base64}");
            background-size: cover;
            background-attachment: fixed;
        }}

        /* FIX SIDEBAR ICON */
        [data-testid="sidebar-button"] {{ color: transparent !important; font-size: 0px !important; }}
        [data-testid="sidebar-button"]::before {{ content: '◀'; color: #B58863; font-size: 18px; visibility: visible; }}

        /* TYPOGRAFIA */
        .stApp, p, label, span, div {{
            font-family: 'Montserrat', sans-serif !important;
            color: #FFFFFF !important;
        }}

        h1, h2, h3, .stSubheader {{
            font-family: 'Orbitron', sans-serif !important;
            color: #B58863 !important;
            text-transform: uppercase;
            letter-spacing: 2px !important;
        }}

        /* KARTY SEKCJI */
        .vorteza-card {{
            background: rgba(10, 10, 10, 0.9);
            border: 1px solid rgba(181, 136, 99, 0.2);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 25px;
            backdrop-filter: blur(20px);
            box-shadow: 0 20px 50px rgba(0,0,0,0.8);
        }}

        /* PODŚWIETLENIE WIERSZA CHECKBOXA */
        div[data-testid="stCheckbox"] {{
            background: rgba(255,255,255,0.03);
            padding: 10px 15px;
            border-radius: 8px;
            margin-bottom: 5px;
            transition: 0.3s;
            border: 1px solid transparent;
        }}

        div[data-testid="stCheckbox"]:hover {{
            background: rgba(181, 136, 99, 0.1);
            border: 1px solid rgba(181, 136, 99, 0.3);
            transform: translateX(5px);
        }}

        /* STYLIZACJA SAMEGO CHECKBOXA (Kwadratu) */
        input[type="checkbox"] {{
            accent-color: #B58863 !important;
        }}

        /* PRZYCISK */
        .stButton > button {{
            background: linear-gradient(90deg, #8B6B4F 0%, #B58863 50%, #8B6B4F 100%);
            color: white !important;
            font-family: 'Orbitron', sans-serif !important;
            font-weight: 700 !important;
            border: none !important;
            padding: 20px !important;
            border-radius: 10px !important;
            width: 100%;
            box-shadow: 0 10px 30px rgba(181, 136, 99, 0.3);
        }}
        
        .stButton > button:hover {{
            box-shadow: 0 0 40px rgba(181, 136, 99, 0.6);
            transform: scale(1.01);
        }}

        /* SIDEBAR */
        section[data-testid="stSidebar"] {{
            background-color: rgba(5, 5, 5, 0.98) !important;
            border-right: 1px solid #B5886333;
        }}

        /* UKRYCIE RAMKI FORMULARZA */
        div[data-testid="stForm"] {{ border: none !important; padding: 0 !important; }}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 4. LOGIKA
# =========================================================
st.set_page_config(page_title="VORTEZA HUB", layout="wide")
apply_vorteza_design()

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown('<div class="vorteza-card" style="text-align:center;">', unsafe_allow_html=True)
        st.subheader("SYSTEM ACCESS")
        u = st.text_input("Operator")
        p = st.text_input("Password", type="password")
        if st.button("AUTHORIZE"):
            if u in USER_DB and USER_DB[u] == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
else:
    with st.sidebar:
        try: st.image('logo_vorteza.png', use_container_width=True)
        except: st.title("VORTEZA")
        st.markdown("---")
        st.write(f"👤 **OPERATOR:** {st.session_state.user}")
        st.write(f"📅 **DATA:** {datetime.now().strftime('%d/%m/%Y')}")
        if st.button("LOGOUT"):
            st.session_state.auth = False
            st.rerun()

    config = get_data()
    if config:
        st.markdown("<h1 style='text-align: center; margin-bottom: 40px;'>OPERATIONAL DASHBOARD</h1>", unsafe_allow_html=True)
        
        with st.form("main_form"):
            # IDENTYFIKACJA
            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            st.subheader("Vehicle Identification")
            c1, c2 = st.columns(2)
            rej = c1.text_input("LICENSE PLATE")
            km = c2.number_input("MILEAGE (KM)", step=1, value=0)
            st.markdown('</div>', unsafe_allow_html=True)

            # CHECKLISTA (Karty sekcji z punktami w środku)
            grid = st.columns(2)
            for i, (kat, punkty) in enumerate(config["lista_kontrolna"].items()):
                with grid[i % 2]:
                    # Otwieramy kartę
                    st.markdown(f'<div class="vorteza-card"><h3>{kat}</h3>', unsafe_allow_html=True)
                    for p_text in punkty:
                        st.checkbox(p_text, key=f"c_{p_text}")
                    # Zamykamy kartę
                    st.markdown('</div>', unsafe_allow_html=True)

            # UWAGI
            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            st.subheader("Technical Notes")
            st.text_area("Describe any issues...", height=100)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("SEND PROTOCOL"):
                if not rej: st.error("Plate number required!")
                else: st.success("SENT"); st.balloons()
    else:
        st.error("Check GitHub Secrets!")
