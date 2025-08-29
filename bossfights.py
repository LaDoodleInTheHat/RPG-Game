from drago_animations import (
    animate_emerge_from_binary,
    animate_dodge_sword,
    animate_dodge_and_counter_sword,
    animate_fumble_fire,
    animate_get_hit_by_sword,
    animate_hit
)
import os, sys, time, random as r
from dataclasses import dataclass
from typing import Dict, Tuple, Callable

# ----------------------
# Data structures
# ----------------------
@dataclass(frozen=True)
class BossState:
    turn: int
    boss_hp: int
    boss_max_hp: int
    player_hp: int
    player_last_action: str   # "attack", "defend", "parry", "counter", "use item", ""
    is_charging: bool
    enraged: bool
    cooldowns: Dict[str, int] # {move_name: turns_remaining}

@dataclass
class BossMove:
    name: str
    priority: Callable[[BossState], float]
    execute_note: str
    dmg_range: Tuple[int, int] = (0, 0)   # positive = damage, negative = heal
    requires_charge: bool = False
    heal_move: bool = False

# ----------------------
# Generic Boss AI
# ----------------------
def boss_pick_action(state: BossState, moves: Dict[str, BossMove]) -> Tuple[BossMove, str]:
    """Return the BossMove chosen and its flavor text."""

    # forced flame_breath if charging
    if state.is_charging and "flame_breath" in moves:
        return (moves["flame_breath"], moves["flame_breath"].execute_note)

    scored = []
    for move_name, move in moves.items():
        if state.cooldowns.get(move_name, 0) > 0:
            continue
        score = move.priority(state)
        if score > 0:
            scored.append((score, move))

    if not scored:
        # fallback basic attack
        fallback = BossMove(
            "basic_attack",
            lambda s: 0,
            "The boss lashes out desperately!",
            dmg_range=(200, 400)
        )
        return (fallback, fallback.execute_note)

    scored.sort(key=lambda x: x[0], reverse=True)
    top_score = scored[0][0]
    filtered = [m for sc, m in scored if sc >= top_score * 0.8]
    chosen = r.choice(filtered)
    return (chosen, chosen.execute_note)

# ----------------------
# Boss Move Definitions
# ----------------------
def get_drago_moves():
    return {
        "charge": BossMove(
            "charge",
            priority=lambda s: 0.3 + (0.1 if s.enraged else 0.0),
            execute_note="Drago inhales—heat distorts the air...",
            dmg_range=(0, 0)
        ),
        "flame_breath": BossMove(
            "flame_breath",
            priority=lambda s: 0,
            execute_note="Drago unleashes the stored inferno!",
            dmg_range=(500, 1000),
            requires_charge=True
        ),
        "tail_swipe": BossMove(
            "tail_swipe",
            priority=lambda s: 0.7 if s.player_last_action == "defend" else 0.4,
            execute_note="A sweeping tail aims to break your guard!",
            dmg_range=(750, 1200)
        ),
        "wing_attack": BossMove(
            "wing_attack",
            priority=lambda s: 0.7 if s.player_last_action == "counter" else 0.4,
            execute_note="Wings blur—multiple strikes to foil a counter!",
            dmg_range=(900, 1300)
        ),
        "heal": BossMove(
            "heal",
            priority=lambda s: 0.8 if (s.boss_hp/s.boss_max_hp <= 0.33) else 0,
            execute_note="Scales glow as wounds knit back together.",
            dmg_range=(-500, 0),
            heal_move=True
        ),
    }

def get_spidey_moves():
    return {
        "web_shot": BossMove(
            "web_shot",
            priority=lambda s: 0.6 if s.player_last_action == "attack" else 0.4,
            execute_note="Spidey shoots sticky webs to slow you!",
            dmg_range=(400, 700)
        ),
        "fang_bite": BossMove(
            "fang_bite",
            priority=lambda s: 0.7 if s.player_last_action in ("defend", "parry") else 0.5,
            execute_note="Spidey lunges with venomous fangs!",
            dmg_range=(600, 1000)
        ),
        "leg_stab": BossMove(
            "leg_stab",
            priority=lambda s: 0.7 if s.player_last_action == "counter" else 0.5,
            execute_note="Spidey jabs with razor legs!",
            dmg_range=(500, 900)
        ),
        "cocoon": BossMove(
            "cocoon",
            priority=lambda s: 0.8 if (s.boss_hp/s.boss_max_hp <= 0.3) else 0,
            execute_note="Spidey spins a cocoon to shield itself.",
            dmg_range=(-400, 0),
            heal_move=True
        ),
    }

