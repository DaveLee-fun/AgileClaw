import json
import unittest
from unittest.mock import MagicMock, patch

from tools import threads


class ThreadsToolTests(unittest.TestCase):
    @patch("tools.threads.httpx.Client")
    def test_get_followers_success(self, client_cls):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "id": "12345",
            "followers_count": 321,
        }
        mock_client.get.return_value = mock_response
        client_cls.return_value.__enter__.return_value = mock_client

        result = threads.get_followers(
            user_id="12345",
            access_token="token",
            fields="followers_count",
        )

        payload = json.loads(result)
        self.assertEqual(payload["user_id"], "12345")
        self.assertEqual(payload["followers_count"], 321)

    @patch("tools.threads.httpx.Client")
    def test_get_followers_http_error(self, client_cls):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = RuntimeError("boom")
        mock_client.get.return_value = mock_response
        client_cls.return_value.__enter__.return_value = mock_client

        result = threads.get_followers(
            user_id="12345",
            access_token="token",
        )

        self.assertIn("Error getting Threads metrics", result)


if __name__ == "__main__":
    unittest.main()
