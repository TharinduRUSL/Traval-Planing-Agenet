from ._common import safe_tool
from ._catalog import TIPS, city_key


@safe_tool
def get_local_tips(city: str) -> dict:
    """Return curated food suggestions, etiquette and general travel precautions.

    Args:
        city: Colombo, Kandy, Paris or London.
    Returns:
        Local foods and practical tips; not current safety alerts or verified venues.
    """
    key = city_key(city)
    return {"city": key, **TIPS[key], "source": "curated general information; verify current local conditions"}
