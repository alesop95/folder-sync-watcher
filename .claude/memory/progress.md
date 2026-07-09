# Work-log

> Append-only, in ordine cronologico inverso (la voce più recente in alto). Ogni passo
> significativo di codice e ogni intervento manuale rilevante lascia una voce con data, file
> toccati, motivo e commit di riferimento. Le voci precedenti al 2026-07-09 sono ricostruite dalla
> storia dei commit in fase di allineamento, senza inventare dettagli che il commit non dimostra.

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
