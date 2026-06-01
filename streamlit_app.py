# =========================
# MAINTENANCE
# =========================
elif menu == "Maintenance":

    set_bg("maintenance.png")

    st.title("Maintenance prédictive du scanner PCCT")

    col1, col2 = st.columns(2)

    with col1:

        # =========================
        # SCANNERS ENREGISTRÉS
        # =========================

        df_scanners = charger_scanners()

        if df_scanners.empty:

            st.warning(
                "Aucun scanner enregistré. Ajoutez d'abord un scanner dans Gestion scanners."
            )

            st.stop()

        scanner = st.selectbox(
            "Scanner concerné",
            df_scanners["nom"].tolist()
        )

        scanner_info = df_scanners[
            df_scanners["nom"] == scanner
        ].iloc[0]

        st.info(
            f"Marque : {scanner_info['marque']} | "
            f"Modèle : {scanner_info['modele']} | "
            f"N° série : {scanner_info['numero_serie']} | "
            f"Localisation : {scanner_info['localisation']}"
        )

        # =========================
        # PARAMÈTRES MAINTENANCE
        # =========================

        snr_sys = st.number_input(
            "SNR système",
            min_value=0.0,
            max_value=100.0,
            value=0.0
        )

        temperature = st.number_input(
            "Température du tube RX (°C)",
            min_value=0.0,
            max_value=150.0,
            value=0.0
        )

        vibration = st.slider(
            "Vibration du gantry (%)",
            0,
            100,
            0
        )

    with col2:

        heures = st.number_input(
            "Heures d’utilisation du scanner",
            min_value=0,
            max_value=100000,
            value=0
        )

        bruit = st.slider(
            "Niveau de bruit image (%)",
            0,
            100,
            0
        )

        detecteurs = st.selectbox(
            "État des détecteurs photon-counting",
            [
                "Stable",
                "Légère dégradation",
                "Dégradation importante"
            ]
        )

        refroidissement = st.selectbox(
            "État du refroidissement",
            [
                "Normal",
                "À surveiller",
                "Défaillant"
            ]
        )

    # =========================
    # CALCUL SCORE
    # =========================

    score = 0

    score += max(0, 50 - snr_sys) * 1.3
    score += max(0, temperature - 60) * 1.2
    score += vibration * 0.5
    score += bruit * 0.4
    score += heures * 0.001

    if detecteurs == "Légère dégradation":
        score += 15

    elif detecteurs == "Dégradation importante":
        score += 35

    if refroidissement == "À surveiller":
        score += 15

    elif refroidissement == "Défaillant":
        score += 35

    score = round(min(score, 100), 2)

    # =========================
    # ÉTAT GLOBAL
    # =========================

    if score < 35:

        etat = "Stable"
        couleur = "🟢"

    elif score < 70:

        etat = "À surveiller"
        couleur = "🟠"

    else:

        etat = "Critique"
        couleur = "🔴"

    composant = "Aucun composant critique détecté"
    cause = "Fonctionnement normal"
    action = "Continuer la surveillance régulière"

    # =========================
    # ANALYSE IA
    # =========================

    if temperature > 75 or refroidissement == "Défaillant":

        composant = "Tube RX / système de refroidissement"

        cause = "Température élevée ou refroidissement insuffisant"

        action = (
            "Contrôler le système de refroidissement "
            "et vérifier le tube RX"
        )

    elif vibration > 60:

        composant = "Gantry"

        cause = "Vibrations mécaniques élevées"

        action = (
            "Vérifier l’alignement mécanique "
            "et les roulements du gantry"
        )

    elif (
        snr_sys < 45
        or bruit > 60
        or detecteurs == "Dégradation importante"
    ):

        composant = "Détecteurs photon-counting"

        cause = (
            "Baisse du SNR ou augmentation du bruit image"
        )

        action = (
            "Effectuer une calibration des détecteurs"
        )

    elif heures > 30000:

        composant = "Tube RX"

        cause = (
            "Nombre d’heures d’utilisation élevé"
        )

        action = (
            "Planifier une maintenance préventive du tube RX"
        )

    # =========================
    # AFFICHAGE
    # =========================

    st.markdown("---")

    st.markdown(
        "## Résultats de l’analyse maintenance"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Score de stress",
        f"{score} %"
    )

    c2.metric(
        "État global",
        f"{couleur} {etat}"
    )

    c3.metric(
        "Scanner",
        scanner
    )

    st.write(
        f"**Composant suspect :** {composant}"
    )

    st.write(
        f"**Cause probable :** {cause}"
    )

    st.write(
        f"**Action recommandée :** {action}"
    )

    # =========================
    # TABLEAU
    # =========================

    df_maintenance = pd.DataFrame({

        "Paramètre": [

            "Scanner",
            "SNR système",
            "Température tube RX",
            "Vibration gantry",
            "Bruit image",
            "Heures d’utilisation",
            "État détecteurs",
            "Refroidissement",
            "Score stress",
            "État global",
            "Composant suspect"
        ],

        "Valeur": [

            scanner,
            snr_sys,
            f"{temperature} °C",
            f"{vibration} %",
            f"{bruit} %",
            heures,
            detecteurs,
            refroidissement,
            f"{score} %",
            etat,
            composant
        ]
    })

    st.dataframe(
        df_maintenance,
        use_container_width=True
    )

    # =========================
    # GRAPHE
    # =========================

    df_graph = pd.DataFrame({

        "Paramètre": [
            "SNR",
            "Température",
            "Vibration",
            "Bruit",
            "Score stress"
        ],

        "Valeur": [
            snr_sys,
            temperature,
            vibration,
            bruit,
            score
        ]
    })

    st.bar_chart(
        df_graph.set_index("Paramètre")
    )
