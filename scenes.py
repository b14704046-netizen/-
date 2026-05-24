"""Scenes - city overworld + all building interiors."""
import pygame
import math
import random
import config
from entities import NPC

# Tile constants
F = 0   # floor (interior)
W = 1   # wall
R = 2   # road
G = 3   # grass
D = 4   # desk
T = 5   # terminal/PC
B = 6   # bed
S = 7   # sidewalk
C = 8   # carpet
DR = 9   # door
TR = 10  # tree
FT = 11  # fountain
BN = 12  # bench
LP = 13  # lamppost
SH = 14  # shop shelf
PD = 15  # podium
CF = 16  # coffee machine
TV = 17  # TV
SK = 18  # sink/counter
CH = 19  # chair
TB = 20  # table
PG = 21  # pigeon spot
FL = 22  # flowers
WD = 23  # wood floor
TI = 24  # tile floor
ST = 25  # stairs
BK = 26  # bookshelf
RG = 27  # rug
TR2 = 28  # building roof (decoration)
WIN = 29  # window
CR = 30  # crosswalk
PV = 31  # pavement (lighter sidewalk)
CB = 32  # cube/box
TM = 33  # treadmill
SG = 34  # sign
FN = 35  # fence
CN = 36  # column (capitol)
MR = 37  # marble floor
RP = 38  # red carpet
SC = 39  # screen wall

SOLID = {W, D, B, FT, BN, LP, SH, PD, CF, TV,
         SK, CH, TB, BK, TR, FN, CN, CB, TM, SG, SC}

TILE_COLOR = {
    F:   (182, 160, 138),
    W:   (62,  72,  92),     # steel/concrete tower base
    R:   (38,  42,  52),     # dark asphalt
    G:   (62,  128, 58),     # urban park green
    D:   (148, 108, 66),
    T:   (12,  68,  108),
    B:   (88,  128, 192),
    S:   (168, 168, 178),    # concrete sidewalk
    C:   (142, 88,  108),
    DR:  (62,  108, 148),    # glass entrance
    TR:  (40,  118, 50),
    FT:  (88,  175, 215),
    BN:  (88,  88,  102),    # metal bench
    LP:  (88,  88,  102),
    SH:  (158, 128, 88),
    PD:  (142, 100, 60),
    CF:  (52,  34,  24),
    TV:  (32,  32,  45),
    SK:  (205, 205, 215),
    CH:  (128, 88,  58),
    TB:  (152, 108, 68),
    PG:  (195, 195, 145),
    FL:  (155, 65,  185),
    WD:  (172, 128, 86),
    TI:  (198, 198, 205),
    ST:  (128, 128, 140),
    BK:  (105, 68,  38),
    RG:  (168, 62,  88),
    TR2: (138, 98,  58),
    WIN: (95,  170, 215),    # bright blue glass
    CR:  (235, 235, 240),    # painted zebra crossing
    PV:  (172, 172, 182),    # pavement
    CB:  (128, 108, 78),
    TM:  (55,  55,  68),
    SG:  (255, 200, 65),     # taxi-yellow sign
    FN:  (118, 118, 132),    # metal fence
    CN:  (235, 225, 205),
    MR:  (225, 222, 215),
    RP:  (148, 28,  38),
    SC:  (24,  55,  105),
}


def _row(*cells):
    return list(cells)


# ── City Overworld Map ────────────────────────────────────────────────
# 72 columns × 48 rows. New east district + south district added.
def _build_city():
    """Build city as a list of lists, then place doors/buildings."""
    cols, rows = 72, 48
    m = [[G for _ in range(cols)] for _ in range(rows)]

    # Horizontal roads: rows 8-10, 24-26 (original), 36-38 (new)
    for y in [8, 9, 10]:
        for x in range(cols):
            m[y][x] = R if y == 9 else S
    for y in [24, 25, 26]:
        for x in range(cols):
            m[y][x] = R if y == 25 else S
    for y in [36, 37, 38]:
        for x in range(cols):
            m[y][x] = R if y == 37 else S

    # Vertical roads: cols 23-25 (original), 49-51 (new east)
    for x in [23, 24, 25]:
        for y in range(rows):
            m[y][x] = R if x == 24 else S
    for x in [49, 50, 51]:
        for y in range(rows):
            m[y][x] = R if x == 50 else S

    # Crosswalks at all intersections
    for y in [8, 10, 24, 26, 36, 38]:
        for x in [23, 25, 49, 51]:
            m[y][x] = CR

    # Building plots — each has walls + door tile
    # Format: (x0, y0, x1, y1, door_x, door_y, scene_name)
    buildings = [
        # Top half (rows 1-7)
        (1,  1,  10, 7,  5,  7,  config.SCENE_APARTMENT),
        (12, 1,  21, 7,  16, 7,  config.SCENE_CAFE),
        (27, 1,  36, 7,  31, 7,  config.SCENE_SUPERMARKET),
        (38, 1,  48, 7,  43, 7,  config.SCENE_GYM),
        (52, 1,  70, 7,  61, 7,  config.SCENE_BANK),       # NEW

        # Middle (rows 11-23)
        (1,  11, 10, 23, 5,  23, config.SCENE_FED),
        (12, 11, 21, 23, 16, 23, config.SCENE_PRESS),
        # Park (27-36, 11-23) — open, no building
        (38, 11, 48, 23, 43, 23, config.SCENE_WALL_ST),
        (52, 11, 70, 23, 61, 23, config.SCENE_HOSPITAL),   # NEW

        # Bottom original (rows 27-34)
        (15, 27, 32, 34, 23, 27, config.SCENE_CAPITOL),

        # New south district (rows 39-47)
        (1,  39, 22, 47, 11, 39, config.SCENE_UNIVERSITY),  # NEW
    ]

    for x0, y0, x1, y1, dx, dy, _ in buildings:
        # Walls
        for x in range(x0, x1+1):
            m[y0][x] = W
            m[y1][x] = W
        for y in range(y0, y1+1):
            m[y][x0] = W
            m[y][x1] = W
        # Windows on wall
        for x in range(x0+2, x1-1, 3):
            if m[y0][x] == W:
                m[y0][x] = WIN
        # Interior floor
        for y in range(y0+1, y1):
            for x in range(x0+1, x1):
                m[y][x] = WD if y < 8 else TI
        # Door
        m[dy][dx] = DR

    # Park area in middle (27-36, 11-23) — unchanged
    for y in range(12, 23):
        for x in range(27, 37):
            m[y][x] = G
    for tx, ty in [(28, 13), (30, 12), (33, 12), (35, 13), (28, 16), (35, 16),
                   (28, 20), (30, 21), (33, 21), (35, 20), (31, 16), (32, 18),
                   (29, 15), (34, 14), (30, 19), (36, 17)]:
        m[ty][tx] = TR
    m[17][31] = FT
    m[17][32] = FT
    m[18][31] = FT
    m[18][32] = FT
    m[15][29] = BN
    m[15][34] = BN
    m[20][29] = BN
    m[20][34] = BN
    m[16][30] = PG
    m[19][33] = PG
    m[14][32] = PG
    m[21][31] = PG
    for tx, ty in [(28, 17), (29, 18), (33, 16), (34, 19), (31, 14), (32, 21)]:
        m[ty][tx] = FL

    # East district open space — benches + trees (cols 52-70, rows 8-10 road strip)
    for tx, ty in [(54, 11), (58, 11), (63, 11), (67, 11),
                   (54, 24), (58, 24), (63, 24), (67, 24)]:
        if m[ty][tx] == S:
            m[ty][tx] = BN
    # East plaza between bank (rows 1-7) and hospital (rows 11-23): rows 8-10 is road
    for tx, ty in [(53, 8), (56, 8), (60, 8), (64, 8), (68, 8)]:
        if m[ty][tx] == S:
            m[ty][tx] = LP

    # South district open plazas (cols 27-70, rows 39-47)
    for y in range(40, 48):
        for x in range(27, 71):
            if m[y][x] == G:
                pass  # will be handled by random below
    # Park-like area south-east of university
    for tx, ty in [(26, 41), (27, 40), (30, 42), (33, 41), (36, 43),
                   (40, 41), (44, 40), (47, 42), (50, 41), (53, 43),
                   (57, 40), (60, 42), (64, 41), (67, 43), (70, 41)]:
        if 0 <= ty < rows and 0 <= tx < cols and m[ty][tx] == G:
            m[ty][tx] = TR
    for tx, ty in [(28, 43), (31, 44), (35, 42), (42, 44), (46, 43), (51, 42)]:
        if 0 <= ty < rows and 0 <= tx < cols and m[ty][tx] == G:
            m[ty][tx] = FL
    # Benches in south plaza
    for tx, ty in [(30, 40), (45, 40), (60, 40), (30, 45), (45, 45), (60, 45)]:
        if 0 <= ty < rows and 0 <= tx < cols and m[ty][tx] == G:
            m[ty][tx] = BN
    # Fountain in south central plaza
    for ty in [42, 43]:
        for tx in [37, 38]:
            m[ty][tx] = FT
    m[42][36] = FL
    m[42][39] = FL
    m[43][36] = FL
    m[43][39] = FL

    # Random trees/flowers on remaining grass
    for x in range(0, cols):
        for y in range(0, rows):
            if m[y][x] == G:
                in_park = (27 <= x <= 36 and 11 <= y <= 23)
                in_south_plaza = (27 <= x <= 70 and 39 <= y <= 47)
                if random.random() < 0.05 and not in_park and not in_south_plaza:
                    m[y][x] = TR
                elif random.random() < 0.06 and not in_park:
                    m[y][x] = FL

    # Lampposts along all road sidewalks
    for x in range(2, cols, 5):
        for sw_y in [7, 11, 23, 27, 35, 39]:
            if 0 <= sw_y < rows and m[sw_y][x] == S:
                m[sw_y][x] = LP

    # Bus stops
    for bx, by in [(8, 7), (20, 11), (38, 27), (12, 23),
                   (56, 7), (56, 23), (8, 35), (30, 35)]:
        if 0 <= by < rows and 0 <= bx < cols and m[by][bx] == S:
            m[by][bx] = BN
        if 0 <= by < rows and 0 <= bx+1 < cols and m[by][bx+1] == S:
            m[by][bx+1] = SG

    # Newspaper stands (SG)
    for nx, ny in [(4, 8), (14, 24), (40, 10), (55, 10), (55, 26), (8, 35)]:
        if 0 <= ny < rows and 0 <= nx < cols and m[ny][nx] == S:
            m[ny][nx] = SG
    # ATMs (CB)
    for ax, ay in [(39, 8), (22, 26), (48, 26), (48, 10)]:
        if 0 <= ay < rows and 0 <= ax < cols and m[ay][ax] == S:
            m[ay][ax] = CB
    # Graffiti walls (SG)
    for gx, gy in [(11, 10), (26, 26), (26, 36), (48, 38)]:
        if 0 <= gy < rows and 0 <= gx < cols and m[gy][gx] == S:
            m[gy][gx] = SG

    signs = {
        (4,  7):  "公寓",
        (15, 7):  "咖啡廳",
        (30, 7):  "超市",
        (42, 7):  "健身房",
        (60, 7):  "聯邦銀行",
        (4,  23): "聯準會",
        (15, 23): "新聞室",
        (42, 23): "華爾街",
        (60, 23): "醫療中心",
        (22, 27): "國會",
        (10, 39): "聯邦大學",
        (4,  8):  "報攤",
        (14, 24): "報攤",
        (39, 8):  "ATM",
        (22, 26): "ATM",
        (11, 10): "塗鴉牆",
        (26, 26): "塗鴉牆",
        (55, 10): "報攤",
        (48, 26): "ATM",
    }

    return m, buildings, signs


CITY_MAP, CITY_BUILDINGS, CITY_SIGNS = _build_city()


# ── Helper to make a simple rectangular room ──────────────────────────
def _room(cols, rows, floor=WD):
    m = [[floor for _ in range(cols)] for _ in range(rows)]
    for x in range(cols):
        m[0][x] = W
        m[rows-1][x] = W
    for y in range(rows):
        m[y][0] = W
        m[y][cols-1] = W
    return m


# ── Apartment ─────────────────────────────────────────────────────────
def _build_apartment():
    m = _room(20, 14, WD)
    # Door at bottom
    m[13][10] = DR
    # Bedroom
    m[2][2] = m[2][3] = B
    m[3][2] = m[3][3] = B
    # Living room TV
    m[2][10] = TV
    m[2][11] = TV
    # Couch
    m[3][10] = CH
    m[3][11] = CH
    m[3][12] = CH
    # Coffee table
    m[5][11] = TB
    # Kitchen
    m[2][16] = SK
    m[2][17] = CF
    m[3][16] = TB
    m[3][17] = TB
    # Bookshelf
    m[2][6] = BK
    m[2][7] = BK
    # Fridge in kitchen corner
    m[2][14] = CB
    # Rug in living area
    for x in range(9, 14):
        for y in range(7, 11):
            m[y][x] = RG
    # Plant/flowers in corners
    m[12][2] = FL
    m[12][17] = FL
    # Window walls
    m[0][5] = WIN
    m[0][10] = WIN
    m[0][15] = WIN

    npcs = []
    doors = [{"x": 10, "y": 13, "target": config.SCENE_CITY,
              "spawn_tx": 5, "spawn_ty": 8}]
    objects = [
        {"x": 2,  "y": 2, "type": "bed",    "label": "床（睡覺跳過時間）"},
        {"x": 17, "y": 2, "type": "coffee", "label": "咖啡機（手沖小遊戲）"},
        {"x": 11, "y": 2, "type": "tv",     "label": "電視（看新聞）"},
        {"x": 6,  "y": 2, "type": "books",  "label": "書架（讀經濟學）"},
        {"x": 14, "y": 2, "type": "fridge", "label": "冰箱（看食物價格）"},
    ]
    return m, npcs, doors, objects, (10, 12)


# ── Cafe ──────────────────────────────────────────────────────────────
def _build_cafe():
    m = _room(18, 12, TI)
    m[11][9] = DR
    # Counter
    for x in range(3, 14):
        m[3][x] = SK
    # Coffee machines on counter
    m[2][5] = CF
    m[2][8] = CF
    m[2][11] = CF
    # Tables and chairs
    for tx in [3, 7, 11]:
        m[7][tx] = TB
        m[7][tx+1] = TB
        m[6][tx] = CH
        m[8][tx] = CH
    # Bulletin board on east wall
    m[5][16] = BK
    # Window
    m[0][4] = WIN
    m[0][9] = WIN
    m[0][13] = WIN

    npcs = [
        NPC(6, 4, "barista",    "店員Anna",   "cafe_barista",    0),
        NPC(4, 7, "citizen",    "上班族",      "cafe_customer1",  0),
        NPC(12, 7, "citizen",   "學生",        "cafe_customer2",  0),
        NPC(8, 7, "citizen",    "作家 David",  "cafe_writer",     1),
        NPC(14, 5, "trader",    "股市老手",    "cafe_trader",     0),
    ]
    doors = [{"x": 9, "y": 11, "target": config.SCENE_CITY,
              "spawn_tx": 16, "spawn_ty": 8}]
    objects = [
        {"x": 5,  "y": 2,  "type": "coffee_mg",  "label": "鷹派咖啡（小遊戲）"},
        {"x": 16, "y": 5,  "type": "bulletin",    "label": "公告欄（看本地消息）"},
        {"x": 13, "y": 7,  "type": "wifi_news",   "label": "WiFi 新聞（看即時動態）"},
    ]
    return m, npcs, doors, objects, (9, 10)


