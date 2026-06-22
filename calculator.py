# calculator.py - CyberDeck Calculator (Landscape Overhaul)
import time
from st7735 import BLACK, WHITE, GREEN, RED, CYAN, GREY, DARKGREY, YELLOW

KEYS = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "=", "+"],
    ["C", "DEL", "()", "EXIT"]
]
COLS = 4
ROWS = len(KEYS)

# Tastenabmessungen perfekt für 160px Breite im Querformat ausgelegt
KEY_W = 40  # 4 * 40 = 160 Pixel volle Displaybreite
KEY_H = 16  # 5 * 16 = 80 Pixel Höhe für das Grid
DISPLAY_H = 34 # 128 - 80 - 14 (Footer) = 34 Pixel Displayhöhe

def get_key_color(k):
    if k in "+-*/": return CYAN
    if k == "=": return GREEN
    if k in ("C", "DEL"): return RED
    if k == "EXIT": return YELLOW
    return DARKGREY

def draw_calc_ui(expr, res, cx, cy):
    tft.fill(BLACK)
    
    # 1. Rechen-Display oben
    tft.fill_rect(0, 0, W, DISPLAY_H, BLACK)
    # Ausdruck oben rechtsbündig
    tft.text(expr[-19:], W - (len(expr[-19:]) * 8) - 4, 4, WHITE)
    # Ergebnis darunter rechtsbündig
    if res:
        tft.text(res[-19:], W - (len(res[-19:]) * 8) - 4, 20, GREEN)
        
    tft.line(0, DISPLAY_H, W, DISPLAY_H, GREY)
    
    # 2. Keypad zeichnen
    for r in range(ROWS):
        for c in range(COLS):
            k = KEYS[r][c]
            kx = c * KEY_W
            ky = DISPLAY_H + 1 + (r * KEY_H)
            
            # Highlight für die ausgewählte Taste
            if r == cy and c == cx:
                tft.fill_rect(kx, ky, KEY_W - 1, KEY_H - 1, WHITE)
                tft.text(k, kx + (KEY_W - len(k)*8)//2, ky + 4, BLACK)
            else:
                tft.fill_rect(kx, ky, KEY_W - 1, KEY_H - 1, get_key_color(k))
                tft.text(k, kx + (KEY_W - len(k)*8)//2, ky + 4, WHITE)
                
    tft.show()

def evaluate(expr):
    try:
        # Sicheres Ersetzen für MicroPython's eval
        s = expr.replace(" ", "")
        if not s: return "0"
        return str(eval(s))
    except ZeroDivisionError:
        return "Div/0"
    except:
        return "Error"

# Main Workflow
cx, cy = 0, 0
expr = ""
result = "0"
open_p = 0
last_l = last_r = last_s = 1

while True:
    draw_calc_ui(expr, result, cx, cy)
    
    while True:
        l = BTN_LEFT.value()
        r = BTN_RIGHT.value()
        s = BTN_SELECT.value()
        
        # Navigation innerhalb der Zeile
        if last_l == 1 and l == 0:
            cx = (cx - 1) % COLS
            time.sleep_ms(130); break
        if last_r == 1 and r == 0:
            cx = (cx + 1) % COLS
            time.sleep_ms(130); break
            
        # Bestätigung / Zeilenwechsel
        if last_s == 1 and s == 0:
            t0 = time.ticks_ms()
            while BTN_SELECT.value() == 0:
                time.sleep_ms(10)
            dur = time.ticks_diff(time.ticks_ms(), t0)
            
            if dur > 500:
                # Langer Klick = Zeile nach unten wechseln
                cy = (cy + 1) % ROWS
                time.sleep_ms(50)
            else:
                # Kurzer Klick = Taste ausführen
                k = KEYS[cy][cx]
                if k == "EXIT":
                    cx = -1 # Signalisiert Beenden
                elif k == "C":
                    expr = ""
                    result = "0"
                    open_p = 0
                elif k == "DEL":
                    expr = expr[:-1]
                    result = evaluate(expr) if expr else "0"
                elif k == "=":
                    result = evaluate(expr)
                    if result not in ("Error", "Div/0"):
                        expr = result
                elif k == "()":
                    if open_p == 0 or (expr and expr[-1] in "+-*/("):
                        expr += "("
                        open_p += 1
                    else:
                        expr += ")"
                        open_p -= 1
                else:
                    # Mathematische Operatoren / Zahlen anhängen
                    expr += k
                    if k not in "+-*/":
                        result = evaluate(expr)
            break
            
        last_l = l; last_r = r; last_s = s
        time.sleep_ms(10)
        
    if cx == -1: # EXIT gedrückt
        break
