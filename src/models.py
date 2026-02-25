from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Candle:
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class Signal:
    ts: datetime
    direction: str  # long | short
    entry: float
    stop: float
    tp: float
    reason: str
