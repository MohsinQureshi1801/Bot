from __future__ import annotations

from src.indicators import atr, ema
from src.models import Candle, Signal


def _swing_high(candles: list[Candle], i: int, w: int) -> bool:
    if i - w < 0 or i + w >= len(candles):
        return False
    h = candles[i].high
    return all(h >= candles[j].high for j in range(i - w, i + w + 1))


def _swing_low(candles: list[Candle], i: int, w: int) -> bool:
    if i - w < 0 or i + w >= len(candles):
        return False
    l = candles[i].low
    return all(l <= candles[j].low for j in range(i - w, i + w + 1))


def generate_signals(
    candles: list[Candle],
    ema_fast: int,
    ema_slow: int,
    atr_period: int,
    swing_window: int,
    rr: float,
    zone_pad_atr: float,
) -> list[Signal]:
    closes = [c.close for c in candles]
    ema_f = ema(closes, ema_fast)
    ema_s = ema(closes, ema_slow)
    at = atr(candles, atr_period)

    signals: list[Signal] = []
    last_high = None
    last_low = None

    for i in range(60, len(candles)):
        c = candles[i]
        if _swing_high(candles, i - 1, swing_window):
            last_high = candles[i - 1].high
        if _swing_low(candles, i - 1, swing_window):
            last_low = candles[i - 1].low

        if last_high is None or last_low is None:
            continue

        trend_up = ema_f[i] > ema_s[i]
        prev_trend_up = ema_f[i - 1] > ema_s[i - 1]

        bullish_bos = c.close > last_high
        bearish_bos = c.close < last_low
        bullish_choch = (not prev_trend_up) and bullish_bos
        bearish_choch = prev_trend_up and bearish_bos

        pad = at[i] * zone_pad_atr

        if trend_up and (bullish_bos or bullish_choch):
            demand_low = max(last_low, c.close - 1.5 * at[i])
            demand_high = demand_low + pad
            if demand_low <= c.low <= demand_high:
                entry = c.close
                stop = demand_low - pad
                risk = max(entry - stop, 0.01)
                signals.append(
                    Signal(
                        ts=c.ts,
                        direction="long",
                        entry=entry,
                        stop=stop,
                        tp=entry + risk * rr,
                        reason="uptrend + BOS/ChoCh + demand",
                    )
                )

        if (not trend_up) and (bearish_bos or bearish_choch):
            supply_high = min(last_high, c.close + 1.5 * at[i])
            supply_low = supply_high - pad
            if supply_low <= c.high <= supply_high:
                entry = c.close
                stop = supply_high + pad
                risk = max(stop - entry, 0.01)
                signals.append(
                    Signal(
                        ts=c.ts,
                        direction="short",
                        entry=entry,
                        stop=stop,
                        tp=entry - risk * rr,
                        reason="downtrend + BOS/ChoCh + supply",
                    )
                )

    return signals
