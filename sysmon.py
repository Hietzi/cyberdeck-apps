# sysmon.py - CyberDeck System Monitor (Landscape Overhaul)
import time
import network
import gc
from machine import freq
from st7735 import BLACK, WHITE, GREEN, CYAN, RED, GREY, DARKGREY, YELLOW

HEADER_H = 14
FOOTER_H = 12

def draw_bar(x, y, w, h, pct, col):
    tft.fill_rect(x, y, w, h, DARKGREY)
    fill_w = int(w * pct)
    if fill_w > 0:
        tft.fill_rect(x, y, fill_w, h, col)

def draw_sysmon():
    gc.collect()
    tft.fill(BLACK)
    
    # Header
    tft.fill_rect(0, 0, W, HEADER_H, GREEN)
    tft.text("SYSTEM MONITOR", 4, 3, BLACK)
    
    y = 20
    
    # 1. WiFi Status
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        try:
            rssi = wlan.status("rssi")
        except:
            rssi = 0
        tft.text("WiFi: Online", 4, y, GREEN)
        tft.text("IP: " + ip, 80, y, WHITE)
        y += 12
        tft.text("RSSI: {} dBm".format(rssi), 4, y, CYAN)
    else:
        tft.text("WiFi: Offline", 4, y, RED)
    
    y += 16
    
    # 2. RAM Usage
    free = gc.mem_free()
    alloc = gc.mem_alloc()
    total = free + alloc
    pct_ram = alloc / total if total > 0 else 0
    tft.text("RAM: {}K / {}K".format(alloc//1024, total//1024), 4, y, WHITE)
    y += 10
    ram_col = GREEN if pct_ram < 0.7 else (YELLOW if pct_ram < 0.9 else RED)
    draw_bar(4, y, W - 8, 6, pct_ram, ram_col)
    
    y += 14
    
    # 3. CPU & Uptime
    cpu = freq() // 1000000
    tft.text("CPU Freq: {} MHz".format(cpu), 4, y, CYAN)
    
    y += 12
    ms = time.ticks_ms()
    secs = ms // 1000
    mins = secs // 60
    hrs = mins // 60
    uptime_str = "Up: {:02d}:{:02d}:{:02d}".format(hrs, mins % 60, secs % 60)
    tft.text(uptime_str, 4, y, GREY)
    
    # Footer
    tft.fill_rect(0, H - FOOTER_H, W, FOOTER_H, BLACK)
    tft.line(0, H - FOOTER_H, W, H - FOOTER_H, DARKGREY)
    tft.text("SEL: Exit to Menu", 4, H - FOOTER_H + 2, GREY)
    
    tft.show()

# Main Loop
last_s = 1
last_draw = 0

while True:
    # Nur jede Sekunde neu zeichnen um CPU zu schonen
    if time.ticks_diff(time.ticks_ms(), last_draw) > 1000:
        draw_sysmon()
        last_draw = time.ticks_ms()
        
    # Smart Exit
    s = BTN_SELECT.value()
    if last_s == 1 and s == 0:
        time.sleep_ms(100)
        break
    last_s = s
    time.sleep_ms(20)
