"""Dialog system — NPC conversations with dynamic responses."""
import pygame
import config


def _by_econ(economy, low, normal, high):
    """Pick a line based on inflation level."""
    if economy.cpi < 3.0:   return low
    if economy.cpi < 7.0:   return normal
    return high


def _by_unemp(economy, low, normal, high):
    if economy.unemployment < 5.0:  return low
    if economy.unemployment < 8.0:  return normal
    return high


# Each dialog returns list of (speaker, text) pages.
# If the last page is a tuple of (choices, callback_key), it's a choice prompt.
def get_dialog(dialog_id, economy):
    cpi  = economy.cpi
    une  = economy.unemployment
    ffr  = economy.ffr
    appr = economy.approval

    D = {
        # ── City street NPCs ──
        "street_citizen_1": [
            ("路人甲", _by_econ(economy,
                "今天天氣真好，股票也漲了！",
                "唉，最近什麼都在漲，受不了。",
                "蛋一打要 30 美金，這還能活嗎！？")),
            ("路人甲", _by_econ(economy,
                "謝謝主席你的辛苦！",
                "你能不能想點辦法？",
                "我要去抗議聯準會了！")),
        ],
        "street_journalist": [
            ("記者", "主席先生！能否評論一下最新通膨數據？"),
            ("Powell", f"目前 CPI 為 {cpi:.1f}%，FFR {ffr:.2f}%。"),
            ("記者", _by_econ(economy,
                "看來軟著陸有望，謝謝！",
                "民眾期待您的下一步動作。",
                "通膨情勢嚴峻，您將如何應對？")),
        ],
        "street_protester": [
            ("抗議者", _by_unemp(economy,
                "（看到你嚇了一跳，匆匆離開）",
                "降息！降息！降息！",
                "聯準會害我失業！下台！")),
        ],
        "street_citizen_2": [
            ("上班族", "今天股市怎麼樣？"),
            ("上班族", _by_econ(economy,
                "好像穩穩漲，繼續加碼。",
                "波動有點大，不敢進場。",
                "全部清倉了，現金為王！")),
        ],
        "street_unemployed": [
            ("失業者", _by_unemp(economy,
                "嗨，主席。其實我才剛找到工作！",
                "找工作好難啊，景氣真的不好。",
                "我已經失業 8 個月了...")),
        ],
        "street_child": [
            ("小朋友", "叔叔，你是電視上的人嗎？"),
            ("Powell", "是啊，叔叔在管利率。"),
            ("小朋友", _by_econ(economy,
                "媽媽說你做得很好！",
                "媽媽說最近什麼都變貴了...",
                "媽媽說都是你的錯！")),
        ],
        "street_elder": [
            ("退休者", "年輕人，我有 30 萬美元存款。"),
            ("退休者", _by_econ(economy,
                f"利率 {ffr:.2f}% 還不錯，定存利息夠用。",
                "利率還可以但通膨吃光利息了。",
                "通膨把我老本都掏空了！")),
        ],
        "street_worker": [
            ("夜班工人", "主席先生這麼晚還在外面？"),
            ("夜班工人", _by_unemp(economy,
                "工廠加班費不錯！",
                "公司有點裁員壓力...",
                "工廠倒了，我兼三份差事。")),
        ],

        # ── Cafe ──
        "cafe_barista": [
            ("Anna", "主席！老樣子，鷹派咖啡？"),
            ("Anna", _by_econ(economy,
                "今天客人不少，生意好。",
                "原物料一直漲，咖啡豆要漲價了。",
                "咖啡豆漲了三倍，我可能要關店了。")),
            ("Anna", "去那邊那台機器自己沖一杯吧！"),
        ],
        "cafe_customer1": [
            ("上班族", "拿鐵又漲了一塊..."),
            ("上班族", _by_econ(economy,
                "不過薪水跟得上，沒差啦。",
                "再漲我要喝白開水了。",
                "我已經改喝公司茶包了。")),
        ],
        "cafe_customer2": [
            ("學生", "您好，我在唸經濟學！"),
            ("學生", f"請問現在泰勒規則隱含利率是 {(config.NEUTRAL_RATE + cpi - config.TARGET_INFLATION):.2f}%，"),
            ("學生", f"和實際 FFR {ffr:.2f}% 差距大嗎？"),
            ("Powell", "好問題，多想想！"),
        ],

        # ── Fed ──
        "fed_guard": [
            ("守衛", "主席早安！"),
        ],
        "fed_secretary": [
            ("Jane", f"主席，今天行程：上午備詢，下午記者會。"),
            ("Jane", f"目前監控：CPI {cpi:.1f}%，失業 {une:.1f}%，支持度 {appr:.0f}%。"),
        ],
        "fed_vicechair": [
            ("副主席", _by_econ(economy,
                "目前路徑漂亮，繼續走。",
                "我建議稍微鷹派一點。",
                "我們必須緊急升息，不然完蛋了！")),
            ("副主席", "你怎麼看？"),
        ],

        # ── Supermarket ──
        "sm_angry_mom": [
            ("怒火主婦", _by_econ(economy,
                "今天買了好多，謝謝主席物價穩定！",
                "蛋一盒漲到 8 塊了，你看著辦！",
                "你給我下來！我家小孩沒奶喝！")),
        ],
        "sm_elder": [
            ("退休伯伯", _by_econ(economy,
                f"FFR {ffr:.2f}% 我很滿意。",
                "退休金縮水了，加減過。",
                "我只能吃泡麵了...")),
        ],
        "sm_young_mom": [
            ("年輕媽媽", _by_econ(economy,
                "尿布還算便宜，謝主席！",
                "奶粉貴了不少，吃緊。",
                "我已經改用布尿布了。")),
        ],
        "sm_child": [
            ("小朋友", _by_econ(economy,
                "我要這個棒棒糖！",
                "媽媽說太貴不能買...",
                "媽媽說我們連飯都快吃不起了。")),
        ],
        "sm_cashier": [
            ("收銀員", f"歡迎光臨！今天總價會嚇到您喔。"),
            ("收銀員", _by_econ(economy,
                "業績穩定！",
                "客人都在抱怨，我也是。",
                "我快忙到精神崩潰了。")),
        ],

        # ── Press ──
        "press_wsj": [("WSJ", "主席對 FFR 路徑有何展望？")],
        "press_cnbc": [("CNBC", "市場想知道何時降息！")],
        "press_bloomberg": [("彭博", f"通膨 {cpi:.1f}% 距 2% 目標還有距離。")],
        "press_ft": [("FT", "全球央行是否協調？")],
        "press_reuters": [("路透", "上次決議的少數意見是？")],

        # ── Wall St ──
        "ws_bull": [
            ("多頭", _by_econ(economy,
                "穩穩漲！主席讚！",
                "我還是看多，撐住！",
                "我...我認賠出場了。")),
        ],
        "ws_bear": [
            ("空頭", _by_econ(economy,
                "等回檔，總有崩盤的一天！",
                "好戲開始了！",
                "我發了！主席謝謝你！")),
        ],
        "ws_quant": [
            ("量化", "我的模型顯示 80% 機率衰退..."),
            ("量化", "...但模型也說有 70% 機率上漲。我不知道。"),
        ],
        "ws_bond": [
            ("債券", f"10Y 殖利率 {ffr + 1.2:.2f}%，殖利率曲線倒掛！"),
        ],
        "ws_analyst": [
            ("分析師", "主席...我可以拍張合照嗎...？"),
            ("Powell", "下次吧。"),
        ],

        # ── Capitol ──
        "cap_warren": [
            ("Warren", "主席！通膨稅是針對窮人的罪行！"),
            ("Warren", _by_econ(economy,
                "...好吧，這次你做得不錯。",
                "你還要看著民眾受苦多久？",
                "你必須辭職！立刻！")),
        ],
        "cap_cruz": [
            ("Cruz", "主席，我支持你獨立運作！"),
            ("Cruz", "但別讓政府開支失控啊..."),
        ],
        "cap_sanders": [
            ("Sanders", "華爾街又賺翻了！"),
            ("Sanders", _by_econ(economy,
                "但至少底層日子過得去。",
                "底層人民已經吃不消。",
                "底層人民正在挨餓！你聽到了嗎？！")),
        ],
        "cap_speaker": [
            ("議長", "主席，請坐。今天的聽證會..."),
            ("議長", "你要上台陳述，請去那個講台。"),
        ],

        # ── Gym ──
        "gym_coach": [
            ("Mike", "嘿主席！想試試跑步機嗎？"),
            ("Mike", "保持中性利率步速，才能有耐力。"),
        ],
        "gym_member": [
            ("會員", _by_econ(economy,
                "今天感覺超好的，謝謝主席！",
                "壓力大，必須運動釋放。",
                "我快崩潰了...只能靠運動麻木自己。")),
        ],

        # ── Park ──
        "park_elder": [
            ("公園老伯", "年輕人，這年頭壓力很大吧？"),
            ("公園老伯", "來餵餵鴿子，放鬆一下。"),
        ],
        "park_kid": [
            ("小孩", "看！我會丟麵包！"),
            ("小孩", "哈哈鴿子好笨！"),
        ],
        "park_jogger": [
            ("慢跑者", "主席也來運動嗎？"),
            ("慢跑者", "保持經濟運轉，跟跑步一樣，要持續。"),
        ],
    }

    return D.get(dialog_id, [("???", "（沒人回應）")])


