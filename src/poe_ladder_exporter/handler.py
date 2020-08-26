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
    client = boto3.client("lambda")
    ssm = boto3.client("ssm")
    leagues = ssm.get_parameter(
        Name="/poe-item-alerts/character-load/ladders"
    )["Parameter"]["Value"]
    logger.info(f"Got ladder: {leagues}")
    logger.info(f"Starting ladder extraction process")
    ladder = ladder_export(leagues)
    logger.info(f"Got ladder with {len(ladder)} entries")
    if len(ladder) < 1:
        logger.warning("Ladder is empty, has the event started?")
        return
    logger.debug(f"Generating events per entry")
    entries = []
    for entry in ladder:
        if entry["dead"]:
            # TODO: exception handling here - needs a retry logic on the invocation for a timeout
            # and just a warning if the lambda does not accept the events
            client.invoke(
                FunctionName="poe_gravedigger",
                InvocationType="Event",
                Payload=json.dumps({"character": entry["character"]["name"]})
            )
            continue
        tmp = {
            "account": entry["account"]["name"],
            "character": entry["character"]["name"],
            "dead": entry["dead"]
        }
        entries.append(tmp)
    correlation_id = str(uuid.uuid4())
    return_event = {"CorrelationId": correlation_id, "characters": entries}
    client = boto3.client('stepfunctions')
    logger.info(f"Starting step function execution with {correlation_id}")
    try:
        state_machines = client.list_state_machines()["stateMachines"]
        state_machine = [s["stateMachineArn"] for s in state_machines if s["name"] == "poe_character_exporter"][0]
        response = client.start_execution(
            # stateMachineArn="arn:aws:states:eu-central-1:983498139013:stateMachine:poe_character_exporter",
            stateMachineArn=state_machine,
            name=f"{correlation_id}",
            input=json.dumps(return_event)
        )
        logger.info(f"Step function triggered successfully at {response['startDate']}")
    except client.exceptions.ExecutionLimitExceeded:
        logger.critical(f"Step function execution limit exceeded - we should not hit this")
    except client.exceptions.ExecutionAlreadyExists:
        logger.critical(f"Step function execution already exists - should never happen")
    return return_event
