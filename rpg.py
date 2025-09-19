"""

Main/Base Game Complete!
Move onto additions.

"""

import sys, time, random as r, os, json, math, string, bossfights

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

bsvc = 0
nsvc = 0
mi = False
x = False
y = False

# Initialize a new game state dictionary
def init_new_game():
    return {
        "level": 1,            
        "hp": 100,               
        "max_hp": 100,           
        "gold": 0,            
        "inventory": [],         
        "weapons": [
            ["Fists", 5, 15]
        ],     
        "equipped": 0,      
        "artifacts": [], 
        "cheat_mode": False,
        "xp": 0,
        "skill_set": {
            "strength": 0,
            "agility": 0,
            "luck": 0,
            "accuracy": 0,
            "defence": 0
        },
        "used_items": [],
        "autosave": {
            "filename": str,
            "enabled": False,
        }
    } if not os.path.exists('cheat') else {
        "level": 1,
        "hp": 9999,
        "max_hp": 9999,
        "gold": 1000000000000000000,
        "inventory": [],
        "weapons": [
            ["Pen", 99999999999999999999999, 9999999999999999999999999999999999999]
        ],
        "equipped": 0,
        "artifacts": ["LaDoodle's Hat"],
        "cheat_mode": True,
        "xp": 0,
        "skill_set": {
            "strength": 100,
            "agility": 100,
            "luck": 100,
            "accuracy": 100,
            "defence": 100
        },
        "used_items": [],
        "autosave": {
            "filename": str,
            "enabled": False,
        }
    }

# Save game state to JSON file
def json_save(game):
    file_name = game["autosave"]["filename"] if game["autosave"]["enabled"] else input(f"{style.BLUE}{style.BOLD}Save filename >>>{style.RESET} ").strip()
    file_name = file_name if file_name.endswith(".json") else file_name+".json"

    if file_name == '':
        print(f' {style.RED} > Invalid filename (either it already exists or blank) try again')
        json_save(game)
        return
    elif os.path.exists(file_name):
        n = input(" Are you sure you want to overwrite this file? (y/n) >>> ").strip().lower() if not game else 'y'

        if n == 'y':
            try:
                with open(file_name, 'w')as f: json.dump(game, f)
                _ = print(f"\n{style.GREEN}Game saved to {file_name}{style.RESET}") if not game["autosave"]["enabled"] else None
            except Exception as e:
                print(f"{style.RED} > Unable to write file with error: {e}{style.RESET}")
        else:
            return
    else:
        try:
            with open(file_name, 'w')as f:
                json.dump(game, f)

            _ = print(f"\n{style.GREEN}Game saved to {file_name}{style.RESET}") if not game["autosave"]["enabled"] else None

        except Exception as e:
            print(f"{style.RED} > Unable to write file with error: {e}{style.RESET}") 

# Typewriter effect for text output
def typewriter(text, color=style.RESET, delay=0.02, post_delay=0.5):
    for c in text:
        print(f"{color}{c}{style.RESET}", end='', flush=True)
        time.sleep(delay)
    print()
    time.sleep(post_delay)

# Load game state from JSON file
def json_load():
    file_name = input(f"{style.BLUE}{style.BOLD} Load file name >>>{style.RESET} ").strip() + ".json"

    if not os.path.exists(file_name):
        print(f"{style.RED} > File not found: {file_name}{style.RESET}")
        time.sleep(2)
        return init_new_game()

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
                "cheat_mode": bool,
                "xp": int,
                "skill_set": dict,
                "used_items": list,
                "autosave": dict
            }

            # Validate required keys and types
            for key, expected_type in required_keys.items():
                if key not in game_state:
                    print(f"{style.RED} > Error loading file, Invalid format{style.RESET}")
                    return init_new_game()
                if not isinstance(game_state[key], expected_type):
                    print(f"{style.RED} > Error loading file, Invalid Format{style.RESET}")
                    return init_new_game()

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
                    return init_new_game()

            # Validate skill_set format
            for skill, level in game_state["skill_set"].items():
                if skill not in ["strength", "agility", "luck", "accuracy", "defence"]:
                    print(f"{style.RED} > Error loading file, Invalid skill: {skill}{style.RESET}")
                    return init_new_game()
                if not isinstance(level, int) or level < 0:
                    print(f"{style.RED} > Error loading file, Invalid level for skill {skill}{style.RESET}")
                    return init_new_game()

            # Validate artifacts format
            if not all(isinstance(a, str) for a in game_state["artifacts"]):
                print(f"{style.RED} > Error loading file, Invalid format{style.RESET}")
                return init_new_game()
            
            if not all(isinstance(a, str) for a in game_state["used_items"]):
                print(f"{style.RED} > Error loading file, Invalid format{style.RESET}")
                return init_new_game()

            for key, value in game_state["autosave"].items():
                if key not in ["filename", "enabled"]:
                    print(f"{style.RED} > Error loading file, Invalid autosave key: {key}{style.RESET}")
                    return init_new_game()
                if key == "enabled" and not isinstance(value, bool):
                    print(f"{style.RED} > Error loading file, Invalid type for autosave key {key}{style.RESET}")
                    return init_new_game()
                if key == "filename" and (not isinstance(value, str) and value):
                    print(f"{style.RED} > Error loading file, Invalid type for autosave key {key}{style.RESET}")
                    return init_new_game()

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
        time.sleep(0.5)
        print(f"{style.RED} > Proceeding to initiate new file...{style.RESET}")

        time.sleep(2)

        return init_new_game()

# Check for game over or victory conditions
def check_game_over(game):
    if game["hp"] <= 0:
        if "Phoenix's Feather" in game["inventory"] and not "Phoenix's Feather" in game["used_items"]:
            print(f"\n{style.BOLD}{style.UNDERLINE}{style.GREEN}REVIVED!{style.RESET} {style.GREEN}You have been revived by the Phoenix's Feather.{style.RESET}")
            game["hp"] = game["max_hp"] // 2
            game["used_items"].append("Phoenix's Feather")
            game['inventory'].remove("Phoenix's Feather")
        else:    
            print(f"\n{style.BOLD}{style.UNDERLINE}{style.RED}GAME OVER!{style.RESET}{style.RED} You have been defeated.{style.RESET}")
            return game, True
    elif game["level"] == 25:
        game = bossfights.lv_25_boss_fight(game)
        return game, True
    else:
        return game, False

