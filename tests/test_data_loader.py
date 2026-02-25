import tempfile
import unittest
from pathlib import Path

from src.data import load_csv


class CsvCompatibilityTest(unittest.TestCase):
    def test_accepts_common_real_data_headers(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "real.csv"
            p.write_text(
                "Date,Open,High,Low,Close,Tick_Volume\n"
                "2024.01.01 00:00,2000,2001,1999,2000.5,123\n",
                encoding="utf-8",
            )
            candles = load_csv(p)
            self.assertEqual(len(candles), 1)
            self.assertEqual(candles[0].open, 2000.0)
            self.assertEqual(candles[0].volume, 123.0)


if __name__ == "__main__":
    unittest.main()
