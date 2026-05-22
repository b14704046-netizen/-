"""Scenes - city overworld + all building interiors."""
import pygame
import math
import random
import config
from entities import NPC

# Tile constants
F  = 0   # floor (interior)
W  = 1   # wall
R  = 2   # road
G  = 3   # grass
D  = 4   # desk
T  = 5   # terminal/PC
B  = 6   # bed
S  = 7   # sidewalk
C  = 8   # carpet
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
TR2= 28  # building roof (decoration)
WIN= 29  # window
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
GW = 40  # graffiti wall

SOLID = {W, D, B, FT, BN, LP, SH, PD, CF, TV, SK, CH, TB, BK, TR, FN, CN, CB, TM, SG, SC, GW}

TILE_COLOR = {
    F:   (182, 160, 138),
    W:   (58,  50,  72),
    R:   (42,  44,  54),
    G:   (55,  145, 58),
    D:   (148, 108, 66),
    T:   (12,  68,  108),
    B:   (88,  128, 192),
    S:   (152, 142, 130),
    C:   (142, 88,  108),
    DR:  (188, 138, 72),
    TR:  (36,  98,  44),
    FT:  (72,  158, 198),
    BN:  (112, 72,  50),
    LP:  (78,  78,  95),
    SH:  (158, 128, 88),
    PD:  (142, 100, 60),
    CF:  (52,  34,  24),
    TV:  (32,  32,  45),
    SK:  (205, 205, 215),
    CH:  (128, 88,  58),
    TB:  (152, 108, 68),
    PG:  (195, 195, 145),
    FL:  (55,  152, 62),
    WD:  (172, 128, 86),
    TI:  (198, 198, 205),
    ST:  (128, 128, 140),
    BK:  (105, 68,  38),
    RG:  (168, 62,  88),
    TR2: (138, 98,  58),
    WIN: (130, 178, 210),
    CR:  (215, 215, 218),
    PV:  (168, 158, 148),
    CB:  (128, 108, 78),
    TM:  (55,  55,  68),
    SG:  (205, 185, 55),
    FN:  (128, 128, 140),
    CN:  (235, 225, 205),
    MR:  (225, 222, 215),
    RP:  (148, 28,  38),
    SC:  (24,  55,  105),
    GW:  (62,  58,  72),
}


def _row(*cells):
    return list(cells)


