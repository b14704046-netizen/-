import pygame
import math
import config


def _bar(surf, x, y, w, h, value, vmin, vmax, good_range, colors, label, fnt):
    ratio = max(0.0, min(1.0, (value - vmin) / (vmax - vmin)))
    pygame.draw.rect(surf, (20, 35, 50), pygame.Rect(x, y, w, h), border_radius=3)
    lo, hi = good_range
    if vmin <= value <= lo or value <= hi:
        bar_col = colors[0]
    elif value <= hi * 1.5:
        bar_col = colors[1]
    else:
        bar_col = colors[2]
    fw = max(2, int(w * ratio))
    pygame.draw.rect(surf, bar_col, pygame.Rect(x, y, fw, h), border_radius=3)
    pygame.draw.rect(surf, config.TERMINAL_DIM, pygame.Rect(x, y, w, h), border_radius=3, width=1)
    txt = fnt.render(f"{label}: {value:.1f}%", True, config.TERMINAL_GREEN)
    surf.blit(txt, (x, y - fnt.get_height() - 2))


def draw_sparkline(surf, history, key, x, y, w, h, col):
    vals = [s[key] for s in history[-20:]]
    if len(vals) < 2: return
    mn, mx = min(vals) - 0.5, max(vals) + 0.5
    if mx == mn: return
    pts = []
    for i, v in enumerate(vals):
        px = x + int(i / (len(vals)-1) * w)
        py = y + h - int((v - mn) / (mx - mn) * h)
        pts.append((px, py))
    if len(pts) >= 2:
        pygame.draw.lines(surf, col, False, pts, 2)
    pygame.draw.circle(surf, config.WHITE, pts[-1], 3)


