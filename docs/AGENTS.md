# AI Agent Instructions for this repository

This repository is a Python/Flask-based tool for managing technical studies and drawings, with additional automation scripts for downloading and organizing documents.

## Key facts

- Primary runtime language: **Python 3.8+**
- Platform: **Windows-first** (paths, browser automation, filesystem layout)
- Main web app entrypoint: `app.py`
- Data source: Excel workbook `Gestione_Studi_DB_20251010.xlsx`
- PDF lookup and storage: environment variable `DRAWINGS_DIR` or default `H:\96-GESTIONE_STUDI\DISEGNI`
- Frontend is vanilla JavaScript + Flask templates under `static/` and `templates/`

## How to run

- Install dependencies from `requirements.txt`
- Start the web app with:
  ```bash
  python app.py
  ```
- Automation/orchestration scripts include:
  - `runner.py`
  - `macro.py`
  - `macro_1.py`
  - `adi_fetcher.py`

## Important repository conventions

- The app is not built around a database; it loads data from Excel and the filesystem.
- `data_loader.py` is the core data access layer for Excel-based families, sequences, and group/machine data.
- `app.py` exposes both UI API endpoints and helper endpoints for PDF proxying, local PDF lookup, and cURL replay.
- PDF lookup is intentionally narrow: it uses `DRAWINGS_DIR` and a folder structure based on code prefixes.
- `static/js/app.js` and `static/js/sidebar-manager.js` drive the client-side behavior.
- The repository currently has no dedicated test suite or CI files.

## What AI agents should do first

- Preserve the current data-loading and PDF lookup behavior unless the task explicitly requires changing it.
- Use `requirements.txt` for dependency reference.
- Prefer small, local changes over large refactors unless asked, because the codebase is a working automation tool.
- When adding new functionality, keep Windows path assumptions and browser automation in mind.

## Helpful entrypoints for code changes

- `app.py` — main HTTP server, API endpoints, proxy helpers
- `data_loader.py` — Excel parsing and data shaping
- `runner.py` / `macro.py` — automation workflow and orchestration
- `create_drawings_structure.py` / `create_drawings_structure_fixed.py` — folder structure creation logic
- `templates/index.html` — main UI template

## Useful notes for agents

- Do not assume a package structure; the repository is a flat script-based project.
- The README contains project context; use it for feature and UX understanding rather than duplicating it.
- The `static/` assets are minimal and should be updated carefully if UI behavior needs to change.
