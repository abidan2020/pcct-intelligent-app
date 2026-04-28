import streamlit as st
import pandas as pd

st.set_page_config(page_title="PCCT Intelligent", layout="centered")

st.title("🧠 Système embarqué intelligent - PCCT")
st.write("Simulation temps réel pour optimisation de dose et maintenance préventive")

df = pd.read_excel("dataset_FINAL_CORRIGE.xlsx")

index = st.slider("Choisir un patient / cycle", 0, len(df)-1, 0)
ligne = df.iloc[index]

snr = ligne["SNR"]
delta = ligne["Delta_SNR"]
stress = ligne["Stress_score"]
decision = ligne["Decision_dose_min_v2"]

st.subheader("📡 Capteurs virtuels")
col1, col2, col3 = st.columns(3)
col1.metric("SNR", round(snr, 2))
col2.metric("Delta SNR", round(delta, 2))
col3.metric("Stress score", round(stress, 2))

st.subheader("🔍 Analyse embarquée")

if decision == "Conserver ou réduire la dose":
    st.success("🟢 Etat : Stable")
elif decision == "Recalibration avant ajustement":
    st.warning("🟡 Etat : Dégradé")
elif decision == "Ajustement léger mAs si nécessaire":
    st.info("🟠 Etat : Surveillance")
else:
    st.error("🔴 Etat : Critique")

st.subheader("⚙️ Décision du système")
st.write(decision)

st.subheader("📊 Données du cycle sélectionné")
st.dataframe(ligne.to_frame().T)
