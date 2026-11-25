# Tasks: Multi-Asset Walk-Forward Backtesting Engine

- [ ] Implement historical OHLCV data ingestion with strict monotonic timestamp validation
- [ ] Implement Walk-Forward rolling window splitter (6M train / 1M val / 1M test)
- [ ] Train fold-isolated XGBoost models inside `XGBWinRatePredictor`
- [ ] Implement 6 baseline strategies (Buy-and-Hold, Random, MA, RSI, XGBoost-Only, LLM-Only)
- [ ] Implement 0–20 bps friction cost sweep and White's Reality Check
- [ ] Populate Section VI empirical results tables in `paper/main.tex`
