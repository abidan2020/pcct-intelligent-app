import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import base64
import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

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
[data-testid="stSidebar"] { background:#03111f; }
[data-testid="stSidebar"] * { color:white; }

.card {
    background:rgba(5,20,35,0.85);
    padding:22px;
    border-radius:18px;
    margin-bottom:18px;
    border:1px solid rgba(14,165,233,0.35);
    box-shadow:0 0 18px rgba(0,0,0,0.45);
}

h1, h2, h3, p, label, div { color:white; }

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


def generer_pdf(patient):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    largeur, hauteur = A4

    y = hauteur - 60

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(190, y, "Rapport Patient")

    y -= 50

    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, y, f"Date : {patient.get('Date', 'Non renseigné')}")

    y -= 45

    def titre(txt):
        nonlocal y
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, y, txt)
        y -= 30

    def ligne(label, valeur):
        nonlocal y
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(60, y, f"{label} :")
        pdf.setFont("Helvetica", 11)
        pdf.drawString(220, y, str(valeur))
        y -= 22

    titre("Informations Patient")
    ligne("Nom", patient.get("Nom", "Non renseigné"))
    ligne("Prénom", patient.get("Prénom", "Non renseigné"))
    ligne("CIN", patient.get("CIN", "Non renseigné"))
    ligne("Sexe", patient.get("Sexe", "Non renseigné"))
    ligne("Âge", patient.get("Age", "Non renseigné"))
    ligne("Poids", f"{patient.get('Poids', 'Non renseigné')} kg")
    ligne("Taille", f"{patient.get('Taille', 'Non renseigné')} cm")
    ligne("IMC", patient.get("IMC", "Non renseigné"))
    ligne("Classe IMC", patient.get("Classe IMC", "Non renseigné"))

    y -= 10
    titre("Examen")
    ligne("Type d'examen", patient.get("Type examen", "Non renseigné"))

    y -= 10
    titre("Paramètres recommandés")
    ligne("Dose recommandée", f"{patient.get('Dose', 'Non renseigné')} mGy")
    ligne("SNR estimé", patient.get("SNR", "Non renseigné"))
    ligne("kVp", patient.get("kVp", "Non renseigné"))
    ligne("mAs", patient.get("mAs", "Non renseigné"))
    ligne("CTDIvol", f"{patient.get('CTDIvol', 'Non renseigné')} mGy")
    ligne("DLP", f"{patient.get('DLP', 'Non renseigné')} mGy.cm")

    y -= 10
    titre("Recommandation IA")

    reco = str(patient.get("Recommandation", "Non renseigné"))
    pdf.setFont("Helvetica", 11)

    for i in range(0, len(reco), 80):
        pdf.drawString(60, y, reco[i:i+80])
        y -= 18

    y -= 20
    titre("Conclusion")

    try:
        snr_value = float(patient.get("SNR", 0))
    except:
        snr_value = 0

    conclusion = (
        "Qualité image acceptable."
        if snr_value >= 50
        else "Qualité image insuffisante : ajustement recommandé."
    )

    pdf.setFont("Helvetica", 11)
    pdf.drawString(60, y, conclusion)

    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(50, 30, "PCCT Intelligent System")

    pdf.save()
    buffer.seek(0)

    return buffer


def generer_excel(df_patients):
    excel_buffer = BytesIO()

    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df_patients.to_excel(
            writer,
            index=False,
            sheet_name="Patients"
        )

        worksheet = writer.sheets["Patients"]

        for column_cells in worksheet.columns:
            longueur = max(
                len(str(cell.value)) if cell.value is not None else 0
                for cell in column_cells
            )

            worksheet.column_dimensions[
                column_cells[0].column_letter
            ].width = longueur + 4

    excel_buffer.seek(0)
    return excel_buffer

# =========================
# MENU
# =========================
st.sidebar.title("PCCT Intelligent System")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Accueil",
        "Technicien",
        "SNR",
        "Dashboard",
        "Rapport"
    ]
)

