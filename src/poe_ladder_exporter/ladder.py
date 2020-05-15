import json
import logging
import uuid
import time
import math

import requests


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def ladder_export(ladder_name):
    logger.debug(f"Started ladder_export function")
    ladder_result = []
    ladder_slice = _request_ladder(ladder_name, 0)
    ladder_result += ladder_slice["entries"]
    ladder_limit = 200
    ladder_total = ladder_limit
    if ladder_slice["total"] > ladder_limit:
        logger.info(f"Ladder total exceeds the current limit of {ladder_limit} and will be cut off.")
    else:
        ladder_total = ladder_slice["total"]
        logger.info(f"Ladder total entries are {ladder_total}")
    for i in range(math.ceil(ladder_total/ladder_limit)):
        ladder_slice = _request_ladder(ladder_name, i*200)
        if ladder_slice:
            ladder_result += ladder_slice["entries"]
        else:
            logger.warning(f"Encountered issues with the current ladder slice!")
            logger.warning(f"Error: {ladder_slice}")
    return ladder_result


def _request_ladder(name, offset, limit=200):
    logger.debug(f"Getting ladder for {name}")
    base_url = "http://api.pathofexile.com"
    url_path = f"ladders/{name}"
    ladder_url = f"{base_url}/{url_path}?limit={limit}&offset={offset}"
    logger.debug(f"Calling ladder api with: {ladder_url}")
    ladder_response = requests.get(ladder_url)
    if ladder_response.status_code == 200:
        logger.debug(f"Ladder API call successful")
        return ladder_response.json()
    elif ladder_response.status_code == 404:
        logger.debug(f"Ladder {name} not found!")
        return None
    else:
        logger.critical(f"Unhandled HTTP response code! Response: {ladder_response.text}")
        return None
    

def generate_events(ladder):
    logger.debug(f"Started send_events function")
    return 
    

def _rate_limit_backoff(headers):
    current_rate_status = headers["X-Rate-Limit-Ip-State"].split(",")
    rate_rules = headers["X-Rate-Limit-Ip"].split(",")
    for status, rule in zip(current_rate_status, rate_rules):
        c_rate, c_int, c_pen = status.split(":")
        m_rate, m_int, m_pen = rule.split(":")
        logger.debug(f"Current rate: {c_rate}, {c_int}, {c_pen}")
        logger.debug(f"Max rate: {m_rate}, {m_int}, {m_pen}")
        rate_ratio = int(c_rate) / int(m_rate)
        if rate_ratio > 0.9:
            backoff_duration = int(m_int) * 0.25
            logger.warning(f"Rate is exceeding 90% backing off for {backoff_duration}s")
            time.sleep(backoff_duration)
