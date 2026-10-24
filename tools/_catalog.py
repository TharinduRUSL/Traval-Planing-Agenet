"""Illustrative USD prices and coordinates, NOT live tickets or opening hours."""
CITIES = {
    "colombo": [("National Museum", "museum", 6.9106, 79.8608, 6), ("Viharamahadevi Park", "park", 6.913, 79.861, 0), ("Galle Face Green", "waterfront", 6.924, 79.8449, 0), ("Gangaramaya Temple", "culture", 6.9167, 79.8566, 3)],
    "kandy": [("Temple of the Tooth", "culture", 7.2936, 80.6413, 7), ("Kandy Lake", "park", 7.2906, 80.642, 0), ("Royal Botanical Gardens", "park", 7.2719, 80.595, 10)],
    "paris": [("Louvre", "museum", 48.8606, 2.3376, 25), ("Luxembourg Gardens", "park", 48.8462, 2.3372, 0), ("Eiffel Tower", "landmark", 48.8584, 2.2945, 35)],
    "london": [("British Museum", "museum", 51.5194, -0.127, 0), ("Hyde Park", "park", 51.5073, -0.1657, 0), ("Tower of London", "culture", 51.5081, -0.0759, 45)],
}
TIPS = {
    "colombo": {"food": ["Rice and curry", "Hoppers", "Kottu"], "tips": ["Carry water and plan breaks from heat.", "Dress respectfully at religious sites.", "Agree on a tuk-tuk fare or use a metered service."]},
    "kandy": {"food": ["Rice and curry", "String hoppers"], "tips": ["Allow extra time for hill roads.", "Cover shoulders and knees at temples.", "Check weather before outdoor walks."]},
    "paris": {"food": ["Crepes", "Baguette sandwiches"], "tips": ["Keep valuables secure in crowded areas.", "Check attraction opening days before visiting.", "Validate public transport tickets as required."]},
    "london": {"food": ["Pie and mash", "Fish and chips"], "tips": ["Carry a rain layer.", "Check transport service notices.", "Look carefully in both directions at crossings."]},
}


def city_key(city):
    from ._common import text
    key = text(city, "city").lower()
    if key not in CITIES:
        raise ValueError("Curated data supports Colombo, Kandy, Paris and London only.")
    return key
