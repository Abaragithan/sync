from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QScrollArea, QComboBox, QGridLayout, QSizePolicy,
    QMessageBox, QApplication, QDialog, QMenu
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor, QPalette

from .dialogs.edit_pc_ip_dialog import EditPcIpDialog
from .dialogs.glass_messagebox import show_glass_message
from .dialogs.confirm_delete_dialog import ConfirmDeleteDialog
from .widgets.pc_card import PcCard


class LabPage(QWidget):
    back_requested = Signal()
    next_to_software = Signal()
    edit_lab_requested = Signal(str)
    delete_lab_requested = Signal(str)

    def __init__(self, inventory_manager, state=None):
        super().__init__()
        self.inventory_manager = inventory_manager
        self.state = state
        self.setObjectName("LabPage")

        self.current_lab = None
        self.pcs = []
        self.selected_pcs = set()
        
        # For tracking PC cards
        self.cards_by_ip = {}
        self.part_frames = []
        self.part_grids = []

        self._build_ui()
        self._apply_styles()
        
        # Initialize the lab selector after UI is built
        QTimer.singleShot(0, self.on_page_show)

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # ========== HEADER ==========
        header = QHBoxLayout()
        header.setSpacing(16)

        # Back button
        self.back_btn = QPushButton("← Back")
        self.back_btn.setObjectName("BackButton")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.setFixedHeight(38)
        self.back_btn.setFixedWidth(90)
        self.back_btn.clicked.connect(self.back_requested.emit)
        header.addWidget(self.back_btn)

        # Lab info
        lab_info = QVBoxLayout()
        lab_info.setSpacing(4)

        self.lab_title = QLabel("Lab Deployment")
        self.lab_title.setObjectName("PageTitle")
        self.lab_title.setFont(QFont("Segoe UI", 24, QFont.Bold))

        self.lab_subtitle = QLabel("Select a lab to begin")
        self.lab_subtitle.setObjectName("SubText")

        lab_info.addWidget(self.lab_title)
        lab_info.addWidget(self.lab_subtitle)
        header.addLayout(lab_info, 1)

        # Lab selector - FIXED version
        self.lab_combo = QComboBox()
        self.lab_combo.setObjectName("LabSelector")
        self.lab_combo.setCursor(Qt.PointingHandCursor)
        self.lab_combo.setMinimumWidth(220)
        self.lab_combo.setFixedHeight(38)
        self.lab_combo.currentTextChanged.connect(self._on_lab_changed)
        header.addWidget(self.lab_combo)

        main_layout.addLayout(header)

        # ========== MAIN CONTENT ==========
        # Scroll area with horizontal centering
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setObjectName("LabScroll")

        # Outer container for vertical centering
        self.wrap = QWidget()
        outer = QVBoxLayout(self.wrap)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        outer.addStretch(1)

        row_holder = QWidget()
        self.wrap_layout = QHBoxLayout(row_holder)
        self.wrap_layout.setSpacing(16)
        self.wrap_layout.setContentsMargins(0, 0, 0, 0)
        self.wrap_layout.setAlignment(Qt.AlignHCenter)

        outer.addWidget(row_holder, 0, Qt.AlignHCenter)
        outer.addStretch(1)

        self.scroll.setWidget(self.wrap)
        main_layout.addWidget(self.scroll, 1)

        # ========== FOOTER ==========
        footer = QFrame()
        footer.setObjectName("FooterBar")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(16, 12, 16, 12)
        footer_layout.setSpacing(16)

        # Left side - Lab action buttons
        actions = QHBoxLayout()
        actions.setSpacing(8)

        self.select_btn = QPushButton("Select PCs")
        self.select_btn.setObjectName("ActionButton")
        self.select_btn.setCursor(Qt.PointingHandCursor)
        self.select_btn.setFixedHeight(38)
        self.select_btn.clicked.connect(self._open_select_menu)
        actions.addWidget(self.select_btn)

        self.edit_lab_btn = QPushButton("✏️ Edit Lab")
        self.edit_lab_btn.setObjectName("ActionButton")
        self.edit_lab_btn.setCursor(Qt.PointingHandCursor)
        self.edit_lab_btn.setFixedHeight(38)
        self.edit_lab_btn.clicked.connect(self._edit_lab)
        actions.addWidget(self.edit_lab_btn)

        self.delete_lab_btn = QPushButton("🗑️ Delete Lab")
        self.delete_lab_btn.setObjectName("DeleteButton")
        self.delete_lab_btn.setCursor(Qt.PointingHandCursor)
        self.delete_lab_btn.setFixedHeight(38)
        self.delete_lab_btn.clicked.connect(self._confirm_delete_lab)
        actions.addWidget(self.delete_lab_btn)

        actions.addStretch()
        footer_layout.addLayout(actions, 2)

        # Center - PC count
        self.count_lbl = QLabel("No PCs selected")
        self.count_lbl.setObjectName("PCCountFooter")
        self.count_lbl.setAlignment(Qt.AlignCenter)
        footer_layout.addWidget(self.count_lbl, 1)

        # Right side - Next button
        right_actions = QHBoxLayout()
        right_actions.setSpacing(12)

        self.next_btn = QPushButton("Next → Software")
        self.next_btn.setObjectName("PrimaryButton")
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.setFixedHeight(42)
        self.next_btn.setFixedWidth(150)
        self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(self.next_to_software.emit)
        right_actions.addWidget(self.next_btn)

        footer_layout.addLayout(right_actions, 1)

        main_layout.addWidget(footer)

    def _apply_styles(self):
        """Apply light theme styles"""
        self.setStyleSheet("""
            /* Page Title */
            QLabel#PageTitle {
                color: #0f172a;
                font-size: 24px;
                font-weight: 800;
                background: transparent;
            }
            
            QLabel#SubText {
                color: #475569;
                font-size: 14px;
                background: transparent;
            }
            
            /* Section Cards */
            QFrame#SectionCard {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin: 0px;
            }
            
            QLabel#SectionTitle {
                color: #0f172a;
                font-size: 16px;
                font-weight: 700;
                padding: 8px 0px;
                background: transparent;
            }
            
            /* Footer Bar */
            QFrame#FooterBar {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
            
            /* Action Buttons */
            QPushButton#ActionButton {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
                color: #0f172a;
            }
            
            QPushButton#ActionButton:hover {
                background-color: #f8fafc;
                border: 1px solid #2563eb;
            }
            
            QPushButton#ActionButton:pressed {
                background-color: #f1f5f9;
            }
            
            /* Delete Button */
            QPushButton#DeleteButton {
                background-color: #ffffff;
                border: 1px solid #ef4444;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
                color: #ef4444;
            }
            
            QPushButton#DeleteButton:hover {
                background-color: #fef2f2;
                border: 1px solid #dc2626;
                color: #dc2626;
            }
            
            QPushButton#DeleteButton:pressed {
                background-color: #fee2e2;
            }
            
            /* Primary Button */
            QPushButton#PrimaryButton {
                background-color: #2563eb;
                border: none;
                border-radius: 8px;
                color: #ffffff;
                font-size: 14px;
                font-weight: 700;
            }
            
            QPushButton#PrimaryButton:hover {
                background-color: #1d4ed8;
            }
            
            QPushButton#PrimaryButton:pressed {
                background-color: #1e40af;
            }
            
            QPushButton#PrimaryButton:disabled {
                background-color: #cbd5e1;
                color: #64748b;
            }
            
            /* Back Button */
            QPushButton#BackButton {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                color: #0f172a;
            }
            
            QPushButton#BackButton:hover {
                background-color: #f8fafc;
                border: 1px solid #2563eb;
            }
            
            /* Lab Selector - FIXED for better visibility */
            QComboBox#LabSelector {
                background-color: #ffffff;
                border: 1px solid #2563eb;
                border-radius: 8px;
                padding: 8px 16px;
                color: #0f172a;
                font-size: 14px;
                font-weight: 500;
                min-width: 220px;
            }
            
            QComboBox#LabSelector:hover {
                border: 2px solid #2563eb;
                background-color: #f8fafc;
            }
            
            QComboBox#LabSelector::drop-down {
                border: none;
                width: 30px;
            }
            
            QComboBox#LabSelector::down-arrow {
                image: none;
                width: 0px;
            }
            
            QComboBox#LabSelector QAbstractItemView {
                background-color: #ffffff;
                border: 1px solid #2563eb;
                border-radius: 8px;
                padding: 4px;
                outline: none;
            }
            
            QComboBox#LabSelector QAbstractItemView::item {
                padding: 10px 16px;
                border-radius: 4px;
                color: #0f172a;
                font-size: 13px;
                min-height: 30px;
            }
            
            QComboBox#LabSelector QAbstractItemView::item:selected {
                background-color: #eff6ff;
                color: #2563eb;
            }
            
            QComboBox#LabSelector QAbstractItemView::item:hover {
                background-color: #f8fafc;
            }
            
            /* Footer PC count */
            QLabel#PCCountFooter {
                color: #0f172a;
                font-size: 14px;
                font-weight: 600;
                background: transparent;
            }
            
            /* Scroll Area */
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            
            QScrollBar:vertical {
                background-color: #f1f5f9;
                width: 8px;
                border-radius: 4px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #cbd5e1;
                border-radius: 4px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #94a3b8;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

    def _clear_sections(self):
        """Clear all section frames and cards"""
        for frame in self.part_frames:
            frame.deleteLater()
        self.part_frames.clear()
        self.part_grids.clear()
        self.cards_by_ip.clear()

        while self.wrap_layout.count():
            item = self.wrap_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _render_lab(self):
        """Render PCs organized by sections"""
        self._clear_sections()

        if not self.current_lab:
            # Show empty state
            empty_label = QLabel("Select a lab to view workstations")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #94a3b8; font-size: 14px; padding: 40px;")
            self.wrap_layout.addWidget(empty_label)
            return

        layout = self.inventory_manager.get_lab_layout(self.current_lab)
        pcs = self.inventory_manager.get_pcs_for_lab(self.current_lab)

        if not layout or not pcs:
            empty_label = QLabel("No workstations in this lab")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #94a3b8; font-size: 14px; padding: 40px;")
            self.wrap_layout.addWidget(empty_label)
            return

        self.wrap_layout.addStretch(1)

        # Create section frames
        for s in range(layout["sections"]):
            frame = QFrame()
            frame.setObjectName("SectionCard")

            v = QVBoxLayout(frame)
            v.setContentsMargins(10, 10, 10, 10)
            v.setSpacing(12)
            v.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

            label = QLabel(f"Section {s+1}")
            label.setObjectName("SectionTitle")
            label.setAlignment(Qt.AlignLeft)
            v.addWidget(label)

            grid = QGridLayout()
            grid.setHorizontalSpacing(5)
            grid.setVerticalSpacing(15)
            grid.setContentsMargins(12, 12, 12, 12)

            v.addLayout(grid)

            self.part_frames.append(frame)
            self.part_grids.append(grid)
            self.wrap_layout.addWidget(frame)

        self.wrap_layout.addStretch(1)

        # Create PC cards
        for pc in pcs:
            card = PcCard(pc["name"], pc["ip"])
            card.setFixedSize(60, 60)

            card.toggled.connect(self._on_toggle)
            card.delete_requested.connect(lambda ip=pc["ip"]: self._unselect_pc(ip))

            self.cards_by_ip[pc["ip"]] = card

            grid = self.part_grids[pc["section"] - 1]
            r = pc["row"] - 1
            c = pc["col"] - 1
            grid.addWidget(card, r, c, alignment=Qt.AlignCenter)

        self._update_footer()

    def _open_select_menu(self):
        """Open selection menu for PCs"""
        if not self.cards_by_ip:
            show_glass_message(self, "No PCs", "No PCs loaded for this lab.", QMessageBox.Information)
            return

        menu = QMenu(self)
        a_all = menu.addAction("Select All")
        a_clear = menu.addAction("Clear Selection")

        act = menu.exec(self.select_btn.mapToGlobal(self.select_btn.rect().bottomLeft()))
        if act == a_all:
            for card in self.cards_by_ip.values():
                card.set_selected(True)
            self.selected_pcs = set(self.cards_by_ip.keys())
        elif act == a_clear:
            for card in self.cards_by_ip.values():
                card.set_selected(False)
            self.selected_pcs.clear()

        self._update_footer()

    def _unselect_pc(self, ip):
        """Unselect a specific PC"""
        card = self.cards_by_ip.get(ip)
        if card:
            card.set_selected(False)
        if ip in self.selected_pcs:
            self.selected_pcs.remove(ip)
        self._update_footer()

    def _on_toggle(self, ip, selected):
        """Handle PC card toggle"""
        if selected:
            self.selected_pcs.add(ip)
        else:
            if ip in self.selected_pcs:
                self.selected_pcs.remove(ip)
        self._update_footer()

    def _update_footer(self):
        """Update footer based on selection"""
        n = len(self.selected_pcs)
        self.next_btn.setEnabled(n > 0)
        self.count_lbl.setText(f"{n} PC(s) selected" if n else "No PCs selected")
        
        # Keep state in sync whenever selection changes
        if self.state:
            self.state.selected_targets = list(self.selected_pcs)
            self.state.current_lab = self.current_lab

   
    def _on_lab_changed(self, lab_name: str):
        """Handle lab selection change"""
        if not lab_name or lab_name == "No labs available":
            self.current_lab = None
            self.pcs = []
            self.selected_pcs.clear()
            self._render_lab()
            self.lab_subtitle.setText("Select a lab to begin")
            self._update_footer()
            return

        self.current_lab = lab_name
        
        # Sync lab name to state immediately
        if self.state:
            self.state.current_lab = lab_name
        
        self.pcs = self.inventory_manager.get_pcs_for_lab(lab_name) or []
        self.selected_pcs.clear()
        self._render_lab()
        self.lab_subtitle.setText(f"Managing: {lab_name}")

    def _edit_lab(self):
            """Edit current lab"""
            if self.current_lab:
                self.edit_lab_requested.emit(self.current_lab)

    def _confirm_delete_lab(self):
        """Confirm and delete current lab"""
        if not self.current_lab:
            show_glass_message(self, "No Lab Selected", "Please select a lab first", QMessageBox.Warning)
            return

        pcs = self.inventory_manager.get_pcs_for_lab(self.current_lab)
        dlg = ConfirmDeleteDialog(self, lab_name=self.current_lab, pcs_count=len(pcs))

        if dlg.exec() == QDialog.Accepted:
            if self.inventory_manager.delete_lab(self.current_lab):
                self.current_lab = None
                self.selected_pcs.clear()
                self.refresh_labs()
                self._render_lab()
                self.lab_subtitle.setText("Select a lab to begin")
                show_glass_message(self, "Deleted", f"Lab has been deleted.", QMessageBox.Information)
            else:
                show_glass_message(self, "Error", f"Failed to delete lab.", QMessageBox.Critical)

    def refresh_labs(self):
        """Refresh lab list"""
        # Store current selection to restore it later
        current_text = self.lab_combo.currentText()
        
        # Clear and repopulate
        self.lab_combo.clear()
        labs = self.inventory_manager.get_all_labs()
        
        if labs:
            self.lab_combo.addItems(labs)
            # Try to restore previous selection
            if current_text and current_text in labs:
                self.lab_combo.setCurrentText(current_text)
            elif labs:
                # If no previous selection or it's invalid, select first lab
                self.lab_combo.setCurrentIndex(0)
                # Trigger the change if this is a new selection
                if self.lab_combo.currentText() != current_text:
                    self._on_lab_changed(self.lab_combo.currentText())
        else:
            self.lab_combo.addItem("No labs available")
            self.lab_combo.setCurrentIndex(0)

    def on_page_show(self):
        """Called when page is shown - refresh the display"""
        self.refresh_labs()
        # Force the current lab to be set
        if self.current_lab:
            # Make sure the combo box shows the current lab
            index = self.lab_combo.findText(self.current_lab)
            if index >= 0:
                self.lab_combo.setCurrentIndex(index)
            else:
                # If current lab not found, clear it
                self.current_lab = None
                self._render_lab()
                self.lab_subtitle.setText("Select a lab to begin")
        else:
            # If no current lab but there are labs, select the first one
            if self.lab_combo.count() > 0 and self.lab_combo.currentText() != "No labs available":
                self.current_lab = self.lab_combo.currentText()
                self._on_lab_changed(self.current_lab)