# To use an item
def use_item(game, battle=True):
    global mi, nsvc

    #m e not code dis bit
    if game['inventory']:
        # Count items manually
        item_counts = {}
        for item in game["inventory"]:
            item_counts[item] = item_counts.get(item, 0) + 1

        # Display them with x(num)
        items_list = list(item_counts.keys())
        for idx, item in enumerate(items_list, start=1):
            print(f" {idx}. {item} x{item_counts[item]}")

        choice = int(input("Pick an item to use (#) >>> ")) - 1
        count = 1 if battle else int(input("How many would you like to use? >>> "))
        for _ in range(count):
            if 0 <= choice < len(items_list):
                item = items_list[choice]

                if item == "Small Health Potion":
                    game["hp"] += 20
                    game["hp"] = min(game["hp"], game["max_hp"])
                    typewriter(f"You used {item}!", style.GREEN)
                    typewriter(f"Your HP is now {game['hp']}.", style.GREEN)
                    game["inventory"].remove(item)

                elif item == "Wooden Shield":
                    game['skill_set']["defence"] += 0.2
                    typewriter(f"You equipped {item}!", style.GREEN)
                    typewriter(f"Your defence is now {game['skill_set']['defence']}.", style.GREEN)
                    game["inventory"].remove(item)

                elif item == "Medium Health Potion":
                    game["hp"] += 50
                    game["hp"] = min(game["hp"], game["max_hp"])
                    typewriter(f"You used {item}!", style.GREEN)
                    typewriter(f"Your HP is now {game['hp']}.", style.GREEN)
                    game["inventory"].remove(item)

                elif item == "Large Health Potion":
                    game["hp"] += 90
                    game["hp"] = min(game["hp"], game["max_hp"])
                    typewriter(f"You used {item}!", style.GREEN)
                    typewriter(f"Your HP is now {game['hp']}.", style.GREEN)
                    game["inventory"].remove(item)

                elif item == "Beginner's Scroll":
                    spells = [["Flare Dash", 80, 120], ["Icicle Barrage", 100, 150], ["Earth Shatter", 120, 180]]
                    spell = r.choice(spells, weights=[50, 35, 15])
                    typewriter(f"You learned a new spell: {spell[0]}!", style.GREEN)
                    game["spells"].append(spell)
                    game["inventory"].remove(item)
                    typewriter(f"The Scroll was used up", style.YELLOW)

                elif item == "Assassin's Cloak" and not "Assassin's Cloak" in game['used_items']:
                    game['skill_set']['agility'] += 5
                    game['skill_set']['accuracy'] += 5

                    typewriter(f"You equipped {item}!", style.GREEN)
                    typewriter(f"Your stats are now {game['skill_set']}.", style.GREEN)
                    game["inventory"].remove(item)
                    game['used_items'].append(item)

                elif item == "Elite Health Potion":
                    game["hp"] += 150
                    game["hp"] = min(game["hp"], game["max_hp"])
                    typewriter(f"You used {item}!", style.GREEN)
                    typewriter(f"Your HP is now {game['hp']}.", style.GREEN)
                    game["inventory"].remove(item)

                elif item == "Secret Map":
                    if not mi:
                        typewriter("You don't seem to know how to use this item!", style.RED)

                elif item == "Assassin Build Scroll" and "Assassin's Cloak" in game['used_items'] and not "Assassin's Build Scroll" in game['used_items']:
                    game["weapons"].append(["Assassin's Dagger", 100, 200])
                    game["skill_set"]["agility"] += 5
                    game["skill_set"]["accuracy"] += 5
                    game["used_items"].append(item)
                    typewriter("You have successfully created the Assassin Build!", style.GREEN)
                    typewriter(f"Your new weapon is: {game['weapons'][-1][0]}")
                    typewriter(f"Your new stats are: {game['skill_set']}")

                elif item == "Legendary Health Potion":
                    game["hp"] += 200
                    game["hp"] = min(game["hp"], game["max_hp"])
                    typewriter(f"You used {item}!", style.GREEN)
                    typewriter(f"Your HP is now {game['hp']}.", style.GREEN)
                    game["inventory"].remove(item)

                elif item == "Divine Health Potion":
                    game["hp"] += 300
                    game["hp"] = min(game["hp"], game["max_hp"])
                    typewriter(f"You used {item}!", style.GREEN)
                    typewriter(f"Your HP is now {game['hp']}.", style.GREEN)
                    game["inventory"].remove(item)

                elif item == "Mystic Cloak" and not "Mystic Cloak" in game['used_items']:
                    new_weapons = []
                    for w in game["weapons"]:
                        w[1] += 50
                        w[2] += 50
                        new_weapons.append(w)

                    game["weapons"] = new_weapons
                    game["max_hp"] += 50
                    game["hp"] = game["max_hp"]

                    typewriter("You have used the Mystic Cloak and buffed all your weapons by 50 dmg and your HP, also regenerated to max.", style.GREEN)
                    typewriter("Your new stats are: ", style.GREEN)
                    typewriter(f"HP: {game['hp']}/{game['max_hp']}", style.GREEN)
                    for w in game["weapons"]:
                        typewriter(f" - {w[0]}: {w[1]}-{w[2]}", style.GREEN, delay=0.01)
                    game["inventory"].remove(item)
                    game["used_items"].append(item)
                
                elif item == "Infinity Buff":
                    game["max_hp"] += round(game["max_hp"]*0.1)
                    game["skill_set"] = {k: v * 2 for k, v in game["skill_set"].items()}

                    game["inventory"].remove(item)
                    game["used_items"].append(item)
                    typewriter("You have used the Infinity Buff and restored your HP to max.", style.GREEN)
                    typewriter(f"Your HP is now: {game['hp']}/{game['max_hp']}", style.GREEN)
                    typewriter("Your skills have been doubled:", style.GREEN)
                    for skill, value in game["skill_set"].items():
                        typewriter(f" - {skill}: {value}", style.GREEN)

                elif item == "Infinity Heal":
                    game["max_hp"] *= 2
                    game["hp"] = game["max_hp"]
                    game["inventory"].remove(item)
                    typewriter("You have used the Infinity Heal and restored your HP to max.", style.GREEN)
                
                elif item == "Secret Map":

                    if mi:
                        if nsvc < 1:
                            typewriter("woosh *portal* wow so exciting so sjdlfkjlksdjfkljlskdfjkl *sarcasm*", style.YELLOW)
                            game = cozycoder(game)
                        else:
                            game = cozycoder(game)
                    else:
                        typewriter("You don't seem to know how to use this item!", style.RED)
    else:
        typewriter("You don't have anything to use!", style.RED)

    return game

