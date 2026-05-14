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

DB_NAME = "pcct_promamec_v2.db"

# =========================================================
# STYLE PROMAMEC
# =========================================================

st.markdown("""
<style>

.stApp{
    background:
    linear-gradient(
        135deg,
        #ffffff 0%,
        #f4fbf7 45%,
        #e6f5ee 100%
    );
}

[data-testid="stSidebar"]{
    background:
    linear-gradient(
        180deg,
        #0b7f5c,
        #0f9f72,
        #7fc8a9
    );
}

[data-testid="stSidebar"] *{
    color:white !important;
}

h1,h2,h3,h4{
    color:#0b7f5c !important;
}

p,label,span,div{
    color:#12352f;
}

.card{
    background:white;
    padding:24px;
    border-radius:20px;
    border:1px solid #d4eee3;
    box-shadow:
    0 6px 20px rgba(11,127,92,0.12);
    margin-bottom:18px;
}

.soft-card{
    background:
    linear-gradient(
        135deg,
        #ffffff,
        #eef9f3
    );

    padding:22px;
    border-radius:20px;
    border:1px solid #d4eee3;
    box-shadow:
    0 4px 16px rgba(11,127,92,0.10);
}

.stButton>button{

    background:#0b7f5c;
    color:white;
    border:none;
    border-radius:12px;
    font-weight:bold;
    padding:0.6rem 1rem;
}

.stButton>button:hover{

    background:#096b4e;
    color:white;
}

[data-testid="stMetric"]{

    background:white;
    padding:14px;
    border-radius:16px;
    border-left:5px solid #0b7f5c;

    box-shadow:
    0 3px 14px rgba(11,127,92,0.10);
}

[data-testid="stMetric"] *{
    color:#12352f !important;
}

input, textarea{
    color:#12352f !important;
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

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        st.markdown(
            '<div class="card">',
            unsafe_allow_html=True
        )

        if os.path.exists("imagespromamec.png"):

            st.image(
                "imagespromamec.png",
                width=260
            )

        st.title("PCCT Intelligent System")

        st.subheader("Connexion sécurisée")

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
        "modele":"NeuViz Glory PCCT",
        "numero_serie":"NS-PCCT-2026-001",
        "localisation":"Radiologie"
    },

    "NS-PCCT-2026-002": {

        "nom":"Scanner PCCT-02",
        "marque":"Neusoft",
        "modele":"NeuViz Prime",
        "numero_serie":"NS-PCCT-2026-002",
        "localisation":"Urgences"
    },

    "NS-PCCT-2026-003": {

        "nom":"Scanner PCCT-03",
        "marque":"Neusoft",
        "modele":"NeuViz Epoch",
        "numero_serie":"NS-PCCT-2026-003",
        "localisation":"Cardiologie"
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

    else:
        return "Obésité"

def dose_adaptee(age, imc):

    dose = (
        12
        + (imc * 0.25)
        + (age * 0.03)
    )

    return round(dose,2)

def calcul_snr(age, imc, dose):

    snr = (
        60
        - (0.30 * imc)
        - (0.05 * age)
        + (0.70 * dose)
    )

    return round(max(snr,10),2)

def qualite_image(snr):

    if snr >= 70:
        return "Excellente"

    elif snr >= 55:
        return "Bonne"

    elif snr >= 50:
        return "Acceptable"

    else:
        return "Insuffisante"

# =========================================================
# MAINTENANCE
# =========================================================

def generer_parametres_scanner(numero_serie):

    if numero_serie == "NS-PCCT-2026-001":

        return (
            65,
            45,
            15,
            18,
            8500,
            "Stable",
            "Normal"
        )

    elif numero_serie == "NS-PCCT-2026-002":

        return (
            48,
            68,
            42,
            45,
            22000,
            "Légère dégradation",
            "À surveiller"
        )

    else:

        return (
            38,
            86,
            75,
            70,
            36000,
            "Dégradation importante",
            "Défaillant"
        )

def analyser_maintenance(numero_serie):

    scanner = SCANNERS[numero_serie]

    (
        snr,
        temp,
        vibration,
        bruit,
        heures,
        detecteurs,
        refroidissement
    ) = generer_parametres_scanner(numero_serie)

    score = 0

    score += max(0,50-snr)*1.3
    score += max(0,temp-60)*1.2
    score += vibration*0.5
    score += bruit*0.4
    score += heures*0.001

    if detecteurs == "Légère dégradation":
        score += 15

    elif detecteurs == "Dégradation importante":
        score += 35

    if refroidissement == "À surveiller":
        score += 15

    elif refroidissement == "Défaillant":
        score += 35

    score = round(min(score,100),2)

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

    if temp > 75:

        composant = "Tube RX"
        cause = "Température élevée"
        action = "Contrôle refroidissement"

    elif vibration > 60:

        composant = "Gantry"
        cause = "Vibrations mécaniques élevées"
        action = "Contrôle mécanique"

    elif snr < 45:

        composant = "Détecteurs"
        cause = "Baisse SNR"
        action = "Calibration détecteurs"

    return {

        "scanner":scanner["nom"],
        "marque":scanner["marque"],
        "modele":scanner["modele"],
        "numero_serie":scanner["numero_serie"],

        "snr_systeme":snr,
        "temperature":temp,
        "vibration":vibration,
        "bruit":bruit,
        "heures":heures,

        "detecteurs":detecteurs,
        "refroidissement":refroidissement,

        "score":score,
        "etat":etat,
        "couleur":couleur,

        "composant":composant,
        "cause":cause,
        "action":action
    }

# =========================================================
# SIDEBAR
# =========================================================

if os.path.exists("imagespromamec.png"):

    st.sidebar.image(
        "imagespromamec.png",
        width=180
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
        "SNR",
        "Dashboard"
    ]

else:

    pages = [

        "Accueil",
        "Maintenance préventive",
        "Maintenance",
        "Dashboard",
        "Logs système"
    ]

menu = st.sidebar.radio(
    "Navigation",
    pages
)

# =========================================================
# ACCUEIL
# =========================================================

if menu == "Accueil":

    st.title(
        "PROMAMEC PCCT Intelligent System"
    )

    st.markdown("""

    <div class="card">

    <h3>
    Objectif de l’application
    </h3>

    <p>

    Cette application permet :

    • optimisation intelligente de dose

    • estimation qualité image via SNR

    • surveillance biomédicale des scanners

    • maintenance prédictive

    • aide décisionnelle IA

    </p>

    </div>

    """, unsafe_allow_html=True)

    st.markdown("""

    <div class="soft-card">

    <h3>
    Présentation de PROMAMEC
    </h3>

    <p>

    PROMAMEC est une entreprise spécialisée
    dans les équipements biomédicaux,
    l’installation et la maintenance des
    dispositifs médicaux.

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
            sc["numero_serie"]
        )

    elif numero_serie != "":

        st.error(
            "Scanner non reconnu"
        )

    if st.button(
        "Lancer acquisition"
    ):

        if (
            nom == ""
            or prenom == ""
            or cin == ""
            or age <= 0
            or poids <= 0
            or taille <= 0
            or numero_serie not in SCANNERS
        ):

            st.error(
                "Veuillez compléter toutes les informations."
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
                "Génération résultats..."
            ]

            for i, txt in enumerate(etapes):

                status.info(txt)

                progress.progress(
                    int((i+1)/len(etapes)*100)
                )

            imc = calcul_imc(
                poids,
                taille
            )

            dose = dose_adaptee(
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
                "Qualité",
                qualite
            )

