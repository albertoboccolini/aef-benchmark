import argparse
import os
import requests
import pandas as pd
from urllib.parse import urlencode
import logging

from services.logging_manager import log_info


def fetch_events(latitude, longitude, start_date, end_date, distance_km):
    base_url = "https://api.predicthq.com/v1/events/"
    params = {
        "within": f"{distance_km}km@{latitude},{longitude}",
        "active.gte": start_date,
        "active.lte": end_date,
        "active.tz": "Europe/Rome",
        "limit": 50
    }
    headers = {
        "Authorization": f"Bearer {os.environ['PREDICT_HQ_TOKEN']}",
        "Accept": "application/json"
    }

    all_results = []
    next_url = base_url + "?" + urlencode(params)

    while next_url:
        log_info(f"Fetching {next_url}")
        response = requests.get(next_url, headers=headers)
        if response.status_code != 200:
            print("Request failed:", response.status_code, response.text)
            break

        data = response.json()
        all_results.extend(data.get("results", []))
        next_url = data.get("next")

    return all_results


def extract_event_data(event):
    hospitality_impact = next(
        (pattern.get("impacts", []) for pattern in event.get("impact_patterns", []) if
         pattern.get("vertical") == "hospitality"),
        []
    )
    return {
        "id": event.get("id"),
        "title": event.get("title"),
        "geo.address": event.get("geo", {}).get("address", {}).get("formatted_address"),
        "location": event.get("location"),
        "address": event.get("geo", {}).get("address", {}).get("locality"),
        "start_local": event.get("start_local"),
        "end_local": event.get("end_local"),
        "timezone": event.get("timezone"),
        "predicted_attendance": event.get("phq_attendance"),
        "impact_patterns_hospitality": hospitality_impact,
        "predicted_event_spend": event.get("predicted_event_spend"),
        "local_rank": event.get("local_rank")
    }


def generate_dataset():
    parser = argparse.ArgumentParser(description="Extract events from PredictHQ.")
    parser.add_argument("--lat", required=True, type=float, help="Latitudine")
    parser.add_argument("--lon", required=True, type=float, help="Longitudine")
    parser.add_argument("--start", required=True, help="Data inizio (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="Data fine (YYYY-MM-DD)")
    parser.add_argument("--distance", required=True, type=int, help="Distanza in km")
    parser.add_argument("--min_attendance", type=int, default=1000, help="Attendance minima")
    parser.add_argument("--min_rank", type=int, default=60, help="Rank minimo")
    args = parser.parse_args()

    events = fetch_events(args.lat, args.lon, args.start, args.end, args.distance)
    if not events:
        print("No events found.")
        return

    df = pd.DataFrame([extract_event_data(e) for e in events])
    os.makedirs("datasets", exist_ok=True)
    output_path = f"./datasets/events_{args.lat}_{args.lon}_{args.start}_{args.end}.csv"
    df.to_csv(output_path, index=False)

    print(f"{len(df)} events saved in '{output_path}_{args.start}_{args.end}'")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    generate_dataset()
