import json
import os

from unittest import TestCase
from unittest.mock import patch

import boto3

from moto import mock_ssm

from poe_ladder_exporter.handler import handler


class TestHandler(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    @mock_ssm
    @patch("poe_ladder_exporter.handler.ladder_export")
    def test_handler_happy_path(self, ladder_export_mock):
        this_dir = os.path.dirname(os.path.abspath(__file__))
        test_path = os.path.join(
            this_dir,
            "resources",
            "ladder_api_response.json"
        )
        with open(test_path) as f:
            ladder_response = json.load(f)
        ladder_export_mock.return_value = ladder_response
        ssm = boto3.client("ssm", region_name="eu-central-1")
        ssm.put_parameter(
            Name="/poe-item-alerts/character-load/ladders",
            Value="test",
            Type="String"
        )
        test_event = {"key": "value"}
        handler(test_event, None)
        ladder_export_mock.assert_called()


    @mock_ssm
    @patch("poe_ladder_exporter.handler.ladder_export")
    def test_handler_empty_ladder_export(self, ladder_export_mock):
        ssm = boto3.client("ssm", region_name="eu-central-1")
        ssm.put_parameter(
            Name="/poe-item-alerts/character-load/ladders",
            Value="test",
            Type="String"
        )
        ladder_export_mock.return_value = {}
        test_event = {"key": "value"}
        handler(test_event, None)
