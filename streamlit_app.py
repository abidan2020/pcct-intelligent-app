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
# CONFIG
# =========================================================

st.set_page_config(
    page_title="PROMAMEC PCCT Intelligent System",
    layout="wide"
)

DB_NAME = "patients_pcct.db"


# =========================================================
# STYLE
# =========================================================

st.markdown("""
<style>

:root{
    --blue:#0ea5e9;
    --dark:#03111f;
    --card:#07192b;
    --text:#e2e8f0;
}

/* GENERAL */

.stApp{
    background:linear-gradient(135deg,#03111f,#07192b);
    color:var(--text);
}

/* SIDEBAR */

[data-testid="stSidebar"]{
    background:#03111f;
    border-right:1px solid rgba(14,165,233,0.2);
}

[data-testid="stSidebar"] *{
    color:white !important;
}

/* TITLES */

h1,h2,h3,h4{
    color:white !important;
    font-weight:800 !important;
}

/* CARDS */

.card{
    background:rgba(7,25,43,0.88);
    padding:24px;
    border-radius:18px;
    border:1px solid rgba(14,165,233,0.15);
    box-shadow:0 0 20px rgba(0,0,0,0.35);
    margin-bottom:20px;
}

/* HERO */

.hero{
    background:
    linear-gradient(
        rgba(0,0,0,0.55),
        rgba(0,0,0,0.55)
    ),
    url("https://images.unsplash.com/photo-1584515933487-779824d29309");

    background-size:cover;
    background-position:center;

    border-radius:22px;

    padding:90px 60px;

    margin-bottom:30px;
}

.hero h1{
    color:white !important;
    font-size:44px !important;
}

.hero p{
    color:#f1f5f9 !important;
    font-size:18px;
}

/* BUTTON */

.stButton > button{

    background:#0ea5e9;

    color:white !important;

    border:none;

    border-radius:10px;

    font-weight:700;
}

.stButton > button:hover{

    background:#0284c7;

    color:white !important;
}

/* METRIC */

[data-testid="stMetric"]{

    background:rgba(7,25,43,0.9);

    border-radius:14px;

    padding:18px;

    border-top:4px solid #0ea5e9;

    box-shadow:0 0 15px rgba(0,0,0,0.35);
}

[data-testid="stMetric"] *{
    color:white !important;
}

/* INPUTS */

input, textarea, select{
    background:#07192b !important;
    color:white !important;
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
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.4, 1])

    with col2:

        st.markdown(
            '<div class="login-box">',
            unsafe_allow_html=True
        )

        st.title("Connexion au système PCCT")

        st.subheader(
            "PROMAMEC Intelligent System"
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

    page_login()

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

        nom TEXT,
        prenom TEXT,
        cin TEXT,

        sexe TEXT,

        age INTEGER,

        poids REAL,
        taille REAL,

        imc REAL,
        dose REAL,
        snr REAL,

        examen TEXT,
        protocole TEXT,

        scanner TEXT,

        date TEXT
    )

    """)

    conn.commit()
    conn.close()

init_db()

# =========================================================
# SCANNERS
# =========================================================

SCANNERS = {

    "NS-PCCT-2026-001":{

        "nom":"Scanner PCCT-01",
        "marque":"Neusoft",
        "modele":"NeuViz Glory"
    },

    "NS-PCCT-2026-002":{

        "nom":"Scanner PCCT-02",
        "marque":"Neusoft",
        "modele":"NeuViz Prime"
    },

    "NS-PCCT-2026-003":{

        "nom":"Scanner PCCT-03",
        "marque":"Neusoft",
        "modele":"NeuViz Epoch"
    }
}

# =========================================================
# CALCULS
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

# =========================================================
# SIDEBAR
# =========================================================


st.sidebar.title(
    "PCCT Intelligent System"
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

if st.session_state.role == "Technicien de radiologie":

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

    <div class="hero">

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
        qualité image
        et aide décisionnelle.

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

        examen = st.selectbox(
            "Type examen",
            [
                "Scanner cérébral",
                "Scanner thoracique",
                "Scanner abdominal",
                "Scanner cardiaque"
            ]
        )

        protocole = st.selectbox(
            "Protocole",
            [
                "Standard",
                "Low Dose",
                "Pédiatrique"
            ]
        )

        numero_serie = st.text_input(
            "Numéro série scanner"
        )

    if numero_serie in SCANNERS:

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
            "N° série",
            numero_serie
        )

    elif numero_serie != "":

        st.error(
            "Scanner non reconnu"
        )

    if st.button("Lancer acquisition IA"):

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

        r1,r2,r3 = st.columns(3)

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
# MAINTENANCE PREVENTIVE
# =========================================================

elif menu == "Maintenance préventive":

    st.title(
        "Maintenance préventive"
    )

    data = [

        ["PCCT-01","Stable",65,45],
        ["PCCT-02","À surveiller",48,68],
        ["PCCT-03","Critique",38,86]
    ]

    df = pd.DataFrame(

        data,

        columns=[
            "Scanner",
            "État",
            "SNR",
            "Température"
        ]
    )

    st.dataframe(
        df,
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

        if numero_serie == "NS-PCCT-2026-001":

            snr = 65
            temp = 45
            vib = 15
            bruit = 18
            etat = "🟢 Stable"

        elif numero_serie == "NS-PCCT-2026-002":

            snr = 48
            temp = 68
            vib = 42
            bruit = 45
            etat = "🟠 À surveiller"

        else:

            snr = 38
            temp = 86
            vib = 75
            bruit = 70
            etat = "🔴 Critique"

        c1,c2,c3,c4 = st.columns(4)

        c1.metric(
            "SNR système",
            snr
        )

        c2.metric(
            "Température",
            f"{temp} °C"
        )

        c3.metric(
            "Vibration",
            f"{vib} %"
        )

        c4.metric(
            "Bruit image",
            f"{bruit} %"
        )

        st.success(
            f"État global : {etat}"
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
