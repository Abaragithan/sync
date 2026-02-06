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
3. Execute the following commands (replace IP addresses with your controller machine IP):
```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\setup-winrm-ansible.ps1 `
  -ControllerIP "10.20.9.154" `
  -ControllerSubnet "172.17.0.0/16" `
  -AllowSelfSigned "true" `
  -EnableLocalAdminWorkaround "true"
```

**Note:** The ControllerSubnet parameter includes the Docker network range to allow connections from containers.

4. Configure WinRM authentication and add domain user to Remote Management Users:
```powershell
# Relax CBT hardening for compatibility
winrm set winrm/config/service/auth '@{CbtHardeningLevel="Relaxed"}'

# Add domain user to Remote Management Users group (replace with your domain\user)
net localgroup "Remote Management Users" cn\DCS /add

# Restart WinRM service
Restart-Service WinRM

# Verify configuration
winrm get winrm/config/service/auth
winrm enumerate winrm/config/Listener
```

### Linux Client Setup

#### 1. Install SSH Server

Ensure the SSH server is installed and running on your Linux client:
```bash
sudo apt update
sudo apt install openssh-server -y
sudo systemctl enable ssh
sudo systemctl start ssh
```

#### 2. Configure Passwordless Sudo (Recommended for Automation)
```bash
sudo visudo
```

Add this line at the end:
```
dcs-user ALL=(ALL) NOPASSWD: ALL
```

Save and exit.

#### 3. Alternative: Use Ansible Vault for Sudo Password

If you prefer not to use passwordless sudo, create an encrypted vault file:
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

# Save vault password to file
echo "your-vault-password" > ~/.ansible_vault_pass
chmod 600 ~/.ansible_vault_pass
```

Then update your inventory to include:
```ini
[linux_clients:vars]
ansible_connection=ssh
ansible_user=dcs-user
ansible_become=yes
ansible_become_method=sudo
ansible_become_password={{ vault_ansible_become_password }}
```

## Inventory Configuration

Update `ansible/inventory/hosts.ini` with your client information:
```ini
[windows_clients]
10.20.9.156

[linux_clients]
10.20.9.154

[windows_clients:vars]
ansible_connection=winrm
ansible_port=5986
ansible_winrm_scheme=https
ansible_winrm_transport=ntlm
ansible_winrm_server_cert_validation=ignore
ansible_user=cn\DCS
ansible_password=CompUser123@

[linux_clients:vars]
ansible_connection=ssh
ansible_user=dcs-user
ansible_become=yes
ansible_become_method=sudo
# If using vault, add: ansible_become_password={{ vault_ansible_become_password }}
```

**Security Note:** For production environments, use Ansible Vault to encrypt sensitive credentials instead of storing them in plaintext.

## Testing Connectivity

### Test Windows Client

**Test WinRM port connectivity** (replace IP address with your Windows client IP):
```bash
curl -v -k https://10.20.9.156:5986/wsman
```

**Test with Ansible** (inside Docker container):
```bash
sudo docker run --rm -it \
  -v "$PWD:/app" \
  -w /app/ansible \
  sync-ansible:latest \
  ansible -i inventory/hosts.ini windows_clients -m win_ping
```

### Test Linux Client

**Test with Ansible** (inside Docker container):

**Without vault:**
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
  ansible -i inventory/hosts.ini linux_clients -m ping --vault-password-file=/vault_pass
```

## Usage Examples

### Ping Test

Test connectivity to Windows clients:
```bash
sudo docker run --rm -it \
  -v "$PWD:/app" \
  -w /app/ansible \
  sync-ansible:latest \
  ansible -i inventory/hosts.ini windows_clients -m win_ping
```

Test connectivity to Linux clients:
```bash
sudo docker run --rm -it \
  -v "$PWD:/app" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -w /app/ansible \
  sync-ansible:latest \
  ansible -i inventory/hosts.ini linux_clients -m ping
```

### Deploy Application

