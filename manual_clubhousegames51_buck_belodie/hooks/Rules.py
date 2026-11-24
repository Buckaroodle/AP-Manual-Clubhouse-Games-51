from typing import Optional
from worlds.AutoWorld import World
from ..Helpers import clamp, get_items_with_value
from BaseClasses import MultiWorld, CollectionState

import re

# Sometimes you have a requirement that is just too messy or repetitive to write out with boolean logic.
# Define a function here, and you can use it in a requires string with {function_name()}.
def overfishedAnywhere(world: World, state: CollectionState, player: int):
    """Has the player collected all fish from any fishing log?"""
    for cat, items in world.item_name_groups:
        if cat.endswith("Fishing Log") and state.has_all(items, player):
            return True
    return False

# You can also pass an argument to your function, like {function_name(15)}
# Note that all arguments are strings, so you'll need to convert them to ints if you want to do math.
def anyClassLevel(state: CollectionState, player: int, level: str):
    """Has the player reached the given level in any class?"""
    for item in ["Figher Level", "Black Belt Level", "Thief Level", "Red Mage Level", "White Mage Level", "Black Mage Level"]:
        if state.count(item, player) >= int(level):
            return True
    return False

# You can also return a string from your function, and it will be evaluated as a requires string.
def requiresMelee():
    """Returns a requires string that checks if the player has unlocked the tank."""
    return "|Figher Level:15| or |Black Belt Level:15| or |Thief Level:15|"

def goalAmount(world: World, state: CollectionState, player: int):
    return f"|@Games:{world.options.games_required_for_victory.value}|"

def boardGoalAmount(world: World, state: CollectionState, player: int):
    return f"|@Board Games:{world.options.board_games_required_for_victory.value}|"

def cardGoalAmount(world: World, state: CollectionState, player: int):
    return f"|@Card Games:{world.options.card_games_required_for_victory.value}|"

def sportsGoalAmount(world: World, state: CollectionState, player: int):
    return f"|@Sports Games:{world.options.sports_games_required_for_victory.value}|"

def varietyAndSinglePlayerGoalAmount(world: World, state: CollectionState, player: int):
    return f"|@Variety and Single-Player Games:{world.options.variety_and_single_player_games_required_for_victory.value}|"

def woodenGoalAmount(world: World, state: CollectionState, player: int):
    return f"|@Wooden Games:{world.options.wooden_games_required_for_victory.value}|"

def paperPlasticGoalAmount(world: World, state: CollectionState, player: int):
    return f"|@Paper and Plastic Board Games:{world.options.paper_plastic_board_games_required_for_victory.value}|"

def japaneseGoalAmount(world: World, state: CollectionState, player: int):
    return f"|@Japanese Games:{world.options.japanese_games_required_for_victory.value}|"

def nonJapaneseCardGoalAmount(world: World, state: CollectionState, player: int):
    return f"|@Non-Japanese Card Games:{world.options.non_japanese_card_games_required_for_victory.value}|"

def sophisticatedGoalAmount(world: World, state: CollectionState, player: int):
    return f"|@Sophisticated Games:{world.options.sophisticated_games_required_for_victory.value}|"

def toyGoalAmount(world: World, state: CollectionState, player: int):
    return f"|@Toy Games:{world.options.toy_games_required_for_victory.value}|"

def varietyGoalAmount(world: World, state: CollectionState, player: int):
    return f"|@Variety Games:{world.options.variety_games_required_for_victory.value}|"

def singlePlayerGoalAmount(world: World, state: CollectionState, player: int):
    return f"|@Single-Player Games:{world.options.single_player_games_required_for_victory.value}|"

def itemGoalAmount(world: World, state: CollectionState, player: int):
    return f"|Mastery Trophy:{world.options.trophies_required_for_victory.value}|"

def victoriesRequired(world: World, state: CollectionState, player: int):
    return f"|Victory Condition Point:{world.options.victory_condition_amount.value}|"

def victoriesPresent(world: World, state: CollectionState, player: int):
    victory_condition_count = 0
    if world.options.victory_condition_0:
        victory_condition_count += 1
    if world.options.victory_condition_1:
        victory_condition_count += 1
    if world.options.victory_condition_2:
        victory_condition_count += 1
    if world.options.victory_condition_3:
        victory_condition_count += 1
    return f"{victory_condition_count}"

def categoryCopiesPresent(world: World, state: CollectionState, player: int):
    return f"{world.options.category_gate_count.value}"