# ── Fed Building ──────────────────────────────────────────────────────
def _build_fed():
    m = _room(22, 14, MR)
    m[13][11] = DR
    # Red carpet entrance
    for y in range(9, 13):
        m[y][10] = RP
        m[y][11] = RP
        m[y][12] = RP
    # Boardroom desk
    for x in range(5, 17):
        m[5][x] = TB
    # Chairs around boardroom
    for x in range(5, 17, 2):
        m[4][x] = CH
        m[6][x] = CH
    # Powell's office
    m[2][3] = D
    m[2][4] = T  # main terminal
    # Secondary terminals
    m[2][10] = T
    m[2][15] = D
    m[2][18] = T
    m[2][19] = D
    # Columns (marble)
    m[8][3] = CN
    m[8][18] = CN
    # Windows
    m[0][6] = WIN
    m[0][11] = WIN
    m[0][16] = WIN

    npcs = [
        NPC(8,  4,  "guard",      "守衛",            "fed_guard",       2),
        NPC(15, 4,  "secretary",  "秘書 Jane",        "fed_secretary",   0),
        NPC(12, 8,  "politician", "副主席 Brian",     "fed_vicechair",   0),
        NPC(5,  6,  "politician", "首席經濟學家 Smith", "fed_economist1",  0),
        NPC(18, 6,  "secretary",  "政策分析師 Park",  "fed_analyst",     1),
    ]
    doors = [{"x": 11, "y": 13, "target": config.SCENE_CITY,
              "spawn_tx": 5, "spawn_ty": 24}]
    objects = [
        {"x": 4,  "y": 2, "type": "terminal",    "label": "主控終端（經濟模擬器）"},
        {"x": 10, "y": 2, "type": "terminal",    "label": "副控終端"},
        {"x": 18, "y": 2, "type": "terminal",    "label": "資料終端"},
        {"x": 11, "y": 5, "type": "policy_memo", "label": "政策備忘錄（Taylor Rule 建議）"},
    ]
    return m, npcs, doors, objects, (11, 12)


# ── Supermarket ───────────────────────────────────────────────────────
def _build_supermarket():
    m = _room(20, 13, TI)
    m[12][10] = DR
    # Aisles of shelves
    for ax in [3, 7, 11, 15]:
        for y in range(2, 9):
            m[y][ax] = SH
    # Checkout counter
    for x in range(4, 16, 3):
        m[10][x] = SK
    npcs = [
        NPC(2, 4, "shopper", "怒火主婦",     "sm_angry_mom", 0),
        NPC(5, 6, "elder",   "退休伯伯",     "sm_elder", 0),
        NPC(13, 4, "shopper", "年輕媽媽",     "sm_young_mom", 0),
        NPC(17, 7, "child",  "小朋友",       "sm_child", 0),
        NPC(9, 10, "shopper", "收銀員",       "sm_cashier", 0),
    ]
    doors = [{"x": 10, "y": 12, "target": config.SCENE_CITY,
              "spawn_tx": 31, "spawn_ty": 8}]
    objects = [
        {"x": 3, "y": 3, "type": "price_check", "label": "看蛋價"},
        {"x": 7, "y": 3, "type": "price_check", "label": "看牛奶價"},
        {"x": 11, "y": 3, "type": "price_check", "label": "看油價"},
        {"x": 15, "y": 3, "type": "price_check", "label": "看肉價"},
    ]
    return m, npcs, doors, objects, (10, 11)


# ── Gym ───────────────────────────────────────────────────────────────
def _build_gym():
    m = _room(16, 11, WD)
    m[10][8] = DR
    # Treadmills
    for x in [3, 6, 9, 12]:
        m[3][x] = TM
        m[4][x] = TM
    # Weight area
    m[7][3] = CB
    m[7][4] = CB
    m[7][11] = CB
    m[7][12] = CB
    # TV
    m[1][8] = TV
    npcs = [
        NPC(3,  5,  "citizen", "教練 Mike",  "gym_coach",    0),
        NPC(10, 6,  "citizen", "健身愛好者", "gym_member",   0),
        NPC(3,  7,  "citizen", "練腿日男",   "gym_heavy",    2),
        NPC(12, 4,  "citizen", "健身新人",   "gym_newbie",   1),
    ]
    doors = [{"x": 8, "y": 10, "target": config.SCENE_CITY,
              "spawn_tx": 43, "spawn_ty": 8}]
    objects = [
        {"x": 6,  "y": 3, "type": "treadmill_mg", "label": "中性利率跑步機（節奏小遊戲）"},
        {"x": 4,  "y": 7, "type": "workout",       "label": "舉重（鍛煉：支持度 +3）"},
        {"x": 10, "y": 1, "type": "tv",            "label": "電視（看財經新聞）"},
    ]
    return m, npcs, doors, objects, (8, 9)


# ── Press Room ────────────────────────────────────────────────────────
def _build_press():
    m = _room(18, 12, MR)
    m[11][9] = DR
    # Podium at front
    m[2][8] = PD
    m[2][9] = PD
    # Audience seats
    for sy in [5, 6, 8, 9]:
        for sx in range(3, 15, 2):
            m[sy][sx] = CH
    # Screen behind podium
    for x in range(6, 12):
        m[1][x] = SC
    npcs = [
        NPC(4, 6, "journalist", "華爾街日報",  "press_wsj", 0),
        NPC(8, 6, "journalist", "CNBC",       "press_cnbc", 0),
        NPC(12, 6, "journalist", "彭博社",      "press_bloomberg", 0),
        NPC(6, 9, "journalist", "金融時報",    "press_ft", 0),
        NPC(10, 9, "journalist", "路透",        "press_reuters", 0),
    ]
    doors = [{"x": 9, "y": 11, "target": config.SCENE_CITY,
              "spawn_tx": 16, "spawn_ty": 24}]
    objects = [
        {"x": 8, "y": 2, "type": "press_mg", "label": "開記者會（小遊戲）"},
    ]
    return m, npcs, doors, objects, (9, 10)


# ── Wall Street ───────────────────────────────────────────────────────
def _build_wall_st():
    m = _room(18, 12, MR)
    m[11][9] = DR
    # Trading floor — desks with screens
    for x in [3, 6, 9, 12, 15]:
        m[3][x] = D
        m[2][x] = T
        m[6][x] = D
        m[5][x] = T
    # Big board on north wall
    for x in range(4, 14):
        m[1][x] = SC
    # Bull statue
    m[9][3] = CB
    # Bear statue
    m[9][14] = CB
    npcs = [
        NPC(4, 4, "trader", "多頭交易員",     "ws_bull", 0),
        NPC(7, 4, "trader", "空頭交易員",     "ws_bear", 0),
        NPC(10, 4, "trader", "量化基金經理",   "ws_quant", 0),
        NPC(13, 4, "trader", "債券交易員",     "ws_bond", 0),
        NPC(5, 8, "trader", "新進分析師",     "ws_analyst", 0),
    ]
    doors = [{"x": 9, "y": 11, "target": config.SCENE_CITY,
              "spawn_tx": 43, "spawn_ty": 24}]
    objects = [
        {"x": 9,  "y": 8, "type": "ticker",     "label": "看即時報價"},
        {"x": 9,  "y": 1, "type": "big_board",  "label": "大看板（詳細市場數據）"},
        {"x": 15, "y": 8, "type": "phone_call", "label": "紅色電話（打給財政部長）"},
    ]
    return m, npcs, doors, objects, (9, 10)


# ── Capitol ───────────────────────────────────────────────────────────
def _build_capitol():
    m = _room(22, 14, MR)
    m[13][11] = DR
    # Red carpet
    for y in range(8, 13):
        m[y][10] = RP
        m[y][11] = RP
        m[y][12] = RP
    # Columns at front
    for x in [3, 7, 14, 18]:
        m[2][x] = CN
    # Tiered seating
    for y in [4, 5, 7]:
        for x in range(3, 19, 2):
            m[y][x] = CH
    # Speaker's podium
    m[3][10] = PD
    m[3][11] = PD
    npcs = [
        NPC(4, 4, "politician", "參議員 Warren", "cap_warren", 0),
        NPC(8, 4, "politician", "參議員 Cruz",   "cap_cruz", 0),
        NPC(13, 4, "politician", "參議員 Sanders", "cap_sanders", 0),
        NPC(17, 4, "politician", "議長",          "cap_speaker", 0),
    ]
    doors = [{"x": 11, "y": 13, "target": config.SCENE_CITY,
              "spawn_tx": 23, "spawn_ty": 27}]
    objects = [
        {"x": 10, "y": 3, "type": "testify", "label": "上台聽證（記者會樣式）"},
    ]
    return m, npcs, doors, objects, (11, 12)


# ── Park ──────────────────────────────────────────────────────────────
def _build_park():
    cols, rows = 24, 16
    m = [[G for _ in range(cols)] for _ in range(rows)]
    # Path
    for x in range(cols):
        m[8][x] = PV
    # Edge fences
    for x in range(cols):
        m[0][x] = TR
        m[rows-1][x] = TR
    for y in range(rows):
        m[y][0] = TR
        m[y][cols-1] = TR
    m[15][12] = PV  # exit
    # Fountain
    for y in [6, 7]:
        for x in [11, 12, 13]:
            m[y][x] = FT
    # Benches
    m[5][4] = BN
    m[5][18] = BN
    m[10][4] = BN
    m[10][18] = BN
    # Trees
    for tx, ty in [(3, 3), (6, 2), (10, 3), (15, 2), (20, 3), (3, 13), (6, 14), (10, 14), (15, 13), (20, 14)]:
        m[ty][tx] = TR
    # Pigeon spots
    for tx, ty in [(5, 9), (8, 10), (11, 9), (14, 10), (17, 9), (20, 10)]:
        m[ty][tx] = PG
    # Flowers
    for tx, ty in [(4, 7), (6, 7), (18, 7), (20, 7), (4, 11), (6, 11), (18, 11), (20, 11)]:
        m[ty][tx] = FL
    # Newspaper stand near entrance
    m[13][3] = SG

    npcs = [
        NPC(7, 5, "elder",     "公園老伯",  "park_elder", 0),
        NPC(15, 5, "child",    "小孩",      "park_kid", 1),
        NPC(20, 11, "citizen", "慢跑者",    "park_jogger", 2),
        NPC(18, 4, "elder",    "下棋老人",  "park_elder", 1),
    ]
    doors = [{"x": 12, "y": 15, "target": config.SCENE_CITY,
              "spawn_tx": 31, "spawn_ty": 15}]
    objects = [
        {"x": 11, "y": 9, "type": "pigeon_mg",     "label": "餵鴿子（紓壓小遊戲）"},
        {"x": 12, "y": 6, "type": "fountain_coin", "label": "噴泉（丟硬幣許願）"},
        {"x": 3,  "y": 13, "type": "newspaper",    "label": "報攤（看今日頭條）"},
    ]
    return m, npcs, doors, objects, (12, 14)


# ── Bank ──────────────────────────────────────────────────────────────
def _build_bank():
    m = _room(22, 14, MR)
    m[13][11] = DR
    # Red carpet entrance
    for y in range(9, 13):
        m[y][10] = RP
        m[y][11] = RP
        m[y][12] = RP
    # Teller counters
    for x in range(4, 18):
        m[4][x] = SK
    # Vault door (decorative CB block cluster)
    for y in range(2, 5):
        for x in range(2, 5):
            m[y][x] = CB
    # Trading terminals
    for x in [6, 9, 12, 15, 18]:
        m[7][x] = T
        m[6][x] = D
    # Columns
    m[9][3] = CN
    m[9][18] = CN
    # Windows
    m[0][6] = WIN
    m[0][11] = WIN
    m[0][16] = WIN

    npcs = [
        NPC(10, 5,  "trader",     "行員 Lisa",     "bank_teller",   0),
        NPC(14, 8,  "trader",     "投資人 Marcus", "bank_investor", 0),
        NPC(5,  8,  "politician", "貸款專員 Chen", "bank_loan",     0),
        NPC(3,  5,  "trader",     "行長 White",    "bank_manager",  0),
        NPC(18, 8,  "citizen",    "企業客戶",      "bank_corp",     1),
    ]
    doors = [{"x": 11, "y": 13, "target": config.SCENE_CITY,
              "spawn_tx": 61, "spawn_ty": 8}]
    objects = [
        {"x": 9,  "y": 7, "type": "terminal", "label": "投資終端（市場數據）"},
        {"x": 12, "y": 7, "type": "ticker",   "label": "即時報價"},
        {"x": 3,  "y": 3, "type": "vault",    "label": "聯邦金庫（財富分配報告）"},
    ]
    return m, npcs, doors, objects, (11, 12)


# ── Hospital ──────────────────────────────────────────────────────────
def _build_hospital():
    m = _room(22, 14, TI)
    m[13][11] = DR
    # Reception desk
    for x in range(5, 17):
        m[3][x] = SK
    # Beds (examination rooms)
    for bx, by_b in [(3, 6), (3, 9), (18, 6), (18, 9)]:
        m[by_b][bx] = B
        m[by_b][bx+1] = B
    # Medical equipment
    m[2][3] = TV
    m[2][18] = TV
    # Columns
    m[7][7] = CN
    m[7][14] = CN
    # Windows
    m[0][5] = WIN
    m[0][11] = WIN
    m[0][17] = WIN
    # Rug in waiting area
    for x in range(8, 14):
        for y in range(5, 8):
            m[y][x] = RG

    npcs = [
        NPC(9,  4,  "secretary",  "王醫生",       "hospital_doctor",   0),
        NPC(14, 4,  "citizen",    "護士 Amy",      "hospital_nurse",    2),
        NPC(5,  7,  "citizen",    "病患",          "hospital_patient",  0),
        NPC(16, 8,  "politician", "主任 Chang",    "hospital_chief",    0),
        NPC(19, 5,  "citizen",    "病人家屬",      "hospital_family",   1),
    ]
    doors = [{"x": 11, "y": 13, "target": config.SCENE_CITY,
              "spawn_tx": 61, "spawn_ty": 24}]
    objects = [
        {"x": 11, "y": 3, "type": "books",   "label": "醫學期刊（放鬆閱讀）"},
        {"x": 10, "y": 6, "type": "checkup", "label": "健康檢查站（恢復血量）"},
    ]
    return m, npcs, doors, objects, (11, 12)


