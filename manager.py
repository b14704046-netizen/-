"""Game manager — random events, scene transitions, NPC reactions."""
import random
import config
from entities import NPC


EVENTS = [
    # ── 國會施壓事件 (結合 v2.0 通膨預期) ──────────────────────────────────────
    {
        "id": "congress_warren",
        "title": "參議員 Warren 施壓！",
        "desc": "「失業率持續攀升，聯準會必須降息救市！你對工人有交代嗎？」",
        "condition": lambda e: e.unemployment > 6.5,
        "choices": [
            {"text": "配合降息 0.25%",     "ffr": -0.25, "approval": +5,  "bubble": "謝謝主席！"},
            {"text": "婉拒，堅守數據導向", "ffr":  0.0,  "approval": -6,  "bubble": "你只顧富人！"},
        ],
        "shake": False,
        "inf_shock": 0.15, "unemp_shock": -0.1,
    },
    {
        "id": "congress_cruz",
        "title": "參議員 Cruz 施壓！",
        "desc": "「通膨已嚴重侵蝕美國家庭！聯準會為何不積極升息？」",
        "condition": lambda e: e.cpi > 5.5,
        "choices": [
            {"text": "配合升息 0.5%",        "ffr": +0.5, "approval": +4,  "bubble": "對！打倒通膨！"},
            {"text": "婉拒，不被政治左右",   "ffr":  0.0, "approval": -5,  "bubble": "聯準會不負責任！"},
        ],
        "shake": False,
        "inf_shock": -0.2, "unemp_shock": 0.2,
    },
    {
        "id": "congress_sanders",
        "title": "參議員 Sanders 衝擊！",
        "desc": "「你的政策讓工人更窮！企業利潤創新高，工資卻追不上物價！」",
        "condition": lambda e: e.cpi > 4.0 and e.unemployment > 5.0,
        "choices": [
            {"text": "承諾兼顧就業與物價",   "ffr": -0.25, "approval": +6,  "bubble": "說得有道理！"},
            {"text": "堅持聯準會獨立立場",   "ffr":  0.0,  "approval": -7,  "bubble": "鮑威爾是精英走狗！"},
        ],
        "shake": True,
        "inf_shock": 0.0, "unemp_shock": -0.2,
    },
    # ── 原有事件 (升級加入 v2.0 QE/QT 政策工具，bs 單位為兆美元) ─────────────
    {
        "id": "oil_spike",
        "title": "油價暴漲！",
        "desc": "地緣衝突導致原油供應中斷，能源價格飆升。",
        "choices": [
            {"text": "緊急升息 0.5%",  "ffr": +0.5,  "bs": 0.0,   "inf": -0.3, "unemp": +0.3, "bubble": "利率太高了！"},
            {"text": "維持利率觀望",   "ffr":  0.0,  "bs": 0.0,   "inf": +0.8, "unemp":  0.0, "bubble": "物價好貴！"},
            {"text": "緊急降息救市",   "ffr": -0.25, "bs": 0.0,   "inf": +1.2, "unemp": -0.2, "bubble": "通膨要失控了！"},
        ],
        "shake": True,
        "inf_shock": 1.5, "unemp_shock": 0.0,
    },
    {
        "id": "bank_fail",
        "title": "銀行倒閉危機！",
        "desc": "矽谷某大型銀行宣告倒閉，市場恐慌蔓延。",
        "choices": [
            # v2.0 改動：降息同時啟動 QE 購債注入流動性 (擴表 0.3 兆)
            {"text": "緊急降息並擴表 QE",   "ffr": -0.5,  "bs": +0.3, "inf": +0.5, "unemp": -0.5, "bubble": "謝謝主席救市！"},
            {"text": "維持利率與資產規模", "ffr":  0.0,  "bs": 0.0,  "inf":  0.0, "unemp": +0.3, "bubble": "太緊縮了..."},
            {"text": "升息展現抗通膨決心", "ffr": +0.25, "bs": -0.1, "inf": -0.2, "unemp": +0.8, "bubble": "要倒大楣了！"},
        ],
        "shake": True,
        "inf_shock": -0.5, "unemp_shock": 1.0,
    },
    {
        "id": "jobs_report",
        "title": "非農就業爆表！",
        "desc": "本月新增就業 80萬，勞動市場嚴重過熱。",
        "choices": [
            {"text": "積極升息 0.75%", "ffr": +0.75, "bs": 0.0,   "inf": -0.6, "unemp": +0.5, "bubble": "要失業了！"},
            {"text": "溫和升息 0.25%", "ffr": +0.25, "bs": 0.0,   "inf": -0.1, "unemp": +0.1, "bubble": "還好啦..."},
            {"text": "手動縮表 QT 壓制", "ffr":  0.0,   "bs": -0.3, "inf": -0.3, "unemp": +0.3, "bubble": "資金變緊了！"},
        ],
        "shake": False,
        "inf_shock": 0.8, "unemp_shock": -0.3,
    },
    {
        "id": "recession_fear",
        "title": "衰退恐慌！",
        "desc": "GDP 連兩季負成長，輿論要求聯準會救市。",
        "choices": [
            # 降息並啟動巨量 QE 灌入市場
            {"text": "大幅降息並瘋狂 QE", "ffr": -1.0,  "bs": +0.3, "inf": +1.0, "unemp": -0.5, "bubble": "華爾街開派對囉！"},
            {"text": "小幅降息 0.25%",   "ffr": -0.25, "bs": 0.0,  "inf": +0.2, "unemp": -0.1, "bubble": "還不夠！"},
            {"text": "堅持抗通膨，加速縮表", "ffr":  0.0, "bs": -0.3, "inf": -0.5, "unemp": +0.6, "bubble": "太狠了吧！"},
        ],
        "shake": True,
        "inf_shock": -0.8, "unemp_shock": 1.2,
    },
    {
        "id": "supply_chain",
        "title": "供應鏈斷裂！",
        "desc": "主要港口罷工，消費品短缺，價格飛漲。",
        "choices": [
            {"text": "升息壓制需求",   "ffr": +0.5,  "bs": 0.0,   "inf": -0.5, "unemp": +0.4, "bubble": "還是很貴！"},
            {"text": "觀望等供給回復", "ffr":  0.0,  "bs": 0.0,   "inf": +0.6, "unemp":  0.0, "bubble": "物價失控！"},
            {"text": "降息刺激生產",   "ffr": -0.25, "bs": 0.0,   "inf": +1.0, "unemp": -0.2, "bubble": "不管用啊！"},
        ],
        "shake": False,
        "inf_shock": 1.8, "unemp_shock": 0.2,
    },
    {
        "id": "election",
        "title": "政治壓力！",
        "desc": "選舉將近，政客要求降息刺激景氣，你怎麼看？",
        "choices": [
            {"text": "獨立運作，不理",  "ffr":  0.0, "bs": 0.0,  "inf":  0.0, "unemp":  0.0, "bubble": "尊重聯準會！"},
            {"text": "放水購債討好政客",  "ffr":  0.0, "bs": +0.2, "inf": +0.3, "unemp": -0.1, "bubble": "政治干預！"},
            {"text": "反升息展示獨立",  "ffr": +0.25,"bs": 0.0,  "inf": -0.2, "unemp": +0.2, "bubble": "勇氣可嘉！"},
        ],
        "shake": False,
        "inf_shock": 0.2, "unemp_shock": 0.0,
    },
    {
        "id": "tech_bubble",
        "title": "科技股泡沫！",
        "desc": "AI 概念股一夜跌 40%，市場恐慌！",
        "choices": [
            {"text": "鎮定發言安撫",     "ffr":  0.0, "bs": 0.0,  "inf":  0.0, "unemp": +0.2, "bubble": "主席太冷靜了！"},
            {"text": "緊急降息 0.5%",    "ffr": -0.5, "bs": 0.0,  "inf": +0.7, "unemp": -0.3, "bubble": "救市了！"},
            {"text": "擴表 QE 接刀救市", "ffr":  0.0, "bs": +0.3, "inf": +0.5, "unemp": -0.2, "bubble": "多頭續命！"},
        ],
        "shake": True,
        "inf_shock": -0.3, "unemp_shock": 0.5,
    },
    {
        "id": "housing_crash",
        "title": "房市崩盤警報！",
        "desc": "全國房價單月下跌 8%，2008年陰影重現？",
        "choices": [
            {"text": "降息並購債穩定房市", "ffr": -0.5, "bs": +0.2, "inf": +0.5, "unemp": -0.3, "bubble": "請救救我們！"},
            {"text": "監控觀察",       "ffr":  0.0, "bs": 0.0,  "inf":  0.0, "unemp": +0.3, "bubble": "你太被動！"},
            {"text": "繼續壓制通膨",   "ffr": +0.25,"bs": 0.0,  "inf": -0.2, "unemp": +0.5, "bubble": "我家要法拍了！"},
        ],
        "shake": True,
        "inf_shock": -0.4, "unemp_shock": 0.8,
    },
]


