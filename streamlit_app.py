import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="PCCT Intelligent", layout="wide")

st.title("🧠 Système embarqué intelligent - PCCT")
st.write("Optimisation intelligente de dose + maintenance prédictive")

# ---------------------------
# Fonction sécurisée
# ---------------------------
def safe_float(value, default):
    try:
        return float(value)
    except:
        return default

# ---------------------------
# Interface 2 colonnes
# ---------------------------
col1, col2 = st.columns(2)

# ---------------------------
# Entrées technicien
# ---------------------------
with col1:
    st.subheader("🧾 Données patient")

    age = safe_float(st.text_input("Âge", "45"), 45)
    sexe = st.selectbox("Sexe", ["F", "M"])
    poids = safe_float(st.text_input("Poids (kg)", "70"), 70)
    taille_cm = safe_float(st.text_input("Taille (cm)", "170"), 170)

    st.subheader("⚙️ Acquisition")

    mas = safe_float(st.text_input("mAs", "80"), 80)
    kvp = st.selectbox("kVp", [80, 100, 120, 140])
    artefacts = st.selectbox("Artefacts", ["Non", "Oui"])

# ---------------------------
# Bouton calcul
# ---------------------------
calculer = st.button("🔍 Calculer")

# ---------------------------
# Calcul seulement si bouton cliqué
# ---------------------------
if calculer:

    artefacts_num = 1 if artefacts == "Oui" else 0
    taille_m = taille_cm / 100
    imc = poids / (taille_m ** 2) if taille_m > 0 else 0

    # Classe IMC
    if imc < 20:
        snr_initial = 65.68
    elif imc < 25:
        snr_initial = 60.48
    elif imc < 30:
        snr_initial = 61.02
    else:
        snr_initial = 59.03

    # SNR estimé
    snr = snr_initial * (mas / 80)**0.5 * (kvp / 120)
    snr -= max(0, (imc - 25) * 0.4)
    snr -= 5 if artefacts == "Oui" else 0
    snr = max(20, min(snr, 80))

    delta_snr = snr - snr_initial

    # Normalisation
    snr_norm = min(max((snr - 35) / 35, 0), 1)
    imc_norm = min(max((imc - 18) / 22, 0), 1)
    mas_norm = min(max((mas - 20) / 180, 0), 1)

    # Stress score
    stress = (
        0.4 * (1 - snr_norm) +
        0.3 * imc_norm +
        0.2 * mas_norm +
        0.1 * artefacts_num
    )

    # Health index (NOUVEAU 🔥)
    health_index = (1 - stress) * 100

    # Décision
    if snr >= 60:
        decision = "Conserver ou réduire la dose"
    elif snr >= 45:
        decision = "Recalibration avant ajustement"
    elif stress > 0.6:
        decision = "Maintenance prioritaire"
    else:
        decision = "Ajustement léger mAs"

    # ---------------------------
    # Affichage
    # ---------------------------
    with col2:
        st.subheader("📊 Résultats")

        st.metric("IMC", round(imc, 2))
        st.metric("SNR estimé", round(snr, 2))
        st.metric("Delta SNR", round(delta_snr, 2))
        st.metric("Stress score", round(stress, 2))

        # Health index 🔥
        st.subheader("💚 Health Index")
        st.progress(int(health_index))
        st.write(f"{round(health_index,2)} %")

        # Etat
        if health_index > 70:
            st.success("🟢 Système sain")
        elif health_index > 40:
            st.warning("🟡 Surveillance")
        else:
            st.error("🔴 Système critique")

        # Décision
        st.subheader("⚙️ Décision")
        st.write(decision)

        # ---------------------------
        # Graphique SNR 🔥
        # ---------------------------
        st.subheader("📈 Analyse SNR")

        x = np.linspace(0, 100, 100)
        y = x

        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.axvline(snr, linestyle="--")
        ax.set_title("Position du SNR")
        ax.set_xlabel("Qualité image")
        ax.set_ylabel("SNR")

        st.pyplot(fig)
