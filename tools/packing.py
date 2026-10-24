from ._common import safe_tool, number, string_list


@safe_tool
def get_packing_list(min_temperature_c: float, max_temperature_c: float, rain_probability: float, activities: list[str]) -> dict:
    """Create a rule-based packing list from forecast values or disclosed assumptions.

    Args:
        min_temperature_c: Expected minimum temperature in Celsius, -60 to 60.
        max_temperature_c: Expected maximum temperature in Celsius, -60 to 60.
        rain_probability: Rain probability from 0 to 100 percent.
        activities: Planned activities, such as walking, hiking, swimming or temple.
    Returns:
        Packing items and the supplied weather assumptions for transparency.
    """
    number(min_temperature_c, "min_temperature_c", -60, 60)
    number(max_temperature_c, "max_temperature_c", -60, 60)
    number(rain_probability, "rain_probability", 0, 100)
    if min_temperature_c > max_temperature_c:
        raise ValueError("Minimum temperature cannot exceed maximum temperature.")
    activities = string_list(activities, "activities")
    items = ["Travel documents", "Phone and charger", "Reusable water bottle", "Personal essentials"]
    if min_temperature_c < 15: items += ["Warm layers"]
    if max_temperature_c >= 25: items += ["Sun hat", "Sunscreen", "Light clothing"]
    if rain_probability >= 40: items += ["Rain jacket or umbrella", "Water-resistant bag"]
    joined = " ".join(activities).lower()
    if any(word in joined for word in ("walk", "hik", "park")): items += ["Comfortable walking shoes"]
    if "swim" in joined: items += ["Swimwear", "Towel"]
    if any(word in joined for word in ("temple", "relig", "culture")): items += ["Clothing covering shoulders and knees"]
    return {"items": items, "inputs": {"min_c": min_temperature_c, "max_c": max_temperature_c, "rain_percent": rain_probability}, "source": "rule-based suggestions using supplied values; not an independent forecast"}
