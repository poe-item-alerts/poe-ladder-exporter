import json
import logging
import uuid

import boto3

from poe_ladder_exporter.ladder import ladder_export, generate_events


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def handler(event, context):
    logger.debug(f"Creating boto3 ssm client to retrieve ladders...")
    ssm = boto3.client("ssm")
    leagues = ssm.get_parameter(
        Name="/poe-item-alerts/character-load/ladders"
    )["Parameter"]["Value"]
    logger.info(f"Starting ladder extraction process...")
    ladder = ladder_export(leagues)
    if not ladder:
        logger.critical(f"There was an error getting the ladder! Exiting...")
        return
    logger.info(f"Got ladder with {len(ladder['entries'])} entries")
    logger.info(f"Starting to generate events per entry")
    entries = []
    for entry in ladder["entries"]:
        tmp = {
            "account": entry["account"]["name"],
            "character": entry["character"]["name"]
        }
        entries.append(tmp)
    correlation_id = str(uuid.uuid4())
    return_event = {"CorrelationId": correlation_id, "characters": entries}
    client = boto3.client('stepfunctions')
    client.start_execution(
        stateMachineArn="arn:aws:states:eu-central-1:983498139013:stateMachine:poe_character_exporter",
        name=f"{correlation_id}",
        input=json.dumps(return_event)
    )
    return return_event
