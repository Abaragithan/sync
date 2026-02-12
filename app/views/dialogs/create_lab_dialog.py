from __future__ import annotations

import ipaddress
from dataclasses import dataclass

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QSizePolicy, QLineEdit, QSpinBox
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve


@dataclass
class CreateLabResult:
    lab_name: str
    layout: dict
    ips: list[str]


class CreateLabDialog(QDialog):
    """
    Modern Create Lab dialog (Delete-dialog-like):
    - Frameless + translucent background
    - Rounded black card
    - Title + subtitle
    - Form rows with clean inputs
    - IP range is TYPEABLE (start IP + end IP)
    - Live validation + warning pill
    - Fade-in animation
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CreateLabDialog")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setModal(True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self._result: CreateLabResult | None = None

        self._build_ui()
        self._wire_signals()
        self._animate_in()
        self._validate_live()  # initial state

    # ---------------- UI ----------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.card = QFrame(self)
        self.card.setObjectName("CreateLabCard")
        self.card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(self.card)
        layout.setContentsMargins(26, 24, 26, 20)
        layout.setSpacing(16)

        # Header
        title = QLabel("Create New Laboratory")
        title.setObjectName("CreateLabTitle")
        title.setTextFormat(Qt.PlainText)
        layout.addWidget(title)

        subtitle = QLabel("Set layout and enter an IP range for workstation generation.")
        subtitle.setObjectName("CreateLabSubtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # Divider
        divider = QFrame()
        divider.setObjectName("CreateLabDivider")
        divider.setFixedHeight(2)
        layout.addWidget(divider)

        # Form container
        form = QVBoxLayout()
        form.setSpacing(12)

        # Lab name row
        form.addWidget(self._row_label("Lab Name", "CreateLabRowLabel"))
        self.lab_name = QLineEdit()
        self.lab_name.setObjectName("CreateLabInput")
        self.lab_name.setPlaceholderText("e.g. CSL 1 & 2")
        form.addWidget(self.lab_name)

        # Layout row
        form.addWidget(self._row_label("Layout", "CreateLabRowLabel"))
        layout_row = QHBoxLayout()
        layout_row.setSpacing(10)

        self.sections = self._chip_spin("Sections", 1, 50, 3)
        self.rows = self._chip_spin("Rows", 1, 50, 7)
        self.cols = self._chip_spin("Cols", 1, 50, 5)

        layout_row.addWidget(self.sections.container)
        layout_row.addWidget(self.rows.container)
        layout_row.addWidget(self.cols.container)

        form.addLayout(layout_row)

        # IP range row (TYPEABLE)
        form.addWidget(self._row_label("IP Range", "CreateLabRowLabel"))
        ip_row = QHBoxLayout()
        ip_row.setSpacing(10)

        self.ip_start = QLineEdit()
        self.ip_start.setObjectName("CreateLabInput")
        self.ip_start.setPlaceholderText("Start IP (e.g. 192.168.10.1)")

        mid = QLabel("—")
        mid.setObjectName("CreateLabDash")
        mid.setAlignment(Qt.AlignCenter)
        mid.setFixedWidth(16)

        self.ip_end = QLineEdit()
        self.ip_end.setObjectName("CreateLabInput")
        self.ip_end.setPlaceholderText("End IP (e.g. 192.168.10.99)")

        ip_row.addWidget(self.ip_start, 1)
        ip_row.addWidget(mid)
        ip_row.addWidget(self.ip_end, 1)

        form.addLayout(ip_row)

        layout.addLayout(form)

        # Warning pill (like delete dialog)
        self.warn = QFrame()
        self.warn.setObjectName("CreateLabWarningPill")
        wlay = QHBoxLayout(self.warn)
        wlay.setContentsMargins(12, 10, 12, 10)
        wlay.setSpacing(10)

        self.warn_icon = QLabel("⚠️")
        self.warn_icon.setObjectName("CreateLabWarningIcon")
        self.warn_icon.setFixedWidth(22)
        self.warn_icon.setAlignment(Qt.AlignCenter)

        self.warn_text = QLabel("")
        self.warn_text.setObjectName("CreateLabWarningText")
        self.warn_text.setWordWrap(True)

        wlay.addWidget(self.warn_icon)
        wlay.addWidget(self.warn_text, 1)
        layout.addWidget(self.warn)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("CreateLabCancelBtn")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setFixedHeight(42)
        self.cancel_btn.setFixedWidth(110)

        self.create_btn = QPushButton("Create Lab")
        self.create_btn.setObjectName("CreateLabPrimaryBtn")
        self.create_btn.setCursor(Qt.PointingHandCursor)
        self.create_btn.setFixedHeight(42)
        self.create_btn.setFixedWidth(150)

        btn_row.addWidget(self.cancel_btn)
        btn_row.addWidget(self.create_btn)

        layout.addLayout(btn_row)

        root.addWidget(self.card)

        # size similar to delete dialog
        self.setFixedWidth(640)

    def _row_label(self, text: str, obj: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName(obj)
        return lbl

    def _chip_spin(self, caption: str, mn: int, mx: int, value: int):
        container = QFrame()
        container.setObjectName("CreateLabChip")
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        lay = QHBoxLayout(container)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(10)

        cap = QLabel(caption)
        cap.setObjectName("CreateLabChipLabel")

        sp = QSpinBox()
        sp.setObjectName("CreateLabSpin")
        sp.setRange(mn, mx)
        sp.setValue(value)
        sp.setButtonSymbols(QSpinBox.NoButtons)
        sp.setFixedWidth(56)
        sp.setAlignment(Qt.AlignCenter)

        lay.addWidget(cap)
        lay.addStretch()
        lay.addWidget(sp)

        # simple holder
        container.spin = sp
        return type("SpinWrap", (), {"container": container, "spin": sp})

    def _wire_signals(self):
        self.cancel_btn.clicked.connect(self.reject)
        self.create_btn.clicked.connect(self._on_create)

        self.lab_name.textChanged.connect(self._validate_live)
        self.ip_start.textChanged.connect(self._validate_live)
        self.ip_end.textChanged.connect(self._validate_live)

        self.sections.spin.valueChanged.connect(self._validate_live)
        self.rows.spin.valueChanged.connect(self._validate_live)
        self.cols.spin.valueChanged.connect(self._validate_live)

    # ---------------- Validation / Data ----------------
    def _required_count(self) -> int:
        return self.sections.spin.value() * self.rows.spin.value() * self.cols.spin.value()

    def _parse_ip(self, text: str):
        text = (text or "").strip()
        if not text:
            return None
        try:
            return ipaddress.ip_address(text)
        except ValueError:
            return None

    def _ip_range_list(self) -> list[str] | None:
        s = self._parse_ip(self.ip_start.text())
        e = self._parse_ip(self.ip_end.text())
        if not s or not e:
            return None
        if s.version != e.version:
            return None

        # ensure order
        if int(s) > int(e):
            s, e = e, s

        # limit to something safe (avoid UI freeze if someone enters huge range)
        max_generate = 5000
        total = int(e) - int(s) + 1
        if total > max_generate:
            return []  # signal "too big"
        return [str(ipaddress.ip_address(int(s) + i)) for i in range(total)]

    def _validate_live(self):
        need = self._required_count()

        name_ok = bool(self.lab_name.text().strip())

        ip_list = self._ip_range_list()
        ip_ok = ip_list is not None and ip_list != []
        too_big = (ip_list == [])

        if too_big:
            self.warn.show()
            self.warn_text.setText("IP range is too large. Please use a smaller range (max 5000 IPs).")
            self.create_btn.setEnabled(False)
            return

        if not name_ok:
            self.warn.show()
            self.warn_text.setText("Please enter a lab name.")
            self.create_btn.setEnabled(False)
            return

        if ip_list is None:
            self.warn.show()
            self.warn_text.setText("Enter a valid start and end IP address.")
            self.create_btn.setEnabled(False)
            return

        have = len(ip_list)
        if have < need:
            self.warn.show()
            self.warn_text.setText(f"Not enough IPs. Need {need}, but range gives {have}.")
            self.create_btn.setEnabled(False)
            return

        # OK
        self.warn.hide()
        self.create_btn.setEnabled(True)

    def _on_create(self):
        self._validate_live()
        if not self.create_btn.isEnabled():
            return

        ips_full = self._ip_range_list() or []
        need = self._required_count()

        self._result = CreateLabResult(
            lab_name=self.lab_name.text().strip(),
            layout={
                "sections": self.sections.spin.value(),
                "rows": self.rows.spin.value(),
                "cols": self.cols.spin.value(),
            },
            ips=ips_full[:need],
        )
        self.accept()

    # public API (same “style” as your current usage)
    def get_data(self) -> dict:
        """
        Returns same structure you already use in DashboardPage:
        { lab_name: str, layout: {sections,rows,cols}, ips: [..] }
        """
        if not self._result:
            return {"lab_name": "", "layout": {"sections": 1, "rows": 1, "cols": 1}, "ips": []}
        return {
            "lab_name": self._result.lab_name,
            "layout": self._result.layout,
            "ips": self._result.ips,
        }

    # ---------------- Anim ----------------
    def _animate_in(self):
        self.setWindowOpacity(0.0)
        self._fade = QPropertyAnimation(self, b"windowOpacity")
        self._fade.setDuration(180)
        self._fade.setStartValue(0.0)
        self._fade.setEndValue(1.0)
        self._fade.setEasingCurve(QEasingCurve.OutCubic)
        self._fade.start()
