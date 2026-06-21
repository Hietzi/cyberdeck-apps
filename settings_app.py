# settings.py - CyberDeck Settings App
# Verfügbar: tft, W, H, BTN_LEFT, BTN_SELECT, BTN_RIGHT

import time
import json
import network

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
ACCENT   = GREEN

HEADER_H = 14
ITEM_H   = 13

# ── Settings lesen/schreiben ─────────────────────────────
def load_settings():
    try:
        with open("/settings.json") as f:
            return json.load(f)
    except:
        return {"ssid": "", "pass": ""}

def save_settings(s):
    with open("/settings.json", "w") as f:
        json.dump(s, f)

# ── Char-Eingabe ─────────────────────────────────────────
CHARSET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 !@#$%&*()-_=+[]{}.,?"

def input_text(title, default=""):
    text  = list(default)
    ci    = 0  # cursor in CHARSET
    last_l = last_r = last_s = 1
    sel_start = None

    while True:
        # Draw
        tft.fill(BLACK)
        tft.fill_rect(0, 0, W, HEADER_H, ACCENT)
        tft.text(title, 2, 3, BLACK)

        # Aktueller Text
        display = "".join(text) + "_"
        tft.fill_rect(0, 18, W, 12, DARKGREY)
        tft.text(display[-20:], 2, 20, WHITE)  # max 20 Zeichen anzeigen

        # Aktuelles Zeichen
        tft.text("Zeichen:", 2, 36, GREY)
        tft.fill_rect(60, 34, 20, 12, DARKGREY)
        tft.text(CHARSET[ci], 64, 36, YELLOW)

        tft.text("L:vor R:nach", 2, 52, GREY)
        tft.text("SEL:add", 2, 64, GREY)
        tft.text("LONG SEL:del", 2, 76, GREY)
        tft.text("2xSEL:fertig", 2, 88, CYAN)
        tft.show()

        while True:
            l = BTN_LEFT.value()
            r = BTN_RIGHT.value()
            s = BTN_SELECT.value()

            if last_l == 1 and l == 0:
                ci = (ci - 1) % len(CHARSET)
                time.sleep_ms(120)
                break

            if last_r == 1 and r == 0:
                ci = (ci + 1) % len(CHARSET)
                time.sleep_ms(120)
                break

            if s == 0 and sel_start is None:
                sel_start = time.ticks_ms()

            if s == 1 and sel_start is not None:
                held = time.ticks_diff(time.ticks_ms(), sel_start)
                sel_start = None
                if held > 600:
                    # Long press = backspace
                    if text:
                        text.pop()
                elif held > 1200:
                    # Sehr lang = fertig
                    return "".join(text)
                else:
                    # Doppelklick-Erkennung: zweiter schneller Klick = fertig
                    # Einfacher Klick = Zeichen hinzufügen
                    text.append(CHARSET[ci])
                time.sleep_ms(50)
                break

            # Fertig-Button: SELECT 2x schnell
            # Einfacher Weg: wenn text nicht leer und SELECT kurz nach letztem
            last_l = l; last_r = r; last_s = s
            time.sleep_ms(10)

        last_l = BTN_LEFT.value()
        last_r = BTN_RIGHT.value()
        last_s = BTN_SELECT.value()

