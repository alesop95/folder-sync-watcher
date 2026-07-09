# Registro delle decisioni architetturali

> Convenzione ADR-lite, append-only. Ogni decisione architetturale non ovvia entra come voce
> numerata con data, stato, contesto, decisione, motivazione e conseguenze. Una decisione non si
> cancella e non si riscrive: quando viene superata, si aggiunge una nuova voce che dichiara di
> superare la precedente e ne cita il numero. Le voci ADR-002/003/004/005 sono ricostruite dalla
> storia dei commit in fase di allineamento (sezione 11 di `PROJECT-SYSTEM.md`): riportano solo
> ciò che il messaggio di commit e il diff dimostrano, senza inferenze non verificabili.

## ADR-001 — Adozione del sistema di progetto portabile

Data: 2026-07-09
Stato: accettata
Contesto: il progetto ha già 15 commit di storia e nessuna documentazione strutturata; lo stato
utile (stack, decisioni, lavoro in corso) viveva solo nella testa dell'autore e nel README.
Decisione: allineare retroattivamente il repository al sistema descritto in
`.claude/PROJECT-SYSTEM.md`, importato da `E:\template-claude-developing`, con motore di
riconciliazione ancorato ai commit e doppio livello documentale tracciato/ignorato.
Motivazione: persistenza strutturale su disco indipendente dalla sessione di chat, recuperabilità
totale da un clone, controllo umano sul versionamento.
Conseguenze: ogni passo significativo aggiorna le schede, `last-verified-commit`, lo snapshot e il
work-log; commit e push restano manuali.

## ADR-002 — Core modularizzato in package Python

Data: 2026-01-26
Stato: accettata
Contesto: la logica di sincronizzazione viveva in script piatti in radice.
Decisione: spostare la logica core nel package `folder_sync_watcher/` (`watcher.py`, `config.py`,
`hashing.py`, `paths.py`, `ssd.py`, `subst.py`), con `sync_watcher.py` e `subst_manager.py` in
radice ridotti a wrapper CLI che importano dal package (commit `b71f812`, `fad898c`, `273e3c8`).
Motivazione: separare la logica riusabile dagli entry point, testabilità a livello di modulo.
Conseguenze: `folder_sync_watcher/__init__.py` esporta l'API pubblica con import lazy per
`FolderSyncWatcher`/`SyncHandler`, per evitare import circolari e costi di import non necessari
(commit `585348e`).

## ADR-003 — Dipendenze opzionali sicure all'import

Data: 2026-01-26
Stato: accettata
Contesto: `colorama` (output colorato) e `pywin32` (`win32api`, per l'SSD e i percorsi corti) non
sono garantiti disponibili in ogni ambiente in cui il modulo viene importato.
Decisione: avvolgere gli import di `colorama` e `win32api` in `try/except`, con fallback che
disattiva la funzionalità invece di fallire (`watcher.py:10-19`, `ssd.py:3-6`, `paths.py:21-25`)
(commit `12a0a0e`).
Motivazione: il modulo deve restare importabile (es. per i test) anche senza le dipendenze
opzionali installate o su piattaforme non Windows.
Conseguenze: le funzionalità dipendenti da `pywin32` restano no-op silenziosi fuori da Windows;
va tenuto presente leggendo `ssd.py` e `paths.py.get_short_path`.

## ADR-004 — Unità SUBST come livello indipendente dal watcher

Data: 2026-01-26
Stato: accettata
Contesto: la gestione dell'unità virtuale SUBST (per accorciare i percorsi Google Drive su
Windows) era accoppiata alla logica del watcher.
Decisione: isolare `SubstManager` in `subst.py` come componente a se stante, invocato dal watcher
tramite `update_gdrive_path`/`_setup_subst_drive`, e normalizzare ovunque la lettera di unità
(uppercase, senza `:` o `\`) prima di confrontarla (commit `1cf7da3`).
Motivazione: la stessa utility serve sia al watcher in avvio automatico sia allo script CLI
`subst_manager.py` invocato a mano da `start_watcher.bat`.
Conseguenze: `SubstManager.list_subst_drives()` è la fonte di verità sulle unità attive; qualunque
nuovo punto che tocca SUBST deve normalizzare la lettera nello stesso modo per evitare mismatch.

## ADR-005 — Path di configurazione parametrizzabile da CLI

Data: 2026-01-26
Stato: accettata
Contesto: `config.json` era un percorso fisso, non adatto a eseguire il watcher con configurazioni
diverse (es. test locali) senza sovrascrivere il file di produzione.
Decisione: aggiungere il flag `--config` a `sync_watcher.py` tramite `argparse`, passato a
`FolderSyncWatcher(config_path=...)` (commit `164c4c1`).
Motivazione: disaccoppiare l'entry point CLI dal percorso di configurazione hardcoded.
Conseguenze: `FolderSyncWatcher.__init__` accetta `config_path` con default `"config.json"` per
compatibilità con gli usi preesistenti (`install_service.py`, che istanzia senza argomenti).

<!-- ADR-006 — <titolo>
Data: <YYYY-MM-DD>
Stato: <proposta / accettata / superata da ADR-NNN>
Contesto: ...
Decisione: ...
Motivazione: ...
Conseguenze: ... -->
