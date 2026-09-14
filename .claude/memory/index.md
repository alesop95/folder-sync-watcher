# Snapshot di sincronizzazione

> Da leggere per primo a inizio sessione. Fotografa lo stato del progetto al commit di
> riferimento e mappa ogni scheda al suo stato di verifica. È la fonte di verità su cosa è fatto,
> non le spunte del diario.

## Stato

```
Branch attivo:        refactor/senior-architecture
Commit di riferimento: 2f8d91773b4d07b87f778d46deb821d646046c7c
Data snapshot:        2026-07-09
```

Lavoro non committato al 2026-09-10, da leggere prima di qualunque altra cosa: la radice della sorgente e' ora dichiarabile in configurazione con `folders.source_base`, secondo ADR-006, e il modulo nuovo e' `folder_sync_watcher/source.py`. La modifica nasce dalla Fase 7 del progetto `my-cv` ed e' stata eseguita da una sessione aperta su quel repository, non da qui, per decisione esplicita dell'utente del 2026-09-10 che ha revocato per questa volta la regola opposta. Il `config.json` di questa macchina non e' stato toccato e punta ancora all'SSD `T7`. Nella stessa giornata e' arrivata anche la prova a vuoto, ADR-007, che ha comportato la rifattorizzazione di tutte le scritture dentro `folder_sync_watcher/operazioni.py`: da qui in avanti una scrittura che non passi da quella classe e' un difetto, perche' romperebbe in silenzio la garanzia della modalita'. Con ADR-008 e' arrivato anche l'ancoraggio in locale del sottoalbero sorgente, attivabile con `sync_settings.pin_source`, che serve quando la sorgente vive dentro un client cloud a segnaposto. Il dettaglio sta nelle tre voci del 2026-09-10 di `progress.md`. Il 2026-09-14, sempre da una sessione aperta su `my-cv` con la stessa revoca puntuale della regola di sessione dedicata, e' arrivata con ADR-009 la funzione simmetrica `libera`/`libera_albero`, che marca `UNPINNED` invece di `PINNED`: serve al microstep 4 della Fase 7 per restringere il perimetro locale dopo lo spostamento di `Ongoing studies`. La suite passa a trentuno test. Nella stessa giornata, eseguendo per la prima volta `python sync_watcher.py --prova-a-vuoto` con `config.json` ripuntato su Proton (fatto da quella stessa sessione, non ancora committato), sono emersi e sono stati corretti tre difetti mai esercitati prima, perche' il watcher e' fermo dal 21 gennaio: la console non regge l'emoji del nome della cartella (`sys.stdout.reconfigure` in `sync_watcher.py`), `SubstManager` passava per `cmd.exe` con `shell=True` mangling l'emoji nella riga di comando, e `list_subst_drives()` non riconosceva mai un'unita' gia' montata per un errore di parsing del formato vero di `subst.exe`. La suite passa a trentasette test. Il `config.json` di questa macchina resta non toccato: punta ancora a `T7`.

## Stato di verifica delle schede

| Scheda | last-verified | Stato |
|---|---|---|
| STACK.md | 2f8d917 | aggiornata |
| design-and-security.md | 2f8d917 | aggiornata |
| deployment.md | 2f8d917 | aggiornata |
| dev-testing.md | 2f8d917 | aggiornata |
| current-work.md | 2f8d917 | aggiornata (feature attiva: allineamento al sistema, in verifica) |
| roadmap.md | 2f8d917 | aggiornata (nessuna direzione dichiarata da tracciare) |

## Punto di ripresa

Allineamento completo: gate MCP accettato (`.mcp.json` con `code-context-provider-mcp`), gate
auto-memory confermato disattivato, test corretto (7/7 pass). Nessuna azione automatica di git è
stata eseguita: restano da fare, a mano dall'utente, `git add`/`commit`/eventuale `push` di tutto
il lavoro di questa sessione (import del bundle, `.gitignore`, `CLAUDE.md`/`CLAUDE.local.md`,
`.claude/memory/`, `.claude/context/`, `.mcp.json`, `tests/test_paths.py`). Il prossimo passo di
merito è un normale ciclo di sviluppo: alla prossima modifica di codice invocare `sync-context` per
la prima misurazione di drift reale rispetto a queste schede.
