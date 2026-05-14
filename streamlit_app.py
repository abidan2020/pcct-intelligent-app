
# =========================================================
# PROMAMEC PCCT INTELLIGENT SYSTEM
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import os
from datetime import datetime

# =========================================================
# CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="PROMAMEC PCCT Intelligent System",
    layout="wide"
)

DB_NAME = "pcct_promamec.db"

# =========================================================
# STYLE PROMAMEC HOMOGÈNE
# =========================================================

st.markdown("""
<style>

:root {
    --green-dark: #006B4F;
    --green-main: #008B68;
    --green-soft: #F2FAF7;
    --green-border: #CFE8DE;
    --text-dark: #1F2933;
    --white: #FFFFFF;
}

.stApp {
    background: #F8FCFA;
    color: var(--text-dark);
}

/* SIDEBAR */

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #006B4F 0%,
        #008B68 100%
    );
}

[data-testid="stSidebar"] * {
    color: white !important;
}

/* TITRES */

h1,h2,h3,h4 {
    color: var(--green-dark) !important;
    font-weight: 700 !important;
}

/* TEXTES */

p,label,span,div {
    color: var(--text-dark);
}

/* CARTES */

.card,
.soft-card,
.hero-card {

    background: white;

    padding: 24px;

    border-radius: 18px;

    border: 1px solid var(--green-border);

    box-shadow:
    0 6px 18px rgba(0,107,79,0.10);

    margin-bottom: 18px;
}

/* BOUTONS */

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

/* METRICS */

[data-testid="stMetric"] {

    background: white;

    border-radius: 14px;

    padding: 14px;

    border-left:
    5px solid var(--green-main);

    box-shadow:
    0 4px 12px rgba(0,107,79,0.08);
}

[data-testid="stMetric"] * {

    color: var(--text-dark) !important;
}

/* INPUTS */

input, textarea {

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

    col1, col2, col3 = st.columns([1,1.5,1])

    with col2:

        st.markdown(
            '<div class="card">',
            unsafe_allow_html=True
        )

        if os.path.exists("imagespromamec.png"):

            st.image(
                "imagespromamec.png",
                width=240
            )

        st.title("PCCT Intelligent System")

        st.subheader(
            "Connexion sécurisée"
        )

        st.markdown("---")

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
        cin TEXT,

        sexe TEXT,
        age INTEGER,

        poids REAL,
        taille REAL,

        type_examen TEXT,
        protocole TEXT,

        imc REAL,
        dose REAL,
        snr REAL,

        qualite TEXT
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
    "Scanner pulmonaire"
]

PROTOCOLES = [

    "Standard",
    "Low Dose",
    "Pédiatrique",
    "Cardiaque"
]

# =========================================================
# FONCTIONS
# =========================================================

def calcul_imc(poids, taille):

    return poids / ((taille/100)**2)

def calcul_dose(age, imc):

    return round(
        12 + (imc*0.25) + (age*0.03),
        2
    )

def calcul_snr(age, imc, dose):

    return round(
        60
        - (0.30*imc)
        - (0.05*age)
        + (0.70*dose),
        2
    )

def qualite_image(snr):

    if snr >= 70:
        return "Excellente"

    elif snr >= 55:
        return "Bonne"

    elif snr >= 50:
        return "Acceptable"

    else:
        return "Insuffisante"

def maintenance_scanner(numero_serie):

    if numero_serie == "NS-PCCT-2026-001":

        return {

            "snr":65,
            "temp":45,
            "vibration":15,
            "bruit":18,
            "etat":"Stable",
            "couleur":"🟢"
        }

    elif numero_serie == "NS-PCCT-2026-002":

        return {

            "snr":48,
            "temp":68,
            "vibration":42,
            "bruit":45,
            "etat":"À surveiller",
            "couleur":"🟠"
        }

    else:

        return {

            "snr":38,
            "temp":86,
            "vibration":75,
            "bruit":70,
            "etat":"Critique",
            "couleur":"🔴"
        }

# =========================================================
# SIDEBAR
# =========================================================

if os.path.exists("imagespromamec.png"):

    st.sidebar.image(
        "imagespromamec.png",
        width=170
    )

st.sidebar.markdown(
    "## PROMAMEC"
)

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
        "Dashboard"
    ]

else:

    pages = [

        "Accueil",
        "Maintenance préventive",
        "Maintenance scanner",
        "Dashboard"
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
    PROMAMEC PCCT Intelligent System
    </h1>

    <h3>
    Optimisation intelligente de dose
    et maintenance prédictive
    </h3>

    <p>

    Cette application permet :

    • optimisation automatique de dose

    • estimation SNR

    • analyse qualité image

    • surveillance scanner

    • maintenance prédictive biomédicale

    </p>

    </div>

    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("""

        <div class="card">

        <h3>
        Objectif du système
        </h3>

        <p>

        Adapter automatiquement
        les paramètres scanner
        selon le profil patient
        tout en gardant une bonne
        qualité image.

        </p>

        </div>

        """, unsafe_allow_html=True)

    with col2:

        st.markdown("""

        <div class="card">

        <h3>
        À propos de PROMAMEC
        </h3>

        <p>

        PROMAMEC est spécialisée
        dans les équipements biomédicaux,
        l’installation et la maintenance
        des dispositifs médicaux.

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

        st.success("Scanner reconnu")

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
            "N° série",
            numero_serie
        )

    elif numero_serie != "":

        st.error("Scanner non reconnu")

    if st.button("Lancer acquisition"):

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

            qualite = qualite_image(snr)

            r1,r2,r3,r4 = st.columns(4)

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

    st.title("Analyse SNR")

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
# MAINTENANCE PRÉVENTIVE
# =========================================================

elif menu == "Maintenance préventive":

    st.title(
        "Maintenance préventive"
    )

    data = []

    for serial in SCANNERS:

        m = maintenance_scanner(serial)

        data.append({

            "Scanner":serial,
            "État":m["etat"],
            "SNR":m["snr"],
            "Température":m["temp"]
        })

    st.dataframe(
        pd.DataFrame(data),
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
