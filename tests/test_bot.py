import unittest

from src.backtest import run_backtest
from src.config import BotConfig
from src.data import generate_sample_data
from src.strategy import generate_signals


class BotFlowTest(unittest.TestCase):
    def test_end_to_end_generates_summary(self):
        cfg = BotConfig()
        candles = generate_sample_data(300)
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

        self.assertEqual(summary.total_trades, len(trades))
        self.assertGreater(summary.ending_balance, 0)


if __name__ == "__main__":
    unittest.main()
