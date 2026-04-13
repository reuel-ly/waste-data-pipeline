# Get WSL IP
$wslIp = (wsl hostname -I).Trim()

Write-Host "WSL IP: $wslIp"

# Remove existing rule (avoid duplicates)
netsh interface portproxy delete v4tov4 `
  listenport=1883 `
  listenaddress=0.0.0.0 2>$null

# Add port forwarding
netsh interface portproxy add v4tov4 `
  listenport=1883 `
  listenaddress=0.0.0.0 `
  connectport=1883 `
  connectaddress=$wslIp

Write-Host "Port forwarding enabled (1883 -> $wslIp)"

# Add firewall rule (if not exists)
if (-not (Get-NetFirewallRule -DisplayName "MQTT 1883" -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -DisplayName "MQTT 1883" `
      -Direction Inbound -Protocol TCP `
      -LocalPort 1883 -Action Allow

    Write-Host "Firewall rule added"
} else {
    Write-Host "Firewall rule already exists"
}

Write-Host "✅ MQTT setup complete"