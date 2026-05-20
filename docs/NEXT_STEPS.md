# Next Steps

## Prioritized Next Actions
1. **Complete Documentation Updates**: Finish updating NEXT_STEPS.md and create ARCHITECTURE.md
2. **Fix Virtual Environment**: Resolve venv activation failure (exit code 1) - recreate if corrupted
3. **Verify App Execution**: Start Flask server and test core API endpoints (/api/families, /api/sequences, /api/fetch_pdf_local)
4. **Test PDF Features**: Validate local PDF lookup, proxy endpoints, and embedded viewer
5. **Check Automation Scripts**: Test runner.py orchestration and macro_1.py individual execution
6. **Validate Frontend**: Ensure search, filtering, and responsive UI work correctly

## Suggested Implementation Order
1. **Documentation Completion**
   - Finalize NEXT_STEPS.md with accurate priorities
   - Create ARCHITECTURE.md with system architecture details
   - Ensure all docs are consistent and based on actual code

2. **Environment Setup**
   - Recreate virtual environment if activation fails
   - Install dependencies from requirements.txt
   - Test basic Python execution and imports

3. **Core Functionality Testing**
   - Start Flask server (python app.py)
   - Test Excel data loading and API responses
   - Verify PDF serving from local filesystem
   - Test proxy endpoints with sample URLs

4. **Frontend Validation**
   - Load web interface and test navigation
   - Verify search and filtering functionality
   - Test PDF embedding and viewer controls
   - Check responsive sidebar behavior

5. **Automation Validation**
   - Test macro_1.py with sample codes (requires ADI access)
   - Run runner.py with small test dataset
   - Verify progress saving and interruption handling
   - Test Selenium-based ADI fetching

6. **Integration Testing**
   - End-to-end test: Excel data → Web UI → PDF display
   - Test folder creation functionality
   - Validate cURL replay and proxy features

## Refactors to Consider
- **Modular Architecture**: Split large files (app.py has many endpoints) into separate modules
- **Error Handling**: Add comprehensive exception handling and user-friendly error messages
- **Configuration Management**: Move hardcoded paths and settings to config files
- **Logging**: Implement structured logging instead of print statements
- **Testing Framework**: Add pytest for unit tests of data_loader.py and API endpoints
- **Security**: Add input validation, rate limiting, and secure credential handling

## Immediate Work (refactor tracking)

- STEP 3: Estrarre PDF lookup logic — COMPLETATO
   - Obiettivo: spostare la logica di ricerca dei PDF in un modulo dedicato (`pdf_finder.py`) e ridurre la complessità di `app.py`.
   - Azioni già effettuate: `pdf_finder.py` creato; `app.py` aggiornato per usare `find_pdf_path()`.
   - Verifiche richieste: test endpoint `/api/fetch_pdf_local` e comportamento della ricerca file.

- STEP 4: Refactor caching — COMPLETATO
   - Obiettivo: rimuovere lo stato globale `_groups_machines_cache` e introdurre un piccolo `CacheManager` per incapsulare il caching.
   - Azioni già effettuate: `cache_manager.py` creato; `routes.py` usa ora `GroupsMachinesCache`.

- STEP 5: Modularizzare `app.py` — COMPLETATO
   - Obiettivo: suddividere `app.py` in moduli separati (`config.py`, `helpers.py`, `cache_manager.py`, `routes.py`).
   - Azioni già effettuate: `app.py` ora è un entrypoint minimale che registra `main_bp`.

Prima di procedere oltre, queste note sono state salvate: il refactor è completato e l'app è stata ricompilata con successo nel venv.

## Missing Features
- **User Authentication**: Login system for web app access control
- **Role-Based Access**: Different permissions for viewing vs. downloading
- **Audit Logging**: Track PDF access and download activities
- **Search Optimization**: Improve frontend search performance for large datasets
- **PDF Upload**: Allow manual PDF uploads to local storage
- **API Documentation**: OpenAPI/Swagger specs for REST endpoints
- **Batch Operations**: Bulk folder creation and PDF operations
- **Progress Monitoring**: Real-time progress for long-running automation tasks

## Technical Debt
- **Browser Dependencies**: Fragile automation relying on specific browser versions and UI elements
- **Hardcoded Paths**: Windows-specific absolute paths throughout codebase
- **Memory Management**: Large Excel files loaded entirely into memory without limits
- **Threading Safety**: Potential race conditions in automation scripts and global state
- **Input Validation**: Missing validation on API endpoints and user inputs
- **Error Recovery**: Limited error handling in automation scripts

## Testing Tasks
- **Unit Tests**: Test DataLoader class methods and data transformations
- **API Tests**: Test Flask endpoints with mock data and error conditions
- **Integration Tests**: Test Excel loading, web UI, and PDF serving together
- **UI Tests**: Selenium tests for web interface interactions
- **Automation Tests**: Mock browser tests for download scripts
- **Performance Tests**: Load testing with large Excel files and concurrent users
- **Security Tests**: Test input validation and credential handling