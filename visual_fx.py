import pygame
import math
import config

_mm_cache = {}       # (scene_name, has_interiors) -> cached Surface
_minimap_font = None # lazy-initialised tiny CJK font for building labels

def _get_minimap_font():
    global _minimap_font
    if _minimap_font is None:
        try:
            path = pygame.font.match_font("microsoftyahei,notosanscjk,arialunicode,arial")
            _minimap_font = pygame.font.Font(path, 10) if path else pygame.font.SysFont("arial", 10)
        except Exception:
            _minimap_font = pygame.font.SysFont("arial", 10)
    return _minimap_font


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
    vals = [s[key] for s in history[-20:] if key in s]
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

    # ── 左側面板：FFR 控制 ────────────────────────────────────────────────────
    panel_x, panel_y = 30, 70
    pygame.draw.rect(surf, (12, 28, 44), pygame.Rect(panel_x, panel_y, 340, 260), border_radius=6)
    pygame.draw.rect(surf, config.TERMINAL_DIM, pygame.Rect(panel_x, panel_y, 340, 260), border_radius=6, width=1)

    t = fnt.render("[ 聯邦基金利率 (FFR) ]", True, config.TERMINAL_AMBER)
    surf.blit(t, (panel_x + 14, panel_y + 10))

    ffr_display = fnt_big.render(f"{snap['ffr']:.2f} %", True, config.TERMINAL_GREEN)
    surf.blit(ffr_display, (panel_x + 14, panel_y + 40))

    hint = fnt_s.render("[ ↑/↓ ] 調整 FFR  [ +/- ] 快速  [ [ / ] ] QT / QE", True, config.TERMINAL_DIM)
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

    # ── 左側面板：QE/QT 控制（新增）─────────────────────────────────────────
    qp_y = panel_y + 272
    pygame.draw.rect(surf, (10, 22, 40), pygame.Rect(panel_x, qp_y, 340, 180), border_radius=6)
    pygame.draw.rect(surf, (40, 80, 130), pygame.Rect(panel_x, qp_y, 340, 180), border_radius=6, width=1)

    qt_title = fnt.render("[ 資產負債表 QE / QT ]", True, (100, 180, 255))
    surf.blit(qt_title, (panel_x + 14, qp_y + 10))

    bs_val = snap.get("balance_sheet", 8.5)
    sr_val = snap.get("shadow_rate", snap["ffr"])
    bs_lbl, bs_col = economy.bs_label()

    bs_big = fnt_big.render(f"${bs_val:.1f}T", True, (100, 220, 255))
    surf.blit(bs_big, (panel_x + 14, qp_y + 38))

    bs_tag = fnt_s.render(bs_lbl, True, bs_col)
    surf.blit(bs_tag, (panel_x + 14 + bs_big.get_width() + 10, qp_y + 54))

    sr_t = fnt_s.render(f"影子利率：{sr_val:.2f}%", True, config.TERMINAL_DIM)
    surf.blit(sr_t, (panel_x + 14, qp_y + 90))

    _bar(surf, panel_x+14, qp_y+130, 308, 14,
         bs_val, 2.0, 15.0, (4.0, 9.0),
         [(80,160,255), config.YELLOW, config.ORANGE],
         "BS($T)", fnt_s)

    qt_hint = fnt_s.render("[ [ ] QT 縮表  /  [ ] ] QE 擴表  每次 $0.1T", True, (60, 100, 160))
    surf.blit(qt_hint, (panel_x + 14, qp_y + 156))

    # ── 中間四個指標面板 ──────────────────────────────────────────────────────
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

    # ── 中間：通膨預期 + 信用利差（新增）────────────────────────────────────
    ie_val = snap.get("inf_exp", 2.5)
    cs_val = snap.get("credit_spread", 1.5)
    ie_lbl, ie_col = economy.inf_exp_label()

    extra_panels = [
        ("通膨預期",  ie_val, 0, 10, (1.5, 3.0), ie_lbl, ie_col),
        ("信用利差",  cs_val, 0,  8, (0.5, 2.5), "", config.TERMINAL_DIM),
    ]
    for i, (label, val, vmin, vmax, good, tag, tag_col) in enumerate(extra_panels):
        iy = 70 + (i + 4) * 90
        pygame.draw.rect(surf, (10, 24, 40), pygame.Rect(ix, iy, 360, 75), border_radius=6)
        pygame.draw.rect(surf, (40, 70, 110), pygame.Rect(ix, iy, 360, 75), border_radius=6, width=1)
        _bar(surf, ix+14, iy+44, 330, 14, val, vmin, vmax, good,
             [(80,160,255), config.YELLOW, config.RED], label, fnt_s)
        vt = fnt.render(f"{val:.2f}", True, (100, 200, 255))
        surf.blit(vt, (ix + 14, iy + 8))
        if tag:
            tg = fnt_s.render(tag, True, tag_col)
            surf.blit(tg, (ix + 14 + vt.get_width() + 8, iy + 14))

    # ── 右側歷史走勢圖 ────────────────────────────────────────────────────────
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
    draw_sparkline(surf, economy.history, "gdp",
                   chart_x+10, chart_y+30, chart_w-20, chart_h-40, config.GREEN)
    draw_sparkline(surf, economy.history, "approval",
                   chart_x+10, chart_y+30, chart_w-20, chart_h-40, config.PURPLE)
    # 新增：資產負債表走勢
    draw_sparkline(surf, economy.history, "balance_sheet",
                   chart_x+10, chart_y+30, chart_w-20, chart_h-40, (100, 200, 255))

    for col, label, ly in [
        (config.ORANGE,    "CPI 通膨率",    chart_y+chart_h-88),
        (config.BLUE,      "失業率",        chart_y+chart_h-72),
        (config.YELLOW,    "FFR 利率",      chart_y+chart_h-55),
        (config.GREEN,     "GDP 成長",      chart_y+chart_h-38),
        (config.PURPLE,    "支持度",        chart_y+chart_h-21),
        ((100, 200, 255),  "資產負債表",    chart_y+chart_h-4),
    ]:
        pygame.draw.rect(surf, col, pygame.Rect(chart_x+10, ly+4, 16, 10))
        lt = fnt_s.render(label, True, config.LIGHT_GRAY)
        surf.blit(lt, (chart_x+32, ly))

    # ── 右側：通膨預期走勢圖（新增）─────────────────────────────────────────
    chart2_y = chart_y + chart_h + 16
    chart2_h = 120
    pygame.draw.rect(surf, (8, 18, 32), pygame.Rect(chart_x, chart2_y, chart_w, chart2_h), border_radius=6)
    pygame.draw.rect(surf, (40, 70, 110), pygame.Rect(chart_x, chart2_y, chart_w, chart2_h), border_radius=6, width=1)
    ct2 = fnt_s.render("[ 通膨預期 & 信用利差 走勢 ]", True, (80, 140, 200))
    surf.blit(ct2, (chart_x + 10, chart2_y + 6))
    draw_sparkline(surf, economy.history, "inf_exp",
                   chart_x+10, chart2_y+24, chart_w-20, chart2_h-34, (255, 160, 60))
    draw_sparkline(surf, economy.history, "credit_spread",
                   chart_x+10, chart2_y+24, chart_w-20, chart2_h-34, (180, 80, 220))
    for col, label, lx in [
        ((255, 160, 60),  "通膨預期", chart_x + 10),
        ((180, 80, 220),  "信用利差", chart_x + 120),
    ]:
        pygame.draw.rect(surf, col, pygame.Rect(lx, chart2_y + chart2_h - 14, 14, 8))
        lt = fnt_s.render(label, True, config.LIGHT_GRAY)
        surf.blit(lt, (lx + 18, chart2_y + chart2_h - 16))

    # ── 底部狀態列 ────────────────────────────────────────────────────────────
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

    # QE/QT 狀態摘要（右側，新增）
    qe_str = (f"BS: ${bs_val:.1f}T   "
              f"影子利率: {sr_val:.2f}%   "
              f"通膨預期: {ie_val:.1f}%   "
              f"信用利差: {cs_val:.2f}%")
    qt_bar = fnt_s.render(qe_str, True, (80, 140, 200))
    surf.blit(qt_bar, (W - qt_bar.get_width() - 12, bar_y + 8))


