# setup-openssh-ansible.ps1
# Run as Administrator (elevated PowerShell)
# Purpose: Configure OpenSSH Server on Windows for Ansible over SSH (port 22)
# Notes:
# - Works for Windows 10/11.
# - Optionally restrict firewall to Controller IP/Subnet.
# - Optional: put an SSH public key to administrators_authorized_keys.

param(
  [Parameter(Mandatory=$true)]
  [string]$ControllerIP,

  [Parameter(Mandatory=$false)]
  [string]$ControllerSubnet = "",

  [Parameter(Mandatory=$false)]
  [ValidateSet("true","false")]
  [string]$RestrictToController = "true",

  [Parameter(Mandatory=$false)]
  [ValidateSet("true","false")]
  [string]$EnablePasswordAuth = "true",

  [Parameter(Mandatory=$false)]
  [ValidateSet("true","false")]
  [string]$EnablePubkeyAuth = "true",

  # If provided, this public key will be written to:
  # C:\ProgramData\ssh\administrators_authorized_keys
  # (Recommended if your Ansible user is admin / in Administrators group)
  [Parameter(Mandatory=$false)]
  [string]$AdminPublicKey = ""
)

Write-Host "== OpenSSH Server (port 22) for Ansible ==" -ForegroundColor Cyan

function Fail($msg) {
  Write-Host $msg -ForegroundColor Red
  exit 1
}

function Ensure-LinePresentInFile {
  param(
    [Parameter(Mandatory=$true)][string]$Path,
    [Parameter(Mandatory=$true)][string]$Line
  )
  if (-not (Test-Path $Path)) { return }
  $content = Get-Content $Path -ErrorAction SilentlyContinue
  if ($content -notcontains $Line) {
    Add-Content -Path $Path -Value $Line
  }
}

# 1) Install OpenSSH Server
Write-Host "[1/7] Installing OpenSSH Server (if missing)..."
try {
  $cap = Get-WindowsCapability -Online | Where-Object Name -like "OpenSSH.Server*"
  if (-not $cap) { Fail "OpenSSH.Server capability not found on this Windows build." }

  if ($cap.State -ne "Installed") {
    Add-WindowsCapability -Online -Name $cap.Name | Out-Null
  }
} catch {
  Fail "Failed to install OpenSSH Server: $($_.Exception.Message)"
}

# 2) Ensure sshd service is running + auto-start
Write-Host "[2/7] Enabling and starting sshd service..."
try {
  Set-Service -Name sshd -StartupType Automatic
  Start-Service sshd -ErrorAction SilentlyContinue
} catch {
  Fail "Failed to start sshd: $($_.Exception.Message)"
}

# 3) Configure sshd_config (password/pubkey options)
Write-Host "[3/7] Configuring sshd_config..."
$sshdConfig = "C:\ProgramData\ssh\sshd_config"
if (-not (Test-Path $sshdConfig)) {
  Fail "sshd_config not found at $sshdConfig (OpenSSH Server install may have failed)."
}

# Backup
$backupPath = "$sshdConfig.bak"
Copy-Item -Path $sshdConfig -Destination $backupPath -Force | Out-Null

# Helper to set or add a config directive (simple + safe)
function Set-SshdConfigOption {
  param(
    [Parameter(Mandatory=$true)][string]$Key,
    [Parameter(Mandatory=$true)][string]$Value
  )

  $lines = Get-Content $sshdConfig
  $pattern = "^\s*#?\s*$Key\s+.*$"

  if ($lines -match $pattern) {
    $lines = $lines -replace $pattern, "$Key $Value"
  } else {
    $lines += "$Key $Value"
  }
  Set-Content -Path $sshdConfig -Value $lines -Encoding ascii
}

# Security defaults (keep it sane for labs)
Set-SshdConfigOption -Key "Port" -Value "22"
Set-SshdConfigOption -Key "PermitRootLogin" -Value "no"
Set-SshdConfigOption -Key "PubkeyAuthentication" -Value ($(if ($EnablePubkeyAuth -eq "true") { "yes" } else { "no" }))
Set-SshdConfigOption -Key "PasswordAuthentication" -Value ($(if ($EnablePasswordAuth -eq "true") { "yes" } else { "no" }))
Set-SshdConfigOption -Key "ChallengeResponseAuthentication" -Value "no"
Set-SshdConfigOption -Key "UsePAM" -Value "no"

