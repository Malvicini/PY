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


def _candidate_family_prefixes(code, base_dir=None):
    """Return plausible family prefixes for a code.

    The lookup should prefer the family prefix derived from the study code itself.
    For example, TUNI032 resolves to TUNI before falling back to a generic stem.
    """
    normalized = sanitize_filesystem_name(str(code).strip()) or str(code).strip()
    if not normalized:
        return []

    code_upper = normalized.upper()
    prefixes = []

    direct_prefix = _derive_family_prefix(code_upper)
    if direct_prefix:
        prefixes.append(direct_prefix)

    stem = code_upper
    previous_stem = None
    while stem and stem != previous_stem:
        previous_stem = stem
        stem = re.sub(r'\d+$', '', stem)
        if stem and stem not in prefixes:
            prefixes.append(stem)
        if len(stem) <= 1:
            break

    unique_prefixes = []
    for prefix in prefixes:
        if prefix and prefix not in unique_prefixes:
            unique_prefixes.append(prefix)

    return sorted(unique_prefixes, key=lambda item: (-len(item), item))


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

    safe_code = sanitize_filesystem_name(str(code).strip()) or str(code).strip()
    if not safe_code:
        return None, 'Code is empty'

    code = safe_code.upper()
    base_dir = os.path.abspath(os.path.expanduser(str(base_dir)))

    prefixes = _candidate_family_prefixes(code, base_dir)
    if not prefixes:
        return None, f'Prefix not found in code: {code}'

    candidate_dirs = []
    for prefisso in prefixes:
        candidate_dirs.append(os.path.join(base_dir, prefisso, code))
        candidate_dirs.append(os.path.join(base_dir, code))
        candidate_dirs.append(os.path.join(base_dir, prefisso))

    seen_dirs = set()
    for candidate_dir in candidate_dirs:
        if not candidate_dir or candidate_dir in seen_dirs:
            continue
        seen_dirs.add(candidate_dir)

        if os.path.isdir(candidate_dir):
            try:
                for fn in os.listdir(candidate_dir):
                    if fn.lower().endswith('.pdf'):
                        stem = os.path.splitext(fn)[0].lower()
                        if stem == code.lower():
                            return os.path.join(candidate_dir, fn), None
            except Exception:
                pass

        for ext in ['.pdf', '.PDF']:
            pdf_path = os.path.join(candidate_dir, code + ext)
            if os.path.isfile(pdf_path):
                return pdf_path, None

    search_roots = []
    for prefisso in prefixes:
        pref_dir = os.path.join(base_dir, prefisso)
        if os.path.isdir(pref_dir):
            search_roots.append(pref_dir)
    if not search_roots and os.path.isdir(base_dir):
        search_roots.append(base_dir)

    seen_roots = set()
    for search_root in search_roots:
        if search_root in seen_roots:
            continue
        seen_roots.add(search_root)
        for root, _, files in os.walk(search_root):
            for filename in files:
                if not filename.lower().endswith('.pdf'):
                    continue
                stem = os.path.splitext(filename)[0].lower()
                stem_without_suffix = re.sub(r'\s*\(\d+\)$', '', stem)
                if stem_without_suffix == code.lower():
                    return os.path.join(root, filename), None

    return None, f'PDF not found for {code}'
