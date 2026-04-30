import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="PCCT Intelligent System",
    page_icon="🧠",
    layout="wide"
)

# =========================
# BACKGROUND (IMAGE COMPLETE)
# =========================
def set_background(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: black;
            background-image: url("{image_url}");
            background-size: contain;   /* image complète */
            background-repeat: no-repeat;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# =========================
# STYLE GLOBAL
# =========================
st.markdown("""
<style>

h1, h2, h3 {
    color: #00D4FF;
}

p, label, span, div {
    color: white;
}

.card {
    background: rgba(15, 23, 42, 0.85);
    padding: 25px;
    border-radius: 20px;
    border: 1px solid rgba(0,212,255,0.3);
    margin-bottom: 20px;
}

.stButton>button {
    background: linear-gradient(135deg, #00D4FF, #7C3AED);
    color: white;
    border-radius: 10px;
    font-weight: bold;
}

[data-testid="stMetric"] {
    background: rgba(15, 23, 42, 0.85);
    padding: 15px;
    border-radius: 15px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# FUNCTIONS
# =========================
def calcul_imc(poids, taille):
    return poids / ((taille/100)**2)

def calcul_dose(age, imc):
    return round(4.5 + 0.08*imc + 0.015*age, 2)

def calcul_snr(age, imc, dose):
    return round(max(70 - 0.35*imc - 0.08*age + 1.8*dose, 10), 2)

def etat_scanner(snr, temp, err, days):
    score = 100
    if snr < 50: score -= 25
    if temp > 75: score -= 25
    if err >= 5: score -= 25
    if days > 90: score -= 25

    if score >= 75:
        return score, "Bon état ✅"
    elif score >= 50:
        return score, "À surveiller ⚠️"
    else:
        return score, "Risque panne 🚨"

# =========================
# MENU
# =========================
menu = st.sidebar.radio("Navigation", [
    "Accueil",
    "Technicien",
    "Qualité SNR",
    "Suivi Scanner",
    "Maintenance",
    "Rapport"
])

# =========================
# ACCUEIL
# =========================
if menu == "Accueil":
    set_background("https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d")

    st.title("🧠 PCCT Intelligent System")
    st.markdown("""
    <div class="card">
    Application intelligente pour :
    ✔ optimisation dose patient  
    ✔ analyse qualité image (SNR)  
    ✔ suivi scanner PCCT  
    ✔ maintenance prédictive  
    </div>
    """, unsafe_allow_html=True)

# =========================
# TECHNICIEN
# =========================
elif menu == "Technicien":
    set_background("https://images.unsplash.com/photo-1581093458791-9d15482442f6")

    st.title("👩‍🔧 Espace Technicien")

    age = st.number_input("Âge", 1, 120, 45)
    poids = st.number_input("Poids", 20.0, 200.0, 70.0)
    taille = st.number_input("Taille", 100.0, 220.0, 170.0)

    imc = calcul_imc(poids, taille)
    dose = calcul_dose(age, imc)
    snr = calcul_snr(age, imc, dose)

    c1, c2, c3 = st.columns(3)
    c1.metric("IMC", round(imc,2))
    c2.metric("Dose", dose)
    c3.metric("SNR", snr)

    if snr >= 50:
        st.success("Bonne qualité image")
    else:
        st.warning("SNR faible")

# =========================
# SNR
# =========================
elif menu == "Qualité SNR":
    set_background("https://images.unsplash.com/photo-1579154204601-01588f351e67")

    st.title("📊 Analyse SNR")

    imc = st.slider("IMC", 15, 45, 25)
    age = st.slider("Âge", 10, 90, 40)

    doses = np.linspace(3,12,20)
    snr = [calcul_snr(age, imc, d) for d in doses]

    df = pd.DataFrame({"Dose":doses, "SNR":snr})
    st.line_chart(df.set_index("Dose"))

# =========================
# SUIVI
# =========================
elif menu == "Suivi Scanner":
    set_background("https://images.unsplash.com/photo-1518005020951-eccb494ad742")

    st.title("🛠️ Suivi Scanner")

    snr = st.number_input("SNR moyen", 10.0,100.0,52.0)
    temp = st.number_input("Température",20.0,120.0,60.0)
    err = st.number_input("Erreurs",0,50,2)
    days = st.number_input("Jours maintenance",0,365,40)

    score, etat = etat_scanner(snr,temp,err,days)

    st.metric("Score", score)
    st.metric("État", etat)

# =========================
# MAINTENANCE
# =========================
elif menu == "Maintenance":
    set_background("https://images.unsplash.com/photo-1636819488524-1f019c4e1c44")

    st.title("🔮 Maintenance prédictive")

    st.warning("Analyse des anomalies en cours...")

# =========================
# RAPPORT
# =========================
elif menu == "Rapport":
    set_background("https://images.unsplash.com/photo-1581091226825-a6a2a5aee158")

    st.title("📄 Rapport")

    nom = st.text_input("Nom patient", "Patient_1")
    age = st.number_input("Âge",1,120,45)
    poids = st.number_input("Poids",20.0,200.0,70.0)
    taille = st.number_input("Taille",100.0,220.0,170.0)

    imc = calcul_imc(poids, taille)
    dose = calcul_dose(age, imc)
    snr = calcul_snr(age, imc, dose)

    rapport = f"""
Patient: {nom}
IMC: {imc:.2f}
Dose: {dose}
SNR: {snr}
Date: {datetime.now()}
"""

    st.text_area("Rapport", rapport)
