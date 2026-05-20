from typing import Any, Dict, List


class GroupsMachinesCache:
    def __init__(self):
        self._cache = None

    def get_cached_data(self, loader) -> List[Dict[str, Any]]:
        if self._cache is not None:
            return self._cache

        df = loader.get_groups_machines()
        if df is None or df.empty:
            self._cache = []
            return self._cache

        data = []
        for _, row in df.iterrows():
            data.append({
                'id': str(row.get('id', '')).strip(),
                'cod': str(row.get('cod', '')).strip(),
                'pro': str(row.get('pro', '')).strip(),
                'tipo': str(row.get('tipo', '')).strip(),
                'articolo': str(row.get('articolo', '')).strip(),
                'desart': str(row.get('desart', '')).strip(),
            })
        self._cache = data
        return self._cache
