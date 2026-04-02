#!/usr/bin/env python3
"""Create folder structure for drawings based on Excel DB.

Usage:
  python create_drawings_structure.py [--base-dir <path>]

Defaults to H:\\96-GESTIONE_STUDI\\DISEGNI
"""
import os
import argparse
import logging
from data_loader import DataLoader


def sanitize(name: str) -> str:
    """Keep only alphanumeric, space, dash, underscore characters."""
    if not name:
        return ''
    return ''.join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()


def make_structure(excel_path: str, base_dir: str, verbose: bool = False):
    """Create folder structure idempotently - only creates missing folders."""
    loader = DataLoader(excel_path)
    families = loader.get_families()

    created = []
    existed = []
    errors = []

    # Setup logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')

    if not os.path.exists(base_dir):
        try:
            os.makedirs(base_dir, exist_ok=True)
            logging.info(f"Created base directory: {base_dir}")
        except Exception as e:
            raise RuntimeError(f'Could not create base dir {base_dir}: {e}')

    logging.info(f"Processing {len(families)} families...")

    for fam in families:
        # CRITICAL FIX: Use family_code instead of family_name for folder name
        fam_code = fam.get('family_code') or fam.get('family_id') or 'Unknown'
        fam_name_s = sanitize(fam_code) or 'Unknown'

        fam_dir = os.path.join(base_dir, fam_name_s)

        try:
            if not os.path.exists(fam_dir):
                os.makedirs(fam_dir, exist_ok=True)
                created.append(fam_dir)
                logging.debug(f"Created family dir: {fam_dir}")
            else:
                existed.append(fam_dir)
                logging.debug(f"Family dir already exists: {fam_dir}")
        except Exception as e:
            errors.append({'path': fam_dir, 'detail': str(e)})
            logging.error(f"Failed to create family dir {fam_dir}: {e}")
            continue  # Skip sequences if family dir failed

        # Get sequences for this family
        family_key = fam.get('family_code') or fam.get('family_id') or fam_code
        seqs = loader.get_sequences_for_family(family_key)

        logging.debug(f"Family {fam_code}: {len(seqs)} sequences")

        for s in seqs:
            seq_code = s.get('sequence_id') or ''
            # Extract numeric part and create proper sequence folder name
            import re
            m = re.search(r"(\d+)", seq_code)
            if m:
                num = m.group(1)
                # CRITICAL FIX: Concatenate directly without space: TRT1001, TRT1002, etc.
                subname = f"{fam_name_s}{int(num):03d}"
            else:
                # Fallback for non-numeric sequences
                subname = f"{fam_name_s}_{sanitize(seq_code) or '0'}"

            subdir = os.path.join(fam_dir, subname)

            try:
                if not os.path.exists(subdir):
                    os.makedirs(subdir, exist_ok=True)
                    created.append(subdir)
                    logging.debug(f"Created sequence dir: {subdir}")
                else:
                    existed.append(subdir)
                    logging.debug(f"Sequence dir already exists: {subdir}")
            except Exception as e:
                errors.append({'path': subdir, 'detail': str(e)})
                logging.error(f"Failed to create sequence dir {subdir}: {e}")

    return {'created': created, 'existed': existed, 'errors': errors}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--excel', default='Gestione_Studi_DB_20251010.xlsx', help='Excel DB file')
    p.add_argument('--base-dir', default=r'H:\96-GESTIONE_STUDI\DISEGNI', help='Base drawings directory to create')
    p.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    args = p.parse_args()

    print('Using Excel:', args.excel)
    print('Creating under:', args.base_dir)
    if args.verbose:
        print('Verbose mode enabled')

    res = make_structure(args.excel, args.base_dir, args.verbose)

    print('\nSummary:')
    print('Created:', len(res['created']))
    print('Existing:', len(res['existed']))
    print('Errors:', len(res['errors']))

    if res['errors']:
        print('\nErrors detail:')
        for e in res['errors']:
            print('-', e['path'], '->', e['detail'])

    # Show examples of created dirs
    if res['created']:
        print('\nExample created directories:')
        for d in res['created'][:10]:
            print('-', d)

    print('\nDone.')