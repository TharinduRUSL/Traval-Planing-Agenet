"""Free Open-Meteo forecast integration."""
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from ._common import safe_tool, text, integer, fetch


@safe_tool
def get_weather(city: str, start_date: str, days: int = 1) -> dict:
    """Get a live daily forecast; never substitute mock data for unavailable dates.

    Args:
        city: City name to resolve using Open-Meteo geocoding.
        start_date: First forecast date in YYYY-MM-DD format.
        days: Number of consecutive days, from 1 to 16.
    Returns:
        Success/data or error envelope, with resolved location, units and source.
    """
    city = text(city, "city")
    start = date.fromisoformat(text(start_date, "start_date"))
    integer(days, "days", 1, 16)
    geo = fetch("https://geocoding-api.open-meteo.com/v1/search", {"name": city, "count": 1, "language": "en", "format": "json"})
    if not geo.get("results"):
        raise ValueError("City not found. Try a more specific city name.")
    place = geo["results"][0]
    today = datetime.now(ZoneInfo(place.get("timezone", "UTC"))).date()
    end = start + timedelta(days=days - 1)
    if start < today or end > today + timedelta(days=15):
        raise ValueError(f"Forecast unavailable for those dates. Supported window: {today} to {today + timedelta(days=15)}. Plan provisionally and check nearer departure.")
    result = fetch("https://api.open-meteo.com/v1/forecast", {"latitude": place["latitude"], "longitude": place["longitude"], "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code", "timezone": "auto", "start_date": start.isoformat(), "end_date": end.isoformat()})
    return {"source": "Open-Meteo live forecast", "location": {k: place.get(k) for k in ("name", "country", "latitude", "longitude")}, "daily": result["daily"], "units": result.get("daily_units", {})}
