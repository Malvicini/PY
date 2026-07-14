# Known Issues

## Known Bugs
- Venv activation failure: virtual environment activation can fail with exit code 1, likely due to corruption or path issues
- PDF lookup edge cases: fallback logic can miss files if the folder structure does not match the expected family-based layout
- Search filtering: frontend search may not handle all data combinations or special characters correctly
- Browser automation fragility: scripts break if ADI UI changes, image recognition fails, or browser versions update
- Excel loading assumptions: app assumes specific sheet/column structure and may fail silently on format changes or missing sheets
- Path handling issues: Windows absolute paths are hardcoded and can fail on different drive letters or network paths
- Memory caching problems: large Excel data is cached in memory without size limits or cleanup
- Threading race conditions: keyboard listener and subprocess calls in runner.py may have race conditions

## Unstable Areas
- Excel parsing: column detection heuristics in data_loader.py are brittle and may fail with different Excel layouts
- Image recognition: PyAutoGUI image matching in macro_1.py depends on exact UI screenshots and screen resolution
- Selenium WebDriver: browser automation in adi_fetcher.py fails with driver mismatches or browser updates
- Global state management: stop_flag and caches shared across threads without proper synchronization
- File system operations: direct path manipulation without validation or error recovery
- HTTP proxying: requests with cookies may fail on network issues or authentication changes

## Temporary Workarounds
- Venv issue: manually activate or recreate the environment using python -m venv .venv
- PDF not found: check the DRAWINGS_DIR structure and verify the family-based path under DRAWINGS_DIR/<family>/<study_code>
- Automation failures: run macro_1.py individually for debugging and update image files if the UI changed
- Browser issues: update Selenium drivers manually and specify driver paths explicitly
- Excel format issues: manually verify column names match expected patterns (cod, pro, descrizione, etc.)
- Path problems: use absolute paths matching the Windows environment and avoid UNC paths

## Edge Cases
- Empty Excel sheets: app may crash or show an empty UI if sheets are missing or empty
- Missing DRAWINGS_DIR: PDF lookup fails without clear error messages if the directory does not exist
- Network timeouts: proxy endpoints may hang on slow connections or unresponsive URLs
- Special characters: file paths with non-ASCII characters may cause encoding issues
- Large datasets: performance degrades with more than 1000 rows in Excel or many concurrent requests
- Browser popups: automation scripts do not handle unexpected dialogs or security warnings
- Multiple PDF matches: fallback search may return the wrong PDF if multiple files exist in the target directory

## Performance Concerns
- Startup time: the entire Excel workbook is loaded into memory at app start, which is slow for large files
- Search speed: frontend filtering runs on every keystroke without debouncing optimization
- PDF serving: no caching exists for frequently accessed PDFs, so each request reads from disk
- Automation pace: fixed delays in scripts may be too slow or too fast for different system performance
- Memory usage: cached data is never cleared and grows with Excel file size
- Concurrent access: no request limiting or queuing exists for multiple simultaneous users

## Risky Code Sections
- Browser automation scripts: fragile to UI changes and image recognition may fail silently
- Subprocess calls: shell execution in runner.py lacks proper sanitization or timeout handling
- File system operations: direct path manipulation in app.py lacks security checks
- Global variables: stop_flag and cache objects are shared across requests
- Excel parsing: relies on column name heuristics and can fail with unexpected data formats
- HTTP requests: proxy endpoints make external requests without rate limiting or validation
- Credential storage: plaintext credentials are stored locally without encryption

## Things That Should NOT be Changed Casually
- Excel column assumptions: data_loader.py column detection logic (cod, pro, descrizione patterns)
- PDF folder structure: DRAWINGS_DIR/<family>/<study_code>/<study_code>.pdf and the family code from the workbook
- API response formats: frontend expects specific JSON structures from Flask endpoints
- Automation sequences: browser interaction steps and image file dependencies in macro scripts
- Environment variables: DRAWINGS_DIR and browser paths used throughout the codebase
- Flask route signatures: API endpoint parameters and return formats expected by frontend
- JavaScript data binding: app.js assumes specific data structures from API responses