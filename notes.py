# notes.py - CyberDeck Notes Viewer
# Verfügbar: tft, W, H, BTN_LEFT, BTN_SELECT, BTN_RIGHT

import os
import time

# Farben (byte-swapped für Framebuffer)
def _c(color):
    return ((color & 0xFF) << 8) | (color >> 8)

BLACK  = _c(0x0000)
WHITE  = _c(0xFFFF)
GREEN  = _c(0x07E0)
CYAN   = _c(0x07FF)
YELLOW = _c(0xFFE0)
RED    = _c(0xF800)
DARK   = _c(0x18C3)

NOTES_DIR = "/notes"

HEADER_H = 12
LINE_H   = 10
LINES    = (H - HEADER_H - 12) // LINE_H

def wait_release():
    time.sleep_ms(80)
    while BTN_LEFT.value() == 0 or BTN_SELECT.value() == 0 or BTN_RIGHT.value() == 0:
        time.sleep_ms(10)
    time.sleep_ms(80)

def get_notes():
    try:
        files = []
        for f in os.listdir(NOTES_DIR):
            if f.lower().endswith(".txt"):
                files.append(f)
        files.sort()
        return files
    except:
        return []

def draw_header(title):
    tft.fill_rect(0, 0, W, HEADER_H, DARK)
    tft.text(title[:24], 2, 2, CYAN)

def draw_status(txt):
    tft.fill_rect(0, H - 12, W, 12, BLACK)
    tft.text(txt[:26], 2, H - 10, GREEN)

def menu(files, sel):
    tft.fill(BLACK)
    draw_header("NOTES")

    for i, f in enumerate(files):
        y = HEADER_H + 4 + i * 11

        if y > H - 14:
            break

        if i == sel:
            tft.fill_rect(0, y - 1, W, 10, DARK)
            tft.text("> " + f[:20], 2, y, YELLOW)
        else:
            tft.text("  " + f[:20], 2, y, WHITE)

    draw_status("L/R nav SEL open")
    tft.show()

def load_note(filename):
    try:
        with open(NOTES_DIR + "/" + filename, "r") as f:
            return f.read()
    except:
        return "Failed to open file."

def wrap_text(text):
    lines = []

    for raw in text.split("\n"):
        while len(raw) > 25:
            lines.append(raw[:25])
            raw = raw[25:]
        lines.append(raw)

    return lines

def view_note(filename):
    lines = wrap_text(load_note(filename))
    page = 0

    while True:
        tft.fill(BLACK)

        draw_header(filename[:20])

        start = page * LINES

        for i in range(LINES):
            idx = start + i
            if idx >= len(lines):
                break

            tft.text(lines[idx], 2,
                     HEADER_H + 2 + i * LINE_H,
                     WHITE)

        pages = max(1, (len(lines) + LINES - 1) // LINES)

        draw_status(
            str(page + 1) + "/" +
            str(pages) +
            " SEL back"
        )

        tft.show()

        last_l = BTN_LEFT.value()
        last_r = BTN_RIGHT.value()
        last_s = BTN_SELECT.value()

        while True:
            l = BTN_LEFT.value()
            r = BTN_RIGHT.value()
            s = BTN_SELECT.value()

            if last_l == 1 and l == 0:
                if page > 0:
                    page -= 1
                wait_release()
                break

            if last_r == 1 and r == 0:
                if page < pages - 1:
                    page += 1
                wait_release()
                break

            if last_s == 1 and s == 0:
                wait_release()
                return

            last_l = l
            last_r = r
            last_s = s

            time.sleep_ms(20)

def run():
    files = get_notes()

    if not files:
        tft.fill(BLACK)
        draw_header("NOTES")
        tft.text("No .txt files", 20, 40, RED)
        tft.text("in /notes", 32, 52, WHITE)
        tft.show()
        wait_release()
        return

    sel = 0

    while True:
        menu(files, sel)

        last_l = BTN_LEFT.value()
        last_r = BTN_RIGHT.value()
        last_s = BTN_SELECT.value()

        while True:
            l = BTN_LEFT.value()
            r = BTN_RIGHT.value()
            s = BTN_SELECT.value()

            if last_l == 1 and l == 0:
                sel = (sel - 1) % len(files)
                wait_release()
                break

            if last_r == 1 and r == 0:
                sel = (sel + 1) % len(files)
                wait_release()
                break

            if last_s == 1 and s == 0:
                wait_release()
                view_note(files[sel])
                break

            last_l = l
            last_r = r
            last_s = s

            time.sleep_ms(20)

run()
