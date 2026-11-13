import pytest
import pandas as pd
import numpy as np
from src.layer1_data.data_loader import generate_mock_ohlcv
from src.layer2_core_engine.swing_detector import detect_swing_points
from src.layer2_core_engine.supply_demand import calculate_supply_demand_zones

def test_mock_ohlcv_generation():
    df = generate_mock_ohlcv(bars=50)
    assert len(df) == 50
    assert "atr_14" in df.columns
    assert "vol_zscore" in df.columns
    assert (df["high"] >= df["low"]).all()

def test_deterministic_swing_points():
    df = generate_mock_ohlcv(bars=80)
    swings = detect_swing_points(df, window=4)
    assert len(swings) > 0
    for s in swings:
        assert s.point_type in ["HIGH", "LOW"]
        assert s.price > 0

def test_supply_demand_zones_calculation():
    df = generate_mock_ohlcv(bars=80)
    zones = calculate_supply_demand_zones(df, swing_window=4)
    assert len(zones) > 0
    for z in zones:
        assert z.upper_bound >= z.lower_bound
        assert z.zone_type in ["DEMAND", "SUPPLY"]
