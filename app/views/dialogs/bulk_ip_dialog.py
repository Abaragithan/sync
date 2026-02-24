from __future__ import annotations
import re

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QGraphicsOpacityEffect, QMessageBox,
    QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QPoint
from PySide6.QtGui import QColor, QFont, QPainter, QMouseEvent, QEnterEvent, QPen

_IPV4_REGEX = re.compile(
    r"^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"
    r"(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$"
)

class CloseButton(QPushButton):
    """Custom close button with red hover effect"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(32, 32)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self._hovered = False
        
    def enterEvent(self, event: QEnterEvent):
        self._hovered = True
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background circle
        if self._hovered:
            painter.setBrush(QColor(239, 68, 68, 30))  # Red with low opacity
        else:
            painter.setBrush(Qt.transparent)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(4, 4, 24, 24)
        
        # X mark
        if self._hovered:
            painter.setPen(QPen(QColor(239, 68, 68), 2.5))  # Red when hovered
        else:
            painter.setPen(QPen(QColor(156, 163, 175), 2))  # Gray default
        margin = 11
        painter.drawLine(margin, margin, 32 - margin, 32 - margin)
        painter.drawLine(32 - margin, margin, margin, 32 - margin)


class BulkIpDialog(QDialog):
    """
    Same DESIGN as EditPcIpDialog - Light Mode Only
    Functionality: keep it simple => Apply => accept()
    """
    def __init__(self, parent=None, default_start_ip: str = ""):
        super().__init__(parent)
        self.setObjectName("BulkIpDialog")
        self.setWindowTitle("Bulk IP Assign")
        self.setModal(True)

        # Frameless + translucent bg
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # For window dragging
        self._drag_position: QPoint | None = None

        # Same size family (you can tweak width)
        self.setFixedSize(540, 300)

        self._default_ip = default_start_ip.strip()

        self._build_ui()
        QTimer.singleShot(0, self._animate_in)

    # ---------------- Window Dragging ----------------
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_position = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_position is not None:
            delta = event.globalPosition().toPoint() - self._drag_position
            self.move(self.pos() + delta)
            self._drag_position = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_position = None

    # ---------------- UI ----------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.card = QFrame(self)
        self.card.setObjectName("BulkIpCard")
        self.card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Apply light mode styles directly
        self.setStyleSheet("""
            QFrame#BulkIpCard {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 20px;
            }
            QLabel#BulkIpIcon { 
                background: transparent; 
                color: #2563eb;
            }
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
            QLineEdit#BulkIpInput:focus { 
                border: 1px solid #2563eb;
                background: #ffffff;
            }
            QLineEdit#BulkIpInput:hover {
                border: 1px solid #94a3b8;
            }

            QPushButton#BulkIpCancelBtn {
                background: white;
                border: 1px solid #e2e8f0;
                color: #64748b;
                border-radius: 10px;
                font-weight: 600;
                font-size: 13px;
                padding: 8px 16px;
            }
            QPushButton#BulkIpCancelBtn:hover {
                background: #f8fafc;
                border: 1px solid #2563eb;
                color: #0f172a;
            }
            QPushButton#BulkIpCancelBtn:pressed {
                background: #f1f5f9;
            }
            QPushButton#BulkIpApplyBtn {
                background: #2563eb;
                border: none;
                color: white;
                border-radius: 10px;
                font-weight: 700;
                font-size: 13px;
                padding: 8px 16px;
            }
            QPushButton#BulkIpApplyBtn:hover { 
                background: #1d4ed8; 
            }
            QPushButton#BulkIpApplyBtn:pressed { 
                background: #1e40af; 
            }
        """)

        card_lay = QVBoxLayout(self.card)
        card_lay.setContentsMargins(32, 24, 32, 24)
        card_lay.setSpacing(18)

        # Header with close button
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
        
        # Close button
        self.close_btn = CloseButton()
        self.close_btn.clicked.connect(self.reject)
        header.addWidget(self.close_btn)
        
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