from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QFrame, QGridLayout, QScrollArea, QMessageBox, QDialog,
    QStyledItemDelegate, QListView, QStyleOptionViewItem, QLineEdit,
    QFormLayout, QDialogButtonBox
)
from PySide6.QtCore import Signal, Qt, QRect, QSize, QEvent
from PySide6.QtGui import QPainter, QColor
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

        bg_normal = QColor("#111827")
        bg_hover = QColor("#1f2937")
        bg_selected = QColor("#2563eb")
        text_normal = QColor("#e5e7eb")
        text_selected = QColor("#ffffff")
        icon_color = QColor("#e5e7eb")

        is_selected = bool(option.state & QStyle.State_Selected)
        is_hover = bool(option.state & QStyle.State_MouseOver)

        if is_selected:
            painter.fillRect(rect, bg_selected)
        elif is_hover:
            painter.fillRect(rect, bg_hover)
        else:
            painter.fillRect(rect, bg_normal)

        right_padding = (self.btn_size * 2) + (self.gap * 3)
        text_rect = QRect(
            rect.left() + 12,
            rect.top(),
            rect.width() - right_padding,
            rect.height()
        )

        painter.setPen(text_selected if is_selected else text_normal)
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, lab)

        edit_rect = self.edit_rect(rect)
        del_rect = self.delete_rect(rect)

        painter.setPen(icon_color)
        painter.drawText(edit_rect, Qt.AlignCenter, "✏")
        painter.drawText(del_rect, Qt.AlignCenter, "🗑")

        painter.restore()

    def edit_rect(self, rect: QRect) -> QRect:
        x = rect.right() - (self.btn_size * 2) - (self.gap * 2)
        y = rect.top() + (rect.height() - self.btn_size) // 2
        return QRect(x, y, self.btn_size, self.btn_size)

    def delete_rect(self, rect: QRect) -> QRect:
        x = rect.right() - self.btn_size - self.gap
        y = rect.top() + (rect.height() - self.btn_size) // 2
        return QRect(x, y, self.btn_size, self.btn_size)


