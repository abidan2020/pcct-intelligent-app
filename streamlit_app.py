import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import base64
import os
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

st.set_page_config(page_title="PCCT Intelligent System", layout="wide")

if "connecte" not in st.session_state:
    st.session_state.connecte = False
if "role" not in st.session_state:
    st.session_state.role = ""
if "nom_utilisateur" not in st.session_state:
    st.session_state.nom_utilisateur = ""

DB_NAME = "patients_pcct.db"

def get_base64_image(path):
    if not path or not os.path.exists(path):
        return ""
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

st.markdown("""
<style>
[data-testid="stSidebar"] {background:#03111f;}
[data-testid="stSidebar"] * {color:white;}

.card {
    background:rgba(5,20,35,0.85);
    padding:22px;
    border-radius:18px;
    margin-bottom:18px;
    border:1px solid rgba(14,165,233,0.35);
    box-shadow:0 0 18px rgba(0,0,0,0.45);
}

h1, h2, h3, p, label, div {color:white;}

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

def page_login():
    login_bg = get_base64_image("login.png")

    st.markdown(f"""
    <style>
    .stApp {{
        background:
        linear-gradient(rgba(0,0,0,0.70), rgba(0,0,0,0.85)),
        url("data:image/png;base64,{login_bg}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    .login-box {{
        background: rgba(5,20,35,0.90);
        padding: 35px;
        border-radius: 22px;
        border: 1px solid rgba(14,165,233,0.35);
        box-shadow: 0 0 25px rgba(0,0,0,0.55);
        text-align: center;
        margin-top: 60px;
    }}
    .promamec-bar {{
        border: 1px solid rgba(14,165,233,0.35);
        border-radius: 25px;
        padding: 18px;
        margin-bottom: 30px;
        text-align: center;
        font-size: 28px;
        font-weight: 800;
        color: #0ea5e9;
        background: rgba(7,25,43,0.55);
    }}
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.4, 1])

    with col2:
        st.markdown('<div class="promamec-bar">PROMAMEC : Healthcare Experts</div>', unsafe_allow_html=True)
        st.title("Connexion au système PCCT")
        st.subheader("PROMAMEC Intelligent System")

        nom = st.text_input("Nom utilisateur")
        identifiant = st.text_input("ID utilisateur", type="password")

        if st.button("Se connecter"):
            if nom.strip().lower() == "yassine abidan" and identifiant == "12345":
                st.session_state.connecte = True
                st.session_state.role = "Technicien de radiologie"
                st.session_state.nom_utilisateur = "Yassine Abidan"
                st.rerun()

            elif nom.strip().lower() == "khadija abidan" and identifiant == "67890":
                st.session_state.connecte = True
                st.session_state.role = "Ingénieure biomédicale"
                st.session_state.nom_utilisateur = "Khadija ABIDAN"
                st.rerun()
            else:
                st.error("Nom ou ID incorrect.")

if not st.session_state.connecte:
    page_login()
    st.stop()

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT, nom TEXT, prenom TEXT, cin TEXT UNIQUE, sexe TEXT, type_examen TEXT,
        age INTEGER, poids REAL, taille REAL, imc REAL, classe_imc TEXT,
        dose REAL, snr REAL, kvp INTEGER, mas INTEGER, ctdivol REAL, dlp REAL, recommandation TEXT
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS scanners (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT, marque TEXT, modele TEXT, numero_serie TEXT UNIQUE,
        localisation TEXT, date_installation TEXT, etat_initial TEXT
    )
    """)
    conn.commit()
    conn.close()

def ajouter_patient(patient):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("""
        INSERT INTO patients (
            date, nom, prenom, cin, sexe, type_examen, age, poids, taille, 
            imc, classe_imc, dose, snr, kvp, mas, ctdivol, dlp, recommandation
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            patient["Date"], patient["Nom"], patient["Prénom"], patient["CIN"],
            patient["Sexe"], patient["Type examen"], patient["Age"],
            patient["Poids"], patient["Taille"], patient["IMC"],
            patient["Classe IMC"], patient["Dose"], patient["SNR"],
            patient["kVp"], patient["mAs"], patient["CTDIvol"],
            patient["DLP"], patient["Recommandation"]
        ))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def charger_patients():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM patients", conn)
    conn.close()
    return df

