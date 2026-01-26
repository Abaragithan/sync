from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QFrame, QGridLayout, QScrollArea, QMenu, QMessageBox
)
from PySide6.QtCore import Signal, Qt

from .widgets.pc_card import PcCard


class LabPage(QWidget):
    next_to_software = Signal()

    # 3 parts, each 7 rows × 5 cols = 35, total 105 (fits your 100~101 count too)
    PARTS = 3
    ROWS = 7
    COLS = 4
    PER_PART = ROWS * COLS

    def __init__(self, inventory_manager, state):
        super().__init__()
        self.inventory_manager = inventory_manager
        self.state = state

        self.manual_mode = True
        self.cards_by_ip = {}
        self.pcs_cache = []

        self._build_ui()
        self._load_labs()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(14)

        title = QLabel("Lab Deployment")
        title.setStyleSheet("font-size: 26px; font-weight: 800;")
        root.addWidget(title)

        # Controls row
        row = QHBoxLayout()
        row.setSpacing(12)

        row.addWidget(QLabel("Lab:"))
        self.lab_combo = QComboBox()
        self.lab_combo.currentTextChanged.connect(self._on_lab_changed)
        row.addWidget(self.lab_combo)

        row.addSpacing(16)

        # ✅ Global OS selection (dual-boot)
        row.addWidget(QLabel("Target OS:"))
        self.os_combo = QComboBox()
        self.os_combo.addItems(["Windows", "Linux"])
        self.os_combo.currentTextChanged.connect(self._on_target_os_changed)
        self.os_combo.setFixedWidth(130)
        row.addWidget(self.os_combo)

        row.addStretch()

        self.select_btn = QPushButton("Select PCs")
        self.select_btn.setStyleSheet("background:#2a2a2a;")
        self.select_btn.clicked.connect(self._open_select_menu)
        row.addWidget(self.select_btn)

        root.addLayout(row)

        # Scroll area holding 3 parts
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;}")
        wrap = QWidget()
        wrap_layout = QHBoxLayout(wrap)
        wrap_layout.setContentsMargins(0, 0, 0, 0)
        wrap_layout.setSpacing(18)

        self.part_frames = []
        self.part_grids = []

        for part_index in range(self.PARTS):
            frame = QFrame()
            frame.setObjectName("Card")
            frame.setStyleSheet("""
                QFrame#Card {
                    background-color: #1b1b1b;
                    border: 1px solid #2a2a2a;
                    border-radius: 12px;
                }
            """)
            frame_layout = QVBoxLayout(frame)
            frame_layout.setContentsMargins(14, 14, 14, 14)
            frame_layout.setSpacing(10)

            label = QLabel(f"Section {part_index + 1}")
            label.setStyleSheet("font-weight: 700; color:#cbd5e1;")
            frame_layout.addWidget(label)

            grid = QGridLayout()
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setHorizontalSpacing(10)
            grid.setVerticalSpacing(10)
            frame_layout.addLayout(grid)

            self.part_frames.append(frame)
            self.part_grids.append(grid)
            wrap_layout.addWidget(frame, 1)

        scroll.setWidget(wrap)
        root.addWidget(scroll, 1)

        # Footer
        footer = QFrame(objectName="Card")
        footer.setStyleSheet("""
            QFrame#Card {
                background-color: #1b1b1b;
                border: 1px solid #2a2a2a;
                border-radius: 12px;
            }
        """)
        lay = QHBoxLayout(footer)
        lay.setContentsMargins(16, 12, 16, 12)

        self.count_lbl = QLabel("No PCs selected")
        self.count_lbl.setStyleSheet("color:#ff6b6b;")
        lay.addWidget(self.count_lbl)

        lay.addStretch()

        self.target_os_lbl = QLabel("Target OS: WINDOWS")
        self.target_os_lbl.setStyleSheet("color:#9aa4b2;")
        lay.addWidget(self.target_os_lbl)

        lay.addSpacing(12)

        self.to_software_btn = QPushButton("Next: Select Software →")
        self.to_software_btn.setEnabled(False)
        self.to_software_btn.clicked.connect(self._stage_and_next)
        lay.addWidget(self.to_software_btn)

        root.addWidget(footer)

    def _load_labs(self):
        labs = self.inventory_manager.get_all_labs()
        self.lab_combo.clear()
        if labs:
            self.lab_combo.addItems(labs)
        else:
            self.lab_combo.addItem("No labs available")

        # default OS from state
        self.os_combo.setCurrentText("Windows" if self.state.target_os == "windows" else "Linux")
        self._update_target_os_label()

    def _on_target_os_changed(self, txt: str):
        self.state.target_os = "windows" if txt.lower().startswith("win") else "linux"
        self._update_target_os_label()

    def _update_target_os_label(self):
        self.target_os_lbl.setText(f"Target OS: {self.state.target_os.upper()}")

    def _on_lab_changed(self, lab):
        if not lab or lab == "No labs available":
            return
        self.state.current_lab = lab
        self.state.clear_targets()
        self._render_lab()
        self._update_footer()

    def _clear_all_grids(self):
        for grid in self.part_grids:
            while grid.count():
                item = grid.takeAt(0)
                w = item.widget()
                if w:
                    w.deleteLater()

    def _render_lab(self):
        self._clear_all_grids()
        self.cards_by_ip.clear()

        pcs = self.inventory_manager.get_pcs_for_lab(self.state.current_lab) or []
        self.pcs_cache = pcs

        if not pcs:
            msg = QLabel("No PCs found in this lab.")
            msg.setStyleSheet("color:#9aa4b2; padding:20px;")
            self.part_grids[0].addWidget(msg, 0, 0)
            return

        # Fill Section 1 -> Section 2 -> Section 3
        # Each section is 7x5
        for idx, pc in enumerate(pcs):
            part = idx // self.PER_PART
            if part >= self.PARTS:
                break  # ignore extra beyond 105

            within = idx % self.PER_PART
            r = within // self.COLS
            c = within % self.COLS

            name = pc.get("name") or f"PC-{idx+1:02d}"
            ip = pc.get("ip")

            card = PcCard(name=name, ip=ip)
            card.toggled.connect(self._on_card_toggled)
            card.delete_requested.connect(self._delete_pc)

            self.cards_by_ip[ip] = card
            self.part_grids[part].addWidget(card, r, c)

    def _open_select_menu(self):
        menu = QMenu(self)
        a_all = menu.addAction("Select All")
        a_clear = menu.addAction("Clear Selection")
        a_manual = menu.addAction("Manual Select")

        act = menu.exec(self.select_btn.mapToGlobal(self.select_btn.rect().bottomLeft()))
        if act == a_all:
            self.manual_mode = False
            self._select_all(True)
        elif act == a_clear:
            self._select_all(False)
        elif act == a_manual:
            self.manual_mode = True

    def _select_all(self, value: bool):
        for ip, card in self.cards_by_ip.items():
            card.set_selected(value)

    def _on_card_toggled(self, ip, selected):
        if selected:
            if ip not in self.state.selected_targets:
                self.state.selected_targets.append(ip)
        else:
            if ip in self.state.selected_targets:
                self.state.selected_targets.remove(ip)

        self._update_footer()

    def _delete_pc(self, ip):
        lab = self.state.current_lab
        ok = QMessageBox.question(self, "Delete PC", f"Remove {ip} from {lab}?")
        if ok != QMessageBox.Yes:
            return

        removed = self.inventory_manager.remove_pc(lab, ip)
        if not removed:
            QMessageBox.warning(self, "Not Found", f"{ip} was not found in {lab}.")
            return

        if ip in self.state.selected_targets:
            self.state.selected_targets.remove(ip)

        self._render_lab()
        self._update_footer()

    def _update_footer(self):
        n = len(self.state.selected_targets)
        if n == 0:
            self.count_lbl.setText("No PCs selected")
            self.count_lbl.setStyleSheet("color:#ff6b6b;")
            self.to_software_btn.setEnabled(False)
        else:
            self.count_lbl.setText(f"✅ {n} PC(s) selected")
            self.count_lbl.setStyleSheet("color:#4ecdc4;")
            self.to_software_btn.setEnabled(True)

    def _stage_and_next(self):
        # targets already staged in state.selected_targets
        self.next_to_software.emit()
