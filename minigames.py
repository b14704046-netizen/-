"""Mini-games: Coffee, Press Conference, Pigeon, Treadmill."""
import pygame
import random
import math
import config


# ── Base class ────────────────────────────────────────────────────────
class MiniGame:
    def __init__(self):
        self.done = False
        self.result = None  # dict of effects when done

    def handle_event(self, ev): pass
    def update(self, dt, keys): pass
    def draw(self, surf, fnt, fnt_big, fnt_s): pass


# ── Coffee Mini-Game ──────────────────────────────────────────────────
class CoffeeGame(MiniGame):
    """Hit SPACE when the moving needle is in the green zone. 4 rounds."""
    STAGES = ["磨豆", "加水", "悶蒸", "萃取"]

    def __init__(self):
        super().__init__()
        self.stage = 0
        self.pos = 0.0
        self.speed = 0.9
        self.dir = 1
        self.scores = []
        self.zone_lo = 0.40
        self.zone_hi = 0.60
        self._feedback = ""
        self._feedback_t = 0.0

    def update(self, dt, keys):
        if self.done: return
        self.pos += self.speed * self.dir * dt
        if self.pos > 1.0:
            self.pos = 1.0
            self.dir = -1
        elif self.pos < 0.0:
            self.pos = 0.0
            self.dir = 1
        if self._feedback_t > 0: self._feedback_t -= dt

    def handle_event(self, ev):
        if self.done: return
        if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_SPACE, pygame.K_RETURN):
            if self.zone_lo <= self.pos <= self.zone_hi:
                score = 100 - abs(self.pos - 0.5) * 400
                self._feedback = "完美！"
            elif self.zone_lo - 0.1 <= self.pos <= self.zone_hi + 0.1:
                score = 50
                self._feedback = "勉強！"
            else:
                score = 0
                self._feedback = "失敗..."
            self._feedback_t = 1.0
            self.scores.append(score)
            self.stage += 1
            self.speed += 0.25
            if self.stage >= len(self.STAGES):
                self._finish()
            else:
                self.pos = 0.0
                self.dir = 1

    def _finish(self):
        avg = sum(self.scores) / len(self.scores)
        if avg >= 80:
            self.result = {"approval": +3, "coffee": 2, "msg": "鷹派咖啡完美！士氣大振！"}
        elif avg >= 50:
            self.result = {"approval": +1, "coffee": 1, "msg": "還可以的咖啡。"}
        else:
            self.result = {"approval": -1, "coffee": 0, "msg": "難喝...今天會很累。"}
        self.done = True

    def draw(self, surf, fnt, fnt_big, fnt_s):
        W, H = config.SCREEN_W, config.SCREEN_H
        surf.fill((50, 30, 20))
        # Title
        title = fnt_big.render("☕ 手沖鷹派咖啡", True, config.TERMINAL_AMBER)
        surf.blit(title, (W//2 - title.get_width()//2, 60))

        stage_txt = fnt.render(f"階段 {self.stage+1}/4：{self.STAGES[min(self.stage, 3)]}", True, config.WHITE)
        surf.blit(stage_txt, (W//2 - stage_txt.get_width()//2, 130))

        # Bar
        bar_x, bar_y, bar_w, bar_h = W//2 - 300, H//2 - 30, 600, 60
        pygame.draw.rect(surf, (30, 20, 15), pygame.Rect(bar_x, bar_y, bar_w, bar_h), border_radius=8)
        # green zone
        gx = bar_x + int(bar_w * self.zone_lo)
        gw = int(bar_w * (self.zone_hi - self.zone_lo))
        pygame.draw.rect(surf, (60, 180, 80), pygame.Rect(gx, bar_y, gw, bar_h), border_radius=8)
        # needle
        nx = bar_x + int(bar_w * self.pos)
        pygame.draw.rect(surf, (255, 255, 100), pygame.Rect(nx-4, bar_y - 10, 8, bar_h + 20))
        # border
        pygame.draw.rect(surf, config.TERMINAL_AMBER, pygame.Rect(bar_x, bar_y, bar_w, bar_h), border_radius=8, width=2)

        # Instruction
        instr = fnt.render("[ SPACE ] 按下！讓針停在綠色區域", True, config.LIGHT_GRAY)
        surf.blit(instr, (W//2 - instr.get_width()//2, H//2 + 60))

        # Scores
        for i, s in enumerate(self.scores):
            col = config.GREEN if s >= 80 else config.YELLOW if s >= 50 else config.RED
            t = fnt.render(f"{self.STAGES[i]}: {int(s)}", True, col)
            surf.blit(t, (W//2 - 200 + i * 120, H//2 + 140))

        # Feedback
        if self._feedback_t > 0:
            col = config.GREEN if "完美" in self._feedback else config.YELLOW if "勉強" in self._feedback else config.RED
            t = fnt_big.render(self._feedback, True, col)
            surf.blit(t, (W//2 - t.get_width()//2, H//2 - 110))

        # ESC hint
        esc = fnt_s.render("[ ESC ] 放棄", True, config.GRAY)
        surf.blit(esc, (W - esc.get_width() - 20, H - 30))


# ── Press Conference Mini-Game ────────────────────────────────────────
PRESS_QS = [
    {
        "q": "WSJ：聯準會何時降息？",
        "choices": [
            ("我們將堅守 2% 通膨目標。", {"approval": +2, "inf_expect": -0.3}),
            ("可能在數據改善後考慮。",     {"approval": +1, "inf_expect": -0.1}),
            ("近期就會降息！",             {"approval": -1, "inf_expect": +0.5}),
        ],
    },
    {
        "q": "CNBC：經濟是否會衰退？",
        "choices": [
            ("我們看見一條軟著陸的路徑。", {"approval": +2, "vol": -1}),
            ("有可能，但會努力避免。",     {"approval":  0, "vol":  0}),
            ("可能性提高了。",             {"approval": -2, "vol": +2}),
        ],
    },
    {
        "q": "彭博：縮表會持續多久？",
        "choices": [
            ("資產負債表會持續正常化。",   {"approval": +1, "vol": -1}),
            ("我們會視市況調整。",         {"approval": +1, "vol":  0}),
            ("可能很快停止 QT。",          {"approval": -1, "vol": +1}),
        ],
    },
    {
        "q": "FT：對銀行體系有信心嗎？",
        "choices": [
            ("銀行業體質強健。",           {"approval": +2, "vol": -2}),
            ("有韌性，但需持續觀察。",     {"approval":  0, "vol":  0}),
            ("我們正密切關注風險。",       {"approval": -2, "vol": +2}),
        ],
    },
    {
        "q": "Reuters：政治壓力影響決策？",
        "choices": [
            ("聯準會獨立運作。",           {"approval": +2, "vol": -1}),
            ("我們聽取各方意見。",         {"approval":  0, "vol":  0}),
            ("不予置評。",                 {"approval": -1, "vol":  0}),
        ],
    },
]


class PressGame(MiniGame):
    def __init__(self):
        super().__init__()
        self.qs = random.sample(PRESS_QS, 4)
        self.qi = 0
        self.sel = 0
        self.totals = {"approval": 0, "inf_expect": 0, "vol": 0}
        self._feedback = ""
        self._feedback_t = 0.0

    def handle_event(self, ev):
        if self.done: return
        if ev.type != pygame.KEYDOWN: return
        if ev.key in (pygame.K_UP, pygame.K_w):
            self.sel = (self.sel - 1) % 3
        elif ev.key in (pygame.K_DOWN, pygame.K_s):
            self.sel = (self.sel + 1) % 3
        elif ev.key in (pygame.K_1, pygame.K_2, pygame.K_3):
            self.sel = ev.key - pygame.K_1
            self._answer()
        elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._answer()

    def _answer(self):
        _, effects = self.qs[self.qi]["choices"][self.sel]
        for k, v in effects.items():
            self.totals[k] = self.totals.get(k, 0) + v
        self._feedback = f"記者點頭" if effects.get("approval", 0) > 0 else (
            "記者皺眉" if effects.get("approval", 0) < 0 else "記者紀錄中"
        )
        self._feedback_t = 1.2
        self.qi += 1
        self.sel = 0
        if self.qi >= len(self.qs):
            self._finish()

    def _finish(self):
        appr = self.totals["approval"]
        if appr >= 6:
            msg = "媒體一片好評！"
        elif appr >= 2:
            msg = "中規中矩的記者會。"
        else:
            msg = "媒體質疑你的表現。"
        self.result = {
            "approval": appr,
            "inf_expect": self.totals.get("inf_expect", 0),
            "msg": msg,
        }
        self.done = True

    def update(self, dt, keys):
        if self._feedback_t > 0: self._feedback_t -= dt

    def draw(self, surf, fnt, fnt_big, fnt_s):
        W, H = config.SCREEN_W, config.SCREEN_H
        surf.fill((20, 25, 35))
        # backdrop
        for i in range(50):
            pygame.draw.circle(surf, (255, 255, 255, 10),
                               (i*30 % W, (i*47) % H), 1)

        # Title
        title = fnt_big.render("📰 聯準會記者會", True, config.TERMINAL_AMBER)
        surf.blit(title, (W//2 - title.get_width()//2, 40))

        # After last question, skip question rendering — result screen will overlay
        if self.qi >= len(self.qs):
            return

        prog = fnt.render(f"問題 {self.qi+1}/{len(self.qs)}", True, config.LIGHT_GRAY)
        surf.blit(prog, (W//2 - prog.get_width()//2, 110))

        # Question
        q = self.qs[self.qi]["q"]
        qt = fnt_big.render(q, True, config.WHITE)
        surf.blit(qt, (W//2 - qt.get_width()//2, 170))

        # Choices
        for i, (text, _) in enumerate(self.qs[self.qi]["choices"]):
            cy = 290 + i * 90
            cw = 800
            cx = W//2 - cw//2
            col = (50, 80, 120) if i == self.sel else (25, 30, 50)
            border = config.TERMINAL_AMBER if i == self.sel else config.TERMINAL_DIM
            pygame.draw.rect(surf, col, pygame.Rect(cx, cy, cw, 70), border_radius=6)
            pygame.draw.rect(surf, border, pygame.Rect(cx, cy, cw, 70), border_radius=6, width=2)
            t = fnt.render(f"[{i+1}] {text}", True, config.WHITE)
            surf.blit(t, (cx + 20, cy + 22))

        # feedback
        if self._feedback_t > 0:
            ft = fnt_big.render(self._feedback, True, config.TERMINAL_AMBER)
            surf.blit(ft, (W//2 - ft.get_width()//2, H - 110))

        nav = fnt_s.render("↑↓ 選擇  /  1-3 直選  /  Enter 確認  /  ESC 放棄", True, config.TERMINAL_DIM)
        surf.blit(nav, (W//2 - nav.get_width()//2, H - 40))


# ── Pigeon Feeding Mini-Game ──────────────────────────────────────────
class PigeonGame(MiniGame):
    """Catch pigeons by pressing SPACE when one is over Powell."""

    DURATION = 25.0

    def __init__(self):
        super().__init__()
        self.t = 0.0
        self.pigeons = []
        self.spawn_t = 0.0
        self.score = 0
        self.missed = 0
        self.powell_x = 0.5  # 0..1
        self._feedback = ""
        self._feedback_t = 0.0

    def update(self, dt, keys):
        if self.done: return
        self.t += dt

        # Powell can move horizontally
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.powell_x = max(0.05, self.powell_x - 0.6 * dt)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.powell_x = min(0.95, self.powell_x + 0.6 * dt)

        # Spawn pigeons
        self.spawn_t -= dt
        if self.spawn_t <= 0:
            self.spawn_t = random.uniform(0.5, 1.2)
            self.pigeons.append({
                "x": random.uniform(0.05, 0.95),
                "y": -0.05,
                "speed": random.uniform(0.18, 0.32),
                "caught": False,
            })

        # Move pigeons
        for p in self.pigeons:
            if p["caught"]: continue
            p["y"] += p["speed"] * dt
        # Remove missed
        for p in self.pigeons[:]:
            if not p["caught"] and p["y"] > 1.05:
                self.missed += 1
                self.pigeons.remove(p)

        if self._feedback_t > 0: self._feedback_t -= dt

        if self.t >= self.DURATION:
            self._finish()

    def handle_event(self, ev):
        if self.done: return
        if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_SPACE, pygame.K_RETURN):
            # Try to catch the closest uncaught pigeon near Powell
            best = None
            best_d = 0.12
            for p in self.pigeons:
                if p["caught"]: continue
                if 0.65 < p["y"] < 0.95:
                    d = abs(p["x"] - self.powell_x)
                    if d < best_d:
                        best_d = d
                        best = p
            if best is not None:
                best["caught"] = True
                self.score += 1
                self._feedback = "+1 🕊"
                self._feedback_t = 0.8

    def _finish(self):
        s = self.score
        if s >= 15:
            self.result = {"approval": +3, "msg": f"優雅！餵了 {s} 隻鴿子。"}
        elif s >= 8:
            self.result = {"approval": +1, "msg": f"還行，餵了 {s} 隻。"}
        else:
            self.result = {"approval":  0, "msg": f"只餵了 {s} 隻..."}
        self.done = True

    def draw(self, surf, fnt, fnt_big, fnt_s):
        W, H = config.SCREEN_W, config.SCREEN_H
        # Sky gradient
        for y in range(H):
            c = (
                int(180 - y * 0.1),
                int(220 - y * 0.05),
                int(240 - y * 0.05),
            )
            pygame.draw.line(surf, c, (0, y), (W, y))
        # Ground
        pygame.draw.rect(surf, (80, 140, 60), pygame.Rect(0, int(H * 0.85), W, H))
        # Trees
        for tx in [120, 350, 800, 1100]:
            pygame.draw.rect(surf, (80, 50, 30), pygame.Rect(tx, int(H*0.65), 20, 100))
            pygame.draw.circle(surf, (50, 130, 60), (tx + 10, int(H*0.65)), 50)

        title = fnt_big.render("🕊 公園餵鴿子", True, (40, 70, 40))
        surf.blit(title, (W//2 - title.get_width()//2, 20))

        # Powell
        px = int(W * self.powell_x)
        py = int(H * 0.78)
        pygame.draw.rect(surf, (25, 90, 170), pygame.Rect(px-12, py-20, 24, 30))
        pygame.draw.ellipse(surf, (210, 175, 140), pygame.Rect(px-10, py-38, 20, 20))
        pygame.draw.ellipse(surf, (170, 170, 175), pygame.Rect(px-10, py-38, 20, 10))

        # Pigeons
        for p in self.pigeons:
            if p["caught"]: continue
            ppx = int(W * p["x"])
            ppy = int(H * p["y"])
            wing = math.sin(self.t * 10 + p["x"] * 12) * 4
            pygame.draw.ellipse(surf, (210, 210, 210), pygame.Rect(ppx-14, ppy-5, 28, 12))
            pygame.draw.ellipse(surf, (180, 180, 180), pygame.Rect(ppx-18, ppy-6 - wing, 12, 6))
            pygame.draw.ellipse(surf, (180, 180, 180), pygame.Rect(ppx+6,  ppy-6 + wing, 12, 6))
            pygame.draw.circle(surf, (190, 190, 190), (ppx-14, ppy-7), 5)

        # Score
        sc = fnt.render(f"餵食：{self.score}    錯過：{self.missed}    剩餘：{max(0, self.DURATION - self.t):.1f}s",
                        True, (40, 50, 60))
        surf.blit(sc, (20, 20))

        # Catch zone hint
        zone_y = int(H * 0.7)
        pygame.draw.line(surf, (180, 200, 180), (0, zone_y), (W, zone_y), 1)

        if self._feedback_t > 0:
            t = fnt_big.render(self._feedback, True, (40, 120, 40))
            surf.blit(t, (px - 20, py - 80))

        nav = fnt_s.render("← →  移動  /  SPACE 餵食  /  ESC 放棄", True, (40, 50, 60))
        surf.blit(nav, (W//2 - nav.get_width()//2, H - 30))


# ── Treadmill Mini-Game ───────────────────────────────────────────────
class TreadmillGame(MiniGame):
    """Alternate LEFT/RIGHT at the rhythm of beats."""

    DURATION = 20.0

    def __init__(self):
        super().__init__()
        self.t = 0.0
        self.beats = []
        self.spawn_t = 0.0
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.beat_period = 0.6
        self.expected = "left"
        self._feedback = ""
        self._feedback_t = 0.0

    def update(self, dt, keys):
        if self.done: return
        self.t += dt
        # Spawn beats
        self.spawn_t -= dt
        if self.spawn_t <= 0:
            self.spawn_t = self.beat_period
            self.beats.append({"side": self.expected, "y": -0.05, "hit": False, "missed": False})
            self.expected = "right" if self.expected == "left" else "left"

        for b in self.beats:
            if not b["hit"] and not b["missed"]:
                b["y"] += dt * 0.65
                if b["y"] > 0.95:
                    b["missed"] = True
                    self.combo = 0

        if self._feedback_t > 0: self._feedback_t -= dt
        if self.t >= self.DURATION:
            self._finish()

    def handle_event(self, ev):
        if self.done: return
        if ev.type != pygame.KEYDOWN: return
        side = None
        if ev.key in (pygame.K_a, pygame.K_LEFT):  side = "left"
        if ev.key in (pygame.K_d, pygame.K_RIGHT): side = "right"
        if side is None: return
        # Find nearest unhit beat of that side
        best = None
        best_d = 0.18
        for b in self.beats:
            if b["hit"] or b["missed"]: continue
            if b["side"] != side: continue
            d = abs(b["y"] - 0.75)
            if d < best_d:
                best_d = d
                best = b
        if best is not None:
            best["hit"] = True
            if best_d < 0.05:
                self.score += 100
                self._feedback = "完美！"
                self.combo += 1
            elif best_d < 0.10:
                self.score += 60
                self._feedback = "好！"
                self.combo += 1
            else:
                self.score += 20
                self._feedback = "OK"
                self.combo = 0
            self.max_combo = max(self.max_combo, self.combo)
            self._feedback_t = 0.4
        else:
            self.combo = 0

    def _finish(self):
        if self.score >= 1500:
            self.result = {"approval": +2, "coffee": 1,
                           "msg": f"恢復滿格！分數 {self.score}, 連擊 {self.max_combo}"}
        elif self.score >= 800:
            self.result = {"approval": +1,
                           "msg": f"還可以。分數 {self.score}"}
        else:
            self.result = {"approval":  0,
                           "msg": f"體力不夠。分數 {self.score}"}
        self.done = True

    def draw(self, surf, fnt, fnt_big, fnt_s):
        W, H = config.SCREEN_W, config.SCREEN_H
        surf.fill((30, 30, 40))
        title = fnt_big.render("🏃 中性利率跑步機", True, config.TERMINAL_AMBER)
        surf.blit(title, (W//2 - title.get_width()//2, 30))

        # Two lanes
        for side, lx, label in [("left", W//2 - 150, "← A"), ("right", W//2 + 150, "D →")]:
            pygame.draw.rect(surf, (40, 50, 70), pygame.Rect(lx - 60, 100, 120, H - 200), border_radius=8)
            # Hit zone
            hit_y = 100 + int((H - 200) * 0.75)
            pygame.draw.rect(surf, (60, 120, 60), pygame.Rect(lx - 60, hit_y - 30, 120, 60))
            pygame.draw.rect(surf, config.GREEN, pygame.Rect(lx - 60, hit_y - 30, 120, 60), width=2)
            lt = fnt.render(label, True, config.WHITE)
            surf.blit(lt, (lx - lt.get_width()//2, hit_y + 50))

        # Beats
        for b in self.beats:
            if b["hit"] or b["missed"]: continue
            lx = W//2 - 150 if b["side"] == "left" else W//2 + 150
            by = 100 + int((H - 200) * b["y"])
            col = (255, 200, 100) if b["side"] == "left" else (100, 200, 255)
            pygame.draw.circle(surf, col, (lx, by), 30)
            pygame.draw.circle(surf, (255,255,255), (lx, by), 30, 2)

        # Score
        sc = fnt.render(f"分數：{self.score}    連擊：{self.combo}", True, config.WHITE)
        surf.blit(sc, (20, 20))
        tm = fnt.render(f"剩餘：{max(0, self.DURATION - self.t):.1f}s", True, config.LIGHT_GRAY)
        surf.blit(tm, (W - tm.get_width() - 20, 20))

        if self._feedback_t > 0:
            col = config.GREEN if "完美" in self._feedback else config.YELLOW if "好" in self._feedback else config.LIGHT_GRAY
            t = fnt_big.render(self._feedback, True, col)
            surf.blit(t, (W//2 - t.get_width()//2, H//2 - 200))

        nav = fnt_s.render("← →  跟著節拍按  /  ESC 放棄", True, config.TERMINAL_DIM)
        surf.blit(nav, (W//2 - nav.get_width()//2, H - 30))


def create_minigame(name):
    return {
        config.MG_COFFEE:    CoffeeGame,
        config.MG_PRESS:     PressGame,
        config.MG_PIGEON:    PigeonGame,
        config.MG_TREADMILL: TreadmillGame,
    }[name]()


def draw_result(surf, result, fnt, fnt_big, fnt_s):
    W, H = config.SCREEN_W, config.SCREEN_H
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 200))
    surf.blit(dim, (0, 0))

    bw, bh = 600, 280
    bx, by = W//2 - bw//2, H//2 - bh//2
    pygame.draw.rect(surf, (20, 30, 50), pygame.Rect(bx, by, bw, bh), border_radius=10)
    pygame.draw.rect(surf, config.TERMINAL_AMBER, pygame.Rect(bx, by, bw, bh), border_radius=10, width=2)

    t = fnt_big.render("✓ 完成", True, config.TERMINAL_GREEN)
    surf.blit(t, (bx + bw//2 - t.get_width()//2, by + 30))

    msg = fnt.render(result.get("msg", ""), True, config.WHITE)
    surf.blit(msg, (bx + bw//2 - msg.get_width()//2, by + 100))

    effects = []
    if result.get("approval", 0) != 0:
        sign = "+" if result["approval"] > 0 else ""
        effects.append(f"支持度 {sign}{result['approval']}")
    if result.get("coffee", 0) != 0:
        effects.append(f"咖啡因 +{result['coffee']}")
    if result.get("inf_expect", 0) != 0:
        sign = "+" if result["inf_expect"] > 0 else ""
        effects.append(f"通膨預期 {sign}{result['inf_expect']:.1f}%")
    for i, e in enumerate(effects):
        et = fnt_s.render(e, True, config.TERMINAL_AMBER)
        surf.blit(et, (bx + bw//2 - et.get_width()//2, by + 150 + i * 24))

    nav = fnt_s.render("[ Enter ] 繼續", True, config.TERMINAL_DIM)
    surf.blit(nav, (bx + bw//2 - nav.get_width()//2, by + bh - 36))
