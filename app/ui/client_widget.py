from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QListWidget,
                               QListWidgetItem, QPushButton, QFrame, QInputDialog, QMessageBox,
                               QCheckBox, QScrollArea, QSizePolicy)
from PySide6.QtCore import Qt, Signal

class ClientWidget(QWidget):
    deployment_requested = Signal(dict)
    targets_updated = Signal(list, str)

    def __init__(self, inventory_manager):
        super().__init__()
        self.inventory_manager = inventory_manager
        self.selected_targets = []
        self.current_lab = ""
        self.setup_ui()
        self._load_labs()

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
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        scroll_area.setWidget(container)
        
        # Container layout
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header = QLabel("Client Management")
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: white;
                padding-bottom: 5px;
            }
        """)
        layout.addWidget(header)

        # Subtitle
        subtitle = QLabel("Select labs and PCs for deployment")
        subtitle.setStyleSheet("color: #aaa; font-size: 14px;")
        layout.addWidget(subtitle)

        # Lab Selection - Fixed height
        lab_frame = QFrame()
        lab_frame.setFixedHeight(120)
        lab_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        lab_frame.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border-radius: 10px;
                border: 1px solid #333;
            }
        """)
        lab_layout = QVBoxLayout(lab_frame)
        lab_layout.setContentsMargins(20, 20, 20, 20)
        lab_layout.setSpacing(10)
        
        lab_label = QLabel("Select Lab")
        lab_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        lab_layout.addWidget(lab_label)
        
        # Lab combo box with fixed width
        lab_combo_layout = QHBoxLayout()
        lab_combo_layout.addWidget(QLabel("Lab:"))
        self.lab_combo = QComboBox()
        self.lab_combo.setFixedWidth(250)
        self.lab_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e1e1e;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px;
                color: white;
                font-size: 14px;
                min-height: 36px;
            }
            QComboBox::drop-down {
                width: 30px;
                border-left: 1px solid #444;
            }
            QComboBox::down-arrow {
                width: 16px;
                height: 16px;
            }
            QComboBox QAbstractItemView {
                background-color: #1e1e1e;
                color: white;
                selection-background-color: #007acc;
                border: 1px solid #444;
            }
        """)
        self.lab_combo.currentTextChanged.connect(self._on_lab_changed)
        lab_combo_layout.addWidget(self.lab_combo)
        lab_combo_layout.addStretch()
        lab_layout.addLayout(lab_combo_layout)
        
        layout.addWidget(lab_frame)

        # PCs Selection - Fixed height
        pc_frame = QFrame()
        pc_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        pc_frame.setMinimumHeight(300)
        pc_frame.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border-radius: 10px;
                border: 1px solid #333;
            }
        """)
        pc_layout = QVBoxLayout(pc_frame)
        pc_layout.setContentsMargins(20, 20, 20, 20)
        pc_layout.setSpacing(15)
        
        pc_header = QHBoxLayout()
        pc_title = QLabel("Select PCs")
        pc_title.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        pc_header.addWidget(pc_title)
        
        self.select_all_checkbox = QCheckBox("Select All")
        self.select_all_checkbox.setStyleSheet("color: #aaa; font-size: 14px;")
        self.select_all_checkbox.stateChanged.connect(self._on_select_all_changed)
        pc_header.addWidget(self.select_all_checkbox)
        pc_header.addStretch()
        pc_layout.addLayout(pc_header)
        
        # Filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("OS Filter:"))
        self.os_combo = QComboBox()
        self.os_combo.setFixedWidth(120)
        self.os_combo.addItems(["All", "Windows", "Linux"])
        self.os_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e1e1e;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 6px;
                color: white;
                font-size: 14px;
            }
        """)
        self.os_combo.currentTextChanged.connect(self._filter_pcs)
        filter_layout.addWidget(self.os_combo)
        filter_layout.addStretch()
        pc_layout.addLayout(filter_layout)
        
        # PC List with fixed height
        list_frame = QFrame()
        list_frame.setStyleSheet("background-color: #1e1e1e; border-radius: 6px; border: 1px solid #444;")
        list_layout = QVBoxLayout(list_frame)
        list_layout.setContentsMargins(1, 1, 1, 1)
        
        self.pc_list = QListWidget()
        self.pc_list.setFixedHeight(180)
        self.pc_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                border: none;
                border-radius: 6px;
                color: white;
                font-size: 14px;
                outline: none;
            }
            QListWidget::item {
                padding: 10px 15px;
                border-bottom: 1px solid #333;
            }
            QListWidget::item:checked {
                background-color: rgba(0, 122, 204, 0.3);
            }
            QListWidget::item:hover {
                background-color: #2a2a2a;
            }
        """)
        self.pc_list.itemChanged.connect(self._on_pc_selection_changed)
        list_layout.addWidget(self.pc_list)
        pc_layout.addWidget(list_frame)
        
        # Add PC button
        add_btn = QPushButton("➕ Add New PC")
        add_btn.setFixedWidth(120)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #444;
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        add_btn.clicked.connect(self._add_pc)
        
        add_layout = QHBoxLayout()
        add_layout.addStretch()
        add_layout.addWidget(add_btn)
        pc_layout.addLayout(add_layout)
        
        layout.addWidget(pc_frame)

        # Action Section - Fixed height
        action_frame = QFrame()
        action_frame.setFixedHeight(180)
        action_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        action_frame.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border-radius: 10px;
                border: 1px solid #333;
            }
        """)
        action_layout = QVBoxLayout(action_frame)
        action_layout.setContentsMargins(20, 20, 20, 20)
        action_layout.setSpacing(15)
        
        action_title = QLabel("Deployment Action")
        action_title.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        action_layout.addWidget(action_title)
        
        # Action selection
        action_row = QHBoxLayout()
        action_row.addWidget(QLabel("Action:"))
        self.action_combo = QComboBox()
        self.action_combo.setFixedWidth(150)
        self.action_combo.addItems(["Install", "Uninstall", "Update", "Verify", "Health Check"])
        self.action_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e1e1e;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px;
                color: white;
                font-size: 14px;
            }
        """)
        self.action_combo.currentTextChanged.connect(self._on_action_changed)
        action_row.addWidget(self.action_combo)
        action_row.addStretch()
        action_layout.addLayout(action_row)
        
        # Selected count
        self.selection_label = QLabel("No PCs selected")
        self.selection_label.setStyleSheet("color: #ff6b6b; font-size: 14px; padding: 5px;")
        action_layout.addWidget(self.selection_label)
        
        # Deploy button
        self.deploy_btn = QPushButton("🚀 Send to Software Tab")
        self.deploy_btn.setFixedHeight(45)
        self.deploy_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                font-size: 15px;
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
            }
        """)
        self.deploy_btn.setEnabled(False)
        self.deploy_btn.clicked.connect(self._queue_deployment)
        action_layout.addWidget(self.deploy_btn)
        
        layout.addWidget(action_frame)
        layout.addStretch()
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)

    def _load_labs(self):
        """Load labs into combo box"""
        labs = self.inventory_manager.get_all_labs()
        self.lab_combo.clear()
        if labs:
            self.lab_combo.addItems(labs)
        else:
            self.lab_combo.addItem("No labs available")

    def _on_lab_changed(self, lab_name):
        """Handle lab selection change"""
        if lab_name and lab_name != "No labs available":
            self.current_lab = lab_name
            self._load_pcs()
            self._clear_selection()

    def _load_pcs(self):
        """Load PCs for current lab"""
        self.pc_list.clear()
        self.select_all_checkbox.setChecked(False)
        
        if not self.current_lab:
            return
            
        pcs = self.inventory_manager.get_pcs_for_lab(self.current_lab)
        
        if not pcs:
            item = QListWidgetItem("No PCs found in this lab")
            item.setFlags(Qt.NoItemFlags)
            item.setForeground(Qt.gray)
            self.pc_list.addItem(item)
            return
            
        for pc in pcs:
            os_icon = "🪟" if pc["os"] == "windows" else "🐧"
            item = QListWidgetItem(f"{os_icon} {pc['name']} ({pc['ip']})")
            item.setData(Qt.UserRole, pc["ip"])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.pc_list.addItem(item)

    def _filter_pcs(self):
        """Filter PCs by OS"""
        filter_os = self.os_combo.currentText().lower()
        if filter_os == "all":
            # Show all items
            for i in range(self.pc_list.count()):
                item = self.pc_list.item(i)
                item.setHidden(False)
        else:
            # Filter items
            for i in range(self.pc_list.count()):
                item = self.pc_list.item(i)
                item_text = item.text().lower()
                show_item = filter_os in item_text
                item.setHidden(not show_item)

    def _on_pc_selection_changed(self):
        """Handle PC selection changes"""
        checked_count = 0
        total_checkable = 0
        
        for i in range(self.pc_list.count()):
            item = self.pc_list.item(i)
            if item.flags() & Qt.ItemIsUserCheckable:
                total_checkable += 1
                if item.checkState() == Qt.Checked:
                    checked_count += 1
        
        # Update select all checkbox
        self.select_all_checkbox.blockSignals(True)
        if checked_count == 0:
            self.select_all_checkbox.setCheckState(Qt.Unchecked)
        elif checked_count == total_checkable:
            self.select_all_checkbox.setCheckState(Qt.Checked)
        else:
            self.select_all_checkbox.setCheckState(Qt.PartiallyChecked)
        self.select_all_checkbox.blockSignals(False)
        
        # Update selection
        self._update_selection()

    def _on_select_all_changed(self, state):
        """Handle select all checkbox"""
        for i in range(self.pc_list.count()):
            item = self.pc_list.item(i)
            if item.flags() & Qt.ItemIsUserCheckable:
                item.setCheckState(state)

    def _update_selection(self):
        """Update selected targets list"""
        self.selected_targets = []
        
        for i in range(self.pc_list.count()):
            item = self.pc_list.item(i)
            if item.checkState() == Qt.Checked:
                ip = item.data(Qt.UserRole)
                if ip:
                    self.selected_targets.append(ip)
        
        # Update UI
        if self.selected_targets:
            count = len(self.selected_targets)
            self.selection_label.setText(f"✅ {count} PC(s) selected")
            self.selection_label.setStyleSheet("color: #4ecdc4; font-size: 14px; padding: 5px;")
            self.deploy_btn.setEnabled(True)
        else:
            self.selection_label.setText("No PCs selected")
            self.selection_label.setStyleSheet("color: #ff6b6b; font-size: 14px; padding: 5px;")
            self.deploy_btn.setEnabled(False)

    def _clear_selection(self):
        """Clear current selection"""
        self.selected_targets = []
        self.selection_label.setText("No PCs selected")
        self.selection_label.setStyleSheet("color: #ff6b6b; font-size: 14px; padding: 5px;")
        self.deploy_btn.setEnabled(False)
        self.targets_updated.emit([], self.action_combo.currentText().lower())

    def _on_action_changed(self, action):
        """Handle action change"""
        if self.selected_targets:
            self.targets_updated.emit(self.selected_targets, action.lower())

    def _add_pc(self):
        """Add a new PC"""
        if not self.current_lab:
            QMessageBox.warning(self, "No Lab", "Please select a lab first.")
            return
            
        # Simple dialog for now
        ip, ok = QInputDialog.getText(self, "Add PC", "Enter IP address:")
        if ok and ip:
            pc_data = {
                "ip": ip,
                "name": f"PC-{ip.split('.')[-1]}",
                "os": "windows"
            }
            self.inventory_manager.add_pc(self.current_lab, pc_data)
            self._load_pcs()
            QMessageBox.information(self, "Success", f"PC added to {self.current_lab}!")

    def _queue_deployment(self):
        """Queue deployment to software tab"""
        if not self.selected_targets:
            QMessageBox.warning(self, "No Selection", "Please select at least one PC.")
            return
            
        action = self.action_combo.currentText().lower()
        
        # Emit signals
        self.deployment_requested.emit({
            "targets": self.selected_targets,
            "action": action
        })
        self.targets_updated.emit(self.selected_targets, action)
        
        QMessageBox.information(
            self, 
            "Deployment Queued",
            f"{len(self.selected_targets)} PC(s) sent to Software tab for {action}."
        )

    def select_all_pcs_for_lab(self, lab: str):
        """Select all PCs for a given lab"""
        if lab in [self.lab_combo.itemText(i) for i in range(self.lab_combo.count())]:
            self.lab_combo.setCurrentText(lab)
            self._load_pcs()
            
            # Check all items
            for i in range(self.pc_list.count()):
                item = self.pc_list.item(i)
                if item.flags() & Qt.ItemIsUserCheckable:
                    item.setCheckState(Qt.Checked)