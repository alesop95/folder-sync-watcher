---
generated-from-commit: 2f8d91773b4d07b87f778d46deb821d646046c7c
generated-from-branch: refactor/senior-architecture
generated-date: 2026-07-09
covers-paths:
  - .claude/**
  - CLAUDE.md
  - CLAUDE.local.md
  - .gitignore
  - .mcp.json
  - tests/test_paths.py
last-verified-commit: 2f8d91773b4d07b87f778d46deb821d646046c7c
stato: in verifica
---

# Lavoro in corso

> La fonte di verità su cosa è fatto resta `memory/index.md` e il work-log, non le spunte di
> questo file. Ogni feature si descrive con lo schema fisso sotto, così il lavoro pendente è
> leggibile senza ricostruire il contesto da capo.

## Feature: Allineamento al sistema di progetto portabile

Cosa fa: importa in questo repository esistente lo standard di contesto, documentazione e version
control descritto in `.claude/PROJECT-SYSTEM.md` (bundle di riferimento
`E:\template-claude-developing`), senza riscrivere la storia git e senza inventare contenuto.

File da creare: nessuno rimasto: `.claude/` (bundle + settings + memory + context), `CLAUDE.md`,
`CLAUDE.local.md` sono già stati creati in questa sessione.

File da modificare: `.gitignore` (fatto: aggiunte le esclusioni del livello privato).

Definition of done:

- [x] Importato il bundle di riferimento (`PROJECT-SYSTEM.md`, `rules/`, skill del motore,
      `templates/`) senza sovrascrivere nulla.
- [x] Inventario dei divari vs anatomia canonica.
- [x] Scansione segreti su file tracciati e intera storia (15 commit): nessun segreto trovato.
- [x] `.gitignore` completato con le esclusioni del livello privato.
- [x] `CLAUDE.md`/`CLAUDE.local.md` creati.
- [x] `memory/decisions.md`/`progress.md` ricostruiti dalla storia dei commit.
- [x] Schede di `context/` create e popolate leggendo il codice attuale.
- [x] Gate MCP: accettato `code-context-provider-mcp`, creato `.mcp.json` in radice da
      `templates/mcp.windows.json`.
- [x] Gate auto-memory nativa: confermata disattivata (`autoMemoryEnabled: false`, già in
      `settings.json`); verificato che `$CLAUDE_CONFIG_DIR/projects/<slug>/` non contenga una
      cartella `memory/` con residui accumulati prima dell'allineamento (non c'è: solo il
      transcript della sessione corrente).
- [x] `memory/index.md` finale con lo snapshot di sincronizzazione.
- [ ] `sync-context` da invocare a un prossimo passo di codice per misurare il primo drift reale
      (oggi coincide banalmente con `HEAD` perché le schede sono appena state scritte).

Domande aperte: nessuna residua. Il test con il letterale errato
(`tests/test_paths.py::test_sanitize_filename_replaces_invalid_chars`) è stato corretto su
richiesta dell'utente: la suite passa 7/7.

## Riconciliazione

Ultima verifica: 2026-07-09 al commit 2f8d91773b4d07b87f778d46deb821d646046c7c.
