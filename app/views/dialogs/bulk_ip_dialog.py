from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton

class BulkIpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bulk IP Assign")

        lay = QVBoxLayout(self)

        lay.addWidget(QLabel("Start IP (e.g. 192.168.1.100)"))
        self.start_ip = QLineEdit()
        lay.addWidget(self.start_ip)

        btn = QPushButton("Apply")
        btn.clicked.connect(self.accept)
        lay.addWidget(btn)

        self.setMinimumSize(420, 180)

