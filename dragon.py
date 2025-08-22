#!/usr/bin/env python3
"""
Detailed ASCII dragon boss animation (single-file).

- Idle breathing (shows "------" idle text)
- Small "rr" growls (one-line chaotic text)
- Big jumpscare roar with expanding colored fire
- Prevention of overlay residue by padding every printed line
- Uses ANSI colors; modern terminals recommended

Run: python3 dragon_roar_full.py
Stop: Ctrl+C
"""

import sys
import time
import random
import shutil
import os
import re

# --------------------
# Terminal / ANSI utils
# --------------------
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
ORANGE = "\033[38;5;208m"     # 256-color orange-ish
DARK_GRAY = "\033[90m"

HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
CLEAR_SCREEN = "\033[2J"
CURSOR_HOME = "\033[H"

# regex to remove ANSI sequences for measuring visible length
_ANSI_RE = re.compile(r'\x1b\[[0-9;?]*[A-Za-z]')

def strip_ansi(s: str) -> str:
    """Return string with ANSI sequences removed (for correct visible-length)."""
    return _ANSI_RE.sub('', s)

def get_term_size():
    try:
        cols, rows = shutil.get_terminal_size()
    except Exception:
        cols, rows = 80, 24
    return cols, rows

# --------------------
# Dragon ASCII art base
# --------------------
# NOTE: avoid raw-strings when ending with backslash; use escaped backslashes.
DRAGON_BASE = [
    "                             ___====-_  _-====___",
    "                       _--^^^#####//      \\\\#####^^^--_",
    "                    _-^##########// (    ) \\\\##########^-_",
    "                   -############//  |\\^^/|  \\\\############-",
    "                 _/############//   (@::@)   \\\\############\\_",
    "                /#############((     \\\\//     ))#############\\",
    "               -###############\\\\    (oo)    //###############-",
    "              -#################\\\\  / UUU \\  //#################-",
    "             _#/|##########/\\######(  / | \\  )######/\\##########|\\#_",
    "            |/ |#/\\# /\\#/\\/  \\#/\\##\\  |||||  /##/\\#/  \\/\\#\\/#\\#| \\|",
    "            `  |/  V  V `   V  \\#\\|| ooo ||/#/  V   ' V  V  \\|  ' ",
    "               `   `  `       `   / |     | \\   '      '  '   '",
    "                                  (  |     |  )",
    "                                   \\ |     | /",
    "                                    \\|_____|/",
    "                                     /  |  \\\\",
    "                                    /   |   \\\\",
    "                                   /    |    \\\\",
    "                                  (_____|_____)",
]

# --------------------
# Frame generator helpers
# --------------------
def dragon_frame(idle_phase=0, mouth_open=0, eye_fierce=False):
    """
    Produce a frame (list of lines) from the base art with small changes:
    - idle_phase toggles small chest/tail breathing shifts
    - mouth_open: 0 (closed), 1 (small), 2 (wide)
    - eye_fierce: toggles fiercer eyes for roaring
    """
    lines = DRAGON_BASE.copy()

    # Slight chest puff effect
    if idle_phase % 2 == 1:
        lines[11] = lines[11].replace("(  |     |  )", "((  |     |  ))")

    # Eyes: change (@::@) to fiercer variants
    if eye_fierce:
        lines[4] = lines[4].replace("(@::@)", "(@><@)")
    else:
        if idle_phase % 5 == 0:
            lines[4] = lines[4].replace("(@::@)", "(@..@)")

    # Mouth changes near lines 6-7
    if mouth_open == 0:
        # closed-ish (default)
        pass
    elif mouth_open == 1:
        # small open
        lines[6] = lines[6].replace("(oo)", "(  )")
        lines[7] = lines[7].replace("UUU", " U ")
    else:  # wide open
        lines[6] = lines[6].replace("(oo)", "(  )")
        lines[7] = lines[7].replace("UUU", "\\_/")

    return lines

def colored(text, color):
    return f"{color}{text}{RESET}"

