import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
from bson.objectid import ObjectId
from streamlit_option_menu import option_menu
import random
from PIL import Image
from dataclasses import asdict
from streamlit_keycloak import login
import streamlit as st

from login import log_user

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['test1_db']
metadata_collection = db['metadata']


# ****************************************************************************************
# *****************************************************************************************
#This is the global part to be appear in all page
# Configuration de la page
st.set_page_config(page_title="Migration Data Hub", page_icon="🌍")


def main():
    st.subheader(f"Welcome {keycloak.user_info.get('preferred_username', 'User')}!")
    st.write("Here is your user information:")
    st.write(asdict(keycloak))
    if st.button("Disconnect"):
        keycloak.authenticated = False

st.title("Streamlit Keycloak example")
keycloak = login(
    url="http://localhost:8080",
    realm="humanmigration",
    client_id="humanmigration",
)

if keycloak.authenticated:
    st.write(keycloak.user_info)  # Debugging line
    main()
else:
    st.write("Authentication failed.")
    st.write("Debug Info:")
    st.write(asdict(keycloak))  # Additional debugging information
    st.write("Check the browser console for more details.")






st.markdown("""
    <style>
        div.block-container {
            padding: 1%; /* Remove default padding */
            margin: 1%; /* Remove default margin */
            max-width: 100%; /* Ensure container takes full width */
            width: 100%; /* Ensure container takes full width */
        }
        
        .header {
            padding: 10px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            width: 100%; /* Ensure header takes full width */
            box-sizing: border-box; /* Include padding in width calculation */
        }
        
        .marquee {
            background-color: #f0f8ff;
            color: #0b0b73;
            font-size: 20px;
            font-weight: bold;
            padding: 10px;
            white-space: nowrap;
            overflow: hidden;
            box-sizing: border-box; /* Include padding in width calculation */
            width: 100%; /* Ensure marquee takes full width */
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
        
    </div>
    <div class="marquee">
        <span>Welcome to the Big Data Management System!</span>
    </div>
""", unsafe_allow_html=True)


# log_user()

# Colonnes requises
required_columns = ['Year', 'Location', 'Origin', 'Region', 'Investment', 'Type', 'Destination', 'Age Group', 'Education Level', 'Rating', 'Migrants', 'raisons']

# Fonctionnalité 1: Charger un fichier
def charger_fichier():
    st.header("Charger un fichier")
    uploaded_file = st.file_uploader("Choisir un fichier CSV ou Excel", type=["csv", "xlsx"])
    
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Vérifier si les colonnes requises sont présentes
        if all(column in df.columns for column in required_columns):
            st.success("Le fichier contient toutes les colonnes requises.")
            
            type_fichier = st.text_input("Type de fichier")
            auteur = st.text_input("Auteur")
            description = st.text_area("Description")
            date_chargement = st.date_input("Date de chargement", datetime.now())
            date_fin = st.date_input("Date de fin")
            visibilite = st.selectbox("Visibilité", ["Public", "Privé"])
            
            if st.button("Enregistrer"):
                metadata = {
                    "type_fichier": type_fichier,
                    "auteur": auteur,
                    "description": description,
                    "date_chargement": date_chargement.strftime("%Y-%m-%d"),
                    "date_fin": date_fin.strftime("%Y-%m-%d"),
                    "visibilite": visibilite,
                    "data": df.to_dict(orient="records")
                }
                metadata_collection.insert_one(metadata)
                st.success("Fichier enregistré avec succès!")
        else:
            st.error("Le fichier ne contient pas toutes les colonnes requises.")

