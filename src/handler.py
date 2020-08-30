import logging
import os


from poe_api import get_ladder, get_character_items
from items import format_item


logger = logging.getLogger(__name__)
if os.environ.get("LOG_LEVEL"):
    logger.setLevel(os.environ["LOG_LEVEL"])
else:
    logger.setLevel("INFO")


def handler(event, context):
    ladder = get_ladder(event["league"])
    characters = []
    for entry in ladder["entries"]:
        account_name = entry["account"]["name"]
        character_name = entry["character"]["name"]
        character = {}
        items = get_character_items(
            account_name,
            character_name
        )
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
    return characters


if __name__ == "__main__":
    response = handler({"league": "Standard"}, {})
    print(response)
