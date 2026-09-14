"""Ancoraggio in locale dei file di un albero gestito da un client cloud a segnaposto.

Perche' serve. Un client di sincronizzazione cloud moderno non tiene i file sul disco: tiene
segnaposto, e scarica il contenuto quando qualcuno lo legge. Se la cartella sorgente di questo
watcher vive dentro un albero cosi', due motori di sincronizzazione governano lo stesso albero:
il client cloud, che disidrata quello che ritiene inutilizzato, e il watcher, che decide per
data di modifica e propaga verso l'altro lato. Il watcher vedrebbe comparire e sparire contenuti
per decisione di un altro programma, e con politica di conflitto sulla data piu' recente
propagherebbe verso la destinazione qualunque cosa il client abbia toccato per ultimo.

L'ancoraggio risolve la contesa dichiarando al sistema che quel sottoalbero deve restare
materializzato. Windows lo esprime con due attributi del Cloud Filter API, `PINNED` e
`UNPINNED`, che il client cloud rispetta.

Perche' non `attrib.exe`. Lo strumento di sistema salta in silenzio ogni percorso che raggiunge
i 260 caratteri, e non lo segnala in alcun modo: su un albero profondo lascia indietro una parte
dei file e dichiara successo. Qui si chiama direttamente `SetFileAttributesW` con il prefisso
`\\\\?\\`, che il limite non ce l'ha, e si verifica il risultato rileggendo gli attributi invece
di fidarsi del codice di uscita.

L'ancoraggio riguarda solo il sottoalbero sorgente e non l'intero albero cloud: su una macchina
condivisa o aziendale la scelta di che cosa scende in locale e' una scelta di riservatezza, e
va dichiarata per la cartella che serve, non in blocco.
"""

import ctypes
import os
from ctypes import wintypes
from pathlib import Path
from typing import Optional

FILE_ATTRIBUTE_PINNED = 0x00080000
FILE_ATTRIBUTE_UNPINNED = 0x00100000
FILE_ATTRIBUTE_OFFLINE = 0x00001000
INVALID_FILE_ATTRIBUTES = 0xFFFFFFFF

try:
    _kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    _kernel32.GetFileAttributesW.argtypes = [wintypes.LPCWSTR]
    _kernel32.GetFileAttributesW.restype = wintypes.DWORD
    _kernel32.SetFileAttributesW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD]
    _kernel32.SetFileAttributesW.restype = wintypes.BOOL
except Exception:  # pragma: no cover - fuori da Windows
    _kernel32 = None


def _lungo(percorso) -> str:
    """Prefissa il percorso per superare il limite dei 260 caratteri.

    La normalizzazione e' puramente lessicale, con `abspath`, e non usa `Path.resolve()`.
    Su un albero a segnaposto `resolve()` e' lavoro inutile e potenzialmente dannoso, perche'
    segue i reparse point e un segnaposto e' un reparse point con richiamo alla lettura; la
    prova sul campo del 2026-09-10 non ha mostrato scaricamenti, quindi la scelta e' una
    precauzione e non la correzione di un difetto osservato. Serve solo un percorso assoluto,
    e `abspath` lo produce senza toccare il filesystem.
    """
    testo = os.path.abspath(str(percorso))
    if testo.startswith('\\\\?\\'):
        return testo
    if testo.startswith('\\\\'):
        return '\\\\?\\UNC\\' + testo[2:]
    return '\\\\?\\' + testo


def leggi_attributi(percorso) -> Optional[int]:
    """Attributi del file secondo `GetFileAttributesW`.

    Limite misurato il 2026-09-10 su un albero Proton reale, da conoscere prima di usare
    questo valore per qualcosa di diverso dall'ancoraggio: attraverso il prefisso `\\\\?\\`
    la funzione non riporta i bit propri del segnaposto, cioe' `OFFLINE`, `REPARSE_POINT` e
    `SPARSE_FILE`, che l'enumerazione della directory riporta invece correttamente. Sullo
    stesso file l'enumerazione dava 5248544 e questa funzione 5242912. I bit `PINNED` e
    `UNPINNED`, che sono quelli su cui l'ancoraggio decide, sono riportati correttamente da
    entrambe. Per giudicare se un file e' materializzato non si usa questa funzione ma
    l'enumerazione della cartella.
    """
    if _kernel32 is None:
        return None
    valore = _kernel32.GetFileAttributesW(_lungo(percorso))
    return None if valore == INVALID_FILE_ATTRIBUTES else valore


def e_ancorato(percorso) -> bool:
    attributi = leggi_attributi(percorso)
    if attributi is None:
        return False
    return bool(attributi & FILE_ATTRIBUTE_PINNED) and not attributi & FILE_ATTRIBUTE_UNPINNED


def e_liberato(percorso) -> bool:
    attributi = leggi_attributi(percorso)
    if attributi is None:
        return False
    return bool(attributi & FILE_ATTRIBUTE_UNPINNED) and not attributi & FILE_ATTRIBUTE_PINNED


