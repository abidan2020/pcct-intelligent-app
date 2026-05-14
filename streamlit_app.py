import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import os
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="PROMAMEC PCCT Intelligent System",
    layout="wide"
)

DB_NAME = "pcct_promamec_final.db"
LOGO_PATH = "imagespromamec.png"

# =========================
# STYLE
# =========================
st.markdown("""
<style>
:root {
    --green-dark: #006B4F;
    --green-main: #008B68;
    --green-light: #EAF6F1;
    --green-border: #CFE8DE;
    --text-dark: #1F2933;
    --white: #FFFFFF;
}

.stApp {
    background: #F8FCFA;
    color: var(--text-dark);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #006B4F 0%, #008B68 100%);
}

[data-testid="stSidebar"] * {
    color: white !important;
}

h1, h2, h3, h4 {
    color: var(--green-dark) !important;
    font-weight: 700 !important;
}

p, label, span {
    color: var(--text-dark);
}

.card {
    background: white;
    padding: 24px;
    border-radius: 18px;
    border: 1px solid var(--green-border);
    box-shadow: 0 6px 18px rgba(0,107,79,0.10);
    margin-bottom: 18px;
}

.hero-card {
    background: linear-gradient(135deg, #FFFFFF, #EAF6F1);
    padding: 32px;
    border-radius: 22px;
    border: 1px solid var(--green-border);
    box-shadow: 0 8px 24px rgba(0,107,79,0.12);
    margin-bottom: 24px;
}

.stButton > button {
    background: var(--green-main);
    color: white !important;
    border: none;
    border-radius: 10px;
    font-weight: 600;
}

.stButton > button:hover {
    background: var(--green-dark);
    color: white !important;
}

[data-testid="stMetric"] {
    background: white;
    border-radius: 14px;
    padding: 14px;
    border-left: 5px solid var(--green-main);
    box-shadow: 0 4px 12px rgba(0,107,79,0.08);
}

[data-testid="stMetric"] * {
    color: var(--text-dark) !important;
}

input, textarea {
    color: var(--text-dark) !important;
    background: white !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# SESSION LOGIN
# =========================
if "connecte" not in st.session_state:
    st.session_state.connecte = False
if "role" not in st.session_state:
    st.session_state.role = ""
if "nom_utilisateur" not in st.session_state:
    st.session_state.nom_utilisateur = ""

def login():
    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=240)

        st.title("PCCT Intelligent System")
        st.subheader("Connexion sécurisée")

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
    login()
    st.stop()

# =========================
# DATABASE
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
        age INTEGER,
        poids REAL,
        taille REAL,
        type_examen TEXT,
        protocole TEXT,
        imc REAL,
        classe_imc TEXT,
        dose REAL,
        snr REAL,
        qualite_image TEXT,
        kvp INTEGER,
        mas INTEGER,
        ctdi REAL,
        dlp REAL,
        scanner TEXT,
        marque TEXT,
        modele TEXT,
        numero_serie TEXT,
        recommandation TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS maintenance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        scanner TEXT,
        marque TEXT,
        modele TEXT,
        numero_serie TEXT,
        snr_systeme REAL,
        temperature REAL,
        vibration REAL,
        bruit REAL,
        heures INTEGER,
        detecteurs TEXT,
        refroidissement TEXT,
        score REAL,
        etat TEXT,
        composant TEXT,
        cause TEXT,
        action TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# DATA
# =========================
SCANNERS = {
    "NS-PCCT-2026-001": {
        "nom": "Scanner PCCT-01",
        "marque": "Neusoft",
        "modele": "NeuViz Glory PCCT",
        "localisation": "Radiologie"
    },
    "NS-PCCT-2026-002": {
        "nom": "Scanner PCCT-02",
        "marque": "Neusoft",
        "modele": "NeuViz Prime",
        "localisation": "Urgences"
    },
    "NS-PCCT-2026-003": {
        "nom": "Scanner PCCT-03",
        "marque": "Neusoft",
        "modele": "NeuViz Epoch",
        "localisation": "Cardiologie"
    }
}

EXAMENS = [
    "Scanner cérébral",
    "Scanner thoracique",
    "Scanner abdominal",
    "Scanner cardiaque",
    "Scanner pulmonaire",
    "Scanner osseux",
    "Scanner pelvien",
    "Scanner corps entier"
]

PROTOCOLES = [
    "Standard",
    "Low Dose",
    "Pédiatrique",
    "Cardiaque",
    "Trauma",
    "Haute résolution"
]

# =========================
# CALCUL PATIENT
# =========================
def protocole_examen(type_examen):
    data = {
        "Scanner cérébral": {"ctdi": 50, "kvp": 120, "mas": 250, "dlp": 900},
        "Scanner thoracique": {"ctdi": 10, "kvp": 100, "mas": 120, "dlp": 350},
        "Scanner abdominal": {"ctdi": 15, "kvp": 120, "mas": 180, "dlp": 600},
        "Scanner cardiaque": {"ctdi": 20, "kvp": 100, "mas": 220, "dlp": 450},
        "Scanner pulmonaire": {"ctdi": 8, "kvp": 100, "mas": 90, "dlp": 250},
        "Scanner osseux": {"ctdi": 12, "kvp": 120, "mas": 160, "dlp": 400},
        "Scanner pelvien": {"ctdi": 14, "kvp": 120, "mas": 170, "dlp": 500},
        "Scanner corps entier": {"ctdi": 25, "kvp": 120, "mas": 300, "dlp": 1100}
    }
    return data[type_examen]

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
    return "Obésité"

def dose_adaptee(age, imc, type_examen, protocole):
    ref = protocole_examen(type_examen)["ctdi"]

    facteur_imc = 1 + 0.015 * (imc - 25)
    facteur_age = 1 + 0.002 * (age - 40)

    facteur_protocole = {
        "Standard": 1.00,
        "Low Dose": 0.75,
        "Pédiatrique": 0.60,
        "Cardiaque": 1.10,
        "Trauma": 1.20,
        "Haute résolution": 1.15
    }[protocole]

    dose = ref * facteur_imc * facteur_age * facteur_protocole
    dose = max(dose, ref * 0.50)
    dose = min(dose, ref * 1.40)
    return round(dose, 2)

def calcul_snr(age, imc, dose):
    snr = 60 - 0.30 * imc - 0.05 * age + 0.70 * dose
    return round(max(snr, 10), 2)

def qualite_image(snr):
    if snr >= 70:
        return "Excellente"
    elif snr >= 55:
        return "Bonne"
    elif snr >= 50:
        return "Acceptable"
    return "Insuffisante"

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

def recommandation_patient(snr, dose, imc):
    if snr < 50:
        return "Qualité image insuffisante : augmenter légèrement le mAs ou ajuster la dose."
    elif snr >= 50 and dose <= 25:
        return "Paramètres acceptables : dose optimisée avec qualité image correcte."
    elif imc > 30:
        return "Patient à IMC élevé : surveiller le bruit image et adapter le mAs."
    return "Acquisition acceptable selon les paramètres estimés."

def creer_patient(nom, prenom, cin, sexe, age, poids, taille, type_examen, protocole, numero_serie):
    scanner = SCANNERS[numero_serie]

    imc = calcul_imc(poids, taille)
    dose = dose_adaptee(age, imc, type_examen, protocole)
    snr = calcul_snr(age, imc, dose)
    kvp, mas, ctdi, dlp = adaptation_parametres(age, imc, type_examen, dose, snr)

    return {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "nom": nom,
        "prenom": prenom,
        "cin": cin,
        "sexe": sexe,
        "age": age,
        "poids": poids,
        "taille": taille,
        "type_examen": type_examen,
        "protocole": protocole,
        "imc": round(imc, 2),
        "classe_imc": classe_imc(imc),
        "dose": dose,
        "snr": snr,
        "qualite_image": qualite_image(snr),
        "kvp": kvp,
        "mas": mas,
        "ctdi": ctdi,
        "dlp": dlp,
        "scanner": scanner["nom"],
        "marque": scanner["marque"],
        "modele": scanner["modele"],
        "numero_serie": numero_serie,
        "recommandation": recommandation_patient(snr, dose, imc)
    }

def save_patient(p):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    try:
        c.execute("""
        INSERT INTO patients (
            date, nom, prenom, cin, sexe, age, poids, taille,
            type_examen, protocole, imc, classe_imc, dose, snr,
            qualite_image, kvp, mas, ctdi, dlp, scanner, marque,
            modele, numero_serie, recommandation
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p["date"], p["nom"], p["prenom"], p["cin"], p["sexe"], p["age"],
            p["poids"], p["taille"], p["type_examen"], p["protocole"],
            p["imc"], p["classe_imc"], p["dose"], p["snr"], p["qualite_image"],
            p["kvp"], p["mas"], p["ctdi"], p["dlp"], p["scanner"], p["marque"],
            p["modele"], p["numero_serie"], p["recommandation"]
        ))
        conn.commit()
        ok = True
    except sqlite3.IntegrityError:
        ok = False

    conn.close()
    return ok

