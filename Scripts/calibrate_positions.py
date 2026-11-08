#!/usr/bin/env python3
"""
calibrate_positions.py

Interactive tool to calibrate exact mouse coordinates on your screen for:
0. New Note button
1. Title input
2. Text input
3. Keyword add positions (1 through 8)
4. Save button

Saves coordinates directly into POS/COORDINATES_CONFIG.json.
"""

import json
import os
import sys
import time

try:
    from pynput.mouse import Controller as MouseController
except ImportError:
    print("pynput is required. Install via: pip install pynput", file=sys.stderr)
    sys.exit(1)

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "POS", "COORDINATES_CONFIG.json")

def get_mouse_pos_after_delay(label, countdown=4):
    mouse = MouseController()
    print(f"\n[TARGET] Move your mouse to: {label}")
    for i in range(countdown, 0, -1):
        print(f"  Recording in {i} seconds...", end="\r", flush=True)
        time.sleep(1)
    pos = mouse.position
    print(f"  Captured {label} at: x={int(pos[0])}, y={int(pos[1])}")
    return {"x": int(pos[0]), "y": int(pos[1])}

def run_calibration():
    print("==================================================")
    print("Character.ai Lorebook Position Calibration Tool")
    print("Make sure your browser with C.ai Lorebook is open.")
    print("==================================================")
    
    config = {}
    config["description"] = "Calibrated screen coordinates for Character.ai Lorebook note entry."
    
    # 0. New Note button
    config["new_note_button"] = get_mouse_pos_after_delay("0. New Note button")
    
    # 1. Title input
    config["title_input"] = get_mouse_pos_after_delay("1. Title input box")
    
    # 2. Text input
    config["text_input"] = get_mouse_pos_after_delay("2. Text input box")
    
    # 3. Keyword add positions 1-8
    keyword_positions = []
    print("\nNext, record Keyword add positions (1 to 8). If keyword boxes are sequential, record each.")
    for idx in range(1, 9):
        resp = input(f"Calibrate Keyword position {idx}? [Y/n/stop]: ").strip().lower()
        if resp == "stop":
            break
        if resp == "n":
            continue
        pos = get_mouse_pos_after_delay(f"3. Keyword input position {idx}")
        keyword_positions.append(pos)
    
    config["keyword_inputs"] = keyword_positions
    
    # 4. Save button
    config["save_button"] = get_mouse_pos_after_delay("4. Save button")
    
    config["delay_between_actions"] = 0.4
    config["delay_after_save"] = 1.5

    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    print(f"\nConfiguration successfully saved to {CONFIG_PATH}")

if __name__ == "__main__":
    run_calibration()
