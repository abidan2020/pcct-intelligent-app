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

LOGO_PATH = "imagespromamec.png"
DB_NAME = "pcct_promamec.db"

# =========================================================
# STYLE GLOBAL
# =========================================================

st.markdown("""
<style>

:root{
    --promamec:#00A99D;
    --promamec-dark:#00857C;
    --text:#1F2933;
    --bg:#F7FAFA;
    --border:#E5E7EB;
}

/* GENERAL */

.stApp{
    background:var(--bg);
}

/* SIDEBAR */

[data-testid="stSidebar"]{
    background:white;
    border-right:1px solid #E5E7EB;
}

[data-testid="stSidebar"] *{
    color:#1F2933 !important;
}

/* TITRES */

h1,h2,h3,h4{
    color:#1F2933 !important;
    font-weight:800 !important;
}

/* CARD */

.card{
    background:white;
    padding:25px;
    border-radius:14px;
    border:1px solid #E5E7EB;
    box-shadow:0 6px 20px rgba(0,0,0,0.06);
    margin-bottom:20px;
}

/* HERO */

.hero{
    background:
    linear-gradient(
        rgba(0,0,0,0.45),
        rgba(0,0,0,0.45)
    ),
    url("https://images.unsplash.com/photo-1584515933487-779824d29309");

    background-size:cover;
    background-position:center;

    border-radius:18px;

    padding:90px 60px;

    margin-bottom:30px;
}

.hero h1{
    color:white !important;
    font-size:42px !important;
}

.hero p{
    color:white !important;
    font-size:18px;
}

/* BUTTON */

.stButton > button{
    background:#00A99D;
    color:white !important;
    border:none;
    border-radius:6px;
    font-weight:700;
}

.stButton > button:hover{
    background:#00857C;
    color:white !important;
}

/* METRIC */

[data-testid="stMetric"]{
    background:white;
    border-radius:10px;
    padding:18px;
    border-top:4px solid #00A99D;
    box-shadow:0 4px 12px rgba(0,0,0,0.05);
}

[data-testid="stMetric"] *{
    color:#1F2933 !important;
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

    st.markdown("""
    <style>

    .login-container{
        display:flex;
        height:100vh;
        margin-top:-80px;
    }

    .left-login{
        flex:1.2;
        background:white;
        display:flex;
        justify-content:center;
        align-items:center;
        padding:60px;
    }

    .right-login{
        flex:0.5;
        background:#00A99D;
    }

    .login-card{
        width:100%;
        max-width:420px;
        background:white;
        padding:40px;
        border-radius:14px;
        box-shadow:0 8px 30px rgba(0,0,0,0.08);
    }

    .login-title{
        font-size:38px;
        font-weight:800;
        color:#1F2933;
        margin-top:20px;
        margin-bottom:5px;
    }

    .login-subtitle{
        color:#6B7280;
        margin-bottom:35px;
        font-size:16px;
    }

    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3,1])

    with col1:

        st.markdown('<div class="login-card">', unsafe_allow_html=True)

        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=230)

        st.markdown(
            '<div class="login-title">Connexion</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="login-subtitle">PROMAMEC PCCT Intelligent System</div>',
            unsafe_allow_html=True
        )

        nom = st.text_input("Nom utilisateur")

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

                st.error("Nom ou ID incorrect.")

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="
        background:#00A99D;
        height:100vh;
        border-radius:0px;">
        </div>
        """, unsafe_allow_html=True)

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

if os.path.exists(LOGO_PATH):

    st.sidebar.image(
        LOGO_PATH,
        width=180
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

    st.title("Workflow acquisition patient")

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

    st.title("Maintenance préventive")

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

    st.title("Maintenance scanner")

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

    st.title("Dashboard global")

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
