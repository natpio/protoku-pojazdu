import streamlit as st
import psycopg2
import json
import base64
import requests
import pandas as pd
from datetime import datetime

# =========================================================
# 1. FUNKCJE BAZODANOWE (ZGODNE Z TWOIM SCHEMATEM)
# =========================================================

def get_connection():
    """Tworzy połączenie z Supabase używając parametrów z Twojego zrzutu ekranu."""
    try:
        # Wyciągamy ID projektu z nazwy użytkownika (część po kropce)
        user_parts = st.secrets["postgres"]["user"].split('.')
        project_id = user_parts[1] if len(user_parts) > 1 else "twjjscfizxnvbxwxqcbw"
        
        return psycopg2.connect(
            host=st.secrets["postgres"]["host"],
            port=st.secrets["postgres"]["port"],
            database=st.secrets["postgres"]["database"],
            user=st.secrets["postgres"]["user"],
            password=st.secrets["postgres"]["password"],
            sslmode="require",
            # To rozwiązuje błąd 'Tenant not found' widoczny na Twoim screenie
            options=f"-c endpoint={project_id}",
            connect_timeout=10
        )
    except Exception as e:
        st.error(f"BŁĄD POŁĄCZENIA: {e}")
        return None

def save_to_supabase(rejestracja, przebieg, uwagi, lista_wynikowa, operator):
    """Zapisuje dane do tabeli protokoly_vorteza widocznej na Twoim zrzucie."""
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            # Nazwy kolumn 1:1 z Twojego schematu bazy
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
    """Pobiera historię, używając kolumny data_wpisu z Twojego schematu."""
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
        except Exception as e:
            st.error(f"BŁĄD POBIERANIA HISTORII: {e}")
            return None
    return None

# =========================================================
# 2. INTERFEJS I STYLIZACJA (NAPRAWIONE LISTY ZWIJANE)
# =========================================================

def apply_vorteza_design():
    """Ustawia wygląd aplikacji. Naprawia błąd nakładania się tekstu."""
    bg_style = "background-color: #050505;"
    try:
        # Próba wczytania tła, jeśli plik istnieje w repozytorium
        with open('bg_vorteza.png', 'rb') as f:
            bg_base64 = base64.b64encode(f.read()).decode()
            bg_style = f'background: linear-gradient(rgba(0,0,0,0.92), rgba(0,0,0,0.92)), url("data:image/png;base64,{bg_base64}");'
    except:
        pass

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Michroma&family=Montserrat:wght@400;600&display=swap');
        
        /* Tło aplikacji */
        .stApp {{
            {bg_style}
            background-size: cover;
            background-attachment: fixed;
        }}

        /* Stylizacja paska bocznego */
        section[data-testid="stSidebar"] {{
            background-color: #080808 !important;
            border-right: 1px solid rgba(181, 136, 99, 0.3) !important;
        }}
        
        /* Naprawa Expandera (Listy zwijane) - usunięcie nakładania się */
        .streamlit-expanderHeader {{
            background-color: rgba(181, 136, 99, 0.1) !important;
            color: #B58863 !important;
            border: 1px solid rgba(181, 136, 99, 0.2) !important;
            font-family: 'Montserrat', sans-serif !important;
        }}

        .logo-font {{
            font-family: 'Michroma', sans-serif !important;
            color: #B58863 !important;
            text-align: center; font-size: 1.5rem !important;
            letter-spacing: 5px; text-transform: uppercase;
            margin: 20px 0;
        }}

        .vorteza-card {{
            background: rgba(15, 15, 15, 0.95);
            border: 1px solid rgba(181, 136, 99, 0.2);
            border-left: 5px solid #B58863;
            border-radius: 4px; padding: 20px; margin-bottom: 15px;
        }}

        .stButton > button {{
            background: #B58863 !important;
            color: white !important; font-family: 'Michroma', sans-serif !important;
            width: 100%; border-radius: 2px !important; padding: 16px !important;
            border: none !important;
        }}

        /* Ukrycie elementów Streamlit */
        #MainMenu, footer, header {{visibility: hidden;}}
        .stDeployButton {{display:none;}}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. LOGIKA APLIKACJI
