# Raccoglitore (Flask + Excel)

Questo progetto fornisce una semplice interfaccia Flask che legge i dati da un file Excel (`Gestione_Studi_DB_20251010.xlsx`) e mostra una sidebar con le famiglie (foglio 1) e sequenze (foglio 2).

Setup rapido (Windows PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
python app.py
```

Visita http://127.0.0.1:5000/

Note:
- Al momento non c'è autenticazione.
- Il progetto è diviso in file separati: `app.py`, `data_loader.py`, template, e static.
- Miglioramenti futuri: caching, ricerca, autenticazione, filtri avanzati.

Selenium / Chrome notes
- The ADI integration uses Selenium. If you get an error "cannot find Chrome binary" on Windows, locate your chrome.exe path and set CHROME_PATH before running tests.

Find Chrome path (PowerShell):

```powershell
# common locations
Get-ChildItem 'C:\Program Files\Google\Chrome\Application\chrome.exe' -ErrorAction SilentlyContinue
Get-ChildItem 'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe' -ErrorAction SilentlyContinue
``` 

Then set env var and run test:

```powershell
$env:CHROME_PATH='C:\Program Files\Google\Chrome\Application\chrome.exe'
# then run test
python adi_test_run.py
```

Alternatively, call the helper directly with chrome_path argument in a small script.

Using Microsoft Edge
--------------------
If you prefer Edge, set the `EDGE_PATH` environment variable to your msedge.exe path and set `BROWSER=edge` for the test run. Example (PowerShell):

```powershell
$env:EDGE_PATH='C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
$env:BROWSER='edge'
python adi_test_run.py
```

The fetcher will use EdgeChromiumDriverManager to install the Edge driver automatically.