# Fonctionnalité 2: Mettre à jour un fichier
def mettre_a_jour_fichier():
    st.header("Mettre à jour un fichier")
    fichiers = metadata_collection.find()

        # Générer fichier_ids avec concaténation
    # fichier_ids = [
    #     f"{fichier['auteur']}_{fichier['date_chargement'][:4]}_{random.randint(1000, 9999)}"
    #     for fichier in fichiers
    # ]

    fichier_ids = [str(fichier["_id"]) for fichier in fichiers]
    fichier_choisi = st.selectbox("Choisir un fichier à mettre à jour", fichier_ids)
    
    if fichier_choisi:
        fichier = metadata_collection.find_one({"_id": ObjectId(fichier_choisi)})
        type_fichier = st.text_input("Type de fichier", fichier["type_fichier"])
        auteur = st.text_input("Auteur", fichier["auteur"])
        description = st.text_area("Description", fichier["description"])
        date_chargement = st.date_input("Date de chargement", datetime.strptime(fichier["date_chargement"], "%Y-%m-%d"))
        date_fin = st.date_input("Date de fin", datetime.strptime(fichier["date_fin"], "%Y-%m-%d"))
        visibilite = st.selectbox("Visibilité", ["Public", "Privé"], index=["Public", "Privé"].index(fichier["visibilite"]))
        
        uploaded_file = st.file_uploader("Choisir un fichier CSV ou Excel pour mise à jour", type=["csv", "xlsx"])
        
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Vérifier si les colonnes requises sont présentes
            if all(column in df.columns for column in required_columns):
                st.success("Le fichier contient toutes les colonnes requises.")
                
                if st.button("Mettre à jour"):
                    metadata_collection.update_one(
                        {"_id": ObjectId(fichier_choisi)},
                        {"$set": {
                            "type_fichier": type_fichier,
                            "auteur": auteur,
                            "description": description,
                            "date_chargement": date_chargement.strftime("%Y-%m-%d"),
                            "date_fin": date_fin.strftime("%Y-%m-%d"),
                            "visibilite": visibilite,
                            "data": df.to_dict(orient="records")
                        }}
                    )
                    st.success("Fichier mis à jour avec succès!")
            else:
                st.error("Le fichier ne contient pas toutes les colonnes requises.")

# Fonctionnalité 3: Supprimer un fichier
def supprimer_fichier():
    st.header("Supprimer un fichier")
    fichiers = metadata_collection.find()
    fichier_ids = [str(fichier["_id"]) for fichier in fichiers]
    fichier_choisi = st.selectbox("Choisir un fichier à supprimer", fichier_ids)
    
    if fichier_choisi and st.button("Supprimer"):
        metadata_collection.delete_one({"_id": ObjectId(fichier_choisi)})
        st.success("Fichier supprimé avec succès!")



def consulter_donnees_tab():
    st.header("Consulter les données")
    fichiers = metadata_collection.find()
    fichier_ids = [str(fichier["_id"]) for fichier in fichiers]
    fichier_choisi = st.selectbox("Choisir un fichier à consulter", fichier_ids)
    
    if fichier_choisi:
        fichier = metadata_collection.find_one({"_id": ObjectId(fichier_choisi)})
        df = pd.DataFrame(fichier["data"])
        st.write(df)


def consulter_metadata():
    st.header("Consulter les métadonnées des fichiers")

    # Retrieve all files from the collection
    fichiers = metadata_collection.find()

    # Create a list of file descriptions or IDs for the selectbox
    fichier_ids = [f"{fichier['auteur']} - {fichier['date_chargement']}" for fichier in fichiers]
    
    # Select a file to view its metadata
    fichier_choisi = st.selectbox("Choisir un fichier pour voir les métadonnées", fichier_ids)
    
    if fichier_choisi:
        # Find the selected file's metadata
        fichier = metadata_collection.find_one({"auteur": fichier_choisi.split(' - ')[0], "date_chargement": fichier_choisi.split(' - ')[1]})
        
        if fichier:
            # Display metadata
            st.subheader("Métadonnées du fichier")
            st.text(f"Type de fichier: {fichier['type_fichier']}")
            st.text(f"Auteur: {fichier['auteur']}")
            st.text(f"Description: {fichier['description']}")
            st.text(f"Date de chargement: {fichier['date_chargement']}")
            st.text(f"Date de fin: {fichier['date_fin']}")
            st.text(f"Visibilité: {fichier['visibilite']}")
            
            # Optionally show the data stored in the file
            if st.checkbox("Afficher les données du fichier"):
                df = pd.DataFrame(fichier['data'])
                st.dataframe(df)
        else:
            st.error("Fichier non trouvé.")
