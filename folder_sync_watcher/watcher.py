import logging
import subprocess
import sys
import threading
import time
from pathlib import Path
from queue import Empty, Queue
from typing import Optional

try:
    from colorama import Fore, init
except Exception:  # pragma: no cover
    class _Fore:
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""

    Fore = _Fore()

    def init(*_args, **_kwargs):
        return None

from logging.handlers import TimedRotatingFileHandler
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .config import SyncConfig
from .hashing import FileHasher
from .paths import FilePathManager
from .source import descrizione_attesa, risolvi_percorso, risolvi_radice, usa_base_esplicita
from .subst import SubstManager


init(autoreset=True)


class SyncHandler(FileSystemEventHandler):
    """Handler per gli eventi del filesystem"""

    def __init__(self, source_folder: str, dest_folder: str, sync_queue: Queue, config_loader: SyncConfig):
        super().__init__()
        self.source_folder = Path(source_folder)
        self.dest_folder = Path(dest_folder)
        self.sync_queue = sync_queue
        self.config_loader = config_loader
        self.logger = logging.getLogger(self.__class__.__name__)

    def on_any_event(self, event):
        """Gestisce tutti gli eventi in modo unificato"""
        if self.config_loader.is_excluded(event.src_path):
            return

        if event.event_type == 'created':
            self.sync_queue.put(('create', event.src_path, self.source_folder, self.dest_folder))
        elif event.event_type == 'modified' and not event.is_directory:
            self.sync_queue.put(('modify', event.src_path, self.source_folder, self.dest_folder))
        elif event.event_type == 'deleted':
            self.sync_queue.put(('delete', event.src_path, self.source_folder, self.dest_folder))
        elif event.event_type == 'moved':
            if not self.config_loader.is_excluded(event.dest_path):
                self.sync_queue.put(('move', (event.src_path, event.dest_path), self.source_folder, self.dest_folder))


