"""Daily quest system."""
import config


class Quest:
    def __init__(self, qid, title, desc, reward_text, check_fn, reward_fn):
        self.qid = qid
        self.title = title
        self.desc = desc
        self.reward_text = reward_text
        self.check_fn = check_fn
        self.reward_fn = reward_fn
        self.done = False
        self.notified = False


def make_default_quests(state):
    return [
        Quest("morning_coffee",
              "晨間咖啡",
              "去咖啡廳沖一杯鷹派咖啡",
              "+2 民眾支持度",
              lambda s: "coffee" in s["completed"],
              lambda eco: setattr(eco, "approval", min(100, eco.approval + 2))),
        Quest("visit_supermarket",
              "民意巡視",
              "去超市看蛋價（與5位民眾對話）",
              "+1 民眾支持度",
              lambda s: s["dialogs"] >= 5,
              lambda eco: setattr(eco, "approval", min(100, eco.approval + 1))),
        Quest("hold_presser",
              "記者會",
              "去新聞室開記者會",
              "+ 媒體支持度",
              lambda s: "press" in s["completed"],
              lambda eco: setattr(eco, "approval", min(100, eco.approval + 2))),
        Quest("feed_pigeons",
              "靜心時刻",
              "在公園餵餵鴿子放鬆",
              "減少壓力",
              lambda s: "pigeon" in s["completed"],
              lambda eco: setattr(eco, "approval", min(100, eco.approval + 1))),
        Quest("workout",
              "體能訓練",
              "在健身房玩跑步機小遊戲",
              "提升耐力",
              lambda s: "treadmill" in s["completed"],
              lambda eco: None),
        Quest("survive",
              "撐到月底",
              f"在 {config.WIN_MONTHS} 個月內維持經濟穩定",
              "傳奇主席結局",
              lambda s: False,
              lambda eco: None),
    ]


class QuestLog:
    def __init__(self):
        self.quests = []
        self.state = {"completed": set(), "dialogs": 0}

    def reset(self, economy):
        self.quests = make_default_quests(self.state)
        self.state = {"completed": set(), "dialogs": 0}

    def mark_completed(self, minigame_name, economy):
        self.state["completed"].add(minigame_name)
        self._check(economy)

    def note_dialog(self, economy):
        self.state["dialogs"] += 1
        self._check(economy)

    def _check(self, economy):
        for q in self.quests:
            if not q.done and q.check_fn(self.state):
                q.done = True
                q.reward_fn(economy)

    def pending(self):
        return [q for q in self.quests if not q.done]

    def completed(self):
        return [q for q in self.quests if q.done]
