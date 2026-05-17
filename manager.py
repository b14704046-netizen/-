"""Game manager — random events, scene transitions, NPC reactions."""
import random
import config
from entities import NPC


EVENTS = [
    {
        "id": "oil_spike",
        "title": "🛢 油價暴漲！",
        "desc": "地緣衝突導致原油供應中斷，能源價格飆升。",
        "choices": [
            {"text": "緊急升息 0.5%",  "ffr": +0.5,  "inf": -0.3, "unemp": +0.3, "bubble": "利率太高了！"},
            {"text": "維持利率觀望",   "ffr":  0.0,  "inf": +0.8, "unemp":  0.0, "bubble": "物價好貴！"},
            {"text": "緊急降息救市",   "ffr": -0.25, "inf": +1.2, "unemp": -0.2, "bubble": "通膨要失控了！"},
        ],
        "shake": True,
        "inf_shock": 1.5, "unemp_shock": 0.0,
    },
    {
        "id": "bank_fail",
        "title": "🏦 銀行倒閉危機！",
        "desc": "矽谷某大型銀行宣告倒閉，市場恐慌蔓延。",
        "choices": [
            {"text": "緊急降息救市",   "ffr": -0.5,  "inf": +0.5, "unemp": -0.5, "bubble": "謝謝主席！"},
            {"text": "維持利率穩定",   "ffr":  0.0,  "inf":  0.0, "unemp": +0.3, "bubble": "太緊縮了..."},
            {"text": "升息展現決心",   "ffr": +0.25, "inf": -0.2, "unemp": +0.8, "bubble": "要倒大楣了！"},
        ],
        "shake": True,
        "inf_shock": -0.5, "unemp_shock": 1.0,
    },
    {
        "id": "jobs_report",
        "title": "📊 非農就業爆表！",
        "desc": "本月新增就業 80萬，遠超預期。勞動市場過熱。",
        "choices": [
            {"text": "積極升息 0.75%", "ffr": +0.75, "inf": -0.6, "unemp": +0.5, "bubble": "要失業了！"},
            {"text": "溫和升息 0.25%", "ffr": +0.25, "inf": -0.1, "unemp": +0.1, "bubble": "還好啦..."},
            {"text": "不動，等數據",   "ffr":  0.0,  "inf": +0.4, "unemp":  0.0, "bubble": "通膨要來了！"},
        ],
        "shake": False,
        "inf_shock": 0.8, "unemp_shock": -0.3,
    },
    {
        "id": "recession_fear",
        "title": "📉 衰退恐慌！",
        "desc": "GDP 連兩季負成長，輿論要求聯準會救市。",
        "choices": [
            {"text": "大幅降息 1%",    "ffr": -1.0,  "inf": +1.0, "unemp": -0.5, "bubble": "謝謝主席！"},
            {"text": "小幅降息 0.25%", "ffr": -0.25, "inf": +0.2, "unemp": -0.1, "bubble": "還不夠！"},
            {"text": "堅持抗通膨",     "ffr":  0.0,  "inf": -0.3, "unemp": +0.5, "bubble": "太狠了吧！"},
        ],
        "shake": True,
        "inf_shock": -0.8, "unemp_shock": 1.2,
    },
    {
        "id": "supply_chain",
        "title": "🚢 供應鏈斷裂！",
        "desc": "主要港口罷工，消費品短缺，價格飛漲。",
        "choices": [
            {"text": "升息壓制需求",   "ffr": +0.5,  "inf": -0.5, "unemp": +0.4, "bubble": "還是很貴！"},
            {"text": "觀望等供給回復", "ffr":  0.0,  "inf": +0.6, "unemp":  0.0, "bubble": "物價失控！"},
            {"text": "降息刺激生產",   "ffr": -0.25, "inf": +1.0, "unemp": -0.2, "bubble": "不管用啊！"},
        ],
        "shake": False,
        "inf_shock": 1.8, "unemp_shock": 0.2,
    },
    {
        "id": "election",
        "title": "🗳 政治壓力！",
        "desc": "選舉將近，政客要求降息刺激景氣，你怎麼看？",
        "choices": [
            {"text": "獨立運作，不理",  "ffr":  0.0, "inf":  0.0, "unemp":  0.0, "bubble": "尊重聯準會！"},
            {"text": "象徵性降息",      "ffr": -0.25,"inf": +0.3, "unemp": -0.1, "bubble": "政治干預！"},
            {"text": "反升息展示獨立",  "ffr": +0.25,"inf": -0.2, "unemp": +0.2, "bubble": "勇氣可嘉！"},
        ],
        "shake": False,
        "inf_shock": 0.2, "unemp_shock": 0.0,
    },
    {
        "id": "tech_bubble",
        "title": "💻 科技股泡沫！",
        "desc": "AI 概念股一夜跌 40%，市場恐慌！",
        "choices": [
            {"text": "鎮定發言安撫",     "ffr":  0.0, "inf":  0.0, "unemp": +0.2, "bubble": "主席太冷靜了！"},
            {"text": "緊急降息 0.5%",    "ffr": -0.5, "inf": +0.7, "unemp": -0.3, "bubble": "救市了！"},
            {"text": "讓市場自我修正",   "ffr":  0.0, "inf": -0.2, "unemp": +0.6, "bubble": "你冷血！"},
        ],
        "shake": True,
        "inf_shock": -0.3, "unemp_shock": 0.5,
    },
    {
        "id": "housing_crash",
        "title": "🏠 房市崩盤警報！",
        "desc": "全國房價單月下跌 8%，2008年陰影重現？",
        "choices": [
            {"text": "降息穩定房市",   "ffr": -0.5,  "inf": +0.5, "unemp": -0.3, "bubble": "請救救我們！"},
            {"text": "監控觀察",       "ffr":  0.0,  "inf":  0.0, "unemp": +0.3, "bubble": "你太被動！"},
            {"text": "繼續壓制通膨",   "ffr": +0.25, "inf": -0.2, "unemp": +0.5, "bubble": "我家要法拍了！"},
        ],
        "shake": True,
        "inf_shock": -0.4, "unemp_shock": 0.8,
    },
]


