# clock.py - CyberDeck Clock App (Landscape Overhaul)
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

def draw_clock_ui(timestr, datestr):
    tft.fill(BLACK)
    
    # Header
    tft.fill_rect(0, 0, W, HEADER_H, GREEN)
    tft.text("REALTIME CLOCK", 4, 3, BLACK)
    
    # Zeit-Anzeige (Groß und mittig platziert)
    # Ein Zeichen ist 8 Pixel breit, 8 Zeichen = 64 Pixel. Mittig bei W=160 -> (160-64)/2 = 48
    tft.text(timestr, 48, 50, GREEN)
    
    # Datum-Anzeige darunter
    # 10 Zeichen = 80 Pixel. Mittig bei W=160 -> (160-80)/2 = 40
    tft.text(datestr, 40, 72, WHITE)
    
    # Footer
    tft.fill_rect(0, H - FOOTER_H, W, FOOTER_H, BLACK)
    tft.line(0, H - FOOTER_H, W, H - FOOTER_H, DARKGREY)
    tft.text("SEL: Exit to Menu", 4, H - FOOTER_H + 2, GREY)
    
    tft.show()

# Main Loop
last_sec = -1
last_l = last_r = last_s = 1

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
        
    # Smart Exit über SELECT-Button
    s = BTN_SELECT.value()
    if last_s == 1 and s == 0:
        time.sleep_ms(100)
        break
    last_s = s
    time.sleep_ms(20)
