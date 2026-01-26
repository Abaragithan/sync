import os

SERVER_IP = "192.168.132.100"
INVENTORY_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/inventory.json"))
SOFTWARE_INVENTORY = {
    "7-Zip": {"os": "windows", "file": "7z.msi", "url": "https://www.7-zip.org/a/7z2301-x64.msi", "pkg": "7-Zip"},
    "VLC": {"os": "linux", "pkg": "vlc", "url": "apt"},
    # Add more: e.g., "Chrome": {"os": "mixed", ...}
}
ACTIONS = ["install", "uninstall", "update", "verify", "rollback", "health"]
LABS = []  # Default labs
OS_OPTIONS = ["windows", "linux"]