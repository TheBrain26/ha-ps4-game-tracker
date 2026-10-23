"""One-time helper snapshots; no inferred sessions or overlapping totals."""

from datetime import date, datetime, timedelta
from math import isfinite

PERIOD_KEYS = ("today", "week", "month", "year")
HELPER_DOMAINS = {
    **{key: "input_number" for key in PERIOD_KEYS},
    "last_duration": "input_number",
    "last_game": "input_text",
    "history": "input_text",
    "last_end": "input_datetime",
}


def period_start(day: date, period: str) -> date:
    if period == "today":
        return day
    if period == "week":
        return day - timedelta(days=day.weekday())
    if period == "month":
        return day.replace(day=1)
    if period == "year":
        return day.replace(month=1, day=1)
    raise ValueError(period)


def snapshot_helpers(states: dict[str, str], captured_at: datetime) -> dict:
    """Validate all fields before returning a complete immutable snapshot."""
    if any(key not in states or states[key] in ("unknown", "unavailable")
           for key in HELPER_DOMAINS):
        raise ValueError("missing_helper")
    values = {}
    for key in (*PERIOD_KEYS, "last_duration"):
        try:
            value = float(states[key])
        except (ValueError, TypeError) as err:
            raise ValueError("invalid_minutes") from err
        if not isfinite(value) or value < 0:
            raise ValueError("invalid_minutes")
        values[key] = value
    try:
        if "T" not in states["last_end"] and " " not in states["last_end"]:
            raise ValueError("date_only")
        datetime.fromisoformat(states["last_end"])
    except (ValueError, TypeError) as err:
        raise ValueError("invalid_last_end") from err
    day = captured_at.date()
    return {
        "captured_at": captured_at.isoformat(),
        "periods": {
            key: {"start": period_start(day, key).isoformat(),
                  "minutes": values[key]}
            for key in PERIOD_KEYS
        },
        "last_game": states["last_game"],
        "last_duration": values["last_duration"],
        "last_end": states["last_end"],
        "history": states["history"],
    }


def baseline_minutes(legacy: dict, day: date, period: str) -> float:
    """Expire each imported aggregate at its own local period boundary."""
    item = legacy.get("periods", {}).get(period, {})
    if item.get("start") == period_start(day, period).isoformat():
        return item["minutes"]
    return 0.0
