# Snake for ESP32 + ST7735S + MicroPython
# Expects these globals from the launcher:
#   tft, W, H, BTN_LEFT, BTN_SELECT, BTN_RIGHT
#
# Controls (3 buttons):
#   LEFT   = turn left
#   RIGHT  = turn right
#   SELECT = start / pause / restart
#
# Designed for a 160x128 logical screen (rotation=1 in your launcher).

import time

try:
    import urandom as _rand
except ImportError:
    import random as _rand

# ------------------------------------------------------------
# Safety check for launcher globals
# ------------------------------------------------------------
_required = ("tft", "W", "H", "BTN_LEFT", "BTN_SELECT", "BTN_RIGHT")
_missing = [name for name in _required if name not in globals()]
if _missing:
    raise RuntimeError("snake.py missing globals: " + ", ".join(_missing))

# ------------------------------------------------------------
# Colors (RGB565)
# ------------------------------------------------------------
BLACK   = 0x0000
WHITE   = 0xFFFF
RED     = 0xF800
GREEN   = 0x07E0
BLUE    = 0x001F
CYAN    = 0x07FF
YELLOW  = 0xFFE0
ORANGE  = 0xFD20
PINK    = 0xF81F
DARK    = 0x18C3
DARK2   = 0x0841
GRID    = 0x2945
ACCENT  = YELLOW

# ------------------------------------------------------------
# Layout
# ------------------------------------------------------------
HUD_H = 12
CELL  = 8

GRID_W = W // CELL
GRID_H = (H - HUD_H) // CELL

PLAY_X = 0
PLAY_Y = HUD_H
PLAY_W = GRID_W * CELL
PLAY_H = GRID_H * CELL

# If your screen is slightly bigger than the integer grid, clear the rest too.
EXTRA_W = W - PLAY_W
EXTRA_H = H - (PLAY_Y + PLAY_H)

# ------------------------------------------------------------
# Direction system
# ------------------------------------------------------------
# 0=up, 1=right, 2=down, 3=left
DX = (0, 1, 0, -1)
DY = (-1, 0, 1, 0)

def _randint(n):
    # returns 0..n-1
    try:
        return _rand.getrandbits(16) % n
    except AttributeError:
        return _rand.randrange(n)

def _draw_hud(score, best, paused=False, game_over=False):
    tft.fill_rect(0, 0, W, HUD_H, DARK)
    tft.text("S:%d" % score, 2, 2, GREEN)
    tft.text("B:%d" % best, 54, 2, CYAN)

    if game_over:
        tft.text("GAME OVER", W - 60, 2, RED)
    elif paused:
        tft.text("PAUSE", W - 36, 2, YELLOW)
    else:
        tft.text("RUN", W - 24, 2, ACCENT)

def _clear_playfield():
    tft.fill_rect(0, HUD_H, W, H - HUD_H, BLACK)
    # subtle border/grid
    for x in range(0, PLAY_W, CELL):
        tft.fill_rect(x, HUD_H, 1, PLAY_H, DARK2)
    for y in range(HUD_H, HUD_H + PLAY_H, CELL):
        tft.fill_rect(0, y, PLAY_W, 1, DARK2)

    if EXTRA_W > 0:
        tft.fill_rect(PLAY_W, HUD_H, EXTRA_W, PLAY_H, BLACK)
    if EXTRA_H > 0:
        tft.fill_rect(0, HUD_H + PLAY_H, W, EXTRA_H, BLACK)

def _cell_to_px(cell):
    x, y = cell
    return x * CELL, HUD_H + y * CELL

def _draw_cell(cell, color):
    x, y = _cell_to_px(cell)
    # small inset so the grid lines remain visible
    tft.fill_rect(x + 1, y + 1, CELL - 2, CELL - 2, color)

def _spawn_food(snake):
    occupied = set(snake)
    free = []
    for y in range(GRID_H):
        for x in range(GRID_W):
            if (x, y) not in occupied:
                free.append((x, y))
    if not free:
        return None
    return free[_randint(len(free))]

def _turn_left(d):
    return (d - 1) & 3

def _turn_right(d):
    return (d + 1) & 3

def _wait_for_release():
    # simple debounce and release wait
    time.sleep_ms(80)
    while BTN_LEFT.value() == 0 or BTN_SELECT.value() == 0 or BTN_RIGHT.value() == 0:
        time.sleep_ms(10)
    time.sleep_ms(80)

