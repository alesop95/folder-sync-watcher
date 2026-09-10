"""Risoluzione della radice sorgente da sincronizzare.

Fino al 2026-09-10 la sorgente era per costruzione l'SSD esterno: la sua lettera si trovava
cercando l'etichetta di volume dichiarata in `sync_settings.ssd_volume_label`, e il percorso
completo era quella lettera piu' `folders.google_drive_relative_path`. L'assunzione implicita
era che la radice fosse sempre un'unita' rimovibile identificabile per etichetta.

Con lo spostamento dell'archivio su un client di sincronizzazione cloud quell'assunzione cade:
la radice diventa una cartella locale dentro il profilo utente, che non ha alcuna etichetta di
volume da cercare. Questo modulo introduce quindi una base esplicita, `folders.source_base`, e
conserva la ricerca per etichetta come comportamento predefinito quando quella chiave manca,
cosi' che le configurazioni esistenti continuino a funzionare senza modifiche.

Il modulo corregge anche un difetto latente del codice che sostituisce: `Path('J:') / rel`
non produce un percorso assoluto ma `J:rel`, che Windows risolve rispetto alla directory
corrente di quell'unita'. La normalizzazione della radice avviene qui una volta sola, invece
che in ognuno dei punti che costruivano il percorso per conto proprio.
"""

from pathlib import Path
from typing import Optional

from .ssd import find_ssd_drive_letter


def _normalizza_radice(radice: str) -> str:
    """Rende assoluta una radice espressa come sola lettera di unita'."""
    radice = str(radice).rstrip('/\\')
    if len(radice) == 2 and radice[1] == ':':
        return radice + '\\'
    return radice


def usa_base_esplicita(config: dict) -> bool:
    """Vero se la configurazione dichiara una base invece di cercarla per etichetta."""
    return bool(config.get('folders', {}).get('source_base'))


def percorso_relativo(config: dict) -> str:
    """Percorso relativo della cartella sorgente rispetto alla radice.

    Accetta il nome nuovo `source_relative_path` e ripiega su quello storico
    `google_drive_relative_path`, che resta valido per le configurazioni esistenti.
    """
    folders = config.get('folders', {})
    return folders.get('source_relative_path') or folders.get('google_drive_relative_path', '')


def risolvi_radice(config: dict) -> Optional[str]:
    """Radice della sorgente, dalla base esplicita o dall'etichetta di volume."""
    base = config.get('folders', {}).get('source_base')
    if base:
        return _normalizza_radice(base)

    settings = config.get('sync_settings', {})
    if not settings.get('check_ssd_connected', True):
        return None

    lettera = find_ssd_drive_letter(settings.get('ssd_volume_label', ''))
    return _normalizza_radice(lettera) if lettera else None


def risolvi_percorso(config: dict) -> Optional[str]:
    """Percorso completo della cartella sorgente, o None se la radice non e' disponibile."""
    radice = risolvi_radice(config)
    if not radice:
        return None
    relativo = percorso_relativo(config)
    if not relativo:
        return radice
    return str(Path(radice) / relativo)


def descrizione_attesa(config: dict) -> str:
    """Testo da mostrare mentre si aspetta che la sorgente diventi disponibile."""
    if usa_base_esplicita(config):
        return "cartella sorgente '{}'".format(config['folders']['source_base'])
    etichetta = config.get('sync_settings', {}).get('ssd_volume_label', '')
    return "SSD con etichetta '{}'".format(etichetta)
