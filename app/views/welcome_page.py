import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap

class WelcomePage(QWidget):
    go_deployment = Signal()

    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignCenter)
        root.setSpacing(18)

        card = QFrame(objectName="Card")
        card.setFixedWidth(520)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(30, 30, 30, 30)
        lay.setSpacing(12)
        lay.setAlignment(Qt.AlignCenter)

        # --- 1. Logo Image ---
        logo_path = self._get_abs_asset_path("assets/icon.png")
        
        logo_label = QLabel()
        pixmap = QPixmap(logo_path)
        
        if not pixmap.isNull():
            # Scale logo to 120x120 pixels, maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(230, 230, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
        else:
            # Fallback if image is missing
            logo_label.setText("LOGO")
            logo_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #555;")
            logo_label.setAlignment(Qt.AlignCenter)

        lay.addWidget(logo_label)

        # --- 2. Title ---
        title = QLabel("SYNC")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 44px; font-weight: 800;")

        sub = QLabel("Centralized Software Deployment")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet("color:#9aa4b2; font-size: 14px;")

        # --- 3. Button ---
        btn = QPushButton("Go to Deployment →")
        btn.setFixedHeight(44)
        btn.clicked.connect(self.go_deployment.emit)

        # Add to layout
        lay.addWidget(title)
        lay.addWidget(sub)
        lay.addSpacing(10)
        lay.addWidget(btn)

        root.addWidget(card)

    def _get_abs_asset_path(self, rel_path: str) -> str:
        """
        Builds absolute path from this file location.
        This ensures the logo loads correctly regardless of where the script is run from.
        """
        # Get the directory of this file (views/welcome_page.py)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to reach the project root
        project_root = os.path.abspath(os.path.join(base_dir, ".."))
        # Join with the relative path of the asset
        return os.path.join(project_root, rel_path)