def LaDoodle_dialouge(game):
    global nsvc, x, bsvc, y, mi
    if bsvc == 0:
        typewriter("...", style.YELLOW, post_delay=1.5)
        typewriter("I see you're a traveler. What brings you here?", style.YELLOW, post_delay=1)
        typewriter("Oh, I forgot, ur playing the game",style.GREEN, post_delay=1)
        typewriter("Weeeelll.", style.GREEN, post_delay=0.75)
        typewriter("I'm Krivi's avatar, LaDoodleInTheHat.", style.GREEN, post_delay=1)
        typewriter("Well without the hat rlly, cause I lost it.", style.YELLOW, post_delay=1)
        typewriter("Have you seen Noah?", style.YELLOW)
        if input(" (y/n) > ").strip().lower() == "y":
            if nsvc > 0:
                typewriter("Oh you have!", style.GREEN, post_delay=1)
                typewriter("That's great to hear!", style.GREEN, post_delay=1)
                typewriter("Then you must have my hat!", style.GREEN)
                if input(" (y/n) > ").strip().lower() == "y":
                    if "LaDoodle's Hat" in game['artifacts']:
                        typewriter("NIIIICCCEEEE", style.GREEN, post_delay=1)
                        typewriter("Can you give it back to me pls?", style.GREEN)
                        if input(" (y/n) > ").strip().lower() == 'y':
                            typewriter("Thx man.", style.GREEN)
                            game['artifacts'].remove("LaDoodle's Hat")
                            print(f" {style.BOLD}- LaDoodle's Hat {style.RESET} ")
                            time.sleep(0.1)
                            print(f" {style.BOLD}+ 500 Gold {style.RESET} ")
                            game['gold'] += 500
                            time.sleep(0.1)
                            typewriter("I gave you a little something extra for your trouble.", style.GREEN)
                    else:
                        typewriter("Dude. Don't lie, I'm a god but like the only thing I can't do is find my hat.", style.RED)
            else:
                typewriter("Dude. Don't lie, I'm a god but like the only thing I can't do is find my hat.", style.RED, post_delay=1)
                typewriter("He's been missing for a while now...", style.YELLOW, post_delay=1)
                typewriter("And I think he has my hat...", style.YELLOW, post_delay=1)
                if not ('Secret Map' in game['inventory']):
                    typewriter("I have this map that might help you find him.", style.YELLOW, post_delay=1)
                    print(f" {style.BOLD}+ Secret Map {style.RESET} ")
                    time.sleep(0.1)
                    game["inventory"].append("Secret Map")
                    typewriter("Use it to find Noah and maybe my Hat", style.YELLOW, post_delay=1)
                    typewriter("It would be nice if you can get my hat back.", style.GREEN)
                elif 'Secret Map' in game['inventory']:
                    typewriter("I see you already have the map.", style.YELLOW, post_delay=1)
                    typewriter("Use it to find Noah and maybe my Hat", style.YELLOW, post_delay=1)
                    typewriter("It would be nice if you can get my hat back.", style.GREEN)

                x = True

        else:
            time.sleep(0.5)
            typewriter("He's been missing for a while now...", style.YELLOW, post_delay=1)
            typewriter("And I think he has my hat...", style.YELLOW, post_delay=1)
            if not ('Secret Map' in game['inventory']):
                typewriter("I have this map that might help you find him.", style.YELLOW, post_delay=0.6)
                print(f" {style.BOLD}+ Secret Map {style.RESET} ")
                time.sleep(0.1)
                game["inventory"].append("Secret Map")
                typewriter("Use it to find Noah and maybe my Hat", style.YELLOW, post_delay=1)
                typewriter("It would be nice if you can get my hat back.", style.GREEN)
            elif 'Secret Map' in game['inventory']:
                typewriter("I see you already have the map.", style.YELLOW, post_delay=1)
                typewriter("Use it to find Noah and maybe my Hat", style.YELLOW, post_delay=1)
                typewriter("It would be nice if you can get my hat back.", style.GREEN, post_delay=1)

            x = True

        time.sleep(0.5)
        typewriter("Anyway, you can buy stuff from here", style.GREEN, post_delay=1)
        typewriter("Pretty op stuff :)", style.GREEN, post_delay=1)
        typewriter("Let's get shopping!", style.GREEN)

        mi = True

    elif bsvc == 1:
        typewriter("Welcome back my friend!", style.GREEN, post_delay=1)
        if x:
            typewriter("Have you seen Noah?", style.YELLOW, post_delay=1)
            typewriter("Yet?", style.YELLOW)
            if input(" (y/n) > ").strip().lower() == "y":
                if nsvc > 0:
                    typewriter("Oh finally!", style.GREEN, post_delay=1)
                    typewriter("That's great to hear!", style.GREEN, post_delay=1)
                    typewriter("Then you must have my hat!", style.GREEN)
                    if input(" (y/n) > ").strip().lower() == "y":
                        if "LaDoodle's Hat" in game['artifacts']:
                            typewriter("NIIIICCCEEEE", style.GREEN, post_delay=1)
                            typewriter("Can you give it back to me pls?", style.GREEN)
                            if input(" (y/n) > ").strip().lower() == 'y':
                                
                                typewriter("Thx man.", style.GREEN)
                                game['artifacts'].remove("LaDoodle's Hat")
                                time.sleep(0.1)
                                print(f" {style.BOLD}- LaDoodle's Hat {style.RESET} ")
                                time.sleep(0.1)
                                print(f" {style.BOLD}+ 500 Gold {style.RESET} ")
                                game['gold'] += 500
                                time.sleep(0.1)
                                typewriter("I gave you a little something extra for your trouble.", style.GREEN)
                        else:
                            typewriter("Dude. Don't lie, I'm a god but like the only thing I can't do is find my hat.", style.RED)
                else:
                    typewriter("Dude. Don't lie, I'm a god but like the only thing I can't do is find my hat.", style.RED)
        typewriter("You know the drill.", post_delay=1)
        typewriter("Let's get shopping!", style.GREEN)

    if bsvc >= 2 :
        if nsvc > 0 and not y:
            typewriter("You saw Noah? That's incredible!", style.GREEN, post_delay=1)
            typewriter("He's been missing for ages... I was starting to worry.", style.YELLOW, post_delay=1)
            typewriter("Did he seem alright? What was he up to?", style.YELLOW, post_delay=1)
            typewriter("If you hear anything interesting, let me know. He's a good friend.", style.GREEN, post_delay=1.5)
            typewriter("I see you have my hat", style.GREEN, post_delay=1)
            typewriter("Can you give it back to me pls?", style.GREEN)
            if input(" (y/n) > ").strip().lower() == 'y':
                typewriter("Thx man.", style.GREEN)
                game['artifacts'].remove("LaDoodle's Hat")
                time.sleep(0.1)
                print(f" {style.BOLD}- LaDoodle's Hat {style.RESET} ")
                time.sleep(0.1)
                print(f" {style.BOLD}+ 500 Gold {style.RESET} ")
                game['gold'] += 500
                time.sleep(0.1)
                typewriter("I gave you a little something extra for your trouble.", style.GREEN)
            else: 
                typewriter("I promise I'll give you something good next time.", style.YELLOW)
            y = True
        elif y and nsvc > 0:
            typewriter("Yo, can I pls have my hat back pretty pls, I'll give you a super special reward!", style.YELLOW)
            if input(" (y/n) > ").strip().lower() == 'y':
                typewriter("Thx man.", style.GREEN)
                game['artifacts'].remove("LaDoodle's Hat")
                time.sleep(0.1)
                print(f" {style.BOLD}- LaDoodle's Hat {style.RESET} ")
                time.sleep(0.1)
                print(f" {style.BOLD}+ 500 Gold {style.RESET} ")
                game['gold'] += 500
                time.sleep(0.1)
                typewriter("I gave you a little something extra for your trouble.", style.GREEN)
            else:
                typewriter(":(", style.YELLOW)
            y = True

        typewriter("Same stuff as before my adventurer friend!", style.GREEN, post_delay=1)
        typewriter("Check them out!", style.GREEN)

    return game

