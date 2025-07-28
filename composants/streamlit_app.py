import streamlit as st
import pandas as pd
import os
import io

st.title("Traitement de fichiers CSV fournisseur")

uploaded_files = st.file_uploader("Déposez vos fichiers CSV ou Excel (séparateur ;)", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.subheader(f"Fichier : {uploaded_file.name}")
        # Lecture du fichier uploadé selon l'extension
        if uploaded_file.name.lower().endswith('.xlsx'):
            try:
                # Utiliser openpyxl avec gestion d'erreur robuste
                df = pd.read_excel(uploaded_file, dtype=str, engine='openpyxl')
            except Exception as e:
                st.error(f"Impossible de lire le fichier Excel. Erreur: {str(e)}")
                st.info("Essayez de sauvegarder votre fichier Excel en format .xlsx plus récent ou convertissez-le en CSV.")
                continue
        else:
            df = pd.read_csv(uploaded_file, sep=';', dtype=str)

        # Colonnes à garder
        colonnes_a_garder = [
            'Réf Fournisseur',
            'Désignation',
            'Date besoin',
            'Version',
            'Ebauche',
            'Qté',
            'Prix',
            'Bande'
        ]
        df = df[colonnes_a_garder].copy()

        # Ajouter colonne vide Annulé
        df['Annulé'] = ''

        # Renommer les colonnes
        renommage = {
            'Réf Fournisseur': 'Référence',
            'Désignation': 'Désignation',
        }
        df = df.rename(columns=renommage)

        # Convertir 'Date besoin' en datetime pour groupby (format automatique)
        df['Date besoin'] = pd.to_datetime(df['Date besoin'], errors='coerce')

        # Groupby sur Référence, Ebauche, Version
        resultat = df.groupby(['Référence', 'Ebauche', 'Version'], as_index=False).agg({
            'Désignation': 'first',
            'Date besoin': 'min',
            'Qté': lambda x: pd.to_numeric(x, errors='coerce').sum(),
            'Prix': 'first',
            'Bande': 'first',
            'Annulé': 'first'
        })

        # Reconvertir 'Date besoin' en texte
        resultat['Date besoin'] = resultat['Date besoin'].dt.strftime('%d/%m/%Y')

        # Nettoyer la colonne Prix
        resultat['Prix'] = resultat['Prix'].str.replace('€', '', regex=False)
        resultat['Prix'] = resultat['Prix'].str.replace(',', '.', regex=False)
        resultat['Prix'] = resultat['Prix'].astype(float)
        def format_prix(x):
            if x == int(x):
                return str(int(x))
            else:
                return str(x).replace('.', ',')
        resultat['Prix'] = resultat['Prix'].apply(format_prix)

        # Ajouter colonne Commande (nom du fichier sans extension)
        nom_commande = os.path.splitext(uploaded_file.name)[0]
        resultat.insert(0, 'Commande', nom_commande)

        # Réorganiser les colonnes
        ordre_colonnes = [
            'Commande',
            'Référence',
            'Désignation',
            'Date besoin',
            'Ebauche',
            'Version',
            'Qté',
            'Annulé',
            'Prix',
            'Bande'
        ]
        resultat = resultat[ordre_colonnes]

        # Nettoyer les colonnes texte pour éviter les caractères bizarres
        for col in resultat.select_dtypes(include='object').columns:
            resultat[col] = resultat[col].astype(str).apply(lambda x: x.encode('utf-8', errors='replace').decode('utf-8'))

        # Remplacer les None/NaN ou 'None' par des cases vides
        resultat = resultat.replace("None", "").fillna("")

        # Affichage du résultat
        st.write("Aperçu du fichier traité :")
        st.dataframe(resultat)

        # Préparation du CSV à télécharger
        csv = resultat.to_csv(sep=',', index=False, encoding='utf-8-sig')
        st.download_button(
            label=f"Télécharger le CSV traité : {nom_commande}.csv",
            data=csv,
            file_name=f"{nom_commande}.csv",
            mime="text/csv"
        )
else:
    st.info("Veuillez déposer un ou plusieurs fichiers CSV ou Excel pour commencer.") 