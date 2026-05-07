import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import base64
import os

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="PCCT Intelligent System",
    layout="wide"
)

# =========================
# BACKGROUND IMAGE
# =========================
def get_base64_image(path):
    if not os.path.exists(path):
        st.error(f"Image introuvable : {path}")
        return None

    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def set_bg(path):
    img = get_base64_image(path)

    if img:
        st.markdown(
            f"""
            <style>
            .stApp {{
                background:
                linear-gradient(rgba(0,0,0,0.65),
                rgba(0,0,0,0.85)),
                url("data:image/png;base64,{img}");

                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

# =========================
# STYLE
# =========================
st.markdown("""
<style>

/* Sidebar */
[data-testid="stSidebar"] {
    background: #04111f;
}

[data-testid="stSidebar"] * {
    color: white;
}

/* Cards */
.card {
    background: rgba(5,20,35,0.82);
    padding: 25px;
    border-radius: 18px;
    margin-bottom: 20px;
    border: 1px solid rgba(14,165,233,0.3);
    box-shadow: 0px 0px 15px rgba(0,0,0,0.35);
}

/* Buttons */
.stButton > button {
    background: #0ea5e9;
    color: white;
    border-radius: 12px;
    border: none;
    padding: 10px 18px;
    font-weight: bold;
}

/* Metrics */
[data-testid="stMetric"] {
    background: rgba(5,20,35,0.82);
    padding: 15px;
    border-radius: 15px;
    border: 1px solid rgba(14,165,233,0.3);
}

/* Titles */
h1, h2, h3 {
    color: white;
}

/* Text */
p, label, div {
    color: white;
}

</style>
""", unsafe_allow_html=True)

# =========================
# CALCULS
# =========================
def imc(poids, taille):
    return poids / ((taille / 100) ** 2)


def dose(age, imc_value):
    return round(4.5 + 0.08 * imc_value + 0.015 * age, 2)


def snr(age, imc_value, dose_value):
    return round(
        max(
            70
            - 0.35 * imc_value
            - 0.08 * age
            + 1.8 * dose_value,
            10
        ),
        2
    )

# =========================
# MENU
# =========================
menu = st.sidebar.radio(
    "Menu",
    [
        "Accueil",
        "Technicien",
        "SNR",
        "Suivi",
        "Maintenance",
        "Rapport"
    ]
)

# =========================
# ACCUEIL
# =========================
if menu == "Accueil":

    set_bg("accueil.png")

    st.title("PCCT Intelligent System")
    st.subheader("Optimisation intelligente de dose & suivi scanner")

    st.markdown("""
    <div class="card">
    Cette plateforme permet :
    <ul>
    <li>Optimisation automatique de dose</li>
    <li>Analyse SNR</li>
    <li>Suivi intelligent scanner</li>
    <li>Maintenance prédictive</li>
    <li>Génération de rapports</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# =========================
# TECHNICIEN
# =========================
elif menu == "Technicien":

    set_bg("accueil.png")

    st.title("Espace Technicien")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown('<div class="card">', unsafe_allow_html=True)

        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        cin = st.text_input("CIN")

        age = st.number_input(
            "Age",
            min_value=1,
            max_value=120,
            value=45
        )

        poids = st.number_input(
            "Poids (kg)",
            min_value=20.0,
            max_value=200.0,
            value=70.0
        )

        taille = st.number_input(
            "Taille (cm)",
            min_value=100.0,
            max_value=220.0,
            value=170.0
        )

        st.markdown('</div>', unsafe_allow_html=True)

    i = imc(poids, taille)
    d = dose(age, i)
    s = snr(age, i, d)

    with col2:

        st.metric("IMC", round(i, 2))
        st.metric("Dose recommandée", d)
        st.metric("SNR estimé", s)

        if s >= 50:
            st.success("Qualité image acceptable")
        else:
            st.warning("Dose à ajuster")

# =========================
# SNR
# =========================
elif menu == "SNR":

    set_bg("snr.png")

    st.title("Analyse SNR")

    imc_v = st.slider("IMC", 15, 45, 25)
    age_v = st.slider("Age", 10, 90, 40)

    doses = np.linspace(3, 12, 20)

    snrs = [snr(age_v, imc_v, x) for x in doses]

    df = pd.DataFrame({
        "Dose": doses,
        "SNR": snrs
    })

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.line_chart(df.set_index("Dose"))

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# SUIVI
# =========================
elif menu == "Suivi":

    set_bg("suivi.png")

    st.title("Suivi Intelligent Scanner")

    st.markdown('<div class="card">', unsafe_allow_html=True)

    snr_m = st.number_input(
        "SNR système",
        min_value=10.0,
        max_value=100.0,
        value=52.0
    )

    temp = st.number_input(
        "Température système",
        min_value=20.0,
        max_value=120.0,
        value=60.0
    )

    vibration = st.slider(
        "Vibration système",
        0,
        100,
        25
    )

    st.markdown('</div>', unsafe_allow_html=True)

    if snr_m > 50 and temp < 75 and vibration < 50:
        st.success("Scanner en bon état")
    else:
        st.warning("Maintenance recommandée")

# =========================
# MAINTENANCE
# =========================
elif menu == "Maintenance":

    set_bg("maintenance.png")

    st.title("Maintenance Prédictive")

    st.markdown("""
    <div class="card">

    <h3>Analyse système :</h3>

    <ul>
    <li>Tube RX surveillé</li>
    <li>Détecteurs analysés</li>
    <li>Température contrôlée</li>
    <li>SNR monitoré</li>
    <li>Prévision de panne active</li>
    </ul>

    </div>
    """, unsafe_allow_html=True)

    st.warning("Analyse intelligente en cours...")

# =========================
# RAPPORT
# =========================
elif menu == "Rapport":

    set_bg("rapport.png")

    st.title("Rapport Patient")

    st.markdown('<div class="card">', unsafe_allow_html=True)

    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    cin = st.text_input("CIN")

    age = st.number_input(
        "Age",
        min_value=1,
        max_value=120,
        value=45
    )

    poids = st.number_input(
        "Poids (kg)",
        min_value=20.0,
        max_value=200.0,
        value=70.0
    )

    taille = st.number_input(
        "Taille (cm)",
        min_value=100.0,
        max_value=220.0,
        value=170.0
    )

    st.markdown('</div>', unsafe_allow_html=True)

    i = imc(poids, taille)
    d = dose(age, i)
    s = snr(age, i, d)

    txt = f"""
==============================
PCCT INTELLIGENT SYSTEM
==============================

Nom : {nom}
Prénom : {prenom}
CIN : {cin}

--------------------------------

IMC : {i:.2f}

Dose recommandée : {d}

SNR estimé : {s}

--------------------------------

Date :
{datetime.now()}

==============================
"""

    st.text_area("Rapport généré", txt, height=300)

    st.download_button(
        "Télécharger Rapport",
        txt,
        file_name="rapport_patient.txt"
    )