# Handle random encounters (monster, treasure, shopkeeper)
def random_encounter(game):
    global bsvc
    spinner(1, 0.1)

    # Monster format: [name, hp, damage, reward, chance, xp drop]
    monsters = [
        # Level 1 (Player: HP 100, Weapon 10-20)
        [
            ["Slime", 90, 28, 50, 10, 55],
            ["Rat", 95, 32, 54, 20, 58],
            ["Goblin", 100, 36, 60, 30, 60],
            ["Bat", 88, 27, 48, 40, 52],
            ["Wild Mouse", 92, 29, 50, 50, 53],
            ["Tiny Spider", 85, 26, 47, 60, 50],
            ["Lost Chick", 83, 25, 45, 70, 48],
            ["Baby Snake", 87, 28, 49, 80, 51],
            ["Mischievous Pixie", 90, 29, 51, 90, 54],
            ["Angry Squirrel", 86, 27, 47, 100, 50],
            ["Bandit Initiate", 98, 31, 68, 110, 62],
            ["Forest Beetle", 89, 28, 49, 120, 52],
        ],
        # Level 2
        [
            ["Wolf", 125, 34, 70, 10, 75],
            ["Bandit", 130, 36, 74, 20, 78],
            ["Goblin Brute", 135, 38, 78, 30, 82],
            ["Snake", 120, 32, 66, 40, 70],
            ["Wild Dog", 128, 33, 68, 50, 72],
            ["Forest Spider", 126, 31, 64, 60, 69],
            ["Bandit Scout", 132, 35, 72, 70, 77],
            ["Angry Crow", 118, 30, 62, 80, 66],
            ["Wild Cat", 125, 33, 68, 90, 74],
            ["Mischievous Goblin", 123, 32, 65, 100, 71],
            ["Bandit Slinger", 137, 37, 80, 110, 84],
            ["Forest Snake", 127, 34, 69, 120, 73],
        ],
        # Level 3
        [
            ["Skeleton", 105, 30, 70, 10, 80],
            ["Wild Boar", 120, 32, 75, 20, 85],
            ["Orc", 140, 35, 80, 30, 90],
            ["Zombie Dog", 110, 28, 65, 40, 75],
            ["Bandit Archer", 125, 31, 68, 50, 78],
            ["Ghoul", 115, 29, 66, 60, 77],
            ["Forest Wolf", 118, 30, 69, 70, 82],
            ["Wild Ram", 122, 31, 71, 80, 84],
            ["Cave Bat", 108, 27, 63, 90, 73],
            ["Angry Boar", 112, 28, 67, 100, 76],
        ],
        # Level 4
        [
            ["Zombie", 170, 38, 95, 10, 105],
            ["Bandit Leader", 190, 42, 100, 20, 110],
            ["Orc Warrior", 210, 46, 110, 30, 120],
            ["Ghoul", 180, 40, 90, 40, 100],
            ["Wild Bear", 200, 44, 105, 50, 115],
            ["Forest Troll", 185, 41, 98, 60, 108],
            ["Bandit Swordsman", 195, 43, 102, 70, 112],
            ["Cave Spider", 175, 39, 93, 80, 103],
            ["Angry Bear", 188, 42, 99, 90, 109],
            ["Wild Lynx", 178, 38, 94, 100, 104],
        ],
        # Level 5
        [
            ["Giant Spider", 240, 60, 120, 10, 130],
            ["Ghoul", 260, 64, 130, 20, 140],
            ["Troll", 280, 68, 140, 30, 150],
            ["Swamp Lizard", 250, 62, 125, 40, 135],
            ["Bandit Mage", 270, 66, 135, 50, 145],
            ["Forest Ogre", 255, 63, 128, 60, 138],
            ["Wild Crocodile", 265, 65, 132, 70, 142],
            ["Cave Troll", 245, 61, 123, 80, 133],
            ["Angry Troll", 258, 64, 129, 90, 139],
            ["Swamp Rat", 248, 60, 121, 100, 131],
        ],
        # Level 6
        [
            ["Dire Wolf", 310, 72, 160, 10, 170],
            ["Dark Mage", 330, 76, 170, 20, 180],
            ["Ogre", 350, 80, 180, 30, 190],
            ["Vampire", 320, 74, 165, 40, 175],
            ["Forest Troll", 340, 78, 175, 50, 185],
            ["Bandit Captain", 325, 75, 168, 60, 178],
            ["Cave Ogre", 335, 77, 172, 70, 182],
            ["Wild Panther", 315, 73, 163, 80, 173],
            ["Angry Ogre", 328, 76, 169, 90, 179],
            ["Dark Sorcerer", 318, 72, 161, 100, 171],
        ],
        # Level 7
        [
            ["Vampire Bat", 390, 84, 190, 10, 200],
            ["Wraith", 410, 88, 200, 20, 210],
            ["Minotaur", 430, 92, 210, 30, 220],
            ["Specter", 400, 86, 195, 40, 205],
            ["Cave Ogre", 420, 90, 205, 50, 215],
            ["Bandit Berserker", 405, 87, 198, 60, 208],
            ["Wild Tiger", 415, 89, 202, 70, 212],
            ["Angry Minotaur", 395, 85, 193, 80, 203],
            ["Dark Wraith", 408, 88, 199, 90, 209],
            ["Spectral Bat", 398, 84, 191, 100, 201],
        ],
        # Level 8
        [
            ["Fire Elemental", 480, 96, 220, 10, 230],
            ["Ice Golem", 500, 100, 230, 20, 240],
            ["Werewolf", 520, 104, 240, 30, 250],
            ["Frost Bat", 490, 98, 225, 40, 235],
            ["Bandit Captain", 510, 102, 235, 50, 245],
            ["Forest Werewolf", 495, 99, 228, 60, 238],
            ["Wild Rhino", 505, 101, 232, 70, 242],
            ["Cave Golem", 485, 97, 223, 80, 233],
            ["Angry Golem", 498, 100, 229, 90, 239],
            ["Ice Elemental", 488, 96, 221, 100, 231],
        ],
        # Level 9
        [
            ["Stone Guardian", 570, 108, 250, 10, 260],
            ["Necromancer", 590, 112, 260, 20, 270],
            ["Cyclops", 610, 116, 270, 30, 280],
            ["Shadow Beast", 580, 110, 255, 40, 265],
            ["Forest Spirit", 600, 114, 265, 50, 275],
            ["Bandit Sorcerer", 585, 111, 258, 60, 268],
            ["Wild Elephant", 595, 113, 262, 70, 272],
            ["Cave Cyclops", 575, 109, 253, 80, 263],
            ["Angry Cyclops", 588, 112, 259, 90, 269],
            ["Shadow Elemental", 578, 108, 251, 100, 261],
        ],
        # Level 11
        [
            ["Hellhound", 750, 132, 310, 10, 320],
            ["Specter", 770, 136, 320, 20, 330],
            ["Demon", 790, 140, 330, 30, 340],
            ["Dark Knight", 760, 134, 315, 40, 325],
            ["Ancient Zombie", 780, 138, 325, 50, 335],
            ["Forest Demon", 765, 135, 318, 60, 328],
            ["Wild Mammoth", 775, 137, 322, 70, 332],
            ["Cave Demon", 755, 133, 313, 80, 323],
            ["Angry Demon", 768, 136, 319, 90, 329],
            ["Spectral Knight", 758, 132, 311, 100, 321],
        ],
        # Level 12
        [
            ["Forest Spirit", 840, 144, 340, 10, 350],
            ["Lich", 860, 148, 350, 20, 360],
            ["Golem King", 880, 152, 360, 30, 370],
            ["Sand Worm", 850, 146, 345, 40, 355],
            ["Thunder Hawk", 870, 150, 355, 50, 365],
            ["Forest Lich", 855, 147, 348, 60, 358],
            ["Wild Gorilla", 865, 149, 352, 70, 362],
            ["Cave Lich", 845, 145, 343, 80, 353],
            ["Angry Lich", 858, 148, 349, 90, 359],
            ["Sand Elemental", 848, 144, 341, 100, 351],
        ],
                # Level 13
        [
            ["Sand Serpent", 920, 156, 360, 10, 370],
            ["Lava Golem", 940, 160, 370, 20, 380],
            ["Bone Dragon", 960, 164, 380, 30, 390],
            ["Storm Eagle", 930, 158, 365, 40, 375],
            ["Ancient Mummy", 950, 162, 375, 50, 385],
            ["Cave Guardian", 935, 159, 368, 60, 378],
            ["Wild Rhino Beast", 945, 161, 372, 70, 382],
            ["Sand Spirit", 925, 157, 363, 80, 373],
            ["Angry Serpent", 938, 160, 369, 90, 379],
            ["Storm Elemental", 928, 156, 361, 100, 371],
        ],
        # Level 14
        [
            ["Crystal Golem", 1000, 168, 390, 10, 400],
            ["Spectral Mage", 1020, 172, 400, 20, 410],
            ["Hydra", 1040, 176, 410, 30, 420],
            ["Stone Serpent", 1010, 170, 395, 40, 405],
            ["Ancient Guardian", 1030, 174, 405, 50, 415],
            ["Forest Chimera", 1015, 171, 398, 60, 408],
            ["Wild Basilisk", 1025, 173, 402, 70, 412],
            ["Crystal Serpent", 1005, 169, 393, 80, 403],
            ["Angry Chimera", 1018, 172, 399, 90, 409],
            ["Spectral Guardian", 1008, 168, 391, 100, 401],
        ],
        # Level 15
        [
            ["Lava Serpent", 1100, 180, 420, 10, 430],
            ["Dark Knight", 1120, 184, 430, 20, 440],
            ["Chaos Beast", 1140, 188, 440, 30, 450],
            ["Shadow Drake", 1110, 182, 425, 40, 435],
            ["Ancient Titan", 1130, 186, 435, 50, 445],
            ["Cave Behemoth", 1115, 183, 428, 60, 438],
            ["Wild Wyvern", 1125, 185, 432, 70, 442],
            ["Chaos Hound", 1105, 181, 423, 80, 433],
            ["Angry Wyvern", 1118, 184, 429, 90, 439],
            ["Dark Elemental", 1108, 180, 421, 100, 431],
        ],
        # Level 16
        [
            ["Storm Titan", 1200, 192, 450, 10, 460],
            ["Doom Knight", 1220, 196, 460, 20, 470],
            ["Lich King", 1240, 200, 470, 30, 480],
            ["Thunder Drake", 1210, 194, 455, 40, 465],
            ["Ancient Colossus", 1230, 198, 465, 50, 475],
            ["Cave Leviathan", 1215, 195, 458, 60, 468],
            ["Wild Chimera", 1225, 197, 462, 70, 472],
            ["Storm Serpent", 1205, 193, 453, 80, 463],
            ["Angry Chimera", 1218, 196, 459, 90, 469],
            ["Thunder Elemental", 1208, 192, 451, 100, 461],
        ],
        # Level 17
        [
            ["Flame Titan", 1300, 204, 480, 10, 490],
            ["Death Knight", 1320, 208, 490, 20, 500],
            ["Chaos Dragon", 1340, 212, 500, 30, 510],
            ["Inferno Drake", 1310, 206, 485, 40, 495],
            ["Ancient Demon", 1330, 210, 495, 50, 505],
            ["Cave Titan", 1315, 207, 488, 60, 498],
            ["Wild Behemoth", 1325, 209, 492, 70, 502],
            ["Infernal Serpent", 1305, 205, 483, 80, 493],
            ["Angry Dragon", 1318, 208, 489, 90, 499],
            ["Fire Elemental", 1308, 204, 481, 100, 491],
        ],
        # Level 18
        [
            ["Frost Titan", 1400, 216, 510, 10, 520],
            ["Dread Knight", 1420, 220, 520, 20, 530],
            ["Elder Dragon", 1440, 224, 530, 30, 540],
            ["Ice Drake", 1410, 218, 515, 40, 525],
            ["Ancient Wraith", 1430, 222, 525, 50, 535],
            ["Cave Colossus", 1415, 219, 518, 60, 528],
            ["Wild Phoenix", 1425, 221, 522, 70, 532],
            ["Frost Serpent", 1405, 217, 513, 80, 523],
            ["Angry Phoenix", 1418, 220, 519, 90, 529],
            ["Ice Elemental", 1408, 216, 511, 100, 521],
        ],
        # Level 19
        [
            ["Storm Colossus", 1500, 228, 540, 10, 550],
            ["Hell Knight", 1520, 232, 550, 20, 560],
            ["Void Dragon", 1540, 236, 560, 30, 570],
            ["Thunder Wyvern", 1510, 230, 545, 40, 555],
            ["Ancient Seraph", 1530, 234, 555, 50, 565],
            ["Cave Leviathan", 1515, 231, 548, 60, 558],
            ["Wild Titan", 1525, 233, 552, 70, 562],
            ["Storm Phoenix", 1505, 229, 543, 80, 553],
            ["Angry Seraph", 1518, 232, 549, 90, 559],
            ["Thunder Elemental", 1508, 228, 541, 100, 551],
        ],
        # Level 20
        [
            ["Infernal Colossus", 1600, 240, 570, 10, 580],
            ["Abyss Knight", 1620, 244, 580, 20, 590],
            ["Chaos Wyrm", 1640, 248, 590, 30, 600],
            ["Hell Serpent", 1610, 242, 575, 40, 585],
            ["Ancient Archdemon", 1630, 246, 585, 50, 595],
            ["Cave Behemoth", 1615, 243, 578, 60, 588],
            ["Wild Dragon", 1625, 245, 582, 70, 592],
            ["Infernal Wyvern", 1605, 241, 573, 80, 583],
            ["Angry Wyrm", 1618, 244, 579, 90, 589],
            ["Abyss Elemental", 1608, 240, 571, 100, 581],
        ],

        # Level 21
        [
            ["Shadow Dragon", 1700, 332, 820, 15, 830],
            ["Archdemon", 1720, 336, 830, 35, 840],
            ["Elder Titan", 1740, 340, 840, 55, 850],
            ["Frost Phoenix", 1710, 334, 825, 75, 835],
            ["Chaos Lord", 1730, 338, 835, 100, 845],
        ],
        # Level 22
        [
            ["Frost Phoenix", 1760, 344, 860, 15, 870],
            ["Chaos Lord", 1780, 348, 870, 35, 880],
            ["Ancient Colossus", 1800, 352, 880, 55, 890],
            ["Solar Serpent", 1770, 346, 865, 75, 875],
            ["Void Titan", 1790, 350, 875, 100, 885],
        ],
        # Level 23
        [
            ["Solar Serpent", 1820, 356, 900, 15, 910],
            ["Void Titan", 1840, 360, 910, 35, 920],
            ["Elder Dragon", 1860, 364, 920, 55, 930],
            ["Star Guardian", 1830, 358, 905, 75, 915],
            ["Time Wraith", 1850, 362, 915, 100, 925],
        ],
        # Level 24
        [
            ["Star Guardian", 1880, 368, 940, 15, 950],
            ["Time Wraith", 1900, 372, 950, 35, 960],
            ["Cosmic Leviathan", 1920, 376, 960, 55, 970],
            ["Celestial Hydra", 1890, 370, 945, 75, 955],
            ["Ancient Phoenix", 1910, 374, 955, 100, 965],
        ],

    ]

    i = r.randint(0, 100)
    i = int(input(" >>> ")) if game["cheat_mode"] else i
    
    if i <= max(43, 89 - 2*game['level']):
        # Monster fight
        i = r.randint(0, 100)
        for monster in monsters[game['level'] - 1]:
            if i <= monster[4]:
                typewriter(f"{monster[0]} appeared!", style.RED)
                player_weapon = game["weapons"][game["equipped"]]
                typewriter(f"{monster[0]} has {monster[1]} HP!", style.YELLOW)
                typewriter(f"You ready your {player_weapon[0]}!", style.YELLOW)

                time.sleep(1)

                # Battle loop
                while monster[1] > 0 and game["hp"] > 0:
                    qu = input(f"\n{style.BOLD}What would you like to do (run/attack/counter/use item) >>> {style.RESET}").strip().lower()
                    print()
                    dmg = r.randint(player_weapon[1] + 5*game['skill_set']['strength'], player_weapon[2] + 5*game['skill_set']['strength'])
                    mdmg = round(r.randint(int(monster[2]*0.7), monster[2]) - 5*game['skill_set']['defence'])
                    os.system('cls' if os.name == 'nt' else 'clear')

                    if qu == "run":
                        if r.randint(0, 100) < 75 - 3*game['level']+5*game['skill_set']['agility']:
                            typewriter("You successfully ran away!", style.GREEN)
                            break
                        else:
                            typewriter("You failed to escape!", style.RED)
                            if monster[1] > 0:
                                if r.randint(0, 100) < 50 - 2*game['level'] + 5*game['skill_set']['agility']:
                                    game["hp"] -= mdmg
                                    typewriter(f"{monster[0]} strikes you for {mdmg} damage!", style.RED)
                                else:
                                    typewriter("The monster's attack missed!", style.GREEN)
                    elif qu == "attack":
                        if r.randint(0, 100) < 75 - 3*game['level'] + 5*game['skill_set']['accuracy']:
                            monster[1] -= dmg
                            typewriter(f"You attack {monster[0]} for {dmg} damage!", style.GREEN)
                        else:
                            typewriter("Your attack missed!", style.RED)
                        if monster[1] > 0:
                            if r.randint(0, 100) < 75 + 2*game['level'] - 5*game['skill_set']['agility']:
                                game["hp"] -= mdmg
                                typewriter(f"{monster[0]} strikes you for {mdmg} damage!", style.RED)
                            else:
                                typewriter("The monster's attack missed!", style.GREEN)
                    elif qu == "counter":
                        if r.randint(0, 100) <= 75 - 3*game['level'] + 5*game['skill_set']['accuracy']:
                            dmg = r.randint(min(player_weapon[2], monster[2]), round(max(player_weapon[2], monster[2]) * 1.5))
                            monster[1] -= dmg
                            typewriter(f"{monster[0]} tried to strike you, but failed!", style.GREEN)
                            typewriter(f"You counter {monster[0]}'s attack for {dmg}!", style.GREEN)
                        else:
                            typewriter("Your counter failed!", style.RED)
                            if monster[1] > 0:
                                if r.randint(0, 100) < 75 - 3*game['level'] + 5*game['skill_set']['agility']:
                                    game["hp"] -= mdmg
                                    typewriter(f"{monster[0]} strikes you for {mdmg} damage!", style.RED)
                                else:
                                    typewriter("The monster's attack missed!", style.GREEN)
                    elif qu == "use item":
                        
                        game = use_item(game)

                        spinner(2, 0.1)

                        i = r.randint(0, 100)
                        if i <= 60 + 3*game['level'] - 5*game['skill_set']['agility'] and monster[1] > 0:
                            typewriter("The monster is preparing to attack!", style.YELLOW)

                            spinner(2, 0.1)

                            his_attack = f"{monster[0]} strikes you for {mdmg} damage!"
                            game["hp"] -= mdmg
                            typewriter(his_attack, style.RED)
                            
                        else:
                            typewriter("You safely use your item.", style.GREEN)

                    hp_line = f"Your HP: {max(game['hp'],0)} | {monster[0]} HP: {max(monster[1],0)}"
                    typewriter(hp_line, style.YELLOW)

                    time.sleep(2)

                if monster[1] <= 0:
                    typewriter(f"{monster[0]} is defeated!", style.MAGENTA)
                    typewriter(f"You gain {monster[3]} gold!", style.YELLOW)
                    typewriter(f"You gain {monster[5]} XP!", style.GREEN)
                    game["gold"] += monster[3]
                    game["xp"] += monster[5]

                time.sleep(3)

    elif i <= max(77, 99 - 2*game['level']):
        spinner(2, 0.1)
        reward = r.randint(0, 200) + game['level'] * 10
        game["gold"] += reward

        typewriter("You found a treasure chest!", style.YELLOW, post_delay=1)
        spinner(2, 0.1)
        typewriter(f"You found {reward} gold!", style.GREEN)

    
    elif i <= 100:
        # Shopkeeper encounter

        game = LaDoodle_dialouge(game)

        pen = ["Pen", 999999999999999999999999999999999, 999999999999999999999999999999999999999999999999999999999999999999]
        
        while True:
            item_costs = {
                "Pen": 2000*game["level"],
                "Infinity Heal": 500*game["level"],
                "Infinity Buff" : 500*game["level"],
                "Level Up": 500*game["level"]
            }

            items = ["Pen", "Infinity Heal", "Infinity Buff", "Level Up"]

            for idx, (item, cost) in enumerate(item_costs.items(), start=1):
                print(f'{idx}. {item}: {cost} gold')
                time.sleep(0.1)

            typewriter(f"\nGold : {game['gold']}", style.YELLOW)
            i = input(f"\nPlease pick your choice (#,  type exit to leave) >>> ").strip()

            if i == "exit":
                break
            elif items[int(i) - 1] == "Level Up":
                if game['gold']>= item_costs["Level Up"]:
                    game["gold"] -= item_costs["Level Up"]
                    game["level"] += 1
                    typewriter(f"\nYou have leveled up to level {game['level']}!", style.GREEN)
                else:
                    typewriter(f"\nHow can you not afford this?", style.RED)
                    time.sleep(0.5)
                    typewriter("Please pay attention of ur gold next time.", style.RED)
            elif items[int(i) - 1] == "Pen":
                if game['gold'] >= item_costs["Pen"]:
                    game['gold'] -= item_costs["Pen"]
                    game['weapons'].append(pen)
                    typewriter("\nIf you lose this, then I will not be very happy :P", style.GREEN)
                    time.sleep(0.5)
                    typewriter("This Pen is my signature weapon", style.GREEN)
                else:
                    typewriter(f"\nPoor.", style.RED)
            elif items[int(i) - 1] in item_costs:
                if game['gold']>= item_costs[items[int(i) - 1]]:
                    game["gold"] -= item_costs[items[int(i) - 1]]
                    game["inventory"].append(items[int(i) - 1])
                    typewriter("\nPlease take care of this, it was quite expensive...", style.GREEN)
                else:
                    typewriter("\nWhy even try, I thought you kept count of taxes man :P", style.RED)
            else:
                typewriter("\nMate, you're meant to type it absolutely perfectly :(", style.RED)
                
            time.sleep(2)
            os.system('cls' if os.name == 'nt' else 'clear')

        bsvc += 1
    
    return game