# =========================================================

st.set_page_config(page_title="VORTEZA LOGISTICS", layout="wide")
apply_vorteza_design()

# Pobranie konfiguracji użytkowników i listy kontrolnej z GitHub
config = None
try:
    g_token = st.secrets["G_TOKEN"]["G_TOKEN"]
    res = requests.get(
        "https://api.github.com/repos/natpio/protoku-pojazdu/contents/lista_kontrolna.json",
        headers={"Authorization": f"token {g_token}"}
    )
    if res.status_code == 200:
        file_content = res.json()['content']
        config = json.loads(base64.b64decode(file_content).decode('utf-8'))
except Exception as e:
    st.error(f"Błąd konfiguracji GitHub: {e}")

# Zarządzanie sesją logowania
if "auth" not in st.session_state:
    st.session_state.auth = False

# --- EKRAN LOGOWANIA ---
if not st.session_state.auth:
    st.markdown("<br><br><p class='logo-font'>VORTEZA SYSTEM</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='vorteza-card'>", unsafe_allow_html=True)
        login = st.text_input("OPERATOR ID")
        pin = st.text_input("SECURITY KEY", type="password")
        if st.button("AUTHORIZE"):
            if config and login in config["uzytkownicy"] and config["uzytkownicy"][login] == pin:
                st.session_state.auth = True
                st.session_state.user = login
                st.rerun()
            else:
                st.error("ACCESS DENIED")
        st.markdown("</div>", unsafe_allow_html=True)

# --- PANEL GŁÓWNY PO ZALOGOWANIU ---
else:
    with st.sidebar:
        st.markdown("<p class='logo-font' style='font-size:1.1rem;'>VORTEZA</p>", unsafe_allow_html=True)
        st.write(f"OPERATOR: **{st.session_state.user.upper()}**")
        if st.button("LOGOUT"):
            st.session_state.auth = False
            st.rerun()

    tab1, tab2 = st.tabs(["📝 NOWY PROTOKÓŁ", "📊 MONITORING DANYCH"])

    # ZAKŁADKA 1: FORMULARZ
    with tab1:
        st.markdown("<p class='logo-font'>VEHICLE INSPECTION</p>", unsafe_allow_html=True)
        with st.form("main_inspection_form"):
            c1, c2 = st.columns(2)
            with c1:
                nr_rej = st.text_input("NUMER REJESTRACYJNY")
                przebieg_km = st.number_input("PRZEBIEG (KM)", step=1, value=0)
            with c2:
                st.write(f"DATA: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
                st.info("Status: Połączono z bazą SQM")

            pomiary = {}
            if config and "lista_kontrolna" in config:
                for kategoria, punkty in config["lista_kontrolna"].items():
                    # LISTA ZWIJANA (EXPANDER)
                    with st.expander(f"➕ {kategoria.upper()}", expanded=False):
                        pomiary[kategoria] = {}
                        # Generowanie pól wyboru (domyślnie odznaczone)
                        for pkt in punkty:
                            pomiary[kategoria][pkt] = st.checkbox(pkt, key=f"chk_{pkt}", value=False)

            komentarz = st.text_area("UWAGI I OPIS USZKODZEŃ")
            
            if st.form_submit_button("TRANSMITUJ PROTOKÓŁ"):
                if not nr_rej:
                    st.warning("WPISZ NUMER REJESTRACYJNY!")
                else:
                    success = save_to_supabase(nr_rej, przebieg_km, komentarz, pomiary, st.session_state.user)
                    if success:
                        st.success("PROTOKÓŁ ZAPISANY POMYŚLNIE")
                        st.balloons()

    # ZAKŁADKA 2: HISTORIA
    with tab2:
        st.markdown("<p class='logo-font'>LOGISTICS FEED</p>", unsafe_allow_html=True)
        if st.button("REFRESH FEED"):
            st.rerun()
        
        historia_df = get_recent_protocols()
        if historia_df is not None:
            for _, r in historia_df.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="vorteza-card">
                        <b>{r['rejestracja']}</b> | {r['operator_id']} | {r['data_wpisu'].strftime('%d.%m %H:%M')}
                    </div>
                    """, unsafe_allow_html=True)
