import json
import os
import sys

def repair_save(file_name):
    if not os.path.exists(file_name):
        print(f"[ERROR] File not found: {file_name}")
        return

    try:
        with open(file_name, 'r') as f:
            game_state = json.load(f)
    except Exception as e:
        print(f"[ERROR] Could not read {file_name}: {e}")
        return

    # --- Validation rules with defaults ---
    required_keys = {
        "level": (int, 1),
        "hp": (int, 100),
        "max_hp": (int, 100),
        "gold": (int, 0),
        "inventory": (list, []),
        "weapons": (list, [["Fists", 5, 15]]),
        "equipped": (int, 0),
        "artifacts": (list, []),
        "cheat_mode": (bool, False),
        "xp": (int, 0),
        "skill_set": (dict, {
            "strength": 0,
            "agility": 0,
            "luck": 0,
            "accuracy": 0,
            "defence": 0
        }),
        "used_items": (list, []),
        "autosave": (dict, {
            "filename": "autosave.json",
            "enabled": False
        })
    }

    fixed = {}
    fixes = []  # summary log

    def log_fix(msg):
        print(f"[FIX] {msg}")
        fixes.append(msg)

    # --- Required keys ---
    for key, (expected_type, default_val) in required_keys.items():
        if key not in game_state:
            log_fix(f"Missing '{key}' → set to default {default_val}")
            fixed[key] = default_val
            continue

        if not isinstance(game_state[key], expected_type):
            log_fix(f"'{key}' wrong type → reset to default {default_val}")
            fixed[key] = default_val
            continue

        fixed[key] = game_state[key]

    # --- Weapons check ---
    valid_weapons = []
    for weapon in fixed["weapons"]:
        if (isinstance(weapon, list) and len(weapon) == 3 and
            isinstance(weapon[0], str) and
            isinstance(weapon[1], int) and weapon[1] > 0 and
            isinstance(weapon[2], int) and weapon[2] > weapon[1]):
            valid_weapons.append(weapon)
        else:
            log_fix(f"Invalid weapon {weapon} → removed")
    if not valid_weapons:
        log_fix("Weapons empty/invalid → set to default [['Fists', 5, 15]]")
    fixed["weapons"] = valid_weapons or [["Fists", 5, 15]]

    # --- Skill set check ---
    if isinstance(fixed["skill_set"], dict):
        for skill in ["strength", "agility", "luck", "accuracy", "defence"]:
            if skill not in fixed["skill_set"] or not isinstance(fixed["skill_set"][skill], int) or fixed["skill_set"][skill] < 0:
                log_fix(f"Invalid skill '{skill}' → set to 0")
                fixed["skill_set"][skill] = 0
    else:
        log_fix("Entire skill_set invalid → reset to defaults")
        fixed["skill_set"] = {
            "strength": 0,
            "agility": 0,
            "luck": 0,
            "accuracy": 0,
            "defence": 0
        }

    # --- Artifacts & used_items ---
    bad_artifacts = [a for a in fixed["artifacts"] if not isinstance(a, str)]
    if bad_artifacts:
        log_fix(f"Invalid artifacts removed: {bad_artifacts}")
    fixed["artifacts"] = [a for a in fixed["artifacts"] if isinstance(a, str)]

    bad_used = [a for a in fixed["used_items"] if not isinstance(a, str)]
    if bad_used:
        log_fix(f"Invalid used_items removed: {bad_used}")
    fixed["used_items"] = [a for a in fixed["used_items"] if isinstance(a, str)]

    # --- Autosave check ---
    if not isinstance(fixed["autosave"], dict):
        log_fix("Autosave invalid → reset to defaults")
        fixed["autosave"] = {"filename": "autosave.json", "enabled": False}
    else:
        if not isinstance(fixed["autosave"].get("filename"), str):
            log_fix("Autosave filename invalid → reset to 'autosave.json'")
            fixed["autosave"]["filename"] = "autosave.json"
        if not isinstance(fixed["autosave"].get("enabled"), bool):
            log_fix("Autosave enabled flag invalid → reset to False")
            fixed["autosave"]["enabled"] = False

    # --- Overwrite repaired ---
    with open(file_name, 'w') as f:
        json.dump(fixed, f, indent=4)
    print(f"[DONE] Repaired file written to {file_name}")

    if not fixes:
        print("\nNo fixes needed. File was already valid.")

if __name__ == "__main__":
    repair_save(input("Enter the path to the save file (on file, ctr+shift+c to copy path) >>> "))
