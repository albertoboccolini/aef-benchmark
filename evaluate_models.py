import argparse
from time import sleep

from services.ai_models_manager import get_gpt_response, get_perplexity_response
import pandas as pd
import logging

from services.csv_manager import save_evaluation_results, generate_evaluation_row
from services.evaluation_manager import event_is_matching
from services.locationiq_apis_manager import get_place_suggestions
from services.logging_manager import log_error, log_info


def process_ai_events(events):
    log_info(f"Processing {len(events)} events")
    processed = []
    for event in events:
        if not event.place:
            continue

        try:
            suggestions = get_place_suggestions(event.place)
        except Exception as e:
            log_error(f"{str(e)} for place: {event.place}")
            continue  # TODO: alternative workflow?

        sleep(2)
        if len(suggestions) < 1:
            continue  # TODO: alternative workflow?

        # We must check all the suggestions
        # to make it sure we not exclude some
        # places during the evaluation
        for suggestion in suggestions:
            lat_long = (suggestion["lat"], suggestion["lng"])
            start_naive = (
                event.startDate.replace(tzinfo=None)
                if event.startDate.tzinfo
                else event.startDate
            )
            end_naive = (
                event.endDate.replace(tzinfo=None)
                if event.endDate.tzinfo
                else event.endDate
            )

            processed.append(
                {
                    "name": event.name,
                    "place": event.place,
                    "lat": lat_long[0],
                    "lon": lat_long[1],
                    "start": start_naive,
                    "end": end_naive,
                }
            )

    return processed


def evaluate(ai_events):
    suggestions_for_ai_events = process_ai_events(ai_events)
    matching_events = []
    non_matching_events = []
    event_match_info = {}

    log_info(
        f"Evaluating {len(df)} dataset rows against {len(suggestions_for_ai_events)} suggestions"
    )

    for idx, row in df.iterrows():
        for suggestion in suggestions_for_ai_events:
            event_key = (
                f"{suggestion['name']}_{suggestion['place']}_"
                f"{suggestion['start'].isoformat()}_{suggestion['end'].isoformat()}"
            )

            if event_key not in event_match_info:
                event_match_info[event_key] = {
                    "matched": False,
                    "best_score": 0,
                    "best_suggestion": suggestion.copy(),
                }

            has_found_event, score = event_is_matching(row, suggestion)

            if has_found_event:
                event_match_info[event_key]["matched"] = True

            if score is not None:
                if score > event_match_info[event_key]["best_score"]:
                    event_match_info[event_key]["best_score"] = score
                    event_match_info[event_key]["best_suggestion"] = suggestion.copy()

    for key, info in event_match_info.items():
        result = info["best_suggestion"].copy()
        result["score"] = info["best_score"]

        if info["matched"]:
            matching_events.append(result)
            continue

        non_matching_events.append(result)

    log_info(f"Matched events: {len(matching_events)}")
    log_info(f"Model events NOT in dataset: {len(non_matching_events)}")

    return matching_events, non_matching_events


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    parser = argparse.ArgumentParser(description="Evaluate models.")
    parser.add_argument(
        "--path", required=True, type=str, help="Path to PredictHQ dataset"
    )
    parser.add_argument("--address", required=True, type=str, help="Place address")
    parser.add_argument("--start", required=True, help="Start Date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="End Date (YYYY-MM-DD)")
    parser.add_argument("--distance", required=True, type=int, help="Distance in km")
    args = parser.parse_args()

    df = pd.read_csv(args.path)
    prompt = f"Find events near '{args.address}' from {args.start} to {args.end} within {args.distance} km."
    log_info(prompt)

    models_to_be_tested = [
        "sonar",
        "sonar-pro",
        "gpt-4o-mini-search-preview",
        "gpt-4o-search-preview",
    ]
    rows = []

    MAX_TRIES = 3

    for model in models_to_be_tested:
        model_matching_events = []
        model_non_matching_events = []
        best_generation_for_matching_events = []
        best_generation_for_non_matching_events = []

        for attempt in range(MAX_TRIES):
            try:
                model_events = (
                    get_perplexity_response(prompt, model)
                    if "sonar" in model
                    else get_gpt_response(prompt, model)
                )
                model_matching_events, model_non_matching_events = evaluate(
                    model_events
                )
                best_generation_for_matching_events = (
                    model_matching_events
                    if len(model_matching_events)
                    > len(best_generation_for_matching_events)
                    else best_generation_for_matching_events
                )

                best_generation_for_non_matching_events = (
                    model_non_matching_events
                    if len(model_non_matching_events)
                    > len(best_generation_for_non_matching_events)
                    else best_generation_for_non_matching_events
                )

                if len(best_generation_for_matching_events) >= 15:
                    break
            except Exception as e:
                log_error(f"[Attempt {attempt + 1}/{MAX_TRIES}] {e}")

        evaluation_results = generate_evaluation_row(
            model,
            best_generation_for_matching_events,
            best_generation_for_non_matching_events,
        )
        rows.append(evaluation_results)

    save_evaluation_results(
        rows,
        args.address,
        args.start,
        args.end,
        args.distance,
    )
