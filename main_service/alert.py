ALERT_RULES = {
    "AAPL": {"target": 220, "direction": "above"},
    "TSLA": {"target": 150, "direction": "below"},
    "NVDA": {"target": 1000, "direction": "above"},
}


def check_alert(symbol: str, price: float) -> dict | None:
    rule = ALERT_RULES.get(symbol.upper())
    if not rule:
        return None

    direction = rule["direction"]
    target = rule["target"]

    if direction == "above" and price >= target:
        return {
            "symbol": symbol.upper(),
            "price": price,
            "condition": "above",
            "threshold": target,
            "message": f"{symbol.upper()} crossed above {target}",
        }

    if direction == "below" and price <= target:
        return {
            "symbol": symbol.upper(),
            "price": price,
            "condition": "below",
            "threshold": target,
            "message": f"{symbol.upper()} crossed below {target}",
        }

    return None