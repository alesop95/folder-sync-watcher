@echo off
title Folder Sync Watcher
cd /d "%~dp0"

echo ========================================
echo    FOLDER SYNC WATCHER
echo    Sincronizzazione OneDrive - Google Drive
echo ========================================
echo.

REM Verifica se Python è installato
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRORE: Python non trovato nel PATH!
    echo Installa Python da https://www.python.org/
    pause
    exit /b 1
)

REM Crea l'ambiente virtuale se non esiste
if not exist "venv" (
    echo Creazione ambiente virtuale...
    python -m venv venv
)

REM Attiva l'ambiente virtuale
call venv\Scripts\activate.bat

REM Installa o aggiorna le dipendenze solo se necessario
set "REQ_FILE=requirements.txt"
set "REQ_HASH_FILE=venv\.requirements.sha256"
set "REQ_HASH="
for /f "tokens=1" %%H in ('certutil -hashfile "%REQ_FILE%" SHA256 ^| findstr /r /c:"^[0-9A-F][0-9A-F]"') do (
    set "REQ_HASH=%%H"
    goto :gotReqHash
)
:gotReqHash

set "NEED_INSTALL=0"
if not exist "%REQ_HASH_FILE%" set "NEED_INSTALL=1"
if exist "%REQ_HASH_FILE%" (
    set /p "OLD_HASH="<"%REQ_HASH_FILE%"
    if /I not "%OLD_HASH%"=="%REQ_HASH%" set "NEED_INSTALL=1"
)

echo.
if "%NEED_INSTALL%"=="1" (
    echo Installazione/Aggiornamento dipendenze...
    python -m pip install -r "%REQ_FILE%"
    if %errorlevel% neq 0 (
        echo ERRORE: Installazione dipendenze fallita
        pause
        exit /b 1
    )
    echo %REQ_HASH%>"%REQ_HASH_FILE%"
) else (
    echo Dipendenze gia' presenti, installazione non necessaria
)
echo.

REM Chiudi eventuali processi Office in background (opzionale)
echo Chiusura processi Office in background...
taskkill /f /im WINWORD.EXE 2>nul
taskkill /f /im EXCEL.EXE 2>nul
taskkill /f /im POWERPNT.EXE 2>nul
echo.

REM Rimuovi SUBST esistente per evitare conflitti
echo Pulizia SUBST precedente...
python subst_manager.py remove 2>nul
echo.

REM Configura SUBST per percorsi corti
echo Configurazione SUBST...
python subst_manager.py setup
if %errorlevel% neq 0 (
    echo ATTENZIONE: Errore nella configurazione SUBST
    echo Il watcher continuerà con percorsi tradizionali
)
echo.

REM Verifica configurazione
echo Verifica configurazione SUBST...
python subst_manager.py list
echo.

REM Avvia il watcher
echo Avvio del watcher...
echo.
python sync_watcher.py --config config.json

pause
