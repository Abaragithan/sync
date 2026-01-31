import os
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap


def _abs_asset_path(rel_path: str) -> str:
    """
    Build absolute path from this file location.
    This avoids 'working directory' problems.
    """
    base = os.path.dirname(os.path.abspath(__file__))  
    app_dir = os.path.abspath(os.path.join(base, "..", ".."))
    return os.path.join(app_dir, rel_path)


class PcCard(QFrame):
    toggled = Signal(str, bool)
    delete_requested = Signal(str)

    def __init__(self, name: str, ip: str, icon_rel_path: str = "assets/pc1.png"):
        super().__init__()
        self.ip = ip
        self.selected = False

        self.setFixedSize(64, 64)

        self.setObjectName("PcCard")

        # 🔹 Added QToolTip styling ONLY
        self.setStyleSheet("""
            QFrame#PcCard {
                background: #1b1b1b;
                border: 1px solid #2a2a2a;
                border-radius: 10px;
            }
            QFrame#PcCard[selected="true"] {
                border: 2px solid #007acc;
                background: #1e2a33;
            }
            QToolTip {
                background-color: #020617;
                color: #ffffff;          /* ✅ WHITE TEXT */
                border: 1px solid #334155;
                padding: 6px;
                border-radius: 6px;
                font-size: 12px;
            }
        """)

        self.setProperty("selected", False)
        self._build_ui(name, ip, icon_rel_path)

    def _build_ui(self, name: str, ip: str, icon_rel_path: str):
        root = QVBoxLayout(self)
        root.setContentsMargins(2, 2, 2, 2)
        root.setSpacing(0)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.addStretch()

        self.icon = QLabel()
        self.icon.setAlignment(Qt.AlignCenter)

        pm = QPixmap(_abs_asset_path(icon_rel_path))
        if not pm.isNull():
            self.icon.setPixmap(
                pm.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self.icon.setText("PC")
            self.icon.setStyleSheet("color: #555; font-weight: 700; font-size: 12px;")

        name_lbl = QLabel(name)
        name_lbl.setAlignment(Qt.AlignCenter)
        name_lbl.setStyleSheet("color:#ddd; font-size: 9px; font-weight: 600;")

        root.addLayout(top)
        root.addWidget(self.icon, 1, Qt.AlignCenter)
        root.addWidget(name_lbl)

       
        self.setToolTip(f"{name}\n{ip}")

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        self.set_selected(not self.selected)

    def set_selected(self, value: bool):
        self.selected = value
        self.setProperty("selected", value)
        self.style().unpolish(self)
        self.style().polish(self)
        self.toggled.emit(self.ip, value)