#Noah, script made by noah
def cozycoder(game):
    global nsvc
    ty = lambda x: typewriter(x, style.YELLOW, post_delay=1)
    tg = lambda x: typewriter(x, style.GREEN, post_delay=1)
    tb = lambda x: typewriter(x, style.BLUE, post_delay=1)
    tr = lambda x: typewriter(x, style.RED, post_delay=1)

    nsvc += 1
    os.system('cls' if os.name == 'nt' else 'clear')

    # Shop inventory
    shop_items = {
        "Cube Sword": {"cost": 350, "type": "weapon", "stats": [200, 450]},
        "Defensive Shield": {"cost": 300, "type": "weapon", "stats": [25, 40]},
        "Magic Scroll": {"cost": 100, "type": "item"},
        "Mysterious Trinket": {"cost": 50, "type": "item"}
    }

    def shopping():
        while True:
            print("\nNoah's Shop:")
            for idx, (item, data) in enumerate(shop_items.items(), start=1):
                print(f" {idx}. {item}: {data['cost']} gold")
            print(" type 'exit' to leave Noah's shop.\n")
            typewriter("Weapon stats:", style.CYAN)
            print(" Cube Sword [200, 450]")
            print(" Defensive Shield [25, 40] (better counters + reduces damage)")
            
            choice = input("\nWhat would you like to buy? (#) >>> ").strip()
            if choice.lower() == "exit":
                tg("Thanks for shopping!")
                tg("cya!")
                break

            try:
                choice = int(choice) - 1
                if 0 <= choice < len(shop_items):
                    item_name = list(shop_items.keys())[choice]
                    data = list(shop_items.values())[choice]
                    if game["gold"] >= data["cost"]:
                        game["gold"] -= data["cost"]
                        if data["type"] == "weapon":
                            game["weapons"].append([item_name, *data["stats"]])
                            if item_name == "Cube Sword":
                                tg("This is my greatest weapon, please take care of it.")
                            else:
                                tg("Not sure if you'd call this a weapon, but it'll help!")
                        else:
                            game["inventory"].append(item_name)
                            if item_name == "Magic Scroll":
                                tg("I got much better prices than that shopkeeper guy.")
                            else:
                                tg("No idea what this is, maybe Krivi would know...")
                    else:
                        if item_name == "Cube Sword":
                            tr("Dude. You need more money before I can give this to you.")
                        elif item_name == "Defensive Shield":
                            tr("Hah! Guess you're too broke for defense.")
                        elif item_name == "Magic Scroll":
                            tr("Dude this is literally the cheaper version of the original???")
                        else:
                            tr("DUDE IT'S 50 GOLD!!!!! HOW CAN YOU NOT AFFORD THIS???? just pay")
                else:
                    tr("Invalid choice.")
            except ValueError:
                tr("Invalid input, enter a number.")

    # === Visit 1 ===
    if nsvc == 1: 
        tg("This is Noah's thing, he was my first alpha tester and made this script so don't judge me or noah 🫡🫡🫡🫡🫡🫡🫡🫡🫡🫡. Thank you to noah for contributing time and effort into this game, enjoy!")
        time.sleep(2)
        os.system('cls' if os.name == 'nt' else 'clear')
        ty("hmm...")
        ty("where to go...")
        tg("Oh!")
        tg("hello adventurer!")
        tg("what brings you here today?")
        # Treasure/XP flavor
        print(" <treasure>, <experience points>")
        tg("sweet!")
        tg("well, I'm Noah, this game's alpha tester, and I came here on a quest with my friend Krivi, but we got split up.")
        tg("do you know krvi?")
        if input(" (y/n) > ").strip().lower() == "y":
            tg("ah, I see.")
            tg("well you probably already know that he lost his hat. can you go bring it back to him?")
            if "LaDoodle's Hat" not in game["artifacts"]:
                game["artifacts"].append("LaDoodle's Hat")
                print(" [+1 hat]")
            tg("Thanks! come back to me when you give it to him.")
        else:
            tg("well krivi's the creator of this game, so he's basically god.")
            tg("He dropped his hat when we split up.")
            tg("can you give it back to him?")
            if "LaDoodle's Hat" not in game["artifacts"]:
                game["artifacts"].append("LaDoodle's Hat")
                print(" [+1 hat]")
            tg("great, come back when you give it back.")
            tg("oh.")
            tg("you can't find him, can you?")
            tg("well, here's a map.")
            if "Doodle Map" not in game["inventory"]:
                game["inventory"].append("Doodle Map")
                print(" [+1 doodle map]")
        tg("so, while you're here, would you like to do some shopping?")
        if input(" (y/n) > ").strip().lower() == "y":
            shopping()

    # === Visit 2 ===
    elif nsvc == 2:
        tg("woah what.")
        tg("I was looting a chest and now i'm… here?")
        tg("oh, it's you again.")
        tg("did you give krivi his hat?")
        if input(" (y/n) > ").strip().lower() == "y":
            tg("great! i'm sure he'll appreciate it.")
            print(" +500 gold")
            game["gold"] += 500
        else:
            tr("why not?!?!")
            tg("uhh, just bring it to him next time.")
        tg("anyway, wanna do some shopping?")
        if input(" (y/n) > ").strip().lower() == "y":
            shopping()

    # === Visit 3 ===
    elif nsvc == 3:
        tg("wha…")
        tg("where am I???")
        tg("why does this keep happening?")
        if "LaDoodle's Hat" in game["artifacts"]:
            tg("did you give krivi the hat yet?")
            if input(" (y/n) > ").strip().lower() == "y":
                tg("finally, okay here's some gold.")
                print(" +300 gold")
                game["gold"] += 300
            else:
                tr("you have one chance remaining. give him the hat or face the consequences")
        tg("now, shopping?")
        if input(" (y/n) > ").strip().lower() == "y":
            shopping()
        tg("i hope you found what you were looking for...")

    # === Visit 4+ ===
    else:
        tg("AH-WUH-HUH????")
        tg("my GOD")
        tg("stop teleporting me here.")
        tg("did you give krivi the hat?")
        if input(" (y/n) > ").strip().lower() == "y":
            tg("finally... please just do what i ask the first time next time, okay?")
            print(" +150 gold")
            game["gold"] += 150
        else:
            print("\nThe ROARING KNIGHT appeared!")
            tr(" (Scripted battle: takes 1 dmg per hit, deals 999999999 dmg. You lose.) ")
            game["hp"] = 0
        tg("okay, now do you want to shop again?")
        if input(" (y/n) > ").strip().lower() == "y":
            shopping()
        tg("okay... hope you found what you wanted...")
        tg("if not...")
        tg("just please don't come back here.")
        tg("i'm not threatening you, but just please don't.")

    return game

