# Sync Deployer

A PySide6 GUI application that triggers Ansible playbooks inside a Docker container. The dashboard provides a unified interface for managing both Windows and Linux lab machines using **OpenSSH**.

Ansible runs **only inside Docker**. No local Ansible installation is required.

---

## Setup

### 1. Clone the Repository
```bash
git clone https://github.com/abaragithan/sync.git
cd sync
```

### 2. Build the Docker Image
The Docker image contains Ansible and all required dependencies.

```bash
docker build -t sync-ansible:latest .
```

### 3. Start the Dashboard

**Linux:**
```bash
chmod +x ./run.sh
./run.sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy Bypass -File run.ps1
```

---

## Dependency Files

- **requirements-gui.txt** - GUI dependencies (PySide6). Installed locally by run.sh / run.ps1.
- **requirements-docker.txt** - Ansible and automation dependencies installed inside the Docker container.

---

## Client Configuration

### Windows Client Setup (OpenSSH)

Windows clients are managed only via OpenSSH (port 22).

1. Open PowerShell as Administrator

2. Run the setup script:
```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\setup-openssh-ansible.ps1 `
  -ControllerIP 10.20.9.154 `
  -ControllerSubnet "10.20.9.0/24" `
  -RestrictToController true
```

This script:
- Installs and enables OpenSSH Server
- Configures sshd
- Configures firewall rules for port 22
- Optionally installs an SSH public key for admin access

3. **(Recommended) Use SSH key authentication**

Generate an SSH key on the controller and pass the public key using:
```powershell
-AdminPublicKey "ssh-ed25519 AAAA... ansible-controller"
```

### Linux Client Setup

1. **Install and enable SSH:**
```bash
sudo apt update
sudo apt install openssh-server -y
sudo systemctl enable ssh
sudo systemctl start ssh
```

2. **Configure passwordless sudo (recommended):**
```bash
sudo visudo
```

Add:
```
dcs-user ALL=(ALL) NOPASSWD: ALL
```

If passwordless sudo is not allowed, use Ansible Vault (see below).

---

## Inventory Configuration

Edit `ansible/inventory/hosts.ini`:

```ini
[windows_clients]
10.20.9.156

[linux_clients]
10.20.9.154

[windows_clients:vars]
ansible_connection=ssh
ansible_user=cn\DCS
ansible_shell_type=powershell
ansible_ssh_private_key_file=~/.ssh/id_ed25519
ansible_ssh_common_args=-o StrictHostKeyChecking=no

[linux_clients:vars]
ansible_connection=ssh
ansible_user=dcs-user
ansible_become=yes
ansible_become_method=sudo
# If using vault:
# ansible_become_password={{ vault_ansible_become_password }}
```

### Optional: Ansible Vault for Linux sudo password

Only required if passwordless sudo is not enabled.

1. Create vault file:
```bash
mkdir -p ansible/inventory/group_vars/linux_clients

sudo docker run --rm -it \
  -v "$PWD:/app" \
  -w /app/ansible \
  sync-ansible:latest \
  ansible-vault create inventory/group_vars/linux_clients/vault.yml
```

2. Example vault content:
```yaml
vault_ansible_become_password: YOUR_SUDO_PASSWORD
```

3. Store the vault password locally:
```bash
echo "your-vault-password" > ~/.ansible_vault_pass
chmod 600 ~/.ansible_vault_pass
```

---

## Testing Connectivity

### Test Windows Clients (SSH + PowerShell)
```bash
sudo docker run --rm -it \
  -v "$PWD:/app" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -w /app/ansible \
  sync-ansible:latest \
  ansible -i inventory/hosts.ini windows_clients \
  -m ansible.windows.win_powershell \
  -a "script: Write-Output 'OK'"
```

### Test Linux Clients
```bash
sudo docker run --rm -it \
  -v "$PWD:/app" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -w /app/ansible \
  sync-ansible:latest \
  ansible -i inventory/hosts.ini linux_clients -m ping
```

**With vault:**
```bash
sudo docker run --rm -it \
  -v "$PWD:/app" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -v "$HOME/.ansible_vault_pass:/vault_pass:ro" \
  -w /app/ansible \
  sync-ansible:latest \
  ansible -i inventory/hosts.ini linux_clients \
  -m ping --vault-password-file=/vault_pass
```

---

## Usage Examples

### Install application on Windows
```bash
sudo docker run --rm -it \
  -v "$PWD:/app" \
  -w /app/ansible \
  sync-ansible:latest \
  ansible-playbook -i inventory/hosts.ini playbooks/master_deploy.yml \
  -e "target_host=windows_clients file_name=7zx64.exe app_state=present"
```

### Install application on Linux
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

---

## Docker Notes

- Ansible runs only inside Docker
- Default Docker bridge network: 172.17.0.0/16
- Windows firewall must allow SSH access from the controller and Docker subnet

---

## Security Recommendations

- Use SSH key authentication (disable passwords after validation)
- Restrict firewall rules to controller IP/subnet
- Use Ansible Vault for any secrets
- Use dedicated automation accounts
- Regularly rotate keys and vault passwords

---

## License

Add license information here.

## Contributing

Add contribution guidelines here.