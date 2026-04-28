import streamlit as st

st.set_page_config(page_title="PCCT Intelligent", layout="centered")

st.title("🧠 Système embarqué intelligent - PCCT")
st.write("Simulation temps réel pour optimisation de dose et maintenance préventive")

# ---------------------------
# Fonction sécurisée
# ---------------------------
def safe_float(value, default):
    try:
        return float(value)
    except:
        return default

# ---------------------------
# Entrée technicien (clavier)
# ---------------------------
st.subheader("🧾 Données patient (saisie clavier)")

age = safe_float(st.text_input("Âge", "45"), 45)
sexe = st.selectbox("Sexe", ["F", "M"])
poids = safe_float(st.text_input("Poids (kg)", "70"), 70)
taille_cm = safe_float(st.text_input("Taille (cm)", "170"), 170)

st.subheader("⚙️ Paramètres d’acquisition")

mas = safe_float(st.text_input("mAs", "80"), 80)
kvp = st.selectbox("kVp", [80, 100, 120, 140])
artefacts = st.selectbox("Artefacts présents ?", ["Non", "Oui"])
artefacts_num = 1 if artefacts == "Oui" else 0

# ---------------------------
# Calcul IMC
# ---------------------------
taille_m = taille_cm / 100
imc = poids / (taille_m ** 2) if taille_m > 0 else 0

# ---------------------------
# Classe IMC + SNR initial
# ---------------------------
if imc < 20:
    imc_classe = "<20"
    snr_initial = 65.68
elif imc < 25:
    imc_classe = "20-25"
    snr_initial = 60.48
elif imc < 30:
    imc_classe = "25-30"
    snr_initial = 61.02
else:
    imc_classe = ">30"
    snr_initial = 59.03

# ---------------------------
# SNR estimé (simulation)
# ---------------------------
facteur_mas = (mas / 80) ** 0.5
facteur_kvp = kvp / 120

penalite_imc = max(0, (imc - 25) * 0.45)
penalite_artefacts = 6 if artefacts == "Oui" else 0
penalite_age = max(0, (age - 60) * 0.03)

snr = snr_initial * facteur_mas * (0.95 + 0.05 * facteur_kvp)
snr = snr - penalite_imc - penalite_artefacts - penalite_age
snr = max(20, min(snr, 80))

# ---------------------------
# Indicateurs
# ---------------------------
delta_snr = snr - snr_initial
dose_snr_ratio = mas / snr if snr != 0 else 0

snr_norm = min(max((snr - 35) / (70 - 35), 0), 1)
imc_norm = min(max((imc - 18) / (40 - 18), 0), 1)
mas_norm = min(max((mas - 20) / (200 - 20), 0), 1)

stress_score = (
    0.4 * (1 - snr_norm) +
    0.3 * imc_norm +
    0.2 * mas_norm +
    0.1 * artefacts_num
)

# ---------------------------
# Décision
# ---------------------------
if snr >= 60:
    decision = "Conserver ou réduire la dose"
elif snr >= 50 and delta_snr >= -5 and stress_score < 0.5:
    decision = "Conserver ou réduire la dose"
elif snr >= 45:
    decision = "Recalibration avant ajustement"
elif snr < 45 and stress_score >= 0.6:
    decision = "Maintenance prioritaire (pas augmentation dose)"
else:
    decision = "Ajustement léger mAs si nécessaire"

# ---------------------------
# Correction dose
# ---------------------------
if decision == "Conserver ou réduire la dose":
    mas_corrige = mas * 0.95
elif decision == "Ajustement léger mAs si nécessaire":
    mas_corrige = mas * 1.05
else:
    mas_corrige = mas

if mas_corrige < mas:
    impact_dose = "Dose réduite"
elif mas_corrige == mas:
    impact_dose = "Dose maintenue"
else:
    impact_dose = "Dose légèrement augmentée"

# ---------------------------
# Etat système
# ---------------------------
if decision == "Conserver ou réduire la dose":
    etat = "🟢 Stable"
elif decision == "Recalibration avant ajustement":
    etat = "🟡 Dégradé"
elif decision == "Ajustement léger mAs si nécessaire":
    etat = "🟠 Surveillance"
else:
    etat = "🔴 Critique"

# ---------------------------
# Affichage
# ---------------------------
st.subheader("📊 Résultats calculés automatiquement")

col1, col2, col3 = st.columns(3)
col1.metric("IMC", round(imc, 2))
col2.metric("Classe IMC", imc_classe)
col3.metric("SNR estimé", round(snr, 2))

col4, col5, col6 = st.columns(3)
col4.metric("SNR initial", round(snr_initial, 2))
col5.metric("Delta SNR", round(delta_snr, 2))
col6.metric("Stress score", round(stress_score, 2))

col7, col8 = st.columns(2)
col7.metric("Dose/SNR ratio", round(dose_snr_ratio, 2))
col8.metric("mAs corrigé", round(mas_corrige, 2))

st.subheader("🔍 Analyse embarquée")

if "Stable" in etat:
    st.success(etat)
elif "Dégradé" in etat:
    st.warning(etat)
elif "Surveillance" in etat:
    st.info(etat)
else:
    st.error(etat)

st.subheader("⚙️ Décision du système")
st.write(decision)

st.subheader("💉 Impact sur la dose")
st.write(impact_dose)

st.subheader("🚨 Alerte")

if "Maintenance" in decision:
    st.error("⚠️ Maintenance prioritaire requise")
elif "Recalibration" in decision:
    st.warning("⚠️ Recalibration recommandée")
elif "Ajustement" in decision:
    st.info("ℹ️ Ajustement léger possible")
else:
    st.success("✅ Système stable")
