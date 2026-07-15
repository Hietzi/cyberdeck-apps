# settings.py - CyberDeck Settings App (Landscape Overhaul with Debounce)
import time
import json
import network
from st7735 import BLACK, WHITE, GREEN, RED, CYAN, GREY, DARKGREY

HEADER_H = 14
FOOTER_H = 12
ITEM_H = 14

CHARSET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?@#*-_"

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
    
    while True:
        tft.fill(BLACK)
        tft.fill_rect(0, 0, W, HEADER_H, CYAN)
        tft.text("EDIT: " + title, 4, 3, BLACK)
        
        curr_str = "".join(text) + "_"
        tft.text(curr_str[-18:], 8, 30, WHITE)
        
        for i in range(-4, 5):
            idx = (ci + i) % len(CHARSET)
            char = CHARSET[idx]
            x = 80 + (i * 14)
            if i == 0:
                tft.fill_rect(x - 2, 58, 12, 14, DARKGREY)
                tft.text(char, x, 61, GREEN)
            else:
                tft.text(char, x, 61, GREY)
                
        tft.fill_rect(0, H - FOOTER_H, W, FOOTER_H, BLACK)
        tft.line(0, H - FOOTER_H, W, H - FOOTER_H, DARKGREY)
        tft.text("L/R: Scroll  SEL: Add (Hold->OK)", 4, H - FOOTER_H + 2, GREY)
        tft.show()
        
        while True:
            # L+R Akkord löscht das letzte Zeichen
            if BTN_LEFT.value() == 0 and BTN_RIGHT.value() == 0:
                time.sleep_ms(20)
                if BTN_LEFT.value() == 0 and BTN_RIGHT.value() == 0:
                    if len(text) > 0:
                        text.pop()
                    wait_btn_release(BTN_LEFT)
                    wait_btn_release(BTN_RIGHT)
                    break
                    
            if btn_pressed(BTN_LEFT):
                ci = (ci - 1) % len(CHARSET)
                wait_btn_release(BTN_LEFT)
                break
            if btn_pressed(BTN_RIGHT):
                ci = (ci + 1) % len(CHARSET)
                wait_btn_release(BTN_RIGHT)
                break
                
            if btn_pressed(BTN_SELECT):
                t0 = time.ticks_ms()
                wait_btn_release(BTN_SELECT)
                dur = time.ticks_diff(time.ticks_ms(), t0) + 20
                
                if dur > 600: # Langer Klick = Fertig!
                    return "".join(text)
                else: 
                    text.append(CHARSET[ci])
                    break
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
            
    tft.line(0, 85, W, 85, DARKGREY)
    tft.text("SSID: " + cfg["ssid"][:16], 4, 90, GREY)
    tft.text("PASS: " + ("*" * min(8, len(cfg["pass"]))), 4, 102, GREY)
    
    tft.fill_rect(0, H - FOOTER_H, W, FOOTER_H, BLACK)
    tft.line(0, H - FOOTER_H, W, H - FOOTER_H, DARKGREY)
    tft.text("L/R: Nav  SEL: Select Option", 4, H - FOOTER_H + 2, GREY)
    tft.show()

# Main Flow
cfg = load_settings()
ITEMS = ["1. Edit SSID", "2. Edit Password", "3. Save & Connect", "4. Exit to Menu"]
sel = 0

while True:
    draw_menu(ITEMS, sel, cfg)
    
    while True:
        if btn_pressed(BTN_LEFT):
            sel = (sel - 1) % len(ITEMS)
            wait_btn_release(BTN_LEFT)
            break
        if btn_pressed(BTN_RIGHT):
            sel = (sel + 1) % len(ITEMS)
            wait_btn_release(BTN_RIGHT)
            break
            
        if btn_pressed(BTN_SELECT):
            wait_btn_release(BTN_SELECT)
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
            break
        time.sleep_ms(10)
        
    if sel == 3 or sel == 2: # Exit ausgewählt oder gespeichert
        break
