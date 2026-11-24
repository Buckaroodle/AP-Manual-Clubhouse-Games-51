# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from typing import Any
from worlds.AutoWorld import World
from BaseClasses import MultiWorld, CollectionState, Item

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem
from ..Locations import ManualLocation

# Raw JSON data from the Manual apworld, respectively:
#          data/game.json, data/items.json, data/locations.json, data/regions.json
#
from ..Data import game_table, item_table, location_table, region_table

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value, format_state_prog_items_key, ProgItemsCat, remove_specific_item

# calling logging.info("message") anywhere below in this file will output the message to both console and log file
import logging

########################################################################################
## Order of method calls when the world generates:
##    1. create_regions - Creates regions and locations
##    2. create_items - Creates the item pool
##    3. set_rules - Creates rules for accessing regions and locations
##    4. generate_basic - Runs any post item pool options, like place item/category
##    5. pre_fill - Creates the victory location
##
## The create_item method is used by plando and start_inventory settings to create an item from an item name.
## The fill_slot_data method will be used to send data to the Manual client for later use, like deathlink.
########################################################################################



# Use this function to change the valid filler items to be created to replace item links or starting items.
# Default value is the `filler_item_name` from game.json
def hook_get_filler_item_name(world: World, multiworld: MultiWorld, player: int) -> str | bool:
    return False

def before_generate_early(world: World, multiworld: MultiWorld, player: int) -> None:
    """
    This is the earliest hook called during generation, before anything else is done.
    Use it to check or modify incompatible options, or to set up variables for later use.
    """
    # If the "victory_condition_amount" option is larger than the number of enabled victory conditions, set it to the amount of enabled victory conditions.
    victory_condition_count = 0
    if world.options.victory_condition_0.value == 1:
        victory_condition_count += 1
    if world.options.victory_condition_1.value == 1:
        victory_condition_count += 1
    if world.options.victory_condition_2.value == 1:
        victory_condition_count += 1
    if world.options.victory_condition_3.value == 1:
        victory_condition_count += 1
    if victory_condition_count == 0:
        world.options.victory_condition_0.value = 1
    if world.options.victory_condition_amount.value > victory_condition_count:
        world.options.victory_condition_amount.value = victory_condition_count

    # Use this hook to remove items from the item pool
    world._itemNamesToStartWith: list[str] = [] # List of item names