def load_patients():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM patients", conn)
    conn.close()
    return df

# =========================
# MAINTENANCE
# =========================
def generer_parametres_scanner(numero_serie):
    if numero_serie == "NS-PCCT-2026-001":
        return 65, 45, 15, 18, 8500, "Stable", "Normal"
    elif numero_serie == "NS-PCCT-2026-002":
        return 48, 68, 42, 45, 22000, "Légère dégradation", "À surveiller"
    return 38, 86, 75, 70, 36000, "Dégradation importante", "Défaillant"

def analyser_maintenance(numero_serie):
    scanner = SCANNERS[numero_serie]
    snr, temp, vibration, bruit, heures, detecteurs, refroidissement = generer_parametres_scanner(numero_serie)

    score = 0
    score += max(0, 50 - snr) * 1.3
    score += max(0, temp - 60) * 1.2
    score += vibration * 0.5
    score += bruit * 0.4
    score += heures * 0.001

    if detecteurs == "Légère dégradation":
        score += 15
    elif detecteurs == "Dégradation importante":
        score += 35

    if refroidissement == "À surveiller":
        score += 15
    elif refroidissement == "Défaillant":
        score += 35

    score = round(min(score, 100), 2)

    if score < 35:
        etat = "Stable"
        couleur = "🟢"
    elif score < 70:
        etat = "À surveiller"
        couleur = "🟠"
    else:
        etat = "Critique"
        couleur = "🔴"

    composant = "Aucun composant critique"
    cause = "Fonctionnement normal"
    action = "Surveillance régulière"

    if temp > 75 or refroidissement == "Défaillant":
        composant = "Tube RX / Refroidissement"
        cause = "Température élevée ou refroidissement insuffisant"
        action = "Contrôler le refroidissement et vérifier le tube RX"
    elif vibration > 60:
        composant = "Gantry"
        cause = "Vibrations mécaniques élevées"
        action = "Vérifier l’alignement mécanique et les roulements"
    elif snr < 45 or bruit > 60 or detecteurs == "Dégradation importante":
        composant = "Détecteurs photon-counting"
        cause = "Baisse du SNR ou bruit image élevé"
        action = "Effectuer une calibration des détecteurs"
    elif heures > 30000:
        composant = "Tube RX"
        cause = "Nombre d’heures d’utilisation élevé"
        action = "Planifier une maintenance préventive"

    return {
        "scanner": scanner["nom"],
        "marque": scanner["marque"],
        "modele": scanner["modele"],
        "numero_serie": numero_serie,
        "snr_systeme": snr,
        "temperature": temp,
        "vibration": vibration,
        "bruit": bruit,
        "heures": heures,
        "detecteurs": detecteurs,
        "refroidissement": refroidissement,
        "score": score,
        "etat": etat,
        "couleur": couleur,
        "composant": composant,
        "cause": cause,
        "action": action
    }

