from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QListWidget, QListWidgetItem, QTextEdit, QFrame, QLineEdit, QSplitter
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
        self.workers = []

        self._all_names = list(SOFTWARE_INVENTORY.keys())
        self._build_ui()

    # ---------------- UI ----------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(14)

        # ===== Header Bar =====
        header = QFrame()
        header.setObjectName("Card")  # reuse your card styling (scoped to SoftwarePage)
        header_lay = QHBoxLayout(header)
        header_lay.setContentsMargins(14, 12, 14, 12)
        header_lay.setSpacing(12)

        title_box = QVBoxLayout()
        title = QLabel("Software Deployment")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Pick a package and run an operation on selected targets")
        subtitle.setObjectName("MutedText")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_lay.addLayout(title_box)

        header_lay.addStretch()

        self.targets_lbl = QLabel("Targets: 0")
        self.targets_lbl.setObjectName("MutedText")
        header_lay.addWidget(self.targets_lbl)

        back = QPushButton("← Back")
        back.setObjectName("SecondaryBtn")
        back.clicked.connect(self.back_to_lab.emit)
        header_lay.addWidget(back)

        root.addWidget(header)

        # ===== Action Strip =====
        action_bar = QFrame()
        action_bar.setObjectName("Card")
        ab = QHBoxLayout(action_bar)
        ab.setContentsMargins(14, 12, 14, 12)
        ab.setSpacing(12)

        op_lbl = QLabel("Operation")
        op_lbl.setObjectName("MutedText")
        ab.addWidget(op_lbl)

        self.action_combo = QComboBox()
        self.action_combo.addItems(["Install", "Uninstall", "Update", "Verify", "Health Check"])
        self.action_combo.currentTextChanged.connect(self._on_action)
        self.action_combo.setFixedWidth(220)
        ab.addWidget(self.action_combo)

        ab.addStretch()

        self.final_btn = QPushButton("Finalize Deployment")
        self.final_btn.setObjectName("PrimaryBtn")
        self.final_btn.setEnabled(False)
        self.final_btn.clicked.connect(self._finalize)
        ab.addWidget(self.final_btn)

        root.addWidget(action_bar)

        # ===== Main Split Layout =====
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        # ---------- Left Panel (Packages) ----------
        left = QFrame()
        left.setObjectName("Card")
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(14, 14, 14, 14)
        left_lay.setSpacing(10)

        left_header = QLabel("Repository Packages")
        left_header.setObjectName("CardHeader")
        left_lay.addWidget(left_header)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search packages...")
        self.search.textChanged.connect(self._filter_packages)
        left_lay.addWidget(self.search)

        self.list = QListWidget()
        self._populate_list(self._all_names)
        self.list.itemSelectionChanged.connect(self._on_software)
        left_lay.addWidget(self.list, 1)

        self.sel_lbl = QLabel("No software selected")
        self.sel_lbl.setObjectName("StatusError")
        left_lay.addWidget(self.sel_lbl)

        splitter.addWidget(left)

        # ---------- Right Panel (Summary + Logs) ----------
        right = QFrame()
        right.setObjectName("Card")
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(14, 14, 14, 14)
        right_lay.setSpacing(10)

        summary_header = QLabel("Deployment Summary")
        summary_header.setObjectName("CardHeader")
        right_lay.addWidget(summary_header)

        self.summary = QLabel("-")
        self.summary.setObjectName("SummaryText")
        self.summary.setWordWrap(True)
        right_lay.addWidget(self.summary)

        log_header = QLabel("Live Log")
        log_header.setObjectName("CardHeader")
        right_lay.addWidget(log_header)

        self.console = QTextEdit()
        self.console.setObjectName("Console")
        self.console.setReadOnly(True)
        right_lay.addWidget(self.console, 1)

        splitter.addWidget(right)

        # Make right panel wider by default
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        root.addWidget(splitter, 1)

    def _populate_list(self, names):
        self.list.clear()
        for name in names:
            it = QListWidgetItem(f"📦 {name}")
            it.setData(Qt.UserRole, name)
            self.list.addItem(it)

    def _filter_packages(self, text: str):
        t = (text or "").strip().lower()
        if not t:
            filtered = self._all_names
        else:
            filtered = [n for n in self._all_names if t in n.lower()]
        self._populate_list(filtered)

        # keep selection if still visible
        if self.state.selected_software and self.state.selected_software in filtered:
            for i in range(self.list.count()):
                item = self.list.item(i)
                if item.data(Qt.UserRole) == self.state.selected_software:
                    self.list.setCurrentItem(item)
                    break

    # ---------------- Lifecycle ----------------
    def on_page_show(self):
        self.targets_lbl.setText(f"Targets: {len(self.state.selected_targets)}")
        self._refresh_summary()
        self._update_button()

        # Sync action combo display with state (optional, no logic change)
        try:
            current = (self.state.action or "install").strip().lower()
            label = current.capitalize()
            # Special cases:
            if current == "health check":
                label = "Health Check"
            elif current == "uninstall":
                label = "Uninstall"
            elif current == "verify":
                label = "Verify"
            elif current == "update":
                label = "Update"
            elif current == "install":
                label = "Install"
            idx = self.action_combo.findText(label, Qt.MatchFixedString)
            if idx >= 0:
                self.action_combo.setCurrentIndex(idx)
        except Exception:
            pass

    # ---------------- Handlers ----------------
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

    # ---------------- Deployment (unchanged logic) ----------------
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