# =========================
# ACCUEIL
# =========================
if menu == "Accueil":
    set_bg("accueil.png")

    st.title("PCCT Intelligent System")
    st.subheader("Optimisation intelligente de dose et qualité image")

    st.markdown("""
    <div class="card">
    <h3>Objectif de l'application</h3>
    <p>
    Cette application permet de calculer une dose personnalisée selon le patient,
    d'estimer le SNR, d'adapter les paramètres scanner et de générer un rapport PDF.
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

        sexe = st.selectbox(
            "Sexe",
            ["Homme", "Femme"]
        )

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

    kvp, mas, ctdi, dlp = adaptation_parametres(
        age,
        imc,
        type_examen,
        dose,
        snr
    )

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
        if cin.strip() == "":
            st.error("Veuillez entrer le CIN du patient.")
        else:
            patient_existe = any(
                p.get("CIN", "").strip().upper() == cin.strip().upper()
                for p in st.session_state.patients
            )

            if patient_existe:
                st.warning("Ce patient est déjà enregistré.")
            else:
                patient = {
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Nom": nom,
                    "Prénom": prenom,
                    "CIN": cin,
                    "Sexe": sexe,
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
                st.success("Le patient a été bien enregistré.")

# =========================
# RAPPORT + MODIFICATION
# =========================
elif menu == "Rapport":
    set_bg("rapport.png")

    st.title("Rapports Patients")

    if len(st.session_state.patients) == 0:
        st.warning("Aucun patient enregistré.")
    else:
        df_patients = pd.DataFrame(st.session_state.patients)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Liste des patients enregistrés")
        st.dataframe(df_patients, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        patient_index = st.selectbox(
            "Choisir un patient",
            df_patients.index,
            format_func=lambda x:
            f"{df_patients.loc[x, 'Nom']} "
            f"{df_patients.loc[x, 'Prénom']} "
            f"- {df_patients.loc[x, 'Type examen']}"
        )

        patient = df_patients.loc[patient_index].to_dict()

        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.subheader("Modifier les informations du patient")

        examens = [
            "Scanner cérébral",
            "Scanner thoracique",
            "Scanner abdominal",
            "Scanner cardiaque",
            "Scanner pulmonaire",
            "Scanner osseux",
            "Scanner pelvien",
            "Scanner corps entier"
        ]

        with st.form("form_modification_patient"):
            nouveau_nom = st.text_input("Nom", patient.get("Nom", ""))
            nouveau_prenom = st.text_input("Prénom", patient.get("Prénom", ""))
            nouveau_cin = st.text_input("CIN", patient.get("CIN", ""))

            nouveau_sexe = st.selectbox(
                "Sexe",
                ["Homme", "Femme"],
                index=0 if patient.get("Sexe", "Homme") == "Homme" else 1
            )

            ancien_type = patient.get("Type examen", "Scanner thoracique")

            nouveau_type = st.selectbox(
                "Type d'examen",
                examens,
                index=examens.index(ancien_type) if ancien_type in examens else 1
            )

            nouveau_age = st.number_input(
                "Âge",
                1,
                120,
                int(patient.get("Age", 45))
            )

            nouveau_poids = st.number_input(
                "Poids (kg)",
                20.0,
                200.0,
                float(patient.get("Poids", 70.0))
            )

            nouveau_taille = st.number_input(
                "Taille (cm)",
                100.0,
                220.0,
                float(patient.get("Taille", 170.0))
            )

            modifier = st.form_submit_button("Enregistrer les modifications")

        if modifier:
            if nouveau_cin.strip() == "":
                st.error("Le CIN ne peut pas être vide.")
            else:
                cin_existe = any(
                    i != patient_index and
                    p.get("CIN", "").strip().upper() == nouveau_cin.strip().upper()
                    for i, p in enumerate(st.session_state.patients)
                )

                if cin_existe:
                    st.warning("Ce CIN existe déjà pour un autre patient.")
                else:
                    imc_mod = calcul_imc(nouveau_poids, nouveau_taille)
                    dose_mod = dose_adaptee(nouveau_age, imc_mod, nouveau_type)
                    snr_mod = calcul_snr(nouveau_age, imc_mod, dose_mod)

                    kvp_mod, mas_mod, ctdi_mod, dlp_mod = adaptation_parametres(
                        nouveau_age,
                        imc_mod,
                        nouveau_type,
                        dose_mod,
                        snr_mod
                    )

                    reco_mod = recommandation_ia(snr_mod, dose_mod, imc_mod)

                    st.session_state.patients[patient_index] = {
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Nom": nouveau_nom,
                        "Prénom": nouveau_prenom,
                        "CIN": nouveau_cin,
                        "Sexe": nouveau_sexe,
                        "Type examen": nouveau_type,
                        "Age": nouveau_age,
                        "Poids": nouveau_poids,
                        "Taille": nouveau_taille,
                        "IMC": round(imc_mod, 2),
                        "Classe IMC": classe_imc(imc_mod),
                        "Dose": dose_mod,
                        "SNR": snr_mod,
                        "kVp": kvp_mod,
                        "mAs": mas_mod,
                        "CTDIvol": ctdi_mod,
                        "DLP": dlp_mod,
                        "Recommandation": reco_mod
                    }

                    st.success("Les informations du patient ont été modifiées avec succès.")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        patient = pd.DataFrame(st.session_state.patients).loc[patient_index].to_dict()

        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.subheader("Aperçu du rapport")

        st.write(f"**Nom :** {patient.get('Nom')}")
        st.write(f"**Prénom :** {patient.get('Prénom')}")
        st.write(f"**CIN :** {patient.get('CIN')}")
        st.write(f"**Sexe :** {patient.get('Sexe')}")
        st.write(f"**Type d'examen :** {patient.get('Type examen')}")
        st.write(f"**IMC :** {patient.get('IMC')} — {patient.get('Classe IMC')}")
        st.write(f"**Dose :** {patient.get('Dose')} mGy")
        st.write(f"**SNR :** {patient.get('SNR')}")
        st.write(f"**kVp :** {patient.get('kVp')}")
        st.write(f"**mAs :** {patient.get('mAs')}")
        st.write(f"**CTDIvol :** {patient.get('CTDIvol')} mGy")
        st.write(f"**DLP :** {patient.get('DLP')} mGy.cm")
        st.info(patient.get("Recommandation"))

        pdf_file = generer_pdf(patient)

        st.download_button(
            "Télécharger le rapport PDF",
            data=pdf_file,
            file_name=f"rapport_{patient.get('Nom')}_{patient.get('Prénom')}.pdf",
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

    df = pd.DataFrame({
        "Dose": doses,
        "SNR": snrs
    })

    st.line_chart(df.set_index("Dose"))

# =========================
# DASHBOARD
# =========================
elif menu == "Dashboard":
    set_bg("rapport.png")

    st.title("Dashboard global")

    if len(st.session_state.patients) == 0:
        st.warning("Aucun patient enregistré.")
    else:
        df_patients = pd.DataFrame(st.session_state.patients)

        col1, col2, col3 = st.columns(3)

        col1.metric("Nombre patients", len(df_patients))
        col2.metric("Dose moyenne", round(df_patients["Dose"].mean(), 2))
        col3.metric("SNR moyen", round(df_patients["SNR"].mean(), 2))

        st.dataframe(df_patients, use_container_width=True)

        st.subheader("Évolution Dose / SNR")
        st.line_chart(df_patients[["Dose", "SNR"]])

        excel_file = generer_excel(df_patients)

        st.download_button(
            "Télécharger historique Excel",
            data=excel_file,
            file_name="historique_patients.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
