import logging
import uuid

import boto3

from poe_character_exporter.character import get_character

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def handler(event, context):
    ddb = boto3.resource("dynamodb")
    if not event.get("CorrelationId"):
        logger.warning(f"Missing correlation id in the envent! Generating one...")
        correlation_id = uuid.uuid4()
    else:
        correlation_id = event["CorrelationId"]
    logger.debug(f"Started handler {correlation_id}")
    # due to the rate limiting of the poe character API
    for i in range(0,44):
        if not event["characters"]:
            logger.info(f"All characters processed, adding -1 to the event")
            event["characters"] = -1
        if event["characters"] == -1:
            break
        c = event["characters"].pop(0)
        character = get_character(c["account"], c["character"])
        if character.get("error"):
            error = character["error"]
            if error["code"] == 1:
                logger.info(f"Character could not be loaded, skipping...")
            elif error["code"] == 2:
                logger.warning(f"Early exit from the character loop, rate limit too high")
                break
        else:
            poe_character_table = ddb.Table("poe_item_alerts_characters") 
            parsed_char = json.loads(json.dumps(character), parse_float=Decimal)
            ddb_item = remove_empty_string(parsed_char)
            poe_character_table.put_item(
                Item={
                    "character_name": c["character"],
                    "account_name": c["account"],
                    "items": ddb_item
                }
            )
    return event


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
