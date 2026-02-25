from __future__ import annotations

from src.models import Candle


def ema(values: list[float], period: int) -> list[float]:
    if not values:
        return []
    k = 2 / (period + 1)
    out = [values[0]]
    for v in values[1:]:
        out.append(v * k + out[-1] * (1 - k))
    return out


def atr(candles: list[Candle], period: int) -> list[float]:
    trs: list[float] = []
    for i, c in enumerate(candles):
        if i == 0:
            tr = c.high - c.low
        else:
            prev = candles[i - 1]
            tr = max(c.high - c.low, abs(c.high - prev.close), abs(c.low - prev.close))
        trs.append(tr)

    out: list[float] = []
    for i in range(len(trs)):
        start = max(0, i - period + 1)
        window = trs[start : i + 1]
        out.append(sum(window) / len(window))
    return out
