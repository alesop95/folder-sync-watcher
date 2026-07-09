---
generated-from-commit: 2f8d91773b4d07b87f778d46deb821d646046c7c
generated-from-branch: refactor/senior-architecture
generated-date: 2026-07-09
covers-paths:
  - install_service.py
  - setup_task_scheduler.ps1
  - start_watcher.bat
  - config.json
last-verified-commit: 2f8d91773b4d07b87f778d46deb821d646046c7c
---

# Deployment

> Popolare leggendo la configurazione reale di infrastruttura e CI. Commit, push e deploy restano
> operazioni manuali dell'utente.

## Livelli

Non esistono livelli test/staging/produzione in senso convenzionale: è un tool desktop eseguito
sulla macchina dell'utente, senza hosting remoto né CI/CD (nessun file di workflow trovato nel
repository). Esistono due modalità di esecuzione persistente alternative sulla stessa macchina
Windows: come processo interattivo lanciato da `start_watcher.bat` (con relativo avvio automatico
al login via Task Scheduler, `setup_task_scheduler.ps1`), oppure come servizio Windows registrato
da `install_service.py` (`FolderSyncService`, nome `FolderSyncWatcher`).

## Comandi

Avvio interattivo: `start_watcher.bat` crea/aggiorna il virtualenv `venv/`, chiude i processi
Office in background, riconfigura la SUBST, e lancia `python sync_watcher.py --config
config.json`.

Avvio automatico al login: `setup_task_scheduler.ps1` (richiede privilegi di amministratore)
registra un task pianificato che esegue `start_watcher.bat` al login dell'utente corrente, con
restart automatico (3 tentativi, intervallo 5 minuti) se il processo termina.

Servizio Windows: `install_service.py install|start|stop|uninstall|debug` (richiede privilegi di
amministratore per `install`/`uninstall`). `debug` esegue il watcher in primo piano senza
registrarlo come servizio, utile per verificare il comportamento prima dell'installazione.

Gestione SUBST a mano: `python subst_manager.py setup|remove|list|test`, indipendente
dall'avvio del watcher.

## Variabili d'ambiente e segreti

Nessuna variabile d'ambiente richiesta e nessun segreto gestito dal progetto: `config.json`
(tracciato in git) contiene solo percorsi locali e parametri di sincronizzazione, non
credenziali. L'unico prerequisito ambientale non dichiarato in un manifest è la presenza
dell'eseguibile Python nel `PATH`, verificata da `start_watcher.bat` prima di procedere.
