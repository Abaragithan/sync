from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QFrame, QGridLayout, QScrollArea, QMenu, QMessageBox, QDialog,
    QStyledItemDelegate, QListView, QStyleOptionViewItem, QLineEdit,
    QFormLayout, QDialogButtonBox
)
from PySide6.QtCore import Signal, Qt, QRect, QSize, QEvent
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QStyle

from .widgets.pc_card import PcCard
from .dialogs.edit_pc_ip_dialog import EditPcIpDialog


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


class AddPcDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add PC")
        self.setMinimumSize(420, 200)
        self.setObjectName("CreateLabDialog")

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setSpacing(12)
        form.setContentsMargins(20, 20, 20, 0)

        self.name_in = QLineEdit()
        self.name_in.setPlaceholderText("e.g., PC-106")
        self.ip_in = QLineEdit()
        self.ip_in.setPlaceholderText("e.g., 192.168.132.250")

        form.addRow("PC Name:", self.name_in)
        form.addRow("IP Address:", self.ip_in)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self):
        return self.name_in.text().strip(), self.ip_in.text().strip()


class BulkIpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bulk IP Assign")
        self.setMinimumSize(420, 180)
        self.setObjectName("CreateLabDialog")

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        form = QFormLayout()
        form.setSpacing(12)
        form.setContentsMargins(20, 20, 20, 0)

        self.start_ip = QLineEdit()
        self.start_ip.setPlaceholderText("e.g., 192.168.132.101")
        form.addRow("Starting IP:", self.start_ip)
        layout.addLayout(form)

        hint = QLabel("This will assign IPs sequentially to all PCs in this lab.")
        hint.setObjectName("DialogHintText")
        layout.addWidget(hint)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def value(self):
        return self.start_ip.text().strip()


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
        self.back_btn.setObjectName("SecondaryBtn")
        self.back_btn.setFixedWidth(90)
        self.back_btn.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(self.back_btn)

        self.title = QLabel("Edit Lab")
        self.title.setObjectName("PageTitle")
        header_layout.addWidget(self.title)

        header_layout.addStretch()
        root.addLayout(header_layout)

        # --- Controls Row ---
        controls = QHBoxLayout()
        controls.setSpacing(5)

        controls.addWidget(QLabel("Lab:"))

        self.lab_combo = LabComboBox()
        self.lab_combo.currentTextChanged.connect(self._on_lab_changed)
        self.lab_combo.edit_requested.connect(self._edit_lab_from_popup)
        self.lab_combo.delete_requested.connect(self._delete_lab_from_popup)
        controls.addWidget(self.lab_combo)

        controls.addStretch()

        # Edit-specific buttons
        self.add_btn = QPushButton("➕ Add PC")
        self.add_btn.clicked.connect(self._add_pc)
        controls.addWidget(self.add_btn)

        self.remove_btn = QPushButton("🗑 Remove PC")
        self.remove_btn.clicked.connect(self._remove_pc)
        controls.addWidget(self.remove_btn)

        self.bulk_btn = QPushButton("🔁 Bulk IP Assign")
        self.bulk_btn.clicked.connect(self._bulk_ip_assign)
        controls.addWidget(self.bulk_btn)

        self.edit_ip_btn = QPushButton("✏ Edit IP")
        self.edit_ip_btn.clicked.connect(self._edit_ip)
        controls.addWidget(self.edit_ip_btn)

        root.addLayout(controls)

        # --- Scroll Area ---
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea{border:none;}")

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

    def _refresh_lab_list(self):
        """Refresh the dropdown list of all labs"""
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

        if QMessageBox.question(self, "Delete Lab", f"Delete lab '{lab}' completely?") != QMessageBox.Yes:
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
        """Load and display a specific lab's PCs"""
        print(f"[EDIT] Loading lab: {lab_name}")
        self.state.current_lab = lab_name
        self.state.selected_targets.clear()
        
        self._clear_sections()
        
        self.title.setText(f"Edit Lab – {lab_name}")
        self.lab_name_lbl.setText(f"📁 {lab_name}")
        
        # Update combo box to match
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

        # Get the actual number of sections from the layout
        num_sections = layout.get("sections", 1)
        print(f"[EDIT] Lab has {num_sections} sections")
        
        self.wrap_layout.addStretch(1)

        # Create ONLY the sections that actually exist in the layout
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

        # Group PCs by section first
        pcs_by_section = {}
        for pc in pcs:
            section = pc.get("section", 1)
            if section not in pcs_by_section:
                pcs_by_section[section] = []
            pcs_by_section[section].append(pc)
        
        print(f"[EDIT] PCs grouped into sections: {list(pcs_by_section.keys())}")
        
        # Add PC cards to their respective sections
        pc_count = 0
        for section_num in range(1, num_sections + 1):
            if section_num in pcs_by_section:
                section_pcs = pcs_by_section[section_num]
                
                # Sort PCs by row and column for consistent display
                section_pcs.sort(key=lambda x: (x.get("row", 1), x.get("col", 1)))
                
                for pc in section_pcs:
                    if not pc.get('ip'):
                        continue
                        
                    card = PcCard(pc.get("name", "PC"), pc.get("ip", ""))
                    card.setFixedSize(60, 60)

                    # Store PC data in the card
                    card.pc_data = pc
                    card.pc_ip = pc.get('ip', '')
                    card.pc_name = pc.get('name', 'PC')

                    card.toggled.connect(self._on_toggle)
                    card.delete_requested.connect(lambda ip=pc["ip"]: self._remove_pc_by_ip(ip))

                    self.cards_by_ip[pc["ip"]] = card

                    # Get the grid for this section (0-indexed)
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
        """Basic IP validation"""
        if not ip:
            return False
        parts = ip.split('.')
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
        """Single selection mode - only one PC can be selected at a time"""
        if selected:
            # Deselect all other cards
            for card_ip, card in self.cards_by_ip.items():
                if card_ip != ip:
                    try:
                        card.set_selected(False)
                    except:
                        pass
            
            # Add to selection
            self.state.selected_targets = [ip]  # Only keep the selected one
        else:
            # Remove from selection
            if ip in self.state.selected_targets:
                self.state.selected_targets.remove(ip)

    # -------- Add PC --------
    def _add_pc(self):
        """Add a new PC to the lab"""
        if not self.state.current_lab:
            QMessageBox.warning(self, "No Lab", "Load a lab first.")
            return

        dlg = AddPcDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return

        name, ip = dlg.values()
        
        # Validate IP format
        if not self._is_valid_ip(ip):
            QMessageBox.warning(self, "Add PC Failed", "Invalid IP address format.")
            return
        
        # Get the lab layout
        layout = self.inventory_manager.get_lab_layout(self.state.current_lab)
        if not layout:
            QMessageBox.warning(self, "Add PC Failed", "Lab layout not found.")
            return
        
        # Check for duplicate IP
        pcs = self.inventory_manager.get_pcs_for_lab(self.state.current_lab)
        for pc in pcs:
            if pc.get('ip') == ip:
                QMessageBox.warning(self, "Add PC Failed", f"Duplicate IP: {ip} already exists in this lab.")
                return
        
        # Find the next available position
        used_positions = set()
        for pc in pcs:
            used_positions.add((pc.get('section', 1), pc.get('row', 1), pc.get('col', 1)))
        
        # Find first empty position
        section = 1
        row = 1
        col = 1
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
            QMessageBox.warning(self, "Add PC Failed", "No available position in this lab.")
            return
        
        # Generate name if not provided
        if not name:
            name = f"PC-{ip.split('.')[-1]}"
        
        # Create PC dictionary with all required fields
        new_pc = {
            "name": name,
            "ip": ip,
            "section": section,
            "row": row,
            "col": col
        }
        
        # Add the PC
        try:
            success = self.inventory_manager.add_pc(self.state.current_lab, new_pc)
            if not success:
                QMessageBox.warning(self, "Add PC Failed", "Failed to add PC. Possible duplicate IP.")
                return
        except Exception as e:
            QMessageBox.warning(self, "Add PC Failed", f"Error adding PC: {str(e)}")
            return

        # Clear selection and reload the lab
        self.state.selected_targets.clear()
        self.load_lab(self.state.current_lab)
        
        QMessageBox.information(self, "Success", f"PC {name} added successfully at Section {section}, Row {row}, Col {col}.")

    # -------- Remove PC --------
    def _remove_pc(self):
        """Remove selected PC"""
        if not self.state.selected_targets:
            QMessageBox.warning(self, "Remove PC", "Select a PC first.")
            return

        ip = self.state.selected_targets[0]

        if QMessageBox.question(self, "Remove PC", f"Remove PC with IP {ip}?") != QMessageBox.Yes:
            return

        self.inventory_manager.remove_pc(self.state.current_lab, ip)
        self.state.selected_targets.clear()
        self.load_lab(self.state.current_lab)

    def _remove_pc_by_ip(self, ip):
        """Remove PC by IP (called from card delete button)"""
        if QMessageBox.question(self, "Remove PC", f"Remove PC with IP {ip}?") != QMessageBox.Yes:
            return

        self.inventory_manager.remove_pc(self.state.current_lab, ip)
        if ip in self.state.selected_targets:
            self.state.selected_targets.remove(ip)
        self.load_lab(self.state.current_lab)

    # -------- Bulk IP Assign --------
    def _bulk_ip_assign(self):
        """Bulk assign IPs to all PCs"""
        if not self.state.current_lab:
            QMessageBox.warning(self, "No Lab", "Load a lab first.")
            return

        dlg = BulkIpDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return

        start_ip = dlg.value()
        
        # Validate start IP
        if not self._is_valid_ip(start_ip):
            QMessageBox.warning(self, "Bulk Assign Failed", "Invalid IP address format.")
            return

        ok = self.inventory_manager.bulk_assign_ips(self.state.current_lab, start_ip)
        if not ok:
            QMessageBox.warning(self, "Bulk Assign Failed", "Invalid IP or conflict.")
            return

        self.state.selected_targets.clear()
        self.load_lab(self.state.current_lab)
        QMessageBox.information(self, "Success", "IP addresses assigned successfully.")

    # -------- Edit IP --------
    def _edit_ip(self):
        """Edit IP of selected PC"""
        if not self.state.selected_targets:
            QMessageBox.warning(self, "Edit IP", "Select a PC first.")
            return

        ip = self.state.selected_targets[0]
        card = self.cards_by_ip.get(ip)
        if not card:
            return

        name = card.pc_name if hasattr(card, 'pc_name') else "PC"

        dlg = EditPcIpDialog(name, ip, self)
        if dlg.exec() != QDialog.Accepted:
            return

        new_ip = dlg.new_ip
        
        # Validate new IP
        if not self._is_valid_ip(new_ip):
            QMessageBox.warning(self, "IP Error", "Invalid IP address format.")
            return

        if self.inventory_manager.update_pc_ip(self.state.current_lab, ip, new_ip):
            self.state.selected_targets.clear()
            self.load_lab(self.state.current_lab)
            QMessageBox.information(self, "Success", f"IP updated to {new_ip}.")
        else:
            QMessageBox.warning(self, "IP Error", "Invalid or duplicate IP")