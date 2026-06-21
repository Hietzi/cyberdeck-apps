# clock.py - CyberDeck Clock App
# Verfügbar: tft, W, H, BTN_LEFT, BTN_SELECT, BTN_RIGHT

import time

def _c(color):
    return ((color & 0xFF) << 8) | (color >> 8)

BLACK  = _c(0x0000)
GREEN  = _c(0x07E0)
GREY   = _c(0x8410)

UTC_OFFSET = 2  # Wien: Sommer=2, Winter=1

try:
    import ntptime
    ntptime.settime()
except:
    pass

# Initiales Layout
tft.fill(BLACK)
tft.fill_rect(0, 0, W, 14, GREEN)
tft.text("Clock", 2, 3, BLACK)
tft.text("SEL: zurueck", 2, H - 10, GREY)
tft.show()

last_sec = -1
running  = True

while running:
    t    = time.localtime()
    sec  = t[5]
    hour = (t[3] + UTC_OFFSET) % 24
    mins = t[4]

    if sec != last_sec:
        last_sec = sec
        timestr = "{:02d}:{:02d}:{:02d}".format(hour, mins, sec)
        datestr = "{:04d}-{:02d}-{:02d}".format(t[0], t[1], t[2])

        tx = (W - len(timestr) * 6) // 2
        tft.fill_rect(0, 35, W, 16, BLACK)
        tft.text(timestr, tx, 38, GREEN)

        dx = (W - len(datestr) * 6) // 2
        tft.fill_rect(0, 56, W, 10, BLACK)
        tft.text(datestr, dx, 58, GREY)
        tft.show()

    if BTN_SELECT.value() == 0:
        time.sleep_ms(100)
        running = False

    time.sleep_ms(50)
