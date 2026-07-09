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
