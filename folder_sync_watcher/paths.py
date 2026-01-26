import re
import time
from pathlib import Path


class FilePathManager:
    """Gestisce i problemi con percorsi lunghi e caratteri speciali"""

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitizza il nome del file rimuovendo caratteri problematici"""
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        sanitized = re.sub(r'\s*,\s*', '_', sanitized)
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        return sanitized

    @staticmethod
    def get_short_path(long_path: str) -> str:
        """Ottiene il percorso corto 8.3 per Windows"""
        try:
            import win32api

            return win32api.GetShortPathName(long_path)
        except Exception:
            return long_path

    @staticmethod
    def is_file_locked(file_path: str) -> bool:
        """Verifica se un file è bloccato da un'altra applicazione"""
        try:
            with open(file_path, 'r+b'):
                return False
        except (IOError, OSError):
            return True

    @staticmethod
    def wait_for_file_unlock(file_path: str, max_wait: int = 30) -> bool:
        """Aspetta che un file venga sbloccato"""
        for _ in range(max_wait):
            if not FilePathManager.is_file_locked(file_path):
                return True
            time.sleep(1)
        return False

    @staticmethod
    def is_office_process_using_file(file_path: str) -> bool:
        """Verifica se un processo Office sta usando il file specifico"""
        try:
            import psutil

            file_name = Path(file_path).name.lower()

            for proc in psutil.process_iter(['pid', 'name', 'open_files']):
                try:
                    if proc.info['name'] and proc.info['name'].lower() in ['winword.exe', 'excel.exe', 'powerpnt.exe']:
                        if proc.info['open_files']:
                            for f in proc.info['open_files']:
                                if file_name in f.path.lower():
                                    return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception:
            return FilePathManager.is_file_locked(file_path)
