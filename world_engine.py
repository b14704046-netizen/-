import pygame
import math
import random
import config

# ── Tile constants ────────────────────────────────────────────────────
FLOOR     = 0
WALL      = 1
ROAD      = 2
GRASS     = 3
DESK      = 4
TERMINAL  = 5
BED       = 6
SIDEWALK  = 7
CARPET    = 8

SOLID = {WALL, DESK, BED}

TILE_COLOR = {
    FLOOR:    (175, 155, 135),
    WALL:     (72,  62,  82),
    ROAD:     (55,  55,  65),
    GRASS:    (55,  135, 55),
    DESK:     (145, 105, 65),
    TERMINAL: (15,  75,  115),
    BED:      (95,  135, 195),
    SIDEWALK: (145, 135, 125),
    CARPET:   (100, 80,  120),
}

# 30×22 map  (W=30, H=22)
_W = [WALL]*30
MAP = [
    # 0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19  20  21  22  23  24  25  26  27  28  29
    [1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1],  # 0
    [1,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  1],  # 1
    [1,  8,  4,  5,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  5,  4,  8,  8,  8,  1],  # 2
    [1,  8,  4,  4,  8,  8,  8,  8,  8,  8,  8,  8,  8,  4,  4,  4,  4,  8,  8,  8,  8,  8,  8,  8,  4,  4,  8,  8,  8,  1],  # 3
    [1,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  4,  5,  4,  4,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  1],  # 4
    [1,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  1],  # 5
    [1,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  1],  # 6
    [1,  1,  1,  1,  1,  1,  1,  1,  0,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  0,  1,  1,  1,  1,  1,  1,  1,  1],  # 7 (FED south wall)
    # Street
    [7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7],  # 8
    [2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2],  # 9
    [2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2],  # 10
    [7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7],  # 11
    # Home/Apartment
    [1,  1,  1,  1,  1,  1,  1,  1,  0,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  0,  1,  1,  1,  1,  1,  1,  1,  1],  # 12
    [1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1],  # 13
    [1,  6,  6,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1],  # 14
    [1,  6,  6,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1],  # 15
    [1,  0,  0,  0,  0,  0,  4,  5,  4,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1],  # 16
    [1,  0,  0,  0,  0,  0,  4,  4,  4,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1],  # 17
    [1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1],  # 18
    [1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1],  # 19
    [1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1],  # 20
    [1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1],  # 21
]

TERMINAL_POSITIONS = [
    (3, 2), (24, 2), (14, 4), (7, 16),
]

