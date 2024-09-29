import os
import pandas as pd
import pyspark
from pyspark.sql import SparkSession
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

# Configurer les variables d'environnement pour PySpark
os.environ["SPARK_LOCAL_IP"] = "127.0.0.1"
os.environ["PYSPARK_PYTHON"] = "python"  # Assurez-vous que "python" est accessible via PATH
os.environ["PYSPARK_DRIVER_PYTHON"] = "python"

# Créer une session Spark
spark = SparkSession.builder.appName("MigrationData").getOrCreate()

# Fonction pour créer une carte avec les migrations
def create_map(data):
    m = folium.Map(location=[12.3714, -1.5197], zoom_start=6)  # Centré sur le Burkina Faso

    marker_cluster = MarkerCluster().add_to(m)

    for index, row in data.iterrows():
        folium.Marker(
            location=[row['Latitude_From'], row['Longitude_From']],
            popup=f"From: {row['From_City']}",
            icon=folium.Icon(color="blue")
        ).add_to(marker_cluster)

        folium.Marker(
            location=[row['Latitude_To'], row['Longitude_To']],
            popup=f"To: {row['To_City']}",
            icon=folium.Icon(color="red")
        ).add_to(marker_cluster)

        folium.PolyLine(
            locations=[(row['Latitude_From'], row['Longitude_From']), (row['Latitude_To'], row['Longitude_To'])],
            color="green"
        ).add_to(m)

    return m

# Fonction pour lire le fichier téléchargé
def load_data(file):
    if file.type == "text/csv":
        df = pd.read_csv(file)
    elif file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        df = pd.read_excel(file)
    else:
        st.error("Format de fichier non supporté!")
        return None
    
    return df

# Interface utilisateur pour télécharger un fichier
st.title("Migrations internes au Burkina Faso")
st.write("Téléchargez un fichier CSV ou Excel contenant les données de migration.")

uploaded_file = st.file_uploader("Choisissez un fichier", type=["csv", "xlsx"])

if uploaded_file is not None:
    data = load_data(uploaded_file)

    if data is not None:
        st.write("Aperçu des données téléchargées:")
        st.write(data.head())

        # Convertir les données Pandas DataFrame en Spark DataFrame
        spark_df = spark.createDataFrame(data)

        # Afficher le schéma du DataFrame Spark
        spark_df.printSchema()

        # Créer la carte
        map_ = create_map(data)

        # Afficher la carte avec Folium
        st.write("Carte des migrations internes:")
        folium_static(map_)
