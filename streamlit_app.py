import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import base64
import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

st.set_page_config(
    page_title="PCCT Intelligent System",
    layout="wide"
)

# =========================
# BACKGROUND
# =========================
def get_base64_image(path):

    if not os.path.exists(path):
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

        "Scanner cérébral": {
            "ctdi": 50,
            "kvp": 120,
            "mas": 250,
            "dlp": 900
        },

        "Scanner thoracique": {
            "ctdi": 10,
            "kvp": 100,
            "mas": 120,
            "dlp": 350
        },

        "Scanner abdominal": {
            "ctdi": 15,
            "kvp": 120,
            "mas": 180,
            "dlp": 600
        },

        "Scanner cardiaque": {
            "ctdi": 20,
            "kvp": 100,
            "mas": 220,
            "dlp": 450
        },

        "Scanner pulmonaire": {
            "ctdi": 8,
            "kvp": 100,
            "mas": 90,
            "dlp": 250
        },

        "Scanner osseux": {
            "ctdi": 12,
            "kvp": 120,
            "mas": 160,
            "dlp": 400
        },

        "Scanner pelvien": {
            "ctdi": 14,
            "kvp": 120,
            "mas": 170,
            "dlp": 500
        },

        "Scanner corps entier": {
            "ctdi": 25,
            "kvp": 120,
            "mas": 300,
            "dlp": 1100
        }
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

# =========================
# PDF
# =========================
def generer_pdf(patient):

    buffer = BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=A4
    )

    largeur, hauteur = A4

    y = hauteur - 60

    pdf.setFont(
        "Helvetica-Bold",
        20
    )

    pdf.drawString(
        190,
        y,
        "Rapport Patient"
    )

    y -= 50

    pdf.setFont(
        "Helvetica",
        11
    )

    pdf.drawString(
        50,
        y,
        f"Date : {patient.get('Date', 'Non renseigné')}"
    )

    y -= 45

    def titre(txt):

        nonlocal y

        pdf.setFont(
            "Helvetica-Bold",
            14
        )

        pdf.drawString(
            50,
            y,
            txt
        )

        y -= 30

    def ligne(label, valeur):

        nonlocal y

        pdf.setFont(
            "Helvetica-Bold",
            11
        )

        pdf.drawString(
            60,
            y,
            f"{label} :"
        )

        pdf.setFont(
            "Helvetica",
            11
        )

        pdf.drawString(
            220,
            y,
            str(valeur)
        )

        y -= 22

    titre("Informations Patient")

    ligne("Nom", patient.get("Nom"))
    ligne("Prénom", patient.get("Prénom"))
    ligne("CIN", patient.get("CIN"))
    ligne("Sexe", patient.get("Sexe"))
    ligne("Âge", patient.get("Age"))
    ligne("Poids", f"{patient.get('Poids')} kg")
    ligne("Taille", f"{patient.get('Taille')} cm")
    ligne("IMC", patient.get("IMC"))
    ligne("Classe IMC", patient.get("Classe IMC"))

    y -= 10

    titre("Examen")

    ligne(
        "Type d'examen",
        patient.get("Type examen")
    )

    y -= 10

    titre("Paramètres recommandés")

    ligne(
        "Dose recommandée",
        f"{patient.get('Dose')} mGy"
    )

    ligne(
        "SNR estimé",
        patient.get("SNR")
    )

    ligne(
        "kVp",
        patient.get("kVp")
    )

    ligne(
        "mAs",
        patient.get("mAs")
    )

    ligne(
        "CTDIvol",
        f"{patient.get('CTDIvol')} mGy"
    )

    ligne(
        "DLP",
        f"{patient.get('DLP')} mGy.cm"
    )

    y -= 10

    titre("Recommandation IA")

    reco = str(
        patient.get("Recommandation")
    )

    pdf.setFont(
        "Helvetica",
        11
    )

    for i in range(0, len(reco), 80):

        pdf.drawString(
            60,
            y,
            reco[i:i+80]
        )

        y -= 18

    pdf.save()

    buffer.seek(0)

    return buffer

