import json

with open("restaurants.geojson", "r", encoding="utf-8") as f:
    data = json.load(f)

wemap_data = []

for feature in data.get("features", []):
    props = feature.get("properties", {}).copy()  # on copie pour ne pas modifier l'original
    geom = feature.get("geometry", {})
    coords = geom.get("coordinates", [])

    if coords:
        nom = props.get("name", "Restaurant sans nom")
        ville = props.get("addr:city", "une ville charmante")
        cuisine = props.get("cuisine", "une cuisine savoureuse")

        # On construit la description personnalisée
        desc = f"{nom} est un restaurant situé à {ville}, spécialisé dans la cuisine {cuisine}. Un lieu apprécié pour une pause gourmande en toute simplicité."
        desc = desc[:500]  # limiter à 500 caractères

        # On ajoute ou remplace la clé description dans les propriétés
        props["description"] = desc

        # On crée un nouvel objet conforme à la structure GeoJSON avec description modifiée
        wemap_data.append({
            "type": "Feature",
            "properties": props,
            "geometry": geom
        })

with open("restaurants_wemap.json", "w", encoding="utf-8") as f:
    json.dump(wemap_data, f, ensure_ascii=False, indent=2)
