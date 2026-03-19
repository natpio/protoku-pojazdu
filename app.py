import streamlit as st
import psycopg2
import json
import base64
import requests
import pandas as pd
from datetime import datetime

# =========================================================
# 1. KONFIGURACJA GITHUB (LISTA KONTROLNA I UŻYTKOWNICY)
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
        st.error(f"Błąd krytyczny konfiguracji JSON: {e}")
    return None

# =========================================================
# 2. KOMUNIKACJA Z BAZĄ (SUPABASE POOLER PORT 6543)
# =========================================================
def get_connection():
    try:
        # Transaction Pooler wymaga sslmode='require' dla stabilności
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
            st.error(f"BŁĄD ZAPISU DO BAZY: {e}")
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
        except Exception as e:
            st.error(f"BŁĄD POBIERANIA HISTORII: {e}")
            return None
    return None

# =========================================================
# 3. DESIGN VORTEZA 8.9 - FULL CUSTOM CSS (DARK SIDEBAR)
# =========================================================
def apply_vorteza_design():
    try:
        with open('bg_vorteza.png', 'rb') as f:
            bg_base64 = base64.b64encode(f.read()).decode()
    except: bg_base64 = ""
    
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Michroma&family=Montserrat:wght@400;600&display=swap');
        
        /* GŁÓWNE TŁO */
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.92), rgba(0,0,0,0.92)), url("data:image/png;base64,{bg_base64}");
            background-size: cover; background-attachment: fixed;
        }}

        /* CIEMNY BOCZNY PASEK (SIDEBAR) */
        section[data-testid="stSidebar"] {{
            background-color: #080808 !important;
            border-right: 1px solid rgba(181, 136, 99, 0.3) !important;
        }}
        
        section[data-testid="stSidebar"] * {{
            color: #FFFFFF !important;
        }}

        /* LOGO I TYPOGRAFIA */
        .logo-font {{
            font-family: 'Michroma', sans-serif !important;
            color: #B58863 !important;
            text-align: center; font-size: 1.4rem !important;
            letter-spacing: 5px !important; text-transform: uppercase;
            margin-bottom: 30px;
        }}

        /* KARTY PROTOKOŁÓW */
        .vorteza-card {{
            background: rgba(15, 15, 15, 0.95);
            border: 1px solid rgba(181, 136, 99, 0.2);
            border-left: 5px solid #B58863;
            border-radius: 4px; padding: 20px; margin-bottom: 15px;
        }}

        /* ALERTY DLA DYSPOZYTORA */
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

        /* PRZYCISKI */
        .stButton > button {{
            background: #B58863 !important;
            color: white !important; font-family: 'Michroma', sans-serif !important;
            width: 100%; border-radius: 2px !important;
            border: none !important; padding: 16px !important;
            letter-spacing: 2px;
        }}
        
        /* FORMULARZ - CHECKBOXY */
        .stCheckbox label p {{
            font-size: 1rem !important;
            color: #ddd !important;
        }}

        /* UKRYWANIE ELEMENTÓW SYSTEMOWYCH */
        #MainMenu, footer, header {{visibility: hidden;}}
        .stDeployButton {{display:none;}}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 4. GŁÓWNA LOGIKA APLIKACJI
# =========================================================
st.set_page_config(page_title="VORTEZA LOGISTICS", layout="wide")
apply_vorteza_design()

config = get_remote_config()

if "auth" not in st.session_state:
    st.session_state.auth = False

# --- EKRAN LOGOWANIA ---
if not st.session_state.auth:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<p class='logo-font'>VORTEZA</p>", unsafe_allow_html=True)
        st.markdown("<div class='vorteza-card'>", unsafe_allow_html=True)
        u_input = st.text_input("OPERATOR ID")
        p_input = st.text_input("SECURITY KEY", type="password")
        if st.button("AUTHORIZE"):
            if config and u_input in config["uzytkownicy"] and config["uzytkownicy"][u_input] == p_input:
                st.session_state.auth, st.session_state.user = True, u_input
                st.rerun()
            else:
                st.error("ACCESS DENIED")
        st.markdown("</div>", unsafe_allow_html=True)

# --- PANEL PO ZALOGOWANIU ---
else:
    with st.sidebar:
        st.markdown("<p class='logo-font' style='font-size:1rem;'>VORTEZA</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;'>OPERATOR: {st.session_state.user.upper()}</p>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("TERMINATE SESSION"):
            st.session_state.auth = False
            st.rerun()

    tab1, tab2 = st.tabs(["📝 NOWY PROTOKÓŁ", "📊 PANEL DYSPOZYTORA"])

    # --- TAB 1: FORMULARZ (Wszystko domyślnie odznaczone) ---
    with tab1:
        st.markdown("<p class='logo-font'>VEHICLE INSPECTION</p>", unsafe_allow_html=True)
        with st.form("inspection_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                rej = st.text_input("LICENSE PLATE (NR REJESTRACYJNY)")
                km = st.number_input("MILEAGE (PRZEBIEG KM)", step=1, value=0)
            with col_b:
                st.write(f"OPERATOR: {st.session_state.user.upper()}")
                st.write(f"TIMESTAMP: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

            wyniki = {}
            if config and "lista_kontrolna" in config:
                for kategoria, punkty in config["lista_kontrolna"].items():
                    st.markdown(f"<h3 style='color:#B58863; font-size:1.1rem; border-bottom:1px solid #333;'>{kategoria.upper()}</h3>", unsafe_allow_html=True)
                    wyniki[kategoria] = {}
                    cols = st.columns(2)
                    for idx, pt in enumerate(punkty):
                        target_col = cols[idx % 2]
                        with target_col:
                            # value=False sprawia, że checkbox jest domyślnie PUSTY
                            val = st.checkbox(pt, key=f"check_{pt}", value=False)
                            wyniki[kategoria][pt] = val

            st.markdown("<br>", unsafe_allow_html=True)
            uwagi_text = st.text_area("ADDITIONAL OBSERVATIONS / DAMAGE DESCRIPTION")
            
            if st.form_submit_button("TRANSMIT PROTOCOL"):
                if not rej:
                    st.error("PLATE REQUIRED!")
                else:
                    if save_to_supabase(rej, km, uwagi_text, wyniki, st.session_state.user):
                        st.success("TRANSMITTED SUCCESSFULLY")
                        st.balloons()

    # --- TAB 2: PODGLĄD DLA DYSPOZYTORA ---
    with tab2:
        st.markdown("<p class='logo-font'>MONITORING CENTER</p>", unsafe_allow_html=True)
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
                    
                    l_k = row['lista_kontrolna']
                    k_cols = st.columns(len(l_k.keys()))
                    for i, (kat, pts) in enumerate(l_k.items()):
                        with k_cols[i]:
                            st.markdown(f"<p style='color:#B58863; font-size:0.7rem; border-bottom:1px solid #333;'>{kat.upper()}</p>", unsafe_allow_html=True)
                            for pt, stan in pts.items():
                                if not stan:
                                    st.markdown(f"<div class='alert-box'>❌ {pt}</div>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<div class='ok-box'>✅ {pt}</div>", unsafe_allow_html=True)
                    st.divider()
