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

# Fonction pour charger un fichier dans MongoDB
def load_data_to_mongo(file, file_type, description, author, source, data_type):
    try:
        # Générer un ID unique pour le fichier
        file_id = str(uuid.uuid4())

        if file_type == 'csv':
            df = pd.read_csv(file)
        elif file_type == 'excel':
            df = pd.read_excel(file)
        else:
            st.error("Type de fichier non pris en charge")
            return

        # Ajout d'un ID unique à chaque document
        df['_id'] = [str(uuid.uuid4()) for _ in range(len(df))]
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
    except OverflowError as e:
        st.error(f"Erreur lors du chargement des données : {e}")

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
def update_data_in_mongo(file_id, updates):
    collection.update_many({'file_id': file_id}, {'$set': updates})
    st.success("Données mises à jour avec succès")

# Fonction pour supprimer des données dans MongoDB
def delete_data_from_mongo(file_id):
    collection.delete_many({'file_id': file_id})
    metadata_collection.delete_one({'_id': file_id})
    st.success("Données supprimées avec succès")

# Interface utilisateur Streamlit
st.title("Application de gestion des données MongoDB")

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
    page = st.sidebar.selectbox("Sélectionner une page", ["Charger les données", "Afficher les données", "Modifier les données", "Supprimer les données", "Afficher les métadonnées", "Déconnexion"])

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
        try:
            # Récupérer les métadonnées pour obtenir la liste des fichiers
            metadata = list(metadata_collection.find())
            if metadata:
                # Afficher une liste déroulante pour choisir le fichier
                selected_file_id = st.selectbox("Choisir un fichier", [m['_id'] for m in metadata], format_func=lambda x: f"{next(m['description'] for m in metadata if m['_id'] == x)} ({x})")
                
                if selected_file_id:
                    # Récupérer les données du fichier sélectionné
                    data = list(collection.find({'file_id': selected_file_id}))
                    if data:
                        df = pd.DataFrame(data)
                        st.dataframe(df)
                        # Télécharger les données
                        st.download_button("Télécharger les données en CSV", df.to_csv(index=False).encode('utf-8'), "data.csv", "text/csv")
                        st.download_button("Télécharger les données en JSON", df.to_json(orient='records').encode('utf-8'), "data.json", "application/json")
                        st.download_button("Télécharger les données en Excel", df.to_excel(index=False).encode('utf-8'), "data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    else:
                        st.warning("Aucune donnée trouvée pour ce fichier dans MongoDB")
            else:
                st.warning("Aucun fichier trouvé dans MongoDB")
        except OverflowError as e:
            st.error(f"Erreur lors de l'affichage des données : {e}")

    elif page == "Modifier les données":
        st.subheader("Modifier les données")
        try:
            metadata = list(metadata_collection.find())
            if metadata:
                # Afficher une liste déroulante pour choisir le fichier
                selected_file_id = st.selectbox("Choisir un fichier à modifier", [m['_id'] for m in metadata], format_func=lambda x: f"{next(m['description'] for m in metadata if m['_id'] == x)} ({x})")

                if selected_file_id:
                    data = list(collection.find({'file_id': selected_file_id}))
                    if data:
                        df = pd.DataFrame(data)
                        st.dataframe(df)
                        
                        with st.form(key='update_form'):
                            updated_data = {}
                            for col in df.columns:
                                if col not in ['_id', 'file_id']:
                                    updated_data[col] = st.text_input(col, value=str(df[col].iloc[0]))
                            submit_button = st.form_submit_button(label='Mettre à jour')

                            if submit_button:
                                update_data_in_mongo(selected_file_id, updated_data)
                    else:
                        st.warning("Aucune donnée trouvée pour ce fichier dans MongoDB")
            else:
                st.warning("Aucun fichier trouvé dans MongoDB")
        except OverflowError as e:
            st.error(f"Erreur lors de la modification des données : {e}")

    elif page == "Supprimer les données":
        st.subheader("Supprimer un fichier")
        try:
            metadata = list(metadata_collection.find())
            if metadata:
                # Afficher une liste déroulante pour choisir le fichier
                selected_file_id = st.selectbox("Choisir un fichier à supprimer", [m['_id'] for m in metadata], format_func=lambda x: f"{next(m['description'] for m in metadata if m['_id'] == x)} ({x})")

                if selected_file_id and st.button("Supprimer"):
                    delete_data_from_mongo(selected_file_id)
            else:
                st.warning("Aucun fichier trouvé dans MongoDB")
        except OverflowError as e:
            st.error(f"Erreur lors de la suppression des données : {e}")

    elif page == "Afficher les métadonnées":
        st.subheader("Afficher les métadonnées des fichiers")
        try:
            metadata = list(metadata_collection.find())
            if metadata:
                df_metadata = pd.DataFrame(metadata)
                st.dataframe(df_metadata)
            else:
                st.warning("Aucune métadonnée trouvée dans MongoDB")
        except OverflowError as e:
            st.error(f"Erreur lors de l'affichage des métadonnées : {e}")

    elif page == "Déconnexion":
        st.session_state.logged_in = False
        st.success("Déconnecté avec succès")
