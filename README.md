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

## Project Structure

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

```text
K. Yathusiga (2021/SP/068)
Email: yathu2708@gmail.com
- Designed user interface for lab management
- Designed user interface for individual client management
- Designed popup alerts for user actions

M. Logadharsan (2021/SP/098)
Email: dharsanmlogadharsan@gmail.com
- Clients inventory management
- Ansible to GUI integration for software management
- Created script for building desktop application

K. Abaragithan (2021/SP/061)
Email: abaragithan02@gmail.com
- Initial project structure setup and Docker configuration
- Designed user interface for software management
- Created script for Windows client configuration

Y. Karththik (2021/SP/166)
Email: karththik2503@gmail.com
- Designed user interface for lab management
- Created script for copying SSH keys in Linux machines
- Configuration and testing in lab environment

T. Pirasanthan (2021/SP/141)
Email: thangavelpirasanthan@gmail.com
- Configuration and testing in lab environment
- Documentation and maintenance of README file
```
# Contact Information



# License

```text

                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

   ```