class FolderSyncWatcher:
    """Classe principale per la sincronizzazione delle cartelle"""

    def __init__(self, config_path: str = "config.json"):
        self.config_loader = SyncConfig(config_path)
        self.config = self.config_loader.config
        self.onedrive_folder = self.config['folders']['onedrive']
        self.google_drive_folder = None
        self.sync_queue = Queue()
        self.observers = []
        self.running = False
        self.sync_thread: Optional[threading.Thread] = None
        self.setup_logging()
        self.update_gdrive_path()

    def setup_logging(self):
        """Configura il sistema di logging"""
        log_config = self.config['logging']
        log_level = getattr(logging, log_config['level'])
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        file_handler = TimedRotatingFileHandler(
            log_dir / log_config['log_file'],
            when='D',
            interval=1,
            backupCount=log_config.get('retention_days', 30),
            encoding='utf-8',
        )
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        self.logger = logging.getLogger('FolderSyncWatcher')
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def find_ssd_drive_letter(self) -> Optional[str]:
        """Radice della sorgente: base esplicita se dichiarata, altrimenti etichetta di volume.

        Il nome resta quello storico per non rompere i chiamanti esistenti, ma la risoluzione
        e' delegata a `source.risolvi_radice`, che accetta anche una cartella locale.
        """
        return risolvi_radice(self.config)

    def update_gdrive_path(self) -> bool:
        """Aggiorna il percorso della cartella Google Drive trovando l'SSD o usando SUBST"""
        sync_settings = self.config['sync_settings']

        if sync_settings.get('use_subst', False):
            subst_letter = sync_settings.get('subst_drive_letter', 'A').upper()

            existing_drives = SubstManager.list_subst_drives()
            if subst_letter in existing_drives:
                self.google_drive_folder = f"{subst_letter}:\\"
                self.logger.info(f"DEBUG: Usando SUBST esistente = {self.google_drive_folder}")
                self.logger.info(f"Usando unità SUBST {subst_letter}:\\ per Google Drive")
                return True
            elif self._setup_subst_drive(subst_letter):
                self.google_drive_folder = f"{subst_letter}:\\"
                self.logger.info(f"DEBUG: Creato nuovo SUBST = {self.google_drive_folder}")
                self.logger.info(f"Usando unità SUBST {subst_letter}:\\ per Google Drive")
                return True

        percorso = risolvi_percorso(self.config)
        if percorso:
            self.google_drive_folder = percorso
            return True

        self.google_drive_folder = None
        return False

    def _setup_subst_drive(self, drive_letter: str) -> bool:
        """Configura l'unità SUBST per Google Drive"""
        try:
            full_path = risolvi_percorso(self.config)
            if not full_path:
                self.logger.error(f"Sorgente non trovata per configurare SUBST: {descrizione_attesa(self.config)}")
                return False

            existing_drives = SubstManager.list_subst_drives()
            if drive_letter in existing_drives:
                if existing_drives[drive_letter] == full_path:
                    self.logger.info(f"SUBST {drive_letter}: già configurato correttamente")
                    return True
                SubstManager.remove_subst_drive(drive_letter)

            if SubstManager.create_subst_drive(drive_letter, full_path):
                self.logger.info(f"SUBST {drive_letter}: creato per {full_path}")
                return True

            self.logger.error(f"Impossibile creare SUBST {drive_letter}:")
            return False

        except Exception as e:
            self.logger.error(f"Errore nella configurazione SUBST: {e}")
            return False

    def check_ssd_connected(self) -> bool:
        """Verifica che la cartella sorgente sia raggiungibile.

        Con una base esplicita la verifica si fa sempre, anche a `check_ssd_connected` falso:
        quel flag disattiva l'attesa di un'unita' rimovibile, non il controllo che la cartella
        da sincronizzare esista. Sincronizzare verso una radice sparita significherebbe
        propagare cancellazioni verso l'altro lato.
        """
        if not usa_base_esplicita(self.config) and not self.config['sync_settings']['check_ssd_connected']:
            return True
        return self.google_drive_folder is not None and Path(self.google_drive_folder).exists()

    def initial_sync(self):
        """Esegue una sincronizzazione iniziale completa"""
        self.logger.info("Avvio sincronizzazione iniziale...")
        if not self.google_drive_folder:
            self.logger.error("Percorso Google Drive non valido, sync iniziale saltata.")
            return

        bidirectional = self.config.get('sync_settings', {}).get('bidirectional', True)
        self._sync_folders(self.onedrive_folder, self.google_drive_folder)
        if bidirectional:
            self._sync_folders(self.google_drive_folder, self.onedrive_folder)
        self.logger.info("Sincronizzazione iniziale completata")

    def _sync_folders(self, source: str, destination: str):
        """Sincronizza ricorsivamente le cartelle"""
        source_path = Path(source)
        dest_path = Path(destination)
        if not source_path.exists():
            self.logger.warning(f"Cartella sorgente non trovata: {source}")
            return

        dest_path.mkdir(parents=True, exist_ok=True)

        for item in source_path.rglob('*'):
            if self.config_loader.is_excluded(str(item)):
                continue

            rel_path = item.relative_to(source_path)
            dest_item = dest_path / rel_path

            try:
                if item.is_dir():
                    dest_item.mkdir(parents=True, exist_ok=True)
                elif self._should_copy_file(item, dest_item):
                    dest_item.parent.mkdir(parents=True, exist_ok=True)
                    from shutil import copy2

                    copy2(str(item), str(dest_item))
                    self.logger.info(f"Copiato: {rel_path}")
            except Exception as e:
                self.logger.error(f"Errore durante la sincronizzazione di {rel_path}: {e}")

    def _should_copy_file(self, source: Path, dest: Path) -> bool:
        """Determina se un file deve essere copiato"""
        if not dest.exists():
            return True
        conflict_resolution = self.config['sync_settings']['conflict_resolution']
        if conflict_resolution == 'newest':
            return source.stat().st_mtime > dest.stat().st_mtime
        if conflict_resolution == 'largest':
            return source.stat().st_size > dest.stat().st_size
        if conflict_resolution == 'hash':
            return FileHasher.get_file_hash(str(source)) != FileHasher.get_file_hash(str(dest))
        return False

    def process_sync_queue(self):
        """Processa la coda di sincronizzazione"""
        while self.running:
            try:
                action, *args = self.sync_queue.get(timeout=1)
                try:
                    if action == '_stop':
                        return
                    if action == 'create':
                        self._handle_create(*args)
                    elif action == 'modify':
                        self._handle_modify(*args)
                    elif action == 'delete':
                        self._handle_delete(*args)
                    elif action == 'move':
                        self._handle_move(*args)
                finally:
                    self.sync_queue.task_done()
            except Empty:
                continue
            except Exception as e:
                self.logger.error(f"Errore nel processamento della coda: {e}")

    def _handle_create(self, src_path: str, source_folder: Path, dest_folder: Path):
        try:
            src = Path(src_path)
            rel_path = src.relative_to(source_folder)
            dest = dest_folder / rel_path
            if src.is_dir():
                dest.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Cartella creata: {rel_path}")
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                from shutil import copy2

                copy2(str(src), str(dest))
                self.logger.info(f"File copiato: {rel_path}")
        except Exception as e:
            self.logger.error(f"Errore nella creazione di {rel_path}: {e}")

    def _handle_modify(self, src_path: str, source_folder: Path, dest_folder: Path):
        try:
            src = Path(src_path)
            rel_path = src.relative_to(source_folder)
            dest = dest_folder / rel_path

            office_extensions = ['.docx', '.xlsx', '.pptx', '.doc', '.xls', '.ppt']
            is_office_file = src.suffix.lower() in office_extensions

            if is_office_file:
                office_delay = self.config['sync_settings'].get('office_file_delay', 5)
                self.logger.info(f"File Office rilevato: {rel_path}, attendo {office_delay} secondi...")
                time.sleep(office_delay)

                if FilePathManager.is_office_process_using_file(str(src)):
                    self.logger.warning(f"File Office in uso: {rel_path}, rimando sincronizzazione...")
                    self.sync_queue.put(('modify', str(src), source_folder, dest_folder))
                    return

            if dest.exists() and self._should_copy_file(src, dest):
                self._safe_copy_file(src, dest, rel_path, is_office_file)
        except Exception as e:
            self.logger.error(f"Errore nella modifica di {rel_path}: {e}")

    def _safe_copy_file(self, src: Path, dest: Path, rel_path: Path, is_office_file: bool = False):
        """Copia sicura di un file con gestione degli errori avanzata"""
        max_attempts = 5 if is_office_file else 3

        dest.parent.mkdir(parents=True, exist_ok=True)

        for attempt in range(max_attempts):
            try:
                if attempt == 0:
                    from shutil import copy2

                    copy2(str(src), str(dest))
                    self.logger.info(f"File aggiornato: {rel_path}")
                    return

                if attempt == 1 and len(str(src)) > 200:
                    try:
                        src_short = FilePathManager.get_short_path(str(src))
                        dest_short = FilePathManager.get_short_path(str(dest.parent)) + "\\" + dest.name
                        from shutil import copy2

                        copy2(src_short, dest_short)
                        self.logger.info(f"File aggiornato con percorsi corti: {rel_path}")
                        return
                    except Exception:
                        pass

                if attempt == 2 and is_office_file:
                    try:
                        subprocess.run(f'handle.exe -c {dest.name} -y', shell=True, capture_output=True)
                    except Exception:
                        pass
                    from shutil import copy2

                    copy2(str(src), str(dest))
                    self.logger.info(f"File aggiornato dopo chiusura handle: {rel_path}")
                    return

                if attempt == 3:
                    temp_dest = dest.parent / f"~temp_{dest.name}"
                    from shutil import copy2

                    copy2(str(src), str(temp_dest))
                    if dest.exists():
                        dest.unlink()
                    temp_dest.rename(dest)
                    self.logger.info(f"File aggiornato con copia temporanea: {rel_path}")
                    return

                sanitized_name = FilePathManager.sanitize_filename(dest.name)
                new_dest = dest.parent / sanitized_name
                from shutil import copy2

                copy2(str(src), str(new_dest))
                self.logger.warning(f"File copiato con nome sanitizzato: {rel_path} -> {sanitized_name}")
                return

            except PermissionError:
                wait_time = 3 * (attempt + 1)
                self.logger.warning(
                    f"File bloccato (tentativo {attempt + 1}/{max_attempts}), attendo {wait_time}s: {rel_path}"
                )
                time.sleep(wait_time)

            except FileNotFoundError:
                self.logger.error(f"File sorgente non trovato: {src}")
                return

            except OSError as e:
                if "name too long" in str(e).lower() or (hasattr(e, 'errno') and e.errno == 36):
                    self.logger.warning(f"Percorso troppo lungo, provo strategia alternativa: {rel_path}")
                    continue
                self.logger.error(f"Errore OS (tentativo {attempt + 1}): {e}")
                if attempt == max_attempts - 1:
                    break
                time.sleep(2)

            except Exception as e:
                self.logger.error(f"Errore imprevisto (tentativo {attempt + 1}): {e}")
                if attempt == max_attempts - 1:
                    break
                time.sleep(2)

        self.logger.error(f"FALLIMENTO: Impossibile copiare il file dopo {max_attempts} tentativi: {rel_path}")
        self.logger.error(f"   Sorgente: {src}")
        self.logger.error(f"   Destinazione: {dest}")

    def _handle_delete(self, src_path: str, source_folder: Path, dest_folder: Path):
        try:
            rel_path = Path(src_path).relative_to(source_folder)
            dest = dest_folder / rel_path
            if dest.exists():
                if dest.is_dir():
                    from shutil import rmtree

                    rmtree(str(dest))
                    self.logger.info(f"Cartella eliminata: {rel_path}")
                else:
                    dest.unlink()
                    self.logger.info(f"File eliminato: {rel_path}")
        except Exception as e:
            self.logger.error(f"Errore nell'eliminazione di {rel_path}: {e}")

    def _handle_move(self, paths: tuple, source_folder: Path, dest_folder: Path):
        try:
            src_old, src_new = paths
            old_rel = Path(src_old).relative_to(source_folder)
            new_rel = Path(src_new).relative_to(source_folder)
            old_dest = dest_folder / old_rel
            new_dest = dest_folder / new_rel
            if old_dest.exists():
                new_dest.parent.mkdir(parents=True, exist_ok=True)
                old_dest.rename(new_dest)
                self.logger.info(f"Spostato: {old_rel} -> {new_rel}")
        except Exception as e:
            self.logger.error(f"Errore nello spostamento: {e}")

    def start(self):
        """Avvia il watcher"""
        print(f"{Fore.GREEN}Avvio del Folder Sync Watcher...")
        self.logger.info("Avvio del servizio di sincronizzazione")

        if usa_base_esplicita(self.config) or self.config['sync_settings']['check_ssd_connected']:
            print(f"{Fore.YELLOW}In attesa della {descrizione_attesa(self.config)}...")
            while not self.update_gdrive_path():
                time.sleep(5)
            print(f"{Fore.GREEN}Sorgente disponibile in: {self.google_drive_folder}")
            self.logger.info(f"Sorgente disponibile, percorso impostato a: {self.google_drive_folder}")

        self.initial_sync()
        self.running = True
        self.start_observers()

        self.sync_thread = threading.Thread(target=self.process_sync_queue, daemon=True)
        self.sync_thread.start()

        print(f"{Fore.GREEN}Watcher avviato con successo!")
        print(f"{Fore.CYAN}Monitoraggio attivo")
        print(f"OneDrive: {self.onedrive_folder}")
        print(f"Google Drive: {self.google_drive_folder}")
        print(f"{Fore.YELLOW}Premi Ctrl+C per terminare")

        try:
            while self.running:
                sorveglia_sorgente = usa_base_esplicita(self.config) or self.config['sync_settings']['check_ssd_connected']
                if sorveglia_sorgente and not self.check_ssd_connected():
                    self.logger.warning("Sorgente non raggiungibile, pausa del monitoraggio")
                    print(f"{Fore.YELLOW}Sorgente non raggiungibile!")
                    self.stop_observers()

                    print(f"{Fore.YELLOW}In attesa della {descrizione_attesa(self.config)}...")
                    while not self.update_gdrive_path():
                        time.sleep(5)

                    print(f"{Fore.GREEN}Sorgente tornata ({self.google_drive_folder}), ripresa del monitoraggio")
                    self.logger.info(f"Sorgente tornata, nuovo percorso: {self.google_drive_folder}")
                    self.initial_sync()
                    self.start_observers()
                time.sleep(5)
        except KeyboardInterrupt:
            self.stop()

    def start_observers(self):
        """Crea e avvia gli observer per le cartelle"""
        if not self.google_drive_folder:
            self.logger.error("Percorso Google Drive non valido, impossibile avviare gli observer.")
            return

        bidirectional = self.config.get('sync_settings', {}).get('bidirectional', True)

        onedrive_handler = SyncHandler(self.onedrive_folder, self.google_drive_folder, self.sync_queue, self.config_loader)
        onedrive_observer = Observer()
        onedrive_observer.schedule(onedrive_handler, self.onedrive_folder, recursive=True)
        onedrive_observer.start()

        observers = [onedrive_observer]
        if bidirectional:
            gdrive_handler = SyncHandler(self.google_drive_folder, self.onedrive_folder, self.sync_queue, self.config_loader)
            gdrive_observer = Observer()
            gdrive_observer.schedule(gdrive_handler, self.google_drive_folder, recursive=True)
            gdrive_observer.start()
            observers.append(gdrive_observer)

        self.observers = observers

    def stop_observers(self):
        """Ferma e rimuove gli observer esistenti"""
        for observer in self.observers:
            try:
                observer.stop()
            except Exception:
                pass
            try:
                observer.join(timeout=10)
            except Exception:
                pass
        self.observers = []

    def stop(self):
        """Ferma il watcher"""
        print(f"\n{Fore.YELLOW}Arresto del watcher...")
        self.logger.info("Arresto del servizio di sincronizzazione")
        self.running = False
        try:
            self.sync_queue.put(('_stop',), timeout=1)
        except Exception:
            pass
        self.stop_observers()
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=10)
        print(f"{Fore.RED}Watcher arrestato")


def main():
    """Funzione principale"""
    try:
        watcher = FolderSyncWatcher()
        watcher.start()
    except Exception as e:
        print(f"{Fore.RED}Errore fatale: {e}")
        logging.error(f"Errore fatale: {e}", exc_info=True)
