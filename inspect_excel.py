import pandas as pd

X = 'Gestione_Studi_DB_20251010.xlsx'
xls = pd.ExcelFile(X)
print('Sheets:', xls.sheet_names)
for i, name in enumerate(xls.sheet_names):
    df = pd.read_excel(xls, sheet_name=i)
    print('\n--- Sheet', i, name, '---')
    print('Columns:', list(df.columns[:10]))
    print(df.head(5))
