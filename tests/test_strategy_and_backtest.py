import unittest

from src.data import generate_sample_data


class DataTest(unittest.TestCase):
    def test_sample_data_shape(self):
        candles = generate_sample_data(25)
        self.assertEqual(len(candles), 25)
        self.assertGreaterEqual(candles[0].high, candles[0].low)


if __name__ == "__main__":
    unittest.main()
