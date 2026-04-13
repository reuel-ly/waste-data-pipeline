Write-Host "Stopping MQTT port forwarding..."

# Remove port forwarding
netsh interface portproxy delete v4tov4 `
  listenport=1883 `
  listenaddress=0.0.0.0

Write-Host "Port forwarding removed"

# Remove firewall rule
Remove-NetFirewallRule -DisplayName "MQTT 1883" -ErrorAction SilentlyContinue

Write-Host "Firewall rule removed"

Write-Host "✅ MQTT cleanup complete"