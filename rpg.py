"""

Main/Base Game Complete!
Move onto additions.

"""

import time, random as r, os, json, math

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
            ["Fists", 10, 20]
        ],     
        "equipped": 0,      
        "artifacts": [], 
        "cheat_mode": False,
        "xp": 0
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
        "xp": 0
    }

# Save game state to JSON file
def json_save(game):
    file_name = input(f"{style.BLUE}{style.BOLD}Save filename >>>{style.RESET} ").strip()
    file_name = file_name if file_name.endswith(".json") else file_name+".json"

    if file_name == '':
        print(f' {style.RED} > Invalid filename (either it already exists or blank) try again')
        json_save(game)
        return
    elif os.path.exists(file_name):
        if input(" Are you sure you want to overwrite this file? (y/n) >>> ").strip().lower() == 'y':
            try:
                with open(file_name, 'w')as f:
                    json.dump(game, f)
                print(f"\n{style.GREEN}Game saved to {file_name}{style.RESET}")
            except Exception as e:
                print(f"{style.RED} > Unable to write file with error: {e}{style.RESET}")
        else:
            return
    else:
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
                "cheat_mode": bool,
                "xp": int
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
        return True
    elif game["level"] == 25:
        print(f"\n{style.BOLD}{style.UNDERLINE}{style.GREEN}CONGRATS!{style.RESET} {style.GREEN}You just won the game and earned {style.BOLD}{style.MAGENTA}Drago's Egg{style.RESET}")
        game["artifacts"].append("Drago's Egg")
        return True
    else:
        return False

# To use an item
def use_item(game):
    
    if game["inventory"]:
        for i, items in enumerate(game["inventory"], start=1):
            print(f"{i}. {items}")
            time.sleep(0.1)

        try:
            item = game["inventory"][int(input(f"{style.BOLD}Which item would you like to use (#){style.RESET} >>> ")) - 1]
        except (IndexError, ValueError) as e:
            typewriter("Invalid item selection.", style.RED)
            return game

        # Mystic Cloak: buffs HP and all weapons, then removes itself
        if item == 'Mystic Cloak':
            game["hp"] += 20
            game["max_hp"] += 20
            for i in range(len(game['weapons'])):
                game['weapons'][i][1] += 20
                game['weapons'][i][2] += 20

            game["inventory"].remove(item)
            typewriter(f"You used a {item} and gained 20 hp to your max hp and buffed all your weapons!", style.GREEN)
            time.sleep(0.5)
            typewriter("🤔 Your cloak mysteriously dissipated and got absorbed into you and your items...", style.YELLOW)
            print()

        # Large Health Potion: heals 50 HP
        elif item == 'Large Health Potion':
            if game["hp"] + 50 > game["max_hp"]:
                game["hp"] = game["max_hp"]
            else:
                game["hp"] += 50
            game["inventory"].remove(item)
            typewriter(f"You used a {item} and gained 50 hp!", style.GREEN)

        # Small Health Potion: heals 20 HP
        elif item == 'Small Health Potion':
            if game["hp"] + 20 > game["max_hp"]:
                game["hp"] = game["max_hp"]
            else:
                game["hp"] += 20
            game["inventory"].remove(item)
            typewriter(f"You used a {item} and gained 20 hp!", style.GREEN)

        # Elixir of Fortitude: heals 100 HP
        elif item == 'Elixir of Fortitude':
            if game["hp"] + 100 > game["max_hp"]:
                game["hp"] = game["max_hp"]
            else:
                game["hp"] += 100
            game["inventory"].remove(item)
            typewriter(f"You used an {item} and gained 100 hp!", style.GREEN)

        # Phoenix Feather: adds a spell weapon if not already known
        elif item == 'Phoenix Feather':
            spell = ["Phoenix's Flare Blitz", 100, 150]
            if not spell in game["weapons"]:
                game["weapons"].append(spell)
                typewriter(f"You used a {item} and learned a new spell: {spell[0]}!", style.GREEN)
                time.sleep(0.5)
                typewriter("Equip spell through 'Equip' command", style.YELLOW)
            else:
                typewriter(f"You already know the spell: {spell[0]}", style.YELLOW)

            game["inventory"].remove(item)
            typewriter('The feather has been used...', style.YELLOW)
            
        # Magic Scroll: grants a random spell weapon if not already known
        elif item == 'Magic Scroll':
            spells = [["Arcane Blast", 80, 120], ["Electrify", 60, 100], ["Frostbite", 70, 110], ["Fireball", 90, 130], ["Meteor Shower", 100, 150], ["Tornado Blast", 85, 125]]

            spell = r.choice(spells)
            if spell not in game["weapons"]:
                game["weapons"].append(spell)
                typewriter(f"You used a {item} and learned a new spell: {spell[0]}!", style.GREEN)
                time.sleep(0.5)
                typewriter("Equip spell through 'Equip' command", style.YELLOW)
            else:
                typewriter(f"You already know the spell: {spell[0]}", style.YELLOW)
                

            game["inventory"].remove(item)
            typewriter('The scroll has been used...', style.YELLOW)

        elif item == 'Infinity Heal':
            game['hp'] = game['max_hp']
            game['inventory'].remove(item)
            typewriter("You have just recovered all of your hp with your Infinity Heal", style.GREEN)
        
        elif item == "Infinity Buff":
            for w in range(0,len(game["weapons"])):
                game["weapons"][w][1] += 100
                game["weapons"][w][2] += 100
            game["inventory"].remove(item)
            typewriter("You used an Infinity Buff and increased all your weapon's damage!", style.GREEN)

        elif item == "Secret Map":
            if mi:
                typewriter("You used the Secret Map!", style.GREEN)
                time.sleep(0.5)
                typewriter("It reveals a hidden path...", style.GREEN)
                time.sleep(0.5)
            else:
                typewriter("You don't seem to know how to use this...", style.RED)

        # Default: item cannot be used in battle
        else:
            typewriter(f"You can't use {item} right now!", style.RED)
        
        return game
    else:
        typewriter("You have no items to use!", style.RED)
        return game

