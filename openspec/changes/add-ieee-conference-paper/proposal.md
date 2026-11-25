# Proposal: Add IEEE Conference Paper Overleaf Draft (`paper/`)

## Why
The Hybrid TPA-Agent project currently documents its architecture in Markdown (`README.md`, `DESIGN.md`, `INFOGRAPHIC_A4.md`, `docs/literature_review.md`) and implements the 4-layer prototype in `src/`. To submit and present the work in an academic conference setting (DIC4 milestone), the project requires a publication-grade IEEE Conference LaTeX manuscript (`IEEEtran`) hosted on GitHub and directly importable into Overleaf (or synced via an Overleaf MCP server).

## What Changes
- Create `paper/main.tex` using `\documentclass[conference]{IEEEtran}` covering:
  - Abstract and IEEE Keywords
  - Introduction & Empirical Motivation (Chaguê et al. 2019, FINRA Rule 2270 & Notice 24-13)
  - Related Work (LLM Financial Hallucination arXiv:2605.19337, FINSABER ACM 2026, XGBoost, CoT, ATR)
  - Decoupled 4-Layer 8-Module Architecture with a native TikZ block diagram
  - Mathematical Formulation & Veto Risk Governance Algorithm
  - Implementation, OpenSpec SDD Verification, and Deterministic Unit/Integration Audit
  - Anti-Leakage Walk-Forward Experimental Protocol & 6 Baselines
  - Limitations, Future Work, and Conclusion
- Create `paper/references.bib` with verified academic and regulatory BibTeX citations.
- Create `paper/README.md` with Overleaf import, Overleaf MCP integration, and local `pdflatex` compilation instructions.
- Update root `README.md` to link directly to `paper/` and `openspec/`.

## Impact
- **Non-breaking**: Adds `paper/` and `openspec/` without modifying `src/` runtime behavior.
- **Verifiable**: Existing tests (`python run_tests.py`) remain 5/5 passing, and every formula/threshold cited in `paper/main.tex` matches `src/` line-for-line.
