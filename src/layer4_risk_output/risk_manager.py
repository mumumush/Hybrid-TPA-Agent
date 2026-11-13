from dataclasses import dataclass
from typing import Optional, Tuple
from ..layer1_data.user_profile import UserProfile
from ..layer2_core_engine.supply_demand import SupplyDemandZone

@dataclass
class RiskDecision:
    status: str                # 'APPROVED', 'NO_TRADE', 'WAIT'
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float
    mathematical_expectation: float
    position_size: float
    reason: str
    circuit_breaker_active: bool = False

class RiskManager:
    """
    模組 4.1: 決策與風控引擎 (Decision & Risk Control Engine)
    擁有整個系統的最高否決權 (Veto Power)。
    嚴格檢驗：
    1. 風報比門檻: RR >= min_rr (預設 2.0)
    2. 正期望值檢驗: E = W * RR - (1 - W) > 0
    3. 動態 ATR 結構停損
    4. 熔斷降級機制 (Level 1~3)
    """
    def __init__(self, user_profile: Optional[UserProfile] = None):
        self.profile = user_profile or UserProfile()

    def evaluate_trade(
        self,
        current_price: float,
        zone: SupplyDemandZone,
        win_rate: float,
        atr: float,
        target_price: Optional[float] = None,
        consecutive_losses: int = 0,
        latency_seconds: float = 0.5
    ) -> RiskDecision:
        # [Level 3 熔斷檢驗: API/數據延遲過高]
        if latency_seconds > 5.0:
            return RiskDecision(
                status="NO_TRADE",
                entry_price=current_price,
                stop_loss=0.0,
                take_profit=0.0,
                risk_reward_ratio=0.0,
                mathematical_expectation=0.0,
                position_size=0.0,
                reason="Level 3 熔斷觸發：數據源延遲 > 5.0 秒，啟動安全保護禁止開倉。",
                circuit_breaker_active=True
            )

        # [Level 2 熔斷檢驗: 當日連續虧損]
        if consecutive_losses >= 2:
            return RiskDecision(
                status="NO_TRADE",
                entry_price=current_price,
                stop_loss=0.0,
                take_profit=0.0,
                risk_reward_ratio=0.0,
                mathematical_expectation=0.0,
                position_size=0.0,
                reason="Level 2 熔斷觸發：當日已連續 2 筆停損，鎖定今日交易以阻斷情緒化過度下單。",
                circuit_breaker_active=True
            )

        # 幾何停損計算 (緊貼結構邊界外加 1.0 ATR)
        atr_buffer = 1.0 * atr
        if zone.zone_type == "DEMAND":
            entry = current_price
            stop_loss = zone.lower_bound - atr_buffer
            risk_per_unit = entry - stop_loss
            if risk_per_unit <= 0:
                risk_per_unit = atr_buffer
                stop_loss = entry - atr_buffer
            
            # 若無指定目標，以最小 2.4 RR 預設目標
            if target_price is None or target_price <= entry:
                target_price = entry + risk_per_unit * 2.4
                
            reward_per_unit = target_price - entry
        else: # SUPPLY
            entry = current_price
            stop_loss = zone.upper_bound + atr_buffer
            risk_per_unit = stop_loss - entry
            if risk_per_unit <= 0:
                risk_per_unit = atr_buffer
                stop_loss = entry + atr_buffer
                
            if target_price is None or target_price >= entry:
                target_price = entry - risk_per_unit * 2.4
                
            reward_per_unit = entry - target_price

        # 計算風報比 (Risk-to-Reward Ratio)
        rr = reward_per_unit / risk_per_unit if risk_per_unit > 0 else 0.0

        # 計算數學期望值: E = W * RR - (1 - W)
        expectation = (win_rate * rr) - (1.0 - win_rate)

        # [閘門檢驗 1: 風報比門檻]
        if rr < self.profile.min_rr_threshold:
            return RiskDecision(
                status="NO_TRADE",
                entry_price=entry,
                stop_loss=stop_loss,
                take_profit=target_price,
                risk_reward_ratio=rr,
                mathematical_expectation=expectation,
                position_size=0.0,
                reason=f"風控否決：風報比 RR ({rr:.2f}) 低於門檻 ({self.profile.min_rr_threshold:.2f})。"
            )

        # [閘門檢驗 2: 期望值必須大於 0]
        if expectation <= 0:
            return RiskDecision(
                status="NO_TRADE",
                entry_price=entry,
                stop_loss=stop_loss,
                take_profit=target_price,
                risk_reward_ratio=rr,
                mathematical_expectation=expectation,
                position_size=0.0,
                reason=f"風控否決：數學期望值 E ({expectation:.3f}) <= 0，不具統計優勢。"
            )

        # 計算倉位手數 (依風險預算嚴格配額)
        risk_budget = self.profile.get_max_loss_budget()
        position_size = risk_budget / risk_per_unit

        return RiskDecision(
            status="APPROVED",
            entry_price=round(entry, 2),
            stop_loss=round(stop_loss, 2),
            take_profit=round(target_price, 2),
            risk_reward_ratio=round(rr, 2),
            mathematical_expectation=round(expectation, 3),
            position_size=round(position_size, 4),
            reason=f"審核通過：滿足勝率 ({win_rate*100:.1f}%)、RR ({rr:.2f} >= 2.0) 與正期望值 (E = {expectation:.3f} > 0)。"
        )
