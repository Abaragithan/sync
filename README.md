# Central Deployer Dashboard

A **PySide6 GUI** for running Ansible playbooks inside a Docker container. This dashboard allows managing both **Windows** and **Linux** clients from a single interface.

---

## 🚀 Setup for Team Members

### 1. Clone the repo

```bash
git clone https://github.com/abaragithan/sync.git
cd sync


docker build -t central-deployer:latest .

chmod +x ./run.sh

./run.sh


