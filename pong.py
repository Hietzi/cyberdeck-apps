# pong.py - CyberDeck Pong App
# Verfügbar: tft, W, H, BTN_LEFT, BTN_SELECT, BTN_RIGHT

import time

try:
    import urandom as _rand
except ImportError:
    import random as _rand

_required = ("tft", "W", "H", "BTN_LEFT", "BTN_SELECT", "BTN_RIGHT")
_missing = [name for name in _required if name not in globals()]
if _missing:
    raise RuntimeError("pong.py missing globals: " + ", ".join(_missing))

def _c(color):
    return ((color & 0xFF) << 8) | (color >> 8)

BLACK  = _c(0x0000)
WHITE  = _c(0xFFFF)
RED    = _c(0xF800)
GREEN  = _c(0x07E0)
CYAN   = _c(0x07FF)
YELLOW = _c(0xFFE0)
DARK   = _c(0x18C3)
DARK2  = _c(0x0841)

HUD_H   = 12
PADDLE_W = 3
PADDLE_H = 22
BALL_S   = 3

TOP    = HUD_H

PLAYER_STEP = 3
AI_STEP     = 2

def _randint(n):
    try:
        return _rand.getrandbits(16) % n
    except AttributeError:
        return _rand.randrange(n)

def _clamp(v, lo, hi):
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v

def _wait_for_release():
    time.sleep_ms(80)
    while BTN_LEFT.value() == 0 or BTN_SELECT.value() == 0 or BTN_RIGHT.value() == 0:
        time.sleep_ms(10)
    time.sleep_ms(80)

def _draw_hud(left_score, right_score, paused=False):
    tft.fill_rect(0, 0, W, HUD_H, DARK)
    tft.text("%d" % left_score, 4, 2, GREEN)
    tft.text("%d" % right_score, W - 12, 2, CYAN)
    if paused:
        tft.text("PAUSE", 48, 2, YELLOW)
    else:
        tft.text("PONG", 46, 2, YELLOW)

def _draw_center_line():
    x = W // 2
    y = TOP + 2
    while y < H:
        tft.fill_rect(x, y, 1, 5, DARK2)
        y += 9

def _clear_playfield():
    tft.fill_rect(0, TOP, W, H - TOP, BLACK)
    _draw_center_line()

def _draw_paddle(x, y, color):
    tft.fill_rect(x, y, PADDLE_W, PADDLE_H, color)

def _draw_ball(x, y, color):
    tft.fill_rect(x, y, BALL_S, BALL_S, color)

def _ball_reset(direction=1):
    vx = direction * (2 + _randint(2))
    vy = -2 if _randint(2) == 0 else 2
    return vx, vy

def _serve_from_left():
    return _ball_reset(direction=1)

def _serve_from_right():
    return _ball_reset(direction=-1)

def _speed_delay(score):
    if score < 2:
        return 16
    if score < 5:
        return 14
    if score < 9:
        return 12
    if score < 14:
        return 10
    return 8

def _draw_title(best):
    tft.fill(BLACK)
    tft.text("PONG", 48, 28, GREEN)
    tft.text("L=up", 40, 52, WHITE)
    tft.text("R=down", 40, 64, WHITE)
    tft.text("SEL=start", 30, 76, WHITE)
    tft.text("best:%d" % best, 34, 96, CYAN)
    tft.show()