NPC_BUBBLES_HIGH_INF = [
    "蛋又漲價了！", "我買不起房！", "薪水跟不上物價！",
    "什麼時候降息？", "通膨害死人！", "主席你在幹嘛？！",
    "連麵包都買不起了", "這個月信用卡爆表",
]
NPC_BUBBLES_HIGH_UNEMP = [
    "我失業了...", "找不到工作...", "利率太高傷到我了",
    "景氣很差...", "求職中...", "公司倒閉裁員了",
    "投了50份履歷沒消息", "租金還是得付...",
]
NPC_BUBBLES_NORMAL = [
    "今天天氣不錯", "股市漲了！", "軟著陸成功？",
    "物價還算穩定", "謝謝主席！", "今天咖啡好喝",
]

# 依 NPC 種類的專屬台詞 (新增 v2.0 專屬台詞)
NPC_BUBBLES_BY_KIND = {
    "unemployed": ["找不到工作...", "求職中...", "失業幾個月了", "有工作機會嗎？"],
    "protester":  ["打倒通膨！", "物價失控！", "鮑威爾下台！", "工人要公平！"],
    "journalist": ["通膨預期去錨了？", "主席下午有記者會？", "資產負債表何時正常化？"],
    "trader":     ["今天做多！", "影子利率跌了！", "信用利差又擴大了！", "Fed put 在哪？"],
    "politician": ["聯準會必須降息！", "你的政策傷害工人！", "我要召開聽證！"],
    "elder":      ["年輕時哪有這種通膨...", "退休金被通膨吃光了", "早買房還好"],
    "child":      ["媽媽說冰淇淋太貴了", "今天學校放假！"],
    "shopper":    ["蛋又漲了！", "買不起肉...", "刷卡刷到怕", "超市東西好貴"],
    "barista":    ["咖啡豆成本暴漲...", "今天來杯美式嗎？"],
}

