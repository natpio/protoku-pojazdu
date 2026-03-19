import streamlit as st
import psycopg2
import json
import base64
import requests
import pandas as pd
from datetime import datetime

# =========================================================
# 1. POBIERANIE KONFIGURACJI Z TWOJEGO PLIKU JSON
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
    except Exception as e:
        st.error(f"Błąd krytyczny konfiguracji: {e}")
    return None

# =========================================================
# 2. KOMUNIKACJA Z BAZĄ SUPABASE (TRANSACTION POOLER)
# =========================================================
def get_connection():
    try:
        # Korzystamy z portu 6543 i sslmode='require' dla stabilności w chmurze
        return psycopg2.connect(
            host=st.secrets["postgres"]["host"],
            port=st.secrets["postgres"]["port"],
            database=st.secrets["postgres"]["database"],
            user=st.secrets["postgres"]["user"],
            password=st.secrets["postgres"]["password"],
            sslmode="require",
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
            st.error(f"BŁĄD TRANSMISJI: {e}")
            return False
    return False

def get_recent_protocols(limit=15):
    conn = get_connection()
    if conn:
        try:
            query = f"""
                SELECT created_at, rejestracja, operator_id, lista_kontrolna, uwagi, przebieg 
                FROM protokoly_vorteza 
                ORDER BY created_at DESC LIMIT {limit}
            """
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except: return None
    return None

# =========================================================
# 3. DESIGN VORTEZA 8.5 - FULL CSS & BRANDING
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
            margin-bottom: 20px;
        }}

        .vorteza-card {{
            background: rgba(25, 25, 25, 0.85);
            border: 1px solid rgba(181, 136, 99, 0.3);
            border-left: 5px solid #B58863;
            border-radius: 4px; padding: 15px; margin-bottom: 10px;
        }}

        .alert-box {{
            background: rgba(255, 75, 75, 0.15);
            border: 1px solid #FF4B4B;
            color: #FF4B4B !important;
            padding: 8px; border-radius: 4px; margin: 4px 0;
            font-size: 0.85rem; font-weight: 600;
        }}

        .ok-box {{
            color: #28A745 !important;
            font-size: 0.8rem; margin: 2px 0;
        }}

        .stButton > button {{
            background: #B58863 !important;
            color: white !important; font-family: 'Michroma', sans-serif !important;
            width: 100%; border-radius: 2px !important;
            border: none !important; padding: 15px !important;
            letter-spacing: 2px;
        }}

        div[data-testid="stExpander"] svg {{ display: none !important; }}
        div[data-testid="stExpander"] summary span {{ color: transparent !important; font-size: 0px !important; }}
        .streamlit-expanderHeader {{
            background: rgba(181, 136, 99, 0.1) !important;
            border: 1px solid rgba(181, 136, 99, 0.4) !important;
        }}
        
        label, p, span, h3 {{ font-family: 'Montserrat', sans-serif !important; color: #FFFFFF !important; }}
        #MainMenu, footer, header {{visibility: hidden;}}
        .stDeployButton {{display:none;}}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 4. LOGIKA APLIKACJI
# =========================================================
st.set_page_config(page_title="VORTEZA LOGISTICS", layout="wide", page_icon="🚛")
apply_vorteza_design()

config = get_remote_config()

if "auth" not in st.session_state: st.session_state.auth = False

# --- EKRAN LOGOWANIA ---
if not st.session_state.auth:
    st.markdown("<br><br><div class='vorteza-card' style='text-align:center;'><p class='logo-font'>SYSTEM ACCESS</p></div>", unsafe_allow_html=True)
    col_l, col_r = st.columns([1,1])
    with col_l: u = st.text_input("OPERATOR ID")
    with col_r: p = st.text_input("SECURITY KEY", type="password")
    
    if st.button("AUTHORIZE"):
        if config and u in config["uzytkownicy"] and config["uzytkownicy"][u] == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else:
            st.error("ACCESS DENIED")

# --- APLIKACJA PO ZALOGOWANIU ---
else:
    tab1, tab2 = st.tabs(["📝 NEW PROTOCOL", "📊 DISPATCHER PANEL"])

    # --- TAB 1: FORMULARZ ---
    with tab1:
        st.markdown('<p class="logo-font">VORTEZA - PROTOCOL</p>', unsafe_allow_html=True)
        with st.form("main_form"):
            c1, c2 = st.columns(2)
            with c1:
                rej = st.text_input("LICENSE PLATE")
                km = st.number_input("MILEAGE (KM)", step=1, value=0)
            with c2:
                st.write(f"**OPERATOR:** {st.session_state.user.upper()}")
                st.write(f"**TIMESTAMP:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")

            wyniki = {}
            if config and "lista_kontrolna" in config:
                for kat, punkty in config["lista_kontrolna"].items():
                    with st.expander(f"► {kat.upper()}"):
                        wyniki[kat] = {}
                        for pt in punkty:
                            val = st.checkbox(pt, key=f"form_{pt}", value=True)
                            wyniki[kat][pt] = val

            uwagi_text = st.text_area("ADDITIONAL OBSERVATIONS / DAMAGE DESCRIPTION")
            
            if st.form_submit_button("TRANSMIT PROTOCOL"):
                if not rej: st.error("PLATE REQUIRED")
                else:
                    with st.spinner("Processing..."):
                        if save_to_supabase(rej, km, uwagi_text, wyniki, st.session_state.user):
                            st.success("PROTOCOL SAVED IN SUPABASE")
                            st.balloons()

    # --- TAB 2: PODGLĄD DLA DYSPOZYTORA ---
    with tab2:
        st.markdown('<p class="logo-font">DISPATCHER DASHBOARD</p>', unsafe_allow_html=True)
        if st.button("REFRESH DATABASE"): st.rerun()
        
        logs = get_recent_protocols()
        if logs is not None:
            for _, row in logs.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="vorteza-card">
                        <span style="color:#B58863;">{row['created_at'].strftime('%H:%M | %d.%m.%Y')}</span> | 
                        <span style="font-size:1.1rem; font-weight:bold;">🚗 {row['rejestracja']}</span> | 
                        👤 {row['operator_id']} | 🛣️ {row['przebieg']} KM
                    </div>
                    """, unsafe_allow_html=True)
                    
                    lista = row['lista_kontrolna']
                    cols = st.columns(len(lista.keys()))
                    
                    for i, (kat, punkty) in enumerate(lista.items()):
                        with cols[i]:
                            st.markdown(f"<p style='color:#B58863; font-size:0.7rem; border-bottom:1px solid #333;'>{kat.upper()}</p>", unsafe_allow_html=True)
                            for pt, stan in punkty.items():
                                if not stan:
                                    st.markdown(f"<div class='alert-box'>❌ {pt}</div>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<div class='ok-box'>• {pt}</div>", unsafe_allow_html=True)
                    
                    if row['uwagi']:
                        st.info(f"KOMENTARZ: {row['uwagi']}")
                    st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("No data found.")

    if st.sidebar.button("TERMINATE SESSION"):
        st.session_state.auth = False
        st.rerun()
