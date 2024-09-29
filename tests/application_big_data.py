import streamlit as st
from pymongo import MongoClient
import pandas as pd
import bcrypt
from datetime import datetime
import uuid

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['mydatabase']
collection = db['mycollection']
users_collection = db['users']
metadata_collection = db['metadata']


# Fonction pour générer un ID de fichier basé sur l'utilisateur, l'année et un numéro d'ordre
def generate_file_id(username):
    year = datetime.now().year
    last_metadata = metadata_collection.find({"author": username}).sort("_id", -1).limit(1)
    last_order_number = 1 if last_metadata.count() == 0 else int(last_metadata[0]['_id'].split('-')[-1]) + 1
    return f"{username}-{year}-{last_order_number}"

# Fonction pour charger un fichier dans MongoDB
def load_data_to_mongo(file, file_type, description, author, source, data_type):
    # Générer un ID unique pour le fichier
    file_id = generate_file_id(author)

    try:
        if file_type == 'csv':
            df = pd.read_csv(file, encoding='utf-8-sig')  # Utiliser utf-8-sig pour gérer les encodages variés
        elif file_type == 'excel':
            df = pd.read_excel(file)
        else:
            st.error("Type de fichier non pris en charge")
            return
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier : {e}")
        return

    # Ajouter le file_id aux données avant l'insertion
    df['file_id'] = file_id

    # Convertir le DataFrame en dictionnaire et insérer les données dans MongoDB
    collection.insert_many(df.to_dict('records'))

    # Stocker les métadonnées du fichier
    metadata = {
        '_id': file_id,
        'description': description,
        'author': author,
        'date_loaded': datetime.now(),
        'source': source,
        'data_type': data_type,
        'file_type': file_type
    }
    metadata_collection.insert_one(metadata)
    st.success("Données chargées avec succès dans MongoDB")

# Fonction pour supprimer un fichier entier de MongoDB
def delete_file(file_id):
    collection.delete_many({'file_id': file_id})
    metadata_collection.delete_one({'_id': file_id})
    st.success("Fichier supprimé avec succès")