# 依場景的專屬台詞
NPC_BUBBLES_SCENE = {
    "supermarket_high": ["這個貴死了！", "蛋要$15了？！", "什麼都漲薪水沒漲"],
    "supermarket_ok":   ["今天有特價！", "新鮮水果！", "買菜囉"],
    "wall_st_up":       ["多頭！影子利率萬歲！", "今天大漲！", "QE 鈔能力！"],
    "wall_st_down":     ["錢荒來了...", "信用利差爆表！", "Fed 搞砸了！"],
    "capitol_bad":      ["鮑威爾應該下台！", "聯準會失職！", "國會應介入！"],
    "park_ok":          ["天氣真好", "鴿子好可愛", "這裡好安靜"],
}

# 街頭突發事件 (配合 v2.0 狀態變數觸發)
STREET_INCIDENTS = [
    {
        "id": "protest_march",
        "title": "抗議遊行爆發！",
        "desc": "通膨憤怒群眾湧上街頭，警察嚴陣以待...",
        "condition": lambda e: e.cpi > 5.5,
        "bubble": "物價太貴活不下去！",
        "approval_hit": -2,
        "duration": 10.0,
    },
    {
        "id": "media_chase",
        "title": "媒體瘋狂追問！",
        "desc": "你剛走出聯準會，記者群圍了上來……",
        "condition": lambda e: True,
        "bubble": "主席！請問何時停止 QT 縮表？",
        "approval_hit": 0,
        "duration": 7.0,
    },
    {
        "id": "food_panic",
        "title": "超市哄搶事件！",
        "desc": "蛋跟牛奶缺貨，民眾大排長龍引發衝突！",
        "condition": lambda e: e.cpi > 7.0,
        "bubble": "沒有蛋！都搶光了！",
        "approval_hit": -3,
        "duration": 12.0,
    },
    {
        "id": "homeless_camp",
        "title": "街頭帳篷城出現！",
        "desc": "失業人口暴增，街邊出現大型遊民聚集地。",
        "condition": lambda e: e.unemployment > 7.0,
        "bubble": "我已三個月沒工作了...",
        "approval_hit": -2,
        "duration": 10.0,
    },
    {
        "id": "stock_crash_crowd",
        "title": "市場崩盤人心惶惶！",
        "desc": "股市暴跌，路人紛紛站在電視前看盤。",
        "condition": lambda e: e.gdp < -2.0,
        "bubble": "我的退休金都沒了！",
        "approval_hit": -2,
        "duration": 9.0,
    },
    {
        "id": "credit_crunch_news",
        "title": "金融海嘯警報！",
        "desc": "信用利差飆升，中小型企業爆發連環倒閉潮！",
        "condition": lambda e: e.credit_spread > 4.5,
        "bubble": "銀行根本不放貸了，公司開不出薪水！",
        "approval_hit": -4,
        "duration": 11.0,
    },
    {
        "id": "good_news_flash",
        "title": "軟著陸跡象出現！",
        "desc": "財經媒體：通膨預期穩固，民眾信心回升！",
        "condition": lambda e: e.cpi < 3.0 and e.month > 6,
        "bubble": "也許經濟真的在好轉？",
        "approval_hit": +2,
        "duration": 8.0,
    },
    {
        "id": "wall_st_bonus",
        "title": "華爾街發獎金！",
        "desc": "市場復甦，金融業大發獎金，貧富差距擴大。",
        "condition": lambda e: e.gdp > 3.0 and e.cpi < 5.0,
        "bubble": "QE 印鈔票，富人爽賺資產增值！",
        "approval_hit": -1,
        "duration": 8.0,
    },
    {
        "id": "rate_hike_shock",
        "title": "升息震撼彈！",
        "desc": "剛宣布的升息決定令街頭民眾議論紛紛。",
        "condition": lambda e: e.ffr > 7.0,
        "bubble": "房貸利息高死了！",
        "approval_hit": -1,
        "duration": 9.0,
    },
]


