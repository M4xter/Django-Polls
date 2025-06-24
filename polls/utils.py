import requests

def get_client_ip(request):
    """
    Récupère l'IP réelle du client depuis la requête Django,
    en tenant compte des proxys éventuels.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def get_geoip_details(ip):
    """
    Récupère des infos géolocalisées à partir de l'IP en utilisant
    l'API Hackertarget, puis Nominatim pour la latitude/longitude.
    Renvoie un dict avec country, city, latitude, longitude.
    """
    try:
        url = f"https://api.hackertarget.com/geoip/?q={ip}&output=json"
        response = requests.get(url, timeout=5)
        data = response.json() if response.ok else {}
    except Exception:
        data = {}

    city = data.get("city", "Inconnue")
    country = data.get("country", "Inconnu")

    latitude = None
    longitude = None

    if city != "Inconnue" and country != "Inconnu":
        try:
            params = {
                "q": f"{city}, {country}",
                "format": "json",
                "limit": 1,
            }
            nominatim_url = "https://nominatim.openstreetmap.org/search"
            nom_resp = requests.get(
                nominatim_url,
                params=params,
                headers={"User-Agent": "DjangoApp"},
                timeout=5
            )
            if nom_resp.ok and nom_resp.json():
                loc = nom_resp.json()[0]
                latitude = loc.get("lat")
                longitude = loc.get("lon")
        except Exception:
            pass

    # Fallback : coordonnées de Montpellier si pas de lat/lon récupérées
    if not latitude or not longitude:
        latitude = "43.6112"
        longitude = "3.8767"

    return {
        "city": city,
        "country": country,
        "latitude": latitude,
        "longitude": longitude,
    }
