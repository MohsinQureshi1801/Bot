from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from src.models import Candle, Signal


@dataclass
class Trade:
    entry_ts: str
    exit_ts: str
    direction: str
    entry: float
    exit: float
    pnl: float
    result: str
    reason: str


@dataclass
class Summary:
    total_trades: int
    win_rate: float
    net_profit: float
    ending_balance: float
    max_drawdown_pct: float


def run_backtest(
    candles: list[Candle],
    signals: list[Signal],
    initial_balance: float,
    risk_per_trade: float,
    fee_per_trade: float,
    max_bars_in_trade: int,
) -> tuple[list[Trade], Summary]:
    idx = {c.ts: i for i, c in enumerate(candles)}
    bal = initial_balance
    peak = bal
    max_dd = 0.0
    trades: list[Trade] = []

    for s in signals:
        if s.ts not in idx:
            continue
        start = idx[s.ts]
        risk_amt = bal * risk_per_trade
        per_unit_risk = (s.entry - s.stop) if s.direction == "long" else (s.stop - s.entry)
        if per_unit_risk <= 0:
            continue
        size = risk_amt / per_unit_risk

        exit_price = candles[start].close
        exit_ts = candles[start].ts
        result = "timeout"

        end = min(len(candles), start + 1 + max_bars_in_trade)
        for j in range(start + 1, end):
            c = candles[j]
            if s.direction == "long":
                if c.low <= s.stop:
                    exit_price = s.stop
                    exit_ts = c.ts
                    result = "loss"
                    break
                if c.high >= s.tp:
                    exit_price = s.tp
                    exit_ts = c.ts
                    result = "win"
                    break
            else:
                if c.high >= s.stop:
                    exit_price = s.stop
                    exit_ts = c.ts
                    result = "loss"
                    break
                if c.low <= s.tp:
                    exit_price = s.tp
                    exit_ts = c.ts
                    result = "win"
                    break

        gross = (exit_price - s.entry) * size if s.direction == "long" else (s.entry - exit_price) * size
        net = gross - fee_per_trade
        bal += net
        peak = max(peak, bal)
        dd = (peak - bal) / peak if peak else 0.0
        max_dd = max(max_dd, dd)

        trades.append(
            Trade(
                entry_ts=s.ts.strftime("%Y-%m-%d %H:%M:%S"),
                exit_ts=exit_ts.strftime("%Y-%m-%d %H:%M:%S"),
                direction=s.direction,
                entry=s.entry,
                exit=exit_price,
                pnl=net,
                result=result,
                reason=s.reason,
            )
        )

    total = len(trades)
    wins = sum(1 for t in trades if t.result == "win")
    summary = Summary(
        total_trades=total,
        win_rate=(wins / total * 100) if total else 0.0,
        net_profit=sum(t.pnl for t in trades),
        ending_balance=bal,
        max_drawdown_pct=max_dd * 100,
    )
    return trades, summary


def save_trades(trades: list[Trade], path: str | Path) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["entry_ts", "exit_ts", "direction", "entry", "exit", "pnl", "result", "reason"])
        for t in trades:
            w.writerow([t.entry_ts, t.exit_ts, t.direction, f"{t.entry:.3f}", f"{t.exit:.3f}", f"{t.pnl:.2f}", t.result, t.reason])
    return out
