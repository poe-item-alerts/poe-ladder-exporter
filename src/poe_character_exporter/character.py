import logging
import time

import boto3
import requests

logging.basicConfig(
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)


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
