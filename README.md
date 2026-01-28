# Sync Deployer

A PySide6 GUI application that triggers Ansible playbooks inside a Docker container. This dashboard provides a unified interface for managing both Windows and Linux clients.

## Setup

### 1. Clone the Repository
```bash
git clone https://github.com/abaragithan/sync.git
cd sync
```

### 2. Build the Docker Image

The Docker image used for this project is `sync-ansible:latest` and it contains only Ansible + required dependencies.

**You do not need to install Ansible locally.**
```bash
docker build -t sync-ansible:latest .
```

### 3. Start the Dashboard

**For Linux:**
```bash
chmod +x ./run.sh
./run.sh
```

**For Windows:**
```powershell
powershell -ExecutionPolicy Bypass -File run.ps1
```

## Dependency Files

This project uses two dependency files:

- **requirements-gui.txt**: Contains only GUI dependencies (PySide6). These are installed locally using a Python virtual environment when running `run.sh` or `run.ps1`.

- **requirements-docker.txt**: Contains Ansible dependencies that are installed inside the Docker container.

## Client Configuration

### Windows Client Setup

Run the setup script on your Windows client machine.

1. Open PowerShell as Administrator
2. Navigate to the folder containing the setup script
3. Execute the following commands (change the ip address of your controller machine):
```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\setup-winrm-ansible.ps1 -ControllerIP "192.168.135.7" -AllowSelfSigned true
```
### Linux Client Setup

Ensure the SSH server is installed and running on your Linux client:
```bash
sudo apt update
sudo apt install openssh-server -y
sudo systemctl enable ssh
sudo systemctl start ssh
```

## Testing Connectivity

### Test Windows Client

**Test WinRM port connectivity** (replace IP address with your Windows client IP):
```bash
curl -v http://192.168.139.36:5985/wsman
```

**Test with Ansible** (inside Docker container):
```bash
docker run --rm -it \
  -v "$PWD:/app" \
  -w /app/ansible \
  sync-ansible:latest \
  ansible -i inventory/hosts.ini windows_clients -m win_ping
```

### Test Linux Client

**Test with Ansible** (inside Docker container):
```bash
docker run --rm -it \
  -v "$PWD:/app" \
  -w /app/ansible \
  sync-ansible:latest \
  ansible -i inventory/hosts.ini linux_clients -m ping
```

## Usage Examples

### Ping Test

Test connectivity to Windows clients:
```bash
docker run --rm -it \
  -v "$PWD:/app" \
  -w /app/ansible \
  sync-ansible:latest \
  ansible -i inventory/hosts.ini windows_clients -m win_ping
```

### Deploy Application

Install an application on Windows clients:
```bash
docker run --rm -it \
  -v "$PWD:/app" \
  -w /app/ansible \
  sync-ansible:latest \
  ansible-playbook -i inventory/hosts.ini playbooks/master_deploy.yml \
  -e "target_host=windows_clients file_name=7zx64.exe app_state=present"
```

## Docker Information

The Docker container includes Ansible and all required dependencies for managing:
- Windows hosts via WinRM
- Linux hosts via SSH

**You do not need to install Ansible locally.** Ensure the Docker host has network access to all client machines.

## Troubleshooting

### Windows Clients Not Connecting

**Check if WinRM is running:**
```powershell
winrm enumerate winrm/config/listener
```

Verify firewall rules are configured correctly.

### Linux Clients Not Connecting

**Ensure the SSH server is running:**
```bash
sudo systemctl status ssh
```

Verify user credentials and SSH authentication settings.

### Docker Container Fails to Start

**Verify the Docker daemon is running:**
```bash
sudo systemctl status docker
```

**If Docker is running but commands fail, add your user to the docker group:**
```bash
sudo usermod -aG docker $USER
newgrp docker
```