# Equip a weapon from the arsenal
def equip(game):
    print(f"\n{style.BLUE}Which weapon would you like to equip?{style.RESET}")

    print()
    for idx, (name, min_dmg, max_dmg) in enumerate(game["weapons"], start=1):
        print(f"    {idx}: {name} {min_dmg} - {max_dmg} dmg")
        time.sleep(0.1)
    
    try:
        game["equipped"] = int(input("\nChoose a weapon (#) >>> ")) - 1
    except Exception as e:
        print(f"\n{style.BOLD}{style.RED}ERROR: {style.RESET}{style.RED}{e}{style.RESET}")

    typewriter(f"You have equipped the {game['weapons'][game['equipped']][0]}", style.BOLD)
    return game

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

    time.sleep(4)
    os.system('cls' if os.name == 'nt' else 'clear')
    return

# TheDoodleShop™
def shop(game):
    # Format (name, cost, level)

    items = [
        # Level 1
        ("Small Health Potion", 20, 1),
        ("Wooden Sword", 35, 1),

        # Level 2 
        ("Medium Health Potion", 50, 2),
        ("Stone Axe", 60, 2),

        # Level 3
        ("Large Health Potion", 200, 3),
        ("Beginner's Scroll", 200, 3),

        # Level 4
        ("Shadow Dagger", 250, 4),
        ("Assassin's Cloak", 300, 4),
        ("Iron Sword", 350, 4),

        # Level 5
        ("Phoenix Feather", 400, 5),
        ("Elite Health Potion", 400, 5),

        # Level 6
        ("Revolver", 450, 6),
        ("Secret Map", 1500, 6),

        # Level 7
        ("Assassin Build Scroll", 550, 7),
        ("Legendary Health Potion", 550, 7),

        # Level 10
        ("Divine Health Potion", 1000, 10),
        ("Reaper's Scythe", 1000, 10),

        # Level 12
        ("Mystic Cloak", 1200, 12),
        ("Beginner Stat Buff", 750, 12),

        # Level 15
        ("Advanced Stat Buff", 1000, 15),
        ("Ultimate Magic Scroll", 1500, 15)
    ]

    # Format : [name, min_damage, max_damage]
    weapon_stats = {
        "Wooden Sword": ["Wooden Sword", 15, 30],
        "Stone Axe": ["Stone Axe", 20, 40],
        "Iron Sword": ["Iron Sword", 45, 60],
        "Revolver": ["Revolver", 100, 120],
        "Reaper's Scythe": ["Reaper's Scythe", 150, 300]
    }

    current_items = [item for item in items if item[2] <= game["level"]]
    current_weapon_stats = {name: stats for name, stats in weapon_stats.items() if stats[0] in [item[0] for item in current_items]}

    print()
    typewriter("Welcome to TheDoodleShop™!", style.BOLD)
    typewriter("You can find an assortment of items and weapons here.", style.BOLD)
    typewriter("Feel free to browse and make a purchase!", style.BOLD)
    typewriter("You will find more items in this shop the more you level up!", style.BOLD)
    print()

    typewriter("Available Items: ", style.BOLD)
    for idx, item in enumerate(current_items, start=1):
        typewriter(f" {idx}. {item[0]}: {item[1]} gold (Level {item[2]} Product)", delay=0.0075, post_delay=0.1)
    print()

    typewriter("Weapon Stats", style.BOLD)
    for name, stats in current_weapon_stats.items():
        typewriter(f" {name}: {stats[1]} - {stats[2]} dmg", delay=0.0075, post_delay=0.1)

    print()

    typewriter(f"Gold : {game['gold']}", style.YELLOW)
    try:
        choice = int(input(f"{style.CYAN}Enter the number of the item you want to buy (#) >>> {style.RESET}").strip())

        if 1 <= int(choice) <= len(current_items) + 1:
            if items[choice - 1][0] in weapon_stats:
                weapon = weapon_stats[items[choice - 1][0]]
                if game["gold"] >= items[choice - 1][1]:
                    game["gold"] -= items[choice - 1][1]
                    game["weapons"].append(weapon)
                    typewriter(f"You have purchased {weapon[0]}!", style.GREEN)
                else:
                    typewriter(f"You do not have enough gold to purchase {weapon[0]}.", style.RED)
            else:
                item = current_items[int(choice) - 1]

                count = int(input(" How many would you like to purchase? (0 for none) >>> ").strip())

                if game["gold"] >= item[1] * count:
                    game["gold"] -= item[1] * count
                    for _ in range(count):
                        game["inventory"].append(item[0])
                    typewriter(f"You have purchased {count} {item[0]}(s)!", style.GREEN)
                else:
                    typewriter(f"You do not have enough gold to purchase {count} {item[0]}(s).", style.RED)
        else:
            typewriter("Invalid choice. Please try again.", style.RED)
    except ValueError:
        typewriter("Invalid input. Please enter a number.", style.RED)

    

    return game

