# 🎯 Raccoglitore - Sistema di Gestione Studi e Disegni

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Un sistema completo per la gestione, visualizzazione e automazione del download di studi tecnici e disegni industriali.

## 📋 Descrizione

### Scopo dell'applicazione
Raccoglitore è una soluzione integrata che combina:
- **Interfaccia web** per esplorare famiglie e sequenze di studi tecnici
- **Visualizzatore PDF integrato** per anteprime immediate
- **Automazione intelligente** per il download massivo di documenti da sistemi ADI
- **Organizzazione automatica** della struttura cartelle per disegni

### Problema che risolve
- **Frammentazione**: Documenti sparsi in sistemi diversi senza catalogazione unificata
- **Download manuale**: Processi ripetitivi per scaricare centinaia di PDF
- **Organizzazione**: Mancanza di struttura standard per archiviare disegni
- **Accessibilità**: Difficoltà nel trovare rapidamente documenti specifici

## 🛠️ Tecnologie utilizzate

### Linguaggi
- **Python 3.8+** - Backend e automazione
- **JavaScript (ES6+)** - Frontend interattivo
- **HTML5/CSS3** - Interfaccia utente

### Framework
- **Flask 2.x** - Web framework leggero e flessibile
- **Pandas** - Manipolazione dati Excel
- **OpenPyXL** - Lettura/scrittura file Excel

### Librerie principali
- **PyAutoGUI** - Automazione interfaccia utente per download
- **PyNput** - Cattura input tastiera per controllo processi
- **Selenium WebDriver** - Automazione browser avanzata
- **Requests** - Chiamate HTTP per API REST

## 📁 Struttura del progetto

```
H:\96-GESTIONE_STUDI\PY\
├── 📄 app.py                    # Applicazione Flask principale
├── 📄 data_loader.py            # Caricamento dati da Excel
├── 📄 adi_fetcher.py            # Fetcher per sistema ADI
├── 📄 runner.py                 # Orchestratore automazione download
├── 📄 macro_1.py                # Script automazione singola
├── 📄 recorder.py               # Registrazione azioni utente
├── 📄 create_drawings_structure*.py  # Creazione struttura cartelle
├── 📄 requirements.txt          # Dipendenze Python
├── 📄 quick_test.json           # Configurazione test ADI
├── 📁 particolari_vecchi/       # App separata per ricerca e download archivio particolari
│   ├── 📄 app.py
│   ├── 📄 routes.py
│   ├── 📄 start_server.bat
│   ├── 📁 templates/
│   │   └── 📄 index.html
│   └── 📁 static/
│       ├── 📁 css/
│       │   └── 📄 style.css
│       └── 📁 js/
│           └── 📄 app.js
├── 📁 static/                   # Asset statici
│   ├── 📁 css/
│   │   └── 📄 style.css         # Stili dark theme
│   └── 📁 js/
│       ├── 📄 app.js            # Logica frontend
│       └── 📄 sidebar-manager.js # Gestione sidebar responsive
├── 📁 templates/
│   └── 📄 index.html            # Template principale
├── 📁 downloads/                # PDF scaricati automaticamente
├── 📁 __pycache__/              # Cache Python
└── 📄 *.xlsx                    # File dati Excel
```

## 🏗️ Architettura

### Pattern utilizzati
- **MVC (Model-View-Controller)**: Separazione logica tra dati, presentazione e controllo
- **Repository Pattern**: `DataLoader` come astrazione per accesso dati
- **Factory Pattern**: Creazione dinamica di strutture cartelle
- **Observer Pattern**: Monitoraggio download con `pynput`

### Organizzazione del codice

#### Backend (Flask)
```python
# Struttura modulare
├── app.py           # Routes e logica principale
├── data_loader.py   # Astrazione dati Excel
└── adi_fetcher.py   # Integrazione sistema esterno
```

#### Frontend (Vanilla JS)
```javascript
// Componenti modulari
├── app.js           # Logica applicazione principale
└── sidebar-manager.js # Gestione UI responsive
```

#### Automazione
```python
# Pipeline di processamento
├── recorder.py      # Cattura azioni utente
├── macro_1.py       # Esecuzione singola
└── runner.py        # Orchestrazione massiva
```

## 🔄 Flusso di esecuzione

### Avvio applicazione web
1. **Caricamento dati**: `DataLoader` legge Excel e popola cache
2. **Avvio Flask**: Server su `http://localhost:8000`
3. **Rendering UI**: Template HTML con sidebar dinamica
4. **Interazione**: JavaScript gestisce filtri e navigazione

### Processo automazione download
1. **Lettura codici**: Excel con lista codici da processare
2. **Esecuzione macro**: PyAutoGUI simula navigazione utente
3. **Monitoraggio**: `pynput` cattura tasti interruzione
4. **Aggiornamento stato**: Progress salvato in JSON
5. **Organizzazione**: File salvati in struttura cartelle

## 🚀 Installazione e utilizzo

### Prerequisiti
- **Python 3.8+**
- **Google Chrome** o **Microsoft Edge** (per automazione)
- **Windows 10/11** (ottimizzato per Windows)

### Installazione rapida
```bash
# Clona repository
git clone <repository-url>
cd raccoglitore

# Setup ambiente virtuale
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate   # Linux/Mac

# Installa dipendenze
pip install -r requirements.txt
```

