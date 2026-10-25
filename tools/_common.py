"""Shared validation and error handling; these helpers are not agent tools."""
import math
from functools import wraps
import requests


def safe_tool(function):
    """Preserve the signature/docstring and turn tool failures into JSON errors."""
    @wraps(function)
    def wrapped(*args, **kwargs):
        try:
            return {"ok": True, "data": function(*args, **kwargs)}
        except (ValueError, TypeError, KeyError) as exc:
            return {"ok": False, "error": str(exc)}
        except requests.RequestException:
            return {"ok": False, "error": "External API unavailable. Check internet and retry; no live data was obtained."}
        except OSError:
            return {"ok": False, "error": "File operation failed. Check the data folder and permissions."}
        except Exception:
            return {"ok": False, "error": "Unexpected tool failure; check inputs and retry."}
    return wrapped


def text(value, label):
    if not isinstance(value, str) or not value.strip() or len(value) > 200:
        raise ValueError(f"{label} must be a non-empty string of at most 200 characters.")
    return value.strip()


def number(value, label, minimum=0, maximum=1_000_000):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not minimum <= value <= maximum:
        raise ValueError(f"{label} must be a finite number between {minimum} and {maximum}.")
    return value


def integer(value, label, minimum=1, maximum=30):
    number(value, label, minimum, maximum)
    if not isinstance(value, int):
        raise ValueError(f"{label} must be an integer.")
    return value


def string_list(value, label):
    if not isinstance(value, list) or len(value) > 50:
        raise ValueError(f"{label} must be a list of at most 50 strings.")
    return [text(item, label) for item in value]


def fetch(url, params):
    response = requests.get(url, params=params, timeout=(5, 20))
    response.raise_for_status()
    return response.json()
