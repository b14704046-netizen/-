"""Dialog system — NPC conversations with dynamic responses and player choices."""
import pygame
import config


def _by_econ(economy, low, normal, high):
    if economy.cpi < 3.0:  return low
    if economy.cpi < 7.0:  return normal
    return high


def _by_unemp(economy, low, normal, high):
    if economy.unemployment < 5.0:  return low
    if economy.unemployment < 8.0:  return normal
    return high


# Normal page: (speaker, text)
# Choice page: ("__choice__", [(option_text, effect_dict), ...])
# effect_dict keys: approval, ffr, cpi_shock, unemp_shock, heal, msg
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
            ("__choice__", [
                ("軟著陸進展順利，數據令人樂觀",
                 {"approval": +4, "msg": "記者搶著記筆記，版面頭條確定！"}),
                ("情況仍在監控中，謹慎行事",
                 {"approval": +1, "msg": "記者點頭記錄。"}),
                ("無可奉告",
                 {"approval": -6, "msg": "記者失望地離開，明天見報批評！"}),
            ]),
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
        "city_banker": [
            ("銀行家", _by_econ(economy,
                "信貸市場很健康！主席功不可沒。",
                f"10年期殖利率 {ffr+1.2:.2f}%，殖利率曲線有點奇怪。",
                "信用緊縮了，企業借不到錢！")),
        ],
        "city_student": [
            ("大學生", "主席！我在寫貨幣政策論文。"),
            ("大學生",
             f"請問 Taylor Gap 現在是 "
             f"{(ffr - (config.NEUTRAL_RATE + cpi - config.TARGET_INFLATION)):.2f}%，這算鷹派嗎？"),
            ("Powell", "你的思路很對，繼續研究！"),
        ],
        "city_nurse": [
            ("護士", "醫院急診最近很忙，民眾壓力山大。"),
            ("護士", _by_unemp(economy,
                "大家還好，有工作心理比較健康。",
                "失業讓很多人生病，心理科滿號了...",
                "急診塞爆！失業症候群大爆發！")),
        ],
        "city_retiree_east": [
            ("退休阿姨", _by_econ(economy,
                "這裡的公園真漂亮，退休日子很好過！",
                "物價漲了，退休金有點不夠用...",
                "存款被通膨吃光了，考慮重回職場！")),
        ],
        "city_worker_south": [
            ("南區居民", _by_unemp(economy,
                "這邊新開了很多店，生意不錯！",
                "附近不少店面空著，景氣不好。",
                "整條街都在關店，很多人失業了...")),
        ],

        # ── City extra ──
        "city_worker_south": [
            ("南區居民", _by_unemp(economy,
                "這邊新開了很多店，生意不錯！",
                "附近不少店面空著，景氣不好。",
                "整條街都在關店，很多人失業了...")),
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
        "cafe_writer": [
            ("作家 David", "我正在寫一本書：《零利率時代的人心》。"),
            ("作家 David", _by_econ(economy,
                "這年頭故事太少，我很苦惱。",
                "通膨這段最精彩！讀者都想知道結局。",
                "不用我虛構了，現實比小說更瘋狂。")),
        ],
        "cafe_trader": [
            ("股市老手", f"S&P 昨天收 {3000 + int(economy.gdp*50)} 點。"),
            ("股市老手", _by_econ(economy,
                "我全倉做多，加油！",
                f"FFR {ffr:.2f}%，資金有點貴，但還撐得住。",
                "我已經空倉避險了，不碰這個環境。")),
        ],
        "cafe_customer2": [
            ("學生", "您好，我在唸經濟學！"),
            ("學生", f"請問現在泰勒規則隱含利率是 "
                    f"{(config.NEUTRAL_RATE + cpi - config.TARGET_INFLATION):.2f}%，"),
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
            ("副主席 Brian", _by_econ(economy,
                "目前路徑漂亮，但我建議繼續保持。",
                "通膨仍在，我建議再升一碼。",
                "我們必須緊急升息，不然完蛋了！")),
            ("副主席 Brian", "你怎麼看，主席？"),
            ("__choice__", [
                ("同意，我會在下次會議升息 0.25%",
                 {"ffr": +0.25, "approval": +3,
                  "msg": "Brian 點頭稱是，聯準會內部共識確立。"}),
                ("保持不動，先多觀察一個月",
                 {"approval": -2,
                  "msg": "Brian 皺眉，但接受了主席的判斷。"}),
                ("我其實考慮降息",
                 {"ffr": -0.25, "approval": -7,
                  "msg": "Brian 大驚！氣氛極為凝重。"}),
            ]),
        ],

        "fed_economist1": [
            ("Smith 博士", f"根據最新模型，中性利率 r* ≈ {config.NEUTRAL_RATE:.1f}%。"),
            ("Smith 博士", _by_econ(economy,
                "通膨收斂速度超預期，太好了！",
                "菲利普曲線似乎平坦化了，傳統工具效力有限。",
                "我們面臨的可能是結構性通膨，不只是需求問題。")),
        ],
        "fed_analyst": [
            ("Park 分析師", "主席，最新數據摘要："),
            ("Park 分析師",
             f"CPI {cpi:.1f}%，失業 {une:.1f}%，GDP {economy.gdp:.1f}%，"
             f"支持度 {appr:.0f}%。"),
            ("Park 分析師", "Taylor Rule 隱含利率約 "
             f"{(config.NEUTRAL_RATE + cpi - config.TARGET_INFLATION):.2f}%。"),
        ],

        # ── Supermarket ──
        "sm_angry_mom": [
            ("怒火主婦", _by_econ(economy,
                "今天買了好多，謝謝主席物價穩定！",
                "蛋一盒漲到 8 塊了，你看著辦！",
                "你給我下來！我家小孩沒奶喝！")),
            ("__choice__", [
                ("我非常理解您的辛苦，通膨是我的首要任務",
                 {"approval": +3,
                  "msg": "主婦稍微消氣，說「那就希望你快點解決」。"}),
                ("通膨正在緩解中，請再耐心等等",
                 {"approval": +1,
                  "msg": "主婦半信半疑地推車離開。"}),
                ("請聯繫你的國會代表反映",
                 {"approval": -10,
                  "msg": "主婦大怒：叫我去找國會？！你這官員！"}),
            ]),
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
        "press_wsj": [
            ("WSJ", "主席對 FFR 路徑有何展望？"),
            ("__choice__", [
                ("我們依數據行事，路徑維持靈活",
                 {"approval": +3,
                  "msg": "WSJ 明天頭條：Powell 維持鷹派靈活立場。"}),
                ("軟著陸仍是主要情境",
                 {"approval": +2,
                  "msg": "WSJ 記者滿意點頭。"}),
                ("降息仍言之過早",
                 {"approval": -2,
                  "msg": "WSJ：市場失望，債券殖利率上升。"}),
            ]),
        ],
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
            ("Warren", "主席！通膨是針對窮人的罪行！"),
            ("Warren", _by_econ(economy,
                "這次你做得還可以，繼續。",
                "你還要看著民眾受苦多久？",
                "通膨 {:.1f}%！你必須立刻降息！".format(cpi))),
            ("__choice__", [
                ("我理解你的關切，但通膨仍需繼續打壓",
                 {"approval": +2,
                  "msg": "Warren 表情嚴肅但接受，說「我盯著你」。"}),
                ("我承諾將在下次會議重新評估利率",
                 {"ffr": -0.25, "approval": +6,
                  "msg": "Warren 暫時滿意，支持度回升！"}),
                ("聯準會的獨立性不容政治干預",
                 {"approval": -8,
                  "msg": "Warren 憤怒離席！媒體大篇幅報導衝突！"}),
            ]),
        ],
        "cap_cruz": [
            ("Cruz", "主席，我支持你獨立運作！"),
            ("Cruz", "但別讓財政部赤字繼續失控啊..."),
        ],
        "cap_sanders": [
            ("Sanders", "華爾街又賺翻了！"),
            ("Sanders", _by_econ(economy,
                "但至少底層日子還過得去。",
                "底層人民已經吃不消了。",
                "底層人民正在挨餓！你聽到了嗎！")),
            ("__choice__", [
                ("我理解，正在評估降息時機",
                 {"approval": +3,
                  "msg": "Sanders 點頭，說「我等著看」。"}),
                ("降息並非解方，物價穩定才是",
                 {"approval": -3,
                  "msg": "Sanders 不以為然，轉身接受媒體採訪。"}),
                ("我承諾下月降息",
                 {"ffr": -0.25, "approval": +8, "cpi_shock": 0.3,
                  "msg": "Sanders 熱烈鼓掌！但通膨預期悄悄升溫..."}),
            ]),
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

        "gym_heavy": [
            ("練腿日男", "主席也來健身啊！"),
            ("練腿日男", _by_unemp(economy,
                "工作穩，有力氣練。",
                "壓力大，只好靠鐵療癒。",
                "失業了，健身費是我最後的奢侈品。")),
        ],
        "gym_newbie": [
            ("健身新人", "您好主席！我剛辦會員..."),
            ("健身新人", "聽說運動可以對抗通膨帶來的焦慮感？"),
            ("Powell", "確實如此，多鍛煉，保持冷靜！"),
        ],

        # ── Park ──
        "park_elder": [
            ("公園老伯", "年輕人，這年頭壓力很大吧？"),
            ("公園老伯", "來餵餵鴿子，放鬆一下。"),
            ("__choice__", [
                ("您說的對，適時放鬆很重要",
                 {"approval": +1,
                  "msg": "老伯開懷笑了，遞給你一把麵包屑。"}),
                ("謝謝，但我有更緊急的事要處理",
                 {"msg": "老伯聳聳肩，繼續悠閒地餵鴿子。"}),
            ]),
        ],
        "park_kid": [
            ("小孩", "看！我會丟麵包！"),
            ("小孩", "哈哈鴿子好笨！"),
        ],
        "park_jogger": [
            ("慢跑者", "主席也來運動嗎？"),
            ("慢跑者", "保持經濟運轉，跟跑步一樣，要持續。"),
        ],

        "hospital_chief": [
            ("主任 Chang", "主席，從醫學角度看，高壓力環境對決策有很大影響。"),
            ("主任 Chang", _by_econ(economy,
                "您看起來狀態不錯，繼續保持。",
                "您的眼神透露疲勞，建議多休息。",
                "您已達到臨床壓力閾值，強烈建議減少工作量！")),
        ],
        "hospital_family": [
            ("病人家屬", _by_unemp(economy,
                "謝謝主席，家人有工作，醫療保險有保。",
                "老公被裁員了，醫療費用好貴...",
                "失業六個月了，沒有保險，家人生病怎麼辦...")),
        ],

        # ── Bank ──
        "bank_teller": [
            ("行員 Lisa", "歡迎來到聯邦儲備銀行！"),
            ("行員 Lisa", f"現行儲蓄利率：{ffr * 0.82:.2f}%。"
                         f"{'存款利息不錯！' if ffr > 4 else '利率偏低，存款回報有限。'}"),
        ],
        "bank_investor": [
            ("投資人 Marcus", f"主席！S&P 目前 {3000 + int(economy.gdp * 50)} 點。"),
            ("投資人 Marcus", "市場對降息預期非常強烈，所有人都看著您。"),
            ("__choice__", [
                ("我的決策以數據為依據，不配合市場情緒",
                 {"approval": +2,
                  "msg": "市場短暫震盪後穩定，機構投資人表示尊重。"}),
                ("我們正在評估降息路徑",
                 {"ffr": -0.25, "approval": +5, "cpi_shock": 0.2,
                  "msg": "市場立刻大漲！但通膨預期微升..."}),
                ("聯準會不理會短期市場波動",
                 {"approval": -4,
                  "msg": "Marcus 皺眉離席。盤中出現震盪賣壓。"}),
            ]),
        ],
        "bank_loan": [
            ("貸款專員 Chen", "主席您好！最近企業貸款需求如何？"),
            ("貸款專員 Chen", _by_econ(economy,
                "信貸市場很活躍，企業擴張積極。",
                "利率高，申請量下滑了不少。",
                "違約率上升，我們收緊了放款標準。")),
        ],

        "bank_manager": [
            ("行長 White", "主席，我行持有大量長期公債。"),
            ("行長 White", _by_econ(economy,
                f"FFR {ffr:.2f}%，息差理想，銀行體質健康。",
                "殖利率曲線扭曲，我們的期限溢酬壓縮中。",
                "市值損失擴大，我們在評估流動性風險！")),
        ],
        "bank_corp": [
            ("企業客戶", _by_econ(economy,
                "這個利率環境可以接受，我們計劃擴廠。",
                f"借貸成本 {ffr+1.5:.2f}%，投資回報率剛好打平。",
                "成本太高，我們已取消三個投資項目了。")),
        ],

        # ── Hospital ──
        "hospital_doctor": [
            ("王醫生", "主席，您的血壓偏高，壓力太大了。"),
            ("王醫生", "讓我幫您做個快速評估。"),
            ("__choice__", [
                ("好，做個完整檢查",
                 {"heal": 60, "approval": +1,
                  "msg": "醫生：血壓偏高但可控。請多休息，少喝咖啡。"}),
                ("我沒事，謝謝醫生",
                 {"heal": 25,
                  "msg": "醫生：主席，您的眼神說明您不好。保重！"}),
            ]),
        ],
        "hospital_nurse": [
            ("護士 Amy", "這裡是聯邦醫療中心。"),
            ("護士 Amy", _by_unemp(economy,
                "今天病人不多，大家還好。",
                "壓力大的病人越來越多了，心理科滿號。",
                "急診滿員！失業導致的憂鬱症病患激增！")),
        ],
        "hospital_patient": [
            ("病患", _by_unemp(economy,
                "主席，謝謝你讓就業率維持得不錯。",
                "我因為公司縮編生病了，希望快快好轉。",
                "我失業了，連醫療保險都沒有了...")),
        ],

        "univ_grad": [
            ("研究生 Lin", "我的論文在研究「利率不確定性對廠商投資的影響」。"),
            ("研究生 Lin", f"目前 FFR {ffr:.2f}%，波動性使企業資本支出下降 "
             f"{max(5, int(abs(ffr - config.NEUTRAL_RATE) * 8))}%。"),
            ("Powell", "很好的方向，繼續深挖！"),
        ],
        "univ_visitor": [
            ("Dr. Kim", "我來自首爾大學，研究比較貨幣政策。"),
            ("Dr. Kim", _by_econ(economy,
                "Fed 的路徑是全球央行教科書範例！",
                "Fed 的路徑引發全球跟進，但各國條件不同。",
                "Fed 的激進緊縮引發全球匯率風暴，影響深遠。")),
            ("__choice__", [
                ("感謝，Fed 以全球穩定為念",
                 {"approval": +2,
                  "msg": "Dr. Kim 熱烈點頭，邀請你訪問首爾。"}),
                ("每國央行應各自為政",
                 {"approval": -1,
                  "msg": "Dr. Kim 若有所思，似乎不完全同意。"}),
            ]),
        ],

        # ── University ──
        "univ_prof": [
            ("陳教授", "主席！歡迎來到聯邦經濟大學！"),
            ("陳教授", "學生們都在問：我們是否會重現1970年代的通膨？"),
            ("__choice__", [
                ("不會，我們從歷史學到了教訓",
                 {"approval": +3,
                  "msg": "教授讚許點頭。學生們熱烈鼓掌！"}),
                ("謹慎行事是正確的應對態度",
                 {"approval": +1,
                  "msg": "教授滿意，佈置了課外閱讀。"}),
                ("過去不等於未來，每次危機都是新的",
                 {"approval": -1,
                  "msg": "教授提出反駁，雙方展開熱烈辯論！"}),
            ]),
        ],
        "univ_student": [
            ("學生 Kevin", "主席！我可以拍照嗎？"),
            ("學生 Kevin", "我的論文題目是「非線性菲利普曲線的實證研究」！"),
            ("Powell", "很好的題目，貨幣政策需要你們這樣的人才。"),
        ],
        "univ_student2": [
            ("學生 Mia", f"請問現在中性利率（r*）大概是多少？"),
            ("Powell", f"目前估算約在 {config.NEUTRAL_RATE:.1f}% 左右，但有相當不確定性。"),
            ("學生 Mia", "謝謝！這比教科書說的有趣多了！"),
        ],
    }

    return D.get(dialog_id, [("???", "（沒人回應）")])


def draw_dialog(surf, pages, page_idx, choice_sel, fnt, fnt_s):
    W, H = config.SCREEN_W, config.SCREEN_H

    if not (0 <= page_idx < len(pages)):
        return

    page = pages[page_idx]
    is_choice = isinstance(page, tuple) and page[0] == "__choice__"

    if is_choice:
        choices = page[1]
        n = len(choices)
        bw = 880
        bh = 48 + n * 46 + 34
        bx = W // 2 - bw // 2
        by = H - bh - 30

        pygame.draw.rect(surf, (12, 14, 22),
                         pygame.Rect(bx, by, bw, bh), border_radius=10)
        pygame.draw.rect(surf, config.TERMINAL_AMBER,
                         pygame.Rect(bx, by, bw, bh), border_radius=10, width=2)

        prompt = fnt_s.render("▼ 請選擇你的回應", True, config.TERMINAL_AMBER)
        surf.blit(prompt, (bx + 22, by + 14))

        for i, (text, _) in enumerate(choices):
            cy = by + 44 + i * 46
            is_sel = i == choice_sel
            if is_sel:
                pygame.draw.rect(surf, (28, 44, 70),
                                 pygame.Rect(bx + 12, cy - 6, bw - 24, 38),
                                 border_radius=6)
                pygame.draw.rect(surf, config.TERMINAL_AMBER,
                                 pygame.Rect(bx + 12, cy - 6, bw - 24, 38),
                                 border_radius=6, width=1)
            arrow = "▶  " if is_sel else "    "
            col = config.TERMINAL_AMBER if is_sel else config.LIGHT_GRAY
            ct = fnt.render(arrow + text, True, col)
            surf.blit(ct, (bx + 26, cy))

        nav = fnt_s.render(
            "↑ ↓  選擇    [ Space / Enter ]  確認    [ ESC ]  取消",
            True, config.TERMINAL_DIM)
        surf.blit(nav, (bx + bw - nav.get_width() - 18, by + bh - 26))
        return

    # ── Normal page ──
    speaker, text = page
    bw, bh = 880, 160
    bx, by = W // 2 - bw // 2, H - bh - 30

    pygame.draw.rect(surf, (12, 14, 22),
                     pygame.Rect(bx, by, bw, bh), border_radius=10)
    pygame.draw.rect(surf, config.TERMINAL_AMBER,
                     pygame.Rect(bx, by, bw, bh), border_radius=10, width=2)

    tag = fnt_s.render(speaker, True, config.TERMINAL_AMBER)
    pygame.draw.rect(surf, (28, 30, 50),
                     pygame.Rect(bx + 18, by + 12,
                                 tag.get_width() + 16, tag.get_height() + 8),
                     border_radius=4)
    surf.blit(tag, (bx + 26, by + 16))

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

    nav = fnt_s.render(
        f"[ Space / Enter ]  下一句    ({page_idx + 1}/{len(pages)})",
        True, config.TERMINAL_DIM)
    surf.blit(nav, (bx + bw - nav.get_width() - 18, by + bh - 26))