def LaDoodle_dialouge(game):
    global nsvc, x, bsvc, y
    if bsvc == 0:
        typewriter("...", style.YELLOW)
        time.sleep(1)
        typewriter("I see you're a traveler. What brings you here?", style.YELLOW)
        time.sleep(0.5)
        typewriter("Oh, I forgot, ur playing the game",style.GREEN)
        time.sleep(0.5)
        typewriter("Weeeelll.", style.GREEN)
        time.sleep(0.25)
        typewriter("I'm Krivi's avatar, LaDoodleInTheHat.", style.GREEN)
        time.sleep(0.5)
        typewriter("Well without the hat rlly, cause I lost it.", style.YELLOW)
        time.sleep(0.5)
        typewriter("Have you seen Noah?", style.YELLOW)
        if input(" (y/n) > ").strip().lower() == "y":
            if nsvc > 0:
                typewriter("Oh you have!", style.GREEN)
                time.sleep(0.5)
                typewriter("That's great to hear!", style.GREEN)
                time.sleep(0.5)
                typewriter("Then you must have my hat!", style.GREEN)
                if input(" (y/n) > ").strip().lower() == "y":
                    if "LaDoodle's Hat" in game['artifacts']:
                        typewriter("NIIIICCCEEEE", style.GREEN)
                        time.sleep(0.5)
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

                time.sleep(0.5)
                typewriter("He's been missing for a while now...", style.YELLOW)
                time.sleep(0.5)
                typewriter("And I think he has my hat...", style.YELLOW)
                time.sleep(0.5)
                if not ('Secret Map' in game['inventory']):
                    typewriter("I have this map that might help you find him.", style.YELLOW)
                    time.sleep(0.1)
                    print(f" {style.BOLD}+ Secret Map {style.RESET} ")
                    time.sleep(0.1)
                    game["inventory"].append("Secret Map")
                    typewriter("Use it to find Noah and maybe my Hat", style.YELLOW)
                    time.sleep(0.5)
                    typewriter("It would be nice if you can get my hat back.", style.GREEN)
                elif 'Secret Map' in game['inventory']:
                    typewriter("I see you already have the map.", style.YELLOW)
                    time.sleep(0.5)
                    typewriter("Use it to find Noah and maybe my Hat", style.YELLOW)
                    time.sleep(0.5)
                    typewriter("It would be nice if you can get my hat back.", style.GREEN)

                x = True

        else:
            time.sleep(0.5)
            typewriter("He's been missing for a while now...", style.YELLOW)
            time.sleep(0.5)
            typewriter("And I think he has my hat...", style.YELLOW)
            time.sleep(0.5)
            if not ('Secret Map' in game['inventory']):
                typewriter("I have this map that might help you find him.", style.YELLOW)
                time.sleep(0.1)
                print(f" {style.BOLD}+ Secret Map {style.RESET} ")
                time.sleep(0.1)
                game["inventory"].append("Secret Map")
                typewriter("Use it to find Noah and maybe my Hat", style.YELLOW)
                time.sleep(0.5)
                typewriter("It would be nice if you can get my hat back.", style.GREEN)
            elif 'Secret Map' in game['inventory']:
                typewriter("I see you already have the map.", style.YELLOW)
                time.sleep(0.5)
                typewriter("Use it to find Noah and maybe my Hat", style.YELLOW)
                time.sleep(0.5)
                typewriter("It would be nice if you can get my hat back.", style.GREEN)

            x = True

        time.sleep(0.5)
        typewriter("Anyway, you can buy stuff from here", style.GREEN)
        time.sleep(0.5)
        typewriter("Pretty op stuff :)", style.GREEN)
        time.sleep(0.5)
        typewriter("Let's get shopping!", style.GREEN)

        mi = True

    elif bsvc == 1:
        typewriter("Welcome back my friend!", style.GREEN)
        time.sleep(0.5)
        if x:
            typewriter("Have you seen Noah?", style.YELLOW)
            time.sleep(0.5)
            typewriter("Yet?", style.YELLOW)
            if input(" (y/n) > ").strip().lower() == "y":
                if nsvc > 0:
                    typewriter("Oh finally!", style.GREEN)
                    time.sleep(0.5)
                    typewriter("That's great to hear!", style.GREEN)
                    time.sleep(0.5)
                    typewriter("Then you must have my hat!", style.GREEN)
                    if input(" (y/n) > ").strip().lower() == "y":
                        if "LaDoodle's Hat" in game['artifacts']:
                            typewriter("NIIIICCCEEEE", style.GREEN)
                            time.sleep(0.5)
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
        typewriter("You know the drill.")
        time.sleep(0.5)
        typewriter("Let's get shopping!", style.GREEN)

    if bsvc >= 2 :
        if nsvc > 0 and not y:
            typewriter("You saw Noah? That's incredible!", style.GREEN)
            time.sleep(0.5)
            typewriter("He's been missing for ages... I was starting to worry.", style.YELLOW)
            time.sleep(0.5)
            typewriter("Did he seem alright? What was he up to?", style.YELLOW)
            time.sleep(0.5)
            typewriter("If you hear anything interesting, let me know. He's a good friend.", style.GREEN)
            time.sleep(0.5)
            typewriter("I see you have my hat", style.GREEN)
            time.sleep(0.5) 
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

        typewriter("Same stuff as before my adventurer friend!", style.GREEN)
        time.sleep(0.5)
        typewriter("Check them out!", style.GREEN)

    return game