def run():
    best = 0

    while True:
        _draw_title(best)

        last_s = BTN_SELECT.value()
        while True:
            s = BTN_SELECT.value()
            if last_s == 1 and s == 0:
                _wait_for_release()
                break
            last_s = s
            time.sleep_ms(20)

        player_x = 6
        ai_x     = W - 6 - PADDLE_W
        player_y = TOP + (H - TOP - PADDLE_H) // 2
        ai_y     = TOP + (H - TOP - PADDLE_H) // 2

        left_score  = 0
        right_score = 0

        ball_x = (W - BALL_S) // 2
        ball_y = TOP + (H - TOP - BALL_S) // 2
        ball_vx, ball_vy = _serve_from_left()

        paused = False
        game_over = False

        _clear_playfield()
        _draw_hud(left_score, right_score)
        _draw_paddle(player_x, player_y, GREEN)
        _draw_paddle(ai_x, ai_y, CYAN)
        _draw_ball(ball_x, ball_y, RED)
        tft.show()

        last_l = BTN_LEFT.value()
        last_s = BTN_SELECT.value()
        last_r = BTN_RIGHT.value()

        last_tick = time.ticks_ms()
        move_delay = _speed_delay(left_score + right_score)

        while True:
            now = time.ticks_ms()

            l = BTN_LEFT.value()
            s = BTN_SELECT.value()
            r = BTN_RIGHT.value()

            left_pressed   = last_l == 1 and l == 0
            select_pressed = last_s == 1 and s == 0
            right_pressed  = last_r == 1 and r == 0
            last_l, last_s, last_r = l, s, r

            if select_pressed:
                paused = not paused
                _draw_hud(left_score, right_score, paused=paused)
                tft.show()
                _wait_for_release()
                last_tick = time.ticks_ms()

            if paused:
                time.sleep_ms(12)
                continue

            old_player_y = player_y
            if left_pressed:
                player_y -= PLAYER_STEP
            elif right_pressed:
                player_y += PLAYER_STEP
            player_y = _clamp(player_y, TOP, H - PADDLE_H)

            if player_y != old_player_y:
                _draw_paddle(player_x, old_player_y, BLACK)
                _draw_paddle(player_x, player_y, GREEN)

            old_ai_y = ai_y
            target = ball_y - (PADDLE_H // 2)
            if ai_y + PADDLE_H // 2 < target:
                ai_y += AI_STEP
            elif ai_y + PADDLE_H // 2 > target:
                ai_y -= AI_STEP
            ai_y = _clamp(ai_y, TOP, H - PADDLE_H)

            if ai_y != old_ai_y:
                _draw_paddle(ai_x, old_ai_y, BLACK)
                _draw_paddle(ai_x, ai_y, CYAN)

            if time.ticks_diff(now, last_tick) >= move_delay:
                last_tick = now

                old_ball_x = ball_x
                old_ball_y = ball_y

                ball_x += ball_vx
                ball_y += ball_vy

                if ball_y <= TOP:
                    ball_y = TOP
                    ball_vy = -ball_vy
                elif ball_y >= H - BALL_S:
                    ball_y = H - BALL_S
                    ball_vy = -ball_vy

                if ball_vx < 0:
                    if (ball_x <= player_x + PADDLE_W and
                        ball_x + BALL_S >= player_x and
                        ball_y + BALL_S >= player_y and
                        ball_y <= player_y + PADDLE_H):
                        ball_x = player_x + PADDLE_W
                        ball_vx = -ball_vx
                        hit = (ball_y + BALL_S // 2) - (player_y + PADDLE_H // 2)
                        if hit < -7:
                            ball_vy = -3
                        elif hit < -2:
                            ball_vy = -2
                        elif hit > 7:
                            ball_vy = 3
                        elif hit > 2:
                            ball_vy = 2
                        else:
                            ball_vy = 1 if ball_vy > 0 else -1

                if ball_vx > 0:
                    if (ball_x + BALL_S >= ai_x and
                        ball_x <= ai_x + PADDLE_W and
                        ball_y + BALL_S >= ai_y and
                        ball_y <= ai_y + PADDLE_H):
                        ball_x = ai_x - BALL_S
                        ball_vx = -ball_vx
                        hit = (ball_y + BALL_S // 2) - (ai_y + PADDLE_H // 2)
                        if hit < -7:
                            ball_vy = -3
                        elif hit < -2:
                            ball_vy = -2
                        elif hit > 7:
                            ball_vy = 3
                        elif hit > 2:
                            ball_vy = 2
                        else:
                            ball_vy = 1 if ball_vy > 0 else -1

                if ball_x < 0:
                    right_score += 1
                    if right_score > best:
                        best = right_score
                    _draw_hud(left_score, right_score)
                    _draw_ball(old_ball_x, old_ball_y, BLACK)
                    ball_x = (W - BALL_S) // 2
                    ball_y = TOP + (H - TOP - BALL_S) // 2
                    ball_vx, ball_vy = _serve_from_right()
                    move_delay = _speed_delay(left_score + right_score)
                    tft.show()
                    if right_score >= 7:
                        game_over = True

                elif ball_x > W - BALL_S:
                    left_score += 1
                    if left_score > best:
                        best = left_score
                    _draw_hud(left_score, right_score)
                    _draw_ball(old_ball_x, old_ball_y, BLACK)
                    ball_x = (W - BALL_S) // 2
                    ball_y = TOP + (H - TOP - BALL_S) // 2
                    ball_vx, ball_vy = _serve_from_left()
                    move_delay = _speed_delay(left_score + right_score)
                    tft.show()
                    if left_score >= 7:
                        game_over = True

                else:
                    _draw_ball(old_ball_x, old_ball_y, BLACK)
                    _draw_ball(ball_x, ball_y, RED)
                    tft.show()

                if game_over:
                    break

            time.sleep_ms(8)

        if left_score > best:
            best = left_score
        if right_score > best:
            best = right_score

        tft.fill(BLACK)
        tft.text("GAME OVER", 24, 34, RED)
        tft.text("you:%d" % left_score, 38, 54, GREEN)
        tft.text("cpu:%d" % right_score, 38, 66, CYAN)
        tft.text("SEL=retry", 30, 90, YELLOW)
        tft.show()

        last_s = BTN_SELECT.value()
        while True:
            s = BTN_SELECT.value()
            if last_s == 1 and s == 0:
                _wait_for_release()
                break
            last_s = s
            time.sleep_ms(20)

run()
