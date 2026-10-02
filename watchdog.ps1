$serviceName = "TelegramTradingBot"
$logFile = "c:\Users\Administrator\Desktop\telegrambot2\watchdog.log"
$nssmPath = "c:\Users\Administrator\Desktop\telegrambot2\nssm.exe"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

try {
    $service = Get-Service -Name $serviceName -ErrorAction Stop

    if ($service.Status -ne "Running") {
        $msg = "[$timestamp] WARNING: Service '$serviceName' is $($service.Status). Restarting..."
        Add-Content -Path $logFile -Value $msg

        & $nssmPath start $serviceName 2>&1 | Out-Null
        Start-Sleep -Seconds 5

        $service = Get-Service -Name $serviceName -ErrorAction Stop
        if ($service.Status -eq "Running") {
            Add-Content -Path $logFile -Value "[$timestamp] SUCCESS: Service restarted successfully."
        } else {
            Add-Content -Path $logFile -Value "[$timestamp] ERROR: Service failed to restart. Status: $($service.Status)"
        }
    }
} catch {
    $msg = "[$timestamp] ERROR: Could not check service - $($_.Exception.Message)"
    Add-Content -Path $logFile -Value $msg
}
