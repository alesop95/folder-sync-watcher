import subprocess


class SubstManager:
    """Gestisce le unità virtuali SUBST per Windows"""

    @staticmethod
    def create_subst_drive(drive_letter: str, path: str) -> bool:
        """Crea un'unità virtuale SUBST.

        Passa gli argomenti come lista, senza `shell=True`: `subst.exe` è un eseguibile vero
        sotto `System32`, non serve una shell per invocarlo, e passare per `cmd.exe` con una
        stringa concatenata codifica la riga di comando con la codepage legacy della console.
        Un percorso con caratteri fuori da quella codepage, come un'emoji, arriva quindi
        troncato o sostituito e il SUBST fallisce senza una ragione visibile. Con la lista,
        Windows riceve gli argomenti in UTF-16 così come sono in Python.
        """
        try:
            result = subprocess.run(
                ['subst', f'{drive_letter}:', path], capture_output=True, text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    @staticmethod
    def remove_subst_drive(drive_letter: str) -> bool:
        """Rimuove un'unità virtuale SUBST"""
        try:
            result = subprocess.run(
                ['subst', f'{drive_letter}:', '/D'], capture_output=True, text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    @staticmethod
    def list_subst_drives() -> dict:
        """Lista tutte le unità SUBST attive"""
        try:
            result = subprocess.run(['subst'], capture_output=True, text=True)
            drives = {}
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if ': => ' in line:
                        drive, path = line.split(': => ', 1)
                        # L'output reale e' "A:\: => percorso", cioe' i due punti seguiti dal
                        # backslash prima del separatore, non solo i due punti come il codice
                        # precedente assumeva: quel `endswith(':')` non scattava mai, la lettera
                        # restava con i due punti attaccati, e un'unita' gia' montata non veniva
                        # mai riconosciuta come tale. rstrip(':\\/ ') toglie ogni combinazione
                        # finale di due punti, backslash, slash e spazi in un solo passaggio.
                        normalized_drive = drive.strip().rstrip(':\\/ ')
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
