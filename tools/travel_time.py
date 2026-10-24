import math
from ._common import safe_tool, text
from ._catalog import CITIES, city_key


@safe_tool
def get_travel_time(city: str, origin: str, destination: str, mode: str = "walking") -> dict:
    """Estimate travel between two catalog attractions; this is not live routing.

    Args:
        city: Supported catalog city.
        origin: Exact attraction name from search_attractions.
        destination: Exact attraction name from search_attractions.
        mode: walking, driving or transit.
    Returns:
        Estimated route distance and minutes, with method and limitations.
    """
    key = city_key(city)
    origin, destination = text(origin, "origin"), text(destination, "destination")
    mode = text(mode, "mode").lower()
    if mode not in ("walking", "driving", "transit"):
        raise ValueError("mode must be walking, driving or transit.")
    places = {r[0].lower(): r for r in CITIES[key]}
    if origin.lower() not in places or destination.lower() not in places:
        raise ValueError("Both places must be exact names returned by search_attractions.")
    a, b = places[origin.lower()], places[destination.lower()]
    lat1, lat2 = map(math.radians, (a[2], b[2]))
    dlat, dlon = lat2 - lat1, math.radians(b[3] - a[3])
    h = math.sin(dlat / 2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon / 2)**2
    distance = 6371 * 2 * math.asin(min(1, math.sqrt(h))) * 1.3
    minutes = distance / {"walking": 4.5, "driving": 25, "transit": 18}[mode] * 60
    if distance and mode == "transit":
        minutes += 10
    return {"distance_km": round(distance, 2), "minutes": math.ceil(minutes), "mode": mode, "source": "estimate: great-circle distance x 1.3; assumed speed; transit adds 10 min", "warning": "Not a route, traffic forecast or accessibility assessment."}