def save_maintenance(m):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    INSERT INTO maintenance (
        date, scanner, marque, modele, numero_serie, snr_systeme,
        temperature, vibration, bruit, heures, detecteurs, refroidissement,
        score, etat, composant, cause, action
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        m["scanner"], m["marque"], m["modele"], m["numero_serie"],
        m["snr_systeme"], m["temperature"], m["vibration"], m["bruit"],
        m["heures"], m["detecteurs"], m["refroidissement"], m["score"],
        m["etat"], m["composant"], m["cause"], m["action"]
    ))

    conn.commit()
    conn.close()

def load_maintenance():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM maintenance", conn)
    conn.close()
    return df

# =========================
# EXPORTS
# =========================
def export_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

def generer_pdf_patient(row):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    y = 800

    pdf.setFont("Helvetica-Bold", 17)
    pdf.drawString(95, y, "Rapport Patient - PROMAMEC PCCT Intelligent System")
    y -= 40

    pdf.setFont("Helvetica", 10)

    for key, value in row.items():
        pdf.drawString(45, y, f"{key} : {value}")
        y -= 18

        if y < 60:
            pdf.showPage()
            y = 800
            pdf.setFont("Helvetica", 10)

    pdf.save()
    buffer.seek(0)
    return buffer

# =========================
# SIDEBAR
# =========================
if os.path.exists(LOGO_PATH):
    st.sidebar.image(LOGO_PATH, width=170)

