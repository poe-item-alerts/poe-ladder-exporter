import collections


def format_item(item):
    """
    Takes in the item JSON format and adds some clarifying fields
    
    * rarity
    * max number of links

    And removes some redundant data about the character wearing it since we're
    attaching the items to the character already.

    args:
        item(dict): JSON representation of the item
            https://app.swaggerhub.com/apis-docs/Chuanhsing/poe/1.0.0#/Item
    returns:
        dict: The formatted item with new fields added to the root level
    """
    if item.get("sockets"):
        item["links"] = get_item_max_links(item["sockets"])
    else:
        item["links"] = 0
    item["rarity"] = get_item_rarity(item["frameType"])
    return item


def get_item_max_links(sockets):
    """
    Takes the groups of the sockets and returns the biggest one to
    identify the maximum links an item has.

    args:
        sockets(dict): sockets like in the item definition
            https://app.swaggerhub.com/apis-docs/Chuanhsing/poe/1.0.0#/Item
    returns:
        int: maximum number of links
    """
    groups = [s["group"] for s in sockets]
    count = collections.Counter(groups)
    return max(count.values())


def get_item_rarity(frame_type):
    """
    Gets the frame type used for the frontend to distinguish between
    rarities and will map the number index to the string repesentation.

    args:
        frame_type(int): number between 0-4 that identifies the frame
            type to be used by the frontend
    returns:
        str: String representation of the item rarity based on frame
            type.
    """
    if frame_type == 0:
        return "normal"
    elif frame_type == 1:
        return "magic"
    elif frame_type == 2:
        return "rare"
    elif frame_type == 3:
        return "unique"
    elif frame_type == 4:
        return "gem"


