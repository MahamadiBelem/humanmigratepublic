import streamlit as st
from pymongo import MongoClient
import pandas as pd
import bcrypt
from datetime import datetime
import uuid

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['migration_in_world']
collection = db['mycollection']
users_collection = db['users']
metadata_collection = db['metadata']

# Fonction pour générer un ID de fichier basé sur l'utilisateur, l'année et un numéro d'ordre
# Fonction pour générer un ID de fichier basé sur l'utilisateur, l'année et un numéro d'ordre
def generate_file_id(username):
    year = datetime.now().year
    last_metadata = metadata_collection.find({"author": username}).sort("_id", -1).limit(1)
    
    last_order_number = 1
    try:
        last_doc = last_metadata.next()
        last_order_number = int(last_doc['_id'].split('-')[-1]) + 1
    except StopIteration:
        pass  # Si le curseur est vide, nous gardons last_order_number à 1
    
    return f"{username}-{year}-{last_order_number}"
# Fonction pour charger un fichier dans MongoDB
def load_data_to_mongo(file, file_type, description, author, source, data_type, start_date, end_date):
    # Convertir start_date et end_date en datetime.datetime
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())

    # Générer un ID unique pour le fichier
    file_id = generate_file_id(author)

    try:
        if file_type == 'csv':
            df = pd.read_csv(file, encoding='utf-8-sig')  # Utiliser utf-8-sig pour gérer les encodages variés
        elif file_type == 'excel':
            df = pd.read_excel(file)
        else:
            st.error("Unsupported file type")
            return
    except Exception as e:
        st.error(f"Error reading the file: {e}")
        return

    # Ajouter le file_id aux données avant l'insertion
    df['file_id'] = file_id
    df['identifiant_fichier'] = file_id  # Ajouter la colonne identifiant_fichier

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
        'file_type': file_type,
        'start_date': start_datetime,
        'end_date': end_datetime
    }
    metadata_collection.insert_one(metadata)
    st.success("Data successfully uploaded to MongoDB")

# Fonction pour supprimer un fichier entier de MongoDB
def delete_file(file_id):
    # Confirmer la suppression du fichier
    if st.button("Confirm Deletion"):
        collection.delete_many({'file_id': file_id})
        metadata_collection.delete_one({'_id': file_id})
        st.success("File successfully deleted")

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
    st.success("Data successfully updated")

# Fonction pour supprimer des données dans MongoDB
def delete_data_from_mongo(doc_id):
    collection.delete_one({'_id': doc_id})
    st.success("Data successfully deleted")

# Interface utilisateur Streamlit
st.title("MongoDB Data Management")

# Gestion des utilisateurs
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login_user(username, password):
            st.session_state.logged_in = True
            st.success("Login successful")
        else:
            st.error("Invalid credentials")
    if st.button("Create Account"):
        if username and password:
            create_user(username, password)
            st.success("Account created successfully")
        else:
            st.error("Please fill in all fields")