# Fonctionnalité 4: Consulter les données
def consulter_donnees():
    st.header("Consulter les données")
    fichiers = metadata_collection.find()
    
    fichier_ids = [str(fichier["_id"]) for fichier in fichiers]
    fichier_choisi = st.selectbox("Choisir un fichier à consulter", fichier_ids)
    
    if fichier_choisi:
        fichier = metadata_collection.find_one({"_id": ObjectId(fichier_choisi)})
        df = pd.DataFrame(fichier["data"])


        # # Sidebar for selecting visualization type
        # st.sidebar.title('Select Visualization Type')
        # visualization_type = option_menu(
        #     'Choose a chart type:',
        #     ['Tabulaire', 'Bar Chart', 'Line Chart', 'Area Chart'],
        #     icons=['list', 'bar-chart', 'line-chart', 'area-chart'],
        #     menu_icon="cast",
        #     default_index=0,
        #     orientation='vertical'
        # )
        with st.sidebar:
            # st.title('Select View Type')
            visualization_type = option_menu(
                'Choose View:',
                ['Tabulaire', 'Bar Chart', 'Line Chart', 'Area Chart'],
                icons=['list', 'bar-chart', 'line-chart', 'area-chart'],
                menu_icon="cast",
                default_index=0,
                orientation='vertical'
            )

        # Display the selected chart type
        st.write(f'You selected: {visualization_type}')

        if visualization_type == 'Tabulaire':
            df = pd.DataFrame(fichier["data"])
            st.write(df)

        # Bar Chart
        if visualization_type == 'Bar Chart':
            st.bar_chart(df.set_index('Year')[['Migrants']])

        # Line Chart
        elif visualization_type == 'Line Chart':
            st.line_chart(df.set_index('Year')[['Migrants']])

        # Area Chart
        elif visualization_type == 'Area Chart':
            st.area_chart(df.set_index('Year')[['Migrants']])

        # Scatter Plot
        elif visualization_type == 'Scatter Plot':
            st.scatter_chart(df.set_index('Year')[['Migrants']])

        # # Histogram
        # elif visualization_type == 'Histogram':
        #     st.hist_chart(df.set_index('Year')[['Migrants']])

        # # Pie Chart
        # elif visualization_type == 'Pie Chart':
        #     st.pie_chart(df.set_index('Year')[['Migrants']])

        # # Box Plot
        # elif visualization_type == 'Box Plot':
        #     st.box_chart(df.set_index('Year')[['Migrants']])

        # # Heatmap
        # elif visualization_type == 'Heatmap':
        #     st.heatmap(df.set_index('Year')[['Migrants']])


# def afficher_details_fichier():
#     st.header("Détails du fichier")

#     # Retrieve the file ID from query parameters
#     query_params = st.experimental_get_query_params()
#     if "file_id" in query_params:
#         file_id = query_params["file_id"][0]
        
#         # Fetch the file metadata from MongoDB
#         fichier = metadata_collection.find_one({"_id": ObjectId(file_id)})
        
#         if fichier:
#             # Display the metadata
#             st.subheader("Métadonnées du fichier")
#             st.text(f"Type de fichier: {fichier['type_fichier']}")
#             st.text(f"Auteur: {fichier['auteur']}")
#             st.text(f"Description: {fichier['description']}")
#             st.text(f"Date de chargement: {fichier['date_chargement']}")
#             st.text(f"Date de fin: {fichier['date_fin']}")
#             st.text(f"Visibilité: {fichier['visibilite']}")
            
#             # Display the data in the file (optional)
#             if st.checkbox("Afficher les données du fichier"):
#                 df = pd.DataFrame(fichier['data'])
#                 st.dataframe(df)
#         else:
#             st.error("Fichier non trouvé.")
#     else:
#         st.error("Aucun fichier sélectionné.")




# def liste_fichiers():
#     st.header("Liste des fichiers disponibles")

#     # Retrieve all files from the collection
#     fichiers = list(metadata_collection.find())
    
