import json
import os

from items import (format_item, get_item_max_links, get_item_rarity)


this_dir = os.path.dirname(os.path.abspath(__file__))


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


def test_get_item_max_links():
    test_sockets = [
        [
            {"group": 0, "sColour": "R", "attr": "S"}
        ],
        [
            {"group": 0, "sColour": "R", "attr": "S"},
            {"group": 0, "sColour": "R", "attr": "S"}
        ],
        [
            {"group": 0, "sColour": "R", "attr": "S"},
            {"group": 0, "sColour": "R", "attr": "S"},
            {"group": 0, "sColour": "R", "attr": "S"}
        ],
        [
            {"group": 0, "sColour": "R", "attr": "S"},
            {"group": 0, "sColour": "R", "attr": "S"},
            {"group": 0, "sColour": "R", "attr": "S"},
            {"group": 0, "sColour": "R", "attr": "S"}
        ],
        [
            {"group": 0, "sColour": "R", "attr": "S"},
            {"group": 0, "sColour": "R", "attr": "S"},
            {"group": 0, "sColour": "R", "attr": "S"},
            {"group": 0, "sColour": "R", "attr": "S"},
            {"group": 0, "sColour": "R", "attr": "S"}
        ],
        [
            {"group": 0, "sColour": "R", "attr": "S"},
            {"group": 0, "sColour": "R", "attr": "S"},
            {"group": 0, "sColour": "R", "attr": "S"},
            {"group": 0, "sColour": "R", "attr": "S"},
            {"group": 0, "sColour": "R", "attr": "S"},
            {"group": 0, "sColour": "R", "attr": "S"}
        ],
    ]
    for sockets in test_sockets:
        assert get_item_max_links(sockets) == len(sockets)


def test_get_item_rarity():
    frame_types = ["normal", "magic", "rare", "unique", "gem"]
    for i, frame in enumerate(frame_types):
        assert get_item_rarity(i) == frame

