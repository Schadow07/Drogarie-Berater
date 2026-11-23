import streamlit as st
from google import genai
from google.genai import types

# --- SEITEN-KONFIGURATION ---
st.set_page_config(
    page_title="KI Drogerie-Berater",
    page_icon="🛍️",
    layout="centered"
)

# --- API-SCHLÜSSEL SICHER LADEN ---
# Lädt den Schlüssel automatisch aus den Streamlit Secrets (online oder lokal)
api_key = st.secrets.get("GEMINI_API_KEY", "")

# --- HAUPTBEREICH ---
st.title("🛍️ KI Drogerie-Berater")
st.markdown("Beschreibe einfach dein Problem oder was du suchst. Die KI findet das **beste Eigenmarken-Produkt** mit dem höchsten Preis-Leistungs-Verhältnis.")

st.divider()

# 1. Drogerie auswählen
markt = st.radio(
    "1. In welchem Markt bist du gerade?",
    ["Beide (dm & Rossmann vergleichen)", "Nur dm", "Nur Rossmann"],
    horizontal=True
)

# 2. Problem / Wunsch eintippen
problem = st.text_area(
    "2. Was suchst du oder welches Problem möchtest du lösen?",
    placeholder="Beispiele:\n- Ich habe sehr trockene, empfindliche Gesichtshaut und suche eine Creme ohne Parfüm.\n- Mein Badezimmer hat starke Kalkflecken.\n- Ich suche ein günstiges Protein-Shampoo für strapazierte Haare.",
    height=110
)

# 3. Button zum Starten
if st.button("🔍 Beste Eigenmarke finden", type="primary", use_container_width=True):
    if not api_key:
        st.error("⚠️ Der API-Key wurde vom App-Betreiber noch nicht in den Secrets hinterlegt.")
    elif not problem.strip():
        st.warning("⚠️ Bitte beschreibe kurz, wonach du suchst.")
    else:
        with st.spinner("Durchsuche das Drogerie-Sortiment nach dem besten Preis-Leistungs-Sieger..."):
            try:
                client = genai.Client(api_key=api_key)

                system_anweisung = """
                Du bist ein unabhängiger, extrem kompetenter Drogerie-Experte für Deutschland (spezialisiert auf dm und Rossmann).
                Deine Aufgabe: Empfiehl dem Nutzer das Produkt mit dem allerbesten Preis-Leistungs-Verhältnis.
                
                Wichtige Regeln:
                1. Bevorzuge IMMER die Eigenmarken der Märkte (bei dm z.B. Balea, Balea Med, Denkmit, Alverde, Dontodent, Mivolis; bei Rossmann z.B. Isana, Isana Med, Domol, Alterra, Prokudent, Altapharma).
                2. Nenne teure Markenprodukte nur, wenn es absolut keine gute Eigenmarken-Alternative gibt.
                3. Achte auf gute Inhaltsstoffe (z.B. reizarm, ohne unnötiges Mikroplastik/Parfüm bei Hautpflege) und bekannte Testsiege (Stiftung Warentest / Öko-Test).
                4. Halte deine Antwort übersichtlich und strukturiert:
                   - **🏆 Top-Empfehlung:** Exakter Produktname & Marke + geschätzter Preis
                   - **✅ Warum genau dieses Produkt?** (Inhaltsstoffe, Wirkung, ggf. Testsieger-Info)
                   - **💡 Anwendungstipp / Alternative:** (Falls relevant)
                """

                anfrage = f"Markt-Auswahl: {markt}\nProblem/Wunsch des Kunden: {problem}"

                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=anfrage,
                    config=types.GenerateContentConfig(
                        system_instruction=system_anweisung,
                        temperature=0.4,
                    )
                )

                st.divider()
                st.subheader("Deine persönliche Empfehlung")
                with st.container(border=True):
                    st.markdown(response.text)

            except Exception as e:
                st.error(f"Es gab ein Problem bei der Anfrage. Fehlerdetails: {e}")