st.sidebar.markdown("## PROMAMEC")
st.sidebar.write(f"Utilisateur : {st.session_state.nom_utilisateur}")
st.sidebar.write(f"Rôle : {st.session_state.role}")

if st.sidebar.button("Déconnexion"):
    st.session_state.connecte = False
    st.session_state.role = ""
    st.session_state.nom_utilisateur = ""
    st.rerun()

if st.session_state.role == "Technicien de radiologie":
    pages = ["Accueil", "Workflow acquisition", "Analyse SNR", "Dashboard", "Rapport"]
else:
    pages = ["Accueil", "Maintenance préventive", "Maintenance scanner", "Dashboard", "Logs système", "Rapport"]

menu = st.sidebar.radio("Navigation", pages)

# =========================
# ACCUEIL
# =========================
if menu == "Accueil":
    st.markdown("""
    <div class="hero-card">
        <h1>PROMAMEC PCCT Intelligent System</h1>
        <h3>Optimisation intelligente de dose et maintenance prédictive</h3>
        <p>
        Cette application simule un système intelligent destiné aux scanners Photon Counting CT.
        Elle permet d’adapter la dose au profil du patient, d’évaluer la qualité image à travers le SNR
        et d’assurer une surveillance biomédicale du scanner.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="card">
            <h3>Objectif de l’application</h3>
            <p>
            L’objectif est d’aider le technicien et l’ingénieur biomédical à optimiser les paramètres
            d’acquisition, suivre les performances du scanner et générer des rapports automatiquement.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
            <h3>Présentation de PROMAMEC</h3>
            <p>
            PROMAMEC est une entreprise spécialisée dans les équipements médicaux, l’installation,
            l’assistance technique et la maintenance des dispositifs biomédicaux.
            </p>
        </div>
        """, unsafe_allow_html=True)

