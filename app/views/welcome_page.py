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

       
        card = QFrame()
        card.setObjectName("WelcomeCard")
        card.setFixedWidth(520)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(30, 30, 30, 30)
        lay.setSpacing(12)
        lay.setAlignment(Qt.AlignCenter)

    
        logo_path = self._get_abs_asset_path("assets/icon.png")

        logo_label = QLabel()
        logo_label.setObjectName("WelcomeLogo")

        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(230, 230, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
        else:
            logo_label.setText("LOGO")
            logo_label.setObjectName("WelcomeLogoFallback")
            logo_label.setAlignment(Qt.AlignCenter)

        lay.addWidget(logo_label)

        title = QLabel("SYNC")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("WelcomeTitle")

        sub = QLabel("Centralized Software Deployment")
        sub.setAlignment(Qt.AlignCenter)
        sub.setObjectName("WelcomeSub")

      
        btn = QPushButton("Go to Deployment →")
        btn.setFixedHeight(44)
        btn.setObjectName("PrimaryBtn")
        btn.clicked.connect(self.go_deployment.emit)

        lay.addWidget(title)
        lay.addWidget(sub)
        lay.addSpacing(10)
        lay.addWidget(btn)

        root.addWidget(card)

    def _get_abs_asset_path(self, rel_path: str) -> str:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(base_dir, ".."))
        return os.path.join(project_root, rel_path)
