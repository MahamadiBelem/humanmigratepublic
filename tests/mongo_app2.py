import streamlit as st
from pymongo import MongoClient
import pandas as pd


# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Sélectionner la base de données et la collection
db = client['migration_externe']
collection = db['test_import']


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

# Interface utilisateur Streamlit
st.title("Chargement et affichage des données MongoDB")

# Option pour télécharger un fichier CSV ou Excel
uploaded_file = st.file_uploader("Choisissez un fichier CSV ou Excel", type=['csv', 'xlsx'])

if uploaded_file is not None:
    file_type = uploaded_file.name.split('.')[-1]
    if st.button("Charger dans MongoDB"):
        load_data_to_mongo(uploaded_file, file_type)

# Option pour afficher les données de MongoDB
if st.button("Afficher les données de MongoDB"):
    data = list(collection.find())
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df)
    else:
        st.warning("Aucune donnée trouvée dans MongoDB")

# Optionnel : Afficher des statistiques basiques
if st.button("Afficher le résumé des données"):
    data = list(collection.find())
    if data:
        df = pd.DataFrame(data)
        st.write(df.describe())
    else:
        st.warning("Aucune donnée trouvée dans MongoDB")