# =========================
# EXCEL
# =========================
def generer_excel(df_patients):

    excel_buffer = BytesIO()

    with pd.ExcelWriter(
        excel_buffer,
        engine="openpyxl"
    ) as writer:

        df_patients.to_excel(
            writer,
            index=False,
            sheet_name="Patients"
        )

        worksheet = writer.sheets["Patients"]

        for column_cells in worksheet.columns:

            longueur = max(
                len(str(cell.value))
                if cell.value is not None else 0
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
st.sidebar.title(
    "PCCT Intelligent System"
)

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

    st.title(
        "PCCT Intelligent System"
    )

    st.subheader(
        "Optimisation intelligente de dose et qualité image"
    )

# =========================
# TECHNICIEN
# =========================
elif menu == "Technicien":

    set_bg("technicien.png")

    st.title(
        "Espace Technicien"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            '<div class="card">',
            unsafe_allow_html=True
        )

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

        age = st.number_input(
            "Âge",
            1,
            120,
            45
        )

        poids = st.number_input(
            "Poids (kg)",
            20.0,
            200.0,
            70.0
        )

        taille = st.number_input(
            "Taille (cm)",
            100.0,
            220.0,
            170.0
        )

        bouton = st.button(
            "Calculer et enregistrer"
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    imc = calcul_imc(
        poids,
        taille
    )

    dose = dose_adaptee(
        age,
        imc,
        type_examen
    )

    snr = calcul_snr(
        age,
        imc,
        dose
    )

    kvp, mas, ctdi, dlp = adaptation_parametres(
        age,
        imc,
        type_examen,
        dose,
        snr
    )

    reco = recommandation_ia(
        snr,
        dose,
        imc
    )

    with col2:

        st.metric(
            "IMC",
            round(imc, 2)
        )

        st.metric(
            "Classe IMC",
            classe_imc(imc)
        )

        st.metric(
            "Dose recommandée",
            f"{dose} mGy"
        )

        st.metric(
            "SNR estimé",
            snr
        )

        st.metric(
            "kVp recommandé",
            kvp
        )

        st.metric(
            "mAs recommandé",
            mas
        )

        st.metric(
            "CTDIvol",
            f"{ctdi} mGy"
        )

        st.metric(
            "DLP",
            f"{dlp} mGy.cm"
        )

        st.info(
            f"Recommandation IA : {reco}"
        )

    # =========================
    # ENREGISTREMENT
    # =========================
    if bouton:

        if cin.strip() == "":

            st.error(
                "Veuillez entrer le CIN du patient."
            )

        else:

            patient_existe = any(
                p.get("CIN", "").strip().upper()
                == cin.strip().upper()
                for p in st.session_state.patients
            )

            if patient_existe:

                st.warning(
                    "Ce patient est déjà enregistré."
                )

            else:

                patient = {

                    "Date": datetime.now().strftime(
                        "%Y-%m-%d %H:%M"
                    ),

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

                st.session_state.patients.append(
                    patient
                )

                st.success(
                    "Le patient a été bien enregistré."
                )

# =========================
# DASHBOARD
# =========================
elif menu == "Dashboard":

    set_bg("rapport.png")

    st.title(
        "Dashboard global"
    )

    st.subheader(
        "Restaurer une ancienne liste de patients"
    )

    fichier_importe = st.file_uploader(
        "Importer un fichier Excel historique",
        type=["xlsx"]
    )

    if fichier_importe is not None:

        df_import = pd.read_excel(
            fichier_importe
        )

        st.session_state.patients = (
            df_import.to_dict("records")
        )

        st.success(
            "Liste des patients restaurée avec succès."
        )

        st.rerun()

    if len(st.session_state.patients) == 0:

        st.warning(
            "Aucun patient enregistré."
        )

    else:

        df_patients = pd.DataFrame(
            st.session_state.patients
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Nombre patients",
            len(df_patients)
        )

        col2.metric(
            "Dose moyenne",
            round(
                df_patients["Dose"].mean(),
                2
            )
        )

        col3.metric(
            "SNR moyen",
            round(
                df_patients["SNR"].mean(),
                2
            )
        )

        st.dataframe(
            df_patients,
            use_container_width=True
        )

        st.subheader(
            "Évolution Dose / SNR"
        )

        st.line_chart(
            df_patients[
                ["Dose", "SNR"]
            ]
        )

        # =========================
        # EXPORT EXCEL
        # =========================
        excel_file = generer_excel(
            df_patients
        )

        st.download_button(
            label="Télécharger historique Excel",
            data=excel_file,
            file_name="historique_patients.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# =========================
# RAPPORT
# =========================
elif menu == "Rapport":

    set_bg("rapport.png")

    st.title(
        "Rapports Patients"
    )

    if len(st.session_state.patients) == 0:

        st.warning(
            "Aucun patient enregistré."
        )

    else:

        df_patients = pd.DataFrame(
            st.session_state.patients
        )

        patient_index = st.selectbox(
            "Choisir un patient",
            df_patients.index,
            format_func=lambda x:
            f"{df_patients.loc[x, 'Nom']} "
            f"{df_patients.loc[x, 'Prénom']}"
        )

        patient = df_patients.loc[
            patient_index
        ].to_dict()

        st.write(
            f"Nom : {patient.get('Nom')}"
        )

        st.write(
            f"Prénom : {patient.get('Prénom')}"
        )

        st.write(
            f"CIN : {patient.get('CIN')}"
        )

        st.write(
            f"Dose : {patient.get('Dose')} mGy"
        )

        st.write(
            f"SNR : {patient.get('SNR')}"
        )

        pdf_file = generer_pdf(
            patient
        )

        st.download_button(
            "Télécharger le rapport PDF",
            data=pdf_file,
            file_name=f"rapport_{patient.get('Nom')}.pdf",
            mime="application/pdf"
        )

# =========================
# SNR
# =========================
elif menu == "SNR":

    set_bg("snr.png")

    st.title(
        "Analyse SNR"
    )

    imc_v = st.slider(
        "IMC",
        15,
        45,
        25
    )

    age_v = st.slider(
        "Âge",
        10,
        90,
        40
    )

    doses = np.linspace(
        3,
        60,
        40
    )

    snrs = [
        calcul_snr(age_v, imc_v, d)
        for d in doses
    ]

    df = pd.DataFrame({
        "Dose": doses,
        "SNR": snrs
    })

    st.line_chart(
        df.set_index("Dose")
    )
