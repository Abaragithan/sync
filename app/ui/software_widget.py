from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, 
                               QListWidgetItem, QTextEdit, QFrame, QPushButton, QSizePolicy, QScrollArea)
from PySide6.QtCore import Qt, Signal
import json
import os

from core.config import SOFTWARE_INVENTORY, SERVER_IP
from core.ansible_worker import AnsibleWorker

class SoftwareWidget(QWidget):
    def __init__(self, inventory_manager):
        super().__init__()
        self.inventory_manager = inventory_manager
        self.current_targets = []
        self.current_action = "install"
        self.selected_software = None
        self.setup_ui()

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        # Container widget
        container = QWidget()
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        scroll_area.setWidget(container)
        
        # Container layout with grid
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(25, 25, 25, 25)
        container_layout.setSpacing(25)

        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border-radius: 12px;
                border: 1px solid #333;
            }
        """)
        header_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        header_frame.setFixedHeight(100)
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(25, 15, 25, 15)
        
        title = QLabel("Software Deployment")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: white;
            }
        """)
        
        subtitle = QLabel("Select software and deploy to selected targets")
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #aaa;
                padding-top: 5px;
            }
        """)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        container_layout.addWidget(header_frame)

        # Main Content Grid
        content_grid = QHBoxLayout()
        content_grid.setSpacing(25)
        content_grid.setContentsMargins(0, 0, 0, 0)

        # Left Panel: Software (40%)
        software_panel = self.create_software_panel()
        content_grid.addWidget(software_panel, 40)

        # Right Panel: Targets (60%)
        targets_panel = self.create_targets_panel()
        content_grid.addWidget(targets_panel, 60)

        container_layout.addLayout(content_grid)

        # Console Panel
        console_panel = self.create_console_panel()
        container_layout.addWidget(console_panel)

        container_layout.addStretch()
        main_layout.addWidget(scroll_area)

    def create_software_panel(self):
        """Create software selection panel"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border-radius: 12px;
                border: 1px solid #333;
            }
        """)
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("📦 Available Software")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        layout.addWidget(header)
        
        # Instructions
        instructions = QLabel("Click to select software for deployment")
        instructions.setStyleSheet("color: #aaa; font-size: 13px;")
        layout.addWidget(instructions)
        
        # Software List
        self.software_list = QListWidget()
        self.software_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #444;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                outline: none;
                padding: 5px;
            }
            QListWidget::item {
                padding: 12px 15px;
                border-radius: 6px;
                margin: 2px;
                border: 1px solid transparent;
            }
            QListWidget::item:selected {
                background-color: rgba(0, 122, 204, 0.2);
                border: 1px solid #007acc;
            }
            QListWidget::item:hover {
                background-color: #2a2a2a;
                border: 1px solid #555;
            }
        """)
        self.software_list.setSelectionMode(QListWidget.SingleSelection)
        self.software_list.itemSelectionChanged.connect(self._on_software_selected)
        
        # Add software items
        for software_name in SOFTWARE_INVENTORY:
            item = QListWidgetItem(f"📦 {software_name}")
            item.setData(Qt.UserRole, software_name)
            self.software_list.addItem(item)
        
        layout.addWidget(self.software_list, 1)  # Stretch factor
        
        # Selection Status
        self.software_status = QLabel("No software selected")
        self.software_status.setStyleSheet("color: #ff6b6b; font-size: 13px; padding: 10px;")
        layout.addWidget(self.software_status)
        
        return panel

    def create_targets_panel(self):
        """Create targets display panel"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border-radius: 12px;
                border: 1px solid #333;
            }
        """)
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("🎯 Selected Targets")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        layout.addWidget(header)
        
        # Status labels
        self.targets_status = QLabel("Waiting for targets from Client tab...")
        self.targets_status.setStyleSheet("color: #ff6b6b; font-size: 13px;")
        layout.addWidget(self.targets_status)
        
        self.action_label = QLabel("Action: None")
        self.action_label.setStyleSheet("color: #aaa; font-size: 13px;")
        layout.addWidget(self.action_label)
        
        # Targets List
        self.targets_list = QListWidget()
        self.targets_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                border: 2px dashed #444;
                border-radius: 8px;
                color: #888;
                font-size: 14px;
                padding: 10px;
                min-height: 150px;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid #333;
            }
        """)
        
        # Placeholder item
        placeholder = QListWidgetItem("📋 Targets will appear here when selected in Client tab")
        placeholder.setTextAlignment(Qt.AlignCenter)
        placeholder.setForeground(Qt.gray)
        placeholder.setFlags(Qt.NoItemFlags)
        self.targets_list.addItem(placeholder)
        
        layout.addWidget(self.targets_list, 1)  # Stretch factor
        
        # Deploy Button (Centered)
        deploy_layout = QHBoxLayout()
        deploy_layout.setContentsMargins(0, 10, 0, 0)
        
        self.deploy_button = QPushButton("🚀 Deploy Selected Software")
        self.deploy_button.setMinimumHeight(45)
        self.deploy_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.deploy_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                font-size: 15px;
                padding: 0 30px;
            }
            QPushButton:hover {
                background-color: #0099ff;
            }
            QPushButton:pressed {
                background-color: #005a99;
            }
            QPushButton:disabled {
                background-color: #444;
                color: #888;
                cursor: not-allowed;
            }
        """)
        self.deploy_button.setEnabled(False)
        self.deploy_button.clicked.connect(self.deploy_selected_software)
        
        deploy_layout.addStretch()
        deploy_layout.addWidget(self.deploy_button)
        deploy_layout.addStretch()
        layout.addLayout(deploy_layout)
        
        return panel

    def create_console_panel(self):
        """Create console panel"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border-radius: 12px;
                border: 1px solid #333;
            }
        """)
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        panel.setMinimumHeight(250)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("📋 Deployment Log")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        layout.addWidget(header)
        
        # Console
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #444;
                border-radius: 8px;
                color: #ffffff;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                padding: 10px;
                selection-background-color: #007acc;
            }
        """)
        self.console.append("[INFO] Ready. Select targets in Client tab, then select software here.")
        layout.addWidget(self.console, 1)  # Stretch factor
        
        # Clear button
        clear_layout = QHBoxLayout()
        clear_layout.setContentsMargins(0, 5, 0, 0)
        
        clear_btn = QPushButton("🗑️ Clear Log")
        clear_btn.setMinimumHeight(35)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #555;
                border: none;
                border-radius: 6px;
                color: white;
                font-size: 13px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)
        clear_btn.clicked.connect(self.console.clear)
        
        clear_layout.addStretch()
        clear_layout.addWidget(clear_btn)
        layout.addLayout(clear_layout)
        
        return panel

    def _on_software_selected(self):
        """Handle software selection"""
        selected_items = self.software_list.selectedItems()
        if selected_items:
            self.selected_software = selected_items[0].data(Qt.UserRole)
            self.software_status.setText(f"✅ Selected: {self.selected_software}")
            self.software_status.setStyleSheet("color: #4ecdc4; font-size: 13px; padding: 10px;")
        else:
            self.selected_software = None
            self.software_status.setText("No software selected")
            self.software_status.setStyleSheet("color: #ff6b6b; font-size: 13px; padding: 10px;")
        
        self.update_deploy_button_state()

    def handle_deployment(self, data):
        """Handle deployment data from client tab"""
        targets = data.get("targets", [])
        action = data.get("action", "install")
        
        if not targets:
            self.console.append("[ERROR] No targets received!")
            return
            
        self.update_targets_display(targets, action)
        self.console.append(f"[INFO] Received {len(targets)} target(s) from Client tab")

    def update_targets_display(self, targets, action):
        """Update the targets display"""
        self.current_targets = targets
        self.current_action = action
        
        # Update UI
        self.targets_list.clear()
        
        if not targets:
            self.targets_status.setText("❌ No targets selected")
            self.targets_status.setStyleSheet("color: #ff6b6b; font-size: 13px;")
            self.action_label.setText("Action: None")
            
            placeholder = QListWidgetItem("📋 No targets selected")
            placeholder.setTextAlignment(Qt.AlignCenter)
            placeholder.setForeground(Qt.gray)
            placeholder.setFlags(Qt.NoItemFlags)
            self.targets_list.addItem(placeholder)
        else:
            self.targets_status.setText(f"✅ {len(targets)} target(s) ready")
            self.targets_status.setStyleSheet("color: #4ecdc4; font-size: 13px;")
            self.action_label.setText(f"Action: {action.upper()}")
            
            for ip in targets:
                item = QListWidgetItem(f"🎯 {ip}")
                item.setForeground(Qt.white)
                self.targets_list.addItem(item)
        
        self.update_deploy_button_state()

    def update_deploy_button_state(self):
        """Update deploy button state"""
        has_targets = len(self.current_targets) > 0
        has_software = self.selected_software is not None
        
        self.deploy_button.setEnabled(has_targets and has_software)
        
        if not has_targets:
            self.deploy_button.setText("Select targets in Client tab first")
        elif not has_software:
            self.deploy_button.setText("Select software to deploy")
        else:
            self.deploy_button.setText(f"🚀 Deploy to {len(self.current_targets)} target(s)")

    def deploy_selected_software(self):
        """Deploy selected software"""
        if not self.selected_software:
            self.console.append("[ERROR] No software selected!")
            return
            
        if not self.current_targets:
            self.console.append("[ERROR] No targets selected!")
            return
            
        self.start_deployment(self.selected_software, self.current_targets, self.current_action)

    def start_deployment(self, software_name, targets, action):
        """Start deployment process"""
        self.console.append(f"\n{'='*60}")
        self.console.append(f"[START] Deployment started")
        self.console.append(f"        Software: {software_name}")
        self.console.append(f"        Targets: {len(targets)}")
        self.console.append(f"        Action: {action.upper()}")
        self.console.append(f"{'='*60}\n")
        
        app_data = SOFTWARE_INVENTORY.get(software_name, {})
        if not app_data:
            self.console.append(f"[ERROR] Software '{software_name}' not found!")
            return
        
        for ip in targets:
            self.deploy_to_target(ip, software_name, app_data, action)

    def deploy_to_target(self, ip, software_name, app_data, action):
        """Deploy to a single target"""
        try:
            self.console.append(f"[EXEC] {action.upper()} {software_name} on {ip}...")
            
            ext_vars = {
                "target_host": ip,
                "server_ip": SERVER_IP,
                "file_name": app_data.get("file", ""),
                "internet_url": app_data.get("url", ""),
                "package_name": app_data.get("pkg", ""),
                "app_state": "present" if action == "install" else "absent"
            }
            
            # Create inventory
            ansible_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../ansible")
            hosts_path = os.path.join(ansible_dir, "inventory/hosts.ini")
            os.makedirs(os.path.dirname(hosts_path), exist_ok=True)
            
            with open(hosts_path, 'w') as f:
                f.write("[targets]\n")
                f.write(f"{ip}\n")
            
            # Run Ansible
            cmd = f"ansible-playbook -i {hosts_path} playbooks/master_deploy.yml -e '{json.dumps(ext_vars)}'"
            worker = AnsibleWorker(cmd)
            worker.output_received.connect(lambda msg: self.console.append(f"[{ip}] {msg}"))
            
            def on_finished(success, ip=ip, software=software_name):
                if success:
                    self.console.append(f"[SUCCESS] {software} on {ip} completed")
                else:
                    self.console.append(f"[FAILED] {software} on {ip} failed")
            
            worker.finished.connect(on_finished)
            worker.start()
            
        except Exception as e:
            self.console.append(f"[ERROR] Failed to deploy to {ip}: {str(e)}")