# ── WiFi Scanner ─────────────────────────────────────────
def scan_wifi():
    tft.fill(BLACK)
    tft.fill_rect(0, 0, W, HEADER_H, ACCENT)
    tft.text("WiFi Scan", 2, 3, BLACK)
    tft.fill_rect(0, H-12, W, 12, BLACK)
    tft.text("Scanne...", 2, H-10, GREY)
    tft.show()

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    nets = wlan.scan()
    # Sortieren nach Signalstärke
    nets.sort(key=lambda x: x[3], reverse=True)

    if not nets:
        tft.fill_rect(0, H-12, W, 12, BLACK)
        tft.text("Keine Netze!", 2, H-10, RED)
        tft.show()
        time.sleep(2)
        return None

    # Auswahl
    sel = 0
    last_l = last_r = last_s = 1

    while True:
        tft.fill(BLACK)
        tft.fill_rect(0, 0, W, HEADER_H, ACCENT)
        tft.text("Netz waehlen", 2, 3, BLACK)

        for i in range(min(len(nets), 6)):
            n   = nets[i]
            ssid = n[0].decode() if isinstance(n[0], bytes) else n[0]
            rssi = n[3]
            y    = HEADER_H + 2 + i * (ITEM_H + 1)
            if i == sel:
                tft.fill_rect(0, y, W, ITEM_H, DARKGREY)
                tft.text(ssid[:16], 2, y+2, ACCENT)
                tft.text("%d" % rssi, W-28, y+2, GREY)
            else:
                tft.text(ssid[:16], 2, y+2, WHITE)
                tft.text("%d" % rssi, W-28, y+2, GREY)

        tft.fill_rect(0, H-12, W, 12, BLACK)
        tft.text("L/R:nav SEL:ok", 2, H-10, GREY)
        tft.show()

        while True:
            l = BTN_LEFT.value()
            r = BTN_RIGHT.value()
            s = BTN_SELECT.value()
            if last_l == 1 and l == 0:
                sel = (sel - 1) % min(len(nets), 6)
                time.sleep_ms(150); break
            if last_r == 1 and r == 0:
                sel = (sel + 1) % min(len(nets), 6)
                time.sleep_ms(150); break
            if last_s == 1 and s == 0:
                time.sleep_ms(100)
                ssid = nets[sel][0].decode() if isinstance(nets[sel][0], bytes) else nets[sel][0]
                return ssid
            last_l = l; last_r = r; last_s = s
            time.sleep_ms(10)

# ── Haupt-Menu ───────────────────────────────────────────
cfg = load_settings()
ITEMS = ["WiFi SSID", "WiFi Passwort", "WiFi Scan+Set", "Speichern", "Zurueck"]
sel = 0
last_l = last_r = last_s = 1

while True:
    tft.fill(BLACK)
    tft.fill_rect(0, 0, W, HEADER_H, ACCENT)
    tft.text("Settings", 2, 3, BLACK)

    for i, name in enumerate(ITEMS):
        y = HEADER_H + 2 + i * (ITEM_H + 1)
        if i == sel:
            tft.fill_rect(0, y, W, ITEM_H, DARKGREY)
            tft.text("* " + name, 2, y+2, ACCENT)
        else:
            tft.text("  " + name, 2, y+2, WHITE)

    # Aktuelle Werte unten anzeigen
    tft.fill_rect(0, H-24, W, 24, BLACK)
    tft.text("SSID:" + cfg["ssid"][:12], 2, H-22, GREY)
    tft.text("PW:  " + "*" * min(len(cfg["pass"]), 12), 2, H-11, GREY)
    tft.show()

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
            time.sleep_ms(100)
            if sel == 0:
                cfg["ssid"] = input_text("SSID", cfg["ssid"])
            elif sel == 1:
                cfg["pass"] = input_text("Passwort", cfg["pass"])
            elif sel == 2:
                ssid = scan_wifi()
                if ssid:
                    cfg["ssid"] = ssid
                    cfg["pass"] = input_text("Passwort fuer", "")
            elif sel == 3:
                save_settings(cfg)
                tft.fill(BLACK)
                tft.fill_rect(0, 0, W, HEADER_H, ACCENT)
                tft.text("Settings", 2, 3, BLACK)
                tft.text("Gespeichert!", 2, 40, GREEN)
                tft.text("Neustart noetig", 2, 56, GREY)
                tft.show()
                time.sleep(2)
            elif sel == 4:
                break  # zurück zum Menu
            break
        last_l = l; last_r = r; last_s = s
        time.sleep_ms(10)

    if sel == 4:
        break
