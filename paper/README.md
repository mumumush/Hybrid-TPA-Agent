# IEEE Conference Paper Draft (`paper/`)

This directory contains the Overleaf-ready IEEE Conference manuscript (`\documentclass[conference]{IEEEtran}`) for **Hybrid TPA-Agent**, aligned with the repository's `openspec/` specifications and `src/` implementation.

## Files
- `main.tex`: Complete IEEE two-column conference manuscript (includes native TikZ architecture figure and Layer 4 Veto Risk Gate algorithm).
- `references.bib`: Verified BibTeX bibliography covering empirical day-trading studies, FINRA Rule 2270 / Notice 24-13, LLM financial agent literature, XGBoost, CoT, and ATR.

## Using with Overleaf
1. **Upload Project via `.zip` (Works on Overleaf Free):**
   - Zip `main.tex` and `references.bib` together, then in Overleaf click **New Project -> Upload Project** and drop the `.zip`.
   - Set **Compiler** to `pdfLaTeX` and **Main document** to `main.tex`.
2. **Import via GitHub (Overleaf GitHub Integration):**
   - In Overleaf, click **New Project -> Import from GitHub** and select `mumumush/Hybrid-TPA-Agent` (Main document: `paper/main.tex`).
3. **Using with an Overleaf MCP Server (e.g., `mjyoo2/overleaf-mcp` or `@netique/overleaf-mcp`):**
   - Configure your Overleaf project credentials / Git remote in your MCP client and point it to `paper/main.tex` and `paper/references.bib` for section-level editing and citation checks.

## Local Compilation (Optional)
If TeX Live / MiKTeX is installed locally:
```bash
cd paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```
