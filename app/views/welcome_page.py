from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Signal, Qt

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

        title = QLabel("SYNC")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 44px; font-weight: 800;")

        sub = QLabel("Centralized Software Deployment")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet("color:#9aa4b2; font-size: 14px;")

        btn = QPushButton("Go to Deployment →")
        btn.setFixedHeight(44)
        btn.clicked.connect(self.go_deployment.emit)

        lay.addWidget(title)
        lay.addWidget(sub)
        lay.addSpacing(10)
        lay.addWidget(btn)

        root.addWidget(card)