def random_roar_text(base="ra", intensity=12):
    """One-line chaotic roar text with random case and repeats."""
    out = []
    for _ in range(intensity):
        ch = random.choice(list(base))
        ch = ch.upper() if random.random() > 0.5 else ch.lower()
        if random.random() > 0.7:
            ch *= random.randint(2, 4)
        out.append(ch)
    return "".join(out)

# --------------------
# Padding renderer (prevents overlay residue)
# --------------------
def render_frame_padded(lines, fire_cols=0, flame_colors=None, shake=0, extra_line=None):
    """
    Compose and return a fully padded framebuffer string:
    - Ensures every printed row is padded to terminal width based on visible length (ANSI-stripped length).
    - Keeps same number of lines across frames so overlay residues are cleaned.
    - Starts with CURSOR_HOME so writing it overwrites previous frame.
    """
    cols, rows = get_term_size()

    # Build per-line text (including appended flames where necessary)
    frame_lines = []
    dragon_width = max(len(strip_ansi(l)) for l in lines)

    # Limit effective fire length to fit available columns
    max_fire = 0
    if fire_cols:
        max_fire = min(max(0, cols - dragon_width - 1), fire_cols)

    mouth_anchor = 6  # approximate anchor for where to append flames

    for idx, ln in enumerate(lines):
        appended = ""
        if max_fire > 0 and mouth_anchor - 1 <= idx <= mouth_anchor + 2:
            pieces = []
            for c in range(max_fire):
                dist = abs(idx - mouth_anchor)
                if dist == 0:
                    ch = random.choice(["^", "A", "@", "*"])
                elif dist == 1:
                    ch = random.choice(["~", "`", "*", "v"])
                else:
                    ch = random.choice([".", " "])
                if flame_colors:
                    color = flame_colors[c % len(flame_colors)]
                else:
                    # simple gradient: near columns hottest
                    if c < max(1, max_fire // 3):
                        color = YELLOW
                    elif c < max(1, 2 * max_fire // 3):
                        color = ORANGE
                    else:
                        color = RED
                if dist > 1:
                    color = DARK_GRAY
                pieces.append(f"{color}{ch}{RESET}")
            appended = "".join(pieces)

        # apply horizontal shake (leading spaces)
        lead = " " * max(0, shake)
        composed = lead + ln + appended

        # measure visible width and pad to terminal cols
        visible_len = len(strip_ansi(composed))
        if visible_len < cols:
            composed = composed + (" " * (cols - visible_len))
        else:
            # rough truncation (keeps things simple)
            composed = composed[:cols]

        frame_lines.append(composed)

    # Ensure an extra_line is also padded and added as last row
    if extra_line is None:
        extra_line = ""
    v_extra = strip_ansi(extra_line)
    if len(v_extra) < cols:
        extra_line_padded = extra_line + (" " * (cols - len(v_extra)))
    else:
        extra_line_padded = extra_line[:cols]

    # Build the framebuffer. Use CURSOR_HOME to overwrite previous frame.
    framebuffer = CURSOR_HOME + "\n".join(frame_lines + [extra_line_padded])
    return framebuffer

# --------------------
# Main animation loop
# --------------------
def animate(count):
    cols, rows = get_term_size()
    if rows < len(DRAGON_BASE) + 4 or cols < 60:
        sys.stdout.write("Please enlarge the terminal (>=60 cols, more recommended) and re-run.\n")
        return

    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.write(CLEAR_SCREEN + CURSOR_HOME)
    sys.stdout.flush()

    for _ in range(count):
        # 1) Idle breathing
        idle_time = random.uniform(1.8, 3.2)
        start = time.time()
        phase = 0
        while time.time() - start < idle_time:
            frame_lines = dragon_frame(idle_phase=phase, mouth_open=0, eye_fierce=False)
            out = render_frame_padded(frame_lines, fire_cols=0, shake=0, extra_line=colored("------   (dragon idle)", DARK_GRAY))
            sys.stdout.write(out)
            sys.stdout.flush()
            time.sleep(0.45)
            phase += 1

        # 2) Small growls (rr)
        for g in range(random.randint(2, 4)):
            rtxt = random_roar_text(base="r", intensity=random.randint(3, 6))
            frame_lines = dragon_frame(idle_phase=phase, mouth_open=1, eye_fierce=False)
            out = render_frame_padded(frame_lines, fire_cols=0, shake=(1 if g % 2 == 0 else 0), extra_line=colored(rtxt, MAGENTA))
            sys.stdout.write(out)
            sys.stdout.flush()
            time.sleep(0.22 + random.random() * 0.18)
            phase += 1

        # tension pause
        frame_lines = dragon_frame(idle_phase=phase, mouth_open=1, eye_fierce=True)
        out = render_frame_padded(frame_lines, fire_cols=0, shake=0, extra_line=colored("...", DARK_GRAY))
        sys.stdout.write(out)
        sys.stdout.flush()
        time.sleep(0.55)

        # 3) Roar buildup
        roar_build_steps = 6
        for step in range(roar_build_steps):
            mouth_open = 1 if step < roar_build_steps - 2 else 2
            frame_lines = dragon_frame(idle_phase=phase, mouth_open=mouth_open, eye_fierce=True)
            shake = random.randint(0, min(3, step))
            text = random_roar_text(base="ra", intensity=4 + step * 2)
            text_color = BOLD + (RED if step > roar_build_steps // 2 else MAGENTA)
            out = render_frame_padded(frame_lines, fire_cols=0, shake=shake, extra_line=colored(text, text_color))
            sys.stdout.write(out)
            sys.stdout.flush()
            time.sleep(0.11)
            phase += 1

        # 4) Big jumpscare roar + expanding fire
        cols, _ = get_term_size()
        dragon_width = max(len(strip_ansi(l)) for l in DRAGON_BASE)
        max_fire_len = max(8, min(max(1, cols - dragon_width - 4), 70))
        flame_colors = [YELLOW, ORANGE, RED, MAGENTA]

        for length in range(0, max_fire_len + 1):
            frame_lines = dragon_frame(idle_phase=phase, mouth_open=2, eye_fierce=True)
            shake = max(0, random.randint(-2, 2) + 2)
            roar_text = " " + random_roar_text(base="RA", intensity=6 + (length // 3))
            text_color = BOLD + (RED if length > max_fire_len * 0.45 else ORANGE)
            out = render_frame_padded(frame_lines, fire_cols=length, flame_colors=flame_colors, shake=shake, extra_line=colored(roar_text, text_color))
            sys.stdout.write(out)
            sys.stdout.flush()
            time.sleep(max(0.03, 0.14 - (length * 0.0025)))
            phase += 1

        # sustain full blast with flicker
        for sustain in range(6):
            frame_lines = dragon_frame(idle_phase=phase, mouth_open=2, eye_fierce=True)
            out = render_frame_padded(frame_lines, fire_cols=max_fire_len, flame_colors=flame_colors, shake=random.randint(0, 3), extra_line=colored(random_roar_text(base="RA", intensity=12), BOLD + RED))
            sys.stdout.write(out)
            sys.stdout.flush()
            time.sleep(0.08)
            phase += 1

        # 5) Smoke + cooldown fade
        for fade in range(12):
            fade_len = int(max_fire_len * (1.0 - (fade / 12.0)))
            smoke_colors = [DARK_GRAY, DARK_GRAY, MAGENTA]
            frame_lines = dragon_frame(idle_phase=phase, mouth_open=1 if fade < 8 else 0, eye_fierce=False)
            out = render_frame_padded(frame_lines, fire_cols=fade_len, flame_colors=smoke_colors, shake=0, extra_line=colored("(smoke)...", DARK_GRAY))
            sys.stdout.write(out)
            sys.stdout.flush()
            time.sleep(0.11)
            phase += 1

        # short cooldown idle
        frame_lines = dragon_frame(idle_phase=phase, mouth_open=0, eye_fierce=False)
        out = render_frame_padded(frame_lines, fire_cols=0, shake=0, extra_line=colored("------   (dragon catches breath)", DARK_GRAY))
        sys.stdout.write(out)
        sys.stdout.flush()
        time.sleep(1.2)