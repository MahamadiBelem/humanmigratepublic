from fastapi import FastAPI
from pymongo import MongoClient
from bson import ObjectId
import math

app = FastAPI()

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['migration_in_world']
collection = db['mycollection']

# Convertir ObjectId en string et gérer les valeurs flottantes non conformes
def object_id_converter(data):
    if isinstance(data, list):
        for item in data:
            item['_id'] = str(item['_id'])
            item = sanitize_floats(item)
    elif isinstance(data, dict):
        data['_id'] = str(data['_id'])
        data = sanitize_floats(data)
    return data

def sanitize_floats(data):
    for key, value in data.items():
        if isinstance(value, float):
            if math.isnan(value) or math.isinf(value):
                data[key] = None
    return data

@app.get("/api/insp/donnee-migration-humaine")
def get_migration_data():
    data = list(collection.find())
    data = object_id_converter(data)
    return {"data": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8510)

# on demare avec py app_API.py
# Ce code crée une API GET à l’adresse http://localhost:8501/api/insp/donnee-migration-humaine 
# qui retourne toutes les données de la collection mycollection dans la base de données migration_in_world. Les identifiants MongoDB (ObjectId) sont convertis en chaînes de
#  caractères pour être facilement lisibles.