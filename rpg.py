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


3- Random Encounters 👍
    Each level triggers one of:

        Monster Fight (79%): random monster with name, HP, reward gold. 

        Treasure Chest (20%): random gold amount or random item drop.

        Shopkeeper (Extra buffed with insane items) (1%): opportunity to buy potions/tools before proceeding.

4- Battle System - one feature left 👍

    When fighting:

    Display monster name and HP.

    Loop: Hero attack → Monster attack (with spinner).

    Damage is random within weapon's damage range.

    If hero HP drops to 0 → Game Over.

    If monster dies → award gold, maybe drop an item.

5- Inventory & Equipment 👍

    Equip one weapon at a time from weapons list.

    Weapons have a name and damage range stored in parallel lists (no dicts!).

    Potions in inventory can heal a fixed amount when used. 

6- Shop System 👍

    Accessible via “shop” command.

    Items to purchase (with prices):

    Small Health Potion - restores 20HP

    Iron Sword - adds to weapons (damage 5-10)

    Magic Scroll - grants temporary attack buff

    Secret Map - reveals next level's danger (chance to avoid monsters)

    Deduct gold and add items/weapons to lists.

7- Level Progression 
    Buy a level up from shop. 👍


8- Cheat Mode 👍
    If a file named invincibility.txt exists, automatically unlock a hidden command cheat allowing you to set any game parameter (HP, gold, level).

9- Commands and Help 👍
    explore (or e) - descend to the next level and trigger encounter

    status (or s) - show current HP, level, gold, inventory, equipped weapon

    shop (or sh) - open the shop

    use ( or u) - use a potion or scroll from inventory

    equip (or eq) - equip a weapon from your arsenal

    save - force save game to JSON

    load - load from existing save file

    help (or h) - list all commands

    quit - exit (prompt to save)

10 - Victory & Defeat 👍

    Victory: Reaching Level-11 (having cleared Level-10) and defeating the Dragon Lord grants the “Drago's Egg” artifact and ends the game.

    Defeat: Hero HP drops to 0 → show “Game Over” you have to make press play again.

11 - One line Logic (OLL)

    Must do this 👍
