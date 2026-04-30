import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import base64
import os

st.set_page_config(page_title="PCCT Intelligent System", page_icon="🧠", layout="wide")

def get_base64_image(image_path):
    if not os.path.exists(image_path):
        st.warning(f"Image introuvable : {image_path}")
        return None
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def set_background(image_path):
    img_base64 = get_base64_image(image_path)
    if img_base64:
        st.markdown(f"""
        <style>
        .stApp {{
            background:
            linear-gradient(rgba(3,10,20,0.48), rgba(3,10,20,0.82)),
            url("data:image/png;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """, unsafe_allow_html=True)

st.markdown("""
<style>
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #04111f, #071827);
    border-right: 1px solid rgba(0, 212, 255, 0.25);
}
[data-testid="stSidebar"] * { color: white; }

h1 { color: white; font-size: 42px; font-weight: 900; }
h2, h3 { color: #22d3ee; }
p, label, span, div { color: #f8fafc; }

.pcct-title {
    font-size: 72px;
    font-weight: 900;
    color: white;
}
.pcct-subtitle {
    font-size: 28px;
    color: #22d3ee;
    font-weight: 800;
}
.card {
    background: rgba(5, 20, 35, 0.82);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(34, 211, 238, 0.28);
    border-radius: 18px;
    padding: 24px;
    box-shadow: 0 0 28px rgba(34, 211, 238, 0.16);
    margin-bottom: 18px;
}
.green-card {
    background: rgba(0, 80, 55, 0.45);
    border: 1px solid rgba(34, 197, 94, 0.45);
    border-radius: 16px;
    padding: 18px;
}
.warning-card {
    background: rgba(95, 65, 0, 0.45);
    border: 1px solid rgba(250, 204, 21, 0.45);
    border-radius: 16px;
    padding: 18px;
}
.stButton>button, .stDownloadButton>button {
    background: linear-gradient(135deg, #0891b2, #7c3aed);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 28px;
    font-weight: 800;
}
[data-testid="stMetric"] {
    background: rgba(5, 20, 35, 0.84);
    border: 1px solid rgba(34, 211, 238, 0.25);
    border-radius: 18px;
    padding: 18px;
}
.stTextInput input, .stNumberInput input, .stSelectbox div, textarea {
    background-color: rgba(5, 20, 35, 0.92) !important;
    color: white !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

def calcul_imc(poids, taille_cm):
    return poids / ((taille_cm / 100) ** 2)

def categorie_imc(imc):
    if imc < 18.5:
        return "Maigreur"
    elif imc < 25:
        return "Normal"
    elif imc < 30:
        return "Surpoids"
    return "Obésité"

def calcul_dose(age, imc):
    return round(4.5 + 0.08 * imc + 0.015 * age, 2)

def calcul_snr(age, imc, dose):
    return round(max(70 - 0.35 * imc - 0.08 * age + 1.8 * dose, 10), 2)

def etat_scanner(snr, temperature, erreurs, jours):
    score = 100
    if snr < 50:
        score -= 25
    if temperature > 75:
        score -= 25
    if erreurs >= 5:
        score -= 25
    if jours > 90:
        score -= 25

    if score >= 75:
        return score, "BON ÉTAT", "success"
    elif score >= 50:
        return score, "À SURVEILLER", "warning"
    return score, "RISQUE ÉLEVÉ", "error"

st.sidebar.markdown("## PCCT")
st.sidebar.markdown("##### INTELLIGENT SYSTEM")

menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Accueil",
        "👩‍🔧 Espace Technicien",
        "📊 Qualité Image SNR",
        "🛠️ Suivi Scanner PCCT",
        "🔮 Maintenance Prédictive",
        "📄 Rapports & Historique"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div class="card">
<h4>État global du système</h4>
<h3 style="color:#22c55e;">● Optimal</h3>
<p>Tous les systèmes fonctionnent normalement.</p>
</div>
""", unsafe_allow_html=True)

if menu == "🏠 Accueil":
    set_background("images/accueil.png")

    st.markdown("""
    <br><br>
    <div class="pcct-title">PCCT</div>
    <div class="pcct-subtitle">INTELLIGENT SYSTEM</div>
    <br>
    <h3>Optimisation de la dose patient<br>et suivi intelligent de l’état du scanner PCCT</h3>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="card">
        <h3>👨‍⚕️ Pour les Techniciens</h3>
        <p>Optimisez chaque examen en fonction du patient pour assurer la meilleure qualité d’image avec la dose la plus faible possible.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card">
        <h3>🛠️ Pour le Service Après-Vente</h3>
        <p>Suivez l’état du scanner PCCT et anticipez les pannes grâce à l’intelligence artificielle.</p>
        </div>
        """, unsafe_allow_html=True)

