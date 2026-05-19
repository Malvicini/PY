"""PDF finder module for resolving drawing codes to local filesystem paths."""

import os
import re


def find_pdf_path(code, base_dir=None):
    """Find PDF file path for a given drawing code in local filesystem.
    
    Directory layout: BASE_DIR / PREFISSO / CODICE / CODICE.pdf
    Example: H:\\96-GESTIONE_STUDI\\DISEGNI\\TT30\\TT30001\\TT30001.pdf
    
    Args:
        code: Drawing code (e.g., 'TT30001')
        base_dir: Base drawings directory. Defaults to DRAWINGS_DIR env or H:\\96-GESTIONE_STUDI\\DISEGNI
    
    Returns:
        Tuple (pdf_path, error):
            - (pdf_path, None) if found
            - (None, error_message) if not found
    """
    if not base_dir:
        base_dir = os.environ.get('DRAWINGS_DIR', r'H:\96-GESTIONE_STUDI\DISEGNI')
    
    # DEBUG: Log the received code
    print(f"DEBUG find_pdf_path: Received code='{code}'")
    
    # Normalize code to uppercase
    code = code.upper()
    print(f"DEBUG find_pdf_path: Normalized code='{code}'")
    
    # Try to find prefix by checking which folder in DISEGNI matches the code
    # Try in descending length order (5 char, 4 char, 3 char, 2 char)
    prefisso = None
    
    for prefix_len in [5, 4, 3, 2]:
        test_prefix = code[:prefix_len]
        test_path = os.path.join(base_dir, test_prefix)
        if os.path.isdir(test_path):
            prefisso = test_prefix
            print(f"DEBUG: Found prefix {prefisso} (length {prefix_len})")
            break
    
    if not prefisso:
        # Fallback: extract only initial letters
        prefisso_match = re.match(r'([A-Z]+)', code)
        if prefisso_match:
            prefisso = prefisso_match.group(1)
            print(f"DEBUG: Prefix extracted from letters: {prefisso}")
        else:
            return None, f'Prefix not found in code: {code}'
    
    # Search ONLY in: BASE_DIR / PREFISSO / CODICE / CODICE.pdf (or .PDF)
    target_dir = os.path.join(base_dir, prefisso, code)
    
    print(f"DEBUG: Searching for PDF with code={code}, prefix={prefisso}")
    print(f"DEBUG: Searching in: {target_dir}")
    
    # Try both .pdf and .PDF extensions
    for ext in ['.pdf', '.PDF']:
        pdf_path = os.path.join(target_dir, code + ext)
        print(f"DEBUG: Checking {pdf_path} - Exists: {os.path.isfile(pdf_path)}")
        if os.path.isfile(pdf_path):
            print(f"DEBUG: Found! {pdf_path}")
            return pdf_path, None
    
    # If exact file not found, try any PDF in the folder
    if os.path.isdir(target_dir):
        print(f"DEBUG: Directory {target_dir} exists, searching for any PDF inside...")
        try:
            for fn in os.listdir(target_dir):
                if fn.lower().endswith('.pdf'):
                    full_path = os.path.join(target_dir, fn)
                    print(f"DEBUG: Found alternative PDF: {full_path}")
                    return full_path, None
        except Exception as e:
            print(f"DEBUG: Error listing directory: {e}")
    
    # If not found, return error (WITHOUT global search)
    print(f"DEBUG: PDF not found in {target_dir}")
    return None, f'PDF not found in {target_dir}'
