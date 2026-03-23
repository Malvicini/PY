#!/usr/bin/env python3
"""Create folder structure for drawings based on Excel DB.

Usage:
  python create_drawings_structure.py [--base-dir <path>]

Defaults to H:\96-GESTIONE_STUDI\DISEGNI
"""
import os
import argparse
from data_loader import DataLoader


def sanitize(name: str) -> str:
    # keep alnum, space, dash, underscore
    return ''.join(c for c in (name or '') if c.isalnum() or c in (' ', '-', '_')).strip()


def make_structure(excel_path: str, base_dir: str):
    loader = DataLoader(excel_path)
    families = loader.get_families()

    created = []
    existed = []
    errors = []

    if not os.path.exists(base_dir):
        try:
            os.makedirs(base_dir, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f'Could not create base dir {base_dir}: {e}')

    for fam in families:
        fam_name = fam.get('family_name') or fam.get('family_code') or fam.get('family_id') or 'Unknown'
        fam_name_s = sanitize(fam_name) or 'Unknown'
        fam_dir = os.path.join(base_dir, fam_name_s)
        try:
            if not os.path.exists(fam_dir):
                os.makedirs(fam_dir, exist_ok=True)
                created.append(fam_dir)
            else:
                existed.append(fam_dir)
        except Exception as e:
            errors.append({'path': fam_dir, 'detail': str(e)})

        # sequences
        seqs = loader.get_sequences_for_family(fam.get('family_code') or fam.get('family_id') or fam_name)
        for s in seqs:
            seq_code = s.get('sequence_id') or ''
            # extract numeric part
            import re
            m = re.search(r"(\d+)", seq_code)
            if m:
                num = m.group(1)
                subname = f"{fam_name_s} {int(num):03d}"
            else:
                subname = f"{fam_name_s} {sanitize(seq_code) or '0'}"
            subdir = os.path.join(fam_dir, subname)
            try:
                if not os.path.exists(subdir):
                    os.makedirs(subdir, exist_ok=True)
                    created.append(subdir)
                else:
                    existed.append(subdir)
            except Exception as e:
                errors.append({'path': subdir, 'detail': str(e)})

    return {'created': created, 'existed': existed, 'errors': errors}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--excel', default='Gestione_Studi_DB_20251010.xlsx', help='Excel DB file')
    p.add_argument('--base-dir', default=r'H:\96-GESTIONE_STUDI\DISEGNI', help='Base drawings directory to create')
    args = p.parse_args()

    print('Using Excel:', args.excel)
    print('Creating under:', args.base_dir)

    res = make_structure(args.excel, args.base_dir)
    print('\nSummary:')
    print('Created:', len(res['created']))
    print('Existing:', len(res['existed']))
    print('Errors:', len(res['errors']))
    if res['errors']:
        print('\nErrors detail:')
        for e in res['errors']:
            print('-', e['path'], '->', e['detail'])

    # Optionally, print a few created dirs for inspection
    if res['created']:
        print('\nExample created directories:')
        for d in res['created'][:10]:
            print('-', d)

    print('\nDone.')
