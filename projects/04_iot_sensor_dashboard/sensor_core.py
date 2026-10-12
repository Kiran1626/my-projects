"""Pure logic for the dashboard (no network), so it can be unit tested."""
import json
from collections import deque
from dataclasses import dataclass
from datetime import datetime

TEMP_LIMIT_C = 35.0
HUMIDITY_LIMIT = 80.0


@dataclass
class Reading:
    device: str
    temperature: float
    humidity: float
    ts: datetime


def parse_payload(raw: bytes | str) -> Reading:
    """Parse a JSON payload like {"device":"esp32-01","temp":27.4,"hum":55.2}. Raises ValueError if invalid."""
    try:
        data = json.loads(raw)
        temp, hum = float(data["temp"]), float(data["hum"])
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Bad sensor payload: {exc}") from exc
    if not (-40 <= temp <= 125) or not (0 <= hum <= 100):
        raise ValueError(f"Reading out of sensor range: temp={temp}, hum={hum}")
    return Reading(str(data.get("device", "unknown")), temp, hum, datetime.now())


def check_alerts(r: Reading) -> list[str]:
    alerts = []
    if r.temperature > TEMP_LIMIT_C:
        alerts.append(f"HIGH TEMP {r.temperature:.1f}C (limit {TEMP_LIMIT_C}C)")
    if r.humidity > HUMIDITY_LIMIT:
        alerts.append(f"HIGH HUMIDITY {r.humidity:.1f}% (limit {HUMIDITY_LIMIT}%)")
    return alerts


class Window:
    """Keeps the latest N readings for plotting and simple statistics."""
    def __init__(self, size: int = 60):
        self.data: deque[Reading] = deque(maxlen=size)

    def add(self, r: Reading) -> None:
        self.data.append(r)

    def stats(self) -> dict:
        if not self.data:
            return {"count": 0}
        t = [r.temperature for r in self.data]
        h = [r.humidity for r in self.data]
        return {"count": len(t), "temp_avg": round(sum(t) / len(t), 2), "temp_max": max(t),
                "hum_avg": round(sum(h) / len(h), 2), "hum_max": max(h)}
