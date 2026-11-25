# Deterministic Price Geometry Engine Specification

## Purpose
Defines Layer 2.1 (`src/layer2_core_engine/swing_detector.py` and `supply_demand.py`) deterministic geometric algorithms that eliminate LLM spatial hallucination.

## Requirements

### Requirement: Deterministic Swing High and Swing Low Detection
The swing detector (`detect_swing_points`) SHALL identify local price extrema over a symmetric window `[i - window, i + window]` using purely deterministic numerical comparisons.

#### Scenario: Detect valid swing points on OHLCV series
- **WHEN** `detect_swing_points(df, window=4)` executes on an 80-bar OHLCV DataFrame
- **THEN** at least one `SwingPoint` is returned
- **AND** every `SwingPoint` has `point_type` in `{"HIGH", "LOW"}` and strictly positive `price`

### Requirement: Supply and Demand Zone Construction and S/R Flip Detection
The supply-demand engine (`calculate_supply_demand_zones`) SHALL transform detected swing points into bounded rectangular zones (`SupplyDemandZone`) and flag Support/Resistance flips (`is_sr_flip`) when subsequent candles break past the zone boundary.

#### Scenario: Construct valid demand and supply bounds
- **WHEN** `calculate_supply_demand_zones(df, swing_window=4)` builds zones from swing points
- **THEN** every `SupplyDemandZone` satisfies `upper_bound >= lower_bound`
- **AND** `zone_type` is either `"DEMAND"` or `"SUPPLY"`
- **AND** if a zero-thickness candle body produces `upper <= lower`, an ATR fallback offset (`0.3 * atr_14`) guarantees positive zone thickness

#### Scenario: Flag Support/Resistance Flip (S/R Flip)
- **WHEN** a `DEMAND` zone experiences any subsequent bar with `low < lower_bound`, or a `SUPPLY` zone experiences any subsequent bar with `high > upper_bound`
- **THEN** `zone.is_sr_flip` is set to `True`
