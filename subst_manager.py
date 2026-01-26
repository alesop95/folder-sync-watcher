#!/usr/bin/env python3
"""
SUBST Manager - Utility per gestire le unità virtuali SUBST
"""

import json
import sys
import subprocess
from pathlib import Path
from folder_sync_watcher import FilePathManager, FolderSyncWatcher, SubstManager, SyncConfig

def main():
    """Funzione principale per gestire SUBST"""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'setup':
        setup_subst_from_config()
    elif command == 'remove':
        remove_subst_from_config()
    elif command == 'list':
        list_subst_drives()
    elif command == 'test':
        test_file_access()
    elif command == 'help':
        print_help()
    else:
        print(f"Comando sconosciuto: {command}")
        print_help()

def print_help():
    """Stampa l'aiuto"""
    print("""
SUBST Manager - Gestione unità virtuali per Folder Sync Watcher

Comandi disponibili:
  setup   - Configura SUBST usando le impostazioni in config.json
  remove  - Rimuove l'unità SUBST configurata
  list    - Lista tutte le unità SUBST attive
  test    - Testa l'accesso al file problematico
  help    - Mostra questo aiuto

Esempi:
  python subst_manager.py setup
  python subst_manager.py list
  python subst_manager.py test
""")

def setup_subst_from_config():
    """Configura SUBST usando le impostazioni del config.json"""
    try:
        config_loader = SyncConfig()
        config = config_loader.config
        
        sync_settings = config['sync_settings']
        drive_letter = sync_settings.get('subst_drive_letter', 'A')
        
        # Trova il percorso fisico dell'SSD
        watcher = FolderSyncWatcher()
        physical_drive = watcher.find_ssd_drive_letter()
        
        if not physical_drive:
            print("SSD non trovato. Verifica che sia connesso e configurato correttamente.")
            return False
        
        relative_path = config['folders']['google_drive_relative_path']
        full_path = str(Path(physical_drive) / relative_path)
        
        print(f"Configurando SUBST {drive_letter}: -> {full_path}")
        
        # Rimuovi SUBST esistente se presente
        existing_drives = SubstManager.list_subst_drives()
        if drive_letter in existing_drives:
            print(f"SUBST {drive_letter}: già esistente, rimuovo...")
            SubstManager.remove_subst_drive(drive_letter)
        
        # Crea nuovo SUBST
        if SubstManager.create_subst_drive(drive_letter, full_path):
            print(f"SUBST {drive_letter}: creato con successo!")
            
            # Aggiorna config.json per abilitare SUBST
            config['sync_settings']['use_subst'] = True
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print("Configurazione aggiornata per usare SUBST")
            
            return True
        else:
            print(f"Errore nella creazione di SUBST {drive_letter}:")
            return False
            
    except Exception as e:
        print(f"Errore: {e}")
        return False

def remove_subst_from_config():
    """Rimuove l'unità SUBST configurata"""
    try:
        config_loader = SyncConfig()
        config = config_loader.config
        
        drive_letter = config['sync_settings'].get('subst_drive_letter', 'A')
        
        if SubstManager.remove_subst_drive(drive_letter):
            print(f"SUBST {drive_letter}: rimosso con successo!")
            
            # Aggiorna config.json per disabilitare SUBST
            config['sync_settings']['use_subst'] = False
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print("Configurazione aggiornata")
            
            return True
        else:
            print(f"Errore nella rimozione di SUBST {drive_letter}:")
            return False
            
    except Exception as e:
        print(f"Errore: {e}")
        return False

def list_subst_drives():
    """Lista tutte le unità SUBST attive"""
    drives = SubstManager.list_subst_drives()
    
    if not drives:
        print("Nessuna unità SUBST attiva")
    else:
        print("Unità SUBST attive:")
        for drive, path in drives.items():
            print(f"  {drive}: => {path}")

def test_file_access():
    """Testa l'accesso al file problematico"""
    try:
        config_loader = SyncConfig()
        config = config_loader.config
        
        # Percorso del file problematico
        problem_file = "Cybersecurity, Normative IT.docx"
        
        # Testa accesso tramite percorso normale
        from sync_watcher import FolderSyncWatcher
        watcher = FolderSyncWatcher()
        physical_drive = watcher.find_ssd_drive_letter()
        
        if physical_drive:
            relative_path = config['folders']['google_drive_relative_path']
            normal_path = Path(physical_drive) / relative_path / problem_file
            
            print("Testando accesso al file problematico...")
            print(f"Percorso normale: {normal_path}")
            
            if normal_path.exists():
                print("File trovato con percorso normale")
                
                # Testa se il file è bloccato
                if FilePathManager.is_file_locked(str(normal_path)):
                    print("File attualmente bloccato")
                else:
                    print("File non bloccato")
                
                # Testa percorso corto
                try:
                    short_path = FilePathManager.get_short_path(str(normal_path))
                    print(f"Percorso corto: {short_path}")
                except Exception as e:
                    print(f"Impossibile ottenere percorso corto: {e}")
                
            else:
                print("File non trovato con percorso normale")
        
        # Testa accesso tramite SUBST se configurato
        if config['sync_settings'].get('use_subst', False):
            drive_letter = config['sync_settings'].get('subst_drive_letter', 'A')
            subst_path = Path(f"{drive_letter}:") / problem_file
            
            print(f"Percorso SUBST: {subst_path}")
            
            if subst_path.exists():
                print("File trovato con percorso SUBST")
                
                # Testa se il file è bloccato
                if FilePathManager.is_file_locked(str(subst_path)):
                    print("File attualmente bloccato via SUBST")
                else:
                    print("File non bloccato via SUBST")
            else:
                print("File non trovato con percorso SUBST")
        
    except Exception as e:
        print(f"Errore durante il test: {e}")

if __name__ == "__main__":
    main()
