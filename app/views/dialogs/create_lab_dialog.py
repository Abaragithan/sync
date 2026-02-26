from __future__ import annotations

import ipaddress
from dataclasses import dataclass

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QSizePolicy, QLineEdit, QSpinBox, QApplication
)
from PySide6.QtCore import Qt, QTimer, QEvent
from PySide6.QtGui import QPainter, QColor, QPen, QMouseEvent

from .dialog_base import BaseDialog, CloseButton


@dataclass
class CreateLabResult:
    lab_name: str
    layout: dict
    ips: list[str]


class CreateLabDialog(BaseDialog):
    """
    Create Lab dialog — matches glass_messagebox light theme.
    All functionality (get_data, validation, layout chips) unchanged.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CreateLabDialog")
        self.setFixedWidth(620)

        # Override any problematic attributes
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WA_OpaquePaintEvent, True)

        # Ensure the dialog can receive focus and pass it to children
        self.setFocusPolicy(Qt.StrongFocus)
        
        self._result: CreateLabResult | None = None

        self._build_ui()
        self._finish_init()
        self._wire_signals()
        self._validate_live()
        
        # Set focus to the first input field after dialog is shown
        QTimer.singleShot(150, self._set_initial_focus)

    def _set_initial_focus(self):
        """Set initial focus to the lab name input field"""
        if self.lab_name:
            self.lab_name.setFocus()
            self.lab_name.setFocusPolicy(Qt.StrongFocus)
            # Force the widget to be focusable
            self.lab_name.setEnabled(True)
            self.lab_name.setVisible(True)
            
    def eventFilter(self, obj, event):
        """Filter events to ensure focus works properly"""
        if event.type() == QEvent.MouseButtonPress:
            # Make sure clicks on the dialog background don't steal focus
            if obj is self:
                # Find the child widget under the mouse and give it focus
                child = self.childAt(self.mapFromGlobal(event.globalPos()))
                if child and hasattr(child, 'setFocus'):
                    child.setFocus()
                    return True
        return super().eventFilter(obj, event)

    def showEvent(self, event):
        """Handle show event to ensure proper focus setup"""
        super().showEvent(event)
        # Install event filter to handle focus properly
        QApplication.instance().installEventFilter(self)
        # Ensure the dialog is raised and focused
        self.raise_()
        self.activateWindow()
        QTimer.singleShot(100, self._set_initial_focus)

    def _build_ui(self):
        self.setStyleSheet(self.BASE_QSS + """
            QLabel#CreateLabSubtitle {
                font-size: 11px;
                color: #64748b;
            }
            QLabel#CreateLabRowLabel {
                font-size: 11px;
                font-weight: 600;
                color: #64748b;
                letter-spacing: 0.4px;
            }
            QLabel#CreateLabDash {
                color: #94a3b8;
                font-size: 16px;
                background: transparent;
            }
            QFrame#CreateLabChip {
                background: #f4f6f9;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QLabel#CreateLabChipLabel {
                font-size: 12px;
                font-weight: 600;
                color: #475569;
                background: transparent;
            }
            QSpinBox#CreateLabSpin {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                color: #0f172a;
                font-size: 13px;
                font-weight: 700;
                padding: 2px 4px;
                min-height: 28px;
            }
            QSpinBox#CreateLabSpin:focus {
                border: 1px solid #2563eb;
            }
            QFrame#CreateLabWarning {
                background: #fffbeb;
                border: 1px solid #fcd34d;
                border-radius: 8px;
            }
            QLabel#CreateLabWarningText {
                color: #92400e;
                font-size: 11px;
                font-weight: 500;
            }
            QLabel#CreateLabWarningIcon {
                background: transparent;
                font-size: 13px;
            }
            /* Ensure input fields are properly styled and focusable */
            QLineEdit#CreateLabInput {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 0 12px;
                color: #0f172a;
                font-size: 13px;
                selection-background-color: #bfdbfe;
            }
            QLineEdit#CreateLabInput:focus {
                border: 1px solid #2563eb;
                background: #ffffff;
            }
            QLineEdit#CreateLabInput:hover {
                border: 1px solid #94a3b8;
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(0)

        # ── Header ────────────────────────────────────────────
        hdr = QHBoxLayout()
        hdr.setSpacing(12)

        class PlusIconWidget(QLabel):
            def paintEvent(self, event):
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(37, 99, 235, 35))
                painter.drawEllipse(4, 4, 40, 40)
                painter.setPen(QPen(QColor(37, 99, 235), 2.2))
                cx, cy = 24, 24
                painter.drawLine(cx, cy - 9, cx, cy + 9)
                painter.drawLine(cx - 9, cy, cx + 9, cy)
                if not self.rect().isValid():
                    return
                super().paintEvent(event)

        icon_widget = PlusIconWidget()
        icon_widget.setFixedSize(48, 48)

        title_col = QVBoxLayout()
        title_col.setSpacing(3)

        title = QLabel("Create New Laboratory")
        title.setObjectName("DialogTitle")

        subtitle = QLabel("Set layout and enter an IP range for workstation generation.")
        subtitle.setObjectName("CreateLabSubtitle")
        subtitle.setWordWrap(True)

        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        self.close_btn = CloseButton()
        self.close_btn.setObjectName("CloseBtn")

        hdr.addWidget(icon_widget)
        hdr.addLayout(title_col, 1)
        hdr.addWidget(self.close_btn)
        root.addLayout(hdr)

        root.addSpacing(14)
        root.addWidget(self._divider())
        root.addSpacing(14)

        # ── Form ──────────────────────────────────────────────
        form = QVBoxLayout()
        form.setSpacing(10)

        form.addWidget(self._row_label("Lab Name", "CreateLabRowLabel"))
        self.lab_name = QLineEdit()
        self.lab_name.setObjectName("CreateLabInput")
        self.lab_name.setPlaceholderText("e.g. CSL 1 & 2")
        self.lab_name.setFixedHeight(38)
        self.lab_name.setFocusPolicy(Qt.StrongFocus)
        self.lab_name.setAttribute(Qt.WA_MacShowFocusRect, True)  # For macOS
        form.addWidget(self.lab_name)

        form.addSpacing(4)
        form.addWidget(self._row_label("Layout", "CreateLabRowLabel"))

        chips_row = QHBoxLayout()
        chips_row.setSpacing(10)
        self.sections = self._chip_spin("Sections", 1, 50, 3)
        self.rows     = self._chip_spin("Rows",     1, 50, 7)
        self.cols     = self._chip_spin("Cols",     1, 50, 5)
        chips_row.addWidget(self.sections.container)
        chips_row.addWidget(self.rows.container)
        chips_row.addWidget(self.cols.container)
        form.addLayout(chips_row)

        form.addSpacing(4)
        form.addWidget(self._row_label("IP Range", "CreateLabRowLabel"))

        ip_row = QHBoxLayout()
        ip_row.setSpacing(8)

        self.ip_start = QLineEdit()
        self.ip_start.setObjectName("CreateLabInput")
        self.ip_start.setPlaceholderText("Start IP  (e.g. 192.168.10.1)")
        self.ip_start.setFixedHeight(38)
        self.ip_start.setFocusPolicy(Qt.StrongFocus)
        self.ip_start.setAttribute(Qt.WA_MacShowFocusRect, True)

        dash = QLabel("—")
        dash.setObjectName("CreateLabDash")
        dash.setAlignment(Qt.AlignCenter)
        dash.setFixedWidth(20)

        self.ip_end = QLineEdit()
        self.ip_end.setObjectName("CreateLabInput")
        self.ip_end.setPlaceholderText("End IP  (e.g. 192.168.10.99)")
        self.ip_end.setFixedHeight(38)
        self.ip_end.setFocusPolicy(Qt.StrongFocus)
        self.ip_end.setAttribute(Qt.WA_MacShowFocusRect, True)

        ip_row.addWidget(self.ip_start, 1)
        ip_row.addWidget(dash)
        ip_row.addWidget(self.ip_end, 1)
        form.addLayout(ip_row)

        root.addLayout(form)
        root.addSpacing(12)

        # ── Warning pill ──────────────────────────────────────
        self.warn = QFrame()
        self.warn.setObjectName("CreateLabWarning")
        wlay = QHBoxLayout(self.warn)
        wlay.setContentsMargins(12, 10, 12, 10)
        wlay.setSpacing(8)

        self.warn_icon = QLabel("⚠️")
        self.warn_icon.setObjectName("CreateLabWarningIcon")
        self.warn_icon.setFixedWidth(20)
        self.warn_icon.setAlignment(Qt.AlignCenter)

        self.warn_text = QLabel("")
        self.warn_text.setObjectName("CreateLabWarningText")
        self.warn_text.setWordWrap(True)

        wlay.addWidget(self.warn_icon)
        wlay.addWidget(self.warn_text, 1)
        root.addWidget(self.warn)

        root.addSpacing(12)
        root.addWidget(self._divider())
        root.addSpacing(12)

        # ── Buttons ───────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("CancelBtn")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setFixedHeight(36)
        self.cancel_btn.setFixedWidth(110)

        self.create_btn = QPushButton("Create Lab")
        self.create_btn.setObjectName("PrimaryBtn")
        self.create_btn.setCursor(Qt.PointingHandCursor)
        self.create_btn.setFixedHeight(36)
        self.create_btn.setFixedWidth(130)

        btn_row.addWidget(self.cancel_btn)
        btn_row.addWidget(self.create_btn)
        root.addLayout(btn_row)

    def resizeEvent(self, event):
        """Handle resize events safely"""
        super().resizeEvent(event)
        # Ensure the new size is valid
        if event.size().isValid():
            self.update()

    def _row_label(self, text: str, obj: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName(obj)
        return lbl

    def _chip_spin(self, caption: str, mn: int, mx: int, value: int):
        container = QFrame()
        container.setObjectName("CreateLabChip")
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        lay = QHBoxLayout(container)
        lay.setContentsMargins(12, 8, 12, 8)
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
        sp.setFocusPolicy(Qt.StrongFocus)
        sp.setAttribute(Qt.WA_MacShowFocusRect, True)

        lay.addWidget(cap)
        lay.addStretch()
        lay.addWidget(sp)

        container.spin = sp
        return type("SpinWrap", (), {"container": container, "spin": sp})

    def _wire_signals(self):
        self.close_btn.clicked.connect(self.reject)
        self.cancel_btn.clicked.connect(self.reject)
        self.create_btn.clicked.connect(self._on_create)
        self.lab_name.textChanged.connect(self._validate_live)
        self.ip_start.textChanged.connect(self._validate_live)
        self.ip_end.textChanged.connect(self._validate_live)
        self.sections.spin.valueChanged.connect(self._validate_live)
        self.rows.spin.valueChanged.connect(self._validate_live)
        self.cols.spin.valueChanged.connect(self._validate_live)

    # ── Unchanged validation / data ───────────────────────────
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
        if int(s) > int(e):
            s, e = e, s
        total = int(e) - int(s) + 1
        if total > 5000:
            return []
        return [str(ipaddress.ip_address(int(s) + i)) for i in range(total)]

    def _validate_live(self):
        need    = self._required_count()
        name_ok = bool(self.lab_name.text().strip())
        ip_list = self._ip_range_list()

        if ip_list == []:
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
        if len(ip_list) < need:
            self.warn.show()
            self.warn_text.setText(f"Not enough IPs. Need {need}, but range gives {len(ip_list)}.")
            self.create_btn.setEnabled(False)
            return

        self.warn.hide()
        self.create_btn.setEnabled(True)

    def _on_create(self):
        self._validate_live()
        if not self.create_btn.isEnabled():
            return
        ips_full = self._ip_range_list() or []
        need     = self._required_count()
        self._result = CreateLabResult(
            lab_name=self.lab_name.text().strip(),
            layout={
                "sections": self.sections.spin.value(),
                "rows":     self.rows.spin.value(),
                "cols":     self.cols.spin.value(),
            },
            ips=ips_full[:need],
        )
        self._dismiss(accepted=True)

    def get_data(self) -> dict:
        if not self._result:
            return {"lab_name": "", "layout": {"sections": 1, "rows": 1, "cols": 1}, "ips": []}
        return {
            "lab_name": self._result.lab_name,
            "layout":   self._result.layout,
            "ips":      self._result.ips,
        }