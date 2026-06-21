# clock.py - CyberDeck Clock App
# Wird von main.py mit exec() gestartet
# Verfügbar: tft, W, H, BTN_LEFT, BTN_SELECT, BTN_RIGHT

import time

try:
    import ntptime
    ntptime.settime()
except:
    pass  # Zeit bleibt auf 2000-01-01 wenn kein NTP

# Offset für Wien (UTC+1 oder UTC+2 im Sommer)
UTC_OFFSET = 2  # Sommerzeit → 2, Winterzeit → 1

# Initiales Layout zeichnen (nur einmal)
tft.fill(0x0000)
tft.fill_rect(0, 0, W, 14, 0x07E0)           # Header grün
tft.text("Clock", 2, 3, 0x0000)              # Header Text
tft.text("SEL: zurueck", 2, H - 10, 0x8410) # Footer

last_sec = -1
running  = True

while running:
    t    = time.localtime()
    sec  = t[5]
    hour = (t[3] + UTC_OFFSET) % 24
    mins = t[4]

    # Nur updaten wenn sich die Sekunde geändert hat
    if sec != last_sec:
        last_sec = sec

        timestr = "{:02d}:{:02d}:{:02d}".format(hour, mins, sec)
        datestr = "{:04d}-{:02d}-{:02d}".format(t[0], t[1], t[2])

        # Zeit groß in der Mitte
        tx = (W - len(timestr) * 6) // 2
        tft.fill_rect(0, 35, W, 16, 0x0000)
        tft.text(timestr, tx, 38, 0x07E0)   # Grün

        # Datum darunter
        dx = (W - len(datestr) * 6) // 2
        tft.fill_rect(0, 56, W, 10, 0x0000)
        tft.text(datestr, dx, 58, 0x8410)   # Grau

    # Button check
    if BTN_SELECT.value() == 0:
        time.sleep_ms(100)
        running = False

    time.sleep_ms(50)
