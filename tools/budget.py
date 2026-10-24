from decimal import Decimal, ROUND_HALF_UP
from ._common import safe_tool, number, integer, text


@safe_tool
def calculate_budget(days: int, travelers: int, daily_meals: float, daily_transport: float, total_admissions: float, budget: float, currency: str = "USD", contingency_percent: float = 10) -> dict:
    """Calculate trip costs consistently for the whole group, excluding lodging/flights.

    Args:
        days: Trip duration, 1 to 30 days.
        travelers: Number of travelers, 1 to 20.
        daily_meals: Meal cost per person per day in the stated currency.
        daily_transport: Local transport cost per person per day in stated currency.
        total_admissions: Sum of all trip admissions per person in stated currency.
        budget: Total group budget in stated currency.
        currency: Three-letter currency code; all inputs must use this currency.
        contingency_percent: Extra percentage added to the subtotal, 0 to 100.
    Returns:
        Cost breakdown, total, remaining budget and within_budget boolean.
    """
    integer(days, "days"); integer(travelers, "travelers", 1, 20)
    for name, value in (("daily_meals", daily_meals), ("daily_transport", daily_transport), ("total_admissions", total_admissions), ("budget", budget)):
        number(value, name)
    number(contingency_percent, "contingency_percent", 0, 100)
    currency = text(currency, "currency").upper()
    if len(currency) != 3 or not currency.isascii() or not currency.isalpha():
        raise ValueError("currency must be a three-letter code.")
    d = lambda v: Decimal(str(v))
    money = lambda v: float(v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    meals = d(daily_meals) * days * travelers
    transport = d(daily_transport) * days * travelers
    admissions = d(total_admissions) * travelers
    subtotal = meals + transport + admissions
    contingency = d(money(subtotal * d(contingency_percent) / 100))
    total = d(money(subtotal + contingency))
    return {"currency": currency, "meals": money(meals), "transport": money(transport), "admissions": money(admissions), "contingency": money(contingency), "total": money(total), "remaining": money(d(budget)-total), "within_budget": total <= d(budget), "scope": "whole group; excludes flights and accommodation; inputs are estimates"}
