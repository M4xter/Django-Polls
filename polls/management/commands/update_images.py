import os
import random
import requests
from django.core.management.base import BaseCommand
from polls.models import Restaurant

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PEXELS_URL = "https://api.pexels.com/v1/search"

HEADERS = {
    "Authorization": PEXELS_API_KEY
}

class Command(BaseCommand):
    help = "Attribue une image aléatoire de pizzeria à chaque restaurant"

    def handle(self, *args, **kwargs):
        if not PEXELS_API_KEY:
            self.stdout.write(self.style.ERROR("Clé API Pexels manquante !"))
            return

        for r in Restaurant.objects.all():
            try:
                response = requests.get(
                    PEXELS_URL,
                    headers=HEADERS,
                    params={"query": "pizzeria", "per_page": 50}
                )
                data = response.json()
                photos = data.get("photos", [])
                if not photos:
                    self.stdout.write(self.style.WARNING(f"Aucune image trouvée pour {r.name}"))
                    continue

                photo = random.choice(photos)
                image_url = photo.get("src", {}).get("large")

                if image_url:
                    r.image_url = image_url
                    r.save()
                    self.stdout.write(self.style.SUCCESS(f"{r.name} — image ajoutée."))
                else:
                    self.stdout.write(self.style.WARNING(f"{r.name} — image non trouvée."))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"{r.name} — erreur : {e}"))
