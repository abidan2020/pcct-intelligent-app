
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="PCCT Intelligent System",
    page_icon="🧠",
    layout="wide"
)

# =========================
# DARK MODE STYLE
# =========================
st.markdown("""
<style>

/* Fond général */
.stApp {
    background-color: #0e1117;
    color: white;
}

/* Texte */
html, body, [class*="css"] {
    color: white;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #161b22;
}

/* Metrics */
[data-testid="stMetric"] {
    background-color: #1c1f26;
    padding: 10px;
    border-radius: 10px;
}

/* Titres */
h1, h2, h3 {
    color: #00e5ff;
}

/* Séparateurs */
hr {
    border: 1px solid #2c2f36;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.title("🧠 PCCT Intelligent Monitoring System")
st.write("Optimisation de dose • Qualité image • Maintenance prédictive")

st.divider()

# =========================
# SAFE INPUT
# =========================
def safe_float(value, default):
    try:
        return float(value)
    except:
        return default

# =========================
# SIDEBAR
# =========================
st.sidebar.header("🧾 Données patient")

age = safe_float(st.sidebar.text_input("Âge", "45"), 45)
sexe = st.sidebar.selectbox("Sexe", ["Femme", "Homme"])
poids = safe_float(st.sidebar.text_input("Poids (kg)", "70"), 70)
taille_cm = safe_float(st.sidebar.text_input("Taille (cm)", "170"), 170)

st.sidebar.header("⚙️ Paramètres scanner")

mas = safe_float(st.sidebar.text_input("mAs", "80"), 80)
kvp = st.sidebar.selectbox("kVp", [80, 100, 120, 140])
artefacts = st.sidebar.selectbox("Artefacts ?", ["Non", "Oui"])

analyse = st.sidebar.button("🚀 Lancer l’analyse")

if not analyse:
    st.info("Remplis les données dans la sidebar puis clique sur **Lancer l’analyse**.")
    st.stop()

# =========================
# CALCUL
# =========================
artefacts_num = 1 if artefacts == "Oui" else 0

taille_m = taille_cm / 100
imc = poids / (taille_m ** 2) if taille_m > 0 else 0

if imc < 20:
    imc_classe = "Maigre"
    snr_initial = 65.68
elif imc < 25:
    imc_classe = "Normal"
    snr_initial = 60.48
elif imc < 30:
    imc_classe = "Surpoids"
    snr_initial = 61.02
else:
    imc_classe = "Obésité"
    snr_initial = 59.03

# SNR simulé
snr = snr_initial * (mas / 80)**0.5 * (kvp / 120)
snr -= max(0, (imc - 25) * 0.4)
snr -= 5 if artefacts == "Oui" else 0
snr = max(20, min(snr, 80))

delta_snr = snr - snr_initial
dose_snr_ratio = mas / snr if snr != 0 else 0

snr_norm = min(max((snr - 35) / 35, 0), 1)
imc_norm = min(max((imc - 18) / 22, 0), 1)
mas_norm = min(max((mas - 20) / 180, 0), 1)

stress = (
    0.4 * (1 - snr_norm) +
    0.3 * imc_norm +
    0.2 * mas_norm +
    0.1 * artefacts_num
)

health = (1 - stress) * 100

# =========================
# DECISION
# =========================
if snr >= 60:
    etat = "🟢 Stable"
    decision = "Conserver ou réduire la dose"
elif snr >= 45:
    etat = "🟡 Dégradé"
    decision = "Recalibration avant ajustement"
elif stress > 0.6:
    etat = "🔴 Critique"
    decision = "Maintenance prioritaire"
else:
    etat = "🟠 Surveillance"
    decision = "Ajustement léger mAs"

if decision == "Conserver ou réduire la dose":
    mas_corrige = mas * 0.95
elif decision == "Ajustement léger mAs":
    mas_corrige = mas * 1.05
else:
    mas_corrige = mas

# =========================
# DASHBOARD
# =========================
c1, c2, c3, c4 = st.columns(4)

c1.metric("IMC", round(imc, 2))
c2.metric("SNR estimé", round(snr, 2))
c3.metric("Delta SNR", round(delta_snr, 2))
c4.metric("Stress", round(stress, 2))

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("🔍 Analyse système")
    st.write(etat)

    st.subheader("⚙️ Décision")
    st.write(decision)

with right:
    st.subheader("💚 Health Index")
    st.progress(int(health))
    st.write(f"{round(health,2)} %")

    st.metric("mAs corrigé", round(mas_corrige, 2))

st.divider()

# =========================
# GRAPH
# =========================
st.subheader("📈 Analyse SNR")

fig, ax = plt.subplots()
ax.bar(["Initial", "Estimé"], [snr_initial, snr])
ax.axhline(45, linestyle="--")
ax.axhline(60, linestyle="--")

st.pyplot(fig)

# =========================
# RESUME
# =========================
st.subheader("📋 Résumé")

st.write({
    "IMC": round(imc,2),
    "SNR": round(snr,2),
    "Décision": decision
})