# Make sure SFTP subsystem line exists (some modules/file transfers rely on it)
# If it's commented, replace will handle it. If missing, add.
Set-SshdConfigOption -Key "Subsystem" -Value "sftp sftp-server.exe"

# 4) Optionally install admin public key
Write-Host "[4/7] Configuring admin public key (optional)..."
if (-not [string]::IsNullOrWhiteSpace($AdminPublicKey)) {
  $adminAuthKeys = "C:\ProgramData\ssh\administrators_authorized_keys"

  # Write key (overwrite to keep clean)
  Set-Content -Path $adminAuthKeys -Value $AdminPublicKey -Encoding ascii

  # Fix permissions for administrators_authorized_keys (required by OpenSSH on Windows)
  # Owner: Administrators, Full control: SYSTEM + Administrators, Read: Users
  try {
    icacls $adminAuthKeys /inheritance:r | Out-Null
    icacls $adminAuthKeys /grant "SYSTEM:F" | Out-Null
    icacls $adminAuthKeys /grant "BUILTIN\Administrators:F" | Out-Null
    icacls $adminAuthKeys /grant "BUILTIN\Users:R" | Out-Null
  } catch {
    Fail "Failed to set permissions on administrators_authorized_keys: $($_.Exception.Message)"
  }
} else {
  Write-Host "No AdminPublicKey provided. Skipping key install."
}

# 5) Firewall: allow SSH port 22 (optionally restricted)
Write-Host "[5/7] Configuring Firewall rule for SSH (port 22)..."
$ruleName = "OpenSSH-Ansible-SSH"
$remote = @()

if ($RestrictToController -eq "true") {
  if (-not [string]::IsNullOrWhiteSpace($ControllerSubnet)) { $remote += $ControllerSubnet }
  $remote += $ControllerIP
  $remoteCsv = ($remote -join ",")
} else {
  $remoteCsv = "Any"
}

$existingRule = Get-NetFirewallRule -Name $ruleName -ErrorAction SilentlyContinue
if (-not $existingRule) {
  New-NetFirewallRule -Name $ruleName `
    -DisplayName "OpenSSH (Ansible) TCP 22" `
    -Enabled True `
    -Direction Inbound `
    -Protocol TCP `
    -Action Allow `
    -LocalPort 22 `
    -RemoteAddress $remoteCsv | Out-Null
} else {
  Set-NetFirewallRule -Name $ruleName -Enabled True | Out-Null
  Set-NetFirewallRule -Name $ruleName -RemoteAddress $remoteCsv | Out-Null
}

# 6) Restart sshd to apply config changes
Write-Host "[6/7] Restarting sshd..."
try {
  Restart-Service sshd
} catch {
  Fail "Failed to restart sshd: $($_.Exception.Message)"
}

# 7) Verification
Write-Host "[7/7] Verification..." -ForegroundColor Yellow

Write-Host "`n--- sshd service ---"
Get-Service sshd | Format-Table -AutoSize

Write-Host "`n--- Port 22 listening ---"
try {
  $listening = Get-NetTCPConnection -LocalPort 22 -State Listen -ErrorAction SilentlyContinue
  if ($null -eq $listening) {
    Write-Host "WARNING: Port 22 not in LISTEN state yet. Check sshd logs/config." -ForegroundColor Yellow
  } else {
    $listening | Select-Object LocalAddress, LocalPort, State | Format-Table -AutoSize
  }
} catch {
  Write-Host "Could not query TCP listeners: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n--- Firewall Rule + Scope ---"
Get-NetFirewallRule -Name $ruleName | Select-Object Name, Enabled, Direction, Action | Format-Table -AutoSize
(Get-NetFirewallRule -Name $ruleName | Get-NetFirewallAddressFilter) | Select-Object RemoteAddress | Format-Table -AutoSize

Write-Host "`n--- sshd_config (key lines) ---"
Select-String -Path $sshdConfig -Pattern "^(Port|PasswordAuthentication|PubkeyAuthentication|Subsystem)" | ForEach-Object { $_.Line }

Write-Host "`nDone. OpenSSH is enabled on port 22 for Ansible." -ForegroundColor Green