Install an application on Windows clients:
```bash
sudo docker run --rm -it \
  -v "$PWD:/app" \
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

- Windows hosts via WinRM over HTTPS (port 5986)
- Linux hosts via SSH

**You do not need to install Ansible locally.** Ensure the Docker host has network access to all client machines.

**Docker Network:** The container uses the default bridge network (172.17.0.0/16). Ensure Windows firewall rules allow connections from this subnet.

## Troubleshooting

### Windows Clients Not Connecting

**1. Check if WinRM is running:**
```powershell
Get-Service WinRM
winrm enumerate winrm/config/listener
```

**2. Verify authentication settings:**
```powershell
winrm get winrm/config/service/auth
# Should show: Negotiate = true, Kerberos = true
# CBT should be Relaxed (not Strict)
```

**3. Check firewall rules:**
```powershell
Get-NetFirewallRule -Name "WinRM-HTTPS-Ansible" | Get-NetFirewallAddressFilter
# Should include Docker subnet: 172.17.0.0/16
```

**4. Verify user is in Remote Management Users group:**
```powershell
net localgroup "Remote Management Users"
```

**5. Test local WinRM:**
```powershell
Test-WSMan -ComputerName localhost -Port 5986 -UseSSL
```

**Common fixes:**
```powershell
# Relax CBT hardening
winrm set winrm/config/service/auth '@{CbtHardeningLevel="Relaxed"}'

# Update firewall to allow Docker network
Set-NetFirewallRule -Name "WinRM-HTTPS-Ansible" -RemoteAddress "10.20.9.154","172.17.0.0/16"

# Restart WinRM
Restart-Service WinRM
```

### Linux Clients Not Connecting

**1. Ensure the SSH server is running:**
```bash
sudo systemctl status ssh
```

**2. Verify SSH keys are properly configured:**
```bash
# Check if SSH key exists
ls -la ~/.ssh/id_rsa*

# Test SSH connection manually
ssh dcs-user@10.20.9.154
```

**3. Check sudo configuration:**
```bash
sudo -l
# Should show NOPASSWD for ALL commands if configured
```

**4. Missing sudo password error:**

If you get "Missing sudo password" error, either:
- Configure passwordless sudo (recommended): Add `dcs-user ALL=(ALL) NOPASSWD: ALL` to `/etc/sudoers`
- Or use Ansible Vault to encrypt the sudo password (see Linux Client Setup section)

### Docker Container Fails to Start

**1. Verify the Docker daemon is running:**
```bash
sudo systemctl status docker
```

**2. If Docker is running but commands fail, add your user to the docker group:**
```bash
sudo usermod -aG docker $USER
newgrp docker
```

**3. Check Docker network:**
```bash
docker network inspect bridge
# Verify the subnet is 172.17.0.0/16
```

### Connection Reset by Peer Error

This error typically indicates:
- Firewall blocking the connection
- CBT hardening set to "Strict" instead of "Relaxed"
- Certificate issues

**Solutions:**
1. Verify firewall allows Docker subnet (172.17.0.0/16)
2. Set CBT to Relaxed: `winrm set winrm/config/service/auth '@{CbtHardeningLevel="Relaxed"}'`
3. Restart WinRM service after changes

## Security Considerations

### Production Recommendations

1. **Use Ansible Vault** for all sensitive credentials:
```bash
# Create vault for Windows credentials
sudo docker run --rm -it \
  -v "$PWD:/app" \
  -w /app/ansible \
  sync-ansible:latest \
  bash -c 'ansible-vault create inventory/group_vars/windows_clients/vault.yml'
```

2. **Use proper CA-signed certificates** instead of self-signed certificates for WinRM HTTPS

3. **Restrict firewall rules** to specific IP addresses instead of broad subnets

4. **Use dedicated service accounts** with minimal required permissions

5. **Regularly rotate credentials** and vault passwords

6. **Enable audit logging** on both Windows and Linux clients

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]