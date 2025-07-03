"""
Adventure Quest: Dungeon Delver Game
You are an intrepid hero exploring an ever-changing dungeon in search of gold, equipment, and legendary artifacts. 
Each level of the dungeon presents random encounters with monsters or treasures. 
You can fight, flee, loot, or visit the dungeons secret shop between levels. 
Your ultimate goal is to clear Level-10 and claim the Dragon's Egg.

1-Styling & Animation

    Create a Styles class with ANSI escape codes for colors, bold, and clearing lines. 👍

    Use simple “spinner” or “typing” animations when generating encounters, attacking, or opening chests. 👍 

2-Maintain a game dictionary in memory with keys:

{
  "level": int,            # current dungeon level
  "hp": int,               # player health
  "max_hp": int,           # maximum health
  "gold": int,             # currency
  "inventory": [],         # list of item names
  "weapons": [],           # list of weapon names
  "artifacts": [],         # list of unique artifacts
  "cheat_mode": bool,      # unlocked by secret code file
}

👍

On exit, prompt to save progress to JSON (using json + os + sys). 👍

On start, allow loading from an existing save file. 👍


3- Random Encounters
    Each level triggers one of:

        Monster Fight (70%): random monster with name, HP, reward gold.

        Treasure Chest (20%): random gold amount or random item drop.

        Shopkeeper (10%): opportunity to buy potions/tools before proceeding.

4- Battle System

    When fighting:

    Display monster name and HP.

    Loop: Hero attack → Monster attack (with spinner).

    Damage is random within weapon's damage range.

    If hero HP drops to 0 → Game Over.

    If monster dies → award gold, maybe drop an item.

5- Inventory & Equipment

    Equip one weapon at a time from weapons list.

    Weapons have a name and damage range stored in parallel lists (no dicts!).

    Potions in inventory can heal a fixed amount when used.

6- Shop System

    Accessible between levels or via secret “shop” command.

    Items to purchase (with prices):

    Small Health Potion - restores 20HP

    Iron Sword - adds to weapons (damage 5-10)

    Magic Scroll - grants temporary attack buff

    Secret Map - reveals next level's danger (chance to avoid monsters)

    Deduct gold and add items/weapons to lists.

7- Level Progression
    Clearing a level increases level by 1.

    On odd levels, increase monster difficulty; on even levels, offer treasure rooms.


8- Cheat Mode
    If a file named invincibility.txt exists, automatically unlock a hidden command cheat allowing you to set any game parameter (HP, gold, level).

9- Commands and Help
    explore (or e) - descend to the next level and trigger encounter

    status (or s) - show current HP, level, gold, inventory, equipped weapon

    shop (or sh) - open the shop

    use ( or u) - use a potion or scroll from inventory

    equip (or eq) - equip a weapon from your arsenal

    save - force save game to JSON

    load - load from existing save file

    help (or h) - list all commands

    quit - exit (prompt to save)

10 - Victory & Defeat

    Victory: Reaching Level-11 (having cleared Level-10) and defeating the Dragon Lord grants the “Drago's Egg” artifact and ends the game.

    Defeat: Hero HP drops to 0 → show “Game Over” you have to make press play again.

11 - One line Logic (OLL)

    Must do this 👍
"""

import time, random as r, math, os, sys, json, pygame as pg, pygwidgets as pgw

class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    CLEAR_LINE = '\033[2K'

def spinner(duration, delay):

    chars = ['-', '\\', '|', '/']

    previous = time.time()

    while time.time() - previous <= duration:
        for char in chars:
            print(f'     {char}', " "*10, end = '\r')
            time.sleep(delay)   

def init_new_game():
    return {
        "level": 1,            
        "hp": 100,               
        "max_hp": 100,           
        "gold": 0,            
        "inventory": [],         
        "weapons": [
            ["God Ray", 100000, 99999999999]
        ],     
        "equipped": 0,      
        "artifacts": ["LaDoodle's Hat"], 
        "cheat_mode": os.path.exists('cheat')
    }

def json_save(game):
    file_name = input(f"\n{style.BLUE}{style.BOLD}Save filename >>>{style.RESET} ").strip() + ".json"
    try:
        with open(file_name, 'w')as f:
            json.dump(game, f)
        print(f"{style.GREEN}Game saved to {file_name}{style.RESET}")
    except Exception as e:
        print(f"{style.RED}Unable to write file with error: {e}{style.RESET}")


def json_load():
    file_name = input(f"{style.BLUE}{style.BOLD} Load file name >>>{style.RESET} ").strip() + ".json"

    try:
        with open(file_name, 'r') as f:
            game_state = json.load(f)

            required_keys = {
                "level": int,
                "hp": int,
                "max_hp": int,
                "gold": int,
                "inventory": list,
                "weapons": list,
                "equipped": int,
                "artifacts": list,
                "cheat_mode": bool
            }

            # check for general formatting in required_keys {...}
            for key, expected_type in required_keys.items():
                if key not in game_state:
                    print(f"{style.RED}Error loading file, Invalid format{style.RESET}")
                    return None
                if not isinstance(game_state[key], expected_type):
                    print(f"{style.RED}Error loading file, Invalid Format{style.RESET}")
                    return None

            # check for weapons format
            for weapon in game_state["weapons"]:
                if not (isinstance(weapon, list) and len(weapon) == 3 and
                        isinstance(weapon[0], str) and
                        isinstance(weapon[1], int) and
                        isinstance(weapon[2], int) and
                        weapon[1] > 0 and
                        weapon[2] > 0 and
                        weapon[2] > weapon[1]):
                    print(f"{style.RED}Error loading file, Invalid format{style.RESET}")
                    return None

            # check for artifacts format (all str)
            if not all(isinstance(a, str) for a in game_state["artifacts"]):

                print(f"{style.RED}Error loading file, Invalid format{style.RESET}")
                return None

            # print gamestate from json file
            print(f"\n{style.GREEN}Game loaded from {file_name}{style.RESET}")
            print(f"{style.CYAN}{style.BOLD}Current Game State:{style.RESET}")
            for key, value in game_state.items():
                print(f"  {key}: {value}")
            
            return game_state
    except Exception as e:
        print(f"{style.RED}Unable to read file with error: {e}{style.RESET}")

def check_game_over(game):
    if game["level"] == 11:
        print(f"\n{style.BOLD}{style.UNDERLINE}{style.GREEN}CONGRATS! {style.RESET}{style.GREEN}You just won the game and earned {style.BOLD}{style.MAGENTA}Drago's Egg")
        return "won"
    elif game["hp"] == 0: return "lose"


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    game = init_new_game()
    print(f"\n{style.MAGENTA}Welcome to DOODLE R.P.G.\n")
    i = input(f"{style.CYAN}{style.BOLD} Would you like to load a game from json file? ({style.RESET}{style.CYAN}Y{style.BOLD}/{style.RESET}{style.CYAN}N{style.BOLD}) >>> {style.RESET}").strip()

    game = json_load() if i == "Y" else init_new_game(); game = init_new_game() if game == None else game

    while True:
        select = input(f" {style.BOLD}{style.BLUE}>>>{style.RESET} ")
        """ >>> 
        explore (or e) - descend to the next level and trigger encounter

        status (or s) - show current HP, level, gold, inventory, equipped weapon

        shop (or sh) - open the shop

        use ( or u) - use a potion or scroll from inventory

        equip (or eq) - equip a weapon from your arsenal

        save - force save game to JSON

        load - load from existing save file

        help (or h) - list all commands

        quit - exit (prompt to save) :
        """

main()