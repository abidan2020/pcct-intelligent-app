# =========================================================
# PROMAMEC PCCT INTELLIGENT SYSTEM
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import os
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="PROMAMEC PCCT Intelligent System",
    layout="wide"
)

DB_NAME = "pcct_promamec.db"
LOGO_PATH = "imagespromamec.png"

# =========================================================
# STYLE PROMAMEC
# =========================================================

st.markdown("""
<style>

:root {
    --promamec: #00A99D;
    --promamec-dark: #007E75;
    --text-dark: #1F2933;
    --bg-light: #F7FAFA;
    --white: #FFFFFF;
    --border: #E5E7EB;
}

.stApp {
    background: var(--bg-light);
    color: var(--text-dark);
}

/* SIDEBAR */

[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #E5E7EB;
}

[data-testid="stSidebar"] * {
    color: var(--text-dark) !important;
}

/* TITRES */

h1, h2, h3 {
    color: var(--text-dark) !important;
    font-weight: 800 !important;
}

/* CARTES */

.card {
    background: white;
    padding: 28px;
    border-radius: 12px;
    border: 1px solid var(--border);
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    margin-bottom: 22px;
}

.hero-card {
    background:
    linear-gradient(
        rgba(0,0,0,0.45),
        rgba(0,0,0,0.45)
    ),
    url("https://images.unsplash.com/photo-1584515933487-779824d29309");

    background-size: cover;
    background-position: center;

    padding: 90px 60px;

    border-radius: 12px;

    margin-bottom: 30px;
}

.hero-card h1 {
    color: white !important;
    font-size: 42px !important;
}

.hero-card p {
    color: white !important;
    font-size: 18px;
}

/* BOUTONS */

.stButton > button {

    background: var(--promamec);

    color: white !important;

    border: none;

    border-radius: 6px;

    font-weight: 700;
}

.stButton > button:hover {

    background: var(--promamec-dark);

    color: white !important;
}

/* METRICS */

[data-testid="stMetric"] {

    background: white;

    border-radius: 10px;

    padding: 18px;

    border-top: 4px solid var(--promamec);

    box-shadow:
    0 4px 14px rgba(0,0,0,0.06);
}

[data-testid="stMetric"] * {
    color: var(--text-dark) !important;
}

/* INPUTS */

input, textarea, select {

    color: var(--text-dark) !important;

    background: white !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION
# =========================================================

if "connecte" not in st.session_state:
    st.session_state.connecte = False

if "role" not in st.session_state:
    st.session_state.role = ""

if "nom_utilisateur" not in st.session_state:
    st.session_state.nom_utilisateur = ""

# =========================================================
# LOGIN
# =========================================================

def login():

    col1, col2, col3 = st.columns([1,1.4,1])

    with col2:

        st.markdown(
            '<div class="card">',
            unsafe_allow_html=True
        )

        if os.path.exists(LOGO_PATH):

            st.image(
                LOGO_PATH,
                width=240
            )

        st.title(
            "PCCT Intelligent System"
        )

        st.subheader(
            "Connexion sécurisée"
        )

        nom = st.text_input(
            "Nom utilisateur"
        )

        identifiant = st.text_input(
            "ID utilisateur",
            type="password"
        )

        if st.button("Se connecter"):

            if (
                nom.strip().lower()
                == "yassine abidan"
                and identifiant == "12345"
            ):

                st.session_state.connecte = True
                st.session_state.role = "Technicien de radiologie"
                st.session_state.nom_utilisateur = "Yassine Abidan"

                st.rerun()

            elif (
                nom.strip().lower()
                == "khadija abidan"
                and identifiant == "67890"
            ):

                st.session_state.connecte = True
                st.session_state.role = "Ingénieure biomédicale"
                st.session_state.nom_utilisateur = "Khadija ABIDAN"

                st.rerun()

            else:

                st.error(
                    "Nom ou ID incorrect."
                )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

if not st.session_state.connecte:

    login()

    st.stop()

# =========================================================
# DATABASE
# =========================================================

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

# =========================================================
# SCANNERS
# =========================================================

SCANNERS = {

    "NS-PCCT-2026-001": {

        "nom":"Scanner PCCT-01",
        "marque":"Neusoft",
        "modele":"NeuViz Glory PCCT"
    },

    "NS-PCCT-2026-002": {

        "nom":"Scanner PCCT-02",
        "marque":"Neusoft",
        "modele":"NeuViz Prime"
    },

    "NS-PCCT-2026-003": {

        "nom":"Scanner PCCT-03",
        "marque":"Neusoft",
        "modele":"NeuViz Epoch"
    }
}

EXAMENS = [

    "Scanner cérébral",
    "Scanner thoracique",
    "Scanner abdominal",
    "Scanner cardiaque",
    "Scanner pulmonaire",
    "Scanner osseux",
    "Scanner pelvien"
]

PROTOCOLES = [

    "Standard",
    "Low Dose",
    "Pédiatrique",
    "Cardiaque",
    "Trauma"
]

# =========================================================
# FONCTIONS
# =========================================================

def calcul_imc(poids, taille):

    if taille <= 0:
        return 0

    return poids / ((taille / 100) ** 2)

def classe_imc(imc):

    if imc < 18.5:
        return "Maigreur"

    elif imc < 25:
        return "Normal"

    elif imc < 30:
        return "Surpoids"

    return "Obésité"

def calcul_dose(age, imc):

    return round(
        12 + (imc * 0.25) + (age * 0.03),
        2
    )

def calcul_snr(age, imc, dose):

    return round(
        60
        - (0.30 * imc)
        - (0.05 * age)
        + (0.70 * dose),
        2
    )

def qualite_image(snr):

    if snr >= 70:
        return "Excellente"

    elif snr >= 55:
        return "Bonne"

    elif snr >= 50:
        return "Acceptable"

    return "Insuffisante"

def maintenance_scanner(numero_serie):

    if numero_serie == "NS-PCCT-2026-001":

        return {

            "snr":65,
            "temp":45,
            "vibration":15,
            "bruit":18,
            "heures":8500,
            "detecteurs":"Stable",
            "refroidissement":"Normal",
            "etat":"Stable",
            "couleur":"🟢"
        }

    elif numero_serie == "NS-PCCT-2026-002":

        return {

            "snr":48,
            "temp":68,
            "vibration":42,
            "bruit":45,
            "heures":22000,
            "detecteurs":"Légère dégradation",
            "refroidissement":"À surveiller",
            "etat":"À surveiller",
            "couleur":"🟠"
        }

    return {

        "snr":38,
        "temp":86,
        "vibration":75,
        "bruit":70,
        "heures":36000,
        "detecteurs":"Dégradation importante",
        "refroidissement":"Défaillant",
        "etat":"Critique",
        "couleur":"🔴"
    }

# =========================================================
# SIDEBAR
# =========================================================

if os.path.exists(LOGO_PATH):

    st.sidebar.image(
        LOGO_PATH,
        width=170
    )

st.sidebar.markdown("## PROMAMEC")

st.sidebar.write(
    f"Utilisateur : {st.session_state.nom_utilisateur}"
)

st.sidebar.write(
    f"Rôle : {st.session_state.role}"
)

if st.sidebar.button("Déconnexion"):

    st.session_state.connecte = False

    st.rerun()

if (
    st.session_state.role
    == "Technicien de radiologie"
):

    pages = [

        "Accueil",
        "Workflow acquisition",
        "Analyse SNR",
        "Dashboard",
        "Rapport"
    ]

else:

    pages = [

        "Accueil",
        "Maintenance préventive",
        "Maintenance scanner",
        "Dashboard",
        "Logs système",
        "Rapport"
    ]

menu = st.sidebar.radio(
    "Navigation",
    pages
)

# =========================================================
# ACCUEIL
# =========================================================

if menu == "Accueil":

    st.markdown("""

    <div class="hero-card">

    <h1>
    Système intelligent pour
    l’optimisation de dose
    et la maintenance prédictive
    en PCCT
    </h1>

    <p>
    Une solution biomédicale inspirée
    des besoins réels des services
    de radiologie et de maintenance.
    </p>

    </div>

    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("""

        <div class="card">

        <h3>
        Objectif de l’application
        </h3>

        <p>

        Optimisation automatique
        de dose patient,
        estimation SNR,
        qualité image,
        aide décisionnelle
        et génération de rapports.

        </p>

        </div>

        """, unsafe_allow_html=True)

    with col2:

        st.markdown("""

        <div class="card">

        <h3>
        Approche biomédicale
        </h3>

        <p>

        Le système intègre
        un module intelligent
        de maintenance prédictive
        permettant de surveiller
        les scanners.

        </p>

        </div>

        """, unsafe_allow_html=True)

# =========================================================
# WORKFLOW ACQUISITION
# =========================================================

elif menu == "Workflow acquisition":

    st.title(
        "Workflow acquisition patient"
    )

    col1, col2 = st.columns(2)

    with col1:

        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        cin = st.text_input("CIN")

        sexe = st.selectbox(
            "Sexe",
            ["Homme","Femme"]
        )

        age = st.number_input(
            "Âge",
            0,
            120,
            0
        )

    with col2:

        poids = st.number_input(
            "Poids (kg)",
            0.0,
            200.0,
            0.0
        )

        taille = st.number_input(
            "Taille (cm)",
            0.0,
            220.0,
            0.0
        )

        type_examen = st.selectbox(
            "Type examen",
            EXAMENS
        )

        protocole = st.selectbox(
            "Protocole",
            PROTOCOLES
        )

        numero_serie = st.text_input(
            "Numéro série scanner"
        )

    if numero_serie in SCANNERS:

        sc = SCANNERS[numero_serie]

        st.success(
            "Scanner reconnu"
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Marque",
            sc["marque"]
        )

        c2.metric(
            "Modèle",
            sc["modele"]
        )

        c3.metric(
            "N° série",
            numero_serie
        )

    elif numero_serie != "":

        st.error(
            "Scanner non reconnu"
        )

    if st.button("Lancer acquisition IA"):

        if (
            nom == ""
            or prenom == ""
            or cin == ""
            or numero_serie not in SCANNERS
        ):

            st.error(
                "Veuillez compléter les informations"
            )

        else:

            progress = st.progress(0)

            status = st.empty()

            etapes = [

                "Connexion scanner...",
                "Analyse patient...",
                "Calcul IMC...",
                "Optimisation dose...",
                "Analyse SNR...",
                "Résultats générés..."
            ]

            for i, e in enumerate(etapes):

                status.info(e)

                progress.progress(
                    int((i+1)/len(etapes)*100)
                )

            imc = calcul_imc(
                poids,
                taille
            )

            dose = calcul_dose(
                age,
                imc
            )

            snr = calcul_snr(
                age,
                imc,
                dose
            )

            qualite = qualite_image(
                snr
            )

            r1, r2, r3, r4 = st.columns(4)

            r1.metric(
                "IMC",
                round(imc,2)
            )

            r2.metric(
                "Dose",
                f"{dose} mGy"
            )

            r3.metric(
                "SNR",
                snr
            )

            r4.metric(
                "Qualité image",
                qualite
            )

# =========================================================
# ANALYSE SNR
# =========================================================

elif menu == "Analyse SNR":

    st.title(
        "Analyse SNR"
    )

    imc = st.slider(
        "IMC",
        15,
        45,
        25
    )

    age = st.slider(
        "Âge",
        10,
        90,
        40
    )

    doses = np.linspace(3,60,40)

    snrs = [

        calcul_snr(
            age,
            imc,
            d
        )

        for d in doses
    ]

    df = pd.DataFrame({

        "Dose":doses,
        "SNR":snrs
    })

    st.line_chart(
        df.set_index("Dose")
    )

# =========================================================
# MAINTENANCE PREVENTIVE
# =========================================================

elif menu == "Maintenance préventive":

    st.title(
        "Maintenance préventive"
    )

    rows = []

    for serial in SCANNERS:

        m = maintenance_scanner(serial)

        rows.append({

            "Scanner":serial,
            "État":m["etat"],
            "SNR":m["snr"],
            "Température":m["temp"]
        })

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True
    )

