import ipaddress
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QSpinBox, QPushButton, QFrame, QMessageBox, QGridLayout
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
        self.setMinimumWidth(560)

        
        self.setObjectName("CreateLabDialog")

        self._cached_ips: list[str] = []
        self._cached_layout: dict | None = None
        self._cached_name: str = ""

        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 18)
        root.setSpacing(14)

        
        title = QLabel("Create Lab Structure")
        title.setObjectName("DialogTitle")
        root.addWidget(title)

        subtitle = QLabel("Define sections, layout size, and an IP range for automatic assignment.")
        subtitle.setObjectName("DialogSubText")
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        card = QFrame()
        card.setObjectName("DialogCard")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(16, 16, 16, 16)
        card_lay.setSpacing(14)

        lab_title = QLabel("Lab Info")
        lab_title.setObjectName("DialogSectionHeader")
        card_lay.addWidget(lab_title)

        name_grid = QGridLayout()
        name_grid.setHorizontalSpacing(12)
        name_grid.setVerticalSpacing(10)

        lbl_name = QLabel("Lab name")
        lbl_name.setObjectName("DialogFieldLabel")
        self.lab_name = QLineEdit()
        self.lab_name.setPlaceholderText("e.g., CSL 1 & 2")
        self.lab_name.setObjectName("DialogInput")

        name_grid.addWidget(lbl_name, 0, 0)
        name_grid.addWidget(self.lab_name, 0, 1)
        card_lay.addLayout(name_grid)

       
        layout_title = QLabel("Layout")
        layout_title.setObjectName("DialogSectionHeader")
        card_lay.addWidget(layout_title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)

        self.sections = QSpinBox()
        self.sections.setRange(1, 10)
        self.sections.setValue(3)
        self.sections.setObjectName("DialogSpin")

        self.rows = QSpinBox()
        self.rows.setRange(1, 30)
        self.rows.setValue(7)
        self.rows.setObjectName("DialogSpin")

        self.cols = QSpinBox()
        self.cols.setRange(1, 30)
        self.cols.setValue(5)
        self.cols.setObjectName("DialogSpin")

        grid.addWidget(QLabel("Sections"), 0, 0)
        grid.addWidget(self.sections, 0, 1)

        grid.addWidget(QLabel("Rows / section"), 0, 2)
        grid.addWidget(self.rows, 0, 3)

        grid.addWidget(QLabel("Cols / section"), 0, 4)
        grid.addWidget(self.cols, 0, 5)

     
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        grid.setColumnStretch(5, 1)

        card_lay.addLayout(grid)

        ip_title = QLabel("IP Range")
        ip_title.setObjectName("DialogSectionHeader")
        card_lay.addWidget(ip_title)

        ip_grid = QGridLayout()
        ip_grid.setHorizontalSpacing(12)
        ip_grid.setVerticalSpacing(10)

        self.start_ip = QLineEdit()
        self.start_ip.setPlaceholderText("192.168.1.10")
        self.start_ip.setObjectName("DialogInput")

        self.end_ip = QLineEdit()
        self.end_ip.setPlaceholderText("192.168.1.200")
        self.end_ip.setObjectName("DialogInput")

        ip_grid.addWidget(QLabel("Start IP"), 0, 0)
        ip_grid.addWidget(self.start_ip, 0, 1)
        ip_grid.addWidget(QLabel("End IP"), 1, 0)
        ip_grid.addWidget(self.end_ip, 1, 1)

        card_lay.addLayout(ip_grid)

       
        self.preview = QLabel("")
        self.preview.setObjectName("DialogHintText")
        card_lay.addWidget(self.preview)

        root.addWidget(card)

        btns = QHBoxLayout()
        btns.setSpacing(10)

        btns.addStretch()

        cancel = QPushButton("Cancel")
        cancel.setObjectName("SecondaryBtn")
        cancel.clicked.connect(self.reject)

        create = QPushButton("Create Lab")
        create.setObjectName("PrimaryBtn")
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

        self._cached_name = name
        self._cached_layout = layout
        self._cached_ips = ips

        self.accept()

    def get_data(self) -> dict:
        if self._cached_layout and self._cached_ips and self._cached_name:
            return {
                "lab_name": self._cached_name,
                "layout": self._cached_layout,
                "ips": self._cached_ips,
            }

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
