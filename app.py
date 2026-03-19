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
        # Wykorzystujemy Transaction Pooler (Port 6543)
        # UWAGA: Parametr 'endpoint' jest kluczowy przy błędach "Tenant not found"
        return psycopg2.connect(
            host=st.secrets["postgres"]["host"],
            port=st.secrets["postgres"]["port"],
            database=st.secrets["postgres"]["database"],
            user=st.secrets["postgres"]["user"],
            password=st.secrets["postgres"]["password"],
            sslmode="require",
            options=f"-c endpoint={st.secrets['postgres']['user'].split('.')[1]}",
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
            st.error(f"BŁĄD ZAPISU DANYCH: {e}")
            return False
    return False

def get_recent_protocols(limit=15):
    conn = get_connection()
    if conn:
        try:
            query = """
                SELECT created_at, rejestracja, operator_id, lista_kontrolna, uwagi, przebieg 
                FROM protokoly_vorteza 
                ORDER BY created_at DESC LIMIT %s
            """
            df = pd.read_sql(query, conn, params=(limit,))
            conn.close()
            return df
        except Exception as e:
            st.error(f"BŁĄD POBIERANIA HISTORII: {e}")
            return None
    return None

# =========================================================
# 2. DESIGN VORTEZA 10.0 - CZYSTY I KOMPLETNY
# =========================================================
def apply_vorteza_design():
    # Próba wczytania tła
    bg_style = ""
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

        /* CIEMNY SIDEBAR - NAPRAWIONY */
        section[data-testid="stSidebar"] {{
            background-color: #080808 !important;
            border-right: 1px solid rgba(181, 136, 99, 0.3) !important;
        }}
        
        section[data-testid="stSidebar"] * {{
            color: #FFFFFF !important;
        }}

        .logo-font {{
            font-family: 'Michroma', sans-serif !important;
            color: #B58863 !important;
            text-align: center; font-size: 1.4rem !important;
            letter-spacing: 5px !important; text-transform: uppercase;
            margin-bottom: 30px;
        }}

        .vorteza-card {{
            background: rgba(15, 15, 15, 0.95);
            border: 1px solid rgba(181, 136, 99, 0.2);
            border-left: 5px solid #B58863;
            border-radius: 4px; padding: 20px; margin-bottom: 15px;
        }}

        /* STYLIZACJA ROZWIJANYCH LIST - BRAK NACHODZENIA */
        .streamlit-expanderHeader {{
            background-color: rgba(181, 136, 99, 0.1) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(181, 136, 99, 0.2) !important;
            font-family: 'Montserrat', sans-serif !important;
            padding: 10px !important;
        }}
        
        div[data-testid="stExpander"] {{
            background: transparent !important;
            border: none !important;
        }}

        .stButton > button {{
            background: #B58863 !important;
            color: white !important; font-family: 'Michroma', sans-serif !important;
            width: 100%; border-radius: 2px !important;
            border: none !important; padding: 16px !important;
            letter-spacing: 2px;
        }}
        
        /* ALERTY DLA DYSPOZYTORA */
        .alert-box {{
            background: rgba(255, 75, 75, 0.1);
            border: 1px solid #FF4B4B;
            color: #FF4B4B !important;
            padding: 8px; border-radius: 4px; margin: 4px 0;
            font-size: 0.85rem; font-weight: 600;
        }}

        .ok-box {{
            color: #28A745 !important;
            font-size: 0.8rem; margin: 2px 0;
        }}

        /* UKRYWANIE ELEMENTÓW SYSTEMOWYCH */
        #MainMenu, footer, header {{visibility: hidden;}}
        .stDeployButton {{display:none;}}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. GŁÓWNA LOGIKA
# =========================================================
st.set_page_config(page_title="VORTEZA LOGISTICS", layout="wide")
apply_vorteza_design()

# Pobieranie konfiguracji z GitHub
config = None
try:
    token = st.secrets["G_TOKEN"]["G_TOKEN"]
    url = "https://api.github.com/repos/natpio/protoku-pojazdu/contents/lista_kontrolna.json"
    res = requests.get(url, headers={"Authorization": f"token {token}"})
    if res.status_code == 200:
        config = json.loads(base64.b64decode(res.json()['content']).decode('utf-8'))
except:
    st.error("Błąd: Nie można połączyć się z GitHub (sprawdź G_TOKEN).")

if "auth" not in st.session_state:
    st.session_state.auth = False

# --- LOGOWANIE ---
if not st.session_state.auth:
    st.markdown("<br><br><p class='logo-font'>VORTEZA SYSTEM</p>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<div class='vorteza-card'>", unsafe_allow_html=True)
        u_id = st.text_input("OPERATOR ID")
        u_key = st.text_input("SECURITY KEY", type="password")
        if st.button("AUTHORIZE"):
            if config and u_id in config["uzytkownicy"] and config["uzytkownicy"][u_id] == u_key:
                st.session_state.auth, st.session_state.user = True, u_id
                st.rerun()
            else:
                st.error("NIEPRAWIDŁOWE DANE")
        st.markdown("</div>", unsafe_allow_html=True)

# --- PANEL OPERACYJNY ---
else:
    with st.sidebar:
        st.markdown("<p class='logo-font' style='font-size:1rem;'>VORTEZA</p>", unsafe_allow_html=True)
        st.write(f"OPERATOR: **{st.session_state.user.upper()}**")
        if st.button("WYLOGUJ"):
            st.session_state.auth = False
            st.rerun()

    tab1, tab2 = st.tabs(["📝 NOWY PROTOKÓŁ", "📊 MONITORING"])

    with tab1:
        st.markdown("<p class='logo-font'>VEHICLE INSPECTION</p>", unsafe_allow_html=True)
        with st.form("inspection_v10"):
            col_a, col_b = st.columns(2)
            with col_a:
                rej = st.text_input("NUMER REJESTRACYJNY")
                km = st.number_input("PRZEBIEG (KM)", step=1, value=0)
            with col_b:
                st.write(f"DATA: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
                st.info("Status: Połączono z SQM Database")

            wyniki = {}
            if config and "lista_kontrolna" in config:
                for kategoria, punkty in config["lista_kontrolna"].items():
                    # LISTA ZWIJANA (ST.EXPANDER) - BEZ KONFLIKTÓW CSS
                    with st.expander(f"➕ {kategoria.upper()}", expanded=False):
                        wyniki[kategoria] = {}
                        for punkt in punkty:
                            # value=False -> Domyślnie odznaczone
                            wyniki[kategoria][punkt] = st.checkbox(punkt, key=f"v_{punkt}", value=False)

            uwagi = st.text_area("UWAGI / OPIS USZKODZEŃ")
            
            if st.form_submit_button("ZATWIERDŹ I TRANSMITUJ"):
                if not rej:
                    st.warning("WPISZ NUMER REJESTRACYJNY!")
                else:
                    if save_to_supabase(rej, km, uwagi, wyniki, st.session_state.user):
                        st.success("PROTOKÓŁ ZAPISANY")
                        st.balloons()

    with tab2:
        st.markdown("<p class='logo-font'>LOGISTICS FEED</p>", unsafe_allow_html=True)
        if st.button("REFRESH FEED"): st.rerun()
        
        df = get_recent_protocols()
        if df is not None:
            for _, row in df.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="vorteza-card">
                        <b>{row['rejestracja']}</b> | {row['operator_id']} | {row['created_at'].strftime('%d.%m %H:%M')} | {row['przebieg']} KM
                    </div>
                    """, unsafe_allow_html=True)
                    
                    l_k = row['lista_kontrolna']
                    cols_h = st.columns(len(l_k.keys()))
                    for i, (kat, pts) in enumerate(l_k.items()):
                        with cols_h[i]:
                            st.markdown(f"<p style='color:#B58863; font-size:0.7rem;'>{kat.upper()}</p>", unsafe_allow_html=True)
                            for p, stan in pts.items():
                                if not stan:
                                    st.markdown(f"<div class='alert-box'>❌ {p}</div>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<div class='ok-box'>✅ {p}</div>", unsafe_allow_html=True)
                    st.divider()
