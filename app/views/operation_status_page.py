from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea,
    QGridLayout, QFrame
)
from PySide6.QtCore import Signal, Qt
import re

from .widgets.pc_card import PcCard


# ---------------- Visual Styles ----------------
PC_STYLES = """
#PcIdle {
    background-color: #ecf0f1;
    border: 1px solid #bdc3c7;
    border-radius: 6px;
    color: #7f8c8d;
}
#PcRun {
    background-color: #9b59b6;
    color: white;
    border-radius: 6px;
}
#PcOK {
    background-color: #2ecc71;
    color: white;
    border-radius: 6px;
}
#PcFail {
    background-color: #e74c3c;
    color: white;
    border-radius: 6px;
}
#PcUnreach {
    background-color: #3498db;
    color: white;
    border-radius: 6px;
}
#PcQueued {
    background-color: #f1c40f;
    color: #2c3e50;
    border-radius: 6px;
}
PcCard QLabel {
    background-color: transparent;
    color: inherit;
}
"""


class OperationStatusPage(QWidget):

    back_to_software = Signal()

    def __init__(self, inventory_manager, state):
        super().__init__()
        self.setObjectName("OperationStatusPage")

        self.inventory_manager = inventory_manager
        self.state = state

        self.cards_by_ip = {}
        self.part_frames = []
        self.part_grids = []

        # -------- Status Tracking --------
        self.status_counts = {
            "idle": 0,
            "queued": 0,
            "running": 0,
            "success": 0,
            "failed": 0,
            "unreachable": 0
        }
        self.current_status = {}

        self.setStyleSheet(PC_STYLES)
        self._build_ui()

    # ---------------- UI ----------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(10)

        header = QHBoxLayout()
        title_box = QVBoxLayout()

        title = QLabel("Operation Status")
        title.setObjectName("PageTitle")

        subtitle = QLabel("Live results for the selected lab deployment")
        subtitle.setObjectName("MutedText")

        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        header.addLayout(title_box)
        header.addStretch()

        back = QPushButton("← Back")
        back.setObjectName("SecondaryBtn")
        back.clicked.connect(self.back_to_software.emit)
        header.addWidget(back)

        root.addLayout(header)

        # -------- Info Row --------
        info = QFrame()
        info.setObjectName("FooterBar")

        info_lay = QHBoxLayout(info)
        info_lay.setContentsMargins(12, 10, 12, 10)
        info_lay.setSpacing(14)

        self.lab_lbl = QLabel("Lab: -")
        self.lab_lbl.setObjectName("MutedText")
        info_lay.addWidget(self.lab_lbl)

        self.action_lbl = QLabel("Action: -")
        self.action_lbl.setObjectName("MutedText")
        info_lay.addWidget(self.action_lbl)

        self.software_lbl = QLabel("Software: -")
        self.software_lbl.setObjectName("MutedText")
        info_lay.addWidget(self.software_lbl)

        info_lay.addStretch()

        # -------- Live Summary Counter --------
        self.counter_lbl = QLabel()
        self.counter_lbl.setObjectName("MutedText")
        info_lay.addWidget(self.counter_lbl)

        root.addWidget(info)
        self._refresh_counter_label()

        # -------- Scroll Area --------
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

    # ---------------- Counter Refresh ----------------
    def _refresh_counter_label(self):
        self.counter_lbl.setText(
            f"🟢 {self.status_counts['success']}   "
            f"🔴 {self.status_counts['failed']}   "
            f"🟦 {self.status_counts['unreachable']}   "
            f"🟨 {self.status_counts['queued']}   "
            f"⏳ {self.status_counts['running']}"
        )

    # ---------------- Internal Helpers ----------------
    def _clear_sections(self):
        for frame in self.part_frames:
            frame.deleteLater()

        self.part_frames.clear()
        self.part_grids.clear()
        self.cards_by_ip.clear()
        self.current_status.clear()

        for key in self.status_counts:
            self.status_counts[key] = 0

        while self.wrap_layout.count():
            item = self.wrap_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        self._refresh_counter_label()

    # ---------------- Log Parsing ----------------
    def handle_log_output(self, text: str):
        if not text:
            return

        line = text.strip()

        ip_match = re.search(r'\[([\d\.]+)\]', line)
        if not ip_match:
            return

        ip = ip_match.group(1)
        lower = line.lower()

        if "unreachable!" in lower:
            self.update_pc_status(ip, "unreachable")
            return

        if "failed!" in lower or "fatal:" in lower:
            self.update_pc_status(ip, "failed")
            return

        if line.startswith("ok: [") or line.startswith("changed: ["):
            self.update_pc_status(ip, "success")
            return

        if line.startswith("skipped: ["):
            self.update_pc_status(ip, "idle")

    # ---------------- Public API ----------------
    def load_lab(self):
        self._clear_sections()

        lab = getattr(self.state, "current_lab", "") or ""
        self.lab_lbl.setText(f"Lab: {lab or '-'}")

        action = getattr(self.state, "action", "") or ""
        self.action_lbl.setText(f"Action: {action.upper() if action else '-'}")

        sw = getattr(self.state, "selected_software", "") or ""
        self.software_lbl.setText(f"Software: {sw or '-'}")

        if not lab:
            return

        layout = self.inventory_manager.get_lab_layout(lab)
        pcs = self.inventory_manager.get_pcs_for_lab(lab)

        if not layout or not pcs:
            return

        self.wrap_layout.addStretch(1)

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

        for pc in pcs:
            card = PcCard(pc["name"], pc["ip"])
            card.setFixedSize(60, 60)

            card.setObjectName("PcIdle")
            card.style().unpolish(card)
            card.style().polish(card)

            self.cards_by_ip[pc["ip"]] = card
            self.current_status[pc["ip"]] = "idle"
            self.status_counts["idle"] += 1

            grid = self.part_grids[pc["section"] - 1]
            r = pc["row"] - 1
            c = pc["col"] - 1
            grid.addWidget(card, r, c, alignment=Qt.AlignCenter)

        self._refresh_counter_label()

    def update_pc_status(self, ip: str, status: str):
        card = self.cards_by_ip.get(ip)
        if not card:
            return

        new_status = (status or "").lower()
        old_status = self.current_status.get(ip)

        if old_status in self.status_counts:
            self.status_counts[old_status] -= 1

        if new_status in self.status_counts:
            self.status_counts[new_status] += 1

        self.current_status[ip] = new_status

        if new_status == "running":
            card.setObjectName("PcRun")
        elif new_status == "success":
            card.setObjectName("PcOK")
        elif new_status == "failed":
            card.setObjectName("PcFail")
        elif new_status == "unreachable":
            card.setObjectName("PcUnreach")
        elif new_status == "queued":
            card.setObjectName("PcQueued")
        else:
            card.setObjectName("PcIdle")

        card.style().unpolish(card)
        card.style().polish(card)

        self._refresh_counter_label()

    def reset_all(self, status: str = "idle"):
        for key in self.status_counts:
            self.status_counts[key] = 0

        self.current_status.clear()

        for ip in list(self.cards_by_ip.keys()):
            self.update_pc_status(ip, status)

        self._refresh_counter_label()

    def load_pcs(self):
        self.load_lab()