from __future__ import annotations
import re

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QGraphicsOpacityEffect, QMessageBox,
    QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QColor, QFont, QPainter


_IPV4_REGEX = re.compile(
    r"^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"
    r"(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$"
)


class AddPcDialog(QDialog):
    """
    Same DESIGN as EditPcIpDialog and BulkIpDialog
    """
    def __init__(self, parent=None, default_name: str = "", default_ip: str = ""):
        super().__init__(parent)
        self.setObjectName("AddPcDialog")
        self.setWindowTitle("Add PC")
        self.setModal(True)

        # Frameless + translucent bg
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # Same size family
        self.setFixedSize(540, 320)

        self._default_name = default_name.strip()
        self._default_ip = default_ip.strip()

        self._build_ui()
        QTimer.singleShot(0, self._animate_in)

    # ---------------- UI ----------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.card = QFrame(self)
        self.card.setObjectName("AddPcCard")
        self.card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        card_lay = QVBoxLayout(self.card)
        card_lay.setContentsMargins(32, 24, 32, 24)
        card_lay.setSpacing(18)

        # Header
        header = QHBoxLayout()
        header.setSpacing(12)

        icon = QLabel("➕")
        icon.setObjectName("AddPcIcon")
        icon.setFixedSize(32, 32)
        icon.setAlignment(Qt.AlignCenter)
        icon.setFont(QFont("Segoe UI", 18))

        title = QLabel("Add New PC")
        title.setObjectName("AddPcTitle")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))

        header.addWidget(icon)
        header.addWidget(title)
        header.addStretch()
        card_lay.addLayout(header)

        # PC Name row
        name_row = QHBoxLayout()
        name_row.setSpacing(12)

        name_lbl = QLabel("PC NAME")
        name_lbl.setObjectName("AddPcLabel")
        name_lbl.setFixedWidth(120)
        name_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.name_edit = QLineEdit()
        self.name_edit.setObjectName("AddPcInput")
        self.name_edit.setPlaceholderText("e.g. PC-106")
        self.name_edit.setText(self._default_name)
        self.name_edit.setFixedHeight(42)
        self.name_edit.setFixedWidth(250)
        self.name_edit.setAlignment(Qt.AlignCenter)

        name_row.addWidget(name_lbl)
        name_row.addWidget(self.name_edit)
        name_row.addStretch()
        card_lay.addLayout(name_row)

        # IP Address row
        ip_row = QHBoxLayout()
        ip_row.setSpacing(12)

        ip_lbl = QLabel("IP ADDRESS")
        ip_lbl.setObjectName("AddPcLabel")
        ip_lbl.setFixedWidth(120)
        ip_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.ip_edit = QLineEdit()
        self.ip_edit.setObjectName("AddPcInput")
        self.ip_edit.setPlaceholderText("e.g. 192.168.1.100")
        self.ip_edit.setText(self._default_ip)
        self.ip_edit.setFixedHeight(42)
        self.ip_edit.setFixedWidth(250)
        self.ip_edit.setAlignment(Qt.AlignCenter)

        ip_row.addWidget(ip_lbl)
        ip_row.addWidget(self.ip_edit)
        ip_row.addStretch()
        card_lay.addLayout(ip_row)

        # Hint text
        hint = QLabel("Enter a valid PC name and IPv4 address.")
        hint.setObjectName("AddPcHint")
        hint.setWordWrap(True)
        hint.setAlignment(Qt.AlignCenter)
        card_lay.addWidget(hint)

        # Spacer (push buttons down)
        card_lay.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Buttons (aligned like EditPcIpDialog)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(16)
        btn_row.setContentsMargins(0, 8, 0, 0)

        btn_row.addStretch(1)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("AddPcCancelBtn")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedHeight(42)
        cancel_btn.setFixedWidth(130)
        cancel_btn.clicked.connect(self.reject)

        add_btn = QPushButton("Add PC")
        add_btn.setObjectName("AddPcAddBtn")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedHeight(42)
        add_btn.setFixedWidth(130)
        add_btn.clicked.connect(self._add)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(add_btn)
        btn_row.addStretch(1)

        card_lay.addLayout(btn_row)

        root.addWidget(self.card)

        # Apply styles based on theme
        self._apply_styles()

    # ---------------- Style ----------------
    def _apply_styles(self):
        theme = "dark"
        if hasattr(self.parent(), "state") and hasattr(self.parent().state, "theme"):
            theme = self.parent().state.theme

        if theme == "light":
            self.setStyleSheet("""
                QFrame#AddPcCard {
                    background: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 20px;
                }
                QLabel#AddPcIcon { background: transparent; }
                QLabel#AddPcTitle {
                    color: #0f172a;
                    font-size: 16px;
                    font-weight: 800;
                    background: transparent;
                }
                QLabel#AddPcHint {
                    color: #475569;
                    font-size: 13px;
                    background: transparent;
                }
                QLabel#AddPcLabel {
                    color: #64748b;
                    font-size: 12px;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    background: transparent;
                    min-width: 120px;
                    max-width: 120px;
                    padding-right: 8px;
                }
                QLineEdit#AddPcInput {
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 10px;
                    padding: 8px 12px;
                    color: #0f172a;
                    font-size: 14px;
                    font-family: 'Consolas', monospace;
                }
                QLineEdit#AddPcInput:focus { border: 1px solid #2563eb; }

                QPushButton#AddPcCancelBtn {
                    background: white;
                    border: 1px solid #e2e8f0;
                    color: #64748b;
                    border-radius: 10px;
                    font-weight: 600;
                    font-size: 13px;
                }
                QPushButton#AddPcCancelBtn:hover {
                    background: #f8fafc;
                    border: 1px solid #2563eb;
                    color: #0f172a;
                }
                QPushButton#AddPcAddBtn {
                    background: #2563eb;
                    border: none;
                    color: white;
                    border-radius: 10px;
                    font-weight: 700;
                    font-size: 13px;
                }
                QPushButton#AddPcAddBtn:hover { background: #1d4ed8; }
            """)
        else:
            # Dark theme
            self.setStyleSheet("""
                QFrame#AddPcCard {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                              stop:0 #1b1b1b,
                                              stop:1 #0f0f0f);
                    border: 1px solid #2a2a2a;
                    border-radius: 20px;
                }
                QLabel#AddPcIcon { background: transparent; }
                QLabel#AddPcTitle {
                    color: #ffffff;
                    font-size: 16px;
                    font-weight: 800;
                    background: transparent;
                }
                QLabel#AddPcHint {
                    color: rgba(226,232,240,170);
                    font-size: 13px;
                    background: transparent;
                }
                QLabel#AddPcLabel {
                    color: #94a3b8;
                    font-size: 12px;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    background: transparent;
                    min-width: 120px;
                    max-width: 120px;
                    padding-right: 8px;
                }
                QLineEdit#AddPcInput {
                    background: #171717;
                    border: 1px solid #2f2f2f;
                    border-radius: 10px;
                    padding: 8px 12px;
                    color: #ffffff;
                    font-size: 14px;
                    font-family: 'Consolas', monospace;
                }
                QLineEdit#AddPcInput:focus { border: 1px solid #60a5fa; }

                QPushButton#AddPcCancelBtn {
                    background: #171717;
                    border: 1px solid #2f2f2f;
                    color: rgba(226,232,240,190);
                    border-radius: 10px;
                    font-weight: 600;
                    font-size: 13px;
                }
                QPushButton#AddPcCancelBtn:hover {
                    background: #202020;
                    border: 1px solid #60a5fa;
                    color: white;
                }
                QPushButton#AddPcAddBtn {
                    background: #2563eb;
                    border: none;
                    color: white;
                    border-radius: 10px;
                    font-weight: 700;
                    font-size: 13px;
                }
                QPushButton#AddPcAddBtn:hover { background: #1d4ed8; }
            """)

    # ---------------- Animation + overlay ----------------
    def _animate_in(self):
        self._center_on_parent()

        fx = QGraphicsOpacityEffect(self.card)
        self.card.setGraphicsEffect(fx)
        fx.setOpacity(0.0)

        anim = QPropertyAnimation(fx, b"opacity", self)
        anim.setDuration(220)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()
        self._anim = anim

    def _center_on_parent(self):
        if not self.parent():
            return
        pg = self.parent().geometry()
        self.move(
            pg.center().x() - self.width() // 2,
            pg.center().y() - self.height() // 2
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 90))
        painter.end()
        super().paintEvent(event)

    # ---------------- Functionality ----------------
    def _add(self):
        name = self.name_edit.text().strip()
        ip = self.ip_edit.text().strip()

        if not name:
            from .glass_messagebox import show_glass_message
            show_glass_message(self, "Invalid Input", "Please enter a PC name.", icon=QMessageBox.Warning)
            return

        if not ip:
            from .glass_messagebox import show_glass_message
            show_glass_message(self, "Invalid Input", "Please enter an IP address.", icon=QMessageBox.Warning)
            return

        if not _IPV4_REGEX.match(ip):
            from .glass_messagebox import show_glass_message
            show_glass_message(self, "Invalid IP", "Please enter a valid IPv4 address.", icon=QMessageBox.Warning)
            return

        self.accept()

    def values(self):
        return self.name_edit.text().strip(), self.ip_edit.text().strip()