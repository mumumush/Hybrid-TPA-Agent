# Paper Draft Delta Specification

## ADDED Requirements

### Requirement: IEEE Conference LaTeX Manuscript
The repository SHALL provide an Overleaf-ready IEEE conference manuscript at `paper/main.tex` using `\documentclass[conference]{IEEEtran}` and a companion BibTeX database at `paper/references.bib`.

#### Scenario: Manuscript compiles cleanly in Overleaf without missing assets
- **WHEN** a user imports `paper/` into Overleaf (via GitHub sync, ZIP upload, or Overleaf MCP) and compiles `main.tex` with `pdfLaTeX` + `BibTeX`
- **THEN** all sections, IEEE author blocks, equations, TikZ architecture diagram, risk-gate algorithm, tables, and references render without external missing-file dependencies

### Requirement: Empirical Honesty and Code Traceability
Every mathematical formula, risk threshold, circuit breaker rule, and test result cited in `paper/main.tex` SHALL match the verified source implementation in `src/` and `run_tests.py`.

#### Scenario: Distinguish implemented verification from planned walk-forward backtest
- **WHEN** `paper/main.tex` reports system verification
- **THEN** Section V reports the verified `5/5` deterministic tests from `run_tests.py` and exact `RiskManager` veto gates
- **AND** Section VI clearly labels the multi-asset 6-baseline walk-forward benchmark as the evaluation protocol rather than fabricated empirical results
