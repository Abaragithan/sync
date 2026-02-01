import os
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPainter, QColor


def _abs_asset_path(rel_path: str) -> str:
    base = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.abspath(os.path.join(base, "..", ".."))
    return os.path.join(app_dir, rel_path)


class PcCard(QFrame):
    toggled = Signal(str, bool)
    delete_requested = Signal(str)  # keep for compatibility with your lab_page.py

    NORMAL_COLOR = "#9F9F9F"
    SELECTED_COLOR = "#007acc"

    def __init__(self, name: str, ip: str, icon_rel_path: str = "assets/pc2.png"):
        super().__init__()

        self.ip = ip
        self.selected = False
        self.icon_rel_path = icon_rel_path

        self.setFixedSize(48, 56)
        self.setToolTip(f"{name}\n{ip}")
        self.setStyleSheet("background: transparent; border: none;")

        self._build_ui(name)
        self._load_icon()

    def _build_ui(self, name: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.icon = QLabel()
        self.icon.setAlignment(Qt.AlignCenter)

        self.name_lbl = QLabel(name)
        self.name_lbl.setAlignment(Qt.AlignCenter)
        self.name_lbl.setStyleSheet(
            f"color:{self.NORMAL_COLOR}; font-size:9px; font-weight:600;"
        )

        layout.addWidget(self.icon, 1)
        layout.addWidget(self.name_lbl)

    def _load_icon(self):
        self.base_pm = QPixmap(_abs_asset_path(self.icon_rel_path))
        if self.base_pm.isNull():
            self.icon.setText("PC")
            self.icon.setStyleSheet(f"color:{self.NORMAL_COLOR}; font-weight:700;")
            return

        self._apply_icon_color(self.NORMAL_COLOR)

    def _apply_icon_color(self, color_hex: str):
        tinted = QPixmap(self.base_pm.size())
        tinted.fill(Qt.transparent)

        painter = QPainter(tinted)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.drawPixmap(0, 0, self.base_pm)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(tinted.rect(), QColor(color_hex))
        painter.end()

        self.icon.setPixmap(
            tinted.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def mousePressEvent(self, event):
        self.set_selected(not self.selected)
        super().mousePressEvent(event)

    def set_selected(self, value: bool):
        self.selected = value
        color = self.SELECTED_COLOR if value else self.NORMAL_COLOR
        if hasattr(self, "base_pm") and self.base_pm and not self.base_pm.isNull():
            self._apply_icon_color(color)
        self.toggled.emit(self.ip, value)

    # Optional helper if later you add a delete button / context menu
    def request_delete(self):
        self.delete_requested.emit(self.ip)
