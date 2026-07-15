# snake.py - CyberDeck Snake (Landscape Overhaul with Debounce)
import time
from st7735 import BLACK, WHITE, GREEN, RED, GREY, DARKGREY, CYAN

try:
    import urandom as random
except:
    import random

HEADER_H = 14
CELL = 8
GRID_W = 20
GRID_H = 14
OFFSET_Y = HEADER_H

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

def draw_cell(pos, color):
    tft.fill_rect(pos[0] * CELL, OFFSET_Y + pos[1] * CELL, CELL - 1, CELL - 1, color)

def spawn_food(snake):
    while True:
        f = (random.getrandbits(8) % GRID_W, random.getrandbits(8) % GRID_H)
        if f not in snake:
            return f

snake = [(5, 7), (4, 7), (3, 7)]
direction = 1 # 0=UP, 1=RIGHT, 2=DOWN, 3=LEFT
food = spawn_food(snake)
score = 0
game_over = False

tft.fill(BLACK)
tft.fill_rect(0, 0, W, HEADER_H, GREEN)
tft.text("SNAKE OS - Score: 0", 4, 3, BLACK)

for p in snake: draw_cell(p, GREEN)
draw_cell(food, RED)
tft.show()

move_timer = time.ticks_ms()
speed = 150 # ms pro Schritt

while True:
    # Smart Chord Exit
    if BTN_LEFT.value() == 0 and BTN_RIGHT.value() == 0:
        time.sleep_ms(20)
        if BTN_LEFT.value() == 0 and BTN_RIGHT.value() == 0:
            wait_btn_release(BTN_LEFT)
            wait_btn_release(BTN_RIGHT)
            break
        
    # Richtungssteuerung (HINWEIS: Hier OHNE wait_btn_release, damit das Spiel nicht pausiert!)
    if btn_pressed(BTN_LEFT):
        direction = (direction - 1) % 4
    if btn_pressed(BTN_RIGHT):
        direction = (direction + 1) % 4
        
    if not game_over:
        if time.ticks_diff(time.ticks_ms(), move_timer) > speed:
            move_timer = time.ticks_ms()
            
            head = snake[0]
            if direction == 0:   new_head = (head[0], head[1] - 1)
            elif direction == 1: new_head = (head[0] + 1, head[1])
            elif direction == 2: new_head = (head[0], head[1] + 1)
            elif direction == 3: new_head = (head[0] - 1, head[1])
            
            if (new_head[0] < 0 or new_head[0] >= GRID_W or 
                new_head[1] < 0 or new_head[1] >= GRID_H or 
                new_head in snake):
                game_over = True
            else:
                snake.insert(0, new_head)
                draw_cell(new_head, GREEN)
                
                if new_head == food:
                    score += 1
                    tft.fill_rect(0, 0, W, HEADER_H, GREEN)
                    tft.text("SNAKE OS - Score: {}".format(score), 4, 3, BLACK)
                    food = spawn_food(snake)
                    draw_cell(food, RED)
                    speed = max(80, 150 - (score * 4))
                else:
                    tail = snake.pop()
                    draw_cell(tail, BLACK)
                    
            tft.show()
    else:
        # Game Over Screen
        tft.fill_rect(20, 35, 120, 65, DARKGREY)
        tft.rect(20, 35, 120, 65, RED)
        tft.text("GAME OVER", 44, 45, RED)
        tft.text("Score: {}".format(score), 44, 60, WHITE)
        tft.text("L+R: Exit Menu", 28, 75, CYAN)
        tft.text("SEL: Try Again", 28, 87, GREEN)
        tft.show()
        
        while True:
            if BTN_LEFT.value() == 0 and BTN_RIGHT.value() == 0:
                time.sleep_ms(20)
                if BTN_LEFT.value() == 0 and BTN_RIGHT.value() == 0:
                    wait_btn_release(BTN_LEFT)
                    wait_btn_release(BTN_RIGHT)
                    break
            
            if btn_pressed(BTN_SELECT):
                wait_btn_release(BTN_SELECT)
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
            
        if game_over: # Break out of outer loop if Exited
            break
    time.sleep_ms(10)
