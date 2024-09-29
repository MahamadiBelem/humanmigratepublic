import streamlit as st
import pandas as pd
from pymongo import MongoClient
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['db_migration_amende']
collection = db['collection_table_canevas_import']

# Fonction pour charger les données depuis MongoDB
def load_data():
    data = list(collection.find())
    return pd.DataFrame(data)

# Fonction pour mettre à jour les données dans MongoDB
def update_data(df):
    collection.delete_many({})  # Supprimer les anciennes données
    records = df.to_dict('records')
    collection.insert_many(records)

# Fonction de prédiction
def predict_investment(df):
    # Assurez-vous que toutes les colonnes nécessaires sont présentes
    required_columns = ['Year', 'Location', 'Origin', 'Region', 'Type', 'Destination', 'Age Group', 'Education Level', 'Rating', 'Migrants']
    if not all(col in df.columns for col in required_columns):
        st.error("Les colonnes nécessaires ne sont pas toutes présentes dans les données.")
        return None
    
    # Préparation des données
    df_numeric = pd.get_dummies(df[required_columns], drop_first=True)  # Convertir les variables catégorielles
    X = df_numeric.drop('Investment', axis=1, errors='ignore')  # Variables indépendantes
    y = df_numeric['Investment'] if 'Investment' in df_numeric.columns else None  # Variable dépendante

    if y is None:
        st.error("La colonne 'Investment' est nécessaire pour la prédiction.")
        return None

    # Diviser les données en ensemble d'entraînement et ensemble de test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    # Entraîner le modèle
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Prédictions
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    st.write(f"Erreur quadratique moyenne (MSE) : {mse}")

    return model

# Afficher l'interface utilisateur avec Streamlit
st.title("Affichage et Analyse des Données")

# Afficher les données
df = load_data()
st.dataframe(df)

# Afficher des statistiques basiques
st.write("Résumé des données")
st.write(df.describe())

# Afficher une visualisation (par exemple, histogramme)
if 'Investment' in df.columns:
    st.write("Histogramme des investissements")
    st.bar_chart(df['Investment'])

# Formulaire pour uploader un fichier CSV
st.subheader("Mettre à jour les données")
uploaded_file = st.file_uploader("Choisir un fichier CSV", type="csv")

if uploaded_file is not None:
    new_data = pd.read_csv(uploaded_file)
    update_data(new_data)
    st.success("Les données ont été mises à jour avec succès.")

# Prédiction des investissements
if st.button("Prédire les Investissements"):
    model = predict_investment(df)
    if model is not None:
        st.write("Modèle de prédiction prêt.")

# Explications
st.write("""
    - **Affichage des données** : Les données sont récupérées depuis MongoDB et affichées dans une table.
    - **Résumé des données** : Affiche les statistiques descriptives des données.
    - **Histogramme** : Affiche un histogramme des investissements si la colonne existe.
    - **Mise à jour des données** : Permet de télécharger un fichier CSV pour mettre à jour les données dans MongoDB.
    - **Prédiction des investissements** : Utilise un modèle de régression linéaire pour prédire les investissements à partir des autres variables.
""")
