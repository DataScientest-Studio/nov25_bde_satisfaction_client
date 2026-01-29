# File: src\frontend\app.py

"""
Module pour l'affichage d'un tableau de bord interactif de satisfaction client
avec des prédictions de sentiment et l'intégration d'un tableau de bord Kibana.

Il inclut :
- Affichage d'un logo et d'un titre centrés
- Prédiction de sentiment basée sur un modèle machine learning
- Intégration d'un dashboard Kibana via iframe
"""

import os
import time
import streamlit as st
import requests
import streamlit.components.v1 as components

LOGOS_FILES_PATHS = {
    "airflow": os.path.join("src", "frontend", "base64_images", "airflow_logo.txt"),
    "datascientest": os.path.join("src", "frontend", "base64_images", "datascientest_logo.txt"),
    "fastapi": os.path.join("src", "frontend", "base64_images", "fastapi_logo.txt"),
    "github": os.path.join("src", "frontend", "base64_images", "github_logo.txt"),
    "grafana": os.path.join("src", "frontend", "base64_images", "grafana_logo.txt"),
    "kibana": os.path.join("src", "frontend", "base64_images", "kibana_logo.txt")
}

def lire_base64(fichier_path: str) -> str:
    """Lire le contenu d'un fichier texte contenant une chaîne Base64 et la retourner."""
    with open(fichier_path, "r") as f:
        return f.read().strip()

# Utilisation d'une compréhension de dictionnaire pour lire tous les fichiers
LOGOS_BASE64 = {key: lire_base64(path) for key, path in LOGOS_FILES_PATHS.items()}

# URLs des ressources externes (API, Kibana, GitHub, FastAPI)
AIRFLOW_URL = "http://localhost:8081/login"
FASTAPI_URL = "http://localhost:8000/docs"
GITHUB_URL = "https://github.com/DataScientest-Studio/nov25_bde_satisfaction_client"
GRAFANA_URL = "http://localhost:3000"
KIBANA_URL = (
    "http://localhost:5601/app/dashboards#/view/4e52a31c-5cea-4429-b435-6d36728ad392"
    "?embed=true"
    "&_g=(time:(from:now-1y,to:now))"
)
API_URL = "http://fastapi-satisfaction:8000/predict"

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Dashboard de Sentiment et Kibana",
    layout="wide"
)

