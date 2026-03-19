import streamlit as st
import psycopg2
import json
import base64
import requests
import pandas as pd
from datetime import datetime

# =========================================================
# 1. KONFIGURACJA I POBIERANIE DANYCH Z JSON (GITHUB)
# =========================================================
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
    except: pass
    return None

# =========================================================
# 2. KOMUNIKACJA Z BAZĄ (SUPABASE)
# =========================================================
def get_connection():
    try:
        return psycopg2.connect(
            host=st.secrets["postgres"]["host"],
            port=st.secrets["postgres"]["port"],
            database=st.secrets["postgres"]["database"],
            user=st.secrets["postgres"]["user"],
            password=st.secrets["postgres"]["password"],
            connect_timeout=10
        )
    except Exception as e:
        st.error(f"DB ERROR: {e}")
        return None

def save_to_supabase(rejestracja, przebieg, uwagi, lista_wynikowa, operator):
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            query = "INSERT INTO protokoly_vorteza (rejestracja, przebieg, uwagi, lista_kontrolna, operator_id) VALUES (%s, %s, %s, %s, %s)"
            cur.execute(query, (rejestracja, przebieg, uwagi, json.dumps(lista_wynikowa), operator))
            conn.commit()
            cur.close()
            conn.close()
            return True
        except: return False
    return False

def get_recent_protocols(limit=10):
    conn = get_connection()
    if conn:
        try:
            query = f"SELECT created_at, rejestracja, operator_id, lista_kontrolna, uwagi, przebieg FROM protokoly_vorteza ORDER BY created_at DESC LIMIT {limit}"
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except: return None
    return None

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
        }}
        .vorteza-card {{
            background: rgba(25, 25, 25, 0.8);
            border: 1px solid rgba(181, 136, 99, 0.3);
            border-radius: 4px; padding: 15px; margin-bottom: 10px;
        }}
        .alert-box {{
            background: rgba(255, 0, 0, 0.1);
            border-left: 5px solid #FF4B4B;
            padding: 10px; margin: 5px 0;
            font-size: 0.85rem;
        }}
        .ok-box {{
            background: rgba(0, 255, 0, 0.05);
            border-left: 5px solid #28A745;
            padding: 5px 10px; margin: 2px 0;
            font-size: 0.8rem; color: #aaa;
        }}
        .stButton > button {{
            background: #B58863 !important; color: white !important;
            font-family: 'Michroma', sans-serif !important; width: 100%;
        }}
        label, p, span, h3 {{ font-family: 'Montserrat', sans-serif !important; color: #FFFFFF !important; }}
        div[data-testid="stExpander"] svg {{ display: none !important; }}
        .streamlit-expanderHeader {{ background: rgba(181, 136, 99, 0.1) !important; border: 1px solid #B58863 !important; }}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 4. LOGIKA GŁÓWNA
# =========================================================
st.set_page_config(page_title="VORTEZA LOGISTICS", layout="wide")
apply_vorteza_design()

config_data = get_remote_config()

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<br><br><div class='vorteza-card' style='text-align:center;'><p class='logo-font'>SYSTEM ACCESS</p></div>", unsafe_allow_html=True)
    u = st.text_input("OPERATOR ID")
    p = st.text_input("SECURITY KEY", type="password")
    if st.button("AUTHORIZE"):
        if config_data and u in config_data["uzytkownicy"] and config_data["uzytkownicy"][u] == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
else:
    # TABS: Formularz vs Panel Dyspozytora
    tab1, tab2 = st.tabs(["📝 NOWY PROTOKÓŁ", "📊 PANEL DYSPOZYTORA"])

    with tab1:
        st.markdown('<p class="logo-font">VORTEZA - PROTOCOL</p>', unsafe_allow_html=True)
        with st.form("main_form"):
            col1, col2 = st.columns(2)
            with col1:
                rej = st.text_input("LICENSE PLATE")
                km = st.number_input("MILEAGE (KM)", step=1, value=0)
            with col2:
                st.write(f"**OPERATOR:** {st.session_state.user.upper()}")
                st.write(f"**DATE:** {datetime.now().strftime('%Y-%m-%d')}")

            wyniki_kontroli = {}
            if config_data and "lista_kontrolna" in config_data:
                for kategoria, punkty in config_data["lista_kontrolna"].items():
                    with st.expander(f"► {kategoria.upper()}"):
                        wyniki_kontroli[kategoria] = {}
                        for pt in punkty:
                            stan = st.checkbox(pt, key=f"chk_{pt}", value=True) # Domyślnie zaznaczone jako OK
                            wyniki_kontroli[kategoria][pt] = stan

            obs = st.text_area("ADDITIONAL OBSERVATIONS")
            if st.form_submit_button("SAVE PROTOCOL"):
                if not rej: st.error("Plate required!")
                else:
                    if save_to_supabase(rej, km, obs, wyniki_kontroli, st.session_state.user):
                        st.success("PROTOCOL TRANSMITTED"); st.balloons()

    with tab2:
        st.markdown('<p class="logo-font">DISPATCHER DASHBOARD</p>', unsafe_allow_html=True)
        if st.button("REFRESH DATA"): st.rerun()
        
        data_logs = get_recent_protocols()
        if data_logs is not None:
            for idx, row in data_logs.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="vorteza-card">
                        <span style="color:#B58863; font-weight:bold;">{row['created_at'].split('.')[0]}</span> | 
                        <span style="font-size:1.2rem;">🚗 {row['rejestracja']}</span> | 
                        👤 {row['operator_id']} | 🛣️ {row['przebieg']} km
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Logika wykrywania braków
                    lista = row['lista_kontrolna']
                    cols = st.columns(len(lista.keys()))
                    
                    for i, (kat, punkty) in enumerate(lista.items()):
                        with cols[i]:
                            st.write(f"**{kat}**")
                            for pt, stan in punkty.items():
                                if not stan:
                                    st.markdown(f"<div class='alert-box'>❌ {pt}</div>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<div class='ok-box'>✅ {pt}</div>", unsafe_allow_html=True)
                    
                    if row['uwagi']:
                        st.warning(f"UWAGI: {row['uwagi']}")
                    st.divider()
        else:
            st.info("Brak protokołów w bazie.")

    if st.sidebar.button("LOGOUT"):
        st.session_state.auth = False
        st.rerun()
