# Data Ingestion & User Risk Profile Specification

## Purpose
Defines Layer 1 (`src/layer1_data/`) responsibilities for capturing user risk constraints and producing leak-free OHLCV market series enriched with volatility and volume normalization indicators.

## Requirements

### Requirement: User Risk Profile Constraints
The system SHALL represent trader capital and hard risk limits via `UserProfile` (`src/layer1_data/user_profile.py`), providing a deterministic per-trade maximum loss budget.

#### Scenario: Compute per-trade risk budget
- **WHEN** `UserProfile` is initialized with `account_capital = 10000.0` and `max_risk_pct = 0.01`
- **THEN** `get_max_loss_budget()` returns `100.0` USD
- **AND** default thresholds enforce `max_daily_loss_pct = 0.03`, `min_rr_threshold = 2.0`, `min_win_rate = 0.55`, and `max_leverage = 5.0`

### Requirement: OHLCV Data Generation and Indicator Enrichment
The data ingestion engine (`generate_mock_ohlcv` in `src/layer1_data/data_loader.py`) SHALL output a time-ordered `pandas.DataFrame` containing valid OHLCV columns along with causal `atr_14` and `vol_zscore` features.

#### Scenario: Generate valid OHLCV stream with ATR(14) and Volume Z-score
- **WHEN** `generate_mock_ohlcv(symbol, bars=60)` is invoked
- **THEN** the returned DataFrame has length `60`
- **AND** every row satisfies `high >= low`
- **AND** columns `timestamp`, `open`, `high`, `low`, `close`, `volume`, `atr_14`, and `vol_zscore` are present without look-ahead dependencies