#     # Convert the list of files into a DataFrame for displaying in a table
#     fichiers_df = pd.DataFrame(fichiers, columns=["_id", "type_fichier", "auteur", "date_chargement", "description", "visibilite"])

#     # Remove the MongoDB ObjectId for simplicity in display
#     fichiers_df["_id"] = fichiers_df["_id"].apply(str)

#     # Create a new column with "Voir détails" links
#     fichiers_df['Voir détails'] = fichiers_df["_id"].apply(
#         lambda id: f'<a href="/?file_id={id}">Voir détails</a>'
#     )

#     # Display the table with links as buttons
#     st.write(fichiers_df[['type_fichier', 'auteur', 'date_chargement', 'description', 'visibilite', 'Voir détails']].to_html(escape=False), unsafe_allow_html=True)


#     if "file_id" in st.experimental_get_query_params():
#         afficher_details_fichier()
#     else:
#         liste_fichiers()



# # Function to show details of the selected file
# def afficher_details_fichier():
#     st.header("Détails du fichier")

#     # Retrieve the file ID from session state query parameters
#     query_params = st.session_state.query_params
#     if "file_id" in query_params:
#         file_id = query_params["file_id"]
        
#         # Fetch the file metadata from MongoDB
#         fichier = metadata_collection.find_one({"_id": ObjectId(file_id)})
        
#         if fichier:
#             # Display the metadata
#             st.subheader("Métadonnées du fichier")
#             st.text(f"Type de fichier: {fichier['type_fichier']}")
#             st.text(f"Auteur: {fichier['auteur']}")
#             st.text(f"Description: {fichier['description']}")
#             st.text(f"Date de chargement: {fichier['date_chargement']}")
#             st.text(f"Date de fin: {fichier['date_fin']}")
#             st.text(f"Visibilité: {fichier['visibilite']}")
            
#             # Display the data in the file (optional)
#             if st.checkbox("Afficher les données du fichier"):
#                 df = pd.DataFrame(fichier['data'])
#                 st.dataframe(df)
#         else:
#             st.error("Fichier non trouvé.")
#     else:
#         st.error("Aucun fichier sélectionné.")





# def liste_fichiers():
#     st.header("Liste des fichiers disponibles")

#     # Retrieve all files from the collection
#     fichiers = list(metadata_collection.find())
    
#     # Convert the list of files into a DataFrame
#     fichiers_df = pd.DataFrame(fichiers, columns=["_id", "type_fichier", "auteur", "date_chargement", "description", "visibilite"])

#     # Remove the MongoDB ObjectId for simplicity in display
#     fichiers_df["_id"] = fichiers_df["_id"].apply(str)

#     # Create a new column with "Voir détails" links
#     fichiers_df['Voir détails'] = fichiers_df["_id"].apply(
#         lambda id: f'<a href="?file_id={id}" target="_self">Voir détails</a>'
#     )

#     # Display the table with the new "Voir détails" column
#     st.write(fichiers_df[['type_fichier', 'auteur', 'date_chargement', 'description', 'visibilite', 'Voir détails']].to_html(escape=False), unsafe_allow_html=True)

#     query_params = st.session_state.query_params

#     if "file_id" in query_params:
#         afficher_details_fichier()  # Display file details if a file_id is set
#     else:
#         liste_fichiers()  # Display the list of files



# def afficher_details_fichier():
#     st.header("Détails du fichier")

#     # Retrieve the file ID from query parameters
#     query_params = st.experimental_get_query_params()
    
#     if "file_id" in query_params:
#         file_id = query_params["file_id"][0]  # query_params returns a list, so take the first element
        
        
#         # Fetch the file metadata from MongoDB
#         fichier = metadata_collection.find_one({"_id": ObjectId(file_id)})
        
#         if fichier:
#             # Display the metadata
#             st.subheader("Métadonnées du fichier")
#             st.text(f"Type de fichier: {fichier['type_fichier']}")
#             st.text(f"Auteur: {fichier['auteur']}")
#             st.text(f"Description: {fichier['description']}")
#             st.text(f"Date de chargement: {fichier['date_chargement']}")
#             st.text(f"Date de fin: {fichier['date_fin']}")
#             st.text(f"Visibilité: {fichier['visibilite']}")
            
