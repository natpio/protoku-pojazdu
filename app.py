import streamlit as st
import psycopg2
import json
import base64
import requests
import pandas as pd
from datetime import datetime

# =========================================================
# 1. KONFIGURACJA STRONY (NATYCHMIASTOWY START)
# =========================================================
st.set_page_config(page_title="VORTEZA-BASE", layout="centered")

# =========================================================
# 2. DESIGN VORTEZA 8.0 - TWOJA STYLIZACJA
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
            background-color: #050505;
        }}

        .logo-font {{
            font-family: 'Michroma', sans-serif !important;
            color: #B58863 !important;
            text-align: center; font-size: 1.5rem !important;
            letter-spacing: 5px !important; text-transform: uppercase;
            margin-bottom: 25px;
        }}

        /* --- FIX DLA EXPANDERÓW (strzałki _arrow_right) --- */
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
# 3. POŁĄCZENIE Z BAZĄ (FIX DLA PORTU 6543)
# =========================================================
def get_connection():
    try:
        # Dane z Twoich secrets
        p_secrets = st.secrets["postgres"]
        # Wyciągamy ID projektu z nazwy użytkownika (część po kropce)
        project_id = p_secrets["user"].split('.')[1]
        
        return psycopg2.connect(
            host=p_secrets["host"],
            port=p_secrets["port"],
            database=p_secrets["database"],
            user=p_secrets["user"],
            password=p_secrets["password"],
            sslmode="require",
            # TA LINIA JEST NIEZBĘDNA DLA PORTU 6543 (Pooler)
            options=f"-c project={project_id}",
            connect_timeout=10
        )
    except Exception as e:
        st.error(f"DATABASE CONNECTION ERROR: {e}")
        return None

# =========================================================
# 4. GITHUB CONFIG (ZABEZPIECZONY TIMEOUTEM)
# =========================================================
@st.cache_data(ttl=600)
def get_config_from_github():
    try:
        token = st.secrets["G_TOKEN"]["G_TOKEN"]
        url = "https://api.github.com/repos/natpio/protoku-pojazdu/contents/lista_kontrolna.json"
        headers = {"Authorization": f"token {token}"}
        # Timeout 5 sekund, żeby apka nie wisiała 4 minuty
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            content = res.json()
            return json.loads(base64.b64decode(content['content']).decode('utf-8'))
    except:
        pass
    # Zapasowe dane, gdyby GitHub padł
    return {"uzytkownicy": {"admin": "vorteza"}, "lista_kontrolna": {"Ogólne": ["Brak punktów w pliku JSON"]}}

# =========================================================
# 5. LOGIKA APLIKACJI
# =========================================================
apply_vorteza_design()
data_config = get_config_from_github()

if "auth" not in st.session_state:
    st.session_state.auth = False

# --- EKRAN LOGOWANIA ---
if not st.session_state.auth:
    st.markdown("<br><br><div class='vorteza-card' style='text-align:center;'><p class='logo-font'>SYSTEM ACCESS</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        u_input = st.text_input("OPERATOR ID")
        p_input = st.text_input("SECURITY KEY", type="password")
        if st.button("AUTHORIZE"):
            if u_input in data_config.get("uzytkownicy", {}) and data_config["uzytkownicy"][u_input] == p_input:
                st.session_state.auth = True
                st.session_state.user = u_input
                st.rerun()
            else:
                st.error("ACCESS DENIED")

# --- PANEL GŁÓWNY ---
else:
    tab1, tab2 = st.tabs(["📝 NOWY PROTOKÓŁ", "📊 HISTORIA"])

    with tab1:
        st.markdown('<p class="logo-font">VORTEZA - BASE</p>', unsafe_allow_html=True)
        
        with st.form("main_form"):
            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            rej = st.text_input("LICENSE PLATE")
            km = st.number_input("MILEAGE (KM)", step=1, value=0)
            st.markdown('</div>', unsafe_allow_html=True)

            wyniki_kontroli = {}
            if "lista_kontrolna" in data_config:
                for kat, punkty in data_config["lista_kontrolna"].items():
                    with st.expander(f"► {kat.upper()}"):
                        wyniki_kontroli[kat] = {}
                        for pt in punkty:
                            wyniki_kontroli[kat][pt] = st.checkbox(pt, key=f"chk_{kat}_{pt}")

            st.markdown('<br>', unsafe_allow_html=True)
            with st.expander("► OBSERVATIONS & NOTES"):
                obs = st.text_area("Notes...", height=100)

            st.markdown('<br>', unsafe_allow_html=True)
            if st.form_submit_button("GENERATE AND ENCRYPT PROTOCOL"):
                if not rej:
                    st.error("Plate required!")
                else:
                    # Łączymy się z bazą dopiero teraz (nie blokuje startu apki)
                    db_conn = get_connection()
                    if db_conn:
                        try:
                            cur = db_conn.cursor()
                            query = """
                                INSERT INTO protokoly_vorteza 
                                (rejestracja, przebieg, uwagi, lista_kontrolna, operator_id) 
                                VALUES (%s, %s, %s, %s, %s)
                            """
                            cur.execute(query, (rej, km, obs, json.dumps(wyniki_kontroli), st.session_state.user))
                            db_conn.commit()
                            st.success("PROTOCOL TRANSMITTED"); st.balloons()
                            cur.close()
                            db_conn.close()
                        except Exception as e:
                            st.error(f"ZAPIS DO BAZY NIEUDANY: {e}")

    with tab2:
        st.markdown('<p class="logo-font">LOGISTICS FEED</p>', unsafe_allow_html=True)
        if st.button("REFRESH"):
            st.rerun()
            
        db_conn = get_connection()
        if db_conn:
            try:
                query = "SELECT data_wpisu, rejestracja, operator_id FROM protokoly_vorteza ORDER BY data_wpisu DESC LIMIT 10"
                df = pd.read_sql(query, db_conn)
                for _, row in df.iterrows():
                    st.markdown(f"""
                        <div class='vorteza-card'>
                            <b>{row['rejestracja']}</b> | {row['operator_id']} | {row['data_wpisu']}
                        </div>
                    """, unsafe_allow_html=True)
                db_conn.close()
            except:
                st.info("Brak wpisów w historii.")
