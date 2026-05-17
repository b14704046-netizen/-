import random
import config


class EconomyState:
    def __init__(self):
        self.ffr          = config.INITIAL_FFR
        self.cpi          = config.INITIAL_CPI
        self.unemployment = config.INITIAL_UNEMPLOYMENT
        self.gdp          = config.INITIAL_GDP
        self.approval     = config.INITIAL_APPROVAL
        self.month        = 0
        self._ev_inf   = 0.0
        self._ev_unemp = 0.0
        self.history   = []   # list of monthly snapshots

    # ------------------------------------------------------------------
    def update(self):
        self._snapshot()

        # Taylor Rule implied direction
        taylor_gap = self.ffr - (config.NEUTRAL_RATE + self.cpi - config.TARGET_INFLATION)
        rate_bite  = taylor_gap * 0.12          # how hard the rate is biting

        # Phillips Curve: tighter money → lower inflation, higher unemployment
        inf_delta   = -rate_bite + random.gauss(0, 0.25) + self._ev_inf
        unemp_delta =  rate_bite * 0.55 + random.gauss(0, 0.18) + self._ev_unemp

        self.cpi          = max(0.0,  min(25.0, self.cpi + inf_delta))
        self.unemployment = max(0.5,  min(20.0, self.unemployment + unemp_delta))

        # GDP
        gdp_delta  = -rate_bite * 0.3 + random.gauss(0, 0.2)
        if self.cpi < 3.5:
            gdp_delta += 0.05
        self.gdp = max(-12.0, min(12.0, self.gdp + gdp_delta))

        # Approval: punish high inflation and high unemployment
        inf_pen   = max(0, self.cpi - 3.0)  * 2.5
        unemp_pen = max(0, self.unemployment - 5.0) * 1.5
        self.approval = max(0, min(100, self.approval - inf_pen - unemp_pen + random.gauss(0, 0.8)))

        self._ev_inf   = 0.0
        self._ev_unemp = 0.0
        self.month    += 1
        return self.snapshot()

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

    def _snapshot(self):
        self.history.append(self.snapshot())
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
        if self.cpi < 2.0: return "通縮警報", config.BLUE
        if self.cpi < 3.0: return "穩定", config.GREEN
        if self.cpi < 6.0: return "偏高", config.YELLOW
        if self.cpi < 10.: return "過熱", config.ORANGE
        return "失控！", config.RED

    def unemp_label(self):
        if self.unemployment < 4.0: return "充分就業", config.GREEN
        if self.unemployment < 6.0: return "正常", config.YELLOW
        if self.unemployment < 9.0: return "偏高", config.ORANGE
        return "嚴重失業", config.RED
