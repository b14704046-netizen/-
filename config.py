SCREEN_W, SCREEN_H = 1280, 720
FPS = 60
TITLE = "Soft Landing: Powell's Monday"
TILE_SIZE = 48

# Colors
BLACK = (0,   0,   0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (40,  40,  50)
LIGHT_GRAY = (200, 200, 210)
RED = (220, 60,  60)
GREEN = (60,  200, 100)
BLUE = (60,  120, 220)
YELLOW = (255, 220, 60)
ORANGE = (255, 140, 60)
DARK_GREEN = (20, 80,  40)
BROWN = (120, 80,  40)
PURPLE = (160, 60,  200)
PINK = (255, 150, 200)
GOLD = (255, 200, 80)
TERMINAL_BG = (10,  18,  28)
TERMINAL_GREEN = (0,   255, 100)
TERMINAL_AMBER = (255, 180, 0)
TERMINAL_DIM = (0,   120, 50)

# Economy
INITIAL_FFR = 5.25
INITIAL_CPI = 3.2
INITIAL_UNEMPLOYMENT = 4.1
INITIAL_GDP = 2.5
INITIAL_APPROVAL = 68


FFR_MIN = 0.0
FFR_MAX = 20.0
FFR_STEP = 0.25

SIM_TICK_SECONDS = 6.0

# Game states
STATE_MENU = "menu"
STATE_WORLD = "world"
STATE_TERMINAL = "terminal"
STATE_EVENT = "event"
STATE_DIALOG = "dialog"
STATE_MINIGAME = "minigame"
STATE_GAMEOVER = "gameover"
STATE_WIN = "win"
STATE_QUEST = "quest"
STATE_TRANSITION = "transition"
STATE_PHONE = "phone"
STATE_INTRO = "intro"

# Scenes
SCENE_CITY = "city"
SCENE_APARTMENT = "apartment"
SCENE_CAFE = "cafe"
SCENE_FED = "fed"
SCENE_SUPERMARKET = "supermarket"
SCENE_PARK = "park"
SCENE_PRESS = "press"
SCENE_CAPITOL = "capitol"
SCENE_WALL_ST = "wall_st"
SCENE_GYM = "gym"
SCENE_BANK = "bank"
SCENE_HOSPITAL = "hospital"
SCENE_UNIVERSITY = "university"

# Mini-games
MG_COFFEE = "coffee"
MG_PRESS = "press"
MG_PIGEON = "pigeon"
MG_TREADMILL = "treadmill"
MG_GOLF = "golf"

STATE_GUITAR_VIDEO = "guitar_video"

# ── 資產負債表 (QE/QT) ──────────────────────────────────────────────────────
INITIAL_BS      = 8.5    # 初始資產負債表規模（兆美元，對應 2022 年高點附近）
BS_MIN          = 2.0    # 最小規模（下限）
BS_MAX          = 15.0   # 最大規模（極端 QE）
BS_STEP         = 0.3    # 每月最大操作量（兆美元）
 
# ── 通膨預期 ─────────────────────────────────────────────────────────────────
INITIAL_INF_EXP = 2.5    # 初始通膨預期（%）
INF_EXP_LOSE    = 8.0    # 通膨預期去錨 → 遊戲失敗閾值
 
# ── 信用利差 ─────────────────────────────────────────────────────────────────
INITIAL_CREDIT_SP = 1.5  # 初始信用利差（%，對應正常時期）
 
# ── 實證校準參數 ──────────────────────────────────────────────────────────────
NAIRU           = 4.5    # 自然失業率（Non-Accelerating Inflation Rate of Unemployment）
POTENTIAL_GDP   = 2.0    # 潛在 GDP 成長率（%）
NEUTRAL_RATE    = 2.5    # 中性利率（%，r*）
 
# ── 原有參數（確保存在）──────────────────────────────────────────────────────
TARGET_INFLATION = 2.0
FFR_MIN          = 0.0
FFR_MAX          = 20.0
INFLATION_LOSE   = 15.0
UNEMPLOY_LOSE    = 15.0
APPROVAL_LOSE    = 15.0
WIN_MONTHS       = 36
 
