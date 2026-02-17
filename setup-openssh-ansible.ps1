# setup-windows-client.ps1
# Run as Administrator (elevated PowerShell)
# Usage:
#   .\setup-windows-client.ps1 -ControllerIP "10.20.9.154" -PublicKey "ssh-ed25519 AAAA... ansible@sync"

param(
  [Parameter(Mandatory=$true)]
  [string]$ControllerIP,

  [Parameter(Mandatory=$true)]
  [string]$PublicKey,

  [Parameter(Mandatory=$false)]
  [string]$DockerSubnet = "172.17.0.0/16",

  [Parameter(Mandatory=$false)]
  [string]$SSHUser = "Administrator",

  [Parameter(Mandatory=$false)]
  [string]$SSHUserPassword = ""
)

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
function Write-Step($n, $total, $msg) {
  Write-Host "[$n/$total] $msg" -ForegroundColor Cyan
}

function Write-Ok($msg)   { Write-Host "  OK: $msg"    -ForegroundColor Green  }
function Write-Warn($msg) { Write-Host "  WARN: $msg"  -ForegroundColor Yellow }
function Write-Fail($msg) { Write-Host "  FAIL: $msg"  -ForegroundColor Red; exit 1 }

$TOTAL_STEPS = 8
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Sync Deployer - Windows Client Setup"          -ForegroundColor Cyan
Write-Host "  Controller : $ControllerIP"                    -ForegroundColor Cyan
Write-Host "  Docker Net : $DockerSubnet"                    -ForegroundColor Cyan
Write-Host "  SSH User   : $SSHUser"                        -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# ─────────────────────────────────────────────
# Step 1 - Install / Enable OpenSSH Server
# ─────────────────────────────────────────────
Write-Step 1 $TOTAL_STEPS "Installing OpenSSH Server..."

$sshCap = Get-WindowsCapability -Online | Where-Object { $_.Name -like "OpenSSH.Server*" }
if ($sshCap.State -ne "Installed") {
  Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 | Out-Null
  Write-Ok "OpenSSH Server installed."
} else {
  Write-Ok "OpenSSH Server already installed."
}

# ─────────────────────────────────────────────
# Step 2 - Generate SSH host keys
# ─────────────────────────────────────────────
Write-Step 2 $TOTAL_STEPS "Ensuring SSH host keys exist..."

$sshdExe    = "C:\Windows\System32\OpenSSH\sshd.exe"
$sshKeygen  = "C:\Windows\System32\OpenSSH\ssh-keygen.exe"

if (-not (Test-Path $sshdExe))   { Write-Fail "sshd.exe not found at $sshdExe" }
if (-not (Test-Path $sshKeygen)) { Write-Fail "ssh-keygen.exe not found at $sshKeygen" }

# Ensure ProgramData\ssh directory exists
if (-not (Test-Path "C:\ProgramData\ssh")) {
  New-Item -ItemType Directory -Path "C:\ProgramData\ssh" -Force | Out-Null
  Write-Ok "Created C:\ProgramData\ssh directory."
}

# Generate each host key type if missing
$keyTypes = @("rsa", "ecdsa", "ed25519")
foreach ($keyType in $keyTypes) {
  $keyPath = "C:\ProgramData\ssh\ssh_host_${keyType}_key"
  if (-not (Test-Path $keyPath)) {
    & $sshKeygen -t $keyType -f $keyPath -N "" -q 2>&1 | Out-Null
    Write-Ok "Generated $keyType host key."
  } else {
    Write-Ok "$keyType host key already exists."
  }
}

Write-Ok "Host keys ready."

# ─────────────────────────────────────────────
# Step 3 - Write clean sshd_config
# ─────────────────────────────────────────────
Write-Step 3 $TOTAL_STEPS "Writing sshd_config..."

$sshdConfig = "C:\ProgramData\ssh\sshd_config"

# Backup existing config
if (Test-Path $sshdConfig) {
  $backup = "$sshdConfig.bak"
  Copy-Item $sshdConfig $backup -Force
  Write-Ok "Backup saved to $backup"
}

$config = @"
Port 22
PubkeyAuthentication yes
AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys
PasswordAuthentication no
PermitRootLogin no
Subsystem sftp sftp-server.exe
"@

Set-Content $sshdConfig $config -Encoding UTF8

# Validate config
$result = & $sshdExe -t 2>&1
if ($LASTEXITCODE -ne 0) { Write-Fail "sshd_config validation failed: $result" }
Write-Ok "sshd_config written and validated."

# ─────────────────────────────────────────────
# Step 4 - Install public key
# ─────────────────────────────────────────────
Write-Step 4 $TOTAL_STEPS "Installing controller public key..."

$authKeysPath = "C:\ProgramData\ssh\administrators_authorized_keys"

Set-Content $authKeysPath $PublicKey -Encoding UTF8

# Fix permissions (CRITICAL for Windows SSH)
icacls $authKeysPath /inheritance:r | Out-Null
icacls $authKeysPath /grant "SYSTEM:(F)" | Out-Null
icacls $authKeysPath /grant "Administrators:(F)" | Out-Null

