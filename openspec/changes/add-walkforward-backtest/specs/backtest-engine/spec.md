# Walk-Forward Backtesting Delta Specification

## ADDED Requirements

### Requirement: Zero-Leakage Chronological Walk-Forward Splitting
The backtest engine SHALL partition historical OHLCV datasets strictly by timestamp without random shuffling or cross-window scaler leakage.

#### Scenario: Rolling fold feature normalization
- **WHEN** a rolling fold trains on `[t_0, t_k]` and tests on `(t_k, t_m]`
- **THEN** all normalization statistics and XGBoost parameters are derived exclusively from `[t_0, t_k]`

### Requirement: Transaction Cost Sensitivity Evaluation
The backtest engine SHALL evaluate net strategy metrics across variable slippage levels (0, 5, 10, 15, and 20 bps) alongside a 5 bps baseline commission.

#### Scenario: Compute friction-adjusted net expectation
- **WHEN** a backtest run completes under slippage `s` bps
- **THEN** the output report records `net_expectation`, `sharpe_ratio`, `sortino_ratio`, `calmar_ratio`, `max_drawdown`, and `realized_rr`
