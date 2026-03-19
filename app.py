import streamlit as st
import psycopg2
import json
import base64
import requests
import pandas as pd
from datetime import datetime

# =========================================================
# 1. KOMUNIKACJA Z BAZĄ (SUPABASE POOLER PORT 6543)
# =========================================================
def get_connection():
    try:
        # Port 6543 wymaga specyficznego formatu dla Poolera
        return psycopg2.connect(
            host=st.secrets["postgres"]["host"],
            port=st.secrets["postgres"]["port"],
            database=st.secrets["postgres"]["database"],
            user=st.secrets["postgres"]["user"],
            password=st.secrets["postgres"]["password"],
            sslmode="require",
            # Dodatkowy parametr pomagający zidentyfikować projekt (Tenant)
            options="-c project=twjjscfizxnvbxwxqcbw",
            connect_timeout=10
        )
    except Exception as e:
        st.error(f"BŁĄD POŁĄCZENIA Z BAZĄ: {e}")
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
            st.error(f"BŁĄD ZAPISU: {e}")
            return False
    return False

def get_recent_protocols(limit=10):
    conn = get_connection()
    if conn:
        try:
            query = "SELECT created_at, rejestracja, operator_id, lista_kontrolna, uwagi, przebieg FROM protokoly_vorteza ORDER BY created_at DESC LIMIT %s"
            df = pd.read_sql(query, conn, params=(limit,))
            conn.close()
            return df
        except: return None
    return None

# =========================================================
# 2. DESIGN VORTEZA 9.8 - NAPRAWIONY CSS
# =========================================================
def apply_vorteza_design():
    try:
        with open('bg_vorteza.png', 'rb') as f:
            bg_base64 = base64.b64encode(f.read()).decode()
            bg_style = f'background: linear-gradient(rgba(0,0,0,0.92), rgba(0,0,0,0.92)), url("data:image/png;base64,{bg_base64}");'
    except:
        bg_style = "background-color: #050505;"

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Michroma&family=Montserrat:wght@400;600&display=swap');
        
        .stApp {{
            {bg_style}
            background-size: cover;
            background-attachment: fixed;
        }}

        /* CIEMNY SIDEBAR */
        section[data-testid="stSidebar"] {{
            background-color: #050505 !important;
            border-right: 1px solid #B5886344 !important;
        }}

        .logo-font {{
            font-family: 'Michroma', sans-serif !important;
            color: #B58863 !important;
            text-align: center; font-size: 1.4rem !important;
            letter-spacing: 5px; text-transform: uppercase;
            margin: 20px 0;
        }}

        .vorteza-card {{
            background: rgba(20, 20, 20, 0.9);
            border: 1px solid #B5886333;
            border-left: 5px solid #B58863;
            border-radius: 4px; padding: 20px; margin-bottom: 15px;
        }}

        /* PRZYCISKI */
        .stButton > button {{
            background: #B58863 !important;
            color: white !important; font-family: 'Michroma', sans-serif !important;
            width: 100%; border-radius: 2px !important; padding: 16px !important;
            border: none !important;
        }}

        /* NAPRAWA EXPANDERÓW (USUNIĘCIE NAKŁADANIA SIĘ TEKSTU) */
        .streamlit-expanderHeader {{
            background-color: rgba(181, 136, 99, 0.1) !important;
            border: 1px solid rgba(181, 136, 99, 0.2) !important;
            color: white !important;
        }}
        
        /* UKRYWANIE ELEMENTÓW SYSTEMOWYCH */
        #MainMenu, footer, header {{visibility: hidden;}}
        .stDeployButton {{display:none;}}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. GŁÓWNA LOGIKA
# =========================================================
st.set_page_config(page_title="VORTEZA SQM", layout="wide")
apply_vorteza_design()

config = None
try:
    token = st.secrets["G_TOKEN"]["G_TOKEN"]
    res = requests.get(
        "https://api.github.com/repos/natpio/protoku-pojazdu/contents/lista_kontrolna.json",
        headers={"Authorization": f"token {token}"}
    )
    if res.status_code == 200:
        config = json.loads(base64.b64decode(res.json()['content']).decode('utf-8'))
except:
    st.error("Błąd konfiguracji GitHub.")

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<br><br><p class='logo-font'>VORTEZA</p>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<div class='vorteza-card'>", unsafe_allow_html=True)
        u = st.text_input("OPERATOR ID")
        p = st.text_input("SECURITY KEY", type="password")
        if st.button("AUTHORIZE"):
            if config and u in config["uzytkownicy"] and config["uzytkownicy"][u] == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("ACCESS DENIED")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    with st.sidebar:
        st.markdown("<p class='logo-font' style='font-size:1rem;'>VORTEZA</p>", unsafe_allow_html=True)
        st.write(f"USER: **{st.session_state.user.upper()}**")
        if st.button("LOGOUT"):
            st.session_state.auth = False
            st.rerun()

    tab1, tab2 = st.tabs(["📝 NOWY PROTOKÓŁ", "📊 HISTORIA"])

    with tab1:
        with st.form("inspection_form"):
            r_rej = st.text_input("REJESTRACJA")
            r_km = st.number_input("PRZEBIEG", step=1, value=0)
            
            wyniki = {}
            if config:
                for kat, punkty in config["lista_kontrolna"].items():
                    # PRZYWRÓCONY CZYSTY EXPANDER
                    with st.expander(f"➕ {kat.upper()}"):
                        wyniki[kat] = {}
                        for pt in punkty:
                            wyniki[kat][pt] = st.checkbox(pt, key=f"v_{pt}", value=False)
            
            r_uwagi = st.text_area("UWAGI / USZKODZENIA")
            if st.form_submit_button("ZAPISZ PROTOKÓŁ"):
                if r_rej:
                    if save_to_supabase(r_rej, r_km, r_uwagi, wyniki, st.session_state.user):
                        st.success("Zapisano!"); st.balloons()
                else:
                    st.warning("Podaj rejestrację!")

    with tab2:
        hist = get_recent_protocols()
        if hist is not None:
            for _, row in hist.iterrows():
                with st.container():
                    st.markdown(f"<div class='vorteza-card'><b>{row['rejestracja']}</b> | {row['operator_id']} | {row['created_at']}</div>", unsafe_allow_html=True)
                    st.divider()