def level_up_check(game):

    while game["xp"] >= 200 * game["level"]:
        game["xp"] -= 200 * game["level"]
        game["level"] += 1
        game["max_hp"] += round(game["max_hp"] * 0.2)
        game["hp"] = game["max_hp"]
        print()
        typewriter(f"Congratulations! You leveled up to level {game['level']}!", style.GREEN, delay=0.005)
        typewriter(f"Your maximum HP has increased to {game['max_hp']}!", style.GREEN, delay=0.005)
        typewriter(f"You have also regened to max hp", style.GREEN, delay=0.005)

        print()
        stats = [(typ, lvl) for typ, lvl in game['skill_set'].items()]

        for idx, (skill, level) in enumerate(stats, start=1):
            print(f"{style.YELLOW}{idx}. {skill.capitalize()}: {level}{style.RESET}")
            time.sleep(0.1)

        
        while True:
            try:
                choice = int(input(f"\n{style.CYAN}Choose a skill to improve (#) >>> {style.RESET}").strip())
                if 1 <= choice <= len(stats):
                    stat = stats[choice - 1]
                    game['skill_set'][stats[choice - 1][0]] += 1
                    typewriter(f"Your {stat[0]} has been improved!", style.GREEN)
                    break

                else:
                    print(f"{style.RED}Invalid choice. Please try again.{style.RESET}")
            except Exception as e:
                print(f"{style.RED}Invalid input. Please enter a number.{style.RESET}")
                continue

    return game

