
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum, avg

# Créer une session Spark
spark = SparkSession.builder \
    .appName("Migration Data Analysis") \
    .getOrCreate()

# Interface Streamlit
st.title("Migration Data Analysis")

# Option pour uploader un fichier
uploaded_file = st.file_uploader("Choisir un fichier CSV", type="csv")

if uploaded_file:
    # Lire le fichier CSV avec pandas
    data = pd.read_csv(uploaded_file)
    st.write(data)
    
    # Convertir le DataFrame pandas en DataFrame Spark
    df = spark.createDataFrame(data)

    # Analyse des flux migratoires : migrants par année et pays de destination
    migration_by_year_destination = df.groupBy("Year", "Destination Country").agg(spark_sum("Migrants").alias("Total Migrants"))
    migration_by_year_destination_pd = migration_by_year_destination.toPandas()

    # Création du graphe pour migrants par année et pays de destination
    fig, ax = plt.subplots(figsize=(10, 6))
    for key, grp in migration_by_year_destination_pd.groupby(['Destination Country']):
        ax = grp.plot(ax=ax, kind='line', x='Year', y='Total Migrants', label=key)
    plt.title('Total Migrants by Year and Destination Country')
    plt.xlabel('Year')
    plt.ylabel('Total Migrants')
    plt.legend(loc='best')
    st.pyplot(fig)

    # Analyse démographique : migrants par groupe d'âge et genre
    migration_by_age_gender = df.groupBy("Age Group", "Gender").agg(spark_sum("Migrants").alias("Total Migrants"))
    migration_by_age_gender_pd = migration_by_age_gender.toPandas()

    # Création du graphe pour migrants par groupe d'âge et genre
    fig, ax = plt.subplots(figsize=(10, 6))
    for key, grp in migration_by_age_gender_pd.groupby(['Gender']):
        ax = grp.plot(ax=ax, kind='bar', x='Age Group', y='Total Migrants', label=key)
    plt.title('Total Migrants by Age Group and Gender')
    plt.xlabel('Age Group')
    plt.ylabel('Total Migrants')
    plt.legend(loc='best')
    st.pyplot(fig)

    # Analyse éducative : migrants par niveau d'éducation
    migration_by_education = df.groupBy("Education Level").agg(spark_sum("Migrants").alias("Total Migrants"))
    migration_by_education_pd = migration_by_education.toPandas()

    # Création du graphe pour migrants par niveau d'éducation
    fig, ax = plt.subplots(figsize=(10, 6))
    ax = migration_by_education_pd.plot(ax=ax, kind='bar', x='Education Level', y='Total Migrants', legend=False)
    plt.title('Total Migrants by Education Level')
    plt.xlabel('Education Level')
    plt.ylabel('Total Migrants')
    st.pyplot(fig)