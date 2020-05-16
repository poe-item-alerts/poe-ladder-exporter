import json
import logging
import uuid
import os

import boto3

from poe_ladder_exporter.ladder import ladder_export


logger = logging.getLogger(__name__)
if os.environ.get("LOG_LEVEL"):
    logger.setLevel(os.environ["LOG_LEVEL"])
else:
    logger.setLevel("INFO")


def handler(event, context):
    logger.debug(f"Started handler function")
    logger.debug(f"Creating boto3 ssm client to retrieve ladders")
    ssm = boto3.client("ssm")
    leagues = ssm.get_parameter(
        Name="/poe-item-alerts/character-load/ladders"
    )["Parameter"]["Value"]
    logger.info(f"Got ladder: {leagues}")
    logger.info(f"Starting ladder extraction process")
    ladder = ladder_export(leagues)
    if not ladder:
        logger.critical(f"There was an error getting the ladder! Exiting...")
        return
    logger.info(f"Got ladder with {len(ladder)} entries")
    logger.debug(f"Generating events per entry")
    entries = []
    for entry in ladder:
        tmp = {
            "account": entry["account"]["name"],
            "character": entry["character"]["name"]
        }
        entries.append(tmp)
    correlation_id = str(uuid.uuid4())
    return_event = {"CorrelationId": correlation_id, "characters": entries}
    client = boto3.client('stepfunctions')
    logger.info(f"Starting step function execution with {correlation_id}")
    try:
        response = client.start_execution(
            stateMachineArn="arn:aws:states:eu-central-1:983498139013:stateMachine:poe_character_exporter",
            name=f"{correlation_id}",
            input=json.dumps(return_event)
        )
        logger.info(f"Step function triggered successfully at {response['startDate']}")
    except client.exceptions.ExecutionLimitExceeded:
        logger.critical(f"Step function execution limit exceeded - we should not hit this")
    except client.exceptions.ExecutionAlreadyExists:
        logger.critical(f"Step function execution already exists - should never happen")
    return return_event
