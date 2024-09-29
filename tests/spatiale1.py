import os
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

# Exemple de jeu de données
data = [
    (2023, "Ouagadougou", "Bobo-Dioulasso", 1500, 12.3686, -1.5275, 11.1771, -4.2979),
    (2023, "Bobo-Dioulasso", "Ouagadougou", 1300, 11.1771, -4.2979, 12.3686, -1.5275),
    (2023, "Koudougou", "Ouagadougou", 800, 12.2565, -2.3731, 12.3686, -1.5275),
    (2023, "Ouagadougou", "Koudougou", 600, 12.3686, -1.5275, 12.2565, -2.3731),
    (2023, "Ouahigouya", "Ouagadougou", 500, 13.5739, -2.4219, 12.3686, -1.5275),
    (2023, "Ouagadougou", "Ouahigouya", 400, 12.3686, -1.5275, 13.5739, -2.4219),
    (2023, "Banfora", "Bobo-Dioulasso", 700, 10.6333, -4.7667, 11.1771, -4.2979),
    (2023, "Bobo-Dioulasso", "Banfora", 650, 11.1771, -4.2979, 10.6333, -4.7667),
    (2023, "Fada N'Gourma", "Ouagadougou", 900, 12.0605, 0.3584, 12.3686, -1.5275),
    (2023, "Ouagadougou", "Fada N'Gourma", 750, 12.3686, -1.5275, 12.0605, 0.3584)
]

columns = ["Year", "From_City", "To_City", "Migrants", "Latitude_From", "Longitude_From", "Latitude_To", "Longitude_To"]
df = spark.createDataFrame(data, columns)

# Afficher le schéma du DataFrame
df.printSchema()

# Afficher les premières lignes des données
df.show()

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

# Convertir les données Spark DataFrame en Pandas DataFrame pour la visualisation
data = df.toPandas()

# Créer la carte
map_ = create_map(data)

# Afficher la carte dans Streamlit
st.title("Migrations internes au Burkina Faso")
st.write("Cette carte montre les migrations internes entre les villes du Burkina Faso.")

# Afficher la carte avec Folium
folium_static(map_)
