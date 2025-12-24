import os
import requests

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def find_places(payload: dict):
    location = payload["location"]
    place_type = payload.get("type", "restaurant")

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": location,
        "radius": 1500,
        "type": place_type,
        "key": GOOGLE_API_KEY
    }

    response = requests.get(url, params=params).json()
    results = response.get("results", [])[:5]

    return [
        {
            "name": p["name"],
            "rating": p.get("rating"),
            "address": p.get("vicinity")
        }
        for p in results
    ]
