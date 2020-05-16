import json
import logging
import uuid
import os

import boto3

from poe_character_exporter.character import get_character, format_item

logger = logging.getLogger(__name__)
if os.environ.get("LOG_LEVEL"):
    logger.setLevel(os.environ["LOG_LEVEL"])
else:
    logger.setLevel("INFO")


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
            for item in character["items"]:
                ddb_item = format_item(item)
                ddb_item["character_name"] = c["character"]
                ddb_item["character_class"] = character["character"]["class"]
                ddb_item["character_level"] = character["character"]["level"]
                ddb_item["account_name"] = c["account"]
                poe_character_table.put_item(Item=ddb_item)
    return event


