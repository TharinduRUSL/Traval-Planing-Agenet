"""Member A: tool labels, examples and trace rendering."""
import streamlit as st

# Display labels are friendly; values match the existing nine-tool registry.
TOOL_CHOICES = {
    "All tools · full trip planning": None,
    "Weather": "get_weather",
    "Attractions": "search_attractions",
    "Travel time": "get_travel_time",
    "Budget": "calculate_budget",
    "Save itinerary": "save_itinerary",
    "Load itinerary": "load_itinerary",
    "Currency conversion": "get_currency_conversion",
    "Packing list": "get_packing_list",
    "Local tips": "get_local_tips",
}

EXAMPLES = {
    None: "Plan 2 days in Colombo starting tomorrow for one traveler with USD 70",
    "get_weather": "Weather in Colombo for tomorrow and the following day",
    "search_attractions": "Find museums and parks in Colombo",
    "get_travel_time": "Walking time from National Museum to Viharamahadevi Park in Colombo",
    "calculate_budget": "2 days, 1 traveler, meals USD 10/day, transport USD 5/day, total admissions USD 6, budget USD 70",
    "save_itinerary": "Save the complete plan above as my_trip.json",
    "load_itinerary": "Load my_trip.json",
    "get_currency_conversion": "Convert USD 100 to EUR",
    "get_packing_list": "Packing for walking and temples: 24–31°C, 80% chance of rain (assumed)",
    "get_local_tips": "Local food and travel tips for Colombo",
}


def render_trace(events):
    for event in events:
        with st.expander(f"Step {event['step']} · {event['name']}", expanded=False):
            st.caption("Arguments")
            st.json(event["arguments"])
            st.caption("Result")
            st.json(event["result"])


