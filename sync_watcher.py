#!/usr/bin/env python3
"""
Folder Sync Watcher - Sincronizzazione bidirezionale tra OneDrive e Google Drive
"""

import logging

from colorama import init, Fore
from folder_sync_watcher import FileHasher, FilePathManager, SubstManager, SyncConfig
from folder_sync_watcher.watcher import FolderSyncWatcher, SyncHandler

# Inizializza colorama per l'output colorato e resetta automaticamente lo stile
init(autoreset=True)

def main():
    """Funzione principale"""
    try:
        watcher = FolderSyncWatcher()
        watcher.start()
    except Exception as e:
        print(f"{Fore.RED}Errore fatale: {e}")
        logging.error(f"Errore fatale: {e}", exc_info=True)
        
if __name__ == "__main__":
    main()