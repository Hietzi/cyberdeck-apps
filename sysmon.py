# sysmon.py - CyberDeck System Monitor
# Verfügbar: tft, W, H, BTN_LEFT, BTN_SELECT, BTN_RIGHT

import time
import network
import micropython
import gc

def _c(color):
    return ((color & 0xFF) << 8) | (color >> 8)

BLACK  = _c(0x0000)
WHITE  = _c(0xFFFF)
GREEN  = _c(0x07E0)
RED    = _c(0xF800)
CYAN   = _c(0x07FF)
YELLOW = _c(0xFFE0)
GREY   = _c(0x8410)
ACCENT = GREEN

def _bar(x, y, w, h, pct, col):
    tft.fill_rect(x, y, w, h, _c(0x2104))
    tft.fill_rect(x, y, int(w * pct), h, col)

def _draw():
    gc.collect()
    tft.fill(BLACK)
    tft.fill_rect(0, 0, W, 14, ACCENT)
    tft.text("System Monitor", 2, 3, BLACK)

    y = 18

    # WiFi
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        ip   = wlan.ifconfig()[0]
        ssid = wlan.config("essid")
        rssi = wlan.status("rssi")
        tft.text("WiFi: " + ssid[:12], 2, y, GREEN); y += 12
        tft.text("IP:   " + ip, 2, y, WHITE);         y += 12
        tft.text("RSSI: %d dBm" % rssi, 2, y, CYAN);  y += 12
    else:
        tft.text("WiFi: nicht verbunden", 2, y, RED);  y += 12

    y += 2

    # RAM
    free  = gc.mem_free()
    total = gc.mem_alloc() + free
    pct   = (total - free) / total
    tft.text("RAM: %dKB/%dKB" % (free//1024, total//1024), 2, y, WHITE); y += 11
    _bar(2, y, W-4, 6, pct, GREEN if pct < 0.7 else YELLOW if pct < 0.9 else RED)
    y += 10

    # CPU
    try:
        from machine import freq
        cpu = freq() // 1_000_000
        tft.text("CPU: %d MHz" % cpu, 2, y, WHITE); y += 12
    except:
        pass

    # Uptime
    ms      = time.ticks_ms()
    secs    = ms // 1000
    mins    = secs // 60
    hrs     = mins // 60
    tft.text("Up: %02d:%02d:%02d" % (hrs, mins % 60, secs % 60), 2, y, GREY); y += 12

    tft.fill_rect(0, H-12, W, 12, BLACK)
    tft.text("SEL:refresh  L/R:exit", 2, H-10, GREY)
    tft.show()

_draw()
last_l = last_r = last_s = 1
last_refresh = time.ticks_ms()

while True:
    l = BTN_LEFT.value()
    r = BTN_RIGHT.value()
    s = BTN_SELECT.value()

    if last_l == 1 and l == 0:
        break
    if last_r == 1 and r == 0:
        break
    if last_s == 1 and s == 0:
        _draw()
        time.sleep_ms(200)

    # Auto-refresh alle 5 Sekunden
    if time.ticks_diff(time.ticks_ms(), last_refresh) > 5000:
        _draw()
        last_refresh = time.ticks_ms()

    last_l = l; last_r = r; last_s = s
    time.sleep_ms(10)
