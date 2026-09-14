---
generated-from-commit: 2f8d91773b4d07b87f778d46deb821d646046c7c
generated-from-branch: refactor/senior-architecture
generated-date: 2026-07-09
covers-paths: []
last-verified-commit: 2f8d91773b4d07b87f778d46deb821d646046c7c
---

# Roadmap

> Direzione e priorità del progetto. Tracciata. Non è il work-log: qui sta dove si va, non cosa è
> già stato fatto.

## Direzione

Nessuna direzione di medio termine dichiarata esplicitamente nella storia dei commit, nel README o
nei materiali in `_notes/`: il progetto risulta a un primo milestone di refactoring completato
(package modulare, test minimi, licenza) senza un piano scritto per i passi successivi.

## Priorità

Non essendoci un backlog dichiarato, questa sezione resta vuota fino a quando l'utente non
definisce le prossime direzioni. Da verificare, non da assumere come priorità: il divario di
copertura test segnalato in `context/dev-testing.md` (nessun test su `watcher.py`) e il letterale
errato in `tests/test_paths.py` sono osservazioni emerse durante l'allineamento, non decisioni di
roadmap.

## Idee e ipotesi da verificare

Rischio noto e non presidiato dal 2026-09-14, ADR-010: due cartelle con nomi diversi sui due lati non vengono riconciliate come la stessa cartella, ma trattate come due cartelle distinte, ciascuna propagata sull'altro lato. Ha gia' prodotto un caso reale, la reintroduzione su Proton di uno screenshot anonimizzato da ADR-011 di `my-cv` sotto il suo nome originale mai anonimizzato. Un preflight che elenca le cartelle di primo livello presenti su un solo lato, con conferma esplicita prima del primo avvio su una coppia nuova, e' l'opzione valutata e non ancora implementata: da riprendere se il caso si ripete o prima di ripuntare il watcher su un'altra coppia.
