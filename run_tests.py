import sys
import traceback
from src.layer1_data.data_loader import generate_mock_ohlcv
from src.layer1_data.user_profile import UserProfile
from src.layer2_core_engine.swing_detector import detect_swing_points
from src.layer2_core_engine.supply_demand import calculate_supply_demand_zones
from src.layer2_core_engine.xgb_predictor import XGBWinRatePredictor
from src.layer3_reasoning.cot_planner import CoTPlanningAgent
from src.layer4_risk_output.risk_manager import RiskManager
from src.layer4_risk_output.report_generator import ReportGenerator

def run_all_tests():
    print("==================================================")
    print("  Hybrid TPA-Agent: 執行全系統單元與整合測試")
    print("==================================================")
    
    passed = 0
    total = 0

    def test(name, fn):
        nonlocal passed, total
        total += 1
        try:
            fn()
            print(f"[PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            traceback.print_exc()

    # Test 1: Data Generation
    def test_data():
        df = generate_mock_ohlcv(bars=60)
        assert len(df) == 60
        assert "atr_14" in df.columns
        assert (df["high"] >= df["low"]).all()
    test("Layer 1: OHLCV 資料生成與 ATR 計算", test_data)

    # Test 2: Geometry & Swings
    def test_geometry():
        df = generate_mock_ohlcv(bars=80)
        swings = detect_swing_points(df, window=4)
        assert len(swings) > 0
        zones = calculate_supply_demand_zones(df, swing_window=4)
        assert len(zones) > 0
        for z in zones:
            assert z.upper_bound >= z.lower_bound
    test("Layer 2: 幾何 Swing Points 與供需區演算法", test_geometry)

    # Test 3: ML Predictor
    def test_ml():
        df = generate_mock_ohlcv(bars=80)
        zones = calculate_supply_demand_zones(df, swing_window=4)
        xgb = XGBWinRatePredictor(confidence_threshold=0.55)
        win_rate, filter_passed, meta = xgb.predict_conditional_win_rate(df, zones[-1])
        assert 0.0 <= win_rate <= 1.0
        assert "win_rate" in meta
    test("Layer 2: XGBoost 條件勝率與防洩漏特徵提取", test_ml)

    # Test 4: CoT Reasoning
    def test_cot():
        df = generate_mock_ohlcv(bars=80)
        zones = calculate_supply_demand_zones(df, swing_window=4)
        xgb = XGBWinRatePredictor()
        _, _, meta = xgb.predict_conditional_win_rate(df, zones[-1])
        agent = CoTPlanningAgent()
        cot_res = agent.generate_cot_reasoning(
            {"zone_type": zones[-1].zone_type, "is_sr_flip": zones[-1].is_sr_flip},
            meta
        )
        assert len(cot_res["chain_of_thought"]) == 4
    test("Layer 3: 領域知識庫與 CoT 思維鏈推理", test_cot)

    # Test 5: Risk Manager & Veto
    def test_risk():
        user = UserProfile(min_rr_threshold=2.0)
        rm = RiskManager(user)
        df = generate_mock_ohlcv(bars=80)
        zones = calculate_supply_demand_zones(df, swing_window=4)
        
        # 測試正常通過
        dec_ok = rm.evaluate_trade(
            current_price=100.0,
            zone=zones[-1],
            win_rate=0.62,
            atr=2.0,
            target_price=112.0
        )
        assert dec_ok.status in ["APPROVED", "NO_TRADE"]
        if dec_ok.status == "APPROVED":
            assert dec_ok.mathematical_expectation > 0
            assert dec_ok.risk_reward_ratio >= 2.0

        # 測試連虧 2 筆 Level 2 熔斷
        dec_halt = rm.evaluate_trade(
            current_price=100.0,
            zone=zones[-1],
            win_rate=0.65,
            atr=2.0,
            consecutive_losses=2
        )
        assert dec_halt.status == "NO_TRADE"
        assert dec_halt.circuit_breaker_active is True
    test("Layer 4: 風控引擎、期望值 E > 0 與 Level 2 熔斷", test_risk)

    print("--------------------------------------------------")
    print(f"測試完成: {passed}/{total} 測試通過")
    if passed == total:
        print("[SUCCESS] 全模組測試 100% 通過！")
        return 0
    else:
        print("[WARNING] 部分測試未通過。")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