# =========================================================
# MAINTENANCE SCANNER
# =========================================================

elif menu == "Maintenance scanner":

    st.title(
        "Maintenance scanner"
    )

    numero_serie = st.text_input(
        "Entrer numéro série scanner"
    )

    if numero_serie == "":

        st.info(
            "Veuillez entrer un numéro de série."
        )

    elif numero_serie not in SCANNERS:

        st.error(
            "Scanner non reconnu."
        )

    else:

        m = maintenance_scanner(
            numero_serie
        )

        sc = SCANNERS[numero_serie]

        st.success(
            "Scanner reconnu"
        )

        c1,c2,c3 = st.columns(3)

        c1.metric(
            "Marque",
            sc["marque"]
        )

        c2.metric(
            "Modèle",
            sc["modele"]
        )

        c3.metric(
            "État",
            f"{m['couleur']} {m['etat']}"
        )

        st.markdown(
            "### Paramètres techniques"
        )

        a1,a2,a3,a4 = st.columns(4)

        a1.metric(
            "SNR système",
            m["snr"]
        )

        a2.metric(
            "Température",
            f"{m['temp']} °C"
        )

        a3.metric(
            "Vibration",
            f"{m['vibration']} %"
        )

        a4.metric(
            "Bruit image",
            f"{m['bruit']} %"
        )

# =========================================================
# DASHBOARD
# =========================================================

elif menu == "Dashboard":

    st.title(
        "Dashboard global"
    )

    data = {

        "Scanner":[
            "PCCT-01",
            "PCCT-02",
            "PCCT-03"
        ],

        "Disponibilité":[
            98,
            87,
            65
        ],

        "SNR":[
            65,
            48,
            38
        ]
    }

    df = pd.DataFrame(data)

    st.dataframe(
        df,
        use_container_width=True
    )

    st.bar_chart(
        df.set_index("Scanner")
    )

# =========================================================
# LOGS SYSTEME
# =========================================================

elif menu == "Logs système":

    st.title(
        "Logs système"
    )

    logs = [

        "[12:05] Scanner connecté",

        "[12:07] Analyse SNR effectuée",

        "[12:08] Température élevée détectée",

        "[12:09] Maintenance préventive recommandée"
    ]

    for log in logs:

        st.markdown(f"""

        <div class="card">

        {log}

        </div>

        """, unsafe_allow_html=True)

# =========================================================
# RAPPORT
# =========================================================

elif menu == "Rapport":

    st.title(
        "Rapports"
    )

    st.info(
        "Module rapport PDF / Excel prêt."
    )