def _button_edge(last_state, btn):
    now = btn.value()
    pressed = last_state == 1 and now == 0
    return now, pressed

def _speed_ms(score):
    # Faster over time, but still playable.
    if score < 5:
        return 220
    if score < 12:
        return 180
    if score < 20:
        return 150
    if score < 30:
        return 125
    return 105

def _draw_title_screen(best):
    tft.fill(BLACK)
    tft.text("SNAKE", 44, 28, GREEN)
    tft.text("L=left", 34, 50, WHITE)
    tft.text("R=right", 34, 62, WHITE)
    tft.text("SEL=start", 34, 74, WHITE)
    tft.text("best:%d" % best, 36, 92, CYAN)

def run():
    best = 0

    while True:
        _draw_title_screen(best)

        # wait for start
        last_l = BTN_LEFT.value()
        last_s = BTN_SELECT.value()
        last_r = BTN_RIGHT.value()
        started = False
        while not started:
            l = BTN_LEFT.value()
            s = BTN_SELECT.value()
            r = BTN_RIGHT.value()

            if last_s == 1 and s == 0:
                started = True
                _wait_for_release()
                break

            last_l, last_s, last_r = l, s, r
            time.sleep_ms(20)

        # reset game
        snake = [(GRID_W // 2, GRID_H // 2),
                 (GRID_W // 2 - 1, GRID_H // 2),
                 (GRID_W // 2 - 2, GRID_H // 2)]
        direction = 1  # right
        score = 0
        paused = False
        game_over = False

        _clear_playfield()
        _draw_hud(score, best, paused=False, game_over=False)

        for part in snake:
            _draw_cell(part, GREEN)

        food = _spawn_food(snake)
        if food is None:
            # impossible on an empty board, but keep it safe
            food = (0, 0)
        _draw_cell(food, RED)

        last_l = BTN_LEFT.value()
        last_s = BTN_SELECT.value()
        last_r = BTN_RIGHT.value()

        last_move = time.ticks_ms()
        move_delay = _speed_ms(score)

        while True:
            now = time.ticks_ms()

            l = BTN_LEFT.value()
            s = BTN_SELECT.value()
            r = BTN_RIGHT.value()

            left_pressed = last_l == 1 and l == 0
            select_pressed = last_s == 1 and s == 0
            right_pressed = last_r == 1 and r == 0

            last_l, last_s, last_r = l, s, r

            if select_pressed:
                paused = not paused
                _draw_hud(score, best, paused=paused, game_over=False)
                _wait_for_release()
                last_move = time.ticks_ms()

            if not paused:
                if left_pressed:
                    direction = _turn_left(direction)
                elif right_pressed:
                    direction = _turn_right(direction)

                if time.ticks_diff(now, last_move) >= move_delay:
                    last_move = now

                    head_x, head_y = snake[0]
                    nx = head_x + DX[direction]
                    ny = head_y + DY[direction]

                    # wall collision
                    if nx < 0 or nx >= GRID_W or ny < 0 or ny >= GRID_H:
                        game_over = True
                    # self collision
                    elif (nx, ny) in snake:
                        game_over = True
                    else:
                        new_head = (nx, ny)
                        snake.insert(0, new_head)
                        _draw_cell(new_head, GREEN)

                        if new_head == food:
                            score += 1
                            if score > best:
                                best = score
                            move_delay = _speed_ms(score)
                            _draw_hud(score, best, paused=False, game_over=False)

                            food = _spawn_food(snake)
                            if food is None:
                                # Board full = win
                                game_over = True
                            else:
                                _draw_cell(food, RED)
                        else:
                            tail = snake.pop()
                            _draw_cell(tail, BLACK)

                    if game_over:
                        break

            time.sleep_ms(12)

        # game over screen
        if score > best:
            best = score

        tft.fill_rect(0, 0, W, H, BLACK)
        tft.text("GAME OVER", 28, 36, RED)
        tft.text("score:%d" % score, 34, 54, WHITE)
        tft.text("best:%d" % best, 36, 66, CYAN)
        tft.text("SEL=retry", 30, 88, YELLOW)

        # wait for restart
        last_s = BTN_SELECT.value()
        while True:
            s = BTN_SELECT.value()
            if last_s == 1 and s == 0:
                _wait_for_release()
                break
            last_s = s
            time.sleep_ms(20)

run()
