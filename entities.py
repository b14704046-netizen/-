"""Player, NPC, Camera entities."""
import pygame
import math
import random
import config

NPC_COLORS = {
    "citizen":    (170, 110, 70),
    "journalist": (70,  100, 160),
    "protester":  (200, 55,  55),
    "unemployed": (110, 110, 110),
    "trader":     (60,  130, 90),
    "politician": (140, 80,  160),
    "barista":    (180, 130, 80),
    "shopper":    (200, 140, 100),
    "guard":      (50,  50,  80),
    "child":      (240, 180, 200),
    "elder":      (180, 180, 180),
    "secretary":  (200, 100, 140),
}


class Player:
    SPEED = 200

    def __init__(self):
        self.x = 200.0
        self.y = 200.0
        self.w = 24
        self.h = 32
        self.facing = "down"
        self._anim = 0
        self._anim_t = 0.0
        self.coffee_level = 0
        self.coffee_drink_t = 0.0   # 喝咖啡動畫計時器 (3 → 0 秒)
        self.hp = 100
        self.max_hp = 100
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.weapons = ["fist", "pistol"]
        self.weapon_idx = 0
        self.ammo = {"pistol": 30}
        self._punch_cd = 0.0

    @property
    def tile_x(self): return int((self.x + self.w / 2) // config.TILE_SIZE)
    @property
    def tile_y(self): return int((self.y + self.h / 2) // config.TILE_SIZE)

    def set_tile(self, tx, ty):
        self.x = tx * config.TILE_SIZE
        self.y = ty * config.TILE_SIZE

    @property
    def current_weapon(self):
        return self.weapons[self.weapon_idx]

    def switch_weapon(self):
        self.weapon_idx = (self.weapon_idx + 1) % len(self.weapons)

    def shoot(self, tx, ty):
        if self.current_weapon != "pistol":
            return None
        if self.ammo.get("pistol", 0) <= 0:
            return None
        self.ammo["pistol"] -= 1
        cx = self.x + self.w / 2
        cy = self.y + self.h / 2
        return Bullet(cx, cy, math.atan2(ty - cy, tx - cx))

    def punch(self, enemies):
        if self._punch_cd > 0:
            return
        self._punch_cd = 0.5
        cx = self.x + self.w / 2
        cy = self.y + self.h / 2
        for enemy in enemies:
            if not enemy.dead:
                ex = enemy.x + Enemy.W / 2
                ey = enemy.y + Enemy.H / 2
                if math.hypot(ex - cx, ey - cy) < 65:
                    enemy.take_damage(35)

    def update(self, dt, keys, scene):
        self._punch_cd = max(0.0, self._punch_cd - dt)
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy = -1; self.facing = "up"
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy =  1; self.facing = "down"
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx = -1; self.facing = "left"
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx =  1; self.facing = "right"

        if dx and dy: dx *= 0.707; dy *= 0.707

        sprinting = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and (dx or dy) and self.stamina > 0
        if sprinting:
            self.stamina = max(0.0, self.stamina - 40 * dt)
        else:
            self.stamina = min(self.max_stamina, self.stamina + 20 * dt)

        speed = self.SPEED + self.coffee_level * 15
        if sprinting:
            speed *= 1.8
        nx = self.x + dx * speed * dt
        ny = self.y + dy * speed * dt

        if not scene.is_solid(nx, self.y, self.w, self.h):
            self.x = nx
        if not scene.is_solid(self.x, ny, self.w, self.h):
            self.y = ny

        self.x = max(0, min(self.x, scene.pixel_w - self.w))
        self.y = max(0, min(self.y, scene.pixel_h - self.h))

        if dx or dy:
            self._anim_t += dt
            if self._anim_t > 0.13:
                self._anim_t = 0
                self._anim = (self._anim + 1) % 4

    def find_interaction(self, scene):
        """Return (kind, target) for closest interactable within 1.5 tiles."""
        best = None
        best_d = config.TILE_SIZE * 1.6
        cx = self.x + self.w / 2
        cy = self.y + self.h / 2

        for door in scene.doors:
            dx = door["x"] * config.TILE_SIZE + config.TILE_SIZE/2 - cx
            dy = door["y"] * config.TILE_SIZE + config.TILE_SIZE/2 - cy
            d = math.hypot(dx, dy)
            if d < best_d:
                best_d = d
                best = ("door", door)

        for npc in scene.npcs:
            if not getattr(npc, "visible", True): continue
            dx = npc.x + 16 - cx
            dy = npc.y + 16 - cy
            d = math.hypot(dx, dy)
            if d < best_d:
                best_d = d
                best = ("npc", npc)

        for obj in scene.objects:
            ox = obj["x"] * config.TILE_SIZE + config.TILE_SIZE/2
            oy = obj["y"] * config.TILE_SIZE + config.TILE_SIZE/2
            d = math.hypot(ox - cx, oy - cy)
            if d < best_d:
                best_d = d
                best = ("object", obj)

        return best

    def draw(self, surf, cx, cy):
        sx, sy = int(self.x - cx), int(self.y - cy)
        leg = [0, 3, 0, -3][self._anim]
        arm = [0, -2, 0, 2][self._anim]

        # Soft cast shadow on the ground (2.5D feel)
        shadow = pygame.Surface((26, 7), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 100), pygame.Rect(0, 0, 26, 7))
        surf.blit(shadow, (sx + 3, sy + 30))

        # ── Legs: pressed black dress trousers + shiny shoes ─────────────
        # Trousers
        pygame.draw.rect(surf, (24, 26, 38),
                         pygame.Rect(sx + 9, sy + 26, 5, 9 + leg))
        pygame.draw.rect(surf, (24, 26, 38),
                         pygame.Rect(sx + 18, sy + 26, 5, 9 - leg))
        # Crease highlight
        pygame.draw.line(surf, (62, 66, 88),
                         (sx + 11, sy + 26), (sx + 11, sy + 33 + leg), 1)
        pygame.draw.line(surf, (62, 66, 88),
                         (sx + 20, sy + 26), (sx + 20, sy + 33 - leg), 1)
        # Polished leather shoes
        pygame.draw.ellipse(surf, (12, 12, 18),
                            pygame.Rect(sx + 7, sy + 33 + leg, 9, 4))
        pygame.draw.ellipse(surf, (12, 12, 18),
                            pygame.Rect(sx + 16, sy + 33 - leg, 9, 4))
        pygame.draw.line(surf, (95, 95, 115),
                         (sx + 9, sy + 33 + leg), (sx + 14, sy + 33 + leg), 1)
        pygame.draw.line(surf, (95, 95, 115),
                         (sx + 18, sy + 33 - leg), (sx + 23, sy + 33 - leg), 1)

        # ── Suit body: dark navy with lapels + white shirt + red tie ─────
        # Jacket main shape (slightly wider at shoulders)
        pygame.draw.polygon(surf, (30, 38, 68), [
            (sx + 4, sy + 17), (sx + 28, sy + 17),
            (sx + 27, sy + 28), (sx + 5, sy + 28),
        ])
        # Shoulder highlight (sun-lit edge)
        pygame.draw.line(surf, (62, 78, 125),
                         (sx + 4, sy + 17), (sx + 28, sy + 17), 1)
        # White dress-shirt collar triangle
        pygame.draw.polygon(surf, (235, 238, 245), [
            (sx + 13, sy + 16), (sx + 19, sy + 16),
            (sx + 17, sy + 22), (sx + 15, sy + 22),
        ])
        # Lapels
        pygame.draw.polygon(surf, (22, 28, 52), [
            (sx + 9, sy + 17), (sx + 14, sy + 18),
            (sx + 13, sy + 24), (sx + 8, sy + 22),
        ])
        pygame.draw.polygon(surf, (22, 28, 52), [
            (sx + 23, sy + 17), (sx + 18, sy + 18),
            (sx + 19, sy + 24), (sx + 24, sy + 22),
        ])
        # Lapel sheen
        pygame.draw.line(surf, (78, 92, 138),
                         (sx + 10, sy + 18), (sx + 12, sy + 22), 1)
        pygame.draw.line(surf, (78, 92, 138),
                         (sx + 22, sy + 18), (sx + 20, sy + 22), 1)
        # Red silk tie (visible knot + body)
        pygame.draw.polygon(surf, (190, 30, 35), [
            (sx + 15, sy + 19), (sx + 17, sy + 19),
            (sx + 18, sy + 23), (sx + 14, sy + 23),
        ])
        pygame.draw.polygon(surf, (175, 25, 30), [
            (sx + 14, sy + 23), (sx + 18, sy + 23),
            (sx + 17, sy + 28), (sx + 15, sy + 28),
        ])
        pygame.draw.line(surf, (240, 110, 100),
                         (sx + 16, sy + 20), (sx + 16, sy + 27), 1)
        # Gold lapel pin
        pygame.draw.circle(surf, (255, 215, 80), (sx + 11, sy + 20), 1)

        # ── Arms swinging at sides (skin tone cuff peek + jacket) ────────
        pygame.draw.rect(surf, (30, 38, 68),
                         pygame.Rect(sx + 3, sy + 18 + arm, 4, 9))
        pygame.draw.rect(surf, (30, 38, 68),
                         pygame.Rect(sx + 25, sy + 18 - arm, 4, 9))
        # White shirt cuff
        pygame.draw.rect(surf, (235, 238, 245),
                         pygame.Rect(sx + 3, sy + 26 + arm, 4, 2))
        pygame.draw.rect(surf, (235, 238, 245),
                         pygame.Rect(sx + 25, sy + 26 - arm, 4, 2))
        # Hand (skin tone)
        pygame.draw.circle(surf, (218, 178, 142),
                           (sx + 5, sy + 29 + arm), 2)
        pygame.draw.circle(surf, (218, 178, 142),
                           (sx + 27, sy + 29 - arm), 2)

        # ── Neck + head ──────────────────────────────────────────────────
        # Neck
        pygame.draw.rect(surf, (200, 162, 130),
                         pygame.Rect(sx + 14, sy + 14, 4, 3))
        # Head (oval, slightly larger for a distinguished look)
        pygame.draw.ellipse(surf, (220, 182, 148),
                            pygame.Rect(sx + 8, sy + 1, 16, 16))
        # Subtle jaw shadow
        pygame.draw.line(surf, (190, 152, 122),
                         (sx + 10, sy + 13), (sx + 22, sy + 13), 1)

        # ── Powell's signature silver hair (top half + side trim) ────────
        # Top hair: silver with slight wave
        pygame.draw.ellipse(surf, (215, 215, 220),
                            pygame.Rect(sx + 7, sy + 0, 18, 9))
        # Darker silver shading
        pygame.draw.arc(surf, (175, 175, 185),
                        pygame.Rect(sx + 7, sy + 0, 18, 12),
                        3.4, 6.0, 2)
        # Side hair (cropped short)
        pygame.draw.rect(surf, (185, 185, 195),
                         pygame.Rect(sx + 7, sy + 5, 2, 6))
        pygame.draw.rect(surf, (185, 185, 195),
                         pygame.Rect(sx + 23, sy + 5, 2, 6))
        # Bright top highlight
        pygame.draw.line(surf, (245, 245, 250),
                         (sx + 11, sy + 2), (sx + 18, sy + 2), 1)

        # ── Face: eyebrows, eyes behind glasses, nose, mouth ─────────────
        # Bushy gray eyebrows
        pygame.draw.line(surf, (140, 140, 150),
                         (sx + 10, sy + 8), (sx + 14, sy + 8), 2)
        pygame.draw.line(surf, (140, 140, 150),
                         (sx + 18, sy + 8), (sx + 22, sy + 8), 2)
        # Rimless glasses (steel frames)
        pygame.draw.circle(surf, (245, 248, 255), (sx + 12, sy + 10), 2)
        pygame.draw.circle(surf, (95, 95, 110), (sx + 12, sy + 10), 2, 1)
        pygame.draw.circle(surf, (245, 248, 255), (sx + 20, sy + 10), 2)
        pygame.draw.circle(surf, (95, 95, 110), (sx + 20, sy + 10), 2, 1)
        pygame.draw.line(surf, (95, 95, 110),
                         (sx + 14, sy + 10), (sx + 18, sy + 10), 1)
        # Pupils (small, look slightly forward/down)
        pygame.draw.circle(surf, (38, 42, 55), (sx + 12, sy + 10), 1)
        pygame.draw.circle(surf, (38, 42, 55), (sx + 20, sy + 10), 1)
        # Nose (small triangle highlight)
        pygame.draw.line(surf, (190, 152, 122),
                         (sx + 16, sy + 11), (sx + 16, sy + 13), 1)
        # Mouth (slight stern line)
        pygame.draw.line(surf, (132, 88, 78),
                         (sx + 14, sy + 14), (sx + 18, sy + 14), 1)

        # ── Coffee boost glow above head ─────────────────────────────────
        if self.coffee_level > 0:
            t = pygame.time.get_ticks()
            glow_r = 4 + (t // 200) % 3
            glow = pygame.Surface((glow_r * 2 + 4, glow_r * 2 + 4),
                                  pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 220, 110, 130),
                               (glow_r + 2, glow_r + 2), glow_r)
            surf.blit(glow, (sx + 16 - glow_r - 2, sy - 6 - glow_r))
            pygame.draw.circle(surf, (255, 245, 180),
                               (sx + 16, sy - 4), 2)


class NPC:
    def __init__(self, tx, ty, kind="citizen", name=None, dialog_id=None, patrol_range=0):
        self.x  = float(tx * config.TILE_SIZE)
        self.y  = float(ty * config.TILE_SIZE)
        self.sx = self.x
        self.sy = self.y
        self.kind = kind
        self.name = name or kind
        self.dialog_id = dialog_id
        self.color = NPC_COLORS.get(kind, (150,150,150))
        self.t = random.uniform(0, 6.28)
        self.visible = True
        self.bubble = ""
        self.bubble_t = 0.0
        self.patrol_range = patrol_range
        self._anim = 0
        self._anim_t = 0

    def update(self, dt, economy):
        self.t += dt * 0.7
        if self.patrol_range > 0:
            self.x = self.sx + math.sin(self.t) * self.patrol_range * config.TILE_SIZE * 0.5
            self._anim_t += dt
            if self._anim_t > 0.18:
                self._anim_t = 0
                self._anim = (self._anim + 1) % 4
        if self.bubble_t > 0:
            self.bubble_t -= dt

    def say(self, text, duration=3.0):
        self.bubble   = text
        self.bubble_t = duration

    def draw(self, surf, cx, cy, fnt):
        if not self.visible: return
        sx, sy = int(self.x - cx), int(self.y - cy)
        if not (-60 < sx < config.SCREEN_W + 60 and -60 < sy < config.SCREEN_H + 60): return
        leg = [0, 3, 0, -3][self._anim] if self.patrol_range > 0 else 0
        pygame.draw.ellipse(surf, (0,0,0,60), pygame.Rect(sx+3, sy+29, 22, 5))
        pygame.draw.rect(surf, (40,40,70), pygame.Rect(sx+7,  sy+26, 6, 8+leg))
        pygame.draw.rect(surf, (40,40,70), pygame.Rect(sx+17, sy+26, 6, 8-leg))
        pygame.draw.rect(surf, self.color, pygame.Rect(sx+5, sy+13, 18, 15), border_radius=2)
        pygame.draw.ellipse(surf, (195, 155, 115), pygame.Rect(sx+7, sy+2, 14, 13))
        # Distinguishing feature based on kind
        if self.kind == "journalist":
            pygame.draw.rect(surf, (50,50,50), pygame.Rect(sx+19, sy+12, 8, 6))
        elif self.kind == "protester":
            pygame.draw.rect(surf, (220,220,180), pygame.Rect(sx+10, sy-8, 10, 12))
            pygame.draw.line(surf, (90,60,40), (sx+15, sy+4), (sx+15, sy-8), 2)
        elif self.kind == "trader":
            pygame.draw.rect(surf, (200, 30, 30), pygame.Rect(sx+5, sy+13, 18, 4))
        elif self.kind == "politician":
            pygame.draw.rect(surf, (40,40,40), pygame.Rect(sx+8, sy+13, 12, 4))
        elif self.kind == "child":
            pass  # small head already
        elif self.kind == "elder":
            pygame.draw.line(surf, (90,60,40), (sx+22, sy+18), (sx+24, sy+34), 2)
        if self.bubble_t > 0 and self.bubble:
            txt = fnt.render(self.bubble, True, config.BLACK)
            bw, bh = txt.get_size()
            bx, by = sx - bw//2 + 14, sy - bh - 14
            pygame.draw.rect(surf, config.WHITE, pygame.Rect(bx-4, by-4, bw+8, bh+8), border_radius=4)
            pygame.draw.rect(surf, config.GRAY,  pygame.Rect(bx-4, by-4, bw+8, bh+8), border_radius=4, width=1)
            surf.blit(txt, (bx, by))


class Bullet:
    SPEED = 650
    LIFETIME = 1.2
    DAMAGE = 25

    def __init__(self, x, y, angle):
        self.x = float(x)
        self.y = float(y)
        self.vx = math.cos(angle) * self.SPEED
        self.vy = math.sin(angle) * self.SPEED
        self.life = self.LIFETIME
        self.dead = False

    def update(self, dt, scene):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        if self.life <= 0 or scene.is_solid(self.x - 3, self.y - 3, 6, 6):
            self.dead = True

    def draw(self, surf, cx, cy):
        sx, sy = int(self.x - cx), int(self.y - cy)
        if not (0 < sx < config.SCREEN_W and 0 < sy < config.SCREEN_H):
            return
        ex = int(self.x - self.vx * 0.04 - cx)
        ey = int(self.y - self.vy * 0.04 - cy)
        pygame.draw.line(surf, (255, 180, 40), (sx, sy), (ex, ey), 3)
        pygame.draw.circle(surf, (255, 240, 120), (sx, sy), 4)


class Enemy:
    SPEED = 72
    HP = 60
    ATTACK_RANGE = 38
    ATTACK_DAMAGE = 12
    ATTACK_COOLDOWN = 1.4
    W = H = 30

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.hp = self.HP
        self.max_hp = self.HP
        self.dead = False
        self._atk_cd = 0.0
        self._anim = 0
        self._anim_t = 0.0
        self._stuck_t = 0.0
        self._nudge_angle = 0.0

    def update(self, dt, player, scene):
        if self.dead:
            return
        self._atk_cd = max(0.0, self._atk_cd - dt)
        cx = self.x + self.W / 2
        cy = self.y + self.H / 2
        px = player.x + player.w / 2
        py = player.y + player.h / 2
        dx = px - cx
        dy = py - cy
        dist = math.hypot(dx, dy)

        if dist < self.ATTACK_RANGE:
            self._stuck_t = 0.0
            if self._atk_cd <= 0:
                player.hp = max(0, player.hp - self.ATTACK_DAMAGE)
                self._atk_cd = self.ATTACK_COOLDOWN
        elif dist < 700:
            spd = self.SPEED * dt
            # When stuck, blend a perpendicular nudge into movement
            if self._stuck_t > 0.5:
                move_angle = math.atan2(dy, dx) + self._nudge_angle
                mx = math.cos(move_angle) * spd
                my = math.sin(move_angle) * spd
            else:
                mx = dx / dist * spd
                my = dy / dist * spd

            prev_x, prev_y = self.x, self.y
            if not scene.is_solid(self.x + mx, self.y, self.W, self.H):
                self.x += mx
            if not scene.is_solid(self.x, self.y + my, self.W, self.H):
                self.y += my

            moved = abs(self.x - prev_x) + abs(self.y - prev_y) > 0.1
            if moved:
                self._stuck_t = 0.0
            else:
                self._stuck_t += dt
                if self._stuck_t > 0.5:
                    # Pick a new random perpendicular nudge angle each time we first get stuck
                    if self._stuck_t < 0.55:
                        self._nudge_angle = math.pi / 2 * random.choice([-1, 1])

            self._anim_t += dt
            if self._anim_t > 0.16:
                self._anim_t = 0
                self._anim = (self._anim + 1) % 4

    def take_damage(self, dmg):
        self.hp = max(0, self.hp - dmg)
        if self.hp <= 0:
            self.dead = True

    def draw(self, surf, cx, cy):
        if self.dead:
            return
        sx, sy = int(self.x - cx), int(self.y - cy)
        if not (-60 < sx < config.SCREEN_W + 60 and -60 < sy < config.SCREEN_H + 60):
            return
        leg = [0, 4, 0, -4][self._anim]

        # Shadow
        pygame.draw.ellipse(surf, (0, 0, 0, 80), pygame.Rect(sx + 3, sy + 29, 24, 6))
        # Suit pants (dark navy)
        pygame.draw.rect(surf, (35, 55, 120), pygame.Rect(sx + 7,  sy + 26, 7, 8 + leg))
        pygame.draw.rect(surf, (35, 55, 120), pygame.Rect(sx + 16, sy + 26, 7, 8 - leg))
        # Blue suit jacket
        pygame.draw.rect(surf, (50, 80, 170), pygame.Rect(sx + 4, sy + 13, 22, 15), border_radius=2)
        # White shirt collar (two small triangles)
        pygame.draw.polygon(surf, (230, 230, 230), [(sx+13, sy+13), (sx+11, sy+17), (sx+13, sy+17)])
        pygame.draw.polygon(surf, (230, 230, 230), [(sx+17, sy+13), (sx+19, sy+17), (sx+17, sy+17)])
        # Signature long red tie
        pygame.draw.polygon(surf, (200, 25, 25), [
            (sx+14, sy+14), (sx+16, sy+14),
            (sx+17, sy+22), (sx+15, sy+29), (sx+13, sy+22),
        ])
        # Orange face
        pygame.draw.ellipse(surf, (255, 155, 70), pygame.Rect(sx + 7, sy + 2, 16, 13))
        # Golden comb-over (main mass + side sweep)
        pygame.draw.ellipse(surf, (255, 200, 55), pygame.Rect(sx + 5, sy + 0, 20, 9))
        pygame.draw.ellipse(surf, (255, 210, 70), pygame.Rect(sx + 4, sy - 1, 14, 7))
        pygame.draw.arc(surf, (240, 185, 45),
                        pygame.Rect(sx + 3, sy + 1, 14, 8), 0, math.pi, 2)
        # Squinty eyes (thin horizontal lines)
        pygame.draw.line(surf, (60, 35, 10), (sx + 9,  sy + 8), (sx + 13, sy + 8), 2)
        pygame.draw.line(surf, (60, 35, 10), (sx + 17, sy + 8), (sx + 21, sy + 8), 2)
        # Pursed pout lips
        pygame.draw.ellipse(surf, (200, 100, 80), pygame.Rect(sx + 11, sy + 11, 8, 4))

        # HP bar
        bw = 30
        ratio = self.hp / self.max_hp
        pygame.draw.rect(surf, (60, 0, 0),    pygame.Rect(sx, sy - 9, bw, 5))
        pygame.draw.rect(surf, (210, 40, 40), pygame.Rect(sx, sy - 9, int(bw * ratio), 5))


class Camera:
    def __init__(self):
        self.x = self.y = 0.0
        self._shake = 0.0
        self._shake_amp = 0

    def update(self, px, py, scene, dt):
        tx = px - config.SCREEN_W // 2
        ty = py - config.SCREEN_H // 2
        tx = max(0, min(tx, max(0, scene.pixel_w - config.SCREEN_W)))
        ty = max(0, min(ty, max(0, scene.pixel_h - config.SCREEN_H)))
        self.x += (tx - self.x) * min(1.0, 8 * dt)
        self.y += (ty - self.y) * min(1.0, 8 * dt)
        if self._shake > 0: self._shake -= dt

    def snap(self, px, py, scene):
        tx = px - config.SCREEN_W // 2
        ty = py - config.SCREEN_H // 2
        self.x = max(0, min(tx, max(0, scene.pixel_w - config.SCREEN_W)))
        self.y = max(0, min(ty, max(0, scene.pixel_h - config.SCREEN_H)))

    def shake(self, amp=8, dur=0.5):
        self._shake = dur; self._shake_amp = amp

    def offset(self):
        if self._shake > 0:
            return (self.x + random.uniform(-self._shake_amp, self._shake_amp),
                    self.y + random.uniform(-self._shake_amp, self._shake_amp))
        return (self.x, self.y)
