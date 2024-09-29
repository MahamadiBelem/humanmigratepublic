import streamlit as st
from pymongo import MongoClient
import pandas as pd
import bcrypt

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['mydatabase']
collection = db['mycollection']
users_collection = db['users']

# Fonction pour charger un fichier dans MongoDB
def load_data_to_mongo(file, file_type):
    if file_type == 'csv':
        df = pd.read_csv(file)
    elif file_type == 'excel':
        df = pd.read_excel(file)
    else:
        st.error("Type de fichier non pris en charge")
        return

    # Convertir le DataFrame en dictionnaire et insérer les données dans MongoDB
    collection.insert_many(df.to_dict('records'))
    st.success("Données chargées avec succès dans MongoDB")

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
    page = st.sidebar.selectbox("Sélectionner une page", ["Charger les données", "Afficher les données", "Modifier les données", "Supprimer les données", "Déconnexion"])

    if page == "Charger les données":
        st.subheader("Charger un fichier")
        uploaded_file = st.file_uploader("Choisissez un fichier CSV ou Excel", type=['csv', 'xlsx'])
        if uploaded_file is not None:
            file_type = uploaded_file.name.split('.')[-1]
            if st.button("Charger dans MongoDB"):
                load_data_to_mongo(uploaded_file, file_type)

    elif page == "Afficher les données":
        st.subheader("Afficher les données de MongoDB")
        data = list(collection.find())
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df)
            # Télécharger les données
            st.download_button("Télécharger les données en CSV", df.to_csv(index=False).encode('utf-8'), "data.csv", "text/csv")
            st.download_button("Télécharger les données en JSON", df.to_json(orient='records').encode('utf-8'), "data.json", "application/json")
            st.download_button("Télécharger les données en Excel", df.to_excel(index=False).encode('utf-8'), "data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.warning("Aucune donnée trouvée dans MongoDB")

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

    elif page == "Déconnexion":
        st.session_state.logged_in = False
        st.success("Déconnecté avec succès")
