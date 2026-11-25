# Design: IEEE Conference Paper Structure & Traceability Mapping

## Document Class and Overleaf Compatibility
- Uses `\documentclass[conference]{IEEEtran}` with standard CTAN packages (`cite`, `amsmath`, `amssymb`, `amsfonts`, `algorithm`, `algorithmic`, `graphicx`, `booktabs`, `tikz`, `url`, `xcolor`, `textcomp`).
- Deliberately avoids `geometry` or custom margin overrides to preserve strict IEEE two-column compliance.
- Renders the system architecture diagram in native vector TikZ inside `main.tex` so Overleaf compiles cleanly with zero external binary dependencies.

## Source-to-Manuscript Traceability
| Paper Section | Ground-Truth Repository Source |
| :--- | :--- |
| Abstract & Motivation | `ABSTRACT_300WORDS.md`, `docs/literature_review.md` |
| 4-Layer 8-Module Architecture | `DESIGN.md`, `src/layer1_data/` – `src/layer4_risk_output/` |
| Swing & S/D Equations | `src/layer2_core_engine/swing_detector.py`, `supply_demand.py` |
| 5-Dim ML Feature Vector | `src/layer2_core_engine/xgb_predictor.py` |
| CoT Prompt & Price Action Rules | `src/layer3_reasoning/price_action_kb.py`, `cot_planner.py` |
| Risk Gates & Circuit Breakers | `src/layer4_risk_output/risk_manager.py`, `report_generator.py` |
| Verification & Deterministic Cases | `run_tests.py`, `tests/test_geometry.py`, `tests/test_risk_manager.py` |
| Walk-Forward Evaluation Protocol | `DESIGN.md` Section 4, `INFOGRAPHIC_A4.md` Section 05 |

## Scientific Integrity Rule
- No synthetic or fabricated backtest Sharpe ratios, win rates, or equity curves are reported as empirical results; unexecuted multi-asset walk-forward experiments are explicitly presented as the evaluation protocol and future work.
