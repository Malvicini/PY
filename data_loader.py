import pandas as pd


class DataLoader:
    """Load families and sequences from the provided Excel file.

    Expectations:
    - Sheet1 contains families with columns: family_code, family_name
    - Sheet2 contains sequences with columns: sequence_id, family_code, description
    """

    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        # Lazy load caches
        self._families = None
        self._sequences = None
        self._groups_machines = None

    def _load(self):
        # Read sheets
        xls = pd.ExcelFile(self.excel_path)
        # Heuristics: first sheet -> families, second -> sequences
        try:
            df_fam = pd.read_excel(xls, sheet_name=0)
        except Exception:
            df_fam = pd.DataFrame()
        try:
            df_seq = pd.read_excel(xls, sheet_name=1)
        except Exception:
            df_seq = pd.DataFrame()

        # Normalize column names to lowercase
        df_fam.columns = [c.lower() for c in df_fam.columns]
        df_seq.columns = [c.lower() for c in df_seq.columns]

        self._families = df_fam
        self._sequences = df_seq

    def get_families(self):
        if self._families is None:
            self._load()
        df = self._families
        if df is None or df.empty:
            return []
        # Try to find appropriate columns (prefer columns containing 'cod' for short code)
        code_col = None
        id_col = None
        name_col = None
        for c in df.columns:
            lc = c.lower()
            if 'cod' in lc and code_col is None:
                code_col = c
            if 'id' == lc or lc.endswith('id') or lc == 'id':
                id_col = c
            if 'name' in lc or 'descr' in lc or 'des' in lc:
                name_col = c

        # Fallbacks
        if id_col is None and len(df.columns) > 0:
            id_col = df.columns[0]
        if code_col is None:
            # prefer second column if first is id
            code_col = df.columns[1] if len(df.columns) > 1 else id_col
        if name_col is None:
            # prefer description-like column else code
            name_col = df.columns[2] if len(df.columns) > 2 else code_col

        families = []
        for _, row in df.iterrows():
            families.append({
                'family_id': str(row.get(id_col, '')).strip(),
                'family_code': str(row.get(code_col, '')).strip(),
                'family_name': str(row.get(name_col, '')).strip(),
            })
        return families

    def get_sequences_for_family(self, family_code: str):
        if self._sequences is None:
            self._load()
        df = self._sequences
        if df is None or df.empty:
            return []
        # For your workbook, sheet 'Studi' uses column 'CODICE' for family short code
        # and 'PROGRESSIVO' for the sequence number. Prefer these explicitly.
        cols = [c.lower() for c in df.columns]
        fam_col = None
        prog_col = None
        desc_col = None

        for c in df.columns:
            lc = c.lower()
            if lc == 'codice' or 'cod' in lc:
                fam_col = c
            if lc == 'progressivo' or 'prog' in lc:
                prog_col = c
            if 'descr' in lc or 'description' in lc or 'desc' in lc:
                desc_col = c

        # Fallbacks
        if fam_col is None:
            fam_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
        if prog_col is None:
            # use PROGRESSIVO if present else use ID or first col
            prog_col = next((c for c in df.columns if 'progress' in c.lower() or 'prog' in c.lower()), df.columns[0])
        if desc_col is None:
            desc_col = next((c for c in df.columns if 'descr' in c.lower() or 'description' in c.lower() or 'des' in c.lower()), prog_col)

        fc = str(family_code).strip()
        filtered = df[df[fam_col].astype(str).str.strip() == fc]

        sequences = []
        for _, row in filtered.iterrows():
            seq_id = str(row.get(prog_col, '')).strip()
            # Pad sequence_id to 3 digits with leading zeros
            try:
                seq_id = str(int(seq_id)).zfill(3)
            except ValueError:
                pass  # keep as is if not numeric
            sequences.append({
                'sequence_id': seq_id,
                'description': str(row.get(desc_col, '')).strip(),
            })
        return sequences

    def get_groups_machines(self):
        if self._groups_machines is None:
            self._load_groups_machines()
        return self._groups_machines

    def _load_groups_machines(self):
        # Read the third sheet for groups and machines details
        xls = pd.ExcelFile(self.excel_path)
        try:
            df = pd.read_excel(xls, sheet_name=2)  # Third sheet
        except Exception:
            df = pd.DataFrame()

        # Normalize column names to lowercase
        df.columns = [c.lower() for c in df.columns]

        self._groups_machines = df

    def get_groups_machines_for_family(self, family_code: str, sequence_code: str = None):
        if self._groups_machines is None:
            self._load_groups_machines()
        df = self._groups_machines
        if df is None or df.empty:
            return []

        # Filter by family code
        fc = str(family_code).strip().upper()
        filtered = df[df['cod'].astype(str).str.strip().str.upper() == fc]

        if sequence_code:
            # Filter by sequence code (progressivo), normalize by removing leading zeros
            sc_normalized = str(sequence_code).lstrip('0') or '0'
            filtered = filtered[filtered['pro'].astype(str).str.strip().str.lstrip('0').fillna('0') == sc_normalized]

        groups_machines = []
        for _, row in filtered.iterrows():
            groups_machines.append({
                'id': str(row.get('id', '')).strip(),
                'cod': str(row.get('cod', '')).strip(),
                'pro': str(row.get('pro', '')).strip(),
                'tipo': str(row.get('tipo', '')).strip(),
                'articolo': str(row.get('articolo', '')).strip(),
                'desart': str(row.get('desart', '')).strip(),
            })
        return groups_machines
