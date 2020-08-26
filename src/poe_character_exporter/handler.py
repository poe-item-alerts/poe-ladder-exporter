import json
import logging
import uuid
import os

from datetime import timezone, datetime

import boto3

from character import get_character

logger = logging.getLogger(__name__)
if os.environ.get("LOG_LEVEL"):
    logger.setLevel(os.environ["LOG_LEVEL"])
else:
    logger.setLevel("INFO")


def handler(event, context):
    ddb = boto3.resource("dynamodb")
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
            poe_character_table.put_item(Item=character)
            logger.info(f"Ingested {c['character']}")
    return event


