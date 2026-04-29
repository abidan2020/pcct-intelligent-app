import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="PCCT Intelligent System",
    page_icon="🧠",
    layout="wide"
)

# =========================
# STYLE
# =========================
st.markdown("""
<style>
.main-title {
    font-size: 38px;
    font-weight: 800;
    color: #1f4e79;
}
.subtitle {
    font-size: 18px;
    color: #555;
}
.section-box {
    background-color: #ffffff;
    padding: 22px;
    border-radius: 14px;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown("<div class='main-title'>🧠 PCCT Intelligent Monitoring System</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>Simulation d’un système embarqué pour optimisation de dose, qualité image et maintenance préventive</div>",
    unsafe_allow_html=True
)

st.divider()

# =========================
# FUNCTIONS
# =========================
def safe_float(value, default):
    try:
        return float(value)
    except:
        return default

# =========================
# SIDEBAR INPUTS
# =========================
st.sidebar.title("🧾 Entrées technicien")

st.sidebar.subheader("Données patient")
age = safe_float(st.sidebar.text_input("Âge", "45"), 45)
sexe = st.sidebar.selectbox("Sexe", ["Femme", "Homme"])
poids = safe_float(st.sidebar.text_input("Poids (kg)", "70"), 70)
taille_cm = safe_float(st.sidebar.text_input("Taille (cm)", "170"), 170)

st.sidebar.subheader("Paramètres scanner")
mas = safe_float(st.sidebar.text_input("mAs", "80"), 80)
kvp = st.sidebar.selectbox("kVp", [80, 100, 120, 140])
artefacts = st.sidebar.selectbox("Artefacts visibles ?", ["Non", "Oui"])

analyse = st.sidebar.button("🚀 Lancer l’analyse")

if not analyse:
    st.info("Saisis les données dans le panneau latéral puis clique sur **Lancer l’analyse**.")
    st.stop()

# =========================
# CALCULATIONS
# =========================
artefacts_num = 1 if artefacts == "Oui" else 0

taille_m = taille_cm / 100
imc = poids / (taille_m ** 2) if taille_m > 0 else 0

if imc < 20:
    imc_classe = "Maigre / faible corpulence"
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

facteur_mas = (mas / 80) ** 0.5
facteur_kvp = 0.95 + 0.05 * (kvp / 120)

penalite_imc = max(0, (imc - 25) * 0.45)
penalite_artefacts = 6 if artefacts == "Oui" else 0
penalite_age = max(0, (age - 60) * 0.03)

snr = snr_initial * facteur_mas * facteur_kvp
snr = snr - penalite_imc - penalite_artefacts - penalite_age
snr = max(20, min(snr, 80))

delta_snr = snr - snr_initial
dose_snr_ratio = mas / snr if snr != 0 else 0

snr_norm = min(max((snr - 35) / 35, 0), 1)
imc_norm = min(max((imc - 18) / 22, 0), 1)
mas_norm = min(max((mas - 20) / 180, 0), 1)

stress_score = (
    0.4 * (1 - snr_norm) +
    0.3 * imc_norm +
    0.2 * mas_norm +
    0.1 * artefacts_num
)

health_index = max(0, min((1 - stress_score) * 100, 100))

# =========================
# DECISION LOGIC
# =========================
if snr >= 60:
    etat = "Stable"
    decision = "Conserver ou réduire la dose"
    recommandation = "Qualité image suffisante. Une légère réduction de dose est possible."
    color = "success"
elif snr >= 45:
    etat = "Dégradé"
    decision = "Recalibration avant ajustement"
    recommandation = "Recalibration recommandée avant toute augmentation de dose."
    color = "warning"
elif snr < 45 and stress_score >= 0.6:
    etat = "Critique"
    decision = "Maintenance prioritaire"
    recommandation = "Ne pas augmenter la dose. Intervention technique prioritaire recommandée."
    color = "error"
else:
    etat = "Surveillance"
    decision = "Ajustement léger mAs"
    recommandation = "Ajustement léger du mAs possible sous surveillance."
    color = "info"

if decision == "Conserver ou réduire la dose":
    mas_corrige = mas * 0.95
elif decision == "Ajustement léger mAs":
    mas_corrige = mas * 1.05
else:
    mas_corrige = mas

if mas_corrige < mas:
    impact_dose = "Dose réduite"
elif mas_corrige > mas:
    impact_dose = "Dose légèrement augmentée"
else:
    impact_dose = "Dose maintenue"

if health_index >= 70:
    risque = "Faible"
elif health_index >= 40:
    risque = "Modéré"
else:
    risque = "Élevé"

# =========================
# DASHBOARD
# =========================
st.subheader("📌 Tableau de bord principal")

k1, k2, k3, k4 = st.columns(4)
k1.metric("IMC", round(imc, 2), imc_classe)
k2.metric("SNR estimé", round(snr, 2))
k3.metric("Delta SNR", round(delta_snr, 2))
k4.metric("Stress score", round(stress_score, 2))

st.divider()

left, middle, right = st.columns([1.1, 1.1, 1])

with left:
    st.subheader("🔍 État du système")
    if color == "success":
        st.success(f"🟢 {etat}")
    elif color == "warning":
        st.warning(f"🟡 {etat}")
    elif color == "error":
        st.error(f"🔴 {etat}")
    else:
        st.info(f"🟠 {etat}")

    st.markdown("### ⚙️ Décision")
    st.write(decision)

    st.markdown("### 🚨 Recommandation opérateur")
    st.write(recommandation)

with middle:
    st.subheader("💚 Health Index")
    st.progress(int(health_index))
    st.metric("Indice santé", f"{round(health_index, 2)} %")
    st.metric("Risque de panne", risque)

    st.markdown("### 💉 Impact dose")
    st.write(impact_dose)

with right:
    st.subheader("📊 Paramètres dose")
    st.metric("mAs initial", round(mas, 2))
    st.metric("mAs corrigé", round(mas_corrige, 2))
    st.metric("Dose/SNR ratio", round(dose_snr_ratio, 2))
    st.metric("SNR initial", round(snr_initial, 2))

st.divider()

# =========================
# GRAPH
# =========================
st.subheader("📈 Visualisation qualité image")

fig, ax = plt.subplots(figsize=(8, 4))
bars = ax.bar(["SNR initial", "SNR estimé"], [snr_initial, snr])
ax.axhline(45, linestyle="--", label="Seuil critique SNR = 45")
ax.axhline(60, linestyle="--", label="Seuil qualité correcte SNR = 60")
ax.set_ylabel("SNR")
ax.set_title("Comparaison SNR initial / SNR estimé")
ax.legend()
st.pyplot(fig)

# =========================
# SUMMARY
# =========================
st.subheader("📋 Résumé clinique du cas")

resume = {
    "Âge": age,
    "Sexe": sexe,
    "Poids (kg)": poids,
    "Taille (cm)": taille_cm,
    "IMC": round(imc, 2),
    "Classe IMC": imc_classe,
    "kVp": kvp,
    "mAs initial": round(mas, 2),
    "mAs corrigé": round(mas_corrige, 2),
    "Artefacts": artefacts,
    "SNR initial": round(snr_initial, 2),
    "SNR estimé": round(snr, 2),
    "Delta SNR": round(delta_snr, 2),
    "Stress score": round(stress_score, 2),
    "Health Index": round(health_index, 2),
    "Risque de panne": risque,
    "État système": etat,
    "Décision": decision,
    "Impact dose": impact_dose,
    "Recommandation": recommandation
}

st.dataframe([resume], use_container_width=True)
