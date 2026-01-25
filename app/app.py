import sys
import subprocess
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QListWidget, QVBoxLayout, 
                             QHBoxLayout, QWidget, QLabel, QTextEdit)
from PySide6.QtCore import Qt, QThread, Signal, QEvent

# --- CONFIGURATION ---
SERVER_IP = "192.168.132.100"
INVENTORY = {
    "7-Zip": {"os": "windows", "file": "7z.msi", "url": "https://www.7-zip.org/a/7z2301-x64.msi", "pkg": "7-Zip"},
    "VLC": {"os": "linux", "pkg": "vlc", "url": "apt"},
}

class AnsibleWorker(QThread):
    output_received = Signal(str)

    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd

    def run(self):
        process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in iter(process.stdout.readline, ""):
            if line:
                self.output_received.emit(line.strip())
        process.stdout.close()
        process.wait()

# We create a custom List class to handle the "Drop" properly
class MachineList(QListWidget):
    dropped_signal = Signal(str, str) # software_name, target_text

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist"):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        # Get the name of the software being dragged
        source_item = event.source().currentItem()
        if source_item:
            software_name = source_item.text()
            # Get the machine it was dropped on
            target_item = self.itemAt(event.position().toPoint())
            if target_item:
                target_text = target_item.text()
                self.dropped_signal.emit(software_name, target_text)
                event.accept()

class ModernDeployer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gemini Central Deployer v1.0")
        self.resize(900, 600)

        layout = QVBoxLayout()
        top_split = QHBoxLayout()

        # 1. Software List (Source) - Must allow dragging
        self.soft_list = QListWidget()
        self.soft_list.setDragEnabled(True)
        self.soft_list.setDragDropMode(QListWidget.DragOnly)
        
        # POPULATE SOFTWARE LIST
        for sw_name in INVENTORY.keys():
            self.soft_list.addItem(sw_name)

        # 2. Machine List (Target) - Must allow dropping
        self.machine_list = MachineList()
        self.machine_list.setAcceptDrops(True)
        self.machine_list.setDragDropMode(QListWidget.DropOnly)
        
        # POPULATE MACHINE LIST (example - modify as needed)
        self.machine_list.addItem("192.168.132.101 - Windows Server")
        self.machine_list.addItem("192.168.132.102 - Linux Desktop")
        self.machine_list.addItem("192.168.132.103 - Windows Workstation")
        
        # CONNECT THE DROP SIGNAL
        self.machine_list.dropped_signal.connect(self.start_deployment)

        # Console
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: monospace;")

        # Layout structure with labels
        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("Software:"))
        left_panel.addWidget(self.soft_list)
        
        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("Target Fleet:"))
        right_panel.addWidget(self.machine_list)

        top_split.addLayout(left_panel)
        top_split.addLayout(right_panel)

        layout.addLayout(top_split)
        layout.addWidget(QLabel("Activity Log:"))
        layout.addWidget(self.console)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        # Initial message
        self.console.append("[READY] Drag software to target machines to deploy")

    def start_deployment(self, sw_name, target_text):
        ip = target_text.split(" ")[0]
        self.console.append(f"\n[EXEC] Deploying {sw_name} to {ip}...")
        
        app_data = INVENTORY[sw_name]
        ext_vars = {
            "target_host": ip,
            "server_ip": SERVER_IP,
            "file_name": app_data.get("file", ""),
            "internet_url": app_data["url"],
            "package_name": app_data["pkg"],
            "app_state": "present"
        }
        
        cmd = f"ansible-playbook -i hosts.ini master_deploy.yml -e '{json.dumps(ext_vars)}'"
        self.worker = AnsibleWorker(cmd)
        self.worker.output_received.connect(self.console.append)
        self.worker.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernDeployer()
    window.show()
    sys.exit(app.exec())