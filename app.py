import streamlit as st
import psycopg2
import json
import base64
import requests
import pandas as pd
from datetime import datetime

# =========================================================
# 1. KONFIGURACJA STRONY (MUSI BYĆ PIERWSZA)
# =========================================================
st.set_page_config(page_title="VORTEZA LOGISTICS", layout="wide")

# =========================================================
# 2. KOMUNIKACJA Z BAZĄ (Z OPTYMALIZACJĄ CZASU)
# =========================================================
def get_connection():
    try:
        user_parts = st.secrets["postgres"]["user"].split('.')
        project_id = user_parts[1] if len(user_parts) > 1 else "twjjscfizxnvbxwxqcbw"
        
        return psycopg2.connect(
            host=st.secrets["postgres"]["host"],
            port=st.secrets["postgres"]["port"],
            database=st.secrets["postgres"]["database"],
            user=st.secrets["postgres"]["user"],
            password=st.secrets["postgres"]["password"],
            sslmode="require",
            options=f"-c endpoint={project_id}",
            connect_timeout=5 # Zmniejszony timeout, by nie mrozić apki
        )
    except Exception as e:
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
            cur.execute(query, (rejestracja, przebieg, uwagi, json.dumps(lista_wynikowa), operator))
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Błąd zapisu: {e}")
            return False
    return False

@st.cache_data(ttl=60) # Cache na 60 sekund, by nie odpytywać bazy przy każdym kliknięciu
def get_recent_protocols(limit=10):
    conn = get_connection()
    if conn:
        try:
            query = """
                SELECT data_wpisu, rejestracja, operator_id, lista_kontrolna, uwagi, przebieg 
                FROM protokoly_vorteza 
                ORDER BY data_wpisu DESC LIMIT %s
            """
            df = pd.read_sql(query, conn, params=(limit,))
            conn.close()
            return df
        except: return None
    return None

# =========================================================
# 3. DESIGN I UKŁAD (NATYCHMIASTOWE RENDEROWANIE)
# =========================================================
def apply_vorteza_design():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Michroma&family=Montserrat:wght@400;600&display=swap');
        .stApp { background-color: #050505; }
        section[data-testid="stSidebar"] { background-color: #080808 !important; border-right: 1px solid #B5886344 !important; }
        .logo-font { font-family: 'Michroma', sans-serif; color: #B58863; text-align: center; font-size: 1.5rem; letter-spacing: 5px; text-transform: uppercase; margin: 20px 0; }
        .vorteza-card { background: rgba(15, 15, 15, 0.95); border: 1px solid #B5886333; border-left: 5px solid #B58863; border-radius: 4px; padding: 20px; margin-bottom: 15px; }
        .stButton > button { background: #B58863 !important; color: white !important; font-family: 'Michroma', sans-serif; width: 100%; padding: 16px !important; border: none; }
        .streamlit-expanderHeader { background-color: rgba(181, 136, 99, 0.1) !important; color: #B58863 !important; }
        #MainMenu, footer, header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

apply_vorteza_design()

# =========================================================
# 4. POBIERANIE CONFIGU (Z OBSŁUGĄ BŁĘDÓW)
# =========================================================
@st.cache_data(ttl=300) # Zapamiętaj listę kontrolną na 5 minut
def load_config():
    try:
        g_token = st.secrets["G_TOKEN"]["G_TOKEN"]
        url = "https://api.github.com/repos/natpio/protoku-pojazdu/contents/lista_kontrolna.json"
        res = requests.get(url, headers={"Authorization": f"token {g_token}"}, timeout=5)
        if res.status_code == 200:
            return json.loads(base64.b64decode(res.json()['content']).decode('utf-8'))
    except: return None
    return None

config = load_config()

# =========================================================
# 5. LOGIKA SESJI I INTERFEJS
# =========================================================
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<br><br><p class='logo-font'>VORTEZA SYSTEM</p>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='vorteza-card'>", unsafe_allow_html=True)
        login = st.text_input("OPERATOR ID")
        pin = st.text_input("SECURITY KEY", type="password")
        if st.button("AUTHORIZE"):
            if config and login in config["uzytkownicy"] and config["uzytkownicy"][login] == pin:
                st.session_state.auth, st.session_state.user = True, login
                st.rerun()
            else: st.error("ACCESS DENIED")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    with st.sidebar:
        st.markdown("<p class='logo-font' style='font-size:1.1rem;'>VORTEZA</p>", unsafe_allow_html=True)
        st.write(f"OPERATOR: **{st.session_state.user.upper()}**")
        if st.button("LOGOUT"):
            st.session_state.auth = False
            st.rerun()

    tab1, tab2 = st.tabs(["📝 NOWY PROTOKÓŁ", "📊 MONITORING"])

    with tab1:
        st.markdown("<p class='logo-font'>VEHICLE INSPECTION</p>", unsafe_allow_html=True)
        with st.form("form_v11"):
            c1, c2 = st.columns(2)
            with c1:
                nr_rej = st.text_input("NUMER REJESTRACYJNY")
                km = st.number_input("PRZEBIEG (KM)", step=1, value=0)
            with c2:
                st.write(f"DATA: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

            pomiary = {}
            if config and "lista_kontrolna" in config:
                for kat, punkty in config["lista_kontrolna"].items():
                    with st.expander(f"➕ {kat.upper()}"):
                        pomiary[kat] = {}
                        for pkt in punkty:
                            pomiary[kat][pkt] = st.checkbox(pkt, key=f"c_{pkt}", value=False)
            
            uwagi = st.text_area("UWAGI I OPIS USZKODZEŃ")
            if st.form_submit_button("WYŚLIJ"):
                if nr_rej and save_to_supabase(nr_rej, km, uwagi, pomiary, st.session_state.user):
                    st.success("ZAPISANO"); st.balloons()

    with tab2:
        st.markdown("<p class='logo-font'>LOGISTICS FEED</p>", unsafe_allow_html=True)
        historia = get_recent_protocols()
        if historia is not None:
            for _, r in historia.iterrows():
                with st.container():
                    st.markdown(f"<div class='vorteza-card'><b>{r['rejestracja']}</b> | {r['operator_id']} | {r['data_wpisu'].strftime('%d.%m %H:%M')}</div>", unsafe_allow_html=True)
