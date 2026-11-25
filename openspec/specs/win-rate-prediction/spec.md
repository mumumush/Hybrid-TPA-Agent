# Conditional Win-Rate Prediction Specification

## Purpose
Defines Layer 2.2 (`src/layer2_core_engine/xgb_predictor.py`) anti-leakage feature engineering and conditional win-rate probability filtering.

## Requirements

### Requirement: Anti-Leakage Price Action Feature Extraction
`XGBWinRatePredictor.extract_features(df, zone)` SHALL compute a 5-dimensional numerical feature vector strictly from the current bar and deterministic zone coordinates: `[dist_zone_atr, body_atr_ratio, vol_z, wick_rejection, is_flip]`.

#### Scenario: Extract 5-element feature vector for a zone
- **WHEN** `extract_features(df, zone)` runs on the latest bar `df.iloc[-1]`
- **THEN** it returns a `numpy.ndarray` of shape `(1, 5)`
- **AND** `wick_rejection` measures lower-wick-to-body ratio for `DEMAND` zones and upper-wick-to-body ratio for `SUPPLY` zones

### Requirement: Conditional Win-Rate Probability Gate
`XGBWinRatePredictor.predict_conditional_win_rate(df, zone)` SHALL output a bounded probability `W` in `[0.35, 0.78]` (within `[0.0, 1.0]`) and a boolean `filter_passed` flag comparing `W >= confidence_threshold` (default `0.55`).

#### Scenario: Evaluate conditional win rate and confidence metadata
- **WHEN** `predict_conditional_win_rate(df, zone)` is called with `confidence_threshold=0.55`
- **THEN** the returned `win_rate` satisfies `0.0 <= win_rate <= 1.0`
- **AND** `filter_passed` is `True` if and only if `win_rate >= 0.55`
- **AND** the returned `meta` dictionary contains `model_version`, `features_raw`, `win_rate`, `threshold`, and `filter_passed`
