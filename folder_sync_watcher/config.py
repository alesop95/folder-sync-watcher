import json
import fnmatch
from pathlib import Path


class SyncConfig:
    """Gestione della configurazione di sincronizzazione"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self) -> dict:
        """Carica la configurazione dal file JSON"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def is_excluded(self, path: str) -> bool:
        """Verifica se un file/cartella deve essere escluso"""
        try:
            path_obj = Path(path)
            path_str = str(path_obj)
            name = path_obj.name
            patterns = self.config.get('sync_settings', {}).get('excluded_patterns', [])

            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(path_str, pattern):
                    return True
                if pattern and pattern in path_str:
                    return True
            return False
        except Exception:
            return True
