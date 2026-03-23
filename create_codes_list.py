import pandas as pd

def main():
    # Leggi il terzo sheet (Gruppi e Macchine)
    df = pd.read_excel('Gestione_Studi_DB_20251010.xlsx', sheet_name=2)
    df.columns = [c.lower() for c in df.columns]

    # Estrai codici unici
    unique_codes = df[['cod', 'pro']].drop_duplicates()

    # Crea il codice completo: COD + PRO (con zeri iniziali a 3 cifre)
    unique_codes['full_code'] = unique_codes['cod'] + unique_codes['pro'].astype(str).str.zfill(3)

    # Ordina alfabeticamente
    unique_codes = unique_codes.sort_values('full_code')

    # Crea un nuovo DataFrame per l'export
    export_df = unique_codes[['full_code']].copy()
    export_df.columns = ['Codice Studio']

    # Salva in Excel
    export_df.to_excel('elenco_codici_studi.xlsx', index=False)

    print(f"Elenco creato con {len(export_df)} codici unici.")
    print("File salvato: elenco_codici_studi.xlsx")
    print("Primi 10 codici:")
    print(export_df.head(10))

if __name__ == "__main__":
    main()