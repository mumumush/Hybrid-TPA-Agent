import pandas as pd
import numpy as np

def generate_mock_ohlcv(symbol: str = "BTC/USDT", bars: int = 120, base_price: float = 65000.0) -> pd.DataFrame:
    """
    模組 1.2: 資料接收引擎 (OHLCV Stream & ATR 計算)
    若無外部即時 API，可自動產出具備價格結構之標準 OHLCV 資料
    """
    np.random.seed(42)
    timestamps = pd.date_range(end=pd.Timestamp.now(), periods=bars, freq="15min")
    
    # 模擬幾何價格波動
    noise = np.random.normal(0, 150, bars)
    trend = np.sin(np.linspace(0, 3 * np.pi, bars)) * 800
    close_prices = base_price + trend + np.cumsum(noise)
    
    high_prices = close_prices + np.abs(np.random.normal(100, 50, bars))
    low_prices = close_prices - np.abs(np.random.normal(100, 50, bars))
    open_prices = np.roll(close_prices, 1)
    open_prices[0] = base_price

    volumes = np.random.randint(100, 1500, bars).astype(float)
    # 局部引發異常成交量
    if bars > 45:
        volumes[int(bars * 0.4)] *= 3.5
    if bars > 70:
        volumes[int(bars * 0.7)] *= 2.8

    df = pd.DataFrame({
        "timestamp": timestamps,
        "open": open_prices,
        "high": high_prices,
        "low": low_prices,
        "close": close_prices,
        "volume": volumes
    })

    # 計算 ATR (Average True Range 14)
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["atr_14"] = tr.rolling(window=14, min_periods=1).mean()
    df["vol_zscore"] = (df["volume"] - df["volume"].rolling(20, min_periods=1).mean()) / (df["volume"].rolling(20, min_periods=1).std() + 1e-6)

    return df
