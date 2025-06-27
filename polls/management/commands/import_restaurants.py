import json
from django.core.management.base import BaseCommand
from polls.models import Restaurant

class Command(BaseCommand):
    help = 'Importe les restaurants depuis un fichier GeoJSON'

    def handle(self, *args, **kwargs):
        with open('restaurants.geojson', encoding='utf-8') as f:
            data = json.load(f)

            for feature in data['features']:
                props = feature['properties']
            coords = feature['geometry']['coordinates']

            name = props.get('name', 'Inconnu')
            r_type = props.get('cuisine') or props.get('amenity') or ''
            lon, lat = coords

            Restaurant.objects.create(
                name=name,
                longitude=lon,
                latitude=lat,
                type=r_type
            )

        self.stdout.write(self.style.SUCCESS('Import terminé !'))