Write-Ok "Public key installed with correct permissions."

# ─────────────────────────────────────────────
# Step 5 - Enable & activate SSH user account
# ─────────────────────────────────────────────
Write-Step 5 $TOTAL_STEPS "Configuring SSH user account ($SSHUser)..."

if ($SSHUser -eq "Administrator") {
  net user Administrator /active:yes | Out-Null
  if ($SSHUserPassword -ne "") {
    net user Administrator $SSHUserPassword | Out-Null
    Write-Ok "Administrator account enabled and password set."
  } else {
    Write-Ok "Administrator account enabled."
    Write-Warn "No password set for Administrator (only SSH key auth is enabled)."
  }
} else {
  $localUser = Get-LocalUser -Name $SSHUser -ErrorAction SilentlyContinue
  if (-not $localUser) {
    if ($SSHUserPassword -eq "") { Write-Fail "User '$SSHUser' not found. Provide -SSHUserPassword to create it." }
    $secPwd = ConvertTo-SecureString $SSHUserPassword -AsPlainText -Force
    New-LocalUser -Name $SSHUser -Password $secPwd -PasswordNeverExpires | Out-Null
    Write-Ok "Local user '$SSHUser' created."
  } else {
    Write-Ok "User '$SSHUser' already exists."
  }

  $inAdmins = (Get-LocalGroupMember -Group "Administrators" -ErrorAction SilentlyContinue) |
              Where-Object { $_.Name -like "*$SSHUser*" }
  if (-not $inAdmins) {
    Add-LocalGroupMember -Group "Administrators" -Member $SSHUser | Out-Null
    Write-Ok "Added '$SSHUser' to Administrators group."
  } else {
    Write-Ok "'$SSHUser' is already in Administrators group."
  }
}

# ─────────────────────────────────────────────
# Step 6 - Enable LocalAccountTokenFilterPolicy
# ─────────────────────────────────────────────
Write-Step 6 $TOTAL_STEPS "Enabling LocalAccountTokenFilterPolicy..."

$regPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
Set-ItemProperty -Path $regPath -Name LocalAccountTokenFilterPolicy -Value 1 -Type DWord -Force
Write-Ok "LocalAccountTokenFilterPolicy set to 1."

# ─────────────────────────────────────────────
# Step 7 - Firewall rule for SSH (port 22)
# ─────────────────────────────────────────────
Write-Step 7 $TOTAL_STEPS "Configuring firewall rule for SSH (port 22)..."

$ruleName   = "OpenSSH-Ansible-SSH"
$remoteList = @($ControllerIP, $DockerSubnet)

$existing = Get-NetFirewallRule -Name $ruleName -ErrorAction SilentlyContinue
if (-not $existing) {
  New-NetFirewallRule `
    -Name          $ruleName `
    -DisplayName   "OpenSSH (Ansible)" `
    -Enabled       True `
    -Direction     Inbound `
    -Protocol      TCP `
    -Action        Allow `
    -LocalPort     22 `
    -RemoteAddress $remoteList | Out-Null
  Write-Ok "Firewall rule created."
} else {
  Set-NetFirewallRule -Name $ruleName -RemoteAddress $remoteList -Enabled True | Out-Null
  Write-Ok "Firewall rule updated."
}

# ─────────────────────────────────────────────
# Step 8 - Start / Restart sshd
# ─────────────────────────────────────────────
Write-Step 8 $TOTAL_STEPS "Starting sshd service..."

Set-Service -Name sshd -StartupType Automatic
Restart-Service sshd
Start-Sleep -Seconds 2

$svc = Get-Service sshd
if ($svc.Status -ne "Running") { Write-Fail "sshd failed to start!" }
Write-Ok "sshd is running."

# ─────────────────────────────────────────────
# Verification Summary
# ─────────────────────────────────────────────
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  Verification Summary"                           -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

Write-Host "`n--- sshd Service ---"
Get-Service sshd | Select-Object Name, Status, StartType | Format-Table -AutoSize

Write-Host "`n--- Port 22 Listening ---"
netstat -an | findstr ":22 "

Write-Host "`n--- Firewall Rule ---"
Get-NetFirewallRule -Name $ruleName | Select-Object Name, Enabled, Direction, Action | Format-Table -AutoSize
Get-NetFirewallRule -Name $ruleName | Get-NetFirewallAddressFilter | Select-Object RemoteAddress | Format-Table -AutoSize

Write-Host "`n--- administrators_authorized_keys ---"
Get-Content $authKeysPath
Write-Host ""
icacls $authKeysPath

Write-Host "`n--- sshd_config ---"
Get-Content $sshdConfig

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  Setup Complete!"                                 -ForegroundColor Green
Write-Host ""
Write-Host "  Test connectivity from your Ansible controller:"
Write-Host "  ssh -i ~/.ssh/id_ed25519 $SSHUser@$(hostname)" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Or test with Ansible:"
Write-Host "  ansible -i inventory/hosts.ini windows_clients -m win_ping" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Green