import json
import logging
import os

import boto3

from poe_gravedigger.gravedigger import dig_grave


logger = logging.getLogger(__name__)
if os.environ.get("LOG_LEVEL"):
    logger.setLevel(os.environ["LOG_LEVEL"])
else:
    logger.setLevel("INFO")


def handler(event, context):
    dig_grave(event["character"])