elif menu == "👩‍🔧 Espace Technicien":
    set_background("images/technicien.png")

    st.title("Espace Technicien")
    st.markdown("### Optimisation patient & paramètres d’acquisition")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Données Patient")

        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        cin = st.text_input("CIN")

        age = st.number_input("Âge (ans)", 1, 120, 45)
        sexe = st.selectbox("Sexe", ["Femme", "Homme"])
        poids = st.number_input("Poids (kg)", 20.0, 200.0, 65.0)
        taille = st.number_input("Taille (cm)", 100.0, 220.0, 165.0)
        region = st.selectbox("Région anatomique", ["Abdomen", "Thorax", "Crâne", "Cardiaque"])
        protocole = st.selectbox("Protocole", ["Standard", "Faible dose", "Haute résolution"])
        st.markdown('</div>', unsafe_allow_html=True)

    imc = calcul_imc(poids, taille)
    dose = calcul_dose(age, imc)
    snr = calcul_snr(age, imc, dose)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Résultats Automatiques")
        c1, c2, c3 = st.columns(3)
        c1.metric("IMC", f"{imc:.1f}", categorie_imc(imc))
        c2.metric("Dose optimale", f"{dose} mGy")
        c3.metric("SNR estimé", f"{snr}")
        st.markdown('</div>', unsafe_allow_html=True)

        if snr >= 50:
            st.markdown("""
            <div class="green-card">
            <h3>✅ Protocole adapté</h3>
            <p>Bonne qualité d’image avec dose optimisée.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warning-card">
            <h3>⚠️ SNR faible</h3>
            <p>Vérifier la calibration ou ajuster les paramètres d’acquisition.</p>
            </div>
            """, unsafe_allow_html=True)

