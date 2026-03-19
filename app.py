import streamlit as st
import psycopg2
import json
import base64
import requests
from datetime import datetime

# =========================================================
# 1. KONFIGURACJA I POBIERANIE DANYCH Z JSON (GITHUB)
# =========================================================
# Używamy Twojego G_TOKEN, aby pobrać listę użytkowników i punkty kontrolne
def get_remote_config():
    try:
        GITHUB_TOKEN = st.secrets["G_TOKEN"]["G_TOKEN"]
        REPO_OWNER = "natpio"
        REPO_NAME = "protoku-pojazdu"
        FILE_PATH = "lista_kontrolna.json"
        
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            content = res.json()
            data = json.loads(base64.b64decode(content['content']).decode('utf-8'))
            return data
    except Exception as e:
        st.error(f"Błąd pobierania konfiguracji JSON: {e}")
    return None

# =========================================================
# 2. POŁĄCZENIE Z BAZĄ (SUPABASE)
# =========================================================
def get_connection():
    try:
        conn = psycopg2.connect(
            host=st.secrets["postgres"]["host"],
            port=st.secrets["postgres"]["port"],
            database=st.secrets["postgres"]["database"],
            user=st.secrets["postgres"]["user"],
            password=st.secrets["postgres"]["password"],
            connect_timeout=10
        )
        return conn
    except Exception as e:
        st.error(f"DATABASE CONNECTION ERROR: {e}")
        return None

def save_to_supabase(rejestracja, przebieg, uwagi, lista_wynikowa, operator):
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            query = """
                INSERT INTO protokoly_vorteza 
                (rejestracja, przebieg, uwagi, lista_kontrolna, operator_id) 
                VALUES (%s, %s, %s, %s, %s)
            """
            cur.execute(query, (
                rejestracja, 
                przebieg, 
                uwagi, 
                json.dumps(lista_wynikowa), 
                operator
            ))
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            st.error(f"TRANSMISSION ERROR: {e}")
            return False
    return False

# =========================================================
# 3. DESIGN VORTEZA 8.0 - STYLE CSS
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
        div[data-testid="stExpander"] svg {{ display: none !important; }}
        div[data-testid="stExpander"] summary span {{ color: transparent !important; font-size: 0px !important; }}
        .streamlit-expanderHeader {{
            background-color: rgba(181, 136, 99, 0.1) !important;
            border: 1px solid rgba(181, 136, 99, 0.3) !important;
            border-left: 5px solid #B58863 !important;
            border-radius: 4px !important;
            padding: 12px !important;
            margin-bottom: 5px;
        }}
        div[data-testid="stExpander"] p {{
            font-family: 'Michroma', sans-serif !important;
            color: #B58863 !important;
            font-size: 0.8rem !important;
            letter-spacing: 2px !important;
            visibility: visible !important;
            display: block !important;
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
# 4. LOGIKA GŁÓWNA
# =========================================================
st.set_page_config(page_title="VORTEZA - LOGISTYKA SQM", layout="centered")
apply_vorteza_design()

# Pobieramy konfigurację z Twojego JSONa
config_data = get_remote_config()

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<br><br><div class='vorteza-card' style='text-align:center;'><p class='logo-font'>SYSTEM ACCESS</p></div>", unsafe_allow_html=True)
    u = st.text_input("OPERATOR ID")
    p = st.text_input("SECURITY KEY", type="password")
    
    if st.button("AUTHORIZE"):
        # Logowanie na podstawie listy "uzytkownicy" z Twojego JSONa
        if config_data and u in config_data["uzytkownicy"] and config_data["uzytkownicy"][u] == p:
            st.session_state.auth = True
            st.session_state.user = u
            st.rerun()
        else:
            st.error("ACCESS DENIED: INVALID CREDENTIALS")

else:
    # Ekran główny po zalogowaniu
    st.markdown('<p class="logo-font">VORTEZA - BASE</p>', unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#B58863;'>LOGGED AS: {st.session_state.user.upper()}</p>", unsafe_allow_html=True)
    
    with st.form("main_form"):
        # 1. Dane pojazdu
        st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
        rej = st.text_input("LICENSE PLATE (NR REJESTRACYJNY)")
        km = st.number_input("MILEAGE (PRZEBIEG KM)", step=1, value=0)
        st.markdown('</div>', unsafe_allow_html=True)

        # 2. Dynamiczna lista kontrolna z Twojego JSONa
        wyniki_kontroli = {}
        if config_data and "lista_kontrolna" in config_data:
            for kategoria, punkty in config_data["lista_kontrolna"].items():
                with st.expander(f"► {kategoria.upper()}"):
                    wyniki_kontroli[kategoria] = {}
                    for pt in punkty:
                        # Każdy checkbox ma unikalny klucz
                        stan = st.checkbox(pt, key=f"chk_{pt}")
                        wyniki_kontroli[kategoria][pt] = stan

        st.markdown('<br>', unsafe_allow_html=True)
        with st.expander("► OBSERVATIONS & NOTES"):
            obs = st.text_area("Notes...", height=100)

        # 3. Przycisk wysyłki
        if st.form_submit_button("GENERATE AND ENCRYPT PROTOCOL"):
            if not rej:
                st.error("LICENSE PLATE REQUIRED")
            else:
                with st.spinner("TRANSMITTING TO SUPABASE SERVER..."):
                    success = save_to_supabase(rej, km, obs, wyniki_kontroli, st.session_state.user)
                
                if success:
                    st.success("PROTOCOL SAVED IN DATABASE")
                    st.balloons()

    if st.sidebar.button("TERMINATE SESSION"):
        st.session_state.auth = False
        st.rerun()
