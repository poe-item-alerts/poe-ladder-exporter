import json
import os
import uuid

from unittest import TestCase
from unittest.mock import patch

from poe_character_exporter.handler import handler
from poe_character_exporter.character import get_character, _rate_limit_backoff


class TestHandler(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    # @patch("poe_character_exporter.handler.requests.get")
    @patch("poe_character_exporter.handler.get_character")
    def test_handler_happy_path(self, get_character_mock):
        this_dir = os.path.dirname(os.path.abspath(__file__))
        ladder_response_path = os.path.join(
            this_dir,
            "resources",
            "ladder_api_response.json"
        )
        with open(ladder_response_path) as f:
            ladder_response = json.load(f)
        test_event = {}
        test_event["characters"] = ladder_response["entries"]
        test_event["CorrelationId"] = uuid.uuid4()
        response = handler(test_event, None)
        get_character_mock.assert_called()
        assert response["characters"] == -1

    @patch("poe_character_exporter.character.requests.get")
    def test_get_character_happy(self, requests_mock):
        this_dir = os.path.dirname(os.path.abspath(__file__))
        character_response_path = os.path.join(
            this_dir,
            "resources",
            "character_api_response.json"
        ) 
        with open(character_response_path) as f:
            character_response = json.load(f)
        requests_mock.return_value = character_response
        test_headers = {
            "X-Rate-Limit-Ip": "45:60:60,240:240:900",
            "X-Rate-Limit-Ip-State": "1:60:0,1:240:0"
        }
        requests_mock.headers.get.return_value = test_headers
        response = get_character("test_account", "test_character")
        requests_mock.assert_called()
        assert response == character_response



    def test_rate_limit_no_violation(self):
        test_headers = {
            "X-Rate-Limit-Ip": "45:60:60,240:240:900",
            "X-Rate-Limit-Ip-State": "1:60:0,1:240:0"
        }
        response = _rate_limit_backoff(test_headers)
        assert response == False
    
    @patch("poe_ladder_exporter.ladder.time.sleep")
    def test_rate_limit_violation(self, sleep_mock):
        test_headers = {
            "X-Rate-Limit-Ip": "45:60:60,240:240:900",
            "X-Rate-Limit-Ip-State": "44:60:0,44:240:0"
        }
        response = _rate_limit_backoff(test_headers)
        assert response == True
