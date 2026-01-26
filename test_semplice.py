#!/usr/bin/env python3
"""
Test semplificato per identificare problemi di sincronizzazione
"""

import time
import json
from pathlib import Path

def _load_onedrive_base_path() -> Path:
    config_path = Path(__file__).resolve().parent / "config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return Path(config["folders"]["onedrive"])

def test_file_singolo():
    """Test con un singolo file alla volta"""
    print("TEST FILE SINGOLO")
    print("=" * 30)
    
    base_path = _load_onedrive_base_path()
    gdrive_path = Path("A:/")
    
    test_files = [
        "test1.txt",
        "test2.xlsx", 
        "test con spazi.txt",
        "test-trattini.txt"
    ]
    
    for i, filename in enumerate(test_files, 1):
        print(f"\nTest {i}/4: {filename}")
        
        # Crea file
        file_path = base_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"Contenuto test: {filename}\n")
        print(f"Creato: {filename}")
        
        # Aspetta sincronizzazione con verifica progressiva
        print("Aspetto sincronizzazione...")
        for attempt in range(6):  # Max 30 secondi
            time.sleep(5)
            gdrive_file = gdrive_path / filename
            if gdrive_file.exists():
                print(f"Sincronizzato dopo {(attempt + 1) * 5} secondi")
                break
            print(f"   ... ancora in attesa ({(attempt + 1) * 5}s)")
        else:
            print("Timeout raggiunto")
        
        # Verifica
        gdrive_file = gdrive_path / filename
        if gdrive_file.exists():
            print(f"SINCRONIZZATO: {filename}")
        else:
            print(f"NON SINCRONIZZATO: {filename}")
        
        print("-" * 30)
    
    # Pulizia
    print("\nPulizia...")
    for filename in test_files:
        try:
            (base_path / filename).unlink(missing_ok=True)
            (gdrive_path / filename).unlink(missing_ok=True)
        except:
            pass

if __name__ == "__main__":
    test_file_singolo()