def ancora(percorso) -> bool:
    """Marca un singolo elemento come da tenere sempre in locale."""
    attributi = leggi_attributi(percorso)
    if attributi is None:
        return False
    nuovi = (attributi | FILE_ATTRIBUTE_PINNED) & ~FILE_ATTRIBUTE_UNPINNED
    if nuovi == attributi:
        return True
    return bool(_kernel32.SetFileAttributesW(_lungo(percorso), nuovi))


def libera(percorso) -> bool:
    """Marca un singolo elemento come disponibile solo online, simmetrico di `ancora`.

    Imposta `UNPINNED` e toglie `PINNED`, con lo stesso prefisso per i percorsi lunghi e la
    stessa idempotenza di `ancora`: se gli attributi sono gia' quelli attesi non chiama
    `SetFileAttributesW` una seconda volta.
    """
    attributi = leggi_attributi(percorso)
    if attributi is None:
        return False
    nuovi = (attributi | FILE_ATTRIBUTE_UNPINNED) & ~FILE_ATTRIBUTE_PINNED
    if nuovi == attributi:
        return True
    return bool(_kernel32.SetFileAttributesW(_lungo(percorso), nuovi))


def ancora_albero(radice, logger, operazioni=None) -> dict:
    """Ancora ricorsivamente un albero e verifica il risultato rileggendo gli attributi.

    Restituisce un riepilogo con quanti elementi sono stati esaminati, quanti risultano
    ancorati alla fine e quanti restano indietro. Il conteggio finale nasce da una rilettura
    e non dall'esito delle chiamate, perche' un attributo impostato senza errore puo' essere
    stato riscritto dal client cloud subito dopo.
    """
    radice = Path(radice)
    esito = {'esaminati': 0, 'ancorati': 0, 'non_ancorati': 0, 'simulati': 0}

    if _kernel32 is None:
        logger.warning("Ancoraggio non disponibile: API di Windows non raggiungibili")
        return esito

    if not radice.exists():
        logger.error(f"Ancoraggio saltato, radice inesistente: {radice}")
        return esito

    elementi = [radice] + sorted(radice.rglob('*'))
    for elemento in elementi:
        esito['esaminati'] += 1
        if operazioni is not None and operazioni.prova_a_vuoto:
            esito['simulati'] += 1
            continue
        ancora(elemento)

    if esito['simulati']:
        logger.info(f"[PROVA A VUOTO] ancorerebbe in locale {esito['simulati']} elementi sotto {radice}")
        return esito

    for elemento in elementi:
        if e_ancorato(elemento):
            esito['ancorati'] += 1
        else:
            esito['non_ancorati'] += 1

    if esito['non_ancorati']:
        logger.warning(
            f"Ancoraggio incompleto sotto {radice}: {esito['ancorati']} ancorati, "
            f"{esito['non_ancorati']} no. Il client cloud potrebbe disidratarli."
        )
    else:
        logger.info(f"Ancorati in locale {esito['ancorati']} elementi sotto {radice}")
    return esito


def libera_albero(radice, logger, operazioni=None) -> dict:
    """Libera ricorsivamente un albero, simmetrico di `ancora_albero`.

    Serve per restringere il perimetro locale dopo uno spostamento su un client cloud: la
    scelta di cosa scende in locale su una macchina condivisa o aziendale e' di riservatezza,
    quindi tutto cio' che non deve restare materializzato va dichiarato esplicitamente
    `UNPINNED`, non lasciato al criterio del client. La verifica del risultato rilegge gli
    attributi con la stessa cautela di `ancora_albero`: un attributo impostato senza errore
    puo' essere stato riscritto dal client subito dopo, e qui in piu' la disidratazione vera e
    propria e' asincrona, quindi un elemento puo' risultare ancora `PINNED` per un istante dopo
    che l'attributo e' stato tolto.
    """
    radice = Path(radice)
    esito = {'esaminati': 0, 'liberati': 0, 'non_liberati': 0, 'simulati': 0}

    if _kernel32 is None:
        logger.warning("Sblocco non disponibile: API di Windows non raggiungibili")
        return esito

    if not radice.exists():
        logger.error(f"Sblocco saltato, radice inesistente: {radice}")
        return esito

    elementi = [radice] + sorted(radice.rglob('*'))
    for elemento in elementi:
        esito['esaminati'] += 1
        if operazioni is not None and operazioni.prova_a_vuoto:
            esito['simulati'] += 1
            continue
        libera(elemento)

    if esito['simulati']:
        logger.info(f"[PROVA A VUOTO] libererebbe (solo online) {esito['simulati']} elementi sotto {radice}")
        return esito

    for elemento in elementi:
        if e_liberato(elemento):
            esito['liberati'] += 1
        else:
            esito['non_liberati'] += 1

    if esito['non_liberati']:
        logger.warning(
            f"Sblocco incompleto sotto {radice}: {esito['liberati']} liberati, "
            f"{esito['non_liberati']} no. Ripetere dopo che il client ha finito di propagare."
        )
    else:
        logger.info(f"Liberati (solo online) {esito['liberati']} elementi sotto {radice}")
    return esito
