import os
from dotenv import load_dotenv
import requests

load_dotenv()

# teste de compartilhamento


url = "https://places.googleapis.com/v1/places:searchNearby"

headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": os.getenv("GOOGLE_MAPS_API_KEY"),
    "X-Goog-FieldMask": "places.displayName,places.websiteUri",
}

categories = [
    # Alimentação
    "restaurant",
    "cafe",
    "bakery",
    "bar",
    "meal_takeaway",
    "meal_delivery",
    # Beleza e estética
    "beauty_salon",
    "hair_salon",
    "nail_salon",
    "spa",
    # Saúde
    "dentist",
    "doctor",
    "physiotherapist",
    "veterinary_care",
    "medical_clinic",
    "pharmacy",
    # Esporte e fitness
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
    # Comércio
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

    response = requests.post(url, headers=headers, json=dados)

    print(category, response.status_code)

    resultado = response.json()

    for place in resultado.get("places", []):

        nome = place["displayName"]["text"]
        site = place.get("websiteUri")

        empresas.append({"nome": nome, "site": site, "categoria": category})


url_fake = ["instagram.com", "facebook.com"]

for i in range(len(empresas)):

    nome = empresas[i]["nome"]
    site = empresas[i]["site"]
    categoria = empresas[i]["categoria"]

    if site is None or any(url in site.lower() for url in url_fake):

        with open("SEM SITE.txt", "a", encoding="utf8") as file:
            file.write(nome + "\n")

    else:

        with open("COM SITE.txt", "a", encoding="utf8") as file:
            file.write(
                "nome: "
                + nome
                + " | url: "
                + site
                + " | categoria: "
                + categoria
                + "\n"
            )