# Called before regions and locations are created. Not clear why you'd want this, but it's here. Victory location is included, but Victory event is not placed yet.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after regions and locations are created, in case you want to see or modify that information. Victory location is included.
def after_create_regions(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to remove locations from the world
    locationNamesToRemove: list[str] = [] # List of location names

    # Add your code here to calculate which locations to remove

    for region in multiworld.regions:
        if region.player == player:
            for location in list(region.locations):
                if location.name in locationNamesToRemove:
                    region.locations.remove(location)

# This hook allows you to access the item names & counts before the items are created. Use this to increase/decrease the amount of a specific item in the pool
# Valid item_config key/values:
# {"Item Name": 5} <- This will create qty 5 items using all the default settings
# {"Item Name": {"useful": 7}} <- This will create qty 7 items and force them to be classified as useful
# {"Item Name": {"progression": 2, "useful": 1}} <- This will create 3 items, with 2 classified as progression and 1 as useful
# {"Item Name": {0b0110: 5}} <- If you know the special flag for the item classes, you can also define non-standard options. This setup
#       will create 5 items that are the "useful trap" class
# {"Item Name": {ItemClassification.useful: 5}} <- You can also use the classification directly
def before_create_items_all(item_config: dict[str, int|dict], world: World, multiworld: MultiWorld, player: int) -> dict[str, int|dict]:
    victory_condition_count = 0
    if get_option_value(multiworld, player, "victory_condition_0"):
        victory_condition_count += 1
    if get_option_value(multiworld, player, "victory_condition_1"):
        victory_condition_count += 1
    if get_option_value(multiworld, player, "victory_condition_2"):
        victory_condition_count += 1
    if get_option_value(multiworld, player, "victory_condition_3"):
        victory_condition_count += 1
    
    category_copies_present = get_option_value(multiworld, player, "category_gate_count")

    if get_option_value(multiworld, player, "gate_categories") == 1 or get_option_value(multiworld, player, "gate_categories") == 3:
        item_config["Minor Category - Wooden Games"] = category_copies_present
        item_config["Minor Category - Japanese Games"] = category_copies_present
        item_config["Minor Category - Paper and Plastic Board Games"] = category_copies_present
        item_config["Minor Category - Non-Japanese Card Games"] = category_copies_present
        item_config["Minor Category - Sophisticated Games"] = category_copies_present
        item_config["Minor Category - Toy Games"] = category_copies_present
        item_config["Minor Category - Variety Games"] = category_copies_present
        item_config["Minor Category - Single-Player Games"] = category_copies_present
        item_config["Minor Category Gate Skip"] = 0
    else:
        item_config["Minor Category - Wooden Games"] = 0
        item_config["Minor Category - Japanese Games"] = 0
        item_config["Minor Category - Paper and Plastic Board Games"] = 0
        item_config["Minor Category - Non-Japanese Card Games"] = 0
        item_config["Minor Category - Sophisticated Games"] = 0
        item_config["Minor Category - Toy Games"] = 0
        item_config["Minor Category - Variety Games"] = 0
        item_config["Minor Category - Single-Player Games"] = 0
        item_config["Minor Category Gate Skip"] = 1
        world._itemNamesToStartWith.append("Minor Category Gate Skip")
    
    if get_option_value(multiworld, player, "gate_categories") == 2 or get_option_value(multiworld, player, "gate_categories") == 3:
        item_config["Major Category - Board Games"] = category_copies_present
        item_config["Major Category - Card Games"] = category_copies_present
        item_config["Major Category - Sports Games"] = category_copies_present
        item_config["Major Category - Variety and Single-Player Games"] = category_copies_present
        item_config["Major Category Gate Skip"] = 0
    else:
        item_config["Major Category - Board Games"] = 0
        item_config["Major Category - Card Games"] = 0
        item_config["Major Category - Sports Games"] = 0
        item_config["Major Category - Variety and Single-Player Games"] = 0
        item_config["Major Category Gate Skip"] = 1
        world._itemNamesToStartWith.append("Major Category Gate Skip")
    
    if victory_condition_count > 0:
        item_config["Victory Condition Point"] = victory_condition_count
    else:
        item_config["Victory Condition Point"] = 1

    major_categories = ["Major Category - Board Games", "Major Category - Card Games", "Major Category - Sports Games", "Major Category - Variety and Single-Player Games"]
    minor_categories = {"Major Category - Board Games": ["Minor Category - Wooden Games", "Minor Category - Japanese Games", "Minor Category - Paper and Plastic Board Games"], "Major Category - Card Games": ["Minor Category - Japanese Games", "Minor Category - Non-Japanese Card Games"], "Major Category - Sports Games": ["Minor Category - Sophisticated Games", "Minor Category - Toy Games"], "Major Category - Variety and Single-Player Games": ["Minor Category - Variety Games", "Minor Category - Single-Player Games"]}
    eligible_games = {"Minor Category - Wooden Games": ["Mancala", "Yacht Dice", "Nine Men's Morris", "Draughts (Checkers)", "Hare and Hounds", "Chinese Checkers", "Backgammon", "Chess"], "Japanese Board Games": ["Gomoku", "Shogi", "Mini Shogi", "Riichi Mahjong"], "Japanese Card Games": ["Hanafuda", "Takoyaki", "Pig's Tail"], "Minor Category - Paper and Plastic Board Games": ["Dots and Boxes", "Four-in-a-Row", "Hit and Blow", "Hex", "Dominoes", "Ludo", "Renegade"], "Minor Category - Non-Japanese Card Games": ["Last Card", "Blackjack", "Texas Hold'em", "President", "Sevens", "Speed", "Matching", "War"], "Minor Category - Sophisticated Games": ["Golf", "Billiards", "Bowling", "Darts", "Air Hockey"], "Minor Category - Toy Games": ["Toy Tennis", "Toy Football (Toy Soccer)", "Toy Curling", "Toy Boxing", "Toy Baseball"], "Minor Category - Variety Games": ["Carrom", "Slot Cars", "Fishing", "Battle Tanks", "Team Tanks", "Shooting Gallery", "6-Ball Puzzle"], "Minor Category - Single-Player Games": ["Sliding Puzzle", "Mahjong Solitaire", "Klondike Solitaire", "Spider Solitaire", "Piano"]}
    if not get_option_value(multiworld, player, "piano_checks"):
        eligible_games["Minor Category - Single-Player Games"].remove("Piano")

    major_category_one = major_categories[world.random.randint(0,len(major_categories)-1)]
    if get_option_value(multiworld, player, "gate_categories")  == 2 or get_option_value(multiworld, player, "gate_categories") == 3:
        item_config[major_category_one] = 1
        world._itemNamesToStartWith.append(major_category_one)
    minor_category_one = minor_categories[major_category_one][world.random.randint(0,len(minor_categories[major_category_one])-1)]
    if get_option_value(multiworld, player, "gate_categories") == 1 or get_option_value(multiworld, player, "gate_categories") == 3:
        item_config[minor_category_one] = 1
        world._itemNamesToStartWith.append(minor_category_one)

    game_one = ""
    if minor_category_one == "Minor Category - Japanese Games":
        if major_category_one == "Major Category - Board Games":
            minor_categories["Major Category - Card Games"].remove("Minor Category - Japanese Games")
            game_one = eligible_games["Japanese Board Games"][world.random.randint(0,len(eligible_games["Japanese Board Games"])-1)]
        else:
            minor_categories["Major Category - Board Games"].remove("Minor Category - Japanese Games")
            game_one = eligible_games["Japanese Card Games"][world.random.randint(0,len(eligible_games["Japanese Card Games"])-1)]
    else:
        game_one = eligible_games[minor_category_one][world.random.randint(0,len(eligible_games[minor_category_one])-1)]
    item_config[game_one] = 1
    world._itemNamesToStartWith.append(game_one)

    major_categories.remove(major_category_one)

    major_category_two = major_categories[world.random.randint(0,len(major_categories)-1)]
    if get_option_value(multiworld, player, "gate_categories") == 2 or get_option_value(multiworld, player, "gate_categories") == 3:
        item_config[major_category_two] = 1
        world._itemNamesToStartWith.append(major_category_two)
    minor_category_two = minor_categories[major_category_two][world.random.randint(0,len(minor_categories[major_category_two])-1)]
    if get_option_value(multiworld, player, "gate_categories") == 1 or get_option_value(multiworld, player, "gate_categories") == 3:
        item_config[minor_category_two] = 1
        world._itemNamesToStartWith.append(minor_category_two)

    game_two = ""
    if minor_category_two == "Minor Category - Japanese Games":
        if major_category_two == "Major Category - Board Games":
            game_two = eligible_games["Japanese Board Games"][world.random.randint(0,len(eligible_games["Japanese Board Games"])-1)]
        else:
            game_two = eligible_games["Japanese Card Games"][world.random.randint(0,len(eligible_games["Japanese Card Games"])-1)]
    else:
        game_two = eligible_games[minor_category_two][world.random.randint(0,len(eligible_games[minor_category_two])-1)]
    item_config[game_two] = 1
    world._itemNamesToStartWith.append(game_two)

    return item_config

# The item pool before place_item(_category) are processed, in case you want to see the raw item pool at that stage
def before_create_items_place_items(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    return item_pool

# The item pool before starting items are processed, in case you want to see the raw item pool at that stage
def before_create_items_starting(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    return item_pool

# The item pool after starting items are processed but before filler is added, in case you want to see the raw item pool at that stage
def before_create_items_filler(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:

    # Add your code here to calculate which items to remove.
    #
    # Because multiple copies of an item can exist, you need to add an item name
    # to the list multiple times if you want to remove multiple copies of it.

    for itemName in world._itemNamesToStartWith:
        item = next(i for i in item_pool if i.name == itemName)
        multiworld.push_precollected(item)
        remove_specific_item(item_pool, item)

    return item_pool

    # Some other useful hook options:

    ## Place an item at a specific location
    # location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == "Location Name")
    # item_to_place = next(i for i in item_pool if i.name == "Item Name")
    # location.place_locked_item(item_to_place)
    # remove_specific_item(item_pool, item_to_place)

# The complete item pool prior to being set for generation is provided here, in case you want to make changes to it
def after_create_items(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    return item_pool

# Called before rules for accessing regions and locations are created. Not clear why you'd want this, but it's here.
def before_set_rules(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after rules for accessing regions and locations are created, in case you want to see or modify that information.
def after_set_rules(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to modify the access rules for a given location

    def Example_Rule(state: CollectionState) -> bool:
        # Calculated rules take a CollectionState object and return a boolean
        # True if the player can access the location
        # CollectionState is defined in BaseClasses
        return True

    ## Common functions:
    # location = world.get_location(location_name, player)
    # location.access_rule = Example_Rule

    ## Combine rules:
    # old_rule = location.access_rule
    # location.access_rule = lambda state: old_rule(state) and Example_Rule(state)
    # OR
    # location.access_rule = lambda state: old_rule(state) or Example_Rule(state)

# The item name to create is provided before the item is created, in case you want to make changes to it
def before_create_item(item_name: str, world: World, multiworld: MultiWorld, player: int) -> str:
    return item_name

# The item that was created is provided after creation, in case you want to modify the item
def after_create_item(item: ManualItem, world: World, multiworld: MultiWorld, player: int) -> ManualItem:
    return item

# This method is run towards the end of pre-generation, before the place_item options have been handled and before AP generation occurs
def before_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This method is run every time an item is added to the state, can be used to modify the value of an item.
# IMPORTANT! Any changes made in this hook must be cancelled/undone in after_remove_item
def after_collect_item(world: World, state: CollectionState, Changed: bool, item: Item):
    # the following let you add to the Potato Item Value count
    # if item.name == "Cooked Potato":
    #     state.prog_items[item.player][format_state_prog_items_key(ProgItemsCat.VALUE, "Potato")] += 1
    pass

# This method is run every time an item is removed from the state, can be used to modify the value of an item.
# IMPORTANT! Any changes made in this hook must be first done in after_collect_item
def after_remove_item(world: World, state: CollectionState, Changed: bool, item: Item):
    # the following let you undo the addition to the Potato Item Value count
    # if item.name == "Cooked Potato":
    #     state.prog_items[item.player][format_state_prog_items_key(ProgItemsCat.VALUE, "Potato")] -= 1
    pass


# This is called before slot data is set and provides an empty dict ({}), in case you want to modify it before Manual does
def before_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called after slot data is set and provides the slot data at the time, in case you want to check and modify it after Manual is done with it
def after_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called right at the end, in case you want to write stuff to the spoiler log
def before_write_spoiler(world: World, multiworld: MultiWorld, spoiler_handle) -> None:
    pass

# This is called when you want to add information to the hint text
def before_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:

    ### Example way to use this hook:
    # if player not in hint_data:
    #     hint_data.update({player: {}})
    # for location in multiworld.get_locations(player):
    #     if not location.address:
    #         continue
    #
    #     use this section to calculate the hint string
    #
    #     hint_data[player][location.address] = hint_string

    pass

def after_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:
    pass

def hook_interpret_slot_data(world: World, player: int, slot_data: dict[str, Any]) -> dict[str, Any]:
    """
        Called when Universal Tracker wants to perform a fake generation
        Use this if you want to use or modify the slot_data for passed into re_gen_passthrough
    """
    return slot_data
