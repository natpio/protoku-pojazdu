import streamlit as json
import pandas as pd
from io import StringIO

# Funkcja do wczytywania danych z JSON
def load_control_list():
    try:
        # Zakładamy, że plik lista_kontrolna.json znajduje się w tym samym katalogu
        with open("lista_kontrolna.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["lista_kontrolna"]
    except FileNotFoundError:
        st.error("Błąd: Plik lista_kontrolna.json nie został znaleziony.")
        return None

# Konfiguracja aplikacji Streamlit
st.set_page_config(page_title="Protokół Przekazania Pojazdu", layout="wide")
st.title("Protokół Przekazania Pojazdu")

control_list = load_control_list()

if control_list:
    with st.form(key="protocol_form"):
        st.header("1. Informacje o pojeździe i kierowcy")
        vehicle_id = st.text_input("Numer rejestracyjny pojazdu")
        driver_name = st.text_input("Imię i nazwisko kierowcy")
        date = st.date_input("Data")
        time = st.time_input("Godzina")

        st.header("2. Lista Kontrolna")
        
        results = {}
        for category, items in control_list.items():
            st.subheader(f"### {category}")
            for item in items:
                # Używamy checkboxów do łatwego zaznaczania
                results[item] = st.checkbox(item)

        submit_button = st.form_submit_button(label="Wyślij Protokół")

        if submit_button:
            # Tutaj można dodać logikę wysyłki danych, np. do bazy danych lub Google Sheets
            st.success("Protokół został pomyślnie wysłany!")
            st.write("Podsumowanie:")
            st.write(f"Pojazd: {vehicle_id}, Kierowca: {driver_name}")
            
            # Przykładowe wyświetlenie wyników
            summary = {k: "Zgodne" if v else "Niezgodne" for k, v in results.items()}
            st.write(summary)
