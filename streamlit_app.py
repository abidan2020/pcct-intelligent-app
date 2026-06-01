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

# Configuration globale unique
st.set_page_config(page_title="PCCT Intelligent System", layout="wide")
DB_NAME = "patients_pcct.db"

# =========================
# CACHING INFRASTRUCTURE (Optimisation Performances)
# =========================
@st.cache_data
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
            background: linear-gradient(rgba(0,0,0,0.72), rgba(0,0,0,0.88)), url("data:image/png;base64,{img}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """, unsafe_allow_html=True)

# =========================
# INITIALISATION SESSIONS & STYLES
# =========================
for key, default in [("connecte", False), ("role", ""), ("nom_utilisateur", "")]:
    if key not in st.session_state:
        st.session_state[key] = default

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

# =========================
# DATABASE LAYER (Correction Concurrence)
# =========================
def get_db_connection():
    # Ajout d'un timeout pour éviter les verrous en multi-utilisateurs
    return sqlite3.connect(DB_NAME, timeout=10)

def init_db():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, nom TEXT, prenom TEXT, cin TEXT UNIQUE, sexe TEXT,
            type_examen TEXT, age INTEGER, poids REAL, taille REAL, imc REAL, classe_imc TEXT,
            dose REAL, snr REAL, kvp INTEGER, mas INTEGER, ctdivol REAL, dlp REAL, recommandation TEXT
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS scanners (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, marque TEXT, modele TEXT, 
            numero_serie TEXT UNIQUE, localisation TEXT, date_installation TEXT, etat_initial TEXT
        )""")
        conn.commit()

def ajouter_patient(patient):
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            INSERT INTO patients (date, nom, prenom, cin, sexe, type_examen, age, poids, taille, imc, 
            classe_imc, dose, snr, kvp, mas, ctdivol, dlp, recommandation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
            (patient["Date"], patient["Nom"], patient["Prénom"], patient["CIN"], patient["Sexe"], patient["Type examen"], 
             patient["Age"], patient["Poids"], patient["Taille"], patient["IMC"], patient["Classe IMC"], patient["Dose"], 
             patient["SNR"], patient["kVp"], patient["mAs"], patient["CTDIvol"], patient["DLP"], patient["Recommandation"]))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False

def charger_patients():
    with get_db_connection() as conn:
        return pd.read_sql_query("SELECT * FROM patients", conn)

def modifier_patient(patient_id, patient):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
        UPDATE patients SET date=?, nom=?, prenom=?, cin=?, sexe=?, type_examen=?, age=?, poids=?, taille=?, 
        imc=?, classe_imc=?, dose=?, snr=?, kvp=?, mas=?, ctdivol=?, dlp=?, recommandation=? WHERE id=?""", 
        (patient["Date"], patient["Nom"], patient["Prénom"], patient["CIN"], patient["Sexe"], patient["Type examen"], 
         patient["Age"], patient["Poids"], patient["Taille"], patient["IMC"], patient["Classe IMC"], patient["Dose"], 
         patient["SNR"], patient["kVp"], patient["mAs"], patient["CTDIvol"], patient["DLP"], patient["Recommandation"], patient_id))
        conn.commit()

