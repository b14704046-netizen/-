"""Scenes - city overworld + all building interiors."""
import pygame
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

SOLID = {W, D, B, FT, BN, LP, SH, PD, CF, TV, SK, CH, TB, BK, TR, FN, CN, CB, TM, SG, SC}

TILE_COLOR = {
    F:   (175, 155, 135),
    W:   (72,  62,  82),
    R:   (50,  50,  60),
    G:   (60,  140, 60),
    D:   (145, 105, 65),
    T:   (15,  75,  115),
    B:   (95,  135, 195),
    S:   (145, 135, 125),
    C:   (140, 90,  110),
    DR:  (180, 130, 70),
    TR:  (40,  100, 50),
    FT:  (90,  170, 200),
    BN:  (110, 70,  50),
    LP:  (90,  90,  100),
    SH:  (160, 130, 90),
    PD:  (140, 100, 60),
    CF:  (60,  40,  30),
    TV:  (40,  40,  50),
    SK:  (200, 200, 210),
    CH:  (130, 90,  60),
    TB:  (155, 110, 70),
    PG:  (200, 200, 150),
    FL:  (90,  160, 90),
    WD:  (175, 130, 90),
    TI:  (200, 200, 200),
    ST:  (130, 130, 140),
    BK:  (110, 70,  40),
    RG:  (170, 70,  90),
    TR2: (140, 100, 60),
    WIN: (140, 180, 200),
    CR:  (220, 220, 220),
    PV:  (170, 160, 150),
    CB:  (130, 110, 80),
    TM:  (60,  60,  70),
    SG:  (200, 180, 60),
    FN:  (130, 130, 140),
    CN:  (230, 220, 200),
    MR:  (220, 220, 210),
    RP:  (140, 30,  40),
    SC:  (30,  60,  100),
}


def _row(*cells):
    return list(cells)