# Main game loop
def main():
    os.system('cls' if os.name == 'nt' else 'clear')

    typewriter("Welcome to DOODLE R.P.G.", style.MAGENTA)
    print()
    typewriter("DOODLE R.P.G. is a game where you can explore the world, fight monsters, and level up your character.\nYou will encounter monsters and enemies, explore and piece together the mysterious lore behind all of the fighting.\nYou Enter the command in the command line, and h is for help on commands, when you win, you will encounter a suprise.\nYou can save and load via a json file which you can name. you can overwrite existing files and load your save.\nThank you for considering DOODLE R.P.G. AND ENJOY!", delay=0.005)

    game = json_load() if input(f"\n{style.CYAN} Would you like to load a game from json file? (Y/N) >>>{style.RESET} ").strip().upper() == "Y" else init_new_game()
    if not game['autosave']['enabled']:
        game['autosave']['enabled'] = True if input(f"{style.CYAN} Would you like to enable autosave? (Y/N) >>> {style.RESET}").strip().upper() == "Y" else False
        game['autosave']['filename'] = input(f"{style.CYAN} Enter a filename for autosave >>> {style.RESET}").strip() if game['autosave']['enabled'] else None
    time.sleep(2)

    while True:
        try:
            backup_game = game
            os.system('cls' if os.name == 'nt' else 'clear')

            s = input(f"{style.BOLD}{style.BLUE}Enter Command (h for help) >>>{style.RESET} ")

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
        autosave (or a) - toggle autosave on/off
        {style.RESET}""")
            elif s in ["quit", "q"]:
                quit_game(game)
                return
            elif s in ["die"] and game["cheat_mode"]:
                print(f"{style.RED} > You have chosen to commit suicide. Game over!{style.RESET}")
                game["hp"] = 0
            elif s in ["win"] and game["cheat_mode"]:
                print(f"\n {style.GREEN}> Win{style.RESET}")
                game["level"] = 25
            elif s in ["addxp"] and game["cheat_mode"]:
                amount = input(f"{style.CYAN}Enter XP amount to add: {style.RESET}")
                if amount.isdigit():
                    game["xp"] += int(amount)
                    typewriter(f"Added {amount} XP!", style.GREEN)
                else:
                    typewriter(f"Invalid input. Please enter a number.", style.RED)
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
                game = use_item(game, False)
            elif s in ["equip", "eq"]:
                game = equip(game)
            elif s in ["autosave", "a"]:
                game["autosave"]["enabled"] = not game["autosave"]["enabled"]
                print(f"{style.YELLOW} > Autosave {'enabled' if game['autosave']['enabled'] else 'disabled'}{style.RESET}")
            else:
                print(f"{style.RED} > Invalid command, type help (or h) to list possible commands{style.RESET}")

            if game['autosave']['enabled']: json_save(game)

            if game == None:
                typewriter("An error has occurred during the process, Don't panic, resorting to backup save.", style.RED)
                game = backup_game

            game, state = check_game_over(game)
            if state:
                if game["autosave"]["enabled"]:
                    game['hp'] = 1
                    game['level'] = game['level'] // 2
                    game['xp'] = 0
                    game['gold'] = game['gold'] // 10
                    game['inventory'] = []
                    game['used_items'] = []
                    game['skill_set'] = {
                        "strength": 0,
                        "agility": 0,
                        "luck": 0,
                        "accuracy": 0,
                        "defence": 0
                    }
                    json_save(game)
                    typewriter("Your save file has been wiped, but you still have some stuff load your new save and see.", style.RED)
                input("Press Enter to continue > ")
                os.system('cls' if os.name == 'nt' else 'clear')
                if input(f"{style.YELLOW} Would you like to restart ? (Y/N) >>> {style.RESET}").strip().upper() == "Y":
                    return main()
                else:
                    return
                
            game = level_up_check(game)
            
            input("Press Enter to continue > ")
        except KeyboardInterrupt:
            print(f"{style.RED}\n > Game interrupted by user. Try 'QUIT' to exit.{style.RESET}")
            input("Press Enter to continue > ")
        # except Exception as e:
        #     print(f"{style.RED}\n > An error occurred: {e}{style.RESET}")
        #     input("Press Enter to continue > ")

# Start the game
if __name__ == "__main__":
    main()
