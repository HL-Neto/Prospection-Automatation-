import os
import time
from dotenv import load_dotenv
import requests

load_dotenv()

# pra teste de compartilhamento com a sua chave api, fresco

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_MAPS_API_KEY não encontrada no .env")

url = "https://places.googleapis.com/v1/places:searchNearby"

headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": "places.id,places.displayName,places.websiteUri",
}

categories = [
    # Alimentação no geral
    "restaurant",
    "cafe",
    "bakery",
    "bar",
    "meal_takeaway",
    "meal_delivery",
    # Beleza e estetica mais preciso
    "beauty_salon",
    "hair_salon",
    "nail_salon",
    "spa",
    # Area de saude
    "dentist",
    "doctor",
    "physiotherapist",
    "veterinary_care",
    "medical_clinic",
    "pharmacy",
    # Esportes
    "gym",
    "fitness_center",
    "yoga_studio",
    "sports_club",
    # Serviços profissionais
    "lawyer",
    "accounting",
    "real_estate_agency",
    "insurance_agency",
    "travel_agency",
    # Automotivo
    "car_dealer",
    "car_rental",
    "car_repair",
    "car_wash",
    "tire_shop",
    # Lojas de comercios
    "clothing_store",
    "shoe_store",
    "jewelry_store",
    "furniture_store",
    "electronics_store",
    "hardware_store",
    "florist",
    "pet_store",
    "book_store",
    "gift_shop",
    "sporting_goods_store",
    "home_goods_store",
    # Casa / construção
    "electrician",
    "plumber",
]

empresas = []
places_vistos = (
    set()
)  # para deduplicar por place_id caso haja erros, ja seria uma correção

session = requests.Session()
session.headers.update(headers)

for category in categories:

    dados = {
        "includedTypes": [category],
        "maxResultCount": 20,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": -7.115, "longitude": -34.861},
                "radius": 20000,
            }
        },
    }

    try:
        response = session.post(url, json=dados, timeout=15)
    except requests.exceptions.RequestException as erro:
        print(category, "ERRO DE CONEXAO:", erro)
        continue

    print(category, response.status_code)

    if response.status_code != 200:
        print(category, "ERRO NA API:", response.text)
        continue

    resultado = response.json()

    for place in resultado.get("places", []):

        place_id = place.get("id")

        # evita empresas duplicadas que aparecem em mais de uma categoria, coisa que estava se repetindo demais
        if place_id in places_vistos:
            continue
        places_vistos.add(place_id)

        nome = place["displayName"]["text"]
        site = place.get("websiteUri")

        empresas.append({"nome": nome, "site": site, "categoria": category})

    time.sleep(
        0.2
    )  # fresco tem quye respeitar o rate limit da API, voce estava ultrapassando


sites_falsos = [
    "instagram.com",
    "facebook.com",
    "linktr.ee",
    "wa.me",
    "linkedin.com",
    "wixsite.com",
]

with open("SEM SITE.txt", "w", encoding="utf8") as arquivo_sem_site, open(
    "COM SITE.txt", "w", encoding="utf8"
) as arquivo_com_site:

    for empresa in empresas:

        nome = empresa["nome"]
        site = empresa["site"]
        categoria = empresa["categoria"]

        if site is None or any(url in site.lower() for url in sites_falsos):

            arquivo_sem_site.write(nome + "\n")

        else:

            arquivo_com_site.write(
                "nome: "
                + nome
                + " | url: "
                + site
                + " | categoria: "
                + categoria
                + "\n"
            )
