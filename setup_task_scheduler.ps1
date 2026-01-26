# Script PowerShell per configurare il Task Scheduler per avviare automaticamente il watcher

# Richiede privilegi di amministratore
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))
{
    Write-Host "Questo script richiede privilegi di amministratore!" -ForegroundColor Red
    Write-Host "Riavvia PowerShell come amministratore e riprova." -ForegroundColor Yellow
    pause
    exit
}

$taskName = "FolderSyncWatcher"
$taskDescription = "Sincronizzazione automatica tra OneDrive aziendale e Google Drive personale"
$scriptPath = "$PSScriptRoot\start_watcher.bat"

# Verifica se il task esiste già
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "Il task '$taskName' esiste già." -ForegroundColor Yellow
    $response = Read-Host "Vuoi sovrascriverlo? (S/N)"
    if ($response -ne 'S' -and $response -ne 's') {
        Write-Host "Operazione annullata." -ForegroundColor Red
        exit
    }
    
    # Rimuove il task esistente
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Task esistente rimosso." -ForegroundColor Yellow
}

# Crea il trigger per l'avvio automatico al login
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

# Crea l'azione che esegue lo script
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$scriptPath`"" -WorkingDirectory $PSScriptRoot

# Crea le impostazioni del task
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -RunOnlyIfNetworkAvailable `
    -StartWhenAvailable `
    -RestartInterval (New-TimeSpan -Minutes 5) `
    -RestartCount 3 `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0)

# Crea il principal (utente che esegue il task)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

# Registra il task
$task = Register-ScheduledTask `
    -TaskName $taskName `
    -Description $taskDescription `
    -Trigger $trigger `
    -Action $action `
    -Settings $settings `
    -Principal $principal

if ($task) {
    Write-Host "`nTask schedulato creato con successo!" -ForegroundColor Green
    Write-Host "Nome: $taskName" -ForegroundColor Cyan
    Write-Host "Il watcher si avvierà automaticamente al prossimo login." -ForegroundColor Cyan
    
    Write-Host "`nVuoi avviare il task ora? (S/N)" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq 'S' -or $response -eq 's') {
        Start-ScheduledTask -TaskName $taskName
        Write-Host "Task avviato!" -ForegroundColor Green
    }
} else {
    Write-Host "Errore nella creazione del task!" -ForegroundColor Red
}

Write-Host "`nPremi un tasto per uscire..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