# Fonction pour créer un nouvel utilisateur
def create_user(username, password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users_collection.insert_one({"username": username, "password": hashed})

# Fonction pour vérifier les identifiants de l'utilisateur
def login_user(username, password):
    user = users_collection.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return True
    return False

# Fonction pour mettre à jour les données dans MongoDB
def update_data_in_mongo(doc_id, updates):
    collection.update_one({'_id': doc_id}, {'$set': updates})
    st.success("Données mises à jour avec succès")

# Fonction pour supprimer des données dans MongoDB
def delete_data_from_mongo(doc_id):
    collection.delete_one({'_id': doc_id})
    st.success("Données supprimées avec succès")

# Interface utilisateur Streamlit
st.title("Gestion des données MongoDB")

# Gestion des utilisateurs
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("Connexion")
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if login_user(username, password):
            st.session_state.logged_in = True
            st.success("Connexion réussie")
        else:
            st.error("Identifiants incorrects")
    if st.button("Créer un compte"):
        if username and password:
            create_user(username, password)
            st.success("Compte créé avec succès")
        else:
            st.error("Veuillez remplir tous les champs")
else:
    st.sidebar.title("Options")
    page = st.sidebar.selectbox("Sélectionner une page", ["Charger les données", "Afficher les données", "Modifier les données", "Supprimer les données", "Afficher les métadonnées", "Supprimer un fichier", "Déconnexion"])

    if page == "Charger les données":
        st.subheader("Charger un fichier")
        uploaded_file = st.file_uploader("Choisissez un fichier CSV ou Excel", type=['csv', 'xlsx'])
        description = st.text_input("Description du fichier")
        author = st.text_input("Auteur du fichier")
        source = st.text_input("Source du fichier")
        data_type = st.text_input("Type de données")

        if uploaded_file is not None:
            file_type = uploaded_file.name.split('.')[-1]
            if st.button("Charger dans MongoDB"):
                load_data_to_mongo(uploaded_file, file_type, description, author, source, data_type)

    elif page == "Afficher les données":
        st.subheader("Afficher les données de MongoDB")
        
        # Sélectionner le fichier à afficher par description
        metadata = list(metadata_collection.find())
        if metadata:
            df_metadata = pd.DataFrame(metadata)
            descriptions = df_metadata['description'].tolist()
            selected_description = st.selectbox("Sélectionnez une description de fichier", descriptions)

            if selected_description:
                selected_metadata = df_metadata[df_metadata['description'] == selected_description].iloc[0]
                selected_file_id = selected_metadata['_id']
                st.write(f"Affichage des données pour le fichier : {selected_file_id}  {selected_metadata}")
                file_data = list(collection.find({"file_id": selected_file_id}))
                if file_data:
                    df = pd.DataFrame(file_data)
                    st.dataframe(df)

                    # Télécharger les données avec gestion des erreurs d'encodage
                    try:
                        csv_data = df.to_csv(index=False, encoding='utf-8-sig')  # Utiliser utf-8-sig pour éviter les problèmes d'encodage
                        st.download_button("Télécharger les données en CSV", csv_data, "data.csv", "text/csv")
                    except OverflowError:
                        st.error("Erreur lors de la génération du fichier CSV")

                    try:
                        json_data = df.to_json(orient='records', force_ascii=False).encode('utf-8')
                        st.download_button("Télécharger les données en JSON", json_data, "data.json", "application/json")
                    except OverflowError:
                        st.error("Erreur lors de la génération du fichier JSON")

                    try:
                        excel_data = df.to_excel(index=False, engine='openpyxl').encode('utf-8')
                        st.download_button("Télécharger les données en Excel", excel_data, "data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    except OverflowError:
                        st.error("Erreur lors de la génération du fichier Excel")

                    # Afficher un résumé des données numériques
                    num_data = df.select_dtypes(include='number')
                    if not num_data.empty:
                        st.subheader("Résumé des données numériques")
                        st.write(num_data.describe())
                    else:
                        st.write("Aucune donnée numérique disponible pour le résumé.")
                else:
                    st.warning(f"Aucune donnée trouvée pour le fichier avec file_id : {selected_file_id}")
        else:
            st.warning("Aucun fichier trouvé dans MongoDB")

    elif page == "Modifier les données":
        st.subheader("Modifier les données")
        data = list(collection.find())
        if data:
            df = pd.DataFrame(data)
            selected_index = st.selectbox("Sélectionnez l'index de la ligne à modifier", df.index)
            selected_row = df.iloc[selected_index]

            with st.form(key='update_form'):
                updated_data = {}
                for col in df.columns:
                    updated_data[col] = st.text_input(col, value=selected_row[col])
                submit_button = st.form_submit_button(label='Mettre à jour')

                if submit_button:
                    update_data_in_mongo(selected_row['_id'], updated_data)

    elif page == "Supprimer les données":
        st.subheader("Supprimer les données")
        data = list(collection.find())
        if data:
            df = pd.DataFrame(data)
            selected_index = st.selectbox("Sélectionnez l'index de la ligne à supprimer", df.index)
            selected_row = df.iloc[selected_index]

            if st.button("Supprimer"):
                delete_data_from_mongo(selected_row['_id'])

    elif page == "Afficher les métadonnées":
        st.subheader("Afficher les métadonnées des fichiers")
        metadata = list(metadata_collection.find())
        if metadata:
            df_metadata = pd.DataFrame(metadata)
            st.dataframe(df_metadata)
        else:
            st.warning("Aucune métadonnée trouvée dans MongoDB")

    elif page == "Supprimer un fichier":
        st.subheader("Supprimer un fichier")
        metadata = list(metadata_collection.find())
        if metadata:
            df_metadata = pd.DataFrame(metadata)
            descriptions = df_metadata['description'].unique().tolist()
            df_metadata['description_author'] = df_metadata['description'] + "-" + df_metadata['author']
            descriptions_authors = df_metadata['description_author'].tolist()
            authors = df_metadata['author'].unique().tolist()

            selected_description = st.selectbox("Sélectionnez la description du fichier", descriptions_authors)
            # selected_author = st.selectbox("Sélectionnez l'auteur du fichier", authors)

            filtered_metadata = df_metadata[(df_metadata['description'] == selected_description)]

            if not filtered_metadata.empty:
                selected_file_id = filtered_metadata.iloc[0]['_id']

                if st.button("Supprimer le fichier"):
                    delete_file(selected_file_id)
        else:
            st.warning("Aucun fichier trouvé dans MongoDB")

    elif page == "Déconnexion":
        st.session_state.logged_in = False
        st.success("Déconnecté avec succès")
