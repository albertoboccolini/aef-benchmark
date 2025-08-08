import os

import pandas as pd

from services.logging_manager import log_info
from datetime import datetime


def generate_evaluation_row(model_name, matching_events, non_matching_events):
    matching_scores = [
        event['score'] for event in matching_events
        if event['score'] is not None
    ]

    non_matching_scores = [
        event['score'] for event in non_matching_events
        if event['score'] is not None
    ]

    return {
        "model_name": model_name,
        "matching_events": matching_events,
        "non_matching_events": non_matching_events,
        "avg_matching_score": sum(matching_scores) / len(
            matching_scores) if matching_scores else 0,
        "avg_non_matching_score": sum(non_matching_scores) / len(
            non_matching_scores) if non_matching_scores else 0
    }


def save_evaluation_results(rows, address, start_date, end_date, distance):
    if not rows:
        raise ValueError("No evaluation rows provided.")

    results_data = {
        'Model': [],
        'Matching events': [],
        'Non Matching events': [],
        "AVG Matching Score (distance > 2km)": [],
        "AVG Non-Matching Score": []
    }

    for row in rows:
        results_data['Model'].append(row['model_name'])
        results_data['Matching events'].append(len(row['matching_events']))
        results_data['Non Matching events'].append(len(row['non_matching_events']))
        results_data["AVG Matching Score (distance > 2km)"].append(round(row['avg_matching_score'], 3))
        results_data["AVG Non-Matching Score"].append(round(row['avg_non_matching_score'], 3))

    results_df = pd.DataFrame(results_data)

    clean_address = "".join(c for c in address if c.isalnum() or c in (' ', '-', '_')).rstrip()
    clean_address = clean_address.replace(' ', '_')
    clean_start_date = start_date.replace('-', '')
    clean_end_date = end_date.replace('-', '')
    today_date = datetime.now().strftime('%Y%m%d_%H%M')

    filename = f"evaluations/evaluation_{clean_address}_{clean_start_date}_{clean_end_date}_{distance}_{today_date}.csv"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    results_df.to_csv(filename, index=False, encoding='utf-8')

    log_info(f"Benchmark saved in: {filename}")
