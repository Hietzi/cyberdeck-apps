# calculator.py - CyberDeck Taschenrechner
# Verfügbar: tft, W, H, BTN_LEFT, BTN_SELECT, BTN_RIGHT

import time

def _c(color):
    return ((color & 0xFF) << 8) | (color >> 8)

BLACK    = _c(0x0000)
WHITE    = _c(0xFFFF)
GREEN    = _c(0x07E0)
RED      = _c(0xF800)
CYAN     = _c(0x07FF)
YELLOW   = _c(0xFFE0)
GREY     = _c(0x8410)
DARKGREY = _c(0x4208)
ORANGE   = _c(0xFD20)

# Tasten-Grid
KEYS = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "=", "+"],
    ["C", "+/-", "DEL", "()"],
]
COLS = 4
ROWS = len(KEYS)

KEY_W = W // COLS
KEY_H = 18

DISPLAY_H = 36

def _key_color(k):
    if k in "+-*/":   return ORANGE
    if k == "=":       return GREEN
    if k in ("C","DEL","()"): return RED
    if k == "+/-":     return CYAN
    return DARKGREY

def _draw_display(expr, result):
    tft.fill_rect(0, 0, W, DISPLAY_H, BLACK)
    # Ausdruck
    disp = expr[-20:] if len(expr) > 20 else expr
    tft.text(disp or "0", 2, 4, WHITE)
    # Ergebnis
    tft.fill_rect(0, 18, W, 16, _c(0x1082))
    tft.text(str(result)[:20], 2, 20, GREEN)

def _draw_keys(cx, cy):
    y0 = DISPLAY_H + 2
    for r, row in enumerate(KEYS):
        for c, k in enumerate(row):
            x = c * KEY_W
            y = y0 + r * KEY_H
            bg = GREY if (c == cx and r == cy) else _key_color(k)
            tft.fill_rect(x+1, y+1, KEY_W-2, KEY_H-2, bg)
            tx = x + (KEY_W - len(k)*6) // 2
            ty = y + (KEY_H - 8) // 2
            fg = BLACK if (c == cx and r == cy) else WHITE
            tft.text(k, tx, ty, fg)

def _calc(expr):
    try:
        # Sicherheitscheck
        allowed = set("0123456789.+-*/() ")
        if not all(ch in allowed for ch in expr):
            return "Fehler"
        result = eval(expr)
        if isinstance(result, float):
            if result == int(result):
                return str(int(result))
            return "%.4g" % result
        return str(result)
    except ZeroDivisionError:
        return "Div/0"
    except:
        return "Fehler"

expr   = ""
result = "0"
cx, cy = 0, 0
last_l = last_r = last_s = 1
open_parens = 0

while True:
    _draw_display(expr, result)
    _draw_keys(cx, cy)
    tft.show()

    while True:
        l = BTN_LEFT.value()
        r = BTN_RIGHT.value()
        s = BTN_SELECT.value()

        if last_l == 1 and l == 0:
            cx = (cx - 1) % COLS
            time.sleep_ms(130); break

        if last_r == 1 and r == 0:
            cx = (cx + 1) % COLS
            time.sleep_ms(130); break

        if last_s == 1 and s == 0:
            time.sleep_ms(50)
            # Lange gedrückt = Zeile wechseln
            t0 = time.ticks_ms()
            while BTN_SELECT.value() == 0:
                time.sleep_ms(10)
            held = time.ticks_diff(time.ticks_ms(), t0)

            if held > 500:
                cy = (cy + 1) % ROWS
            else:
                k = KEYS[cy][cx]
                if k == "C":
                    expr = ""; result = "0"; open_parens = 0
                elif k == "DEL":
                    expr = expr[:-1]
                    result = _calc(expr) if expr else "0"
                elif k == "=":
                    result = _calc(expr)
                    if result not in ("Fehler", "Div/0"):
                        expr = result
                        result = ""
                elif k == "+/-":
                    if expr and expr[0] == "-":
                        expr = expr[1:]
                    else:
                        expr = "-" + expr
                elif k == "()":
                    if open_parens == 0 or (expr and expr[-1] in "0123456789)"):
                        expr += "("
                        open_parens += 1
                    else:
                        expr += ")"
                        open_parens -= 1
                else:
                    expr += k
                    result = _calc(expr) if expr else "0"
            break

        last_l = l; last_r = r; last_s = s
        time.sleep_ms(10)
