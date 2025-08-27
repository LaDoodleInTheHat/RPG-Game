"""
Detailed ASCII dragon boss animation (single-file).

- Idle breathing (shows "------" idle text)
- Small "rr" growls (one-line chaotic text)
- Big jumpscare roar with expanding colored fire
- Prevention of overlay residue by padding every printed line
- Uses ANSI colors; modern terminals recommended

Run: python3 dragon.py
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
GREEN = "\033[32m"
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

min_lead = min(len(l) - len(l.lstrip(' ')) for l in DRAGON_BASE if l.strip())

SWORD_BASE = ["<====|---"]

# --------------------
# Frame generator helpers
# --------------------
def dragon_frame(idle_phase=0, mouth_open=0, eye_fierce=False, shift_left=0, hurt=False):
    """
    Produce a frame (list of lines) from the base art with small changes:
    - idle_phase toggles small chest/tail breathing shifts
    - mouth_open: 0 (closed), 1 (small), 2 (wide)
    - eye_fierce: toggles fiercer eyes for roaring
    - shift_left: shift the art left by removing leading spaces (up to min_lead)
    - hurt: changes eyes to hurt expression
    """
    lines = [l[shift_left:] if shift_left <= min_lead else l for l in DRAGON_BASE]

    # Slight chest puff effect
    if idle_phase % 2 == 1:
        lines[11] = lines[11].replace("(  |     |  )", "((  |     |  ))")

    # Eyes: change (@::@) to fiercer variants
    if eye_fierce:
        lines[4] = lines[4].replace("(@::@)", "(@><@)")
    else:
        if idle_phase % 5 == 0:
            lines[4] = lines[4].replace("(@::@)", "(@..@)")

    if hurt:
        lines[4] = lines[4].replace("(@::@)", "(X X)")
        lines[4] = lines[4].replace("(@><@)", "(X X)")
        lines[4] = lines[4].replace("(@..@)", "(X X)")

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
def render_frame_padded(lines, fire_cols=0, flame_colors=None, shake=0, extra_line=None, sword_pos=None, sword_row_offset=0, sword_color=RESET, sword_lines=SWORD_BASE):
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

        # add sword if applicable
        visible_len = len(strip_ansi(composed))
        if sword_pos is not None and sword_row_offset <= idx < sword_row_offset + len(sword_lines):
            s_idx = idx - sword_row_offset
            s_ln = sword_lines[s_idx]
            s_composed = f"{sword_color}{s_ln}{RESET}"
            if sword_pos >= visible_len:
                composed += " " * round(sword_pos - visible_len) + s_composed

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
def animate_hit(count):
    cols, rows = get_term_size()
    if rows < len(DRAGON_BASE) + 4 or cols < 60:
        sys.stdout.write("Please enlarge the terminal (>=60 cols, more recommended) and re-run.\n")
        return

    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.write(CLEAR_SCREEN + CURSOR_HOME)
    sys.stdout.flush()

    for _ in range(count):
        # 1) Idle breathing
        idle_time = random.uniform(1.8, 5)
        start = time.time()
        phase = 0
        while time.time() - start < idle_time:
            frame_lines = dragon_frame(idle_phase=phase, mouth_open=0, eye_fierce=False)
            out = render_frame_padded(frame_lines, fire_cols=0, shake=0, extra_line=colored("------   (dragon idle)", DARK_GRAY))
            sys.stdout.write(out)
            sys.stdout.flush()
            time.sleep(0.45)
            phase += 1

        # tension pause
        frame_lines = dragon_frame(idle_phase=phase, mouth_open=1, eye_fierce=True)
        out = render_frame_padded(frame_lines, fire_cols=0, shake=0, extra_line=colored("...", DARK_GRAY))
        sys.stdout.write(out)
        sys.stdout.flush()
        time.sleep(2)

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
        for sustain in range(24):
            frame_lines = dragon_frame(idle_phase=phase, mouth_open=2, eye_fierce=True)
            out = render_frame_padded(frame_lines, fire_cols=max_fire_len, flame_colors=flame_colors, shake=random.randint(0, 3), extra_line=colored(random_roar_text(base="RA", intensity=12), BOLD + RED))
            sys.stdout.write(out)
            sys.stdout.flush()
            time.sleep(0.02)
            phase += 1

        # 5) Smoke + cooldown fade
        for fade in range(20):
            fade_len = int(max_fire_len * (1.0 - (fade / 12.0)))
            smoke_colors = [DARK_GRAY, DARK_GRAY, MAGENTA]
            frame_lines = dragon_frame(idle_phase=phase, mouth_open=1 if fade < 8 else 0, eye_fierce=False)
            out = render_frame_padded(frame_lines, fire_cols=fade_len, flame_colors=smoke_colors, shake=0, extra_line=colored("(smoke)...", DARK_GRAY))
            sys.stdout.write(out)
            sys.stdout.flush()
            time.sleep(0.15)
            phase += 1

        # short cooldown idle
        frame_lines = dragon_frame(idle_phase=phase, mouth_open=0, eye_fierce=False)
        out = render_frame_padded(frame_lines, fire_cols=0, shake=0, extra_line=colored("------   (dragon catches breath)", DARK_GRAY))
        sys.stdout.write(out)
        sys.stdout.flush()
        time.sleep(1.2)

# --------------------
# New animation functions
# --------------------
def animate_emerge_from_binary():
    cols, rows = get_term_size()
    if rows < len(DRAGON_BASE) + 4 or cols < 60:
        sys.stdout.write("Please enlarge the terminal (>=60 cols, more recommended) and re-run.\n")
        return

    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.write(CLEAR_SCREEN + CURSOR_HOME)
    sys.stdout.flush()

    # Initial binary screen animation
    for _ in range(10):
        binary_lines = []
        for _ in range(rows):
            line = ''.join(random.choice('01') for _ in range(cols))
            binary_lines.append(colored(line, DARK_GRAY))
        out = CURSOR_HOME + '\n'.join(binary_lines)
        sys.stdout.write(out)
        sys.stdout.flush()
        time.sleep(0.05)

    # Prepare for reveal
    dh = len(DRAGON_BASE)
    dw = max(len(l) for l in DRAGON_BASE)
    padded_dragon = [l.ljust(dw) for l in DRAGON_BASE]
    row_start = 0
    col_start = 0

    # Initialize grid with binary
    grid = [[random.choice('01') for _ in range(cols)] for _ in range(rows)]

    # Positions to reveal (dragon area)
    reveal_positions = [(dr, dc) for dr in range(dh) for dc in range(dw) if row_start + dr < rows and col_start + dc < cols]
    random.shuffle(reveal_positions)

    num_steps = 100
    per_step = len(reveal_positions) // num_steps if num_steps > 0 else 0

    for step in range(num_steps):
        start_idx = step * per_step
        end_idx = len(reveal_positions) if step == num_steps - 1 else (step + 1) * per_step
        for i in range(start_idx, end_idx):
            dr, dc = reveal_positions[i]
            grid[row_start + dr][col_start + dc] = padded_dragon[dr][dc]

        # Build and render frame
        frame_lines = [''.join(grid[r]) for r in range(rows - 1)]
        extra_line = colored("Dragon emerging from the digital void...", DARK_GRAY)
        extra_padded = extra_line + ' ' * (cols - len(strip_ansi(extra_line)))
        out = CURSOR_HOME + '\n'.join(frame_lines) + '\n' + extra_padded
        sys.stdout.write(out)
        sys.stdout.flush()
        time.sleep(0.03)

    # Fade out non-dragon binary
    non_dragon_positions = [(r, c) for r in range(rows) for c in range(cols) if not (row_start <= r < row_start + dh and col_start <= c < col_start + dw)]
    random.shuffle(non_dragon_positions)
    num_fade_steps = 50
    per_fade_step = len(non_dragon_positions) // num_fade_steps if num_fade_steps > 0 else 0

    for step in range(num_fade_steps):
        start_idx = step * per_fade_step
        end_idx = len(non_dragon_positions) if step == num_fade_steps - 1 else (step + 1) * per_fade_step
        for i in range(start_idx, end_idx):
            r, c = non_dragon_positions[i]
            grid[r][c] = ' '

        # Build and render frame
        frame_lines = [''.join(grid[r]) for r in range(rows - 1)]
        extra_line = colored("Digital void fading...", DARK_GRAY)
        extra_padded = extra_line + ' ' * (cols - len(strip_ansi(extra_line)))
        out = CURSOR_HOME + '\n'.join(frame_lines) + '\n' + extra_padded
        sys.stdout.write(out)
        sys.stdout.flush()
        time.sleep(0.03)

    time.sleep(1)
    sys.stdout.write(SHOW_CURSOR)

def animate_dodge_sword():
    cols, rows = get_term_size()
    if rows < len(DRAGON_BASE) + 4 or cols < 60:
        sys.stdout.write("Please enlarge the terminal (>=60 cols, more recommended) and re-run.\n")
        return

    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.write(CLEAR_SCREEN + CURSOR_HOME)
    sys.stdout.flush()

    sword_row_offset = 6  # Align with dragon's head
    sword_color = BOLD + RED
    dragon_width = max(len(strip_ansi(l)) for l in DRAGON_BASE)
    start_pos = cols - max(len(l) for l in SWORD_BASE) - 5
    end_pos = dragon_width + 5
    steps = 30
    step_delta = (start_pos - end_pos) / (steps - 1) if steps > 1 else 0
    max_shift = min_lead // 2
    dodge_start_step = steps // 2
    shift_left = 0
    pos = start_pos

    for step in range(steps):
        if step > dodge_start_step:
            shift_left = min(max_shift, shift_left + (max_shift // 5))

        frame_lines = dragon_frame(eye_fierce=True, shift_left=shift_left)
        current_dragon_width = max(len(strip_ansi(l)) for l in frame_lines)
        sword_p = pos if pos >= current_dragon_width else None
        out = render_frame_padded(frame_lines, fire_cols=0, shake=0, extra_line=colored("Dodging the sword!", YELLOW), sword_pos=sword_p, sword_row_offset=sword_row_offset, sword_color=sword_color, sword_lines=SWORD_BASE)
        sys.stdout.write(out)
        sys.stdout.flush()
        time.sleep(0.1)
        pos -= step_delta

    # Return to normal position
    for _ in range(5):
        shift_left = max(0, shift_left - (max_shift // 5))
        frame_lines = dragon_frame(shift_left=shift_left)
        out = render_frame_padded(frame_lines, fire_cols=0, shake=0, extra_line=colored("Safe!", GREEN))
        sys.stdout.write(out)
        sys.stdout.flush()
        time.sleep(0.1)

    sys.stdout.write(SHOW_CURSOR)

def animate_dodge_and_counter_sword():
    cols, rows = get_term_size()
    if rows < len(DRAGON_BASE) + 4 or cols < 60:
        sys.stdout.write("Please enlarge the terminal (>=60 cols, more recommended) and re-run.\n")
        return

    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.write(CLEAR_SCREEN + CURSOR_HOME)
    sys.stdout.flush()

    sword_row_offset = 6  # Align with dragon's head
    sword_color = BOLD + RED
    dragon_width = max(len(strip_ansi(l)) for l in DRAGON_BASE)
    start_pos = cols - max(len(l) for l in SWORD_BASE) - 5
    end_pos = dragon_width + 5
    steps = 30
    step_delta = (start_pos - end_pos) / (steps - 1) if steps > 1 else 0
    max_shift = min_lead // 2
    dodge_start_step = steps // 2
    shift_left = 0
    pos = start_pos

    for step in range(steps):
        if step > dodge_start_step:
            shift_left = min(max_shift, shift_left + (max_shift // 5))

        frame_lines = dragon_frame(eye_fierce=True, shift_left=shift_left)
        current_dragon_width = max(len(strip_ansi(l)) for l in frame_lines)
        sword_p = pos if pos >= current_dragon_width else None
        out = render_frame_padded(frame_lines, fire_cols=0, shake=0, extra_line=colored("Dodging and preparing counter!", YELLOW), sword_pos=sword_p, sword_row_offset=sword_row_offset, sword_color=sword_color, sword_lines=SWORD_BASE)
        sys.stdout.write(out)
        sys.stdout.flush()
        time.sleep(0.1)
        pos -= step_delta

    # Counter with fire
    flame_colors = [YELLOW, ORANGE, RED, MAGENTA]
    max_fire_len = max(8, min(cols - dragon_width - 4, 70))
    for length in range(0, max_fire_len + 1):
        frame_lines = dragon_frame(mouth_open=2, eye_fierce=True, shift_left=shift_left)
        current_dragon_width = max(len(strip_ansi(l)) for l in frame_lines)
        sword_p = end_pos if end_pos >= current_dragon_width + length else None  # disappear when fire reaches
        out = render_frame_padded(frame_lines, fire_cols=length, flame_colors=flame_colors, shake=random.randint(0, 3), extra_line=colored("Counter fire!", RED), sword_pos=sword_p, sword_row_offset=sword_row_offset, sword_color=sword_color, sword_lines=SWORD_BASE)
        sys.stdout.write(out)
        sys.stdout.flush()
        time.sleep(0.05)

    # Return to normal
    for _ in range(5):
        shift_left = max(0, shift_left - (max_shift // 5))
        frame_lines = dragon_frame(shift_left=shift_left)
        out = render_frame_padded(frame_lines, fire_cols=0, shake=0, extra_line=colored("Victory!", GREEN))
        sys.stdout.write(out)
        sys.stdout.flush()
        time.sleep(0.1)

    sys.stdout.write(SHOW_CURSOR)

def animate_get_hit_by_sword():
    cols, rows = get_term_size()
    if rows < len(DRAGON_BASE) + 4 or cols < 60:
        sys.stdout.write("Please enlarge the terminal (>=60 cols, more recommended) and re-run.\n")
        return

    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.write(CLEAR_SCREEN + CURSOR_HOME)
    sys.stdout.flush()

    sword_row_offset = 6  # Align with dragon's head
    sword_color = BOLD + RED
    dragon_width = max(len(strip_ansi(l)) for l in DRAGON_BASE)
    start_pos = cols - max(len(l) for l in SWORD_BASE) - 5
    end_pos = dragon_width - 10  # allow overlap for hit
    steps = 30
    step_delta = (start_pos - end_pos) / (steps - 1) if steps > 1 else 0
    pos = start_pos
    hit_step = steps - 5  # near end
    hurt = False
    shake = 0

    for step in range(steps):
        if step > hit_step:
            hurt = True
            shake = random.randint(5, 10)
            sword_p = None  # hide sword on impact
        else:
            hurt = False
            shake = 0
            sword_p = pos if pos >= dragon_width else None

        frame_lines = dragon_frame(eye_fierce=True, hurt=hurt)
        out = render_frame_padded(frame_lines, fire_cols=0, shake=shake, extra_line=colored("Getting hit!", RED), sword_pos=sword_p, sword_row_offset=sword_row_offset, sword_color=sword_color, sword_lines=SWORD_BASE)
        sys.stdout.write(out)
        sys.stdout.flush()
        time.sleep(0.1)
        pos -= step_delta

    # Recovery
    for _ in range(10):
        shake = max(0, shake - 1)
        frame_lines = dragon_frame(hurt=True if _ < 5 else False, mouth_open=0)
        out = render_frame_padded(frame_lines, fire_cols=0, shake=shake, extra_line=colored("Ouch!", RED))
        sys.stdout.write(out)
        sys.stdout.flush()
        time.sleep(0.15)

    sys.stdout.write(SHOW_CURSOR)

def animate_fumble_fire():
    cols, rows = get_term_size()
    if rows < len(DRAGON_BASE) + 4 or cols < 60:
        sys.stdout.write("Please enlarge the terminal (>=60 cols, more recommended) and re-run.\n")
        return

    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.write(CLEAR_SCREEN + CURSOR_HOME)
    sys.stdout.flush()

    # Idle start
    frame_lines = dragon_frame(mouth_open=0, eye_fierce=False)
    out = render_frame_padded(frame_lines, fire_cols=0, shake=0, extra_line=colored("Preparing fire...", DARK_GRAY))
    sys.stdout.write(out)
    sys.stdout.flush()
    time.sleep(1)

    # Buildup
    roar_build_steps = 6
    phase = 0
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

    # Fumble fire: expand a bit, then fizzle
    dragon_width = max(len(strip_ansi(l)) for l in DRAGON_BASE)
    max_fire_len = 10  # small max
    flame_colors = [YELLOW, ORANGE, RED, MAGENTA]
    for length in range(0, max_fire_len + 1):
        frame_lines = dragon_frame(idle_phase=phase, mouth_open=2, eye_fierce=True)
        out = render_frame_padded(frame_lines, fire_cols=length, flame_colors=flame_colors, shake=random.randint(0, 3), extra_line=colored("Firing... oh no!", RED))
        sys.stdout.write(out)
        sys.stdout.flush()
        time.sleep(0.05)
        phase += 1

    # Fizzle: reduce with smoke
    for fade in range(max_fire_len, 0, -1):
        smoke_colors = [DARK_GRAY, DARK_GRAY, MAGENTA]
        frame_lines = dragon_frame(idle_phase=phase, mouth_open=1, eye_fierce=False)
        out = render_frame_padded(frame_lines, fire_cols=fade, flame_colors=smoke_colors, shake=0, extra_line=colored("Fumbled! (cough)", DARK_GRAY))
        sys.stdout.write(out)
        sys.stdout.flush()
        time.sleep(0.1)
        phase += 1

    # Cooldown
    frame_lines = dragon_frame(mouth_open=0, eye_fierce=False)
    out = render_frame_padded(frame_lines, fire_cols=0, shake=0, extra_line=colored("------   (dragon embarrassed)", DARK_GRAY))
    sys.stdout.write(out)
    sys.stdout.flush()
    time.sleep(1.5)

    sys.stdout.write(SHOW_CURSOR)

def animate_all():
    animate_emerge_from_binary()
    animate_dodge_sword()
    animate_dodge_and_counter_sword()
    animate_fumble_fire()
    animate_get_hit_by_sword()
    animate_hit(1)