class LabComboBox(QComboBox):
    edit_requested = Signal(str)
    delete_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._view = QListView()
        self.setView(self._view)

        self._delegate = LabComboDelegate(self)
        self.setItemDelegate(self._delegate)

        self._view.setStyleSheet("""
            QListView {
                background: #111827;
                color: #e5e7eb;
                border: 1px solid #334155;
                outline: none;
            }
        """)

        self._view.viewport().installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self._view.viewport() and event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            pos = event.position().toPoint() if hasattr(event, "position") else event.pos()

            index = self._view.indexAt(pos)
            if not index.isValid():
                return False

            rect = self._view.visualRect(index)
            edit_rect = self._delegate.edit_rect(rect)
            del_rect = self._delegate.delete_rect(rect)
            lab = index.data(Qt.DisplayRole)

            if edit_rect.contains(pos):
                self.edit_requested.emit(lab)
                return True

            if del_rect.contains(pos):
                self.delete_requested.emit(lab)
                return True

            return False

        return super().eventFilter(obj, event)


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
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(6)

        # --- Header ---
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        self.back_btn = QPushButton("← Back")
        self.back_btn.setObjectName("BackBtn")
        self.back_btn.setFixedWidth(90)
        self.back_btn.setFixedHeight(36)
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(self.back_btn)

        self.title = QLabel("Edit Lab")
        self.title.setObjectName("PageTitle")
        header_layout.addWidget(self.title)

        header_layout.addStretch()
        root.addLayout(header_layout)

        # --- Controls Row ---
        controls = QHBoxLayout()
        controls.setSpacing(8)

        controls.addWidget(QLabel("Lab:"))

        self.lab_combo = LabComboBox()
        self.lab_combo.setMinimumWidth(200)
        self.lab_combo.setFixedHeight(36)
        self.lab_combo.currentTextChanged.connect(self._on_lab_changed)
        self.lab_combo.edit_requested.connect(self._edit_lab_from_popup)
        self.lab_combo.delete_requested.connect(self._delete_lab_from_popup)
        controls.addWidget(self.lab_combo)

        controls.addStretch()

        # Edit-specific buttons with distinct colors
        self.add_btn = QPushButton("➕ Add PC")
        self.add_btn.setObjectName("AddPcBtn")
        self.add_btn.setFixedHeight(36)
        self.add_btn.setMinimumWidth(100)
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.clicked.connect(self._add_pc)
        controls.addWidget(self.add_btn)

        self.remove_btn = QPushButton("🗑 Remove PC")
        self.remove_btn.setObjectName("RemovePcBtn")
        self.remove_btn.setFixedHeight(36)
        self.remove_btn.setMinimumWidth(100)
        self.remove_btn.setCursor(Qt.PointingHandCursor)
        self.remove_btn.clicked.connect(self._remove_pc)
        controls.addWidget(self.remove_btn)

        self.bulk_btn = QPushButton("🔁 Bulk IP")
        self.bulk_btn.setObjectName("BulkIpBtn")
        self.bulk_btn.setFixedHeight(36)
        self.bulk_btn.setMinimumWidth(100)
        self.bulk_btn.setCursor(Qt.PointingHandCursor)
        self.bulk_btn.clicked.connect(self._bulk_ip_assign)
        controls.addWidget(self.bulk_btn)

        self.edit_ip_btn = QPushButton("✏ Edit IP")
        self.edit_ip_btn.setObjectName("EditIpBtn")
        self.edit_ip_btn.setFixedHeight(36)
        self.edit_ip_btn.setMinimumWidth(100)
        self.edit_ip_btn.setCursor(Qt.PointingHandCursor)
        self.edit_ip_btn.clicked.connect(self._edit_ip)
        controls.addWidget(self.edit_ip_btn)

        root.addLayout(controls)

        # --- Scroll Area ---
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea{border:none;}")

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
        root.addWidget(self.scroll, 1)

        # --- Footer ---
        footer = QFrame()
        footer.setObjectName("FooterBar")
        f = QHBoxLayout(footer)

        self.lab_name_lbl = QLabel("No lab loaded")
        self.lab_name_lbl.setObjectName("SubText")
        f.addWidget(self.lab_name_lbl)

        f.addStretch()
        root.addWidget(footer)

        # Apply button styles
        self._apply_button_styles()

    def _apply_button_styles(self):
        """Apply distinct colors for each button in both dark and light modes"""
        theme = getattr(self.state, "theme", "dark")
        
        if theme == "light":
            # Light mode styles
            self.setStyleSheet("""
                /* Back button - neutral */
                QPushButton#BackBtn {
                    background-color: #f1f5f9;
                    border: 1px solid #cbd5e1;
                    border-radius: 8px;
                    color: #334155;
                    font-weight: 600;
                }
                QPushButton#BackBtn:hover {
                    background-color: #e2e8f0;
                    border: 1px solid #94a3b8;
                }
                QPushButton#BackBtn:pressed {
                    background-color: #cbd5e1;
                }
                
                /* Add PC button - green */
                QPushButton#AddPcBtn {
                    background-color: #10b981;
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-weight: 600;
                }
                QPushButton#AddPcBtn:hover {
                    background-color: #059669;
                }
                QPushButton#AddPcBtn:pressed {
                    background-color: #047857;
                }
                
                /* Remove PC button - red */
                QPushButton#RemovePcBtn {
                    background-color: #ef4444;
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-weight: 600;
                }
                QPushButton#RemovePcBtn:hover {
                    background-color: #dc2626;
                }
                QPushButton#RemovePcBtn:pressed {
                    background-color: #b91c1c;
                }
                
                /* Bulk IP button - purple */
                QPushButton#BulkIpBtn {
                    background-color: #8b5cf6;
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-weight: 600;
                }
                QPushButton#BulkIpBtn:hover {
                    background-color: #7c3aed;
                }
                QPushButton#BulkIpBtn:pressed {
                    background-color: #6d28d9;
                }
                
                /* Edit IP button - blue */
                QPushButton#EditIpBtn {
                    background-color: #3b82f6;
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-weight: 600;
                }
                QPushButton#EditIpBtn:hover {
                    background-color: #2563eb;
                }
                QPushButton#EditIpBtn:pressed {
                    background-color: #1d4ed8;
                }
                
                /* Lab combo box */
                QComboBox {
                    background-color: white;
                    border: 1px solid #cbd5e1;
                    border-radius: 8px;
                    padding: 6px 12px;
                    color: #0f172a;
                }
                QComboBox:hover {
                    border: 1px solid #94a3b8;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 24px;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 5px solid #64748b;
                    width: 0;
                    height: 0;
                }
                
                /* Footer */
                QFrame#FooterBar {
                    background-color: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 10px;
                }
                QLabel#SubText {
                    color: #64748b;
                }
            """)
        else:
            # Dark mode styles
            self.setStyleSheet("""
                /* Back button - neutral dark */
                QPushButton#BackBtn {
                    background-color: #2d3a4f;
                    border: 1px solid #475569;
                    border-radius: 8px;
                    color: #e2e8f0;
                    font-weight: 600;
                }
                QPushButton#BackBtn:hover {
                    background-color: #334155;
                    border: 1px solid #64748b;
                }
                QPushButton#BackBtn:pressed {
                    background-color: #1e293b;
                }
                
                /* Add PC button - green */
                QPushButton#AddPcBtn {
                    background-color: #10b981;
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-weight: 600;
                }
                QPushButton#AddPcBtn:hover {
                    background-color: #34d399;
                }
                QPushButton#AddPcBtn:pressed {
                    background-color: #059669;
                }
                
                /* Remove PC button - red */
                QPushButton#RemovePcBtn {
                    background-color: #ef4444;
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-weight: 600;
                }
                QPushButton#RemovePcBtn:hover {
                    background-color: #f87171;
                }
                QPushButton#RemovePcBtn:pressed {
                    background-color: #dc2626;
                }
                
                /* Bulk IP button - purple */
                QPushButton#BulkIpBtn {
                    background-color: #8b5cf6;
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-weight: 600;
                }
                QPushButton#BulkIpBtn:hover {
                    background-color: #a78bfa;
                }
                QPushButton#BulkIpBtn:pressed {
                    background-color: #7c3aed;
                }
                
                /* Edit IP button - blue */
                QPushButton#EditIpBtn {
                    background-color: #3b82f6;
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-weight: 600;
                }
                QPushButton#EditIpBtn:hover {
                    background-color: #60a5fa;
                }
                QPushButton#EditIpBtn:pressed {
                    background-color: #2563eb;
                }
                
                /* Lab combo box */
                QComboBox {
                    background-color: #1e293b;
                    border: 1px solid #334155;
                    border-radius: 8px;
                    padding: 6px 12px;
                    color: #e2e8f0;
                }
                QComboBox:hover {
                    border: 1px solid #475569;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 24px;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 5px solid #94a3b8;
                    width: 0;
                    height: 0;
                }
                
                /* Footer */
                QFrame#FooterBar {
                    background-color: #1e293b;
                    border: 1px solid #334155;
                    border-radius: 10px;
                }
                QLabel#SubText {
                    color: #94a3b8;
                }
            """)

    def _refresh_lab_list(self):
        self.lab_combo.clear()
        self.lab_combo.addItems(self.inventory_manager.get_all_labs())

    def _on_lab_changed(self, lab):
        if not lab:
            return
        if getattr(self.state, "current_lab", "") == lab:
            return
        self.load_lab(lab)

    def _edit_lab_from_popup(self, lab: str):
        if lab:
            self.edit_lab_requested.emit(lab)
            self.lab_combo.hidePopup()

    def _delete_lab_from_popup(self, lab: str):
        if not lab:
            return

        result = show_glass_message(
            self,
            "Delete Lab",
            f"Delete lab '{lab}' completely?",
            icon=QMessageBox.Question,
            buttons=QMessageBox.Yes | QMessageBox.No
        )

        if result != QMessageBox.Yes:
            return

        if self.inventory_manager.delete_lab(lab):
            if self.state.current_lab == lab:
                self.state.current_lab = ""
                self.state.selected_targets.clear()
                self._clear_sections()
                self.lab_name_lbl.setText("No lab loaded")
                self.title.setText("Edit Lab")

            self._refresh_lab_list()
            self.lab_combo.hidePopup()

            show_glass_message(
                self,
                "Deleted",
                f"Lab '{lab}' has been deleted.",
                icon=QMessageBox.Information
            )

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

        start_ip = dlg.value()

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