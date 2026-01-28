import ipaddress
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QSpinBox, QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import Qt


def _generate_ips(start_ip: str, end_ip: str, count: int) -> list[str]:
    try:
        start = ipaddress.ip_address(start_ip.strip())
        end = ipaddress.ip_address(end_ip.strip())
    except Exception:
        raise ValueError("Invalid IP address format.")

    if start.version != 4 or end.version != 4:
        raise ValueError("Only IPv4 is supported.")

    if int(end) < int(start):
        raise ValueError("End IP must be greater than or equal to Start IP.")

    available = int(end) - int(start) + 1
    if count > available:
        raise ValueError(f"IP range has only {available} addresses, but you need {count}.")

    return [str(ipaddress.ip_address(int(start) + i)) for i in range(count)]


class CreateLabDialog(QDialog):
    """
    Admin creates lab layout + IP assignment rules.
    Assign IPs section1 row-by-row, then section2, etc.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Lab")
        self.setModal(True)
        self.setMinimumWidth(480)

        # ✅ cache generated data so get_data() cannot fail later
        self._cached_ips: list[str] = []
        self._cached_layout: dict | None = None
        self._cached_name: str = ""

        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        title = QLabel("Create Lab Structure")
        title.setStyleSheet("font-size:18px; font-weight:800;")
        root.addWidget(title)

        card = QFrame()
        card.setObjectName("Card")
        card.setStyleSheet("""
            QFrame#Card { background:#1b1b1b; border:1px solid #2a2a2a; border-radius:12px; }
            QLabel { color: #cbd5e1; }
        """)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(10)

        # Lab name
        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Lab name:"))
        self.lab_name = QLineEdit()
        self.lab_name.setPlaceholderText("e.g., CSL 1&2")
        r1.addWidget(self.lab_name, 1)
        lay.addLayout(r1)

        # Layout
        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Sections:"))
        self.sections = QSpinBox()
        self.sections.setRange(1, 10)
        self.sections.setValue(3)
        r2.addWidget(self.sections)

        r2.addSpacing(10)
        r2.addWidget(QLabel("Rows/section:"))
        self.rows = QSpinBox()
        self.rows.setRange(1, 30)
        self.rows.setValue(7)
        r2.addWidget(self.rows)

        r2.addSpacing(10)
        r2.addWidget(QLabel("Cols/section:"))
        self.cols = QSpinBox()
        self.cols.setRange(1, 30)
        self.cols.setValue(5)
        r2.addWidget(self.cols)

        r2.addStretch()
        lay.addLayout(r2)

        # IP assignment
        r3 = QHBoxLayout()
        r3.addWidget(QLabel("Start IP:"))
        self.start_ip = QLineEdit()
        self.start_ip.setPlaceholderText("192.168.1.10")
        r3.addWidget(self.start_ip, 1)
        lay.addLayout(r3)

        r4 = QHBoxLayout()
        r4.addWidget(QLabel("End IP:"))
        self.end_ip = QLineEdit()
        self.end_ip.setPlaceholderText("192.168.1.200")
        r4.addWidget(self.end_ip, 1)
        lay.addLayout(r4)

        self.preview = QLabel("")
        self.preview.setStyleSheet("color:#9aa4b2;")
        lay.addWidget(self.preview)

        root.addWidget(card)

        # Buttons
        btns = QHBoxLayout()
        btns.addStretch()

        cancel = QPushButton("Cancel")
        cancel.setStyleSheet("background:#2a2a2a;")
        cancel.clicked.connect(self.reject)

        create = QPushButton("Create Lab")
        create.clicked.connect(self._validate_and_accept)

        btns.addWidget(cancel)
        btns.addWidget(create)
        root.addLayout(btns)

        # live preview
        self.sections.valueChanged.connect(self._update_preview)
        self.rows.valueChanged.connect(self._update_preview)
        self.cols.valueChanged.connect(self._update_preview)
        self._update_preview()

    def _update_preview(self):
        total = self.sections.value() * self.rows.value() * self.cols.value()
        self.preview.setText(f"Total PCs that will be created: {total}")

    def _validate_and_accept(self):
        name = self.lab_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing", "Please enter a lab name.")
            return

        total = self.sections.value() * self.rows.value() * self.cols.value()
        s_ip = self.start_ip.text().strip()
        e_ip = self.end_ip.text().strip()

        if not s_ip or not e_ip:
            QMessageBox.warning(self, "Missing", "Please enter Start IP and End IP.")
            return

        layout = {
            "sections": self.sections.value(),
            "rows": self.rows.value(),
            "cols": self.cols.value(),
        }

        try:
            ips = _generate_ips(s_ip, e_ip, total)
        except Exception as e:
            QMessageBox.critical(self, "Invalid IP Range", str(e))
            return

        # ✅ cache once (prevents get_data() from failing later)
        self._cached_name = name
        self._cached_layout = layout
        self._cached_ips = ips

        self.accept()

    def get_data(self) -> dict:
        """
        Return cached values generated during _validate_and_accept().
        If get_data() is called without accept(), we fallback to computing (safe).
        """
        if self._cached_layout and self._cached_ips and self._cached_name:
            return {
                "lab_name": self._cached_name,
                "layout": self._cached_layout,
                "ips": self._cached_ips,
            }

        # Fallback (shouldn't happen if dialog accepted properly)
        total = self.sections.value() * self.rows.value() * self.cols.value()
        ips = _generate_ips(self.start_ip.text(), self.end_ip.text(), total)
        return {
            "lab_name": self.lab_name.text().strip(),
            "layout": {
                "sections": self.sections.value(),
                "rows": self.rows.value(),
                "cols": self.cols.value(),
            },
            "ips": ips,
        }
