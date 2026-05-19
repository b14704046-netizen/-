import random
import config


class EconomyState:
    def __init__(self):
        self.ffr           = config.INITIAL_FFR
        self.cpi           = config.INITIAL_CPI
        self.unemployment = config.INITIAL_UNEMPLOYMENT
        self.gdp           = config.INITIAL_GDP
        self.approval      = config.INITIAL_APPROVAL
        self.month         = 0
        self._ev_inf       = 0.0
        self._ev_unemp     = 0.0
        self.history       = []   # 儲存過去每月的 snapshot

    # ------------------------------------------------------------------
    def update(self):
        # 1. 基礎政策力道 (泰勒法則)
        taylor_gap = self.ffr - (config.NEUTRAL_RATE + self.cpi - config.TARGET_INFLATION)
        rate_bite  = taylor_gap * 0.12  

        # 2. 提取歷史資料，計算 AR(3) 的權重貢獻
        ar_inf, ar_unemp, ar_gdp = self._calculate_ar_contribution()

        # 3. 結合歷史動態、貨幣政策與隨機衝擊 (菲利浦曲線動態)
        inf_delta   = ar_inf + (-rate_bite * 0.3) + random.gauss(0, 0.15) + self._ev_inf
        unemp_delta = ar_unemp + (rate_bite * 0.15) + random.gauss(0, 0.08) + self._ev_unemp

        self.cpi           = max(0.0, min(25.0, self.cpi + inf_delta))
        self.unemployment = max(0.5, min(20.0, self.unemployment + unemp_delta))

        # 4. GDP 動態優化
        gdp_bonus = 0.1 if 1.5 < self.cpi < 3.5 else 0.0
        gdp_delta = ar_gdp + (-rate_bite * 0.1) + gdp_bonus + random.gauss(0, 0.12)
        self.gdp  = max(-12.0, min(12.0, self.gdp + gdp_delta))

        # 5. 滿意度機制計算
        self.approval = self._calculate_approval()

        # 6. 清除事件衝擊，時間前進
        self._ev_inf   = 0.0
        self._ev_unemp = 0.0
        
        # 7. 先記錄這回合更新完的最終狀態，再前進月份並回傳
        current_snap = self.snapshot()
        self._record_history(current_snap)
        self.month += 1
        
        return current_snap

    # ------------------------------------------------------------------
    def _calculate_ar_contribution(self):
        """依據歷史資料長度，計算自迴歸 AR(1) ~ AR(3) 的趨勢貢獻量"""
        ar_inf, ar_unemp, ar_gdp = 0.0, 0.0, 0.0
        h_len = len(self.history)

        if h_len >= 3:
            t_minus_1 = self.history[-1]
            t_minus_2 = self.history[-2]
            t_minus_3 = self.history[-3]

            # 計算歷史各期的連續差值 (Delta)
            delta_inf_1 = self.cpi - t_minus_1["cpi"]
            delta_inf_2 = t_minus_1["cpi"] - t_minus_2["cpi"]
            delta_inf_3 = t_minus_2["cpi"] - t_minus_3["cpi"]

            delta_unemp_1 = self.unemployment - t_minus_1["unemployment"]
            delta_unemp_2 = t_minus_1["unemployment"] - t_minus_2["unemployment"]
            delta_unemp_3 = t_minus_2["unemployment"] - t_minus_3["unemployment"]

            delta_gdp_1 = self.gdp - t_minus_1["gdp"]
            delta_gdp_2 = t_minus_1["gdp"] - t_minus_2["gdp"]
            delta_gdp_3 = t_minus_1["gdp"] - t_minus_3["gdp"]

            # 套用 AR(3) 權重
            ar_inf   = (0.50 * delta_inf_1) + (0.20 * delta_inf_2) + (0.10 * delta_inf_3)
            ar_unemp = (0.45 * delta_unemp_1) + (0.25 * delta_unemp_2) + (0.15 * delta_unemp_3)
            ar_gdp   = (0.40 * delta_gdp_1) + (0.20 * delta_gdp_2) + (0.10 * delta_gdp_3)

        elif h_len == 2:
            t_minus_1 = self.history[-1]
            t_minus_2 = self.history[-2]
            
            ar_inf   = 0.5 * (self.cpi - t_minus_1["cpi"]) + 0.2 * (t_minus_1["cpi"] - t_minus_2["cpi"])
            ar_unemp = 0.5 * (self.unemployment - t_minus_1["unemployment"]) + 0.2 * (t_minus_1["unemployment"] - t_minus_2["unemployment"])
            ar_gdp   = 0.4 * (self.gdp - t_minus_1["gdp"]) + 0.2 * (t_minus_1["gdp"] - t_minus_2["gdp"])

        elif h_len == 1:
            t_minus_1 = self.history[-1]
            
            ar_inf   = 0.5 * (self.cpi - t_minus_1["cpi"])
            ar_unemp = 0.5 * (self.unemployment - t_minus_1["unemployment"])
            ar_gdp   = 0.4 * (self.gdp - t_minus_1["gdp"])

        return ar_inf, ar_unemp, ar_gdp

    def _calculate_approval(self):
        """計算滿意度的獎懲與隨機波動"""
        # 懲罰項：通膨太高/通縮、失業率過高
        inf_pen   = max(0, self.cpi - 4.0) * 3.0 + max(0, 1.5 - self.cpi) * 2.0
        unemp_pen = max(0, self.unemployment - 5.5) * 2.0
        
        # 獎勵項：指標在完美區間時加分
        app_bonus = 0.0
        if 1.8 <= self.cpi <= 2.5:   app_bonus += 1.0
        if self.unemployment <= 4.5: app_bonus += 1.0
        if self.gdp > 2.0:           app_bonus += 0.5

        new_approval = self.approval - inf_pen - unemp_pen + app_bonus + random.gauss(0, 0.5)
        return max(0, min(100, new_approval))

    # ------------------------------------------------------------------
    def adjust_ffr(self, delta):
        self.ffr = round(
            max(config.FFR_MIN, min(config.FFR_MAX, self.ffr + delta)), 2
        )

    def apply_shock(self, inf_shock=0.0, unemp_shock=0.0):
        self._ev_inf   += inf_shock
        self._ev_unemp += unemp_shock

    # ------------------------------------------------------------------
    def snapshot(self):
        return {
            "ffr":          round(self.ffr, 2),
            "cpi":          round(self.cpi, 2),
            "unemployment": round(self.unemployment, 2),
            "gdp":          round(self.gdp, 2),
            "approval":     round(self.approval, 1),
            "month":        self.month,
        }

    def _record_history(self, snap):
        self.history.append(snap)
        if len(self.history) > 36: 
            self.history.pop(0)

    # ------------------------------------------------------------------
    def lose_reason(self):
        if self.cpi          >= config.INFLATION_LOSE:  return "inflation"
        if self.unemployment >= config.UNEMPLOY_LOSE:   return "unemployment"
        if self.approval     <= config.APPROVAL_LOSE:   return "approval"
        return None

    def check_win(self):
        return (
            self.month >= config.WIN_MONTHS
            and abs(self.cpi - config.TARGET_INFLATION) < 1.0
            and self.unemployment < 6.0
        )

    # ------------------------------------------------------------------
    def inflation_label(self):
        if self.cpi < 1.5: return "通縮警報", config.BLUE
        if self.cpi < 3.0: return "穩定", config.GREEN
        if self.cpi < 5.0: return "偏高", config.YELLOW
        if self.cpi < 8.0: return "過熱", config.ORANGE
        return "失控！", config.RED

    def unemp_label(self):
        if self.unemployment < 4.0: return "充分就業", config.GREEN
        if self.unemployment < 5.5: return "正常", config.YELLOW
        if self.unemployment < 8.0: return "偏高", config.ORANGE
        return "嚴重失業", config.RED