# ----------------------
# Style & Utils
# ----------------------
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

# ----------------------
# Boss Fight: Drago (Lv25)
# ----------------------
def lv_25_boss_fight(game, use_item):
    os.system("cls" if os.name == "nt" else "clear")

    # cinematic intro
    line = "-"*35
    line2 = "="*35
    sys.stdout.write(style.RED + style.BOLD)
    for char in line: sys.stdout.write(char); sys.stdout.flush(); time.sleep(0.5)
    sys.stdout.write("\r" + style.GREEN + style.BOLD)
    for char in line2: sys.stdout.write(char); sys.stdout.flush(); time.sleep(0.05)
    sys.stdout.write("\r" + style.GREEN + style.BOLD)
    for s in range(500): sys.stdout.write(str(r.randint(0,1))); sys.stdout.flush(); time.sleep(1/(s+1))
    os.system("cls")
    animate_emerge_from_binary()

    drago = {"name": "Drago the Eternal", "hp": 2500, "max_hp": 2500}
    player_weapon = game["weapons"][game["equipped"]]
    cooldowns = {"charge":0, "flame_breath":0, "tail_swipe":0, "wing_attack":0, "heal":0}
    is_charging, enraged, turn, player_last_action = False, False, 1, ""
    moves = get_drago_moves()

    def clamp_hp():
        game["hp"] = max(0, min(game["hp"], game["max_hp"]))
        drago["hp"] = max(0, min(drago["hp"], drago["max_hp"]))

    def player_roll_damage():
        return r.randint(
            player_weapon[1] + 5*game['skill_set']['strength'],
            player_weapon[2] + 5*game['skill_set']['strength']
        )

    def boss_roll_damage(min_d, max_d, mult=1.0):
        raw = r.randint(int(min_d), int(max_d))
        return max(0, round(raw*mult - 5*game['skill_set']['defence']))

    def print_status():
        typewriter(f"Your HP: {game['hp']} | {drago['name']} HP: {drago['hp']}", style.YELLOW)

    typewriter(f"{drago['name']} descends. The air shimmers with heat...", style.MAGENTA)

    while drago["hp"] > 0 and game["hp"] > 0:
        enraged = enraged or drago["hp"] <= drago["max_hp"]*0.35
        for k in cooldowns: cooldowns[k] = max(0, cooldowns[k]-1)

        # --- Player turn ---
        print_status()
        action = input("Do (attack/defend/parry/counter/use item): ").strip().lower()
        if action == "attack":
            if r.randint(0,100) < (75 - 3*game['level'] + 5*game['skill_set']['accuracy']):
                dmg = player_roll_damage()
                drago["hp"] -= dmg
                animate_get_hit_by_sword()
                typewriter(f"You slash for {dmg}!", style.GREEN)
                if is_charging and r.randint(0,100) < 85:
                    is_charging = False; cooldowns["flame_breath"]=2
                    typewriter("You interrupt the charge!", style.CYAN)
            else:
                typewriter("You miss!", style.RED); animate_dodge_sword()
        elif action == "use item":
            game = use_item(game); clamp_hp()
        else:
            typewriter(f"You prepare to {action}.", style.BLUE)

        player_last_action = action
        if drago["hp"] <= 0: break

        # --- Boss turn ---
        state = BossState(turn, drago["hp"], drago["max_hp"], game["hp"],
                          player_last_action, is_charging, enraged, cooldowns.copy())
        chosen_move, ai_note = boss_pick_action(state, moves)

        typewriter(ai_note, style.YELLOW)
        if chosen_move.heal_move:
            heal_amt = abs(r.randint(*chosen_move.dmg_range))
            drago["hp"] = min(drago["hp"] + heal_amt, drago["max_hp"])
            typewriter(f"{drago['name']} heals for {heal_amt}!", style.GREEN)
        else:
            dmg = boss_roll_damage(*chosen_move.dmg_range)
            game["hp"] -= dmg
            animate_hit(1)
            typewriter(f"{drago['name']} uses {chosen_move.name} for {dmg}!", style.RED)

        clamp_hp()
        turn += 1
        time.sleep(0.6)

    if game["hp"] > 0:
        typewriter("Drago falls! Victory!", style.MAGENTA)
        game["gold"] += 1200; game["xp"] += 1400
    else:
        typewriter("You are defeated...", style.RED)
    return game
