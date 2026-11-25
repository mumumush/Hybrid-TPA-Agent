# Design: Anti-Leakage Walk-Forward Backtesting Engine

## Chronological Split Policy
- All feature scalers (mean, standard deviation) and XGBoost trees are fit strictly on `[t_start, t_train_end]` and evaluated out-of-sample on `(t_val_end, t_test_end]`.
- Random shuffling (`shuffle=True`) is strictly forbidden.

## Friction Cost Model
- Each executed round-trip trade deducts baseline exchange fee (5 bps) plus variable slippage (0, 5, 10, 15, 20 bps).
- Reports Sharpe Ratio, Sortino Ratio, Calmar Ratio, Maximum Drawdown (MDD), realized risk-reward ratio, and net expectation $E_{\text{net}}$.