# Handle random encounters (monster, treasure, shopkeeper)
def random_encounter(game):
    global bsvc
    spinner(1, 0.1)

    # Monster format: [name, hp, damage, reward, chance, xp drop]
    # The chance value is cumulative; the first monster is picked if i <= chance, next if i <= chance, etc.
    # Each level has progressively harder monsters, higher rewards and xp drops.
    # Player starts with 100 HP, weapon damage 10-20, and no armor.
    # Let's balance early monsters to be a real threat but not overwhelming.
    # Increase monster HP and damage, and XP/reward for challenge.
    # Adjusted for better balance: monsters scale more smoothly, rewards and XP are more consistent.
    monsters = [
        # Level 1 (Player: HP 100, Weapon 10-20)
        [
            ["Slime", 60, 18, 30, 10, 35],
            ["Rat", 65, 20, 32, 20, 38],
            ["Goblin", 70, 22, 36, 30, 40],
            ["Bat", 58, 17, 28, 40, 32],
            ["Wild Mouse", 62, 19, 30, 50, 33],
            ["Tiny Spider", 55, 16, 27, 60, 30],
            ["Lost Chick", 53, 15, 25, 70, 28],
            ["Baby Snake", 57, 18, 29, 80, 31],
            ["Mischievous Pixie", 60, 19, 31, 90, 34],
            ["Angry Squirrel", 56, 17, 27, 100, 30],
            ["Bandit Initiate", 68, 21, 38, 110, 42],
            ["Forest Beetle", 59, 18, 29, 120, 32],
        ],
        # Level 2 (Player: HP ~120, Weapon 10-20 or better)
        [
            ["Wolf", 85, 24, 40, 10, 45],
            ["Bandit", 90, 26, 44, 20, 48],
            ["Goblin Brute", 95, 28, 48, 30, 52],
            ["Snake", 80, 22, 36, 40, 40],
            ["Wild Dog", 88, 23, 38, 50, 42],
            ["Forest Spider", 86, 21, 34, 60, 39],
            ["Bandit Scout", 92, 25, 42, 70, 47],
            ["Angry Crow", 78, 20, 32, 80, 36],
            ["Wild Cat", 85, 23, 38, 90, 44],
            ["Mischievous Goblin", 83, 22, 35, 100, 41],
            ["Bandit Slinger", 97, 27, 50, 110, 54],
            ["Forest Snake", 87, 24, 39, 120, 43],
        ],
        # Level 3
        [
            ["Skeleton", 65, 20, 40, 10, 50],
            ["Wild Boar", 80, 22, 45, 20, 55],
            ["Orc", 100, 25, 50, 30, 60],
            ["Zombie Dog", 70, 18, 35, 40, 45],
            ["Bandit Archer", 85, 21, 38, 50, 48],
            ["Ghoul", 75, 19, 36, 60, 47],
            ["Forest Wolf", 78, 20, 39, 70, 52],
            ["Wild Ram", 82, 21, 41, 80, 54],
            ["Cave Bat", 68, 17, 33, 90, 43],
            ["Angry Boar", 72, 18, 37, 100, 46],
        ],
        # Level 4
        [
            ["Zombie", 110, 28, 55, 10, 65],
            ["Bandit Leader", 130, 32, 60, 20, 70],
            ["Orc Warrior", 150, 36, 70, 30, 80],
            ["Ghoul", 120, 30, 50, 40, 60],
            ["Wild Bear", 140, 34, 65, 50, 75],
            ["Forest Troll", 125, 31, 58, 60, 68],
            ["Bandit Swordsman", 135, 33, 62, 70, 72],
            ["Cave Spider", 115, 29, 53, 80, 63],
            ["Angry Bear", 128, 32, 59, 90, 69],
            ["Wild Lynx", 118, 28, 54, 100, 64],
        ],
        # Level 5
        [
            ["Giant Spider", 160, 40, 80, 10, 90],
            ["Ghoul", 180, 44, 90, 20, 100],
            ["Troll", 200, 48, 100, 30, 110],
            ["Swamp Lizard", 170, 42, 85, 40, 95],
            ["Bandit Mage", 190, 46, 95, 50, 105],
            ["Forest Ogre", 175, 43, 88, 60, 98],
            ["Wild Crocodile", 185, 45, 92, 70, 102],
            ["Cave Troll", 165, 41, 83, 80, 93],
            ["Angry Troll", 178, 44, 89, 90, 99],
            ["Swamp Rat", 168, 40, 81, 100, 91],
        ],
        # Level 6
        [
            ["Dire Wolf", 210, 52, 110, 10, 120],
            ["Dark Mage", 230, 56, 120, 20, 130],
            ["Ogre", 250, 60, 130, 30, 140],
            ["Vampire", 220, 54, 115, 40, 125],
            ["Forest Troll", 240, 58, 125, 50, 135],
            ["Bandit Captain", 225, 55, 118, 60, 128],
            ["Cave Ogre", 235, 57, 122, 70, 132],
            ["Wild Panther", 215, 53, 113, 80, 123],
            ["Angry Ogre", 228, 56, 119, 90, 129],
            ["Dark Sorcerer", 218, 52, 111, 100, 121],
        ],
        # Level 7
        [
            ["Vampire Bat", 260, 64, 140, 10, 150],
            ["Wraith", 280, 68, 150, 20, 160],
            ["Minotaur", 300, 72, 160, 30, 170],
            ["Specter", 270, 66, 145, 40, 155],
            ["Cave Ogre", 290, 70, 155, 50, 165],
            ["Bandit Berserker", 275, 67, 148, 60, 158],
            ["Wild Tiger", 285, 69, 152, 70, 162],
            ["Angry Minotaur", 265, 65, 143, 80, 153],
            ["Dark Wraith", 278, 68, 149, 90, 159],
            ["Spectral Bat", 268, 64, 141, 100, 151],
        ],
        # Level 8
        [
            ["Fire Elemental", 320, 76, 170, 10, 180],
            ["Ice Golem", 340, 80, 180, 20, 190],
            ["Werewolf", 360, 84, 190, 30, 200],
            ["Frost Bat", 330, 78, 175, 40, 185],
            ["Bandit Captain", 350, 82, 185, 50, 195],
            ["Forest Werewolf", 335, 79, 178, 60, 188],
            ["Wild Rhino", 345, 81, 182, 70, 192],
            ["Cave Golem", 325, 77, 173, 80, 183],
            ["Angry Golem", 338, 80, 179, 90, 189],
            ["Ice Elemental", 328, 76, 171, 100, 181],
        ],
        # Level 9
        [
            ["Stone Guardian", 380, 88, 200, 10, 210],
            ["Necromancer", 400, 92, 210, 20, 220],
            ["Cyclops", 420, 96, 220, 30, 230],
            ["Shadow Beast", 390, 90, 205, 40, 215],
            ["Forest Spirit", 410, 94, 215, 50, 225],
            ["Bandit Sorcerer", 395, 91, 208, 60, 218],
            ["Wild Elephant", 405, 93, 212, 70, 222],
            ["Cave Cyclops", 385, 89, 203, 80, 213],
            ["Angry Cyclops", 398, 92, 209, 90, 219],
            ["Shadow Elemental", 388, 88, 201, 100, 211],
        ],
        # Level 10
        [
            ["Thunder Lizard", 440, 100, 230, 10, 240],
            ["Shadow Assassin", 460, 104, 240, 20, 250],
            ["Giant", 480, 108, 250, 30, 260],
            ["Storm Hawk", 450, 102, 235, 40, 245],
            ["Bandit King", 470, 106, 245, 50, 255],
            ["Forest Giant", 455, 103, 238, 60, 248],
            ["Wild Buffalo", 465, 105, 242, 70, 252],
            ["Cave Giant", 445, 101, 233, 80, 243],
            ["Angry Giant", 458, 104, 239, 90, 249],
            ["Thunder Elemental", 448, 100, 231, 100, 241],
        ],
        # Level 11
        [
            ["Hellhound", 500, 112, 260, 10, 270],
            ["Specter", 520, 116, 270, 20, 280],
            ["Demon", 540, 120, 280, 30, 290],
            ["Dark Knight", 510, 114, 265, 40, 275],
            ["Ancient Zombie", 530, 118, 275, 50, 285],
            ["Forest Demon", 515, 115, 268, 60, 278],
            ["Wild Mammoth", 525, 117, 272, 70, 282],
            ["Cave Demon", 505, 113, 263, 80, 273],
            ["Angry Demon", 518, 116, 269, 90, 279],
            ["Spectral Knight", 508, 112, 261, 100, 271],
        ],
        # Level 12
        [
            ["Forest Spirit", 560, 124, 290, 10, 300],
            ["Lich", 580, 128, 300, 20, 310],
            ["Golem King", 600, 132, 310, 30, 320],
            ["Sand Worm", 570, 126, 295, 40, 305],
            ["Thunder Hawk", 590, 130, 305, 50, 315],
            ["Forest Lich", 575, 127, 298, 60, 308],
            ["Wild Gorilla", 585, 129, 302, 70, 312],
            ["Cave Lich", 565, 125, 293, 80, 303],
            ["Angry Lich", 578, 128, 299, 90, 309],
            ["Sand Elemental", 568, 124, 291, 100, 301],
        ],
        # Level 13
        [
            ["Hydra", 620, 136, 320, 10, 330],
        ],
        # Level 21
        [
            ["Shadow Dragon", 1100, 232, 620, 15, 630],
            ["Archdemon", 1120, 236, 630, 35, 640],
            ["Elder Titan", 1140, 240, 640, 55, 650],
            ["Frost Phoenix", 1110, 234, 625, 75, 635],
            ["Chaos Lord", 1130, 238, 635, 100, 645],
        ],
        # Level 22
        [
            ["Frost Phoenix", 1160, 244, 660, 15, 670],
            ["Chaos Lord", 1180, 248, 670, 35, 680],
            ["Ancient Colossus", 1200, 252, 680, 55, 690],
            ["Solar Serpent", 1170, 246, 665, 75, 675],
            ["Void Titan", 1190, 250, 675, 100, 685],
        ],
        # Level 23
        [
            ["Solar Serpent", 1220, 256, 700, 15, 710],
            ["Void Titan", 1240, 260, 710, 35, 720],
            ["Elder Dragon", 1260, 264, 720, 55, 730],
            ["Star Guardian", 1230, 258, 705, 75, 715],
            ["Time Wraith", 1250, 262, 715, 100, 725],
        ],
        # Level 24
        [
            ["Star Guardian", 1280, 268, 740, 15, 750],
            ["Time Wraith", 1300, 272, 750, 35, 760],
            ["Cosmic Leviathan", 1320, 276, 760, 55, 770],
            ["Celestial Hydra", 1290, 270, 745, 75, 755],
            ["Ancient Phoenix", 1310, 274, 755, 100, 765],
        ],

    ]

    # Adjust monster chances based on level
    
    try:
        i = r.randint(0, 100) if not game['cheat_mode'] else int(input("Monster : (0-79), Treasure : (80-99), Shopkeeper : (100) >>> "))
    except Exception as e:
        typewriter("Invalid input! Defaulting to normal encounter.", style.RED)
        i = r.randint(0, 100)

    if i <= 79 - 2*game['level']:
        # Monster fight
        i = r.randint(0, 100)
        for monster in monsters[game['level'] - 1]:
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
                xp_drop = monster[5]

                # Battle loop
                while monster_hp > 0 and game["hp"] > 0:
                    qu = input(f"\n{style.BOLD}What would you like to do (run/attack/counter/useItem) >>> {style.RESET}")
                    print()
                    dmg = r.randint(player_weapon[1], player_weapon[2])
                    mdmg = r.randint(int(monster_damage*0.7), monster_damage)
                    os.system('cls' if os.name == 'nt' else 'clear')

                    if qu == "run":
                        if r.randint(0, 100) < 75 - 3*game['level']:
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
                        if r.randint(0, 100) <= 75 - 3*game['level']:
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
                    typewriter(f"You gain {xp_drop} XP!", style.GREEN)
                    game["gold"] += reward_gold
                    game["xp"] += xp_drop

                time.sleep(3)
                return game           

    elif i <= 99 - 2*game['level']:
        # Treasure Chest Encounter
        typewriter("You found a mysterious treasure chest!", style.YELLOW)
        spinner(1, 0.1)
        reward_type = r.choices(["gold", "item"], weights=[70, 30])[0]
        if reward_type == "gold":
            gold_found = r.randint(30, 120) + game["level"] * 20
            typewriter(f"You open the chest and find {gold_found} gold!", style.GREEN)
            game["gold"] += gold_found
        else:
            items = [
                "Small Health Potion",
                "Large Health Potion",
                "Magic Scroll",
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
            weapon_stats = {
                "Iron Sword": ["Iron Sword", 5, 10],
                "Steel Axe": ["Steel Axe", 8, 16],
                "Enchanted Dagger": ["Enchanted Dagger", 4, 14],
                "(Totally) Mjölnir": ["(Totally) Mjölnir", 100, 220]
            }

            item = r.choice(items)

            # Check if item is a weapon
            if item in weapon_stats:
                # Only add if not already owned
                if not item in game["weapons"]:
                    game["weapons"].append(weapon_stats[item])
                    typewriter(f"You found a {item}! (Damage {item[1]}-{item[2]})", style.CYAN)
                else:
                    typewriter(f"You found a {item}, but you already have one. You sell it for 50 gold.", style.YELLOW)
                    game["gold"] += 50
            
            # Check if item is an artifact
            elif item == 'Shadow Amulet':
                if not item in game['artifacts']:
                    game['artifacts'].append(item)
                    typewriter(f"You found a {item}!", style.CYAN)
                else:
                    typewriter(f"You found a {item}, but you already have one. It magicly turns into 50 gold.", style.YELLOW)
                    game["gold"] += 50
            
            # Otherwise, add to inventory
            else:
                game["inventory"].append(item)
                typewriter(f"You found a {item}!", style.CYAN)
        
        return game
    
    elif i <= 100:
        # Shopkeeper encounter

        game = LaDoodle_dialouge(game)

        pen = ["Pen", 999999999999999999999999999999999, 999999999999999999999999999999999999999999999999999999999999999999]
        
        while True:
            item_costs = {
                "Pen": 2000,
                "Infinity Heal": 300,
                "Infinity Buff" : 300,
                "Level Up": 300*game["level"]
            }
            for idx, (item, cost) in enumerate(item_costs.items(), start=1):
                print(f'{idx}. {item}: {cost} gold')
                time.sleep(0.1)

            typewriter(f"\nGold : {game['gold']}", style.YELLOW)
            i = input(f"\nPlease pick your choice (remember to type it perfectly, type exit to leave) >>> ").strip()

            if i == "exit":
                break
            elif i == "Level Up":
                if game['gold']>= item_costs["Level Up"]:
                    game["gold"] -= item_costs[i]
                    game["level"] += 1
                    typewriter(f"\nYou have leveled up to level {game['level']}!", style.GREEN)
                else:
                    typewriter(f"\nHow can you not afford this?", style.RED)
                    time.sleep(0.5)
                    typewriter("It literally says 'Level Up' in the name", style.RED)
                    time.sleep(0.5)
                    typewriter("Please pay attention of ur gold next time.", style.RED)
            elif i == "Pen":
                if game['gold'] >= item_costs["Pen"]:
                    game['gold'] -= item_costs[i]
                    game['weapons'].append(pen)
                    typewriter("\nIf you lose this, then I will not be very happy :P", style.GREEN)
                    time.sleep(0.5)
                    typewriter("This Pen is my signature weapon", style.GREEN)
                else:
                    typewriter(f"\nPoor.", style.RED)
            elif i in item_costs:
                if game['gold']>= item_costs[i]:
                    game["gold"] -= item_costs[i]
                    game["inventory"].append(i)
                    typewriter("\nPlease take care of this, it was quite expensive...", style.GREEN)
                else:
                    typewriter("\nWhy even try, I thought you kept count of taxes man :P", style.RED)
            else:
                typewriter("\nMate, you're meant to type it absolutely perfectly :(", style.RED)
                
            time.sleep(2)
            os.system('cls' if os.name == 'nt' else 'clear')

        bsvc += 1
        return game

# Equip a weapon from the arsenal
def equip(game):
    print(f"\n{style.BLUE}Which weapon would you like to equip?{style.RESET}")

    for weapon in game["weapons"]:
        print(f"\n    {game['weapons'].index(weapon) + 1}: {weapon[0]} {weapon[1]} - {weapon[2]} dmg")
        time.sleep(0.1)
    
    try:
        game["equipped"] = int(input("\nChoose a weapon (#) >>> ")) - 1
    except Exception as e:
        print(f"\n{style.BOLD}{style.RED}ERROR: {style.RESET}{style.RED}{e}{style.RESET}")

    typewriter(f"You have equipped the {game['weapons'][game['equipped']]}", style.BOLD)
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

# The shop to buy items and level ups
def shop(game):

    # Weapons and their damage ranges
    weapon_stats = {
        "Iron Sword": ["Iron Sword", 20, 50],
        "Steel Axe": ["Steel Axe", 30, 55],
        "Enchanted Dagger": ["Enchanted Dagger", 15, 70],
        "(Totally) Mjölnir": ["(Totally) Mjölnir", 100, 220]
    }

    item_costs = {
        "Small Health Potion": 30,
        "Large Health Potion": 90,
        "Magic Scroll": 400,
        "Secret Map": 1000,
        "Iron Sword": 100,
        "Steel Axe": 200,
        "Enchanted Dagger": 150,
        "Phoenix Feather": 300,
        "Elixir of Fortitude": 200,
        "Mystic Cloak": 600,
        "(Totally) Mjölnir": 500,
        "Shadow Amulet": 350,
    }

    typewriter(f'Welcome adventurer to my shop! I have an assortment of items to buy. Pick your choice:', style.BOLD)

    while True:
        for idx, (item, cost) in enumerate(item_costs.items(), start=1):
            print(f'{idx}. {item}: {cost} gold')
            time.sleep(0.1)

        print()
        typewriter("Weapons:")
        print()
        for item, (name, min_dmg, max_dmg) in weapon_stats.items():
            print(f"{style.YELLOW} {name}: {min_dmg}-{max_dmg} dmg {style.RESET}")

        print(f"\n{style.YELLOW}Current Gold: {game['gold']} {style.RESET}")
        try:
            choice = str(input(f"{style.CYAN}Enter the item you wish to buy (or 'exit' to leave) >>> {style.RESET}")).strip()
        except Exception as e:
            print(f"\n{style.BOLD}{style.RED}ERROR: {style.RESET}{style.RED}{e}{style.RESET}")
            continue

        if choice == "exit":
            typewriter(f"Thank you for visiting the shop!", style.BLUE)
            break
        elif choice in weapon_stats:
            if game['gold'] >= item_costs[choice]:
                game["gold"] -= item_costs[choice]
                game["weapons"].append(weapon_stats[choice])
                typewriter(f"You have purchased {choice}!", style.GREEN)
            else:
                typewriter(f"You do not have enough gold to buy {choice}.", style.RED)
        elif choice in item_costs:
            if game["gold"] >= item_costs[choice]:
                game["gold"] -= item_costs[choice]
                game["inventory"].append(choice)
                typewriter(f"You have purchased {choice}!", style.GREEN)
            else:
                typewriter(f"You do not have enough gold to buy {choice}.", style.RED)
        else:
            typewriter(f" > Invalid item choice, Make sure you type it perfectly", style.RED)

        os.system('cls' if os.name == 'nt' else 'clear')


    time.sleep(2)
    print()

    return game

def level_up_check(game):

    while game["xp"] >= 450 * game["level"]:
        game["level"] += 1
        game["xp"] -= 450 * game["level"]
        game["max_hp"] += round(game["max_hp"] * 0.2)
        game["hp"] = game["max_hp"]
        print()
        typewriter(f"Congratulations! You leveled up to level {game['level']}!", style.GREEN)
        typewriter(f"Your maximum HP has increased to {game['max_hp']}!", style.GREEN)
        typewriter(f"You have also regened to max hp", style.GREEN)

        time.sleep(1)

    return game

# Main game loop
def main():
    os.system('cls' if os.name == 'nt' else 'clear')

    print(f"\n{style.MAGENTA}Welcome to DOODLE R.P.G.\n")
    i = input(f"{style.CYAN}{style.BOLD} Would you like to load a game from json file? ({style.RESET}{style.CYAN}Y{style.BOLD}/{style.RESET}{style.CYAN}N{style.BOLD}) >>> {style.RESET}").strip().upper()

    game = json_load() if i == "Y" else init_new_game()

    while True:
        try:
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
                game = use_item(game)
            elif s in ["equip", "eq"]:
                game = equip(game)
            else:
                print(f"{style.RED} > Invalid command, type help (or h) to list possible commands{style.RESET}")

            if check_game_over(game):
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
