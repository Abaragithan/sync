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


class BulkIpDialog(QDialog):
    """
    Same DESIGN as EditPcIpDialog
    Functionality: keep it simple -> Apply => accept()
    """
    def __init__(self, parent=None, default_start_ip: str = ""):
        super().__init__(parent)
        self.setObjectName("BulkIpDialog")
        self.setWindowTitle("Bulk IP Assign")
        self.setModal(True)

        # Frameless + translucent bg
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # Same size family (you can tweak width)
        self.setFixedSize(540, 300)

        self._default_ip = default_start_ip.strip()

        self._build_ui()
        QTimer.singleShot(0, self._animate_in)

    # ---------------- UI ----------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.card = QFrame(self)
        self.card.setObjectName("BulkIpCard")
        self.card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        card_lay = QVBoxLayout(self.card)
        card_lay.setContentsMargins(32, 24, 32, 24)
        card_lay.setSpacing(18)

        # Header
        header = QHBoxLayout()
        header.setSpacing(12)

        icon = QLabel("🧩")
        icon.setObjectName("BulkIpIcon")
        icon.setFixedSize(32, 32)
        icon.setAlignment(Qt.AlignCenter)
        icon.setFont(QFont("Segoe UI", 18))

        title = QLabel("Bulk IP Assign")
        title.setObjectName("BulkIpTitle")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))

        header.addWidget(icon)
        header.addWidget(title)
        header.addStretch()
        card_lay.addLayout(header)

        # Description
        hint = QLabel("Start IP will be used to assign sequential IPs to all PCs in this section.")
        hint.setObjectName("BulkIpHint")
        hint.setWordWrap(True)
        card_lay.addWidget(hint)

        # Start IP row (same row style)
        row = QHBoxLayout()
        row.setSpacing(12)

        lbl = QLabel("START IP")
        lbl.setObjectName("BulkIpLabel")
        lbl.setFixedWidth(120)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.start_ip = QLineEdit()
        self.start_ip.setObjectName("BulkIpInput")
        self.start_ip.setPlaceholderText("e.g. 192.168.1.100")
        self.start_ip.setText(self._default_ip)
        self.start_ip.setFixedHeight(42)
        self.start_ip.setFixedWidth(200)
        self.start_ip.setAlignment(Qt.AlignCenter)

        row.addWidget(lbl)
        row.addWidget(self.start_ip)
        row.addStretch()
        card_lay.addLayout(row)

        # Spacer (push buttons down)
        card_lay.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Buttons (aligned like EditPcIpDialog)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(16)
        btn_row.setContentsMargins(0, 8, 0, 0)

        btn_row.addStretch(1)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("BulkIpCancelBtn")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedHeight(42)
        cancel_btn.setFixedWidth(130)
        cancel_btn.clicked.connect(self.reject)

        apply_btn = QPushButton("Apply")
        apply_btn.setObjectName("BulkIpApplyBtn")
        apply_btn.setCursor(Qt.PointingHandCursor)
        apply_btn.setFixedHeight(42)
        apply_btn.setFixedWidth(130)
        apply_btn.clicked.connect(self._apply)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(apply_btn)
        btn_row.addStretch(1)

        card_lay.addLayout(btn_row)

        root.addWidget(self.card)

        # Apply styles based on theme (same approach)
        self._apply_styles()

    # ---------------- Style ----------------
    def _apply_styles(self):
        theme = "dark"
        if hasattr(self.parent(), "state") and hasattr(self.parent().state, "theme"):
            theme = self.parent().state.theme

        if theme == "light":
            self.setStyleSheet("""
                QFrame#BulkIpCard {
                    background: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 20px;
                }
                QLabel#BulkIpIcon { background: transparent; }
                QLabel#BulkIpTitle {
                    color: #0f172a;
                    font-size: 16px;
                    font-weight: 800;
                    background: transparent;
                }
                QLabel#BulkIpHint {
                    color: #475569;
                    font-size: 13px;
                    background: transparent;
                }
                QLabel#BulkIpLabel {
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
                QLineEdit#BulkIpInput {
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 10px;
                    padding: 8px 12px;
                    color: #0f172a;
                    font-size: 14px;
                    font-family: 'Consolas', monospace;
                }
                QLineEdit#BulkIpInput:focus { border: 1px solid #2563eb; }

                QPushButton#BulkIpCancelBtn {
                    background: white;
                    border: 1px solid #e2e8f0;
                    color: #64748b;
                    border-radius: 10px;
                    font-weight: 600;
                    font-size: 13px;
                }
                QPushButton#BulkIpCancelBtn:hover {
                    background: #f8fafc;
                    border: 1px solid #2563eb;
                    color: #0f172a;
                }
                QPushButton#BulkIpApplyBtn {
                    background: #2563eb;
                    border: none;
                    color: white;
                    border-radius: 10px;
                    font-weight: 700;
                    font-size: 13px;
                }
                QPushButton#BulkIpApplyBtn:hover { background: #1d4ed8; }
            """)
        else:
            # ✅ Dark theme: keep it BLACK (not blue)
            self.setStyleSheet("""
                QFrame#BulkIpCard {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                              stop:0 #1b1b1b,
                                              stop:1 #0f0f0f);
                    border: 1px solid #2a2a2a;
                    border-radius: 20px;
                }
                QLabel#BulkIpIcon { background: transparent; }
                QLabel#BulkIpTitle {
                    color: #ffffff;
                    font-size: 16px;
                    font-weight: 800;
                    background: transparent;
                }
                QLabel#BulkIpHint {
                    color: rgba(226,232,240,170);
                    font-size: 13px;
                    background: transparent;
                }
                QLabel#BulkIpLabel {
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
                QLineEdit#BulkIpInput {
                    background: #171717;
                    border: 1px solid #2f2f2f;
                    border-radius: 10px;
                    padding: 8px 12px;
                    color: #ffffff;
                    font-size: 14px;
                    font-family: 'Consolas', monospace;
                }
                QLineEdit#BulkIpInput:focus { border: 1px solid #60a5fa; }

                QPushButton#BulkIpCancelBtn {
                    background: #171717;
                    border: 1px solid #2f2f2f;
                    color: rgba(226,232,240,190);
                    border-radius: 10px;
                    font-weight: 600;
                    font-size: 13px;
                }
                QPushButton#BulkIpCancelBtn:hover {
                    background: #202020;
                    border: 1px solid #60a5fa;
                    color: white;
                }
                QPushButton#BulkIpApplyBtn {
                    background: #2563eb;
                    border: none;
                    color: white;
                    border-radius: 10px;
                    font-weight: 700;
                    font-size: 13px;
                }
                QPushButton#BulkIpApplyBtn:hover { background: #1d4ed8; }
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

    # ---------------- Functionality (unchanged simple) ----------------
    def _apply(self):
        ip = self.start_ip.text().strip()

        # optional: keep validation (remove if you truly want 0 logic change)
        if ip and not _IPV4_REGEX.match(ip):
            QMessageBox.warning(self, "Invalid IP", "Please enter a valid IPv4 address.")
            return

        self.accept()
