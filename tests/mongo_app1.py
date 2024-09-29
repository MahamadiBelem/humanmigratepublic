import streamlit as st
import pandas as pd
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

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
def predict_destination(age_group, education_level, model, encoder):
    input_data = pd.DataFrame({
        'Age Group': [age_group],
        'Education Level': [education_level]
    })
    input_data_encoded = pd.get_dummies(input_data, columns=['Age Group', 'Education Level'])
    input_data_encoded = input_data_encoded.reindex(columns=encoder.get_feature_names_out(), fill_value=0)
    prediction = model.predict(input_data_encoded)
    return prediction[0]

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

# Préparer les données pour le modèle
def prepare_data_for_classification(df):
    df_encoded = pd.get_dummies(df[['Age Group', 'Education Level', 'Destination']])
    X = df_encoded.drop('Destination', axis=1)
    y = df_encoded['Destination']
    return X, y, df_encoded.columns

# Entraîner le modèle
X, y, feature_names = prepare_data_for_classification(df)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
model = RandomForestClassifier()
model.fit(X_train, y_train)
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
st.write(f"Précision du modèle : {accuracy:.2f}")

# Prédiction de la destination
st.subheader("Prédiction de la Destination")
age_group = st.selectbox("Age Group", df['Age Group'].unique())
education_level = st.selectbox("Education Level", df['Education Level'].unique())

if st.button("Prédire la Destination"):
    prediction = predict_destination(age_group, education_level, model, feature_names)
    st.write(f"La destination prédite est : {prediction}")

# Explications
st.write("""
    - **Affichage des données** : Les données sont récupérées depuis MongoDB et affichées dans une table.
    - **Résumé des données** : Affiche les statistiques descriptives des données.
    - **Histogramme** : Affiche un histogramme des investissements si la colonne existe.
    - **Mise à jour des données** : Permet de télécharger un fichier CSV pour mettre à jour les données dans MongoDB.
    - **Prédiction de la destination** : Utilise un modèle de classification pour prédire la destination en fonction de l'âge et du niveau d'éducation.
""")
