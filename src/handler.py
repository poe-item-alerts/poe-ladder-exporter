import logging
import os

from time import perf_counter

from poe_api import get_ladder, get_character_items
from items import format_item


logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
if os.environ.get("LOG_LEVEL"):
    logger.setLevel(os.environ["LOG_LEVEL"])
else:
    logger.setLevel("DEBUG")


def handler(event, context):
    ladder = get_ladder(event["league"])
    characters = []
    for entry in ladder["entries"]:
        c_start = perf_counter()
        account_name = entry["account"]["name"]
        character_name = entry["character"]["name"]
        character = {}
        i_start = perf_counter()
        items = get_character_items(
            account_name,
            character_name
        )
        i_stop = perf_counter()
        logger.debug(f"Items for {character_name} processed in {i_stop - i_start}s")
        if not items:
            logger.info(f"No items found for {character_name} skipping...")
            continue
        character["account"] = account_name
        character["class"] = entry["character"]["class"]
        character["items"] = [format_item(item) for item in items["items"]]
        character["league"] = event["league"]
        character["level"] = entry["character"]["level"]
        character["name"] = character_name
        characters.append(character)
        c_stop = perf_counter()
        logger.debug(f"Character {character_name} processed in {c_stop - c_start}s")
    return characters


if __name__ == "__main__":
    t1_start = perf_counter()
    response = handler({"league": "Standard"}, {})
    t1_stop = perf_counter()
    logger.debug(f"Total characters successfully processed: {len(response)}")
    logger.debug(f"Total characters not successfully processed: {44 - len(response)}")
    logger.debug(f"Took: {t1_stop - t1_start}s")