# ── City Overworld Map ────────────────────────────────────────────────
# 72 columns × 48 rows. New east district + south district added.
def _build_city():
    """Build city — smaller building footprints, 2.5D sprites drawn separately."""
    cols, rows = 72, 48
    m = [[G for _ in range(cols)] for _ in range(rows)]

    # ── Roads (unchanged) ────────────────────────────────────────────────
    for y in [8, 9, 10]:
        for x in range(cols):
            m[y][x] = R if y == 9 else S
    for y in [24, 25, 26]:
        for x in range(cols):
            m[y][x] = R if y == 25 else S
    for y in [36, 37, 38]:
        for x in range(cols):
            m[y][x] = R if y == 37 else S
    for x in [23, 24, 25]:
        for y in range(rows):
            m[y][x] = R if x == 24 else S
    for x in [49, 50, 51]:
        for y in range(rows):
            m[y][x] = R if x == 50 else S
    for y in [8, 10, 24, 26, 36, 38]:
        for x in [23, 25, 49, 51]:
            m[y][x] = CR

    # ── Smaller building footprints ───────────────────────────────────────
    # Top row: y=4-7 (3 tiles deep), door at south wall y=7
    # Middle row: y=12-22 (10 tiles deep), door at south wall y=22
    # Capitol: y=27-33, door at north wall y=27
    # University: y=39-45, door at north wall y=39
    buildings = [
        (2,  4,  7,  7,  4,  7,  config.SCENE_APARTMENT),
        (10, 4,  15, 7,  12, 7,  config.SCENE_CAFE),
        (27, 4,  32, 7,  29, 7,  config.SCENE_SUPERMARKET),
        (35, 4,  41, 7,  38, 7,  config.SCENE_GYM),
        (53, 4,  63, 7,  58, 7,  config.SCENE_BANK),
        (2,  12, 9,  22, 5,  22, config.SCENE_FED),
        (12, 12, 18, 22, 15, 22, config.SCENE_PRESS),
        (38, 12, 44, 22, 41, 22, config.SCENE_WALL_ST),
        (52, 12, 62, 22, 57, 22, config.SCENE_HOSPITAL),
        (20, 27, 33, 33, 26, 27, config.SCENE_CAPITOL),
        (2,  39, 15, 45, 8,  39, config.SCENE_UNIVERSITY),
    ]

    for x0, y0, x1, y1, dx, dy, _ in buildings:
        for x in range(x0, x1 + 1):
            m[y0][x] = W
            m[y1][x] = W
        for y in range(y0, y1 + 1):
            m[y][x0] = W
            m[y][x1] = W
        for x in range(x0 + 2, x1 - 1, 3):
            if m[y0][x] == W: m[y0][x] = WIN
        for y in range(y0 + 1, y1):
            for x in range(x0 + 1, x1):
                m[y][x] = WD if y < 8 else TI
        m[dy][dx] = DR

    # ── Central park ─────────────────────────────────────────────────────
    for y in range(12, 23):
        for x in range(27, 37):
            m[y][x] = G
    for tx, ty in [(28,13),(30,12),(33,12),(35,13),(28,16),(35,16),
                   (28,20),(30,21),(33,21),(35,20),(31,16),(32,18),
                   (29,15),(34,14),(30,19),(36,17)]:
        m[ty][tx] = TR
    m[17][31] = FT; m[17][32] = FT
    m[18][31] = FT; m[18][32] = FT
    m[15][29] = BN; m[15][34] = BN
    m[20][29] = BN; m[20][34] = BN
    m[16][30] = PG; m[19][33] = PG
    m[14][32] = PG; m[21][31] = PG
    for tx, ty in [(28,17),(29,18),(33,16),(34,19),(31,14),(32,21)]:
        m[ty][tx] = FL

    # ── Street furniture ─────────────────────────────────────────────────
    for tx, ty in [(54,11),(58,11),(63,11),(67,11),(54,24),(58,24),(63,24),(67,24)]:
        if m[ty][tx] == S: m[ty][tx] = BN
    for tx, ty in [(53,8),(56,8),(60,8),(64,8),(68,8)]:
        if m[ty][tx] == S: m[ty][tx] = LP

    # South plaza (same as before)
    for tx, ty in [(26,41),(27,40),(30,42),(33,41),(36,43),
                   (40,41),(44,40),(47,42),(50,41),(53,43),
                   (57,40),(60,42),(64,41),(67,43),(70,41)]:
        if 0 <= ty < rows and 0 <= tx < cols and m[ty][tx] == G:
            m[ty][tx] = TR
    for tx, ty in [(28,43),(31,44),(35,42),(42,44),(46,43),(51,42)]:
        if 0 <= ty < rows and 0 <= tx < cols and m[ty][tx] == G:
            m[ty][tx] = FL
    for tx, ty in [(30,40),(45,40),(60,40),(30,45),(45,45),(60,45)]:
        if 0 <= ty < rows and 0 <= tx < cols and m[ty][tx] == G:
            m[ty][tx] = BN
    for ty in [42, 43]:
        for tx in [37, 38]:
            m[ty][tx] = FT
    m[42][36] = FL; m[42][39] = FL; m[43][36] = FL; m[43][39] = FL

    # Random trees/flowers on remaining grass
    for x in range(0, cols):
        for y in range(0, rows):
            if m[y][x] == G:
                in_park  = (27 <= x <= 36 and 12 <= y <= 22)
                in_south = (27 <= x <= 70 and 39 <= y <= 47)
                if random.random() < 0.05 and not in_park and not in_south:
                    m[y][x] = TR
                elif random.random() < 0.06 and not in_park:
                    m[y][x] = FL

    # Lampposts on actual sidewalk rows
    for x in range(2, cols, 5):
        for sw_y in [8, 10, 24, 26, 36, 38]:
            if 0 <= sw_y < rows and m[sw_y][x] == S:
                m[sw_y][x] = LP

    # Bus stops (moved to actual S rows)
    for bx, by in [(8,8),(20,10),(38,26),(12,24),(56,8),(56,24),(8,36),(30,36)]:
        if 0 <= by < rows and 0 <= bx < cols and m[by][bx] == S:
            m[by][bx] = BN
        if 0 <= by < rows and 0 <= bx+1 < cols and m[by][bx+1] == S:
            m[by][bx+1] = SG

    for nx, ny in [(4,8),(14,24),(40,10),(55,10),(55,26),(8,36)]:
        if 0 <= ny < rows and 0 <= nx < cols and m[ny][nx] == S:
            m[ny][nx] = SG
    for ax, ay in [(39,8),(22,26),(48,26),(48,10)]:
        if 0 <= ay < rows and 0 <= ax < cols and m[ay][ax] == S:
            m[ay][ax] = CB
    for gx, gy in [(11,10),(26,26),(26,36),(48,38)]:
        if 0 <= gy < rows and 0 <= gx < cols and m[gy][gx] == S:
            m[gy][gx] = GW

    signs = {
        (4,  7):  "公寓",
        (12, 7):  "咖啡廳",
        (29, 7):  "超市",
        (38, 7):  "健身房",
        (58, 7):  "聯邦銀行",
        (5,  22): "聯準會",
        (15, 22): "新聞室",
        (41, 22): "華爾街",
        (57, 22): "醫療中心",
        (26, 27): "國會",
        (8,  39): "聯邦大學",
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
    # Sofa (L-shape facing TV): back row + armrests
    for x in range(9, 14):
        m[3][x] = CH
    m[4][9] = CH
    m[4][13] = CH
    # Coffee table in front of sofa
    m[5][10] = TB; m[5][11] = TB; m[5][12] = TB
    # Kitchen
    m[2][16] = SK; m[2][17] = CF
    m[3][16] = TB; m[3][17] = TB
    # Bookshelf
    m[2][6] = BK; m[2][7] = BK
    # Fridge
    m[2][14] = CB
    # Rug under sofa/living area
    for x in range(8, 15):
        for y in range(6, 10):
            if m[y][x] == WD:
                m[y][x] = RG
    # Plants in corners
    m[12][2] = FL
    m[12][17] = FL
    # Windows
    m[0][5] = WIN; m[0][10] = WIN; m[0][15] = WIN
    # Golf putting green (lower-right area)
    for y in range(8, 13):
        for x in range(15, 19):
            m[y][x] = G

    npcs = []
    doors = [{"x": 10, "y": 13, "target": config.SCENE_CITY, "spawn_tx": 5, "spawn_ty": 8}]
    objects = [
        {"x": 2,  "y": 2,  "type": "bed",     "label": "床（睡覺跳過時間）"},
        {"x": 17, "y": 2,  "type": "coffee",  "label": "咖啡機（手沖小遊戲）"},
        {"x": 11, "y": 2,  "type": "tv",      "label": "電視（看新聞）"},
        {"x": 6,  "y": 2,  "type": "books",   "label": "書架（讀經濟學）"},
        {"x": 14, "y": 2,  "type": "fridge",  "label": "冰箱（看食物價格）"},
        {"x": 7,  "y": 4,  "type": "guitar",  "label": "吉他（聖誕演奏）"},
        {"x": 3,  "y": 9,  "type": "bicycle", "label": "自行車"},
        {"x": 17, "y": 10, "type": "golf",    "label": "高爾夫（小遊戲）"},
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
    m[2][5] = CF; m[2][8] = CF; m[2][11] = CF
    # Tables and chairs
    for tx in [3, 7, 11]:
        m[7][tx] = TB; m[7][tx+1] = TB
        m[6][tx] = CH; m[8][tx] = CH
    # Bulletin board on east wall
    m[5][16] = BK
    # Window
    m[0][4] = WIN; m[0][9] = WIN; m[0][13] = WIN

    npcs = [
        NPC(6, 4, "barista",    "店員Anna",   "cafe_barista",    0),
        NPC(4, 7, "citizen",    "上班族",      "cafe_customer1",  0),
        NPC(12, 7, "citizen",   "學生",        "cafe_customer2",  0),
        NPC(8, 7, "citizen",    "作家 David",  "cafe_writer",     1),
        NPC(14, 5, "trader",    "股市老手",    "cafe_trader",     0),
    ]
    doors = [{"x": 9, "y": 11, "target": config.SCENE_CITY, "spawn_tx": 16, "spawn_ty": 8}]
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
        m[y][10] = RP; m[y][11] = RP; m[y][12] = RP
    # Boardroom desk
    for x in range(5, 17):
        m[5][x] = TB
    # Chairs around boardroom
    for x in range(5, 17, 2):
        m[4][x] = CH
        m[6][x] = CH
    # Powell's office
    m[2][3] = D; m[2][4] = T  # main terminal
    # Secondary terminals
    m[2][10] = T; m[2][15] = D
    m[2][18] = T; m[2][19] = D
    # Columns (marble)
    m[8][3] = CN; m[8][18] = CN
    # Windows
    m[0][6] = WIN; m[0][11] = WIN; m[0][16] = WIN

    npcs = [
        NPC(8,  4,  "guard",      "守衛",            "fed_guard",       2),
        NPC(15, 4,  "secretary",  "秘書 Jane",        "fed_secretary",   0),
        NPC(12, 8,  "politician", "副主席 Brian",     "fed_vicechair",   0),
        NPC(5,  6,  "politician", "首席經濟學家 Smith","fed_economist1",  0),
        NPC(18, 6,  "secretary",  "政策分析師 Park",  "fed_analyst",     1),
    ]
    doors = [{"x": 11, "y": 13, "target": config.SCENE_CITY, "spawn_tx": 5, "spawn_ty": 24}]
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
        NPC(13, 4, "shopper","年輕媽媽",     "sm_young_mom", 0),
        NPC(17, 7, "child",  "小朋友",       "sm_child", 0),
        NPC(9, 10, "shopper","收銀員",       "sm_cashier", 0),
    ]
    doors = [{"x": 10, "y": 12, "target": config.SCENE_CITY, "spawn_tx": 31, "spawn_ty": 8}]
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
    m[7][3] = CB; m[7][4] = CB
    m[7][11] = CB; m[7][12] = CB
    # TV
    m[1][8] = TV
    npcs = [
        NPC(3,  5,  "citizen", "教練 Mike",  "gym_coach",    0),
        NPC(10, 6,  "citizen", "健身愛好者", "gym_member",   0),
        NPC(3,  7,  "citizen", "練腿日男",   "gym_heavy",    2),
        NPC(12, 4,  "citizen", "健身新人",   "gym_newbie",   1),
    ]
    doors = [{"x": 8, "y": 10, "target": config.SCENE_CITY, "spawn_tx": 43, "spawn_ty": 8}]
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
    m[2][8] = PD; m[2][9] = PD
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
        NPC(12, 6, "journalist","彭博社",      "press_bloomberg", 0),
        NPC(6, 9, "journalist", "金融時報",    "press_ft", 0),
        NPC(10, 9, "journalist","路透",        "press_reuters", 0),
    ]
    doors = [{"x": 9, "y": 11, "target": config.SCENE_CITY, "spawn_tx": 16, "spawn_ty": 24}]
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
        m[3][x] = D; m[2][x] = T
        m[6][x] = D; m[5][x] = T
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
        NPC(10, 4, "trader","量化基金經理",   "ws_quant", 0),
        NPC(13, 4, "trader","債券交易員",     "ws_bond", 0),
        NPC(5, 8, "trader", "新進分析師",     "ws_analyst", 0),
    ]
    doors = [{"x": 9, "y": 11, "target": config.SCENE_CITY, "spawn_tx": 43, "spawn_ty": 24}]
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
        m[y][10] = RP; m[y][11] = RP; m[y][12] = RP
    # Columns at front
    for x in [3, 7, 14, 18]:
        m[2][x] = CN
    # Tiered seating
    for y in [4, 5, 7]:
        for x in range(3, 19, 2):
            m[y][x] = CH
    # Speaker's podium
    m[3][10] = PD; m[3][11] = PD
    npcs = [
        NPC(4, 4, "politician", "參議員 Warren", "cap_warren", 0),
        NPC(8, 4, "politician", "參議員 Cruz",   "cap_cruz", 0),
        NPC(13, 4, "politician","參議員 Sanders","cap_sanders", 0),
        NPC(17, 4, "politician","議長",          "cap_speaker", 0),
    ]
    doors = [{"x": 11, "y": 13, "target": config.SCENE_CITY, "spawn_tx": 23, "spawn_ty": 27}]
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
        m[0][x] = TR; m[rows-1][x] = TR
    for y in range(rows):
        m[y][0] = TR; m[y][cols-1] = TR
    m[15][12] = PV  # exit
    # Fountain
    for y in [6, 7]:
        for x in [11, 12, 13]:
            m[y][x] = FT
    # Benches
    m[5][4] = BN; m[5][18] = BN; m[10][4] = BN; m[10][18] = BN
    # Trees
    for tx, ty in [(3,3), (6,2), (10,3), (15,2), (20,3), (3,13), (6,14), (10,14), (15,13), (20,14)]:
        m[ty][tx] = TR
    # Pigeon spots
    for tx, ty in [(5,9), (8,10), (11,9), (14,10), (17,9), (20,10)]:
        m[ty][tx] = PG
    # Flowers
    for tx, ty in [(4,7), (6,7), (18,7), (20,7), (4,11), (6,11), (18,11), (20,11)]:
        m[ty][tx] = FL
    # Newspaper stand near entrance
    m[13][3] = SG

    npcs = [
        NPC(7, 5, "elder",     "公園老伯",  "park_elder", 0),
        NPC(15, 5, "child",    "小孩",      "park_kid", 1),
        NPC(20, 11, "citizen", "慢跑者",    "park_jogger", 2),
        NPC(18, 4, "elder",    "下棋老人",  "park_elder", 1),
    ]
    doors = [{"x": 12, "y": 15, "target": config.SCENE_CITY, "spawn_tx": 31, "spawn_ty": 15}]
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
        m[y][10] = RP; m[y][11] = RP; m[y][12] = RP
    # Teller counters
    for x in range(4, 18):
        m[4][x] = SK
    # Vault door (decorative CB block cluster)
    for y in range(2, 5):
        for x in range(2, 5):
            m[y][x] = CB
    # Trading terminals
    for x in [6, 9, 12, 15, 18]:
        m[7][x] = T; m[6][x] = D
    # Columns
    m[9][3] = CN; m[9][18] = CN
    # Windows
    m[0][6] = WIN; m[0][11] = WIN; m[0][16] = WIN

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
        m[by_b][bx] = B; m[by_b][bx+1] = B
    # Medical equipment
    m[2][3] = TV; m[2][18] = TV
    # Columns
    m[7][7] = CN; m[7][14] = CN
    # Windows
    m[0][5] = WIN; m[0][11] = WIN; m[0][17] = WIN
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
    m[11][11] = PD; m[11][12] = PD
    # Tiered lecture seating (rows 3-9, audience faces south toward screen)
    for sy in [3, 4, 6, 7, 9]:
        for sx in range(3, 21, 2):
            m[sy][sx] = CH
    # Library corner (west side)
    for x in range(2, 7):
        m[12][x] = BK
    # Study tables (east side)
    for tx in [16, 19]:
        m[12][tx] = TB; m[12][tx+1] = TB
        m[13][tx] = CH; m[13][tx+1] = CH
    # Vending machine near entry
    m[2][2] = CB
    # Windows
    m[0][6] = WIN; m[0][17] = WIN
    m[15][6] = WIN; m[15][12] = WIN; m[15][18] = WIN

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
    def __init__(self, name, tiles, npcs, doors, objects, spawn=(2,2)):
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
            if not (0 <= tx < self.cols and 0 <= ty < self.rows): return True
            if self.tiles[ty][tx] in SOLID: return True
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
        config.SCENE_SUPERMARKET:(10, 11),
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
_SIGN_STYLES = {
    "咖啡": ((0, 70, 40),    (0, 130, 78),   (255, 248, 200)),
    "超市": ((180, 36, 24),  (240, 72, 48),  (255, 255, 255)),
    "健身": ((22, 30, 72),   (56, 80, 200),  (200, 220, 255)),
    "銀行": ((28, 22, 16),   (188, 158, 72), (255, 240, 160)),
    "聯準": ((18, 28, 56),   (158, 138, 72), (240, 228, 172)),
    "新聞": ((28, 28, 30),   (80, 80, 88),   (240, 240, 240)),
    "華爾": ((10, 48, 20),   (40, 160, 72),  (180, 255, 180)),
    "醫療": ((230, 242, 255),(200, 22, 22),  (20, 20, 20)),
    "國會": ((188, 180, 166),(98, 88, 68),   (26, 20, 16)),
    "大學": ((16, 32, 84),   (100, 118, 218),(255, 255, 255)),
    "公寓": ((76, 56, 40),   (136, 96, 64),  (255, 238, 196)),
    "報攤": ((208, 172, 32), (150, 114, 16), (24, 14, 4)),
    "ATM":  ((18, 44, 136),  (78, 118, 218), (255, 255, 255)),
    "塗鴉": ((38, 38, 48),   (118, 78, 158), (200, 158, 238)),
}

