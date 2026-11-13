import pytest
from src.layer1_data.user_profile import UserProfile
from src.layer2_core_engine.supply_demand import SupplyDemandZone
from src.layer4_risk_output.risk_manager import RiskManager

def test_risk_manager_veto_low_rr():
    profile = UserProfile(min_rr_threshold=2.0)
    rm = RiskManager(profile)
    zone = SupplyDemandZone(zone_type="DEMAND", upper_bound=100.0, lower_bound=95.0, start_index=10)
    
    # 故意設定低目標價格，導致 RR < 2.0
    decision = rm.evaluate_trade(
        current_price=100.0,
        zone=zone,
        win_rate=0.60,
        atr=2.0,
        target_price=102.0 # 停損約 93 (risk=7), 獲利 2 (reward=2) -> RR < 1
    )
    assert decision.status == "NO_TRADE"
    assert "風報比 RR" in decision.reason

def test_risk_manager_approval_and_positive_expectation():
    profile = UserProfile(min_rr_threshold=2.0)
    rm = RiskManager(profile)
    zone = SupplyDemandZone(zone_type="DEMAND", upper_bound=100.0, lower_bound=96.0, start_index=10)
    
    # 正常高勝率、足夠空間獲利設定
    decision = rm.evaluate_trade(
        current_price=100.0,
        zone=zone,
        win_rate=0.60,
        atr=2.0,
        target_price=115.0 # risk=6, reward=15 -> RR = 2.5
    )
    assert decision.status == "APPROVED"
    assert decision.risk_reward_ratio >= 2.0
    assert decision.mathematical_expectation > 0
    assert decision.position_size > 0

def test_circuit_breaker_consecutive_losses():
    rm = RiskManager()
    zone = SupplyDemandZone(zone_type="DEMAND", upper_bound=100.0, lower_bound=96.0, start_index=10)
    decision = rm.evaluate_trade(
        current_price=100.0,
        zone=zone,
        win_rate=0.65,
        atr=2.0,
        consecutive_losses=2
    )
    assert decision.status == "NO_TRADE"
    assert decision.circuit_breaker_active is True
    assert "Level 2 熔斷" in decision.reason