def supprimer_patient(patient_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM patients WHERE id=?", (patient_id,))
        conn.commit()

def ajouter_scanner(nom, marque, modele, numero_serie, localisation, date_installation, etat_initial):
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            INSERT INTO scanners (nom, marque, modele, numero_serie, localisation, date_installation, etat_initial)
            VALUES (?, ?, ?, ?, ?, ?, ?)""", (nom, marque, modele, numero_serie, localisation, date_installation, etat_initial))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False

def charger_scanners():
    with get_db_connection() as conn:
        return pd.read_sql_query("SELECT * FROM scanners", conn)

# =========================
# CORE BIOMEDICAL LOGIC
# =========================
def calcul_imc(poids, taille):
    return poids / ((taille / 100) ** 2) if taille > 0 else 0

def classe_imc(imc):
    if imc == 0: return "Non calculé"
    if imc < 18.5: return "Maigreur"
    if imc < 25: return "Normal"
    if imc < 30: return "Surpoids"
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
    return protocoles.get(type_examen, {"ctdi": 15, "kvp": 120, "mas": 150, "dlp": 500})

def dose_adaptee(age, imc, type_examen):
    p = protocole_examen(type_examen)
    ctdi_ref = p["ctdi"]
    facteur_imc = 1 + 0.015 * (imc - 25)
    facteur_age = 1 + 0.002 * (age - 40)
    dose = ctdi_ref * facteur_imc * facteur_age
    return round(max(min(dose, ctdi_ref * 1.35), ctdi_ref * 0.55), 2)

def calcul_snr(age, imc, dose):
    return round(max(60 - 0.30 * imc - 0.05 * age + 0.70 * dose, 10), 2)

def adaptation_parametres(age, imc, type_examen, dose, snr):
    p = protocole_examen(type_examen)
    kvp, mas = p["kvp"], p["mas"]
    if imc > 30: mas *= 1.20
    elif imc < 20: mas *= 0.85
    if snr < 50: mas *= 1.15
    elif snr > 65: mas *= 0.90
    dlp = p["dlp"] * (dose / p["ctdi"]) if p["ctdi"] > 0 else 0
    return round(kvp), round(mas), round(dose, 2), round(dlp, 2)

def recommandation_ia(snr, dose, imc):
    if snr < 50: return "SNR faible : augmenter légèrement le mAs ou ajuster la dose."
    if dose > 30 and imc < 25: return "Dose élevée : réduction progressive possible tout en surveillant le SNR."
    if snr >= 50 and dose <= 25: return "Paramètres acceptables : dose optimisée avec qualité image correcte."
    if imc > 30: return "Patient à IMC élevé : surveiller le bruit image et adapter le mAs."
    return "Acquisition acceptable selon les paramètres estimés."

def creer_patient(nom, prenom, cin, sexe, type_examen, age, poids, taille):
    imc = calcul_imc(poids, taille)
    dose = dose_adaptee(age, imc, type_examen)
    snr = calcul_snr(age, imc, dose)
    kvp, mas, ctdi, dlp = adaptation_parametres(age, imc, type_examen, dose, snr)
    reco = recommandation_ia(snr, dose, imc)
    return {
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Nom": nom, "Prénom": prenom, "CIN": cin,
        "Sexe": sexe, "Type examen": type_examen, "Age": age, "Poids": poids, "Taille": taille,
        "IMC": round(imc, 2), "Classe IMC": classe_imc(imc), "Dose": dose, "SNR": snr,
        "kVp": kvp, "mAs": mas, "CTDIvol": ctdi, "DLP": dlp, "Recommandation": reco
    }

# =========================
# EXPORTS (EXCEL & PDF)
# =========================
def generer_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Patients")
        ws = writer.sheets["Patients"]
        for col in ws.columns:
            max_len = max(len(str(cell.value)) if cell.value else 0 for cell in col)
            ws.column_dimensions[col[0].column_letter].width = max_len + 4
    output.seek(0)
    return output

def generer_pdf(patient):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    y = A4[1] - 60
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
    for label, value in infos:
        ligne(label, value)
    pdf.save()
    buffer.seek(0)
    return buffer

# Initialization
init_db()
examens = ["Scanner cérébral", "Scanner thoracique", "Scanner abdominal", "Scanner cardiaque", "Scanner pulmonaire", "Scanner osseux", "Scanner pelvien", "Scanner corps entier"]

# =========================
# SECURITE & AUTHENTIFICATION
# =========================
def page_login():
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown('<div class="card" style="margin-top:60px; text-align:center;">', unsafe_allow_html=True)
        st.markdown('<div style="border:1px solid rgba(14,165,233,0.35); border-radius:25px; padding:18px; margin-bottom:30px; font-size:28px; font-weight:800; color:#0ea5e9; background:rgba(7,25,43,0.55);">PROMAMEC : Healthcare Experts</div>', unsafe_allow_html=True)
        st.title("Connexion au système PCCT")
        nom = st.text_input("Nom utilisateur")
        identifiant = st.text_input("ID utilisateur", type="password")
        
        if st.button("Se connecter"):
            if nom.strip().lower() == "yassine abidan" and identifiant == "12345":
                st.session_state.connecte, st.session_state.role, st.session_state.nom_utilisateur = True, "Technicien de radiologie", "Yassine Abidan"
                st.rerun()
            elif nom.strip().lower() == "khadija abidan" and identifiant == "67890":
                st.session_state.connecte, st.session_state.role, st.session_state.nom_utilisateur = True, "Ingénieure biomédicale", "Khadija ABIDAN"
                st.rerun()
            else:
                st.error("Nom ou ID incorrect.")
        st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.connecte:
    page_login()
    st.stop()

# =========================
# NAVIGATION & CONTENU
# =========================
st.sidebar.title("PCCT Intelligent System")
st.sidebar.write(f"**Utilisateur :** {st.session_state.nom_utilisateur}")
st.sidebar.write(f"**Rôle :** {st.session_state.role}")

if st.sidebar.button("Déconnexion"):
    st.session_state.connecte = False
    st.rerun()

menu = st.sidebar.radio("Navigation", ["Accueil", "Technicien", "SNR", "Maintenance", "Gestion scanners", "Dashboard", "Validation", "Rapport"])

if menu == "Accueil":
    set_bg("accueil.png")
    st.title("PCCT Intelligent System")
    st.subheader("Optimisation de dose photon-counting & Maintenance prédictive")
    st.markdown("<div class='card'><h3>Objectif</h3><p>Cette application simule un système intelligent pour adapter la dose scanner selon le patient, préserver un SNR acceptable et surveiller le scanner.</p></div>", unsafe_allow_html=True)

# =========================
# WORKSPACE TECHNICIEN (Correction Logique Dynamique)
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
        sexe = st.selectbox("Sexe", ["Homme", "Femme"])
        type_examen = st.selectbox("Type d'examen", examens)
        age = st.number_input("Âge", min_value=0, max_value=120, value=30)
        poids = st.number_input("Poids (kg)", min_value=0.
