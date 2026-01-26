#!/usr/bin/env python3
"""
Script per installare il Folder Sync Watcher come servizio Windows
"""

import os
import sys
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import logging
from pathlib import Path
import subprocess

class FolderSyncService(win32serviceutil.ServiceFramework):
    """Servizio Windows per il Folder Sync Watcher"""
    
    _svc_name_ = "FolderSyncWatcher"
    _svc_display_name_ = "Folder Sync Watcher Service"
    _svc_description_ = "Servizio di sincronizzazione bidirezionale tra OneDrive e Google Drive"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.watcher = None
        
    def SvcStop(self):
        """Arresta il servizio"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        if self.watcher:
            self.watcher.stop()
            
    def SvcDoRun(self):
        """Esegue il servizio"""
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()
        
    def main(self):
        """Funzione principale del servizio"""
        # Importa il watcher
        sys.path.insert(0, str(Path(__file__).parent))
        from folder_sync_watcher import FolderSyncWatcher
        
        try:
            # Avvia il watcher
            self.watcher = FolderSyncWatcher()
            self.watcher.start()
        except Exception as e:
            servicemanager.LogErrorMsg(f"Errore nel servizio: {str(e)}")

def install_service():
    """Installa il servizio Windows"""
    print("Installazione del servizio Folder Sync Watcher...")
    
    # Verifica di essere amministratore
    import ctypes
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("ERRORE: Questo script deve essere eseguito come amministratore!")
        sys.exit(1)
        
    # Installa il servizio
    win32serviceutil.InstallService(
        FolderSyncService,
        FolderSyncService._svc_name_,
        FolderSyncService._svc_display_name_,
        description=FolderSyncService._svc_description_,
        startType=win32service.SERVICE_AUTO_START
    )
    
    print(f"Servizio '{FolderSyncService._svc_display_name_}' installato con successo!")
    
def uninstall_service():
    """Disinstalla il servizio Windows"""
    print("Disinstallazione del servizio Folder Sync Watcher...")
    
    # Verifica di essere amministratore
    import ctypes
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("ERRORE: Questo script deve essere eseguito come amministratore!")
        sys.exit(1)
        
    # Disinstalla il servizio
    win32serviceutil.RemoveService(FolderSyncService._svc_name_)
    print(f"Servizio '{FolderSyncService._svc_display_name_}' disinstallato con successo!")
    
def start_service():
    """Avvia il servizio"""
    win32serviceutil.StartService(FolderSyncService._svc_name_)
    print(f"Servizio '{FolderSyncService._svc_display_name_}' avviato!")
    
def stop_service():
    """Arresta il servizio"""
    win32serviceutil.StopService(FolderSyncService._svc_name_)
    print(f"Servizio '{FolderSyncService._svc_display_name_}' arrestato!")
    
def main():
    """Gestisce i comandi da linea di comando"""
    if len(sys.argv) == 1:
        print("Uso:")
        print("  install_service.py install    - Installa il servizio")
        print("  install_service.py uninstall  - Disinstalla il servizio")
        print("  install_service.py start      - Avvia il servizio")
        print("  install_service.py stop       - Arresta il servizio")
        print("  install_service.py debug      - Esegue in modalità debug")
        sys.exit(0)
        
    command = sys.argv[1].lower()
    
    if command == 'install':
        install_service()
    elif command == 'uninstall':
        uninstall_service()
    elif command == 'start':
        start_service()
    elif command == 'stop':
        stop_service()
    elif command == 'debug':
        # Esegue in modalità debug (non come servizio)
        sys.path.insert(0, str(Path(__file__).parent))
        from folder_sync_watcher import FolderSyncWatcher
        watcher = FolderSyncWatcher()
        watcher.start()
    else:
        print(f"Comando non riconosciuto: {command}")
        
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'service':
        # Il servizio è stato chiamato da Windows
        win32serviceutil.HandleCommandLine(FolderSyncService)
    else:
        main()
