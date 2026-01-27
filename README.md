# Folder Sync Watcher

Sistema di sincronizzazione bidirezionale automatica tra OneDrive aziendale e Google Drive personale per Windows 11 per allineamento materiale specifico.

## Funzionalità Principali

Sincronizzazione bidirezionale in tempo reale tra due cartelle con monitoraggio automatico dei cambiamenti (creazione, modifica, eliminazione, spostamento).
Include rilevamento automatico della connessione/disconnessione di un SSD esterno a sua volta sincronizzato con Google Drive (con l'app Google Drive dentro Windows 11 alle cui cartelle si può accedere con esplora risorse) e gestione intelligente dei conflitti (basata su file più recente, più grande o hash).
Il sistema include un logging completo con rotazione automatica e supporta l'esclusione di pattern personalizzabili per file temporanei e cartelle.

## rerequisiti

- Windows 11
- Python >3.8
- Accesso alle cartelle OneDrive e Google Drive

## Quick setup

### Opzione 1: Avvio Manuale

1. Lanciare `start_watcher.bat`
   - Lo script installerà automaticamente le dipendenze al primo avvio
   - Il watcher inizierà a monitorare le cartelle

### Opzione 2: Avvio Automatico con Task Scheduler (Consigliato)

1. Lanciare `setup_task_scheduler.ps1` ed eseguirlo con PowerShell
2. Se richiesto, conferma i privilegi di amministratore
3. Il watcher si avvierà automaticamente ad ogni login

### Opzione 3: Installazione come Servizio Windows

1. Aprire il prompt dei comandi come amministratore
2. Navigare alla cartella del progetto:
   ```cmd
   cd "ONEDRIVE PATH HERE"
   ```
3. Installare le dipendenze:
   ```cmd
   pip install -r requirements.txt
   ```
4. Installare il servizio:
   ```cmd
   python install_service.py install
   ```
5. Avviare il servizio:
   ```cmd
   python install_service.py start
   ```

## Configurazione

Modificare il file `config.json` per personalizzare il comportamento. Ecco una spiegazione delle impostazioni principali:

- `onedrive`: percorso della cartella OneDrive da sincronizzare
- `google_drive_relative_path`: percorso relativo della cartella Google Drive
- `bidirectional`: abilitare/disabilitare la sincronizzazione bidirezionale
- `sync_interval_seconds`: intervallo di sincronizzazione in secondi
- `conflict_resolution`: strategia per la risoluzione dei conflitti ('newest', 'largest', 'hash')
- `excluded_patterns`: pattern di file e cartelle da escludere dalla sincronizzazione (inclusi file temporanei, cartelle di sistema, e le cartelle 'folder-sync-watcher' e 'venv')
- `check_ssd_connected`: controllare se l'SSD è connesso
- `ssd_volume_label`: Etichetta del volume SSD da controllare

```json
{
    "folders": {
        "onedrive": "ONEDRIVE PATH HERE",
        "google_drive_relative_path": "googleDrive_sync\\Portfolio and ongoing studies\\Ongoing studies\\Cybersec, Business continuity, Disaster recovery, Normative IT, DevOps, Programming, Networking\\CYBERSECURITY, Business continuity, Disaster recovery, Normative IT"
    },
    "sync_settings": {
        "bidirectional": true,
        "sync_interval_seconds": 5,
        "conflict_resolution": "newest",
        "excluded_patterns": [
            "~$*",
            ".tmp",
            ".~lock.*#",
            "desktop.ini",
            "Thumbs.db"
        ],
        "check_ssd_connected": true,
        "ssd_volume_label": "T7"
    },
    "logging": {
        "level": "INFO",
        "log_file": "sync_watcher.log",
        "retention_days": 30,
        "backup_count": 30
    }
}
```

## Utilizzo di SUBST per Creare un'Unità Virtuale

### Panoramica
Il comando `subst` di Windows permette di associare una lettera di unità a una cartella locale, creando un'unità virtuale. Questo può essere utile per semplificare i percorsi lunghi o creare percorsi più gestibili perchè a volte in Windows crea problema questa cosa.
Fondamentalmente viene creato un path virtuale accorciato utile allo scopo che il sistema operativo riconosce come fosse una periferica aggiuntiva connessa. 

Inoltre, l'utilizzo di unità virtuali con SUBST offre diversi vantaggi: percorsi più brevi che facilitano la lettura dei log e la risoluzione dei problemi, riduzione degli errori legati a caratteri speciali o spazi nei percorsi, e maggiore flessibilità nel modificare i percorsi fisici senza dover aggiornare la configurazione del watcher.

Assumendo che l’etichetta reale sia "T7" per un sistema robusto Windows può cambiare la lettera dell’unità, ma l’etichetta non cambia a meno che tu non la si rinomini manualmente.
Con una configurazione del genere lo script scansiona tutte le unità montate (A:, B:, C: … Z:) e per ciascuna interroga l’etichetta del volume. Se trova un drive con etichetta "T7", costruisce il percorso: <Lettera>: + percorso_relativo_configurato e avvia il watcher sulla cartella individuata. Se l’SSD viene scollegato, smette di sincronizzare mentre se viene ricollegato con qualsiasi lettera, lo ritroverà automaticamente.
Questo comportamento è tecnicamente solido perché basato sul volume label, che Windows assegna anche a dispositivi che cambiano porta.

### Come Utilizzare SUBST

#### Creare un'Unità Virtuale
```powershell
# Sostituire X: con la lettera di unità desiderata e il percorso con il percorso completo della cartella
subst X: "FULL PATH TO FOLDER"
```

#### Esempio Pratico
Per mappare la cartella di Google Drive a un'unità virtuale:
```powershell
subst A: "J:\\googleDrive_sync\\Portfolio and ongoing studies\\Ongoing studies\\Cybersec, Business continuity, Disaster recovery, Normative IT, DevOps, Programming, Networking\\CYBERSECURITY, Business continuity, Disaster recovery, Normative IT"
```

**Perché "A:"?**
E' una lettera storicamente riservata per floppy disk e ora inutilizzata e si vede subito come unità virtuale/speciale/dedicata. Non confligge mai con USB, CD/DVD o unità di rete e alfabeticametne è la prima e più facile da trovare in esplora risorse.

#### Rendere l'Associazione Permanente (Opzionale)
Le associazioni create con `subst` vengono perse al riavvio. Per renderle permanenti:

1. Bisogna creare un file batch (es. `startup_drives.bat`) con il comando `subst`
2. Aggiungere il file al percorso di avvio di Windows:
   - Premere `Win + R`, digitare `shell:startup`
   - Incollare il file batch in questa cartella

#### Rimuovere un'Unità Virtuale
```powershell
# Sostituire X: con la lettera di unità da rimuovere
subst X: /D
```

### Configurazione Consigliata
Per abilitare SUBST, aggiorna il file `config.json`:
```json
{
    "sync_settings": {
        "use_subst": true,
        "subst_drive_letter": "A",
        "sanitize_filenames": true,
        "office_file_delay": 5
    }
}
```

### Gestione Automatica con Script
Usare lo script `subst_manager.py` per gestire SUBST facilmente:
```cmd
# Configurare SUBST automaticamente
python subst_manager.py setup

# Listare unità SUBST attive
python subst_manager.py list

# Testare accesso ai file problematici
python subst_manager.py test

# Rimuovere SUBST
python subst_manager.py remove
```

### Note

Le unità virtuali create con SUBST sono visibili solo all'utente che le ha create e non sono disponibili finché non viene eseguito lo script di avvio. Inoltre, potrebbero non essere accessibili ai servizi di sistema che girano con credenziali diverse.

## Monitoraggio

### Log Files

I log sono salvati nella cartella `logs/`:
- `sync_watcher.log`: log principale
- Rotazione automatica giornaliera
- Mantiene gli ultimi 30 giorni di log

### Visualizzare i Log in Tempo Reale

```powershell
Get-Content "logs\sync_watcher.log" -Wait -Tail 30
```

## Gestione del Servizio

### Comandi Disponibili

```cmd
# Avvio manuale (modalità console)
python sync_watcher.py --config config.json

# Gestione servizio Windows
python install_service.py install    # Installare il servizio
python install_service.py uninstall  # Disinstallare il servizio
python install_service.py start      # Avviare il servizio
python install_service.py stop       # Arrestare il servizio
python install_service.py debug      # Modalità debug
```

### Gestione Task Scheduler

Per rimuovere l'avvio automatico:
1. Aprire **Task Scheduler** (taskschd.msc)
2. Trovare il task **"FolderSyncWatcher"**
3. Eliminarlo cliccando con tasto destro → **Elimina**

## Troubleshooting

### Il watcher non si avvia

1. **Verifica versione Python installata**: Assicurarsi che Python sia installato e nel PATH
   ```cmd
   python --version
   ```

2. **Verifica dipendenze**: Reinstallare le dipendenze
   ```cmd
   pip install -r requirements.txt --force-reinstall
   ```

3. **Controllo dei permessi**: Assicurarsi di avere accesso in lettura/scrittura a entrambe le cartelle

### L'SSD non viene rilevato

1. Verificare che `ssd_volume_label` in `config.json` corrisponda all'etichetta del volume (non alla lettera)
2. Disabilitare temporaneamente il controllo SSD:
   ```json
   "check_ssd_connected": false
   ```

### File non sincronizzati

1. Controllare i pattern di esclusione in `config.json`
2. Verificare i log per eventuali errori
3. Assicurarsi che i file non siano aperti in altri programmi

### Problemi con File Office (.docx, .xlsx, .pptx)

Può accadere che ci siano problemi con file Office che non possono essere aperti, copiati o rinominati:

1. **Abilitare la sanitizzazione dei nomi file**:
   ```json
   "sanitize_filenames": true
   ```

2. **Aumentare il ritardo per file Office**:
   ```json
   "office_file_delay": 10
   ```
3. **Testa l'accesso al file problematico**:
   ```cmd
   python subst_manager.py test
   ```

4. **Verificare se il file è bloccato da Google Drive**:
   - Chiudere Google Drive File Stream
   - Riavviare Google Drive File Stream
   - Provare ad accedere al file tramite browser web

### Percorsi Troppo Lunghi

Per risolvere errori di percorsi troppo lunghi:
1. Abilita SUBST per accorciare i percorsi come scritto sopra
2. Abilita la sanitizzazione dei nomi file
3. Considera di riorganizzare la struttura delle cartelle

## Struttura del Progetto

```
folder-sync-watcher/
│
├── sync_watcher.py           # Script principale del watcher
├── install_service.py        # Gestione servizio Windows
├── subst_manager.py          # Utility per gestione SUBST
├── start_watcher.bat         # Avvio rapido
├── setup_task_scheduler.ps1  # Configurazione avvio automatico
├── config.json               # Configurazione
├── requirements.txt          # Dipendenze Python
├── requirements-dev.txt      # Dipendenze dev (test)
├── README.md                # Documentazione
│
├── folder_sync_watcher/      # Package core (logica di sincronizzazione e utility)
│   ├── __init__.py
│   ├── watcher.py
│   ├── config.py
│   ├── hashing.py
│   ├── paths.py
│   ├── ssd.py
│   └── subst.py
│
├── tests/                    # Test minimi pytest (funzioni pure/invarianti)
│   ├── test_config.py
│   ├── test_hashing.py
│   └── test_paths.py
│
└── logs/                   # Directory dei log (creata automaticamente)
    └── sync_watcher.log
```

## Architettura del codice e razionale tecnico

Il progetto è organizzato per separare la logica core dall’avvio operativo. Il package `folder_sync_watcher/` contiene la logica riusabile di sincronizzazione e le utility, mentre gli entry point rimangono file top-level per garantire compatibilità con l’uso quotidiano e con i meccanismi di deploy su Windows (avvio manuale, Task Scheduler, servizio).

L’approccio è orientato alla robustezza operativa su Windows. Sono gestiti esplicitamente casi frequenti come file temporaneamente bloccati (in particolare Office), percorsi molto lunghi, caratteri non graditi in alcuni contesti e disconnessione di dischi esterni. La scelta di mantenere una configurazione esterna `config.json` evita hardcoding di path e riduce la complessità di rollout su macchine diverse.

## Feature principali e ratio

La sincronizzazione bidirezionale in tempo reale è la feature centrale: consente di lavorare sia sul lato OneDrive sia sul lato Google Drive mantenendo coerenza. Quando necessario può essere resa unidirezionale tramite `bidirectional` per ridurre il rischio di propagare cancellazioni o modifiche indesiderate.

Esempio nel core (`folder_sync_watcher/watcher.py`) di sincronizzazione iniziale che rispetta `bidirectional`:

```python
bidirectional = self.config.get('sync_settings', {}).get('bidirectional', True)
self._sync_folders(self.onedrive_folder, self.google_drive_folder)
if bidirectional:
    self._sync_folders(self.google_drive_folder, self.onedrive_folder)
```

La gestione dei conflitti è configurabile. La strategia `newest` privilegia il file più recente, la strategia `largest` è un fallback pragmatico quando i timestamp non sono affidabili, la strategia `hash` confronta il contenuto e riduce falsi positivi, a costo di maggiore lavoro I/O.

Esempio (`folder_sync_watcher/watcher.py`) della funzione decisionale `_should_copy_file` in base a `conflict_resolution`:

```python
conflict_resolution = self.config['sync_settings']['conflict_resolution']
if conflict_resolution == 'newest':
    return source.stat().st_mtime > dest.stat().st_mtime
if conflict_resolution == 'largest':
    return source.stat().st_size > dest.stat().st_size
if conflict_resolution == 'hash':
    return FileHasher.get_file_hash(str(source)) != FileHasher.get_file_hash(str(dest))
return False
```

Il rilevamento dell’SSD tramite `ssd_volume_label` esiste per compensare il fatto che Windows può cambiare lettera di unità. L’etichetta è un riferimento più stabile e riduce interventi manuali.

Esempio (`folder_sync_watcher/ssd.py`) del rilevamento per volume label:

```python
def find_ssd_drive_letter(volume_label: str) -> Optional[str]:
    if win32api is None:
        return None
    drives = win32api.GetLogicalDriveStrings().split('\000')[:-1]
    for drive in drives:
        try:
            current_label = win32api.GetVolumeInformation(drive)[0].strip()
            if current_label.lower() == volume_label.lower().strip():
                return drive.rstrip('\\')
        except Exception:
            continue
    return None
```

L’uso di SUBST riduce lunghezza e complessità dei path, con impatto diretto su errori di percorso troppo lungo e su leggibilità dei log. È gestito tramite `subst_manager.py` e tramite `use_subst`/`subst_drive_letter` in configurazione.

Esempio (`folder_sync_watcher/watcher.py`) di utilizzo di SUBST se già presente, altrimenti setup:

```python
if sync_settings.get('use_subst', False):
    subst_letter = sync_settings.get('subst_drive_letter', 'A').upper()
    existing_drives = SubstManager.list_subst_drives()
    if subst_letter in existing_drives:
        self.google_drive_folder = f"{subst_letter}:\\"
        return True
    elif self._setup_subst_drive(subst_letter):
        self.google_drive_folder = f"{subst_letter}:\\"
        return True
```

Il logging con rotazione automatica abilita troubleshooting e audit in modo sostenibile nel tempo, evitando crescita indefinita del file di log.

Esempio (`folder_sync_watcher/watcher.py`) di logging con `TimedRotatingFileHandler`:

```python
file_handler = TimedRotatingFileHandler(
    log_dir / log_config['log_file'],
    when='D',
    interval=1,
    backupCount=log_config.get('retention_days', 30),
    encoding='utf-8',
)
self.logger = logging.getLogger('FolderSyncWatcher')
if not self.logger.handlers:
    self.logger.addHandler(file_handler)
```

Il bootstrap con `start_watcher.bat` è idempotente: crea il `venv` solo se assente e installa dipendenze solo se `requirements.txt` è cambiato. Questo riduce tempi di avvio e variabilità, mantenendo comunque un setup ripetibile.

Esempio (`start_watcher.bat`) di installazione dipendenze solo se necessario (hash SHA256 di `requirements.txt`):

```bat
set "REQ_FILE=requirements.txt"
set "REQ_HASH_FILE=venv\.requirements.sha256"
for /f "tokens=1" %%H in ('certutil -hashfile "%REQ_FILE%" SHA256 ^| findstr /r /c:"^[0-9A-F][0-9A-F]"') do (
    set "REQ_HASH=%%H"
    goto :gotReqHash
)
:gotReqHash

if not exist "%REQ_HASH_FILE%" set "NEED_INSTALL=1"
if exist "%REQ_HASH_FILE%" (
    set /p "OLD_HASH="<"%REQ_HASH_FILE%"
    if /I not "%OLD_HASH%"=="%REQ_HASH%" set "NEED_INSTALL=1"
)

if "%NEED_INSTALL%"=="1" (
    python -m pip install -r "%REQ_FILE%"
    echo %REQ_HASH%>"%REQ_HASH_FILE%"
)
```

L’esclusione di file e cartelle tramite `excluded_patterns` evita loop su file temporanei e riduce rumore operativo.

Esempio (`folder_sync_watcher/config.py`) di esclusione tramite glob e fallback su substring:

```python
patterns = self.config.get('sync_settings', {}).get('excluded_patterns', [])
for pattern in patterns:
    if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(path_str, pattern):
        return True
    if pattern and pattern in path_str:
        return True
return False
```

La gestione dei file Office riduce errori tipici di sincronizzazione durante il salvataggio, introducendo un ritardo configurabile e un check best-effort di lock/uso processo.

Esempio (`folder_sync_watcher/watcher.py`) di `office_file_delay` e requeue in caso di file ancora in uso:

```python
if is_office_file:
    office_delay = self.config['sync_settings'].get('office_file_delay', 5)
    time.sleep(office_delay)

    if FilePathManager.is_office_process_using_file(str(src)):
        self.sync_queue.put(('modify', str(src), source_folder, dest_folder))
        return
```

La copia robusta applica tentativi multipli e fallback progressivi (incluso path corto 8.3) per aumentare la probabilità di completamento.

Esempio (`folder_sync_watcher/watcher.py`) di retry e fallback su short path:

```python
max_attempts = 5 if is_office_file else 3
for attempt in range(max_attempts):
    try:
        if attempt == 0:
            copy2(str(src), str(dest))
            return
        if attempt == 1 and len(str(src)) > 200:
            src_short = FilePathManager.get_short_path(str(src))
            dest_short = FilePathManager.get_short_path(str(dest.parent)) + "\\" + dest.name
            copy2(src_short, dest_short)
            return
    except PermissionError:
        time.sleep(3 * (attempt + 1))
```

L’avvio in console supporta `--config` per puntare a una configurazione diversa senza modificare codice.

Esempio (`sync_watcher.py`) di parsing `--config`:

```python
parser = argparse.ArgumentParser(add_help=True)
parser.add_argument('--config', default='config.json')
args = parser.parse_args(argv)
watcher = FolderSyncWatcher(config_path=args.config)
```

La modalità servizio Windows usa `pywin32` e implementa il contratto di `ServiceFramework`, delegando ciclo di vita a `FolderSyncWatcher`.

Esempio (`install_service.py`) di stop e start del watcher in un servizio:

```python
class FolderSyncService(win32serviceutil.ServiceFramework):
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        if self.watcher:
            self.watcher.stop()

    def main(self):
        from folder_sync_watcher import FolderSyncWatcher
        self.watcher = FolderSyncWatcher()
        self.watcher.start()
```

## Spiegazione didattica OOP (Python) applicata a questo progetto

Il progetto usa un approccio a oggetti per modellare uno scenario operativo: esiste un oggetto che rappresenta il “servizio” di sincronizzazione, con stato, configurazione, thread e observer. Questo è il ruolo della classe `FolderSyncWatcher`, che incapsula il ciclo di vita del watcher e riduce l’uso di variabili globali.

La separazione delle responsabilità è ottenuta decomponendo il problema in classi e moduli. `SyncHandler` si occupa di tradurre eventi filesystem in comandi da eseguire; `SyncConfig` gestisce caricamento e interpretazione della configurazione; utility come `FileHasher`, `FilePathManager` e `SubstManager` isolano operazioni atomiche e riusabili. In termini OOP questo significa privilegiare composizione e responsabilità chiare, riducendo accoppiamenti e semplificando manutenzione.

## Descrizione file-per-file (Python)

### sync_watcher.py

È l’entry point principale in modalità console. Implementa una CLI minimale con `--config` e avvia `FolderSyncWatcher`. Importa le classi principali dal package per mantenere compatibilità e rendere l’avvio operativo semplice.

### folder_sync_watcher/watcher.py

Contiene la logica runtime. `SyncHandler` eredita da `watchdog.events.FileSystemEventHandler` e converte gli eventi in messaggi su una coda. `FolderSyncWatcher` gestisce configurazione, logging, sincronizzazione iniziale, avvio observer e processing asincrono della coda, includendo gestione disconnessione SSD e stop controllato.

Esempio (`folder_sync_watcher/watcher.py`) di arresto controllato con sentinella `_stop` in coda:

```python
self.running = False
try:
    self.sync_queue.put(('_stop',), timeout=1)
except Exception:
    pass
```

### folder_sync_watcher/config.py

Contiene `SyncConfig` che carica `config.json` e applica le regole di esclusione. L’esclusione viene applicata sia sul nome file sia sul percorso, con supporto a pattern in stile glob.

### folder_sync_watcher/hashing.py

Contiene `FileHasher` che calcola l’hash MD5, usato per la strategia di conflitto `hash`.

### folder_sync_watcher/paths.py

Contiene `FilePathManager`, che gestisce problemi tipici Windows: sanitizzazione nome file, path corto 8.3, verifica lock e rilevamento (best-effort) di processi Office che stanno usando un file.

### folder_sync_watcher/ssd.py

Espone `find_ssd_drive_letter` basata su volume label. Se `pywin32` non è disponibile, la funzione ritorna `None` e il sistema può proseguire con altre strategie.

### folder_sync_watcher/subst.py

Contiene `SubstManager`, wrapper del comando Windows `subst`, con funzioni create/remove/list e normalizzazione della lettera.

### install_service.py

Gestisce installazione e lifecycle come servizio Windows tramite `pywin32`. Definisce una classe servizio e fornisce comandi CLI per install/start/stop/uninstall e una modalità debug.

### subst_manager.py

Utility operativa per gestire SUBST e fare un test di accesso a file “problematici”. Usa `config.json` come fonte di verità e normalizza la lettera di unità.

## Test minimi (pytest)

La cartella `tests/` contiene test automatici su funzioni pure e invarianti, con dipendenze separate in `requirements-dev.txt`. L’obiettivo è avere una baseline di regressione su hashing, sanitizzazione dei nomi e logica di esclusione.

Esempio di installazione dipendenze dev ed esecuzione test:

```cmd
pip install -r requirements-dev.txt
pytest
```

Esempio (`tests/test_hashing.py`) di test su stabilità dell’hash:

```python
h1 = FileHasher.get_file_hash(str(p))
h2 = FileHasher.get_file_hash(str(p))
assert h1
assert h1 == h2
```

## Nota su import e dipendenze opzionali

Alcuni moduli sono progettati per non fallire immediatamente in import quando l’ambiente non è ancora completamente provisionato, così da facilitare tooling e test. Esempio (`folder_sync_watcher/__init__.py`) di export lazy dei simboli runtime:

```python
def __getattr__(name: str):
    if name in {"FolderSyncWatcher", "SyncHandler"}:
        from .watcher import FolderSyncWatcher, SyncHandler
        return {"FolderSyncWatcher": FolderSyncWatcher, "SyncHandler": SyncHandler}[name]
    raise AttributeError(name)
```

## Sicurezza

- I file esclusi dai pattern non vengono mai sincronizzati
- Il watcher stesso (`folder-sync-watcher`) è automaticamente escluso dalla sincronizzazione
- I log non contengono contenuti dei file, solo metadati
- Nessun dato viene inviato a servizi esterni

## Note Importanti

1. **Prima Sincronizzazione**: al primo avvio, il watcher esegue una sincronizzazione completa che potrebbe richiedere tempo
2. **Conflitti**: in caso di modifiche simultanee, viene applicata la strategia definita in `config.json`
3. **Performance**: Per cartelle molto grandi (>10.000 file), bisogna aumentare la variabile `sync_interval_seconds`

## Supporto

Per problemi o domande:
1. Controlla i log in `logs/sync_watcher.log`
2. Verifica la configurazione in `config.json`
3. Esegui in modalità debug: `python install_service.py debug`

## Licenza

Questo progetto è rilasciato sotto licenza MIT. Consulta il file `LICENSE` per i dettagli.

Copyright (c) 2026 Alessio Sopranzi

---

**Versione**: 1.0.0  
**Ultimo aggiornamento**: Dicembre 2025
