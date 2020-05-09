import logging
import json
import time
import collections

from decimal import Decimal

import boto3
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_character(account_name, character_name):
    logger.debug(f"Getting {character_name} from account: {account_name}")
    base_url = "http://www.pathofexile.com"
    url_path = f"character-window/get-items"
    url_options = f"character={character_name}&accountName={account_name}"
    character_url = f"{base_url}/{url_path}?{url_options}"
    headers = {"content-type": "application/json"}
    character = requests.get(character_url, headers=headers)
    resp_headers = character.headers
    if _rate_limit_backoff(resp_headers):
        return {
            "error": {
                "code": 2,
                "message": "Rate limit exceeded!"
            }
        }
    character_json = character.json()
    logger.debug(f"{character_json}")
    if character_json.get("error"):
        error = character_json["error"]
        if error["code"] == 1:
            logger.info(f"Character({character_name}) was deleted, skipping!")
        if error["code"] == 6:
            logger.info(f"Profile({account_name}) set to private, skipping!")
        else:
            logger.warning(f"Encountered error while running {account_name}: {error}")
        return {
            "error": {
                "code": 1,
                "message": "Character resource could not be loaded."
            }
        }
    logger.debug(f"Got {character_name}!")
    return character_json


def _rate_limit_backoff(headers):
    current_rate_status = headers["X-Rate-Limit-Ip-State"].split(",")
    rate_rules = headers["X-Rate-Limit-Ip"].split(",")
    for status, rule in zip(current_rate_status, rate_rules):
        c_rate, c_int, c_pen = status.split(":")
        m_rate, m_int, m_pen = rule.split(":")
        logger.debug(f"Current rate: {c_rate}, {c_int}, {c_pen}")
        logger.debug(f"Max rate: {m_rate}, {m_int}, {m_pen}")
        if int(c_rate) == 44:
            backoff_duration = 60
            logger.warning(f"Rate is at 44req/s backing off for {backoff_duration}s")
            return True
    return False


def format_character(character, account):
    logger.debug(f"Starting function format_character")
    parsed = remove_empty_string(json.loads(json.dumps(character), parse_float=Decimal))
    ddb_item = {
        "league_name": parsed["character"]["league"],
        "account_name": account,
        "character_name": parsed["character"]["name"],
        "character_class": parsed["character"]["class"],
        "character_level": parsed["character"]["level"],
        "items": [format_item(i) for i in parsed["items"]]
    }
    return ddb_item


def format_item(item):
    formatted_item = {
        "id": item["id"]
        "league": item["league"]
        "name": item["name"],
        "icon": item["icon"],
        "typeLine": item["typeLine"],
        "inventoryId": item["inventoryId"]
    }
    try:
        formatted_item["flavourText"] = item["flavourText"]
    except KeyError:
        formatted_item["flavourText"] = None
    try:
        formatted_item["craftedMods"] = item["craftedMods"]
    except KeyError:
        formatted_item["craftedMods"] = None
    try:
        formatted_item["explicitMods"] = item["explicitMods"]
    except KeyError:
        formatted_item["explicitMods"] = None
    try:
        links = format_sockets(item["sockets"])
        formatted_item["links"] = links
    except KeyError:
        formatted_item["links"] = 0
    return formatted_item


def format_sockets(sockets):
    groups = [s["group"] for s in sockets]
    count = collections.Counter(groups)
    links = max(count.values())
    return links


def remove_empty_string(dic):
    if isinstance(dic, str):
        if dic == "":
            return None
        else:
            return dic

    if isinstance(dic, list):
        conv = lambda i: i or None  # noqa: E731
        return [conv(i) for i in dic]

    for e in dic:
        if isinstance(dic[e], dict):
            dic[e] = remove_empty_string(dic[e])
        if isinstance(dic[e], str) and dic[e] == "":
            dic[e] = None
        if isinstance(dic[e], list):
            for entry in dic[e]:
                remove_empty_string(entry)

    return dic
