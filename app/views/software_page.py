from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QListWidget, QListWidgetItem, QTextEdit, QFrame
)
from PySide6.QtCore import Signal, Qt
import json, os, tempfile

from core.config import SOFTWARE_INVENTORY, SERVER_IP
from core.ansible_worker import AnsibleWorker


class SoftwarePage(QWidget):
    back_to_lab = Signal()

    def __init__(self, inventory_manager, state):
        super().__init__()
        self.setObjectName("SoftwarePage")  

        self.inventory_manager = inventory_manager
        self.state = state
        self._build_ui()
        self.workers = []

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        title = QLabel("Select Software & Action")
        title.setObjectName("PageTitle")
        root.addWidget(title)

        top = QHBoxLayout()
        top.addWidget(QLabel("Operation:"))

        self.action_combo = QComboBox()
        self.action_combo.addItems(["Install", "Uninstall", "Update", "Verify", "Health Check"])
        self.action_combo.currentTextChanged.connect(self._on_action)
        top.addWidget(self.action_combo)

        top.addSpacing(16)

        self.targets_lbl = QLabel("Targets: 0")
        self.targets_lbl.setObjectName("MutedText")
        top.addWidget(self.targets_lbl)

        top.addStretch()

        back = QPushButton("← Back")
        back.setObjectName("SecondaryBtn")
        back.clicked.connect(self.back_to_lab.emit)
        top.addWidget(back)

        root.addLayout(top)

        row = QHBoxLayout()

        left = QFrame(objectName="Card")
        l = QVBoxLayout(left)

        left_header = QLabel("Repository Packages")
        left_header.setObjectName("CardHeader")
        l.addWidget(left_header)

        self.list = QListWidget()
        for name in SOFTWARE_INVENTORY:
            it = QListWidgetItem(f"📦 {name}")
            it.setData(Qt.UserRole, name)
            self.list.addItem(it)
        self.list.itemSelectionChanged.connect(self._on_software)
        l.addWidget(self.list, 1)

        self.sel_lbl = QLabel("No software selected")
        self.sel_lbl.setObjectName("StatusError")
        l.addWidget(self.sel_lbl)

        row.addWidget(left, 40)

        right = QFrame(objectName="Card")
        r = QVBoxLayout(right)

        right_header = QLabel("Deployment Summary")
        right_header.setObjectName("CardHeader")
        r.addWidget(right_header)

        self.summary = QLabel("-")
        self.summary.setObjectName("SummaryText")  # ✅ themed text
        self.summary.setWordWrap(True)
        r.addWidget(self.summary)

        self.final_btn = QPushButton("Finalize Deployment")
        self.final_btn.setObjectName("PrimaryBtn")
        self.final_btn.setEnabled(False)
        self.final_btn.clicked.connect(self._finalize)
        r.addWidget(self.final_btn)

        log_header = QLabel("Live Log")
        log_header.setObjectName("CardHeader")
        r.addWidget(log_header)

        self.console = QTextEdit()
        self.console.setObjectName("Console")
        self.console.setReadOnly(True)
        r.addWidget(self.console, 1)

        row.addWidget(right, 60)
        root.addLayout(row, 1)

    def on_page_show(self):
        self.targets_lbl.setText(f"Targets: {len(self.state.selected_targets)}")
        self._refresh_summary()
        self._update_button()

    def _on_action(self, t):
        self.state.action = t.lower()
        self._refresh_summary()

    def _on_software(self):
        items = self.list.selectedItems()
        self.state.selected_software = items[0].data(Qt.UserRole) if items else None

        if self.state.selected_software:
            self.sel_lbl.setText(f"✅ Selected: {self.state.selected_software}")
            self.sel_lbl.setObjectName("StatusSuccess")
        else:
            self.sel_lbl.setText("No software selected")
            self.sel_lbl.setObjectName("StatusError")

        # refresh style after changing objectName
        self.sel_lbl.style().unpolish(self.sel_lbl)
        self.sel_lbl.style().polish(self.sel_lbl)

        self._refresh_summary()
        self._update_button()

    def _refresh_summary(self):
        self.summary.setText(
            f"Lab: {self.state.current_lab}\n"
            f"Targets: {len(self.state.selected_targets)}\n"
            f"Action: {self.state.action.upper()}\n"
            f"Software: {self.state.selected_software or '-'}\n"
            f"Target OS: {self.state.target_os.upper()}\n"
        )

    def _update_button(self):
        self.final_btn.setEnabled(bool(self.state.selected_targets) and bool(self.state.selected_software))

    def _finalize(self):
        software_name = self.state.selected_software
        targets = self.state.selected_targets
        action = self.state.action

        if not software_name:
            self.console.append("[ERROR] Select a software package first.")
            return
        if not targets:
            self.console.append("[ERROR] Select targets first.")
            return

        app_data = SOFTWARE_INVENTORY.get(software_name, {})
        if not app_data:
            self.console.append("[ERROR] Software not found in inventory.")
            return

        self.console.append(f"[START] {action.upper()} {software_name} on {len(targets)} target(s)")

        hosts_content = "[targets]\n" + "\n".join(targets) + "\n"
        fd, hosts_path = tempfile.mkstemp(prefix="sync_hosts_", suffix=".ini")
        with os.fdopen(fd, "w") as f:
            f.write(hosts_content)

        ext_vars = {
            "server_ip": SERVER_IP,
            "file_name": app_data.get("file", ""),
            "internet_url": app_data.get("url", ""),
            "package_name": app_data.get("pkg", ""),
            "app_state": "present" if action in ("install", "update") else "absent"
        }

        ansible_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../ansible")
        playbook = os.path.join(ansible_dir, "playbooks/master_deploy.yml")

        cmd = f"ansible-playbook -i {hosts_path} {playbook} -e '{json.dumps(ext_vars)}'"

        worker = AnsibleWorker(cmd)
        self.workers.append(worker)

        worker.output_received.connect(lambda msg: self.console.append(msg))

        def _cleanup(ok, w=worker, hosts=hosts_path):
            self.console.append("[DONE] Success" if ok else "[DONE] Failed")
            try:
                if os.path.exists(hosts):
                    os.remove(hosts)
            except Exception as e:
                self.console.append(f"[WARN] Could not remove temp inventory: {e}")

            if w in self.workers:
                self.workers.remove(w)
            w.deleteLater()

        worker.finished.connect(_cleanup)
        worker.start()