#             # Display the data in the file (optional)
#             if st.checkbox("Afficher les données du fichier"):
#                 df = pd.DataFrame(fichier['data'])
#                 st.dataframe(df)
#         else:
#             st.error("Fichier non trouvé.")
#     else:
#         st.error("Aucun fichier sélectionné.")

#         # Main application logic



# def liste_fichiers():
#     st.header("Liste des fichiers disponibles")

#     # Retrieve all files from the collection
#     fichiers = list(metadata_collection.find())
    
#     # Convert the list of files into a DataFrame
#     fichiers_df = pd.DataFrame(fichiers, columns=["_id", "type_fichier", "auteur", "date_chargement", "description", "visibilite"])

#     # Remove the MongoDB ObjectId for simplicity in display
#     fichiers_df["_id"] = fichiers_df["_id"].apply(str)

#     # Create a new column with "Voir détails" links
#     fichiers_df['Voir détails'] = fichiers_df["_id"].apply(
#         lambda id: f'<a href="?file_id={id}">Voir détails</a>'
#     )

#     # Display the table with the new "Voir détails" column
#     st.write(fichiers_df[['type_fichier', 'auteur', 'date_chargement', 'description', 'visibilite', 'Voir détails']].to_html(escape=False), unsafe_allow_html=True)
#     query_params = st.experimental_get_query_params()

#     if "file_id" in query_params:
#         afficher_details_fichier()  # Display file details if a file_id is set
#     else:
#         liste_fichiers()  # Display the list of files




# # Function to display file details when a file is selected
# def afficher_details_fichier(file_id):
#     st.header("Détails du fichier")
    
#     # Fetch the file metadata from MongoDB
#     fichier = metadata_collection.find_one({"_id": ObjectId(file_id)})
    
#     if fichier:
#         # Display the metadata
#         st.subheader("Métadonnées du fichier")
#         st.text(f"Type de fichier: {fichier['type_fichier']}")
#         st.text(f"Auteur: {fichier['auteur']}")
#         st.text(f"Description: {fichier['description']}")
#         st.text(f"Date de chargement: {fichier['date_chargement']}")
#         st.text(f"Date de fin: {fichier['date_fin']}")
#         st.text(f"Visibilité: {fichier['visibilite']}")
        
#         # Option to display file data (optional)
#         if st.checkbox("Afficher les données du fichier"):
#             df = pd.DataFrame(fichier['data'])
#             st.dataframe(df)
#     else:
#         st.error("Fichier non trouvé.")

# # Function to display the list of available files with buttons in a table
# def liste_fichiers():
#     st.header("Liste des fichiers disponibles")

#     # Retrieve all files from the collection
#     fichiers = list(metadata_collection.find())
    
#     # Convert the list of files into a DataFrame
#     fichiers_df = pd.DataFrame(fichiers, columns=["_id", "type_fichier", "auteur", "date_chargement", "description", "visibilite"])

#     # Remove the MongoDB ObjectId for simplicity in display
#     fichiers_df["_id"] = fichiers_df["_id"].apply(str)

#     # Display file information in a table format
#     st.subheader("Tableau des fichiers")
#     for index, row in fichiers_df.iterrows():
#         col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 3, 2, 2])
        
#         # Display file details in columns
#         with col1:
#             st.text(row['type_fichier'])
#         with col2:
#             st.text(row['auteur'])
#         with col3:
#             st.text(row['date_chargement'])
#         with col4:
#             st.text(row['description'])
#         with col5:
#             st.text(row['visibilite'])
        
#         # Add a "Voir détails" button for each file
#         with col6:
#             if st.button("Voir détails", key=row["_id"]):
#                 afficher_details_fichier(row["_id"])

# # Main application logic
# # liste_fichiers()