else:
    st.sidebar.title("Options")
    page = st.sidebar.selectbox("Select a page", ["Upload Data", "View Data", "Update Data", "Delete Data", "View Metadata", "Delete a File", "Logout"])

    if page == "Upload Data":
        st.subheader("Upload a file")
        uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx'])
        description = st.text_input("File Description")
        author = st.text_input("File Author")
        source = st.text_input("File Source")
        data_type = st.text_input("Data Type")
        start_date = st.date_input("Start Date", datetime.now())
        end_date = st.date_input("End Date", datetime.now())

        if uploaded_file is not None:
            file_type = uploaded_file.name.split('.')[-1]
            if st.button("Upload to MongoDB"):
                load_data_to_mongo(uploaded_file, file_type, description, author, source, data_type, start_date, end_date)

    elif page == "View Data":
        st.subheader("View MongoDB Data")

        # Afficher les métadonnées
        metadata = list(metadata_collection.find())
        if metadata:
            df_metadata = pd.DataFrame(metadata)
            st.dataframe(df_metadata)

            # Ajouter un bouton "Voir" pour chaque fichier
            selected_description = st.selectbox("Select a file description", df_metadata['description'])
            if selected_description:
                selected_metadata = df_metadata[df_metadata['description'] == selected_description].iloc[0]
                selected_file_id = selected_metadata['_id']
                
                st.write("File Information:")
                st.write(f"Author: {selected_metadata['author']}")
                st.write(f"Description: {selected_metadata['description']}")
                st.write(f"Source: {selected_metadata['source']}")
                st.write(f"Start Date: {selected_metadata['start_date']}")
                st.write(f"End Date: {selected_metadata['end_date']}")

                st.write(f"Displaying data for file: {selected_file_id}")
                
                # Afficher les données du fichier sélectionné
                file_data = list(collection.find({"file_id": selected_file_id}))
                if file_data:
                    df = pd.DataFrame(file_data)
                    st.dataframe(df)

                    # Télécharger les données avec gestion des erreurs d'encodage
                    try:
                        csv_data = df.to_csv(index=False, encoding='utf-8-sig')  # Utiliser utf-8-sig pour éviter les problèmes d'encodage
                        st.download_button("Download Data as CSV", csv_data, "data.csv", "text/csv")
                    except OverflowError:
                        st.error("Error generating CSV file")

                    try:
                        json_data = df.to_json(orient='records', force_ascii=False).encode('utf-8')
                        st.download_button("Download Data as JSON", json_data, "data.json", "application/json")
                    except OverflowError:
                        st.error("Error generating JSON file")

                    try:
                        excel_data = df.to_excel(index=False, engine='openpyxl').encode('utf-8')
                        st.download_button("Download Data as Excel", excel_data, "data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    except OverflowError:
                        st.error("Error generating Excel file")

                    # Afficher un résumé des données numériques
                    num_data = df.select_dtypes(include='number')
                    if not num_data.empty:
                        st.subheader("Numeric Data Summary")
                        st.write(num_data.describe())
                    else:
                        st.write("No numeric data available for summary.")
                else:
                    st.warning(f"No data found for file with file_id: {selected_file_id}")
        else:
            st.warning("No files found in MongoDB")

    elif page == "Update Data":
        st.subheader("Update Data")
        data = list(collection.find())
        if data:
            df = pd.DataFrame(data)
            selected_index = st.selectbox("Select the index of the row to update", df.index)
            selected_row = df.iloc[selected_index]

            with st.form(key='update_form'):
                updated_data = {}
                for col in df.columns:
                    updated_data[col] = st.text_input(col, value=selected_row[col])
                submit_button = st.form_submit_button(label='Update')

                if submit_button:
                    update_data_in_mongo(selected_row['_id'], updated_data)

    elif page == "Delete Data":
        st.subheader("Delete Data")
        data = list(collection.find())
        if data:
            df = pd.DataFrame(data)
            selected_index = st.selectbox("Select the index of the row to delete", df.index)
            selected_row = df.iloc[selected_index]

            if st.button("Delete"):
                if st.button("Confirm Deletion"):
                    delete_data_from_mongo(selected_row['_id'])
                else:
                    st.warning("Please confirm the deletion.")

    elif page == "View Metadata":
        st.subheader("View File Metadata")
        metadata = list(metadata_collection.find())
        if metadata:
            df_metadata = pd.DataFrame(metadata)
            st.dataframe(df_metadata)
        else:
            st.warning("No metadata found in MongoDB")

    elif page == "Delete a File":
        st.subheader("Delete a File")
        metadata = list(metadata_collection.find())
        if metadata:
            df_metadata = pd.DataFrame(metadata)
            descriptions_authors = df_metadata['description'] + " - " + df_metadata['author']
            selected_description_author = st.selectbox("Select file description and author", descriptions_authors)

            if selected_description_author:
                selected_metadata = df_metadata[df_metadata['description'] + " - " + df_metadata['author'] == selected_description_author]
                selected_file_id = selected_metadata.iloc[0]['_id']
                
                if st.button("Delete File"):
                    if st.button("Confirm Deletion"):
                        delete_file(selected_file_id)
                    else:
                        st.warning("Please confirm the deletion.")
        else:
            st.warning("No files found in MongoDB")

    elif page == "Logout":
        st.session_state.logged_in = False
        st.success("Logged out successfully")
