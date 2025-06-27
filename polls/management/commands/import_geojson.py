import json
import os
import requests
from django.core.management.base import BaseCommand
from polls.models import Restaurant
from django.conf import settings

class Command(BaseCommand):
    help = "Importe les restaurants depuis un GeoJSON et télécharge leurs images"

    def handle(self, *args, **options):
        path = "restaurants.geojson"
        print(f"Ouverture du fichier : {path}")

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier : {e}")
            return

        media_dir = os.path.join(settings.BASE_DIR, 'media', 'restaurants')
        os.makedirs(media_dir, exist_ok=True)

        count = 0

        for feature in data.get("features", []):
            props = feature.get("properties", {})
            geometry = feature.get("geometry", {})
            coords = geometry.get("coordinates")
            name = props.get("name")

            if not name or not coords:
                print("Manque nom ou coordonnées, skip")
                continue

            longitude, latitude = coords

            address_parts = [
                props.get("addr:housenumber"),
                props.get("addr:street"),
                props.get("addr:postcode"),
                props.get("addr:city"),
            ]
            address = ", ".join(filter(None, address_parts))

            image_url = props.get("image_url") or props.get("photo")  # adapte selon ta clé
            print(f"URL image pour {name} : {image_url}")

            # Mise à jour ou création du restaurant
            restaurant, created = Restaurant.objects.update_or_create(
                name=name,
                latitude=latitude,
                longitude=longitude,
                defaults={
                    "address": address or "",
                    "type": props.get("amenity", ""),
                    "image_url": image_url or "",
                }
            )

            if created:
                print(f"Création: {name} ({latitude},{longitude})")
            else:
                print(f"Mise à jour: {name} ({latitude},{longitude})")

            # Télécharger l'image si URL dispo et fichier pas déjà téléchargé
            if image_url:
                ext = os.path.splitext(image_url)[1].split("?")[0]  # .jpg, .png, sans params URL
                safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{safe_name}_{latitude}_{longitude}{ext}"
                filepath = os.path.join(media_dir, filename)

                if not os.path.exists(filepath):
                    print(f"Téléchargement de l'image pour {name}...")
                    try:
                        response = requests.get(image_url, timeout=10)
                        response.raise_for_status()
                        with open(filepath, "wb") as img_file:
                            img_file.write(response.content)
                        print(f"Image enregistrée : {filepath}")
                    except Exception as e:
                        print(f"Erreur téléchargement image pour {name} : {e}")
                else:
                    print(f"Image déjà présente localement pour {name}")

            count += 1

        print(f"{count} restaurants traités.")
