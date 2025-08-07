import os
import requests

from dotenv import load_dotenv

load_dotenv()
LOCATIONIQ_API_KEY = os.environ.get("LOCATIONIQ_API_KEY")


def get_place_suggestions(query: str):
    url = "https://api.locationiq.com/v1/autocomplete"
    params = {
        "key": LOCATIONIQ_API_KEY,
        "q": query,
        "format": "json",
        "limit": 3,
        "countrycodes": "it"
    }

    response = requests.get(url, params=params)

    if not response.ok:
        raise Exception(f"LocationIQ Autocomplete error: {response.text}")

    data = response.json()

    suggestions = []
    for item in data:
        suggestions.append({
            "name": item.get("display_name", ""),
            "address": item.get("address", {}),
            "place_id": item.get("place_id"),
            "lat": item.get("lat"),
            "lng": item.get("lon")
        })

    return suggestions
