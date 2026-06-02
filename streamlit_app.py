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

DB_NAME = "patients_pcct.db"

# =========================
# LOGIN / SESSION STATE
# =========================
if "connecte" not in st.session_state:
    st.session_state.connecte = False

if "role" not in st.session_state:
    st.session_state.role = ""

if "nom_utilisateur" not in st.session_state:
    st.session_state.nom_utilisateur = ""

def page_login():
    st.markdown("""
    <style>
    .login-box {
        background: rgba(5,20,35,0.90);
        padding: 35px;
        border-radius: 22px;
        border: 1px solid rgba(14,165,233,0.35);
        box-shadow: 0 0 25px rgba(0,0,0,0.55);
        text-align: center;
        margin-top: 60px;
    }

    .promamec-bar {
        border: 1px solid rgba(14,165,233,0.35);
        border-radius: 25px;
        padding: 18px;
        margin-bottom: 30px;
        text-align: center;
        font-size: 28px;
        font-weight: 800;
        color: #0ea5e9;
        background: rgba(7,25,43,0.55);
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.4, 1])

    with col2:
        st.markdown(
            '<div class="promamec-bar">PROMAMEC : Healthcare Experts</div>',
            unsafe_allow_html=True
        )

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

        st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.connecte:
    page_login()
    st.stop()


# =========================
# BACKGROUND IMAGE SYSTEM
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
# GLOBAL CSS STYLE
# =========================
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
# DATABASE OPERATIONS
# =========================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        nom TEXT,
        prenom TEXT,
        cin TEXT UNIQUE,
        sexe TEXT,
        type_examen TEXT,
        age INTEGER,
        poids REAL,
        taille REAL,
        imc REAL,
        classe_imc TEXT,
        dose REAL,
        snr REAL,
        kvp INTEGER,
        mas INTEGER,
        ctdivol REAL,
        dlp REAL,
        recommandation TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS scanners (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        marque TEXT,
        modele TEXT,
        numero_serie TEXT UNIQUE,
        localisation TEXT,
        date_installation TEXT,
        etat_initial TEXT
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
            date, nom, prenom, cin, sexe, type_examen, age,
            poids, taille, imc, classe_imc, dose, snr,
            kvp, mas, ctdivol, dlp, recommandation
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

def modifier_patient(patient_id, patient):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    UPDATE patients SET
        date=?, nom=?, prenom=?, cin=?, sexe=?, type_examen=?,
        age=?, poids=?, taille=?, imc=?, classe_imc=?,
        dose=?, snr=?, kvp=?, mas=?, ctdivol=?, dlp=?, recommandation=?
    WHERE id=?
    """, (
        patient["Date"], patient["Nom"], patient["Prénom"], patient["CIN"],
        patient["Sexe"], patient["Type examen"], patient["Age"],
        patient["Poids"], patient["Taille"], patient["IMC"],
        patient["Classe IMC"], patient["Dose"], patient["SNR"],
        patient["kVp"], patient["mAs"], patient["CTDIvol"],
        patient["DLP"], patient["Recommandation"], patient_id
    ))

    conn.commit()
    conn.close()

def supprimer_patient(patient_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM patients WHERE id=?", (patient_id,))
    conn.commit()
    conn.close()

def ajouter_scanner(nom, marque, modele, numero_serie, localisation, date_installation, etat_initial):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    try:
        c.execute("""
        INSERT INTO scanners (
            nom, marque, modele, numero_serie,
            localisation, date_installation, etat_initial
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            nom, marque, modele, numero_serie,
            localisation, date_installation, etat_initial
        ))
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

# =========================
# CALCULS BIOMÉDICAUX PATIENT
# =========================
def calcul_imc(poids, taille):
    if taille <= 0:
        return 0
    return poids / ((taille / 100) ** 2)

def classe_imc(imc):
    if imc == 0:
        return "Non calculé"
    elif imc < 18.5:
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
    p = protocole_examen(type
