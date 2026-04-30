import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(
    page_title="PCCT Intelligent System",
    page_icon="🧠",
    layout="wide"
)

# =========================
# BACKGROUND PAR PAGE
# =========================
def set_background(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background:
            linear-gradient(rgba(0,0,0,0.78), rgba(0,0,0,0.88)),
            url("{image_url}");
            background-size: cover;
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
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #061923, #0B1020);
}

h1, h2, h3 {
    color: #00D4FF;
}

p, label, span, div {
    color: #F8FAFC;
}

.main-title {
    font-size: 55px;
    font-weight: 900;
    color: #00D4FF;
    text-align: center;
    margin-top: 70px;
}

.sub-title {
    font-size: 22px;
    color: white;
    text-align: center;
    margin-bottom: 40px;
}

.card {
    background: rgba(15, 23, 42, 0.82);
    backdrop-filter: blur(12px);
    padding: 25px;
    border-radius: 22px;
    border: 1px solid rgba(0, 212, 255, 0.25);
    box-shadow: 0 0 25px rgba(0, 212, 255, 0.18);
    margin-bottom: 20px;
}

.big-card {
    background: rgba(15, 23, 42, 0.88);
    backdrop-filter: blur(14px);
    padding: 30px;
    border-radius: 24px;
    border: 1px solid rgba(124, 58, 237, 0.35);
    box-shadow: 0 0 35px rgba(124, 58, 237, 0.22);
}

