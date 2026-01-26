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
        "google_drive_relative_path": "googleDrive_sync\\Portfolio and ongoing studies\\🛠️ Ongoing studies\\Cybersec, Business continuity, Disaster recovery, Normative IT, DevOps, Programming, Networking\\CYBERSECURITY, Business continuity, Disaster recovery, Normative IT"
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
subst A: "J:\\googleDrive_sync\\Portfolio and ongoing studies\\🛠️ Ongoing studies\\Cybersec, Business continuity, Disaster recovery, Normative IT, DevOps, Programming, Networking\\CYBERSECURITY, Business continuity, Disaster recovery, Normative IT"
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
python sync_watcher.py

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

1. Verificare che la lettera dell'unità in `config.json` sia corretta
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
├── README.md                # Documentazione
│
└── logs/                   # Directory dei log (creata automaticamente)
    └── sync_watcher.log
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

## 📄 Licenza

Non protetto attualmente da licenza.

---

**Versione**: 1.0.0  
**Ultimo aggiornamento**: Dicembre 2025
