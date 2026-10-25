"""The sole tool registry: exactly nine functions are exposed to Ollama."""
from .weather import get_weather
from .attractions import search_attractions
from .travel_time import get_travel_time
from .budget import calculate_budget
from .itinerary import save_itinerary, load_itinerary
from .currency import get_currency_conversion
from .packing import get_packing_list
from .local_tips import get_local_tips

TOOLS = [get_weather, search_attractions, get_travel_time, calculate_budget,
         save_itinerary, load_itinerary, get_currency_conversion,
         get_packing_list, get_local_tips]
TOOL_MAP = {tool.__name__: tool for tool in TOOLS}
