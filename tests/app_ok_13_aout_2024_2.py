import streamlit as st
from pymongo import MongoClient
import pandas as pd
from datetime import datetime
import bcrypt
from io import StringIO
import os

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['migration_in_world']
collection = db['mycollection']
metadata_collection = db['metadata']
users_collection = db['users']

import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Application de Gestion",
    layout="wide"
)

# Définir la mise en page
st.markdown(
    """
    <style>
    .main {
        padding: 2rem;
    }
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .login-button {
        padding: 0.5rem 1rem;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    .login-button:hover {
        background-color: #45a049;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Contenu de la page
def main():
    st.markdown('<div class="header">', unsafe_allow_html=True)
    if st.button('Login', key='login', help='Se connecter'):
        st.write("Vous avez cliqué sur le bouton de connexion.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.title("Bienvenue dans l'Application de Gestion")
    st.write(
        """
        Cette application vous permet de gérer vos données de manière efficace.
        Utilisez le bouton de connexion en haut à gauche pour accéder aux fonctionnalités sécurisées.
        """
    )

if __name__ == "__main__":
    main()

def generate_file_id(username):
    year = datetime.now().year
    last_metadata = metadata_collection.find({"author": username}).sort("_id", -1).limit(1)
    
    last_order_number = 1
    try:
        last_doc = last_metadata.next()
        last_order_number = int(last_doc['_id'].split('-')[-1]) + 1
    except StopIteration:
        pass
    
    return f"{username}-{year}-{last_order_number}"

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

    try:
        collection.insert_many(df.to_dict('records'))
    except Exception as e:
        st.error(f"Error inserting data into MongoDB: {e}")
        return

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
    try:
        metadata_collection.insert_one(metadata)
        st.success("Data successfully uploaded to MongoDB")
    except Exception as e:
        st.error(f"Error inserting metadata into MongoDB: {e}")

def update_data_in_mongo(file_id, updates):
    try:
        if not isinstance(updates, dict):
            raise ValueError("Updates must be a dictionary.")
        
        updates.pop('_id', None)
        
        if not updates:
            st.warning("No fields to update.")
            return

        result = collection.update_many({'file_id': file_id}, {'$set': updates})
        
        if result.matched_count > 0:
            st.success(f"Data successfully updated for file_id: {file_id}. Matched {result.matched_count} document(s) and updated {result.modified_count} document(s).")
        else:
            st.warning(f"No matching documents found for file_id: {file_id}. No updates were made.")
    
    except ValueError as ve:
        st.error(f"ValueError: {ve}")
    except Exception as e:
        st.error(f"An error occurred while updating data: {e}")

def delete_file(file_id):
    try:
        collection.delete_many({'file_id': file_id})
        metadata_collection.delete_one({'_id': file_id})
        st.success("File successfully deleted")
    except Exception as e:
        st.error(f"Error deleting file: {e}")

def create_user(username, password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users_collection.insert_one({"username": username, "password": hashed})

def login_user(username, password):
    user = users_collection.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return True
    return False

def delete_data_from_mongo(doc_id):
    try:
        collection.delete_one({'_id': doc_id})
        st.success("Data successfully deleted")
    except Exception as e:
        st.error(f"Error deleting data: {e}")

def upload_by_update(file):
    try:
        df = pd.read_csv(file, encoding='utf-8-sig')
        
        required_columns = ['Year', 'Location', 'Origin', 'Region', 'Investment', 'Type', 'Destination', 'Age Group', 'Education Level', 'Rating', 'Migrants', 'raisons']
        if not all(col in df.columns for col in required_columns):
            st.error(f"File must contain the following columns: {', '.join(required_columns)}")
            return

        file_id = generate_file_id('admin')
        df['file_id'] = file_id

        records = df.to_dict('records')

        filter_criteria = {col: {'$in': df[col].tolist()} for col in required_columns}
        collection.delete_many(filter_criteria)
        
        collection.insert_many(records)
        st.success("Data successfully updated from the file")
        
    except Exception as e:
        st.error(f"Error updating data from the file: {e}")

st.markdown('<style>div.block-container{padding-top: 2rem;}</style>', unsafe_allow_html=True)

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
        "View Metadata", 
        "Delete a File", 
        "Logout"
    ])
    # page = st.sidebar.selectbox("Select a page", [
    #     "Home",
    # ])
    # page = st.sidebar.selectbox("Select a page", [
    #     "Home",
    #     "Upload Data", 
    # ])
        
    
    # st.title("Main Menu")
    # option = st.selectbox(
    #     "Choose a file to run:",
    #     ("mongo_5.py", "app_ok.py")
    # )

    # if st.button("Run"):
    #     if option == "mongo_5.py":
    #         os.system("streamlit run file2.py")
    #     elif option == "app_ok.py":
    #         os.system("streamlit run file3.py")

   



    if page == "Home":
        st.subheader("Welcome to the Big Data Management System")
        st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR8Dssfc06wlo2Wc7zdOVb676dPJBJAyrwbBPsns3CY_54WAIBM1u0T7z6w8of2hJeYSbw&usqp=CAU", caption="Big Data Management", use_column_width=True)
        # st.write("""
        #     This application allows you to manage your data in MongoDB efficiently. 
        #     Use the sidebar to navigate between different sections:
        #     - **Upload Data**: Add new data files to the database.
        #     - **View Data**: Explore and download data files.
        #     - **Update Data**: Modify existing data records.
        #     - **Delete Data**: Remove specific data records.
        #     - **View Metadata**: Review metadata information about your files.
        #     - **Delete a File**: Permanently delete a file and its associated data.
        # """)

        st.markdown("""
        <style>
        .custom-header {
            font-size: 24px;
            font-weight: bold;
            color: #2F4F4F;
            margin-bottom: 10px;
        }
        .custom-section {
            font-size: 18px;
            margin-bottom: 10px;
        }
        .upload { color: #1E90FF; }
        .view { color: #32CD32; }
        .update { color: #FF8C00; }
        .delete { color: #FF4500; }
        .metadata { color: #8A2BE2; }
        .file { color: #DC143C; }
        </style>
        """, unsafe_allow_html=True)

        # Display the styled text
        st.markdown("""
            <div class="custom-header">
                This application allows you to manage your data in MongoDB efficiently.
            </div>
            <div class="custom-section">
                Use the sidebar to navigate between different sections:
                <ul>
                    <li><span class="upload"><strong>Upload Data</strong></span>: Add new data files to the database.</li>
                    <li><span class="view"><strong>View Data</strong></span>: Explore and download data files.</li>
                    <li><span class="update"><strong>Update Data</strong></span>: Modify existing data records.</li>
                    <li><span class="delete"><strong>Delete Data</strong></span>: Remove specific data records.</li>
                    <li><span class="metadata"><strong>View Metadata</strong></span>: Review metadata information about your files.</li>
                    <li><span class="file"><strong>Delete a File</strong></span>: Permanently delete a file and its associated data.</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    elif page == "Upload Data":
        st.subheader("Upload a file")
        description = st.text_input("File Description")
        author = st.text_input("File Author")
        source = st.text_input("File Source")
        # data_type = st.text_input("Data Type")
        data_type = st.selectbox("Type de fichier", ["csv", "excel", "json"])
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx'])

        if uploaded_file and description and author and source and data_type:
            if st.button("Upload Data"):
                load_data_to_mongo(uploaded_file, uploaded_file.type.split('/')[1], description, author, source, data_type, start_date, end_date)

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
                
                # st.write("File Information:")
                # st.write(f"Author: {selected_metadata['author']}")
                # st.write(f"Description: {selected_metadata['description']}")
                # st.write(f"Source: {selected_metadata['source']}")
                # st.write(f"Start Date: {selected_metadata['start_date']}")
                # st.write(f"End Date: {selected_metadata['end_date']}")

                # Créer un DataFrame à partir des données
                data = {
                    'Field': ['Author', 'Description', 'Source', 'Start Date', 'End Date'],
                    'Value': [
                        selected_metadata['author'],
                        selected_metadata['description'],
                        selected_metadata['source'],
                        selected_metadata['start_date'],
                        selected_metadata['end_date']
                    ]
                }
                df_info = pd.DataFrame(data)

                # Afficher le tableau
                st.write("File Information:")
                st.dataframe(df_info)

                st.write(f"Displaying data for file: {selected_file_id}")
                
                file_data = list(collection.find({"file_id": selected_file_id}))
                if file_data:
                    df = pd.DataFrame(file_data)
                    st.dataframe(df)
                    # st.dataframe(edited_df)

                    try:
                        csv_data = df.to_csv(index=False, encoding='utf-8-sig')
                        st.download_button("Download Data as CSV", csv_data, "data.csv", "text/csv")
                    except OverflowError:
                        st.error("Error generating CSV file")

                    # try:
                    #     #json_data = df.to_json(orient='records', force_ascii=False).encode('utf-8')
                    #     json_data = df.to_json(orient='records', force_ascii=False)

                    #     # Convertir le JSON en bytes
                    #     json_bytes = json_data.encode('utf-8')
                    #     st.download_button("Download Data as JSON", json_bytes, "data.json", "application/json")
                    # except OverflowError:
                    #     st.error("Error generating JSON file")

                    # try:
                    #     excel_data = df.to_excel(index=False, engine='openpyxl').encode('utf-8')
                    #     st.download_button("Download Data as Excel", excel_data, "data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    # except OverflowError:
                    #     st.error("Error generating Excel file")

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
        # uploaded_update_file = st.file_uploader("Choose a CSV file with specific columns for update", type=['csv'])
        # if uploaded_update_file is not None:
        #     if st.button("Upload and Update Data"):
        #         upload_by_update(uploaded_update_file)

        metadata = list(metadata_collection.find())
        if metadata:
            df_metadata = pd.DataFrame(metadata)
            descriptions_authors = df_metadata['description'] + " - " + df_metadata['author']
            selected_description_author = st.selectbox("Select file description and author", descriptions_authors)

            if selected_description_author:
                selected_metadata = df_metadata[df_metadata['description'] + " - " + df_metadata['author'] == selected_description_author]
                selected_file_id = selected_metadata.iloc[0]['_id']
                
                st.write(f"Selected file ID for update: {selected_file_id}")

                uploaded_update_file = st.file_uploader("Choose a CSV file with specific columns for update", type=['csv'])
                if uploaded_update_file is not None:
                    if st.button("Upload and Update Data"):
                        upload_by_update(uploaded_update_file)
                

                file_data = list(collection.find({"file_id": selected_file_id}))
                if file_data:
                    df = pd.DataFrame(file_data)
                    st.write("Current Data:")
                

                    # Afficher les données dans un tableau éditable
                    edited_df = st.data_editor(df, use_container_width=True)

                    # Ajouter un bouton pour sauvegarder les modifications
                    if st.button("Save Changes"):
                        updates = edited_df.to_dict(orient='records')
                                                # Insertion des données dans MongoDB
                        

                        print("Données insérées avec succès dans MongoDB")
                                                
                        for update in updates:
                            if '_id' in update:

                                del update['_id']  # Supprimer l'_id pour éviter les conflits
                            collection.update_many({"file_id": selected_file_id}, {"$set": update})
                           

                        st.success("Données mises à jour avec succès dans MongoDB")
                    else:
                        st.warning(f"Aucune donnée trouvée pour le fichier avec file_id : {selected_file_id}")
                         # Ajouter un bouton pour télécharger les données en CSV
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="Télécharger les données en CSV",
                            data=csv,
                            file_name='data.csv',
                            mime='text/csv',
                        )

                    # st.write("Updated Data Preview:")
                    # st.dataframe(edited_df)
                else:
                    st.warning(f"No data found for file with file_id: {selected_file_id}")
                    
        else:
            st.warning("No files found in MongoDB")

    # elif page == "Upload by Update":
    #     st.subheader("Upload and Update Data")
    #     uploaded_update_file = st.file_uploader("Choose a CSV file with specific columns for update", type=['csv'])
    #     if uploaded_update_file is not None:
    #         if st.button("Upload and Update Data"):
    #             upload_by_update(uploaded_update_file)

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
            # Create a column combining description and author
            df_metadata['description_author'] = df_metadata['description'] + " - " + df_metadata['author']
            
            # Display the selectbox with combined description and author
            selected_description_author = st.selectbox("Select file description and author", df_metadata['description_author'])
            
            # Find the selected description and author
            selected_metadata = df_metadata[df_metadata['description_author'] == selected_description_author].iloc[0]
            
            # Display the selected file metadata
            st.write("Selected File Metadata:")
            st.write(selected_metadata)

            # Display the DataFrame of all metadata
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
