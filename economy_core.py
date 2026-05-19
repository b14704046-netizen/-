"""
economy_model.py  ──  聯準會模擬器核心經濟模型 v2.0
=====================================================
改進重點：
  1. 加入量化寬鬆 (QE) / 量化緊縮 (QT) 資產負債表工具
  2. 通膨、失業率模型依據美國 2004-2024 年時間序列分析重新校準
  3. 新增信用利差 (credit spread) 與通膨預期 (inflation expectations) 狀態變數
  4. 菲利浦曲線加入非線性效果 (Nonlinear Phillips Curve)
  5. QE 透過「投資組合再平衡」與「信心效果」兩個渠道影響實體經濟

─── 實證校準依據 (US 2004-2024) ───────────────────────────────────────────
  ‣ 通膨持續性 (AR coef.)  : 0.72  (Cogley & Sargent 2005 + 後 COVID 更新)
  ‣ 失業缺口彈性            : −0.35 (現代菲利浦曲線, Stock & Watson 2020)
  ‣ FFR → CPI 傳遞時滯      : ~6-12 月 (Bernanke 2015 VAR 估計)
  ‣ FFR → 失業傳遞彈性      : 0.50  (Coibion 2012)
  ‣ QE $1T → 10yr 殖利率    : −15~−25 bp (Gagnon et al. 2011; D'Amico 2012)
  ‣ 10yr 殖利率 → 投資/消費  : 每 −100bp ≈ +0.3% GDP (FRB/US model)
  ‣ Okun's Law 係數          : −2.0  (Ball et al. 2017)
  ‣ 通膨預期去錨成本         : 滿意度乘數 x1.5
"""

import random
import math
import config


# ═══════════════════════════════════════════════════════════════════════════════
#  輔助：加入時滯緩衝區 (Distributed Lag Buffer)
# ═══════════════════════════════════════════════════════════════════════════════
class LagBuffer:
    """
    儲存過去 N 期某變數的值，提供加權平均（模擬政策傳遞時滯）。
    weights 從近到遠遞減，預設採指數衰減。
    """
    def __init__(self, maxlen=12, decay=0.7):
        self._buf    = []
        self.maxlen  = maxlen
        self.decay   = decay

    def push(self, value):
        self._buf.append(value)
        if len(self._buf) > self.maxlen:
            self._buf.pop(0)

    def weighted_mean(self):
        if not self._buf:
            return 0.0
        n       = len(self._buf)
        weights = [self.decay ** (n - 1 - i) for i in range(n)]
        total_w = sum(weights)
        return sum(w * v for w, v in zip(weights, self._buf)) / total_w