# =========================
# WORKFLOW ACQUISITION
# =========================
elif menu == "Workflow acquisition":
    st.title("Workflow acquisition patient")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        cin = st.text_input("CIN")
        sexe = st.selectbox("Sexe", ["Homme", "Femme"])
        age = st.number_input("Âge", 0, 120, 0)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        poids = st.number_input("Poids (kg)", 0.0, 200.0, 0.0)
        taille = st.number_input("Taille (cm)", 0.0, 220.0, 0.0)
        type_examen = st.selectbox("Type d’examen", EXAMENS)
        protocole = st.selectbox("Protocole", PROTOCOLES)
        numero_serie = st.text_input("Numéro de série du scanner")
        st.markdown('</div>', unsafe_allow_html=True)

    if numero_serie in SCANNERS:
        sc = SCANNERS[numero_serie]
        st.success("Scanner reconnu.")
        c1, c2, c3 = st.columns(3)
        c1.metric("Marque", sc["marque"])
        c2.metric("Modèle", sc["modele"])
        c3.metric("N° série", numero_serie)
    elif numero_serie != "":
        st.error("Numéro de série non reconnu.")

    if st.button("Lancer acquisition et analyse IA"):
        if nom == "" or prenom == "" or cin == "" or age <= 0 or poids <= 0 or taille <= 0 or numero_serie not in SCANNERS:
            st.error("Veuillez compléter toutes les informations.")
        else:
            progress = st.progress(0)
            status = st.empty()

            etapes = [
                "Connexion scanner...",
                "Analyse patient...",
                "Calcul IMC...",
                "Optimisation dose...",
                "Analyse SNR...",
                "Génération résultats..."
            ]

            for i, e in enumerate(etapes):
                status.info(e)
                progress.progress(int((i + 1) / len(etapes) * 100))

            p = creer_patient(nom, prenom, cin, sexe, age, poids, taille, type_examen, protocole, numero_serie)
            ok = save_patient(p)

            if ok:
                st.success("Patient enregistré avec succès.")
            else:
                st.warning("Patient déjà enregistré avec ce CIN.")

            r1, r2, r3, r4 = st.columns(4)
            r1.metric("IMC", p["imc"])
            r2.metric("Dose", f"{p['dose']} mGy")
            r3.metric("SNR", p["snr"])
            r4.metric("Qualité image", p["qualite_image"])

            st.info(p["recommandation"])

# =========================
# ANALYSE SNR
# =========================
elif menu == "Analyse SNR":
    st.title("Analyse SNR")

    imc = st.slider("IMC", 15, 45, 25)
    age = st.slider("Âge", 10, 90, 40)

    doses = np.linspace(3, 60, 40)
    snrs = [calcul_snr(age, imc, d) for d in doses]

    df = pd.DataFrame({"Dose": doses, "SNR": snrs})
    st.line_chart(df.set_index("Dose"))