NPC_BUBBLES_HIGH_INF = [
    "蛋又漲價了！", "我買不起房！", "薪水跟不上物價！",
    "什麼時候降息？", "通膨害死人！", "主席你在幹嘛？！",
]
NPC_BUBBLES_HIGH_UNEMP = [
    "我失業了...", "找不到工作...", "利率太高傷到我了",
    "景氣很差...", "求職中...",
]
NPC_BUBBLES_NORMAL = [
    "今天天氣不錯", "股市漲了！", "軟著陸成功？",
    "物價還算穩定", "謝謝主席！",
]


class EventManager:
    def __init__(self):
        self.active_event = None
        self._cooldown    = 25.0
        self._min_gap     = 30.0

    def tick(self, dt, economy):
        if self.active_event: return
        self._cooldown -= dt
        if self._cooldown <= 0:
            self._cooldown = self._min_gap + random.uniform(0, 15)
            self.active_event = random.choice(EVENTS).copy()

    def resolve(self, choice_idx, economy, camera):
        if not self.active_event: return
        ev = self.active_event
        ch = ev["choices"][choice_idx]
        economy.adjust_ffr(ch["ffr"])
        economy.apply_shock(ev["inf_shock"], ev["unemp_shock"])
        if ev.get("shake") and camera: camera.shake()
        self.active_event = None
        return ch.get("bubble", "")


class GameManager:
    def __init__(self, economy, camera):
        self.economy = economy
        self.camera  = camera
        self.events  = EventManager()
        self.message = ""
        self.message_t = 0.0
        self._npc_bubble_t = 0.0

    def update(self, dt, economy, scene):
        self.events.tick(dt, economy)

        # NPCs in current scene
        for npc in scene.npcs:
            npc.update(dt, economy)

        # Random NPC reactions
        self._npc_bubble_t -= dt
        if self._npc_bubble_t <= 0:
            self._npc_bubble_t = random.uniform(4, 9)
            visible = [n for n in scene.npcs if n.visible and n.bubble_t <= 0]
            if visible:
                npc = random.choice(visible)
                if economy.cpi > 6:
                    npc.say(random.choice(NPC_BUBBLES_HIGH_INF))
                elif economy.unemployment > 7:
                    npc.say(random.choice(NPC_BUBBLES_HIGH_UNEMP))
                elif random.random() < 0.4:
                    npc.say(random.choice(NPC_BUBBLES_NORMAL))

        # Hide some NPCs when unemployment is high (street empties)
        unemp_ratio = min(1.0, economy.unemployment / 14.0)
        street_npcs = [n for n in scene.npcs if n.kind in ("citizen", "child", "elder")]
        n_hidden = int(unemp_ratio * len(street_npcs))
        for i, npc in enumerate(street_npcs):
            npc.visible = (i >= n_hidden)

        if self.message_t > 0: self.message_t -= dt

    def post_message(self, text, duration=3.0):
        self.message   = text
        self.message_t = duration

    def resolve_event(self, idx, scene):
        bubble = self.events.resolve(idx, self.economy, self.camera)
        if bubble:
            for npc in scene.npcs:
                if npc.visible:
                    npc.say(bubble, 4.0)
                    break
