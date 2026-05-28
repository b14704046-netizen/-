import sys
import math
import random
import pygame
import config
import sounds
from economy_core import EconomyState
from entities import Player, Camera, Bullet, Enemy
from scenes import build_all_scenes, draw_scene, draw_city_signs
from manager import GameManager
from dialog import get_dialog, draw_dialog
from minigames import create_minigame, draw_result
from quests import QuestLog
from visual_fx import (
    draw_terminal, draw_hud, draw_event,
    draw_gameover, draw_win, draw_menu,
    draw_quest_log, draw_transition,
    apply_economic_tint, draw_phone,
    draw_combat_hud, draw_street_incident,
    draw_intro, INTRO_SLIDES,
    draw_guitar_video,
    draw_minimap,
)


def make_fonts():
    pygame.font.init()
    try:
        path = pygame.font.match_font(
            "microsoftyahei,notosanscjk,arialunicode,arial")
        fnt_s = pygame.font.Font(
            path, 16) if path else pygame.font.SysFont("arial", 16)
        fnt = pygame.font.Font(
            path, 20) if path else pygame.font.SysFont("arial", 20)
        fnt_big = pygame.font.Font(
            path, 32) if path else pygame.font.SysFont("arial", 32)
    except Exception:
        fnt_s = pygame.font.SysFont("arial", 16)
        fnt = pygame.font.SysFont("arial", 20)
        fnt_big = pygame.font.SysFont("arial", 32)
    return fnt_s, fnt, fnt_big


def new_game():
    economy = EconomyState()
    player = Player()
    camera = Camera()
    scenes = build_all_scenes()
    manager = GameManager(economy, camera)
    quests = QuestLog()
    quests.reset(economy)
    # Start in apartment
    scene = scenes[config.SCENE_APARTMENT]
    player.set_tile(*scene.spawn)
    camera.snap(player.x + player.w/2, player.y + player.h/2, scene)
    return economy, player, camera, scenes, scene, manager, quests


