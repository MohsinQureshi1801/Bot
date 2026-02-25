import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from src.data import fetch_twelvedata_xauusd_5m


class TwelveDataErrorTest(unittest.TestCase):
    @patch("src.data._download_twelvedata")
    def test_http_403_has_helpful_message(self, mock_download):
        mock_download.side_effect = HTTPError(url="x", code=403, msg="Forbidden", hdrs=None, fp=None)
        with self.assertRaises(RuntimeError) as ctx:
            fetch_twelvedata_xauusd_5m(api_key="abc", output_size=100)
        self.assertIn("HTTP 403", str(ctx.exception))
        self.assertIn("--source csv", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
