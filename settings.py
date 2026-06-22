# settings.py - CyberDeck Settings App (Landscape Overhaul)
import time
import json
import network
from st7735 import BLACK, WHITE, GREEN, RED, CYAN, GREY, DARKGREY

HEADER_H = 14
FOOTER_H = 12
ITEM_H = 14

CHARSET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?@#*-_"

def load_settings():
    try:
        with open("/settings.json") as f:
            return json.load(f)
    except:
        return {"ssid": "", "pass": ""}

def save_settings(s):
    try:
        with open("/settings.json", "w") as f:
            json.dump(s, f)
    except:
        pass

def input_text(title, default=""):
    text = list(default)
    ci = 0
    last_l = last_r = last_s = 1
    
    while True:
        tft.fill(BLACK)
        tft.fill_rect(0, 0, W, HEADER_H, CYAN)
        tft.text("EDIT: " + title, 4, 3, BLACK)
        
        # Aktueller Text-String mittig anzeigen
        curr_str = "".join(text) + "_"
        tft.text(curr_str[-18:], 8, 30, WHITE)
        
        # Zeichen-Auswahl-Rad im Querformat breiter fächern
        # Zeige vorherige, aktuelles und nächste Zeichen an
        for i in range(-4, 5):
            idx = (ci + i) % len(CHARSET)
            char = CHARSET[idx]
            x = 80 + (i * 14)
            if i == 0:
                tft.fill_rect(x - 2, 58, 12, 14, DARKGREY)
                tft.text(char, x, 61, GREEN)
            else:
                tft.text(char, x, 61, GREY)
                
        # Steuerungs-Hinweis im Footer
        tft.fill_rect(0, H - FOOTER_H, W, FOOTER_H, BLACK)
        tft.line(0, H - FOOTER_H, W, H - FOOTER_H, DARKGREY)
        tft.text("L/R: Scroll  SEL: Add (Hold->OK)", 4, H - FOOTER_H + 2, GREY)
        tft.show()
        
        # Button-Logik mit Long-Press Erkennung für Bestätigung
        while True:
            l = BTN_LEFT.value()
            r = BTN_RIGHT.value()
            s = BTN_SELECT.value()
            
            if last_l == 1 and l == 0:
                ci = (ci - 1) % len(CHARSET)
                time.sleep_ms(100); break
            if last_r == 1 and r == 0:
                ci = (ci + 1) % len(CHARSET)
                time.sleep_ms(100); break
                
            if last_s == 1 and s == 0:
                t0 = time.ticks_ms()
                while BTN_SELECT.value() == 0:
                    time.sleep_ms(10)
                dur = time.ticks_diff(time.ticks_ms(), t0)
                
                if dur > 600: # Langer Klick = Fertig!
                    return "".join(text)
                else: # Kurzer Klick = Zeichen hinzufügen / löschen bei Backspace-Logik (hier simulieren wir Löschen, wenn man ganz am Ende klickt oder ein bestimmtes Zeichen wählt. Machen wir es einfacher: Wenn Text leer ist, gehts zurück, oder wir fügen an)
                    # Wenn wir das letzte Zeichen wählen und es gibt Text, löschen wir das letzte als Shortcut per Akkord (L+R zum Löschen)
                    text.append(CHARSET[ci])
                    break
                    
            # Akkord-Löschen Shortcut: Wenn Links+Rechts gedrückt wird, letztes Zeichen löschen!
            if l == 0 and r == 0:
                if len(text) > 0:
                    text.pop()
                time.sleep_ms(200); break
                
            last_l = l; last_r = r; last_s = s
            time.sleep_ms(10)

def draw_menu(items, selected, cfg):
    tft.fill(BLACK)
    tft.fill_rect(0, 0, W, HEADER_H, GREEN)
    tft.text("SETTINGS CONFIG", 4, 3, BLACK)
    
    for i, item in enumerate(items):
        y = HEADER_H + 6 + (i * ITEM_H)
        if i == selected:
            tft.fill_rect(0, y, W, ITEM_H, DARKGREY)
            tft.fill_rect(0, y, 3, ITEM_H, GREEN)
            tft.text(item, 8, y + 3, GREEN)
        else:
            tft.text(item, 8, y + 3, WHITE)
            
    # Aktuelle Konfiguration ganz unten anzeigen
    tft.line(0, 85, W, 85, DARKGREY)
    tft.text("SSID: " + cfg["ssid"][:16], 4, 90, GREY)
    tft.text("PASS: " + ("*" * min(8, len(cfg["pass"]))), 4, 102, GREY)
    
    # Footer
    tft.fill_rect(0, H - FOOTER_H, W, FOOTER_H, BLACK)
    tft.line(0, H - FOOTER_H, W, H - FOOTER_H, DARKGREY)
    tft.text("L/R: Nav  SEL: Select Option", 4, H - FOOTER_H + 2, GREY)
    tft.show()

# Main Flow
cfg = load_settings()
ITEMS = ["1. Edit SSID", "2. Edit Password", "3. Save & Connect", "4. Exit to Menu"]
sel = 0
last_l = last_r = last_s = 1

while True:
    draw_menu(ITEMS, sel, cfg)
    
    while True:
        l = BTN_LEFT.value()
        r = BTN_RIGHT.value()
        s = BTN_SELECT.value()
        
        if last_l == 1 and l == 0:
            sel = (sel - 1) % len(ITEMS)
            time.sleep_ms(150); break
        if last_r == 1 and r == 0:
            sel = (sel + 1) % len(ITEMS)
            time.sleep_ms(150); break
            
        if last_s == 1 and s == 0:
            time.sleep_ms(150)
            if sel == 0:
                cfg["ssid"] = input_text("SSID", cfg["ssid"])
            elif sel == 1:
                cfg["pass"] = input_text("Password", cfg["pass"])
            elif sel == 2:
                save_settings(cfg)
                tft.fill(BLACK)
                tft.fill_rect(0, 0, W, HEADER_H, GREEN)
                tft.text("Saving...", 4, 3, BLACK)
                tft.show()
                time.sleep(1.0)
                # Direktes Beenden nach Save oder zurück zum Menü
            elif sel == 3:
                pass # Bricht den äußeren Loop via Condition ab
            break
            
        last_l = l; last_r = r; last_s = s
        time.sleep_ms(10)
        
    if last_s == 0 and sel == 3: # Exit ausgewählt
        break
    if last_s == 0 and sel == 2: # Nach dem Speichern auch ins Hauptmenü zurück
        break