# ── University ────────────────────────────────────────────────────────
def _build_university():
    m = _room(24, 16, WD)
    m[0][12] = DR   # north wall door — spawn (12,1) is now clear
    # Screen moved to south end so entry rows 1-2 stay clear
    for x in range(9, 15):
        m[13][x] = SC
    # Podium just north of screen
    m[11][11] = PD
    m[11][12] = PD
    # Tiered lecture seating (rows 3-9, audience faces south toward screen)
    for sy in [3, 4, 6, 7, 9]:
        for sx in range(3, 21, 2):
            m[sy][sx] = CH
    # Library corner (west side)
    for x in range(2, 7):
        m[12][x] = BK
    # Study tables (east side)
    for tx in [16, 19]:
        m[12][tx] = TB
        m[12][tx+1] = TB
        m[13][tx] = CH
        m[13][tx+1] = CH
    # Vending machine near entry
    m[2][2] = CB
    # Windows
    m[0][6] = WIN
    m[0][17] = WIN
    m[15][6] = WIN
    m[15][12] = WIN
    m[15][18] = WIN

    npcs = [
        NPC(12, 10, "politician", "陳教授",          "univ_prof",     0),
        NPC(5,  5,  "citizen",    "學生 Kevin",       "univ_student",  1),
        NPC(15, 5,  "citizen",    "學生 Mia",         "univ_student2", 0),
        NPC(4,  12, "citizen",    "圖書館員",          "park_jogger",   0),
        NPC(9,  8,  "citizen",    "研究生 Lin",        "univ_grad",     1),
        NPC(18, 8,  "politician", "訪問學者 Dr. Kim",  "univ_visitor",  0),
    ]
    doors = [{"x": 12, "y": 0, "target": config.SCENE_CITY,
              "spawn_tx": 11, "spawn_ty": 38}]
    objects = [
        {"x": 11, "y": 11, "type": "press_mg", "label": "上台演講（記者會模式）"},
        {"x": 4,  "y": 12, "type": "books",    "label": "圖書館（讀經濟學）"},
        {"x": 2,  "y": 2,  "type": "vend",     "label": "自動販賣機（買飲料）"},
    ]
    return m, npcs, doors, objects, (12, 1)


