from __future__ import annotations

import argparse
import os
from pathlib import Path

from src.backtest import run_backtest, save_trades
from src.config import BotConfig
from src.data import fetch_twelvedata_xauusd_5m, generate_sample_data, load_csv, save_csv
from src.strategy import generate_signals


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="XAUUSD 5m supply-demand bot")
    p.add_argument(
        "--source",
        choices=["sample", "csv", "twelvedata"],
        default="sample",
        help="Data source to use",
    )
    p.add_argument("--csv", default="", help="CSV path when --source csv")
    p.add_argument(
        "--api-key",
        default="",
        help="TwelveData API key when --source twelvedata (or set TWELVEDATA_API_KEY env var)",
    )
    p.add_argument("--bars", type=int, default=1200, help="Bars for sample or API output size")
    p.add_argument("--output-dir", default="data", help="Folder for outputs")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cfg = BotConfig()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.source == "csv":
        if not args.csv:
            raise ValueError("--csv is required when --source csv")
        candles = load_csv(args.csv)
        source = args.csv

    elif args.source == "twelvedata":
        api_key = args.api_key or os.getenv("TWELVEDATA_API_KEY", "")
        candles = fetch_twelvedata_xauusd_5m(api_key=api_key, output_size=args.bars)
        source = str(save_csv(candles, out_dir / "xauusd_5m_twelvedata.csv"))
        print(f"Downloaded real XAUUSD 5m data to: {source}")

    else:
        candles = generate_sample_data(args.bars)
        source = str(save_csv(candles, out_dir / "xauusd_5m_sample.csv"))
        print(f"Generated sample data at: {source}")

    signals = generate_signals(
        candles,
        ema_fast=cfg.ema_fast,
        ema_slow=cfg.ema_slow,
        atr_period=cfg.atr_period,
        swing_window=cfg.swing_window,
        rr=cfg.rr,
        zone_pad_atr=cfg.zone_pad_atr,
    )

    trades, summary = run_backtest(
        candles,
        signals,
        initial_balance=cfg.initial_balance,
        risk_per_trade=cfg.risk_per_trade,
        fee_per_trade=cfg.fee_per_trade,
        max_bars_in_trade=cfg.max_bars_in_trade,
    )

    trades_path = save_trades(trades, out_dir / "trades.csv")

    print("\n=== BOT SUMMARY ===")
    print(f"Pair: {cfg.pair} | Timeframe: {cfg.timeframe}")
    print(f"Data source: {source}")
    print(f"Candles: {len(candles)}")
    print(f"Signals: {len(signals)}")
    print(f"Total trades: {summary.total_trades}")
    print(f"Win rate: {summary.win_rate:.2f}%")
    print(f"Net profit: {summary.net_profit:.2f}")
    print(f"Ending balance: {summary.ending_balance:.2f}")
    print(f"Max drawdown: {summary.max_drawdown_pct:.2f}%")
    print(f"Trades CSV: {trades_path}")


if __name__ == "__main__":
    main()
