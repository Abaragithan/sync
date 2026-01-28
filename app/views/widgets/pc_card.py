from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal, Qt

class PcCard(QFrame):
    toggled = Signal(str, bool)     
    delete_requested = Signal(str)  

    def __init__(self, name: str, ip: str):
        super().__init__()
        self.ip = ip
        self.selected = False

        
        self.setFixedSize(70, 70)

        self.setObjectName("PcCard")
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
        """)
        self.setProperty("selected", False)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 8, 10, 8)
        root.setSpacing(4)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(6)

        
        title = QLabel(name)
        title.setStyleSheet("font-weight: 700; font-size: 12px;")
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        top.addWidget(title)
        top.addStretch()

        # del_btn = QPushButton("✕")
        # del_btn.setFixedSize(22, 22)
        # del_btn.setStyleSheet("""
        #     QPushButton {
        #         background: #2b2b2b;
        #         border: none;
        #         border-radius: 6px;
        #         color: #ddd;
        #         font-size: 11px;
        #     }
        #     QPushButton:hover { background: #3a3a3a; }
        # """)
        # del_btn.clicked.connect(lambda: self.delete_requested.emit(self.ip))
        # top.addWidget(del_btn)

        ip_lbl = QLabel(ip)
        ip_lbl.setStyleSheet("color:#9aa4b2; font-size: 11px;")

        root.addLayout(top)
        root.addWidget(ip_lbl)

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        self.set_selected(not self.selected)

    def set_selected(self, value: bool):
        self.selected = value
        self.setProperty("selected", value)
        self.style().unpolish(self)
        self.style().polish(self)
        self.toggled.emit(self.ip, value)
