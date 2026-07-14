"""PDF finder module for resolving drawing codes to local filesystem paths."""

import os
import re

from helpers import sanitize_filesystem_name


def _derive_family_prefix(code):
    """Derive the drawings family folder from a study code.

    The canonical rule is to use the exact family code already present in the Excel
    workbook when possible. For example, codes like TUNI032 and GS-U008 should be
    grouped under their family folders TUNI and GS-U, respectively.
    """
    normalized = sanitize_filesystem_name(str(code).strip()) or str(code).strip()
    if not normalized:
        return None

    match = re.match(r'^([A-Z]+(?:-[A-Z]+)*)', normalized.upper())
    if match:
        return match.group(1)

    return None


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
    
    # Normalize code to uppercase and keep a filesystem-safe version for paths
    safe_code = sanitize_filesystem_name(str(code).strip()) or str(code).strip()
    code = safe_code.upper()
    print(f"DEBUG find_pdf_path: Normalized code='{code}'")
    
    # Derive the family folder from the leading letters of the code.
    # Examples: TUNI032 -> TUNI, GS-U008 -> GS-U, ULHD015 -> ULHD.
    prefisso = _derive_family_prefix(code)
    if prefisso:
        print(f"DEBUG: Found prefix {prefisso}")

    if not prefisso:
        return None, f'Prefix not found in code: {code}'
    
    # Search the historical layout first: BASE_DIR / FAMIGLIA / CODICE / CODICE.pdf
    target_dir = os.path.join(base_dir, prefisso, code)
    print(f"DEBUG: Searching in family folder: {target_dir}")

    for ext in ['.pdf', '.PDF']:
        pdf_path = os.path.join(target_dir, code + ext)
        print(f"DEBUG: Checking {pdf_path} - Exists: {os.path.isfile(pdf_path)}")
        if os.path.isfile(pdf_path):
            print(f"DEBUG: Found! {pdf_path}")
            return pdf_path, None

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

    # If the family-based folder does not exist yet, create it retroactively.
    try:
        os.makedirs(target_dir, exist_ok=True)
        print(f"DEBUG: Created missing folder {target_dir}")
    except Exception as exc:
        print(f"DEBUG: Could not create folder {target_dir}: {exc}")

    # Fallback to the flat direct folder layout for newer entries.
    direct_dir = os.path.join(base_dir, code)
    print(f"DEBUG: Searching in direct folder: {direct_dir}")

    for ext in ['.pdf', '.PDF']:
        pdf_path = os.path.join(target_dir, code + ext)
        print(f"DEBUG: Checking {pdf_path} - Exists: {os.path.isfile(pdf_path)}")
        if os.path.isfile(pdf_path):
            print(f"DEBUG: Found! {pdf_path}")
            return pdf_path, None

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

    print(f"DEBUG: PDF not found in {direct_dir} or {target_dir}")
    return None, f'PDF not found in {direct_dir} or {target_dir}'
