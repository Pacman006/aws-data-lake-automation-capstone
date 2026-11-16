"""Validation shared by the local producer and the Lambda stream processor."""

import math
import re
from datetime import datetime, timezone

DEVICE_ID = re.compile(r"^[A-Za-z0-9_-]{1,40}$")


class InvalidTelemetry(ValueError):
    pass


def _number(value, field, minimum, maximum):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InvalidTelemetry(f"{field} must be a number")
    if not math.isfinite(value) or not minimum <= value <= maximum:
        raise InvalidTelemetry(f"{field} must be between {minimum} and {maximum}")
    return round(float(value), 2)


def validate_record(record):
    """Return a cleaned event or raise InvalidTelemetry."""
    if not isinstance(record, dict):
        raise InvalidTelemetry("event must be a JSON object")
    device_id = record.get("device_id")
    event_id = record.get("event_id")
    if not isinstance(device_id, str) or not DEVICE_ID.fullmatch(device_id):
        raise InvalidTelemetry("device_id must contain 1-40 letters, numbers, '-' or '_'")
    if not isinstance(event_id, str) or not 1 <= len(event_id) <= 100:
        raise InvalidTelemetry("event_id must be a non-empty string (max 100 characters)")

    timestamp = record.get("event_time")
    if not isinstance(timestamp, str):
        raise InvalidTelemetry("event_time must be an ISO 8601 timestamp")
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise InvalidTelemetry("event_time is not a valid ISO 8601 timestamp") from exc
    if dt.tzinfo is None:
        raise InvalidTelemetry("event_time must include a timezone")

    codes = record.get("diagnostic_codes", [])
    if not isinstance(codes, list) or len(codes) > 20 or any(
        not isinstance(c, str) or len(c) > 30 for c in codes
    ):
        raise InvalidTelemetry("diagnostic_codes must be an array of up to 20 short strings")

    return {
        "event_id": event_id,
        "device_id": device_id,
        "event_time": dt.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "speed_kmh": _number(record.get("speed_kmh"), "speed_kmh", 0, 300),
        "fuel_percent": _number(record.get("fuel_percent"), "fuel_percent", 0, 100),
        "diagnostic_codes": codes,
    }
