import streamlit as st
import psycopg2
import json
import base64
from datetime import datetime

# =========================================================
# 1. KONFIGURACJA BAZY DANYCH (SUPABASE)
# =========================================================
def get_connection():
    try:
        conn = psycopg2.connect(
            host=st.secrets["postgres"]["host"],
            port=st.secrets["postgres"]["port"],
            database=st.secrets["postgres"]["database"],
            user=st.secrets["postgres"]["user"],
            password=st.secrets["postgres"]["password"],
            connect_timeout=10
        )
        return conn
    except Exception as e:
        st.error(f"DATABASE CONNECTION ERROR: {e}")
        return None

def save_to_supabase(rejestracja, przebieg, uwagi, lista_kontrolna, operator):
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            query = """
                INSERT INTO protokoly_vorteza 
                (rejestracja, przebieg, uwagi, lista_kontrolna, operator_id) 
                VALUES (%s, %s, %s, %s, %s)
            """
            cur.execute(query, (
                rejestracja, 
                przebieg, 
                uwagi, 
                json.dumps(lista_kontrolna), 
                operator
            ))
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            st.error(f"ENCRYPTION/TRANSMISSION ERROR: {e}")
            return False
    return False

# =========================================================
# 2. DESIGN VORTEZA 8.0 - FULL CSS STYLING
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
            margin-bottom: 25px;
        }}

        /* --- KLUCZOWA NAPRAWA BLEDU _arrow_right --- */
        div[data-testid="stExpander"] svg {{ display: none !important; }}
        div[data-testid="stExpander"] summary span {{ color: transparent !important; font-size: 0px !important; }}

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
# 3. LOGIKA APLIKACJI & DASHBOARD
# =========================================================
st.set_page_config(page_title="VORTEZA - SQM LOGISTICS", layout="centered")
apply_vorteza_design()

# Proste logowanie (możesz później przenieść listę użytkowników do bazy)
USERS = {"admin": "vorteza", "kierowca1": "sqm2026", "logistyka": "sqm2026"}

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<br><br><div class='vorteza-card' style='text-align:center;'><p class='logo-font'>SYSTEM ACCESS</p></div>", unsafe_allow_html=True)
    u = st.text_input("OPERATOR ID")
    p = st.text_input("SECURITY KEY", type="password")
    if st.button("AUTHORIZE"):
        if u in USERS and USERS[u] == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else:
            st.error("ACCESS DENIED: INVALID KEY")
else:
    # Header po zalogowaniu
    try: st.image('logo_vorteza.png', width=180)
    except: pass
    st.markdown(f'<p class="logo-font">VORTEZA - BASE</p>', unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#B58863;'>OPERATOR: {st.session_state.user.upper()}</p>", unsafe_allow_html=True)
    
    with st.form("main_form"):
        # Dane pojazdu
        st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
        rej = st.text_input("LICENSE PLATE (NR REJESTRACYJNY)", placeholder="np. PO 12345")
        km = st.number_input("MILEAGE (PRZEBIEG KM)", step=1, value=0)
        st.markdown('</div>', unsafe_allow_html=True)

        # Sekcje techniczne (Checklist)
        with st.expander("► EXTERIOR & BODY"):
            f1 = st.checkbox("Brak nowych uszkodzeń powłoki")
            f2 = st.checkbox("Oświetlenie zewnętrzne sprawne")
            f3 = st.checkbox("Szyby i lusterka bez pęknięć")

        with st.expander("► INTERIOR & CARGO"):
            f4 = st.checkbox("Kabina czysta / wyczyszczona")
            f5 = st.checkbox("Pasy transportowe kpl.")
            f6 = st.checkbox("Dokumenty i klucze kpl.")

        st.markdown('<br>', unsafe_allow_html=True)
        with st.expander("► OBSERVATIONS & NOTES"):
            obs = st.text_area("Szczegółowe uwagi logistyczne...", height=100)

        st.markdown('<br>', unsafe_allow_html=True)
        if st.form_submit_button("GENERATE AND ENCRYPT PROTOCOL"):
            if not rej: 
                st.error("PLATE REQUIRED!")
            else:
                # Przygotowanie danych do JSON
                checklist = {
                    "exterior": [f1, f2, f3],
                    "interior": [f4, f5, f6]
                }
                
                with st.spinner("TRANSMITTING TO SECURE SERVER..."):
                    success = save_to_supabase(rej, km, obs, checklist, st.session_state.user)
                
                if success:
                    st.success("PROTOCOL TRANSMITTED & ENCRYPTED")
                    st.balloons()

    if st.sidebar.button("TERMINATE SESSION"):
        st.session_state.auth = False
        st.rerun()