def draw_dialog(surf, pages, page_idx, fnt, fnt_s):
    W, H = config.SCREEN_W, config.SCREEN_H
    bw, bh = 880, 160
    bx, by = W//2 - bw//2, H - bh - 30

    # backdrop
    pygame.draw.rect(surf, (12, 14, 22), pygame.Rect(bx, by, bw, bh), border_radius=10)
    pygame.draw.rect(surf, config.TERMINAL_AMBER, pygame.Rect(bx, by, bw, bh), border_radius=10, width=2)

    if 0 <= page_idx < len(pages):
        speaker, text = pages[page_idx]
        # speaker tag
        tag = fnt_s.render(speaker, True, config.TERMINAL_AMBER)
        pygame.draw.rect(surf, (28, 30, 50), pygame.Rect(bx+18, by+12, tag.get_width()+16, tag.get_height()+8), border_radius=4)
        surf.blit(tag, (bx+26, by+16))

        # text wrap
        words = text.replace('\n', ' \n ').split(' ')
        line = ""
        ly = by + 50
        for w in words:
            if w == '\n':
                t = fnt.render(line, True, config.WHITE)
                surf.blit(t, (bx + 24, ly))
                ly += 28
                line = ""
                continue
            test = (line + w) if line else w
            if fnt.size(test)[0] > bw - 50:
                t = fnt.render(line, True, config.WHITE)
                surf.blit(t, (bx + 24, ly))
                ly += 28
                line = w
            else:
                line = test
        if line:
            t = fnt.render(line, True, config.WHITE)
            surf.blit(t, (bx + 24, ly))

        # progress
        nav = fnt_s.render(f"[ Space / Enter ] 下一句  ({page_idx+1}/{len(pages)})", True, config.TERMINAL_DIM)
        surf.blit(nav, (bx + bw - nav.get_width() - 18, by + bh - 26))
