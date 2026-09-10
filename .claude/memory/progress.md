# Work-log

> Append-only, in ordine cronologico inverso (la voce più recente in alto). Ogni passo
> significativo di codice e ogni intervento manuale rilevante lascia una voce con data, file
> toccati, motivo e commit di riferimento. Le voci precedenti al 2026-07-09 sono ricostruite dalla
> storia dei commit in fase di allineamento, senza inventare dettagli che il commit non dimostra.

## 2026-09-10 - Radice della sorgente dichiarabile in configurazione

Commit di riferimento: working tree non ancora commitato
File toccati: `folder_sync_watcher/source.py` (nuovo), `folder_sync_watcher/watcher.py`,
`subst_manager.py`, `tests/test_source.py` (nuovo), `README.md`

Modifica richiesta dalla Fase 7 del progetto `my-cv`, che sposta su Proton Drive l'archivio di studio di cui questo watcher sorveglia una sottocartella. La sorgente smette di essere l'SSD `T7` e diventa una cartella locale del client Proton, che non ha etichetta di volume: senza questa modifica non esisteva modo di dichiararla.

Cosa cambia nel codice. Nasce `folder_sync_watcher/source.py`, che risolve radice e percorso completo della sorgente e che accetta la chiave nuova `folders.source_base`. I quattro punti che prima componevano il percorso da soli, `update_gdrive_path` e `_setup_subst_drive` in `watcher.py` e le due funzioni di `subst_manager.py`, ora chiamano lui. Il metodo `FolderSyncWatcher.find_ssd_drive_letter` conserva il nome storico ma delega, così i chiamanti esterni non si rompono. La decisione e le opzioni scartate stanno in ADR-006.

Difetto latente trovato e corretto strada facendo, che è il guadagno inatteso di questa modifica: `Path('J:') / relativo` restituisce `J:relativo`, cioè un percorso relativo alla directory corrente di quell'unità e non un percorso assoluto, e il codice lo faceva in tutti e quattro i punti. Ha un test di regressione dedicato in `tests/test_source.py`.

Retrocompatibilità verificata e non assunta: caricando il `config.json` reale di questa macchina, senza toccarlo, la radice si risolve a `J:\` e il percorso completo esiste su disco. La configurazione non è stata modificata, perché il ripuntamento alla cartella Proton è un passo separato che si fa quando quella cartella esisterà davvero.

Test: otto casi nuovi in `tests/test_source.py` coprono base esplicita contro etichetta, precedenza fra i due nomi del percorso relativo, normalizzazione della lettera nuda e sorgente assente. La suite passa a quindici test.

Cosa resta aperto, in ordine. Il ripuntamento della configurazione, che richiede la cartella di destinazione già popolata. Il primo avvio dopo il ripuntamento, che va provato su una coppia di cartelle finte perché questo programma non ha alcuna modalità di prova a vuoto e la prima esecuzione è già una scrittura reale su una cartella specchiata con l'azienda. Il pin dei file cloud in locale, che la Fase 7 di `my-cv` assegna a questo programma e che qui non è ancora progettato.

---

## 2026-07-09 — Gate MCP, gate auto-memory, e fix di un test durante la verifica

Commit di riferimento: 2f8d917 (working tree ancora non commitato)
File toccati: `.mcp.json` (nuovo, `code-context-provider-mcp` accettato al gate),
`tests/test_paths.py` (corretto il letterale atteso di
`test_sanitize_filename_replaces_invalid_chars`, da `a_b__c_d________` a `a_b__c_d_____`,
verificato eseguendo `pytest`: 7/7 passano dopo il fix), `.claude/context/current-work.md`,
`.claude/memory/index.md`.
Motivo: chiusura dei due gate espliciti previsti dalla sezione 15 di `PROJECT-SYSTEM.md` (MCP e
auto-memory nativa, entrambi posti all'utente, non assunti) e correzione di un bug reale nel test
scoperto eseguendo per davvero la suite durante la popolazione di `dev-testing.md`, su richiesta
esplicita dell'utente. Verificato che `$CLAUDE_CONFIG_DIR/projects/<slug>/` non avesse residui di
auto-memory nativa accumulati prima dell'allineamento.

## 2026-07-09 — Allineamento al sistema di progetto portabile

Commit: 2f8d917 (nessun nuovo commit di codice in questo passo)
File toccati: `.claude/` (import di `PROJECT-SYSTEM.md`, `rules/`, skill del motore, `templates/`,
`settings.json`, `memory/`, `context/`), `CLAUDE.md`, `CLAUDE.local.md`, `.gitignore` (esclusioni
del livello privato).
Motivo: adozione retroattiva del sistema descritto in `.claude/PROJECT-SYSTEM.md`, importato da
`E:\template-claude-developing`. Scansione segreti sulla storia completa (15 commit): nessun
segreto trovato. Schede di `context/` create con frontmatter ancorato al commit corrente e
popolate leggendo il codice attuale.

## 2026-01-27 — Licenza e sezione licenza nel README

Commit: 2f8d917
File toccati: `LICENSE`, `README.md`.
Motivo: aggiunta la licenza MIT (2026, Alessio Sopranzi) e la sezione corrispondente nel README.

## 2026-01-26 — Pulizia legacy, README estesa, suite di test minima

Commit: 7085d45, 1917b9e
File toccati: file legacy rimossi, `README.md` (snippet di codice), `tests/` (nuovo),
`requirements-dev.txt` (nuovo, `pytest`).
Motivo: chiusura del primo milestone di refactoring con documentazione estesa e una prima
copertura di test su `SyncConfig.is_excluded`, `FileHasher` e `FilePathManager.sanitize_filename`.

## 2026-01-26 — Refactoring in package e hardening del core

Commit: 709691f, 2c9cf6e, 6614da9, 1b2f38c, b71f812, fad898c, 273e3c8, 12a0a0e, 164c4c1, 585348e,
5f4f660, 1cf7da3.
File toccati: `folder_sync_watcher/` (nuovo package: `watcher.py`, `config.py`, `hashing.py`,
`paths.py`, `ssd.py`, `subst.py`), `sync_watcher.py`, `subst_manager.py`, `install_service.py`,
`start_watcher.bat`.
Motivo: refactoring che ha spostato la logica core in un package importabile (vedi
`memory/decisions.md` ADR-002), reso sicuri all'import `colorama`/`pywin32` (ADR-003), isolato
`SubstManager` (ADR-004), parametrizzato il path di configurazione da CLI (ADR-005), e reso
idempotente il launcher `start_watcher.bat` (installa le dipendenze solo se l'hash di
`requirements.txt` è cambiato). Rimossi anche emoji e artefatti dal repository.
