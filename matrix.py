# matrix.py - CyberDeck Matrix Rain
# Verfügbar: tft, W, H, BTN_LEFT, BTN_SELECT, BTN_RIGHT

import time

try:
    import urandom as _rand
except:
    import random as _rand

def _c(color):
    return ((color & 0xFF) << 8) | (color >> 8)

BLACK = _c(0x0000)
GREEN = _c(0x07E0)
WHITE = _c(0xFFFF)
DARKG = _c(0x0200)

CHAR_W = 6
CHAR_H = 8

COLS = W // CHAR_W

CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def rnd(n):
    try:
        return _rand.getrandbits(16) % n
    except:
        return _rand.randrange(n)

# Spalten erzeugen
streams = []

for x in range(COLS):
    streams.append({
        "x": x * CHAR_W,
        "y": -rnd(H),
        "speed": 2 + rnd(4),
        "len": 4 + rnd(12)
    })

tft.fill(BLACK)
tft.show()

while True:

    # irgendein Button -> App verlassen
    if (BTN_LEFT.value() == 0 or
        BTN_SELECT.value() == 0 or
        BTN_RIGHT.value() == 0):
        break

    for s in streams:

        # alte Spur löschen
        tail_y = s["y"] - s["len"] * CHAR_H

        if tail_y >= 0:
            tft.fill_rect(
                s["x"],
                tail_y,
                CHAR_W,
                CHAR_H,
                BLACK
            )

        # Kopf zeichnen
        head_char = CHARS[rnd(len(CHARS))]
        tft.text(
            head_char,
            s["x"],
            s["y"],
            WHITE
        )

        # Körper zeichnen
        for i in range(1, s["len"]):

            y = s["y"] - i * CHAR_H

            if y < 0:
                continue

            c = GREEN if i < 3 else DARKG

            tft.text(
                CHARS[rnd(len(CHARS))],
                s["x"],
                y,
                c
            )

        s["y"] += s["speed"]

        if s["y"] > H + s["len"] * CHAR_H:
            s["y"] = -rnd(H)
            s["speed"] = 2 + rnd(4)
            s["len"] = 4 + rnd(12)

    tft.show()
    time.sleep_ms(40)
