# XAUUSD 5m Supply/Demand Bot (No MT5, No TradingView)

This bot now supports **real XAUUSD 5m market data** (Twelve Data API) and still supports CSV + offline sample data.

## Features

- Supply & Demand zones
- Trend filter (EMA20/EMA50)
- BOS (Break of Structure)
- ChoCh (Change of Character)
- SL/TP with risk-based sizing
- Backtest report + trade CSV export

---

## Quick Start

### 1) Create venv

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install

```bash
pip install -r requirements.txt
```

### 3) Run with sample data (instant)

```bash
python run_bot.py --source sample --bars 1200
```

### 4) Run with your own real XAUUSD 5m CSV

```bash
python run_bot.py --source csv --csv /path/to/xauusd_5m.csv
```

Accepted CSV headers are flexible (case-insensitive), including common broker exports:

- timestamp/datetime/date/time
- open/high/low/close
- volume/tick_volume/vol

Accepted time formats include:

- `YYYY-MM-DD HH:MM:SS`
- `YYYY-MM-DD HH:MM`
- `YYYY.MM.DD HH:MM:SS`
- `YYYY.MM.DD HH:MM`
- ISO datetime

### 5) Run on real API data (XAU/USD 5m)

1. Get a free Twelve Data API key: https://twelvedata.com/
2. Run:

```bash
python run_bot.py --source twelvedata --api-key YOUR_KEY --bars 5000
```

This downloads real 5m XAU/USD candles, saves them to `data/xauusd_5m_twelvedata.csv`, then runs the full strategy + backtest.

---

## Output files

- `data/trades.csv` → trade-by-trade results
- `data/xauusd_5m_sample.csv` or `data/xauusd_5m_twelvedata.csv` depending on source

---

## Strategy logic

- Trend: EMA20 > EMA50 (bull), EMA20 < EMA50 (bear)
- Structure: rolling swing highs/lows
- BOS: break of last swing in trend direction
- ChoCh: break opposite previous trend
- Entry: BOS/ChoCh + touch of demand/supply zone (ATR-padded)
- Exit: SL/TP or timeout

---

## Tests

```bash
python -m unittest discover -s tests -v
```

---

## Tune settings

Edit `src/config.py`:

- `rr`
- `risk_per_trade`
- `ema_fast`, `ema_slow`
- `swing_window`
- `zone_pad_atr`
- `max_bars_in_trade`

---

## Notes

- Research/backtesting only, not financial advice.
- For live trading, add broker integration and execution safeguards.
