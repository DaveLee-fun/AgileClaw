import json
import unittest
from unittest.mock import MagicMock, patch

from tools import reddit


class RedditToolTests(unittest.TestCase):
    @patch("tools.reddit.httpx.Client")
    def test_get_karma_success(self, client_cls):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "data": {
                "name": "example_user",
                "total_karma": 50,
                "link_karma": 20,
                "comment_karma": 30,
                "created_utc": 1700000000,
                "is_suspended": False,
            }
        }
        mock_client.get.return_value = mock_response
        client_cls.return_value.__enter__.return_value = mock_client

        result = reddit.get_karma("example_user")

        payload = json.loads(result)
        self.assertEqual(payload["username"], "example_user")
        self.assertEqual(payload["total_karma"], 50)

    @patch("tools.reddit.httpx.Client")
    def test_get_karma_http_error(self, client_cls):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = RuntimeError("boom")
        mock_client.get.return_value = mock_response
        client_cls.return_value.__enter__.return_value = mock_client

        result = reddit.get_karma("example_user")
        self.assertIn("Error getting Reddit karma", result)


if __name__ == "__main__":
    unittest.main()
