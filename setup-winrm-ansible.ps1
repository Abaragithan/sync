# setup-winrm-ansible.ps1
# Run as Administrator (elevated PowerShell)

param(
  [Parameter(Mandatory=$true)]
  [string]$ControllerIP,

  [Parameter(Mandatory=$false)]
  [string]$ControllerSubnet = "",

  [Parameter(Mandatory=$false)]
  [string]$CertThumbprint = "",

  [Parameter(Mandatory=$false)]
  [ValidateSet("true","false")]
  [string]$AllowSelfSigned = "false",

  [Parameter(Mandatory=$false)]
  [string]$CertDnsName = $env:COMPUTERNAME,

  [Parameter(Mandatory=$false)]
  [ValidateSet("true","false")]
  [string]$EnableLocalAdminWorkaround = "false"
)

Write-Host "== Hardened WinRM over HTTPS (5986) for Ansible ==" -ForegroundColor Cyan

function Fail($msg) {
  Write-Host $msg -ForegroundColor Red
  exit 1
}

# 1) Enable WinRM service
Write-Host "[1/8] Enabling WinRM service..."
winrm quickconfig -force | Out-Null
Set-Service -Name WinRM -StartupType Automatic
Start-Service WinRM

# 2) Harden auth
Write-Host "[2/8] Hardening WinRM authentication..."
winrm set winrm/config/service '@{AllowUnencrypted="false"}' | Out-Null
winrm set winrm/config/service/auth '@{Basic="false"}' | Out-Null
winrm set winrm/config/service/auth '@{Kerberos="true"}' | Out-Null
winrm set winrm/config/service/auth '@{Negotiate="true"}' | Out-Null
winrm set winrm/config/service/auth '@{Certificate="false"}' | Out-Null
winrm set winrm/config/service/auth '@{CredSSP="false"}' | Out-Null

# CBT hardening (Strict is best; if you face compatibility issues, change to Relaxed)
winrm set winrm/config/service/auth '@{CbtHardeningLevel="Strict"}' | Out-Null

# 3) Optional local admin workaround (workgroup/lab only)
if ($EnableLocalAdminWorkaround -eq "true") {
  Write-Host "[3/8] Enabling LocalAccountTokenFilterPolicy (lab/workgroup workaround)..."
  New-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" `
    -Name LocalAccountTokenFilterPolicy -PropertyType DWord -Value 1 -Force | Out-Null
} else {
  Write-Host "[3/8] Skipping LocalAccountTokenFilterPolicy."
}

# 4) Certificate
Write-Host "[4/8] Preparing certificate for HTTPS listener..."
if ([string]::IsNullOrWhiteSpace($CertThumbprint)) {
  if ($AllowSelfSigned -ne "true") {
    Fail "No CertThumbprint provided and AllowSelfSigned=false. For production, install a CA cert and pass -CertThumbprint."
  }

  Write-Host "Creating self-signed certificate (lab/testing only)..." -ForegroundColor Yellow
  $cert = New-SelfSignedCertificate `
    -DnsName $CertDnsName `
    -CertStoreLocation "Cert:\LocalMachine\My" `
    -KeyLength 2048 `
    -KeyAlgorithm RSA `
    -HashAlgorithm "SHA256"

  $CertThumbprint = $cert.Thumbprint
  Write-Host "Self-signed cert created. Thumbprint: $CertThumbprint"
} else {
  $existing = Get-ChildItem -Path Cert:\LocalMachine\My | Where-Object { $_.Thumbprint -eq $CertThumbprint }
  if (-not $existing) { Fail "Certificate '$CertThumbprint' not found in LocalMachine\My." }
  Write-Host "Using existing certificate thumbprint: $CertThumbprint"
}

# 5) Configure HTTPS-only listener
Write-Host "[5/8] Configuring WinRM listeners (HTTPS only)..."
winrm delete winrm/config/Listener?Address=*+Transport=HTTP 2>$null | Out-Null
winrm delete winrm/config/Listener?Address=*+Transport=HTTPS 2>$null | Out-Null

winrm create winrm/config/Listener?Address=*+Transport=HTTPS `
  "@{Hostname=`"$CertDnsName`"; CertificateThumbprint=`"$CertThumbprint`"}" | Out-Null

# 6) Tighten safe WinRM limits (do NOT touch deprecated MaxConcurrentOperations)
Write-Host "[6/8] Tightening WinRM service limits (compatible)..."
winrm set winrm/config/service '@{MaxConnections="50"}' | Out-Null
winrm set winrm/config/service '@{MaxConcurrentOperationsPerUser="50"}' | Out-Null

# 7) Firewall: allow only controller IP/subnet to 5986
Write-Host "[7/8] Configuring Firewall rule scoped to controller..."
$ruleName = "WinRM-HTTPS-Ansible"

$remote = @()
if (-not [string]::IsNullOrWhiteSpace($ControllerSubnet)) { $remote += $ControllerSubnet }
$remote += $ControllerIP
$remoteCsv = ($remote -join ",")

$existingRule = Get-NetFirewallRule -Name $ruleName -ErrorAction SilentlyContinue
if (-not $existingRule) {
  New-NetFirewallRule -Name $ruleName `
    -DisplayName "WinRM HTTPS (Ansible)" `
    -Enabled True `
    -Direction Inbound `
    -Protocol TCP `
    -Action Allow `
    -LocalPort 5986 `
    -RemoteAddress $remoteCsv | Out-Null
} else {
  Set-NetFirewallRule -Name $ruleName -Enabled True | Out-Null
  # Update scope in a version-compatible way
  Set-NetFirewallRule -Name $ruleName -RemoteAddress $remoteCsv | Out-Null
}

# Restart WinRM
Restart-Service WinRM

# 8) Verify
Write-Host "[8/8] Verification..." -ForegroundColor Yellow

Write-Host "`n--- Listeners ---"
winrm enumerate winrm/config/Listener

Write-Host "`n--- Auth ---"
winrm get winrm/config/service/auth

Write-Host "`n--- Service (key settings) ---"
winrm get winrm/config/service | Select-String "AllowUnencrypted|DefaultPorts|MaxConnections|MaxConcurrentOperationsPerUser|AllowRemoteAccess|IPv4Filter|IPv6Filter"

Write-Host "`n--- Firewall Rule + Scope ---"
Get-NetFirewallRule -Name $ruleName | Select-Object Name, Enabled, Direction, Action | Format-Table -AutoSize
(Get-NetFirewallRule -Name $ruleName | Get-NetFirewallAddressFilter) | Select-Object RemoteAddress | Format-Table -AutoSize

Write-Host "`nDone. WinRM is HTTPS-only on 5986 and restricted to your controller." -ForegroundColor Green
