# clock.py - CyberDeck Clock App (Landscape Overhaul with Debounce)
import time
import ntptime
from st7735 import BLACK, WHITE, GREEN, GREY, DARKGREY

# Versuche Zeit zu synchronisieren
try:
    ntptime.settime()
except:
    pass

UTC_OFFSET = 2  # Sommerzeit: +2, Winterzeit: +1

# UI Konstanten für 160x128
HEADER_H = 14
FOOTER_H = 12

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

def draw_clock_ui(timestr, datestr):
    tft.fill(BLACK)
    
    # Header
    tft.fill_rect(0, 0, W, HEADER_H, GREEN)
    tft.text("REALTIME CLOCK", 4, 3, BLACK)
    
    # Zeit-Anzeige (Groß und mittig platziert)
    tft.text(timestr, 48, 50, GREEN)
    
    # Datum-Anzeige darunter
    tft.text(datestr, 40, 72, WHITE)
    
    # Footer
    tft.fill_rect(0, H - FOOTER_H, W, FOOTER_H, BLACK)
    tft.line(0, H - FOOTER_H, W, H - FOOTER_H, DARKGREY)
    tft.text("SEL: Exit to Menu", 4, H - FOOTER_H + 2, GREY)
    
    tft.show()

# Main Loop
last_sec = -1

while True:
    t = time.localtime()
    sec = t[5]
    hour = (t[3] + UTC_OFFSET) % 24
    mins = t[4]
    
    if sec != last_sec:
        last_sec = sec
        timestr = "{:02d}:{:02d}:{:02d}".format(hour, mins, sec)
        datestr = "{:04d}-{:02d}-{:02d}".format(t[0], t[1], t[2])
        draw_clock_ui(timestr, datestr)
        
    # Smart Exit über SELECT-Button mit stabiler Entprellung
    if btn_pressed(BTN_SELECT):
        wait_btn_release(BTN_SELECT)
        break
        
    time.sleep_ms(20)
