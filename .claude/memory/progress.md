# Work-log

> Append-only, in ordine cronologico inverso (la voce più recente in alto). Ogni passo
> significativo di codice e ogni intervento manuale rilevante lascia una voce con data, file
> toccati, motivo e commit di riferimento. Le voci precedenti al 2026-07-09 sono ricostruite dalla
> storia dei commit in fase di allineamento, senza inventare dettagli che il commit non dimostra.

## 2026-09-14 - Cartelle con nomi diversi non riconciliate: un'anonimizzazione tornata indietro, e la correzione a mano

**Trovato non dal codice ma controllando lo stato dopo un avvio reale.** Il primo avvio sulla coppia ripuntata su Proton (dopo il ripuntamento e il quarto difetto qui sotto) aveva gia' sincronizzato correttamente 352 cartelle e 243 file, ma fra questi c'era `NIST Cybersecurity Framework -CSF` (senza spazio), una cartella che OneDrive aveva da tempo e che il lato personale non aveva mai avuto con quel nome esatto: il lato personale la chiamava `NIST Cybersecurity Framework - CSF`, con lo spazio. Il confronto bidirezionale lavora per percorso esatto, quindi le ha trattate come due cartelle distinte e ha creato su ciascun lato la copia mancante.

**La conseguenza reale.** Uno screenshot dentro quella cartella era uno dei quattro file che l'anonimizzazione di ADR-011 di `my-cv` aveva trattato il 2026-09-08, rimuovendo il nome della societa'. La versione anonimizzata viveva solo sotto il nome "con spazio"; quella "senza spazio" era ancora l'originale mai anonimizzato. Il primo avvio l'ha copiata per la prima volta su Proton, riportando in chiaro sul cloud personale esattamente cio' che ADR-011 aveva tolto. Verificato aprendo entrambe le immagini (`Nome Societa': Intrawelt Sas` in chiaro contro il campo oscurato nella versione anonimizzata), non dedotto dal nome del file. Controllato l'intero albero sincronizzato per lo stesso pattern con un confronto ricorsivo completo: nessun'altra coppia divergeva per nome.

**Rimedio, manuale e fuori da questo codice.** Cancellata la cartella "senza spazio" da entrambi i lati, dopo aver verificato che fosse identica alla cartella "con spazio" file per file tranne quel singolo screenshot (112 file su 113 con lo stesso hash). Confermata la propagazione della cancellazione anche lato cloud dal log del client Proton: 120 cancellazioni rilevate in blocco, propagate in un ciclo di sincronizzazione chiuso senza errori in meno di un secondo.

**Decisione, in ADR-010.** Nessuna modifica al codice per ora. Il gap resta aperto: due nomi di cartella diversi sui due lati continuano a essere trattati come cartelle distinte, mai riconciliate, con le opzioni valutate e scartate scritte nell'ADR. Chi ripunta il watcher su una coppia nuova deve verificare a mano, prima del primo avvio, che i nomi di primo livello coincidano esattamente sui due lati.

## 2026-09-14 - Un quarto difetto, trovato solo dal primo avvio reale: destinazione read-only

Commit di riferimento: working tree non ancora commitato
File toccati: `folder_sync_watcher/operazioni.py`, `tests/test_operazioni.py`

Ultimo dei difetti emersi oggi, e l'unico che la prova a vuoto non poteva scoprire per costruzione: `prova_a_vuoto` non tocca mai il filesystem, quindi un `PermissionError` che dipende dagli attributi reali di un file di destinazione si vede solo scrivendo per davvero. L'utente ha eseguito il primo avvio reale del watcher ripuntato su Proton (fuori da questa sessione, a mano, come da procedura) e ha riportato l'errore: `Errno 13] Permission denied` su un PDF lato OneDrive durante la sincronizzazione iniziale.

Causa verificata sul file reale, non dedotta: il PDF è marcato read-only dal 9 ottobre 2025, indipendente dall'anonimizzazione di ADR-011, che ha toccato altri quattro file soltanto. `OperazioniFile.copia` chiama `shutil.copy2`, che copia anche i permessi ma non prima di aver aperto la destinazione in scrittura: se la destinazione esiste già ed è read-only, l'apertura fallisce prima che `copy2` abbia la possibilità di sistemare alcunché.

Scelta, con l'utente consultato perché il difetto tocca una scelta di comportamento e non solo un bug: sbloccare la destinazione prima di sovrascrivere o rimuovere, in qualunque punto dell'albero sincronizzato, non solo su questo file. Alternativa scartata: lasciare il limite noto e sbloccare a mano solo questo file, perché il watcher tornerebbe a fallire silenziosamente al primo altro file protetto che incontrasse, e la protezione com'era before era comunque casuale (un file bloccato nel 2025 per una ragione che nessuno ha registrato), non una politica dichiarata.

La funzione nuova è `_sblocca_se_read_only`, un varco condiviso da `copia` e `rimuovi_file`: toglie l'attributo read-only solo se il file di destinazione esiste già ed è effettivamente read-only, prima dell'operazione. Non cambia la decisione se copiare o rimuovere, che resta di chi chiama; toglie solo l'ostacolo tecnico. Dopo la copia, `copy2` riporta comunque i permessi della sorgente sulla destinazione: un file la cui sorgente è a sua volta read-only lo ridiventa, quindi la protezione non si perde se è intenzionale sul lato che il watcher considera autorevole.

Verifica: due test nuovi in `tests/test_operazioni.py`, con un file di destinazione reso read-only prima della copia o della rimozione. Prova sul campo sul file vero che aveva fallito: sorgente e destinazione risolti dalla configurazione reale, `copia()` chiamata direttamente fuori dal watcher, riuscita, e la destinazione resta read-only dopo perché la sorgente lo è. La suite passa a trentanove test.

## 2026-09-14 - Tre difetti trovati dalla prima prova a vuoto reale, tutti corretti

Commit di riferimento: working tree non ancora commitato
File toccati: `sync_watcher.py`, `folder_sync_watcher/subst.py`, `tests/test_subst.py` (nuovo)

Eseguito dalla stessa sessione su `my-cv` di cui parla la voce sotto, immediatamente dopo, per lo stesso motivo: il microstep 4 richiedeva di eseguire davvero `python sync_watcher.py --prova-a-vuoto` sulla coppia ripuntata (passo 8 del suo piano), e i tre difetti sono emersi solo eseguendolo, non leggendo il codice. Nessuno dei tre e' specifico di `my-cv`: tutti e tre esistevano gia' e non erano mai stati esercitati, perche' questo watcher e' fermo dal 21 gennaio e nessuna delle sessioni precedenti lo aveva ancora avviato con una configurazione reale che punta a Proton.

Primo difetto: la console di Windows usa una codepage legacy (cp1252 su questa macchina), che non rappresenta l'emoji nel nome di `🛠️ Ongoing studies`. Ogni `print()` o messaggio di log che la contenesse mandava in eccezione `UnicodeEncodeError` l'intero avvio, prima ancora che il watcher facesse alcunche'. Corretto in `sync_watcher.py` con `sys.stdout.reconfigure(errors='replace')` e lo stesso per `stderr`, prima di `colorama.init()`: la codepage resta quella del sistema, i soli caratteri non rappresentabili vengono sostituiti invece di far fallire l'avvio.

Secondo difetto, in `SubstManager.create_subst_drive`/`remove_subst_drive`: il comando passava per `cmd.exe` con `shell=True` e una stringa concatenata, che codifica la riga di comando con la stessa codepage legacy. Un percorso con l'emoji arrivava quindi troncato o alterato e SUBST falliva con "Impossibile creare SUBST A:", senza altra indicazione. Corretto passando gli argomenti come lista senza `shell=True`: `subst.exe` e' un eseguibile vero sotto `System32` e non serve una shell per invocarlo, e con la lista Windows riceve gli argomenti in UTF-16 cosi' come sono in Python.

Terzo difetto, indipendente dai primi due e non legato all'emoji: `list_subst_drives()` non riconosceva mai un'unita' gia' montata. Il formato reale dell'output di `subst.exe` e' `A:\: => percorso`, due punti seguiti da un backslash prima del separatore `=> `, mentre il codice assumeva che la lettera finisse solo con i due punti; il controllo `endswith(':')` non scattava mai, il backslash restava attaccato alla lettera nella chiave del dizionario, e `subst_letter in existing_drives` era sempre falso. Il sintomo pratico: al secondo avvio o dopo un'unita' rimasta montata da una sessione precedente, il watcher tentava sempre di ricrearla e falliva con "Unita' gia' sostituita" invece di riusare quella che c'era. Corretto con `drive.strip().rstrip(':\\/ ')`, che toglie qualunque combinazione finale di due punti, backslash, slash e spazi in un solo passaggio.

Verifica: quattro test nuovi in `tests/test_subst.py`, che mockano `subprocess.run` per controllare che gli argomenti passati non includano `shell=True` e che il parsing riconosca il formato vero `A:\: => percorso`, incluso un percorso con l'emoji per il primo difetto. La suite passa a trentasette test. Prova sul campo, non solo simulata: `python sync_watcher.py --prova-a-vuoto` con `config.json` ripuntato su Proton ha completato la sincronizzazione iniziale simulata senza errori, con `SUBST A:` creato al primo avvio e riusato correttamente a una seconda chiamata nello stesso processo.

## 2026-09-14 - Sblocco simmetrico dell'ancoraggio: libera/libera_albero

Commit di riferimento: working tree non ancora commitato
File toccati: `folder_sync_watcher/pin.py`, `tests/test_pin.py`

Eseguito da una sessione aperta su `my-cv`, non da qui, per decisione esplicita dell'utente che ha revocato per questa volta la regola opposta: lo stesso precedente gia' applicato il 2026-09-10 per ADR-006. Il motivo e' lo stesso: il microstep 4 della Fase 7 di quel progetto sposta `Ongoing studies` su Proton e deve restringere subito dopo il perimetro locale al solo sottoalbero specchiato con l'azienda, e farlo da una sessione dedicata su questo repository avrebbe solo rimandato il lavoro senza cambiarne la forma.

La decisione, con le opzioni scartate, e' in ADR-009. La funzione nuova e' simmetrica di quella che gia' c'era: `libera`/`libera_albero` impostano `UNPINNED` e tolgono `PINNED`, con lo stesso prefisso per i percorsi lunghi, la stessa verifica per rilettura invece che per codice di uscita, e la stessa modalita' di prova a vuoto di `ancora`/`ancora_albero`. Aggiunta anche `e_liberato`, simmetrica di `e_ancorato`, per la verifica.

Test: sei casi nuovi in `tests/test_pin.py`, sullo stesso modello di quelli gia' presenti per `ancora_albero`, incluso lo stesso caso di regressione oltre i 260 caratteri sul lato opposto. La suite passa a trentuno test.

Non fatto qui, e resta al chiamante: applicare `libera_albero` su un albero Proton reale e verificarne l'esito con l'enumerazione della cartella, perche' la disidratazione vera e propria dipende dal client e non da questo codice, esattamente come per l'ancoraggio in ADR-008.

## 2026-09-10 - Ancoraggio in locale del sottoalbero sorgente

Commit di riferimento: working tree non ancora commitato
File toccati: `folder_sync_watcher/pin.py` (nuovo), `folder_sync_watcher/watcher.py`,
`tests/test_pin.py` (nuovo), `README.md`

Terza e ultima delle cose che il ripuntamento verso una cartella cloud richiedeva. La decisione, con le opzioni scartate, e' in ADR-008. Si attiva con `sync_settings.pin_source` e gira prima della sincronizzazione iniziale, perche' altrimenti sarebbe il confronto dei file a scaricarli uno alla volta.

Si chiama `SetFileAttributesW` con il prefisso per percorsi lunghi invece di `attrib.exe`, e la ragione e' misurata e non teorica: lo stesso giorno, su un albero Proton reale, `attrib` aveva saltato in silenzio 780 file su 1994 perche' i loro percorsi stavano fra 260 e 263 caratteri, dichiarando successo. Un test di regressione costruisce un percorso oltre i 260 caratteri e verifica che l'ancoraggio lo copra.

Prova sul campo, su un solo file di un albero Proton reale, ancorato e poi riportato a solo online: gli attributi passano da `UNPINNED` a `PINNED` e tornano indietro, quindi il client rispetta la dichiarazione. Verificato dopo, con l'enumerazione della cartella, che nessuno dei 2370 file del perimetro sia rimasto materializzato.

Errore di diagnosi commesso e corretto nella stessa prova, che vale piu' del risultato. Leggendo gli attributi con la funzione nuova avevo concluso che l'intero albero si fosse idratato, e avevo attribuito la colpa a `Path.resolve()`, che segue i reparse point. L'enumerazione della cartella diceva il contrario: nessun file era cambiato. La causa vera e' che attraverso il prefisso per percorsi lunghi `GetFileAttributesW` non riporta i bit del segnaposto, quindi era la mia misura a mentire, non il filesystem a cedere. Il limite e' ora documentato nella docstring della funzione e in ADR-008. La sostituzione di `resolve()` con `abspath` e' rimasta, ma come precauzione dichiarata e non come correzione di un difetto osservato: non ho prove che `resolve()` idratasse.

Test: cinque casi nuovi in `tests/test_pin.py`, fra cui il percorso oltre i 260 caratteri e la prova che in prova a vuoto non venga ancorato nulla. La suite passa a ventisei test.

## 2026-09-10 - Prova a vuoto, e le scritture ridotte a un varco solo

Commit di riferimento: segue `442b4ee`, che ha catturato questo lavoro a meta'
File toccati: `folder_sync_watcher/operazioni.py` (nuovo), `folder_sync_watcher/watcher.py`,
`sync_watcher.py`, `tests/test_operazioni.py` (nuovo), `README.md`

Seconda modifica della giornata, richiesta perche' il programma non ha mai avuto un modo di provare senza scrivere, e la prima esecuzione dopo un ripuntamento e' gia' una scrittura reale su una cartella specchiata con l'azienda. La decisione, con le opzioni scartate, e' in ADR-007.

Il lavoro vero non e' stata la modalita' ma la rifattorizzazione che la rende credibile. Le scritture erano nove, sparse in altrettanti punti con `copy2` importato inline ogni volta; ora passano tutte da `OperazioniFile`, che esegue o annota a seconda della modalita' e conta in entrambi i casi. La verifica che non ne sia rimasta fuori nessuna e' meccanica e va rifatta a ogni modifica: in `watcher.py` non deve comparire alcun `copy2`, `rmtree`, `unlink`, `rename` o `mkdir` fuori da quella classe, e oggi l'unica occorrenza rimasta e' `log_dir.mkdir`, che crea la cartella dei log e non e' una scrittura di sincronizzazione.

Attivazione da configurazione con `sync_settings.dry_run` o da riga di comando con `--prova-a-vuoto`, che ha la precedenza. All'arresto viene stampato un riepilogo per tipo di operazione, in entrambe le modalita'.

Prova end-to-end su due cartelle finte, che verifica insieme questa modifica e quella precedente sulla radice dichiarata. La radice si e' risolta al percorso atteso partendo da `folders.source_base`; in prova a vuoto entrambi i lati sono rimasti identici confrontando percorsi e dimensioni prima e dopo, con sei cartelle e tre copie annunciate; la stessa sincronizzazione eseguita davvero ha fatto convergere i due lati sugli stessi quattro elementi, con sette cartelle e tre copie. La differenza fra sei e sette e' il limite dichiarato in ADR-007 e non un difetto: senza scrivere, lo stato del filesystem non avanza e il conteggio riflette il primo passaggio.

Test: sei casi nuovi in `tests/test_operazioni.py`, e quello che conta davvero verifica che dopo una prova a vuoto l'elenco dei file e le loro dimensioni siano immutati, non che i metodi restituiscano il valore giusto. La suite passa a ventuno test.

Incidente di percorso da registrare perche' spiega la storia dei commit: il commit `442b4ee` e' stato dato mentre questa rifattorizzazione era a meta', perche' l'utente ha rilanciato per errore la stessa sequenza di comandi due volte. Contiene `operazioni.py` e un `watcher.py` incompleto, quindi non e' un punto della storia da cui il programma funzioni; il commit successivo lo chiude. Non e' stato riscritto perche' era gia' sul remoto.

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
