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

On exit, prompt to save progress to JSON (using json + os + sys). 👍 (make overwrite feature later maybe)

On start, allow loading from an existing save file. 👍


3- Random Encounters
    Each level triggers one of:

        Monster Fight (79%): random monster with name, HP, reward gold.

        Treasure Chest (20%): random gold amount or random item drop.

        Shopkeeper (Extra buffed with insane items) (1%): opportunity to buy potions/tools before proceeding.

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
from pathlib import Path

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

    print(style.CLEAR_LINE) 

def init_new_game():
    return {
        "level": 1,            
        "hp": 100,               
        "max_hp": 100,           
        "gold": 0,            
        "inventory": [],         
        "weapons": [
            ["Fists", 10, 20]
        ],     
        "equipped": 0,      
        "artifacts": ["LaDoodle's Hat"], 
        "cheat_mode": os.path.exists('cheat')
    }

def json_save(game):

    file_name = input(f"{style.BLUE}{style.BOLD}Save filename >>>{style.RESET} ").strip()
    file_name = file_name if file_name.endswith(".json") else file_name+".json"

    if os.path.exists(file_name) or file_name == '':
        print(f' {style.RED} > Invalid filename (either it already exists or blank) try again')
        json_save(game)
        return
    try:
        with open(file_name, 'w')as f:
            json.dump(game, f)
        print(f"\n{style.GREEN}Game saved to {file_name}{style.RESET}")
    except Exception as e:
        print(f"{style.RED} > Unable to write file with error: {e}{style.RESET}")

def typewriter(text, color=style.RESET):
    for c in text:
        print(f"{color}{c}{style.RESET}", end='', flush=True)
        time.sleep(0.02)
    print()
    time.sleep(0.5)

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
                    print(f"{style.RED} > Error loading file, Invalid format{style.RESET}")
                    return None
                if not isinstance(game_state[key], expected_type):
                    print(f"{style.RED} > Error loading file, Invalid Format{style.RESET}")
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
                    print(f"{style.RED} > Error loading file, Invalid format{style.RESET}")
                    return None

            # check for artifacts format (all str)
            if not all(isinstance(a, str) for a in game_state["artifacts"]):

                print(f"{style.RED} > Error loading file, Invalid format{style.RESET}")
                return None

            # print gamestate from json file
            print(f"\n{style.GREEN}Game loaded from {file_name}{style.RESET}")
            print(f"{style.CYAN}{style.BOLD}Current Game State:{style.RESET}")
            for key, value in game_state.items():
                print(f"  {key}: {value}")
                time.sleep(0.1)

            time.sleep(5)

            return game_state
    except Exception as e:
        print(f"{style.RED} > Unable to read file with error: {e}{style.RESET}")
        time.sleep(2)

def check_game_over(game):
    if game["hp"] <= 0:
        print(f"\n{style.BOLD}{style.UNDERLINE}{style.RED}GAME OVER!{style.RESET}{style.RED} You have been defeated.{style.RESET}")
        return "lost"
    elif game["level"] == 11:
        print(f"\n{style.BOLD}{style.UNDERLINE}{style.GREEN}CONGRATS!{style.RESET} {style.GREEN}You just won the game and earned {style.BOLD}{style.MAGENTA}Drago's Egg{style.RESET}")
        game["artifacts"].append("Drago's Egg")

        return "won"
    else:
        return "none"
    
