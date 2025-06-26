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

On exit, prompt to save progress to JSON (using json + os + sys).
On start, allow loading from an existing save file.


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

    Defeat: Hero HP drops to 0 → show “Game Over,” offer to load a saved game.
"""

import time, random, math, os, sys, json, pygame as pg, pygwidgets as pgw

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
        

game = {
  "level": int,            
  "hp": int,               
  "max_hp": int,           
  "gold": int,            
  "inventory": [],         
  "weapons": [],           
  "artifacts": [], 
  "cheat_mode": bool
}, 