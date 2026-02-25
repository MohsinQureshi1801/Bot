from dataclasses import dataclass


@dataclass
class BotConfig:
    pair: str = "XAUUSD"
    timeframe: str = "5m"
    ema_fast: int = 20
    ema_slow: int = 50
    atr_period: int = 14
    swing_window: int = 3
    rr: float = 2.0
    zone_pad_atr: float = 0.25
    initial_balance: float = 10_000.0
    risk_per_trade: float = 0.01
    fee_per_trade: float = 1.0
    max_bars_in_trade: int = 72
