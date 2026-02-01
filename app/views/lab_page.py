from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QFrame, QGridLayout, QScrollArea, QMenu, QMessageBox, QDialog,
    QStyledItemDelegate, QListView, QStyleOptionViewItem
)
from PySide6.QtCore import Signal, Qt, QRect, QSize, QEvent
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QStyle

from .widgets.pc_card import PcCard
from .create_lab_dialog import CreateLabDialog


class LabComboDelegate(QStyledItemDelegate):
    """
    Paint each popup row as:
        Lab name .......... ✏ 🗑
    with explicit colors so it stays visible under dark themes.
    """
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


class LabPage(QWidget):
    # ---------------------------------------------------------
    # FIXED: Added the missing back_requested signal here
    # ---------------------------------------------------------
    back_requested = Signal()
    next_to_software = Signal()
    edit_lab_requested = Signal(str)

    def __init__(self, inventory_manager, state):
        super().__init__()
        self.inventory_manager = inventory_manager
        self.state = state

        self.cards_by_ip = {}
        self.part_frames = []
        self.part_grids = []

        self._build_ui()
        self._load_labs()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(15, 15, 15, 15)
        root.setSpacing(4)

        # ---------------------------------------------------------
        # FIXED: Created header_layout and arranged Back Button + Title
        # ---------------------------------------------------------
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        self.back_btn = QPushButton("← Back")
        self.back_btn.setObjectName("SecondaryBtn")
        self.back_btn.setFixedWidth(85)
        self.back_btn.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(self.back_btn)

        title = QLabel("Lab Deployment")
        title.setStyleSheet("font-size:26px; font-weight:800;")
        header_layout.addWidget(title)
        
        header_layout.addStretch() # Pushes title to the left
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

        controls.addSpacing(10)

        controls.addWidget(QLabel("Target OS:"))
        self.os_combo = QComboBox()
        self.os_combo.addItems(["Windows", "Linux"])
        self.os_combo.currentTextChanged.connect(self._on_target_os_changed)
        self.os_combo.setFixedWidth(120)
        controls.addWidget(self.os_combo)

        controls.addStretch()

        self.create_lab_btn = QPushButton("➕ Create Lab")
        self.create_lab_btn.clicked.connect(self._create_lab)
        controls.addWidget(self.create_lab_btn)

        self.select_btn = QPushButton("Select PCs")
        self.select_btn.clicked.connect(self._open_select_menu)
        controls.addWidget(self.select_btn)

        root.addLayout(controls)

        # --- Scroll Area ---
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea{border:none;}")

        self.wrap = QWidget()
        self.wrap_layout = QHBoxLayout(self.wrap)

        self.wrap_layout.setSpacing(10)                
        self.wrap_layout.setContentsMargins(0, 0, 0, 0)
        self.wrap_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.scroll.setWidget(self.wrap)
        root.addWidget(self.scroll, 1)

        # --- Footer ---
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background:#1b1b1b;
                border-radius:10px;
            }
        """)
        f = QHBoxLayout(footer)

        self.count_lbl = QLabel("No PCs selected")
        self.count_lbl.setStyleSheet("color:#ff6b6b;")
        f.addWidget(self.count_lbl)

        f.addStretch()

        self.target_os_lbl = QLabel("Target OS: WINDOWS")
        self.target_os_lbl.setStyleSheet("color:#9aa4b2;")
        f.addWidget(self.target_os_lbl)

        self.next_btn = QPushButton("Next → Software")
        self.next_btn.setEnabled(False)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background:#2563eb;
                color:white;
                padding:8px 16px;
                border-radius:8px;
                font-weight:600;
            }
            QPushButton:disabled {
                background:#334155;
                color:#94a3b8;
            }
            QPushButton:hover:!disabled {
                background:#1d4ed8;
            }
        """)
        self.next_btn.clicked.connect(self.next_to_software.emit)
        f.addWidget(self.next_btn)

        root.addWidget(footer)

    def _create_lab(self):
        dlg = CreateLabDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return

        data = dlg.get_data()
        layout = data["layout"]
        ips = data["ips"]

        pcs = []
        idx = 0
        for sec in range(1, layout["sections"] + 1):
            for r in range(1, layout["rows"] + 1):
                for c in range(1, layout["cols"] + 1):
                    pcs.append({
                        "name": f"PC-{idx+1:03d}",
                        "ip": ips[idx],
                        "section": sec,
                        "row": r,
                        "col": c
                    })
                    idx += 1

        self.inventory_manager.add_lab_with_layout(data["lab_name"], layout, pcs)
        self._load_labs()
        self.lab_combo.setCurrentText(data["lab_name"])

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

    def _render_lab(self):
        self._clear_sections()

        lab = self.state.current_lab
        layout = self.inventory_manager.get_lab_layout(lab)
        pcs = self.inventory_manager.get_pcs_for_lab(lab)

        if not layout or not pcs:
            return

        for s in range(layout["sections"]):
            frame = QFrame()
            frame.setStyleSheet("background:#1b1b1b; border-radius:12px;")

            v = QVBoxLayout(frame)

            v.setContentsMargins(10, 10, 10, 10)
            v.setSpacing(12)
            v.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

            label = QLabel(f"Section {s+1}")
            label.setStyleSheet("font-weight:700;")
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

    def _open_select_menu(self):
        if not self.cards_by_ip:
            QMessageBox.information(self, "No PCs", "No PCs loaded for this lab.")
            return

        menu = QMenu(self)
        a_all = menu.addAction("Select All")
        a_clear = menu.addAction("Clear Selection")

        act = menu.exec(self.select_btn.mapToGlobal(self.select_btn.rect().bottomLeft()))
        if act == a_all:
            for card in self.cards_by_ip.values():
                card.set_selected(True)
            self.state.selected_targets = list(self.cards_by_ip.keys())
        elif act == a_clear:
            for card in self.cards_by_ip.values():
                card.set_selected(False)
            self.state.selected_targets.clear()
        
        self._update_footer()

    def _unselect_pc(self, ip):
        card = self.cards_by_ip.get(ip)
        if card:
            card.set_selected(False)
        if ip in self.state.selected_targets:
            self.state.selected_targets.remove(ip)
        self._update_footer()

    def _on_toggle(self, ip, selected):
        if selected:
            if ip not in self.state.selected_targets:
                self.state.selected_targets.append(ip)
        else:
            if ip in self.state.selected_targets:
                self.state.selected_targets.remove(ip)
        self._update_footer()

    def _update_footer(self):
        n = len(self.state.selected_targets)
        self.next_btn.setEnabled(n > 0)
        self.count_lbl.setText(f"{n} PC(s) selected" if n else "No PCs selected")

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
                self._update_footer()

            self._load_labs()
            self.lab_combo.hidePopup()

    def _load_labs(self):
        self.lab_combo.clear()
        self.lab_combo.addItems(self.inventory_manager.get_all_labs())
        self._update_os_label()

    def _on_lab_changed(self, lab):
        self.state.current_lab = lab
        self.state.selected_targets.clear()
        self._render_lab()
        self._update_footer()

    def _on_target_os_changed(self, txt):
        self.state.target_os = "windows" if "win" in txt.lower() else "linux"
        self._update_os_label()

    def _update_os_label(self):
        self.target_os_lbl.setText(f"Target OS: {self.state.target_os.upper()}")