def random_encounter(game):
    spinner(1, 0.1)

    # Format: [name, hp, damage, reward, chance]
    monsters = [
        ["VENOM DRAKE", 110, 35, 70, 47],    # 47% - Easiest, lowest reward
        ["NIGHT STALKER", 130, 45, 90, 67],  # 20% - Tougher, better reward
        ["CRYPT LICH", 170, 60, 120, 79],    # 12% - Harder, higher reward
        ["STONE GOLEM", 220, 80, 160, 88],   # 9% - Very tough, big reward
        ["VOID SHADE", 260, 100, 200, 94],   # 6% - Deadly, huge reward
        ["GORM", 320, 130, 300, 99],         # 5% - Brutal, massive reward
        ["BLADE PHANTOM", 400, 180, 500, 100], # 1% - Insane, legendary reward
    ]

    i = r.randint(0, 100)
    if i <= 89:
        i = r.randint(0, 100)
        for monster in monsters:
            if i <= monster[4]:
                typewriter(f"{monster[0]} appeared!", style.RED)
                player_weapon = game["weapons"][game["equipped"]]
                typewriter(f"{monster[0]} has {monster[1]} HP!", style.YELLOW)
                typewriter(f"You ready your {player_weapon[0]}!", style.YELLOW)

                time.sleep(1)
                # Monster fight logic
                
                monster_hp = monster[1]
                monster_name = monster[0]
                monster_damage = monster[2]
                reward_gold = monster[3]

                while monster_hp > 0 and game["hp"] > 0:
                    qu = input("Press Enter to attack!")
                    dmg = r.randint(player_weapon[1], player_weapon[2])
                    mdmg = r.randint(int(monster_damage*0.7), monster_damage)

                    my_attack = f"You attack {monster_name} for {dmg} damage!"
                    monster_hp -= dmg

                    his_attack = f"{monster_name} strikes you for {mdmg} damage!"
                    game["hp"] -= mdmg

                    hp_line = f"Your HP: {max(game['hp'],0)} | {monster_name} HP: {max(monster_hp,0)}"
    
                    os.system('cls' if os.name == 'nt' else 'clear')
                    typewriter(my_attack, style.GREEN)
                    typewriter(his_attack, style.RED)
                    typewriter(hp_line, style.YELLOW)
                    time.sleep(2)

                if monster_hp <= 0:
                    typewriter(f"{monster_name} is defeated!", style.MAGENTA)
                    typewriter(f"You gain {reward_gold} gold!", style.YELLOW)
                    typewriter(f"Your HP: {max(game['hp'],0)} | {monster_name} HP: {max(monster_hp,0)}", style.YELLOW)
                    game["gold"] += reward_gold
                
                return game
                
    elif i <= 99:
        return print("chest")
    elif i <= 100:
        return print("buffed keeper")

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    game = init_new_game()
    print(f"\n{style.MAGENTA}Welcome to DOODLE R.P.G.\n")
    i = input(f"{style.CYAN}{style.BOLD} Would you like to load a game from json file? ({style.RESET}{style.CYAN}Y{style.BOLD}/{style.RESET}{style.CYAN}N{style.BOLD}) >>> {style.RESET}").strip().upper()

    game = json_load() if i == "Y" else init_new_game(); game = init_new_game() if game == None else game

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')

        s = input(f" {style.BOLD}{style.BLUE}>>>{style.RESET} ")

        if s in ["help", "h"]:
            print(f"""{style.BOLD}explore (or e) - descend to the next level and trigger encounter
            status (or s) - show current HP, level, gold, inventory, equipped weapon
            shop (or sh) - open the shop
            use ( or u) - use a potion or scroll from inventory
            equip (or eq) - equip a weapon from your arsenal
            save - force save game to JSON
            load - load from existing save file
            help (or h) - list all commands
            quit (or q) to prompt save and exit
            
            {style.RESET}""")
        elif s in ["quit", "q"]:
            s = input(f'\n{style.CYAN}You are going to quit the game, would you like to save in a file? Y/N >>> {style.RESET}').upper().strip()
            if s[0] == 'Y':json_save(game)
            
            print(f"{style.MAGENTA}Thank you for playing DOODLE R.P.G.!{style.RESET}")

            time.sleep(7)
            os.system('cls' if os.name == 'nt' else 'clear')

            return
        elif s in ["die"] and game["cheat_mode"]:
            print(f"{style.RED} > You have chosen to commit suicide. Game over!{style.RESET}")
            game["hp"] = 0
        elif s in ["win"] and game["cheat_mode"]:
            print(f"\n {style.GREEN}> Win{style.RESET}")
            game["level"] = 11
        elif s in ["save"]:
            json_save()
        elif s in ["load"]:
            json_load()
        elif s in ["explore", "e"]:
            game = random_encounter(game)
        elif s in ["status", "s"]:
            print(f"{style.CYAN}{style.BOLD}Current Game State:{style.RESET}")
            for key, value in game.items():
                print(f"  {key}: {value}")
                time.sleep(0.1)
            time.sleep(5)
        elif s in ["shop", "sh"]:
            pass
        elif s in ["use", "u"]:
            pass
        elif s in ["equip", "eq"]:
            pass
        else:
            print(f"{style.RED} > Invalid command, type help (or h) to list possible commands{style.RESET}")

        g = check_game_over(game); g = False if g == "none" else True
        
        if g:
            time.sleep(7)
            return os.system('cls' if os.name == 'nt' else 'clear')
        
        time.sleep(1)

main()