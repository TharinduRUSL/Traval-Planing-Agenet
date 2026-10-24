from ._common import safe_tool, string_list
from ._catalog import CITIES, city_key


@safe_tool
def search_attractions(city: str, interests: list[str]) -> dict:
    """Search a small curated destination catalog with illustrative admission prices.

    Args:
        city: Colombo, Kandy, Paris or London.
        interests: Keywords such as museum, park or culture; empty list means all.
    Returns:
        Matching attractions with per-person USD estimates, coordinates and caveats.
    """
    key = city_key(city)
    keywords = [x.lower().rstrip("s") for x in string_list(interests, "interests")]
    rows = [{"name": n, "category": c, "latitude": lat, "longitude": lon, "admission_usd_per_person": cost} for n, c, lat, lon, cost in CITIES[key]]
    matches = [row for row in rows if not keywords or any(k in (row["name"] + " " + row["category"]).lower() for k in keywords)]
    return {"city": key, "source": "curated illustrative catalog; verify prices and opening hours", "attractions": matches}
