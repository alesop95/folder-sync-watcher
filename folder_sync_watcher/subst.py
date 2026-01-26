import subprocess


class SubstManager:
    """Gestisce le unità virtuali SUBST per Windows"""

    @staticmethod
    def create_subst_drive(drive_letter: str, path: str) -> bool:
        """Crea un'unità virtuale SUBST"""
        try:
            cmd = f'subst {drive_letter}: "{path}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    @staticmethod
    def remove_subst_drive(drive_letter: str) -> bool:
        """Rimuove un'unità virtuale SUBST"""
        try:
            cmd = f'subst {drive_letter}: /D'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    @staticmethod
    def list_subst_drives() -> dict:
        """Lista tutte le unità SUBST attive"""
        try:
            result = subprocess.run('subst', shell=True, capture_output=True, text=True)
            drives = {}
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if ': => ' in line:
                        drive, path = line.split(': => ', 1)
                        normalized_drive = drive.strip()
                        if normalized_drive.endswith(':'):
                            normalized_drive = normalized_drive[:-1]
                        normalized_drive = normalized_drive.replace('\\', '').replace('/', '')
                        if normalized_drive:
                            drives[normalized_drive.upper()] = path.strip()
            return drives
        except Exception:
            return {}

    @staticmethod
    def is_subst_drive(drive_letter: str) -> bool:
        """Verifica se una lettera di unità è un SUBST"""
        drives = SubstManager.list_subst_drives()
        return drive_letter.upper().rstrip(':').rstrip('\\') in drives
