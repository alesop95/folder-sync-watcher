"""Punto unico attraverso cui il watcher scrive sul filesystem.

Prima del 2026-09-10 ogni scrittura era fatta dove serviva, con `copy2` importato inline in
nove punti diversi di `watcher.py`. Finché il programma scriveva e basta la dispersione era
solo brutta; diventa un problema nel momento in cui si vuole una modalità che non scriva,
perché una prova a vuoto è credibile solo se esiste un unico varco da presidiare. Nove varchi
significano nove occasioni di dimenticarne uno, e la dimenticanza si scopre quando la prova a
vuoto ha già scritto.

Questa classe è quel varco. In modalità normale esegue; in prova a vuoto registra che cosa
avrebbe fatto e non tocca nulla. Ogni metodo restituisce vero se l'operazione è avvenuta
davvero, così il chiamante può distinguere il fatto dal simulato senza interrogare la
configurazione.

Limite dichiarato della prova a vuoto, che è inerente e non un difetto dell'implementazione:
non creando cartelle e non copiando file, lo stato del filesystem non avanza, quindi le
decisioni che dipendono da quello stato, in particolare `_should_copy_file` che confronta le
date, vedono un mondo diverso da quello che vedrebbero in una esecuzione reale. La prova a
vuoto dice quali operazioni il primo passaggio produrrebbe, non quelle di un secondo passaggio.
"""

import os
import stat
from pathlib import Path
from shutil import copy2, rmtree
from typing import Optional


def _sblocca_se_read_only(percorso: Path) -> None:
    """Toglie l'attributo read-only da un file esistente, se presente.

    Windows rifiuta di aprire in scrittura un file read-only prima ancora che `copy2` possa
    riallineare i permessi con quelli della sorgente: senza questo passaggio, sovrascrivere o
    rimuovere un file protetto solleva `PermissionError` (verificato sul campo il 2026-09-14,
    su un file lato OneDrive read-only dal 2025, indipendente dall'anonimizzazione). La
    decisione se copiare o rimuovere è gia' presa da chi chiama: questa funzione toglie solo
    l'ostacolo tecnico, non cambia quella decisione. Dopo una copia, `copy2` riporta comunque i
    permessi della sorgente sulla destinazione, quindi un file che deve restare read-only lo
    ridiventa se la sua sorgente lo è.
    """
    if not percorso.exists():
        return
    modo = percorso.stat().st_mode
    if not modo & stat.S_IWRITE:
        os.chmod(percorso, modo | stat.S_IWRITE)


class OperazioniFile:
    """Esegue o simula le scritture, contandole in entrambi i casi."""

    def __init__(self, logger, prova_a_vuoto: bool = False):
        self.logger = logger
        self.prova_a_vuoto = bool(prova_a_vuoto)
        self.conteggi = {'cartelle': 0, 'copie': 0, 'rimozioni': 0, 'spostamenti': 0}

    def _simula(self, tipo: str, verbo: str, etichetta: str) -> bool:
        self.conteggi[tipo] += 1
        if self.prova_a_vuoto:
            self.logger.info(f"[PROVA A VUOTO] {verbo}: {etichetta}")
            return False
        return True

    def crea_cartella(self, percorso: Path, etichetta: Optional[str] = None) -> bool:
        if not self._simula('cartelle', 'creerebbe la cartella', str(etichetta or percorso)):
            return False
        Path(percorso).mkdir(parents=True, exist_ok=True)
        return True

    def copia(self, sorgente, destinazione, etichetta: Optional[str] = None) -> bool:
        if not self._simula('copie', 'copierebbe', str(etichetta or f"{sorgente} -> {destinazione}")):
            return False
        _sblocca_se_read_only(Path(destinazione))
        copy2(str(sorgente), str(destinazione))
        return True

    def rimuovi_file(self, percorso: Path, etichetta: Optional[str] = None) -> bool:
        if not self._simula('rimozioni', 'rimuoverebbe il file', str(etichetta or percorso)):
            return False
        percorso = Path(percorso)
        _sblocca_se_read_only(percorso)
        percorso.unlink()
        return True

    def rimuovi_albero(self, percorso: Path, etichetta: Optional[str] = None) -> bool:
        if not self._simula('rimozioni', 'rimuoverebbe la cartella', str(etichetta or percorso)):
            return False
        rmtree(str(percorso))
        return True

    def rinomina(self, origine: Path, destinazione: Path, etichetta: Optional[str] = None) -> bool:
        if not self._simula('spostamenti', 'sposterebbe', str(etichetta or f"{origine} -> {destinazione}")):
            return False
        Path(origine).rename(destinazione)
        return True

    def riepilogo(self) -> str:
        c = self.conteggi
        prefisso = 'Prova a vuoto' if self.prova_a_vuoto else 'Operazioni eseguite'
        return (f"{prefisso}: {c['cartelle']} cartelle, {c['copie']} copie, "
                f"{c['rimozioni']} rimozioni, {c['spostamenti']} spostamenti")
