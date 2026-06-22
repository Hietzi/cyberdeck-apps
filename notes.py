# notes.py - CyberDeck Notes Browser (Landscape Overhaul)
import os
import time
from st7735 import BLACK, WHITE, GREEN, GREY, DARKGREY, CYAN

NOTES_DIR = "/notes"
HEADER_H = 14
FOOTER_H = 12
ITEM_H = 14
MAX_VISIBLE = 6

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
    # Zeilenweises Splitten für das Querformat (ca. 20 Zeichen pro Zeile bei 160px Breite)
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
    
    last_l = last_r = last_s = 1
    
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
            
        # Reader Footer
        tft.fill_rect(0, H - FOOTER_H, W, FOOTER_H, BLACK)
        tft.line(0, H - FOOTER_H, W, H - FOOTER_H, DARKGREY)
        tft.text("L/R: Pages  SEL: Close Note", 4, H - FOOTER_H + 2, GREY)
        tft.show()
        
        while True:
            l = BTN_LEFT.value()
            r = BTN_RIGHT.value()
            s = BTN_SELECT.value()
            
            if last_l == 1 and l == 0:
                page = max(0, page - 1)
                time.sleep_ms(150); break
            if last_r == 1 and r == 0:
                page = min(total_pages - 1, page + 1)
                time.sleep_ms(150); break
            if last_s == 1 and s == 0:
                time.sleep_ms(100)
                return # Zurück zur Dateiliste
                
            last_l = l; last_r = r; last_s = s
            time.sleep_ms(10)

# Main File Browser Loop
sel = 0
last_l = last_r = last_s = 1

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
        while BTN_SELECT.value() == 1: time.sleep_ms(10)
        time.sleep_ms(150)
        break
        
    # Zeichne Dateiliste im Stil des Hauptmenüs (Fullscreen Landscape)
    tft.fill(BLACK)
    tft.fill_rect(0, 0, W, HEADER_H, GREEN)
    tft.text("NOTES BROWSER", 4, 3, BLACK)
    
    # Scroll-Indizierung
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
            
    # Scrollbar rechts
    if len(files) > MAX_VISIBLE:
        sb_h = max(10, (MAX_VISIBLE * 90) // len(files))
        sb_y = HEADER_H + 4 + ((sel * (90 - sb_h)) // (len(files) - 1))
        tft.fill_rect(W - 4, HEADER_H + 4, 2, 90, DARKGREY)
        tft.fill_rect(W - 4, sb_y, 2, sb_h, GREEN)
        
    # Footer mit Exit-Hinweis über Button-Akkord oder langes Drücken
    tft.fill_rect(0, H - FOOTER_H, W, FOOTER_H, BLACK)
    tft.line(0, H - FOOTER_H, W, H - FOOTER_H, DARKGREY)
    tft.text("L/R: Nav SEL: Open (L+R: Exit)", 4, H - FOOTER_H + 2, GREY)
    tft.show()
    
    # Navigation Logik
    action = None
    while True:
        l = BTN_LEFT.value()
        r = BTN_RIGHT.value()
        s = BTN_SELECT.value()
        
        if l == 0 and r == 0: # Akkord zum Beenden
            action = "EXIT"
            time.sleep_ms(200); break
        if last_l == 1 and l == 0:
            sel = (sel - 1) % len(files)
            time.sleep_ms(150); break
        if last_r == 1 and r == 0:
            sel = (sel + 1) % len(files)
            time.sleep_ms(150); break
        if last_s == 1 and s == 0:
            action = "OPEN"
            time.sleep_ms(100); break
            
        last_l = l; last_r = r; last_s = s
        time.sleep_ms(10)
        
    if action == "EXIT":
        break
    if action == "OPEN":
        content = read_note_file(files[sel])
        view_note(files[sel], content)
