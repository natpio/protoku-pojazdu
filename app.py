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
    except Exception as e:
        st.error(f"Błąd krytyczny konfiguracji JSON: {e}")
    return None

# =========================================================
# 2. KOMUNIKACJA Z BAZĄ SUPABASE (TRANSACTION POOLER)
# =========================================================
def get_connection():
    try:
        # Port 6543 i sslmode='require' są kluczowe dla stabilności w Streamlit Cloud
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
# 3. DESIGN VORTEZA 8.6 - FULL CSS & DARK SIDEBAR
# =========================================================
def apply_vorteza_design():
    try:
        with open('bg_vorteza.png', 'rb') as f:
            bg_base64 = base64.b64encode(f.read()).decode()
    except: bg_base64 = ""
    
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Michroma&family=Montserrat:wght@400;600&display=swap');
        
        /* GŁÓWNA APLIKACJA */
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.88), rgba(0,0,0,0.88)), url("data:image/png;base64,{bg_base64}");
            background-size: cover; background-attachment: fixed;
        }}

        /* STYLIZACJA BOCZNEGO PASKA (SIDEBAR) */
        section[data-testid="stSidebar"] {{
            background-color: rgba(15, 15, 15, 0.98) !important;
            border-right: 1px solid rgba(181, 136, 99, 0.3) !important;
        }}
        
        section[data-testid="stSidebar"] .stButton > button {{
            background: rgba(181, 136, 99, 0.1) !important;
            border: 1px solid #B58863 !important;
            color: #B58863 !important;
            font-size: 0.7rem !important;
        }}

        /* LOGO I TYPOGRAFIA */
        .logo-font {{
            font-family: 'Michroma', sans-serif !important;
            color: #B58863 !important;
            text-align: center; font-size: 1.4rem !important;
            letter-spacing: 4px !important; text-transform: uppercase;
            margin-bottom: 30px; margin-top: 10px;
        }}

        /* KARTY WPISÓW */
        .vorteza-card {{
            background: rgba(25, 25, 25, 0.85);
            border: 1px solid rgba(181, 136, 99, 0.2);
            border-left: 5px solid #B58863;
            border-radius: 4px; padding: 18px; margin-bottom: 12px;
        }}

        /* ALERTY DLA DYSPOZYTORA */
        .alert-box {{
            background: rgba(255, 75, 75, 0.12);
            border: 1px solid rgba(255, 75, 75, 0.4);
            color: #FF4B4B !important;
            padding: 8px; border-radius: 4px; margin: 4px 0;
            font-size: 0.82rem; font-weight: 600;
        }}

        .ok-box {{
            color: #28A745 !important;
            font-size: 0.78rem; margin: 2px 0; opacity: 0.8;
        }}

        /* PRZYCISKI GŁÓWNE */
        .stButton > button {{
            background: #B58863 !important;
            color: white !important; font-family: 'Michroma', sans-serif !important;
            width: 100%; border-radius: 2px !important;
            border: none !important; padding: 16px !important;
            letter-spacing: 2px; transition: 0.3s;
        }}
        
        .stButton > button:hover {{
            background: #966b4a !important;
            box-shadow: 0 0 15px rgba(181, 136, 99, 0.4);
        }}

        /* FIX DLA EXPANDERÓW */
        div[data-testid="stExpander"] svg {{ display: none !important; }}
        div[data-testid="stExpander"] summary span {{ color: transparent !important; font-size: 0px !important; }}
        .streamlit-expanderHeader {{
            background: rgba(181, 136, 99, 0.08) !important;
            border: 1px solid rgba(181, 136, 99, 0.3) !important;
            border-radius: 4px !important;
        }}
        
        /* OGÓLNE TEKSTY */
        label, p, span, h3 {{ font-family: 'Montserrat', sans-serif !important; color: #FFFFFF !important; }}
        
        /* UKRYWANIE ELEMENTÓW SYSTEMOWYCH */
        #MainMenu, footer, header {{visibility: hidden;}}
        .stDeployButton {{display:none;}}
        </style>
    """, unsafe_allow_html=True)

def show_logo():
    try:
        # Wyświetlanie logo z pliku lokalnego
        st.image('logo_vorteza.png', width=200)
    except:
        # Jeśli pliku nie ma, wyświetlamy stylowy tekst zastępczy
        st.markdown('<p class="logo-font">VORTEZA</p>', unsafe_allow_html=True)

# =========================================================
# 4. GŁÓWNA LOGIKA APLIKACJI
# =========================================================
st.set_page_config(page_title="VORTEZA LOGISTICS - SQM", layout="wide", page_icon="🚛")
apply_vorteza_design()

config = get_remote_config()

if "auth" not in st.session_state:
    st.session_state.auth = False

# --- EKRAN LOGOWANIA (SYSTEM ACCESS) ---
if not st.session_state.auth:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_l, col_mid, col_r = st.columns([1, 2, 1])
    
    with col_mid:
        st.markdown("<div class='vorteza-card' style='text-align:center;'>", unsafe_allow_html=True)
        show_logo()
        st.markdown("<p style='letter-spacing:3px; color:#B58863; font-size:0.8rem;'>SYSTEM ACCESS</p>", unsafe_allow_html=True)
        
        u = st.text_input("OPERATOR ID")
        p = st.text_input("SECURITY KEY", type="password")
        
        if st.button("AUTHORIZE"):
            if config and u in config["uzytkownicy"] and config["uzytkownicy"][u] == p:
                st.session_state.auth = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("ACCESS DENIED: INVALID CREDENTIALS")
        st.markdown("</div>", unsafe_allow_html=True)

# --- PANEL GŁÓWNY PO AUTORYZACJI ---
else:
    # Sidebar z Logo i Operatorem
    with st.sidebar:
        show_logo()
        st.markdown(f"<p style='text-align:center; color:#B58863; font-size:0.8rem; margin-top:-20px;'>OPERATOR: {st.session_state.user.upper()}</p>", unsafe_allow_html=True)
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        if st.button("TERMINATE SESSION"):
            st.session_state.auth = False
            st.rerun()

    # Taby główne
    tab1, tab2 = st.tabs(["📝 NEW PROTOCOL", "📊 DISPATCHER DASHBOARD"])

    # --- TAB 1: FORMULARZ PROTOKOŁU ---
    with tab1:
        st.markdown('<p class="logo-font">VEHICLE INSPECTION</p>', unsafe_allow_html=True)
        
        with st.form("inspection_form"):
            c1, c2 = st.columns(2)
            with c1:
                rej = st.text_input("LICENSE PLATE (NR REJESTRACYJNY)", placeholder="np. PO 12345")
                km = st.number_input("MILEAGE (PRZEBIEG KM)", step=1, value=0)
            with c2:
                st.info(f"Wypełniasz protokół jako: {st.session_state.user.upper()}")
                st.write(f"Data operacji: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

            wyniki = {}
            if config and "lista_kontrolna" in config:
                for kategoria, punkty in config["lista_kontrolna"].items():
                    with st.expander(f"► {kategoria.upper()}"):
                        wyniki[kategoria] = {}
                        # Ustawiamy 3 kolumny dla oszczędności miejsca w formularzu
                        cols = st.columns(2)
                        for idx, pt in enumerate(punkty):
                            target_col = cols[idx % 2]
                            with target_col:
                                val = st.checkbox(pt, key=f"check_{pt}", value=True)
                                wyniki[kategoria][pt] = val

            st.markdown("<br>", unsafe_allow_html=True)
            uwagi_text = st.text_area("ADDITIONAL OBSERVATIONS / DAMAGE DESCRIPTION", height=100)
            
            if st.form_submit_button("TRANSMIT AND ENCRYPT PROTOCOL"):
                if not rej or rej == "":
                    st.error("WPROWADŹ NUMER REJESTRACYJNY!")
                else:
                    with st.spinner("TRANSMITTING TO SECURE SERVER..."):
                        if save_to_supabase(rej, km, uwagi_text, wyniki, st.session_state.user):
                            st.success("PROTOCOL SAVED AND TRANSMITTED SUCCESSFULLY")
                            st.balloons()

    # --- TAB 2: DASHBOARD DYSPOZYTORA (HISTORIA I ALERTY) ---
    with tab2:
        st.markdown('<p class="logo-font">LOGISTICS MONITORING</p>', unsafe_allow_html=True)
        
        col_ref, col_empty = st.columns([1, 4])
        with col_ref:
            if st.button("REFRESH DATA"): st.rerun()
        
        logs = get_recent_protocols()
        
        if logs is not None and not logs.empty:
            for _, row in logs.iterrows():
                with st.container():
                    # Nagłówek wpisu w formie karty
                    st.markdown(f"""
                    <div class="vorteza-card">
                        <span style="color:#B58863; font-weight:600;">{row['created_at'].strftime('%d.%m.%Y %H:%M')}</span> | 
                        <span style="font-size:1.1rem; font-weight:bold; letter-spacing:1px;">🚗 {row['rejestracja']}</span> | 
                        👤 {row['operator_id']} | 🛣️ {row['przebieg']} KM
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Analiza braków w kategoriach
                    lista_danych = row['lista_kontrolna']
                    kategorie_cols = st.columns(len(lista_danych.keys()))
                    
                    for i, (kat, punkty) in enumerate(lista_danych.items()):
                        with kategorie_cols[i]:
                            st.markdown(f"<p style='color:#B58863; font-size:0.75rem; font-weight:600; border-bottom:1px solid #333; padding-bottom:3px;'>{kat.upper()}</p>", unsafe_allow_html=True)
                            for pt, stan in punkty.items():
                                if not stan:
                                    # Czerwony alert dla brakującego elementu
                                    st.markdown(f"<div class='alert-box'>❌ {pt}</div>", unsafe_allow_html=True)
                                else:
                                    # Subtelny zielony znacznik dla sprawnego elementu
                                    st.markdown(f"<div class='ok-box'>• {pt}</div>", unsafe_allow_html=True)
                    
                    if row['uwagi'] and row['uwagi'].strip() != "":
                        st.markdown(f"<div style='background:rgba(181,136,99,0.05); padding:10px; border-radius:4px; border:1px dashed rgba(181,136,99,0.3); font-size:0.85rem; color:#ddd;'><b>OBSERVATIONS:</b> {row['uwagi']}</div>", unsafe_allow_html=True)
                    
                    st.markdown("<br><hr style='border:0.5px solid rgba(255,255,255,0.05);'><br>", unsafe_allow_html=True)
        else:
            st.info("Brak zarejestrowanych protokołów w bazie danych.")

# =========================================================
# KONIEC KODU
# =========================================================