# ── Player ────────────────────────────────────────────────────────────
class Player:
    SPEED = 190

    def __init__(self):
        self.x = float(8 * config.TILE_SIZE)
        self.y = float(18 * config.TILE_SIZE)
        self.w = self.h = 32
        self.facing = "down"
        self._anim = 0
        self._anim_t = 0.0

    @property
    def tile_x(self): return int((self.x + self.w / 2) // config.TILE_SIZE)
    @property
    def tile_y(self): return int((self.y + self.h / 2) // config.TILE_SIZE)

    def near_terminal(self):
        for ty, tx in TERMINAL_POSITIONS:
            if abs(self.tile_x - tx) <= 1 and abs(self.tile_y - ty) <= 1:
                return True
        return False

    def update(self, dt, keys):
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy = -1; self.facing = "up"
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy =  1; self.facing = "down"
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx = -1; self.facing = "left"
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx =  1; self.facing = "right"

        if dx and dy: dx *= 0.707; dy *= 0.707

        nx = self.x + dx * self.SPEED * dt
        ny = self.y + dy * self.SPEED * dt

        if not self._solid(nx, self.y): self.x = nx
        if not self._solid(self.x, ny): self.y = ny

        self.x = max(0, min(self.x, (config.MAP_COLS - 1) * config.TILE_SIZE))
        self.y = max(0, min(self.y, (config.MAP_ROWS - 1) * config.TILE_SIZE))

        moving = bool(dx or dy)
        if moving:
            self._anim_t += dt
            if self._anim_t > 0.13: self._anim_t = 0; self._anim = (self._anim + 1) % 4

    @staticmethod
    def _solid(x, y):
        m = 5
        corners = [(x+m, y+m), (x+30, y+m), (x+m, y+30), (x+30, y+30)]
        for cx, cy in corners:
            tx, ty = int(cx // config.TILE_SIZE), int(cy // config.TILE_SIZE)
            if not (0 <= tx < config.MAP_COLS and 0 <= ty < config.MAP_ROWS):
                return True
            if MAP[ty][tx] in SOLID:
                return True
        return False

    def draw(self, surf, cx, cy):
        sx, sy = int(self.x - cx), int(self.y - cy)
        leg = [0, 4, 0, -4][self._anim]
        # Shadow
        pygame.draw.ellipse(surf, (0,0,0,80), pygame.Rect(sx+4, sy+30, 24, 6))
        # Legs
        pygame.draw.rect(surf, (30, 30, 60), pygame.Rect(sx+7,  sy+28, 7, 8+leg))
        pygame.draw.rect(surf, (30, 30, 60), pygame.Rect(sx+18, sy+28, 7, 8-leg))
        # Suit body
        pygame.draw.rect(surf, (25, 90, 170), pygame.Rect(sx+4, sy+14, 24, 16), border_radius=3)
        # Tie
        pygame.draw.polygon(surf, (180, 20, 20), [(sx+15, sy+15), (sx+17, sy+15), (sx+16, sy+28)])
        # Head
        pygame.draw.ellipse(surf, (210, 175, 140), pygame.Rect(sx+8, sy+2, 16, 14))
        # Gray hair
        pygame.draw.ellipse(surf, (170, 170, 175), pygame.Rect(sx+8, sy+2, 16, 7))
        # Eyes
        pygame.draw.circle(surf, (40,40,40), (sx+12, sy+10), 2)
        pygame.draw.circle(surf, (40,40,40), (sx+20, sy+10), 2)


# ── Camera ────────────────────────────────────────────────────────────
class Camera:
    def __init__(self):
        self.x = self.y = 0.0
        self._shake = 0.0
        self._shake_amp = 0

    def update(self, px, py, dt):
        tx = px - config.SCREEN_W // 2
        ty = py - config.SCREEN_H // 2
        tx = max(0, min(tx, config.MAP_COLS * config.TILE_SIZE - config.SCREEN_W))
        ty = max(0, min(ty, config.MAP_ROWS * config.TILE_SIZE - config.SCREEN_H))
        self.x += (tx - self.x) * min(1.0, 8 * dt)
        self.y += (ty - self.y) * min(1.0, 8 * dt)
        if self._shake > 0: self._shake -= dt

    def shake(self, amp=8, dur=0.5):
        self._shake = dur; self._shake_amp = amp

    def offset(self):
        if self._shake > 0:
            return (self.x + random.uniform(-self._shake_amp, self._shake_amp),
                    self.y + random.uniform(-self._shake_amp, self._shake_amp))
        return (self.x, self.y)


# ── NPC ───────────────────────────────────────────────────────────────
NPC_COLORS = {
    "citizen":   (170, 110, 70),
    "journalist":(70,  100, 160),
    "protester": (200, 55,  55),
    "unemployed":(110, 110, 110),
}

class NPC:
    def __init__(self, tx, ty, kind="citizen"):
        self.x  = float(tx * config.TILE_SIZE)
        self.y  = float(ty * config.TILE_SIZE)
        self.sx = self.x
        self.kind = kind
        self.color = NPC_COLORS.get(kind, (150,150,150))
        self.t = random.uniform(0, 6.28)
        self.visible = True
        self.bubble = ""
        self.bubble_t = 0.0

    def update(self, dt, economy):
        self.t += dt * 0.7
        self.x = self.sx + math.sin(self.t) * 2.5 * config.TILE_SIZE
        if self.bubble_t > 0:
            self.bubble_t -= dt

    def say(self, text, duration=3.0):
        self.bubble   = text
        self.bubble_t = duration

    def draw(self, surf, cx, cy, fnt):
        if not self.visible: return
        sx, sy = int(self.x - cx), int(self.y - cy)
        if not (-60 < sx < config.SCREEN_W + 60): return

        # Shadow
        pygame.draw.ellipse(surf, (0,0,0,60), pygame.Rect(sx+3, sy+29, 22, 5))
        # Legs
        pygame.draw.rect(surf, (40,40,70), pygame.Rect(sx+7,  sy+26, 6, 8))
        pygame.draw.rect(surf, (40,40,70), pygame.Rect(sx+17, sy+26, 6, 8))
        # Body
        pygame.draw.rect(surf, self.color, pygame.Rect(sx+5, sy+13, 18, 15), border_radius=2)
        # Head
        pygame.draw.ellipse(surf, (195, 155, 115), pygame.Rect(sx+7, sy+2, 14, 13))

        # Speech bubble
        if self.bubble_t > 0 and self.bubble:
            alpha = min(1.0, self.bubble_t) * 255
            txt = fnt.render(self.bubble, True, config.BLACK)
            bw, bh = txt.get_size()
            bx, by = sx - bw//2 + 14, sy - bh - 14
            pygame.draw.rect(surf, config.WHITE, pygame.Rect(bx-4, by-4, bw+8, bh+8), border_radius=4)
            pygame.draw.rect(surf, config.GRAY,  pygame.Rect(bx-4, by-4, bw+8, bh+8), border_radius=4, width=1)
            surf.blit(txt, (bx, by))


# ── Map renderer ──────────────────────────────────────────────────────
def draw_map(surf, cx, cy, economy, fnt_s):
    ts = config.TILE_SIZE
    x0, y0 = int(cx // ts), int(cy // ts)
    x1 = min(config.MAP_COLS, x0 + config.SCREEN_W // ts + 2)
    y1 = min(config.MAP_ROWS, y0 + config.SCREEN_H // ts + 2)

    for ty in range(max(0, y0), y1):
        for tx in range(max(0, x0), x1):
            tile = MAP[ty][tx]
            color = TILE_COLOR.get(tile, (80,80,80))
            sx, sy = tx * ts - int(cx), ty * ts - int(cy)
            r = pygame.Rect(sx, sy, ts-1, ts-1)
            pygame.draw.rect(surf, color, r)

            if tile == WALL:
                pygame.draw.line(surf, (55,48,65), (sx, sy+ts//2), (sx+ts, sy+ts//2), 1)
                pygame.draw.line(surf, (55,48,65), (sx+ts//2, sy), (sx+ts//2, sy+ts), 1)

            elif tile == TERMINAL:
                pygame.draw.rect(surf, config.TERMINAL_BG, pygame.Rect(sx+4, sy+4, ts-9, ts-9), border_radius=3)
                pygame.draw.rect(surf, config.TERMINAL_GREEN, pygame.Rect(sx+4, sy+4, ts-9, ts-9), border_radius=3, width=1)
                t = fnt_s.render("PC", True, config.TERMINAL_GREEN)
                surf.blit(t, (sx + (ts - t.get_width())//2, sy + (ts - t.get_height())//2))

            elif tile == BED:
                pygame.draw.rect(surf, (75,115,180), pygame.Rect(sx+2, sy+2, ts-5, ts-5), border_radius=5)
                pygame.draw.rect(surf, (200,205,220), pygame.Rect(sx+3, sy+3, ts-7, 12))

            elif tile == ROAD:
                # lane markings
                if ty == 9 and tx % 3 == 0:
                    pygame.draw.rect(surf, (200,200,100), pygame.Rect(sx + ts//2 - 2, sy + 4, 4, ts - 8))

    # Price tags appear when inflation is high
    if economy and economy.cpi > 5:
        for tx in range(max(0,x0), x1, 6):
            for ty in [8, 11]:
                sx, sy = tx * ts - int(cx), ty * ts - int(cy)
                scale = 1 + (economy.cpi - 5) * 0.08
                size = int(10 * min(scale, 2.2))
                label = f"${int(economy.cpi * 4)}↑"
                t = fnt_s.render(label, True, config.RED)
                surf.blit(t, (sx + 2, sy + 2))

    # Street / zone labels
    for label, lx, ly in [
        ("■ FED 聯準會大樓", 8, 1),
        ("─── 賓夕法尼亞大道 ───", 6, 9),
        ("■ 鮑威爾的公寓", 8, 13),
    ]:
        sx, sy = lx * ts - int(cx), ly * ts - int(cy)
        if -200 < sx < config.SCREEN_W + 200:
            t = fnt_s.render(label, True, (220,220,220))
            surf.blit(t, (sx, sy))
