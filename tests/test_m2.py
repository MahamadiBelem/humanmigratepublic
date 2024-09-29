import streamlit as st
import pandas as pd
import pymongo
from pymongo import MongoClient
import datetime

# # Connexion à MongoDB
# @st.cache_resource
# def init_connection():
#     return MongoClient(st.secrets["mongo"]["host"], 
#                        st.secrets["mongo"]["port"], 
#                        username=st.secrets["mongo"]["username"], 
#                        password=st.secrets["mongo"]["password"])

client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase2"]
collection = db["mycollection2"]

# Fonction pour uploader un fichier
def upload_file(file, description, author, visibility, start_date, end_date, file_type):
    if file_type == 'csv':
        df = pd.read_csv(file)
    elif file_type == 'excel':
        df = pd.read_excel(file)
    # elif file_type == 'json':
    #     df = pd.read_json(file)
    else:
        st.error("Type de fichier non supporté")
        return

    data = {
        "description": description,
        "author": author,
        "visibility": visibility,
        "upload_date": datetime.datetime.now(),
        "start_date": start_date,
        "end_date": end_date,
        "file_type": file_type,
        "data": df.to_dict(orient='records')
    }
    collection.insert_one(data)
    st.success("Fichier uploadé avec succès")

# Fonction pour mettre à jour un fichier
def update_file(file_id, file, description, author, visibility, start_date, end_date, file_type):
    if file_type == 'csv':
        df = pd.read_csv(file)
    elif file_type == 'excel':
        df = pd.read_excel(file)
    elif file_type == 'json':
        df = pd.read_json(file)
    else:
        st.error("Type de fichier non supporté")
        return

    data = {
        "description": description,
        "author": author,
        "visibility": visibility,
        "upload_date": datetime.datetime.now(),
        "start_date": start_date,
        "end_date": end_date,
        "file_type": file_type,
        "data": df.to_dict(orient='records')
    }
    collection.update_one({"_id": file_id}, {"$set": data})
    st.success("Fichier mis à jour avec succès")

# Fonction pour supprimer un fichier
def delete_file(file_id):
    collection.delete_one({"_id": file_id})
    st.success("Fichier supprimé avec succès")

# Fonction pour afficher et télécharger un fichier
def display_file(file_id):
    file = collection.find_one({"_id": file_id})
    if file:
        df = pd.DataFrame(file["data"])
        st.write(df)
        st.download_button(label="Télécharger le fichier", data=df.to_csv(index=False), file_name="file.csv")
    else:
        st.error("Fichier non trouvé")

# Interface utilisateur
st.title("Gestion de fichiers avec MongoDB")

# Upload de fichier
st.header("Uploader un fichier")
uploaded_file = st.file_uploader("Choisissez un fichier", type=["csv", "excel", "json"])
description = st.text_input("Description")
author = st.text_input("Auteur")
visibility = st.selectbox("Visibilité", ["Public", "Privé"])
start_date = st.date_input("Date de début")
end_date = st.date_input("Date de fin")
file_type = st.selectbox("Type de fichier", ["csv", "excel", "json"])

if st.button("Uploader"):
    upload_file(uploaded_file, description, author, visibility, start_date, end_date, file_type)

# Mise à jour de fichier
st.header("Mettre à jour un fichier")
file_id = st.text_input("ID du fichier à mettre à jour")
uploaded_file = st.file_uploader("Choisissez un fichier pour mise à jour", type=["csv", "excel", "json"])

if st.button("Mettre à jour"):
    update_file(file_id, uploaded_file, description, author, visibility, start_date, end_date, file_type)

# Suppression de fichier
st.header("Supprimer un fichier")
file_id = st.text_input("ID du fichier à supprimer")

if st.button("Supprimer"):
    delete_file(file_id)

# Affichage et téléchargement de fichier
st.header("Afficher et télécharger un fichier")
file_id = st.text_input("ID du fichier à afficher")

if st.button("Afficher"):
    display_file(file_id)