# Affichage du logo DataScientest et du titre du dashboard
st.markdown(
    f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <img src="data:image/png;base64,{LOGOS_BASE64['datascientest']}" width="50" />
        <h1 style="display: inline;">NOV25 BDE SATISFACTION CLIENT</h1>
    </div>
    """, 
    unsafe_allow_html=True
)

# Affichage des logos avec des liens vers leurs ressources
st.markdown(
    f"""
    <table style="width: 100%; text-align: left; margin-bottom: 10px; border-collapse: collapse;">
        <tr>
            <td style="padding-right: 15px;">
                <img src="data:image/png;base64,{LOGOS_BASE64['airflow']}" width="20" />
                <a href="{AIRFLOW_URL}" style="text-decoration: none; color: black;">Apache Airflow — </a>
                <img src="data:image/png;base64,{LOGOS_BASE64['fastapi']}" width="20" />
                <a href="{FASTAPI_URL}" style="text-decoration: none; color: black;">FastAPI — </a>
                <img src="data:image/png;base64,{LOGOS_BASE64['github']}" width="20" />
                <a href="{GITHUB_URL}" style="text-decoration: none; color: black;">GitHub — </a>
                <img src="data:image/png;base64,{LOGOS_BASE64['kibana']}" width="20" />
                <a href="{KIBANA_URL}" style="text-decoration: none; color: black;">Kibana — </a>
                <img src="data:image/png;base64,{LOGOS_BASE64['grafana']}" width="20" />
                <a href="{GRAFANA_URL}" style="text-decoration: none; color: black;">Grafana</a>
            </td>
        </tr>
    </table>
    """, 
    unsafe_allow_html=True
)

# Affichage du dashboard Kibana dans un iframe
st.subheader("📊 Tableau de bord - Elasticsearch / Kibana")

# Initialisation du timestamp pour forcer reload
if "kibana_ts" not in st.session_state:
    st.session_state.kibana_ts = int(time.time())

# Callback pour mettre à jour le timestamp uniquement lors du changement de période
def on_periode_change() -> None:
    st.session_state.kibana_ts = int(time.time())

# Choix de la période
col_select, _ = st.columns([1, 5])
with col_select:
    periode = st.selectbox(
        "Sélectionner une période :",
        ["7 derniers jours", "14 derniers jours", "1 mois", "3 mois", "6 mois", "1 an"],
        on_change=on_periode_change
    )

# Conversion en format Kibana
from_to_map = {
    "7 derniers jours": "now-7d",
    "14 derniers jours": "now-14d",
    "1 mois": "now-1M",
    "3 mois": "now-3M",
    "6 mois": "now-6M",
    "1 an": "now-1y"
}

# Conversion sélection → format Kibana
from_time = from_to_map[periode]

# URL dynamique avec période et timestamp
KIBANA_URL = (
    "http://localhost:5601/app/dashboards#/view/4e52a31c-5cea-4429-b435-6d36728ad392"
    "?embed=true"
    f"&_g=(time:(from:{from_time},to:now))"
    f"&_ts={st.session_state.kibana_ts}"
)

# Affichage dans l'iframe
components.iframe(
    src=KIBANA_URL,
    height=600,
    scrolling=True
)

st.markdown("---")

# Section de prédiction de sentiment
st.subheader("🔮 Outil de prédiction de sentiment - Modèle ML")

# Mise en page avec deux colonnes
col1, col2 = st.columns([1, 1])

with col1:
    # Zone de saisie pour l'avis de l'utilisateur
    text_input = st.text_area("Entrer votre avis ci-dessous (4000 caractères max.) :", "", height=150)

with col2:
    sentiment = ""        # Variable pour stocker le sentiment prédit
    sentiment_color = ""  # Variable pour définir la couleur du texte en fonction du sentiment

    text_clean = text_input.strip()

    if text_clean:  # Si le texte n'est pas vide
        # Bloquer texte de 1 caractère ou deux caractères identiques
        if len(text_clean) == 1 or (len(text_clean) == 2 and text_clean[0] == text_clean[1]):
            sentiment = "Texte trop court ou répétitif pour prédiction"
            sentiment_color = "gray"
        else:
            response = requests.post(API_URL, json={"text": text_input})

            if response.status_code == 200:
                sentiment = response.json().get("sentiment", "Erreur lors de la prédiction")
                
                if sentiment.lower() == "positif":
                    sentiment_color = "green"
                elif sentiment.lower() == "négatif":
                    sentiment_color = "red"
                else:
                    sentiment_color = "gray"
            else:
                st.error(f"Erreur {response.status_code}: Impossible de prédire le sentiment")
    else:
        sentiment = ""  # Aucun texte saisi
        sentiment_color = ""

    # Affichage du sentiment prédit
    st.markdown("<u><strong>Sentiment prédit :</strong></u>", unsafe_allow_html=True)
    
    if sentiment:
        st.markdown(f"""
            <p style="color: {sentiment_color}; font-size: 16px;">
                {sentiment}
            </p>
        """, unsafe_allow_html=True)

# Bouton pour envoyer l'avis et obtenir la prédiction
if st.button("Envoyer l'avis pour prédiction"):
    if not text_input:
        st.warning("Veuillez entrer un avis avant de soumettre.")

# Footer
st.markdown(
    """
    <footer style="text-align: center; font-size: 12px; color: gray; margin-top: 20px;">
        &copy; 2026 DataScientest. Tous droits réservés.
    </footer>
    """, 
    unsafe_allow_html=True
)
