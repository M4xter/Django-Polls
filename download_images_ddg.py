import json
import os
import requests
from urllib.parse import urlencode

# Ton fichier geojson
GEOJSON_FILE = "restaurants.geojson"
# Dossier de sauvegarde des images
IMAGE_DIR = "images"
# Ta clé API Google Street View (à remplacer par ta clé)
API_KEY = "AIzaSyBKQUudMfHiIMa553JnQn9TMf9V2iMm9NY"

def build_address(props):
    # Compose l'adresse complète à partir des propriétés dispo
    parts = []
    if "addr:housenumber" in props:
        parts.append(props["addr:housenumber"])
    if "addr:street" in props:
        parts.append(props["addr:street"])
    if "addr:postcode" in props:
        parts.append(props["addr:postcode"])
    if "addr:city" in props:
        parts.append(props["addr:city"])
    return ", ".join(parts)

def download_image(url, filepath):
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(resp.content)
        print(f"Image sauvegardée : {filepath}")
    except Exception as e:
        print(f"Erreur téléchargement {url} : {e}")

def main():
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)
    with open(GEOJSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    features = data.get("features", [])
    for feature in features:
        props = feature.get("properties", {})
        name = props.get("name")
        if not name:
            continue

        address = build_address(props)
        query = f"{name} {address}"
        print(f"Recherche Google Street View pour : {query}")

        # Paramètres pour Google Street View API
        params = {
            "size": "640x640",              # taille max
            "location": query,
            "fov": "90",                   # champ de vision
            "heading": "235",              # orientation caméra (optionnel)
            "pitch": "10",                 # inclinaison caméra (optionnel)
            "key": API_KEY
        }
        url = f"https://maps.googleapis.com/maps/api/streetview?{urlencode(params)}"

        # Nom de fichier image safe
        filename = f"{name.replace(' ', '_').replace('\'','')}.jpg"
        filepath = os.path.join(IMAGE_DIR, filename)

        download_image(url, filepath)

if __name__ == "__main__":
    main()