def ajouter_scanner(nom, marque, modele, numero_serie, localisation, date_installation, etat_initial):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("""
        INSERT INTO scanners (nom, marque, modele, numero_serie, localisation, date_installation, etat_initial)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nom, marque, modele, numero_serie, localisation, date_installation, etat_initial))
        conn.commit()
        ok = True
    except sqlite3.IntegrityError:
        ok = False
    conn.close()
    return ok

def charger_scanners():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM scanners", conn)
    conn.close()
    return df

def calcul_imc(poids, taille):
    if taille <= 0: return 0
    return poids / ((taille / 100) ** 2)

def classe_imc(imc):
    if imc == 0: return "Non calculé"
    elif imc < 18.5: return "Maigreur"
    elif imc < 25: return "Normal"
    elif imc < 30: return "Surpoids"
    else: return "Obésité"

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
    return round(max(min(dose, ctdi_ref * 1.35), ctdi_ref * 0.55), 2)

def calcul_snr(age, imc, dose):
    snr = 60 - 0.30 * imc - 0.05 * age + 0.70 * dose
    return round(max(snr, 10), 2)

def adaptation_parametres(age, imc, type_examen, dose, snr):
    p = protocole_examen(type_examen)
    kvp = p["kvp"]
    mas = p["mas"]
    if imc > 30: mas *= 1.20
    elif imc < 20: mas *= 0.85
    if snr < 50: mas *= 1.15
    elif snr > 65: mas *= 0.90
    dlp = p["dlp"] * (dose / p["ctdi"])
    return round(kvp), round(mas), round(dose, 2), round(dlp, 2)

def recommandation_ia(snr, dose, imc):
    if snr < 50: return "SNR faible : augmenter légèrement le mAs ou ajuster la dose."
    elif dose > 30 and imc < 25: return "Dose élevée : réduction progressive possible tout en surveillant le SNR."
    elif snr >= 50 and dose <= 25: return "Paramètres acceptables : dose optimisée avec qualité image correcte."
    elif imc > 30: return "Patient à IMC élevé : surveiller le bruit image et adapter le mAs."
    else: return "Acquisition acceptable selon les paramètres estimés."

def creer_patient(nom, prenom, cin, sexe, type_examen, age, poids, taille):
    imc = calcul_imc(poids, taille)
    dose = dose_adaptee(age, imc, type_examen)
    snr = calcul_snr(age, imc, dose)
    kvp, mas, ctdi, dlp = adaptation_parametres(age, imc, type_examen, dose, snr)
    reco = recommandation_ia(snr, dose, imc)
    return {
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Nom": nom, "Prénom": prenom, "CIN": cin, "Sexe": sexe, "Type examen": type_examen,
        "Age": age, "Poids": poids, "Taille": taille, "IMC": round(imc, 2), "Classe IMC": classe_imc(imc),
        "Dose": dose, "SNR": snr, "kVp": kvp, "mAs": mas, "CTDIvol": ctdi, "DLP": dlp, "Recommandation": reco
    }

def generer_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Patients")
        ws = writer.sheets["Patients"]
        for col in ws.columns:
            max_len = max(len(str(cell.value)) if cell.value else 0 for cell in col)
            ws.column_dimensions[col.column_letter].width = max_len + 4
    output.seek(0)
    return output

def generer_pdf(patient):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    y = A4 - 60
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(190, y, "Rapport Patient")
    y -= 50
    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, y, f"Date : {patient.get('date', patient.get('Date', ''))}")
    y -= 45

    def ligne(label, valeur):
        nonlocal y
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(60, y, f"{label} :")
        pdf.setFont("Helvetica", 11)
        pdf.drawString(220, y, str(valeur))
        y -= 22

    infos = [
        ("Nom", patient.get("nom", patient.get("Nom", ""))),
        ("Prénom", patient.get("prenom", patient.get("Prénom", ""))),
        ("CIN", patient.get("cin", patient.get("CIN", ""))),
        ("Sexe", patient.get("sexe", patient.get("Sexe", ""))),
        ("Âge", patient.get("age", patient.get("Age", ""))),
        ("IMC", patient.get("imc", patient.get("IMC", ""))),
        ("Dose", patient.get("dose", patient.get("Dose", ""))),
        ("SNR", patient.get("snr", patient.get("SNR", ""))),
        ("kVp", patient.get("kvp", patient.get("kVp", ""))),
        ("mAs", patient.get("mas", patient.get("mAs", ""))),
        ("CTDIvol", patient.get("ctdivol", patient.get("CTDIvol", ""))),
        ("DLP", patient.get("dlp", patient.get("DLP", ""))),
        ("Recommandation", patient.get("recommandation", patient.get("Recommandation", "")))
    ]
    for label, value in infos: ligne(label, value)
    pdf.save()
    buffer.seek(0)
    return buffer

init_db()

examens = [
    "Scanner cérébral", "Scanner thoracique", "Scanner abdominal", "Scanner cardiaque",
    "Scanner pulmonaire", "Scanner osseux", "Scanner pelvien", "Scanner corps entier"
]

st.sidebar.title("PCCT Intelligent System")
st.sidebar.write(f"**Utilisateur :** {st.session_state.nom_utilisateur}")
st.sidebar.write(f"**Rôle :** {st.session_state.role}")

if st.sidebar.button("Déconnexion"):
    st.session_state.connecte = False
    st.session_state.role = ""
    st.session_state.nom_utilisateur = ""
    st.rerun()

options_menu = ["Accueil", "Technicien", "SNR", "Maintenance", "Dashboard", "Validation"]
if st.session_state.role == "Ingénieure biomédicale":
    options_menu.insert(4, "Gestion scanners")

menu = st.sidebar.radio("Navigation", options_menu)

if menu == "Accueil":
    set_bg("accueil.png")
    st.title("PCCT Intelligent System")
    st.subheader("Optimisation intelligente de dose, qualité image et maintenance prédictive")
    st.markdown("<div class='card'><h3>Objectif</h3><p>Cette application simule un système intelligent pour adapter la dose scanner selon le patient, préserver un SNR acceptable et surveiller le scanner.</p></div>", unsafe_allow_html=True)
    if st.session_state.role == "Ingénieure biomédicale":
        st.markdown("<div class='card'><h3>Espace ingénieure biomédicale</h3><p>Cet espace permet de suivre les performances du scanner, analyser les anomalies, consulter les alertes techniques et préparer les rapports de maintenance.</p></div>", unsafe_allow_html=True)

elif menu == "Technicien":
    set_bg("technicien.png")
    st.title("Espace Technicien")

    col1, col2 = st.columns(2)

    with col1:
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        cin = st.text_input("CIN")
        sexe = st.selectbox("Sexe", ["Homme", "Femme"])
        type_examen = st.selectbox("Type d'examen", examens)
        age = st.number_input("Âge", min_value=0, max_value=120, value=0)
        poids = st.number_input("Poids (kg)", min_value=0.0, max_value=200.0, value=0.0)
        taille = st.number_input("Taille (cm)", min_value=0.0, max_value=220.0, value=0.0)

    if cin.strip() != "" and age > 0 and poids > 0 and taille > 0:
        patient = creer_patient(nom, prenom, cin, sexe, type_examen, age, poids, taille)

        with col2:
            st.metric("IMC", patient["IMC"])
            st.metric("Classe IMC", patient["Classe IMC"])
            st.metric("Dose recommandée", f"{patient['Dose']} mGy")
            st.metric("SNR estimé", patient["SNR"])
            st.metric("kVp recommandé", patient["kVp"])
            st.metric("mAs recommandé", patient["mAs"])
            st.metric("CTDIvol", f"{patient['CTDIvol']} mGy")
            st.metric("DLP", f"{patient['DLP']} mGy.cm")

            if patient["SNR"] >= 50:
                st.success("Qualité image acceptable")
            else:
                st.error("SNR insuffisant")
            st.info(patient["Recommandation"])

        if st.button("Enregistrer le patient"):
            ok = ajouter_patient(patient)
            if ok: st.success("Patient enregistré.")
            else: st.warning("Ce CIN existe déjà.")
    else:
        with col2:
            st.warning("Veuillez remplir toutes les informations du patient.")

elif menu == "SNR":
    set_bg("snr.png")
    st.title("Analyse SNR")
    imc_v = st.slider("IMC", 15, 45, 25)
    age_v = st.slider("Âge", 10, 90, 40)
    doses = np.linspace(3, 60, 40)
    snrs = [calcul_snr(age_v, imc_v, d) for d in doses]
    df = pd.DataFrame({"Dose": doses, "SNR": snrs})
    st.line_chart(df.set_index("Dose"))

elif menu == "Maintenance":
    set_bg("maintenance.png")
    st.title("Maintenance prédictive du scanner PCCT")
    col1, col2 = st.columns(2)

    with col1:
        df_scanners = charger_scanners()
        if df_scanners.empty:
            st.warning("Aucun scanner enregistré. Ajoutez d'abord un scanner dans Gestion scanners.")
            st.stop()

        scanner = st.selectbox("Scanner concerné", df_scanners["nom"].tolist())
        scanner_info = df_scanners[df_scanners["nom"] == scanner].iloc
        st.info(f"Marque : {scanner_info['marque']} | Modèle : {scanner_info['modele']} | N° série : {scanner_info['numero_serie']}")

        snr_sys = st.number_input("SNR système", min_value=0.0, max_value=100.0, value=55.0)
        temperature = st.number_input("Température du tube RX (°C)", min_value=0.0, max_value=150.0, value=38.0)
        vibration = st.slider("Vibration du gantry (%)", 0, 100, 15)

    with col2:
        heures = st.number_input("Heures d’utilisation du scanner", min_value=0, max_value=100000, value=1200)
        bruit = st.slider("Niveau de bruit image (%)", 0, 100, 10)
        detecteurs = st.selectbox("État des détecteurs photon-counting", ["Stable", "Légère dégradation", "Dégradation importante"])
        refroidissement = st.selectbox("État du refroidissement", ["Normal", "À surveiller", "Défaillant"])

    score = 0
    score += max(0, 50 - snr_sys) * 1.3
    score += max(0, temperature - 60) * 1.2
    score += vibration * 0.5
    score += bruit * 0.4
    score += heures * 0.001
    if detecteurs == "Légère dégradation": score += 15
    elif detecteurs == "Dégradation importante": score += 35
    if refroidissement == "À surveiller": score += 15
    elif refroidissement == "Défaillant": score += 35
    score = round(min(score, 100), 2)

    if score < 35: etat, couleur = "Stable", "🟢"
    elif score < 70: etat, couleur = "À surveiller", "🟠"
    else: etat, couleur = "Critique", "🔴"

    composant, cause, action = "Aucun", "Fonctionnement normal", "Continuer la surveillance régulière"
    if temperature > 75 or refroidissement == "Défaillant":
        composant = "Tube RX / système de refroidissement"
        cause = "Température élevée ou refroidissement insuffisant"
        action = "Contrôler le système de refroidissement et vérifier le tube RX"
    elif vibration > 60:
        composant = "Gantry"
        cause = "Vibrations mécaniques élevées"
        action = "Vérifier l’alignement mécanique et les roulements du gantry"
    elif snr_sys < 45 or bruit > 60 or detecteurs == "Dégradation importante":
        composant = "Détecteurs photon-counting"
        cause = "Baisse du SNR ou augmentation du bruit image"
        action = "Effectuer une calibration des détecteurs"
    elif heures > 30000:
        composant = "Tube RX"
        cause = "Nombre d’heures d’utilisation élevé"
        action = "Planifier une maintenance préventive du tube RX"

    st.markdown("---")
    st.markdown("## Résultats de l’analyse maintenance")
    c1, c2, c3 = st.columns(3)
    c1.metric("Score de stress", f"{score} %")
    c2.metric("État global", f"{couleur} {etat}")
    c3.metric("Scanner", scanner)

    st.write(f"**Composant suspect :** {composant}")
    st.write(f"**Cause probable :** {cause}")
    st.write(f"**Action recommandée :** {action}")

    df_maintenance = pd.DataFrame({
        "Paramètre": ["Scanner", "SNR système", "Température tube RX", "Vibration gantry", "Bruit image", "Heures d’utilisation", "État détecteurs", "Refroidissement", "Score stress", "État global"],
        "Valeur": [scanner, snr_sys, f"{temperature} °C", f"{vibration} %", f"{bruit} %", heures, detecteurs, refroidissement, f"{score} %", etat]
    })
    st.dataframe(df_maintenance, use_container_width=True)

elif menu == "Gestion scanners" and st.session_state.role == "Ingénieure biomédicale":
    st.title("Gestion du parc scanner")
    st.write("Ajouter un nouveau scanner")
    col1, col2 = st.columns(2)
    with col1:
        nom_scanner = st.text_input("Nom du scanner")
        marque = st.text_input("Marque", value="Neusoft")
        modele = st.text_input("Modèle")
        numero_serie = st.text_input("Numéro de série")
    with col2:
        localisation = st.text_input("Localisation")
        date_installation = st.date_input("Date d’installation")
        etat_initial = st.selectbox("État initial", ["Stable", "À surveiller", "Critique"])

    if st.button("Ajouter le scanner"):
        if nom_scanner == "" or numero_serie == "":
            st.error("Veuillez compléter les informations.")
        else:
            ok = ajouter_scanner(nom_scanner, marque, modele, numero_serie, localisation, str(date_installation), etat_initial)
            if ok: st.success("Scanner ajouté avec succès.")
            else: st.warning("Ce numéro de série existe déjà.")

    st.write("Liste des scanners enregistrés")
    df_scanners = charger_scanners()
    if df_scanners.empty: st.info("Aucun scanner enregistré.")
    else: st.dataframe(df_scanners, use_container_width=True)

elif menu == "Dashboard":
    set_bg("rapport.png")
    st.title("Dashboard global")
    fichier = st.file_uploader("Importer historique Excel (.xlsx)", type=["xlsx"])
    if fichier is not None:
        try:
            df_import = pd.read_excel(fichier, engine="openpyxl")
            for _, row in df_import.iterrows():
                patient_import = {
                    "Date": str(row.get("Date", datetime.now().strftime("%Y-%m-%d %H:%M"))),
                    "Nom": str(row.get("Nom", "")), "Prénom": str(row.get("Prénom", "")), "CIN": str(row.get("CIN", "")),
                    "Sexe": str(row.get("Sexe", "")), "Type examen": str(row.get("Type examen", "")), "Age": int(row.get("Age", 0)),
                    "Poids": float(row.get("Poids", 0)), "Taille": float(row.get("Taille", 0)), "IMC": float(row.get("IMC", 0)),
                    "Classe IMC": str(row.get("Classe IMC", "")), "Dose": float(row.get("Dose", 0)), "SNR": float(row.get("SNR", 0)),
                    "kVp": int(row.get("kVp", 0)), "mAs": int(row.get("mAs", 0)), "CTDIvol": float(row.get("CTDIvol", 0)),
                    "DLP": float(row.get("DLP", 0)), "Recommandation": str(row.get("Recommandation", ""))
                }
                if patient_import["CIN"] != "": ajouter_patient(patient_import)
            st.success("Historique importé avec succès.")
            st.rerun()
        except Exception as e:
            st.error("Impossible de lire ce fichier Excel.")
    df = charger_patients()
    if df.empty:
     st.warning("Aucun patient enregistré en base de données.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Nombre patients", len(df))
        col2.metric("Dose moyenne", round(df["dose"].mean(), 2))
        col3.metric("SNR moyen", round(df["snr"].mean(), 2))
        col4.metric("Cas SNR < 50", int((df["snr"] < 50).sum()))

        st.dataframe(df, use_container_width=True)
        st.subheader("Évolution Dose / SNR")
        st.line_chart(df[["dose", "snr"]])
        st.subheader("Répartition des examens")
        st.bar_chart(df["type_examen"].value_counts())

        excel_file = generer_excel(df)
        st.download_button("Télécharger historique Excel", data=excel_file, file_name="historique_patients.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

elif menu == "Validation":
    set_
