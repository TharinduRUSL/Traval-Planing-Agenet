"""Persistent JSON storage confined to this project's data directory."""
import json
from datetime import date, timedelta
from decimal import Decimal
import math
import os
import re
import tempfile
from pathlib import Path
from ._common import safe_tool, text

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def itinerary_path(filename):
    filename = text(filename, "filename")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}\.json", filename):
        raise ValueError("Use a simple filename such as colombo_trip.json; paths are not allowed.")
    root = DATA_DIR.resolve()
    target = root / filename
    if target.is_symlink() or target.resolve().parent != root:
        raise ValueError("Invalid itinerary path.")
    return target


def validate_itinerary(content):
    """Check new and loaded plans using the same documented schema."""
    if not isinstance(content, dict):
        raise ValueError("Itinerary must be a JSON object.")
    text(content.get("destination"), "destination")
    days = content.get("days")
    if not isinstance(days, list) or not 1 <= len(days) <= 30:
        raise ValueError("Itinerary needs 1 to 30 day objects.")
    previous = None
    for day in days:
        if not isinstance(day, dict):
            raise ValueError("Each day must be an object with date and activities.")
        raw_date = day.get("date")
        if not isinstance(raw_date, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw_date):
            raise ValueError("Each day needs a YYYY-MM-DD date.")
        current = date.fromisoformat(raw_date)
        if previous is not None and current != previous + timedelta(days=1):
            raise ValueError("Day dates must be consecutive and in order.")
        previous = current
        activities = day.get("activities")
        if not isinstance(activities, list) or not 1 <= len(activities) <= 30:
            raise ValueError("Each day needs 1 to 30 activity strings.")
        if any(not isinstance(item, str) or not item.strip() or len(item) > 2000 for item in activities):
            raise ValueError("Activities must be non-empty strings under 2000 characters.")
    budget = content.get("budget")
    if not isinstance(budget, dict):
        raise ValueError("A budget object is required.")
    currency = budget.get("currency")
    if not isinstance(currency, str) or not re.fullmatch(r"[A-Z]{3}", currency):
        raise ValueError("budget.currency must be an uppercase three-letter code.")
    amounts = {}
    for key in ("meals", "transport", "admissions", "contingency", "total"):
        value = budget.get(key)
        if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or not 0 <= value <= 1_000_000_000:
            raise ValueError(f"budget.{key} must be a finite non-negative number.")
        amounts[key] = Decimal(str(value))
    subtotal = sum(amounts[key] for key in ("meals", "transport", "admissions", "contingency"))
    if abs(subtotal - amounts["total"]) > Decimal("0.01"):
        raise ValueError("budget.total must equal meals + transport + admissions + contingency (within one cent).")
    return content


@safe_tool
def save_itinerary(filename: str, itinerary_json: str, overwrite: bool = False) -> dict:
    """Save a complete plan as JSON; never silently replace an existing file.

    Args:
        filename: Simple .json filename without any directory components.
        itinerary_json: JSON object encoded as a string, with destination, days (each with activities), budget, and any weather/tips/packing details.
        overwrite: Set true only when the user explicitly requests replacing this file.
    Returns:
        Confirmed filename and absolute path only after successful persistence.
    """
    path = itinerary_path(filename)
    if not isinstance(overwrite, bool):
        raise ValueError("overwrite must be a boolean.")
    if not isinstance(itinerary_json, str) or len(itinerary_json.encode("utf-8")) > 1_000_000:
        raise ValueError("itinerary_json must be a JSON string under 1 MB.")
    content = validate_itinerary(json.loads(itinerary_json))
    payload = json.dumps(content, indent=2, ensure_ascii=False, allow_nan=False)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise ValueError("File already exists. Choose another filename or explicitly request overwrite.")
    if not overwrite:
        # Exclusive creation prevents accidentally overwriting a concurrently saved file.
        with path.open("x", encoding="utf-8") as file:
            file.write(payload)
    else:
        temp_name = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=DATA_DIR, delete=False) as file:
                temp_name = file.name
                file.write(payload)
            os.replace(temp_name, path)
        finally:
            if temp_name and os.path.exists(temp_name):
                os.unlink(temp_name)
    return {"saved": True, "filename": path.name, "path": str(path)}


@safe_tool
def load_itinerary(filename: str) -> dict:
    """Read and validate an itinerary previously saved in the data directory.

    Args:
        filename: Simple .json filename, for example colombo_trip.json.
    Returns:
        Saved itinerary contents or a clear missing/corrupt file error.
    """
    path = itinerary_path(filename)
    if not path.is_file():
        raise ValueError("Itinerary does not exist. Check the filename or save a plan first.")
    if path.stat().st_size > 1_000_000:
        raise ValueError("Itinerary exceeds the 1 MB size limit.")
    return {"filename": path.name, "itinerary": validate_itinerary(json.loads(path.read_text(encoding="utf-8")))}
