import re
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)

_IPV4_REGEX = re.compile(
    r"^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"
    r"(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$"
)

class EditPcIpDialog(QDialog):
    def __init__(self, pc_name: str, current_ip: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit IP Address")
        self.new_ip = None

        lay = QVBoxLayout(self)

        lay.addWidget(QLabel(f"{pc_name}"))

        self.ip_edit = QLineEdit(current_ip)
        lay.addWidget(self.ip_edit)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save)
        lay.addWidget(save_btn)

    def _save(self):
        ip = self.ip_edit.text().strip()

        if not _IPV4_REGEX.match(ip):
            QMessageBox.warning(self, "Invalid IP", "Enter a valid IPv4 address")
            return

        self.new_ip = ip
        self.accept()
