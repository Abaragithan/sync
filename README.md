# Sync Deployer

A PySide6 GUI application that triggers Ansible playbooks inside a Docker container. This dashboard provides a unified interface for managing both Windows and Linux clients.

# Project Description

## Problem Statement

Managing multiple client systems across different operating systems can be complex and time-consuming when deployments are done manually. System administrators often need a centralized tool to deploy software, monitor connectivity, and automate configuration tasks.

## Objectives

The main objectives of this project are:
- Provide a centralized GUI dashboard for deployment automation
- Automate software installation across multiple systems
- Integrate Docker and Ansible for secure automation
- Support both Windows and Linux clients
- Simplify infrastructure management for administrators

## Target Users

-System administrators
-DevOps engineers
-IT infrastructure teams
-Educational labs managing multiple machines

## System Overview

The system provides a graphical interface that allows administrators to run automation tasks. Behind the scenes, the application launches Ansible playbooks within a Docker container, which communicates with client machines via SSH.

# System Architecture

## Workflow

1. The user launches the Sync Dashboard application. From the dashboard, the user can create a new lab by providing the lab name, section, number of rows, number of columns, start IP address, and end IP address. Once these details are submitted, the system creates the lab and automatically generates the PCs based on the given IP range.

2. After the lab is created, the user can manage it from the dashboard. If any changes are required, the user can click the Edit button to modify the lab configuration. This includes adding PCs, removing PCs, editing IP addresses, or assigning IP addresses in bulk. If no changes are required, the user can simply click Open to view the lab.

3. Inside the lab view, the user selects the target PCs where the software deployment should be performed. After selecting the machines, the user clicks Next button, which redirects to the Software Manager page.

4. In the Software Manager page, the user first selects the target operating system, either Windows or Linux, and then selects the action to perform such as install, remove, or update.

5. For Windows deployments, the user can either provide Chocolatey package names for the required software or browse and select a local installer file such as .exe or .msi. If a local installer is used, optional silent installation arguments can be provided to run the installation without user interaction. For Linux deployments, the user simply provides the package name and the installation is performed using sudo apt through Ansible automation.

6. After configuring the deployment, the user clicks the Execute button. The system then runs the deployment process using an Ansible playbook inside a Docker container, which connects to the selected PCs via SSH and performs the requested action.

7. During execution, the progress is displayed in the Execution Log panel in the dashboard. This log shows the status of each operation and any errors that occur. After the process is completed, the logs can also be saved locally as a text file for future reference.

## Architecture Components

# GUI Layer
  - PySide6 dashboard
# Automation Layer
  - Ansible Playboks
# Container Layer
  - Docker container running Ansible
# Infrastructure Layer
  - Windows clients
  - Linux clients

## Architecture Diagrams
```text
+----------------------+
|    User (Admin)      |
+----------+-----------+
           |
           v
+----------------------+
|  PySide6 Dashboard   |
|   (GUI Interface)    |
+----------+-----------+
           |
           v
+----------------------+
|  Docker Container    |
|   (Ansible Engine)   |
+----------+-----------+
           |
           v
+----------------------+
|   SSH Connections    |
+----------+-----------+
           |
     +-----+-----+
     |           |
     v           v
+------------+ +------------+
|  Windows   | |   Linux    |
|  Clients   | |  Clients   |
+------------+ +------------+
```
# Technologies Used

## Programming Languages
  - Python

## Frameworks / Libraries
  - PySide6 (GUI framework)
  - Ansible (automation)
  - OpenSSH

## Containerization
  - Docker

## Configuration Management
  - Ansible Playbooks
  - Ansible Inventory

## Operating Systems
  - Linux
  - Windows

## Security Tools
  - SSH Key Authentication

# Installation Instructions

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

Windows clients are managed via **OpenSSH (port 22)** using SSH key authentication.

#### 1. Generate SSH Key on Controller (if not already done)

```bash
ssh-keygen -t ed25519 -C "ansible@sync" -f ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub
```

Copy the public key output — you will need it in the next step.

#### 2. Run Setup Script on Windows Client

Open PowerShell as Administrator on each Windows client and run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force

.\setup-openssh-ansible.ps1 `
  -ControllerIP "10.20.9.154" `
  -PublicKey "ssh-ed25519 AAAA... ansible@sync"
```

Replace `10.20.9.154` with your controller IP and the public key with your actual key from step 1.

The script will automatically:
- Install and configure OpenSSH Server
- Write a secure `sshd_config` with correct `AuthorizedKeysFile` path
- Install your public key with correct permissions
- Enable the `Administrator` account
- Set `LocalAccountTokenFilterPolicy`
- Configure firewall rules for controller IP and Docker subnet (`172.17.0.0/16`)
- Start the `sshd` service

### Linux Client Setup

Linux clients are managed via **SSH** using sudo for privilege escalation.

#### 1. Install SSH Server

```bash
sudo apt update
sudo apt install openssh-server -y
sudo systemctl enable ssh
sudo systemctl start ssh
```

#### 2. Configure Sudo Password via Ansible Vault

```bash
# Create directory structure
mkdir -p ansible/inventory/group_vars/linux_clients

