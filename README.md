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

```bash
./run.sh
```

## Client Configuration

### Windows Client

1. Open PowerShell as Administrator:

```powershell
winrm quickconfig -force
Enable-NetFirewallRule -Name "WINRM-HTTP-In-TCP"
```

2. (Optional) Set trusted hosts if the server is not in the same domain:

```powershell
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "<Server-IP>"
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
