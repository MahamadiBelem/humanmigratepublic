import streamlit as st
from pymongo import MongoClient
import pandas as pd
import bcrypt
from datetime import datetime, timedelta

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['migration_in_world']
collection = db['mycollection']
users_collection = db['users']
metadata_collection = db['metadata']

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
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())

    file_id = generate_file_id(author)

    try:
        if file_type == 'csv':
            df = pd.read_csv(file, encoding='utf-8-sig')
        elif file_type == 'excel':
            df = pd.read_excel(file)
        else:
            st.error("Unsupported file type")
            return
    except Exception as e:
        st.error(f"Error reading the file: {e}")
        return

    df['file_id'] = file_id
    df['identifiant_fichier'] = file_id

    collection.insert_many(df.to_dict('records'))

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

# Fonction pour mettre à jour les données dans MongoDB
def update_data_in_mongo(file_id, updates):
    try:
        for update in updates:
            # Si vous avez une clé unique, assurez-vous de ne pas la mettre à jour par erreur
            if '_id' in update:
                del update['_id']  # Retirer '_id' pour ne pas le modifier
        result = collection.update_many({'file_id': file_id}, {'$set': updates})
        if result.matched_count > 0:
            st.success(f"Data successfully updated for file_id: {file_id}")
        else:
            st.warning(f"No matching documents found for file_id: {file_id}")
    except Exception as e:
        st.error(f"Error updating data: {e}")

# Fonction pour supprimer un fichier entier de MongoDB
def delete_file(file_id):
    try:
        collection.delete_many({'file_id': file_id})
        metadata_collection.delete_one({'_id': file_id})
        st.success("File successfully deleted")
    except Exception as e:
        st.error(f"Error deleting file: {e}")

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

# Fonction pour supprimer des données dans MongoDB
def delete_data_from_mongo(doc_id):
    try:
        collection.delete_one({'_id': doc_id})
        st.success("Data successfully deleted")
    except Exception as e:
        st.error(f"Error deleting data: {e}")

# Interface utilisateur Streamlit
st.markdown('<style>div.block-container{padding-top: 2rem;}</style>', unsafe_allow_html=True)

# Barre horizontale de couleur bleue ciel
st.markdown("""
    <style>
        .header {
            background-color: #87CEEB;
            padding: 10px;
            color: white;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
        }
        .marquee {
            background-color: #f0f8ff;
            color: #00008b;
            font-size: 20px;
            font-weight: bold;
            padding: 10px;
            white-space: nowrap;
            overflow: hidden;
            box-sizing: border-box;
        }
        .marquee span {
            display: inline-block;
            padding-left: 100%;
            animation: marquee 10s linear infinite;
        }
        @keyframes marquee {
            from {
                transform: translateX(0);
            }
            to {
                transform: translateX(-100%);
            }
        }
    </style>
    <div class="header">
        MongoDB Data Management
    </div>
    <div class="marquee">
        <span>Welcome to the Big Data Management System!</span>
    </div>
""", unsafe_allow_html=True)

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
    page = st.sidebar.selectbox("Select a page", [
        "Home",
        "Upload Data", 
        "View Data", 
        "Update Data", 
        "Delete Data", 
        "View Metadata", 
        "Delete a File", 
        "Logout"
    ])

    if page == "Home":
        st.subheader("Welcome to the Big Data Management System")
        st.image("https://www.example.com/path-to-your-big-data-image.jpg", caption="Big Data Management", use_column_width=True)
        st.write("""
            This application allows you to manage your data in MongoDB efficiently. 
            Use the sidebar to navigate between different sections:
            - **Upload Data**: Add new data files to the database.
            - **View Data**: Explore and download data files.
            - **Update Data**: Modify existing data records.
            - **Delete Data**: Remove specific data records.
            - **View Metadata**: Review metadata information about your files.
            - **Delete a File**: Permanently delete a file and its associated data.
        """)

    elif page == "Upload Data":
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
        metadata = list(metadata_collection.find())
        if metadata:
            df_metadata = pd.DataFrame(metadata)
            st.dataframe(df_metadata)

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
                
                file_data = list(collection.find({"file_id": selected_file_id}))
                if file_data:
                    df = pd.DataFrame(file_data)
                    st.dataframe(df)

                    try:
                        csv_data = df.to_csv(index=False, encoding='utf-8-sig')
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
        metadata = list(metadata_collection.find())
        if metadata:
            df_metadata = pd.DataFrame(metadata)
            descriptions_authors = df_metadata['description'] + " - " + df_metadata['author']
            selected_description_author = st.selectbox("Select file description and author", descriptions_authors)

            if selected_description_author:
                selected_metadata = df_metadata[df_metadata['description'] + " - " + df_metadata['author'] == selected_description_author]
                selected_file_id = selected_metadata.iloc[0]['_id']
                
                st.write(f"Selected file ID for update: {selected_file_id}")

                file_data = list(collection.find({"file_id": selected_file_id}))
                if file_data:
                    df = pd.DataFrame(file_data)
                    st.write("Current Data:")
                    
                    # Afficher les données dans un tableau éditable
                    edited_df = st.data_editor(df, use_container_width=True)

                    # Ajouter un bouton pour sauvegarder les modifications
                    if st.button("Save Changes"):
                        # Convertir les données modifiées en dictionnaire
                        updates = edited_df.to_dict(orient='records')
                        
                        # Convertir le dictionnaire en une liste de mises à jour pour MongoDB
                        for update in updates:
                            if '_id' in update:
                                del update['_id']  # Retirer '_id' pour ne pas le modifier
                        update_data_in_mongo(selected_file_id, edited_df.to_dict(orient='records'))

                    st.write("Updated Data Preview:")
                    st.dataframe(edited_df)
                else:
                    st.warning(f"No data found for file with file_id: {selected_file_id}")
        else:
            st.warning("No files found in MongoDB")

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