def main():
    pygame.mixer.pre_init(22050, -16, 2, 512)
    pygame.init()
    sounds.init()
    screen = pygame.display.set_mode((config.SCREEN_W, config.SCREEN_H))
    pygame.display.set_caption(config.TITLE)
    clock = pygame.time.Clock()
    fnt_s, fnt, fnt_big = make_fonts()

    economy, player, camera, scenes, scene, manager, quests = new_game()

    state = config.STATE_INTRO
    prev_state = config.STATE_WORLD
    sim_timer = 0.0
    event_sel = 0
    lose_reason = None
    intro_slide = 0
    intro_slide_t = 0.0
    dialog_choice_sel = 0
    dialog_pages = []
    dialog_page = 0
    current_minigame = None
    minigame_kind = None
    result_screen = None      # holds mg result dict while shown
    # {"t": 0, "target": scene_obj, "spawn":(x,y), "label": str}
    transition = None
    bullets = []
    enemies = []
    enemy_spawn_t = random.uniform(8.0, 14.0)
    walk_snd_t = 0.0
    guitar_video_t = 0.0

    world_surf = pygame.Surface((config.SCREEN_W, config.SCREEN_H))

    running = True
    while running:
        dt = clock.tick(config.FPS) / 1000.0
        keys = pygame.key.get_pressed()

        # ── Event handling ───────────────────────────────────────────
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

            elif ev.type == pygame.KEYDOWN:

                if state == config.STATE_INTRO:
                    if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                        intro_slide += 1
                        intro_slide_t = 0.0
                        if intro_slide >= len(INTRO_SLIDES):
                            intro_slide = 0
                            state = config.STATE_MENU
                    elif ev.key == pygame.K_ESCAPE:
                        intro_slide = 0
                        state = config.STATE_MENU

                elif state == config.STATE_MENU:
                    if ev.key == pygame.K_RETURN:
                        state = config.STATE_WORLD

                elif state == config.STATE_WORLD:
                    if ev.key == pygame.K_TAB:
                        player.switch_weapon()
                    elif ev.key == pygame.K_e:
                        inter = player.find_interaction(scene)
                        if inter:
                            kind, target = inter
                            if kind == "door":
                                sounds.play('door')
                                target_scene = scenes[target["target"]]
                                transition = {
                                    "t": 0.0,
                                    "target_scene": target_scene,
                                    "spawn": (target["spawn_tx"], target["spawn_ty"]),
                                    "label": _scene_label(target["target"]),
                                }
                                prev_state = state
                                state = config.STATE_TRANSITION
                            elif kind == "npc":
                                sounds.play('tick', 0.25)
                                dialog_pages = get_dialog(
                                    target.dialog_id, economy)
                                dialog_page = 0
                                dialog_choice_sel = 0
                                state = config.STATE_DIALOG
                                quests.note_dialog(economy)
                            elif kind == "object":
                                otype = target["type"]
                                if otype == "terminal":
                                    state = config.STATE_TERMINAL
                                elif otype == "bed":
                                    # Sleep: advance time
                                    for _ in range(3):
                                        economy.update()
                                        if economy.lose_reason():
                                            break
                                    manager.post_message("一夜好眠... 3個月過去了")
                                elif otype == "coffee_mg":
                                    current_minigame = create_minigame(
                                        config.MG_COFFEE)
                                    minigame_kind = "coffee"
                                    state = config.STATE_MINIGAME
                                elif otype == "press_mg" or otype == "testify":
                                    current_minigame = create_minigame(
                                        config.MG_PRESS)
                                    minigame_kind = "press"
                                    state = config.STATE_MINIGAME
                                elif otype == "pigeon_mg":
                                    current_minigame = create_minigame(
                                        config.MG_PIGEON)
                                    minigame_kind = "pigeon"
                                    state = config.STATE_MINIGAME
                                elif otype == "treadmill_mg":
                                    current_minigame = create_minigame(
                                        config.MG_TREADMILL)
                                    minigame_kind = "treadmill"
                                    state = config.STATE_MINIGAME
                                elif otype == "coffee":  # apartment coffee
                                    current_minigame = create_minigame(
                                        config.MG_COFFEE)
                                    minigame_kind = "coffee"
                                    state = config.STATE_MINIGAME
                                elif otype == "tv":
                                    manager.post_message(
                                        f"新聞：CPI {economy.cpi:.1f}%，失業 {economy.unemployment:.1f}%。"
                                    )
                                elif otype == "books":
                                    manager.post_message("讀經濟學...頭腦清醒了。")
                                    economy.approval = min(
                                        100, economy.approval + 1)
                                elif otype == "price_check":
                                    label = target.get("label", "")
                                    price = int(5 * (1 + economy.cpi / 5))
                                    manager.post_message(
                                        f"{label}：${price} ({'↑' if economy.cpi > 4 else '正常'})")
                                elif otype == "ticker":
                                    manager.post_message(
                                        f"S&P {3000 + int(economy.gdp * 50)} ({'+' if economy.gdp > 0 else ''}{economy.gdp:.1f}%)"
                                    )
                                elif otype == "newspaper":
                                    if economy.cpi > 8:
                                        headline = f"頭條：通膨飆至 {economy.cpi:.1f}%！恐慌蔓延"
                                    elif economy.unemployment > 7:
                                        headline = f"頭條：失業率 {economy.unemployment:.1f}%，就業市場崩潰"
                                    elif economy.cpi < 2.5 and economy.month > 4:
                                        headline = "頭條：物價趨穩！軟著陸真的有望？"
                                    elif economy.gdp < 0:
                                        headline = f"頭條：GDP 負成長 {economy.gdp:.1f}%，衰退警報"
                                    else:
                                        headline = f"頭條：FED 利率 {economy.ffr:.2f}%，市場觀望"
                                    manager.post_message(headline)
                                elif otype == "atm":
                                    balance = int(50000 * max(0.3, 1 + economy.gdp / 20))
                                    manager.post_message(
                                        f"帳戶餘額：${balance:,}  利息：{economy.ffr:.2f}%/年")
                                elif otype == "graffiti":
                                    if economy.cpi > 6:
                                        msg = "塗鴉：「INFLATION IS THEFT」"
                                    elif economy.unemployment > 7:
                                        msg = "塗鴉：「NO JOBS NO PEACE」"
                                    elif economy.approval < 30:
                                        msg = "塗鴉：「POWELL GO HOME」"
                                    else:
                                        msg = "塗鴉：「Soft Landing When?」"
                                    manager.post_message(msg)
                                elif otype == "fridge":
                                    egg = int(4 * (1 + economy.cpi / 5))
                                    milk = int(3 * (1 + economy.cpi / 5))
                                    bread = int(2 * (1 + economy.cpi / 5))
                                    manager.post_message(
                                        f"冰箱：雞蛋 ${egg}  牛奶 ${milk}  麵包 ${bread}")
                                elif otype == "bulletin":
                                    rent_hike = int(economy.cpi * 1.5)
                                    manager.post_message(
                                        f"公告欄：本月租金調漲 {rent_hike}%  CPI {economy.cpi:.1f}%")
                                elif otype == "fountain_coin":
                                    import random as _r
                                    if _r.random() < 0.35:
                                        economy.approval = min(100, economy.approval + 1)
                                        manager.post_message("硬幣落入水中... 願望成真！支持度 +1")
                                    else:
                                        manager.post_message("硬幣沉入水底... 願望石沉大海。")
                                elif otype == "big_board":
                                    sp = 3000 + int(economy.gdp * 50)
                                    bond = economy.ffr + 1.2
                                    vix = max(10, int(30 - economy.gdp * 2 + economy.cpi))
                                    manager.post_message(
                                        f"S&P {sp}  |  10Y {bond:.2f}%  |  VIX {vix}")
                                elif otype == "vend":
                                    if player.hp < player.max_hp:
                                        player.hp = min(player.max_hp, player.hp + 25)
                                        cost = int(3 * (1 + economy.cpi / 10))
                                        manager.post_message(
                                            f"買了飲料！恢復 25 血量。花費 ${cost}")
                                    else:
                                        manager.post_message("血量已滿，不需要飲料。")
                                elif otype == "workout":
                                    economy.approval = min(100, economy.approval + 3)
                                    player.hp = min(player.max_hp, player.hp + 10)
                                    manager.post_message("鍛煉完成！肌肉充實。支持度 +3")
                                elif otype == "policy_memo":
                                    taylor = (config.NEUTRAL_RATE
                                              + economy.cpi - config.TARGET_INFLATION)
                                    if economy.ffr > taylor + 0.5:
                                        rec = f"建議考慮降息（Taylor {taylor:.2f}%）"
                                    elif economy.ffr < taylor - 0.5:
                                        rec = f"建議繼續升息（Taylor {taylor:.2f}%）"
                                    else:
                                        rec = f"利率大致適中（Taylor {taylor:.2f}%）"
                                    manager.post_message(f"政策備忘錄：{rec}")
                                elif otype == "vault":
                                    top1 = int(10 + economy.gdp * 3 + economy.ffr * 0.5)
                                    mid = max(20, int(60 - economy.cpi))
                                    manager.post_message(
                                        f"金庫報告：頂層 1% 資產佔 {top1}%，"
                                        f"中產財富 {mid}%")
                                elif otype == "checkup":
                                    heal = int(40 + economy.approval / 5)
                                    player.hp = min(player.max_hp, player.hp + heal)
                                    manager.post_message(
                                        f"健康檢查完成！恢復 {heal} 血量。請多休息。")
                                elif otype == "wifi_news":
                                    if economy.cpi > 7:
                                        news = (f"[新聞] 通膨 {economy.cpi:.1f}%！"
                                                "民眾搶購囤積！")
                                    elif economy.unemployment > 7:
                                        news = (f"[新聞] 失業率 {economy.unemployment:.1f}%！"
                                                "就業市場警報！")
                                    elif economy.gdp < 0:
                                        news = "[新聞] GDP 負成長！衰退陰影籠罩市場！"
                                    elif economy.approval > 75:
                                        news = (f"[新聞] 民調：Powell 支持度 "
                                                f"{economy.approval:.0f}%！軟著陸可期？")
                                    else:
                                        news = (f"[新聞] FED 利率 {economy.ffr:.2f}%，"
                                                "市場等待下次會議。")
                                    manager.post_message(news)
                                elif otype == "phone_call":
                                    opts = [
                                        ("財政部：支持你的政策路徑！", 3),
                                        ("白宮：希望盡快表態降息...", 2),
                                        ("IMF：全球對你有信心！", 4),
                                    ]
                                    msg, gain = random.choice(opts)
                                    economy.approval = min(100, economy.approval + gain)
                                    manager.post_message(
                                        f"{msg} 支持度 +{gain}")
                                elif otype == "guitar":
                                    guitar_video_t = 0.0
                                    state = config.STATE_GUITAR_VIDEO
                                elif otype == "bicycle":
                                    manager.post_message("這是鮑威爾的愛車，環保又健康！")
                                elif otype == "golf":
                                    current_minigame = create_minigame(config.MG_GOLF)
                                    minigame_kind = "golf"
                                    state = config.STATE_MINIGAME
                    elif ev.key == pygame.K_q:
                        state = config.STATE_QUEST
                    elif ev.key == pygame.K_p:
                        state = config.STATE_PHONE

                elif state == config.STATE_PHONE:
                    step = config.FFR_STEP
                    if ev.key in (pygame.K_UP, pygame.K_w):
                        economy.adjust_ffr(+step)
                    elif ev.key in (pygame.K_DOWN, pygame.K_s):
                        economy.adjust_ffr(-step)
                    elif ev.key in (pygame.K_EQUALS, pygame.K_PLUS):
                        economy.adjust_ffr(+1.0)
                    elif ev.key == pygame.K_MINUS:
                        economy.adjust_ffr(-1.0)
                    elif ev.key == pygame.K_LEFTBRACKET:   # [ 鍵 → QT 縮表
                        economy.adjust_balance_sheet(-0.1)
                    elif ev.key == pygame.K_RIGHTBRACKET:  # ] 鍵 → QE 擴表
                        economy.adjust_balance_sheet(+0.1 )
                    elif ev.key in (pygame.K_p, pygame.K_ESCAPE):
                        state = config.STATE_WORLD

                elif state == config.STATE_TERMINAL:
                    step = config.FFR_STEP
                    if ev.key in (pygame.K_UP, pygame.K_w):
                        economy.adjust_ffr(+step)
                    if ev.key in (pygame.K_DOWN, pygame.K_s):
                        economy.adjust_ffr(-step)
                    if ev.key in (pygame.K_EQUALS, pygame.K_PLUS):
                        economy.adjust_ffr(+1.0)
                    if ev.key == pygame.K_MINUS:
                        economy.adjust_ffr(-1.0)
                    if ev.key == pygame.K_LEFTBRACKET:    # [ → QT
                        economy.adjust_balance_sheet(-0.1)
                    if ev.key == pygame.K_RIGHTBRACKET:   # ] → QE
                        economy.adjust_balance_sheet(+0.1)
                    if ev.key in (pygame.K_e, pygame.K_RETURN, pygame.K_ESCAPE):
                        state = config.STATE_WORLD

                elif state == config.STATE_DIALOG:
                    _pg = (dialog_pages[dialog_page]
                           if 0 <= dialog_page < len(dialog_pages) else None)
                    _is_ch = (isinstance(_pg, tuple)
                              and _pg[0] == "__choice__")
                    if _is_ch:
                        _n = len(_pg[1])
                        if ev.key in (pygame.K_UP, pygame.K_w):
                            dialog_choice_sel = (dialog_choice_sel - 1) % _n
                        elif ev.key in (pygame.K_DOWN, pygame.K_s):
                            dialog_choice_sel = (dialog_choice_sel + 1) % _n
                        elif ev.key in (pygame.K_SPACE, pygame.K_RETURN,
                                        pygame.K_e):
                            sounds.play('confirm')
                            _, eff = _pg[1][dialog_choice_sel]
                            economy.approval = max(0, min(100,
                                economy.approval + eff.get("approval", 0)))
                            if eff.get("ffr", 0.0) != 0.0:
                                economy.adjust_ffr(eff["ffr"])
                            economy.apply_shock(
                                inf_shock=eff.get("cpi_shock", 0.0),
                                unemp_shock=eff.get("unemp_shock", 0.0))
                            if "heal" in eff:
                                player.hp = min(player.max_hp,
                                                player.hp + eff["heal"])
                            if "msg" in eff:
                                manager.post_message(eff["msg"])
                            dialog_choice_sel = 0
                            dialog_page += 1
                            if dialog_page >= len(dialog_pages):
                                state = config.STATE_WORLD
                        elif ev.key == pygame.K_ESCAPE:
                            dialog_choice_sel = 0
                            state = config.STATE_WORLD
                    else:
                        if ev.key in (pygame.K_SPACE, pygame.K_RETURN,
                                      pygame.K_e):
                            sounds.play('tick', 0.28)
                            dialog_choice_sel = 0
                            dialog_page += 1
                            if dialog_page >= len(dialog_pages):
                                state = config.STATE_WORLD
                        elif ev.key == pygame.K_ESCAPE:
                            state = config.STATE_WORLD

                elif state == config.STATE_MINIGAME:
                    if result_screen is not None:
                        if ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                            # Apply result
                            if result_screen.get("approval"):
                                economy.approval = max(
                                    0, min(100, economy.approval + result_screen["approval"]))
                            if result_screen.get("coffee"):
                                player.coffee_level = min(
                                    3, player.coffee_level + result_screen["coffee"])
                                player.coffee_drink_t = 3.0   # 觸發3秒喝咖啡動畫
                            if result_screen.get("inf_expect"):
                                economy.cpi = max(
                                    0, economy.cpi + result_screen["inf_expect"])
                            quests.mark_completed(minigame_kind, economy)
                            result_screen = None
                            current_minigame = None
                            state = config.STATE_WORLD
                    else:
                        if ev.key == pygame.K_ESCAPE:
                            current_minigame = None
                            result_screen = None
                            state = config.STATE_WORLD
                        else:
                            current_minigame.handle_event(ev)

                elif state == config.STATE_EVENT:
                    n = len(manager.events.active_event["choices"])
                    if ev.key in (pygame.K_UP,   pygame.K_w):
                        event_sel = (event_sel - 1) % n
                    if ev.key in (pygame.K_DOWN, pygame.K_s):
                        event_sel = (event_sel + 1) % n
                    if ev.key == pygame.K_1:
                        event_sel = 0
                    if ev.key == pygame.K_2 and n > 1:
                        event_sel = 1
                    if ev.key == pygame.K_3 and n > 2:
                        event_sel = 2
                    if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                        manager.resolve_event(event_sel, scene)
                        event_sel = 0
                        state = config.STATE_WORLD

                elif state == config.STATE_QUEST:
                    if ev.key in (pygame.K_q, pygame.K_ESCAPE):
                        state = config.STATE_WORLD

                elif state == config.STATE_GUITAR_VIDEO:
                    if ev.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                        state = config.STATE_WORLD

                elif state in (config.STATE_GAMEOVER, config.STATE_WIN):
                    if ev.key == pygame.K_r:
                        economy, player, camera, scenes, scene, manager, quests = new_game()
                        sim_timer = 0.0
                        lose_reason = None
                        bullets.clear()
                        enemies.clear()
                        enemy_spawn_t = random.uniform(8.0, 14.0)
                        state = config.STATE_MENU
                    if ev.key == pygame.K_q:
                        running = False

            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if state == config.STATE_WORLD:
                    cx_off, cy_off = camera.offset()
                    if player.current_weapon == "pistol":
                        b = player.shoot(ev.pos[0] + cx_off, ev.pos[1] + cy_off)
                        if b:
                            bullets.append(b)
                            sounds.play('shoot', 0.40)
                    else:
                        player.punch(enemies)
                elif state == config.STATE_PHONE:
                    # 手機按鈕點擊
                    pw_ph = 360
                    px_ph = config.SCREEN_W // 2 - pw_ph // 2
                    py_ph = config.SCREEN_H // 2 - 310
                    by_ph = py_ph + 110 + 152
                    bw_ph = (pw_ph - 50) // 4
                    for i, delta in enumerate([-1.0, -config.FFR_STEP,
                                               +config.FFR_STEP, +1.0]):
                        bx_ph = px_ph + 20 + i * (bw_ph + 4)
                        if pygame.Rect(bx_ph, by_ph, bw_ph, 56).collidepoint(ev.pos):
                            economy.adjust_ffr(delta)
                            break
                    bs_by = by_ph + 68          # FFR 按鈕下方再空一行
                    bs_bw = (pw_ph - 30) // 2
                    # QT 按鈕（左）
                    if pygame.Rect(px_ph + 10, bs_by, bs_bw, 44).collidepoint(ev.pos):
                        economy.adjust_balance_sheet(-0.1)
                    # QE 按鈕（右）
                    if pygame.Rect(px_ph + 20 + bs_bw, bs_by, bs_bw, 44).collidepoint(ev.pos):
                        economy.adjust_balance_sheet(+0.1)

        # ── Update ────────────────────────────────────────────────────
        if state == config.STATE_WORLD:
            player.update(dt, keys, scene)
            if player.coffee_drink_t > 0:
                player.coffee_drink_t = max(0.0, player.coffee_drink_t - dt)
            camera.update(player.x + player.w / 2,
                          player.y + player.h / 2, scene, dt)
            moving = any(keys[k] for k in (pygame.K_w, pygame.K_s, pygame.K_a,
                                           pygame.K_d, pygame.K_UP, pygame.K_DOWN,
                                           pygame.K_LEFT, pygame.K_RIGHT))
            walk_snd_t += dt
            if moving and walk_snd_t >= 0.28:
                walk_snd_t = 0.0
                sounds.play('walk', 0.20)
            manager.update(dt, economy, scene)

            # Bullets
            for b in bullets:
                b.update(dt, scene)
            for b in bullets[:]:
                if b.dead:
                    bullets.remove(b)
                    continue
                for enemy in enemies:
                    if not enemy.dead:
                        if math.hypot(b.x - enemy.x - 15, b.y - enemy.y - 15) < 20:
                            enemy.take_damage(Bullet.DAMAGE)
                            b.dead = True
                            break

            # Enemies (only active in city)
            if scene.name == config.SCENE_CITY:
                for enemy in enemies:
                    enemy.update(dt, player, scene)
                enemies[:] = [e for e in enemies if not e.dead]

                enemy_spawn_t -= dt
                if enemy_spawn_t <= 0 and len(enemies) < 6:
                    enemy_spawn_t = random.uniform(10.0, 16.0)
                    _ROAD, _SIDE = 2, 7  # R, S tile values from scenes.py
                    for _ in range(80):
                        tx = random.randint(0, scene.cols - 1)
                        ty = random.randint(0, scene.rows - 1)
                        if scene.tiles[ty][tx] not in (_ROAD, _SIDE):
                            continue
                        ex = tx * config.TILE_SIZE + 9.0
                        ey = ty * config.TILE_SIZE + 9.0
                        if scene.is_solid(ex, ey, 28, 28):
                            continue
                        if math.hypot(ex - player.x, ey - player.y) > 420:
                            enemies.append(Enemy(ex, ey))
                            break
            else:
                enemies.clear()
                bullets.clear()

            if player.hp <= 0:
                lose_reason = "combat"
                state = config.STATE_GAMEOVER

            sim_timer += dt
            if sim_timer >= config.SIM_TICK_SECONDS:
                sim_timer = 0.0
                economy.update()
                sounds.play('econ', 0.18)
                player.coffee_level = max(0, player.coffee_level - 1)
                reason = economy.lose_reason()
                if reason:
                    lose_reason = reason
                    sounds.play('lose')
                    state = config.STATE_GAMEOVER
                elif economy.check_win():
                    sounds.play('win')
                    state = config.STATE_WIN

            if manager.events.active_event and state == config.STATE_WORLD:
                sounds.play('event')
                state = config.STATE_EVENT
                event_sel = 0
                camera.shake(6, 0.4)

        elif state == config.STATE_TERMINAL:
            sim_timer += dt
            if sim_timer >= config.SIM_TICK_SECONDS:
                sim_timer = 0.0
                economy.update()
                reason = economy.lose_reason()
                if reason:
                    lose_reason = reason
                    state = config.STATE_GAMEOVER
            if manager.events.active_event:
                state = config.STATE_EVENT
                event_sel = 0

        elif state == config.STATE_PHONE:
            # Economy and events tick while phone is open
            manager.events.tick(dt, economy)
            sim_timer += dt
            if sim_timer >= config.SIM_TICK_SECONDS:
                sim_timer = 0.0
                economy.update()
                reason = economy.lose_reason()
                if reason:
                    lose_reason = reason
                    state = config.STATE_GAMEOVER
                elif economy.check_win():
                    state = config.STATE_WIN
            if manager.events.active_event:
                state = config.STATE_EVENT
                event_sel = 0

        elif state == config.STATE_MINIGAME and result_screen is None:
            current_minigame.update(dt, keys)
            if current_minigame.done:
                result_screen = current_minigame.result

        elif state == config.STATE_TRANSITION:
            transition["t"] += dt * 1.6
            if transition["t"] >= 0.5 and transition.get("switched") != True:
                # Switch scene at midpoint
                scene = transition["target_scene"]
                player.set_tile(*transition["spawn"])
                camera.snap(player.x + player.w/2,
                            player.y + player.h/2, scene)
                transition["switched"] = True
                bullets.clear()
                enemies.clear()
                enemy_spawn_t = random.uniform(8.0, 14.0)
            if transition["t"] >= 1.0:
                transition = None
                state = config.STATE_WORLD

        elif state == config.STATE_GUITAR_VIDEO:
            guitar_video_t += dt

        elif state == config.STATE_INTRO:
            intro_slide_t += dt
            if intro_slide_t >= INTRO_SLIDES[intro_slide]["timeout"]:
                intro_slide += 1
                intro_slide_t = 0.0
                if intro_slide >= len(INTRO_SLIDES):
                    intro_slide = 0
                    state = config.STATE_MENU

        # ── Render ────────────────────────────────────────────────────
        if state == config.STATE_MENU:
            draw_menu(screen, fnt, fnt_big, fnt_s)

        elif state in (config.STATE_WORLD, config.STATE_EVENT, config.STATE_DIALOG, config.STATE_QUEST, config.STATE_TRANSITION, config.STATE_PHONE):
            cx, cy = camera.offset()
            world_surf.fill((25, 28, 34))
            draw_scene(world_surf, scene, cx, cy, economy, fnt_s, scenes)
            for npc in scene.npcs:
                npc.draw(world_surf, cx, cy, fnt_s)
            for enemy in enemies:
                enemy.draw(world_surf, cx, cy)
            player.draw(world_surf, cx, cy)
            for b in bullets:
                b.draw(world_surf, cx, cy)
            apply_economic_tint(world_surf, economy)
            # 像素藝術效果：半解析度縮小再放大，製造清晰像素顆粒感
            _half = pygame.transform.scale(
                world_surf, (config.SCREEN_W // 2, config.SCREEN_H // 2))
            screen.blit(pygame.transform.scale(_half, (config.SCREEN_W, config.SCREEN_H)), (0, 0))
            draw_city_signs(screen, scene, cx, cy, fnt_s)

            inter = player.find_interaction(
                scene) if state == config.STATE_WORLD else None
            draw_hud(screen, economy, fnt_s, scene.name, inter, quests)
            draw_combat_hud(screen, player, fnt_s)
            draw_minimap(screen, scene, player, fnt_s, scenes)
            draw_street_incident(screen, manager.street.current, fnt, fnt_s)

            # Manager message
            if manager.message_t > 0:
                mt = fnt.render(manager.message, True, config.TERMINAL_AMBER)
                bg = pygame.Surface(
                    (mt.get_width()+24, mt.get_height()+14), pygame.SRCALPHA)
                bg.fill((0, 0, 0, 200))
                screen.blit(bg, (config.SCREEN_W//2 - bg.get_width()//2, 90))
                screen.blit(mt, (config.SCREEN_W//2 - mt.get_width()//2, 96))

            if state == config.STATE_EVENT and manager.events.active_event:
                draw_event(screen, manager.events.active_event,
                           fnt, fnt_big, fnt_s, event_sel)
            elif state == config.STATE_DIALOG:
                draw_dialog(screen, dialog_pages, dialog_page,
                            dialog_choice_sel, fnt, fnt_s)
            elif state == config.STATE_QUEST:
                draw_quest_log(screen, quests, fnt, fnt_big, fnt_s)
            elif state == config.STATE_TRANSITION:
                draw_transition(
                    screen, transition["t"], transition["label"], fnt_big)
            elif state == config.STATE_PHONE:
                draw_phone(screen, economy, fnt, fnt_big, fnt_s)

        elif state == config.STATE_TERMINAL:
            tick_progress = sim_timer / config.SIM_TICK_SECONDS
            draw_terminal(screen, economy, fnt, fnt_big, fnt_s, tick_progress)

        elif state == config.STATE_MINIGAME:
            current_minigame.draw(screen, fnt, fnt_big, fnt_s)
            if result_screen is not None:
                draw_result(screen, result_screen, fnt, fnt_big, fnt_s)

        elif state == config.STATE_GAMEOVER:
            draw_gameover(screen, lose_reason, economy, fnt, fnt_big, fnt_s)

        elif state == config.STATE_WIN:
            draw_win(screen, economy, fnt, fnt_big, fnt_s)

        elif state == config.STATE_GUITAR_VIDEO:
            draw_guitar_video(screen, fnt, fnt_big, fnt_s, guitar_video_t)

        elif state == config.STATE_INTRO:
            draw_intro(screen, intro_slide, intro_slide_t, fnt, fnt_big, fnt_s)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


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


if __name__ == "__main__":
    main()
