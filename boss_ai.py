# boss_ai.py
from dataclasses import dataclass
import random as r
from typing import Dict, Tuple

@dataclass(frozen=True)
class DragoState:
    turn: int
    drago_hp: int
    drago_max_hp: int
    player_hp: int
    player_last_action: str  # "attack" | "defend" | "parry" | "counter" | "use item" | ""
    is_charging: bool
    enraged: bool
    cooldowns: Dict[str, int]  # keys: "flame", "heal", "tail", "wing"

def drago_pick_action(state: DragoState) -> Tuple[str, str]:
    """
    Returns (action, note)
    action ∈ {"charge","flame_breath","tail_swipe","wing_attack","heal"}
    """
    if state.is_charging:
        return ("flame_breath", "Drago unleashes the stored inferno!")

    hp_ratio = state.drago_hp / max(1, state.drago_max_hp)
    if state.cooldowns.get("heal", 0) == 0 and hp_ratio <= 0.33:
        if r.random() < 0.6:
            return ("heal", "Scales glow as wounds knit back together.")

    if state.player_last_action == "defend" and state.cooldowns.get("tail", 0) == 0:
        return ("tail_swipe", "A sweeping tail aims to break your guard!")

    if state.player_last_action == "counter" and state.cooldowns.get("wing", 0) == 0:
        return ("wing_attack", "Wings blur—multiple strikes to foil a counter!")

    if state.cooldowns.get("flame", 0) == 0:
        base_p = 0.25 + (0.02 * max(0, state.turn - 3))
        if state.enraged:
            base_p += 0.1
        if r.random() < min(0.6, base_p):
            return ("charge", "Drago inhales—heat distorts the air...")

    choices = []
    if state.cooldowns.get("tail", 0) == 0:
        choices += ["tail_swipe"] * 3
    if state.cooldowns.get("wing", 0) == 0:
        choices += ["wing_attack"] * 2
    if not choices:
        return ("wing_attack", "Wings lash out in desperation!")

    action = r.choice(choices)
    note = "A brutal tail arcs toward you!" if action == "tail_swipe" else "Wings slice the air—rapid strikes incoming!"
    return (action, note)
