from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea,
    QGridLayout, QFrame
)
from PySide6.QtCore import Signal, Qt
import re  # Required for parsing the logs

from .widgets.pc_card import PcCard
import os
from app.core.ansible_worker import AnsibleWorker


# Visual Styles for PC Status
PC_STYLES = """
/* --- PC Card Colors --- */
#PcIdle {
    background-color: #ecf0f1;
    border: 1px solid #bdc3c7;
    border-radius: 6px;
    color: #7f8c8d;
}
#PcRun {
    background-color: #9b59b6; /* Purple-ish / Active */
    color: white;
    border-radius: 6px;
}
#PcOK {
    background-color: #2ecc71; /* Green / Success */
    color: white;
    border-radius: 6px;
}
#PcFail {
    background-color: #e74c3c; /* Red / Failed */
    color: white;
    border-radius: 6px;
}
#PcUnreach {
    background-color: #3498db; /* Blue / Unreachable */
    color: white;
    border-radius: 6px;
}
#PcQueued {
    background-color: #f1c40f; /* Yellow / Queued */
    color: #2c3e50;
    border-radius: 6px;
}
PcCard QLabel {
    background-color: transparent;
    color: inherit;
}
"""


class OperationStatusPage(QWidget):
    """
    Shows the lab structure and parses live logs to color PCs automatically.
    """

    back_to_software = Signal()

    def __init__(self, inventory_manager, state):
        super().__init__()
        self.setObjectName("OperationStatusPage")

        self.inventory_manager = inventory_manager
        self.state = state

        self.cards_by_ip = {}
        self.part_frames = []
        self.part_grids = []

        # Apply the color styles
        self.setStyleSheet(PC_STYLES)
        
        self._build_ui()

    # ---------------- UI ----------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(10)

        # ===== Header =====
        header = QHBoxLayout()
        header.setSpacing(10)

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

        # ===== Info Row (lab + action + software) =====
        info = QFrame()
        info.setObjectName("FooterBar")  # reuse existing bar style
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

        # small legend (text only, colors come from PC styles)
        legend = QLabel("Legend: ✅ Success  ❌ Failed  🟦 Unreachable  🟨 Queued  ⏳ Running")
        legend.setObjectName("MutedText")
        info_lay.addWidget(legend)

        root.addWidget(info)

        # ===== Scroll Area (same center layout as LabPage) =====
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

    # ---------------- Helpers ----------------
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

    # ---------------- Logic ----------------
    
    def handle_log_output(self, text: str):
        """
        Parses raw terminal output (Ansible logs) and updates PC status automatically.
        Call this whenever a new line of log arrives.
        """
        if not text:
            return

        text_lower = text.lower()

        # 1. Check for UNREACHABLE
        # Output: "fatal: [192.168.1.5]: UNREACHABLE! => ..."
        if "unreachable" in text_lower:
            match = re.search(r'\[([\d\.]+)\]', text)
            if match:
                self.update_pc_status(match.group(1), "unreachable")

        # 2. Check for FAILED
        # Output: "fatal: [192.168.1.5]: FAILED! => ..."
        elif "failed" in text_lower:
            match = re.search(r'\[([\d\.]+)\]', text)
            if match:
                self.update_pc_status(match.group(1), "failed")

        # 3. Check for SUCCESS (ok or changed)
        # Output: "ok: [192.168.1.5] => ..." or "changed: [192.168.1.5] => ..."
        elif "ok: [" in text or "changed: [" in text:
            match = re.search(r'(ok|changed): \[([\d\.]+)\]', text)
            if match:
                self.update_pc_status(match.group(2), "success")
        
        # 4. (Optional) Check for SKIPPED
        elif "skipped: [" in text:
            match = re.search(r'skipped: \[([\d\.]+)\]', text)
            if match:
                self.update_pc_status(match.group(1), "idle")

    # ---------------- Public API ----------------
    def load_lab(self):
        """
        Call this when opening the page.
        It builds the SAME structure as LabPage using current_lab layout.
        """
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

        # Create section frames + grids
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

        # Place PCs into correct section/row/col
        for pc in pcs:
            card = PcCard(pc["name"], pc["ip"])
            card.setFixedSize(60, 60)

            # default status = idle
            card.setObjectName("PcIdle")
            card.style().unpolish(card)
            card.style().polish(card)

            self.cards_by_ip[pc["ip"]] = card

            grid = self.part_grids[pc["section"] - 1]
            r = pc["row"] - 1
            c = pc["col"] - 1
            grid.addWidget(card, r, c, alignment=Qt.AlignCenter)

    def update_pc_status(self, ip: str, status: str):
        """
        Change PC color based on result.
        """
        card = self.cards_by_ip.get(ip)
        if not card:
            return

        s = (status or "").strip().lower()

        if s == "running":
            card.setObjectName("PcRun")
        elif s == "success":
            card.setObjectName("PcOK")
        elif s == "failed":
            card.setObjectName("PcFail")
        elif s == "unreachable":
            card.setObjectName("PcUnreach")   # blue
        elif s == "queued":
            card.setObjectName("PcQueued")    # yellow
        else:
            card.setObjectName("PcIdle")

        card.style().unpolish(card)
        card.style().polish(card)

    def reset_all(self, status: str = "idle"):
        """
        Set all cards to one status (useful before running again).
        """
        for ip in list(self.cards_by_ip.keys()):
            self.update_pc_status(ip, status)

    def load_pcs(self):
        # Backward compatible name
        self.load_lab()