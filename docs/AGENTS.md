# AI Agent Instructions for this repository

This repository is a Python/Flask-based document management and automation tool for technical studies and drawings.

## Key facts

- Primary runtime language: **Python 3.8+**
- Platform: **Windows-first** (paths, browser automation, filesystem layout)
- Main web app entrypoint: `app.py`
- Data source: Excel workbook configured in `config.py`
- PDF lookup and storage: environment variable `DRAWINGS_DIR` or default `H:\96-GESTIONE_STUDI\DISEGNI`
- Frontend is vanilla JavaScript + Flask templates under `static/` and `templates/`

## How to run

- Install dependencies from `requirements.txt`
- Start the web app with:
  ```bash
  python app.py
  ```

## Important repository conventions

- The project is a flat script-based Python workspace, not a packaged library.
- `app.py` creates the Flask app and registers the `main_bp` blueprint from `routes.py`.
- `routes.py` contains the majority of API endpoints and web route logic.
- Core backend modules include:
  - `config.py` for file paths and constants
  - `data_loader.py` for Excel data access and caching
  - `helpers.py` for HTTP and filesystem helpers
  - `cache_manager.py` for cached groups/machines data
  - `pdf_finder.py` for local PDF discovery
- Excel data is loaded at startup and served from memory caches.
- PDF lookup is intentionally narrow and should continue using the existing code path unless the task explicitly requires changing it.
- There is no dedicated test suite or CI configuration in this repository.

## What AI agents should do first

- Preserve the current data-loading, PDF lookup, and route behavior unless the task explicitly requires a redesign.
- Use `requirements.txt` as the dependency source.
- Prefer small, incremental changes over large refactors.
- Keep Windows path assumptions and browser automation patterns in mind.

## Helpful entrypoints for code changes

- `app.py` — Flask application factory and server startup
- `routes.py` — API endpoints, PDF serving, proxy, and credential handling
- `data_loader.py` — Excel parsing and data shaping
- `helpers.py` — request parsing, file sanitization, and HTTP helpers
- `cache_manager.py` — groups/machines caching logic
- `pdf_finder.py` — local PDF discovery
- `runner.py` / `macro_1.py` / `adi_fetcher.py` — automation and download workflows
- `templates/index.html` — main UI template
- `static/js/app.js` and `static/js/sidebar-manager.js` — frontend interactions and sidebar logic

## Useful notes for agents

- Do not assume a package structure; this is a script-first repository.
- `routes.py` is the canonical source of current API behavior.
- The README and `docs/ARCHITECTURE.md` are the main project documentation sources.
- For validation, prefer running `python app.py` and checking route behavior rather than relying on missing tests.
