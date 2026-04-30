import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import base64
import os

st.set_page_config(page_title="PCCT Intelligent System", layout="wide")

# =========================
# BACKGROUND BASE64
# =========================
def get_base64_image(path):
    if not os.path.exists(path):
        st.error(f"Image introuvable : {path}")
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
            linear-gradient(rgba(0,0,0,0.65), rgba(0,0,0,0.85)),
            url("data:image/jpg;base64,{img}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """, unsafe_allow_html=True)

# =========================
# STYLE
# =========================
st.markdown("""
<style>
[data-testid="stSidebar"] {background:#04111f;}
[data-testid="stSidebar"] * {color:white;}

.card {
    background: rgba(5,20,35,0.8);
    padding:20px;
    border-radius:15px;
    margin-bottom:15px;
}

.stButton>button {
    background:#0ea5e9;
    color:white;
    border-radius:10px;
}

[data-testid="stMetric"] {
    background: rgba(5,20,35,0.8);
    padding:10px;
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# CALCULS
# =========================
def imc(p,t):
    return p/((t/100)**2)

def dose(age,imc):
    return round(4.5 + 0.08*imc + 0.015*age,2)

def snr(age,imc,d):
    return round(max(70 - 0.35*imc - 0.08*age + 1.8*d,10),2)

# =========================
# MENU
# =========================
menu = st.sidebar.radio("Menu",[
    "Accueil","Technicien","SNR","Suivi","Maintenance","Rapport"
])

# =========================
# ACCUEIL
# =========================
if menu=="Accueil":
    set_bg("images/accueil.jpg")

    st.title("PCCT Intelligent System")
    st.write("Optimisation dose + suivi scanner")

# =========================
# TECHNICIEN
# =========================
elif menu=="Technicien":
    set_bg("images/technicien.jpg")

    st.title("Espace Technicien")

    col1,col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">',unsafe_allow_html=True)

        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        cin = st.text_input("CIN")

        age = st.number_input("Age",1,120,45)
        poids = st.number_input("Poids",20.0,200.0,70.0)
        taille = st.number_input("Taille",100.0,220.0,170.0)

        st.markdown('</div>',unsafe_allow_html=True)

    i = imc(poids,taille)
    d = dose(age,i)
    s = snr(age,i,d)

    with col2:
        st.metric("IMC",round(i,2))
        st.metric("Dose",d)
        st.metric("SNR",s)

# =========================
# SNR
# =========================
elif menu=="SNR":
    set_bg("images/snr.jpg")

    st.title("Analyse SNR")

    imc_v = st.slider("IMC",15,45,25)
    age_v = st.slider("Age",10,90,40)

    doses = np.linspace(3,12,20)
    snrs = [snr(age_v,imc_v,x) for x in doses]

    df = pd.DataFrame({"Dose":doses,"SNR":snrs})
    st.line_chart(df.set_index("Dose"))

# =========================
# SUIVI
# =========================
elif menu=="Suivi":
    set_bg("images/suivi.jpg")

    st.title("Suivi Scanner")

    snr_m = st.number_input("SNR",10.0,100.0,52.0)
    temp = st.number_input("Température",20.0,120.0,60.0)

    if snr_m>50 and temp<75:
        st.success("Bon état")
    else:
        st.warning("A surveiller")

# =========================
# MAINTENANCE
# =========================
elif menu=="Maintenance":
    set_bg("images/maintenance.jpg")

    st.title("Maintenance prédictive")
    st.warning("Analyse en cours...")

# =========================
# RAPPORT
# =========================
elif menu=="Rapport":
    set_bg("images/rapport.jpg")

    st.title("Rapport")

    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    cin = st.text_input("CIN")

    age = st.number_input("Age",1,120,45)
    poids = st.number_input("Poids",20.0,200.0,70.0)
    taille = st.number_input("Taille",100.0,220.0,170.0)

    i = imc(poids,taille)
    d = dose(age,i)
    s = snr(age,i,d)

    txt = f"""
Nom: {nom}
Prenom: {prenom}
CIN: {cin}

IMC: {i:.2f}
Dose: {d}
SNR: {s}

Date: {datetime.now()}
"""

    st.text_area("Rapport",txt)

    st.download_button("Télécharger",txt,file_name="rapport.txt")