# ── City Overworld Map ────────────────────────────────────────────────
# 50 columns × 35 rows. Has multiple buildings with doors.
def _build_city():
    """Build city as a list of lists, then place doors/buildings."""
    cols, rows = 50, 35
    m = [[G for _ in range(cols)] for _ in range(rows)]

    # Main horizontal roads (rows 8-10, 24-26)
    for y in [8, 9, 10]:
        for x in range(cols):
            m[y][x] = R if y == 9 else S
    for y in [24, 25, 26]:
        for x in range(cols):
            m[y][x] = R if y == 25 else S

    # Main vertical road (cols 23-25)
    for x in [23, 24, 25]:
        for y in range(rows):
            m[y][x] = R if x == 24 else S

    # Crosswalks at intersections
    for y in [8, 10, 24, 26]:
        for x in [23, 25]:
            m[y][x] = CR

    # Building plots — each has walls + door tile
    # Format: (x0, y0, x1, y1, door_x, door_y, scene_name)
    buildings = [
        # Top half (rows 0-7)
        (1,  1,  10, 7,  5,  7,  config.SCENE_APARTMENT),  # Powell's apartment
        (12, 1,  21, 7,  16, 7,  config.SCENE_CAFE),       # Coffee shop
        (27, 1,  36, 7,  31, 7,  config.SCENE_SUPERMARKET),# Supermarket
        (38, 1,  48, 7,  43, 7,  config.SCENE_GYM),        # Gym

        # Middle (rows 11-23) — between two roads, includes park
        (1,  11, 10, 23, 5,  23, config.SCENE_FED),        # Fed building
        (12, 11, 21, 23, 16, 23, config.SCENE_PRESS),      # Press room
        # Park (no building, just trees)
        (38, 11, 48, 23, 43, 23, config.SCENE_WALL_ST),    # Wall Street

        # Bottom (rows 27-34)
        (15, 27, 32, 34, 23, 27, config.SCENE_CAPITOL),    # Capitol
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
            if m[y0][x] == W: m[y0][x] = WIN
        # Interior floor
        for y in range(y0+1, y1):
            for x in range(x0+1, x1):
                m[y][x] = WD if y < 8 else TI
        # Door
        m[dy][dx] = DR

    # Park area in middle (around 27-36, 11-23)
    for y in range(12, 23):
        for x in range(27, 37):
            m[y][x] = G
    # Trees in park
    for tx, ty in [(28,13), (30,12), (33,12), (35,13), (28,16), (35,16),
                    (28,20), (30,21), (33,21), (35,20), (31,16), (32,18)]:
        m[ty][tx] = TR
    # Fountain
    m[17][31] = FT
    m[17][32] = FT
    m[18][31] = FT
    m[18][32] = FT
    # Benches
    m[15][29] = BN
    m[15][34] = BN
    m[20][29] = BN
    m[20][34] = BN
    # Pigeon spots
    m[16][30] = PG
    m[19][33] = PG
    m[14][32] = PG

    # Trees/flowers on grass borders
    for x in range(0, cols):
        for y in range(0, rows):
            if m[y][x] == G:
                if random.random() < 0.05 and not (27 <= x <= 36 and 11 <= y <= 23):
                    m[y][x] = TR
                elif random.random() < 0.06:
                    m[y][x] = FL

    # Lampposts along road
    for x in range(2, cols, 6):
        if m[7][x] == S: m[7][x] = LP
        if m[11][x] == S: m[11][x] = LP
        if m[23][x] == S: m[23][x] = LP
        if m[27][x] == S: m[27][x] = LP

    # Sign markers near doors
    signs = {
        (4, 7):  "🏠 公寓",
        (15, 7): "☕ 咖啡廳",
        (30, 7): "🛒 超市",
        (42, 7): "💪 健身房",
        (4, 23): "🏛 聯準會",
        (15, 23):"📰 新聞室",
        (42, 23):"📈 華爾街",
        (22, 27):"🏛 國會",
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
    m[3][10] = CH; m[3][11] = CH; m[3][12] = CH
    # Coffee table
    m[5][11] = TB
    # Kitchen
    m[2][16] = SK; m[2][17] = CF
    m[3][16] = TB; m[3][17] = TB
    # Bookshelf
    m[2][6] = BK; m[2][7] = BK
    # Rug
    for x in range(9, 14):
        for y in range(7, 11):
            m[y][x] = RG
    # Window walls
    m[0][5] = WIN; m[0][10] = WIN; m[0][15] = WIN

    npcs = []
    doors = [{"x": 10, "y": 13, "target": config.SCENE_CITY, "spawn_tx": 5, "spawn_ty": 8}]
    objects = [
        {"x": 2, "y": 2, "type": "bed",    "label": "床（睡覺跳過時間）"},
        {"x": 17, "y": 2, "type": "coffee","label": "咖啡機（手沖小遊戲）"},
        {"x": 11, "y": 2, "type": "tv",    "label": "電視（看新聞）"},
        {"x": 6, "y": 2, "type": "books",  "label": "書架（讀經濟學）"},
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
    # Window
    m[0][4] = WIN; m[0][9] = WIN; m[0][13] = WIN

    npcs = [
        NPC(6, 4, "barista", "店員Anna", "cafe_barista", 0),
        NPC(4, 7, "citizen", "上班族",     "cafe_customer1", 0),
        NPC(12, 7, "citizen", "學生",      "cafe_customer2", 0),
    ]
    doors = [{"x": 9, "y": 11, "target": config.SCENE_CITY, "spawn_tx": 16, "spawn_ty": 8}]
    objects = [
        {"x": 5, "y": 2, "type": "coffee_mg", "label": "鷹派咖啡（小遊戲）"},
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
        NPC(8, 4, "guard",     "守衛",         "fed_guard", 2),
        NPC(15, 4, "secretary","秘書 Jane",    "fed_secretary", 0),
        NPC(12, 8, "politician","副主席 Brain","fed_vicechair", 0),
    ]
    doors = [{"x": 11, "y": 13, "target": config.SCENE_CITY, "spawn_tx": 5, "spawn_ty": 24}]
    objects = [
        {"x": 4, "y": 2, "type": "terminal", "label": "主控終端（經濟模擬器）"},
        {"x": 10, "y": 2, "type": "terminal", "label": "副控終端"},
        {"x": 18, "y": 2, "type": "terminal", "label": "資料終端"},
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
        NPC(3, 5, "citizen", "教練 Mike",   "gym_coach", 0),
        NPC(10, 6, "citizen", "健身愛好者",  "gym_member", 0),
    ]
    doors = [{"x": 8, "y": 10, "target": config.SCENE_CITY, "spawn_tx": 43, "spawn_ty": 8}]
    objects = [
        {"x": 6, "y": 3, "type": "treadmill_mg", "label": "中性利率跑步機（節奏小遊戲）"},
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
    # Bull statue
    m[9][3] = CB
    npcs = [
        NPC(4, 4, "trader", "多頭交易員",     "ws_bull", 0),
        NPC(7, 4, "trader", "空頭交易員",     "ws_bear", 0),
        NPC(10, 4, "trader","量化基金經理",   "ws_quant", 0),
        NPC(13, 4, "trader","債券交易員",     "ws_bond", 0),
        NPC(5, 8, "trader", "新進分析師",     "ws_analyst", 0),
    ]
    doors = [{"x": 9, "y": 11, "target": config.SCENE_CITY, "spawn_tx": 43, "spawn_ty": 24}]
    objects = [
        {"x": 9, "y": 8, "type": "ticker", "label": "看即時報價"},
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

    npcs = [
        NPC(7, 5, "elder",  "公園老伯",   "park_elder", 0),
        NPC(15, 5, "child", "小孩",       "park_kid", 1),
        NPC(20, 11, "citizen", "慢跑者",  "park_jogger", 2),
    ]
    doors = [{"x": 12, "y": 15, "target": config.SCENE_CITY, "spawn_tx": 31, "spawn_ty": 15}]
    objects = [
        {"x": 11, "y": 9, "type": "pigeon_mg", "label": "餵鴿子（紓壓小遊戲）"},
    ]
    return m, npcs, doors, objects, (12, 14)


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
    park_door = {"x": 31, "y": 14, "target": config.SCENE_PARK, "spawn_tx": 12, "spawn_ty": 14}
    city_doors = [park_door]
    for x0, y0, x1, y1, dx, dy, target in CITY_BUILDINGS:
        spawn = {
            config.SCENE_APARTMENT: (10, 12), config.SCENE_CAFE: (9, 10),
            config.SCENE_SUPERMARKET: (10, 11), config.SCENE_GYM: (8, 9),
            config.SCENE_FED: (11, 12), config.SCENE_PRESS: (9, 10),
            config.SCENE_WALL_ST: (9, 10), config.SCENE_CAPITOL: (11, 12),
        }[target]
        city_doors.append({"x": dx, "y": dy, "target": target,
                            "spawn_tx": spawn[0], "spawn_ty": spawn[1]})
    city_npcs = [
        NPC(15, 9,  "citizen",  "路人甲",   "street_citizen_1", 3),
        NPC(30, 9,  "journalist","記者",    "street_journalist", 2),
        NPC(20, 25, "protester", "抗議者",  "street_protester", 1),
        NPC(35, 25, "citizen",   "上班族",  "street_citizen_2", 3),
        NPC(8, 25,  "unemployed","失業者",  "street_unemployed", 1),
        NPC(24, 12, "child",     "小朋友",  "street_child", 2),
        NPC(40, 12, "elder",     "退休者",  "street_elder", 0),
        NPC(45, 30, "citizen",   "夜班工人","street_worker", 2),
    ]
    scenes[config.SCENE_CITY] = Scene(config.SCENE_CITY, CITY_MAP,
                                       city_npcs, city_doors, [], spawn=(5, 8))

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
    ]:
        tiles, npcs, doors, objects, spawn = builder()
        scenes[name] = Scene(name, tiles, npcs, doors, objects, spawn=spawn)

    return scenes


# ── Rendering ─────────────────────────────────────────────────────────
def draw_scene(surf, scene, cx, cy, economy, fnt_s):
    ts = config.TILE_SIZE
    x0 = max(0, int(cx // ts))
    y0 = max(0, int(cy // ts))
    x1 = min(scene.cols, x0 + config.SCREEN_W // ts + 2)
    y1 = min(scene.rows, y0 + config.SCREEN_H // ts + 2)

    for ty in range(y0, y1):
        for tx in range(x0, x1):
            tile = scene.tiles[ty][tx]
            base = TILE_COLOR.get(tile, (80,80,80))
            sx, sy = tx * ts - int(cx), ty * ts - int(cy)
            r = pygame.Rect(sx, sy, ts, ts)
            pygame.draw.rect(surf, base, r)
            _decorate(surf, sx, sy, ts, tile, fnt_s, economy)

    # Overlay text for city signs
    if scene.name == config.SCENE_CITY:
        for (tx, ty), label in CITY_SIGNS.items():
            sx, sy = tx * ts - int(cx), ty * ts - int(cy) - 14
            if -200 < sx < config.SCREEN_W + 200:
                bg = pygame.Surface((len(label)*16+12, 22), pygame.SRCALPHA)
                bg.fill((0,0,0,150))
                surf.blit(bg, (sx - 4, sy - 2))
                t = fnt_s.render(label, True, config.WHITE)
                surf.blit(t, (sx, sy))

    # Show inflation-driven price tags in supermarket
    if scene.name == config.SCENE_SUPERMARKET:
        cpi = economy.cpi
        for ax in [3, 7, 11, 15]:
            base_prices = {3: 5, 7: 4, 11: 8, 15: 12}
            price = int(base_prices[ax] * (1 + cpi / 5))
            sx, sy = ax * ts - int(cx), 2 * ts - int(cy) - 18
            col = config.RED if cpi > 6 else config.YELLOW if cpi > 3 else config.GREEN
            t = fnt_s.render(f"${price}", True, col)
            bg = pygame.Surface((t.get_width()+8, t.get_height()+4), pygame.SRCALPHA)
            bg.fill((0,0,0,180))
            surf.blit(bg, (sx, sy))
            surf.blit(t, (sx+4, sy+2))

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


def _decorate(surf, sx, sy, ts, tile, fnt_s, economy):
    if tile == W:
        pygame.draw.line(surf, (55,48,65), (sx, sy+ts//2), (sx+ts, sy+ts//2), 1)
        pygame.draw.line(surf, (55,48,65), (sx+ts//2, sy), (sx+ts//2, sy+ts), 1)
    elif tile == DR:
        pygame.draw.rect(surf, (140, 100, 50), pygame.Rect(sx+8, sy+4, ts-16, ts-8), border_radius=4)
        pygame.draw.circle(surf, (255,220,80), (sx+ts-14, sy+ts//2), 3)
    elif tile == T:
        pygame.draw.rect(surf, config.TERMINAL_BG, pygame.Rect(sx+4, sy+4, ts-9, ts-9), border_radius=3)
        pygame.draw.rect(surf, config.TERMINAL_GREEN, pygame.Rect(sx+4, sy+4, ts-9, ts-9), border_radius=3, width=1)
        t = fnt_s.render("PC", True, config.TERMINAL_GREEN)
        surf.blit(t, (sx+(ts-t.get_width())//2, sy+(ts-t.get_height())//2))
    elif tile == B:
        pygame.draw.rect(surf, (75,115,180), pygame.Rect(sx+2, sy+2, ts-5, ts-5), border_radius=5)
        pygame.draw.rect(surf, (200,205,220), pygame.Rect(sx+3, sy+3, ts-7, 12))
    elif tile == TR:
        pygame.draw.rect(surf, (80, 55, 30), pygame.Rect(sx+ts//2-3, sy+ts-16, 6, 16))
        pygame.draw.circle(surf, (40, 110, 50), (sx+ts//2, sy+ts//2-2), ts//2-4)
        pygame.draw.circle(surf, (30, 90, 40), (sx+ts//2, sy+ts//2-2), ts//2-8, 2)
    elif tile == FT:
        pygame.draw.circle(surf, (60, 140, 180), (sx+ts//2, sy+ts//2), ts//2-4)
        pygame.draw.circle(surf, (200, 230, 255), (sx+ts//2, sy+ts//2), ts//4)
    elif tile == BN:
        pygame.draw.rect(surf, (110, 70, 50), pygame.Rect(sx+4, sy+ts//2, ts-8, 10), border_radius=2)
        pygame.draw.rect(surf, (90, 55, 40), pygame.Rect(sx+6, sy+ts//2+10, 4, 8))
        pygame.draw.rect(surf, (90, 55, 40), pygame.Rect(sx+ts-10, sy+ts//2+10, 4, 8))
    elif tile == LP:
        pygame.draw.rect(surf, (60, 60, 70), pygame.Rect(sx+ts//2-2, sy+4, 4, ts-8))
        pygame.draw.circle(surf, (255, 240, 180), (sx+ts//2, sy+6), 5)
        pygame.draw.circle(surf, (255, 255, 200, 100), (sx+ts//2, sy+6), 10)
    elif tile == SH:
        pygame.draw.rect(surf, (160, 130, 90), pygame.Rect(sx+2, sy+2, ts-5, ts-5))
        for ly in range(sy+8, sy+ts-4, 8):
            pygame.draw.line(surf, (100, 70, 40), (sx+4, ly), (sx+ts-6, ly), 1)
            # produce
            pygame.draw.circle(surf, (220, 80, 80), (sx+10, ly-3), 2)
            pygame.draw.circle(surf, (80, 220, 80), (sx+22, ly-3), 2)
            pygame.draw.circle(surf, (220, 220, 80), (sx+34, ly-3), 2)
    elif tile == PD:
        pygame.draw.rect(surf, (140, 100, 60), pygame.Rect(sx+6, sy+8, ts-12, ts-12), border_radius=3)
        pygame.draw.line(surf, (60,40,20), (sx+ts//2, sy+8), (sx+ts//2, sy+ts-8), 2)
    elif tile == CF:
        pygame.draw.rect(surf, (60, 40, 30), pygame.Rect(sx+6, sy+4, ts-12, ts-8), border_radius=2)
        pygame.draw.circle(surf, (200, 50, 50), (sx+ts//2, sy+ts//2), 3)
        # steam
        for i in range(3):
            ox = (pygame.time.get_ticks() // 100 + i*60) % 30
            pygame.draw.circle(surf, (220,220,220,100), (sx+ts//2-5+i*5, sy-ox//3), 3)
    elif tile == TV:
        pygame.draw.rect(surf, (30, 30, 40), pygame.Rect(sx+2, sy+4, ts-5, ts-12), border_radius=2)
        pygame.draw.rect(surf, (60, 120, 180), pygame.Rect(sx+5, sy+7, ts-11, ts-18))
    elif tile == SK:
        pygame.draw.rect(surf, (200, 200, 210), pygame.Rect(sx+2, sy+2, ts-5, ts-5), border_radius=2)
        pygame.draw.line(surf, (100, 100, 120), (sx+ts//2, sy+4), (sx+ts//2, sy+ts-4), 1)
    elif tile == CH:
        pygame.draw.rect(surf, (130, 90, 60), pygame.Rect(sx+8, sy+8, ts-16, ts-16), border_radius=3)
        pygame.draw.rect(surf, (90, 60, 40), pygame.Rect(sx+8, sy+6, ts-16, 4))
    elif tile == TB:
        pygame.draw.rect(surf, (155, 110, 70), pygame.Rect(sx+2, sy+2, ts-5, ts-5), border_radius=3)
        pygame.draw.rect(surf, (110, 75, 45), pygame.Rect(sx+2, sy+ts-12, ts-5, 6))
    elif tile == BK:
        pygame.draw.rect(surf, (110, 70, 40), pygame.Rect(sx+2, sy+2, ts-5, ts-5))
        for ly in range(sy+6, sy+ts-4, 8):
            pygame.draw.rect(surf, (180, 60, 60), pygame.Rect(sx+5, ly, 8, 6))
            pygame.draw.rect(surf, (60, 180, 60), pygame.Rect(sx+14, ly, 8, 6))
            pygame.draw.rect(surf, (60, 60, 180), pygame.Rect(sx+23, ly, 8, 6))
            pygame.draw.rect(surf, (180, 180, 60), pygame.Rect(sx+32, ly, 8, 6))
    elif tile == RG:
        pygame.draw.rect(surf, (170, 70, 90), pygame.Rect(sx, sy, ts, ts))
        pygame.draw.line(surf, (130, 50, 70), (sx, sy+ts//2), (sx+ts, sy+ts//2), 1)
    elif tile == WIN:
        pygame.draw.rect(surf, (140, 180, 200), pygame.Rect(sx+2, sy+8, ts-5, ts-20))
        pygame.draw.line(surf, (90, 130, 160), (sx+ts//2, sy+8), (sx+ts//2, sy+ts-12), 2)
    elif tile == CR:
        for stripe_y in range(sy+4, sy+ts, 8):
            pygame.draw.rect(surf, (220, 220, 220), pygame.Rect(sx+4, stripe_y, ts-8, 4))
    elif tile == TM:
        pygame.draw.rect(surf, (60, 60, 70), pygame.Rect(sx+4, sy+8, ts-9, ts-16), border_radius=2)
        pygame.draw.rect(surf, (30, 30, 40), pygame.Rect(sx+6, sy+10, ts-13, ts-20))
    elif tile == CN:
        pygame.draw.rect(surf, (230, 220, 200), pygame.Rect(sx+ts//4, sy, ts//2, ts))
        pygame.draw.rect(surf, (200, 190, 170), pygame.Rect(sx+ts//4, sy+2, ts//2, 6))
        pygame.draw.rect(surf, (200, 190, 170), pygame.Rect(sx+ts//4, sy+ts-8, ts//2, 6))
    elif tile == SC:
        pygame.draw.rect(surf, (30, 60, 100), pygame.Rect(sx+2, sy+4, ts-5, ts-8), border_radius=2)
        pygame.draw.rect(surf, (40, 90, 140), pygame.Rect(sx+4, sy+6, ts-9, ts-12), 1)
    elif tile == PG:
        # pigeon
        pygame.draw.ellipse(surf, (200, 200, 200), pygame.Rect(sx+10, sy+ts-16, 14, 8))
        pygame.draw.circle(surf, (180, 180, 180), (sx+10, sy+ts-14), 4)
        pygame.draw.circle(surf, (40,40,40), (sx+8, sy+ts-14), 1)
    elif tile == FL:
        pygame.draw.rect(surf, (60, 140, 60), pygame.Rect(sx, sy, ts, ts))
        for fx, fy, fc in [(8,8,(255,80,80)),(20,12,(255,200,80)),(32,8,(160,80,200)),
                            (12,28,(255,150,200)),(28,30,(80,180,255))]:
            pygame.draw.circle(surf, fc, (sx+fx, sy+fy), 3)
    elif tile == FN:
        pygame.draw.rect(surf, (130, 130, 140), pygame.Rect(sx+2, sy+ts//3, ts-5, 4))
        pygame.draw.rect(surf, (130, 130, 140), pygame.Rect(sx+2, sy+2*ts//3, ts-5, 4))
    elif tile == CB:
        pygame.draw.rect(surf, (130, 110, 80), pygame.Rect(sx+4, sy+4, ts-9, ts-9), border_radius=3)
        pygame.draw.rect(surf, (100, 80, 60), pygame.Rect(sx+4, sy+4, ts-9, ts-9), border_radius=3, width=2)
    elif tile == RP:
        pygame.draw.rect(surf, (140, 30, 40), pygame.Rect(sx, sy, ts, ts))
        pygame.draw.line(surf, (90, 20, 30), (sx, sy+ts-1), (sx+ts, sy+ts-1), 2)