class StreetIncidentManager:
    """非阻斷式街頭突發事件，只在城市場景觸發。"""

    def __init__(self):
        self.current = None   
        self._cooldown = 22.0

    def tick(self, dt, economy, scene_name, scene_npcs):
        if scene_name != "city":
            self.current = None
            return

        if self.current:
            self.current["t"] -= dt
            if self.current["t"] <= 0:
                self.current = None
            return

        self._cooldown -= dt
        if self._cooldown > 0:
            return

        self._cooldown = random.uniform(20.0, 45.0)
        eligible = [i for i in STREET_INCIDENTS if i["condition"](economy)]
        if not eligible:
            return

        chosen = random.choice(eligible)
        self.current = dict(chosen)
        self.current["t"] = chosen["duration"]
        
        visible = [n for n in scene_npcs if getattr(n, "visible", True) and n.bubble_t <= 0]
        if visible:
            random.choice(visible[:4]).say(chosen["bubble"], 5.0)


class EventManager:
    def __init__(self):
        self.active_event = None
        self._cooldown    = 25.0
        self._min_gap     = 30.0

    def tick(self, dt, economy):
        if self.active_event:
            return
        self._cooldown -= dt
        if self._cooldown <= 0:
            self._cooldown = self._min_gap + random.uniform(0, 15)
            eligible = [e for e in EVENTS
                        if e.get("condition", lambda _: True)(economy)]
            if eligible:
                self.active_event = random.choice(eligible).copy()

    def resolve(self, choice_idx, economy, camera):
        if not self.active_event:
            return ""
        ev = self.active_event
        ch = ev["choices"][choice_idx]
        
        # 1. [升級] 同時支援調整 FFR 利率與資產負債表 (bs)
        if "ffr" in ch:
            economy.adjust_ffr(ch["ffr"])
        if "bs" in ch:
            economy.adjust_balance_sheet(ch["bs"])
            
        # 2. 注入事件環境衝擊 + 選項自帶衝擊
        total_inf_shock = ev.get("inf_shock", 0) + ch.get("inf", 0)
        total_unemp_shock = ev.get("unemp_shock", 0) + ch.get("unemp", 0)
        economy.apply_shock(total_inf_shock, total_unemp_shock)
        
        # 3. 處理滿意度增減
        if ch.get("approval"):
            economy.approval = max(0, min(100, economy.approval + ch["approval"]))
            
        if ev.get("shake") and camera:
            camera.shake()
            
        self.active_event = None
        return ch.get("bubble", "")


