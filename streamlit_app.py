import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import base64
import os
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

st.set_page_config(page_title="PCCT Intelligent System", layout="wide")

# =========================
# BACKGROUND
# =========================
def get_base64_image(path):
    if not os.path.exists(path):
        st.warning(f"Image introuvable : {path}")
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def set_bg(path):
    img = get_base64_image(path)
    if img:
        st.markdown(f"""
        <style>
        .stApp {{
            background:
            linear-gradient(rgba(0,0,0,0.72), rgba(0,0,0,0.88)),
            url("data:image/png;base64,{img}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """, unsafe_allow_html=True)

# =========================
# STYLE
# =========================
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background:#03111f;
}
[data-testid="stSidebar"] * {
    color:white;
}
.card {
    background:rgba(5,20,35,0.85);
    padding:22px;
    border-radius:18px;
    margin-bottom:18px;
    border:1px solid rgba(14,165,233,0.35);
    box-shadow:0 0 18px rgba(0,0,0,0.45);
}
h1, h2, h3, p, label, div {
    color:white;
}
.stButton > button {
    background:#0ea5e9;
    color:white;
    border-radius:12px;
    border:none;
    font-weight:bold;
}
[data-testid="stMetric"] {
    background:rgba(5,20,35,0.88);
    padding:15px;
    border-radius:15px;
    border:1px solid rgba(14,165,233,0.3);
}
</style>
""", unsafe_allow_html=True)

# =========================
# SESSION
# =========================
if "patients" not in st.session_state:
    st.session_state.patients = []

if "dernier_patient" not in st.session_state:
    st.session_state.dernier_patient = None

# =========================
# FONCTIONS
# =========================
def calcul_imc(poids, taille):
    return poids / ((taille / 100) ** 2)

def classe_imc(imc):
    if imc < 18.5:
        return "Maigreur"
    elif imc < 25:
        return "Normal"
    elif imc < 30:
        return "Surpoids"
    else:
        return "Obésité"

def protocole_examen(type_examen):
    protocoles = {
        "Scanner cérébral": {"ctdi": 50, "kvp": 120, "mas": 250, "dlp": 900},
        "Scanner thoracique": {"ctdi": 10, "kvp": 100, "mas": 120, "dlp": 350},
        "Scanner abdominal": {"ctdi": 15, "kvp": 120, "mas": 180, "dlp": 600},
        "Scanner cardiaque": {"ctdi": 20, "kvp": 100, "mas": 220, "dlp": 450},
        "Scanner pulmonaire": {"ctdi": 8, "kvp": 100, "mas": 90, "dlp": 250},
        "Scanner osseux": {"ctdi": 12, "kvp": 120, "mas": 160, "dlp": 400},
        "Scanner pelvien": {"ctdi": 14, "kvp": 120, "mas": 170, "dlp": 500},
        "Scanner corps entier": {"ctdi": 25, "kvp": 120, "mas": 300, "dlp": 1100}
    }
    return protocoles[type_examen]

def dose_adaptee(age, imc, type_examen):
    p = protocole_examen(type_examen)
    ctdi_ref = p["ctdi"]

    facteur_imc = 1 + 0.015 * (imc - 25)
    facteur_age = 1 + 0.002 * (age - 40)

    dose = ctdi_ref * facteur_imc * facteur_age
    dose = max(dose, ctdi_ref * 0.55)
    dose = min(dose, ctdi_ref * 1.35)

    return round(dose, 2)

def calcul_snr(age, imc, dose):
    snr = 60 - 0.30 * imc - 0.05 * age + 0.70 * dose
    return round(max(snr, 10), 2)

def adaptation_parametres(age, imc, type_examen, dose, snr):
    p = protocole_examen(type_examen)

    kvp = p["kvp"]
    mas = p["mas"]

    if imc > 30:
        mas *= 1.20
    elif imc < 20:
        mas *= 0.85

    if snr < 50:
        mas *= 1.15
    elif snr > 65:
        mas *= 0.90

    ctdi = dose
    dlp = p["dlp"] * (dose / p["ctdi"])

    return round(kvp), round(mas), round(ctdi, 2), round(dlp, 2)

def recommandation_ia(snr, dose, imc):
    if snr < 50:
        return "SNR faible : augmenter légèrement le mAs ou ajuster la dose."
    elif dose > 30 and imc < 25:
        return "Dose élevée : réduction progressive possible tout en surveillant le SNR."
    elif snr >= 50 and dose <= 25:
        return "Paramètres acceptables : dose optimisée avec qualité image correcte."
    elif imc > 30:
        return "Patient à IMC élevé : surveiller le bruit image et adapter le mAs."
    else:
        return "Acquisition acceptable selon les paramètres estimés."

def stress_score(snr_sys, temp, vibration, heures):
    score = 0
    score += max(0, (50 - snr_sys)) * 1.5
    score += max(0, (temp - 60)) * 1.2
    score += vibration * 0.4
    score += heures * 0.01
    return round(min(score, 100), 2)

def etat_systeme(score):
    if score < 35:
        return "Stable"
    elif score < 70:
        return "À surveiller"
    else:
        return "Critique"

# =========================
# PDF
# =========================
def generer_pdf(patient):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    largeur, hauteur = A4

    pdf.setFillColor(colors.HexColor("#04111f"))
    pdf.rect(0, 0, largeur, hauteur, fill=1)

    pdf.setFillColor(colors.HexColor("#0ea5e9"))
    pdf.rect(0, hauteur - 90, largeur, 90, fill=1)

    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(40, hauteur - 45, "PCCT Intelligent System")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(40, hauteur - 70, "Rapport patient - Optimisation dose, SNR et paramètres scanner")

    y = hauteur - 125

    def section(titre):
        nonlocal y
        pdf.setFillColor(colors.HexColor("#0ea5e9"))
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(40, y, titre)
        y -= 25

    def ligne(label, valeur):
        nonlocal y
        pdf.setFillColor(colors.white)
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(55, y, f"{label} :")
        pdf.setFont("Helvetica", 11)
        pdf.drawString(200, y, str(valeur))
        y -= 20

    section("Informations patient")
    ligne("Date", patient["Date"])
    ligne("Nom", patient["Nom"])
    ligne("Prénom", patient["Prénom"])
    ligne("CIN", patient["CIN"])
    ligne("Âge", patient["Age"])
    ligne("Poids", f'{patient["Poids"]} kg')
    ligne("Taille", f'{patient["Taille"]} cm')
    ligne("IMC", patient["IMC"])
    ligne("Classe IMC", patient["Classe IMC"])

    y -= 10
    section("Examen")
    ligne("Type d'examen", patient["Type examen"])

    y -= 10
    section("Paramètres recommandés")
    ligne("Dose recommandée", f'{patient["Dose"]} mGy')
    ligne("SNR estimé", patient["SNR"])
    ligne("kVp", patient["kVp"])
    ligne("mAs", patient["mAs"])
    ligne("CTDIvol", f'{patient["CTDIvol"]} mGy')
    ligne("DLP", f'{patient["DLP"]} mGy.cm')

    y -= 10
    section("Recommandation IA")

    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica", 11)

    reco = patient["Recommandation"]
    lignes_reco = [reco[i:i+80] for i in range(0, len(reco), 80)]

    for l in lignes_reco:
        pdf.drawString(55, y, l)
        y -= 18

    y -= 20
    section("Conclusion")

    conclusion = (
        "Qualité image acceptable."
        if patient["SNR"] >= 50
        else "Qualité image insuffisante : ajustement recommandé."
    )

    ligne("Résultat", conclusion)

    pdf.setFillColor(colors.HexColor("#0ea5e9"))
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(40, 35, "Rapport généré automatiquement par PCCT Intelligent System")

    pdf.save()
    buffer.seek(0)
    return buffer

# =========================
# MENU
# =========================
st.sidebar.title("PCCT Intelligent System")

menu = st.sidebar.radio(
    "Navigation",
    ["Accueil", "Technicien", "SNR", "Suivi", "Maintenance", "Dashboard", "Rapport"]
)

# =========================
# ACCUEIL
# =========================
if menu == "Accueil":
    set_bg("accueil.png")

    st.title("PCCT Intelligent System")
    st.subheader("Optimisation intelligente de dose, SNR et maintenance prédictive")

    st.markdown("""
    <div class="card">
    <h3>Objectif de l'application</h3>
    <p>
    Cette plateforme propose une dose adaptée au patient tout en conservant
    une qualité d'image acceptable, puis surveille l'état du scanner pour anticiper
    les besoins de maintenance.
    </p>
    </div>
    """, unsafe_allow_html=True)

# =========================
# TECHNICIEN
# =========================
elif menu == "Technicien":
    set_bg("technicien.png")

    st.title("Espace Technicien")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        cin = st.text_input("CIN")

        type_examen = st.selectbox(
            "Type d'examen",
            [
                "Scanner cérébral",
                "Scanner thoracique",
                "Scanner abdominal",
                "Scanner cardiaque",
                "Scanner pulmonaire",
                "Scanner osseux",
                "Scanner pelvien",
                "Scanner corps entier"
            ]
        )

        age = st.number_input("Âge", 1, 120, 45)
        poids = st.number_input("Poids (kg)", 20.0, 200.0, 70.0)
        taille = st.number_input("Taille (cm)", 100.0, 220.0, 170.0)

        bouton = st.button("Calculer et enregistrer")

        st.markdown('</div>', unsafe_allow_html=True)

    imc = calcul_imc(poids, taille)
    dose = dose_adaptee(age, imc, type_examen)
    snr = calcul_snr(age, imc, dose)
    kvp, mas, ctdi, dlp = adaptation_parametres(age, imc, type_examen, dose, snr)
    reco = recommandation_ia(snr, dose, imc)

    with col2:
        st.metric("IMC", round(imc, 2))
        st.metric("Classe IMC", classe_imc(imc))
        st.metric("Dose recommandée", f"{dose} mGy")
        st.metric("SNR estimé", snr)
        st.metric("kVp recommandé", kvp)
        st.metric("mAs recommandé", mas)
        st.metric("CTDIvol", f"{ctdi} mGy")
        st.metric("DLP", f"{dlp} mGy.cm")

        if snr >= 50:
            st.success("Qualité image acceptable")
        else:
            st.error("SNR insuffisant")

        st.info(f"Recommandation IA : {reco}")

    if bouton:
        patient = {
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Nom": nom,
            "Prénom": prenom,
            "CIN": cin,
            "Type examen": type_examen,
            "Age": age,
            "Poids": poids,
            "Taille": taille,
            "IMC": round(imc, 2),
            "Classe IMC": classe_imc(imc),
            "Dose": dose,
            "SNR": snr,
            "kVp": kvp,
            "mAs": mas,
            "CTDIvol": ctdi,
            "DLP": dlp,
            "Recommandation": reco
        }

        st.session_state.patients.append(patient)
        st.session_state.dernier_patient = patient
        st.success("Patient enregistré. Le rapport PDF est prêt dans la page Rapport.")

# =========================
# RAPPORT
# =========================
elif menu == "Rapport":
    set_bg("rapport.png")

    st.title("Rapport Patient PDF")

    patient = st.session_state.dernier_patient

    if patient is None:
        st.warning("Aucun patient enregistré. Va d'abord dans l'espace Technicien et clique sur Calculer et enregistrer.")
    else:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.subheader("Aperçu du rapport")

        st.write(f"**Nom :** {patient['Nom']}")
        st.write(f"**Prénom :** {patient['Prénom']}")
        st.write(f"**CIN :** {patient['CIN']}")
        st.write(f"**Type d'examen :** {patient['Type examen']}")
        st.write(f"**IMC :** {patient['IMC']} — {patient['Classe IMC']}")
        st.write(f"**Dose recommandée :** {patient['Dose']} mGy")
        st.write(f"**SNR estimé :** {patient['SNR']}")
        st.write(f"**kVp :** {patient['kVp']}")
        st.write(f"**mAs :** {patient['mAs']}")
        st.write(f"**CTDIvol :** {patient['CTDIvol']} mGy")
        st.write(f"**DLP :** {patient['DLP']} mGy.cm")
        st.info(patient["Recommandation"])

        pdf_file = generer_pdf(patient)

        st.download_button(
            "Télécharger le rapport PDF",
            data=pdf_file,
            file_name="rapport_patient_pcct.pdf",
            mime="application/pdf"
        )

        st.markdown('</div>', unsafe_allow_html=True)

# =========================
# SNR
# =========================
elif menu == "SNR":
    set_bg("snr.png")
    st.title("Analyse SNR")

    imc_v = st.slider("IMC", 15, 45, 25)
    age_v = st.slider("Âge", 10, 90, 40)

    doses = np.linspace(3, 60, 40)
    snrs = [calcul_snr(age_v, imc_v, d) for d in doses]

    df = pd.DataFrame({"Dose": doses, "SNR": snrs})
    st.line_chart(df.set_index("Dose"))

# =========================
# SUIVI
# =========================
elif menu == "Suivi":
    set_bg("suivi.png")
    st.title("Suivi Scanner")

    snr_sys = st.number_input("SNR système", 10.0, 100.0, 52.0)
    temp = st.number_input("Température tube RX (°C)", 20.0, 120.0, 60.0)
    vibration = st.slider("Vibration gantry (%)", 0, 100, 25)
    heures = st.number_input("Heures d'utilisation du scanner", 0, 50000, 5000)

    score = stress_score(snr_sys, temp, vibration, heures)
    etat = etat_systeme(score)

    st.metric("Score de stress système", score)
    st.metric("État système", etat)

    if etat == "Stable":
        st.success("Scanner stable")
    elif etat == "À surveiller":
        st.warning("Scanner à surveiller")
    else:
        st.error("Risque élevé : maintenance recommandée")

# =========================
# MAINTENANCE
# =========================
elif menu == "Maintenance":
    set_bg("maintenance.png")
    st.title("Maintenance prédictive")

    snr_sys = st.number_input("SNR système", 10.0, 100.0, 48.0)
    temp = st.number_input("Température tube RX (°C)", 20.0, 120.0, 78.0)
    vibration = st.slider("Vibration gantry (%)", 0, 100, 55)
    heures = st.number_input("Heures d'utilisation", 0, 50000, 12000)

    score = stress_score(snr_sys, temp, vibration, heures)
    etat = etat_systeme(score)

    st.metric("Score maintenance", score)
    st.metric("État", etat)

    if etat == "Stable":
        st.success("Fonctionnement normal")
    elif etat == "À surveiller":
        st.warning("Contrôle préventif recommandé")
    else:
        st.error("Inspection tube RX / détecteurs recommandée")

# =========================
# DASHBOARD
# =========================
elif menu == "Dashboard":
    set_bg("rapport.png")
    st.title("Dashboard global")

    if len(st.session_state.patients) == 0:
        st.warning("Aucun patient enregistré pour le moment.")
    else:
        df_patients = pd.DataFrame(st.session_state.patients)

        col1, col2, col3 = st.columns(3)
        col1.metric("Nombre patients", len(df_patients))
        col2.metric("Dose moyenne", round(df_patients["Dose"].mean(), 2))
        col3.metric("SNR moyen", round(df_patients["SNR"].mean(), 2))

        st.dataframe(df_patients)
        st.line_chart(df_patients[["Dose", "SNR"]])

        csv = df_patients.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Télécharger historique CSV",
            csv,
            file_name="historique_patients.csv",
            mime="text/csv"
        )
