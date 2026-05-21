# Next Steps

## Immediate UI Development
1. Implementare la schermata di creazione del nuovo studio.
   - Aprire una modale quando si clicca `Nuovo studio`.
   - Inserire famiglia, sequenza e descrizione.
   - Non salvare ancora in Excel: mantenere il comportamento come simulazione locale.
2. Implementare la logica di selezione studio a sinistra.
   - Evidenziare la sequenza cliccata nella sidebar.
   - Mostrare un riepilogo dello studio selezionato.
3. Abilitare `Aggiungi codice grp.` solo quando uno studio è selezionato.
   - Se non c'è selezione, impedire l’apertura della modale e mostrare un messaggio.
   - Se c’è selezione, aprire una seconda modale per aggiungere un gruppo.
4. Mantenere il backend invariato per ora.
   - Nessuna scrittura su `Gestione_Studi_DB_20251010.xlsx`.
   - La fase successiva sarà collegare le nuove schermate ai nuovi endpoint.

## Implementation Plan
1. Aggiornare `templates/index.html`.
   - aggiungere `Nuovo studio` e `Aggiungi codice grp.` con ID e abilitazione condizionale.
   - aggiungere area di stato studio selezionato.
   - aggiungere due modali HTML per la creazione dello studio e l’aggiunta del gruppo.
2. Aggiornare `static/js/app.js`.
   - gestire lo stato `selectedStudy`.
   - rendere selezionabile la sequenza cliccata e mantenere l’evidenziazione.
   - aprire/chiudere le modali e simulare la creazione.
3. Aggiornare `static/css/style.css`.
   - aggiungere stili per la selezione attiva, il banner informativo e le modali.
4. Verificare l’interfaccia.
   - testare l’apertura e chiusura dei modali.
   - verificare che `Aggiungi codice grp.` sia disabilitato finché non si seleziona uno studio.
   - verificare che il riepilogo dello studio selezionato venga mostrato.

## Follow-up Work
- creare gli endpoint backend per salvare nei fogli Excel.
- collegare le modali ai nuovi endpoint API.
- aggiungere validazione lato server e messaggi di errore.
- testare il salvataggio reale in `Gestione_Studi_DB_20251010.xlsx`.

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