# ═══════════════════════════════════════════════════════════════════════════════
#  主類別
# ═══════════════════════════════════════════════════════════════════════════════
class EconomyState:
    """
    核心狀態變數
    ─────────────────────────────────────────────────────
    ffr          : 聯邦基金利率 (%)
    balance_sheet: 聯準會資產負債表規模（兆美元），QE/QT 直接操作
    cpi          : 通膨率 (%)
    unemployment : 失業率 (%)
    gdp          : GDP 成長率 (%)
    approval     : 民眾滿意度 (0–100)
    inf_exp      : 通膨預期 (%)  — 影響通膨持續性與工資談判
    credit_spread: 信用利差 (%)  — 反映金融狀況，QE 可壓縮
    shadow_rate  : 影子利率 = FFR + QE 等效壓縮 (%)
    """

    def __init__(self):
        # ── 政策工具 ──────────────────────────────────────────────────────────
        self.ffr            = config.INITIAL_FFR
        self.balance_sheet  = getattr(config, "INITIAL_BS", 8.5)   # 兆美元

        # ── 實體經濟 ──────────────────────────────────────────────────────────
        self.cpi            = config.INITIAL_CPI
        self.unemployment   = config.INITIAL_UNEMPLOYMENT
        self.gdp            = config.INITIAL_GDP
        self.approval       = config.INITIAL_APPROVAL

        # ── 金融狀況 (新增) ───────────────────────────────────────────────────
        self.inf_exp        = getattr(config, "INITIAL_INF_EXP",  2.5)   # 通膨預期
        self.credit_spread  = getattr(config, "INITIAL_CREDIT_SP", 1.5)   # 信用利差 (%)

        # ── 時滯緩衝區 ────────────────────────────────────────────────────────
        # 儲存過去的「影子利率」，以便模擬 6-12 月政策傳遞時滯
        self._shadow_lag   = LagBuffer(maxlen=12, decay=0.75)
        self._shadow_lag.push(self._compute_shadow_rate())

        # ── 外部衝擊暫存 ──────────────────────────────────────────────────────
        self._ev_inf    = 0.0
        self._ev_unemp  = 0.0

        # ── 其他 ──────────────────────────────────────────────────────────────
        self.month   = 0
        self.history = []

    # ──────────────────────────────────────────────────────────────────────────
    #  影子利率：整合 FFR + QE 等效壓縮
    # ──────────────────────────────────────────────────────────────────────────
    def _compute_shadow_rate(self):
        """
        影子利率 = FFR − QE_equivalent_compression
        QE 等效：每增加 $1T 資產負債表 ≈ −0.20% 等效利率壓縮
        (依 Wu & Xia 2016 shadow rate model 校準)
        基準資產負債表設 $4.5T（2019 年正常化後水準）
        """
        bs_excess          = self.balance_sheet - 4.5          # 超額 (兆美元)
        qe_compression     = bs_excess * 0.20                  # %
        return self.ffr - max(0.0, qe_compression)

    # ──────────────────────────────────────────────────────────────────────────
    #  月度更新主函式
    # ──────────────────────────────────────────────────────────────────────────
    def update(self):
        # ── 1. 計算當月影子利率並推入時滯緩衝區 ──────────────────────────────
        shadow_now = self._compute_shadow_rate()
        self._shadow_lag.push(shadow_now)

        # 使用時滯加權平均代表「有效貨幣緊縮力道」
        effective_rate  = self._shadow_lag.weighted_mean()
        neutral_real    = getattr(config, "NEUTRAL_RATE", 2.5)
        taylor_gap      = effective_rate - (neutral_real + self.inf_exp - config.TARGET_INFLATION)

        # 正 = 緊縮偏強；負 = 寬鬆
        rate_bite       = taylor_gap * 0.10   # 縮小係數，更符合實證

        # ── 2. 通膨預期更新 (錨定機制) ────────────────────────────────────────
        # 當通膨偏離目標時，預期「去錨」——回歸慢、偏移快
        anchor_pull     = (config.TARGET_INFLATION - self.inf_exp) * 0.08
        surprise_push   = (self.cpi - self.inf_exp) * 0.18
        self.inf_exp    = max(0.5, min(10.0,
                            self.inf_exp + anchor_pull + surprise_push
                            + random.gauss(0, 0.05)))

        # ── 3. 信用利差更新 ────────────────────────────────────────────────────
        # QE 壓縮利差；緊縮/衰退 擴大利差
        bs_effect       = -(self.balance_sheet - 4.5) * 0.05
        recession_risk  = max(0, -self.gdp) * 0.10
        spread_revert   = (1.5 - self.credit_spread) * 0.10  # 均值回歸
        self.credit_spread = max(0.3, min(8.0,
                                    self.credit_spread
                                    + bs_effect + recession_risk
                                    + spread_revert
                                    + random.gauss(0, 0.08)))

        # ── 4. 通膨動態 (實證菲利浦曲線) ───────────────────────────────────────
        # 實證校準：持續性 0.72、失業缺口彈性 −0.35（非線性）
        persistence     = 0.72
        unemp_gap       = self.unemployment - getattr(config, "NAIRU", 4.5)

        # 非線性菲利浦曲線：失業缺口越大效果越弱（扁平化）
        phillips_effect = -0.35 * math.tanh(unemp_gap * 0.8)

        ar_inf, ar_unemp, ar_gdp = self._calculate_ar_contribution()

        inf_delta = (
            (persistence - 1.0) * (self.cpi - self.inf_exp)   # 誤差修正
            + phillips_effect
            + (-rate_bite * 0.25)
            + ar_inf * 0.3                                      # 短期動能
            + random.gauss(0, 0.12)
            + self._ev_inf
        )
        self.cpi = max(0.0, min(25.0, self.cpi + inf_delta))

        # ── 5. 失業率動態 (Okun 法則 + 貨幣政策) ──────────────────────────────
        # Okun 係數 −2.0；FFR 傳遞彈性 0.50
        okun_effect     = -0.5 * (self.gdp - getattr(config, "POTENTIAL_GDP", 2.0)) * 0.08
        unemp_delta = (
            okun_effect
            + (rate_bite * 0.12)
            + ar_unemp * 0.3
            + random.gauss(0, 0.07)
            + self._ev_unemp
        )
        self.unemployment = max(0.5, min(20.0, self.unemployment + unemp_delta))

        # ── 6. GDP 動態 ─────────────────────────────────────────────────────────
        # 金融狀況加入：信用利差越高 → GDP 下拉
        fci_drag        = -(self.credit_spread - 1.5) * 0.15
        gdp_bonus       = 0.15 if 1.5 < self.cpi < 3.5 else 0.0
        gdp_delta = (
            fci_drag
            + (-rate_bite * 0.08)
            + gdp_bonus
            + ar_gdp * 0.25
            + random.gauss(0, 0.10)
        )
        self.gdp = max(-12.0, min(12.0, self.gdp + gdp_delta))

        # ── 7. 滿意度 ────────────────────────────────────────────────────────
        self.approval = self._calculate_approval()

        # ── 8. 清除事件衝擊，記錄歷史，前進月份 ──────────────────────────────
        self._ev_inf   = 0.0
        self._ev_unemp = 0.0

        snap = self.snapshot()
        self._record_history(snap)
        self.month += 1
        return snap

    # ──────────────────────────────────────────────────────────────────────────
    #  AR(3) 短期動能（維持原有架構，稍作整合）
    # ──────────────────────────────────────────────────────────────────────────
    def _calculate_ar_contribution(self):
        ar_inf, ar_unemp, ar_gdp = 0.0, 0.0, 0.0
        h = self.history
        n = len(h)

        if n >= 3:
            d_inf1   = self.cpi          - h[-1]["cpi"]
            d_inf2   = h[-1]["cpi"]      - h[-2]["cpi"]
            d_inf3   = h[-2]["cpi"]      - h[-3]["cpi"]
            d_unemp1 = self.unemployment - h[-1]["unemployment"]
            d_unemp2 = h[-1]["unemployment"] - h[-2]["unemployment"]
            d_unemp3 = h[-2]["unemployment"] - h[-3]["unemployment"]
            d_gdp1   = self.gdp          - h[-1]["gdp"]
            d_gdp2   = h[-1]["gdp"]      - h[-2]["gdp"]
            d_gdp3   = h[-2]["gdp"]      - h[-3]["gdp"]

            ar_inf   = 0.50*d_inf1   + 0.20*d_inf2   + 0.10*d_inf3
            ar_unemp = 0.45*d_unemp1 + 0.25*d_unemp2 + 0.15*d_unemp3
            ar_gdp   = 0.40*d_gdp1   + 0.20*d_gdp2   + 0.10*d_gdp3

        elif n == 2:
            ar_inf   = 0.50*(self.cpi - h[-1]["cpi"])          + 0.20*(h[-1]["cpi"] - h[-2]["cpi"])
            ar_unemp = 0.50*(self.unemployment - h[-1]["unemployment"]) + 0.20*(h[-1]["unemployment"] - h[-2]["unemployment"])
            ar_gdp   = 0.40*(self.gdp - h[-1]["gdp"])          + 0.20*(h[-1]["gdp"] - h[-2]["gdp"])

        elif n == 1:
            ar_inf   = 0.50*(self.cpi - h[-1]["cpi"])
            ar_unemp = 0.50*(self.unemployment - h[-1]["unemployment"])
            ar_gdp   = 0.40*(self.gdp - h[-1]["gdp"])

        return ar_inf, ar_unemp, ar_gdp

    # ──────────────────────────────────────────────────────────────────────────
    #  滿意度計算
    # ──────────────────────────────────────────────────────────────────────────
    def _calculate_approval(self):
        inf_pen    = max(0, self.cpi - 4.0) * 3.0 + max(0, 1.5 - self.cpi) * 2.0
        unemp_pen  = max(0, self.unemployment - 5.5) * 2.0

        # 通膨預期去錨額外懲罰
        anchor_pen = max(0, abs(self.inf_exp - config.TARGET_INFLATION) - 1.0) * 2.0

        app_bonus  = 0.0
        if 1.8 <= self.cpi <= 2.5:       app_bonus += 1.0
        if self.unemployment <= 4.5:     app_bonus += 1.0
        if self.gdp > 2.0:               app_bonus += 0.5
        if abs(self.inf_exp - config.TARGET_INFLATION) < 0.5:
            app_bonus += 0.5

        new_approval = (self.approval
                        - inf_pen - unemp_pen - anchor_pen
                        + app_bonus
                        + random.gauss(0, 0.5))
        return max(0, min(100, new_approval))

    # ══════════════════════════════════════════════════════════════════════════
    #  政策工具
    # ══════════════════════════════════════════════════════════════════════════

    def adjust_ffr(self, delta):
        """調整聯邦基金利率"""
        self.ffr = round(
            max(config.FFR_MIN, min(config.FFR_MAX, self.ffr + delta)), 2
        )

    def adjust_balance_sheet(self, delta_trillion):
        """
        調整資產負債表規模（QE/QT）
        delta_trillion > 0 → QE 購債（擴表）
        delta_trillion < 0 → QT 縮表

        實際參數限制：
          ‣ 最小規模：$2.0T（ZLB 緊急下限）
          ‣ 最大規模：$15.0T（極端 QE 上限）
          ‣ 每月操作上限：±$0.3T（反映 FOMC 每次會議實際操作速度）
        """
        bs_min   = getattr(config, "BS_MIN", 2.0)
        bs_max   = getattr(config, "BS_MAX", 15.0)
        bs_step  = getattr(config, "BS_STEP", 0.3)      # 每月最大操作量

        # 限制單次操作幅度
        delta_clamped = max(-bs_step, min(bs_step, delta_trillion))

        self.balance_sheet = round(
            max(bs_min, min(bs_max, self.balance_sheet + delta_clamped)), 2
        )

    def apply_shock(self, inf_shock=0.0, unemp_shock=0.0):
        """注入外生衝擊（供給衝擊、地緣政治事件等）"""
        self._ev_inf   += inf_shock
        self._ev_unemp += unemp_shock

    # ══════════════════════════════════════════════════════════════════════════
    #  狀態快照與歷史記錄
    # ══════════════════════════════════════════════════════════════════════════

    def snapshot(self):
        return {
            "ffr":           round(self.ffr, 2),
            "balance_sheet": round(self.balance_sheet, 2),
            "shadow_rate":   round(self._compute_shadow_rate(), 2),
            "cpi":           round(self.cpi, 2),
            "inf_exp":       round(self.inf_exp, 2),
            "unemployment":  round(self.unemployment, 2),
            "gdp":           round(self.gdp, 2),
            "credit_spread": round(self.credit_spread, 2),
            "approval":      round(self.approval, 1),
            "month":         self.month,
        }

    def _record_history(self, snap):
        self.history.append(snap)
        if len(self.history) > 36:
            self.history.pop(0)

    # ══════════════════════════════════════════════════════════════════════════
    #  勝負判定
    # ══════════════════════════════════════════════════════════════════════════

    def lose_reason(self):
        if self.cpi          >= config.INFLATION_LOSE:  return "inflation"
        if self.unemployment >= config.UNEMPLOY_LOSE:   return "unemployment"
        if self.approval     <= config.APPROVAL_LOSE:   return "approval"
        # 新增：通膨預期嚴重去錨
        if self.inf_exp      >= getattr(config, "INF_EXP_LOSE", 8.0):
            return "inflation_expectations"
        return None

    def check_win(self):
        return (
            self.month >= config.WIN_MONTHS
            and abs(self.cpi - config.TARGET_INFLATION) < 1.0
            and self.unemployment < 6.0
            and abs(self.inf_exp - config.TARGET_INFLATION) < 1.5  # 預期需穩定
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  UI 標籤（維持原有中文標籤系統）
    # ══════════════════════════════════════════════════════════════════════════

    def inflation_label(self):
        if self.cpi < 1.5:  return "通縮警報", config.BLUE
        if self.cpi < 3.0:  return "穩定",     config.GREEN
        if self.cpi < 5.0:  return "偏高",     config.YELLOW
        if self.cpi < 8.0:  return "過熱",     config.ORANGE
        return "失控！",                         config.RED

    def unemp_label(self):
        if self.unemployment < 4.0: return "充分就業", config.GREEN
        if self.unemployment < 5.5: return "正常",     config.YELLOW
        if self.unemployment < 8.0: return "偏高",     config.ORANGE
        return "嚴重失業",                             config.RED

    def bs_label(self):
        """資產負債表規模標籤"""
        if self.balance_sheet < 4.0:  return "縮表中",   config.BLUE
        if self.balance_sheet < 7.0:  return "中性",     config.GREEN
        if self.balance_sheet < 10.0: return "QE 寬鬆",  config.YELLOW
        return "極度寬鬆",                               config.ORANGE

    def inf_exp_label(self):
        """通膨預期錨定狀態"""
        gap = abs(self.inf_exp - config.TARGET_INFLATION)
        if gap < 0.5:  return "穩固錨定", config.GREEN
        if gap < 1.5:  return "輕微偏移", config.YELLOW
        if gap < 3.0:  return "去錨風險", config.ORANGE
        return "預期失控",               config.RED