def _sign_style(label):
    for key, style in _SIGN_STYLES.items():
        if key in label:
            return style
    return (18, 18, 26), (78, 78, 98), (255, 255, 255)


def draw_city_signs(screen, scene, cx, cy, fnt_s):
    """Draw building name signs directly on screen (after pixel-art scaling) — no flicker."""
    if scene.name != config.SCENE_CITY:
        return
    ts = config.TILE_SIZE
    for (tx, ty_t), label in CITY_SIGNS.items():
        sx = tx * ts - int(cx)
        sy = ty_t * ts - int(cy) - 18
        if -200 < sx < config.SCREEN_W + 200 and -60 < sy < config.SCREEN_H:
            _, _, text_col = _sign_style(label)
            # Dark shadow for contrast against any background
            sh = fnt_s.render(label, True, (0, 0, 0))
            screen.blit(sh, (sx + 1, sy + 1))
            t = fnt_s.render(label, True, text_col)
            screen.blit(t, (sx, sy))


def _draw_apartment_extras(surf, cx, cy, ts, t_ms):
    """Draw guitar, bicycle, and golf hole for the apartment scene."""
    # ── Guitar at tile (7, 4) ───────────────────────────────────────────
    gx = 7 * ts - int(cx) + ts // 2
    gy = 4 * ts - int(cy) + ts // 2 + 4
    # Body (figure-8 shape: two ellipses)
    pygame.draw.ellipse(surf, (160, 100, 30), pygame.Rect(gx - 8, gy - 2, 16, 18))
    pygame.draw.ellipse(surf, (160, 100, 30), pygame.Rect(gx - 7, gy - 14, 14, 14))
    pygame.draw.ellipse(surf, (190, 130, 50), pygame.Rect(gx - 7, gy - 1, 14, 16))
    pygame.draw.ellipse(surf, (190, 130, 50), pygame.Rect(gx - 6, gy - 13, 12, 12))
    # Sound hole
    pygame.draw.circle(surf, (100, 60, 15), (gx, gy + 6), 4)
    # Neck
    pygame.draw.rect(surf, (140, 88, 25), pygame.Rect(gx - 2, gy - 36, 4, 26))
    # Headstock
    pygame.draw.rect(surf, (120, 75, 20), pygame.Rect(gx - 5, gy - 44, 10, 9), border_radius=2)
    # Strings (3 visible)
    for si in range(3):
        sxs = gx - 3 + si * 3
        pygame.draw.line(surf, (215, 205, 160), (sxs, gy - 36), (sxs, gy + 13), 1)
    # Guitar strap (leaning against wall hint)
    pygame.draw.line(surf, (120, 60, 20), (gx + 7, gy - 8), (gx + 10, gy + 15), 2)

    # ── Bicycle at tile (3, 9) ──────────────────────────────────────────
    bx = 3 * ts - int(cx) + ts // 2
    by = 9 * ts - int(cy) + ts // 2 + 2
    wr = ts // 4 - 2  # wheel radius = 10
    # Wheels
    pygame.draw.circle(surf, (40, 40, 48), (bx - wr - 6, by), wr, 3)
    pygame.draw.circle(surf, (40, 40, 48), (bx + wr + 6, by), wr, 3)
    # Spokes
    for spoke in range(4):
        ang = spoke * math.pi / 4
        for bwx, bwy in [(bx - wr - 6, by), (bx + wr + 6, by)]:
            pygame.draw.line(surf, (80, 80, 90),
                             (bwx, bwy),
                             (bwx + int((wr - 2) * math.cos(ang)),
                              bwy + int((wr - 2) * math.sin(ang))), 1)
    # Frame tubes
    rear_hub = (bx - wr - 6, by)
    front_hub = (bx + wr + 6, by)
    bb = (bx + 2, by - 4)           # bottom bracket
    seat_tube_top = (bx - 4, by - wr - 2)  # seat tube top
    head_tube = (bx + wr, by - wr + 2)     # head tube
    pygame.draw.line(surf, (60, 100, 200), rear_hub,      bb,            3)
    pygame.draw.line(surf, (60, 100, 200), rear_hub,      seat_tube_top, 2)
    pygame.draw.line(surf, (60, 100, 200), bb,            seat_tube_top, 2)
    pygame.draw.line(surf, (60, 100, 200), bb,            head_tube,     3)
    pygame.draw.line(surf, (60, 100, 200), seat_tube_top, head_tube,     2)
    pygame.draw.line(surf, (60, 100, 200), head_tube,     front_hub,     2)
    # Saddle
    pygame.draw.rect(surf, (30, 30, 36), pygame.Rect(seat_tube_top[0] - 7, seat_tube_top[1] - 2, 13, 3), border_radius=1)
    # Handlebar
    pygame.draw.line(surf, (30, 30, 36), (head_tube[0] - 2, head_tube[1]),
                     (head_tube[0] - 2, head_tube[1] - 8), 2)
    pygame.draw.line(surf, (30, 30, 36), (head_tube[0] - 6, head_tube[1] - 8),
                     (head_tube[0] + 2, head_tube[1] - 8), 2)

    # ── Golf hole + flag at tile (17, 10) ──────────────────────────────
    hx = 17 * ts - int(cx) + ts // 2
    hy = 10 * ts - int(cy) + ts // 2
    # Cup shadow
    pygame.draw.circle(surf, (10, 38, 14), (hx, hy), 10)
    pygame.draw.circle(surf, (8, 28, 10), (hx, hy), 8)
    # Pole
    pygame.draw.line(surf, (218, 205, 170), (hx, hy - 2), (hx, hy - 30), 2)
    # Flag (waving)
    wave = int(3 * math.sin(t_ms / 280.0))
    pygame.draw.polygon(surf, (220, 38, 38), [
        (hx + 1, hy - 30),
        (hx + 14 + wave, hy - 24),
        (hx + 1, hy - 18),
    ])


