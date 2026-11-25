# Veto-Enabled Risk Governance & Audit Output Specification

## Purpose
Defines Layer 4 (`src/layer4_risk_output/risk_manager.py` and `report_generator.py`) mandatory mathematical veto gates, circuit breakers, and Human-in-the-Loop (HITL) audit card generation.

## Requirements

### Requirement: Circuit Breaker Protection (Level 2 & Level 3)
`RiskManager.evaluate_trade` SHALL hold absolute veto authority (`NO_TRADE`) when operational safety or consecutive loss limits are breached.

#### Scenario: Level 3 API latency circuit breaker
- **WHEN** `latency_seconds > 5.0`
- **THEN** `evaluate_trade` immediately returns `status = "NO_TRADE"` with `circuit_breaker_active = True` and `position_size = 0.0`

#### Scenario: Level 2 consecutive loss circuit breaker
- **WHEN** `consecutive_losses >= 2`
- **THEN** `evaluate_trade` immediately returns `status = "NO_TRADE"` with `circuit_breaker_active = True` and `position_size = 0.0`

### Requirement: Mandatory Risk-Reward, Positive Expectation, and ATR Stop-Loss Gates
For any non-halted trade candidate, `RiskManager.evaluate_trade` SHALL compute a `1.0 * ATR` structural stop-loss buffer, verify `risk_reward_ratio >= min_rr_threshold` (default `2.0`), verify positive mathematical expectation `E = W * RR - (1 - W) > 0`, and size positions strictly by the user's risk budget.

#### Scenario: Veto trade with insufficient risk-reward ratio
- **WHEN** `RR < profile.min_rr_threshold` (e.g., `target_price = 102.0` vs. `entry = 100.0`, `stop_loss = 93.0`)
- **THEN** `evaluate_trade` returns `status = "NO_TRADE"` with `position_size = 0.0`

#### Scenario: Veto trade with non-positive mathematical expectation
- **WHEN** `E = W * RR - (1 - W) <= 0`
- **THEN** `evaluate_trade` returns `status = "NO_TRADE"` with `position_size = 0.0`

#### Scenario: Approve valid positive-expectation trade
- **WHEN** `RR >= profile.min_rr_threshold`, `E > 0`, and no circuit breaker is active
- **THEN** `evaluate_trade` returns `status = "APPROVED"` with `position_size = get_max_loss_budget() / risk_per_unit`

### Requirement: Human-in-the-Loop Audit Card Generation
`ReportGenerator.generate_audit_card` SHALL assemble risk metrics, 4-step CoT evidence, and risk governance status with `human_confirmation_required = True`.

#### Scenario: Produce structured audit card
- **WHEN** `ReportGenerator.generate_audit_card(symbol, risk_decision, cot_data, ml_meta)` is called
- **THEN** the returned dictionary includes `title`, `decision_status`, `metrics`, `reasoning_evidence`, and `risk_governance` with `human_confirmation_required` set to `True`
