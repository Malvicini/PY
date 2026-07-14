# Project Context

## Project Purpose
Raccoglitore is a Python/Flask-based web application for managing technical studies and drawings. It provides:
- Web interface to browse families, sequences, and groups/machines from Excel data
- Integrated PDF viewer for local drawings stored in a structured filesystem
- Automated download scripts for bulk PDF retrieval from ADI systems using UI automation
- Folder structure creation for organized document storage
- Proxy endpoints for fetching PDFs from external URLs with authentication
- cURL replay functionality for testing API calls

## At a glance
- Goal: manage studies and drawings from Excel-backed metadata and local PDF storage.
- Current state: the core Flask routes and folder logic are working and should be preserved.
- Main guardrail: do not invent new folder conventions; follow the workbook and existing reference script.

## Current Architecture
- Backend: Flask web server with REST API endpoints
- Data Layer: Excel-based data loading with in-memory caching (no database)
- Frontend: Vanilla JavaScript + HTML templates with responsive sidebar
- Automation: PyAutoGUI/Selenium scripts for browser automation and UI interaction
- Storage: Local filesystem for PDFs with a family-based folder hierarchy

## Tech Stack
- Runtime: Python 3.8+
- Web Framework: Flask 2.x
- Data Processing: Pandas, OpenPyXL
- UI Automation: PyAutoGUI, PyNput, Selenium WebDriver
- HTTP Client: Requests library
- Frontend: Vanilla JavaScript ES6+, HTML5, CSS3
- Platform: Windows-first (absolute paths, browser automation)

## Implemented Modules/Features
- app.py: Main Flask application with API endpoints for data access, PDF serving, proxying, folder creation, and cURL replay
- data_loader.py: Excel data access layer with lazy loading and caching for families, sequences, and groups/machines
- runner.py: Orchestration script for bulk PDF downloads using macro_1.py with progress tracking and keyboard interruption
- macro_1.py: Individual automation script for single PDF download via image-based UI automation
- adi_fetcher.py: Selenium-based integration for ADI system PDF fetching with browser automation
- Web UI: Responsive sidebar navigation, real-time search/filtering, embedded PDF viewer, credentials modal
- PDF Lookup: Local filesystem search using the family-based layout DRAWINGS_DIR/<family>/<study_code>/<study_code>.pdf, with fallback support for older legacy paths
- Proxy Features: Arbitrary PDF URL proxying with cookie support, quick test endpoint, cURL command replay
- Folder Management: Automated directory structure creation from Excel data, using the workbook family codes as the source of truth
- Credentials Storage: Secure local storage for ADI authentication

## Important Workflows
1. Data Loading: Excel workbook loaded at startup with lazy caching for performance
2. Web Browsing: Hierarchical navigation (Families → Sequences → Groups/Machines) with search
3. PDF Viewing: Local lookup in DRAWINGS_DIR with structured path resolution
4. Automation: Excel list processing, PyAutoGUI image recognition for UI interaction, progress saving
5. Proxy Operations: URL-based PDF fetching with session cookies, cURL command parsing and replay
6. Folder Creation: Dynamic directory structure generation from family/sequence data

## Database/Services Overview
- No Database: Data stored in Excel files (Gestione_Studi_DB_20251010.xlsx, elenco_codici_studi.xlsx)
- External Services: ADI system for PDF downloads via Selenium automation and HTTP proxying
- File Storage: Local DRAWINGS_DIR (default: H:\96-GESTIONE_STUDI\DISEGNI) with family-based organization
- Configuration: quick_test.json for test URLs/cookies, stored_credentials.json for ADI auth
- State Management: .runner_state.json for automation progress tracking

## Current Project Status
- State: Working production tool for internal Windows-based document management
- Testing: Basic endpoint testing exists, no formal test suite or CI/CD
- Documentation: README.md and docs/ are available and should be treated as the first source of context for new chats
- Deployment: Local Windows execution with virtual environment
- Maintenance: Active development with recent documentation improvements

## Source of truth for important decisions
- Workbook: Gestione_Studi_DB_20251010.xlsx is the authoritative source for family and study metadata.
- Reference script: create_drawings_structure_fixed.py is the reference implementation for rebuilding the drawings tree.
- Handoff context: docs/ is the persistent memory layer for future chats and should be read before any change.

## Important Constraints and Conventions
- Platform: Optimized for Windows (absolute paths, PowerShell scripts, browser automation)
- Browser: Chrome/Edge automation with driver dependencies and image-based UI recognition
- Paths: DRAWINGS_DIR environment variable for PDF storage, hardcoded defaults
- Data Format: Excel sheets with specific column naming (family_code, sequence_id, cod/pro columns)
- PDF Structure: the canonical layout is DRAWINGS_DIR/<family>/<study_code>/<study_code>.pdf; for example H:\96-GESTIONE_STUDI\DISEGNI\GS-U\GS-U008\GS-U008.pdf
- New study folders: when a study code is created, the folder must be created under the family directory derived from the Excel workbook family code
- Do not create new study folders directly under DRAWINGS_DIR root; that breaks the historical layout and can confuse PDF lookup
- Do not invent prefixes: the family folder must come from the workbook data, not from guessed patterns
- Automation: UI-based browser automation (fragile to ADI interface changes)
- Security: Local credential storage, no user authentication in web app

## Brief Explanation of Main Folders
- static/: CSS styles (dark theme), JavaScript frontend code (app.js, sidebar-manager.js)
- templates/: Flask HTML templates (index.html with responsive UI)
- particolari_vecchi/: separate Flask app for searching and downloading particular archives
- downloads/: Temporary storage for automation downloads
- Root scripts: Various automation and utility Python files (macro_1.py, runner.py, adi_fetcher.py)
- Excel files: Data sources (Gestione_Studi_DB_20251010.xlsx for main data, elenco_codici_studi.xlsx for automation lists)