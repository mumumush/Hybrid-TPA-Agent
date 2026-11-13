from dataclasses import dataclass
from typing import List
import pandas as pd
import numpy as np

@dataclass
class SwingPoint:
    index: int
    timestamp: pd.Timestamp
    price: float
    point_type: str  # 'HIGH' or 'LOW'

def detect_swing_points(df: pd.DataFrame, window: int = 5) -> List[SwingPoint]:
    """
    模組 2.1 幾何子元件: 確定性波動高低點 (Swing High / Swing Low) 演算法
    100% 確定性數學運算，嚴格杜絕 LLM 空間幻覺。
    """
    swing_points = []
    highs = df["high"].values
    lows = df["low"].values
    timestamps = df["timestamp"].values

    for i in range(window, len(df) - window):
        # 檢驗局部高點
        if highs[i] == np.max(highs[i - window : i + window + 1]):
            swing_points.append(SwingPoint(
                index=i,
                timestamp=timestamps[i],
                price=float(highs[i]),
                point_type="HIGH"
            ))
        # 檢驗局部低點
        elif lows[i] == np.min(lows[i - window : i + window + 1]):
            swing_points.append(SwingPoint(
                index=i,
                timestamp=timestamps[i],
                price=float(lows[i]),
                point_type="LOW"
            ))
            
    return swing_points
