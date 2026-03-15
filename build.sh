#!/bin/bash
set -e
echo "======================================"
echo "   SyncDeployer - Build Script"
echo "======================================"
# Navigate to project root
cd "$(dirname "$0")"
# Activate virtual environment
echo "[1/5] Activating virtual environment..."
source .venv/bin/activate
# Install/update dependencies
echo "[2/5] Installing dependencies..."
pip install -r requirements-gui.txt -q
pip install pyinstaller -q
# Clean old build
echo "[3/5] Cleaning old build..."
rm -rf build dist SyncDeployer.spec
# Build the application
echo "[4/5] Building application..."
pyinstaller --name "SyncDeployer" \
  --onefile \
  --windowed \
  --paths "app" \
  --add-data "app/assets:assets" \
  --add-data "data:data" \
  --add-data "requirements-docker.txt:." \
  --add-data "ansible.cfg:." \
  --hidden-import "core.inventory_manager" \
  --hidden-import "views.software_theme" \
  --hidden-import "views.software_widgets" \
  --hidden-import "views.software_controller" \
  --hidden-import "json" \
  app/main.py
# Create desktop shortcut with icon
echo "[5/5] Creating desktop shortcut..."
EXEC_PATH="$(pwd)/dist/SyncDeployer"
ICON_PATH="$(pwd)/app/assets/icon.png"
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/syncdeployer.desktop << EOF
[Desktop Entry]
Name=Sync Deployer
Comment=Centralized Software Deployment Tool
Exec=$EXEC_PATH
Icon=$ICON_PATH
Terminal=false
Type=Application
Categories=Network;System;
EOF
# Desktop shortcut
cp ~/.local/share/applications/syncdeployer.desktop ~/Desktop/
chmod +x ~/Desktop/syncdeployer.desktop
# Refresh icon cache
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true
gtk-update-icon-cache ~/.local/share/icons/ 2>/dev/null || true
# Make binary executable
chmod +x dist/SyncDeployer
echo ""
echo "======================================"
echo " Build complete!"
echo " Binary : $(pwd)/dist/SyncDeployer"
echo " Shortcut: ~/Desktop/syncdeployer.desktop"
echo " Run with: ./dist/SyncDeployer"
echo "======================================"