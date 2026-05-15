# Known Issues

## Known Bugs
- **Venv Activation Failure**: Virtual environment activation fails with exit code 1, likely due to corruption or path issues
- **PDF Lookup Edge Cases**: Fallback logic in fetch_pdf_local may not find PDFs if folder structure doesn't exactly match expected prefix/code/code.pdf format
- **Search Filtering**: Frontend search may not handle all data combinations or special characters correctly
- **Browser Automation Fragility**: Scripts break if ADI UI changes, image recognition fails, or browser versions update
- **Excel Loading Assumptions**: App assumes specific sheet/column structure; fails silently on format changes or missing sheets
- **Path Handling Issues**: Windows absolute paths hardcoded; fails on different drive letters or network paths
- **Memory Caching Problems**: Large Excel data cached in memory without size limits or cleanup
- **Threading Race Conditions**: Keyboard listener and subprocess calls in runner.py may have race conditions

## Unstable Areas
- **Excel Parsing**: Column detection heuristics in data_loader.py are brittle and may fail with different Excel layouts
- **Image Recognition**: PyAutoGUI image matching in macro_1.py depends on exact UI screenshots and screen resolution
- **Selenium WebDriver**: Browser automation in adi_fetcher.py fails with driver mismatches or browser updates
- **Global State Management**: stop_flag and caches shared across threads without proper synchronization
- **File System Operations**: Direct path manipulation without validation or error recovery
- **HTTP Proxying**: Requests with cookies may fail on network issues or authentication changes

## Temporary Workarounds
- **Venv Issue**: Manually activate or recreate environment using `python -m venv .venv`
- **PDF Not Found**: Check DRAWINGS_DIR structure manually and verify prefix extraction logic
- **Automation Failures**: Run macro_1.py individually for debugging, update image files if UI changed
- **Browser Issues**: Update Selenium drivers manually, specify driver paths explicitly
- **Excel Format Issues**: Manually verify column names match expected patterns (cod, pro, descrizione, etc.)
- **Path Problems**: Use absolute paths matching the Windows environment, avoid UNC paths

## Edge Cases
- **Empty Excel Sheets**: App may crash or show empty UI if sheets are missing or empty
- **Missing DRAWINGS_DIR**: PDF lookup fails without clear error messages if directory doesn't exist
- **Network Timeouts**: Proxy endpoints may hang on slow connections or unresponsive URLs
- **Special Characters**: File paths with non-ASCII characters may cause encoding issues
- **Large Datasets**: Performance degrades with >1000 rows in Excel or many concurrent requests
- **Browser Popups**: Automation scripts don't handle unexpected dialogs or security warnings
- **Multiple PDF Matches**: Fallback search may return wrong PDF if multiple files exist in target directory

## Performance Concerns
- **Startup Time**: Entire Excel workbook loaded into memory at app start, slow for large files
- **Search Speed**: Frontend filtering runs on every keystroke without debouncing optimization
- **PDF Serving**: No caching for frequently accessed PDFs, each request reads from disk
- **Automation Pace**: Fixed delays in scripts may be too slow/fast for different system performance
- **Memory Usage**: Cached data never cleared, grows with Excel file size
- **Concurrent Access**: No request limiting or queuing for multiple simultaneous users

## Risky Code Sections
- **Browser Automation Scripts**: Fragile to UI changes; image recognition may fail silently
- **Subprocess Calls**: Shell execution in runner.py without proper sanitization or timeout handling
- **File System Operations**: Direct path manipulation in app.py without security checks
- **Global Variables**: stop_flag and _groups_machines_cache shared across requests
- **Excel Parsing**: Relies on column name heuristics; fails with unexpected data formats
- **HTTP Requests**: Proxy endpoints make external requests without rate limiting or validation
- **Credential Storage**: Plaintext credentials stored locally without encryption

## Things That Should NOT be Changed Casually
- **Excel Column Assumptions**: data_loader.py column detection logic (cod, pro, descrizione patterns)
- **PDF Folder Structure**: DRAWINGS_DIR/prefix/code/code.pdf hierarchy and prefix extraction
- **API Response Formats**: Frontend expects specific JSON structures from Flask endpoints
- **Automation Sequences**: Browser interaction steps and image file dependencies in macro scripts
- **Environment Variables**: DRAWINGS_DIR and browser paths used throughout codebase
- **Flask Route Signatures**: API endpoint parameters and return formats expected by frontend
- **JavaScript Data Binding**: app.js assumes specific data structures from API responses