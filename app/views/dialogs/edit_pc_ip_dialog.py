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


class EditPcIpDialog(QDialog):
    def __init__(self, pc_name: str, current_ip: str, parent=None):
        super().__init__(parent)
        self.setObjectName("EditPcIpDialog")
        self.setWindowTitle("Edit IP Address")
        self.setModal(True)

        self.new_ip: str | None = None
        self._pc_name = pc_name
        self._current_ip = current_ip

        # Frameless + translucent bg (for overlay)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # Size for proper alignment
        self.setFixedSize(540, 320)

        self._build_ui()
        QTimer.singleShot(0, self._animate_in)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.card = QFrame(self)
        self.card.setObjectName("EditPcIpCard")
        self.card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        card_lay = QVBoxLayout(self.card)
        card_lay.setContentsMargins(32, 24, 32, 24)
        card_lay.setSpacing(18)

        # Header
        header = QHBoxLayout()
        header.setSpacing(12)

        icon = QLabel("✏️")
        icon.setObjectName("EditPcIpIcon")
        icon.setFixedSize(32, 32)
        icon.setAlignment(Qt.AlignCenter)
        icon.setFont(QFont("Segoe UI", 18))

        title = QLabel("Edit IP Address")
        title.setObjectName("EditPcIpTitle")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))

        header.addWidget(icon)
        header.addWidget(title)
        header.addStretch()
        card_lay.addLayout(header)

        # PC NAME row - side by side
        pc_row = QHBoxLayout()
        pc_row.setSpacing(12)

        pc_label = QLabel("PC NAME")
        pc_label.setObjectName("EditPcIpLabel")
        pc_label.setFixedWidth(120)
        pc_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        pc_value = QLabel(self._pc_name)
        pc_value.setObjectName("EditPcIpPcName")
        pc_value.setAlignment(Qt.AlignCenter)
        pc_value.setFixedHeight(42)
        pc_value.setFixedWidth(200)

        pc_row.addWidget(pc_label)
        pc_row.addWidget(pc_value)
        pc_row.addStretch()
        card_lay.addLayout(pc_row)

        # Current IP row - side by side
        current_row = QHBoxLayout()
        current_row.setSpacing(12)

        current_label = QLabel("Current IP:")
        current_label.setObjectName("EditPcIpCurrentLabel")
        current_label.setFixedWidth(120)
        current_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        current_value = QLabel(self._current_ip)
        current_value.setObjectName("EditPcIpCurrentValue")
        current_value.setAlignment(Qt.AlignCenter)
        current_value.setFixedHeight(42)
        current_value.setFixedWidth(200)

        current_row.addWidget(current_label)
        current_row.addWidget(current_value)
        current_row.addStretch()
        card_lay.addLayout(current_row)

        # NEW IP ADDRESS row - side by side (fixed width 120px)
        new_row = QHBoxLayout()
        new_row.setSpacing(12)

        new_label = QLabel("NEW IP ADDRESS")
        new_label.setObjectName("EditPcIpLabel")
        new_label.setFixedWidth(120)
        new_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        new_label.setWordWrap(False)

        self.ip_edit = QLineEdit()
        self.ip_edit.setObjectName("EditPcIpInput")
        self.ip_edit.setPlaceholderText("Enter new IP address")
        self.ip_edit.setText(self._current_ip)
        self.ip_edit.selectAll()
        self.ip_edit.setFixedHeight(42)
        self.ip_edit.setFixedWidth(200)
        self.ip_edit.setAlignment(Qt.AlignCenter)

        new_row.addWidget(new_label)
        new_row.addWidget(self.ip_edit)
        new_row.addStretch()
        card_lay.addLayout(new_row)

        # Spacer
        card_lay.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Buttons - at bottom
        btn_container = QHBoxLayout()
        btn_container.setSpacing(16)
        btn_container.setContentsMargins(0, 8, 0, 0)

        btn_container.addStretch(1)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("EditPcIpCancelBtn")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedHeight(42)
        cancel_btn.setFixedWidth(130)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save")
        save_btn.setObjectName("EditPcIpSaveBtn")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setFixedHeight(42)
        save_btn.setFixedWidth(130)
        save_btn.clicked.connect(self._save)

        btn_container.addWidget(cancel_btn)
        btn_container.addWidget(save_btn)
        btn_container.addStretch(1)

        card_lay.addLayout(btn_container)

        # Add card to root
        root.addWidget(self.card)

        # Apply styles based on theme
        self._apply_styles()

    def _apply_styles(self):
        """Apply theme-aware styles - fixed for both dark and light mode"""
        # Check parent theme
        theme = "dark"
        if hasattr(self.parent(), "state") and hasattr(self.parent().state, "theme"):
            theme = self.parent().state.theme
        
        if theme == "light":
            # Light mode styles
            self.setStyleSheet("""
                QFrame#EditPcIpCard {
                    background: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 20px;
                }
                QLabel#EditPcIpIcon {
                    color: #2563eb;
                    background: transparent;
                }
                QLabel#EditPcIpTitle {
                    color: #0f172a;
                    font-size: 16px;
                    font-weight: 800;
                    background: transparent;
                }
                QLabel#EditPcIpLabel {
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
                QLabel#EditPcIpCurrentLabel {
                    color: #64748b;
                    font-size: 13px;
                    font-weight: 500;
                    background: transparent;
                    min-width: 120px;
                    max-width: 120px;
                    padding-right: 8px;
                }
                QLabel#EditPcIpPcName {
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 10px;
                    color: #0f172a;
                    font-size: 15px;
                    font-weight: 600;
                }
                QLabel#EditPcIpCurrentValue {
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 10px;
                    color: #2563eb;
                    font-size: 14px;
                    font-weight: 600;
                    font-family: 'Consolas', monospace;
                }
                QLineEdit#EditPcIpInput {
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 10px;
                    padding: 8px 12px;
                    color: #0f172a;
                    font-size: 14px;
                    font-family: 'Consolas', monospace;
                }
                QLineEdit#EditPcIpInput:focus {
                    border: 1px solid #2563eb;
                }
                QPushButton#EditPcIpCancelBtn {
                    background: white;
                    border: 1px solid #e2e8f0;
                    color: #64748b;
                    border-radius: 10px;
                    font-weight: 600;
                    font-size: 13px;
                }
                QPushButton#EditPcIpCancelBtn:hover {
                    background: #f8fafc;
                    border: 1px solid #2563eb;
                    color: #0f172a;
                }
                QPushButton#EditPcIpSaveBtn {
                    background: #2563eb;
                    border: none;
                    color: white;
                    border-radius: 10px;
                    font-weight: 700;
                    font-size: 13px;
                }
                QPushButton#EditPcIpSaveBtn:hover {
                    background: #1d4ed8;
                }
            """)
        else:
            # Dark mode styles
            self.setStyleSheet("""
                QFrame#EditPcIpCard {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                              stop:0 #1e1e1e,
                                              stop:1 #121212);
                    border: 1px solid #2a2a2a;
                    border-radius: 20px;
                }
                QLabel#EditPcIpIcon {
                    color: #60a5fa;
                    background: transparent;
                }
                QLabel#EditPcIpTitle {
                    color: #ffffff;
                    font-size: 16px;
                    font-weight: 800;
                    background: transparent;
                }
                QLabel#EditPcIpLabel {
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
                QLabel#EditPcIpCurrentLabel {
                    color: #94a3b8;
                    font-size: 13px;
                    font-weight: 500;
                    background: transparent;
                    min-width: 120px;
                    max-width: 120px;
                    padding-right: 8px;
                }
                QLabel#EditPcIpPcName {
                    background: #2a2a2a;
                    border: 1px solid #3a3a3a;
                    border-radius: 10px;
                    color: #ffffff;
                    font-size: 15px;
                    font-weight: 600;
                }
                QLabel#EditPcIpCurrentValue {
                    background: #2a2a2a;
                    border: 1px solid #3a3a3a;
                    border-radius: 10px;
                    color: #60a5fa;
                    font-size: 14px;
                    font-weight: 600;
                    font-family: 'Consolas', monospace;
                }
                QLineEdit#EditPcIpInput {
                    background: #2a2a2a;
                    border: 1px solid #3a3a3a;
                    border-radius: 10px;
                    padding: 8px 12px;
                    color: #ffffff;
                    font-size: 14px;
                    font-family: 'Consolas', monospace;
                }
                QLineEdit#EditPcIpInput:focus {
                    border: 1px solid #60a5fa;
                }
                QPushButton#EditPcIpCancelBtn {
                    background: #2a2a2a;
                    border: 1px solid #3a3a3a;
                    color: #cccccc;
                    border-radius: 10px;
                    font-weight: 600;
                    font-size: 13px;
                }
                QPushButton#EditPcIpCancelBtn:hover {
                    background: #333333;
                    border: 1px solid #60a5fa;
                    color: white;
                }
                QPushButton#EditPcIpSaveBtn {
                    background: #2563eb;
                    border: none;
                    color: white;
                    border-radius: 10px;
                    font-weight: 700;
                    font-size: 13px;
                }
                QPushButton#EditPcIpSaveBtn:hover {
                    background: #1d4ed8;
                }
            """)

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

    def _save(self):
        ip = self.ip_edit.text().strip()
        if not _IPV4_REGEX.match(ip):
            try:
                from .glass_messagebox import show_glass_message
                show_glass_message(
                    self,
                    "Invalid IP",
                    "Please enter a valid IPv4 address.",
                    icon=QMessageBox.Warning
                )
            except Exception:
                QMessageBox.warning(self, "Invalid IP", "Please enter a valid IPv4 address.")
            return

        self.new_ip = ip
        self.accept()