def draw_scene(surf, scene, cx, cy, economy, fnt_s):
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

    if scene.name == config.SCENE_CITY:
        _draw_city_ambience(surf, scene, cx, cy)

    if scene.name == config.SCENE_APARTMENT:
        _draw_apartment_extras(surf, cx, cy, ts, pygame.time.get_ticks())

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
                    bg = pygame.Surface((out_t.get_width()+8, out_t.get_height()+4), pygame.SRCALPHA)
                    bg.fill((80, 0, 0, 200))
                    surf.blit(bg, (sx, sy))
                    surf.blit(out_t, (sx+4, sy+2))
            else:
                col = config.RED if cpi > 6 else config.YELLOW if cpi > 3 else config.GREEN
                t = fnt_s.render(f"${price}", True, col)
                bg = pygame.Surface((t.get_width()+8, t.get_height()+4), pygame.SRCALPHA)
                bg.fill((0,0,0,180))
                surf.blit(bg, (sx, sy))
                surf.blit(t, (sx+4, sy+2))

    # 城市蕭條視覺：失業高時部分建築燈光熄滅、貼封店告示
    if scene.name == config.SCENE_CITY and economy.unemployment > 8:
        severity = min(1.0, (economy.unemployment - 8) / 6.0)
        closed_buildings = [
            (2,  4, 7,  7),   # 公寓
            (35, 4, 41, 7),   # 健身房
        ]
        if severity > 0.5:
            closed_buildings.append((10, 4, 15, 7))  # 咖啡廳
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
    """Animated cars and ambient life on the city map."""
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
        (37, (100, 130, 255),0.032, 0.80, -1),
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
            pygame.draw.rect(surf, color, pygame.Rect(car_x, car_y, cw, ch), border_radius=4)
            wind_x = (car_x + cw - 14) if direction > 0 else (car_x + 2)
            pygame.draw.rect(surf, (155, 212, 242),
                             pygame.Rect(wind_x, car_y + 3, 12, 10), border_radius=2)
            pygame.draw.circle(surf, (28, 28, 28), (car_x + 7, car_y + ch - 1), 4)
            pygame.draw.circle(surf, (28, 28, 28), (car_x + cw - 7, car_y + ch - 1), 4)
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
            pygame.draw.rect(surf, color, pygame.Rect(car_x, car_y, cw, ch), border_radius=4)
            wind_y = (car_y + ch - 14) if direction > 0 else (car_y + 2)
            pygame.draw.rect(surf, (155, 212, 242),
                             pygame.Rect(car_x + 3, wind_y, 14, 12), border_radius=2)
            pygame.draw.circle(surf, (28, 28, 28), (car_x + cw // 2, car_y + 5), 4)
            pygame.draw.circle(surf, (28, 28, 28), (car_x + cw // 2, car_y + ch - 5), 4)

    # Building facades — drawn over wall tiles on building fronts
    _draw_building_facades(surf, cx, cy, ts, t_ms)


# 2.5D building data: (x0, y0, x1, y1, floors, face_rgb, side_rgb, roof_rgb, style)
_BLD_2D5 = [
    (2,  4,  7,  7,  4, (148, 94,  62), (104, 64, 42), (122, 78, 52), "apartment"),
    (10, 4,  15, 7,  4, (18,  80,  46), (10,  56, 30), (14,  66, 38), "cafe"),
    (27, 4,  32, 7,  4, (192, 48,  28), (148, 32, 16), (160, 40, 22), "market"),
    (35, 4,  41, 7,  4, (26,  42,  86), (16,  28, 64), (20,  34, 74), "gym"),
    (53, 4,  63, 7,  5, (180, 172, 152),(136,128,108), (192,184,164), "bank"),
    (2,  12, 9,  22, 7, (52,  44,  66), (34,  28, 48), (42,  36, 56), "fed"),
    (12, 12, 18, 22, 7, (62,  72,  92), (42,  52, 70), (52,  62, 82), "press"),
    (38, 12, 44, 22, 8, (16,  20,  34), (8,   12, 22), (12,  16, 28), "wall_st"),
    (52, 12, 62, 22, 6, (202, 212, 222),(160,170,180), (212,220,228), "hospital"),
    (20, 27, 33, 33, 4, (210, 202, 182),(168,160,140), (220,212,192), "capitol"),
    (2,  39, 15, 45, 5, (102, 74,  44), (74,  50, 28), (86,  60, 36), "university"),
]


def _bld_win_row(surf, fx, ftop, fw, floor_h, f, num_w, ww, wh, win_c):
    """Draw one row of windows on floor f (0 = topmost floor)."""
    fy_f = ftop + f * floor_h + (floor_h - wh) // 2
    sp = fw // (num_w + 1)
    for wi in range(num_w):
        wx = fx + sp * (wi + 1) - ww // 2
        pygame.draw.rect(surf, win_c, pygame.Rect(wx, fy_f, ww, wh))
        pygame.draw.rect(surf, tuple(max(0, c - 40) for c in win_c),
                         pygame.Rect(wx, fy_f, ww, wh), 1)


def _bld_details(surf, fx, ftop, fw, fh, floors, fbot, style, base_c, ts, t_ms):
    fh_fl = ts          # pixels per floor
    wg = int(185 + 40 * math.sin(t_ms / 1100.0))

    if style == "apartment":
        # Brick texture
        bc = tuple(max(0, c - 16) for c in base_c)
        for i in range(0, fh, 7):
            pygame.draw.line(surf, bc, (fx, ftop + i), (fx + fw, ftop + i), 1)
        for row in range(fh // 7 + 1):
            off = (row % 2) * (ts // 2)
            for bk in range(fw // ts + 2):
                bkx = fx + bk * ts + off - ts // 2
                pygame.draw.line(surf, bc, (bkx, ftop + row * 7),
                                 (bkx, min(ftop + row * 7 + 7, fbot)), 1)
        # Windows with mullions on upper floors
        for f in range(floors - 1):
            fy_f = ftop + f * fh_fl
            sp = fw // 3
            for wi in range(2):
                wx = fx + sp * (wi + 1) - ts // 4
                wy = fy_f + (fh_fl - ts // 2) // 2
                ww, wh = ts // 2, ts // 2
                pygame.draw.rect(surf, (wg - 30, wg - 10, 50), pygame.Rect(wx, wy, ww, wh))
                pygame.draw.line(surf, (wg - 60, wg - 40, 28), (wx + ww // 2, wy), (wx + ww // 2, wy + wh), 1)
                pygame.draw.line(surf, (wg - 60, wg - 40, 28), (wx, wy + wh // 2), (wx + ww, wy + wh // 2), 1)
            # Balcony ledge at floor divider
            if f > 0:
                pygame.draw.rect(surf, tuple(min(255, c + 12) for c in base_c),
                                 pygame.Rect(fx + 2, fy_f - 3, fw - 4, 3))
        # Ground floor entrance
        gf = fbot - fh_fl
        dw, dh = ts // 2, fh_fl - 6
        pygame.draw.rect(surf, (58, 36, 14), pygame.Rect(fx + 2, gf, fw - 4, 8))
        pygame.draw.rect(surf, (78, 50, 26),
                         pygame.Rect(fx + fw // 2 - dw // 2, gf + 10, dw, dh - 4),
                         border_radius=2)
        pygame.draw.rect(surf, (48, 28, 10),
                         pygame.Rect(fx + fw // 2 - dw // 2, gf + 10, dw, dh - 4),
                         border_radius=2, width=1)
        pygame.draw.circle(surf, (200, 160, 40), (fx + fw // 2, gf + 8), 3)

    elif style == "cafe":
        gf = fbot - fh_fl
        # Upper residential floors (above cafe) — warm lit windows
        for f in range(floors - 1):
            fy_f = ftop + f * fh_fl
            sp = fw // 3
            for wi in range(2):
                wx2 = fx + sp * (wi + 1) - ts // 4
                wh2 = fh_fl - 14
                g2 = int(145 + 50 * math.sin(t_ms / 900.0 + wi * 1.2 + f * 0.8))
                pygame.draw.rect(surf, (g2, max(0, g2 - 55), 18),
                                 pygame.Rect(wx2, fy_f + 7, ts // 2, wh2))
                pygame.draw.rect(surf, (0, 48, 26),
                                 pygame.Rect(wx2, fy_f + 7, ts // 2, wh2), 1)
                pygame.draw.line(surf, (0, 38, 18),
                                 (wx2 + ts // 4, fy_f + 7), (wx2 + ts // 4, fy_f + 7 + wh2), 1)
            # Small flower box at floor divider
            if f > 0:
                pygame.draw.rect(surf, (0, 62, 36),
                                 pygame.Rect(fx + 4, fy_f - 4, fw - 8, 4))
        # Green awning strip at ground floor
        pygame.draw.rect(surf, (0, 76, 42), pygame.Rect(fx, gf, fw, 8))
        for i in range(fw // 10):
            pygame.draw.arc(surf, (0, 54, 28),
                            pygame.Rect(fx + i * 10, gf + 4, 10, 8), 0, math.pi, 2)
        # Large storefront windows
        for wi in range(3):
            ww2 = fw // 3 - 6
            wx2 = fx + wi * (fw // 3) + 3
            wh2 = fh_fl - 14
            g2 = int(145 + 50 * math.sin(t_ms / 900.0 + wi))
            pygame.draw.rect(surf, (g2, max(0, g2 - 55), 18),
                             pygame.Rect(wx2, gf + 10, ww2, wh2))
            pygame.draw.rect(surf, (0, 48, 26),
                             pygame.Rect(wx2, gf + 10, ww2, wh2), 1)
        # Logo circle + inner ring
        pygame.draw.circle(surf, (0, 108, 58), (fx + fw // 2, gf + 4), 10)
        pygame.draw.circle(surf, (255, 248, 218), (fx + fw // 2, gf + 4), 7)
        pygame.draw.circle(surf, (0, 78, 46), (fx + fw // 2, gf + 4), 4)
        # Cornice line at top of ground floor
        pygame.draw.rect(surf, (0, 62, 36), pygame.Rect(fx, gf - 3, fw, 3))

    elif style == "market":
        gf = fbot - fh_fl
        dc = [(255, 220, 40), (40, 200, 80), (255, 120, 40), (80, 180, 255)]
        # Upper office floors (above market)
        for f in range(floors - 1):
            fy_f = ftop + f * fh_fl
            _bld_win_row(surf, fx, ftop, fw, fh_fl, f, 3, ts // 2 - 4, ts * 2 // 3,
                         (148, 188, 218))
            # Horizontal floor band
            pygame.draw.rect(surf, tuple(max(0, c - 22) for c in base_c),
                             pygame.Rect(fx, fy_f + fh_fl - 3, fw, 3))
        # Red banner at ground floor
        pygame.draw.rect(surf, (210, 38, 18), pygame.Rect(fx, gf, fw, 10))
        for i in range(fw // 14):
            pygame.draw.circle(surf, dc[i % 4], (fx + i * 14 + 7, gf + 5), 4)
        # Wide glass front
        pygame.draw.rect(surf, (158, 198, 218),
                         pygame.Rect(fx + 3, gf + 11, fw - 6, fh_fl - 14))
        pygame.draw.rect(surf, (78, 118, 138),
                         pygame.Rect(fx + 3, gf + 11, fw - 6, fh_fl - 14), 1)
        # Sliding door divider
        pygame.draw.line(surf, (78, 118, 138),
                         (fx + fw // 2, gf + 11), (fx + fw // 2, gf + fh_fl - 3), 1)
        for si in range(2):
            sx2 = fx + 6 + si * (fw // 2 - 4)
            pygame.draw.rect(surf, (98, 68, 38), pygame.Rect(sx2, gf + 20, fw // 2 - 10, 4))
            pygame.draw.rect(surf, (198, 78, 38), pygame.Rect(sx2 + 2, gf + 16, 8, 4))
            pygame.draw.rect(surf, (38, 178, 78), pygame.Rect(sx2 + 12, gf + 16, 8, 4))

    elif style == "gym":
        seg_w = fw // 3
        for f in range(floors):
            fy_f = ftop + f * fh_fl
            for s in range(3):
                g2 = int(55 + 20 * math.sin(t_ms / 600.0 + f + s))
                gl = pygame.Surface((seg_w - 3, fh_fl - 2), pygame.SRCALPHA)
                gl.fill((58 + g2, 98 + g2, 198 + g2 // 2, 85))
                surf.blit(gl, (fx + s * seg_w + 1, fy_f + 1))
                pygame.draw.rect(surf, tuple(max(0, c - 18) for c in base_c),
                                 pygame.Rect(fx + s * seg_w, fy_f, seg_w, fh_fl), 1)
            if f == floors // 2:
                mid_x = fx + fw // 2
                anim = int(5 * math.sin(t_ms / 580.0))
                pygame.draw.line(surf, (28, 48, 118),
                                 (mid_x - 12, fy_f + 8), (mid_x + 12, fy_f + 8), 3)
                pygame.draw.line(surf, (28, 48, 118),
                                 (mid_x, fy_f + 8), (mid_x, fy_f + 30 + anim), 2)
        # Logo stripe at top of ground floor
        gf = fbot - fh_fl
        pygame.draw.rect(surf, (22, 36, 80), pygame.Rect(fx + 4, gf + 4, fw - 8, 6))
        # Entrance: dark frame + double door
        pygame.draw.rect(surf, (16, 24, 56),
                         pygame.Rect(fx + fw // 2 - ts // 3, gf + 12, ts * 2 // 3, fh_fl - 14))
        pygame.draw.line(surf, (40, 60, 140),
                         (fx + fw // 2, gf + 12), (fx + fw // 2, gf + fh_fl - 2), 1)

    elif style == "bank":
        col_sp = fw // 5
        # Stone columns
        for ci in range(6):
            colx = fx + ci * col_sp
            pygame.draw.rect(surf, tuple(min(255, c + 22) for c in base_c),
                             pygame.Rect(colx, ftop, 8, fh), border_radius=2)
            pygame.draw.rect(surf, tuple(max(0, c - 18) for c in base_c),
                             pygame.Rect(colx, ftop, 8, fh), border_radius=2, width=1)
            pygame.draw.rect(surf, tuple(min(255, c + 32) for c in base_c),
                             pygame.Rect(colx - 2, ftop, 12, 8))
            pygame.draw.rect(surf, tuple(min(255, c + 32) for c in base_c),
                             pygame.Rect(colx - 2, fbot - 8, 12, 8))
        # Arched windows
        for f in range(floors - 1):
            for wi in range(2):
                wx2 = fx + col_sp * (wi * 2 + 1) + (col_sp - ts // 2) // 2
                wy2 = ftop + f * fh_fl + 6
                ww2, wh2 = ts // 2, fh_fl - 10
                g2 = int(118 + 35 * math.sin(t_ms / 1200.0 + wi * f * 0.4))
                pygame.draw.rect(surf, (g2, max(0, g2 - 22), 18),
                                 pygame.Rect(wx2, wy2, ww2, wh2), border_radius=ww2 // 2)
                pygame.draw.rect(surf, (78, 74, 58),
                                 pygame.Rect(wx2, wy2, ww2, wh2), border_radius=ww2 // 2, width=1)
        pygame.draw.rect(surf, (186, 154, 58), pygame.Rect(fx, ftop, fw, 4))
        pygame.draw.rect(surf, (186, 154, 58), pygame.Rect(fx, fbot - 4, fw, 4))
        # Entrance steps at base
        for st in range(3):
            sx2 = fx + st * 4
            pygame.draw.rect(surf, tuple(min(255, c + 14 + st * 6) for c in base_c),
                             pygame.Rect(sx2, fbot - 6 - st * 3, fw - st * 8, 3))
        # Eagle/emblem at pediment center
        mid_x = fx + fw // 2
        pygame.draw.circle(surf, (186, 154, 58), (mid_x, ftop + 8), 6)
        pygame.draw.circle(surf, tuple(min(255, c + 28) for c in base_c), (mid_x, ftop + 8), 4)
        pygame.draw.line(surf, (186, 154, 58), (mid_x - 8, ftop + 8), (mid_x + 8, ftop + 8), 2)

    elif style == "fed":
        # Stone block rows
        for i in range(0, fh, fh_fl // 2):
            pygame.draw.line(surf, tuple(min(255, c + 8) for c in base_c),
                             (fx, ftop + i), (fx + fw, ftop + i), 1)
        col_sp = fw // 4
        for ci in range(5):
            colx = fx + ci * col_sp
            pygame.draw.rect(surf, tuple(min(255, c + 14) for c in base_c),
                             pygame.Rect(colx, ftop + fh_fl, 6, fh - fh_fl * 2))
            pygame.draw.rect(surf, tuple(max(0, c - 8) for c in base_c),
                             pygame.Rect(colx, ftop + fh_fl, 6, fh - fh_fl * 2), width=1)
            # Column capitals
            pygame.draw.rect(surf, tuple(min(255, c + 20) for c in base_c),
                             pygame.Rect(colx - 3, ftop + fh_fl, 12, 5))
            pygame.draw.rect(surf, tuple(min(255, c + 20) for c in base_c),
                             pygame.Rect(colx - 3, fbot - fh_fl * 2 - 5, 12, 5))
        for f in range(1, floors - 1):
            _bld_win_row(surf, fx, ftop, fw, fh_fl, f, 3, ts // 2, ts // 2, (88, 108, 132))
        # Heavy cornice at top
        pygame.draw.rect(surf, tuple(max(0, c - 14) for c in base_c),
                         pygame.Rect(fx, ftop, fw, fh_fl // 2))
        pygame.draw.rect(surf, tuple(min(255, c + 18) for c in base_c),
                         pygame.Rect(fx, ftop + fh_fl // 2 - 3, fw, 3))
        # Entrance pediment (ground floor center)
        gf = fbot - fh_fl
        mid_x = fx + fw // 2
        ped_pts = [(mid_x - ts, gf), (mid_x + ts, gf), (mid_x, gf - ts // 2 + 4)]
        pygame.draw.polygon(surf, tuple(min(255, c + 16) for c in base_c), ped_pts)
        pygame.draw.polygon(surf, tuple(max(0, c - 10) for c in base_c), ped_pts, 1)
        # Entrance steps
        for st in range(3):
            pygame.draw.rect(surf, tuple(min(255, c + 10 + st * 5) for c in base_c),
                             pygame.Rect(fx + st * 5, fbot - 5 - st * 3, fw - st * 10, 3))

    elif style == "press":
        for f in range(floors):
            fy_f = ftop + f * fh_fl
            g2 = int(38 + 12 * math.sin(t_ms / 800.0 + f * 0.5))
            gl = pygame.Surface((fw - 2, fh_fl - 2), pygame.SRCALPHA)
            gl.fill((g2 + 18, g2 + 38, g2 + 68, 72))
            surf.blit(gl, (fx + 1, fy_f + 1))
            pygame.draw.line(surf, tuple(min(255, c + 22) for c in base_c),
                             (fx, fy_f), (fx + fw, fy_f), 2)
        for vi in range(4):
            vx = fx + vi * (fw // 3)
            pygame.draw.line(surf, tuple(min(255, c + 20) for c in base_c),
                             (vx, ftop), (vx, fbot), 1)
        # News ticker strip at ground floor
        gf = fbot - fh_fl
        pygame.draw.rect(surf, (180, 30, 20), pygame.Rect(fx, gf + fh_fl - 12, fw, 8))
        # Broadcast antenna at top center
        mid_x = fx + fw // 2
        pygame.draw.line(surf, tuple(min(255, c + 30) for c in base_c),
                         (mid_x, ftop - 1), (mid_x, ftop - ts // 3), 2)
        for aw in range(3):
            aw_y = ftop - 4 - aw * 5
            pygame.draw.line(surf, tuple(min(255, c + 20) for c in base_c),
                             (mid_x - aw * 3 - 3, aw_y), (mid_x + aw * 3 + 3, aw_y), 1)
        # Satellite dish
        pygame.draw.arc(surf, (150, 160, 180),
                        pygame.Rect(fx + fw - ts // 2 - 2, ftop + 4, ts // 2, ts // 3),
                        0, math.pi, 3)

    elif style == "wall_st":
        for f in range(floors):
            fy_f = ftop + f * fh_fl
            for vi in range(4):
                wsx = fx + vi * (fw // 4)
                refl = int(12 + 7 * math.sin(t_ms / 1000.0 + vi * 0.7 + f * 0.3))
                gl = pygame.Surface((fw // 4 - 2, fh_fl - 1), pygame.SRCALPHA)
                gl.fill((refl, refl + 4, refl + 18, 92))
                surf.blit(gl, (wsx + 1, fy_f))
                pygame.draw.line(surf, tuple(min(255, c + 12) for c in base_c),
                                 (wsx, fy_f), (wsx, fy_f + fh_fl), 1)
            pygame.draw.line(surf, tuple(min(255, c + 8) for c in base_c),
                             (fx, fy_f), (fx + fw, fy_f), 1)
        # Dark granite entrance base
        gf = fbot - fh_fl
        pygame.draw.rect(surf, tuple(max(0, c - 6) for c in base_c),
                         pygame.Rect(fx, gf, fw, fh_fl))
        # Arched entrance
        mid_x = fx + fw // 2
        ew = ts * 2 // 3
        pygame.draw.rect(surf, (6, 8, 16),
                         pygame.Rect(mid_x - ew // 2, gf + 8, ew, fh_fl - 9))
        pygame.draw.ellipse(surf, (6, 8, 16),
                            pygame.Rect(mid_x - ew // 2, gf + 4, ew, ew // 2))
        # Gold trim at entrance surround
        pygame.draw.rect(surf, (160, 138, 42),
                         pygame.Rect(mid_x - ew // 2 - 2, gf + 6, ew + 4, fh_fl - 7), 1)
        # Spire at top
        pygame.draw.line(surf, tuple(min(255, c + 22) for c in base_c),
                         (mid_x, ftop - 1), (mid_x, ftop - ts // 2), 2)
        pygame.draw.polygon(surf, (160, 138, 42),
                            [(mid_x - 4, ftop - 1), (mid_x + 4, ftop - 1), (mid_x, ftop - ts // 2 - 4)])

    elif style == "hospital":
        for f in range(floors):
            _bld_win_row(surf, fx, ftop, fw, fh_fl, f, 3, ts // 2 + 2, ts // 2 + 4,
                         (198, 218, 238))
        # Horizontal floor spandrels (blue glass bands)
        for f in range(floors):
            fy_f = ftop + f * fh_fl
            pygame.draw.rect(surf, (78, 118, 198), pygame.Rect(fx, fy_f, fw, 4))
        # Red cross emblem (white background, red cross)
        cx2, cy2 = fx + fw // 2, ftop + fh_fl + fh_fl // 2
        pygame.draw.rect(surf, (240, 240, 248), pygame.Rect(cx2 - 14, cy2 - 14, 28, 28))
        pygame.draw.rect(surf, (218, 28, 28), pygame.Rect(cx2 - 3, cy2 - 11, 6, 22))
        pygame.draw.rect(surf, (218, 28, 28), pygame.Rect(cx2 - 11, cy2 - 3, 22, 6))
        pygame.draw.rect(surf, (78, 118, 198), pygame.Rect(fx, ftop, fw, 6))
        # Ground floor entrance canopy
        gf = fbot - fh_fl
        pygame.draw.rect(surf, (78, 118, 198),
                         pygame.Rect(fx + fw // 4, gf - 5, fw // 2, 5))
        pygame.draw.line(surf, (60, 100, 180),
                         (fx + fw // 4, gf), (fx + fw // 4, gf + 8), 1)
        pygame.draw.line(surf, (60, 100, 180),
                         (fx + fw * 3 // 4, gf), (fx + fw * 3 // 4, gf + 8), 1)
        # Sliding glass doors
        mid_x = fx + fw // 2
        pygame.draw.rect(surf, (188, 218, 238),
                         pygame.Rect(mid_x - ts // 2, gf + 8, ts, fh_fl - 10))
        pygame.draw.line(surf, (78, 118, 198),
                         (mid_x, gf + 8), (mid_x, gf + fh_fl - 2), 1)

    elif style == "capitol":
        col_sp = fw // 8
        for ci in range(9):
            colx = fx + ci * col_sp
            pygame.draw.rect(surf, tuple(min(255, c + 26) for c in base_c),
                             pygame.Rect(colx, ftop + fh_fl, 8, fh - fh_fl))
            pygame.draw.rect(surf, tuple(max(0, c - 8) for c in base_c),
                             pygame.Rect(colx, ftop + fh_fl, 8, fh - fh_fl), 1)
            # Column capital + base
            pygame.draw.rect(surf, tuple(min(255, c + 32) for c in base_c),
                             pygame.Rect(colx - 2, ftop + fh_fl, 12, 6))
            pygame.draw.rect(surf, tuple(min(255, c + 32) for c in base_c),
                             pygame.Rect(colx - 2, fbot - 7, 12, 7))
        mid_x = fx + fw // 2
        ped_pts = [(fx + 4, ftop + fh_fl), (fx + fw - 4, ftop + fh_fl), (mid_x, ftop + 4)]
        pygame.draw.polygon(surf, tuple(min(255, c + 22) for c in base_c), ped_pts)
        pygame.draw.polygon(surf, tuple(max(0, c - 14) for c in base_c), ped_pts, 1)
        for si in range(3):
            pygame.draw.rect(surf, tuple(min(255, c + si * 6) for c in base_c),
                             pygame.Rect(fx + si * 5, fbot - si * 4 - 4, fw - si * 10, 4))
        for f in range(1, floors - 1):
            _bld_win_row(surf, fx, ftop, fw, fh_fl, f, 4, ts // 2, ts // 2 + 4,
                         (wg - 42, wg - 32, 48))
        # Central dome above pediment
        dome_y = ftop + 2
        dome_r = ts // 2 + 2
        pygame.draw.ellipse(surf, tuple(min(255, c + 28) for c in base_c),
                            pygame.Rect(mid_x - dome_r, dome_y - dome_r // 2, dome_r * 2, dome_r))
        pygame.draw.ellipse(surf, tuple(max(0, c - 14) for c in base_c),
                            pygame.Rect(mid_x - dome_r, dome_y - dome_r // 2, dome_r * 2, dome_r), 1)
        pygame.draw.line(surf, tuple(min(255, c + 20) for c in base_c),
                         (mid_x, dome_y - dome_r // 2), (mid_x, dome_y - dome_r // 2 - ts // 3), 2)
        # Flag (red/white/blue stripes)
        pole_top = dome_y - dome_r // 2 - ts // 3
        for fi in range(3):
            fcol = [(218, 28, 28), (240, 240, 240), (28, 60, 168)][fi]
            pygame.draw.rect(surf, fcol,
                             pygame.Rect(mid_x + 1, pole_top + fi * 4, ts // 3, 4))

    elif style == "university":
        bc = tuple(max(0, c - 12) for c in base_c)
        for i in range(0, fh, 8):
            pygame.draw.line(surf, bc, (fx, ftop + i), (fx + fw, ftop + i), 1)
        for row in range(fh // 8 + 1):
            off = (row % 2) * (ts // 2)
            for bk in range(fw // ts + 2):
                bkx = fx + bk * ts + off - ts // 2
                pygame.draw.line(surf, bc, (bkx, ftop + row * 8),
                                 (bkx, min(ftop + row * 8 + 8, fbot)), 1)
        num_w = max(2, fw // (ts + 6))
        sp = fw // (num_w + 1)
        for f in range(floors):
            wy2 = ftop + f * fh_fl + 6
            for wi in range(num_w):
                wx2 = fx + sp * (wi + 1) - ts // 4
                ww2, wh2 = ts // 2, fh_fl - 10
                pygame.draw.rect(surf, (wg - 52, wg - 32, 48),
                                 pygame.Rect(wx2, wy2, ww2, wh2), border_radius=ww2 // 2)
                pygame.draw.rect(surf, (58, 38, 18),
                                 pygame.Rect(wx2, wy2, ww2, wh2), border_radius=ww2 // 2, width=1)
        # Central tower with clock
        mid_x = fx + fw // 2
        tw = 18
        tower_top = ftop - ts * 2 // 3
        pygame.draw.rect(surf, tuple(max(0, c - 8) for c in base_c),
                         pygame.Rect(mid_x - tw // 2, tower_top, tw, ftop - tower_top + 4))
        pygame.draw.rect(surf, tuple(max(0, c - 22) for c in base_c),
                         pygame.Rect(mid_x - tw // 2, tower_top, tw, ftop - tower_top + 4), width=1)
        # Clock face on tower
        clock_y = tower_top + (ftop - tower_top) // 2
        pygame.draw.circle(surf, (245, 238, 210), (mid_x, clock_y), 6)
        pygame.draw.circle(surf, (80, 60, 28), (mid_x, clock_y), 6, 1)
        hr_a = (t_ms / 3600000.0) * 2 * math.pi
        mn_a = (t_ms / 60000.0) * 2 * math.pi
        pygame.draw.line(surf, (60, 40, 14),
                         (mid_x, clock_y),
                         (mid_x + int(3 * math.sin(hr_a)), clock_y - int(3 * math.cos(hr_a))), 2)
        pygame.draw.line(surf, (60, 40, 14),
                         (mid_x, clock_y),
                         (mid_x + int(5 * math.sin(mn_a)), clock_y - int(5 * math.cos(mn_a))), 1)
        # Entrance arch at ground floor
        gf = fbot - fh_fl
        aw = ts * 2 // 3
        pygame.draw.rect(surf, tuple(max(0, c - 18) for c in base_c),
                         pygame.Rect(mid_x - aw // 2, gf + 6, aw, fh_fl - 7))
        pygame.draw.ellipse(surf, tuple(max(0, c - 18) for c in base_c),
                            pygame.Rect(mid_x - aw // 2, gf + 2, aw, aw // 2))
        pygame.draw.ellipse(surf, tuple(max(0, c - 30) for c in base_c),
                            pygame.Rect(mid_x - aw // 2, gf + 2, aw, aw // 2), 1)
        pygame.draw.rect(surf, tuple(max(0, c - 30) for c in base_c),
                         pygame.Rect(mid_x - aw // 2, gf + 6, aw, fh_fl - 7), 1)


def _draw_building_facades(surf, cx, cy, ts, t_ms):
    """Draw 2.5D building sprites over the tile grid."""
    old_clip = surf.get_clip()
    ddx = ts // 3   # depth: rightward
    ddy = ts // 3   # depth: upward (will subtract in y)

    for (x0, y0, x1, y1, floors, fc, sc, rc, style) in _BLD_2D5:
        fw = (x1 - x0 + 1) * ts
        fh = floors * ts
        fx = x0 * ts - int(cx)
        fbot = (y1 + 1) * ts - int(cy)
        ftop = fbot - fh

        if fx + fw + ddx < 0 or fx > config.SCREEN_W:
            continue

        # Clip to building x-range (allow full y for height extension)
        surf.set_clip(pygame.Rect(fx, 0, fw + ddx + 2, config.SCREEN_H))

        # Cover exposed tile rows above facade (upper-building setback)
        ftop_tile = y0 * ts - int(cy)
        if ftop_tile < ftop:
            uc = tuple(max(0, c - 28) for c in fc)
            us = tuple(max(0, c - 14) for c in sc)
            ur = tuple(max(0, c - 8) for c in rc)
            pygame.draw.rect(surf, uc, pygame.Rect(fx, ftop_tile, fw, ftop - ftop_tile))
            pygame.draw.polygon(surf, us, [
                (fx + fw, ftop_tile), (fx + fw + ddx, ftop_tile - ddy),
                (fx + fw + ddx, ftop - ddy), (fx + fw, ftop),
            ])
            pygame.draw.polygon(surf, ur, [
                (fx, ftop_tile), (fx + fw, ftop_tile),
                (fx + fw + ddx, ftop_tile - ddy), (fx + ddx, ftop_tile - ddy),
            ])
            pygame.draw.polygon(surf, tuple(max(0, c - 22) for c in rc), [
                (fx, ftop_tile), (fx + fw, ftop_tile),
                (fx + fw + ddx, ftop_tile - ddy), (fx + ddx, ftop_tile - ddy),
            ], 1)

        # 1. Right side face (east, slightly darker)
        side_pts = [
            (fx + fw,        ftop),
            (fx + fw + ddx,  ftop - ddy),
            (fx + fw + ddx,  fbot - ddy),
            (fx + fw,        fbot),
        ]
        pygame.draw.polygon(surf, sc, side_pts)
        for fi in range(1, floors):
            ry = ftop + fi * ts
            pygame.draw.line(surf, tuple(max(0, c - 12) for c in sc),
                             (fx + fw, ry), (fx + fw + ddx, ry - ddy), 1)

        # 2. Front face
        pygame.draw.rect(surf, fc, pygame.Rect(fx, ftop, fw, fh))
        for fi in range(1, floors):
            fy_div = ftop + fi * ts
            pygame.draw.line(surf, tuple(max(0, c - 20) for c in fc),
                             (fx, fy_div), (fx + fw, fy_div), 1)
        pygame.draw.rect(surf, tuple(max(0, c - 32) for c in fc),
                         pygame.Rect(fx, ftop, fw, fh), 1)

        # 3. Roof top face (lighter, parallelogram)
        roof_pts = [
            (fx,             ftop),
            (fx + fw,        ftop),
            (fx + fw + ddx,  ftop - ddy),
            (fx + ddx,       ftop - ddy),
        ]
        pygame.draw.polygon(surf, rc, roof_pts)
        pygame.draw.polygon(surf, tuple(max(0, c - 16) for c in rc), roof_pts, 1)

        # 4. Style-specific facade details
        _bld_details(surf, fx, ftop, fw, fh, floors, fbot, style, fc, ts, t_ms)

    surf.set_clip(old_clip)


def _decorate(surf, sx, sy, ts, tile, tx, ty, fnt_s, economy):
    h = (tx * 2654435761 + ty * 2246822519) & 0xFFFF
    t_ms = pygame.time.get_ticks()

    if tile == W:
        pygame.draw.line(surf, (48, 40, 60), (sx, sy+ts//2), (sx+ts, sy+ts//2), 1)
        pygame.draw.line(surf, (48, 40, 60), (sx+ts//2, sy), (sx+ts//2, sy+ts), 1)
    elif tile == G:
        # Grass variation tufts
        for i in range(4):
            gx = sx + ((h + i * 41) % (ts - 6)) + 3
            gy = sy + ((h + i * 67) % (ts - 6)) + 3
            v = ((h + i * 29) % 24) - 12
            gc = (max(38, min(90, 48 + v)), max(110, min(185, 148 + v)), max(38, min(75, 52 + v)))
            pygame.draw.circle(surf, gc, (gx, gy), 2)
    elif tile == R:
        # Center lane markings: vertical road cols (24, 50) vs horizontal
        is_v_road = tx in (24, 50)
        if is_v_road:
            if ty % 4 < 2:
                pygame.draw.rect(surf, (212, 202, 50),
                                 pygame.Rect(sx + ts//2 - 1, sy + 4, 3, ts - 8))
        else:
            if tx % 4 < 2:
                pygame.draw.rect(surf, (212, 202, 50),
                                 pygame.Rect(sx + 4, sy + ts//2 - 1, ts - 8, 3))
        # Asphalt grain
        for i in range(2):
            ax = sx + ((h + i * 53) % (ts - 2)) + 1
            ay = sy + ((h + i * 71) % (ts - 2)) + 1
            pygame.draw.circle(surf, (38, 40, 50), (ax, ay), 1)
    elif tile == S:
        # Sidewalk stone joint lines
        mid = ts // 2
        pygame.draw.line(surf, (132, 124, 112), (sx + mid, sy + 2), (sx + mid, sy + ts - 2), 1)
        pygame.draw.line(surf, (132, 124, 112), (sx + 2, sy + mid), (sx + ts - 2, sy + mid), 1)
    elif tile == WD:
        # Wood grain lines
        for i in range(3):
            gy = sy + (i * ts // 3 + (ty * 7 + tx * 3) % (ts // 3))
            pygame.draw.line(surf, (155, 112, 72), (sx, gy), (sx + ts, gy), 1)
        pygame.draw.line(surf, (162, 120, 78), (sx, sy + ts - 1), (sx + ts, sy + ts - 1), 1)
    elif tile == TI:
        # Grout lines
        pygame.draw.line(surf, (178, 178, 185), (sx, sy + ts//2), (sx + ts, sy + ts//2), 1)
        pygame.draw.line(surf, (178, 178, 185), (sx + ts//2, sy), (sx + ts//2, sy + ts), 1)
    elif tile == MR:
        # Marble veining
        vx1 = sx + (h % (ts // 2))
        vy2 = sy + ((h >> 4) % ts)
        pygame.draw.line(surf, (205, 200, 192), (vx1, sy), (sx + ts, vy2), 1)
        vx2 = sx + ((h >> 8) % (ts // 2)) + ts // 2
        pygame.draw.line(surf, (210, 205, 198), (sx, sy + (h >> 12) % ts), (vx2, sy + ts), 1)
    elif tile == DR:
        pygame.draw.rect(surf, (148, 108, 52), pygame.Rect(sx+6, sy+4, ts-12, ts-8), border_radius=4)
        hw = (ts - 16) // 2
        pygame.draw.rect(surf, (120, 85, 38), pygame.Rect(sx+8, sy+6, hw-1, (ts-14)//2), border_radius=2)
        pygame.draw.rect(surf, (120, 85, 38), pygame.Rect(sx+8+hw+1, sy+6, hw-1, (ts-14)//2), border_radius=2)
        pygame.draw.circle(surf, (255, 220, 80), (sx + ts - 14, sy + ts//2), 3)
    elif tile == T:
        pygame.draw.rect(surf, config.TERMINAL_BG, pygame.Rect(sx+4, sy+4, ts-9, ts-9), border_radius=3)
        pygame.draw.rect(surf, config.TERMINAL_GREEN, pygame.Rect(sx+4, sy+4, ts-9, ts-9), border_radius=3, width=1)
        t_surf = fnt_s.render("PC", True, config.TERMINAL_GREEN)
        surf.blit(t_surf, (sx + (ts - t_surf.get_width())//2, sy + (ts - t_surf.get_height())//2))
    elif tile == B:
        pygame.draw.rect(surf, (72, 112, 182), pygame.Rect(sx+2, sy+2, ts-5, ts-5), border_radius=5)
        pygame.draw.rect(surf, (205, 210, 225), pygame.Rect(sx+3, sy+3, ts-7, 12))
        pygame.draw.ellipse(surf, (235, 238, 255), pygame.Rect(sx+5, sy+4, 20, 10))
    elif tile == TR:
        # Layered foliage + trunk shadow
        pygame.draw.ellipse(surf, (25, 25, 28), pygame.Rect(sx + ts//2 - 10, sy + ts - 9, 20, 7))
        pygame.draw.rect(surf, (72, 48, 24), pygame.Rect(sx+ts//2-3, sy+ts-18, 6, 18))
        pygame.draw.circle(surf, (32, 95, 40), (sx+ts//2, sy+ts//2-2), ts//2-3)
        pygame.draw.circle(surf, (42, 118, 52), (sx+ts//2-3, sy+ts//2-6), ts//2-9)
        pygame.draw.circle(surf, (55, 138, 65), (sx+ts//2+2, sy+ts//2-9), ts//2-14)
        pygame.draw.circle(surf, (72, 162, 80), (sx+ts//2-4, sy+ts//2-10), 5)
    elif tile == FT:
        anim = t_ms / 700.0
        pygame.draw.circle(surf, (52, 130, 178), (sx+ts//2, sy+ts//2), ts//2-3)
        pygame.draw.circle(surf, (190, 228, 252), (sx+ts//2, sy+ts//2), ts//4)
        for ri in range(3):
            rr = int(((anim + ri * 0.9) % 2.7) / 2.7 * (ts//2 - 2))
            if 2 < rr < ts//2:
                pygame.draw.circle(surf, (168, 215, 245), (sx+ts//2, sy+ts//2), rr, 1)
        jet = int(4 + math.sin(anim * 3) * 2)
        pygame.draw.line(surf, (205, 238, 255), (sx+ts//2, sy+ts//2-2), (sx+ts//2, sy+ts//2-jet-4), 2)
    elif tile == BN:
        pygame.draw.rect(surf, (115, 74, 52), pygame.Rect(sx+4, sy+ts//2, ts-8, 10), border_radius=2)
        pygame.draw.rect(surf, (88, 55, 38), pygame.Rect(sx+6, sy+ts//2+10, 4, 8))
        pygame.draw.rect(surf, (88, 55, 38), pygame.Rect(sx+ts-10, sy+ts//2+10, 4, 8))
        pygame.draw.rect(surf, (130, 90, 62), pygame.Rect(sx+4, sy+ts//2-4, ts-8, 5))
    elif tile == LP:
        anim = t_ms / 900.0
        pygame.draw.rect(surf, (58, 58, 72), pygame.Rect(sx+ts//2-2, sy+4, 4, ts-8))
        # Cross bar
        pygame.draw.rect(surf, (65, 65, 80), pygame.Rect(sx+ts//2-8, sy+6, 16, 3))
        # Pulsing glow rings
        glow_r = 12 + int(math.sin(anim * 2.2) * 3)
        pygame.draw.circle(surf, (255, 235, 140), (sx+ts//2, sy+6), glow_r)
        pygame.draw.circle(surf, (255, 248, 190), (sx+ts//2, sy+6), 6)
        pygame.draw.circle(surf, (255, 255, 220), (sx+ts//2, sy+6), 3)
    elif tile == SH:
        pygame.draw.rect(surf, (160, 130, 90), pygame.Rect(sx+2, sy+2, ts-5, ts-5))
        for ly in range(sy+8, sy+ts-4, 8):
            pygame.draw.line(surf, (100, 70, 38), (sx+4, ly), (sx+ts-6, ly), 1)
            pygame.draw.circle(surf, (220, 72, 72), (sx+10, ly-3), 2)
            pygame.draw.circle(surf, (72, 220, 72), (sx+22, ly-3), 2)
            pygame.draw.circle(surf, (220, 220, 72), (sx+34, ly-3), 2)
    elif tile == PD:
        pygame.draw.rect(surf, (142, 102, 62), pygame.Rect(sx+6, sy+8, ts-12, ts-12), border_radius=3)
        pygame.draw.line(surf, (58, 38, 18), (sx+ts//2, sy+8), (sx+ts//2, sy+ts-8), 2)
        pygame.draw.circle(surf, (58, 58, 70), (sx+ts//2, sy+ts//2-2), 3)
    elif tile == CF:
        pygame.draw.rect(surf, (52, 34, 24), pygame.Rect(sx+6, sy+4, ts-12, ts-8), border_radius=2)
        pygame.draw.circle(surf, (205, 52, 52), (sx+ts//2, sy+ts//2), 3)
        anim = t_ms / 320.0
        for i in range(3):
            off = (anim + i * 0.85) % 2.5
            oy = int(off * 6)
            brightness = max(80, 220 - int(off * 80))
            pygame.draw.circle(surf, (brightness, brightness, brightness),
                               (sx + ts//2 - 5 + i*5, sy + 3 - oy), 3)
    elif tile == TV:
        pygame.draw.rect(surf, (28, 28, 38), pygame.Rect(sx+2, sy+4, ts-5, ts-12), border_radius=2)
        sc_cols = [(55, 115, 178), (118, 55, 55), (55, 118, 62), (118, 118, 55)]
        sc = sc_cols[(t_ms // 3000) % 4]
        pygame.draw.rect(surf, sc, pygame.Rect(sx+5, sy+7, ts-11, ts-18))
        scan = (t_ms // 55) % (ts - 20)
        pygame.draw.line(surf, (255, 255, 255), (sx+5, sy+7+scan), (sx+ts-6, sy+7+scan), 1)
    elif tile == SK:
        pygame.draw.rect(surf, (202, 202, 212), pygame.Rect(sx+2, sy+2, ts-5, ts-5), border_radius=2)
        pygame.draw.line(surf, (98, 98, 118), (sx+ts//2, sy+4), (sx+ts//2, sy+ts-4), 1)
        pygame.draw.rect(surf, (148, 148, 158), pygame.Rect(sx+ts//2-4, sy+5, 8, 4))
    elif tile == CH:
        pygame.draw.rect(surf, (130, 90, 60), pygame.Rect(sx+8, sy+8, ts-16, ts-16), border_radius=3)
        pygame.draw.rect(surf, (90, 60, 38), pygame.Rect(sx+8, sy+6, ts-16, 4))
    elif tile == TB:
        pygame.draw.rect(surf, (155, 110, 70), pygame.Rect(sx+2, sy+2, ts-5, ts-5), border_radius=3)
        pygame.draw.rect(surf, (112, 76, 46), pygame.Rect(sx+2, sy+ts-12, ts-5, 6))
        if h % 5 == 0:
            pygame.draw.circle(surf, (178, 138, 98), (sx+ts//2, sy+ts//2), 5)
            pygame.draw.circle(surf, (118, 78, 58), (sx+ts//2, sy+ts//2), 3)
    elif tile == BK:
        pygame.draw.rect(surf, (108, 70, 40), pygame.Rect(sx+2, sy+2, ts-5, ts-5))
        for ly in range(sy+6, sy+ts-4, 8):
            pygame.draw.rect(surf, (178, 55, 55), pygame.Rect(sx+5,  ly, 8, 6))
            pygame.draw.rect(surf, (55, 178, 55), pygame.Rect(sx+14, ly, 8, 6))
            pygame.draw.rect(surf, (55, 55, 178), pygame.Rect(sx+23, ly, 8, 6))
            pygame.draw.rect(surf, (178, 178, 55), pygame.Rect(sx+32, ly, 8, 6))
    elif tile == RG:
        pygame.draw.rect(surf, (170, 65, 88), pygame.Rect(sx, sy, ts, ts))
        pygame.draw.line(surf, (128, 48, 68), (sx, sy+ts//2), (sx+ts, sy+ts//2), 1)
        pygame.draw.rect(surf, (198, 95, 118), pygame.Rect(sx+3, sy+3, ts-6, ts-6), width=2)
    elif tile == WIN:
        pygame.draw.rect(surf, (132, 180, 208), pygame.Rect(sx+2, sy+8, ts-5, ts-20))
        pygame.draw.line(surf, (88, 128, 160), (sx+ts//2, sy+8), (sx+ts//2, sy+ts-12), 2)
        pygame.draw.line(surf, (88, 128, 160), (sx+2, sy+(ts-20)//2+8), (sx+ts-3, sy+(ts-20)//2+8), 2)
        pygame.draw.line(surf, (205, 235, 255), (sx+5, sy+10), (sx+12, sy+18), 1)
    elif tile == CR:
        for stripe_y in range(sy+4, sy+ts, 8):
            pygame.draw.rect(surf, (215, 215, 218), pygame.Rect(sx+4, stripe_y, ts-8, 4))
    elif tile == TM:
        pygame.draw.rect(surf, (55, 55, 68), pygame.Rect(sx+4, sy+8, ts-9, ts-16), border_radius=2)
        pygame.draw.rect(surf, (28, 28, 38), pygame.Rect(sx+6, sy+10, ts-13, ts-20))
        belt = (t_ms // 55) % max(1, ts - 22)
        pygame.draw.line(surf, (48, 48, 60), (sx+6, sy+10+belt), (sx+ts-7, sy+10+belt), 1)
    elif tile == CN:
        pygame.draw.rect(surf, (232, 222, 202), pygame.Rect(sx+ts//4, sy, ts//2, ts))
        pygame.draw.rect(surf, (198, 188, 168), pygame.Rect(sx+ts//4, sy+2, ts//2, 6))
        pygame.draw.rect(surf, (198, 188, 168), pygame.Rect(sx+ts//4, sy+ts-8, ts//2, 6))
        pygame.draw.line(surf, (208, 198, 178), (sx+ts//4+4, sy+8), (sx+ts//4+4, sy+ts-8), 1)
        pygame.draw.line(surf, (208, 198, 178), (sx+ts//4+9, sy+8), (sx+ts//4+9, sy+ts-8), 1)
    elif tile == SC:
        pygame.draw.rect(surf, (26, 56, 104), pygame.Rect(sx+2, sy+4, ts-5, ts-8), border_radius=2)
        pygame.draw.rect(surf, (38, 88, 142), pygame.Rect(sx+4, sy+6, ts-9, ts-12), 1)
        line_col = [(0, 255, 100), (255, 180, 0), (255, 60, 60), (60, 180, 255)][(t_ms // 2000) % 4]
        for i in range(3):
            pygame.draw.line(surf, line_col, (sx+8, sy+12+i*8),
                             (sx+ts-10+((t_ms//2000+i) % 3)*4, sy+12+i*8), 1)
    elif tile == PG:
        anim_bob = [0, 1, 0, -1][(t_ms // 700) % 4]
        pygame.draw.ellipse(surf, (192, 186, 198), pygame.Rect(sx+10, sy+ts-16+anim_bob, 14, 8))
        pygame.draw.circle(surf, (178, 172, 185), (sx+10, sy+ts-14+anim_bob), 4)
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
        pygame.draw.rect(surf, (128, 128, 140), pygame.Rect(sx+2, sy+ts//3, ts-5, 4))
        pygame.draw.rect(surf, (128, 128, 140), pygame.Rect(sx+2, sy+2*ts//3, ts-5, 4))
        for px_f in range(sx+4, sx+ts-4, 9):
            pygame.draw.rect(surf, (118, 118, 130), pygame.Rect(px_f, sy+4, 4, ts-8))
    elif tile == CB:
        # ATM machine — steel casing, screen, keypad, card/cash slots
        # Steel outer casing
        pygame.draw.rect(surf, (148, 152, 162), pygame.Rect(sx+3, sy+2, ts-6, ts-4), border_radius=2)
        pygame.draw.rect(surf, (100, 104, 114), pygame.Rect(sx+3, sy+2, ts-6, ts-4), border_radius=2, width=1)
        # Bank logo bar (blue)
        pygame.draw.rect(surf, (20, 50, 158), pygame.Rect(sx+5, sy+4, ts-10, 7))
        # Screen with animated blue-grey glow
        sg = int(38 + 22 * math.sin(t_ms / 780.0))
        pygame.draw.rect(surf, (sg, sg + 14, sg + 38), pygame.Rect(sx+5, sy+12, ts-10, 13))
        pygame.draw.rect(surf, (72, 78, 98), pygame.Rect(sx+5, sy+12, ts-10, 13), width=1)
        # Green "online" indicator dot
        pygame.draw.circle(surf, (0, 212, 72), (sx + ts - 8, sy + 5), 2)
        # Card slot (dark horizontal slit beside screen)
        pygame.draw.rect(surf, (52, 56, 66), pygame.Rect(sx + ts - 14, sy + 14, 8, 2))
        # 3×3 keypad grid
        for row in range(3):
            for col in range(3):
                kx = sx + 7 + col * 8
                ky = sy + 28 + row * 6
                pygame.draw.rect(surf, (118, 122, 132), pygame.Rect(kx, ky, 6, 4), border_radius=1)
        # Function keys (two side buttons beside screen)
        pygame.draw.rect(surf, (90, 94, 104), pygame.Rect(sx+3, sy+14, 3, 5))
        pygame.draw.rect(surf, (90, 94, 104), pygame.Rect(sx+3, sy+20, 3, 5))
        # Cash dispenser slot at bottom
        pygame.draw.rect(surf, (52, 56, 66), pygame.Rect(sx+6, sy+ts-7, ts-13, 3))
    elif tile == RP:
        pygame.draw.rect(surf, (148, 28, 38), pygame.Rect(sx, sy, ts, ts))
        pygame.draw.line(surf, (88, 18, 28), (sx, sy+ts-1), (sx+ts, sy+ts-1), 2)
        pygame.draw.rect(surf, (165, 42, 52), pygame.Rect(sx+3, sy+3, ts-6, ts-6), width=1)
    elif tile == SG:
        pygame.draw.rect(surf, (210, 188, 55), pygame.Rect(sx+4, sy+8, ts-9, ts-16), border_radius=2)
        pygame.draw.rect(surf, (178, 158, 42), pygame.Rect(sx+4, sy+8, ts-9, ts-16), border_radius=2, width=1)
        pygame.draw.rect(surf, (98, 88, 65), pygame.Rect(sx+ts//2-2, sy+ts-10, 4, 10))
    elif tile == GW:
        # Graffiti wall — colourful spray-painted tags on concrete
        pygame.draw.rect(surf, (78, 74, 88), pygame.Rect(sx, sy, ts, ts))
        # Horizontal concrete block lines
        pygame.draw.line(surf, (92, 88, 104), (sx, sy+ts//3), (sx+ts, sy+ts//3), 1)
        pygame.draw.line(surf, (92, 88, 104), (sx, sy+2*ts//3), (sx+ts, sy+2*ts//3), 1)
        pygame.draw.line(surf, (92, 88, 104), (sx+ts//2, sy), (sx+ts//2, sy+ts), 1)
        # Graffiti colour patches (deterministic from tile hash)
        graffiti_cols = [
            (255, 60, 80), (255, 200, 40), (40, 210, 100),
            (80, 160, 255), (220, 80, 255), (255, 140, 40),
        ]
        for i in range(4):
            gc = graffiti_cols[(h + i * 7) % len(graffiti_cols)]
            gx2 = sx + ((h + i * 41) % (ts - 12)) + 4
            gy2 = sy + ((h + i * 67) % (ts - 10)) + 4
            gw2 = 8 + (h + i * 29) % 12
            gh2 = 5 + (h + i * 53) % 8
            pygame.draw.rect(surf, gc, pygame.Rect(gx2, gy2, gw2, gh2))
        # Thin tag lines over the blocks
        for i in range(3):
            lc = graffiti_cols[(h + i * 13 + 2) % len(graffiti_cols)]
            lx1 = sx + ((h + i * 23) % (ts - 8)) + 2
            ly1 = sy + ((h + i * 37) % (ts - 6)) + 3
            lx2 = lx1 + ((h + i * 19) % 20) - 10
            ly2 = ly1 + ((h + i * 31) % 14) - 7
            pygame.draw.line(surf, lc, (lx1, ly1), (lx2, ly2), 2)
