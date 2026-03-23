import os
import shutil
from data_loader import DataLoader
import re

def normalize_name(name):
    """Normalizza un nome per il confronto"""
    return re.sub(r'[^\w\s]', '', name).upper().replace(' ', '')

def find_matching_folder(family_name, existing_folders):
    """Trova la cartella corrispondente a una famiglia"""
    normalized_family = normalize_name(family_name)

    # Prima cerca corrispondenza esatta
    for folder in existing_folders:
        if normalize_name(folder) == normalized_family:
            return folder

    # Poi cerca corrispondenze parziali (contiene il nome)
    for folder in existing_folders:
        if normalized_family in normalize_name(folder) or normalize_name(folder) in normalized_family:
            return folder

    return None

def rename_all_folders():
    # Percorso base dei disegni
    base_path = r"H:\96-GESTIONE_STUDI\DISEGNI"

    # Carica i dati dal Excel
    loader = DataLoader('Gestione_Studi_DB_20251010.xlsx')
    families = loader.get_families()

    # Ottieni la lista delle cartelle esistenti
    existing_folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]

    print(f"Trovate {len(families)} famiglie nel database e {len(existing_folders)} cartelle")

    # Processa ogni famiglia
    renamed_count = 0
    skipped_count = 0

    for fam in families:
        family_name = fam['family_name']
        family_code = fam['family_code'].lower()

        # Trova la cartella corrispondente
        matching_folder = find_matching_folder(family_name, existing_folders)

        if not matching_folder:
            print(f"  Saltato {family_name} ({family_code}) - nessuna cartella corrispondente trovata")
            skipped_count += 1
            continue

        old_family_path = os.path.join(base_path, matching_folder)
        new_family_path = os.path.join(base_path, family_code.upper())

        # Salta se è già rinominata correttamente
        if matching_folder.upper() == family_code.upper():
            print(f"  Già rinominata: {matching_folder}")
            continue

        print(f"\nRinomino famiglia: {matching_folder} -> {family_code.upper()}")

        try:
            # Rinomina la cartella principale
            os.rename(old_family_path, new_family_path)
            renamed_count += 1
            print(f"  Cartella principale rinominata")

            # Ora rinomina le sotto-cartelle
            if os.path.exists(new_family_path):
                rename_subfolders(new_family_path, family_code.upper(), loader)

        except Exception as e:
            print(f"  Errore nel rinominare {matching_folder}: {e}")
            continue

    print(f"\nRinominazione completata! {renamed_count} famiglie rinominate, {skipped_count} saltate")

def rename_subfolders(family_path, family_code, loader):
    """Rinomino le sotto-cartelle per una famiglia"""
    try:
        # Carica le sequenze per questa famiglia
        sequences = loader.get_sequences_for_family(family_code)

        if not sequences:
            print(f"  Nessuna sequenza trovata per {family_code}")
            return

        # Lista le sotto-cartelle
        subfolders = [f for f in os.listdir(family_path) if os.path.isdir(os.path.join(family_path, f))]

        renamed_subs = 0
        for subfolder in subfolders:
            # Estrai il numero dalla cartella (cerca pattern come "XXX" alla fine)
            match = re.search(r'(\d+)$', subfolder)
            if match:
                seq_num = match.group(1).zfill(3)  # padding a 3 cifre
                new_name = f"{family_code}{seq_num}"

                old_path = os.path.join(family_path, subfolder)
                new_path = os.path.join(family_path, new_name)

                # Salta se già rinominata
                if subfolder == new_name:
                    continue

                try:
                    os.rename(old_path, new_path)
                    renamed_subs += 1
                    print(f"    {subfolder} -> {new_name}")
                except Exception as e:
                    print(f"    Errore nel rinominare {subfolder}: {e}")
            else:
                print(f"    Saltato {subfolder} (numero non trovato)")

        if renamed_subs > 0:
            print(f"  Rinominate {renamed_subs} sotto-cartelle")

    except Exception as e:
        print(f"  Errore nel processare sotto-cartelle per {family_code}: {e}")

if __name__ == "__main__":
    rename_all_folders()