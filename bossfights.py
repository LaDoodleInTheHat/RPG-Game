from dragon import animate_emerge_from_binary, animate_dodge_sword, animate_dodge_and_counter_sword, animate_fumble_fire, animate_get_hit_by_sword, animate_hit
from boss_ai import drago_pick_action, DragoState
import os, sys, time, random as r

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


def typewriter(text, color=style.RESET, delay=0.02, post_delay=0.5):
    for c in text:
        print(f"{color}{c}{style.RESET}", end='', flush=True)
        time.sleep(delay)
    print()
    time.sleep(post_delay)

def lv_25_boss_fight(game, use_item):

    os.system("cls" if os.name == "nt" else "clear")

    # --- Intro animation (kept from your original style) ---
    line = "-"*35
    line2 = "="*35

    sys.stdout.write(style.RED + style.BOLD)
    for char in line:
        sys.stdout.write(char); sys.stdout.flush(); time.sleep(0.5)

    sys.stdout.write("\r")
    sys.stdout.write(style.GREEN + style.BOLD)
    for char in line2:
        sys.stdout.write(char); sys.stdout.flush(); time.sleep(0.05)

    sys.stdout.write("\r")
    sys.stdout.write(style.GREEN + style.BOLD)

    for s in range(10000):
        sys.stdout.write(str(r.randint(0,1))); sys.stdout.flush(); time.sleep(1/(s+1))

    os.system("cls")
    animate_emerge_from_binary()

    # --- Boss & battle state ---
    drago = {
        "name": "Drago the Eternal",
        "hp": 2500,
        "max_hp": 2500,
        # reference move bands, min/max *base* damage before defence
        "moves": [
            ["Flame Breath", 500, 1000],  # idx 0
            ["Tail Swipe", 750, 1200],    # idx 1
            ["Wing Attack", 900, 1300],   # idx 2  (multi-hit in this fight logic)
            ["Heal", -500, 0]             # idx 3
        ],
    }

    player_weapon = game["weapons"][game["equipped"]]

    # cooldowns and flags used by the AI
    cooldowns = {"flame": 0, "tail": 0, "wing": 0, "heal": 0}
    is_charging = False
    enraged = False
    turn = 1
    player_last_action = ""

    def clamp_hp():
        game["hp"] = max(0, min(game["hp"], game["max_hp"]))
        drago["hp"] = max(0, min(drago["hp"], drago["max_hp"]))

    def player_roll_damage():
        base_min = player_weapon[1] + 5*game['skill_set']['strength']
        base_max = player_weapon[2] + 5*game['skill_set']['strength']
        return r.randint(base_min, base_max)

    def boss_roll_damage(min_d, max_d, mult=1.0):
        # apply defence reduction similar to normal fights
        raw = r.randint(int(min_d), int(max_d))
        reduced = max(0, round(raw * mult - 5*game['skill_set']['defence']))
        return reduced

    def print_status():
        typewriter(f"Your HP: {max(game['hp'],0)} | {drago['name']} HP: {max(drago['hp'],0)}",
                   style.YELLOW, delay=0.01, post_delay=0.2)

    # helpful flavor line
    typewriter(f"{drago['name']} descends. The air shimmers with heat...", style.MAGENTA, post_delay=1.0)

    while drago["hp"] > 0 and game["hp"] > 0:
        # update flags
        enraged = enraged or (drago["hp"] <= drago["max_hp"] * 0.35)

        # tick down cooldowns at the start of turn
        for k in cooldowns:
            cooldowns[k] = max(0, cooldowns[k]-1)

        # --- Player Turn ---
        action = input("What would you like to do? (attack, defend, use item, parry, counter) >>> ").strip().lower()

        # calculate a preliminary player hit roll used by multiple branches
        hit_chance = 75 - 3*game['level'] + 5*game['skill_set']['accuracy']
        avoid_chance = 75 + 2*game['level'] - 5*game['skill_set']['agility']

        player_dmg = 0
        player_hit = False

        if action == "attack":
            if r.randint(0, 100) < hit_chance:
                # if Drago was charging, you have a higher chance to interrupt
                dm = player_roll_damage()
                player_hit = True
                player_dmg = dm
                drago["hp"] -= dm
                typewriter(f"You slash for {dm} damage!", style.GREEN, post_delay=0.2)
                animate_get_hit_by_sword()
                if is_charging and r.randint(0, 100) < 85:
                    is_charging = False
                    cooldowns["flame"] = 2   # canceled charge still incurs some CD
                    typewriter("Your strike interrupts the charge!", style.CYAN)
            else:
                typewriter("Your attack missed!", style.RED, post_delay=0.2)
                animate_dodge_sword()

        elif action == "parry":
            typewriter("You brace for a precise parry...", style.BLUE)

        elif action == "counter":
            typewriter("You set up a counter stance...", style.BLUE)

        elif action == "defend":
            typewriter("You raise your guard!", style.BLUE)

        elif action == "use item":
            game = use_item(game)
            clamp_hp()
            typewriter("You quickly stow the item.", style.CYAN)
        else:
            typewriter("Invalid action. Please choose again.", style.RED)
            continue

        player_last_action = action

        # if Drago died from your attack before acting
        if drago["hp"] <= 0:
            break

        # --- Boss AI chooses action ---
        state = DragoState(
            turn=turn,
            drago_hp=drago["hp"],
            drago_max_hp=drago["max_hp"],
            player_hp=game["hp"],
            player_last_action=player_last_action,
            is_charging=is_charging,
            enraged=enraged,
            cooldowns=cooldowns.copy()
        )
        ai_action, ai_note = drago_pick_action(state)
        if ai_note:
            typewriter(ai_note, style.YELLOW, delay=0.01, post_delay=0.4)

        # --- Resolve Boss Action vs Player Choice ---
        # Map move helpers
        FLAME, TAIL, WING, HEAL = 0, 1, 2, 3

        def move_band(idx):
            return drago["moves"][idx][1], drago["moves"][idx][2]

        # defaults
        boss_dmg_done = 0

        if ai_action == "charge":
            is_charging = True
            cooldowns["flame"] = max(cooldowns["flame"], 1)  # soft lock to prevent instant re-charge next turn

        elif ai_action == "heal":
            if cooldowns["heal"] == 0:
                heal_min, _ = move_band(HEAL)
                healed = abs(heal_min) + r.randint(0, 200)  # a little variability
                drago["hp"] += healed
                drago["hp"] = min(drago["hp"], drago["max_hp"])
                cooldowns["heal"] = 4
                typewriter(f"Drago heals for {healed}!", style.GREEN)

        elif ai_action == "flame_breath":
            # If flame is released, it's a strong AoE-like hit; parry halves, defend reduces.
            min_d, max_d = move_band(FLAME)
            mult = 1.8 if enraged else 1.5
            # if you parried *this* turn, bigger mitigation
            if action == "parry":
                mult *= 0.4
                typewriter("Your parry angles the inferno away!", style.CYAN)
            elif action == "defend":
                mult *= 0.7
                typewriter("Your guard blunts some of the flames!", style.CYAN)

            # counter only helps if it was a single surge (we treat flame as a single big packet)
            if action == "counter" and r.randint(0,100) < hit_chance - 10:
                riposte = round(player_roll_damage() * 0.6)
                drago["hp"] -= riposte
                typewriter(f"You cut through the plume for {riposte} counter-damage!", style.GREEN)
                animate_get_hit_by_sword()

            boss_dmg_done = boss_roll_damage(min_d, max_d, mult)
            game["hp"] -= boss_dmg_done
            cooldowns["flame"] = 3
            is_charging = False

            if boss_dmg_done == 0:
                animate_fumble_fire()
            else:
                animate_hit(1)

        elif ai_action == "tail_swipe":
            # guard-break style; defend is less effective
            min_d, max_d = move_band(TAIL)
            mult = 1.25 if enraged else 1.0

            if action == "parry":
                if r.randint(0,100) < 65 + 5*game['skill_set']['agility']:
                    typewriter("Perfect parry! Tail is wide open!", style.CYAN)
                    dm = round(player_roll_damage() * 1.3)
                    drago["hp"] -= dm
                    animate_fumble_fire()
                    mult = 0.2
                else:
                    typewriter("Your parry mistimes!", style.RED)
                    mult = 1.0

            elif action == "defend":
                mult *= 0.85   # reduced defence vs guard-break
                typewriter("The tail rattles your guard!", style.YELLOW)

            elif action == "counter":
                if r.randint(0,100) < hit_chance:
                    dm = round(player_roll_damage() * 1.1)
                    drago["hp"] -= dm
                    typewriter(f"You counter the tail for {dm}!", style.GREEN)
                    animate_get_hit_by_sword()
                    mult *= 0.4
                else:
                    typewriter("Your counter fails!", style.RED)

            boss_dmg_done = boss_roll_damage(min_d, max_d, mult)
            game["hp"] -= boss_dmg_done
            cooldowns["tail"] = 2
            animate_hit(1)

        elif ai_action == "wing_attack":
            # multi-hit to foil counters: two lighter hits
            min_d, max_d = move_band(WING)
            base = boss_roll_damage(min_d, max_d, (1.0 if not enraged else 1.15))
            hit1 = round(base * 0.55)
            hit2 = round(base * 0.55)

            mitig = 1.0
            if action == "defend":
                mitig = 0.7
                typewriter("Your guard weathers the flurry!", style.CYAN)
            elif action == "parry":
                mitig = 0.6
                typewriter("You deflect part of the barrage!", style.CYAN)
            elif action == "counter":
                typewriter("Multiple blows ruin your counter timing!", style.RED)

            for idx, h in enumerate((hit1, hit2), start=1):
                taken = round(h * mitig)
                game["hp"] -= taken
                typewriter(f"Wing hit {idx} strikes for {taken}!", style.RED, post_delay=0.15)
                animate_hit(1)

            cooldowns["wing"] = 2

        clamp_hp()

        # End of turn: quick status and pacing
        print_status()
        turn += 1
        time.sleep(0.6)

    # --- End of battle ---
    os.system("cls" if os.name == "nt" else "clear")

    if game["hp"] <= 0 and drago["hp"] <= 0:
        typewriter("Both fighters collapse... but you stand up first!", style.MAGENTA)
        victor = "player"
    elif game["hp"] <= 0:
        typewriter("Drago roars in triumph. You fall...", style.RED)
        victor = "drago"
    else:
        typewriter("Drago the Eternal is defeated!", style.MAGENTA)
        victor = "player"

    if victor == "player":
        gold_reward = 1200
        xp_reward = 1400
        game["gold"] += gold_reward
        game["xp"] += xp_reward
        typewriter(f"You gain {gold_reward} gold!", style.YELLOW)
        typewriter(f"You gain {xp_reward} XP!", style.GREEN)
        time.sleep(2)

    return game