# =========================
# MAINTENANCE PREVENTIVE
# =========================
elif menu == "Maintenance préventive":
    st.title("Maintenance préventive du parc scanner")

    rows = []

    for serial in SCANNERS:
        m = analyser_maintenance(serial)
        rows.append({
            "Scanner": m["scanner"],
            "Marque": m["marque"],
            "Modèle": m["modele"],
            "N° série": m["numero_serie"],
            "État": m["etat"],
            "Score stress": m["score"],
            "Composant suspect": m["composant"]
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)
    st.bar_chart(df.set_index("Scanner")["Score stress"])

# =========================
# MAINTENANCE SCANNER
# =========================
elif menu == "Maintenance scanner":
    st.title("Maintenance scanner")

    numero_serie = st.text_input("Entrer le numéro de série du scanner")

    if numero_serie == "":
        st.info("Veuillez entrer un numéro de série.")

        c1, c2, c3, c4 = st.columns(4)
        c1.text_input("SNR système", value="", disabled=True)
        c2.text_input("Température", value="", disabled=True)
        c3.text_input("Vibration", value="", disabled=True)
        c4.text_input("Bruit image", value="", disabled=True)

    elif numero_serie not in SCANNERS:
        st.error("Scanner non reconnu.")

    else:
        m = analyser_maintenance(numero_serie)

        st.success("Scanner reconnu.")

        c1, c2, c3 = st.columns(3)
        c1.metric("Marque", m["marque"])
        c2.metric("Modèle", m["modele"])
        c3.metric("N° série", m["numero_serie"])

        st.markdown("### Paramètres techniques calculés automatiquement")

        a1, a2, a3, a4 = st.columns(4)
        a1.text_input("SNR système", value=str(m["snr_systeme"]), disabled=True)
        a2.text_input("Température", value=f"{m['temperature']} °C", disabled=True)
        a3.text_input("Vibration", value=f"{m['vibration']} %", disabled=True)
        a4.text_input("Bruit image", value=f"{m['bruit']} %", disabled=True)

        b1, b2, b3 = st.columns(3)
        b1.text_input("Heures d’utilisation", value=str(m["heures"]), disabled=True)
        b2.text_input("État détecteurs", value=m["detecteurs"], disabled=True)
        b3.text_input("Refroidissement", value=m["refroidissement"], disabled=True)

        st.markdown("### Diagnostic IA")

        d1, d2, d3 = st.columns(3)
        d1.metric("Score stress", f"{m['score']} %")
        d2.metric("État global", f"{m['couleur']} {m['etat']}")
        d3.metric("Composant suspect", m["composant"])

        st.write(f"**Cause probable :** {m['cause']}")
        st.write(f"**Action recommandée :** {m['action']}")

        dfm = pd.DataFrame({
            "Paramètre": ["SNR", "Température", "Vibration", "Bruit", "Score"],
            "Valeur": [m["snr_systeme"], m["temperature"], m["vibration"], m["bruit"], m["score"]]
        })

        st.bar_chart(dfm.set_index("Paramètre"))

        if st.button("Enregistrer log maintenance"):
            save_maintenance(m)
            st.success("Log maintenance enregistré.")

# =========================
# DASHBOARD
# =========================
elif menu == "Dashboard":
    st.title("Dashboard global")

    df_patients = load_patients()

    if df_patients.empty:
        st.warning("Aucun patient enregistré.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Patients", len(df_patients))
        c2.metric("Dose moyenne", round(df_patients["dose"].mean(), 2))
        c3.metric("SNR moyen", round(df_patients["snr"].mean(), 2))
        c4.metric("SNR < 50", int((df_patients["snr"] < 50).sum()))

        st.dataframe(df_patients, use_container_width=True)

        st.subheader("Évolution Dose / SNR")
        st.line_chart(df_patients[["dose", "snr"]])

        st.subheader("Répartition des examens")
        st.bar_chart(df_patients["type_examen"].value_counts())

        st.download_button(
            "Exporter Excel",
            data=export_excel(df_patients),
            file_name="patients_pcct.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# =========================
# LOGS SYSTEME
# =========================
elif menu == "Logs système":
    st.title("Logs système et historique maintenance")

    df_logs = load_maintenance()

    if df_logs.empty:
        st.warning("Aucun log maintenance enregistré.")
    else:
        st.dataframe(df_logs, use_container_width=True)
        st.subheader("États scanners")
        st.bar_chart(df_logs["etat"].value_counts())

# =========================
# RAPPORT
# =========================
elif menu == "Rapport":
    st.title("Rapports patients")

    df = load_patients()

    if df.empty:
        st.warning("Aucun patient enregistré.")
    else:
        st.dataframe(df, use_container_width=True)

        patient_id = st.selectbox(
            "Choisir patient",
            df["id"],
            format_func=lambda x: f"{df[df['id'] == x]['nom'].values[0]} {df[df['id'] == x]['prenom'].values[0]}"
        )

        row = df[df["id"] == patient_id].iloc[0].to_dict()

        st.markdown("### Aperçu")
        st.write(row)

        pdf = generer_pdf_patient(row)

        st.download_button(
            "Télécharger rapport PDF",
            data=pdf,
            file_name=f"rapport_{row['nom']}_{row['prenom']}.pdf",
            mime="application/pdf"
        )
