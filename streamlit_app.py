# =========================
# VALIDATION
# =========================
elif menu == "Validation":
    set_bg("rapport.png")
    st.title("Validation des cas de test")

    cas_tests = [
        ("Patient mince", "Lina", "Sara", "RED001", "Femme", "Scanner thoracique", 23, 45.0, 170.0),
        ("Enfant", "Adam", "Youssef", "RED002", "Homme", "Scanner pulmonaire", 9, 32.0, 138.0),
        ("Patient obèse", "Mehdi", "Rachid", "RED003", "Homme", "Scanner corps entier", 59, 145.0, 171.0),
        ("Patient âgé", "Nadia", "Salma", "RED004", "Femme", "Scanner cardiaque", 72, 69.0, 162.0)
    ]

    rows = []

    for nom_cas, nom, prenom, cin, sexe, exam, age, poids, taille in cas_tests:
        p = creer_patient(nom, prenom, cin, sexe, exam, age, poids, taille)
        p["Cas test"] = nom_cas
        rows.append(p)

    df_val = pd.DataFrame(rows)

    st.dataframe(df_val, use_container_width=True)

    st.subheader("Comparaison Dose / SNR des cas de test")
    st.bar_chart(df_val.set_index("Cas test")[["Dose", "SNR"]])

    st.info(
        "Cette validation montre que la dose diminue chez les patients minces ou pédiatriques, "
        "et augmente chez les patients obèses pour maintenir un SNR acceptable."
    )

# =========================
# RAPPORT
# =========================
elif menu == "Rapport":
    set_bg("rapport.png")
    st.title("Rapports Patients")

    df = charger_patients()

    if df.empty:
        st.warning("Aucun patient enregistré.")
    else:
        st.dataframe(df, use_container_width=True)

        patient_id = st.selectbox(
            "Choisir un patient",
            df["id"],
            format_func=lambda x: f"{df[df['id']==x]['nom'].values[0]} {df[df['id']==x]['prenom'].values[0]}"
        )

        patient = df[df["id"] == patient_id].iloc[0].to_dict()

        st.subheader("Modifier les informations")

        with st.form("modification_patient"):
            nom = st.text_input("Nom", patient["nom"])
            prenom = st.text_input("Prénom", patient["prenom"])
            cin = st.text_input("CIN", patient["cin"])
            sexe = st.selectbox("Sexe", ["Homme", "Femme"], index=0 if patient["sexe"] == "Homme" else 1)

            type_examen = st.selectbox(
                "Type d'examen",
                examens,
                index=examens.index(patient["type_examen"]) if patient["type_examen"] in examens else 0
            )

            age = st.number_input("Âge", 1, 120, int(patient["age"]))
            poids = st.number_input("Poids (kg)", 20.0, 200.0, float(patient["poids"]))
            taille = st.number_input("Taille (cm)", 100.0, 220.0, float(patient["taille"]))

            modifier = st.form_submit_button("Enregistrer modifications")

        if modifier:
            p_mod = creer_patient(nom, prenom, cin, sexe, type_examen, age, poids, taille)
            modifier_patient(patient_id, p_mod)
            st.success("Patient modifié avec succès.")
            st.rerun()

        st.subheader("Aperçu du rapport")

        st.write(f"**Nom :** {patient['nom']}")
        st.write(f"**Prénom :** {patient['prenom']}")
        st.write(f"**CIN :** {patient['cin']}")
        st.write(f"**Sexe :** {patient['sexe']}")
        st.write(f"**Type examen :** {patient['type_examen']}")
        st.write(f"**IMC :** {patient['imc']} — {patient['classe_imc']}")
        st.write(f"**Dose :** {patient['dose']} mGy")
        st.write(f"**SNR :** {patient['snr']}")
        st.write(f"**kVp :** {patient['kvp']}")
        st.write(f"**mAs :** {patient['mas']}")
        st.write(f"**CTDIvol :** {patient['ctdivol']} mGy")
        st.write(f"**DLP :** {patient['dlp']} mGy.cm")
        st.info(patient["recommandation"])

        pdf_file = generer_pdf(patient)

        st.download_button(
            "Télécharger rapport PDF",
            data=pdf_file,
            file_name=f"rapport_{patient['nom']}_{patient['prenom']}.pdf",
            mime="application/pdf"
        )

        if st.button("Supprimer ce patient"):
            supprimer_patient(patient_id)
            st.success("Patient supprimé.")
            st.rerun()