def draw_hud(surf, economy, fnt_s, scene_name, near_interaction, quest_log):
    snap = economy.snapshot()
    W = config.SCREEN_W

    inf_label, inf_col = economy.inflation_label()
    unemp_label, unemp_col = economy.unemp_label()

    panels = [
        (f"{_scene_label(scene_name)}", config.LIGHT_GRAY),
        (f"第 {snap['month']}/{config.WIN_MONTHS} 月", config.LIGHT_GRAY),
        (f"CPI: {snap['cpi']:.1f}%  {inf_label}", inf_col),
        (f"失業: {snap['unemployment']:.1f}%  {unemp_label}", unemp_col),
        (f"利率: {snap['ffr']:.2f}%", config.TERMINAL_AMBER),
        (f"BS: ${snap.get('balance_sheet', 8.5):.1f}T", (100, 180, 255)),
        (f"支持度: {snap['approval']:.0f}%", config.GREEN if snap['approval'] > 40 else config.RED),
    ]
    for i, (text, col) in enumerate(panels):
        t = fnt_s.render(text, True, col)
        bg = pygame.Surface((t.get_width()+12, t.get_height()+6), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        surf.blit(bg, (8, 8 + i * 26))
        surf.blit(t, (14, 11 + i * 26))

    # Phone hint (bottom-right)
    ph = fnt_s.render("[ P ] 手機", True, config.TERMINAL_AMBER)
    ph_bg = pygame.Surface((ph.get_width()+16, ph.get_height()+8), pygame.SRCALPHA)
    ph_bg.fill((0, 0, 0, 180))
    surf.blit(ph_bg, (W - ph_bg.get_width() - 10, config.SCREEN_H - 36))
    surf.blit(ph, (W - ph.get_width() - 18, config.SCREEN_H - 32))

    # Pending quests in top-right
    pending = quest_log.pending()[:4]
    if pending:
        title = fnt_s.render("任務 [ Q ]", True, config.TERMINAL_AMBER)
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
            alarm = fnt_s.render("通膨失控警報！立刻升息！", True, config.RED)
            surf.blit(alarm, (W//2 - alarm.get_width()//2, 8))


def draw_combat_hud(surf, player, fnt_s):
    H = config.SCREEN_H
    bx, by = 20, H - 88

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

    st_ratio = player.stamina / player.max_stamina
    st_col = (160, 220, 50) if st_ratio > 0.3 else (255, 180, 0)
    pygame.draw.rect(surf, (40, 50, 0),  pygame.Rect(bx, by2 + 12, bw, 5))
    pygame.draw.rect(surf, st_col,       pygame.Rect(bx, by2 + 12, int(bw * st_ratio), 5))

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


def draw_minimap(surf, scene, player, fnt_s, scenes=None):
    """左下角小地圖：顯示當前場景地圖、建築內裝與玩家位置"""
    from scenes import TILE_COLOR
    H = config.SCREEN_H

    max_map_w, max_map_h = 176, 110
    tile_px = min(max_map_w / max(1, scene.cols), max_map_h / max(1, scene.rows))
    map_w = max(1, int(tile_px * scene.cols))
    map_h = max(1, int(tile_px * scene.rows))

    panel_w = map_w + 10
    panel_h = map_h + 30

    px = 10
    py = H - 88 - 14 - panel_h
    map_x = px + 5
    map_y = py + 24

    # Panel background + border
    bg = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    bg.fill((8, 10, 20, 205))
    surf.blit(bg, (px, py))
    pygame.draw.rect(surf, (68, 78, 108), pygame.Rect(px, py, panel_w, panel_h), width=1)

    # Scene label
    label = _scene_label(scene.name)
    lt = fnt_s.render(label, True, config.TERMINAL_AMBER)
    lx = px + 1 + max(0, (map_w + 8 - lt.get_width()) // 2)
    surf.blit(lt, (lx, py + 4))

    # ── Static map surface (cached per scene) ────────────────────────────
    has_interiors = (scenes is not None and scene.name == config.SCENE_CITY)
    cache_key = (scene.name, has_interiors)

    if cache_key not in _mm_cache:
        mm_surf = pygame.Surface((map_w, map_h))
        mm_surf.fill((25, 28, 38))

        # Draw base city / interior tiles
        for ty in range(scene.rows):
            for tx in range(scene.cols):
                tile_id = scene.tiles[ty][tx]
                col = TILE_COLOR.get(tile_id, (75, 75, 85))
                col = (max(0, col[0] - 18), max(0, col[1] - 18), max(0, col[2] - 18))
                x0t = int(tx * tile_px)
                y0t = int(ty * tile_px)
                tw = max(1, int((tx + 1) * tile_px) - x0t)
                th = max(1, int((ty + 1) * tile_px) - y0t)
                pygame.draw.rect(mm_surf, col, pygame.Rect(x0t, y0t, tw, th))

        # For city: overlay each building's full interior tiles + label
        if has_interiors:
            from scenes import CITY_BUILDINGS
            tiny = _get_minimap_font()
            SHORT = {
                config.SCENE_APARTMENT:   "公寓",
                config.SCENE_CAFE:        "咖啡廳",
                config.SCENE_FED:         "聯準會",
                config.SCENE_SUPERMARKET: "超市",
                config.SCENE_GYM:         "健身房",
                config.SCENE_PRESS:       "新聞室",
                config.SCENE_WALL_ST:     "華爾街",
                config.SCENE_CAPITOL:     "國會",
                config.SCENE_BANK:        "銀行",
                config.SCENE_HOSPITAL:    "醫院",
                config.SCENE_UNIVERSITY:  "大學",
            }
            for (bx0_t, by0_t, bx1_t, by1_t, _dx, _dy, sname) in CITY_BUILDINGS:
                interior = scenes.get(sname)
                if interior is None:
                    continue
                # Building footprint on minimap (tile coords are inclusive)
                mm_bx0 = int(bx0_t * tile_px)
                mm_by0 = int(by0_t * tile_px)
                mm_bx1 = int((bx1_t + 1) * tile_px)
                mm_by1 = int((by1_t + 1) * tile_px)
                mm_bw = mm_bx1 - mm_bx0
                mm_bh = mm_by1 - mm_by0
                if mm_bw < 1 or mm_bh < 1:
                    continue
                # Scale interior tiles into the building footprint
                ipx_x = mm_bw / max(1, interior.cols)
                ipx_y = mm_bh / max(1, interior.rows)
                for ity in range(interior.rows):
                    for itx in range(interior.cols):
                        tile_id = interior.tiles[ity][itx]
                        col = TILE_COLOR.get(tile_id, (75, 75, 85))
                        col = (max(0, col[0] - 10), max(0, col[1] - 10), max(0, col[2] - 10))
                        ix0 = mm_bx0 + int(itx * ipx_x)
                        iy0 = mm_by0 + int(ity * ipx_y)
                        iw = max(1, int((itx + 1) * ipx_x) - int(itx * ipx_x))
                        ih = max(1, int((ity + 1) * ipx_y) - int(ity * ipx_y))
                        pygame.draw.rect(mm_surf, col, pygame.Rect(ix0, iy0, iw, ih))
                # Building label (only if it fits)
                short = SHORT.get(sname, "")
                if short:
                    lt_s = tiny.render(short, True, (255, 238, 170))
                    if lt_s.get_width() <= mm_bw - 2 and lt_s.get_height() <= mm_bh - 2:
                        lbx = mm_bx0 + (mm_bw - lt_s.get_width()) // 2
                        lby = mm_by0 + (mm_bh - lt_s.get_height()) // 2
                        lb_bg = pygame.Surface(
                            (lt_s.get_width() + 2, lt_s.get_height() + 2), pygame.SRCALPHA)
                        lb_bg.fill((0, 0, 0, 160))
                        mm_surf.blit(lb_bg, (lbx - 1, lby - 1))
                        mm_surf.blit(lt_s, (lbx, lby))

        _mm_cache[cache_key] = mm_surf

    # Blit cached static map
    surf.blit(_mm_cache[cache_key], (map_x, map_y))

    # Inner border (drawn over map, under player dot)
    pygame.draw.rect(surf, (50, 58, 85),
                     pygame.Rect(map_x - 1, map_y - 1, map_w + 2, map_h + 2), width=1)

    # Player dot — redrawn every frame so it moves smoothly
    pt_x = map_x + int((player.x + player.w / 2) / config.TILE_SIZE * tile_px)
    pt_y = map_y + int((player.y + player.h / 2) / config.TILE_SIZE * tile_px)
    pt_x = max(map_x + 2, min(map_x + map_w - 3, pt_x))
    pt_y = max(map_y + 2, min(map_y + map_h - 3, pt_y))
    dot_r = min(5, max(2, int(tile_px * 0.75)))
    pygame.draw.circle(surf, (255, 55, 55), (pt_x, pt_y), dot_r)
    pygame.draw.circle(surf, (255, 205, 205), (pt_x, pt_y), max(1, dot_r - 1))


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
        config.SCENE_BANK:        "聯邦銀行",
        config.SCENE_HOSPITAL:    "聯邦醫療中心",
        config.SCENE_UNIVERSITY:  "聯邦經濟大學",
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
        "inflation":              ("大通膨時代",   "通膨失控——物價飛漲，民不聊生。",             config.RED),
        "unemployment":           ("硬著陸！",     "失業率暴增——鮑威爾被迫在街頭賣藝。",         config.ORANGE),
        "approval":               ("下台吧！",     "民眾已失去信心，你被迫辭職。",               config.YELLOW),
        "combat":                 ("倒在街頭！",   "你被街頭怪人打倒——主席需要更多保全。",       config.RED),
        "inflation_expectations": ("預期失控！",   "通膨預期嚴重去錨，市場信心崩潰，無力回天。", config.ORANGE),
    }
    title, subtitle, col = titles.get(reason, ("遊戲結束", str(reason), config.RED))
    t = fnt_big.render(title, True, col)
    surf.blit(t, (W//2 - t.get_width()//2, H//3))
    st = fnt.render(subtitle, True, config.LIGHT_GRAY)
    surf.blit(st, (W//2 - st.get_width()//2, H//3 + 80))

    bs_val = snap.get("balance_sheet", 8.5)
    ie_val = snap.get("inf_exp", 2.5)
    stats = [
        f"最終通膨率：{snap['cpi']:.1f}%",
        f"最終失業率：{snap['unemployment']:.1f}%",
        f"在位月數：{snap['month']} 個月",
        f"最終支持度：{snap['approval']:.0f}%",
        f"最終資產負債表：${bs_val:.1f}T",
        f"最終通膨預期：{ie_val:.1f}%",
    ]
    for i, s in enumerate(stats):
        st = fnt_s.render(s, True, config.GRAY)
        surf.blit(st, (W//2 - st.get_width()//2, H//2 + 20 + i * 28))

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

    dove = fnt_big.render("鮑威爾在公園安詳地餵鴿子", True, config.TERMINAL_GREEN)
    surf.blit(dove, (W//2 - dove.get_width()//2, H//2 - 30))

    bs_val = snap.get("balance_sheet", 8.5)
    stats = [
        f"最終通膨率：{snap['cpi']:.1f}%",
        f"最終失業率：{snap['unemployment']:.1f}%",
        f"在位月數：{snap['month']} 個月",
        f"最終支持度：{snap['approval']:.0f}%",
        f"最終資產負債表：${bs_val:.1f}T",
    ]
    for i, s in enumerate(stats):
        st = fnt_s.render(s, True, config.GREEN)
        surf.blit(st, (W//2 - st.get_width()//2, H//2 + 60 + i * 28))

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
        "和民眾對話、玩小遊戲、處理黑天鵝事件，用利率與QE政策拯救經濟。",
        "",
        "WASD / 方向鍵：移動",
        "E：互動（門/NPC/物件）",
        "滑鼠左鍵：射擊（需裝備手槍）    Tab：切換武器（手槍 / 拳頭）",
        "P：開啟手機（隨時隨地調整利率與資產負債表）",
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

    t = fnt_big.render("任務日誌", True, config.TERMINAL_AMBER)
    surf.blit(t, (bx + bw//2 - t.get_width()//2, by + 24))

    y = by + 90
    for q in quest_log.quests:
        col = config.GREEN if q.done else config.WHITE
        mark = "[V]" if q.done else "[ ]"
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
    """手機介面：FFR 控制 + QE/QT 資產負債表控制"""
    W, H = config.SCREEN_W, config.SCREEN_H
    snap = economy.snapshot()

    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 100))
    surf.blit(dim, (0, 0))

    # ── 手機外殼（加高以容納 QE/QT 區塊）────────────────────────────────────
    pw, ph = 360, 760
    px, py = W//2 - pw//2, H//2 - ph//2

    pygame.draw.rect(surf, (25, 25, 30), pygame.Rect(px-8, py-8, pw+16, ph+16), border_radius=32)
    pygame.draw.rect(surf, (50, 50, 55), pygame.Rect(px-8, py-8, pw+16, ph+16), border_radius=32, width=2)
    pygame.draw.rect(surf, (15, 15, 18), pygame.Rect(px + pw//2 - 30, py - 2, 60, 4), border_radius=2)

    # ── 螢幕 ─────────────────────────────────────────────────────────────────
    pygame.draw.rect(surf, (12, 18, 28), pygame.Rect(px, py, pw, ph), border_radius=18)

    # 狀態列
    pygame.draw.rect(surf, (8, 12, 20), pygame.Rect(px, py, pw, 28))
    import datetime as _dt
    t_str = _dt.datetime.now().strftime("%H:%M")
    tt = fnt_s.render(t_str, True, config.TERMINAL_GREEN)
    surf.blit(tt, (px + 14, py + 6))
    bat = fnt_s.render("5G ", True, config.TERMINAL_GREEN)
    surf.blit(bat, (px + pw - bat.get_width() - 14, py + 6))

    # App 標頭
    pygame.draw.rect(surf, (20, 28, 44), pygame.Rect(px, py + 28, pw, 56))
    app = fnt.render("FED Mobile", True, config.TERMINAL_AMBER)
    surf.blit(app, (px + pw//2 - app.get_width()//2, py + 40))
    sub = fnt_s.render("聯準會政策控制中心", True, config.TERMINAL_DIM)
    surf.blit(sub, (px + pw//2 - sub.get_width()//2, py + 64))

    # ── FFR 大數字顯示 ────────────────────────────────────────────────────────
    cy = py + 110
    pygame.draw.rect(surf, (8, 18, 30), pygame.Rect(px + 20, cy, pw - 40, 130), border_radius=10)
    pygame.draw.rect(surf, config.TERMINAL_DIM, pygame.Rect(px + 20, cy, pw - 40, 130), border_radius=10, width=1)
    label = fnt_s.render("FFR  聯邦基金利率", True, config.TERMINAL_DIM)
    surf.blit(label, (px + 36, cy + 10))
    ffr_txt = fnt_big.render(f"{snap['ffr']:.2f}", True, config.TERMINAL_GREEN)
    surf.blit(ffr_txt, (px + pw//2 - ffr_txt.get_width()//2, cy + 36))
    pct = fnt.render("%", True, config.TERMINAL_GREEN)
    surf.blit(pct, (px + pw//2 + ffr_txt.get_width()//2 + 4, cy + 56))
    taylor = config.NEUTRAL_RATE + snap["cpi"] - config.TARGET_INFLATION
    rec = fnt_s.render(f"泰勒規則建議：{taylor:.2f}%", True, config.TERMINAL_AMBER)
    surf.blit(rec, (px + pw//2 - rec.get_width()//2, cy + 96))

    # FFR 按鈕列
    ffr_by = cy + 152
    for i, (label_txt, key_hint) in enumerate([
        ("－1.0", "—"), ("－", "↓"), ("＋", "↑"), ("＋1.0", "+"),
    ]):
        bw_btn = (pw - 50) // 4
        bx_btn = px + 20 + i * (bw_btn + 4)
        col = (60, 100, 60) if i >= 2 else (100, 60, 60)
        pygame.draw.rect(surf, col, pygame.Rect(bx_btn, ffr_by, bw_btn, 56), border_radius=8)
        pygame.draw.rect(surf, config.TERMINAL_DIM, pygame.Rect(bx_btn, ffr_by, bw_btn, 56), border_radius=8, width=1)
        lt = fnt.render(label_txt, True, config.WHITE)
        surf.blit(lt, (bx_btn + bw_btn//2 - lt.get_width()//2, ffr_by + 8))
        kt = fnt_s.render(f"[{key_hint}]", True, config.LIGHT_GRAY)
        surf.blit(kt, (bx_btn + bw_btn//2 - kt.get_width()//2, ffr_by + 34))

    # ── QE / QT 區塊（新增）────────────────────────────────────────────────
    qy = ffr_by + 72
    pygame.draw.rect(surf, (10, 20, 38), pygame.Rect(px + 20, qy, pw - 40, 152), border_radius=10)
    pygame.draw.rect(surf, (40, 80, 130), pygame.Rect(px + 20, qy, pw - 40, 152), border_radius=10, width=1)

    qh = fnt_s.render("資產負債表規模  QE / QT", True, (100, 180, 255))
    surf.blit(qh, (px + pw//2 - qh.get_width()//2, qy + 8))

    bs_val = snap.get("balance_sheet", 8.5)
    sr_val = snap.get("shadow_rate", snap["ffr"])
    bs_lbl, bs_col = economy.bs_label()

    bs_big = fnt_big.render(f"${bs_val:.1f}T", True, (100, 220, 255))
    surf.blit(bs_big, (px + pw//2 - bs_big.get_width()//2, qy + 28))

    bs_tag = fnt_s.render(bs_lbl, True, bs_col)
    surf.blit(bs_tag, (px + pw//2 - bs_tag.get_width()//2, qy + 66))

    # 影子利率 & 通膨預期小字
    ie_val = snap.get("inf_exp", 2.5)
    ie_lbl, ie_col = economy.inf_exp_label()
    sr_t = fnt_s.render(f"影子利率：{sr_val:.2f}%", True, config.TERMINAL_DIM)
    ie_t = fnt_s.render(f"通膨預期：{ie_val:.1f}%  {ie_lbl}", True, ie_col)
    surf.blit(sr_t, (px + 30, qy + 86))
    surf.blit(ie_t, (px + pw - 30 - ie_t.get_width(), qy + 86))

    # QT / QE 兩個大按鈕
    qbw = (pw - 50) // 2
    qb_y = qy + 108
    for i, (label_txt, border_col, btn_col) in enumerate([
        ("QT  縮表  [  [  ]", (180, 80, 80),  (80, 40, 40)),
        ("QE  擴表  [  ]  ]", (60, 180, 100), (30, 80, 50)),
    ]):
        bx_q = px + 20 + i * (qbw + 10)
        pygame.draw.rect(surf, btn_col,    pygame.Rect(bx_q, qb_y, qbw, 36), border_radius=8)
        pygame.draw.rect(surf, border_col, pygame.Rect(bx_q, qb_y, qbw, 36), border_radius=8, width=1)
        lt = fnt_s.render(label_txt, True, config.WHITE)
        surf.blit(lt, (bx_q + qbw//2 - lt.get_width()//2, qb_y + 10))

    # ── 即時指標面板 ──────────────────────────────────────────────────────────
    sy = qy + 162
    pygame.draw.rect(surf, (8, 18, 30), pygame.Rect(px + 20, sy, pw - 40, 110), border_radius=10)
    pygame.draw.rect(surf, config.TERMINAL_DIM, pygame.Rect(px + 20, sy, pw - 40, 110), border_radius=10, width=1)
    h_lbl = fnt_s.render("即時指標", True, config.TERMINAL_AMBER)
    surf.blit(h_lbl, (px + 30, sy + 8))

    inf_lbl, inf_c = economy.inflation_label()
    un_lbl,  un_c  = economy.unemp_label()
    rows = [
        ("通膨 CPI",  f"{snap['cpi']:.1f}%  {inf_lbl}",        inf_c),
        ("失業率",    f"{snap['unemployment']:.1f}%  {un_lbl}", un_c),
        ("GDP",       f"{snap['gdp']:.1f}%",                    config.GREEN if snap['gdp'] > 0 else config.RED),
        ("支持度",    f"{snap['approval']:.0f}%",               config.GREEN if snap['approval'] > 40 else config.RED),
        ("第幾個月",  f"{snap['month']} / {config.WIN_MONTHS}", config.LIGHT_GRAY),
    ]
    for i, (k, v, c) in enumerate(rows):
        kt = fnt_s.render(k, True, config.TERMINAL_DIM)
        vt = fnt_s.render(v, True, c)
        ry = sy + 28 + i * 18
        surf.blit(kt, (px + 30, ry))
        surf.blit(vt, (px + pw - 30 - vt.get_width(), ry))

    # ── 關閉提示 & Home bar ───────────────────────────────────────────────────
    hint = fnt_s.render("[ P / ESC ] 收起手機", True, config.TERMINAL_DIM)
    surf.blit(hint, (px + pw//2 - hint.get_width()//2, py + ph - 26))
    pygame.draw.rect(surf, (40, 40, 50), pygame.Rect(px + pw//2 - 30, py + ph - 4, 60, 4), border_radius=2)


def draw_street_incident(surf, incident, fnt, fnt_s):
    if not incident:
        return
    W = config.SCREEN_W
    t = incident["t"]
    duration = incident.get("duration", 8.0)
    fade = min(1.0, min(t, duration - t) * 2.0)
    alpha = int(fade * 210)

    bw, bh = 680, 72
    bx = W // 2 - bw // 2
    by = config.SCREEN_H - 110

    bg = pygame.Surface((bw, bh), pygame.SRCALPHA)
    bg.fill((10, 18, 30, alpha))
    surf.blit(bg, (bx, by))

    border_surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(border_surf, (255, 180, 0, alpha),
                     pygame.Rect(0, 0, bw, bh), border_radius=8, width=2)
    surf.blit(border_surf, (bx, by))

    title_s = pygame.Surface((bw, 30), pygame.SRCALPHA)
    title_t = fnt.render(incident["title"], True, config.TERMINAL_AMBER)
    title_s.blit(title_t, (bw // 2 - title_t.get_width() // 2, 0))
    title_s.set_alpha(alpha)
    surf.blit(title_s, (bx, by + 8))

    desc_s = pygame.Surface((bw, 24), pygame.SRCALPHA)
    desc_t = fnt_s.render(incident["desc"], True, config.WHITE)
    desc_s.blit(desc_t, (bw // 2 - desc_t.get_width() // 2, 0))
    desc_s.set_alpha(alpha)
    surf.blit(desc_s, (bx, by + 38))


INTRO_SLIDES = [
    {
        "bg": (8, 12, 28),
        "accent": (180, 200, 255),
        "title": "凌晨五點，華盛頓特區",
        "lines": [
            "2023年9月，一個星期一的清晨。",
            "聯準會主席 Jerome Powell 的手機震動了。",
            "",
            "屏幕亮起：CPI 3.2%，失業率 4.1%。",
            "",
            "「還沒降下來……」他喃喃自語，",
            "瞪著天花板，徹夜未眠。",
        ],
        "timeout": 10.0,
    },
    {
        "bg": (28, 8, 8),
        "accent": (255, 180, 80),
        "title": "這不只是數字",
        "lines": [
            "那 3.2% 背後，",
            "是每一個去超市結帳時默默嘆氣的家庭。",
            "",
            "那 4.1% 背後，",
            "是每一封寄出去等待回音的履歷。",
            "",
            "利率調高，企業縮編；",
            "利率調低，通膨死灰復燃。",
        ],
        "timeout": 10.0,
    },
    {
        "bg": (18, 8, 28),
        "accent": (220, 80, 80),
        "title": "所有人都盯著你",
        "lines": [
            "參議員呼籲：「現在就降息！」",
            "市場喊著：「不能降，通膨還沒死！」",
            "白宮暗示：「不要讓經濟衰退！」",
            "教科書警告：「別重蹈1970年代的覆轍！」",
            "",
            "而你，有兩個工具——",
            "聯邦基金利率（FFR）與資產負債表（QE/QT）。",
        ],
        "timeout": 10.0,
    },
    {
        "bg": (8, 20, 12),
        "accent": (60, 220, 100),
        "title": "軟著陸的神話",
        "lines": [
            "1980年代，Volcker 主席用 20% 的利率",
            "終結了大通膨——代價是嚴峻衰退。",
            "",
            "你的任務，是做到前人沒做到的：",
            "在 24 個月內，",
            "不引發大規模失業的前提下，",
            "把通膨壓回 2% 的目標區間。",
        ],
        "timeout": 10.0,
    },
    {
        "bg": (8, 14, 24),
        "accent": (255, 200, 80),
        "title": "今天，從這裡開始",
        "lines": [
            "2023年9月11日，星期一。",
            "你在公寓裡醒來。",
            "",
            "外面的城市正等著你——",
            "咖啡廳、超市、公園、國會、華爾街。",
            "每一個角落，都有你需要聽見的聲音。",
            "",
            "24個月。2%的目標。",
            "一切，從這個星期一開始。",
        ],
        "timeout": 11.0,
    },
]


def _draw_intro_visual(surf, slide_idx, t, x, y, w, h, accent, fnt, fnt_s):
    cx, cy = x + w // 2, y + h // 2

    if slide_idx == 0:
        r = min(w // 2, h // 2) - 20
        pygame.draw.circle(surf, (15, 20, 40), (cx, cy), r)
        pygame.draw.circle(surf, accent, (cx, cy), r, 2)
        for i in range(12):
            a = i * math.pi / 6 - math.pi / 2
            ox = cx + int(r * 0.90 * math.cos(a))
            oy = cy + int(r * 0.90 * math.sin(a))
            ix = cx + int(r * 0.78 * math.cos(a))
            iy = cy + int(r * 0.78 * math.sin(a))
            pygame.draw.line(surf, accent, (ix, iy), (ox, oy), 2)
        ha = 5 / 6 * math.pi * 2 - math.pi / 2
        hx = cx + int(r * 0.52 * math.cos(ha))
        hy = cy + int(r * 0.52 * math.sin(ha))
        pygame.draw.line(surf, config.WHITE, (cx, cy), (hx, hy), 4)
        ma = -math.pi / 2
        mx = cx + int(r * 0.72 * math.cos(ma))
        my = cy + int(r * 0.72 * math.sin(ma))
        pygame.draw.line(surf, config.WHITE, (cx, cy), (mx, my), 3)
        sa = (t % 60) / 60 * math.pi * 2 - math.pi / 2
        sx = cx + int(r * 0.82 * math.cos(sa))
        sy_s = cy + int(r * 0.82 * math.sin(sa))
        pygame.draw.line(surf, config.RED, (cx, cy), (sx, sy_s), 2)
        pygame.draw.circle(surf, accent, (cx, cy), 5)
        tl = fnt.render("05:00  AM", True, accent)
        surf.blit(tl, (cx - tl.get_width() // 2, cy + r + 12))

    elif slide_idx == 1:
        bw = w // 4
        base_y = y + h - 30
        cpi_ratio = 0.55 + 0.12 * math.sin(t * 1.5)
        cpi_h = int((h - 60) * cpi_ratio)
        cpi_x = cx - bw - 12
        pygame.draw.rect(surf, (140, 40, 40),
                         pygame.Rect(cpi_x, base_y - cpi_h, bw, cpi_h), border_radius=3)
        cl = fnt_s.render("CPI", True, config.WHITE)
        vl = fnt_s.render("3.2%", True, (255, 120, 120))
        surf.blit(cl, (cpi_x + bw // 2 - cl.get_width() // 2,
                       base_y - cpi_h - cl.get_height() - 4))
        surf.blit(vl, (cpi_x + bw // 2 - vl.get_width() // 2,
                       base_y - cpi_h - vl.get_height() - cl.get_height() - 8))
        target_y = base_y - int((h - 60) * 0.15)
        pygame.draw.line(surf, config.GREEN,
                         (cpi_x - 5, target_y), (cpi_x + bw + 5, target_y), 1)
        tgt = fnt_s.render("2%", True, config.GREEN)
        surf.blit(tgt, (cpi_x - tgt.get_width() - 4, target_y - 8))
        un_ratio = 0.22 + 0.08 * math.cos(t * 1.2)
        un_h = int((h - 60) * un_ratio)
        un_x = cx + 12
        pygame.draw.rect(surf, (40, 80, 160),
                         pygame.Rect(un_x, base_y - un_h, bw, un_h), border_radius=3)
        ul = fnt_s.render("失業率", True, config.WHITE)
        uvl = fnt_s.render("4.1%", True, (100, 150, 255))
        surf.blit(ul, (un_x + bw // 2 - ul.get_width() // 2,
                       base_y - un_h - ul.get_height() - 4))
        surf.blit(uvl, (un_x + bw // 2 - uvl.get_width() // 2,
                        base_y - un_h - uvl.get_height() - ul.get_height() - 8))
        pygame.draw.line(surf, (60, 60, 80), (x + 10, base_y), (x + w - 10, base_y), 1)

    elif slide_idx == 2:
        dirs = [
            ("降息！",   (-1,  0), config.BLUE),
            ("升息！",   ( 1,  0), config.RED),
            ("別衰退！", ( 0, -1), config.YELLOW),
            ("別通膨！", ( 0,  1), config.ORANGE),
        ]
        anim = 0.65 + 0.15 * math.sin(t * 2.2)
        dist = min(w, h) // 2 - 40
        for msg, (dx, dy), col in dirs:
            tx = cx + int(dx * dist)
            ty = cy + int(dy * dist)
            ex = cx + int(dx * 38)
            ey = cy + int(dy * 38)
            atx = cx + int(dx * dist * anim)
            aty = cy + int(dy * dist * anim)
            pygame.draw.line(surf, col, (atx, aty), (ex, ey), 3)
            ang = math.atan2(ey - aty, ex - atx)
            for da in (0.4, -0.4):
                hx = ex - int(16 * math.cos(ang + da))
                hy = ey - int(16 * math.sin(ang + da))
                pygame.draw.line(surf, col, (ex, ey), (hx, hy), 3)
            lt = fnt_s.render(msg, True, col)
            surf.blit(lt, (tx - lt.get_width() // 2 + int(dx * 24),
                           ty - lt.get_height() // 2 + int(dy * 24)))
        ft = fnt.render("FFR+QE", True, accent)
        surf.blit(ft, (cx - ft.get_width() // 2, cy - ft.get_height() // 2))

    elif slide_idx == 3:
        pivot_y = y + 70
        arm = w // 2 - 20
        tilt = math.sin(t * 0.9) * 0.22
        pygame.draw.line(surf, accent, (cx, pivot_y), (cx, y + h - 30), 4)
        pygame.draw.line(surf, accent,
                         (cx - 20, y + h - 30), (cx + 20, y + h - 30), 4)
        lx_arm = cx - int(arm * math.cos(tilt))
        ly_arm = pivot_y + int(arm * math.sin(tilt))
        rx_arm = cx + int(arm * math.cos(tilt))
        ry_arm = pivot_y - int(arm * math.sin(tilt))
        pygame.draw.line(surf, accent, (lx_arm, ly_arm), (rx_arm, ry_arm), 3)
        pygame.draw.circle(surf, accent, (cx, pivot_y), 8)
        pan_r = 26
        rope_l = 50
        lp_x, lp_y = lx_arm, ly_arm + rope_l
        pygame.draw.line(surf, (160, 160, 160), (lx_arm, ly_arm), (lp_x, lp_y), 2)
        pygame.draw.circle(surf, (180, 80, 60), (lp_x, lp_y + pan_r), pan_r)
        inf_l = fnt_s.render("通膨", True, config.WHITE)
        surf.blit(inf_l, (lp_x - inf_l.get_width() // 2, lp_y + pan_r * 2 + 6))
        rp_x, rp_y = rx_arm, ry_arm + rope_l
        pygame.draw.line(surf, (160, 160, 160), (rx_arm, ry_arm), (rp_x, rp_y), 2)
        pygame.draw.circle(surf, (60, 140, 100), (rp_x, rp_y + pan_r), pan_r)
        rec_l = fnt_s.render("衰退", True, config.WHITE)
        surf.blit(rec_l, (rp_x - rec_l.get_width() // 2, rp_y + pan_r * 2 + 6))
        tgt = fnt_s.render("軟著陸", True, accent)
        surf.blit(tgt, (cx - tgt.get_width() // 2, y + h - 24))

    else:
        base_y = y + h - 20
        sun_rise = min(1.0, t / 5.0)
        sun_cy = base_y - 20 - int((h - 40) * 0.52 * sun_rise)
        pygame.draw.circle(surf, (255, 180, 60), (cx, sun_cy), 35)
        blds = [
            (x + 10,  70, 40), (x + 58, 100, 35), (x + 101, 55, 45),
            (x + 154, 120, 38), (x + 200, 85, 50), (x + 258, 110, 42),
            (x + 308, 65, 55), (x + 371, 130, 36), (x + 415, 90, 48),
        ]
        for bx_bld, bh_bld, bw_bld in blds:
            if bx_bld + bw_bld > x + w:
                break
            pygame.draw.rect(surf, (20, 25, 45),
                             pygame.Rect(bx_bld, base_y - bh_bld, bw_bld, bh_bld))
            for wy in range(base_y - bh_bld + 8, base_y - 8, 14):
                for wx in range(bx_bld + 5, bx_bld + bw_bld - 5, 10):
                    if (wx * 7 + wy * 13) % 5 != 0:
                        lit = int(200 * sun_rise + 55)
                        pygame.draw.rect(surf, (lit, int(lit * 0.9), 60),
                                         pygame.Rect(wx, wy, 5, 7))
        ml = fnt.render("星期一  早晨", True, accent)
        surf.blit(ml, (cx - ml.get_width() // 2, base_y - ml.get_height() - 2))


def draw_intro(surf, slide_idx, slide_t, fnt, fnt_big, fnt_s):
    W, H = config.SCREEN_W, config.SCREEN_H
    slide  = INTRO_SLIDES[slide_idx]
    bg     = slide["bg"]
    accent = slide["accent"]
    lines  = slide["lines"]

    surf.fill(bg)
    for ly in range(0, H, 6):
        pygame.draw.line(surf, (0, 0, 0), (0, ly), (W, ly), 1)

    panel_w = W * 3 // 5

    ts = fnt_big.render(slide["title"], True, accent)
    surf.blit(ts, (60, 72))
    pygame.draw.line(surf, accent,
                     (60, 72 + ts.get_height() + 5),
                     (60 + ts.get_width(), 72 + ts.get_height() + 5), 2)

    TYPE_SPEED = 26
    total_typed = int(slide_t * TYPE_SPEED)
    chars_consumed = 0
    all_shown = True
    ty = 148
    for line in lines:
        if line == "":
            ty += 22
            continue
        to_show = min(len(line), max(0, total_typed - chars_consumed))
        if to_show > 0:
            lt = fnt.render(line[:to_show], True, config.WHITE)
            surf.blit(lt, (60, ty))
            if to_show < len(line):
                cx_cur = 60 + lt.get_width() + 3
                if (pygame.time.get_ticks() // 260) % 2 == 0:
                    pygame.draw.rect(surf, accent,
                                     pygame.Rect(cx_cur, ty + 3, 10, fnt.get_height() - 6))
                all_shown = False
        else:
            all_shown = False
        chars_consumed += len(line)
        ty += 36

    rp_x = panel_w + 20
    rp_y = 60
    rp_w = W - panel_w - 40
    rp_h = H - 120
    _draw_intro_visual(surf, slide_idx, slide_t, rp_x, rp_y, rp_w, rp_h, accent, fnt, fnt_s)

    show_hint = all_shown or slide_t > 4.5
    if show_hint and (pygame.time.get_ticks() // 520) % 2 == 0:
        is_last = slide_idx >= len(INTRO_SLIDES) - 1
        hint_str = "[ ENTER / SPACE ]  開始遊戲" if is_last else "[ ENTER / SPACE ]  繼續"
        ht = fnt_s.render(hint_str, True, accent)
        surf.blit(ht, (W // 2 - ht.get_width() // 2, H - 70))

    skip = fnt_s.render("[ ESC ]  跳至主選單", True, (80, 80, 100))
    surf.blit(skip, (W - skip.get_width() - 20, H - 30))

    n = len(INTRO_SLIDES)
    dot_cx = W // 2
    for i in range(n):
        dx = dot_cx - (n - 1) * 12 + i * 24
        r = 7 if i == slide_idx else 4
        c = accent if i == slide_idx else (50, 50, 70)
        pygame.draw.circle(surf, c, (dx, H - 44), r)


def draw_guitar_video(surf, fnt, fnt_big, fnt_s, t):
    W, H = config.SCREEN_W, config.SCREEN_H
    surf.fill((12, 4, 4))

    # Scanline texture
    for ly in range(0, H, 4):
        pygame.draw.line(surf, (0, 0, 0), (0, ly), (W, ly), 1)

    # Falling snowflakes (deterministic via sin/cos so no random seed needed)
    for i in range(72):
        phase = i * 2.618
        sx = (math.cos(phase) * W * 0.48 + W * 0.5 + t * (12 + i % 8)) % W
        sy = (math.sin(phase * 1.3) * H * 0.38 + H * 0.5 + t * (22 + i % 14)) % H
        sr = 2 + (i % 3)
        pygame.draw.circle(surf, (210, 230, 255), (int(sx), int(sy)), sr)

    # Stage spotlights
    for i in range(3):
        angle = math.sin(t * 0.8 + i * 2.1) * 0.4
        lx = W // 4 + i * W // 4
        pts = [
            (lx, 0),
            (lx + int(110 * math.sin(angle + 0.35)), H // 2),
            (lx + int(110 * math.sin(angle - 0.35)), H // 2),
        ]
        light = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.polygon(light, (255, 210, 120, 18), pts)
        surf.blit(light, (0, 0))

    # Banner
    pygame.draw.rect(surf, (110, 8, 8), pygame.Rect(0, 28, W, 66))
    pygame.draw.line(surf, (200, 20, 20), (0, 28), (W, 28), 2)
    pygame.draw.line(surf, (200, 20, 20), (0, 93), (W, 93), 2)
    title_t = fnt_big.render("All I Want for Christmas Is You", True, config.GOLD)
    surf.blit(title_t, (W // 2 - title_t.get_width() // 2, 36))
    sub_t = fnt_s.render("Mariah Carey  /  演奏：鮑威爾（聖誕女郎特別版）", True, config.PINK)
    surf.blit(sub_t, (W // 2 - sub_t.get_width() // 2, 72))

    # Character center position with body-bob
    pcx = W // 2
    pcy = H // 2 + 20 + int(5 * math.sin(t * 4.2))

    # Christmas dress (red trapezoid)
    pygame.draw.polygon(surf, (190, 18, 18), [
        (pcx - 22, pcy - 10),
        (pcx + 22, pcy - 10),
        (pcx + 36, pcy + 70),
        (pcx - 36, pcy + 70),
    ])
    # White fur trim at dress top and hem
    pygame.draw.polygon(surf, config.WHITE, [
        (pcx - 22, pcy - 10),
        (pcx + 22, pcy - 10),
        (pcx + 24, pcy - 2),
        (pcx - 24, pcy - 2),
    ])
    pygame.draw.rect(surf, config.WHITE, pygame.Rect(pcx - 36, pcy + 62, 72, 10), border_radius=4)

    # Head
    pygame.draw.circle(surf, (215, 175, 128), (pcx, pcy - 28), 20)

    # Gray-white hair (sides + slight top tuft visible under hat)
    hair_col = (210, 210, 215)
    pygame.draw.ellipse(surf, hair_col, pygame.Rect(pcx - 20, pcy - 44, 12, 18))  # left side
    pygame.draw.ellipse(surf, hair_col, pygame.Rect(pcx + 8,  pcy - 44, 12, 18))  # right side
    pygame.draw.ellipse(surf, hair_col, pygame.Rect(pcx - 8,  pcy - 48, 16, 8))   # top tuft

    # Santa hat
    pygame.draw.polygon(surf, (190, 18, 18), [
        (pcx - 16, pcy - 45),
        (pcx + 16, pcy - 45),
        (pcx + 6,  pcy - 76),
    ])
    pygame.draw.rect(surf, config.WHITE, pygame.Rect(pcx - 18, pcy - 48, 36, 8), border_radius=4)
    pygame.draw.circle(surf, config.WHITE, (pcx + 6, pcy - 76), 5)

    # Eyes
    pygame.draw.circle(surf, (40, 25, 15), (pcx - 7, pcy - 31), 3)
    pygame.draw.circle(surf, (40, 25, 15), (pcx + 7, pcy - 31), 3)

    # Glasses (thin gold frames)
    glass_col = (180, 150, 60)
    pygame.draw.rect(surf, glass_col, pygame.Rect(pcx - 16, pcy - 35, 12, 9), border_radius=2, width=2)
    pygame.draw.rect(surf, glass_col, pygame.Rect(pcx + 4,  pcy - 35, 12, 9), border_radius=2, width=2)
    pygame.draw.line(surf, glass_col, (pcx - 4, pcy - 31), (pcx + 4, pcy - 31), 1)  # bridge
    pygame.draw.line(surf, glass_col, (pcx - 16, pcy - 31), (pcx - 20, pcy - 29), 1)  # left arm
    pygame.draw.line(surf, glass_col, (pcx + 16, pcy - 31), (pcx + 20, pcy - 29), 1)  # right arm

    # Smile
    pygame.draw.arc(surf, (180, 80, 80),
                    pygame.Rect(pcx - 9, pcy - 20, 18, 10),
                    math.pi, 0, 2)

    # Left arm (holding guitar neck)
    pygame.draw.line(surf, (215, 175, 128),
                     (pcx - 22, pcy - 4),
                     (pcx - 58, pcy + 28), 6)

    # Right arm (strumming — oscillates)
    strum = int(10 * math.sin(t * 8.5))
    pygame.draw.line(surf, (215, 175, 128),
                     (pcx + 22, pcy - 4),
                     (pcx + 52 + strum, pcy + 38), 6)

    # Guitar body (figure-8, left of center)
    gx, gy = pcx - 68, pcy + 10
    pygame.draw.ellipse(surf, (110, 62, 18), pygame.Rect(gx, gy, 52, 38))
    pygame.draw.ellipse(surf, (110, 62, 18), pygame.Rect(gx + 6, gy - 24, 40, 30))
    pygame.draw.ellipse(surf, (150, 85, 28), pygame.Rect(gx + 2, gy + 2, 48, 34), width=2)
    # Sound hole
    pygame.draw.circle(surf, (55, 28, 8), (gx + 26, gy + 19), 9)
    pygame.draw.circle(surf, (80, 40, 12), (gx + 26, gy + 19), 9, width=1)
    # Neck (going up-left to left hand)
    pygame.draw.rect(surf, (90, 52, 12), pygame.Rect(gx + 18, gy - 24 - 68, 16, 72))
    # Frets
    for fi in range(4):
        fy = gy - 24 - 60 + fi * 16
        pygame.draw.line(surf, (180, 140, 60), (gx + 18, fy), (gx + 34, fy), 1)
    # Strings (vibrating)
    for si in range(3):
        sx_s = gx + 22 + si * 5
        vib = int(3 * math.sin(t * 14.0 + si * 1.8))
        pygame.draw.line(surf, (200, 190, 110),
                         (sx_s, gy - 24 - 60),
                         (sx_s + vib, gy + 34), 1)

    # Floating music notes
    note_syms = ["#", "~", "o", "*", "#", "~", "o", "*"]
    note_cols = [
        config.GOLD, config.PINK, (180, 100, 240), config.WHITE,
        config.PINK, config.GOLD, config.WHITE, (180, 100, 240),
    ]
    for i in range(8):
        angle_n = t * 0.55 + i * 0.785
        orbit_x = pcx + int((260 + 40 * math.cos(angle_n * 1.3)) * math.cos(angle_n))
        orbit_y = pcy - 20 + int((130 + 20 * math.sin(angle_n * 0.9)) * math.sin(angle_n))
        if 0 <= orbit_x < W and 0 <= orbit_y < H:
            nt = fnt.render(note_syms[i], True, note_cols[i])
            scale = 0.7 + 0.3 * math.sin(t * 1.5 + i)
            if scale > 0.5:
                surf.blit(nt, (orbit_x, orbit_y))

    # Progress bar
    total = 28.0
    prog = min(1.0, t / total)
    pygame.draw.rect(surf, (50, 12, 12), pygame.Rect(60, H - 44, W - 120, 10), border_radius=5)
    pygame.draw.rect(surf, (200, 20, 20), pygame.Rect(60, H - 44, int((W - 120) * prog), 10), border_radius=5)
    elapsed = fnt_s.render(f"{int(t // 60):02d}:{int(t % 60):02d}", True, config.LIGHT_GRAY)
    surf.blit(elapsed, (60, H - 60))
    dur = fnt_s.render(f"0:28", True, config.LIGHT_GRAY)
    surf.blit(dur, (W - 60 - dur.get_width(), H - 60))

    # LIVE badge
    if int(t * 2) % 2 == 0:
        pygame.draw.rect(surf, (160, 10, 10), pygame.Rect(W - 88, 32, 64, 24), border_radius=5)
        live = fnt_s.render("LIVE", True, config.WHITE)
        surf.blit(live, (W - 88 + 32 - live.get_width() // 2, 38))

    # ESC hint
    hint = fnt_s.render("[ ESC / Enter ]  關閉影片", True, (100, 100, 120))
    surf.blit(hint, (W // 2 - hint.get_width() // 2, H - 24))


def apply_economic_tint(surf, economy):
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