def draw_terminal(surf, economy, fnt, fnt_big, fnt_s, tick_progress):
    W, H = config.SCREEN_W, config.SCREEN_H
    snap = economy.snapshot()
    surf.fill(config.TERMINAL_BG)
    for ly in range(0, H, 4):
        pygame.draw.line(surf, (0, 0, 0), (0, ly), (W, ly), 1)
    pygame.draw.rect(surf, (8, 22, 38), pygame.Rect(0, 0, W, 52))
    pygame.draw.line(surf, config.TERMINAL_GREEN, (0, 52), (W, 52), 1)

    title = fnt_big.render("■ FED 聯準會 經濟監控終端", True, config.TERMINAL_GREEN)
    surf.blit(title, (20, 12))

    month_str = f"Month {snap['month']:02d} / {config.WIN_MONTHS}"
    mt = fnt.render(month_str, True, config.TERMINAL_AMBER)
    surf.blit(mt, (W - mt.get_width() - 20, 14))

    panel_x, panel_y = 30, 70
    pygame.draw.rect(surf, (12, 28, 44), pygame.Rect(panel_x, panel_y, 340, 260), border_radius=6)
    pygame.draw.rect(surf, config.TERMINAL_DIM, pygame.Rect(panel_x, panel_y, 340, 260), border_radius=6, width=1)

    t = fnt.render("[ 聯邦基金利率 (FFR) ]", True, config.TERMINAL_AMBER)
    surf.blit(t, (panel_x + 14, panel_y + 10))

    ffr_display = fnt_big.render(f"{snap['ffr']:.2f} %", True, config.TERMINAL_GREEN)
    surf.blit(ffr_display, (panel_x + 14, panel_y + 40))

    hint = fnt_s.render("[ ↑/↓ ] 調整  [ +/- ] 快速  [ Enter ] 返回", True, config.TERMINAL_DIM)
    surf.blit(hint, (panel_x + 14, panel_y + 110))

    _bar(surf, panel_x+14, panel_y+165, 308, 20,
         snap['ffr'], 0, 20, (1.0, 7.0),
         [config.GREEN, config.YELLOW, config.RED],
         "FFR", fnt_s)

    nr_x = panel_x + 14 + int(config.NEUTRAL_RATE / 20 * 308)
    pygame.draw.line(surf, config.BLUE, (nr_x, panel_y+160), (nr_x, panel_y+190), 2)
    nt = fnt_s.render("中性利率", True, config.BLUE)
    surf.blit(nt, (nr_x - 20, panel_y+192))

    tt = fnt_s.render("▲ 調升利率 = 壓制通膨，代價是失業率上升", True, (80,120,80))
    surf.blit(tt, (panel_x+14, panel_y + 225))

    ix = 390
    indicators = [
        ("通膨率 (CPI)",  snap["cpi"],          0, 20, (0.5, 4.0)),
        ("失業率",        snap["unemployment"],   0, 16, (2.0, 6.0)),
        ("GDP 成長",      snap["gdp"] + 6,        0, 12, (5.5, 8.5)),
        ("民眾支持度",    snap["approval"],        0,100, (50, 80)),
    ]
    colors_template = [config.GREEN, config.YELLOW, config.RED]

    for i, (label, val, vmin, vmax, good) in enumerate(indicators):
        iy = 70 + i * 90
        pygame.draw.rect(surf, (12, 28, 44), pygame.Rect(ix, iy, 360, 75), border_radius=6)
        pygame.draw.rect(surf, config.TERMINAL_DIM, pygame.Rect(ix, iy, 360, 75), border_radius=6, width=1)
        _bar(surf, ix+14, iy+44, 330, 16, val, vmin, vmax, good, colors_template, label, fnt_s)
        actual = [snap["cpi"], snap["unemployment"], snap["gdp"], snap["approval"]][i]
        vt = fnt.render(f"{actual:.1f}", True, config.TERMINAL_GREEN)
        surf.blit(vt, (ix + 14, iy + 8))

    chart_x, chart_y, chart_w, chart_h = 770, 70, 480, 280
    pygame.draw.rect(surf, (8, 20, 34), pygame.Rect(chart_x, chart_y, chart_w, chart_h), border_radius=6)
    pygame.draw.rect(surf, config.TERMINAL_DIM, pygame.Rect(chart_x, chart_y, chart_w, chart_h), border_radius=6, width=1)

    ct = fnt_s.render("[ 歷史走勢 ]", True, config.TERMINAL_AMBER)
    surf.blit(ct, (chart_x + 10, chart_y + 8))

    if len(economy.history) >= 2:
        target_y = chart_y + 30 + chart_h - 30 - int(config.TARGET_INFLATION / 20 * (chart_h - 40))
        pygame.draw.line(surf, (30, 80, 30), (chart_x+10, target_y), (chart_x+chart_w-10, target_y), 1)
        tl = fnt_s.render("目標 2%", True, (30,80,30))
        surf.blit(tl, (chart_x + chart_w - 60, target_y - 14))

    draw_sparkline(surf, economy.history, "cpi",
                   chart_x+10, chart_y+30, chart_w-20, chart_h-40, config.ORANGE)
    draw_sparkline(surf, economy.history, "unemployment",
                   chart_x+10, chart_y+30, chart_w-20, chart_h-40, config.BLUE)
    draw_sparkline(surf, economy.history, "ffr",
                   chart_x+10, chart_y+30, chart_w-20, chart_h-40, config.YELLOW)

    for col, label, ly in [
        (config.ORANGE, "CPI 通膨率",  chart_y+chart_h-55),
        (config.BLUE,   "失業率",      chart_y+chart_h-38),
        (config.YELLOW, "FFR 利率",    chart_y+chart_h-21),
    ]:
        pygame.draw.rect(surf, col, pygame.Rect(chart_x+10, ly+4, 16, 10))
        lt = fnt_s.render(label, True, config.LIGHT_GRAY)
        surf.blit(lt, (chart_x+32, ly))

    bar_y = H - 36
    pygame.draw.rect(surf, (15, 30, 45), pygame.Rect(0, bar_y-2, W, 38))
    pygame.draw.line(surf, config.TERMINAL_DIM, (0, bar_y-2), (W, bar_y-2), 1)
    tw = int(W * tick_progress)
    pygame.draw.rect(surf, (0, 60, 30), pygame.Rect(0, bar_y+4, tw, 22), border_radius=2)
    pt = fnt_s.render("下一個月：", True, config.TERMINAL_DIM)
    surf.blit(pt, (8, bar_y + 8))

    taylor = config.NEUTRAL_RATE + snap["cpi"] - config.TARGET_INFLATION
    rec = fnt_s.render(f"泰勒規則建議利率：{taylor:.2f}%", True, config.TERMINAL_DIM)
    surf.blit(rec, (W//2 - rec.get_width()//2, bar_y + 8))


def draw_hud(surf, economy, fnt_s, scene_name, near_interaction, quest_log):
    snap = economy.snapshot()
    W = config.SCREEN_W

    inf_label, inf_col = economy.inflation_label()
    unemp_label, unemp_col = economy.unemp_label()

    panels = [
        (f"📍 {_scene_label(scene_name)}", config.LIGHT_GRAY),
        (f"📅 第 {snap['month']}/{config.WIN_MONTHS} 月", config.LIGHT_GRAY),
        (f"📈 CPI: {snap['cpi']:.1f}%  {inf_label}", inf_col),
        (f"💼 失業: {snap['unemployment']:.1f}%  {unemp_label}", unemp_col),
        (f"💰 利率: {snap['ffr']:.2f}%", config.TERMINAL_AMBER),
        (f"❤ 支持度: {snap['approval']:.0f}%", config.GREEN if snap['approval'] > 40 else config.RED),
    ]
    for i, (text, col) in enumerate(panels):
        t = fnt_s.render(text, True, col)
        bg = pygame.Surface((t.get_width()+12, t.get_height()+6), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        surf.blit(bg, (8, 8 + i * 26))
        surf.blit(t, (14, 11 + i * 26))

    # Phone hint (bottom-right)
    ph = fnt_s.render("📱 [ P ] 手機", True, config.TERMINAL_AMBER)
    ph_bg = pygame.Surface((ph.get_width()+16, ph.get_height()+8), pygame.SRCALPHA)
    ph_bg.fill((0, 0, 0, 180))
    surf.blit(ph_bg, (W - ph_bg.get_width() - 10, config.SCREEN_H - 36))
    surf.blit(ph, (W - ph.get_width() - 18, config.SCREEN_H - 32))

    # Pending quests in top-right
    pending = quest_log.pending()[:4]
    if pending:
        title = fnt_s.render("📋 任務 [ Q ]", True, config.TERMINAL_AMBER)
        bg = pygame.Surface((title.get_width()+12, title.get_height()+6), pygame.SRCALPHA)
        bg.fill((0,0,0,180))
        surf.blit(bg, (W - bg.get_width() - 10, 8))
        surf.blit(title, (W - title.get_width() - 16, 11))
        for i, q in enumerate(pending):
            t = fnt_s.render(f"• {q.title}", True, config.LIGHT_GRAY)
            bg = pygame.Surface((t.get_width()+12, t.get_height()+4), pygame.SRCALPHA)
            bg.fill((0,0,0,140))
            surf.blit(bg, (W - bg.get_width() - 10, 36 + i * 24))
            surf.blit(t, (W - t.get_width() - 16, 38 + i * 24))

    # Interaction hint
    if near_interaction:
        kind, target = near_interaction
        label = _interaction_label(kind, target)
        if label:
            txt = fnt_s.render(label, True, config.TERMINAL_GREEN)
            bg = pygame.Surface((txt.get_width()+24, txt.get_height()+12), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 200))
            surf.blit(bg, (W//2 - bg.get_width()//2, config.SCREEN_H - 80))
            surf.blit(txt, (W//2 - txt.get_width()//2, config.SCREEN_H - 74))

    if snap["cpi"] > 10:
        t = pygame.time.get_ticks() // 500
        if t % 2 == 0:
            alarm = fnt_s.render("⚠ 通膨失控警報！立刻升息！", True, config.RED)
            surf.blit(alarm, (W//2 - alarm.get_width()//2, 8))


def draw_combat_hud(surf, player, fnt_s):
    H = config.SCREEN_H
    bx, by = 20, H - 88

    # HP bar
    hp_ratio = player.hp / player.max_hp
    hp_col = (220, 60, 60) if hp_ratio > 0.4 else (255, 100, 40) if hp_ratio > 0.2 else (255, 30, 30)
    ht = fnt_s.render(f"HP  {player.hp}/{player.max_hp}", True, config.WHITE)
    bg = pygame.Surface((ht.get_width() + 10, ht.get_height() + 4), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 160))
    surf.blit(bg, (bx - 4, by - 2))
    surf.blit(ht, (bx, by))
    by2 = by + fnt_s.get_height() + 6
    bw = 180
    pygame.draw.rect(surf, (60, 0, 0),  pygame.Rect(bx, by2, bw, 8))
    pygame.draw.rect(surf, hp_col,      pygame.Rect(bx, by2, int(bw * hp_ratio), 8))
    pygame.draw.rect(surf, (180, 0, 0), pygame.Rect(bx, by2, bw, 8), width=1)

    # Stamina bar
    st_ratio = player.stamina / player.max_stamina
    st_col = (160, 220, 50) if st_ratio > 0.3 else (255, 180, 0)
    pygame.draw.rect(surf, (40, 50, 0),  pygame.Rect(bx, by2 + 12, bw, 5))
    pygame.draw.rect(surf, st_col,       pygame.Rect(bx, by2 + 12, int(bw * st_ratio), 5))

    # Weapon + ammo
    wpn = player.current_weapon
    if wpn == "fist":
        wlabel = "[Tab] 拳頭"
    else:
        ammo = player.ammo.get(wpn, 0)
        names = {"pistol": "手槍"}
        wlabel = f"[Tab] {names.get(wpn, wpn)}  彈藥:{ammo}"
    wt = fnt_s.render(wlabel, True, config.YELLOW)
    wbg = pygame.Surface((wt.get_width() + 10, wt.get_height() + 6), pygame.SRCALPHA)
    wbg.fill((0, 0, 0, 160))
    surf.blit(wbg, (bx - 4, by2 + 22))
    surf.blit(wt, (bx, by2 + 25))


def _scene_label(name):
    return {
        config.SCENE_CITY:        "華盛頓特區",
        config.SCENE_APARTMENT:   "鮑威爾的公寓",
        config.SCENE_CAFE:        "Starbucks",
        config.SCENE_FED:         "聯邦準備理事會",
        config.SCENE_SUPERMARKET: "Whole Foods 超市",
        config.SCENE_PARK:        "國家廣場公園",
        config.SCENE_PRESS:       "新聞發佈室",
        config.SCENE_CAPITOL:     "國會山莊",
        config.SCENE_WALL_ST:     "華爾街交易所",
        config.SCENE_GYM:         "Powell Fitness",
    }.get(name, name)


def _interaction_label(kind, target):
    if kind == "door":
        scene_name = target["target"]
        return f"[ E ] 前往 {_scene_label(scene_name)}"
    if kind == "npc":
        return f"[ E ] 與 {target.name} 對話"
    if kind == "object":
        return f"[ E ] {target.get('label', '互動')}"
    return None


def draw_event(surf, event, fnt, fnt_big, fnt_s, selected):
    W, H = config.SCREEN_W, config.SCREEN_H
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 170))
    surf.blit(dim, (0, 0))

    bw, bh = 700, 380
    bx, by = W//2 - bw//2, H//2 - bh//2

    pygame.draw.rect(surf, (18, 30, 48), pygame.Rect(bx, by, bw, bh), border_radius=10)
    pygame.draw.rect(surf, config.TERMINAL_AMBER, pygame.Rect(bx, by, bw, bh), border_radius=10, width=2)

    t = fnt_big.render(event["title"], True, config.TERMINAL_AMBER)
    surf.blit(t, (bx + bw//2 - t.get_width()//2, by + 18))

    d = fnt.render(event["desc"], True, config.WHITE)
    surf.blit(d, (bx + bw//2 - d.get_width()//2, by + 72))

    for i, ch in enumerate(event["choices"]):
        cy = by + 130 + i * 72
        cw, ch_h = bw - 80, 56
        cx = bx + 40
        col = config.TERMINAL_GREEN if i == selected else (30, 55, 80)
        border_col = config.TERMINAL_GREEN if i == selected else config.TERMINAL_DIM
        pygame.draw.rect(surf, col, pygame.Rect(cx, cy, cw, ch_h), border_radius=6)
        pygame.draw.rect(surf, border_col, pygame.Rect(cx, cy, cw, ch_h), border_radius=6, width=1)
        label = f"  [{i+1}]  {ch['text']}"
        lt = fnt.render(label, True, config.WHITE if i == selected else config.LIGHT_GRAY)
        surf.blit(lt, (cx + 12, cy + 16))

    nav = fnt_s.render("↑↓ 選擇  /  Enter 確認", True, config.TERMINAL_DIM)
    surf.blit(nav, (bx + bw//2 - nav.get_width()//2, by + bh - 30))


def draw_gameover(surf, reason, economy, fnt, fnt_big, fnt_s):
    W, H = config.SCREEN_W, config.SCREEN_H
    snap = economy.snapshot()
    surf.fill((12, 5, 8))
    titles = {
        "inflation":    ("大通膨時代", "通膨失控——物價飛漲，民不聊生。", config.RED),
        "unemployment": ("硬著陸！",   "失業率暴增——鮑威爾被迫在街頭賣藝。", config.ORANGE),
        "approval":     ("下台吧！",   "民眾已失去信心，你被迫辭職。", config.YELLOW),
    }
    title, subtitle, col = titles.get(reason, ("遊戲結束", "", config.RED))
    t = fnt_big.render(title, True, col)
    surf.blit(t, (W//2 - t.get_width()//2, H//3))
    st = fnt.render(subtitle, True, config.LIGHT_GRAY)
    surf.blit(st, (W//2 - st.get_width()//2, H//3 + 80))

    stats = [
        f"最終通膨率：{snap['cpi']:.1f}%",
        f"最終失業率：{snap['unemployment']:.1f}%",
        f"在位月數：{snap['month']} 個月",
        f"最終支持度：{snap['approval']:.0f}%",
    ]
    for i, s in enumerate(stats):
        st = fnt_s.render(s, True, config.GRAY)
        surf.blit(st, (W//2 - st.get_width()//2, H//2 + 20 + i * 30))

    r = fnt_s.render("[ R ] 重新開始   [ Q ] 退出", True, config.TERMINAL_DIM)
    surf.blit(r, (W//2 - r.get_width()//2, H - 80))


def draw_win(surf, economy, fnt, fnt_big, fnt_s):
    W, H = config.SCREEN_W, config.SCREEN_H
    snap = economy.snapshot()
    t_val = pygame.time.get_ticks() / 1000.0
    surf.fill((8, 22, 14))

    col = (
        int(100 + 80 * math.sin(t_val * 1.5)),
        200,
        int(100 + 80 * math.cos(t_val * 2.0)),
    )
    t = fnt_big.render("傳奇的主席！", True, col)
    surf.blit(t, (W//2 - t.get_width()//2, H//4))

    st = fnt.render("你成功達成軟著陸——通膨受控，經濟穩健成長！", True, config.WHITE)
    surf.blit(st, (W//2 - st.get_width()//2, H//4 + 80))

    dove = fnt_big.render("🕊  鮑威爾在公園安詳地餵鴿子  🕊", True, config.TERMINAL_GREEN)
    surf.blit(dove, (W//2 - dove.get_width()//2, H//2 - 30))

    stats = [
        f"最終通膨率：{snap['cpi']:.1f}%  ✓",
        f"最終失業率：{snap['unemployment']:.1f}%",
        f"在位月數：{snap['month']} 個月",
        f"最終支持度：{snap['approval']:.0f}%",
    ]
    for i, s in enumerate(stats):
        st = fnt_s.render(s, True, config.GREEN)
        surf.blit(st, (W//2 - st.get_width()//2, H//2 + 60 + i * 30))

    r = fnt_s.render("[ R ] 重新開始   [ Q ] 退出", True, config.TERMINAL_DIM)
    surf.blit(r, (W//2 - r.get_width()//2, H - 80))


def draw_menu(surf, fnt, fnt_big, fnt_s):
    W, H = config.SCREEN_W, config.SCREEN_H
    t_val = pygame.time.get_ticks() / 1000.0
    surf.fill(config.TERMINAL_BG)
    for ly in range(0, H, 3):
        pygame.draw.line(surf, (0,0,0), (0, ly), (W, ly), 1)

    col_title = (
        int(60 + 40 * math.sin(t_val)),
        int(200 + 40 * math.cos(t_val * 0.8)),
        int(80 + 40 * math.sin(t_val * 1.3)),
    )
    t = fnt_big.render("軟著陸之夢：鮑威爾的週一", True, col_title)
    surf.blit(t, (W//2 - t.get_width()//2, H//4))

    st = fnt.render("Soft Landing: Powell's Monday", True, config.TERMINAL_DIM)
    surf.blit(st, (W//2 - st.get_width()//2, H//4 + 60))

    lines = [
        "你是聯準會主席 Jerome Powell。",
        "走進整座華盛頓城——咖啡廳、超市、公園、國會、華爾街、新聞室。",
        "和民眾對話、玩小遊戲、處理黑天鵝事件，用利率政策拯救經濟。",
        "",
        "WASD / 方向鍵：移動",
        "E：互動（門/NPC/物件）",
        "P：開啟手機（隨時隨地調整利率）",
        "Q：開啟任務日誌",
        "SPACE / Enter：對話、確認    ESC：取消",
        "目標：24個月內讓CPI穩定在2%附近",
    ]
    for i, line in enumerate(lines):
        col = config.TERMINAL_GREEN if line else config.BLACK
        lt = fnt_s.render(line, True, col)
        surf.blit(lt, (W//2 - lt.get_width()//2, H//2 + i * 28))

    blink = (pygame.time.get_ticks() // 600) % 2 == 0
    if blink:
        start = fnt.render("[ ENTER ] 開始遊戲", True, config.TERMINAL_AMBER)
        surf.blit(start, (W//2 - start.get_width()//2, H - 80))


def draw_quest_log(surf, quest_log, fnt, fnt_big, fnt_s):
    W, H = config.SCREEN_W, config.SCREEN_H
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 180))
    surf.blit(dim, (0, 0))

    bw, bh = 700, 520
    bx, by = W//2 - bw//2, H//2 - bh//2
    pygame.draw.rect(surf, (20, 25, 40), pygame.Rect(bx, by, bw, bh), border_radius=10)
    pygame.draw.rect(surf, config.TERMINAL_AMBER, pygame.Rect(bx, by, bw, bh), border_radius=10, width=2)

    t = fnt_big.render("📋 任務日誌", True, config.TERMINAL_AMBER)
    surf.blit(t, (bx + bw//2 - t.get_width()//2, by + 24))

    y = by + 90
    for q in quest_log.quests:
        col = config.GREEN if q.done else config.WHITE
        mark = "✓" if q.done else "○"
        head = fnt.render(f"{mark} {q.title}", True, col)
        surf.blit(head, (bx + 30, y))
        desc = fnt_s.render(q.desc, True, config.LIGHT_GRAY)
        surf.blit(desc, (bx + 60, y + 28))
        rew = fnt_s.render(f"獎勵：{q.reward_text}", True, config.TERMINAL_DIM)
        surf.blit(rew, (bx + 60, y + 50))
        y += 76

    nav = fnt_s.render("[ Q / ESC ] 關閉", True, config.TERMINAL_DIM)
    surf.blit(nav, (bx + bw//2 - nav.get_width()//2, by + bh - 36))


def draw_transition(surf, progress, target_label, fnt_big):
    """Fade-to-black transition."""
    W, H = config.SCREEN_W, config.SCREEN_H
    alpha = int(min(255, abs(progress - 0.5) * -510 + 255))
    overlay = pygame.Surface((W, H))
    overlay.fill(config.BLACK)
    overlay.set_alpha(255 - alpha)
    surf.blit(overlay, (0, 0))
    if progress > 0.3 and progress < 0.7:
        t = fnt_big.render(f"→ {target_label}", True, config.TERMINAL_AMBER)
        surf.blit(t, (W//2 - t.get_width()//2, H//2 - 20))


def draw_phone(surf, economy, fnt, fnt_big, fnt_s):
    """Draw a smartphone-style FFR control overlay. World stays visible."""
    W, H = config.SCREEN_W, config.SCREEN_H
    snap = economy.snapshot()

    # Dim background slightly
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 100))
    surf.blit(dim, (0, 0))

    # Phone body (centered, portrait orientation)
    pw, ph = 360, 620
    px, py = W//2 - pw//2, H//2 - ph//2

    # Outer phone body
    pygame.draw.rect(surf, (25, 25, 30), pygame.Rect(px-8, py-8, pw+16, ph+16), border_radius=32)
    pygame.draw.rect(surf, (50, 50, 55), pygame.Rect(px-8, py-8, pw+16, ph+16), border_radius=32, width=2)
    # Speaker
    pygame.draw.rect(surf, (15, 15, 18), pygame.Rect(px + pw//2 - 30, py - 2, 60, 4), border_radius=2)

    # Screen
    pygame.draw.rect(surf, (12, 18, 28), pygame.Rect(px, py, pw, ph), border_radius=18)

    # Status bar
    pygame.draw.rect(surf, (8, 12, 20), pygame.Rect(px, py, pw, 28))
    import datetime as _dt
    t_str = _dt.datetime.now().strftime("%H:%M")
    tt = fnt_s.render(t_str, True, config.TERMINAL_GREEN)
    surf.blit(tt, (px + 14, py + 6))
    bat = fnt_s.render("📶 5G   🔋", True, config.TERMINAL_GREEN)
    surf.blit(bat, (px + pw - bat.get_width() - 14, py + 6))

    # App header
    pygame.draw.rect(surf, (20, 28, 44), pygame.Rect(px, py + 28, pw, 56))
    app = fnt.render("📱 FED Mobile", True, config.TERMINAL_AMBER)
    surf.blit(app, (px + pw//2 - app.get_width()//2, py + 40))
    sub = fnt_s.render("聯邦基金利率控制", True, config.TERMINAL_DIM)
    surf.blit(sub, (px + pw//2 - sub.get_width()//2, py + 64))

    # Big FFR display
    cy = py + 110
    pygame.draw.rect(surf, (8, 18, 30), pygame.Rect(px + 20, cy, pw - 40, 130), border_radius=10)
    pygame.draw.rect(surf, config.TERMINAL_DIM, pygame.Rect(px + 20, cy, pw - 40, 130), border_radius=10, width=1)
    label = fnt_s.render("FFR", True, config.TERMINAL_DIM)
    surf.blit(label, (px + 36, cy + 10))
    ffr_txt = fnt_big.render(f"{snap['ffr']:.2f}", True, config.TERMINAL_GREEN)
    surf.blit(ffr_txt, (px + pw//2 - ffr_txt.get_width()//2, cy + 36))
    pct = fnt.render("%", True, config.TERMINAL_GREEN)
    surf.blit(pct, (px + pw//2 + ffr_txt.get_width()//2 + 4, cy + 56))
    taylor = config.NEUTRAL_RATE + snap["cpi"] - config.TARGET_INFLATION
    rec = fnt_s.render(f"建議：{taylor:.2f}%", True, config.TERMINAL_AMBER)
    surf.blit(rec, (px + pw//2 - rec.get_width()//2, cy + 96))

    # Buttons row
    by = cy + 152
    for i, (label_txt, key_hint) in enumerate([
        ("－1.0", "—"), ("－", "↓"), ("＋", "↑"), ("＋1.0", "+"),
    ]):
        bw = (pw - 50) // 4
        bx = px + 20 + i * (bw + 4)
        col = (60, 100, 60) if i >= 2 else (100, 60, 60)
        pygame.draw.rect(surf, col, pygame.Rect(bx, by, bw, 56), border_radius=8)
        pygame.draw.rect(surf, config.TERMINAL_DIM, pygame.Rect(bx, by, bw, 56), border_radius=8, width=1)
        lt = fnt.render(label_txt, True, config.WHITE)
        surf.blit(lt, (bx + bw//2 - lt.get_width()//2, by + 8))
        kt = fnt_s.render(f"[{key_hint}]", True, config.LIGHT_GRAY)
        surf.blit(kt, (bx + bw//2 - kt.get_width()//2, by + 34))

    # Mini stats
    sy = by + 78
    pygame.draw.rect(surf, (8, 18, 30), pygame.Rect(px + 20, sy, pw - 40, 130), border_radius=10)
    pygame.draw.rect(surf, config.TERMINAL_DIM, pygame.Rect(px + 20, sy, pw - 40, 130), border_radius=10, width=1)
    h = fnt_s.render("即時指標", True, config.TERMINAL_AMBER)
    surf.blit(h, (px + 30, sy + 8))

    inf_lbl, inf_c = economy.inflation_label()
    un_lbl,  un_c  = economy.unemp_label()
    rows = [
        ("通膨 CPI",    f"{snap['cpi']:.1f}%  {inf_lbl}",   inf_c),
        ("失業率",      f"{snap['unemployment']:.1f}%  {un_lbl}", un_c),
        ("支持度",      f"{snap['approval']:.0f}%",           config.GREEN if snap['approval']>40 else config.RED),
        ("第幾個月",    f"{snap['month']} / {config.WIN_MONTHS}", config.LIGHT_GRAY),
    ]
    for i, (k, v, c) in enumerate(rows):
        kt = fnt_s.render(k, True, config.TERMINAL_DIM)
        vt = fnt_s.render(v, True, c)
        ry = sy + 32 + i * 24
        surf.blit(kt, (px + 30, ry))
        surf.blit(vt, (px + pw - 30 - vt.get_width(), ry))

    # Close hint
    hint = fnt_s.render("[ P / ESC ] 收起手機", True, config.TERMINAL_DIM)
    surf.blit(hint, (px + pw//2 - hint.get_width()//2, py + ph - 26))

    # Home button
    pygame.draw.rect(surf, (40, 40, 50), pygame.Rect(px + pw//2 - 30, py + ph - 4, 60, 4), border_radius=2)


def apply_economic_tint(surf, economy):
    """Visual filter based on economy state."""
    if economy.cpi > 6:
        tint = min(120, int((economy.cpi - 6) * 15))
        tint_surf = pygame.Surface((config.SCREEN_W, config.SCREEN_H), pygame.SRCALPHA)
        tint_surf.fill((tint, 0, 0, 40))
        surf.blit(tint_surf, (0, 0))
    elif economy.unemployment > 8:
        tint = min(60, int((economy.unemployment - 8) * 10))
        tint_surf = pygame.Surface((config.SCREEN_W, config.SCREEN_H), pygame.SRCALPHA)
        tint_surf.fill((30, 30, 50, tint))
        surf.blit(tint_surf, (0, 0))