# ── Scene class ───────────────────────────────────────────────────────
class Scene:
    def __init__(self, name, tiles, npcs, doors, objects, spawn=(2, 2)):
        self.name = name
        self.tiles = tiles
        self.rows = len(tiles)
        self.cols = len(tiles[0])
        self.pixel_w = self.cols * config.TILE_SIZE
        self.pixel_h = self.rows * config.TILE_SIZE
        self.npcs = npcs
        self.doors = doors
        self.objects = objects
        self.spawn = spawn

    def get_tile(self, tx, ty):
        if 0 <= tx < self.cols and 0 <= ty < self.rows:
            return self.tiles[ty][tx]
        return W

    def is_solid(self, x, y, w, h):
        m = 5
        for cx, cy in [(x+m, y+m), (x+w-m, y+m), (x+m, y+h-m), (x+w-m, y+h-m)]:
            tx, ty = int(cx // config.TILE_SIZE), int(cy // config.TILE_SIZE)
            if not (0 <= tx < self.cols and 0 <= ty < self.rows):
                return True
            if self.tiles[ty][tx] in SOLID:
                return True
        return False


def build_all_scenes():
    """Construct every scene and return a dict."""
    scenes = {}

    # City overworld
    park_door = {"x": 31, "y": 14, "target": config.SCENE_PARK,
                 "spawn_tx": 12, "spawn_ty": 14}
    city_doors = [park_door]
    spawn_map = {
        config.SCENE_APARTMENT:  (10, 12),
        config.SCENE_CAFE:       (9,  10),
        config.SCENE_SUPERMARKET: (10, 11),
        config.SCENE_GYM:        (8,   9),
        config.SCENE_FED:        (11, 12),
        config.SCENE_PRESS:      (9,  10),
        config.SCENE_WALL_ST:    (9,  10),
        config.SCENE_CAPITOL:    (11, 12),
        config.SCENE_BANK:       (11, 12),
        config.SCENE_HOSPITAL:   (11, 12),
        config.SCENE_UNIVERSITY: (12,  1),
    }
    for x0, y0, x1, y1, dx, dy, target in CITY_BUILDINGS:
        sp = spawn_map[target]
        city_doors.append({"x": dx, "y": dy, "target": target,
                           "spawn_tx": sp[0], "spawn_ty": sp[1]})

    city_npcs = [
        # Original city NPCs
        NPC(15, 9,  "citizen",    "路人甲",    "street_citizen_1",  3),
        NPC(30, 9,  "journalist", "記者",      "street_journalist", 2),
        NPC(20, 25, "protester",  "抗議者",    "street_protester",  1),
        NPC(35, 25, "citizen",    "上班族",    "street_citizen_2",  3),
        NPC(8,  25, "unemployed", "失業者",    "street_unemployed", 1),
        NPC(24, 12, "child",      "小朋友",    "street_child",      2),
        NPC(40, 12, "elder",      "退休者",    "street_elder",      0),
        NPC(45, 30, "citizen",    "夜班工人",  "street_worker",     2),
        NPC(12, 25, "protester",  "示威者",    "street_protester",  2),
        NPC(47, 9,  "shopper",    "購物者",    "street_citizen_2",  1),
        # East district NPCs (near bank & hospital)
        NPC(57, 9,  "trader",     "銀行家",    "city_banker",       2),
        NPC(64, 9,  "citizen",    "東區居民",  "city_retiree_east", 1),
        NPC(57, 25, "citizen",    "護士",      "city_nurse",        2),
        NPC(63, 25, "elder",      "退休阿姨",  "city_retiree_east", 0),
        # South district NPCs (near university + plaza)
        NPC(11, 37, "citizen",    "大學生",    "city_student",      2),
        NPC(35, 41, "citizen",    "南區居民",  "city_worker_south", 1),
        NPC(55, 41, "unemployed", "失業者",    "street_unemployed", 2),
        NPC(42, 43, "child",      "小孩",      "street_child",      1),
        NPC(28, 30, "citizen",    "路人",      "street_citizen_2",  2),
        NPC(60, 30, "journalist", "記者",      "street_journalist", 1),
    ]
    city_objects = [
        {"x": 4,  "y": 8,  "type": "newspaper", "label": "報攤（看今日頭條）"},
        {"x": 14, "y": 24, "type": "newspaper",  "label": "報攤（看今日頭條）"},
        {"x": 39, "y": 8,  "type": "atm",        "label": "ATM（查帳戶）"},
        {"x": 22, "y": 26, "type": "atm",         "label": "ATM（查帳戶）"},
        {"x": 11, "y": 10, "type": "graffiti",    "label": "塗鴉牆（看民意）"},
        {"x": 26, "y": 26, "type": "graffiti",    "label": "塗鴉牆（看民意）"},
        {"x": 55, "y": 10, "type": "newspaper",   "label": "報攤（東區）"},
        {"x": 48, "y": 26, "type": "atm",         "label": "ATM（東區）"},
        {"x": 26, "y": 36, "type": "graffiti",    "label": "塗鴉牆（南區）"},
        {"x": 8,  "y": 35, "type": "newspaper",   "label": "報攤（南區）"},
    ]
    scenes[config.SCENE_CITY] = Scene(config.SCENE_CITY, CITY_MAP,
                                      city_npcs, city_doors,
                                      city_objects, spawn=(5, 8))

    # Interiors
    for name, builder in [
        (config.SCENE_APARTMENT,   _build_apartment),
        (config.SCENE_CAFE,        _build_cafe),
        (config.SCENE_FED,         _build_fed),
        (config.SCENE_SUPERMARKET, _build_supermarket),
        (config.SCENE_GYM,         _build_gym),
        (config.SCENE_PRESS,       _build_press),
        (config.SCENE_WALL_ST,     _build_wall_st),
        (config.SCENE_CAPITOL,     _build_capitol),
        (config.SCENE_PARK,        _build_park),
        (config.SCENE_BANK,        _build_bank),
        (config.SCENE_HOSPITAL,    _build_hospital),
        (config.SCENE_UNIVERSITY,  _build_university),
    ]:
        tiles, npcs, doors, objects, spawn = builder()
        scenes[name] = Scene(name, tiles, npcs, doors, objects, spawn=spawn)

    return scenes


# ── Rendering ─────────────────────────────────────────────────────────
BUILDING_EXTERIORS = {
    # Each building gets a base body color, accent trim and a kind selector.
    config.SCENE_APARTMENT:   {"body": (148, 122, 95),  "trim": (78, 62, 48),    "glass": (118, 168, 205), "kind": "apartment"},
    config.SCENE_CAFE:        {"body": (115, 78, 52),   "trim": (62, 42, 28),    "glass": (235, 180, 95),  "kind": "cafe"},
    config.SCENE_SUPERMARKET: {"body": (95, 138, 95),   "trim": (45, 78, 48),    "glass": (215, 235, 215), "kind": "supermarket"},
    config.SCENE_GYM:         {"body": (78, 88, 105),   "trim": (38, 48, 65),    "glass": (185, 215, 230), "kind": "gym"},
    config.SCENE_BANK:        {"body": (215, 200, 165), "trim": (138, 118, 78),  "glass": (215, 215, 195), "kind": "bank"},
    config.SCENE_FED:         {"body": (225, 220, 205), "trim": (148, 128, 95),  "glass": (185, 200, 215), "kind": "fed"},
    config.SCENE_PRESS:       {"body": (62, 88, 128),   "trim": (28, 42, 75),    "glass": (115, 165, 220), "kind": "press"},
    config.SCENE_WALL_ST:     {"body": (38, 52, 78),    "trim": (15, 22, 38),    "glass": (95, 165, 215),  "kind": "wallst"},
    config.SCENE_HOSPITAL:    {"body": (235, 240, 245), "trim": (148, 158, 175), "glass": (185, 215, 235), "kind": "hospital"},
    config.SCENE_CAPITOL:     {"body": (232, 225, 208), "trim": (165, 152, 128), "glass": (215, 220, 195), "kind": "capitol"},
    config.SCENE_UNIVERSITY:  {"body": (155, 95, 78),   "trim": (95, 52, 38),    "glass": (215, 220, 200), "kind": "university"},
}


def _draw_skyscraper_body(surf, x, y, w, h, body, trim, glass,
                          story_h=18, window_w=14, window_gap=6,
                          ground_h=22, roof_h=14):
    """Draw a 2.5D skyscraper facade inside the building footprint.

    Layout (top → bottom):
      • roof_h pixels of building crown / rooftop deck
      • middle band: repeated stories of glass windows
      • ground_h pixels of ground floor with main entrance / lobby
    Adds right-side shadow + top/left highlights for 3D depth.
    """
    # Body base colour
    pygame.draw.rect(surf, body, pygame.Rect(x, y, w, h))

    # Right-side depth shadow (suggests the building has a "right wall")
    sh_w = max(6, w // 14)
    shadow_s = pygame.Surface((sh_w, h), pygame.SRCALPHA)
    for i in range(sh_w):
        a = int(140 * (i / max(1, sh_w - 1)))
        pygame.draw.line(shadow_s, (0, 0, 0, a), (i, 0), (i, h))
    surf.blit(shadow_s, (x + w - sh_w, y))

    # Top-left highlight (sun-lit edge)
    pygame.draw.line(surf, (min(255, body[0] + 35),
                            min(255, body[1] + 35),
                            min(255, body[2] + 35)),
                     (x, y), (x + w - sh_w, y), 2)
    pygame.draw.line(surf, (min(255, body[0] + 20),
                            min(255, body[1] + 20),
                            min(255, body[2] + 20)),
                     (x, y), (x, y + h - 2), 1)

    # Crown band (roof level) — darker trim with cornice line
    pygame.draw.rect(surf, trim, pygame.Rect(x, y, w - sh_w, roof_h))
    pygame.draw.line(surf, (min(255, trim[0] + 30),
                            min(255, trim[1] + 30),
                            min(255, trim[2] + 30)),
                     (x, y + 1), (x + w - sh_w, y + 1), 1)
    pygame.draw.line(surf, (max(0, trim[0] - 25),
                            max(0, trim[1] - 25),
                            max(0, trim[2] - 25)),
                     (x, y + roof_h - 1), (x + w - sh_w, y + roof_h - 1), 1)

    # Window grid (curtain wall)
    win_zone_top = y + roof_h + 4
    win_zone_bottom = y + h - ground_h
    win_zone_h = win_zone_bottom - win_zone_top
    inner_w = w - sh_w - 8
    stories = max(1, win_zone_h // story_h)
    cols = max(2, (inner_w + window_gap) // (window_w + window_gap))
    # Re-centre the grid so columns are evenly distributed
    actual_grid_w = cols * window_w + (cols - 1) * window_gap
    grid_x0 = x + (w - sh_w - actual_grid_w) // 2
    glass_dark = (max(0, glass[0] - 35),
                  max(0, glass[1] - 35), max(0, glass[2] - 35))
    glass_hi = (min(255, glass[0] + 35), min(255,
                glass[1] + 35), min(255, glass[2] + 35))
    for s in range(stories):
        wy = win_zone_top + s * story_h
        if wy + story_h - 6 > win_zone_bottom:
            break
        for c in range(cols):
            wx = grid_x0 + c * (window_w + window_gap)
            wh_px = story_h - 6
            # Frame
            pygame.draw.rect(surf, trim,
                             pygame.Rect(wx - 1, wy - 1, window_w + 2, wh_px + 2))
            # Glass (lit windows: occasionally brighter for night-life feel)
            lit = ((c * 7 + s * 13) % 11 == 0)
            g = glass_hi if lit else glass
            pygame.draw.rect(surf, g, pygame.Rect(wx, wy, window_w, wh_px))
            # Inner mullion
            pygame.draw.line(surf, glass_dark,
                             (wx + window_w // 2, wy),
                             (wx + window_w // 2, wy + wh_px), 1)
            # Reflection highlight
            pygame.draw.line(surf, (min(255, g[0] + 50),
                                    min(255, g[1] + 50),
                                    min(255, g[2] + 50)),
                             (wx + 1, wy + 1), (wx + 4, wy + 4), 1)

    # Ground floor base — darker, with lobby entrance
    gf_y = y + h - ground_h
    pygame.draw.rect(surf, trim, pygame.Rect(x, gf_y, w - sh_w, ground_h))
    # Cornice between stories and ground floor
    pygame.draw.line(surf, (max(0, trim[0] - 25),
                            max(0, trim[1] - 25),
                            max(0, trim[2] - 25)),
                     (x, gf_y), (x + w - sh_w, gf_y), 2)
    # Lobby (large glass storefront)
    lobby_w = min(120, max(48, (w - sh_w) // 3))
    lobby_x = x + (w - sh_w - lobby_w) // 2
    pygame.draw.rect(surf, glass,
                     pygame.Rect(lobby_x, gf_y + 4, lobby_w, ground_h - 8))
    pygame.draw.rect(surf, trim,
                     pygame.Rect(lobby_x, gf_y + 4, lobby_w, ground_h - 8), 2)
    # Lobby reflection
    pygame.draw.polygon(surf, glass_hi, [
        (lobby_x + 4, gf_y + 6), (lobby_x + 16, gf_y + 6),
        (lobby_x + 4, gf_y + 18)
    ])
    # Lobby vertical seam
    pygame.draw.line(surf, trim,
                     (lobby_x + lobby_w // 2, gf_y + 4),
                     (lobby_x + lobby_w // 2, gf_y + ground_h - 4), 2)


def _draw_roof_crown(surf, x, y, w, h, kind, body, trim, glass, t_ms, fnt_s):
    """Type-specific rooftop crown features (sign, antenna, dome, etc.)
    drawn ON TOP of the skyscraper body. Pass in the building inner-area
    rect (x, y, w, h) — the same rect already filled by _draw_skyscraper_body.
    """
    sh_w = max(6, w // 14)
    crown_w = w - sh_w
    # The crown band lives in the top ~14px region; we render features just
    # above the cornice line to look like rooftop equipment.
    if kind == "apartment":
        # Residential rooftop: water tank + small chimney
        tank_x = x + crown_w // 4
        pygame.draw.rect(surf, (108, 92, 78),
                         pygame.Rect(tank_x, y + 2, 24, 10))
        pygame.draw.rect(surf, trim, pygame.Rect(tank_x, y + 2, 24, 10), 1)
        pygame.draw.rect(surf, (78, 62, 48),
                         pygame.Rect(tank_x + 4, y, 16, 4))
        # Chimney with animated smoke
        chx = x + 3 * crown_w // 4
        pygame.draw.rect(surf, (62, 52, 48),
                         pygame.Rect(chx, y + 2, 8, 10))
        for i in range(3):
            sy_smoke = y - 2 - i * 4 - (t_ms // 250) % 4
            puff = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(puff, (200, 200, 200, max(60, 200 - i * 50)),
                               (4, 4), 3 + i)
            surf.blit(puff, (chx, sy_smoke))

    elif kind == "cafe":
        # Coffee shop awning + neon sign
        # Striped awning band just above ground floor (visual cue)
        # (Awning placed on roof crown for visibility)
        for i in range(crown_w // 6):
            stripe_x = x + i * 6
            col = (188, 95, 65) if i % 2 == 0 else (235, 220, 180)
            pygame.draw.rect(surf, col,
                             pygame.Rect(stripe_x, y + 2, 6, 8))
        # Neon coffee sign
        lbl = fnt_s.render("CAFE", True, (255, 220, 80))
        glow_s = pygame.Surface((lbl.get_width() + 12, lbl.get_height() + 8),
                                pygame.SRCALPHA)
        glow_s.fill((40, 30, 0, 0))
        pygame.draw.rect(glow_s, (40, 25, 8, 220),
                         pygame.Rect(0, 0, lbl.get_width() + 12,
                                     lbl.get_height() + 8))
        pygame.draw.rect(glow_s, (255, 220, 80, 255),
                         pygame.Rect(0, 0, lbl.get_width() + 12,
                                     lbl.get_height() + 8), 1)
        glow_s.blit(lbl, (6, 4))
        sx_s = x + (crown_w - glow_s.get_width()) // 2
        sy_s = y + h // 2 - 8
        surf.blit(glow_s, (sx_s, sy_s))

    elif kind == "supermarket":
        # Large green & white storefront sign across the building
        # "WHOLE FOODS" sign on facade middle band
        sign_w = min(crown_w - 16, 240)
        sign_h = 32
        sx_s = x + (crown_w - sign_w) // 2
        sy_s = y + h // 2 - sign_h // 2
        pygame.draw.rect(surf, (52, 122, 62),
                         pygame.Rect(sx_s, sy_s, sign_w, sign_h))
        pygame.draw.rect(surf, (255, 255, 255),
                         pygame.Rect(sx_s, sy_s, sign_w, sign_h), 2)
        lbl = fnt_s.render("WHOLE FOODS", True, (255, 255, 255))
        if lbl.get_width() <= sign_w - 8:
            surf.blit(lbl,
                      (sx_s + (sign_w - lbl.get_width()) // 2,
                       sy_s + (sign_h - lbl.get_height()) // 2))

    elif kind == "gym":
        # HVAC units + rooftop GYM sign
        for ux in range(x + 12, x + crown_w - 28, 50):
            pygame.draw.rect(surf, trim, pygame.Rect(ux, y + 2, 22, 10))
            pygame.draw.rect(surf, (32, 38, 50),
                             pygame.Rect(ux + 2, y + 4, 18, 6))
        # Big yellow GYM sign mid-building
        lbl = fnt_s.render("GYM", True, (255, 215, 65))
        big = pygame.transform.scale(lbl,
                                     (lbl.get_width() * 2, lbl.get_height() * 2))
        sign_x = x + (crown_w - big.get_width()) // 2
        sign_y = y + h // 2 - big.get_height() // 2
        # Sign plate
        pygame.draw.rect(surf, (35, 38, 50),
                         pygame.Rect(sign_x - 8, sign_y - 4,
                                     big.get_width() + 16, big.get_height() + 8))
        pygame.draw.rect(surf, (255, 215, 65),
                         pygame.Rect(sign_x - 8, sign_y - 4,
                                     big.get_width() + 16, big.get_height() + 8), 2)
        surf.blit(big, (sign_x, sign_y))

    elif kind == "bank":
        # Classical NYSE-style: pediment + gold $
        # Pediment triangle on top
        ped_w = min(crown_w * 2 // 3, 220)
        ped_x = x + (crown_w - ped_w) // 2
        pygame.draw.polygon(surf, (245, 230, 195), [
            (ped_x, y + 14), (ped_x + ped_w, y + 14),
            (ped_x + ped_w // 2, y - 12)
        ])
        pygame.draw.polygon(surf, trim, [
            (ped_x, y + 14), (ped_x + ped_w, y + 14),
            (ped_x + ped_w // 2, y - 12)
        ], 2)
        # American flag on top of pediment
        fl_x = ped_x + ped_w // 2
        pygame.draw.line(surf, (62, 52, 38),
                         (fl_x, y - 12), (fl_x, y - 28), 2)
        # Wave the flag with sine
        wave = int(math.sin(t_ms / 400.0) * 3)
        pygame.draw.polygon(surf, (188, 28, 38), [
            (fl_x, y - 26), (fl_x + 12 + wave, y - 24),
            (fl_x + 12 + wave, y - 18), (fl_x, y - 18)
        ])
        pygame.draw.polygon(surf, (28, 38, 110), [
            (fl_x, y - 26), (fl_x + 5, y - 26),
            (fl_x + 5, y - 22), (fl_x, y - 22)
        ])
        # Big gold $ mid-facade
        dollar = fnt_s.render("$", True, (255, 215, 65))
        big = pygame.transform.scale(dollar, (dollar.get_width() * 3,
                                              dollar.get_height() * 3))
        d_x = x + (crown_w - big.get_width()) // 2
        d_y = y + h // 2 - big.get_height() // 2
        surf.blit(big, (d_x, d_y))

    elif kind == "fed":
        # FED building: pediment + columns + eagle insignia
        # Pediment
        ped_w = min(crown_w * 3 // 4, 260)
        ped_x = x + (crown_w - ped_w) // 2
        pygame.draw.polygon(surf, (245, 240, 220), [
            (ped_x, y + 14), (ped_x + ped_w, y + 14),
            (ped_x + ped_w // 2, y - 14)
        ])
        pygame.draw.polygon(surf, trim, [
            (ped_x, y + 14), (ped_x + ped_w, y + 14),
            (ped_x + ped_w // 2, y - 14)
        ], 2)
        # Gold eagle disc on pediment
        eg_x = ped_x + ped_w // 2
        pygame.draw.circle(surf, (215, 175, 85), (eg_x, y + 2), 9)
        pygame.draw.circle(surf, trim, (eg_x, y + 2), 9, 2)
        # FED label mid-facade
        lbl = fnt_s.render("FED", True, (255, 255, 255))
        big = pygame.transform.scale(lbl,
                                     (lbl.get_width() * 2, lbl.get_height() * 2))
        f_x = x + (crown_w - big.get_width()) // 2
        f_y = y + h // 2 - big.get_height() // 2
        # Plate behind label
        pygame.draw.rect(surf, trim,
                         pygame.Rect(f_x - 10, f_y - 4,
                                     big.get_width() + 20, big.get_height() + 8))
        surf.blit(big, (f_x, f_y))

    elif kind == "press":
        # Media tower: large rooftop antenna + satellite dish + neon PRESS sign
        ax = x + crown_w // 2
        # Antenna mast (rising above the building)
        pygame.draw.line(surf, (185, 185, 195), (ax, y + 4), (ax, y - 32), 4)
        pygame.draw.line(surf, (235, 235, 245), (ax, y + 4), (ax, y - 32), 1)
        # Cross arms
        pygame.draw.line(surf, (185, 185, 195),
                         (ax - 10, y - 8), (ax + 10, y - 8), 2)
        pygame.draw.line(surf, (185, 185, 195),
                         (ax - 6, y - 18), (ax + 6, y - 18), 2)
        # Blinking warning light
        if (t_ms // 500) % 2:
            pygame.draw.circle(surf, (255, 60, 60), (ax, y - 32), 4)
            glow = pygame.Surface((14, 14), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 60, 60, 140), (7, 7), 7)
            surf.blit(glow, (ax - 7, y - 39))
        # Satellite dish on roof
        sat_x = x + 20
        pygame.draw.circle(surf, (215, 215, 220), (sat_x, y + 6), 10, 2)
        pygame.draw.line(surf, (185, 185, 195),
                         (sat_x, y + 6), (sat_x + 8, y - 2), 2)
        # Neon PRESS sign
        lbl = fnt_s.render("PRESS", True, (255, 60, 60))
        big = pygame.transform.scale(lbl,
                                     (lbl.get_width() * 2, lbl.get_height() * 2))
        p_x = x + (crown_w - big.get_width()) // 2
        p_y = y + h // 2 - big.get_height() // 2
        pygame.draw.rect(surf, (20, 25, 38),
                         pygame.Rect(p_x - 8, p_y - 4,
                                     big.get_width() + 16, big.get_height() + 8))
        pygame.draw.rect(surf, (255, 60, 60),
                         pygame.Rect(p_x - 8, p_y - 4,
                                     big.get_width() + 16, big.get_height() + 8), 2)
        surf.blit(big, (p_x, p_y))

    elif kind == "wallst":
        # Wall Street tower: classical pediment + American flag + NYSE scrolling ticker
        ped_w = min(crown_w * 3 // 5, 180)
        ped_x = x + (crown_w - ped_w) // 2
        pygame.draw.polygon(surf, (215, 215, 225), [
            (ped_x, y + 14), (ped_x + ped_w, y + 14),
            (ped_x + ped_w // 2, y - 12)
        ])
        pygame.draw.polygon(surf, trim, [
            (ped_x, y + 14), (ped_x + ped_w, y + 14),
            (ped_x + ped_w // 2, y - 12)
        ], 2)
        # Flag pole with US flag
        fl_x = ped_x + ped_w // 2
        pygame.draw.line(surf, (62, 62, 75),
                         (fl_x, y - 12), (fl_x, y - 34), 2)
        wave = int(math.sin(t_ms / 400.0) * 3)
        pygame.draw.polygon(surf, (188, 28, 38), [
            (fl_x, y - 32), (fl_x + 14 + wave, y - 30),
            (fl_x + 14 + wave, y - 22), (fl_x, y - 22)
        ])
        pygame.draw.polygon(surf, (28, 38, 110), [
            (fl_x, y - 32), (fl_x + 6, y - 32),
            (fl_x + 6, y - 26), (fl_x, y - 26)
        ])
        # Animated NYSE ticker tape across middle band
        tk_y = y + h // 2 - 12
        pygame.draw.rect(surf, (15, 18, 28),
                         pygame.Rect(x + 4, tk_y, crown_w - 8, 24))
        pygame.draw.rect(surf, (235, 195, 65),
                         pygame.Rect(x + 4, tk_y, crown_w - 8, 24), 1)
        scroll = (t_ms // 30) % 80
        clip_rect = pygame.Rect(x + 5, tk_y + 1, crown_w - 10, 22)
        old_clip = surf.get_clip()
        surf.set_clip(clip_rect)
        col_pos = -scroll
        symbols = [("AAPL", True), ("GS", False), ("JPM", True),
                   ("MS", True), ("XOM", False), ("TSLA", True)]
        i = 0
        while x + 8 + col_pos < x + crown_w - 4:
            sym, up = symbols[i % len(symbols)]
            arrow_col = (60, 200, 100) if up else (220, 60, 60)
            txt = fnt_s.render(
                f"{sym} {'▲' if up else '▼'}{0.5 + (i*0.7) % 4:.2f}",
                True, arrow_col)
            surf.blit(txt, (x + 8 + col_pos, tk_y + 4))
            col_pos += 80
            i += 1
        surf.set_clip(old_clip)
        # Big NYSE label below
        lbl = fnt_s.render("NYSE", True, (235, 195, 65))
        big = pygame.transform.scale(lbl,
                                     (lbl.get_width() * 2, lbl.get_height() * 2))
        n_x = x + (crown_w - big.get_width()) // 2
        n_y = tk_y + 30
        if n_y + big.get_height() < y + h - 24:
            surf.blit(big, (n_x, n_y))

    elif kind == "hospital":
        # Medical center: big red cross above + helipad H on roof
        # Red cross sign on roof crown
        cx_c = x + crown_w // 2
        cs = 18
        pygame.draw.rect(surf, (215, 55, 55),
                         pygame.Rect(cx_c - cs // 3, y - 4, 2 * cs // 3, cs))
        pygame.draw.rect(surf, (215, 55, 55),
                         pygame.Rect(cx_c - cs // 2, y + cs // 3 - 4, cs, 2 * cs // 3))
        # Big red cross mid-facade
        cy_m = y + h // 2
        bs = min(50, crown_w // 4)
        pygame.draw.rect(surf, (220, 60, 60),
                         pygame.Rect(cx_c - bs // 4, cy_m - bs // 2, bs // 2, bs))
        pygame.draw.rect(surf, (220, 60, 60),
                         pygame.Rect(cx_c - bs // 2, cy_m - bs // 4, bs, bs // 2))
        pygame.draw.rect(surf, (255, 255, 255),
                         pygame.Rect(cx_c - bs // 4, cy_m - bs // 2, bs // 2, bs), 2)
        pygame.draw.rect(surf, (255, 255, 255),
                         pygame.Rect(cx_c - bs // 2, cy_m - bs // 4, bs, bs // 2), 2)
        # Helipad H on rooftop right side
        if crown_w > 200:
            hpx = x + crown_w - 30
            hpy = y + 4
            pygame.draw.circle(surf, (255, 195, 0), (hpx, hpy + 8), 16, 3)
            lbl = fnt_s.render("H", True, (255, 195, 0))
            big = pygame.transform.scale(lbl,
                                         (lbl.get_width() * 2, lbl.get_height() * 2))
            surf.blit(big, (hpx - big.get_width() // 2,
                            hpy + 8 - big.get_height() // 2))

    elif kind == "capitol":
        # Capitol: large central dome rising above the roof
        cx_d = x + crown_w // 2
        cy_d = y + h // 2 - 10
        dome_r = min(36, min(crown_w, h) // 4)
        # Dome drum (rectangular base under the dome)
        pygame.draw.rect(surf, (215, 210, 195),
                         pygame.Rect(cx_d - dome_r, cy_d - 4, dome_r * 2, 14))
        pygame.draw.rect(surf, trim,
                         pygame.Rect(cx_d - dome_r, cy_d - 4, dome_r * 2, 14), 2)
        # Dome (hemisphere)
        dome_rect = pygame.Rect(cx_d - dome_r, cy_d - dome_r,
                                dome_r * 2, dome_r * 2)
        pygame.draw.ellipse(surf, (245, 240, 220), dome_rect)
        pygame.draw.ellipse(surf, trim, dome_rect, 2)
        # Dome highlight (left side, sun-lit)
        pygame.draw.arc(surf, (255, 250, 230),
                        pygame.Rect(cx_d - dome_r + 4, cy_d - dome_r + 2,
                                    dome_r * 2 - 8, dome_r * 2 - 4),
                        2.0, 3.6, 2)
        # Dome ridges (vertical)
        for ridge_x in (cx_d - dome_r // 2, cx_d, cx_d + dome_r // 2):
            pygame.draw.arc(surf, trim,
                            pygame.Rect(ridge_x - 4, cy_d - dome_r,
                                        8, dome_r * 2),
                            0.5, 2.7, 1)
        # Spire on top with star
        pygame.draw.rect(surf, trim,
                         pygame.Rect(cx_d - 2, cy_d - dome_r - 14, 4, 14))
        pygame.draw.circle(surf, (255, 215, 100),
                           (cx_d, cy_d - dome_r - 18), 5)

    elif kind == "university":
        # University: brick body + central clock tower with spire
        # Clock tower rises above the building crown
        tw = min(56, crown_w // 5)
        th = 60
        tx = x + (crown_w - tw) // 2
        ty = y - th + 14
        # Tower body
        pygame.draw.rect(surf, (185, 105, 78), pygame.Rect(tx, ty, tw, th))
        pygame.draw.rect(surf, trim, pygame.Rect(tx, ty, tw, th), 2)
        # Brick course lines
        for ply in range(ty + 6, ty + th - 6, 6):
            pygame.draw.line(surf, (148, 78, 58),
                             (tx + 2, ply), (tx + tw - 2, ply), 1)
        # Pointed spire
        pygame.draw.polygon(surf, trim, [
            (tx - 4, ty), (tx + tw + 4, ty), (tx + tw // 2, ty - 22)
        ])
        pygame.draw.polygon(surf, (95, 50, 38), [
            (tx - 4, ty), (tx + tw + 4, ty), (tx + tw // 2, ty - 22)
        ], 2)
        # Clock face
        clk_x = tx + tw // 2
        clk_y = ty + 14
        clk_r = tw // 3
        pygame.draw.circle(surf, (255, 255, 255), (clk_x, clk_y), clk_r)
        pygame.draw.circle(surf, (0, 0, 0), (clk_x, clk_y), clk_r, 1)
        ang_h = (t_ms / 30000.0) % (2 * math.pi) - math.pi / 2
        ang_m = (t_ms / 2500.0) % (2 * math.pi) - math.pi / 2
        pygame.draw.line(surf, (0, 0, 0), (clk_x, clk_y),
                         (int(clk_x + (clk_r - 4) * math.cos(ang_h)),
                          int(clk_y + (clk_r - 4) * math.sin(ang_h))), 2)
        pygame.draw.line(surf, (0, 0, 0), (clk_x, clk_y),
                         (int(clk_x + (clk_r - 1) * math.cos(ang_m)),
                          int(clk_y + (clk_r - 1) * math.sin(ang_m))), 1)


def _draw_roof_pattern(surf, x, y, w, h, kind, roof, trim, t_ms, fnt_s):
    """[Legacy] No longer used — kept for backward compatibility."""
    if kind == "apartment":
        # Cozy red pitched roof with chimney + smoke
        _draw_pitched_roof_base(surf, x, y, w, h, roof, trim)
        # Central ridge (the roof peak)
        pygame.draw.rect(surf, trim, pygame.Rect(
            x + 6, y + h // 2 - 2, w - 12, 4))
        pygame.draw.line(surf, (min(255, trim[0]+30), min(255, trim[1]+30), min(255, trim[2]+30)),
                         (x + 6, y + h // 2 - 2), (x + w - 6, y + h // 2 - 2), 1)
        # Brick chimney (positioned toward upper-right)
        chx = x + w * 3 // 4
        if chx + 16 < x + w - 4:
            pygame.draw.rect(surf, (132, 78, 52),
                             pygame.Rect(chx, y + 4, 14, 22))
            pygame.draw.rect(surf, (95, 55, 35),
                             pygame.Rect(chx, y + 4, 14, 22), 1)
            pygame.draw.rect(surf, (62, 42, 30),
                             pygame.Rect(chx - 2, y + 4, 18, 5))
            # Animated smoke puffs
            for i in range(4):
                sy_smoke = y - 2 - i * 6 - (t_ms // 250) % 6
                if sy_smoke > y - 24:
                    radius = 3 + i
                    smoke_a = max(60, 200 - i * 40)
                    smoke_s = pygame.Surface(
                        (radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
                    pygame.draw.circle(smoke_s, (220, 220, 220, smoke_a),
                                       (radius + 1, radius + 1), radius)
                    surf.blit(smoke_s, (chx + 7 - radius, sy_smoke - radius))

    elif kind == "cafe":
        # Warm wood-style roof + chimney + coffee sign hanging from eaves
        _draw_pitched_roof_base(surf, x, y, w, h, roof, trim)
        # Ridge with a slight golden trim
        pygame.draw.rect(surf, trim, pygame.Rect(
            x + 6, y + h // 2 - 2, w - 12, 4))
        pygame.draw.line(surf, (228, 178, 95),
                         (x + 6, y + h // 2 - 2), (x + w - 6, y + h // 2 - 2), 1)
        # Coffee cup roof sign at center
        ccx, ccy = x + w // 2, y + h // 2
        pygame.draw.circle(surf, (245, 235, 210), (ccx, ccy), 18)
        pygame.draw.circle(surf, trim, (ccx, ccy), 18, 2)
        pygame.draw.ellipse(surf, (95, 58, 32),
                            pygame.Rect(ccx - 12, ccy - 8, 24, 16))
        pygame.draw.ellipse(surf, (135, 82, 45),
                            pygame.Rect(ccx - 12, ccy - 8, 24, 16), 1)
        pygame.draw.arc(surf, trim,
                        pygame.Rect(ccx + 10, ccy - 6, 10, 14), -1.4, 1.4, 3)
        # Steam wisps
        steam_off = (t_ms // 250) % 8
        for i in range(3):
            sx_st = ccx - 8 + i * 8
            s_alpha = max(40, 180 - i * 40)
            puff = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(puff, (255, 255, 255, s_alpha), (3, 3), 3)
            surf.blit(puff, (sx_st - 3, ccy - 22 + steam_off - i * 3))

    elif kind == "supermarket":
        # Light blue pitched roof + skylights + sign
        _draw_pitched_roof_base(surf, x, y, w, h, roof, trim)
        # Skylights on roof
        for sx_l in range(x + 32, x + w - 64, 60):
            pygame.draw.rect(surf, (185, 215, 232),
                             pygame.Rect(sx_l, y + 12, 32, 16))
            pygame.draw.rect(surf, trim, pygame.Rect(sx_l, y + 12, 32, 16), 1)
            pygame.draw.line(surf, (220, 235, 245),
                             (sx_l + 2, y + 14), (sx_l + 10, y + 22), 1)
        # Central sign (Whole Foods)
        sign_w = min(w - 32, 200)
        sign_h = min(h - 28, 42)
        sx_s = x + (w - sign_w) // 2
        sy_s = y + h - sign_h - 10
        pygame.draw.rect(surf, (78, 138, 78), pygame.Rect(
            sx_s, sy_s, sign_w, sign_h))
        pygame.draw.rect(surf, (255, 255, 255), pygame.Rect(
            sx_s, sy_s, sign_w, sign_h), 2)
        lbl = fnt_s.render("WHOLE FOODS", True, (255, 255, 255))
        if lbl.get_width() <= sign_w - 8:
            surf.blit(lbl, (sx_s + (sign_w - lbl.get_width()) // 2,
                            sy_s + (sign_h - lbl.get_height()) // 2))

    elif kind == "gym":
        # Slate-gray pitched roof + skylight + GYM sign on the front
        _draw_pitched_roof_base(surf, x, y, w, h, roof, trim)
        # Central skylight panels
        for sx_l in range(x + 24, x + w - 48, 60):
            pygame.draw.rect(surf, (185, 200, 215),
                             pygame.Rect(sx_l, y + 14, 36, 18))
            pygame.draw.rect(surf, trim, pygame.Rect(sx_l, y + 14, 36, 18), 1)
            pygame.draw.line(surf, (220, 235, 245),
                             (sx_l + 4, y + 16), (sx_l + 12, y + 24), 1)
        # Bottom GYM sign
        lbl = fnt_s.render("GYM", True, (255, 215, 65))
        big = pygame.transform.scale(
            lbl, (lbl.get_width() * 2, lbl.get_height() * 2))
        if big.get_width() <= w - 16:
            sign_x = x + (w - big.get_width()) // 2
            sign_y = y + h - big.get_height() - 10
            # Sign plate background
            pygame.draw.rect(surf, trim,
                             pygame.Rect(sign_x - 6, sign_y - 4,
                                         big.get_width() + 12, big.get_height() + 8))
            surf.blit(big, (sign_x, sign_y))

    elif kind == "bank":
        # Classical: 4 columns + center pediment with $
        col_count = max(3, (w - 24) // 40)
        spacing = (w - 24) // (col_count + 1)
        for i in range(col_count):
            col_x = x + 12 + spacing * (i + 1) - 7
            pygame.draw.rect(surf, (240, 225, 195),
                             pygame.Rect(col_x, y + 10, 14, h - 20))
            pygame.draw.rect(surf, trim, pygame.Rect(
                col_x, y + 10, 14, h - 20), 1)
            pygame.draw.rect(surf, trim, pygame.Rect(col_x - 2, y + 8, 18, 4))
            pygame.draw.rect(surf, trim, pygame.Rect(
                col_x - 2, y + h - 12, 18, 4))
        pygame.draw.polygon(surf, trim, [
            (x + w // 2 - 40, y + 8), (x + w // 2 + 40, y + 8),
            (x + w // 2, y - 6)
        ])
        # $ symbol in center
        dollar = fnt_s.render("$", True, (255, 215, 65))
        big = pygame.transform.scale(
            dollar, (dollar.get_width() * 3, dollar.get_height() * 3))
        surf.blit(big, (x + (w - big.get_width()) // 2,
                        y + (h - big.get_height()) // 2))

    elif kind == "fed":
        # Greek columns + FED label + eagle insignia (circle)
        col_count = max(4, (w - 24) // 36)
        spacing = (w - 24) // (col_count + 1)
        for i in range(col_count):
            col_x = x + 12 + spacing * (i + 1) - 6
            pygame.draw.rect(surf, (245, 235, 210),
                             pygame.Rect(col_x, y + 14, 12, h - 28))
            pygame.draw.rect(surf, trim, pygame.Rect(
                col_x, y + 14, 12, h - 28), 1)
        pygame.draw.rect(surf, trim, pygame.Rect(x + 4, y + 4, w - 8, 8))
        pygame.draw.rect(surf, trim, pygame.Rect(x + 4, y + h - 12, w - 8, 8))
        # Eagle insignia (golden circle)
        cx_e, cy_e = x + w // 2, y + h // 2
        pygame.draw.circle(surf, (215, 175, 85), (cx_e, cy_e), 18)
        pygame.draw.circle(surf, trim, (cx_e, cy_e), 18, 2)
        lbl = fnt_s.render("FED", True, (255, 255, 255))
        surf.blit(lbl, (cx_e - lbl.get_width() //
                  2, cy_e - lbl.get_height() // 2))

    elif kind == "press":
        # Blue tile pitched roof + antenna + satellite + PRESS sign
        _draw_pitched_roof_base(surf, x, y, w, h, roof, trim)
        # Antenna mast (center)
        ax = x + w // 2
        pygame.draw.line(surf, (75, 75, 80), (ax, y + 4), (ax, y + h // 2), 3)
        pygame.draw.line(surf, (75, 75, 80), (ax - 8, y + 14),
                         (ax + 8, y + 14), 2)
        pygame.draw.line(surf, (75, 75, 80),
                         (ax - 10, y + 22), (ax + 10, y + 22), 2)
        # Blinking aircraft warning light
        if (t_ms // 500) % 2:
            pygame.draw.circle(surf, (255, 60, 60), (ax, y + 4), 4)
            glow = pygame.Surface((14, 14), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 80, 80, 120), (7, 7), 7)
            surf.blit(glow, (ax - 7, y - 3))
        # Satellite dish
        sat_x, sat_y = x + 24, y + h // 2 + 10
        pygame.draw.circle(surf, (235, 235, 235), (sat_x, sat_y), 10)
        pygame.draw.circle(surf, (75, 75, 80), (sat_x, sat_y), 10, 2)
        pygame.draw.line(surf, (75, 75, 80), (sat_x, sat_y),
                         (sat_x + 7, sat_y - 7), 2)
        # PRESS sign on roof
        lbl = fnt_s.render("PRESS", True, (255, 240, 110))
        sign_w = lbl.get_width() + 12
        sign_h = lbl.get_height() + 4
        sx_s = x + w - sign_w - 10
        sy_s = y + h - sign_h - 10
        pygame.draw.rect(surf, trim, pygame.Rect(sx_s, sy_s, sign_w, sign_h))
        pygame.draw.rect(surf, (255, 240, 110), pygame.Rect(
            sx_s, sy_s, sign_w, sign_h), 1)
        surf.blit(lbl, (sx_s + 6, sy_s + 2))

    elif kind == "wallst":
        # Dark glass + animated ticker
        pygame.draw.rect(surf, trim, pygame.Rect(x + 6, y + 6, w - 12, h - 12))
        # Vertical glass lines
        for gx in range(x + 12, x + w - 12, 14):
            pygame.draw.line(surf, (62, 70, 92), (gx, y + 10),
                             (gx, y + h - 36), 1)
        # Ticker
        tk_y = y + h - 30
        pygame.draw.rect(surf, (12, 15, 22),
                         pygame.Rect(x + 8, tk_y, w - 16, 22))
        scroll = (t_ms // 30) % 60
        col_pos = -scroll
        while x + 12 + col_pos < x + w - 16:
            green = (col_pos // 60) % 2 == 0
            if x + 12 + col_pos > x + 8 and x + 12 + col_pos + 50 < x + w - 8:
                arrow_col = (60, 200, 100) if green else (200, 60, 60)
                arrow = "▲ " if green else "▼ "
                txt = fnt_s.render(
                    arrow + ("2.3" if green else "1.4"), True, arrow_col)
                # Clip blit so it doesn't overflow
                clip_rect = pygame.Rect(x + 8, tk_y, w - 16, 22)
                old_clip = surf.get_clip()
                surf.set_clip(clip_rect)
                surf.blit(txt, (x + 12 + col_pos, tk_y + 3))
                surf.set_clip(old_clip)
            col_pos += 60
        lbl = fnt_s.render("NYSE", True, (235, 195, 65))
        big = pygame.transform.scale(
            lbl, (lbl.get_width() * 2, lbl.get_height() * 2))
        if big.get_width() <= w - 16:
            surf.blit(big, (x + (w - big.get_width()) // 2, y + 12))

    elif kind == "hospital":
        # Marble texture + big red cross + helipad
        for ly in range(y + 8, y + h - 8, 12):
            pygame.draw.line(surf, (210, 210, 215),
                             (x + 4, ly), (x + w - 4, ly), 1)
        cx_c, cy_c = x + w // 2, y + h // 2
        cs = min(72, min(w, h) - 24)
        pygame.draw.rect(surf, (225, 55, 55),
                         pygame.Rect(cx_c - cs // 6, cy_c - cs // 2, cs // 3, cs))
        pygame.draw.rect(surf, (225, 55, 55),
                         pygame.Rect(cx_c - cs // 2, cy_c - cs // 6, cs, cs // 3))
        pygame.draw.rect(surf, (255, 255, 255),
                         pygame.Rect(cx_c - cs // 6, cy_c - cs // 2, cs // 3, cs), 2)
        pygame.draw.rect(surf, (255, 255, 255),
                         pygame.Rect(cx_c - cs // 2, cy_c - cs // 6, cs, cs // 3), 2)
        # Helipad H
        if w > 220:
            hpx, hpy = x + 28, y + 28
            pygame.draw.circle(surf, (255, 215, 0), (hpx, hpy), 18, 3)
            lbl = fnt_s.render("H", True, (255, 215, 0))
            big = pygame.transform.scale(
                lbl, (lbl.get_width() * 2, lbl.get_height() * 2))
            surf.blit(big, (hpx - big.get_width() //
                      2, hpy - big.get_height() // 2))

    elif kind == "capitol":
        # Marble veining + central dome with spire + columns
        for ly in range(y + 6, y + h - 6, 14):
            pygame.draw.line(surf, (210, 200, 175),
                             (x + 4, ly), (x + w - 4, ly), 1)
        cx_d, cy_d = x + w // 2, y + h // 2 + 12
        dome_r = min(40, min(w, h) // 4)
        # Dome base
        pygame.draw.rect(surf, trim, pygame.Rect(
            cx_d - dome_r - 6, cy_d, dome_r * 2 + 12, 8))
        # Dome
        pygame.draw.circle(surf, (250, 245, 225), (cx_d, cy_d), dome_r)
        pygame.draw.circle(surf, trim, (cx_d, cy_d), dome_r, 2)
        # Inner ridges
        pygame.draw.arc(surf, trim, pygame.Rect(cx_d - dome_r + 6, cy_d - dome_r + 6,
                                                (dome_r - 6) * 2, (dome_r - 6) * 2),
                        3.14, 6.28, 1)
        # Spire on top
        pygame.draw.rect(surf, trim, pygame.Rect(
            cx_d - 2, cy_d - dome_r - 14, 4, 14))
        pygame.draw.circle(surf, (255, 215, 100),
                           (cx_d, cy_d - dome_r - 16), 4)
        # Side wings (columns)
        for cx_col in [x + 18, x + w - 30]:
            pygame.draw.rect(surf, (250, 245, 225),
                             pygame.Rect(cx_col, y + 14, 12, h - 28))
            pygame.draw.rect(surf, trim, pygame.Rect(
                cx_col, y + 14, 12, h - 28), 1)

    elif kind == "university":
        # Brick pitched roof + central clock tower
        _draw_pitched_roof_base(surf, x, y, w, h, roof, trim)
        # Clock tower (centered)
        tw = min(64, w // 4)
        th = h - 12
        tx = x + (w - tw) // 2
        ty = y + 8
        # Tower body
        pygame.draw.rect(surf, (245, 230, 200), pygame.Rect(tx, ty, tw, th))
        pygame.draw.rect(surf, trim, pygame.Rect(tx, ty, tw, th), 2)
        # Brick texture on tower
        for ply in range(ty + 6, ty + th - 6, 6):
            pygame.draw.line(surf, (215, 195, 165),
                             (tx + 2, ply), (tx + tw - 2, ply), 1)
        # Pointed roof top
        pygame.draw.polygon(surf, trim, [
            (tx - 6, ty), (tx + tw + 6, ty), (tx + tw // 2, ty - 22)
        ])
        pygame.draw.polygon(surf, (95, 50, 40), [
            (tx - 6, ty), (tx + tw + 6, ty), (tx + tw // 2, ty - 22)
        ], 2)
        # Tiny flag on top
        pygame.draw.line(surf, (95, 50, 40),
                         (tx + tw // 2, ty - 22), (tx + tw // 2, ty - 30), 1)
        pygame.draw.polygon(surf, (220, 70, 70), [
            (tx + tw // 2, ty - 30), (tx + tw // 2 + 8, ty - 27),
            (tx + tw // 2, ty - 24)
        ])
        # Clock face (animated)
        clk_x = tx + tw // 2
        clk_y = ty + th // 3
        clk_r = min(tw // 3, 14)
        pygame.draw.circle(surf, (255, 255, 255), (clk_x, clk_y), clk_r)
        pygame.draw.circle(surf, (0, 0, 0), (clk_x, clk_y), clk_r, 1)
        ang_h = (t_ms / 30000.0) % (2 * math.pi) - math.pi / 2
        ang_m = (t_ms / 2500.0) % (2 * math.pi) - math.pi / 2
        pygame.draw.line(surf, (0, 0, 0), (clk_x, clk_y),
                         (int(clk_x + (clk_r - 5) * math.cos(ang_h)),
                          int(clk_y + (clk_r - 5) * math.sin(ang_h))), 2)
        pygame.draw.line(surf, (0, 0, 0), (clk_x, clk_y),
                         (int(clk_x + (clk_r - 2) * math.cos(ang_m)),
                          int(clk_y + (clk_r - 2) * math.sin(ang_m))), 1)


def _draw_building_exteriors(surf, cx, cy, fnt_s):
    """Draw 2.5D skyscraper facades on city building footprints."""
    ts = config.TILE_SIZE
    t_ms = pygame.time.get_ticks()

    # Sort buildings top-to-bottom so the rooftop crowns from taller buildings
    # in the back are drawn before crowns from buildings in the front,
    # giving a proper layered 2.5D feel.
    sorted_buildings = sorted(CITY_BUILDINGS, key=lambda b: b[1])

    for (bx0, by0, bx1, by1, _dx, _dy, sname) in sorted_buildings:
        style = BUILDING_EXTERIORS.get(sname)
        if style is None:
            continue
        # Building inner area (skip the 1-tile wall ring)
        x = (bx0 + 1) * ts - int(cx)
        y = (by0 + 1) * ts - int(cy)
        w = (bx1 - bx0 - 1) * ts
        h = (by1 - by0 - 1) * ts
        if w <= 0 or h <= 0:
            continue
        # Wider culling because rooftop crowns extend ABOVE the footprint
        if x + w < 0 or x > config.SCREEN_W:
            continue
        if y + h < -60 or y > config.SCREEN_H:
            continue

        body = style["body"]
        trim = style["trim"]
        glass = style["glass"]

        # Drop shadow on the ground in front-right of the building (2.5D ground projection)
        drop = pygame.Surface((w + 16, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(drop, (0, 0, 0, 90), pygame.Rect(0, 0, w + 16, 12))
        surf.blit(drop, (x - 4, y + h - 4))

        # Skyscraper body (glass curtain wall + ground floor + side shadow)
        _draw_skyscraper_body(surf, x, y, w, h, body, trim, glass)
        # Type-specific rooftop crown (may draw above y)
        _draw_roof_crown(surf, x, y, w, h, style["kind"],
                         body, trim, glass, t_ms, fnt_s)


def draw_scene(surf, scene, cx, cy, economy, fnt_s, scenes=None):
    ts = config.TILE_SIZE
    x0 = max(0, int(cx // ts))
    y0 = max(0, int(cy // ts))
    x1 = min(scene.cols, x0 + config.SCREEN_W // ts + 2)
    y1 = min(scene.rows, y0 + config.SCREEN_H // ts + 2)

    for ty in range(y0, y1):
        for tx in range(x0, x1):
            tile = scene.tiles[ty][tx]
            base = TILE_COLOR.get(tile, (80, 80, 80))
            sx, sy = tx * ts - int(cx), ty * ts - int(cy)
            pygame.draw.rect(surf, base, pygame.Rect(sx, sy, ts, ts))
            _decorate(surf, sx, sy, ts, tile, tx, ty, fnt_s, economy)

    # Building exteriors: replace the plain floor inside each building footprint
    # with a distinctive roof / architecture for that building type.
    if scene.name == config.SCENE_CITY:
        _draw_building_exteriors(surf, cx, cy, fnt_s)

    if scene.name == config.SCENE_CITY:
        _draw_city_ambience(surf, scene, cx, cy)

    # Door sparkle hint on city map
    if scene.name == config.SCENE_CITY:
        t_ms = pygame.time.get_ticks()
        pulse = int(180 + 60 * math.sin(t_ms / 400.0))
        for door in scene.doors:
            dsx = door["x"] * ts - int(cx)
            dsy = door["y"] * ts - int(cy)
            if -ts < dsx < config.SCREEN_W + ts:
                pygame.draw.rect(surf, (pulse, pulse//2, 0),
                                 pygame.Rect(dsx, dsy, ts, ts), 2)

    # City signs — modern illuminated LED street signs
    if scene.name == config.SCENE_CITY:
        for (tx, ty), label in CITY_SIGNS.items():
            sx, sy = tx * ts - int(cx), ty * ts - int(cy) - 22
            if -200 < sx < config.SCREEN_W + 200:
                t = fnt_s.render(label, True, (255, 235, 145))
                sign_w = t.get_width() + 14
                sign_h = t.get_height() + 8
                # Dark metal backplate
                pygame.draw.rect(surf, (28, 32, 42),
                                 pygame.Rect(sx - 4, sy - 2, sign_w, sign_h))
                # Yellow LED border
                pygame.draw.rect(surf, (255, 200, 65),
                                 pygame.Rect(sx - 4, sy - 2, sign_w, sign_h), 2)
                # Inner glow line
                pygame.draw.line(surf, (90, 70, 25),
                                 (sx - 2, sy + sign_h - 3),
                                 (sx + sign_w - 6, sy + sign_h - 3), 1)
                # Steel mounting pole hanging down
                pygame.draw.rect(surf, (75, 78, 92),
                                 pygame.Rect(sx + sign_w // 2 - 6, sy + sign_h - 2, 3, 8))
                surf.blit(t, (sx + 3, sy + 2))

    # Show inflation-driven price tags in supermarket
    if scene.name == config.SCENE_SUPERMARKET:
        cpi = economy.cpi
        sold_out_axes = []
        if cpi > 7:
            sold_out_axes = [3, 11]   # 蛋跟油缺貨
        if cpi > 9:
            sold_out_axes = [3, 7, 11, 15]  # 全面缺貨
        for ax in [3, 7, 11, 15]:
            base_prices = {3: 5, 7: 4, 11: 8, 15: 12}
            price = int(base_prices[ax] * (1 + cpi / 5))
            sx, sy = ax * ts - int(cx), 2 * ts - int(cy) - 18
            if ax in sold_out_axes:
                # 缺貨標示（閃爍紅字）
                if (pygame.time.get_ticks() // 500) % 2 == 0:
                    out_t = fnt_s.render("缺貨！", True, config.RED)
                    bg = pygame.Surface(
                        (out_t.get_width()+8, out_t.get_height()+4), pygame.SRCALPHA)
                    bg.fill((80, 0, 0, 200))
                    surf.blit(bg, (sx, sy))
                    surf.blit(out_t, (sx+4, sy+2))
            else:
                col = config.RED if cpi > 6 else config.YELLOW if cpi > 3 else config.GREEN
                t = fnt_s.render(f"${price}", True, col)
                bg = pygame.Surface(
                    (t.get_width()+8, t.get_height()+4), pygame.SRCALPHA)
                bg.fill((0, 0, 0, 180))
                surf.blit(bg, (sx, sy))
                surf.blit(t, (sx+4, sy+2))

    # 城市蕭條視覺：失業高時部分建築燈光熄滅、貼封店告示
    if scene.name == config.SCENE_CITY and economy.unemployment > 8:
        severity = min(1.0, (economy.unemployment - 8) / 6.0)
        closed_buildings = [
            (1, 1, 10, 7),   # 公寓附近店家
            (38, 1, 48, 7),  # 健身房
        ]
        if severity > 0.5:
            closed_buildings.append((12, 1, 21, 7))  # 咖啡廳
        for x0, y0, x1, y1 in closed_buildings:
            bx_s = x0 * ts - int(cx)
            by_s = y0 * ts - int(cy)
            bw_s = (x1 - x0) * ts
            bh_s = (y1 - y0) * ts
            if -bw_s < bx_s < config.SCREEN_W:
                dark = pygame.Surface((bw_s, bh_s), pygame.SRCALPHA)
                dark.fill((0, 0, 0, int(severity * 100)))
                surf.blit(dark, (bx_s, by_s))
                # 封店標示
                label_t = fnt_s.render("CLOSED", True, (180, 60, 60))
                lx = bx_s + bw_s // 2 - label_t.get_width() // 2
                ly = by_s + bh_s // 2 - label_t.get_height() // 2
                pygame.draw.rect(surf, (40, 0, 0),
                                 pygame.Rect(lx - 4, ly - 2,
                                             label_t.get_width() + 8,
                                             label_t.get_height() + 4))
                surf.blit(label_t, (lx, ly))

    # Wall St ticker
    if scene.name == config.SCENE_WALL_ST:
        for x in [3, 6, 9, 12, 15]:
            for row_y in [2, 5]:
                sx, sy = x * ts - int(cx), row_y * ts - int(cy)
                green = economy.gdp > 0
                col = config.GREEN if green else config.RED
                arrow = "▲" if green else "▼"
                t = fnt_s.render(f"{arrow}{abs(economy.gdp):.1f}", True, col)
                surf.blit(t, (sx + 6, sy + 14))

    # Press room screen
    if scene.name == config.SCENE_PRESS:
        sx, sy = 6 * ts - int(cx), 1 * ts - int(cy)
        msg = f"FED: {economy.ffr:.2f}%"
        t = fnt_s.render(msg, True, config.TERMINAL_GREEN)
        surf.blit(t, (sx + 30, sy + 10))


def _draw_city_ambience(surf, scene, cx, cy):
    """Animated cars (yellow taxis + sedans) on the city streets."""
    ts = config.TILE_SIZE
    t_ms = pygame.time.get_ticks()
    road_w = scene.cols * ts
    road_h = scene.rows * ts

    # Horizontal road cars: (road_y_tile, color, speed px/ms, phase 0-1, direction +1/-1)
    h_cars = [
        (9,  (185, 52, 52),  0.050, 0.00,  1),
        (9,  (52, 52, 188),  0.038, 0.55, -1),
        (9,  (52, 178, 52),  0.060, 0.28,  1),
        (25, (225, 122, 40), 0.044, 0.12,  1),
        (25, (178, 52, 178), 0.048, 0.72, -1),
        (25, (178, 178, 52), 0.036, 0.62,  1),
        (37, (255, 160, 50), 0.040, 0.35,  1),
        (37, (100, 130, 255), 0.032, 0.80, -1),
    ]
    for (road_ty, color, speed, phase, direction) in h_cars:
        cw, ch = 38, 22
        travel = int((t_ms * speed + phase * road_w) * direction) % road_w
        if direction < 0:
            travel = road_w - (int((t_ms * speed + phase * road_w)) % road_w)
        tile_x = travel // ts
        if not (0 <= tile_x < scene.cols and scene.tiles[road_ty][tile_x] in (R, S, CR)):
            continue
        lane_off = (ts // 4) if direction > 0 else (ts // 2 + 4)
        car_x = travel - int(cx)
        car_y = road_ty * ts - int(cy) + lane_off - ch // 2
        if -cw < car_x < config.SCREEN_W + cw:
            pygame.draw.rect(surf, color, pygame.Rect(
                car_x, car_y, cw, ch), border_radius=4)
            wind_x = (car_x + cw - 14) if direction > 0 else (car_x + 2)
            pygame.draw.rect(surf, (155, 212, 242),
                             pygame.Rect(wind_x, car_y + 3, 12, 10), border_radius=2)
            pygame.draw.circle(surf, (28, 28, 28),
                               (car_x + 7, car_y + ch - 1), 4)
            pygame.draw.circle(surf, (28, 28, 28),
                               (car_x + cw - 7, car_y + ch - 1), 4)
            light_col = (255, 245, 180) if direction > 0 else (255, 60, 60)
            light_x = (car_x + cw - 3) if direction > 0 else (car_x + 1)
            pygame.draw.circle(surf, light_col, (light_x, car_y + 5), 2)
            pygame.draw.circle(surf, light_col, (light_x, car_y + ch - 5), 2)

    # Vertical road cars: (road_x_tile, color, speed, phase, direction)
    v_cars = [
        (24, (62, 182, 182), 0.042, 0.20,  1),
        (24, (202, 102, 62), 0.036, 0.78, -1),
        (50, (72, 192, 122), 0.038, 0.45,  1),
        (50, (182, 72,  62), 0.044, 0.85, -1),
    ]
    for (road_tx, color, speed, phase, direction) in v_cars:
        cw, ch = 22, 38
        travel = int((t_ms * speed + phase * road_h) * direction) % road_h
        if direction < 0:
            travel = road_h - (int((t_ms * speed + phase * road_h)) % road_h)
        tile_y = travel // ts
        if not (0 <= tile_y < scene.rows and scene.tiles[tile_y][road_tx] in (R, S, CR)):
            continue
        lane_off = (ts // 4) if direction > 0 else (ts // 2 + 4)
        car_x = road_tx * ts - int(cx) + lane_off - cw // 2
        car_y = travel - int(cy)
        if -ch < car_y < config.SCREEN_H + ch:
            pygame.draw.rect(surf, color, pygame.Rect(
                car_x, car_y, cw, ch), border_radius=4)
            wind_y = (car_y + ch - 14) if direction > 0 else (car_y + 2)
            pygame.draw.rect(surf, (155, 212, 242),
                             pygame.Rect(car_x + 3, wind_y, 14, 12), border_radius=2)
            pygame.draw.circle(surf, (28, 28, 28),
                               (car_x + cw // 2, car_y + 5), 4)
            pygame.draw.circle(surf, (28, 28, 28),
                               (car_x + cw // 2, car_y + ch - 5), 4)


def _decorate(surf, sx, sy, ts, tile, tx, ty, fnt_s, economy):
    h = (tx * 2654435761 + ty * 2246822519) & 0xFFFF
    t_ms = pygame.time.get_ticks()

    if tile == W:
        # Steel/concrete tower base — vertical mullions + floor lines
        for px in range(sx + ts // 4, sx + ts, ts // 4):
            pygame.draw.line(surf, (38, 45, 62), (px, sy), (px, sy + ts), 1)
        for py in range(sy + ts // 3, sy + ts, ts // 3):
            pygame.draw.line(surf, (38, 45, 62), (sx, py), (sx + ts, py), 1)
        # Top highlight (sun on north face)
        pygame.draw.line(surf, (108, 122, 145),
                         (sx, sy + 1), (sx + ts, sy + 1), 1)
    elif tile == G:
        # Manicured urban park grass — sparse darker dots
        for i in range(3):
            gx = sx + ((h + i * 41) % (ts - 4)) + 2
            gy = sy + ((h + i * 67) % (ts - 4)) + 2
            pygame.draw.circle(surf, (48, 105, 48), (gx, gy), 1)
        if h % 8 == 0:
            bx = sx + ((h * 13) % (ts - 6)) + 3
            by = sy + ((h * 17) % (ts - 6)) + 3
            pygame.draw.circle(surf, (95, 170, 78), (bx, by), 1)
    elif tile == R:
        # Dark asphalt with dashed yellow center line + texture
        # Horizontal road rows: yellow dashed center
        if ty in (8, 9, 10, 24, 25, 26, 36, 37, 38):
            dash_period = 28
            phase = (tx * ts) % (dash_period * 2)
            if phase < dash_period:
                pygame.draw.line(surf, (235, 195, 70),
                                 (sx + 4, sy + ts // 2), (sx + ts - 4, sy + ts // 2), 2)
        # Vertical road cols: yellow dashed center
        elif tx in (24, 50):
            dash_period = 28
            phase = (ty * ts) % (dash_period * 2)
            if phase < dash_period:
                pygame.draw.line(surf, (235, 195, 70),
                                 (sx + ts // 2, sy + 4), (sx + ts // 2, sy + ts - 4), 2)
        # Asphalt grain
        for i in range(3):
            ax = sx + ((h + i * 53) % (ts - 2)) + 1
            ay = sy + ((h + i * 71) % (ts - 2)) + 1
            pygame.draw.circle(surf, (28, 32, 42), (ax, ay), 1)
        # Subtle lighter speckles
        if h % 7 == 0:
            lx_s = sx + ((h * 13) % (ts - 4)) + 2
            ly_s = sy + ((h * 17) % (ts - 4)) + 2
            pygame.draw.circle(surf, (62, 65, 75), (lx_s, ly_s), 1)
    elif tile == S:
        # Concrete sidewalk with sectional panel grout
        mid = ts // 2
        pygame.draw.line(surf, (132, 132, 142),
                         (sx + mid, sy + 2), (sx + mid, sy + ts - 2), 1)
        pygame.draw.line(surf, (132, 132, 142),
                         (sx + 2, sy + mid), (sx + ts - 2, sy + mid), 1)
        # Subtle texture flecks
        for i in range(2):
            gx = sx + ((h + i * 41) % (ts - 4)) + 2
            gy = sy + ((h + i * 67) % (ts - 4)) + 2
            pygame.draw.circle(surf, (190, 190, 200), (gx, gy), 1)
    elif tile == WD:
        # Wood grain lines
        for i in range(3):
            gy = sy + (i * ts // 3 + (ty * 7 + tx * 3) % (ts // 3))
            pygame.draw.line(surf, (155, 112, 72), (sx, gy), (sx + ts, gy), 1)
        pygame.draw.line(surf, (162, 120, 78), (sx, sy +
                         ts - 1), (sx + ts, sy + ts - 1), 1)
    elif tile == TI:
        # Grout lines
        pygame.draw.line(surf, (178, 178, 185),
                         (sx, sy + ts//2), (sx + ts, sy + ts//2), 1)
        pygame.draw.line(surf, (178, 178, 185), (sx + ts //
                         2, sy), (sx + ts//2, sy + ts), 1)
    elif tile == MR:
        # Marble veining
        vx1 = sx + (h % (ts // 2))
        vy2 = sy + ((h >> 4) % ts)
        pygame.draw.line(surf, (205, 200, 192), (vx1, sy), (sx + ts, vy2), 1)
        vx2 = sx + ((h >> 8) % (ts // 2)) + ts // 2
        pygame.draw.line(surf, (210, 205, 198), (sx, sy +
                         (h >> 12) % ts), (vx2, sy + ts), 1)
    elif tile == DR:
        # Modern glass entrance with metal frame
        # Frame
        pygame.draw.rect(surf, (45, 52, 68),
                         pygame.Rect(sx + 3, sy + 2, ts - 6, ts - 4))
        # Glass panels (double doors)
        pygame.draw.rect(surf, (95, 170, 215),
                         pygame.Rect(sx + 5, sy + 4, (ts - 12) // 2, ts - 8))
        pygame.draw.rect(surf, (95, 170, 215),
                         pygame.Rect(sx + 7 + (ts - 12) // 2, sy + 4,
                                     (ts - 12) // 2, ts - 8))
        # Center seam
        pygame.draw.line(surf, (45, 52, 68),
                         (sx + ts // 2, sy + 4), (sx + ts // 2, sy + ts - 4), 1)
        # Glass reflection sheen
        pygame.draw.line(surf, (210, 235, 250),
                         (sx + 7, sy + 6), (sx + 13, sy + 12), 1)
        pygame.draw.line(surf, (210, 235, 250),
                         (sx + ts - 17, sy + 8), (sx + ts - 11, sy + 14), 1)
        # Push bars (chrome)
        pygame.draw.line(surf, (205, 205, 215),
                         (sx + 8, sy + ts // 2 + 4), (sx + 16, sy + ts // 2 + 4), 2)
        pygame.draw.line(surf, (205, 205, 215),
                         (sx + ts - 17, sy + ts // 2 + 4),
                         (sx + ts - 9, sy + ts // 2 + 4), 2)
    elif tile == T:
        pygame.draw.rect(surf, config.TERMINAL_BG, pygame.Rect(
            sx+4, sy+4, ts-9, ts-9), border_radius=3)
        pygame.draw.rect(surf, config.TERMINAL_GREEN, pygame.Rect(
            sx+4, sy+4, ts-9, ts-9), border_radius=3, width=1)
        t_surf = fnt_s.render("PC", True, config.TERMINAL_GREEN)
        surf.blit(t_surf, (sx + (ts - t_surf.get_width()) //
                  2, sy + (ts - t_surf.get_height())//2))
    elif tile == B:
        pygame.draw.rect(surf, (72, 112, 182), pygame.Rect(
            sx+2, sy+2, ts-5, ts-5), border_radius=5)
        pygame.draw.rect(surf, (205, 210, 225),
                         pygame.Rect(sx+3, sy+3, ts-7, 12))
        pygame.draw.ellipse(surf, (235, 238, 255),
                            pygame.Rect(sx+5, sy+4, 20, 10))
    elif tile == TR:
        # Urban park tree — tighter, neater (planted look) with strong shadow
        # Strong ground shadow (suggesting raised perspective)
        shadow_s = pygame.Surface((28, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_s, (0, 0, 0, 130),
                            pygame.Rect(0, 0, 28, 10))
        surf.blit(shadow_s, (sx + ts // 2 - 14, sy + ts - 9))
        # Trunk (taller for 2.5D feel)
        pygame.draw.rect(surf, (72, 48, 28),
                         pygame.Rect(sx + ts // 2 - 3, sy + ts - 24, 6, 24))
        pygame.draw.line(surf, (45, 28, 18),
                         (sx + ts // 2 - 3, sy + ts - 24),
                         (sx + ts // 2 - 3, sy + ts - 1), 1)
        # Canopy (darker base)
        cx_t, cy_t = sx + ts // 2, sy + ts // 2 - 6
        pygame.draw.circle(surf, (22, 65, 32), (cx_t, cy_t + 2), ts // 2 - 3)
        pygame.draw.circle(surf, (32, 92, 42), (cx_t, cy_t), ts // 2 - 5)
        pygame.draw.circle(surf, (52, 132, 58),
                           (cx_t - 2, cy_t - 3), ts // 2 - 9)
        # Light highlight (upper-left)
        pygame.draw.circle(surf, (88, 175, 78), (cx_t - 6, cy_t - 8), 5)
        pygame.draw.circle(surf, (135, 210, 105), (cx_t - 7, cy_t - 9), 2)
    elif tile == FT:
        # Modern circular plaza fountain (steel + jet)
        anim = t_ms / 700.0
        # Granite plaza tile around the fountain
        pygame.draw.rect(surf, (155, 155, 168), pygame.Rect(sx, sy, ts, ts))
        for i in range(2):
            tx_g = sx + ((h + i * 41) % (ts - 4)) + 2
            ty_g = sy + ((h + i * 67) % (ts - 4)) + 2
            pygame.draw.circle(surf, (175, 175, 188), (tx_g, ty_g), 1)
        # Steel ring rim
        pygame.draw.circle(surf, (95, 100, 115),
                           (sx + ts // 2, sy + ts // 2), ts // 2 - 3)
        pygame.draw.circle(surf, (165, 170, 185),
                           (sx + ts // 2, sy + ts // 2), ts // 2 - 3, 2)
        # Water body
        pygame.draw.circle(surf, (52, 130, 188),
                           (sx + ts // 2, sy + ts // 2), ts // 2 - 6)
        pygame.draw.circle(surf, (95, 175, 215),
                           (sx + ts // 2, sy + ts // 2), ts // 2 - 9)
        # Ripples
        for ri in range(3):
            rr = int(((anim + ri * 0.9) % 2.7) / 2.7 * (ts // 2 - 8))
            if 2 < rr < ts // 2 - 6:
                pygame.draw.circle(surf, (180, 220, 240),
                                   (sx + ts // 2, sy + ts // 2), rr, 1)
        # Central jet (vertical water spray)
        jet = int(6 + math.sin(anim * 3) * 3)
        pygame.draw.line(surf, (215, 235, 255),
                         (sx + ts // 2, sy + ts // 2 - 4),
                         (sx + ts // 2, sy + ts // 2 - jet - 8), 3)
        pygame.draw.circle(surf, (235, 245, 255),
                           (sx + ts // 2, sy + ts // 2 - jet - 8), 2)
    elif tile == BN:
        # Modern street bench — steel frame + wood slats
        # Cast shadow
        shadow_s = pygame.Surface((ts - 4, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_s, (0, 0, 0, 110),
                            pygame.Rect(0, 0, ts - 4, 6))
        surf.blit(shadow_s, (sx + 2, sy + ts - 8))
        # Steel legs
        pygame.draw.rect(surf, (62, 65, 78),
                         pygame.Rect(sx + 6, sy + ts // 2 + 8, 4, 12))
        pygame.draw.rect(surf, (62, 65, 78),
                         pygame.Rect(sx + ts - 10, sy + ts // 2 + 8, 4, 12))
        # Wood slat seat
        pygame.draw.rect(surf, (118, 80, 52),
                         pygame.Rect(sx + 4, sy + ts // 2, ts - 8, 8))
        pygame.draw.line(surf, (148, 100, 65),
                         (sx + 4, sy + ts // 2), (sx + ts - 5, sy + ts // 2), 1)
        # Backrest (wood slat)
        pygame.draw.rect(surf, (118, 80, 52),
                         pygame.Rect(sx + 4, sy + ts // 2 - 8, ts - 8, 6))
        pygame.draw.line(surf, (148, 100, 65),
                         (sx + 4, sy + ts // 2 - 8), (sx + ts - 5, sy + ts // 2 - 8), 1)
        # Vertical backrest supports
        pygame.draw.line(surf, (62, 65, 78),
                         (sx + 8, sy + ts // 2 - 8), (sx + 8, sy + ts // 2), 1)
        pygame.draw.line(surf, (62, 65, 78),
                         (sx + ts - 9, sy + ts // 2 - 8), (sx + ts - 9, sy + ts // 2), 1)
    elif tile == LP:
        # Modern streetlight — tall steel post + cool white LED + cast shadow
        anim = t_ms / 900.0
        # Long cast shadow (2.5D effect)
        shadow_s = pygame.Surface((28, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_s, (0, 0, 0, 120),
                            pygame.Rect(0, 0, 28, 10))
        surf.blit(shadow_s, (sx + ts // 2 - 5, sy + ts - 8))
        # Concrete base
        pygame.draw.rect(surf, (78, 78, 92),
                         pygame.Rect(sx + ts // 2 - 5, sy + ts - 8, 10, 6))
        pygame.draw.rect(surf, (52, 52, 65),
                         pygame.Rect(sx + ts // 2 - 5, sy + ts - 8, 10, 6), 1)
        # Slim steel pole
        pygame.draw.rect(surf, (95, 95, 110),
                         pygame.Rect(sx + ts // 2 - 2, sy + 6, 4, ts - 14))
        pygame.draw.line(surf, (135, 135, 155),
                         (sx + ts // 2 - 2, sy + 6),
                         (sx + ts // 2 - 2, sy + ts - 9), 1)
        # Top cap
        pygame.draw.rect(surf, (52, 52, 65),
                         pygame.Rect(sx + ts // 2 - 4, sy + 4, 8, 4))
        # Modern arm + LED housing
        pygame.draw.rect(surf, (62, 62, 78),
                         pygame.Rect(sx + ts // 2 - 8, sy + 8, 16, 4))
        # LED panel (bright cool white)
        pygame.draw.rect(surf, (235, 245, 255),
                         pygame.Rect(sx + ts // 2 - 6, sy + 12, 12, 3))
        # Cool blue-white glow
        glow_r = 14 + int(math.sin(anim * 2.2) * 2)
        glow = pygame.Surface(
            (glow_r * 2 + 4, glow_r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (200, 220, 255, 50),
                           (glow_r + 2, glow_r + 2), glow_r + 2)
        pygame.draw.circle(glow, (235, 245, 255, 100),
                           (glow_r + 2, glow_r + 2), glow_r - 4)
        surf.blit(glow, (sx + ts // 2 - glow_r - 2, sy + 14 - glow_r - 2))
    elif tile == SH:
        pygame.draw.rect(surf, (160, 130, 90),
                         pygame.Rect(sx+2, sy+2, ts-5, ts-5))
        for ly in range(sy+8, sy+ts-4, 8):
            pygame.draw.line(surf, (100, 70, 38), (sx+4, ly), (sx+ts-6, ly), 1)
            pygame.draw.circle(surf, (220, 72, 72), (sx+10, ly-3), 2)
            pygame.draw.circle(surf, (72, 220, 72), (sx+22, ly-3), 2)
            pygame.draw.circle(surf, (220, 220, 72), (sx+34, ly-3), 2)
    elif tile == PD:
        pygame.draw.rect(surf, (142, 102, 62), pygame.Rect(
            sx+6, sy+8, ts-12, ts-12), border_radius=3)
        pygame.draw.line(surf, (58, 38, 18), (sx+ts//2, sy+8),
                         (sx+ts//2, sy+ts-8), 2)
        pygame.draw.circle(surf, (58, 58, 70), (sx+ts//2, sy+ts//2-2), 3)
    elif tile == CF:
        pygame.draw.rect(surf, (52, 34, 24), pygame.Rect(
            sx+6, sy+4, ts-12, ts-8), border_radius=2)
        pygame.draw.circle(surf, (205, 52, 52), (sx+ts//2, sy+ts//2), 3)
        anim = t_ms / 320.0
        for i in range(3):
            off = (anim + i * 0.85) % 2.5
            oy = int(off * 6)
            brightness = max(80, 220 - int(off * 80))
            pygame.draw.circle(surf, (brightness, brightness, brightness),
                               (sx + ts//2 - 5 + i*5, sy + 3 - oy), 3)
    elif tile == TV:
        pygame.draw.rect(surf, (28, 28, 38), pygame.Rect(
            sx+2, sy+4, ts-5, ts-12), border_radius=2)
        sc_cols = [(55, 115, 178), (118, 55, 55),
                   (55, 118, 62), (118, 118, 55)]
        sc = sc_cols[(t_ms // 3000) % 4]
        pygame.draw.rect(surf, sc, pygame.Rect(sx+5, sy+7, ts-11, ts-18))
        scan = (t_ms // 55) % (ts - 20)
        pygame.draw.line(surf, (255, 255, 255),
                         (sx+5, sy+7+scan), (sx+ts-6, sy+7+scan), 1)
    elif tile == SK:
        pygame.draw.rect(surf, (202, 202, 212), pygame.Rect(
            sx+2, sy+2, ts-5, ts-5), border_radius=2)
        pygame.draw.line(surf, (98, 98, 118), (sx+ts//2, sy+4),
                         (sx+ts//2, sy+ts-4), 1)
        pygame.draw.rect(surf, (148, 148, 158),
                         pygame.Rect(sx+ts//2-4, sy+5, 8, 4))
    elif tile == CH:
        pygame.draw.rect(surf, (130, 90, 60), pygame.Rect(
            sx+8, sy+8, ts-16, ts-16), border_radius=3)
        pygame.draw.rect(surf, (90, 60, 38), pygame.Rect(sx+8, sy+6, ts-16, 4))
    elif tile == TB:
        pygame.draw.rect(surf, (155, 110, 70), pygame.Rect(
            sx+2, sy+2, ts-5, ts-5), border_radius=3)
        pygame.draw.rect(surf, (112, 76, 46),
                         pygame.Rect(sx+2, sy+ts-12, ts-5, 6))
        if h % 5 == 0:
            pygame.draw.circle(surf, (178, 138, 98), (sx+ts//2, sy+ts//2), 5)
            pygame.draw.circle(surf, (118, 78, 58), (sx+ts//2, sy+ts//2), 3)
    elif tile == BK:
        pygame.draw.rect(surf, (108, 70, 40),
                         pygame.Rect(sx+2, sy+2, ts-5, ts-5))
        for ly in range(sy+6, sy+ts-4, 8):
            pygame.draw.rect(surf, (178, 55, 55), pygame.Rect(sx+5,  ly, 8, 6))
            pygame.draw.rect(surf, (55, 178, 55), pygame.Rect(sx+14, ly, 8, 6))
            pygame.draw.rect(surf, (55, 55, 178), pygame.Rect(sx+23, ly, 8, 6))
            pygame.draw.rect(surf, (178, 178, 55),
                             pygame.Rect(sx+32, ly, 8, 6))
    elif tile == RG:
        pygame.draw.rect(surf, (170, 65, 88), pygame.Rect(sx, sy, ts, ts))
        pygame.draw.line(surf, (128, 48, 68), (sx, sy+ts//2),
                         (sx+ts, sy+ts//2), 1)
        pygame.draw.rect(surf, (198, 95, 118), pygame.Rect(
            sx+3, sy+3, ts-6, ts-6), width=2)
    elif tile == WIN:
        # Modern glass curtain wall panel — bright reflective glass + steel mullion
        # Steel mullion frame (thicker for 2.5D depth feel)
        pygame.draw.rect(surf, (38, 45, 62),
                         pygame.Rect(sx + 1, sy + 4, ts - 3, ts - 14))
        # Bright sky-blue glass panel
        pygame.draw.rect(surf, (108, 178, 222),
                         pygame.Rect(sx + 3, sy + 6, ts - 7, ts - 18))
        # Mullion divider (vertical only — looks more modern)
        pygame.draw.line(surf, (38, 45, 62),
                         (sx + ts // 2, sy + 6), (sx + ts // 2, sy + ts - 14), 2)
        # Diagonal glass reflection
        pygame.draw.polygon(surf, (185, 220, 245), [
            (sx + 4, sy + 6), (sx + 12, sy + 6),
            (sx + 4, sy + 14)
        ])
        # Bright sheen line
        pygame.draw.line(surf, (220, 240, 255),
                         (sx + ts // 2 + 4, sy + 8),
                         (sx + ts - 6, sy + 16), 1)
        # Bottom shadow (suggests building depth)
        pygame.draw.rect(surf, (28, 35, 50),
                         pygame.Rect(sx + 1, sy + ts - 12, ts - 3, 2))
    elif tile == CR:
        # White zebra crossing painted on asphalt
        for stripe_y in range(sy + 4, sy + ts, 8):
            pygame.draw.rect(surf, (235, 235, 240),
                             pygame.Rect(sx + 4, stripe_y, ts - 8, 4))
            pygame.draw.rect(surf, (255, 255, 255),
                             pygame.Rect(sx + 4, stripe_y, ts - 8, 1))
    elif tile == TM:
        pygame.draw.rect(surf, (55, 55, 68), pygame.Rect(
            sx+4, sy+8, ts-9, ts-16), border_radius=2)
        pygame.draw.rect(surf, (28, 28, 38), pygame.Rect(
            sx+6, sy+10, ts-13, ts-20))
        belt = (t_ms // 55) % max(1, ts - 22)
        pygame.draw.line(surf, (48, 48, 60), (sx+6, sy+10+belt),
                         (sx+ts-7, sy+10+belt), 1)
    elif tile == CN:
        pygame.draw.rect(surf, (232, 222, 202),
                         pygame.Rect(sx+ts//4, sy, ts//2, ts))
        pygame.draw.rect(surf, (198, 188, 168),
                         pygame.Rect(sx+ts//4, sy+2, ts//2, 6))
        pygame.draw.rect(surf, (198, 188, 168),
                         pygame.Rect(sx+ts//4, sy+ts-8, ts//2, 6))
        pygame.draw.line(surf, (208, 198, 178), (sx+ts//4 +
                         4, sy+8), (sx+ts//4+4, sy+ts-8), 1)
        pygame.draw.line(surf, (208, 198, 178), (sx+ts//4 +
                         9, sy+8), (sx+ts//4+9, sy+ts-8), 1)
    elif tile == SC:
        pygame.draw.rect(surf, (26, 56, 104), pygame.Rect(
            sx+2, sy+4, ts-5, ts-8), border_radius=2)
        pygame.draw.rect(surf, (38, 88, 142), pygame.Rect(
            sx+4, sy+6, ts-9, ts-12), 1)
        line_col = [(0, 255, 100), (255, 180, 0), (255, 60, 60),
                    (60, 180, 255)][(t_ms // 2000) % 4]
        for i in range(3):
            pygame.draw.line(surf, line_col, (sx+8, sy+12+i*8),
                             (sx+ts-10+((t_ms//2000+i) % 3)*4, sy+12+i*8), 1)
    elif tile == PG:
        anim_bob = [0, 1, 0, -1][(t_ms // 700) % 4]
        pygame.draw.ellipse(surf, (192, 186, 198), pygame.Rect(
            sx+10, sy+ts-16+anim_bob, 14, 8))
        pygame.draw.circle(surf, (178, 172, 185),
                           (sx+10, sy+ts-14+anim_bob), 4)
        pygame.draw.circle(surf, (38, 38, 38), (sx+8, sy+ts-14+anim_bob), 1)
        pygame.draw.arc(surf, (148, 98, 148),
                        pygame.Rect(sx+10, sy+ts-18+anim_bob, 14, 8), 0, math.pi, 1)
    elif tile == FL:
        anim = t_ms / 850.0
        for fx, fy, fc in [(8, 8, (255, 80, 80)), (20, 12, (255, 205, 80)),
                           (32, 8, (162, 80, 205)), (12, 28, (255, 148, 205)),
                           (28, 30, (80, 178, 255))]:
            sway = int(math.sin(anim + fx * 0.28) * 1.5)
            pygame.draw.circle(surf, fc, (sx+fx+sway, sy+fy), 3)
            pygame.draw.line(surf, (38, 112, 42),
                             (sx+fx+sway, sy+fy+3), (sx+fx, sy+fy+9), 1)
    elif tile == FN:
        # Modern metal railing fence with chrome highlights
        # Top and bottom rails (steel)
        pygame.draw.rect(surf, (108, 108, 122),
                         pygame.Rect(sx + 2, sy + ts // 3, ts - 5, 4))
        pygame.draw.line(surf, (165, 165, 180),
                         (sx + 2, sy + ts // 3), (sx + ts - 4, sy + ts // 3), 1)
        pygame.draw.rect(surf, (108, 108, 122),
                         pygame.Rect(sx + 2, sy + 2 * ts // 3, ts - 5, 4))
        pygame.draw.line(surf, (165, 165, 180),
                         (sx + 2, sy + 2 * ts // 3),
                         (sx + ts - 4, sy + 2 * ts // 3), 1)
        # Vertical balusters (thin steel rods)
        for px_f in range(sx + 4, sx + ts - 4, 8):
            pygame.draw.rect(surf, (95, 95, 108),
                             pygame.Rect(px_f, sy + 4, 3, ts - 8))
            pygame.draw.line(surf, (155, 155, 168),
                             (px_f, sy + 4), (px_f, sy + ts - 5), 1)
    elif tile == CB:
        pygame.draw.rect(surf, (130, 110, 80), pygame.Rect(
            sx+4, sy+4, ts-9, ts-9), border_radius=3)
        pygame.draw.rect(surf, (98, 78, 58), pygame.Rect(
            sx+4, sy+4, ts-9, ts-9), border_radius=3, width=2)
        pygame.draw.line(surf, (108, 88, 65), (sx+ts//2, sy+4),
                         (sx+ts//2, sy+ts-4), 1)
        pygame.draw.line(surf, (108, 88, 65), (sx+4, sy+ts//2),
                         (sx+ts-4, sy+ts//2), 1)
    elif tile == RP:
        pygame.draw.rect(surf, (148, 28, 38), pygame.Rect(sx, sy, ts, ts))
        pygame.draw.line(surf, (88, 18, 28), (sx, sy+ts-1),
                         (sx+ts, sy+ts-1), 2)
        pygame.draw.rect(surf, (165, 42, 52), pygame.Rect(
            sx+3, sy+3, ts-6, ts-6), width=1)
    elif tile == SG:
        pygame.draw.rect(surf, (210, 188, 55), pygame.Rect(
            sx+4, sy+8, ts-9, ts-16), border_radius=2)
        pygame.draw.rect(surf, (178, 158, 42), pygame.Rect(
            sx+4, sy+8, ts-9, ts-16), border_radius=2, width=1)
        pygame.draw.rect(surf, (98, 88, 65), pygame.Rect(
            sx+ts//2-2, sy+ts-10, 4, 10))
