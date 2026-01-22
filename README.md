# Sync Deployer Dashboard

A PySide6 GUI for running Ansible playbooks inside a Docker container. This dashboard allows managing both Windows and Linux clients from a single interface.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/abaragithan/sync.git
cd sync
```

### 2. Build the Docker image

```bash
sudo docker build -t sync:latest .
```

### 3. Make the run script executable

```bash
chmod +x ./run.sh
```

### 4. Start the dashboard
### for ubuntu
```bash
./run.sh
```
### for windows
```bash
./run.ps1
```

## Client Configuration

### Windows Client

# Enable WinRM
```powershell
winrm quickconfig -force
```

# Create a new rule
```powershell
New-NetFirewallRule -Name "WinRM-HTTP" -DisplayName "Windows Remote Management (HTTP-In)" -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 5985
```

# Verify the rule is active
```powershell
Get-NetFirewallRule -Name "WinRM-HTTP" | Select-Object Name, Enabled, Direction, Action
```

# Quick setup (run as Administrator)
```powershell
winrm quickconfig -q
```

# Set Netowrk Profile as Private
```powershell
 Set-NetConnectionProfile -NetworkCategory Private
 ```

# Enable Basic authentication
```powershell
winrm set winrm/config/service/auth '@{Basic="true"}'
```

# Allow unencrypted traffic (for basic auth over HTTP)
```powershell
winrm set winrm/config/service '@{AllowUnencrypted="true"}'
```

# Verify configuration
```powershell
winrm get winrm/config
```

# Test WinRM port connectivity ( change the ip address accordingly )
```powershell
curl -v http://192.168.139.36:5985/wsman
```

# Test with Ansible
```powershell
ansible -i hosts.ini windows_clients -m win_ping
```


### Linux Client

1. Ensure SSH server is installed and running:

```bash
sudo apt update
sudo apt install openssh-server -y
sudo systemctl enable ssh
sudo systemctl start ssh
```

## Docker Notes

* The container includes Ansible and all dependencies required to manage Windows (via WinRM) and Linux (via SSH) hosts.
* You do not need to install Ansible locally.
* Ensure the Docker host has network access to the clients.

## Troubleshooting

1. **Windows clients not connecting**:

   * Check WinRM is running: `winrm enumerate winrm/config/listener`
   * Ensure firewall rules are applied correctly.

2. **Linux clients not connecting**:

   * Ensure SSH server is running.
   * Check user credentials and key-based authentication if used.

3. **Docker container fails to start**:

   * Check permissions on `run.sh`.
   * Ensure Docker daemon is running.

## ansible ping pong test example
```bash
ansible -i hosts.ini windows_clients -m win_ping
```

## install a file on windows using ansible cmd example
```bash
ansible-playbook -i hosts.ini playbooks/master_deploy.yml -e "target_host=windows_clients file_name=7zx64.exe app_state=present"
```

