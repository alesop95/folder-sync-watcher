import hashlib


class FileHasher:
    """Utility per calcolare hash dei file"""

    @staticmethod
    def get_file_hash(file_path: str) -> str:
        """Calcola l'hash MD5 di un file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""
