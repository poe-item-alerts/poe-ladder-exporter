import json
import os

from unittest import TestCase
from unittest.mock import patch

from poe_ladder_exporter.ladder import ladder_export, _rate_limit_backoff, generate_events


class TestLadder(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch("poe_ladder_exporter.ladder.requests.get")
    def test_ladder_export_200(self, mock_get):
        this_dir = os.path.dirname(os.path.abspath(__file__))
        test_path = os.path.join(
            this_dir,
            "resources",
            "ladder_api_response.json"
        )
        mock_get.return_value.status_code = 200
        with open(test_path) as f:
            ladder_response = json.load(f)
        mock_get.return_value.json.return_value = ladder_response
        response = ladder_export("test_ladder")
        assert response == ladder_response

    @patch("poe_ladder_exporter.ladder.requests.get")
    def test_ladder_export_404(self, mock_get):
        mock_get.return_value.status_code = 404
        response = ladder_export("test_ladder")
        assert response == {}
    
    @patch("poe_ladder_exporter.ladder.requests.get")
    def test_ladder_export_unhandled(self, mock_get):
        mock_get.return_value.status_code = 401
        response = ladder_export("test_ladder")
        assert response == {}

    def test_rate_limit_no_violation(self):
        test_headers = {
            "X-Rate-Limit-Ip": "45:60:60,240:240:900",
            "X-Rate-Limit-Ip-State": "1:60:0,1:240:0"
        }
        _rate_limit_backoff(test_headers)
    
    @patch("poe_ladder_exporter.ladder.time.sleep")
    def test_rate_limit_violation(self, sleep_mock):
        test_headers = {
            "X-Rate-Limit-Ip": "45:60:60,240:240:900",
            "X-Rate-Limit-Ip-State": "44:60:0,44:240:0"
        }
        _rate_limit_backoff(test_headers)
        sleep_mock.assert_called_once()

    def test_generate_events(self):
        this_dir = os.path.dirname(os.path.abspath(__file__))
        test_path = os.path.join(
            this_dir,
            "resources",
            "ladder_api_response.json"
        )
        with open(test_path) as f:
            ladder_response = json.load(f)
        generate_events(ladder_response)
