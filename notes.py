# notes.py - CyberDeck Notes Browser (Landscape Overhaul with Debounce)
import os
import time
from st7735 import BLACK, WHITE, GREEN, GREY, DARKGREY, CYAN

NOTES_DIR = "/notes"
HEADER_H = 14
FOOTER_H = 12
ITEM_H = 14
MAX_VISIBLE = 6

# --- Debounce & Hardware Safety Logic ---
DEBOUNCE_MS = 200
last_press_time = 0

def btn_pressed(btn):
    global last_press_time
    now = time.ticks_ms()
    if time.ticks_diff(now, last_press_time) < DEBOUNCE_MS:
        return False
    if btn.value() == 0:
        time.sleep_ms(20)
        if btn.value() == 0:
            last_press_time = time.ticks_ms()
            return True
    return False

def wait_btn_release(btn):
    while btn.value() == 0:
        time.sleep_ms(10)

def get_notes():
    try:
        return [f for f in os.listdir(NOTES_DIR) if f.lower().endswith(".txt")]
    except:
        try: os.mkdir(NOTES_DIR)
        except: pass
        return []

def read_note_file(filename):
    try:
        with open(NOTES_DIR + "/" + filename, "r") as f:
            return f.read()
    except:
        return "Fehler beim Lesen!"

def view_note(filename, content):
    words = content.replace("\n", " \n ").split(" ")
    lines = []
    curr_line = ""
    
    for w in words:
        if w == "\n":
            lines.append(curr_line)
            curr_line = ""
        elif len(curr_line) + len(w) < 19:
            curr_line += w + " "
        else:
            lines.append(curr_line)
            curr_line = w + " "
    if curr_line:
        lines.append(curr_line)
        
    lines_per_page = 8
    page = 0
    total_pages = max(1, (len(lines) + lines_per_page - 1) // lines_per_page)
    
    while True:
        tft.fill(BLACK)
        tft.fill_rect(0, 0, W, HEADER_H, CYAN)
        tft.text(filename[:16], 4, 3, BLACK)
        tft.text("{}/{}".format(page+1, total_pages), W - 35, 3, BLACK)
        
        start = page * lines_per_page
        for i in range(lines_per_page):
            idx = start + i
            if idx >= len(lines): break
            tft.text(lines[idx], 4, HEADER_H + 4 + (i * 11), WHITE)
            
        tft.fill_rect(0, H - FOOTER_H, W, FOOTER_H, BLACK)
        tft.line(0, H - FOOTER_H, W, H - FOOTER_H, DARKGREY)
        tft.text("L/R: Pages  SEL: Close Note", 4, H - FOOTER_H + 2, GREY)
        tft.show()
        
        while True:
            if btn_pressed(BTN_LEFT):
                page = max(0, page - 1)
                wait_btn_release(BTN_LEFT)
                break
            if btn_pressed(BTN_RIGHT):
                page = min(total_pages - 1, page + 1)
                wait_btn_release(BTN_RIGHT)
                break
            if btn_pressed(BTN_SELECT):
                wait_btn_release(BTN_SELECT)
                return 
            time.sleep_ms(10)

# Main File Browser Loop
sel = 0

while True:
    files = get_notes()
    if not files:
        tft.fill(BLACK)
        tft.fill_rect(0, 0, W, HEADER_H, GREEN)
        tft.text("NOTES BROWSER", 4, 3, BLACK)
        tft.text("Keine Notizen (.txt)", 4, 40, RED)
        tft.text("Ordner: /notes/", 4, 55, WHITE)
        tft.fill_rect(0, H - FOOTER_H, W, FOOTER_H, BLACK)
        tft.line(0, H - FOOTER_H, W, H - FOOTER_H, DARKGREY)
        tft.text("SEL: Exit to Menu", 4, H - FOOTER_H + 2, GREY)
        tft.show()
        
        while not btn_pressed(BTN_SELECT):
            time.sleep_ms(10)
        wait_btn_release(BTN_SELECT)
        break
        
    tft.fill(BLACK)
    tft.fill_rect(0, 0, W, HEADER_H, GREEN)
    tft.text("NOTES BROWSER", 4, 3, BLACK)
    
    start_idx = 0
    if len(files) > MAX_VISIBLE:
        if sel >= MAX_VISIBLE - 2:
            start_idx = min(sel - (MAX_VISIBLE - 3), len(files) - MAX_VISIBLE)
            
    for idx in range(MAX_VISIBLE):
        f_idx = start_idx + idx
        if f_idx >= len(files): break
        name = files[f_idx]
        y = HEADER_H + 4 + (idx * ITEM_H)
        
        if f_idx == sel:
            tft.fill_rect(0, y, W - 6, ITEM_H, DARKGREY)
            tft.fill_rect(0, y, 3, ITEM_H, GREEN)
            tft.text(name[:22], 8, y + 3, GREEN)
        else:
            tft.text(name[:22], 8, y + 3, WHITE)
            
    if len(files) > MAX_VISIBLE:
        sb_h = max(10, (MAX_VISIBLE * 90) // len(files))
        sb_y = HEADER_H + 4 + ((sel * (90 - sb_h)) // (len(files) - 1))
        tft.fill_rect(W - 4, HEADER_H + 4, 2, 90, DARKGREY)
        tft.fill_rect(W - 4, sb_y, 2, sb_h, GREEN)
        
    tft.fill_rect(0, H - FOOTER_H, W, FOOTER_H, BLACK)
    tft.line(0, H - FOOTER_H, W, H - FOOTER_H, DARKGREY)
    tft.text("L/R: Nav SEL: Open (L+R: Exit)", 4, H - FOOTER_H + 2, GREY)
    tft.show()
    
    action = None
    while True:
        # L+R Akkord zum Beenden
        if BTN_LEFT.value() == 0 and BTN_RIGHT.value() == 0:
            time.sleep_ms(20)
            if BTN_LEFT.value() == 0 and BTN_RIGHT.value() == 0:
                action = "EXIT"
                wait_btn_release(BTN_LEFT)
                wait_btn_release(BTN_RIGHT)
                break
                
        if btn_pressed(BTN_LEFT):
            sel = (sel - 1) % len(files)
            wait_btn_release(BTN_LEFT)
            break
        if btn_pressed(BTN_RIGHT):
            sel = (sel + 1) % len(files)
            wait_btn_release(BTN_RIGHT)
            break
        if btn_pressed(BTN_SELECT):
            action = "OPEN"
            wait_btn_release(BTN_SELECT)
            break
        time.sleep_ms(10)
        
    if action == "EXIT":
        break
    if action == "OPEN":
        content = read_note_file(files[sel])
        view_note(files[sel], content)