def _pick_bubble(npc, economy, scene_name):
    """依據 NPC 種類、場景、經濟狀況挑選合適台詞。"""
    kind = npc.kind

    # 場景專屬優先
    if scene_name == "supermarket":
        pool = NPC_BUBBLES_SCENE["supermarket_high" if economy.cpi > 5 else "supermarket_ok"]
        return random.choice(pool)
    if scene_name == "wall_st":
        pool = NPC_BUBBLES_SCENE["wall_st_up" if economy.gdp > 1 else "wall_st_down"]
        return random.choice(pool)
    if scene_name == "capitol" and economy.approval < 40:
        return random.choice(NPC_BUBBLES_SCENE["capitol_bad"])
    if scene_name == "park":
        return random.choice(NPC_BUBBLES_SCENE["park_ok"])

    # [升級] v2.0 隱藏數據反饋優先：通膨預期去錨
    if abs(economy.inf_exp - 2.0) > 1.5:
        return random.choice(["市場預期物價再也回不去了...", "聯聯準會講的話還能信嗎？", "大家都開始囤民資了"])
    # [升級] v2.0 隱藏數據反饋優先：金融市場錢荒 (信用利差高)
    if economy.credit_spread > 4.0:
        return random.choice(["銀行根本不放貸了！", "小企業債務利息快還不出來了...", "金融市場流動性好乾"])

    # NPC 種類專屬
    if kind in NPC_BUBBLES_BY_KIND:
        return random.choice(NPC_BUBBLES_BY_KIND[kind])

    # 通用經濟狀況
    if economy.cpi > 6:
        return random.choice(NPC_BUBBLES_HIGH_INF)
    if economy.unemployment > 7:
        return random.choice(NPC_BUBBLES_HIGH_UNEMP)
    if random.random() < 0.4:
        return random.choice(NPC_BUBBLES_NORMAL)
    return None


class GameManager:
    def __init__(self, economy, camera):
        self.economy = economy
        self.camera  = camera
        self.events  = EventManager()
        self.street  = StreetIncidentManager()
        self.message = ""
        self.message_t = 0.0
        self._npc_bubble_t = 0.0

    def update(self, dt, economy, scene):
        self.events.tick(dt, economy)
        self.street.tick(dt, economy, scene.name, scene.npcs)

        if self.street.current:
            hit = self.street.current.get("approval_hit", 0)
            if hit != 0:
                economy.approval = max(0, min(100, economy.approval + hit * dt / self.street.current["duration"]))

        for npc in scene.npcs:
            npc.update(dt, economy)

        self._npc_bubble_t -= dt
        if self._npc_bubble_t <= 0:
            self._npc_bubble_t = random.uniform(3.5, 8.0)
            visible = [n for n in scene.npcs if getattr(n, "visible", True) and n.bubble_t <= 0]
            if visible:
                npc = random.choice(visible)
                bubble = _pick_bubble(npc, economy, scene.name)
                if bubble:
                    npc.say(bubble)

        unemp_ratio = min(1.0, economy.unemployment / 14.0)
        street_npcs = [n for n in scene.npcs if n.kind in ("citizen", "child", "elder")]
        n_hidden = int(unemp_ratio * len(street_npcs))
        for i, npc in enumerate(street_npcs):
            npc.visible = (i >= n_hidden)

        if economy.cpi > 6:
            for npc in scene.npcs:
                if npc.kind == "protester":
                    npc.visible = True

        if self.message_t > 0:
            self.message_t -= dt
    def post_message(self, text, duration=3.0):
            self.message   = text
            self.message_t = duration
    # [升級] 用於發布新聞跑馬燈，安撫或警告面對「政策時滯」的玩家
    def check_policy_news_flash(self, choice_data, event_data):
        """依據玩家剛剛的重大決策，推播即時財經新聞跑馬燈。"""
        # 如果啟動了大規模 QE
        if choice_data.get("bs", 0) > 0.15:
            self.post_message("📰 彭博快訊：聯準會啟動大規模 QE，華爾街流動性爆棚！", 4.5)
        # 如果啟動了大規模 QT
        elif choice_data.get("bs", 0) < -0.15:
            self.post_message("📰 華爾街日報：聯準會加速縮表，市場高呼緊縮寒冬將至！", 4.5)
        # 如果大幅度降息
        elif choice_data.get("ffr", 0) <= -0.5:
            self.post_message("📰 CNBC：暴力降息引發市場震驚！美股期指直線狂飆！", 4.0)
        # 如果大幅度升息
        elif choice_data.get("ffr", 0) >= 0.5:
            self.post_message("📰 路透社：聯準會祭出強硬鷹派升息，借貸成本壓力劇增！", 4.0)

    def resolve_event(self, idx, scene):
        # 暫存當前事件的選項資料，用於跑馬燈檢查
        current_event = self.events.active_event
        if not current_event:
            return
        chosen_choice = current_event["choices"][idx]

        bubble = self.events.resolve(idx, self.economy, self.camera)
        if bubble:
            for npc in scene.npcs:
                if getattr(npc, "visible", True):
                    npc.say(bubble, 4.0)
                    break
        
        # [升級] 玩家做完決策後，立刻推播對應的新聞跑馬燈提示
        self.check_policy_news_flash(chosen_choice, current_event)
