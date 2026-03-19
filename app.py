import streamlit as st
import psycopg2
import json
import base64
import requests
import pandas as pd
from datetime import datetime

# =========================================================
# 1. KOMUNIKACJA Z BAZĄ (ZGODNIE ZE SCHEMATEM SUPABASE)
# =========================================================
def get_connection():
    try:
        # Pobieranie ID projektu z nazwy użytkownika w secrets
        user_parts = st.secrets["postgres"]["user"].split('.')
        project_id = user_parts[1] if len(user_parts) > 1 else "twjjscfizxnvbxwxqcbw"
        
        return psycopg2.connect(
            host=st.secrets["postgres"]["host"],
            port=st.secrets["postgres"]["port"],
            database=st.secrets["postgres"]["database"],
            user=st.secrets["postgres"]["user"],
            password=st.secrets["postgres"]["password"],
            sslmode="require",
            # Rozwiązanie błędu "Tenant not found"
            options=f"-c endpoint={project_id}",
            connect_timeout=10
        )
    except Exception as e:
        st.error(f"BŁĄD POŁĄCZENIA: {e}")
        return None

def save_to_supabase(rejestracja, przebieg, uwagi, lista_wynikowa, operator):
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            # Kolumny 1:1 z Twojego zdjęcia bazy danych
            query = """
                INSERT INTO protokoly_vorteza 
                (rejestracja, przebieg, uwagi, lista_kontrolna, operator_id) 
                VALUES (%s, %s, %s, %s, %s)
            """
            cur.execute(query, (rejestracja, przebieg, uwagi, json.dumps(lista_wynikowa), operator))
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            st.error(f"BŁĄD ZAPISU: {e}")
            return False
    return False

def get_recent_protocols(limit=10):
    conn = get_connection()
    if conn:
        try:
            # Użycie Twojej kolumny data_wpisu
            query = "SELECT data_wpisu, rejestracja, operator_id, lista_kontrolna FROM protokoly_vorteza ORDER BY data_wpisu DESC LIMIT %s"
            df = pd.read_sql(query, conn, params=(limit,))
            conn.close()
            return df
        except: return None
    return None

# =========================================================
# 2. DESIGN VORTEZA 8.0 - TWOJA ORYGINALNA STYLIZACJA
# =========================================================
def apply_vorteza_design():
    try:
        with open('bg_vorteza.png', 'rb') as f:
            bg_base64 = base64.b64encode(f.read()).decode()
    except: 
        bg_base64 = ""
    
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

        /* --- TWOJA NAPRAWA BLEDU _arrow_right --- */
        div[data-testid="stExpander"] svg {{
            display: none !important;
        }}
        
        div[data-testid="stExpander"] summary span {{
            color: transparent !important;
            font-size: 0px !important;
        }}

        .streamlit-expanderHeader {{
            background-color: rgba(181, 136, 99, 0.1) !important;
            border: 1px solid rgba(181, 136, 99, 0.3) !important;
            border-left: 5px solid #B58863 !important;
            border-radius: 4px !important;
            padding: 12px !important;
        }}

        div[data-testid="stExpander"] p {{
            font-family: 'Michroma', sans-serif !important;
            color: #B58863 !important;
            font-size: 0.8rem !important;
            letter-spacing: 2px !important;
            visibility: visible !important;
            display: block !important;
            margin: 0 !important;
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
# 3. LOGIKA APLIKACJI
# =========================================================
st.set_page_config(page_title="VORTEZA-BASE", layout="centered")
apply_vorteza_design()

# Pobieranie konfiguracji z GitHub (użytkownicy i punkty kontrolne)
@st.cache_data(ttl=300)
def get_config():
    try:
        token = st.secrets["G_TOKEN"]["G_TOKEN"]
        url = "https://api.github.com/repos/natpio/protoku-pojazdu/contents/lista_kontrolna.json"
        res = requests.get(url, headers={"Authorization": f"token {token}"})
        if res.status_code == 200:
            return json.loads(base64.b64decode(res.json()['content']).decode('utf-8'))
    except: return None
    return None

data = get_config()
if not data: data = {"uzytkownicy": {"admin": "vorteza"}, "lista_kontrolna": {}}

if "auth" not in st.session_state: st.session_state.auth = False

# --- LOGOWANIE ---
if not st.session_state.auth:
    st.markdown("<br><br><div class='vorteza-card' style='text-align:center;'><p class='logo-font'>SYSTEM ACCESS</p></div>", unsafe_allow_html=True)
    u = st.text_input("OPERATOR ID")
    p = st.text_input("SECURITY KEY", type="password")
    if st.button("AUTHORIZE"):
        if u in data.get("uzytkownicy", {}) and data["uzytkownicy"][u] == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else: st.error("ACCESS DENIED")

# --- PANEL GŁÓWNY ---
else:
    tab1, tab2 = st.tabs(["📝 PROTOKÓŁ", "📊 HISTORIA"])

    with tab1:
        st.markdown('<p class="logo-font">VORTEZA - BASE</p>', unsafe_allow_html=True)
        with st.form("main_form"):
            # Dane pojazdu
            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            rej = st.text_input("LICENSE PLATE")
            km = st.number_input("MILEAGE (KM)", step=1, value=0)
            st.markdown('</div>', unsafe_allow_html=True)

            # Twoje dynamiczne sekcje z poprawionym expanderem
            wyniki_kontroli = {}
            if "lista_kontrolna" in data:
                for kat, punkty in data["lista_kontrolna"].items():
                    with st.expander(f"► {kat.upper()}"):
                        wyniki_kontroli[kat] = {}
                        for pt in punkty:
                            wyniki_kontroli[kat][pt] = st.checkbox(pt, key=f"chk_{kat}_{pt}", value=False)

            st.markdown('<br>', unsafe_allow_html=True)
            with st.expander("► OBSERVATIONS & NOTES"):
                obs = st.text_area("Notes...", height=100)

            st.markdown('<br>', unsafe_allow_html=True)
            if st.form_submit_button("GENERATE AND ENCRYPT PROTOCOL"):
                if not rej: 
                    st.error("Plate required!")
                else:
                    # Zapis do Supabase
                    if save_to_supabase(rej, km, obs, wyniki_kontroli, st.session_state.user):
                        st.success("PROTOCOL TRANSMITTED"); st.balloons()

    with tab2:
        st.markdown('<p class="logo-font">HISTORY FEED</p>', unsafe_allow_html=True)
        if st.button("ODŚWIEŻ"): st.rerun()
        
        hist = get_recent_protocols()
        if hist is not None:
            for _, row in hist.iterrows():
                with st.container():
                    st.markdown(f"<div class='vorteza-card'><b>{row['rejestracja']}</b> | {row['operator_id']} | {row['data_wpisu']}</div>", unsafe_allow_html=True)