elif menu == "📊 Qualité Image SNR":
    set_background("images/snr.png")

    st.title("Qualité d’Image - SNR")
    st.markdown("### Analyse de la qualité d’image en fonction de la dose")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        imc_test = st.slider("IMC", 15, 45, 27)
        age_test = st.slider("Âge", 10, 90, 45)
        dose_actuelle = st.slider("Dose actuelle (mGy)", 2.0, 15.0, 8.2)
        snr_actuel = calcul_snr(age_test, imc_test, dose_actuelle)
        st.metric("SNR actuel", snr_actuel, "Acceptable" if snr_actuel >= 50 else "Faible")
        st.metric("Dose actuelle", f"{dose_actuelle} mGy")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        doses = np.linspace(2, 15, 25)
        snr_values = [calcul_snr(age_test, imc_test, d) for d in doses]
        df = pd.DataFrame({"Dose (mGy)": doses, "SNR estimé": snr_values})

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Courbe Dose vs SNR")
        st.line_chart(df.set_index("Dose (mGy)"))
        st.markdown("""
        **Interprétation :**  
        🟢 SNR ≥ 50 : qualité acceptable  
        🟡 40 ≤ SNR < 50 : qualité moyenne  
        🔴 SNR < 40 : qualité insuffisante
        """)
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🛠️ Suivi Scanner PCCT":
    set_background("images/suivi.png")

    st.title("Suivi de l’État du Scanner PCCT")
    st.markdown("### Tableau de bord en temps réel")

    snr_moyen = st.number_input("SNR moyen hebdomadaire", 10.0, 100.0, 51.2)
    dose_moyenne = st.number_input("Dose moyenne hebdomadaire (mGy)", 1.0, 30.0, 8.7)
    temperature = st.number_input("Température tube RX (°C)", 20.0, 120.0, 67.0)
    erreurs = st.number_input("Erreurs système / semaine", 0, 50, 2)
    examens = st.number_input("Examens cette semaine", 0, 1000, 142)
    jours = st.number_input("Jours depuis dernière maintenance", 0, 365, 15)

    c1, c2, c3 = st.columns(3)
    c1.metric("SNR moyen", snr_moyen, "Acceptable")
    c2.metric("Dose moyenne", f"{dose_moyenne} mGy", "Optimale")
    c3.metric("Température tube", f"{temperature} °C", "Normale")

    c4, c5, c6 = st.columns(3)
    c4.metric("Erreurs système", erreurs, "Faible")
    c5.metric("Examens", examens, "+12%")
    c6.metric("Dernière maintenance", f"{jours} jours")

    score, etat, niveau = etat_scanner(snr_moyen, temperature, erreurs, jours)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("État global du scanner")
    st.metric(etat, f"{score}/100")
    if niveau == "success":
        st.success("✅ Le scanner fonctionne normalement.")
    elif niveau == "warning":
        st.warning("⚠️ Certaines valeurs nécessitent une surveillance.")
    else:
        st.error("🚨 Risque de panne élevé.")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🔮 Maintenance Prédictive":
    set_background("images/maintenance.png")

    st.title("Maintenance Prédictive")
    st.markdown("### Anticipez les pannes, évitez les interruptions")

    snr_moyen = st.slider("SNR moyen", 10, 100, 48)
    temperature = st.slider("Température tube", 20, 120, 78)
    erreurs = st.slider("Erreurs système", 0, 50, 6)
    jours = st.slider("Jours depuis maintenance", 0, 365, 120)

    score, etat, niveau = etat_scanner(snr_moyen, temperature, erreurs, jours)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("Score de santé", f"{score}/100", etat)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Points d’attention")
        if snr_moyen < 50:
            st.write("⚠️ SNR en baisse progressive")
        if temperature > 75:
            st.write("⚠️ Température tube légèrement élevée")
        if erreurs >= 5:
            st.write("⚠️ Erreurs système répétées")
        if jours > 90:
            st.write("⚠️ Maintenance préventive à prévoir")
        if snr_moyen >= 50 and temperature <= 75 and erreurs < 5 and jours <= 90:
            st.write("✅ Aucun point critique détecté")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
    <h3>Actions recommandées</h3>
    <p>🛠️ Vérifier la calibration des détecteurs</p>
    <p>❄️ Nettoyer le système de refroidissement</p>
    <p>📅 Planifier une maintenance préventive</p>
    <p>📈 Surveiller l’évolution du SNR</p>
    </div>
    """, unsafe_allow_html=True)

elif menu == "📄 Rapports & Historique":
    set_background("images/rapport.png")

    st.title("Rapports & Historique")
    st.markdown("### Consultez et exportez vos rapports")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Générer un rapport")
        type_rapport = st.selectbox("Type de rapport", ["Rapport patient", "Rapport scanner", "Rapport maintenance"])
        periode = st.selectbox("Période", ["Cette semaine", "Ce mois", "Cette année"])

        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        cin = st.text_input("CIN")

        age = st.number_input("Âge patient", 1, 120, 45)
        poids = st.number_input("Poids patient (kg)", 20.0, 200.0, 65.0)
        taille = st.number_input("Taille patient (cm)", 100.0, 220.0, 165.0)
        st.markdown('</div>', unsafe_allow_html=True)

    imc = calcul_imc(poids, taille)
    dose = calcul_dose(age, imc)
    snr = calcul_snr(age, imc, dose)

    with col2:
        historique = pd.DataFrame({
            "Date": ["30/04/2026", "23/04/2026", "16/04/2026"],
            "Type": ["Rapport patient", "Rapport scanner", "Rapport maintenance"],
            "Période": ["Cette semaine", "Cette semaine", "Semaine précédente"],
            "Statut": ["Terminé", "Terminé", "Terminé"]
        })

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Historique des rapports")
        st.dataframe(historique, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    rapport = f"""
RAPPORT PCCT INTELLIGENT SYSTEM

Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}
Type : {type_rapport}
Période : {periode}

Nom : {nom}
Prénom : {prenom}
CIN : {cin}

Âge : {age} ans
Poids : {poids} kg
Taille : {taille} cm

IMC : {imc:.2f}
Catégorie IMC : {categorie_imc(imc)}
Dose optimale estimée : {dose} mGy
SNR estimé : {snr}

Conclusion :
Le système assure l’optimisation de la dose patient,
l’analyse du SNR et le suivi intelligent de l’état du scanner PCCT.
"""

    st.text_area("Aperçu du rapport", rapport, height=300)

    st.download_button(
        "📥 Télécharger le rapport",
        data=rapport,
        file_name=f"{type_rapport}_{nom}_{prenom}.txt",
        mime="text/plain"
    )
