import logging
import os
import sys

from urllib.parse import urlencode

import requests


logger = logging.getLogger(__name__)
if os.environ.get("LOG_LEVEL"):
    logger.setLevel(os.environ["LOG_LEVEL"])
else:
    logger.setLevel("INFO")


def get_character_items(account_name, character_name):
    """
    Gets a specific character from the poe frontend api, this is not an
    official resource but it has been stable for the time being. This
    function uses the https://www.pathofexile.com endpoint by passing
    in the account_name and character_name URL parameters to the
    `character-windows/get-items` path.

    args:
        account_name(str): Name of the account that the character
            belongs to
        character_name(str): Name of the character the items will be
            requested for
    returns:
        dict: JSON containing all items the character is currently
            wearing. https://app.swaggerhub.com/apis-docs/Chuanhsing/poe/1.0.0#/
    """
    response = _make_call("character-window/get-items",
                       parameters={
                           "accountName": account_name,
                           "character": character_name
                       },
                       headers={"content-type": "application/json"})
    response_json = response.json()
    # handling website api error response since they come back with 200s
    if response_json.get("error"):
        error = response_json["error"]
        if error["code"] == 1:
            logger.warning(f"Character {character_name} was deleted! Returning empty result.")
            return {}
        elif error["code"] == 6:
            logger.warning(f"Account {account_name} is set to private! Returning empty result.")
            return {}
        else:
            logger.critical(f"Unhandled error code from character-window API! Returning empty result and dumping error: {error}")
            return {}
    return response_json


def get_ladder(ladder_name, limit=44, offset=0):
    """
    Gets a specific amount of entries from the path of exile ladder api
    https://www.pathofexile.com/developer/docs/api-resource-ladders#get
    This function is assuming we're not hitting the rate limit of the
    ladder API during it's execution ever since it's only issueing one
    request at a time. Handling this logic is down to the calling
    function currently.
    
    args:
        ladder_name(str): The name identifier of a specific ladder 
            like "Racing Gauntlet Points Event (PL10667)"
        limit(int): The upper limit of characters returned by the
            ladder api
        offset(int): The offset on where to start getting
            ladder entries
    returns:
        dict: json repesentation documented on the api docs
            https://www.pathofexile.com/developer/docs/api-resource-ladders#get
    """
    logger.debug(f"ladder_export invoked for {ladder_name}")
    response = _make_call(
        f"ladders/{ladder_name}",
        parameters={"limit": limit, "offset": offset},
        headers={"content-type": "application/json"}
    )
    if response.status_code == 404:
        logger.warning(f"{ladder_name} is not a valid ladder returning empty result!")
        return {}
    elif response.status_code != 200 and response.status_code != 404:
        logger.critical(f"Unhandled {response.status_code} code in response! Response: {response.text}")
        sys.exit(1)
    return response.json()


def _make_call(path, parameters=None, headers=None,
               base_url="https://api.pathofexile.com"):
    """
    Executes an api call against the given path with the given parameters against
    the api in the base_url. Currently it is assumed that we make only GET requests
    so I did not bother implementing different methods.

    args:
        path(str): The url path to use for the call
        parameters(dict): Pass in a dictionary of param_name:param_val
        base_url(str): Base url for the call, varies from APIs usually since the poe
            apis are not streamlines at this point in time. The actual api domain is
            set as a default though.

    returns:
        response(obj): The response object of the requests library
    """
    if parameters is None:
        url = f"{base_url}/{path}"
    else:
        url = f"{base_url}/{path}?{urlencode(parameters)}"
    if headers is None:
        response = requests.get(url)
    else:
        response = requests.get(url, headers=headers)
    return response


# def _rate_limit_backoff(headers):
#     current_rate_status = headers["X-Rate-Limit-Ip-State"].split(",")
#     rate_rules = headers["X-Rate-Limit-Ip"].split(",")
#     for status, rule in zip(current_rate_status, rate_rules):
#         c_rate, c_int, c_pen = status.split(":")
#         m_rate, m_int, m_pen = rule.split(":")
#         logger.debug(f"Current rate: {c_rate}, {c_int}, {c_pen}")
#         logger.debug(f"Max rate: {m_rate}, {m_int}, {m_pen}")
#         rate_ratio = int(c_rate) / int(m_rate)
#         if rate_ratio > 0.9:
#             backoff_duration = int(m_int) * 0.25
#             logger.warning(f"Rate is exceeding 90% backing off for {backoff_duration}s")
#             time.sleep(backoff_duration)