# Create encrypted vault file using Docker
sudo docker run --rm -it \
  -v "$PWD:/app" \
  -w /app/ansible \
  sync-ansible:latest \
  bash -c 'echo "your-vault-password" > /tmp/vault_pass && \
  cat << EOF | ansible-vault encrypt --vault-password-file=/tmp/vault_pass --output=inventory/group_vars/linux_clients/vault.yml
---
vault_ansible_become_password: YOUR_SUDO_PASSWORD_HERE
EOF'

# Save vault password securely
echo "your-vault-password" > ~/.ansible_vault_pass
chmod 600 ~/.ansible_vault_pass


# copy the public key to client
ssh-copy-id -i ~/.ssh/id_ed25519.pub <user-name>@<clinet_ip>
```

## Inventory Configuration

Update `ansible/inventory/hosts.ini` with your client information:

```ini
[windows_clients]
10.20.9.156
#10.20.9.157
#10.20.9.158
#10.20.9.159
#10.20.9.160

[linux_clients]
10.20.9.154

[windows_clients:vars]
ansible_connection=ssh
ansible_port=22
ansible_user=Administrator
ansible_ssh_private_key_file=/root/.ssh/id_ed25519
ansible_shell_type=powershell
ansible_shell_executable=None
ansible_ssh_common_args=-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null

[linux_clients:vars]
ansible_connection=ssh
ansible_user=dcs-user
ansible_become=yes
ansible_become_method=sudo
ansible_become_password={{ vault_ansible_become_password }}
```

## Testing Connectivity

### Test Windows Client

**Test SSH port connectivity:**

```bash
nc -zv 10.20.9.156 22
```

**Test SSH connection directly:**

```bash
ssh -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no Administrator@10.20.9.156
```

**Test with Ansible:**

```bash
sudo docker run --rm -it \
  -v "$PWD:/app" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -w /app/ansible \
  sync-ansible:latest \
  ansible -i inventory/hosts.ini windows_clients -m win_ping
```

### Test Linux Client

**Test with Ansible:**

```bash
sudo docker run --rm -it \
  -v "$PWD:/app" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -v "$HOME/.ansible_vault_pass:/vault_pass:ro" \
  -w /app/ansible \
  sync-ansible:latest \
  ansible -i inventory/hosts.ini linux_clients -m ping \
  --vault-password-file=/vault_pass
```

## Usage Examples

### Ping Test

Test connectivity to all Windows clients:

```bash
sudo docker run --rm -it \
  -v "$PWD:/app" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -w /app/ansible \
  sync-ansible:latest \
  ansible -i inventory/hosts.ini windows_clients -m win_ping
```

Test connectivity to all Linux clients:

```bash
sudo docker run --rm -it \
  -v "$PWD:/app" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -v "$HOME/.ansible_vault_pass:/vault_pass:ro" \
  -w /app/ansible \
  sync-ansible:latest \
  ansible -i inventory/hosts.ini linux_clients -m ping \
  --vault-password-file=/vault_pass
```

### Deploy Application

Install an application on Windows clients:

```bash
sudo docker run --rm -it \
  -v "$PWD:/app" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -w /app/ansible \
  sync-ansible:latest \
  ansible-playbook -i inventory/hosts.ini playbooks/master_deploy.yml \
  -e "target_host=windows_clients file_name=7zx64.exe app_state=present"
```

Install an application on Linux clients:

```bash
sudo docker run --rm -it \
  -v "$PWD:/app" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -v "$HOME/.ansible_vault_pass:/vault_pass:ro" \
  -w /app/ansible \
  sync-ansible:latest \
  ansible-playbook -i inventory/hosts.ini playbooks/master_deploy.yml \
  -e "target_host=linux_clients package_name=vlc app_state=present" \
  --vault-password-file=/vault_pass
```

## Docker Information

The Docker container includes Ansible and all required dependencies for managing:

- **Windows hosts** via OpenSSH (port 22) using SSH key authentication
- **Linux hosts** via SSH using sudo privilege escalation

**You do not need to install Ansible locally.** Ensure the Docker host has network access to all client machines.

**Docker Network:** The container uses the default bridge network (`172.17.0.0/16`). Windows firewall rules must allow connections from this subnet.

## Troubleshooting

### Windows Clients Not Connecting

**1. Check if sshd is running:**

```powershell
Get-Service sshd
netstat -an | findstr :22
```

**2. Check SSH logs:**

```powershell
Get-Content "C:\ProgramData\ssh\logs\sshd.log" -Tail 30
```

**3. Verify authorized keys file:**

```powershell
Get-Content "C:\ProgramData\ssh\administrators_authorized_keys"
icacls "C:\ProgramData\ssh\administrators_authorized_keys"
# Should only show SYSTEM and Administrators with (F) permission
```

**4. Verify sshd_config has correct AuthorizedKeysFile:**

```powershell
Get-Content "C:\ProgramData\ssh\sshd_config"
# Must contain: AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys
```

**5. Check firewall allows Docker subnet:**

```powershell
Get-NetFirewallRule -Name "OpenSSH-Ansible-SSH" | Get-NetFirewallAddressFilter
# Should include 172.17.0.0/16
```

**6. Verify Administrator account is enabled:**

```powershell
net user Administrator | findstr "Account active"
# Should show: Account active    Yes
```

**Common fix - re-run the setup script:**

```powershell
.\setup-windows-client.ps1 `
  -ControllerIP "10.20.9.154" `
  -PublicKey "ssh-ed25519 AAAA... ansible@sync"