def afficher_details_fichier(file_id):
    # Center the header
    st.write("""
        <div style="display: flex; justify-content: center; margin: 20px;">
            <h1>Détails du fichier</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Fetch the file metadata from MongoDB
    fichier = metadata_collection.find_one({"_id": ObjectId(file_id)})
    
    if fichier:
        # Display the metadata in a table
        # st.subheader("Métadonnées du fichier")
        st.write("""
            <div style="display: flex; justify-content: center; margin: 20px;">
                <table style="border-collapse: collapse; width: 50%;">
                    <tr>
                        <th style="border: 1px solid black; padding: 8px;">Type de fichier</th>
                        <td style="border: 1px solid black; padding: 8px;">{type_fichier}</td>
                    </tr>
                    <tr>
                        <th style="border: 1px solid black; padding: 8px;">Auteur</th>
                        <td style="border: 1px solid black; padding: 8px;">{auteur}</td>
                    </tr>
                    <tr>
                        <th style="border: 1px solid black; padding: 8px;">Description</th>
                        <td style="border: 1px solid black; padding: 8px;">{description}</td>
                    </tr>
                    <tr>
                        <th style="border: 1px solid black; padding: 8px;">Date de chargement</th>
                        <td style="border: 1px solid black; padding: 8px;">{date_chargement}</td>
                    </tr>
                    <tr>
                        <th style="border: 1px solid black; padding: 8px;">Date de fin</th>
                        <td style="border: 1px solid black; padding: 8px;">{date_fin}</td>
                    </tr>
                    <tr>
                        <th style="border: 1px solid black; padding: 8px;">Visibilité</th>
                        <td style="border: 1px solid black; padding: 8px;">{visibilite}</td>
                    </tr>
                </table>
            </div>
        """.format(
            type_fichier=fichier['type_fichier'],
            auteur=fichier['auteur'],
            description=fichier['description'],
            date_chargement=fichier['date_chargement'],
            date_fin=fichier['date_fin'],
            visibilite=fichier['visibilite']
        ), unsafe_allow_html=True)
        
        # Option to display file data (optional)
        if st.checkbox("Afficher les données du fichier"):
            df = pd.DataFrame(fichier['data'])
            st.dataframe(df)
    else:
        st.error("Fichier non trouvé.")



# Function to display file details when a file is selected
def liste_fichiers():
    st.subheader("Available Dataset")
    st.write("""
        <div style="background-color: #3498db; padding: 7px;">
            <h3 style="color: white; text-align: center;">
                View Different Data from institutions and researchers around the world
            </h3>
        </div>
    """, unsafe_allow_html=True)

    # Retrieve all files from the collection
    fichiers = list(metadata_collection.find())
    
    # Convert the list of files into a DataFrame
    fichiers_df = pd.DataFrame(fichiers, columns=["_id", "type_fichier", "auteur", "date_chargement", "description", "visibilite"])

    # Remove the MongoDB ObjectId for simplicity in display
    fichiers_df["_id"] = fichiers_df["_id"].apply(str)

    # Create a column with "Voir détails" links using HTML and query parameters
    fichiers_df['Voir détails'] = fichiers_df["_id"].apply(
        lambda id: f'<a href="?file_id={id}" target="_self">Voir détails</a>'
    )

    # Display the table using st.write with the HTML-rendered links
    st.write("""
        <div style="display: flex; justify-content: center; margin: 20px;">
            {table}
        </div>
    """.format(table=fichiers_df[['type_fichier', 'auteur', 'date_chargement', 'description', 'visibilite', 'Voir détails']].to_html(escape=False)), unsafe_allow_html=True)

    # Check if a file_id is passed in query parameters
    query_params = st.experimental_get_query_params()
    if "file_id" in query_params:
        file_id = query_params["file_id"][0]
        afficher_details_fichier(file_id)


# Main application logic
# liste_fichiers()

# Function to display the welcome page
def display_welcome_page():
    # Load the background image
    image = Image.open("img5.jpg")

    # Title and slogan
    st.markdown("<h1 style='text-align: center; color: #004d99;'>Migration Data Hub</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #0066cc;'>Votre portail pour explorer, analyser et visualiser les données migratoires.</h2>", unsafe_allow_html=True)
    
    st.header("Overview")
    st.write("""
        <div style="text-align: center;">
            Dealing with population migration is a significant challenge for policymakers, especially in developing countries. The lack of relevant data and tools hinders effective migration policy formulation and implementation.
        </div>
    """, unsafe_allow_html=True)

    # Show the background image
    st.image(image, use_column_width=True)

    st.write("""
        <h2 style="text-align: center; color: #e74c3c;">
            Challenges
        </h2>
    """, unsafe_allow_html=True)
    # st.header("Challenges")
    st.write("""
        <div style="text-align: center;">
            1. <span style="color: #e74c3c;">**Data Fragmentation**</span>: Researchers collect data in various formats and for different purposes, leading to fragmented information.
            2. <span style="color: #e74c3c;">**Lack of Analytical Tools**</span>: Despite the large volumes of data, there are no tools to analyze and provide decision-making indicators, recommendations, and predictions.
            3. <span style="color: #e74c3c;">**Redundancy and Waste**</span>: Data is often collected multiple times, wasting time and resources without adding value.
            4. <span style="color: #e74c3c;">**Diverse Expert Opinions**</span>: Experts have differing views on migration issues, which need to be integrated for a comprehensive understanding.</br>
        </div>
    """, unsafe_allow_html=True)


    st.write("""
        <h2 style="text-align: center; color: #e74c3c;">
            Proposed Big Data Solution
        </h2>
    """, unsafe_allow_html=True)
    

    
    # st.header("Proposed Big Data Solution") 
    st.write("""
        <div style="text-align: center;">
            - <span style="color: #e74c3c;">Integration Framework</span>: Develop a big data platform using Hadoop to integrate and visualize migration data.
            - <span style="color: #e74c3c;">Data Sources</span>: Include data on climate, demography, geography, scientific evolution, soils, households, socio-economic activities, and administrative organization.
            - <span style="color: #e74c3c;">Technologies</span>: Combine several migration databases and ontology databases.
            - <span style="color: #e74c3c;">Processing</span>: Utilize MapReduce paradigm for processing and visualization tools to display indicators and migration trends.
        </div>
    """, unsafe_allow_html=True)


    st.write("""
        <h2 style="text-align: center; color: #e74c3c;">
            Goals
        </h2>
    """, unsafe_allow_html=True)

    # st.header("Goals")
    st.write("""
        <div style="text-align: center;">
            <span style="color: #e74c3c;">Comprehensive Data Integration</span>: Create a unified framework for acquiring and integrating migration data.
            <span style="color: #e74c3c;">Enhanced Decision-Making</span>: Provide tools for analyzing data and visualizing relevant decision indicators and recommendations.
            <span style="color: #e74c3c;">Efficient Resource Use</span>: Reduce redundancy and improve the value of collected data. <br><br><br><br><br>
        </div>
    """, unsafe_allow_html=True)


# # Menu de navigation
# menu = ["Charger un fichier", "Mettre à jour un fichier", "Supprimer un fichier", "Consulter les données"]
# choix = st.sidebar.selectbox("Menu", menu)

# Add the new option in the sidebar menu
st.session_state.logged_in = False
with st.sidebar:
    choix = option_menu(
        "Menu", 
        ["Welcome dashboard", "Charger un fichier", "Mettre à jour un fichier", "Supprimer un fichier", "Consulter les données", "Consulter les métadonnées"],
        icons=["cloud-upload","cloud-upload", "pencil", "trash", "table", "info-circle"],
        menu_icon="cast",
        default_index=0,
        orientation='vertical'
    )

# Add functionality for the new metadata consultation option

if choix == "Welcome dashboard":
    liste_fichiers()
# if choix == "Dashboard":
#     display_welcome_page()
if choix == "Charger un fichier" and not st.session_state.logged_in:
    charger_fichier()
elif choix == "Mettre à jour un fichier":
    mettre_a_jour_fichier()
elif choix == "Supprimer un fichier":
    supprimer_fichier()
elif choix == "Consulter les données":
    consulter_donnees()
elif choix == "Consulter les métadonnées":
    consulter_metadata()

    