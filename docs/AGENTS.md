# AI Agent Instructions for this repository

This repository is a Python/Flask-based document management and automation tool for technical studies and drawings.

## Quick start for new chats

- Read the docs/ files before changing code or answering questions.
- Preserve the current Flask behavior, Windows-first assumptions, and Excel-driven data flow.
- Treat the workbook and create_drawings_structure_fixed.py as the source of truth for drawings-folder rules.
- Keep changes small and update the documentation when behavior changes.
- Validate with python app.py or a targeted route check when possible.

## Mandatory startup behavior for every new chat

Before answering, proposing changes, or editing files, read these documents first and treat them as the repository memory for the current state:

1. docs/AGENTS.md
2. docs/PROJECT_CONTEXT.md
3. docs/CURRENT_TASK.md
4. docs/NEXT_STEPS.md
5. docs/KNOWN_ISSUES.md
6. docs/ARCHITECTURE.md

Do not assume that previous chat context is enough. If these files are missing or stale, update them before continuing.

## Key facts

- Primary runtime language: Python 3.8+
- Platform: Windows-first (paths, browser automation, filesystem layout)
- Main web app entrypoint: app.py
- Data source: Excel workbook configured in config.py
- PDF lookup and storage: environment variable DRAWINGS_DIR or default H:\96-GESTIONE_STUDI\DISEGNI
- Frontend is vanilla JavaScript + Flask templates under static/ and templates/

## How to run

- Install dependencies from requirements.txt
- Start the web app with:
  python app.py

## Important repository conventions

- The project is a flat script-based Python workspace, not a packaged library.
- app.py creates the Flask app and registers the main_bp blueprint from routes.py.
- routes.py contains the majority of API endpoints and web route logic.
- Core backend modules include:
  - config.py for file paths and constants
  - data_loader.py for Excel data access and caching
  - helpers.py for HTTP and filesystem helpers
  - cache_manager.py for cached groups/machines data
  - pdf_finder.py for local PDF discovery
- Excel data is loaded at startup and served from memory caches.
- Keep the current data-loading, PDF lookup, and route behavior unless the task explicitly requires a redesign.
- The drawings-folder rule is based on the real Excel workbook data: use the family code from the workbook (for example GS-U or TUNI) and create folders as DRAWINGS_DIR/<family>/<study_code>.
- Do not create root-level study folders such as DRAWINGS_DIR/GS or DRAWINGS_DIR/TUNI067; do not invent prefixes that are not present in the workbook.
- The existing bulk script create_drawings_structure_fixed.py is the reference implementation for rebuilding the structure from the workbook.
- There is no dedicated test suite or CI configuration in this repository.

## Non-negotiable rules

- Treat the docs/ folder as the primary handoff memory for this repository.
- When a change affects folder layout, PDF lookup, or Excel assumptions, inspect the workbook and the existing bulk script before implementing a new rule.
- Do not invent new naming conventions or prefixes that are not supported by the workbook data.
- If behavior changes, update the relevant Markdown files before moving on.

## What AI agents should do first

- Preserve the current behavior unless the task explicitly requires a redesign.
- Use requirements.txt as the dependency source.
- Prefer small, incremental changes over large refactors.
- Keep Windows path assumptions and browser automation patterns in mind.
- Keep the Markdown documentation aligned with the codebase whenever behavior changes.

## Helpful entrypoints for code changes

- app.py — Flask application factory and server startup
- routes.py — API endpoints, PDF serving, proxy, and credential handling
- data_loader.py — Excel parsing and data shaping
- helpers.py — request parsing, file sanitization, and HTTP helpers
- cache_manager.py — groups/machines caching logic
- pdf_finder.py — local PDF discovery
- runner.py / macro_1.py / adi_fetcher.py — automation and download workflows
- templates/index.html — main UI template
- static/js/app.js and static/js/sidebar-manager.js — frontend interactions and sidebar logic

## Useful notes for agents

- Do not assume a package structure; this is a script-first repository.
- routes.py is the canonical source of current API behavior.
- The README and docs/ARCHITECTURE.md are the main project documentation sources.
- The canonical drawings layout is DRAWINGS_DIR/<family>/<study_code>/<study_code>.pdf (for example H:\96-GESTIONE_STUDI\DISEGNI\GS-U\GS-U008\GS-U008.pdf or H:\96-GESTIONE_STUDI\DISEGNI\TUNI\TUNI032\TUNI032.pdf).
- The family folder must come from the Excel workbook family code, not from a guessed prefix.
- For legacy entries, PDF lookup may still need to support older folders, but new study folders must always be created under the family directory.
- Do not create new study folders directly under the drawings root; that breaks the historical structure and can confuse the PDF resolver.
- The PDF preview must remain served through the Flask endpoint /api/fetch_pdf_local and rendered in the browser via a direct iframe-based preview flow. Do not revert to fragile fetch-to-blob logic or any timeout-based workaround that replaces the stable route behavior.
- The frontend must continue to request PDFs through /api/fetch_pdf_local with the selected study code and must not introduce alternative preview mechanisms or custom binary handling in the browser.
- For validation, prefer running python app.py and checking route behavior rather than relying on missing tests.
