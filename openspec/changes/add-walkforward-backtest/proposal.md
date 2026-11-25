# Proposal: Multi-Asset Walk-Forward Backtesting & Six-Baseline Evaluation

## Why
Currently, `src/layer1_data/data_loader.py` generates synthetic OHLCV series and `src/layer2_core_engine/xgb_predictor.py` uses calibrated heuristic weights. To validate the FINSABER critique and evaluate whether the decoupled Hybrid TPA-Agent outperforms traditional technical indicators, XGBoost-only, and LLM-only baselines under realistic transaction friction, we need a full anti-leakage Walk-Forward Backtesting engine.

## What Changes
- Add a historical multi-asset OHLCV loader supporting cryptocurrencies, large-cap equities, and index ETFs.
- Implement a strict chronological Walk-Forward splitter (60% train / 20% validation / 20% out-of-sample test, or 6M/1M/1M rolling windows) with zero future-bar scaling leakage.
- Train and persist real `xgboost` classifiers per rolling fold inside `XGBWinRatePredictor`.
- Implement six comparison baselines: Buy-and-Hold, Random Signals (matched RR), MA Dual Crossover, RSI Strategy, XGBoost-Only, and LLM-Only.
- Simulate fee + slippage sensitivity curves across 0, 5, 10, 15, and 20 bps.

## Impact
- Modifies `src/layer1_data/data_loader.py` and `src/layer2_core_engine/xgb_predictor.py`.
- Adds `src/backtest/` and corresponding unit/regression tests in `tests/`.
