# Architecture

## System Architecture Overview

Raccoglitore is a web-based document management system built with a traditional three-tier architecture: presentation layer (frontend), application layer (Flask backend), and data/storage layer (Excel + filesystem). The system integrates automation capabilities for bulk document retrieval from external systems.

## Quick architectural summary
- The app is still a lightweight Flask application with Excel-backed metadata and local PDF storage.
- The storage rule is driven by the workbook family codes and should remain stable.
- The docs directory is part of the runtime context and should be read before making changes.

## Core Components

### Backend Architecture (Flask Application)

#### Main Application (app.py)
- Framework: Flask 2.x web framework
- Endpoints:
  - /: Serves the main web interface
  - /api/families: Returns family hierarchy data
  - /api/sequences: Returns sequences for a family
  - /api/groups_machines: Returns groups/machines for family/sequence
  - /api/all_*: Cached bulk data endpoints for frontend performance
  - /api/fetch_pdf_local: Local PDF lookup and serving
  - /api/proxy_pdf: External PDF proxying with authentication
  - /api/run_quick_proxy: Quick test proxy using config file
  - /api/init_drawings: Folder structure creation
  - /api/replay_curl: cURL command parsing and execution
  - /api/credentials: Credential storage management
- Configuration: Environment variables (DRAWINGS_DIR), config files (quick_test.json)
- Server: Runs on 0.0.0.0:8000 for network access

#### Data Access Layer (data_loader.py)
- Class: DataLoader with lazy loading and caching
- Data Sources: Excel files (Gestione_Studi_DB_20251010.xlsx)
- Sheets Processed:
  - Sheet 0: Families (family_code, family_name)
  - Sheet 1: Sequences (sequence_id, family_code, description)
  - Sheet 2: Groups/Machines (id, cod, pro, tipo, articolo, desart)
- Caching Strategy: In-memory caching with global variables
- Column Detection: Heuristic-based column name matching

### Frontend Architecture (Vanilla JavaScript)

#### Core Application (static/js/app.js)
- Responsibilities: API communication, UI state management, search/filtering
- Key Features:
  - Dynamic sidebar population with family/sequence hierarchy
  - Real-time search with debouncing (300ms delay)
  - PDF embedding and viewer management
  - Groups/machines detail display
  - Error handling and user feedback

#### UI Management (static/js/sidebar-manager.js)
- Class: SidebarManager for responsive behavior
- Features:
  - Desktop: Resizable sidebar (180-800px width)
  - Mobile: Overlay sidebar with fixed width
  - Drag-resize functionality with mouse events
  - Window resize handling and layout recalculation

#### Templates (templates/index.html)
- Structure: Single-page application with sidebar and main content
- Components:
  - Responsive sidebar with search input
  - PDF preview container with toolbar
  - Credentials modal for ADI authentication
  - Top bar with informational notices

### Automation Architecture

#### Orchestration Layer (runner.py)
- Purpose: Bulk processing of PDF downloads
- Features:
  - Excel-based code list processing (elenco_codici_studi.xlsx)
  - Progress tracking with state file (.runner_state.json)
  - Keyboard interruption handling (Ctrl key)
  - Subprocess management for individual downloads

#### Individual Automation (macro_1.py)
- Technology: PyAutoGUI image-based UI automation
- Process:
  - Input code via stdin
  - Image recognition for UI elements
  - Browser interaction simulation
  - Download monitoring and completion detection

#### Advanced Automation (adi_fetcher.py)
- Technology: Selenium WebDriver
- Capabilities:
  - Browser automation with multiple driver support
  - ADI system login and navigation
  - PDF download via authenticated sessions
  - Cookie management and session handling

### Storage Architecture

#### Data Storage
- Primary: Excel workbooks for metadata
- Format: XLSX with multiple sheets
- Access Pattern: Read-only with periodic updates
- Caching: In-memory for performance

#### Document Storage
- Location: DRAWINGS_DIR environment variable (default: H:\96-GESTIONE_STUDI\DISEGNI)
- Structure: <family>/<study_code>/<study_code>.pdf hierarchy
- Family Logic: Taken from the Excel workbook family code (for example GS-U or TUNI)
- Access: Direct filesystem reads with a fallback search for older legacy folders

#### Configuration Storage
- Files:
  - quick_test.json: Test URLs and cookies
  - stored_credentials.json: ADI authentication
  - .runner_state.json: Automation progress
- Format: JSON with local encryption for credentials

## Context handoff for future chats

The docs directory is part of the runtime context for this repository. New chats should start from the documents in this folder before making changes, because the codebase is script-first and there is no database to rehydrate the current state.

## Data Flow

### Web Interface Flow
1. Startup: Flask loads Excel data into DataLoader cache
2. Page Load: Frontend fetches all families and sequences
3. Navigation: User selects family → loads sequences → displays groups/machines
4. PDF View: Code lookup → family-based filesystem search → embed PDF in browser

### Automation Flow
1. Bulk Processing: runner.py reads Excel code list
2. Individual Download: macro_1.py or adi_fetcher.py processes each code
3. UI Automation: Image recognition → browser interaction → download trigger
4. Monitoring: File system watching → progress update → state save
5. Folder Rebuild: create_drawings_structure_fixed.py can regenerate the folder tree from the workbook when needed

### Proxy Flow
1. Request: Frontend sends URL + cookies to proxy endpoint
2. Authentication: Session setup with provided credentials
3. Download: HTTP request with cookie headers
4. Response: Stream PDF content back to client

## Module Structure and Responsibilities

```
raccoglitore/
├── app.py                    # Main Flask app, routing, PDF serving
├── data_loader.py           # Excel data access and caching
├── runner.py                # Bulk automation orchestration
├── macro_1.py               # Single download automation
├── adi_fetcher.py           # Selenium-based ADI integration
├── templates/
│   └── index.html           # Main UI template
├── static/
│   ├── css/style.css        # Dark theme styling
│   └── js/
│       ├── app.js           # Frontend logic and API calls
│       └── sidebar-manager.js # Responsive UI management
├── docs/                    # Documentation and persistent context
└── *.xlsx                  # Data files
```

## Architectural Constraints

### Platform Constraints
- Windows-first: absolute paths, PowerShell integration, browser automation
- Browser Dependencies: Chrome/Edge with specific versions for automation
- Filesystem: NTFS with long path support for DRAWINGS_DIR structure

### Performance Constraints
- Memory-bound: Excel data fully loaded at startup
- Single-threaded: Flask development server, no concurrency
- Network-dependent: external PDF fetching and ADI access

### Security Constraints
- Local-only: no authentication, runs on local network
- Plaintext storage: credentials stored locally unencrypted
- No validation: API endpoints accept arbitrary inputs

## Integration Points

### External Systems
- ADI System: HTTP-based document repository with web interface
- Browser Automation: Chrome/Edge for UI interaction
- Filesystem: Windows NTFS for document storage

### Data Formats
- Excel: primary data source with fixed schema expectations
- JSON: API communication and configuration files
- PDF: document format for viewing and storage

## Architectural Patterns Used

- MVC Pattern: Flask routes (Controller), templates (View), data_loader (Model)
- Repository Pattern: DataLoader abstracts Excel access
- Factory Pattern: Dynamic folder structure creation
- Observer Pattern: Keyboard monitoring in automation
- Proxy Pattern: PDF proxying for external access
- Singleton Pattern: Global data caches

## Deployment Architecture

- Development: local Windows execution with virtual environment
- Runtime: single Flask process serving web interface and APIs
- Storage: local filesystem with network-accessible paths
- Automation: separate processes for bulk operations
- Configuration: environment variables and local config files