```

### Linux Clients Not Connecting

**1. Ensure SSH server is running:**

```bash
sudo systemctl status ssh
```

**2. Check vault password file exists:**

```bash
ls -la ~/.ansible_vault_pass
```

**3. Test SSH connection manually:**

```bash
ssh dcs-user@10.20.9.154
```

**4. Verify sudo access:**

```bash
sudo -l
```

### Docker Container Fails to Start

**1. Verify the Docker daemon is running:**

```bash
sudo systemctl status docker
```

**2. Add user to docker group to avoid sudo:**

```bash
sudo usermod -aG docker $USER
newgrp docker
```

**3. Check Docker network:**

```bash
docker network inspect bridge | grep Subnet
# Should show: 172.17.0.0/16
```

### Connection Timeout

This usually means the firewall is blocking the connection. On the Windows client:

```powershell
# Update firewall to allow Docker subnet
Set-NetFirewallRule -Name "OpenSSH-Ansible-SSH" `
  -RemoteAddress @("10.20.9.154", "172.17.0.0/16")

Restart-Service sshd
```

### Permission Denied (publickey)

This means the SSH key is not being found or has wrong permissions. On Windows:

```powershell
# Fix key file permissions
icacls "C:\ProgramData\ssh\administrators_authorized_keys" /inheritance:r
icacls "C:\ProgramData\ssh\administrators_authorized_keys" /grant "SYSTEM:(F)"
icacls "C:\ProgramData\ssh\administrators_authorized_keys" /grant "Administrators:(F)"

# Verify sshd_config has AuthorizedKeysFile directive
Get-Content "C:\ProgramData\ssh\sshd_config"

Restart-Service sshd
```

## Security Considerations

1. **SSH key authentication only** - password authentication is disabled on Windows clients
2. **Firewall restricted** to controller IP and Docker subnet only
3. **Ansible Vault** used for Linux sudo password - never stored in plaintext
4. **Rotate SSH keys** regularly and update `administrators_authorized_keys` on all clients
5. **Use dedicated service accounts** with minimal required permissions where possible

# Project Structure
```text
sync/
├── ansible/
│   ├── inventory/
│   │   └── group_vars/
│   │       └── windows_clients/
│   └── playbooks/
│       └── master_deploy_v2.yml
├── app/
│   ├── assets/
│   │   ├── icon.ico
│   │   ├── icon.png
│   │   └── pc2.png
│   ├── core/
│   │   ├── ansible_worker.py
│   │   ├── app_state.py
│   │   ├── config.py
│   │   ├── inventory_manager.py
│   │   └── __init__.py
│   ├── ui/
│   │   ├── theme.py
│   │   └── __init__.py
│   ├── views/
│   │   ├── dialogs/
│   │   │   ├── add_pc_dialog.py
│   │   │   ├── bulk_ip_dialog.py
│   │   │   ├── confirm_delete_dialog.py
│   │   │   ├── create_lab_dialog.py
│   │   │   ├── dialog_base.py
│   │   │   ├── edit_pc_ip_dialog.py
│   │   │   └── glass_messagebox.py
│   │   ├── widgets/
│   │   │   └── pc_card.py
│   │   ├── action_forms.py
│   │   ├── create_lab_dialog.py
│   │   ├── dashboard_page.py
│   │   ├── lab_edit_page.py
│   │   ├── lab_page.py
│   │   ├── software_controller.py
│   │   ├── software_page.py
│   │   ├── software_theme.py
│   │   ├── software_widgets.py
│   │   └── welcome_page.py
│   ├── main.py
│   └── __init__.py
├── data/
│   └── inventory.json
├── software_repo/
│   └── jdk-25_windows-x64_bin.msi
├── ansible.cfg
├── build.bat
├── build.sh
├── Dockerfile
├── LICENSE
├── README.md
├── requirements-docker.txt
├── requirements-gui.txt
├── run.ps1
├── run.sh
└── setup-openssh-ansible.ps1

```

# Contributors

[Add contribution guidelines here]

# Contact Information



# License

[Add your license information here]