from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from random import random
from urllib.parse import urlencode
from urllib.request import urlopen

from src.models import Candle


TIME_FMT = "%Y-%m-%d %H:%M:%S"


def _pick(row: dict[str, str], keys: list[str], required: bool = True, default: str = "") -> str:
    lowered = {k.strip().lower(): v for k, v in row.items()}
    for key in keys:
        if key.lower() in lowered and lowered[key.lower()] not in (None, ""):
            return lowered[key.lower()]
    if required:
        raise ValueError(f"Missing required column. Expected one of: {keys}")
    return default


def load_csv(path: str | Path) -> list[Candle]:
    """
    Load CSV data in a tolerant way so real broker/vendor exports work.

    Supported aliases:
    - timestamp/date/time/datetime
    - open/high/low/close
    - volume/tick_volume
    """
    rows: list[Candle] = []
    with open(path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            ts_raw = _pick(r, ["timestamp", "datetime", "date", "time"])
            ts = _parse_timestamp(ts_raw)
            rows.append(
                Candle(
                    ts=ts,
                    open=float(_pick(r, ["open", "o"])),
                    high=float(_pick(r, ["high", "h"])),
                    low=float(_pick(r, ["low", "l"])),
                    close=float(_pick(r, ["close", "c"])),
                    volume=float(_pick(r, ["volume", "tick_volume", "vol"], required=False, default="0") or 0),
                )
            )

    rows.sort(key=lambda x: x.ts)
    if not rows:
        raise ValueError("CSV contained no candles")
    return rows


def _parse_timestamp(value: str) -> datetime:
    candidates = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y.%m.%d %H:%M:%S",
        "%Y.%m.%d %H:%M",
        "%d-%m-%Y %H:%M:%S",
        "%d-%m-%Y %H:%M",
    ]
    for fmt in candidates:
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
    # ISO fallback
    try:
        return datetime.fromisoformat(value.strip().replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError as exc:
        raise ValueError(f"Unsupported timestamp format: {value}") from exc


def fetch_twelvedata_xauusd_5m(api_key: str, output_size: int = 5000, timeout_s: int = 30) -> list[Candle]:
    """Download real XAU/USD 5m candles using Twelve Data REST API."""
    if not api_key:
        raise ValueError("TwelveData API key is required")

    query = urlencode(
        {
            "symbol": "XAU/USD",
            "interval": "5min",
            "outputsize": str(output_size),
            "apikey": api_key,
            "format": "JSON",
        }
    )
    url = f"https://api.twelvedata.com/time_series?{query}"

    with urlopen(url, timeout=timeout_s) as resp:
        payload = resp.read().decode("utf-8")

    data = json.loads(payload)
    if "status" in data and data["status"] == "error":
        raise RuntimeError(f"TwelveData error: {data.get('message', 'unknown error')}")
    if "values" not in data:
        raise RuntimeError("Unexpected TwelveData response: missing 'values'")

    out: list[Candle] = []
    for r in data["values"]:
        out.append(
            Candle(
                ts=_parse_timestamp(r["datetime"]),
                open=float(r["open"]),
                high=float(r["high"]),
                low=float(r["low"]),
                close=float(r["close"]),
                volume=float(r.get("volume", 0.0) or 0.0),
            )
        )

    out.sort(key=lambda x: x.ts)
    if not out:
        raise RuntimeError("No candles returned from TwelveData")
    return out


def save_csv(candles: list[Candle], path: str | Path) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "open", "high", "low", "close", "volume"])
        for c in candles:
            writer.writerow(
                [
                    c.ts.strftime(TIME_FMT),
                    f"{c.open:.3f}",
                    f"{c.high:.3f}",
                    f"{c.low:.3f}",
                    f"{c.close:.3f}",
                    f"{c.volume:.1f}",
                ]
            )
    return out


def generate_sample_data(bars: int = 1000) -> list[Candle]:
    """Generate deterministic-ish 5m synthetic XAUUSD-like data so you can test offline."""
    base = 2350.0
    ts = datetime(2024, 1, 1, 0, 0, 0)
    out: list[Candle] = []
    drift = 0.02
    for i in range(bars):
        wave = ((i % 80) - 40) * 0.03
        move = drift + wave * 0.02 + (random() - 0.5) * 0.9
        op = base
        cl = max(1000.0, op + move)
        hi = max(op, cl) + random() * 0.6
        lo = min(op, cl) - random() * 0.6
        out.append(Candle(ts=ts, open=op, high=hi, low=lo, close=cl, volume=100 + random() * 50))
        base = cl
        ts += timedelta(minutes=5)
    return out
