import requests
from django.core.management.base import BaseCommand
from polls.models import Restaurant  # adapte si ton modèle est dans un autre app

class Command(BaseCommand):
    help = "Met à jour le champ 'address' de chaque restaurant à partir de l'API Wemap"

    def handle(self, *args, **options):
        for resto in Restaurant.objects.all():
            if resto.latitude is None or resto.longitude is None:
                self.stdout.write(self.style.WARNING(f"{resto.name} → coordonnées manquantes"))
                continue

            url = f"https://api.getwemap.com/v3.0/geocoding/geocode?longitude={resto.longitude}&latitude={resto.latitude}"

            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                data = response.json()

                print("DEBUG:", data)  # optionnel

                if isinstance(data, dict) and "address" in data:
                    address = data["address"]
                else:
                    address = None

                if address:
                    resto.address = address
                    resto.save()
                    self.stdout.write(self.style.SUCCESS(f"{resto.name} → {address}"))
                else:
                    self.stdout.write(self.style.WARNING(f"{resto.name} → adresse non trouvée"))

            except requests.RequestException as e:
                self.stdout.write(self.style.ERROR(f"Erreur pour {resto.name} : {e}"))
