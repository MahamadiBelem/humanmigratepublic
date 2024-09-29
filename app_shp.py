import streamlit as st
import geopandas as gpd
import json
import pandas as pd
from pymongo import MongoClient
import os
import tempfile
import zipfile

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['data_apps']
files_collection = db['files']

# Fonction pour extraire les fichiers d'un zip
def extract_zip(file):
    temp_dir = tempfile.mkdtemp()  # Crée un répertoire temporaire
    with zipfile.ZipFile(file, "r") as zip_ref:
        zip_ref.extractall(temp_dir)
    return temp_dir

# Fonction pour charger des fichiers shapefiles depuis un zip
def upload_file_zip():
    uploaded_file = st.file_uploader("Choisissez un fichier zip contenant les fichiers shapefile (.shp, .shx, .dbf)", type=["zip"])
    if uploaded_file:
        temp_dir = extract_zip(uploaded_file)
        
        shp_files = [f for f in os.listdir(temp_dir) if f.endswith('.shp')]
        if not shp_files:
            st.error("Aucun fichier .shp trouvé dans le zip.")
            return None
        
        shp_file = shp_files[0]  # Supposez qu'il n'y ait qu'un seul fichier .shp
        required_files = {
            'shp': os.path.join(temp_dir, shp_file),
            'shx': os.path.join(temp_dir, shp_file.replace('.shp', '.shx')),
            'dbf': os.path.join(temp_dir, shp_file.replace('.shp', '.dbf')),
        }

        if not all(os.path.exists(path) for path in required_files.values()):
            st.error("Tous les fichiers nécessaires (.shp, .shx, .dbf) doivent être présents dans le zip.")
            return None
        
        return required_files
    return None

def process_shapefile(files):
    # Chargez le shapefile depuis les chemins extraits
    shp_path = files['shp']
    gdf = gpd.read_file(shp_path)
    
    # Convertir les données géométriques en latitude et longitude
    if gdf.geometry.name == 'geometry':
        gdf['latitude'] = gdf.geometry.centroid.y
        gdf['longitude'] = gdf.geometry.centroid.x
    return gdf

def process_json(file):
    data = json.load(file)
    return pd.DataFrame(data)

def save_to_mongo(file_info, gdf=None):
    if gdf is not None:
        # Convertir GeoDataFrame en GeoJSON et stocker dans MongoDB
        geojson = gdf.to_json()
        file_info['data'] = geojson
    files_collection.insert_one(file_info)

def display_map(gdf):
    if 'latitude' in gdf.columns and 'longitude' in gdf.columns:
        st.write("Carte des régions :")
        st.map(gdf[['latitude', 'longitude']])
    else:
        st.error("Les colonnes 'latitude' et 'longitude' sont nécessaires pour afficher la carte.")

def show_files():
    files = files_collection.find({})
    for file in files:
        st.write(file)

def load_default_shapefile():
    # Chargement du shapefile par défaut pour le Burkina Faso
    shapefile_path = "path/to/burkina_faso_regions.shp"  # Chemin vers le shapefile
    if os.path.exists(shapefile_path):
        gdf = gpd.read_file(shapefile_path)
        return gdf
    return None

# Interface utilisateur
def main():
    st.title("Application de Gestion de Données")

    # Charger le shapefile par défaut au démarrage
    default_gdf = load_default_shapefile()
    if default_gdf is not None:
        file_info = {
            "author": "System",
            "source": "Default",
            "visibility": "Public",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "description": "Shapefile des régions du Burkina Faso",
            "file_type": "Shapefile"
        }
        save_to_mongo(file_info, default_gdf)
        st.success("Shapefile par défaut enregistré dans MongoDB!")

    user_profile = st.selectbox("Sélectionnez votre profil", ["Admin", "User"])

    if user_profile == "User":
        st.write("Bienvenue, utilisateur !")
        st.write("Vous pouvez consulter et télécharger les fichiers publics ici.")
        show_files()

    elif user_profile == "Admin":
        st.write("Bienvenue, administrateur !")
        st.write("Téléchargez et gérez les fichiers ici.")

        files = upload_file_zip()
        if files:
            gdf = process_shapefile(files)
            display_map(gdf)

            st.text_input("Nom de l'auteur")
            st.text_input("Source du fichier")
            st.text_input("Visibilité")
            st.date_input("Date de début")
            st.date_input("Date de fin")
            st.text_area("Description du fichier")
            st.text_input("Type de fichier")
            
            if st.button("Sauvegarder dans MongoDB"):
                file_info = {
                    "author": st.text_input("Nom de l'auteur"),
                    "source": st.text_input("Source du fichier"),
                    "visibility": st.text_input("Visibilité"),
                    "start_date": str(st.date_input("Date de début")),
                    "end_date": str(st.date_input("Date de fin")),
                    "description": st.text_area("Description du fichier"),
                    "file_type": st.text_input("Type de fichier"),
                }
                save_to_mongo(file_info, gdf)
                st.success("Fichier enregistré avec succès!")

if __name__ == "__main__":
    main()
