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

    def update(self):
        # 1. 基礎政策力道 (泰勒法則)
        taylor_gap = self.ffr - (config.NEUTRAL_RATE + self.cpi - config.TARGET_INFLATION)
        rate_bite  = taylor_gap * 0.12  

        # --- 2. 提取歷史資料，計算 AR(3) 的權重貢獻 ---
        # 宣告歷史慣性的累積變數
        ar_inf_contribution   = 0.0
        ar_unemp_contribution = 0.0
        ar_gdp_contribution   = 0.0

        h_len = len(self.history)
        
        # 必須有足夠的歷史資料 (至少3個月) 才能啟動完整的 AR(3)
        if h_len >= 3:
            # 取得歷史快照
            t_minus_1 = self.history[-1]  # 上個月
            t_minus_2 = self.history[-2]  # 前兩個月
            t_minus_3 = self.history[-3]  # 前三個月

            # 計算歷史各期的實際數值
            # (註：因為歷史存的是絕對值，我們用當前值與歷史值的差來推估最近期的趨勢)
            delta_inf_1 = self.cpi - t_minus_1["cpi"]
            delta_inf_2 = t_minus_1["cpi"] - t_minus_2["cpi"]
            delta_inf_3 = t_minus_2["cpi"] - t_minus_3["cpi"]

            delta_unemp_1 = self.unemployment - t_minus_1["unemployment"]
            delta_unemp_2 = t_minus_1["unemployment"] - t_minus_2["unemployment"]
            delta_unemp_3 = t_minus_2["unemployment"] - t_minus_3["unemployment"]

            delta_gdp_1 = self.gdp - t_minus_1["gdp"]
            delta_gdp_2 = t_minus_1["gdp"] - t_minus_2["gdp"]
            delta_gdp_3 = t_minus_2["gdp"] - t_minus_3["gdp"]

            # AR(3) 權重設定：越近的月份影響越大 (權重相加不需要等於1，但總和大約在 0.5~0.8 遊戲感最好)
            # 通膨：上月影響 50%，前月 20%，大前月 10%
            ar_inf_contribution = (0.50 * delta_inf_1) + (0.20 * delta_inf_2) + (0.10 * delta_inf_3)
            # 失業率：上月影響 45%，前月 25%，大前月 15% (失業率結構性更強，長尾效應明顯)
            ar_unemp_contribution = (0.45 * delta_unemp_1) + (0.25 * delta_unemp_2) + (0.15 * delta_unemp_3)
            # GDP：上月影響 40%，前月 20%，大前月 10%
            ar_gdp_contribution = (0.40 * delta_gdp_1) + (0.20 * delta_gdp_2) + (0.10 * delta_gdp_3)
            
        elif h_len == 2:  # 歷史資料只有2個月時的過渡方案 AR(2)
            ar_inf_contribution   = 0.5 * (self.cpi - self.history[-1]["cpi"]) + 0.2 * (self.history[-1]["cpi"] - self.history[-2]["cpi"])
            ar_unemp_contribution = 0.5 * (self.unemployment - self.history[-1]["unemployment"]) + 0.2 * (self.history[-1]["unemployment"] - self.history[-2]["unemployment"])
            ar_gdp_contribution   = 0.4 * (self.gdp - self.history[-1]["gdp"]) + 0.2 * (self.history[-1]["gdp"] - self.history[-2]["gdp"])
            
        elif h_len == 1:  # 歷史資料只有1個月時的過渡方案 AR(1)
            ar_inf_contribution   = 0.5 * (self.cpi - self.history[-1]["cpi"])
            ar_unemp_contribution = 0.5 * (self.unemployment - self.history[-1]["unemployment"])
            ar_gdp_contribution   = 0.4 * (self.gdp - self.history[-1]["gdp"])

        # --- 3. 結合歷史動態與當前衝擊 ---
        inf_delta   = ar_inf_contribution + (-rate_bite * 0.3) + random.gauss(0, 0.15) + self._ev_inf
        unemp_delta = ar_unemp_contribution + (rate_bite * 0.15) + random.gauss(0, 0.08) + self._ev_unemp

        self.cpi           = max(0.0,  min(25.0, self.cpi + inf_delta))
        self.unemployment = max(0.5,  min(20.0, self.unemployment + unemp_delta))

        gdp_bonus = 0.1 if 1.5 < self.cpi < 3.5 else 0.0
        gdp_delta = ar_gdp_contribution + (-rate_bite * 0.1) + gdp_bonus + random.gauss(0, 0.12)
        self.gdp  = max(-12.0, min(12.0, self.gdp + gdp_delta))

        # 4. 滿意度機制 (維持不變)
        inf_pen   = max(0, self.cpi - 4.0) * 3.0 + max(0, 1.5 - self.cpi) * 2.0
        unemp_pen = max(0, self.unemployment - 5.5) * 2.0
        app_bonus = 1.0 if (1.8 <= self.cpi <= 2.5 and self.unemployment <= 4.5) else 0.0
        self.approval = max(0, min(100, self.approval - inf_pen - unemp_pen + app_bonus + random.gauss(0, 0.5)))

        # 5. 清除事件衝擊，時間前進
        self._ev_inf   = 0.0
        self._ev_unemp = 0.0
        
        # 6. 先記錄這回合更新完的最終狀態，再前進月份並回傳
        current_snap = self.snapshot()
        self.history.append(current_snap)
        if len(self.history) > 36: 
            self.history.pop(0)
            
        self.month += 1
        return current_snap