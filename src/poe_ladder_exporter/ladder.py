import json
import logging
import uuid
import time

import requests


logger = logging.getLogger(__name__)


def ladder_export(ladder_name):
    logger.debug(f"Started ladder_export function")
    base_url = "http://api.pathofexile.com"
    url_path = f"ladders/{ladder_name}"
    ladder_url = f"{base_url}/{url_path}?limit=200"
    logger.debug(f"Calling {ladder_url}")
    ladder = requests.get(ladder_url)
    if ladder.status_code == 200:
        logger.debug(f"Got a successful response!")
        logger.debug(f"Returning ladder.")
        return ladder.json()
    elif ladder.status_code == 404:
        logger.warning(f"Ladder resource cannot be found, make sure it exists!")
        return {}
    else:
        logger.critical(
            f"Unhandled HTTP response code encountered! Dumping error: {ladder.json()}"
        )
        return {}


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
