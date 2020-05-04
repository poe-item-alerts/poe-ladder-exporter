from unittest import TestCase

from poe_ladder_exporter.handler import handler


class TestHandler(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_handler_happy_path(self):
        test_event = {"key": "value"}
        handler(test_event, None)
