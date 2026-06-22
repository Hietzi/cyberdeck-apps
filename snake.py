# snake.py - CyberDeck Snake (Landscape Overhaul)
import time
from st7735 import BLACK, WHITE, GREEN, RED, GREY, DARKGREY, CYAN

try:
    import urandom as random
except:
    import random

# UI Dimensionen
HEADER_H = 14
CELL = 8
# Spielfeld berechnen für 160x128
# Breite 160 -> 20 Zellen à 8 Pixel
# Höhe 128 - 14 (Header) = 114 -> 14 Zellen à 8 Pixel = 112 Pixel (2 Pixel Rest unten)
GRID_W = 20
GRID_H = 14
OFFSET_Y = HEADER_H

def draw_cell(pos, color):
    tft.fill_rect(pos[0] * CELL, OFFSET_Y + pos[1] * CELL, CELL - 1, CELL - 1, color)

def spawn_food(snake):
    while True:
        f = (random.getrandbits(8) % GRID_W, random.getrandbits(8) % GRID_H)
        if f not in snake:
            return f

# Spiel-Initialisierung
snake = [(5, 7), (4, 7), (3, 7)]
direction = 1 # 0=UP, 1=RIGHT, 2=DOWN, 3=LEFT
food = spawn_food(snake)
score = 0
game_over = False

tft.fill(BLACK)
tft.fill_rect(0, 0, W, HEADER_H, GREEN)
tft.text("SNAKE OS - Score: 0", 4, 3, BLACK)

# Zellen initial zeichnen
for p in snake: draw_cell(p, GREEN)
draw_cell(food, RED)
tft.show()

last_l = last_r = last_s = 1
move_timer = time.ticks_ms()
speed = 150 # ms pro Schritt

while True:
    l = BTN_LEFT.value()
    r = BTN_RIGHT.value()
    s = BTN_SELECT.value()
    
    # Smart Chord Exit: Wenn Links + Rechts GLEICHZEITIG gedrückt werden, sofort beenden!
    if l == 0 and r == 0:
        time.sleep_ms(200)
        break
        
    # Richtungssteuerung
    if last_l == 1 and l == 0:
        direction = (direction - 1) % 4
        time.sleep_ms(50)
    if last_r == 1 and r == 0:
        direction = (direction + 1) % 4
        time.sleep_ms(50)
        
    last_l = l; last_r = r
    
    if not game_over:
        if time.ticks_diff(time.ticks_ms(), move_timer) > speed:
            move_timer = time.ticks_ms()
            
            # Nächsten Schritt berechnen
            head = snake[0]
            if direction == 0:   new_head = (head[0], head[1] - 1)
            elif direction == 1: new_head = (head[0] + 1, head[1])
            elif direction == 2: new_head = (head[0], head[1] + 1)
            elif direction == 3: new_head = (head[0] - 1, head[1])
            
            # Kollisionsprüfung Wand oder sich selbst
            if (new_head[0] < 0 or new_head[0] >= GRID_W or 
                new_head[1] < 0 or new_head[1] >= GRID_H or 
                new_head in snake):
                game_over = True
            else:
                snake.insert(0, new_head)
                draw_cell(new_head, GREEN)
                
                if new_head == food:
                    score += 1
                    # Header updaten
                    tft.fill_rect(0, 0, W, HEADER_H, GREEN)
                    tft.text("SNAKE OS - Score: {}".format(score), 4, 3, BLACK)
                    food = spawn_food(snake)
                    draw_cell(food, RED)
                    speed = max(80, 150 - (score * 4)) # Wird schneller
                else:
                    tail = snake.pop()
                    draw_cell(tail, BLACK)
                    
            tft.show()
    else:
        # Game Over Screen im Cyberpunk-Look
        tft.fill_rect(20, 35, 120, 65, DARKGREY)
        tft.rect(20, 35, 120, 65, RED)
        tft.text("GAME OVER", 44, 45, RED)
        tft.text("Score: {}".format(score), 44, 60, WHITE)
        tft.text("L+R: Exit Menu", 28, 75, CYAN)
        tft.text("SEL: Try Again", 28, 87, GREEN)
        tft.show()
        
        while True:
            l = BTN_LEFT.value()
            r = BTN_RIGHT.value()
            s = BTN_SELECT.value()
            if l == 0 and r == 0: # Exit Chord
                time.sleep_ms(200)
                break
            if s == 0: # Restart
                time.sleep_ms(150)
                snake = [(5, 7), (4, 7), (3, 7)]
                direction = 1
                score = 0
                speed = 150
                game_over = False
                tft.fill(BLACK)
                tft.fill_rect(0, 0, W, HEADER_H, GREEN)
                tft.text("SNAKE OS - Score: 0", 4, 3, BLACK)
                for p in snake: draw_cell(p, GREEN)
                draw_cell(food, RED)
                tft.show()
                break
            time.sleep_ms(10)
        if game_over: # Loop abgebrochen durch Exit Chord
            break
    time.sleep_ms(10)
