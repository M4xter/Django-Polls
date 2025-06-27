import os
import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from polls.models import Restaurant

def get_image_url(query):
    headers = {"User-Agent": "Mozilla/5.0"}
    search_url = f"https://www.bing.com/images/search?q={query.replace(' ', '+')}&form=HDRSC2"
    response = requests.get(search_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all("a", class_="iusc")
        for img in images:
            m = re.search(r'"murl":"(.*?)"', str(img))
            if m:
                return m.group(1)
    return None

def update_restaurant_images():
    restaurants = Restaurant.objects.filter(image='')  # ou image__isnull=True
    for r in restaurants:
        query = f"{r.name} {r.address}"
        print(f"Recherche image pour {query}")
        img_url = get_image_url(query)
        if img_url:
            try:
                img_response = requests.get(img_url)
                if img_response.status_code == 200:
                    img_name = f"{r.name.lower().replace(' ', '_')}.jpg"
                    r.image.save(img_name, ContentFile(img_response.content), save=True)
                    print(f"Image enregistrée pour {r.name}")
                else:
                    print(f"Erreur téléchargement image pour {r.name}")
            except Exception as e:
                print(f"Erreur avec {r.name} : {e}")
        else:
            print(f"Aucune image trouvée pour {r.name}")
