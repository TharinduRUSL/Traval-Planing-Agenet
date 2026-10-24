from ._common import safe_tool, text, number, fetch


@safe_tool
def get_currency_conversion(amount: float, from_currency: str, to_currency: str) -> dict:
    """Convert an amount using the latest available Frankfurter reference rate.

    Args:
        amount: Non-negative amount to convert.
        from_currency: Source ISO currency code, for example USD.
        to_currency: Target ISO currency code, for example EUR.
    Returns:
        Converted amount, rate, rate date and source; unsupported codes are errors.
    """
    number(amount, "amount")
    source, target = text(from_currency, "from_currency").upper(), text(to_currency, "to_currency").upper()
    for code in (source, target):
        if len(code) != 3 or not code.isascii() or not code.isalpha():
            raise ValueError("Currencies must be three-letter ISO codes.")
    currencies = fetch("https://api.frankfurter.dev/v1/currencies", {})
    if source not in currencies or target not in currencies:
        raise ValueError("Currency is not supported by this reference-rate API (LKR may be unavailable). Keep the budget in USD or choose a supported currency.")
    if source == target:
        return {"amount": amount, "converted_amount": amount, "from": source, "to": target, "rate": 1, "rate_date": None, "source": "identity conversion"}
    data = fetch("https://api.frankfurter.dev/v1/latest", {"base": source, "symbols": target})
    rate = data["rates"][target]
    number(rate, "API exchange rate", 0.00000001, 1_000_000)
    return {"amount": amount, "from": source, "to": target, "converted_amount": round(amount * rate, 2), "rate": rate, "rate_date": data["date"], "source": "Frankfurter reference rate; excludes transaction fees"}
