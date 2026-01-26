#!/usr/bin/env python3
"""
Test completo del sync watcher con diversi tipi di file e strutture
"""

import os
import time
from pathlib import Path
import shutil

def create_test_structure():
    """Crea una struttura di test complessa"""
    print("🧪 CREAZIONE STRUTTURA DI TEST COMPLETA")
    print("=" * 50)
    
    base_path = Path("C:/Users/Utente/OneDrive - Intrawelt S.a.s/Documenti - IT/Cybersec & IT Governance/_ 🧰 Resources")
    
    # 1. File di testo semplici
    files_semplici = [
        "documento1.txt",
        "note_importanti.md", 
        "readme.txt"
    ]
    
    for filename in files_semplici:
        file_path = base_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"Contenuto di {filename}\nCreato: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        print(f"✅ Creato: {filename}")
        time.sleep(2)  # Pausa tra file per evitare sovraccarico
    
    # 2. File Office (simulati)
    office_files = [
        "presentazione.pptx",
        "foglio_calcolo.xlsx", 
        "documento_word.docx"
    ]
    
    for filename in office_files:
        file_path = base_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"File Office simulato: {filename}\n")
        print(f"✅ Creato: {filename}")
        time.sleep(3)  # Pausa più lunga per file Office
    
    # 3. Struttura di cartelle annidate
    cartelle_struttura = [
        "progetti/progetto_a",
        "progetti/progetto_b/sottocartella",
        "documenti/2024/gennaio",
        "documenti/2024/febbraio", 
        "backup/vecchi_file",
        "temp/lavori_in_corso"
    ]
    
    for cartella in cartelle_struttura:
        cartella_path = base_path / cartella
        cartella_path.mkdir(parents=True, exist_ok=True)
        
        # Crea un file in ogni cartella
        file_in_cartella = cartella_path / f"file_in_{cartella.replace('/', '_').replace(' ', '_')}.txt"
        with open(file_in_cartella, 'w', encoding='utf-8') as f:
            f.write(f"File nella cartella: {cartella}\n")
        print(f"✅ Creata cartella: {cartella} con file interno")
        time.sleep(2)  # Pausa tra cartelle
    
    # 4. File con caratteri speciali
    file_speciali = [
        "file con spazi.txt",
        "file-con-trattini.txt", 
        "file_con_underscore.txt",
        "file.con.punti.txt",
        "file (con parentesi).txt"
    ]
    
    for filename in file_speciali:
        file_path = base_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"File con caratteri speciali: {filename}\n")
        print(f"✅ Creato: {filename}")
        time.sleep(3)  # Pausa più lunga per caratteri speciali
    
    # 5. File di diverse dimensioni
    dimensioni_files = [
        ("file_piccolo.txt", "Piccolo"),
        ("file_medio.txt", "Medio " * 100),
        ("file_grande.txt", "Grande " * 1000)
    ]
    
    for filename, contenuto in dimensioni_files:
        file_path = base_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(contenuto)
        print(f"✅ Creato: {filename} ({len(contenuto)} caratteri)")
        time.sleep(2)  # Pausa tra file di dimensioni diverse
    
    print(f"\n🎯 Struttura di test creata con {len(files_semplici) + len(office_files) + len(file_speciali) + len(dimensioni_files)} file")
    print(f"📁 Cartelle create: {len(cartelle_struttura)}")
    
    return {
        'files_semplici': files_semplici,
        'office_files': office_files, 
        'cartelle_struttura': cartelle_struttura,
        'file_speciali': file_speciali,
        'dimensioni_files': [f[0] for f in dimensioni_files]
    }

def verify_sync(test_files):
    """Verifica che tutti i file siano sincronizzati"""
    print("\n🔄 VERIFICA SINCRONIZZAZIONE")
    print("=" * 50)
    
    gdrive_path = Path("A:/")  # Percorso SUBST
    
    tutti_i_file = []
    tutti_i_file.extend(test_files['files_semplici'])
    tutti_i_file.extend(test_files['office_files'])
    tutti_i_file.extend(test_files['file_speciali']) 
    tutti_i_file.extend(test_files['dimensioni_files'])
    
    # Aggiungi file nelle cartelle
    for cartella in test_files['cartelle_struttura']:
        file_in_cartella = f"{cartella}/file_in_{cartella.replace('/', '_').replace(' ', '_')}.txt"
        tutti_i_file.append(file_in_cartella)
    
    sincronizzati = 0
    non_sincronizzati = []
    
    for file_rel in tutti_i_file:
        gdrive_file = gdrive_path / file_rel
        if gdrive_file.exists():
            sincronizzati += 1
            print(f"✅ {file_rel}")
        else:
            non_sincronizzati.append(file_rel)
            print(f"❌ {file_rel}")
    
    print(f"\n📊 RISULTATI:")
    print(f"✅ Sincronizzati: {sincronizzati}/{len(tutti_i_file)}")
    print(f"❌ Non sincronizzati: {len(non_sincronizzati)}")
    
    if non_sincronizzati:
        print(f"\n📋 File non sincronizzati:")
        for file in non_sincronizzati:
            print(f"  - {file}")
    
    return len(non_sincronizzati) == 0

