#!/usr/bin/env python3
"""Simple recorder using pynput that outputs a pyautogui macro.

Controls:
- Left mouse click: record a click at that position
- Ctrl (left or right): record current mouse position as a named position (POS1...)
- Shift (left or right): record a placeholder for typed text (VAR1...)
- Alt (left or right): stop recording and write `macro.py`

Usage: python recorder.py

The generated `macro.py` will contain a sequence of pyautogui calls and a prompt for any placeholders.
"""
import sys
import json
from pathlib import Path
from pynput import mouse, keyboard

OUT_FILE = Path('macro.py')

actions = []
positions = []
placeholders = []

print('Recorder started.')
print('Controls: Left-click to record click, Ctrl to save position, Shift to add text-placeholder, Alt to stop and save.')

def on_click(x, y, button, pressed):
    # Only record on press events
    if pressed and button == mouse.Button.left:
        print(f'Recorded click at {x},{y}')
        actions.append({'type': 'click', 'pos': (x, y)})

def on_press(key):
    try:
        k = key.char
    except Exception:
        k = None

    # Ctrl -> save current mouse position as POSn
    if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
        # get current mouse position
        from pynput.mouse import Controller
        mc = Controller()
        pos = mc.position
        positions.append(pos)
        name = f'POS{len(positions)}'
        print(f'Saved position {name}: {pos}')
        actions.append({'type': 'position', 'name': name, 'pos': pos})

    # Shift -> placeholder for text input
    if key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
        name = f'VAR{len(placeholders)+1}'
        placeholders.append(name)
        print(f'Added placeholder {name}')
        actions.append({'type': 'placeholder', 'name': name})

    # Alt -> stop recording
    if key in (keyboard.Key.alt_l, keyboard.Key.alt_r):
        print('Stop key pressed. Writing macro and exiting...')
        write_macro()
        # stop listeners by returning False from both listeners (we'll stop externally)
        return False

def write_macro():
    # Build macro file content
    lines = []
    lines.append('import pyautogui')
    lines.append('import time')
    lines.append('')
    # placeholders prompt
    if placeholders:
        lines.append('# Prompt for placeholder values')
        for p in placeholders:
            lines.append(f"{p} = input('Enter value for {p}: ')")
        lines.append('')

    # positions as variables
    if positions:
        for i, pos in enumerate(positions, start=1):
            lines.append(f'POS{i} = {pos}')
        lines.append('')

    lines.append('time.sleep(1)  # short delay before starting')
    lines.append('')
    for a in actions:
        if a['type'] == 'click':
            x, y = a['pos']
            lines.append(f'pyautogui.click({x}, {y})')
            lines.append('time.sleep(0.15)')
        elif a['type'] == 'position':
            # using positions already declared as POSn; no action emitted by saving a position
            lines.append(f'# saved position {a["name"]} = {a["pos"]}')
        elif a['type'] == 'placeholder':
            lines.append(f"# placeholder {a['name']} - type where needed")
            # by default, type placeholder value
            lines.append(f'pyautogui.typewrite(str({a["name"]}))')
            lines.append('time.sleep(0.15)')

    if not actions:
        lines.append("print('No actions recorded')")

    OUT_FILE.write_text('\n'.join(lines), encoding='utf-8')
    print(f'Wrote macro to {OUT_FILE.resolve()}')


def main():
    # Setup listeners
    kb_listener = keyboard.Listener(on_press=on_press)
    ms_listener = mouse.Listener(on_click=on_click)

    kb_listener.start()
    ms_listener.start()

    # Wait until keyboard listener stops (on Alt press we return False)
    kb_listener.join()
    # stop mouse listener as well
    ms_listener.stop()
    print('Recorder finished.')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted by user')