.stButton>button {
    background: linear-gradient(135deg, #00D4FF, #7C3AED);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 25px;
    font-weight: bold;
}

.stDownloadButton>button {
    background: linear-gradient(135deg, #00D4FF, #7C3AED);
    color: white;
    border-radius: 12px;
    font-weight: bold;
}

[data-testid="stMetric"] {
    background: rgba(15, 23, 42, 0.82);
    border: 1px solid rgba(0, 212, 255, 0.25);
    padding: 18px;
    border-radius: 18px;
}

.stTextInput input, .stNumberInput input, .stSelectbox div {
    background-color: rgba(15,23,42,0.85);
    color: white;
}

textarea {
    background-color: rgba(15,23,42,0.92) !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# FONCTIONS
# =========================
def calcul_imc(poids, taille_cm):
    taille_m = taille_cm / 100
    return poids / (taille_m ** 2)

def categorie_imc(imc):
    if imc < 18.5:
        return "Maigreur"
    elif imc < 25:
        return "Normal"
    elif imc < 30:
        return "Surpoids"
    else:
        return "Obésité"

def calcul_dose_optimale(age, imc):
    return round(4.5 + (0.08 * imc) + (0.015 * age), 2)

def calcul_snr(age, imc, dose):
    snr = 70 - (0.35 * imc) - (0.08 * age) + (1.8 * dose)
    return round(max(snr, 10), 2)

def interpretation_snr(snr):
    if snr >= 50:
        return "Qualité d’image acceptable ✅"
    elif snr >= 40:
        return "Qualité moyenne ⚠️"
    else:
        return "Qualité insuffisante 🚨"

def etat_scanner(snr_moyen, temperature, erreurs, jours_maintenance):
    score = 100
    if snr_moyen < 50:
        score -= 25
    if temperature > 75:
        score -= 25
    if erreurs >= 5:
        score -= 25
    if jours_maintenance > 90:
        score -= 25

    if score >= 75:
        return score, "Bon état ✅"
    elif score >= 50:
        return score, "À surveiller ⚠️"
    else:
        return score, "Risque élevé 🚨"

def diagnostic_maintenance(snr_moyen, dose_moyenne, temperature, erreurs, jours_maintenance):
    actions = []

    if snr_moyen < 50:
        actions.append("Vérifier la calibration des détecteurs PCCT.")
    if dose_moyenne > 10:
        actions.append("Contrôler les paramètres de dose : kVp, mAs et protocole.")
    if temperature > 75:
        actions.append("Vérifier le système de refroidissement du tube RX.")
    if erreurs >= 5:
        actions.append("Analyser les logs d’erreurs du scanner.")
    if jours_maintenance > 90:
        actions.append("Planifier une maintenance préventive.")

    if not actions:
        actions.append("Aucune anomalie critique détectée.")

    return actions

# =========================
# MENU
# =========================
st.sidebar.markdown("## 🧠 PCCT")
st.sidebar.markdown("### Intelligent System")

menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Accueil",
        "👩‍🔧 Espace Technicien",
        "📊 Qualité Image SNR",
        "🛠️ Suivi Scanner PCCT",
        "🔮 Maintenance Prédictive",
        "📄 Rapport"
    ]
)

# =========================
# ACCUEIL
# =========================
if menu == "🏠 Accueil":
    set_background("https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d")

    st.markdown('<div class="main-title">PCCT INTELLIGENT SYSTEM</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Optimisation de la dose patient et suivi intelligent de l’état du scanner PCCT</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="card">
        <h2>👨‍⚕️ Pour les techniciens</h2>
        <p>Optimisation de chaque examen en fonction du patient.</p>
        <ul>
        <li>Calcul IMC automatique</li>
        <li>Dose optimale estimée</li>
        <li>SNR estimé</li>
        <li>Recommandation d’acquisition</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
        <h2>🛠️ Pour le service après-vente</h2>
        <p>Suivi intelligent de l’état du scanner PCCT.</p>
        <ul>
        <li>Suivi SNR moyen</li>
        <li>Suivi température tube</li>
        <li>Détection erreurs</li>
        <li>Maintenance prédictive</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

# =========================
# ESPACE TECHNICIEN
# =========================
elif menu == "👩‍🔧 Espace Technicien":
    set_background("https://images.unsplash.com/photo-1581093458791-9d15482442f6")

    st.title("👩‍🔧 Espace Technicien Radiologie")

    st.markdown('<div class="big-card">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.number_input("Âge du patient", 1, 120, 45)
        sexe = st.selectbox("Sexe", ["Femme", "Homme"])

    with col2:
        poids = st.number_input("Poids du patient (kg)", 20.0, 200.0, 70.0)
        taille = st.number_input("Taille du patient (cm)", 100.0, 220.0, 170.0)

    with col3:
        region = st.selectbox("Région anatomique", ["Thorax", "Abdomen", "Crâne", "Cardiaque"])
        protocole = st.selectbox("Protocole", ["Standard", "Faible dose", "Haute résolution"])

    imc = calcul_imc(poids, taille)
    dose = calcul_dose_optimale(age, imc)
    snr = calcul_snr(age, imc, dose)

    st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("📌 Résultats automatiques")

    c1, c2, c3 = st.columns(3)
    c1.metric("IMC", f"{imc:.2f}", categorie_imc(imc))
    c2.metric("Dose optimale", f"{dose:.2f} mGy")
    c3.metric("SNR estimé", f"{snr:.2f}")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🧠 Recommandation")
    if snr >= 50 and dose <= 10:
        st.success("✅ Protocole adapté : bonne qualité d’image avec dose optimisée.")
    elif snr < 50:
        st.warning("⚠️ SNR faible : améliorer la qualité image ou vérifier la calibration.")
    else:
        st.error("🚨 Dose élevée : optimiser les paramètres d’acquisition.")
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# QUALITÉ IMAGE
# =========================
elif menu == "📊 Qualité Image SNR":
    set_background("https://images.unsplash.com/photo-1579154204601-01588f351e67")

    st.title("📊 Qualité d’image - SNR")

    st.markdown('<div class="big-card">', unsafe_allow_html=True)

    imc_test = st.slider("IMC utilisé pour simulation", 15, 45, 27)
    age_test = st.slider("Âge utilisé pour simulation", 10, 90, 45)

    doses = np.linspace(3, 14, 25)
    snr_values = [calcul_snr(age_test, imc_test, d) for d in doses]

    df = pd.DataFrame({
        "Dose (mGy)": doses,
        "SNR estimé": snr_values
    })

    st.line_chart(df.set_index("Dose (mGy)"))

    st.markdown("""
    ### Interprétation
    - **SNR ≥ 50** : qualité acceptable.
    - **40 ≤ SNR < 50** : qualité moyenne.
    - **SNR < 40** : qualité insuffisante.
    """)

    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# SUIVI SCANNER
# =========================
elif menu == "🛠️ Suivi Scanner PCCT":
    set_background("https://images.unsplash.com/photo-1518005020951-eccb494ad742")

    st.title("🛠️ Suivi de l’état du Scanner PCCT")

    col1, col2 = st.columns(2)

    with col1:
        snr_moyen = st.number_input("SNR moyen hebdomadaire", 10.0, 100.0, 52.0)
        dose_moyenne = st.number_input("Dose moyenne hebdomadaire (mGy)", 1.0, 30.0, 8.5)

    with col2:
        temperature = st.number_input("Température tube RX (°C)", 20.0, 120.0, 65.0)
        erreurs = st.number_input("Nombre d’erreurs / semaine", 0, 50, 2)
        jours_maintenance = st.number_input("Jours depuis dernière maintenance", 0, 365, 45)

    score, etat = etat_scanner(snr_moyen, temperature, erreurs, jours_maintenance)

    c1, c2, c3 = st.columns(3)
    c1.metric("Score santé", f"{score}/100")
    c2.metric("État global", etat)
    c3.metric("Dernière maintenance", f"{jours_maintenance} jours")

    if score >= 75:
        st.success("✅ Le scanner fonctionne normalement.")
    elif score >= 50:
        st.warning("⚠️ Scanner à surveiller.")
    else:
        st.error("🚨 Risque de panne élevé.")

# =========================
# MAINTENANCE
# =========================
elif menu == "🔮 Maintenance Prédictive":
    set_background("https://images.unsplash.com/photo-1636819488524-1f019c4e1c44")

    st.title("🔮 Maintenance Prédictive")

    st.markdown('<div class="big-card">', unsafe_allow_html=True)

    snr_moyen = st.slider("SNR moyen", 10, 100, 48)
    dose_moyenne = st.slider("Dose moyenne (mGy)", 1, 30, 11)
    temperature = st.slider("Température tube RX (°C)", 20, 120, 78)
    erreurs = st.slider("Erreurs système / semaine", 0, 50, 6)
    jours_maintenance = st.slider("Jours depuis dernière maintenance", 0, 365, 120)

    score, etat = etat_scanner(snr_moyen, temperature, erreurs, jours_maintenance)
    actions = diagnostic_maintenance(
        snr_moyen,
        dose_moyenne,
        temperature,
        erreurs,
        jours_maintenance
    )

    st.metric("Score santé scanner", f"{score}/100", etat)

    st.subheader("🛠️ Actions recommandées")
    for action in actions:
        st.write("•", action)

    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# RAPPORT
# =========================
elif menu == "📄 Rapport":
    set_background("https://images.unsplash.com/photo-1581091226825-a6a2a5aee158")

    st.title("📄 Rapport automatique")

    nom_patient = st.text_input("Nom / ID patient", "Patient_001")
    age = st.number_input("Âge", 1, 120, 45)
    poids = st.number_input("Poids (kg)", 20.0, 200.0, 70.0)
    taille = st.number_input("Taille (cm)", 100.0, 220.0, 170.0)

    imc = calcul_imc(poids, taille)
    dose = calcul_dose_optimale(age, imc)
    snr = calcul_snr(age, imc, dose)
    interpretation = interpretation_snr(snr)

    rapport = f"""
RAPPORT PCCT INTELLIGENT SYSTEM

Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}

Patient : {nom_patient}
Âge : {age} ans
Poids : {poids} kg
Taille : {taille} cm

IMC : {imc:.2f}
Catégorie IMC : {categorie_imc(imc)}

Dose optimale estimée : {dose:.2f} mGy
SNR estimé : {snr:.2f}

Interprétation :
{interpretation}

Conclusion :
Le système propose une optimisation personnalisée de la dose patient
tout en gardant une qualité d’image acceptable et un suivi intelligent
de l’état du scanner PCCT.
"""

    st.text_area("Rapport généré", rapport, height=350)

    st.download_button(
        "📥 Télécharger le rapport",
        data=rapport,
        file_name=f"rapport_{nom_patient}.txt",
        mime="text/plain"
    )
