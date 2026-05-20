import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = os.environ.get('GESTIONE_STUDI_DB', 'Gestione_Studi_DB_20251010.xlsx')
DEFAULT_DRAWINGS_DIR = os.environ.get('DRAWINGS_DIR', r'H:\96-GESTIONE_STUDI\DISEGNI')
QUICK_TEST_FILE = BASE_DIR / 'quick_test.json'
CREDENTIALS_FILE = BASE_DIR / 'stored_credentials.json'
