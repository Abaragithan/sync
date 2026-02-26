from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QFrame, QGridLayout, QScrollArea, QMessageBox, QDialog,
    QStyledItemDelegate, QListView, QStyleOptionViewItem, QLineEdit,
    QFormLayout, QDialogButtonBox
)
from PySide6.QtCore import Signal, Qt, QRect, QSize, QEvent, QTimer
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtWidgets import QStyle

from .widgets.pc_card import PcCard
from .dialogs.edit_pc_ip_dialog import EditPcIpDialog
from .dialogs.bulk_ip_dialog import BulkIpDialog
from .dialogs.add_pc_dialog import AddPcDialog
from .dialogs.glass_messagebox import show_glass_message


class LabComboDelegate(QStyledItemDelegate):
    def __init__(self, combo: "LabComboBox"):
        super().__init__(combo)
        self.combo = combo
        self.btn_size = 12
        self.gap = 8

    def sizeHint(self, option, index):
        base = super().sizeHint(option, index)
        return QSize(base.width(), max(base.height(), 34))

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        painter.save()

        lab = index.data(Qt.DisplayRole) or ""
        rect = option.rect

        # Light mode colors
        bg_normal = QColor("#f8fafc")
        bg_hover = QColor("#f1f5f9")
        bg_selected = QColor("#2563eb")
        text_normal = QColor("#0f172a")
        text_selected = QColor("#ffffff")

        is_selected = bool(option.state & QStyle.State_Selected)
        is_hover = bool(option.state & QStyle.State_MouseOver)

        if is_selected:
            painter.fillRect(rect, bg_selected)
        elif is_hover:
            painter.fillRect(rect, bg_hover)
        else:
            painter.fillRect(rect, bg_normal)

        # No right padding for icons - full width for text
        text_rect = QRect(
            rect.left() + 12,
            rect.top(),
            rect.width() - 24,
            rect.height()
        )

        painter.setPen(text_selected if is_selected else text_normal)
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, lab)

        painter.restore()


class LabComboBox(QComboBox):
    # Remove signals since we're removing edit/delete functionality
    # edit_requested = Signal(str)
    # delete_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._view = QListView()
        self.setView(self._view)

        self._delegate = LabComboDelegate(self)
        self.setItemDelegate(self._delegate)

        self._view.setStyleSheet("""
            QListView {
                background: #ffffff;
                color: #0f172a;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                outline: none;
                padding: 4px;
            }
            QListView::item {
                padding: 8px 12px;
                border-radius: 4px;
            }
            QListView::item:hover {
                background: #f8fafc;
            }
            QListView::item:selected {
                background: #eff6ff;
                color: #2563eb;
            }
        """)

        # Remove event filter since we don't need to handle icon clicks
        # self._view.viewport().installEventFilter(self)

    # Remove eventFilter method since we don't need it