### Avvio applicazione
```bash
# Avvia server web
python app.py

# Accedi a http://localhost:8000
```

### Configurazione automazione
```powershell
# Imposta percorso Chrome (se necessario)
$env:CHROME_PATH = 'C:\Program Files\Google\Chrome\Application\chrome.exe'

# Oppure usa Edge
$env:EDGE_PATH = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
$env:BROWSER = 'edge'
```

### Utilizzo base
1. **Navigazione**: Usa sidebar per esplorare famiglie → sequenze
2. **Visualizzazione PDF**: Clicca su sequenza per anteprima
3. **Download manuale**: Pulsante "Apri PDF locale"
4. **Automazione**: `python runner.py` per processamento massivo
5. **Azioni rapide**: Top bar con avviso a sinistra e pulsanti "Nuovo studio" / "Aggiungi codice grp." a destra (solo grafica, senza logica)

## 📦 Dipendenze principali

| Libreria | Versione | Scopo |
|----------|----------|--------|
| **Flask** | 2.x | Web framework |
| **Pandas** | 1.x | Manipolazione dati Excel |
| **OpenPyXL** | 3.x | Lettura/scrittura Excel |
| **PyAutoGUI** | 0.9.x | Automazione UI |
| **PyNput** | 1.x | Cattura input tastiera |
| **Selenium** | 4.x | Automazione browser |
| **Requests** | 2.x | Chiamate HTTP |

### Installazione dipendenze
```bash
pip install flask pandas openpyxl pyautogui pynput selenium requests
```

## 🔧 Possibili miglioramenti

### Criticità attuali
- **Autenticazione mancante**: Nessun controllo accessi
- **Gestione errori**: Alcuni edge case non gestiti
- **Performance**: Cache limitata per grandi dataset
- **Browser dependency**: Dipendenza da Chrome/Edge specifici

### Suggerimenti di refactor

#### 1. **Architettura modulare**
```python
# Struttura proposta
raccoglitore/
├── 📁 src/
│   ├── 📁 api/          # Routes Flask
│   ├── 📁 core/         # Business logic
│   ├── 📁 automation/   # Script automazione
│   └── 📁 utils/        # Utilities
├── 📁 tests/            # Unit tests
├── 📁 docs/             # Documentazione
└── 📁 config/           # Configurazioni
```

#### 2. **Database relazionale**
```python
# Sostituire Excel con SQLite/PostgreSQL
from sqlalchemy import create_engine
engine = create_engine('sqlite:///studies.db')
```

#### 3. **API REST completa**
```python
# Aggiungere versioning e documentazione
@app.route('/api/v1/families')
def get_families_v1():
    # Implementazione con pagination, filtri, ecc.
```

#### 4. **Frontend moderno**
```javascript
// Migrare a React/Vue per migliore UX
// Aggiungere:
// - Virtual scrolling per grandi liste
// - Drag & drop per organizzazione
// - Real-time updates con WebSocket
```

#### 5. **Sistema di logging strutturato**
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('raccoglitore.log'),
        logging.StreamHandler()
    ]
)
```

#### 6. **Containerizzazione**
```dockerfile
# Dockerfile per deployment consistente
FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "app.py"]
```

#### 7. **Testing automatizzato**
```python
# Aggiungere pytest per coverage completa
import pytest
def test_pdf_download():
    # Test end-to-end automazione
```

#### 8. **Sicurezza migliorata**
```python
# Aggiungere autenticazione JWT
from flask_jwt_extended import JWTManager
jwt = JWTManager(app)
```

## 📖 Esempi di utilizzo

### Visualizzazione dati
```javascript
// Caricamento famiglie via API
fetch('/api/families')
  .then(r => r.json())
  .then(families => {
    // Render sidebar con famiglie
  });
```

### Automazione download
```python
# Processamento singolo codice
from runner import process_code
result = process_code('TUNI032')
print(f"Downloaded: {result['filename']}")
```

### Creazione struttura cartelle
```python
# Genera struttura da Excel
from create_drawings_structure_fixed import make_structure
result = make_structure('data.xlsx', 'H:\\DISEGNI')
print(f"Created {len(result['created'])} directories")
```

## ❓ FAQ

### Perché l'automazione usa immagini invece di selettori CSS?
**Risposta**: I sistemi legacy spesso non hanno API o selettori stabili. Il riconoscimento immagini garantisce compatibilità anche con interfacce che cambiano frequentemente.

### Come gestire timeout durante i download?
**Risposta**: Il sistema `runner.py` include retry logic e gestione interruzioni. Premi `Ctrl` per fermare gracefully.

### Posso usare browser diversi da Chrome?
**Risposta**: Sì, supporta Chrome, Edge e Firefox. Configura le variabili d'ambiente `BROWSER` e percorsi appropriati.

### Come aggiungere nuove famiglie di prodotti?
**Risposta**: Modifica il file Excel `Gestione_Studi_DB_20251010.xlsx` e riavvia l'applicazione. La struttura si aggiorna automaticamente.

### Il sistema è sicuro per uso in produzione?
**Risposta**: Attualmente è un prototipo per uso interno. Per produzione aggiungere: autenticazione, validazione input, logging sicuro, e containerizzazione.

---

**Sviluppato per ottimizzare la gestione documentale in ambiente industriale.**  
*Per supporto o contributi, aprire issue nel repository.*
