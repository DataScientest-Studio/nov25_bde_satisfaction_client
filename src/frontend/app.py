# File: src\frontend\app.py

"""
Module pour l'affichage d'un tableau de bord interactif de satisfaction client
avec des prédictions de sentiment et l'intégration d'un tableau de bord Kibana.

Il inclut :
- Affichage d'un logo et d'un titre centrés
- Prédiction de sentiment basée sur un modèle machine learning
- Intégration d'un dashboard Kibana via iframe
"""

import streamlit as st
import requests
import streamlit.components.v1 as components

LOGO_DATASCIENTEST = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAAsSAAALEgHS3X78AAAFVUlEQVRYha2WX4ycVRnGf88538zObtfS0uoFbelUtGS3u9tWSlr5E1KQAgZjjH+uFA0hkeitpEIkISGEFmLQ4K3CBRBMRA2GBqyWEAnWps12d6dLum3BpU1VasmW7dLdb75zXi9md7qz3+zM2nBuZvKd57zP8z7nvO85Yomjt1Lp9jG5B+l20FbJyhgrQDIxAYzLOGqyN4vTk/uObNt2YSlx1Q6w+d33yzFLdwt9F9G9lKBmdgl4mRj3jmzuOX5FAr4wNtbRlfIoZj9B6lgKcU4IVGX2q8LV3T87smbNJ0sWsPXYe+tDrP4e6UtXQpwTYjYqn3xjuPe6sbYCeiuVXk9xv+CaXKQqkMyuymb/L13EebN4d2Wg5/D8766R/NS13pqTu7NG8o8IM1B4MaCZeVmcM9wHhv5t6L+GO2Xo4oJMpVWSe71/6N3rmwrorVSKCeEVKU+uCSg8FwjbHKU9GbZa2LLL88n+SPH5QOFPkeQto+PZgDsRcy5IWoX3fxg4erS+ui7Aq+MRYFvDilD7KbwQCDscyRsRN2aEWxuMA8tx1dfmREAPrvOJBgGbRk6sI8bdC8H+mKFJSA5GQq/whyI4sAU1oQg6bfghI3k7oglD080FAJjTjzeNHO+pC3CEhySVcgKORNy4QQDZbKYBfKUxZU2ALoLO184BMwsj5VxInOynAG7HOx90It3XDOiHrW6vP2iEG2rWF38dcP+anaiCqzTut3VC/HzrHifTd/qHh1e6qWVTdwpdlUMY6CPDSrWAhT8G4lqI64XOGaXdGcXfBNxZI7vLwzz/sl2O4jMBtWrGUkkq3uvk3c7mAIhrRGFfpPo9Dxl0/DJgVwPFWubJ/kjp4Qw3bkw/khB21Bxy/4Fwi8udlXyO2ukMtiwGyHY5/MGIO2WkD3isE/ygQdrolD8U6dibkd3hSB/0+MORwu/Cgi7TNMktDlN5UQG3ObKbHclfI4UXAnbN4vuqKeh4OiOWRfqDmmOaalaf8/lVdmArWiBIf+SpfsujDNzJ1gFJofBqJNvpsM8Avs1la7aifTd3UP2mI9spkjcNPxzRWUNTNG9AHxs4iGXBtMHyFiIkS4AJYHEX5sSuFGEAwoAnXisogCah88FqAy7c4vCDRvXbvrnAxqgXEqT3gXIrmD6B4i8y/MhsRAe2Slx6OsGWgz4GBNWvO2y18Eci6X2+HTtm/DOR2VGk5qUItfLbm+HG5qUTazdg8aXA9OMJ7j3D1gsTlB4PhO1tH1pzY9CBDrRCFF4JjeTzRvLnSOmJQOxxuEGj8+EMfdTW9/ow6YC70F34i2ETzQC6AIV9+Wu1AfNh7WDSCbS4gHLkcMlXC6+58Q0bpoV7vhnIvxMbm06dFWz1ZZt12ghfdljn5fl2Q8Zvh7ZumHAAFuznsy/ZRgGjeTttGaQ/9MR1YJ8TsSxspbAShBvbtb7ZGFC1GPbAbLMc2bzxjMz25FSebRRgXRB7HW7UiL2OS88kTD+ZkN1TI547fP5vkWR/i60ze3buuV5vRIX0+ifT0omvCrbPfcu+5lre7Tpv2Gcv+x0GHOn91LZAtfK1roXZW6U4M/loPcb8yf6hsbXy9nfQ2sVpr3yY2blE7qbBvi+enPvWsGkjmzeesRC/AnbmUyeHDxV013zynICaiJ7jwdKbzDj06bHbSCC9eXjLxsGFU02P7bH+/tNB6a3AY2b2f1T3QmJSsKe6Js9vH+3rO9kM0rZiN42cWOecPUS070tavjRem5LpxQBPHevfeKoVdslN+4bDh7tmit27JHc7sFWyshkrkQAmBOMWbQinA4H09dG+vottQgLwPz5ONQqZ51zqAAAAAElFTkSuQmCC"
LOGO_GITHUB = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAQCAIAAAD4YuoOAAAACXBIWXMAAAsSAAALEgHS3X78AAACOUlEQVQ4jZ2Uv2saYRjHn7cKF3/WobnDwaVBvdNJh3SKEP+A6gWhp9JMLg3N0GzNFtN0UIs0q6MopJAOppsVmqiTq4hFUhQEQR2uJ6Li6dvhqBXia5o8w/G87/N5ny/Pcw8PGgwGsMowxstHSZKq1Wq320UIMQzjdDqNRuMafmHqlbfL1m63U6lU8eZmNpv9e6ZW73g8kUjEYrGsf47WV5DP5+Ox2GQyWclQFPX++Njr9a6p4Mka8VKx+PHsjNrYsNlsd6Msy1IUFT05KZfLj6lAkqRQMChJEs/z746OarXar9tbs9kMAJ1O5/nWlsPhiMVi366unppMmUzGYDCszEP8B18vLyVJAgBZljHGHMdxHAcACKEFM5/NAOC3KOZyuXA4vDIPsUWlUklxXvp8JMb3N1QqFkkMUaDVagGAyWSy2+0khuU4pTPNZvPBAtPpVPmSxgMAMMYKJsvycuv+S4CmaQAYDoc/63USU6/Xx+MxADzb3HzwmLrcbsVJJpOiKN4F+v3+p0RC8d0uFykPUcDv9yOEXgkCzTCCIHw4PV00utFoRKPRcCjUaDQAACHE7+2R8hDHlGVZnue/XFx8Pj/X63SiKDIMo4Romv6ezy/IQCBgtVofs4veHh72er1EPB4MBvV6vUajUe51Ot2C2fF43hwcrElyzy7C83k2m02n06PR6Mf1NUIIISTLsnd3V6vVvt7fFwRBpVIBeRfdI6DYYDCoVCrKUkMIYYwLhcKL7W3D0sYmCfwBQSv3SG9EuQkAAAAASUVORK5CYII="

