from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QLineEdit, QSpinBox, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen

from core.inventory_manager import InventoryManager
from .dialog_base import BaseDialog, CloseButton
from .glass_messagebox import show_glass_message

@dataclass
class EditLabResult:
    lab_name: str
    layout: dict


class EditLabDialog(BaseDialog):
    """
    Edit Lab dialog — allows changing lab name and structure.
    Similar to CreateLabDialog but with IP reassignment option.
    """

    def __init__(self, parent=None, current_lab_name: str = "", current_layout: dict = None):
        super().__init__(parent)
        self.setObjectName("EditLabDialog")
        self.setFixedWidth(620)
        
        self.current_lab_name = current_lab_name
        self.current_layout = current_layout or {"sections": 1, "rows": 1, "cols": 1}
        
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        self.setFocusPolicy(Qt.StrongFocus)
        
        self._result: EditLabResult | None = None
        
        self._build_ui()
        self._finish_init()
        self._wire_signals()
        self._validate_live()
        
        QTimer.singleShot(150, self._set_initial_focus)

    def _set_initial_focus(self):
        """Set initial focus to the lab name input field"""
        if self.lab_name:
            self.lab_name.setFocus()
            self.lab_name.setFocusPolicy(Qt.StrongFocus)
            self.lab_name.setEnabled(True)
            self.lab_name.setVisible(True)
            
    def _build_ui(self):
        self.setStyleSheet(self.BASE_QSS + """
            QLabel#EditLabSubtitle {
                font-size: 11px;
                color: #64748b;
            }
            QLabel#EditLabRowLabel {
                font-size: 11px;
                font-weight: 600;
                color: #64748b;
                letter-spacing: 0.4px;
            }
            QLabel#EditLabDash {
                color: #94a3b8;
                font-size: 16px;
                background: transparent;
            }
            QFrame#EditLabChip {
                background: #f4f6f9;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QLabel#EditLabChipLabel {
                font-size: 12px;
                font-weight: 600;
                color: #475569;
                background: transparent;
            }
            QSpinBox#EditLabSpin {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                color: #0f172a;
                font-size: 13px;
                font-weight: 700;
                padding: 2px 4px;
                min-height: 28px;
            }
            QSpinBox#EditLabSpin:focus {
                border: 1px solid #2563eb;
            }
            QFrame#EditLabWarning {
                background: #fffbeb;
                border: 1px solid #fcd34d;
                border-radius: 8px;
            }
            QLabel#EditLabWarningText {
                color: #92400e;
                font-size: 11px;
                font-weight: 500;
            }
            QLabel#EditLabWarningIcon {
                background: transparent;
                font-size: 13px;
            }
            QLineEdit#EditLabInput {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 0 12px;
                color: #0f172a;
                font-size: 13px;
                selection-background-color: #bfdbfe;
            }
            QLineEdit#EditLabInput:focus {
                border: 1px solid #2563eb;
                background: #ffffff;
            }
            QLineEdit#EditLabInput:hover {
                border: 1px solid #94a3b8;
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(0)

        # ── Header ────────────────────────────────────────────
        hdr = QHBoxLayout()
        hdr.setSpacing(12)

        class EditIconWidget(QLabel):
            def paintEvent(self, event):
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(37, 99, 235, 35))
                painter.drawEllipse(4, 4, 40, 40)
                painter.setPen(QPen(QColor(37, 99, 235), 2.2))
                cx, cy = 24, 24
                # Draw pencil icon
                painter.drawLine(cx - 8, cy + 6, cx + 6, cy - 8)
                painter.drawLine(cx + 2, cy - 8, cx + 8, cy - 2)
                painter.drawLine(cx - 8, cy + 6, cx - 2, cy + 8)
                painter.drawLine(cx - 2, cy + 8, cx + 6, cy - 8)
                if not self.rect().isValid():
                    return
                super().paintEvent(event)

        icon_widget = EditIconWidget()
        icon_widget.setFixedSize(48, 48)

        title_col = QVBoxLayout()
        title_col.setSpacing(3)

        title = QLabel("Edit Laboratory")
        title.setObjectName("DialogTitle")

        subtitle = QLabel(f"Modify configuration for: {self.current_lab_name}")
        subtitle.setObjectName("EditLabSubtitle")
        subtitle.setWordWrap(True)

        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        self.close_btn = CloseButton()
        self.close_btn.setObjectName("CloseBtn")

        hdr.addWidget(icon_widget)
        hdr.addLayout(title_col, 1)
        hdr.addWidget(self.close_btn)
        root.addLayout(hdr)

        root.addSpacing(14)
        root.addWidget(self._divider())
        root.addSpacing(14)

        # ── Form ──────────────────────────────────────────────
        form = QVBoxLayout()
        form.setSpacing(10)

        # Lab Name
        form.addWidget(self._row_label("Lab Name", "EditLabRowLabel"))
        self.lab_name = QLineEdit()
        self.lab_name.setObjectName("EditLabInput")
        self.lab_name.setText(self.current_lab_name)
        self.lab_name.setPlaceholderText("Enter lab name")
        self.lab_name.setFixedHeight(38)
        self.lab_name.setFocusPolicy(Qt.StrongFocus)
        form.addWidget(self.lab_name)

        form.addSpacing(4)
        form.addWidget(self._row_label("New Layout", "EditLabRowLabel"))

        # Layout chips
        chips_row = QHBoxLayout()
        chips_row.setSpacing(10)
        self.sections = self._chip_spin("Sections", 1, 50, self.current_layout.get("sections", 3))
        self.rows     = self._chip_spin("Rows",     1, 50, self.current_layout.get("rows", 7))
        self.cols     = self._chip_spin("Cols",     1, 50, self.current_layout.get("cols", 5))
        chips_row.addWidget(self.sections.container)
        chips_row.addWidget(self.rows.container)
        chips_row.addWidget(self.cols.container)
        form.addLayout(chips_row)

        form.addSpacing(8)
        
        # ── Warning about IP reassignment ────────────────────

        warn_icon = QLabel("⚠️")
        warn_icon.setObjectName("EditLabWarningIcon")
        warn_icon.setFixedWidth(20)
        warn_icon.setAlignment(Qt.AlignCenter)



        form.addSpacing(8)

        # ── Reassign IPs checkbox ────────────────────────────

        # Info about PC count
        self.pc_info_label = QLabel("")
        self.pc_info_label.setObjectName("EditLabRowLabel")
        self.pc_info_label.setStyleSheet("color: #2563eb; font-size: 11px; padding: 4px 0;")
        form.addWidget(self.pc_info_label)

        root.addLayout(form)
        root.addSpacing(12)

        # ── Warning message area (for validation) ─────────────
        self.warn = QFrame()
        self.warn.setObjectName("EditLabWarning")
        wlay2 = QHBoxLayout(self.warn)
        wlay2.setContentsMargins(12, 10, 12, 10)
        wlay2.setSpacing(8)

        self.warn_icon = QLabel("⚠️")
        self.warn_icon.setObjectName("EditLabWarningIcon")
        self.warn_icon.setFixedWidth(20)
        self.warn_icon.setAlignment(Qt.AlignCenter)

        self.warn_text = QLabel("")
        self.warn_text.setObjectName("EditLabWarningText")
        self.warn_text.setWordWrap(True)

        wlay2.addWidget(self.warn_icon)
        wlay2.addWidget(self.warn_text, 1)
        root.addWidget(self.warn)

        root.addSpacing(12)
        root.addWidget(self._divider())
        root.addSpacing(12)

        # ── Buttons ───────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("CancelBtn")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setFixedHeight(36)
        self.cancel_btn.setFixedWidth(110)

        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setObjectName("PrimaryBtn")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setFixedHeight(36)
        self.save_btn.setFixedWidth(130)

        btn_row.addWidget(self.cancel_btn)
        btn_row.addWidget(self.save_btn)
        root.addLayout(btn_row)

    def _row_label(self, text: str, obj: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName(obj)
        return lbl

    def _chip_spin(self, caption: str, mn: int, mx: int, value: int):
        container = QFrame()
        container.setObjectName("EditLabChip")

        lay = QHBoxLayout(container)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(10)

        cap = QLabel(caption)
        cap.setObjectName("EditLabChipLabel")

        sp = QSpinBox()
        sp.setObjectName("EditLabSpin")
        sp.setRange(mn, mx)
        sp.setValue(value)
        sp.setButtonSymbols(QSpinBox.NoButtons)
        sp.setFixedWidth(56)
        sp.setAlignment(Qt.AlignCenter)
        sp.setFocusPolicy(Qt.StrongFocus)

        lay.addWidget(cap)
        lay.addStretch()
        lay.addWidget(sp)

        container.spin = sp
        return type("SpinWrap", (), {"container": container, "spin": sp})

    def _wire_signals(self):
        self.close_btn.clicked.connect(self.reject)
        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self._on_save)
        self.lab_name.textChanged.connect(self._validate_live)
        self.sections.spin.valueChanged.connect(self._validate_live)
        self.rows.spin.valueChanged.connect(self._validate_live)
        self.cols.spin.valueChanged.connect(self._validate_live)

    def _required_count(self) -> int:
        return self.sections.spin.value() * self.rows.spin.value() * self.cols.spin.value()

    def _validate_live(self):
        """Validate the form inputs"""
        name = self.lab_name.text().strip()
        need = self._required_count()
        
        # Check if lab name is empty
        if not name:
            self.warn.show()
            self.warn_text.setText("Please enter a lab name.")
            self.save_btn.setEnabled(False)
            return
            
        # Check if lab name changed and if it already exists (except current lab)
        if name != self.current_lab_name:
            inventory = InventoryManager()
            all_labs = inventory.get_all_labs()
            if name in all_labs:
                self.warn.show()
                self.warn_text.setText(f"A lab with name '{name}' already exists. Please choose a different name.")
                self.save_btn.setEnabled(False)
                return
        
        # Check if layout changed
        layout_changed = (
            self.sections.spin.value() != self.current_layout.get("sections") or
            self.rows.spin.value() != self.current_layout.get("rows") or
            self.cols.spin.value() != self.current_layout.get("cols")
        )
        
        # Update warning about PC count if layout changed
        # Hide main warning if all is good
        self.warn.hide()
        self.save_btn.setEnabled(True)

    def _on_save(self):
        """Handle save button click"""
        self._validate_live()
        if not self.save_btn.isEnabled():
            return
        
        # Check if layout actually changed
        layout_changed = (
            self.sections.spin.value() != self.current_layout.get("sections") or
            self.rows.spin.value() != self.current_layout.get("rows") or
            self.cols.spin.value() != self.current_layout.get("cols")
        )
        
        new_layout = {
            "sections": self.sections.spin.value(),
            "rows": self.rows.spin.value(),
            "cols": self.cols.spin.value()
        }
        
        # If layout didn't change and name didn't change, no need to do anything
        if not layout_changed and self.lab_name.text().strip() == self.current_lab_name:
            show_glass_message(
                self,
                "No Changes",
                "No changes were made to the lab configuration.",
                icon=QMessageBox.Information
            )
            return
        
        self._result = EditLabResult(
            lab_name=self.lab_name.text().strip(),
            layout=new_layout
        )
        self._dismiss(accepted=True)

    def get_result(self) -> Optional[EditLabResult]:
        """Get the result from the dialog"""
        return self._result
