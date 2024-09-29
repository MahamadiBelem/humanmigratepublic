import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum, avg
import os
import time

# Chemin vers le répertoire de stockage des fichiers
upload_directory = "C:\\fichier"

def create_spark_session(retries=5, delay=2):
    for attempt in range(retries):
        try:
            # Configuration pour Windows
            spark = SparkSession.builder \
                .appName("Migration Data Analysis") \
                .config("spark.executorEnv.PYTHON", "python") \
                .config("spark.driverEnv.PYTHON", "python") \
                .getOrCreate()
            return spark
        except Exception as e:
            st.warning(f"Tentative {attempt+1} de création de la session Spark échouée : {e}")
            time.sleep(delay)
    st.error("Impossible de créer une session Spark après plusieurs tentatives.")
    return None

# Créer une session Spark avec des tentatives de réessai
spark = create_spark_session()

if spark:
    # Vérifier si le répertoire upload_directory existe, sinon le créer
    if not os.path.exists(upload_directory):
        os.makedirs(upload_directory)

    # Interface Streamlit
    st.title("Migration Data Analysis")

    # Option pour uploader un fichier dans la barre latérale
    uploaded_file = st.sidebar.file_uploader("Choisir un fichier CSV", type="csv")

    if uploaded_file:
        try:
            # Enregistrer le fichier uploadé dans le répertoire upload_directory
            file_path = os.path.join(upload_directory, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.sidebar.success(f"Fichier '{uploaded_file.name}' uploadé et enregistré avec succès!")

            # Lire le fichier CSV avec pandas
            data = pd.read_csv(file_path)
            st.write(data)
            
            # Convertir le DataFrame pandas en DataFrame Spark
            df = spark.createDataFrame(data)
            st.write("DataFrame Spark créé avec succès")

            # Afficher les noms des colonnes disponibles dans le DataFrame Spark
            st.write("Colonnes disponibles dans le DataFrame Spark:", df.columns)

            # Vérifiez les noms des colonnes et utilisez les noms exacts
            if 'Year' in df.columns and 'Destination Country' in df.columns and 'Migrants' in df.columns:
                st.write("Analyse des flux migratoires : migrants par année et pays de destination")
                migration_by_year_destination = df.groupBy("Year", "Destination Country").agg(spark_sum("Migrants").alias("Total Migrants"))
                migration_by_year_destination_pd = migration_by_year_destination.toPandas()
                st.write("Analyse des flux migratoires réussie")

                # Création du graphe pour migrants par année et pays de destination
                fig, ax = plt.subplots(figsize=(10, 6))
                for key, grp in migration_by_year_destination_pd.groupby(['Destination Country']):
                    ax = grp.plot(ax=ax, kind='line', x='Year', y='Total Migrants', label=key)
                plt.title('Total Migrants by Year and Destination Country')
                plt.xlabel('Year')
                plt.ylabel('Total Migrants')
                plt.legend(loc='best')
                st.pyplot(fig)
            else:
                st.warning("Les colonnes nécessaires pour l'analyse des flux migratoires ne sont pas disponibles dans le DataFrame.")

            if 'Age Group' in df.columns and 'Gender' in df.columns:
                st.write("Analyse démographique : migrants par groupe d'âge et genre")
                migration_by_age_gender = df.groupBy("Age Group", "Gender").agg(spark_sum("Migrants").alias("Total Migrants"))
                migration_by_age_gender_pd = migration_by_age_gender.toPandas()
                st.write("Analyse démographique réussie")

                # Création du graphe pour migrants par groupe d'âge et genre
                fig, ax = plt.subplots(figsize=(10, 6))
                for key, grp in migration_by_age_gender_pd.groupby(['Gender']):
                    ax = grp.plot(ax=ax, kind='bar', x='Age Group', y='Total Migrants', label=key)
                plt.title('Total Migrants by Age Group and Gender')
                plt.xlabel('Age Group')
                plt.ylabel('Total Migrants')
                plt.legend(loc='best')
                st.pyplot(fig)
            else:
                st.warning("Les colonnes nécessaires pour l'analyse démographique ne sont pas disponibles dans le DataFrame.")

            if 'Education Level' in df.columns:
                st.write("Analyse éducative : migrants par niveau d'éducation")
                migration_by_education = df.groupBy("Education Level").agg(spark_sum("Migrants").alias("Total Migrants"))
                migration_by_education_pd = migration_by_education.toPandas()
                st.write("Analyse éducative réussie")

                # Création du graphe pour migrants par niveau d'éducation
                fig, ax = plt.subplots(figsize=(10, 6))
                ax = migration_by_education_pd.plot(ax=ax, kind='bar', x='Education Level', y='Total Migrants', legend=False)
                plt.title('Total Migrants by Education Level')
                plt.xlabel('Education Level')
                plt.ylabel('Total Migrants')
                st.pyplot(fig)
            else:
                st.warning("Les colonnes nécessaires pour l'analyse éducative ne sont pas disponibles dans le DataFrame.")

            if 'Year' in df.columns and 'Migrants' in df.columns:
                st.write("Analyse des tendances : moyenne des migrants par année")
                avg_migrants_per_year = df.groupBy("Year").agg(avg("Migrants").alias("Average Migrants"))
                avg_migrants_per_year_pd = avg_migrants_per_year.toPandas()
                st.write("Analyse des tendances réussie")

                # Création du graphe pour la moyenne des migrants par année
                fig, ax = plt.subplots(figsize=(10, 6))
                ax = avg_migrants_per_year_pd.plot(ax=ax, kind='line', x='Year', y='Average Migrants', legend=False)
                plt.title('Average Migrants per Year')
                plt.xlabel('Year')
                plt.ylabel('Average Migrants')
                st.pyplot(fig)
            else:
                st.warning("Les colonnes nécessaires pour l'analyse des tendances ne sont pas disponibles dans le DataFrame.")

            # Option pour télécharger le fichier analysé
            csv = data.to_csv(index=False)
            st.sidebar.download_button(label="Télécharger le fichier analysé", data=csv, file_name="migration_analysis.csv", mime="text/csv")
        
        except Exception as e:
            st.sidebar.error(f"Une erreur s'est produite : {e}")

    # Lister les fichiers déjà présents dans le répertoire upload_directory
    st.sidebar.write("Fichiers existants :")
    existing_files = os.listdir(upload_directory)
    selected_file = st.sidebar.selectbox("Choisir un fichier existant", existing_files)

    if selected_file:
        try:
            # Lire et afficher le fichier sélectionné
            file_path = os.path.join(upload_directory, selected_file)
            data = pd.read_csv(file_path)
            st.write(f"Affichage du fichier : {selected_file}")
            st.write(data)
            
            # Convertir le DataFrame pandas en DataFrame Spark
            df = spark.createDataFrame(data)
            st.write("DataFrame Spark créé avec succès")

            # Afficher les noms des colonnes disponibles dans le DataFrame Spark
            st.write("Colonnes disponibles dans le DataFrame Spark:", df.columns)

            # Vérifiez les noms des colonnes et utilisez les noms exacts
            if 'Year' in df.columns and 'Destination Country' in df.columns and 'Migrants' in df.columns:
                st.write("Analyse des flux migratoires : migrants par année et pays de destination")
                migration_by_year_destination = df.groupBy("Year", "Destination Country").agg(spark_sum("Migrants").alias("Total Migrants"))
                migration_by_year_destination_pd = migration_by_year_destination.toPandas()
                st.write("Analyse des flux migratoires réussie")

                # Création du graphe pour migrants par année et pays de destination
                fig, ax = plt.subplots(figsize=(10, 6))
                for key, grp in migration_by_year_destination_pd.groupby(['Destination Country']):
                    ax = grp.plot(ax=ax, kind='line', x='Year', y='Total Migrants', label=key)
                plt.title('Total Migrants by Year and Destination Country')
                plt.xlabel('Year')
                plt.ylabel('Total Migrants')
                plt.legend(loc='best')
                st.pyplot(fig)
            else:
                st.warning("Les colonnes nécessaires pour l'analyse des flux migratoires ne sont pas disponibles dans le DataFrame.")

            if 'Age Group' in df.columns and 'Gender' in df.columns:
                st.write("Analyse démographique : migrants par groupe d'âge et genre")
                migration_by_age_gender = df.groupBy("Age Group", "Gender").agg(spark_sum("Migrants").alias("Total Migrants"))
                migration_by_age_gender_pd = migration_by_age_gender.toPandas()
                st.write("Analyse démographique réussie")

                # Création du graphe pour migrants par groupe d'âge et genre
                fig, ax = plt.subplots(figsize=(10, 6))
                for key, grp in migration_by_age_gender_pd.groupby(['Gender']):
                    ax = grp.plot(ax=ax, kind='bar', x='Age Group', y='Total Migrants', label=key)
                plt.title('Total Migrants by Age Group and Gender')
                plt.xlabel('Age Group')
                plt.ylabel('Total Migrants')
                plt.legend(loc='best')
                st.pyplot(fig)
            else:
                st.warning("Les colonnes nécessaires pour l'analyse démographique ne sont pas disponibles dans le DataFrame.")

            if 'Education Level' in df.columns:
                st.write("Analyse éducative : migrants par niveau d'éducation")
                migration_by_education = df.groupBy("Education Level").agg(spark_sum("Migrants").alias("Total Migrants"))
                migration_by_education_pd = migration_by_education.toPandas()
                st.write("Analyse éducative réussie")

                # Création du graphe pour migrants par niveau d'éducation
                fig, ax = plt.subplots(figsize=(10, 6))
                ax = migration_by_education_pd.plot(ax=ax, kind='bar', x='Education Level', y='Total Migrants', legend=False)
                plt.title('Total Migrants by Education Level')
                plt.xlabel('Education Level')
                plt.ylabel('Total Migrants')
                st.pyplot(fig)
            else:
                st.warning("Les colonnes nécessaires pour l'analyse éducative ne sont pas disponibles dans le DataFrame.")

            if 'Year' in df.columns and 'Migrants' in df.columns:
                st.write("Analyse des tendances : moyenne des migrants par année")
                avg_migrants_per_year = df.groupBy("Year").agg(avg("Migrants").alias("Average Migrants"))
                avg_migrants_per_year_pd = avg_migrants_per_year.toPandas()
                st.write("Analyse des tendances réussie")

                # Création du graphe pour la moyenne des migrants par année
                fig, ax = plt.subplots(figsize=(10, 6))
                ax = avg_migrants_per_year_pd.plot(ax=ax, kind='line', x='Year', y='Average Migrants', legend=False)
                plt.title('Average Migrants per Year')
                plt.xlabel('Year')
                plt.ylabel('Average Migrants')
                st.pyplot(fig)
            else:
                st.warning("Les colonnes nécessaires pour l'analyse des tendances ne sont pas disponibles dans le DataFrame.")
        
        except Exception as e:
            st.sidebar.error(f"Une erreur s'est produite : {e}")

    # Arrêter la session Spark
    spark.stop()
