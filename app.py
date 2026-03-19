import streamlit as st
import psycopg2
import json
from datetime import datetime

# --- KONFIGURACJA POŁĄCZENIA ---
# Funkcja pobiera dane z Twoich Streamlit Secrets i otwiera "tunel" do bazy Supabase
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
        st.error(f"❌ Błąd połączenia z bazą: {e}")
        return None

# --- LOGIKA ZAPISU DO BAZY ---
# Ta funkcja bierze dane z formularza i układa je w tabeli SQL
def save_to_supabase(rejestracja, przebieg, uwagi, checklist, operator):
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            # SQL Query - dopasowane do Twojej tabeli protokoly_vorteza
            query = """
                INSERT INTO protokoly_vorteza 
                (rejestracja, przebieg, uwagi, lista_kontrolna, operator_id) 
                VALUES (%s, %s, %s, %s, %s)
            """
            cur.execute(query, (
                rejestracja, 
                przebieg, 
                uwagi, 
                json.dumps(checklist), # Zamieniamy listę kontrolną na format tekstowy JSON
                operator
            ))
            conn.commit() # Zatwierdzenie zmian w bazie
            cur.close()
            conn.close()
            return True
        except Exception as e:
            st.error(f"❌ Błąd zapisu SQL: {e}")
            return False
    return False

# --- INTERFEJS UŻYTKOWNIKA (UI) ---
st.set_page_config(page_title="Vorteza Logistyka - SQM", page_icon="🚛", layout="centered")

# Nagłówek i branding
st.title("🚛 Protokół Przekazania Pojazdu")
st.markdown("### System Logistyczny SQM Multimedia Solutions")
st.divider()

# Formularz - grupuje pola i zapobiega odświeżaniu strony przy każdym kliknięciu
with st.form("form_protokol"):
    st.subheader("📋 Dane podstawowe")
    col1, col2 = st.columns(2)
    
    with col1:
        rejestracja = st.text_input("Numer rejestracyjny", placeholder="np. PO 12345")
        operator = st.text_input("Imię i Nazwisko / ID Operatora")
    
    with col2:
        przebieg = st.number_input("Aktualny przebieg (km)", min_value=0, step=1, value=0)
        data_kontroli = st.date_input("Data kontroli", datetime.now())

    st.write("---")
    st.subheader("🛠️ Stan techniczny i czystość")
    
    c1, c2 = st.columns(2)
    with c1:
        f_czysto = st.checkbox("Wnętrze kabiny posprzątane")
        f_paliwo = st.checkbox("Poziom paliwa / energii OK")
        f_dokumenty = st.checkbox("Dokumenty i klucze kpl.")
    
    with c2:
        f_uszkodzenia = st.checkbox("Brak nowych uszkodzeń zewnętrznych")
        f_swiatla = st.checkbox("Oświetlenie i płyny sprawne")
        f_pasy = st.checkbox("Pasy transportowe / wyposażenie kpl.")

    uwagi = st.text_area("Uwagi dodatkowe / Opis uszkodzeń (jeśli wystąpiły)")

    # Przycisk wysyłki
    submit_button = st.form_submit_button("✅ Zapisz protokół w systemie")

# Obsługa kliknięcia przycisku
if submit_button:
    if not rejestracja or not operator:
        st.error("⚠️ Musisz podać numer rejestracyjny oraz dane operatora!")
    else:
        # Tworzymy strukturę danych dla listy kontrolnej
        checklist_data = {
            "czystosc": f_czysto,
            "paliwo": f_paliwo,
            "dokumenty": f_dokumenty,
            "uszkodzenia": f_uszkodzenia,
            "oswietlenie": f_swiatla,
            "wyposazenie": f_pasy
        }
        
        with st.spinner("📦 Wysyłanie do bazy Supabase..."):
            sukces = save_to_supabase(rejestracja, przebieg, uwagi, checklist_data, operator)
            
        if sukces:
            st.success(f"✔️ Protokół dla pojazdu **{rejestracja}** został zapisany!")
            st.balloons()
            st.info("Dane są już widoczne w panelu logistycznym SQM.")

# Stopka w panelu bocznym
st.sidebar.markdown("---")
st.sidebar.success("🟢 System Połączony")
st.sidebar.write(f"Zalogowany: Logistyka SQM")
