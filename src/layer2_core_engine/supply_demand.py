from dataclasses import dataclass
from typing import List, Optional
import pandas as pd
from .swing_detector import SwingPoint, detect_swing_points

@dataclass
class SupplyDemandZone:
    zone_type: str         # 'DEMAND' or 'SUPPLY'
    upper_bound: float
    lower_bound: float
    start_index: int
    is_sr_flip: bool = False
    is_mitigated: bool = False

def calculate_supply_demand_zones(df: pd.DataFrame, swing_window: int = 5) -> List[SupplyDemandZone]:
    """
    模組 2.1: 供需區算術引擎 (Supply & Demand Zone Calculator)
    將市場結構量化為確定性矩形區域，並檢測 S/R Flip（支撐壓力互換）
    """
    swings = detect_swing_points(df, window=swing_window)
    zones: List[SupplyDemandZone] = []
    
    current_price = df["close"].iloc[-1]
    
    for pt in swings:
        bar = df.iloc[pt.index]
        if pt.point_type == "LOW":
            # 需求區：低點至當根 K 線實體下緣
            lower = float(bar["low"])
            upper = float(min(bar["open"], bar["close"]))
            if upper <= lower:
                upper = lower + float(bar["atr_14"]) * 0.3
                
            zone = SupplyDemandZone(
                zone_type="DEMAND",
                upper_bound=upper,
                lower_bound=lower,
                start_index=pt.index,
                is_sr_flip=False
            )
            # 檢查後續是否被跌破轉壓力 (S/R Flip)
            subsequent_lows = df["low"].iloc[pt.index + 1 :]
            if len(subsequent_lows) > 0 and (subsequent_lows < lower).any():
                zone.is_sr_flip = True
                
            zones.append(zone)
            
        elif pt.point_type == "HIGH":
            # 供給區：當根 K 線實體上緣至最高點
            upper = float(bar["high"])
            lower = float(max(bar["open"], bar["close"]))
            if upper <= lower:
                lower = upper - float(bar["atr_14"]) * 0.3
                
            zone = SupplyDemandZone(
                zone_type="SUPPLY",
                upper_bound=upper,
                lower_bound=lower,
                start_index=pt.index,
                is_sr_flip=False
            )
            # 檢查後續是否被突破轉支撐 (S/R Flip)
            subsequent_highs = df["high"].iloc[pt.index + 1 :]
            if len(subsequent_highs) > 0 and (subsequent_highs > upper).any():
                zone.is_sr_flip = True
                
            zones.append(zone)
            
    return zones
