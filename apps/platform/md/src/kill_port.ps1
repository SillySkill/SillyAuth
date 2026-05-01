$ports = @(8000, 8080)
foreach ($port in $ports) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    foreach ($conn in $connections) {
        Write-Host ("Killing PID " + $conn.OwningProcess + " on port " + $port)
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}
Start-Sleep -Seconds 3
foreach ($port in $ports) {
    $remaining = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($remaining) {
        Write-Host ("Port " + $port + " STILL listening:")
        $remaining | Format-Table
    } else {
        Write-Host ("Port " + $port + " is free")
    }
}
