import json
import logging
import uuid

import boto3

from poe_ladder_exporter.ladder import ladder_export, generate_events


logging.basicConfig(
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)


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
    return_event = {"CorrelationId": uuid.uuid4(), "characters": ladder["entries"]}
    client = boto3.client('stepfunctions')
    client.start_execution(
        stateMachineArn="arn:aws:states:eu-central-1:983498139013:stateMachine:poe_character_exporter",
        name="Run for {leagues}",
        input=json.dumps(return_event)
    )
    return return_event