API_URL = "http://fastapi-satisfaction:8000/predict"
KIBANA_DASHBOARD_URL = (
    "http://localhost:5601/app/dashboards#/view/4e52a31c-5cea-4429-b435-6d36728ad392"
    "?embed=true"
    "&_g=(time:(from:now-7d,to:now))"
)

st.set_page_config(
    page_title="Dashboard de Sentiment et Kibana",
    layout="wide"
)

# Ajout du CSS personnalisé pour aligner le logo avec le texte
st.markdown("""
    <style>
        .logo-text-container {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 10px;
        }
        
        .logo-text-container img {
            width: 50px;
            height: auto;
            margin-right: 10px;
        }

        h1, h2 {
            margin: 0;
            padding: 0;
        }

        .github-container {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-top: 5px;
        }

        .github-container img {
            width: 20px;
            height: auto;
            margin-right: 10px;
        }

        .footer {
            text-align: center;
            font-size: 12px;
            color: gray;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Affichage du logo et titre sur la même ligne
st.markdown(
    f'<div class="logo-text-container">'
    f'<img src="{LOGO_DATASCIENTEST}" width="50" />'
    f'<h1 style="display: inline;">NOV25 BDE SATISFACTION CLIENT</h1>'
    f'</div>', 
    unsafe_allow_html=True
)

# Affichage du logo GitHub et lien sur la même ligne
st.markdown(
    f'<div class="github-container">'
    f'<img src="{LOGO_GITHUB}" width="20" />'
    f"""
    <h2 style="display: inline;">
        <a href="https://github.com/DataScientest-Studio/nov25_bde_satisfaction_client" style="text-decoration: none; color: black;">
            <strong style="font-size: 14px;">Lien vers la repository GitHub</strong>
        </a>
    </h2>
    </div>
    """, 
    unsafe_allow_html=True
)

# Affichage du dashboard Kibana
st.subheader("📊 Tableau de bord via Elasticsearch / Kibana")
components.iframe(
    src=KIBANA_DASHBOARD_URL,
    height=600,
    scrolling=True
)

st.markdown("---")

# Section de prédiction de sentiment
st.subheader("🔮 Outil de prédiction de sentiment via modèle ML")

col1, col2 = st.columns([1, 1])

with col1:
    text_input = st.text_area("Entrez votre avis ci-dessous", "", height=150)

with col2:
    sentiment = ""
    sentiment_color = ""

    if text_input:
        response = requests.post(API_URL, json={"text": text_input})
        
        if response.status_code == 200:
            sentiment = response.json().get("sentiment", "Erreur lors de la prédiction")
            
            if sentiment == "POSITIF":
                sentiment_color = "green"
            elif sentiment == "NÉGATIF":
                sentiment_color = "red"
            else:
                sentiment_color = "gray"
        else:
            st.error(f"Erreur {response.status_code}: Impossible de prédire le sentiment")

    st.markdown("<u><strong>Sentiment prédit :</strong></u>", unsafe_allow_html=True)
    
    if sentiment:
        st.markdown(f"""
            <p style="color: {sentiment_color}; font-size: 16px;">
                {sentiment}
            </p>
        """, unsafe_allow_html=True)

if st.button("Envoyer l'avis pour prédiction"):
    if not text_input:
        st.warning("Veuillez entrer un avis avant de soumettre.")

# Footer
st.markdown(
    """
    <footer class="footer">
        &copy; 2026 DataScientest. Tous droits réservés.
    </footer>
    """, 
    unsafe_allow_html=True
)