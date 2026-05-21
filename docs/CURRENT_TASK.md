# Current Task

## What is Currently Being Worked On
Implementare le nuove schermate web per i comandi `Nuovo studio` e `Aggiungi codice grp.`, mantenendo il backend invariato per questa fase.

## Current Objective
Sviluppare l’interfaccia HTTP e i componenti front-end necessari per la creazione simulata dei nuovi studi e l’aggiunta di gruppi, come primo step prima di collegare i form al salvataggio Excel.

## Files/Modules Involved
- `docs/PROJECT_CONTEXT.md`: Updated with actual features from app.py, data_loader.py, frontend code
- `docs/CURRENT_TASK.md`: This file (being updated)
- `docs/NEXT_STEPS.md`: Will be updated with actionable priorities
- `docs/KNOWN_ISSUES.md`: Updated with discovered issues from code review
- `docs/ARCHITECTURE.md`: Created with detailed system architecture
- Core codebase files analyzed: app.py, data_loader.py, runner.py, macro_1.py, adi_fetcher.py, templates/index.html, static/js/app.js, static/js/sidebar-manager.js, requirements.txt, README.md

## Unfinished Work
- Complete updates to NEXT_STEPS.md and ARCHITECTURE.md
- Verify documentation accuracy against running application
- Test venv activation and app startup after documentation completion

## Blockers/Problems
- Virtual environment activation failing (exit code 1) - may require recreation
- ARCHITECTURE.md file was missing and needs to be created

## Important Recent Changes
- Analyzed entire codebase including all API endpoints, automation scripts, and frontend logic
- Updated PROJECT_CONTEXT.md with comprehensive feature list and actual architecture
- Discovered additional implemented features (proxy endpoints, cURL replay, credentials storage, folder creation)
- Identified missing documentation for ARCHITECTURE.md

## What Should be Continued Next
- Complete the remaining documentation updates (NEXT_STEPS.md, ARCHITECTURE.md)
- Test the Flask application startup and core functionality
- Validate PDF lookup and automation features work correctly
- Ensure all documentation files are internally consistent

## Refactor Progress (app.py)

- STEP 1: Pulizia imports — COMPLETATO
	- Consolidati gli import di `flask` e rimossi gli import inutilizzati
	- Rimosso `import re as _re` duplicato
	- Files modificati: `app.py`

- STEP 2: Estrarre logica HTTP — COMPLETATO
	- Aggiunte helper `_build_http_headers()` e `_fetch_url_and_respond()`
	- `proxy_pdf()` e `run_quick_proxy()` refattorizzati per usare gli helper
	- Files modificati: `app.py`

- STEP 3: Estrarre PDF lookup logic — COMPLETATO
	- Logica di ricerca PDF spostata in `pdf_finder.py` (creata)
	- `fetch_pdf_local()` refattorizzato per usare `find_pdf_path()`
	- Stato: `pdf_finder.py` creato, `app.py` aggiornato

- STEP 4: Refactor caching — COMPLETATO
	- Cache globale `_groups_machines_cache` estratta in `cache_manager.py`
	- `routes.py` ora utilizza `GroupsMachinesCache` per i dati `all_groups_machines`
	- `app.py` è stato ridotto a un entrypoint minimale che registra il blueprint

Note: tutte le modifiche finora sono state effettuate per minimizzare i cambiamenti runtime; gli endpoint principali risultano registrati e testati localmente.