$port = 8080
$connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
foreach ($c in $connections) {
    Write-Host ("Killing PID=" + $c.OwningProcess + " on port " + $port)
    try {
        Stop-Process -Id $c.OwningProcess -Force -ErrorAction Stop
        Write-Host "  Success"
    } catch {
        Write-Host ("  Error: " + $_.Exception.Message)
    }
}
Start-Sleep -Seconds 2
$remaining = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if ($remaining) {
    Write-Host "Warning: Port $port still has connections!"
    $remaining | Format-Table LocalPort, OwningProcess, State
} else {
    Write-Host "Port $port is free"
}
