import ast
from datetime import datetime
from geopy.distance import geodesic


def event_is_matching(event, ai_event) -> bool:
    event_location = ast.literal_eval(event['location'])
    score = 0

    distance_between_events = geodesic((ai_event['lat'], ai_event['lon']), (event_location[0], event_location[1])).km

    if distance_between_events <= 2.0:
        return True, None

    if distance_between_events <= 5.0:
        score += 1

    # Start date within 5 days
    if abs((ai_event['start'] - datetime.fromisoformat(event['start_local'])).days) <= 5:
        score += 1

    # End date within 5 days
    if abs((ai_event['end'] - datetime.fromisoformat(event['end_local'])).days) <= 5:
        score += 1

    if score >= 2:
        return True, score

    return False, score
