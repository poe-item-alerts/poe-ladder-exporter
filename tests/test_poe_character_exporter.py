import json
import os

import boto3
import pytest
import requests
from moto import mock_dynamodb2
from requests_mock import ANY as http_any

from character import get_character, format_item
from handler import handler


this_dir = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def ddb_character_table(ddb_mock):
    ddb_mock.create_table(
        TableName="poe_item_alerts_characters",
        KeySchema=[
            {
                "AttributeName": "character_name",
                "KeyType": "HASH"
            }
        ],
        AttributeDefinitions=[
            {
                "AttributeName": "character_name",
                "AttributeType": "S"
            }
        ]
    )
        
        
def test_handler_happy_path(mocker, ddb_character_table):
    formatted_character_path = os.path.join(
        this_dir,
        "poe_api_responses",
        "formatted_character.json"
    )
    with open(formatted_character_path) as f:
        formatted_character = json.load(f)

    mocker.patch("handler.get_character", return_value=formatted_character)
    event = {
        "characters": [
            {
                "account": "TestAccount",
                "character": "TestCharacter"
            }
        ]
    }
    result = handler(event, {})
    assert result == {"characters": -1}


def test_handler_character_error(mocker, ddb_character_table):
    formatted_character_path = os.path.join(
        this_dir,
        "poe_api_responses",
        "formatted_character.json"
    )
    with open(formatted_character_path) as f:
        formatted_character = json.load(f)

    mocker.patch("handler.get_character", return_value={"error": { "code": 1}})
    event = {
        "characters": [
            {
                "account": "TestAccount",
                "character": "TestCharacter"
            }
        ]
    }
    result = handler(event, {})
    assert result == {"characters": -1}


def test_handler_rate_limit_error(mocker, ddb_character_table):
    formatted_character_path = os.path.join(
        this_dir,
        "poe_api_responses",
        "formatted_character.json"
    )
    with open(formatted_character_path) as f:
        formatted_character = json.load(f)

    mocker.patch("handler.get_character", return_value={"error": { "code": 2}})
    event = {
        "characters": [
            {
                "account": "TestAccount",
                "character": "TestCharacter"
            }
        ]
    }
    result = handler(event, {})
    assert result == {"characters": []}

    
def test_get_character_happy_path(requests_mock):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    get_items_response_path = os.path.join(
        this_dir,
        "poe_api_responses",
        "character_window_get_items.json"
    )
    with open(get_items_response_path) as f:
        get_items_response = json.load(f)
    
    formatted_items_path = os.path.join(
        this_dir,
        "poe_api_responses",
        "formatted_items_test.json"
    )
    with open(formatted_items_path) as f:
        formatted_items = json.load(f)

    requests_mock.get(
        http_any,
        json=get_items_response,
        headers={
            "X-Rate-Limit-Ip": "45:60:60,240:240:900",
            "X-Rate-Limit-Ip-State": "1:60:0,3:240:0"
        }
    )
    result = get_character("foo", "bar")
    assert result["league_name"] == get_items_response["character"]["league"]
    assert result["account_name"] == "foo"
    assert result["character_name"] == get_items_response["character"]["name"]
    assert result["character_class"] == get_items_response["character"]["class"]
    assert result["character_level"] == get_items_response["character"]["level"]
    # the test data has all the fields that should be `None` set to `null`
    # since json.load parses it to None
    assert result["items"] == formatted_items["items"]


def test_get_character__poe_api_error_code_1(requests_mock):

    requests_mock.get(
        http_any,
        json={"error": {"code": 1}},
        headers={
            "X-Rate-Limit-Ip": "45:60:60,240:240:900",
            "X-Rate-Limit-Ip-State": "1:60:0,3:240:0"
        }
    )
    result = get_character("foo", "bar")
    print(result)
    assert result == {"error": {"code": 1, "message": "Character resource could not be loaded."}}


def test_get_character_poe_api_error_code_6(requests_mock):

    requests_mock.get(
        http_any,
        json={"error": {"code": 6}},
        headers={
            "X-Rate-Limit-Ip": "45:60:60,240:240:900",
            "X-Rate-Limit-Ip-State": "1:60:0,3:240:0"
        }
    )
    result = get_character("foo", "bar")
    print(result)
    assert result == {"error": {"code": 1, "message": "Character resource could not be loaded."}}


def test_get_character_poe_api_rate_limit(requests_mock):

    requests_mock.get(
        http_any,
        json={},
        headers={
            "X-Rate-Limit-Ip": "45:60:60,240:240:900",
            "X-Rate-Limit-Ip-State": "44:60:0,44:240:0"
        }
    )
    result = get_character("foo", "bar")
    print(result)
    assert result == {"error": {"code": 2, "message": "Rate limit exceeded!"}}


def test_format_item_happy_path():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    test_path = os.path.join(
        this_dir,
        "poe_api_responses",
        "test_item_boots_no_gems.json"
    )
    with open(test_path) as f:
        test_item = json.load(f)

    result = format_item(test_item)
    assert result["id"] == test_item["id"]
    assert result["league"] == test_item["league"]
    assert result["name"] == test_item["name"]
    assert result["icon"] == test_item["icon"]
    assert result["typeLine"] == test_item["typeLine"]
    assert result["flavourText"] == None
    assert result["craftedMods"] == test_item["craftedMods"]
    assert result["explicitMods"] == test_item["explicitMods"]
    assert result["links"] == 4


def test_format_item_no_mods():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    test_path = os.path.join(
        this_dir,
        "poe_api_responses",
        "test_item_boots_no_gems_no_mods_no_sockets.json"
    )
    with open(test_path) as f:
        test_item = json.load(f)

    result = format_item(test_item)
    assert result["id"] == test_item["id"]
    assert result["league"] == test_item["league"]
    assert result["name"] == test_item["name"]
    assert result["icon"] == test_item["icon"]
    assert result["typeLine"] == test_item["typeLine"]
    assert result["flavourText"] == None
    assert result["craftedMods"] == None
    assert result["explicitMods"] == None
    assert result["links"] == 0
