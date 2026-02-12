from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QPainter, QBrush, QColor, QPen, QPainterPath


class ConfirmDeleteDialog(QDialog):
    """
    Modern confirm dialog:
    - Frameless + translucent background
    - Rounded card container
    - Professional icon (custom drawn)
    - Title + subtitle (rich text)
    - Cancel + Delete buttons
    - Smooth fade-in animation
    """

    def __init__(self, parent=None, lab_name: str = "", pcs_count: int = 0):
        super().__init__(parent)
        self.setObjectName("ConfirmDeleteDialog")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setModal(True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self._lab_name = lab_name
        self._pcs_count = pcs_count

        self._build_ui(lab_name, pcs_count)
        self._animate_in()

    def _build_ui(self, lab_name: str, pcs_count: int):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        card = QFrame(self)
        card.setObjectName("ConfirmDeleteCard")
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(16)

        # Header row with custom icon widget
        header = QHBoxLayout()
        header.setSpacing(16)

        # Custom icon widget instead of emoji
        icon_widget = QFrame()
        icon_widget.setObjectName("ConfirmDeleteIconContainer")
        icon_widget.setFixedSize(48, 48)
        
        # Create a custom drawn icon
        class DeleteIcon(QLabel):
            def paintEvent(self, event):
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                
                # Draw circle background
                painter.setBrush(QColor(239, 68, 68, 40))  # Red with low opacity
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(4, 4, 40, 40)
                
                # Draw trash can icon
                painter.setPen(QPen(QColor(239, 68, 68), 2))
                painter.setBrush(QColor(239, 68, 68, 30))
                
                # Trash body
                painter.drawRoundedRect(14, 18, 20, 22, 3, 3)
                # Trash lid
                painter.drawLine(10, 14, 38, 14)
                painter.drawLine(16, 10, 32, 10)
                # Lines on trash body
                painter.drawLine(20, 24, 20, 34)
                painter.drawLine(28, 24, 28, 34)
                
        icon_label = DeleteIcon()
        icon_label.setFixedSize(48, 48)
        
        icon_layout = QVBoxLayout(icon_widget)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.addWidget(icon_label, 0, Qt.AlignCenter)
        
        header.addWidget(icon_widget)

        # Title column
        title_col = QVBoxLayout()
        title_col.setSpacing(8)

        title = QLabel("Delete Laboratory?")
        title.setObjectName("ConfirmDeleteTitle")
        title_font = QFont("Segoe UI", 16, QFont.Bold)
        title.setFont(title_font)

        # Format the subtitle with better visual hierarchy
        subtitle_text = (
            f"You are about to delete <span style='font-weight:700; color:#ef4444;'>{lab_name}</span> "
            f"which contains <span style='font-weight:700;'>{pcs_count}</span> workstation(s).<br><br>"
            f"This action <span style='font-weight:700;'>cannot be undone</span>."
        )
        subtitle = QLabel(subtitle_text)
        subtitle.setObjectName("ConfirmDeleteSubtitle")
        subtitle.setTextFormat(Qt.RichText)
        subtitle.setWordWrap(True)
        subtitle_font = QFont("Segoe UI", 12)
        subtitle.setFont(subtitle_font)

        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        header.addLayout(title_col, 1)

        layout.addLayout(header)

        # Divider with gradient
        divider = QFrame()
        divider.setObjectName("ConfirmDeleteDivider")
        divider.setFixedHeight(2)
        layout.addWidget(divider)

        # Warning summary
        warning_frame = QFrame()
        warning_frame.setObjectName("ConfirmDeleteWarning")
        warning_layout = QHBoxLayout(warning_frame)
        warning_layout.setContentsMargins(12, 12, 12, 12)
        warning_layout.setSpacing(12)
        
        warning_icon = QLabel("⚠️")
        warning_icon.setObjectName("ConfirmDeleteWarningIcon")
        warning_icon.setFixedWidth(24)
        warning_icon.setAlignment(Qt.AlignCenter)
        
        warning_text = QLabel("This operation is permanent and cannot be recovered")
        warning_text.setObjectName("ConfirmDeleteWarningText")
        warning_text.setWordWrap(True)
        
        warning_layout.addWidget(warning_icon)
        warning_layout.addWidget(warning_text, 1)
        
        layout.addWidget(warning_frame)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("ConfirmCancelBtn")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedHeight(42)
        cancel_btn.setFixedWidth(100)
        cancel_btn.clicked.connect(self.reject)

        delete_btn = QPushButton("Delete ")
        delete_btn.setObjectName("ConfirmDeleteBtn")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setFixedHeight(42)
        delete_btn.setFixedWidth(140)
        delete_btn.clicked.connect(self.accept)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(delete_btn)
        layout.addLayout(btn_row)

        root.addWidget(card)

        self.setFixedWidth(480)

    def _animate_in(self):
        self.setWindowOpacity(0.0)
        self._fade = QPropertyAnimation(self, b"windowOpacity")
        self._fade.setDuration(200)
        self._fade.setStartValue(0.0)
        self._fade.setEndValue(1.0)
        self._fade.setEasingCurve(QEasingCurve.OutCubic)
        self._fade.start()