"""

import time, random as r, math, os, sys, json, pygame as pg, pygwidgets as pgw

# Styles class for ANSI escape codes for terminal colors and formatting
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

# Spinner animation for loading effects
def spinner(duration, delay):
    chars = ['-', '\\', '|', '/']
    previous = time.time()
    while time.time() - previous <= duration:
        for char in chars:
            print(f'     {char}', " "*10, end = '\r')
            time.sleep(delay)  
    print(style.CLEAR_LINE) 

# Initialize a new game state dictionary
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

# Save game state to JSON file
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

# Typewriter effect for text output
def typewriter(text, color=style.RESET):
    for c in text:
        print(f"{color}{c}{style.RESET}", end='', flush=True)
        time.sleep(0.02)
    print()
    time.sleep(0.5)

# Load game state from JSON file
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

            # Validate required keys and types
            for key, expected_type in required_keys.items():
                if key not in game_state:
                    print(f"{style.RED} > Error loading file, Invalid format{style.RESET}")
                    return None
                if not isinstance(game_state[key], expected_type):
                    print(f"{style.RED} > Error loading file, Invalid Format{style.RESET}")
                    return None

            # Validate weapons format
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

            # Validate artifacts format
            if not all(isinstance(a, str) for a in game_state["artifacts"]):
                print(f"{style.RED} > Error loading file, Invalid format{style.RESET}")
                return None

            # Print loaded game state
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

# Check for game over or victory conditions
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

# To use an item
def use_item(game):
    if game["inventory"]:
        for i, items in enumerate(game["inventory"], start=1):
            print(f"{i + 1}. {items}")
            time.sleep(0.1)

        try:
            item = game["inventory"][int(input(f"{style.BOLD}Which item would you like to use (#){style.RESET} >>> ")) - 1]
        except (IndexError, ValueError) as e:
            typewriter("Invalid item selection.", style.RED)
            return game

        # Mystic Cloak: buffs HP and all weapons, then removes itself
        if item[0] == 'mystic cloak':
            game["hp"] += 20
            game["max_hp"] += 20
            for i in range(len(game['weapons'])):
                game['weapons'][i][1] += 20
                game['weapons'][i][2] += 20

            game["inventory"].remove(item)
            typewriter(f"You used a {item[0]} and gained 20 hp to your max hp and buffed all your weapons!", style.GREEN)
            time.sleep(0.5)
            typewriter("🤔 Your cloak mysteriously dissipated and got absorbed into your items...", style.YELLOW)
            print()

        # Large Health Potion: heals 50 HP
        elif item[0] == 'Large Health Potion':
            game["hp"] += 50
            game["inventory"].remove(item)
            typewriter(f"You used a {item[0]} and gained 50 hp!", style.GREEN)

        # Small Health Potion: heals 20 HP
        elif item[0] == 'Small Health Potion':
            game["hp"] += 20
            game["inventory"].remove(item)
            typewriter(f"You used a {item[0]} and gained 20 hp!", style.GREEN)

        # Elixir of Fortitude: heals 100 HP
        elif item[0] == 'Elixir of Fortitude':
            game["hp"] += 100
            game["inventory"].remove(item)
            typewriter(f"You used an {item[0]} and gained 100 hp!", style.GREEN)

        # Phoenix Feather: adds a spell weapon if not already known
        elif item[0] == 'Phoenix Feather':
            spell = ["Phoenix's Flare Blitz", 100, 150]
            if not spell in game["weapons"]:
                game["weapons"].append(spell)
                typewriter(f"You used a {item[0]} and learned a new spell: {spell[0]}!", style.GREEN)
                time.sleep(0.5)
                typewriter("Equip spell through 'Equip' command", style.YELLOW)
            else:
                typewriter(f"You already know the spell: {spell[0]}", style.YELLOW)

            game["inventory"].remove(item)
            typewriter('The feather has been used...', style.YELLOW)
            
        # Magic Scroll: grants a random spell weapon if not already known
        elif item[0] == 'Magic Scroll':
            spells = [["Arcane Blast", 80, 120], ["Electrify", 60, 100], ["Frostbite", 70, 110], ["Fireball", 90, 130], ["Meteor Shower", 100, 150], ["Tornado Blast", 85, 125]]

            spell = r.choice(spells)
            if spell not in game["weapons"]:
                game["weapons"].append(spell)
                typewriter(f"You used a {item[0]} and learned a new spell: {spell[0]}!", style.GREEN)
                time.sleep(0.5)
                typewriter("Equip spell through 'Equip' command", style.YELLOW)
            else:
                typewriter(f"You already know the spell: {spell[0]}", style.YELLOW)
                

            game["inventory"].remove(item)
            typewriter('The scroll has been used...', style.YELLOW)

        # Default: item cannot be used in battle
        else:
            typewriter(f"You can't use {item[0]} right now!", style.RED)
        
        return game
    else:
        typewriter("You have no items to use!", style.RED)

# Handle random encounters (monster, treasure, shopkeeper)
def random_encounter(game):
    spinner(1, 0.1)

    # Monster format: [name, hp, damage, reward, chance]
    monsters = [
        ["VENOM DRAKE", 110, 35, 70, 180],
        ["NIGHT STALKER", 130, 45, 90, 340],
        ["CRYPT LICH", 170, 60, 120, 520],
        ["STONE GOLEM", 220, 80, 160, 700],
        ["VOID SHADE", 260, 100, 200, 850],
        ["GORM", 320, 130, 300, 950],
        ["BLADE PHANTOM", 400, 180, 500, 1000],
    ]

    # Adjust monster chances based on level
    level = game["level"]
    bias = min(max(level - 1, 0), 9)  # 0 to 9
    half = len(monsters)//2
    bias_shift = bias*2
    new_monsters = []
    
    for i, (name, hp, damage, reward, chance) in enumerate(monsters):
        shift = bias_shift if i >= half else - bias_shift
        new_chance = max(0,min(1000, chance + shift))  
        new_monsters.append([name, hp, damage, reward, new_chance])
    
    monsters = new_monsters

    i = r.randint(0, 100)
    if i <= 79:
        # Monster fight
        i = r.randint(0, 1000)
        for monster in monsters:
            if i <= monster[4]:
                typewriter(f"{monster[0]} appeared!", style.RED)
                player_weapon = game["weapons"][game["equipped"]]
                typewriter(f"{monster[0]} has {monster[1]} HP!", style.YELLOW)
                typewriter(f"You ready your {player_weapon[0]}!", style.YELLOW)

                time.sleep(1)
                monster_hp = monster[1]
                monster_name = monster[0]
                monster_damage = monster[2]
                reward_gold = monster[3]

                # Battle loop
                while monster_hp > 0 and game["hp"] > 0:
                    qu = input(f"\n{style.BOLD}What would you like to do (run/attack/counter/useItem) >>> {style.RESET}")
                    print()
                    dmg = r.randint(player_weapon[1], player_weapon[2])
                    mdmg = r.randint(int(monster_damage*0.7), monster_damage)
                    os.system('cls' if os.name == 'nt' else 'clear')

                    if qu == "run":
                        if r.randint(1, 100) <= 100:
                            typewriter("You successfully ran away!", style.GREEN)
                            return game
                        else:
                            typewriter("You failed to escape!", style.RED)
                            if monster_hp > 0:
                                his_attack = f"{monster_name} strikes you for {mdmg} damage!"
                                game["hp"] -= mdmg
                                typewriter(his_attack, style.RED)
                    elif qu == "attack":
                        my_attack = f"You attack {monster_name} for {dmg} damage!"
                        monster_hp -= dmg
                        typewriter(my_attack, style.GREEN)
                        if monster_hp > 0:
                            his_attack = f"{monster_name} strikes you for {mdmg} damage!"
                            game["hp"] -= mdmg
                            typewriter(his_attack, style.RED)
                    elif qu == "counter":
                        if r.randint(1, 100) <= 50:
                            his_attack = f"{monster_name} tried to strike you, but failed!"
                            dmg = r.randint(max(dmg, mdmg)-min(dmg, mdmg), (max(dmg, mdmg)-min(dmg, mdmg))*2)
                            my_attack = f"You counter {monster_name}'s attack for {dmg}!"
                            monster_hp -= dmg
                            typewriter(his_attack, style.GREEN)
                            typewriter(my_attack, style.GREEN)
                        else:
                            typewriter("Your counter failed!", style.RED)
                            if monster_hp > 0:
                                his_attack = f"{monster_name} strikes you for {mdmg} damage!"
                                game["hp"] -= mdmg
                                typewriter(his_attack, style.RED)
                    elif qu == "useItem":
                        
                        game = use_item(game)

                        spinner(2, 0.1)

                        i = r.randint(1, 2)
                        if i == 1 and monster_hp > 0:
                            typewriter("The monster is preparing to attack!", style.YELLOW)

                            spinner(2, 0.1)

                            his_attack = f"{monster_name} strikes you for {mdmg} damage!"
                            game["hp"] -= mdmg
                            typewriter(his_attack, style.RED)
                            
                        else:
                            typewriter("You safely use your item.", style.GREEN)

                    hp_line = f"Your HP: {max(game['hp'],0)} | {monster_name} HP: {max(monster_hp,0)}"
                    typewriter(hp_line, style.YELLOW)

                    time.sleep(2)

                if monster_hp <= 0:
                    typewriter(f"{monster_name} is defeated!", style.MAGENTA)
                    typewriter(f"You gain {reward_gold} gold!", style.YELLOW)
                    game["gold"] += reward_gold

                time.sleep(3)
                return game           

    elif i <= 99:
        # Treasure Chest Encounter
        typewriter("You found a mysterious treasure chest!", style.YELLOW)
        spinner(1, 0.1)
        reward_type = r.choices(["gold", "item"], weights=[70, 30])[0]
        if reward_type == "gold":
            gold_found = r.randint(30, 120) + game["level"] * 5
            typewriter(f"You open the chest and find {gold_found} gold!", style.GREEN)
            game["gold"] += gold_found
        else:
            items = [
                "Small Health Potion",
                "Large Health Potion",
                "Magic Scroll",
                "Secret Map",
                "Iron Sword",
                "Steel Axe",
                "Enchanted Dagger",
                "Phoenix Feather",
                "Elixir of Fortitude",
                "Mystic Cloak",
                "(Totally) Mjölnir",
                "Shadow Amulet"
            ]

            # Weapons and their damage ranges
            weapon_stats = [
                ["Iron Sword", 5, 10],
                ["Steel Axe", 8, 16],
                ["Enchanted Dagger", 4, 14],
                ["(Totally) Mjölnir", 100, 220]
            ]

            item = r.choice(items)

            # Check if item is a weapon
            if item in [w[0] for w in weapon_stats]:
                # Only add if not already owned
                if not item in game["weapons"]:
                    game["weapons"].append(item)
                    typewriter(f"You found a {item}! (Damage {item[1]}-{item[2]})", style.CYAN)
                else:
                    typewriter(f"You found a {item}, but you already have one. You sell it for 50 gold.", style.YELLOW)
                    game["gold"] += 50
            
            # Check if item is an artifact
            elif item[0] == 'Shadow Amulet':
                if not item in game['Artifacts']:
                    game['Artifacts'].append(item)
                    typewriter(f"You found a {item}!", style.CYAN)
                else:
                    typewriter(f"You found a {item}, but you already have one. You sell it for 50 gold.", style.YELLOW)
                    game["gold"] += 50
            
            # Otherwise, add to inventory
            else:
                game["inventory"].append(item)
                typewriter(f"You found a {item}!", style.CYAN)
        
        return game
    
    elif i <= 100:
        # Shopkeeper encounter
        typewriter("You have encountered a Buffed Shopkeeper, buy an op item with your gold!", style.YELLOW)
        return game

# Equip a weapon from the arsenal
def equip(game):
    print(f"\n{style.BLUE}Which weapon would you like to equip?{style.RESET}")

    for weapon in game["weapons"]:
        print(f"\n    {game['weapons'].index(weapon) + 1}: {weapon[0]} {weapon[1]} - {weapon[2]} dmg")
        time.sleep(0.1)
    
    try:
        game["equipped"] = int(input("\nChoose a weapon number >>> "))-1
    except Exception as e:
        print(f"\n{style.BOLD}{style.RED}ERROR: {style.RESET}{style.RED}{e}{style.RESET}")

    typewriter(f"{style.YELLOW}You have equipped the {style.UNDERLINE}{style.BOLD}{game['weapons'][game['equipped']]}")

# Print current game status
def status(game):
    print(f"{style.CYAN}{style.BOLD}Current Game State:{style.RESET}")
    for key, value in game.items():
        print(f"  {key}: {value}")
        time.sleep(0.1)
    time.sleep(5)

# Handle quitting the game and saving
def quit_game(game):
    s = input(f'\n{style.CYAN}You are going to quit the game, would you like to save in a file? Y/N >>> {style.RESET}').upper().strip()
    if s[0] == 'Y':
        json_save(game)
    
    print(f"{style.MAGENTA}Thank you for playing DOODLE R.P.G.!{style.RESET}")

    time.sleep(7)
    os.system('cls' if os.name == 'nt' else 'clear')
    return

# The shop to buy items and level ups
def shop(game):
    items = [
        "Small Health Potion",
        "Large Health Potion",
        "Magic Scroll",
        "Secret Map",
        "Iron Sword",
        "Steel Axe",
        "Enchanted Dagger",
        "Phoenix Feather",
        "Elixir of Fortitude",
        "Mystic Cloak",
        "(Totally) Mjölnir",
        "Shadow Amulet",
        "Level Up"
    ]

    # Weapons and their damage ranges
    weapon_stats = [
        ["Iron Sword", 5, 10],
        ["Steel Axe", 8, 16],
        ["Enchanted Dagger", 4, 14],
        ["(Totally) Mjölnir", 100, 220]
    ]

    item_costs = {
        "Small Health Potion": 30,
        "Large Health Potion": 90,
        "Magic Scroll": 120,
        "Secret Map": 150,
        "Iron Sword": 100,
        "Steel Axe": 200,
        "Enchanted Dagger": 150,
        "Phoenix Feather": 300,
        "Elixir of Fortitude": 200,
        "Mystic Cloak": 250,
         "(Totally) Mjölnir": 500,
        "Shadow Amulet": 350,
        "Level Up": 300 * game["level"]
    }

    typewriter(f'Welcome adventurer to my shop! I have an assortment of items to buy. Pick your choice:')

    while True:
        for item, cost in item_costs.items():
            print(f' {item_costs.index(item) - 1}. {item}: {cost} gold')
            time.sleep(0.1)
        print()
        try:
            choice = str(input(f"{style.CYAN}Enter the item you wish to buy (or 'exit' to leave) >>> {style.RESET}")).strip()
        except Exception as e:
            print(f"\n{style.BOLD}{style.RED}ERROR: {style.RESET}{style.RED}{e}{style.RESET}")
            continue

        if choice == "exit":
            typewriter(f"Thank you for visiting the shop!", style.BLUE)
            break
        elif choice == 'Level Up':
            if game['gold']>= item_costs["Level Up"]:
                game["gold"] -= item_costs[choice]
                game["level"] += 1
                typewriter(f"You have leveled up to level {game['level']}!", style.GREEN)
        elif choice in [w[0] for w in weapon_stats]:
            if game['gold'] >= item_costs[choice]:
                game["gold"] -= item_costs[choice]
                game["weapons"].append(choice)
                typewriter(f"You have purchased {choice}!", style.GREEN)
        elif choice in item_costs:
            if game["gold"] >= item_costs[choice]:
                game["gold"] -= item_costs[choice]
                game["inventory"].append(choice)
                typewriter(f"You have purchased {choice}!", style.GREEN)
            else:
                typewriter(f"You do not have enough gold to buy {choice}.", style.RED)
        else:
            typewriter(f"Invalid item choice.", style.RED)

        os.system('cls' if os.name == 'nt' else 'clear')


    time.sleep(2)
    print()

    return game

# Main game loop
def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    game = init_new_game()
    print(f"\n{style.MAGENTA}Welcome to DOODLE R.P.G.\n")
    i = input(f"{style.CYAN}{style.BOLD} Would you like to load a game from json file? ({style.RESET}{style.CYAN}Y{style.BOLD}/{style.RESET}{style.CYAN}N{style.BOLD}) >>> {style.RESET}").strip().upper()

    game = json_load() if i == "Y" else init_new_game()

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')

        s = input(f" {style.BOLD}{style.BLUE}>>>{style.RESET} ")

        if s in ["help", "h"]:
            print(f"""  
    explore (or e) - descend to the next level and trigger encounter
    status (or s) - show current HP, level, gold, inventory, equipped weapon
    shop (or sh) - open the shop
    use ( or u) - use a potion or scroll from inventory
    equip (or eq) - equip a weapon from your arsenal
    save - force save game to JSON
    load - load from existing save file
    help (or h) - list all commands
    quit (or q) to prompt save and exit
      {style.RESET}""")
            time.sleep(5)
        elif s in ["quit", "q"]:
            quit_game(game)
            return
        elif s in ["die"] and game["cheat_mode"]:
            print(f"{style.RED} > You have chosen to commit suicide. Game over!{style.RESET}")
            game["hp"] = 0
        elif s in ["win"] and game["cheat_mode"]:
            print(f"\n {style.GREEN}> Win{style.RESET}")
            game["level"] = 11
        elif s in ["save"]:
            json_save(game)
        elif s in ["load"]:
            game = json_load()
        elif s in ["explore", "e"]:
            game = random_encounter(game)
        elif s in ["status", "s"]:
            status(game)
        elif s in ["shop", "sh"]:
            game = shop(game)
        elif s in ["use", "u"]:
            game = use_item(game)
        elif s in ["equip", "eq"]:
            game = equip(game)
        else:
            print(f"{style.RED} > Invalid command, type help (or h) to list possible commands{style.RESET}")

        g = False if check_game_over(game) == "none" else True
        
        if g:
            time.sleep(7)
            return os.system('cls' if os.name == 'nt' else 'clear')
        
        time.sleep(3)

# Start the game
if __name__ == "__main__":
    main()
