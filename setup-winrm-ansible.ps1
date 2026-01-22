# setup-winrm-ansible.ps1
# Run as Administrator

Write-Host "== WinRM + Firewall setup for Ansible ==" -ForegroundColor Cyan

# 1) Ensure WinRM is enabled and running
Write-Host "[1/6] Enabling WinRM..."
winrm quickconfig -force | Out-Null

# 2) Create/ensure firewall rule for WinRM HTTP (5985)
Write-Host "[2/6] Configuring Firewall rule for port 5985..."
$ruleName = "WinRM-HTTP"
$existingRule = Get-NetFirewallRule -Name $ruleName -ErrorAction SilentlyContinue

if (-not $existingRule) {
    New-NetFirewallRule -Name $ruleName `
        -DisplayName "Windows Remote Management (HTTP-In)" `
        -Enabled True `
        -Direction Inbound `
        -Protocol TCP `
        -Action Allow `
        -LocalPort 5985 | Out-Null
    Write-Host "Firewall rule created: $ruleName"
} else {
    Set-NetFirewallRule -Name $ruleName -Enabled True | Out-Null
    Write-Host "Firewall rule already exists, ensured Enabled=True: $ruleName"
}

# 3) Set the active network profile to Private (common requirement)
Write-Host "[3/6] Setting Network Profile to Private..."
try {
    $activeProfile = Get-NetConnectionProfile | Where-Object { $_.IPv4Connectivity -ne "Disconnected" } | Select-Object -First 1
    if ($null -ne $activeProfile) {
        Set-NetConnectionProfile -InterfaceIndex $activeProfile.InterfaceIndex -NetworkCategory Private
        Write-Host "Network profile set to Private on interface: $($activeProfile.InterfaceAlias)"
    } else {
        Write-Warning "No active network profile found. Skipping profile change."
    }
} catch {
    Write-Warning "Could not set network profile: $($_.Exception.Message)"
}

# 4) Enable Basic auth
Write-Host "[4/6] Enabling Basic authentication..."
winrm set winrm/config/service/auth '@{Basic="true"}' | Out-Null

# 5) Allow unencrypted (needed for Basic over HTTP)
Write-Host "[5/6] Allowing unencrypted WinRM traffic..."
winrm set winrm/config/service '@{AllowUnencrypted="true"}' | Out-Null

# 6) Show verification info
Write-Host "[6/6] Verifying configuration..."
Write-Host "`n--- Firewall Rule ---"
Get-NetFirewallRule -Name $ruleName | Select-Object Name, Enabled, Direction, Action

Write-Host "`n--- WinRM Config (summary) ---"
winrm get winrm/config/service/auth
winrm get winrm/config/service

Write-Host "`n Done. WinRM should be reachable on HTTP port 5985." -ForegroundColor Green
