import os
import logging

import boto3


logger = logging.getLogger(__name__)
if os.environ.get("LOG_LEVEL"):
    logger.setLevel(os.environ["LOG_LEVEL"])
else:
    logger.setLevel("INFO")


def dig_grave(character):
    logger.info("Starting to dig grave for {character}")
    client = boto3.client("dynamodb")
    paginator = client.get_paginator("scan")
    item_iterator = paginator.paginate(
        TableName="poe_item_alerts_characters",
        FilterExpression="character_name IN (:character)",
        ExpressionAttributeValues={
            ":character": {"S": character}
        }
    )
    for i in item_iterator:
        if i["Items"]:
            logger.info(f"Found {len(i['Items'])} items for our grave")
            for item in i["Items"]:
                item["dead"] = {"BOOL": True}
                logger.debug(f"Putting {item['id']} in the grave")
                response = client.put_item(
                    TableName="poe_item_alerts_characters",
                    Item=item
                )
                logger.debug(f"{response}")
                if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                    logger.info("{item['id']} arrived in the grave")
                else:
                    logger.warning(f"There was an issue with the item: {response}")
            logger.info(f"Grave dug for {character}")

