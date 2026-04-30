import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# =========================
# CONFIGURATION PAGE
# =========================
st.set_page_config(
    page_title="PCCT Intelligent System",
    page_icon="🧠",
    layout="wide"
)

# =========================
# STYLE CSS
# =========================
st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: white;
}

.main-title {
    font-size: 38px;
    font-weight: bold;
    color: #00D4FF;
    text-align: center;
    margin-bottom: 10px;
}

.sub-title {
    font-size: 18px;
    color: #CFCFCF;
    text-align: center;
    margin-bottom: 30px;
}

.card {
    background-color: #161B22;
    padding: 25px;
    border-radius: 18px;
    border: 1px solid #30363D;
    box-shadow: 0px 0px 12px rgba(0, 212, 255, 0.15);
    margin-bottom: 20px;
}

.metric-card {
    background-color: #1F2937;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    border: 1px solid #374151;
}

.good {
    color: #22C55E;
    font-weight: bold;
}

.warning {
    color: #FACC15;
    font-weight: bold;
}

.danger {
    color: #EF4444;
    font-weight: bold;
}

h1, h2, h3 {
    color: #00D4FF;
}
</style>
""", unsafe_allow_html=True)

# =========================
# FUNCTIONS
# =========================
def calcul_imc(poids, taille_cm):
    taille_m = taille_cm / 100
    return poids / (taille_m ** 2)

def categorie_imc(imc):
    if imc < 18.5:
        return "Maigreur", "warning"
    elif imc < 25:
        return "Normal", "good"
    elif imc < 30:
        return "Surpoids", "warning"
    else:
        return "Obésité", "danger"

def calcul_snr(age, imc, dose):
    # Modèle simplifié pédagogique
    snr = 70 - (0.35 * imc) - (0.08 * age) + (1.8 * dose)
    return max(snr, 10)

def calcul_dose_optimale(age, imc):
    # Modèle simplifié adapté au patient
    dose = 4.5 + (0.08 * imc) + (0.015 * age)
    return round(dose, 2)

def interpretation_snr(snr):
    if snr >= 50:
        return "Qualité d’image acceptable", "good"
    elif snr >= 40:
        return "Qualité moyenne - surveillance nécessaire", "warning"
    else:
        return "Qualité insuffisante - optimisation nécessaire", "danger"

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
        return score, "Scanner stable", "good"
    elif score >= 50:
        return score, "Scanner à surveiller", "warning"
    else:
        return score, "Risque de panne élevé", "danger"

def diagnostic_maintenance(snr_moyen, dose_moyenne, temperature, erreurs, jours_maintenance):
    actions = []

    if snr_moyen < 50:
        actions.append("Vérifier la calibration des détecteurs PCCT.")
    if dose_moyenne > 10:
        actions.append("Contrôler les paramètres dose : kVp, mAs et protocole.")
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
# SIDEBAR
# =========================
st.sidebar.title("🧠 PCCT Intelligent System")
menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Accueil",
        "👨‍⚕️ Espace Technicien",
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
    st.markdown('<div class="main-title">PCCT Intelligent System</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Optimisation dose patient + suivi intelligent de l’état du scanner PCCT</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="card">
        <h3>👨‍⚕️ Pour le technicien radiologie</h3>
        <p>Le technicien entre les données patient : âge, sexe, poids, taille.</p>
        <p>L’application calcule automatiquement :</p>
        <ul>
        <li>IMC</li>
        <li>Dose optimale</li>
        <li>SNR estimé</li>
        <li>Recommandation d’acquisition</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
        <h3>🛠️ Pour le service après-vente</h3>
        <p>L’application permet le suivi de l’état du scanner PCCT :</p>
        <ul>
        <li>SNR moyen</li>
        <li>Dose moyenne</li>
        <li>Température tube</li>
        <li>Erreurs système</li>
        <li>Maintenance prédictive</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

# =========================
# ESPACE TECHNICIEN
# =========================
elif menu == "👨‍⚕️ Espace Technicien":
    st.title("👨‍⚕️ Espace Technicien Radiologie")

    st.markdown('<div class="card">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.number_input("Âge du patient", min_value=1, max_value=120, value=45)
        sexe = st.selectbox("Sexe", ["Femme", "Homme"])

    with col2:
        poids = st.number_input("Poids du patient (kg)", min_value=20.0, max_value=200.0, value=70.0)
        taille = st.number_input("Taille du patient (cm)", min_value=100.0, max_value=220.0, value=170.0)

    with col3:
        region = st.selectbox("Région anatomique", ["Thorax", "Abdomen", "Crâne", "Cardiaque"])
        protocole = st.selectbox("Type de protocole", ["Standard", "Faible dose", "Haute résolution"])

    imc = calcul_imc(poids, taille)
    dose_opt = calcul_dose_optimale(age, imc)
    snr = calcul_snr(age, imc, dose_opt)

    cat_imc, color_imc = categorie_imc(imc)
    interpretation, color_snr = interpretation_snr(snr)

    st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("📌 Résultats automatiques")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("IMC", f"{imc:.2f}", cat_imc)

    with c2:
        st.metric("Dose optimale estimée", f"{dose_opt:.2f} mGy")

    with c3:
        st.metric("SNR estimé", f"{snr:.2f}")

    st.markdown("### 🧠 Recommandation")

    if snr >= 50 and dose_opt <= 10:
        st.success("✅ Protocole acceptable : bonne qualité d’image avec dose optimisée.")
    elif snr < 50 and dose_opt <= 10:
        st.warning("⚠️ SNR faible : il faut améliorer la qualité d’image, par exemple ajuster mAs ou vérifier la calibration.")
    elif dose_opt > 10:
        st.error("🚨 Dose élevée : vérifier les paramètres d’acquisition et chercher une optimisation.")
    else:
        st.info("ℹ️ Résultat à valider par le technicien ou le radiologue.")

# =========================
# QUALITÉ IMAGE
# =========================
elif menu == "📊 Qualité Image SNR":
    st.title("📊 Analyse de la qualité d’image par SNR")

    st.markdown("Cette partie permet d’analyser la relation entre la dose et le SNR.")

    doses = np.linspace(3, 12, 20)
    imc_test = st.slider("IMC utilisé pour simulation", 15, 45, 27)
    age_test = st.slider("Âge utilisé pour simulation", 10, 90, 45)

    snr_values = [calcul_snr(age_test, imc_test, d) for d in doses]

    df_snr = pd.DataFrame({
        "Dose (mGy)": doses,
        "SNR estimé": snr_values
    })

    st.line_chart(df_snr.set_index("Dose (mGy)"))

    st.markdown("""
    ### Interprétation
    - Si le SNR est inférieur à 50 : qualité image insuffisante.
    - Si le SNR est supérieur ou égal à 50 : qualité image acceptable.
    - L’objectif est d’obtenir un bon SNR avec la dose la plus faible possible.
    """)

# =========================
# SUIVI SCANNER
# =========================
elif menu == "🛠️ Suivi Scanner PCCT":
    st.title("🛠️ Suivi de l’état du scanner PCCT")

    col1, col2 = st.columns(2)

    with col1:
        snr_moyen = st.number_input("SNR moyen hebdomadaire", min_value=10.0, max_value=100.0, value=52.0)
        dose_moyenne = st.number_input("Dose moyenne hebdomadaire (mGy)", min_value=1.0, max_value=30.0, value=8.5)

    with col2:
        temperature = st.number_input("Température tube RX (°C)", min_value=20.0, max_value=120.0, value=65.0)
        erreurs = st.number_input("Nombre d’erreurs système / semaine", min_value=0, max_value=50, value=2)
        jours_maintenance = st.number_input("Jours depuis dernière maintenance", min_value=0, max_value=365, value=45)

    score, etat, couleur = etat_scanner(snr_moyen, temperature, erreurs, jours_maintenance)

    st.subheader("📌 État global du scanner")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Score santé scanner", f"{score}/100")

    with c2:
        st.metric("État", etat)

    with c3:
        if couleur == "good":
            st.success("✅ Scanner stable")
        elif couleur == "warning":
            st.warning("⚠️ Scanner à surveiller")
        else:
            st.error("🚨 Risque de panne élevé")

# =========================
# MAINTENANCE PREDICTIVE
# =========================
elif menu == "🔮 Maintenance Prédictive":
    st.title("🔮 Maintenance prédictive du scanner PCCT")

    st.markdown("Cette partie aide le service après-vente à détecter les anomalies avant la panne.")

    snr_moyen = st.slider("SNR moyen", 10, 100, 48)
    dose_moyenne = st.slider("Dose moyenne (mGy)", 1, 30, 11)
    temperature = st.slider("Température tube RX (°C)", 20, 120, 78)
    erreurs = st.slider("Erreurs système / semaine", 0, 50, 6)
    jours_maintenance = st.slider("Jours depuis dernière maintenance", 0, 365, 120)

    actions = diagnostic_maintenance(
        snr_moyen,
        dose_moyenne,
        temperature,
        erreurs,
        jours_maintenance
    )

    score, etat, couleur = etat_scanner(snr_moyen, temperature, erreurs, jours_maintenance)

    st.subheader("🧠 Diagnostic automatique")

    if couleur == "good":
        st.success(f"✅ {etat}")
    elif couleur == "warning":
        st.warning(f"⚠️ {etat}")
    else:
        st.error(f"🚨 {etat}")

    st.subheader("🛠️ Actions recommandées")

    for action in actions:
        st.write("•", action)

# =========================
# RAPPORT
# =========================
elif menu == "📄 Rapport":
    st.title("📄 Rapport automatique")

    nom_patient = st.text_input("Nom / ID patient", "Patient_001")
    age = st.number_input("Âge", 1, 120, 45)
    poids = st.number_input("Poids (kg)", 20.0, 200.0, 70.0)
    taille = st.number_input("Taille (cm)", 100.0, 220.0, 170.0)

    imc = calcul_imc(poids, taille)
    dose_opt = calcul_dose_optimale(age, imc)
    snr = calcul_snr(age, imc, dose_opt)
    interpretation, color_snr = interpretation_snr(snr)

    rapport = f"""
RAPPORT PCCT INTELLIGENT

Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}

Patient : {nom_patient}
Âge : {age} ans
Poids : {poids} kg
Taille : {taille} cm

IMC : {imc:.2f}
Dose optimale estimée : {dose_opt:.2f} mGy
SNR estimé : {snr:.2f}

Interprétation :
{interpretation}

Conclusion :
Le système propose une optimisation personnalisée de la dose patient
tout en gardant une qualité d’image acceptable.
"""

    st.text_area("Rapport généré", rapport, height=350)

    st.download_button(
        label="📥 Télécharger le rapport",
        data=rapport,
        file_name=f"rapport_{nom_patient}.txt",
        mime="text/plain"
    )
