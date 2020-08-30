import logging
import os


from poe_api import get_ladder, get_character_items


def handler(event, context):
    ladder = get_ladder(event["league"])
    characters = []
    for entry in ladder:
        account_name = entry["account"]["name"]
        character_name = entry["character"]["name"]
        character = {}
        items = get_character_items(
            account_name,
            character_name
        )
        character["account"] = account_name
        character["class"] = entry["character"]["class"]
        character["items"] = [format_item(item) for item in items]
        character["league"] = entry["character"]["league"]
        character["level"] = entry["character"]["level"]
        character["name"] = character_name
        characters.append(character)
    return characters


if __name__ == "__main__":
    response = handler({"league": "Standard"}, {})
    print(response)
