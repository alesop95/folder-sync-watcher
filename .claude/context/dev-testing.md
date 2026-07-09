---
generated-from-commit: 2f8d91773b4d07b87f778d46deb821d646046c7c
generated-from-branch: refactor/senior-architecture
generated-date: 2026-07-09
covers-paths:
  - tests/**
  - requirements-dev.txt
last-verified-commit: 2f8d91773b4d07b87f778d46deb821d646046c7c
---

# Test di sviluppo

> Popolare leggendo la configurazione reale dei test. La checklist operativa locale dei test
> manuali vive invece in `_notes/TEST-CHECKLIST.md`, ignorata da git.

## Test runner e comandi

`pytest` (manifest `requirements-dev.txt`, nessun `pytest.ini`/`pyproject.toml`/`setup.cfg`:
configurazione di default). Comando: `pytest` (o `python -m pytest`) dalla radice del
repository, con `venv/Scripts/python.exe` se si usa il virtualenv creato da `start_watcher.bat`.
Nessuna `conftest.py` e nessun `__init__.py` in `tests/`: l'import di `folder_sync_watcher` nei
test funziona perché `pytest` inserisce la radice del repository in `sys.path` in assenza di
package marker in `tests/`.

Copertura attuale, verificata eseguendo la suite il 2026-07-09 (dopo `pip install -r
requirements-dev.txt` nel virtualenv, non ancora installato di default): 7 test in 3 file,
`test_config.py` (esclusione pattern glob e substring), `test_hashing.py` (stabilità e sensibilità
al contenuto dell'hash MD5), `test_paths.py` (sanificazione nomi file). **6 passano, 1 fallisce**:
`test_sanitize_filename_replaces_invalid_chars` in `tests/test_paths.py:5` si aspetta
`'a_b__c_d________'` ma `FilePathManager.sanitize_filename` restituisce correttamente
`'a_b__c_d_____'` per l'input `'a<b>:c"d/\\|?*'` (9 caratteri non validi nella stringa, 9
sostituzioni 1-a-1 con `_`, come implementa `re.sub(r'[<>:"/\\|?*]', '_', filename)` in
`paths.py:12`). Il valore atteso nel test conta più underscore di quanti la funzione ne produca
per quell'input: sembra un errore nel letterale del test, non un difetto della funzione, ma non è
stato corretto in questa fase di allineamento perché tocca codice, non solo documentazione. Nessun
altro modulo del package (`ssd.py`, `subst.py`, `watcher.py`) ha test dedicati.

Nessun test copre `folder_sync_watcher/watcher.py` (il modulo più grande, 511 righe): la
sincronizzazione, la gestione della coda, il ciclo di riconnessione SSD e `_safe_copy_file` non
hanno copertura automatica.

## Rotte e dati mockati

Non applicabile: nessuna rotta HTTP né servizio mockato. I test usano `tmp_path` di `pytest` per
file e configurazioni temporanee, senza toccare il filesystem reale del progetto.

## Hook e controlli di qualità

Nessun hook di pre-commit, nessun lint o type-check configurato nel repository (nessun
`.flake8`, `ruff.toml`, `mypy.ini` o sezione equivalente trovata). Nessuna integrazione continua
(nessun file sotto `.github/workflows/` o equivalente).
