---
generated-from-commit: 2f8d91773b4d07b87f778d46deb821d646046c7c
generated-from-branch: refactor/senior-architecture
generated-date: 2026-07-09
covers-paths:
  - folder_sync_watcher/**
  - sync_watcher.py
  - subst_manager.py
  - install_service.py
  - config.json
  - requirements.txt
  - requirements-dev.txt
last-verified-commit: 2f8d91773b4d07b87f778d46deb821d646046c7c
---

# Stack applicativo

> Documento di recupero più importante: tracciato, perché un collega che clona deve vederlo.
> Popolare leggendo il codice attuale, non inventare. Affinare `covers-paths` man mano.

## Stack e runtime

Python 3, nessuna versione minima fissata nei manifest (`requirements.txt`/`requirements-dev.txt`
non dichiarano `python_requires`). Dipendenze di runtime: `watchdog>=4.0.0` (osservazione del
filesystem), `psutil==5.9.5` (rilevamento processi Office che tengono un file aperto),
`colorama==0.4.6` (output colorato in console, opzionale a runtime), `pywin32>=306` (API Windows
per etichette di volume e percorsi corti, opzionale a runtime). Dipendenza di sviluppo:
`pytest>=7.0.0`. Ambiente virtuale gestito da `start_watcher.bat` con `venv/` (creato al primo
avvio, ignorato da git) e un hash di `requirements.txt` salvato in `venv/.requirements.sha256`
per evitare reinstalli inutili. Nessun manifest di packaging (`pyproject.toml`/`setup.py`): il
progetto si esegue da sorgente, non si distribuisce come libreria installabile.

## Alternative deliberatamente escluse

Non risulta dalla storia dei commit alcuna alternativa tecnologica scartata esplicitamente. Da
osservare: il progetto usa `subst` (comando nativo Windows) invece di un link simbolico o di un
mount point per accorciare i percorsi verso Google Drive, scelta implicita nel codice
(`subst.py`) e non commentata nei commit.

## Flussi di codice e ruolo architetturale dei file

`sync_watcher.py` è l'entry point CLI: parsa `--config` (default `config.json`) e istanzia
`FolderSyncWatcher`. `subst_manager.py` è un secondo entry point CLI, indipendente, per
`setup`/`remove`/`list`/`test` dell'unità SUBST. `install_service.py` registra
`FolderSyncWatcher` come servizio Windows (`pywin32`/`win32serviceutil`), con gli stessi comandi
`install`/`uninstall`/`start`/`stop`/`debug`.

Il package `folder_sync_watcher/` contiene la logica core. `config.py` (`SyncConfig`) carica
`config.json` e implementa `is_excluded`, che confronta nome file, percorso completo e substring
contro i pattern di `sync_settings.excluded_patterns` (glob via `fnmatch`, poi substring come
fallback). `hashing.py` (`FileHasher`) calcola l'hash MD5 di un file per la modalità di risoluzione
conflitti `"hash"`. `paths.py` (`FilePathManager`) gestisce percorsi lunghi (percorsi corti 8.3
via `win32api.GetShortPathName`), sanificazione nomi file, e rilevamento di un processo Office che
tiene un file aperto (`psutil`, controllo `open_files` di `WINWORD.EXE`/`EXCEL.EXE`/
`POWERPNT.EXE`). `ssd.py` trova la lettera di unità di un SSD esterno per etichetta di volume
tramite `win32api.GetLogicalDriveStrings`/`GetVolumeInformation`. `subst.py` (`SubstManager`)
crea/rimuove/elenca unità virtuali SUBST invocando il comando `subst` via `subprocess`.

`watcher.py` è il modulo più grande (511 righe) e contiene `SyncHandler`
(`watchdog.events.FileSystemEventHandler`), che traduce gli eventi del filesystem
(`created`/`modified`/`deleted`/`moved`) in voci su una `Queue` filtrate da `is_excluded`, e
`FolderSyncWatcher`, che orchestra il ciclo di vita: risolve il percorso Google Drive (SUBST se
configurato, altrimenti ricerca dell'SSD per etichetta), esegue una sincronizzazione iniziale
ricorsiva bidirezionale (`initial_sync`/`_sync_folders`), avvia due `watchdog.Observer` (uno per
direzione se `bidirectional`) e un thread che consuma la coda (`process_sync_queue`). La copia di
un file (`_safe_copy_file`) è un ciclo di tentativi con strategie progressive per file bloccati o
percorsi lunghi: copia diretta, percorsi corti, tentativo di chiudere handle (`handle.exe`), copia
tramite file temporaneo con rename atomico, infine nome sanificato come ultima risorsa. I file
Office attivano un ritardo configurabile (`office_file_delay`) e un controllo esplicito che il
file non sia aperto in un processo Office prima di copiarlo.

`FolderSyncWatcher.start()` contiene anche il loop di sorveglianza della connessione SSD: se
`check_ssd_connected` è vero e l'SSD si disconnette, ferma gli observer, attende la riconnessione
in polling ogni 5 secondi, poi rilancia una sincronizzazione iniziale e riavvia gli observer.

## Riferimenti a snippet

`folder_sync_watcher/watcher.py:62` `FolderSyncWatcher` — orchestratore principale.
`folder_sync_watcher/watcher.py:292` `_safe_copy_file` — copia con retry progressivi.
`folder_sync_watcher/config.py:18` `SyncConfig.is_excluded` — logica di esclusione pattern.
`folder_sync_watcher/subst.py:4` `SubstManager` — gestione unità virtuali SUBST.
`folder_sync_watcher/ssd.py:9` `find_ssd_drive_letter` — ricerca SSD per etichetta di volume.
`config.json` — unica fonte di configurazione a runtime, percorso parametrizzabile da `--config`.