# =========================================================
# SNR
# =========================================================

elif menu == "SNR":

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

    rows = []

    for serial in SCANNERS:

        m = analyser_maintenance(serial)

        rows.append({

            "Scanner":m["scanner"],
            "Marque":m["marque"],
            "N° série":m["numero_serie"],
            "État":m["etat"],
            "Score":m["score"],
            "Composant":m["composant"]
        })

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True
    )

# =========================================================
# MAINTENANCE
# =========================================================

elif menu == "Maintenance":

    st.title(
        "Maintenance intelligente"
    )

    numero_serie = st.text_input(
        "Entrer le numéro de série du scanner"
    )

    if numero_serie == "":

        st.info(
            "Veuillez entrer un numéro de série."
        )

        a1,a2,a3,a4 = st.columns(4)

        a1.text_input(
            "SNR système",
            value="",
            disabled=True
        )

        a2.text_input(
            "Température",
            value="",
            disabled=True
        )

        a3.text_input(
            "Vibration",
            value="",
            disabled=True
        )

        a4.text_input(
            "Bruit",
            value="",
            disabled=True
        )

    elif numero_serie not in SCANNERS:

        st.error(
            "Scanner non reconnu."
        )

    else:

        m = analyser_maintenance(
            numero_serie
        )

        st.success(
            "Scanner reconnu."
        )

        c1,c2,c3 = st.columns(3)

        c1.metric(
            "Marque",
            m["marque"]
        )

        c2.metric(
            "Modèle",
            m["modele"]
        )

        c3.metric(
            "N° série",
            m["numero_serie"]
        )

        st.markdown(
            "### Paramètres techniques"
        )

        a1,a2,a3,a4 = st.columns(4)

        a1.text_input(
            "SNR système",
            value=str(m["snr_systeme"]),
            disabled=True
        )

        a2.text_input(
            "Température",
            value=f"{m['temperature']} °C",
            disabled=True
        )

        a3.text_input(
            "Vibration",
            value=f"{m['vibration']} %",
            disabled=True
        )

        a4.text_input(
            "Bruit",
            value=f"{m['bruit']} %",
            disabled=True
        )

        st.markdown(
            "### Diagnostic IA"
        )

        d1,d2,d3 = st.columns(3)

        d1.metric(
            "Score stress",
            f"{m['score']} %"
        )

        d2.metric(
            "État",
            f"{m['couleur']} {m['etat']}"
        )

        d3.metric(
            "Composant suspect",
            m["composant"]
        )

        st.write(
            f"Cause probable : {m['cause']}"
        )

        st.write(
            f"Action recommandée : {m['action']}"
        )

        dfm = pd.DataFrame({

            "Paramètre":[

                "SNR",
                "Température",
                "Vibration",
                "Bruit",
                "Score"
            ],

            "Valeur":[

                m["snr_systeme"],
                m["temperature"],
                m["vibration"],
                m["bruit"],
                m["score"]
            ]
        })

        st.bar_chart(
            dfm.set_index("Paramètre")
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
        ],

        "État":[
            "Stable",
            "À surveiller",
            "Critique"
        ]
    }

    df = pd.DataFrame(data)

    st.dataframe(
        df,
        use_container_width=True
    )

    st.bar_chart(
        df.set_index("Scanner")["SNR"]
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

        <div class="soft-card">

        {log}

        </div>

        """, unsafe_allow_html=True)