class LabEditPage(QWidget):
    back_requested = Signal()
    edit_lab_requested = Signal(str)

    def __init__(self, inventory_manager, state):
        super().__init__()
        self.inventory_manager = inventory_manager
        self.state = state

        if not hasattr(self.state, "selected_targets") or self.state.selected_targets is None:
            self.state.selected_targets = []

        self.cards_by_ip = {}
        self.part_frames = []
        self.part_grids = []

        self._build_ui()
        self._refresh_lab_list()

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

        # Title
        self.title = QLabel("Edit Lab")
        self.title.setObjectName("PageTitle")
        self.title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        header.addWidget(self.title)

        header.addStretch()

        # Lab selector - SIMPLIFIED (no edit/delete icons)
        self.lab_combo = LabComboBox()
        self.lab_combo.setObjectName("LabSelector")
        self.lab_combo.setCursor(Qt.PointingHandCursor)
        self.lab_combo.setMinimumWidth(220)
        self.lab_combo.setFixedHeight(38)
        self.lab_combo.currentTextChanged.connect(self._on_lab_changed)
        # Remove connections to edit/delete signals
        # self.lab_combo.edit_requested.connect(self._edit_lab_from_popup)
        # self.lab_combo.delete_requested.connect(self._delete_lab_from_popup)
        header.addWidget(self.lab_combo)

        main_layout.addLayout(header)

        # ========== MAIN CONTENT ==========
        # Scroll area with horizontal centering
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setObjectName("EditScroll")

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

        # Left side - Action buttons (like in Lab page)
        actions = QHBoxLayout()
        actions.setSpacing(8)

        self.add_btn = QPushButton("➕ Add PC")
        self.add_btn.setObjectName("ActionButton")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setFixedHeight(38)
        self.add_btn.clicked.connect(self._add_pc)
        actions.addWidget(self.add_btn)

        self.remove_btn = QPushButton("🗑 Remove PC")
        self.remove_btn.setObjectName("DeleteButton")
        self.remove_btn.setCursor(Qt.PointingHandCursor)
        self.remove_btn.setFixedHeight(38)
        self.remove_btn.clicked.connect(self._remove_pc)
        actions.addWidget(self.remove_btn)

        self.bulk_btn = QPushButton("🔁 Bulk IP")
        self.bulk_btn.setObjectName("ActionButton")
        self.bulk_btn.setCursor(Qt.PointingHandCursor)
        self.bulk_btn.setFixedHeight(38)
        self.bulk_btn.clicked.connect(self._bulk_ip_assign)
        actions.addWidget(self.bulk_btn)

        self.edit_ip_btn = QPushButton("✏ Edit IP")
        self.edit_ip_btn.setObjectName("ActionButton")
        self.edit_ip_btn.setCursor(Qt.PointingHandCursor)
        self.edit_ip_btn.setFixedHeight(38)
        self.edit_ip_btn.clicked.connect(self._edit_ip)
        actions.addWidget(self.edit_ip_btn)

        actions.addStretch()
        footer_layout.addLayout(actions, 2)

        # Center - PC count (like in Lab page)
        self.pc_count_lbl = QLabel("0 PCs")
        self.pc_count_lbl.setObjectName("PCCountFooter")
        self.pc_count_lbl.setAlignment(Qt.AlignCenter)
        footer_layout.addWidget(self.pc_count_lbl, 1)

        # Right side - Lab info (replacing Next button)
        right_info = QHBoxLayout()
        right_info.setSpacing(8)

        self.lab_name_lbl = QLabel("No lab loaded")
        self.lab_name_lbl.setObjectName("LabInfo")
        right_info.addWidget(self.lab_name_lbl)

        footer_layout.addLayout(right_info, 1)

        main_layout.addWidget(footer)

        # Apply light mode styles
        self._apply_styles()

    def _apply_styles(self):
        """Apply light mode styles matching Lab page"""
        self.setStyleSheet("""
            /* Page Title */
            QLabel#PageTitle {
                color: #0f172a;
                font-size: 24px;
                font-weight: 800;
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
            
            /* Footer Bar - matching Lab page */
            QFrame#FooterBar {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
            
            QLabel#LabInfo {
                color: #0f172a;
                font-size: 14px;
                font-weight: 600;
                background: transparent;
            }
            
            QLabel#PCCountFooter {
                color: #0f172a;
                font-size: 14px;
                font-weight: 600;
                background: #f8fafc;
                padding: 8px 16px;
                border-radius: 20px;
            }
            
            /* Action Buttons - matching Lab page style */
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
            
            /* Delete Button - special red styling */
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
            QPushButton#BackButton:pressed {
                background-color: #f1f5f9;
            }
            
            /* Lab Selector - SIMPLIFIED like Lab page */
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

    def _refresh_lab_list(self):
        self.lab_combo.clear()
        labs = self.inventory_manager.get_all_labs()
        if labs:
            self.lab_combo.addItems(labs)
        else:
            self.lab_combo.addItem("No labs available")

    def _on_lab_changed(self, lab):
        if not lab or lab == "No labs available":
            return
        if getattr(self.state, "current_lab", "") == lab:
            return
        self.load_lab(lab)

    # Remove _edit_lab_from_popup and _delete_lab_from_popup methods
    # since they're no longer needed

    def _clear_sections(self):
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

    def load_lab(self, lab_name: str):
        print(f"[EDIT] Loading lab: {lab_name}")
        self.state.current_lab = lab_name
        self.state.selected_targets.clear()

        self._clear_sections()

        self.title.setText(f"Edit Lab – {lab_name}")
        self.lab_name_lbl.setText(f"📁 {lab_name}")

        index = self.lab_combo.findText(lab_name)
        if index >= 0 and self.lab_combo.currentIndex() != index:
            self.lab_combo.blockSignals(True)
            self.lab_combo.setCurrentIndex(index)
            self.lab_combo.blockSignals(False)

        layout = self.inventory_manager.get_lab_layout(lab_name)
        pcs = self.inventory_manager.get_pcs_for_lab(lab_name)

        print(f"[EDIT] Found {len(pcs) if pcs else 0} PCs for {lab_name}")

        if not layout or not pcs:
            print(f"[EDIT] No layout or PCs found for {lab_name}")
            empty_label = QLabel("No workstations in this lab")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #94a3b8; font-size: 14px; padding: 40px;")
            self.wrap_layout.addWidget(empty_label)
            self.pc_count_lbl.setText("0 PCs")
            return

        num_sections = layout.get("sections", 1)
        print(f"[EDIT] Lab has {num_sections} sections")

        self.wrap_layout.addStretch(1)

        for s in range(num_sections):
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

        pcs_by_section = {}
        for pc in pcs:
            section = pc.get("section", 1)
            pcs_by_section.setdefault(section, []).append(pc)

        print(f"[EDIT] PCs grouped into sections: {list(pcs_by_section.keys())}")

        pc_count = 0
        for section_num in range(1, num_sections + 1):
            if section_num not in pcs_by_section:
                continue

            section_pcs = pcs_by_section[section_num]
            section_pcs.sort(key=lambda x: (x.get("row", 1), x.get("col", 1)))

            for pc in section_pcs:
                if not pc.get("ip"):
                    continue

                card = PcCard(pc.get("name", "PC"), pc.get("ip", ""))
                card.setFixedSize(60, 60)

                card.pc_data = pc
                card.pc_ip = pc.get("ip", "")
                card.pc_name = pc.get("name", "PC")

                card.toggled.connect(self._on_toggle)
                card.delete_requested.connect(lambda ip=pc["ip"]: self._remove_pc_by_ip(ip))

                self.cards_by_ip[pc["ip"]] = card

                grid_index = section_num - 1
                if grid_index < len(self.part_grids):
                    grid = self.part_grids[grid_index]
                    r = pc.get("row", 1) - 1
                    c = pc.get("col", 1) - 1
                    grid.addWidget(card, r, c, alignment=Qt.AlignCenter)
                    pc_count += 1
                else:
                    print(f"[EDIT] Warning: Section {section_num} grid not found")

        self.pc_count_lbl.setText(f"{pc_count} PCs")
        print(f"[EDIT] Displayed {pc_count} PC cards for {lab_name}")

    def _is_valid_ip(self, ip: str) -> bool:
        if not ip:
            return False
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        for part in parts:
            if not part.isdigit():
                return False
            num = int(part)
            if num < 0 or num > 255:
                return False
        return True

    def _on_toggle(self, ip, selected):
        if selected:
            for card_ip, card in self.cards_by_ip.items():
                if card_ip != ip:
                    try:
                        card.set_selected(False)
                    except:
                        pass
            self.state.selected_targets = [ip]
        else:
            if ip in self.state.selected_targets:
                self.state.selected_targets.remove(ip)

    # -------- Add PC --------
    def _add_pc(self):
        if not self.state.current_lab:
            show_glass_message(self, "No Lab", "Load a lab first.", icon=QMessageBox.Warning)
            return

        dlg = AddPcDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return

        name, ip = dlg.values()

        if not self._is_valid_ip(ip):
            show_glass_message(self, "Add PC Failed", "Invalid IP address format.", icon=QMessageBox.Warning)
            return

        layout = self.inventory_manager.get_lab_layout(self.state.current_lab)
        if not layout:
            show_glass_message(self, "Add PC Failed", "Lab layout not found.", icon=QMessageBox.Warning)
            return

        pcs = self.inventory_manager.get_pcs_for_lab(self.state.current_lab)
        for pc in pcs:
            if pc.get("ip") == ip:
                show_glass_message(self, "Add PC Failed", f"Duplicate IP: {ip} already exists in this lab.",
                                  icon=QMessageBox.Warning)
                return

        used_positions = set()
        for pc in pcs:
            used_positions.add((pc.get("section", 1), pc.get("row", 1), pc.get("col", 1)))

        section = row = col = 1
        found = False
        for s in range(1, layout.get("sections", 1) + 1):
            for r in range(1, layout.get("rows", 1) + 1):
                for c in range(1, layout.get("cols", 1) + 1):
                    if (s, r, c) not in used_positions:
                        section, row, col = s, r, c
                        found = True
                        break
                if found:
                    break
            if found:
                break

        if not found:
            show_glass_message(self, "Add PC Failed", "No available position in this lab.", icon=QMessageBox.Warning)
            return

        if not name:
            name = f"PC-{ip.split('.')[-1]}"

        new_pc = {"name": name, "ip": ip, "section": section, "row": row, "col": col}

        try:
            success = self.inventory_manager.add_pc(self.state.current_lab, new_pc)
            if not success:
                show_glass_message(self, "Add PC Failed", "Failed to add PC. Possible duplicate IP.",
                                  icon=QMessageBox.Warning)
                return
        except Exception as e:
            show_glass_message(self, "Add PC Failed", f"Error adding PC: {str(e)}", icon=QMessageBox.Warning)
            return

        self.state.selected_targets.clear()
        self.load_lab(self.state.current_lab)

        show_glass_message(self, "Success", f"PC {name} added successfully", icon=QMessageBox.Information)

    # -------- Remove PC --------
    def _remove_pc(self):
        if not self.state.selected_targets:
            show_glass_message(self, "Remove PC", "Select a PC first.", icon=QMessageBox.Warning)
            return

        ip = self.state.selected_targets[0]

        result = show_glass_message(
            self,
            "Remove PC",
            f"Remove PC with IP {ip}?",
            icon=QMessageBox.Question,
            buttons=QMessageBox.Yes | QMessageBox.No
        )

        if result != QMessageBox.Yes:
            return

        self.inventory_manager.remove_pc(self.state.current_lab, ip)
        self.state.selected_targets.clear()
        self.load_lab(self.state.current_lab)

    def _remove_pc_by_ip(self, ip):
        result = show_glass_message(
            self,
            "Remove PC",
            f"Remove PC with IP {ip}?",
            icon=QMessageBox.Question,
            buttons=QMessageBox.Yes | QMessageBox.No
        )

        if result != QMessageBox.Yes:
            return

        self.inventory_manager.remove_pc(self.state.current_lab, ip)
        if ip in self.state.selected_targets:
            self.state.selected_targets.remove(ip)
        self.load_lab(self.state.current_lab)

    # -------- Bulk IP Assign --------
    def _bulk_ip_assign(self):
        if not self.state.current_lab:
            show_glass_message(self, "No Lab", "Load a lab first.", icon=QMessageBox.Warning)
            return

        dlg = BulkIpDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return

        start_ip = dlg.start_ip.text().strip()

        if not self._is_valid_ip(start_ip):
            show_glass_message(self, "Bulk Assign Failed", "Invalid IP address format.", icon=QMessageBox.Warning)
            return

        ok = self.inventory_manager.bulk_assign_ips(self.state.current_lab, start_ip)
        if not ok:
            show_glass_message(self, "Bulk Assign Failed", "Invalid IP or conflict.", icon=QMessageBox.Warning)
            return

        self.state.selected_targets.clear()
        self.load_lab(self.state.current_lab)

        show_glass_message(self, "Success", "IP addresses assigned successfully.", icon=QMessageBox.Information)

    # -------- Edit IP --------
    def _edit_ip(self):
        if not self.state.selected_targets:
            show_glass_message(self, "Edit IP", "Select a PC first.", icon=QMessageBox.Warning)
            return

        ip = self.state.selected_targets[0]
        card = self.cards_by_ip.get(ip)
        if not card:
            return

        name = card.pc_name if hasattr(card, "pc_name") else "PC"

        dlg = EditPcIpDialog(name, ip, self)
        if dlg.exec() != QDialog.Accepted:
            return

        new_ip = dlg.new_ip

        if not self._is_valid_ip(new_ip):
            show_glass_message(self, "IP Error", "Invalid IP address format.", icon=QMessageBox.Warning)
            return

        if self.inventory_manager.update_pc_ip(self.state.current_lab, ip, new_ip):
            self.state.selected_targets.clear()
            self.load_lab(self.state.current_lab)

            show_glass_message(self, "Success", f"IP updated to {new_ip}.", icon=QMessageBox.Information)
        else:
            show_glass_message(self, "IP Error", "Invalid or duplicate IP", icon=QMessageBox.Warning)