def test_modifiche():
    """Testa le modifiche ai file esistenti"""
    print("\n✏️ TEST MODIFICHE FILE")
    print("=" * 50)
    
    base_path = Path("C:/Users/Utente/OneDrive - Intrawelt S.a.s/Documenti - IT/Cybersec & IT Governance/_ 🧰 Resources")
    
    # Modifica un file esistente
    file_da_modificare = base_path / "documento1.txt"
    if file_da_modificare.exists():
        with open(file_da_modificare, 'a', encoding='utf-8') as f:
            f.write(f"\nModifica aggiunta: {time.strftime('%H:%M:%S')}\n")
        print(f"✅ Modificato: documento1.txt")
        
        # Aspetta un po' per la sincronizzazione
        print("⏳ Attendo 10 secondi per la sincronizzazione...")
        time.sleep(10)
        
        # Verifica che sia sincronizzato
        gdrive_file = Path("A:/documento1.txt")
        if gdrive_file.exists():
            with open(gdrive_file, 'r', encoding='utf-8') as f:
                contenuto = f.read()
                if "Modifica aggiunta" in contenuto:
                    print("✅ Modifica sincronizzata correttamente!")
                    return True
                else:
                    print("❌ Modifica non sincronizzata")
                    return False
        else:
            print("❌ File non trovato su Google Drive")
            return False
    else:
        print("❌ File da modificare non trovato")
        return False

def cleanup_test():
    """Pulisce i file di test"""
    print("\n🧹 PULIZIA FILE DI TEST")
    print("=" * 50)
    
    base_path = Path("C:/Users/Utente/OneDrive - Intrawelt S.a.s/Documenti - IT/Cybersec & IT Governance/_ 🧰 Resources")
    
    # Lista di tutto quello che abbiamo creato
    items_to_remove = [
        "documento1.txt", "note_importanti.md", "readme.txt",
        "presentazione.pptx", "foglio_calcolo.xlsx", "documento_word.docx",
        "file con spazi.txt", "file-con-trattini.txt", "file_con_underscore.txt",
        "file.con.punti.txt", "file (con parentesi).txt",
        "file_piccolo.txt", "file_medio.txt", "file_grande.txt",
        "test.txt", "test_manuale.txt",  # File precedenti
        "progetti", "documenti", "backup", "temp"  # Cartelle
    ]
    
    for item in items_to_remove:
        item_path = base_path / item
        try:
            if item_path.exists():
                if item_path.is_file():
                    item_path.unlink()
                    print(f"✅ Rimosso file: {item}")
                elif item_path.is_dir():
                    shutil.rmtree(item_path)
                    print(f"✅ Rimossa cartella: {item}")
        except Exception as e:
            print(f"❌ Errore rimozione {item}: {e}")

def main():
    """Test completo"""
    print("🚀 TEST COMPLETO SYNC WATCHER")
    print("=" * 50)
    
    # 1. Crea struttura di test
    test_files = create_test_structure()
    
    print(f"\n⏳ Aspetta 60 secondi per la sincronizzazione di tutti i file...")
    time.sleep(60)
    
    # 2. Verifica sincronizzazione
    sync_ok = verify_sync(test_files)
    
    if sync_ok:
        print("\n🎉 SINCRONIZZAZIONE INIZIALE OK!")
        
        # 3. Testa modifiche
        modifica_ok = test_modifiche()
        
        if modifica_ok:
            print("\n🎉 TEST MODIFICHE OK!")
        else:
            print("\n❌ TEST MODIFICHE FALLITO!")
    else:
        print("\n❌ SINCRONIZZAZIONE INIZIALE FALLITA!")
    
    # 4. Pulizia (opzionale)
    print(f"\nPremi INVIO per pulire i file di test...")
    input()
    cleanup_test()
    
    if sync_ok and modifica_ok:
        print("\n🎉 TUTTI I TEST COMPLETATI CON SUCCESSO!")
        print("Il watcher è pronto per i file reali!")
    else:
        print("\n❌ ALCUNI TEST SONO FALLITI!")
        print("Controlla i log prima di procedere con i file reali.")

if __name__ == "__main__":
    main()
