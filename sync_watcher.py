#!/usr/bin/env python3
"""
Folder Sync Watcher - Sincronizzazione bidirezionale tra OneDrive e Google Drive
"""

import argparse
import logging
from typing import List, Optional

try:
    from colorama import init, Fore
except Exception:  # pragma: no cover
    class _Fore:
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""

    Fore = _Fore()

    def init(*_args, **_kwargs):
        return None

from folder_sync_watcher import FileHasher, FilePathManager, SubstManager, SyncConfig
from folder_sync_watcher.watcher import FolderSyncWatcher, SyncHandler

# Inizializza colorama per l'output colorato e resetta automaticamente lo stile
init(autoreset=True)

def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('--config', default='config.json')
    parser.add_argument(
        '--prova-a-vuoto',
        dest='prova_a_vuoto',
        action='store_true',
        default=None,
        help="Non scrive nulla: registra le operazioni che eseguirebbe e le conta. "
             "Ha la precedenza su sync_settings.dry_run del file di configurazione.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None):
    """Funzione principale"""
    args = _parse_args(argv)
    try:
        watcher = FolderSyncWatcher(config_path=args.config, prova_a_vuoto=args.prova_a_vuoto)
        watcher.start()
    except Exception as e:
        print(f"{Fore.RED}Errore fatale: {e}")
        logging.error(f"Errore fatale: {e}", exc_info=True)
        
if __name__ == "__main__":
    main()