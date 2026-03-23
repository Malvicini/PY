from adi_fetcher import fetch_pdf_via_selenium
import os

USERNAME = os.environ.get('ADI_USER') or input('ADI username: ')
PASSWORD = os.environ.get('ADI_PASS') or input('ADI password: ')
SEARCH_CODE = os.environ.get('ADI_CODE') or input('Search code (Codice Disegno): ')

CHROME_PATH = os.environ.get('CHROME_PATH')
BROWSER = os.environ.get('BROWSER', 'edge')
DRIVER_PATH = os.environ.get('DRIVER_PATH')

EDGE_PATH = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'

pdf_bytes = fetch_pdf_via_selenium(USERNAME, PASSWORD, SEARCH_CODE,
                                  headless=False, timeout=60,
                                  chrome_path=CHROME_PATH,
                                  browser=BROWSER, browser_path=os.environ.get('EDGE_PATH') if BROWSER=='edge' else CHROME_PATH,
                                  driver_path=DRIVER_PATH)
if pdf_bytes:
    with open('result_test.pdf', 'wb') as f:
        f.write(pdf_bytes)
    print('PDF salvato in result_test.pdf')
else:
    print('PDF non trovato')