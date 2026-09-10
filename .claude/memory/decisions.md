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

## ADR-006 - Radice della sorgente dichiarabile, non solo derivata dall'etichetta di volume

Data: 2026-09-10.

Contesto: fino a oggi la cartella sorgente si otteneva sempre nello stesso modo, cioè cercando fra le unità montate quella con l'etichetta dichiarata in `sync_settings.ssd_volume_label` e componendo la sua lettera con `folders.google_drive_relative_path`. L'assunzione implicita era che la sorgente vivesse su un'unità rimovibile identificabile per etichetta, e regge finché la sorgente è l'SSD esterno. Il progetto `my-cv`, nella sua Fase 7, sposta quell'archivio dentro la cartella locale di un client di sincronizzazione cloud: quella cartella sta nel profilo utente, non ha etichetta di volume, e non esiste oggi alcun modo di dichiararla in configurazione.

Opzioni valutate. Dare al volume di sistema un'etichetta e continuare a cercare per etichetta: scartata, perché rinomina un volume di sistema per aggirare un limite del programma, e l'etichetta di `C:` non è una scelta che spetta a questo progetto. Riscrivere `find_ssd_drive_letter` perché accetti anche un percorso: scartata, perché quella funzione ha un compito solo, trovare una lettera da un'etichetta, e allargarlo la renderebbe una funzione che fa due cose diverse a seconda dell'argomento. Introdurre una chiave di configurazione che dichiara la radice: scelta.

Scelta: la radice si dichiara con `folders.source_base`, un percorso assoluto. Quando è presente vince sulla ricerca per etichetta; quando manca il comportamento è identico a prima, quindi le configurazioni esistenti continuano a funzionare senza alcuna modifica. Il percorso relativo accetta il nome nuovo `source_relative_path` e ripiega su `google_drive_relative_path`, che resta valido. La risoluzione vive in un modulo nuovo, `folder_sync_watcher/source.py`, e i quattro punti che prima componevano il percorso per conto proprio, due in `watcher.py` e due in `subst_manager.py`, ora lo chiedono a lui: la duplicazione era la ragione per cui un difetto è sopravvissuto a lungo.

Difetto corretto contestualmente, ed è la ragione per cui questa non è solo una aggiunta. `Path('J:') / relativo` non produce un percorso assoluto ma `J:relativo`, che Windows risolve rispetto alla directory corrente di quell'unità: il codice sostituito lo faceva in tutti e quattro i punti. La normalizzazione della radice ora avviene una volta sola, dentro il modulo nuovo, e un test di regressione la copre.

Conseguenza sul controllo di raggiungibilità: `check_ssd_connected` significava due cose insieme, cioè attendere un'unità rimovibile e verificare che la cartella esista. Con una base esplicita la prima non ha senso e la seconda serve più di prima, perché una cartella cloud può sparire senza che sparisca un disco. Il flag continua quindi a governare l'attesa, mentre la verifica di esistenza diventa incondizionata quando la base è dichiarata: sincronizzare in bidirezionale verso una radice sparita significherebbe propagare cancellazioni all'altro lato.

Cosa questa decisione non fa, e va detto perché è la parte che manca. Non cambia la configurazione di questa macchina, che resta puntata all'SSD: il ripuntamento è un passo separato, da fare quando la cartella di destinazione esisterà davvero. Non introduce alcuna modalità di prova a vuoto, che il watcher continua a non avere, quindi il primo avvio dopo un ripuntamento resta una scrittura reale e va provato prima su cartelle finte. E non implementa il pin dei file cloud in locale, che la Fase 7 di `my-cv` assegna a questo programma e che resta da progettare.

## ADR-007 - Un solo varco di scrittura, e la prova a vuoto che ne consegue

Data: 2026-09-10.

Contesto: il programma non ha mai avuto una modalita' che non scrive, e la sua assenza non e' un dettaglio di comodita'. Ogni volta che si cambiano le cartelle in configurazione la prima esecuzione e' gia' una scrittura reale su entrambi i lati, e la sincronizzazione e' bidirezionale, quindi una configurazione sbagliata non produce un errore ma una propagazione. Il caso concreto che ha reso urgente la questione e' il ripuntamento verso una cartella specchiata con una OneDrive aziendale, dove una prima esecuzione sbagliata non si annulla.

L'ostacolo non era scrivere la modalita' ma dove metterla. Le scritture erano nove, sparse in altrettanti punti di `watcher.py`, ciascuna con `copy2` importato inline: un controllo per punto avrebbe funzionato finche' qualcuno non ne avesse aggiunto un decimo, e la dimenticanza si sarebbe scoperta a scrittura avvenuta. Una modalita' che non scrive e' credibile solo se esiste un unico varco da presidiare.

Opzioni valutate. Un flag controllato in ognuno dei nove punti: scartata per la ragione appena detta, e perche' avrebbe lasciato la duplicazione che ha gia' permesso a un difetto di percorso di sopravvivere in quattro copie. Una copia dell'albero su cui provare: scartata, perche' su un albero da quasi due gigabyte il costo e' reale e la copia non riproduce i lock dei file Office, che sono meta' della difficolta' di questo programma. Un solo oggetto che media tutte le scritture: scelta.

Scelta: nasce `folder_sync_watcher/operazioni.py` con la classe `OperazioniFile`, che espone creazione di cartelle, copia, rimozione di file e di alberi e rinomina, e che in prova a vuoto registra e conta invece di eseguire. Ogni metodo restituisce vero solo se l'operazione e' avvenuta davvero, cosi' il chiamante distingue il fatto dal simulato senza interrogare la configurazione. La modalita' si attiva con `sync_settings.dry_run` oppure con `--prova-a-vuoto`, che ha la precedenza. All'arresto il programma stampa un riepilogo per tipo di operazione, valido in entrambe le modalita'.

Limite dichiarato, e va scritto qui perche' chi legge il riepilogo di una prova a vuoto deve sapere che cosa sta leggendo: non creando cartelle e non copiando file, la prova lascia il filesystem fermo, quindi le decisioni che dipendono dal suo stato, in particolare il confronto delle date in `_should_copy_file`, vedono un mondo diverso da quello di meta' esecuzione reale. Il riepilogo descrive il primo passaggio, non il secondo. Nella prova end-to-end su cartelle finte questo si e' visto come sei cartelle annunciate contro sette create.

Conseguenza di progetto che vale oltre questa modalita': da oggi una scrittura nuova che non passi da `OperazioniFile` e' un difetto, non una scelta di stile, perche' romperebbe in silenzio una garanzia dichiarata. Il controllo e' meccanico: in `watcher.py` non deve comparire nessun `copy2`, `rmtree`, `unlink`, `rename` o `mkdir` fuori da quella classe, con la sola eccezione della cartella dei log, che non e' una scrittura di sincronizzazione.
