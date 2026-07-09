---
generated-from-commit: 2f8d91773b4d07b87f778d46deb821d646046c7c
generated-from-branch: refactor/senior-architecture
generated-date: 2026-07-09
covers-paths:
  - folder_sync_watcher/**
  - subst_manager.py
  - install_service.py
last-verified-commit: 2f8d91773b4d07b87f778d46deb821d646046c7c
---

# Design e sicurezza applicativa

> Popolare leggendo il codice attuale. I diagrammi referenziati vivono in `diagrams/` in
> corrispondenza uno a uno con i componenti descritti (sezione 7).

## Paradigmi di software design

Produttore-consumatore: `SyncHandler` (produttore, un'istanza per direzione di sincronizzazione)
inserisce tuple di evento su una `queue.Queue` condivisa; un singolo thread demone
(`process_sync_queue`) consuma la coda in serie, così le scritture sul filesystem di destinazione
non avvengono in concorrenza da più thread di eventi.

Observer pattern via `watchdog`: `SyncHandler` estende `FileSystemEventHandler` e viene registrato
su un `Observer` per cartella monitorata; in modalità bidirezionale esistono due observer
indipendenti, uno per direzione, ciascuno con la propria coppia (cartella-sorgente,
cartella-destinazione) passata al costruttore dell'handler.

Separazione per singola responsabilità nel package: `config.py` (caricamento e regole di
esclusione), `hashing.py` (hash di contenuto), `paths.py` (percorsi lunghi, sanificazione nomi,
rilevamento processi Office), `ssd.py` (individuazione unità per etichetta di volume), `subst.py`
(unità virtuali SUBST). `watcher.py` è l'unico modulo che li compone.

Degrado controllato per dipendenze opzionali (vedi `memory/decisions.md` ADR-003): `colorama` e
`win32api` sono importati in `try/except`, con stub che rende no-op la funzionalità invece di
propagare l'eccezione all'import. Lo stesso principio vale per `psutil` in
`FilePathManager.is_office_process_using_file`, che ricade su `is_file_locked` se `psutil` non è
disponibile o solleva eccezione.

Strategia a tentativi progressivi per la copia file (`_safe_copy_file`): copia diretta, poi
percorso corto 8.3, poi tentativo di chiusura handle (`handle.exe`, tool esterno non incluso nel
progetto), poi copia via file temporaneo con `rename` atomico, infine nome sanificato. Ogni
tentativo gestisce eccezioni specifiche (`PermissionError`, `FileNotFoundError`, `OSError` con
messaggio "name too long") con backoff crescente (`3 * (attempt + 1)` secondi su
`PermissionError`).

## Sicurezza applicativa

Il progetto è un tool desktop locale senza superficie di rete: nessuna autenticazione,
autorizzazione o input da rete. Il confine di sicurezza rilevante è locale, tra il processo e il
filesystem/sistema operativo.

`subst.py` invoca il comando di sistema `subst` con `subprocess.run(cmd, shell=True, ...)` dove
`cmd` è costruito per interpolazione di stringa (`f'subst {drive_letter}: "{path}"'`), con
`drive_letter` e `path` provenienti da `config.json` (rispettivamente
`sync_settings.subst_drive_letter` e `folders.google_drive_relative_path` combinato col percorso
fisico dell'SSD). `config.json` è un file locale tracciato in git, non un input remoto o
proveniente dalle cartelle sincronizzate, quindi il rischio di command injection è basso nell'uso
previsto; resta comunque una `shell=True` con interpolazione non sanificata, da non riusare se in
futuro `drive_letter` o `path` diventassero derivabili da input meno fidato.

Lo stesso pattern (`subprocess.run(..., shell=True, ...)` con interpolazione di stringa) ricorre
in `watcher.py:321` per invocare `handle.exe -c {dest.name} -y`, dove `dest.name` è il nome del
file di destinazione così come arriva dagli eventi del filesystem monitorato, prima che
`sanitize_filename` (usata solo come ultima strategia di fallback) venga eventualmente applicata:
un nome file con metacaratteri di shell arriverebbe qui non sanificato. Anche qui il vettore è
locale (nomi di file nelle cartelle sincronizzate dall'utente stesso), non un ingresso di rete.

`subst_manager.py` scrive `config.json` con percorso relativo hardcoded (`open('config.json',
'w', ...)` in `setup_subst_from_config`/`remove_subst_from_config`), indipendentemente dal flag
`--config` che invece `sync_watcher.py` supporta (ADR-005): un'esecuzione con un file di
configurazione diverso da `config.json` lascerebbe `subst_manager.py` a scrivere nel file
sbagliato. Nessuna gestione di segreti: `config.json` non contiene credenziali, solo percorsi
locali e parametri di sincronizzazione.

## Diagrammi

Nessun diagramma prodotto in questa fase di allineamento. Se in seguito si documenta un flusso
(es. lo schema produttore-consumatore o il ciclo di riconnessione SSD), va aggiunto qui e in
`context/diagrams/` con corrispondenza uno a uno secondo la sezione 7 di `PROJECT-SYSTEM.md`.
