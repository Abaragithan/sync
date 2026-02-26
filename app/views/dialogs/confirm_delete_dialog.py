from __future__ import annotations

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame
)
from PySide6.QtCore import Qt, QPropertyAnimation, QTimer, QPoint
from PySide6.QtGui import QFont

from .dialog_base import BaseDialog, CloseButton


class ConfirmDeleteDialog(BaseDialog):
    """
    Delete confirmation — red destructive style.
    Matches glass_messagebox Critical type: dimmed backdrop,
    rounded white card, shake animation, fade-in.
    Same functionality as original (accept / reject).
    """

    def __init__(self, parent=None, lab_name: str = "", pcs_count: int = 0):
        super().__init__(parent)
        self.setObjectName("ConfirmDeleteDialog")
        self.setFixedSize(440, 256)

        self._lab_name  = lab_name
        self._pcs_count = pcs_count

        self._build_ui(lab_name, pcs_count)
        self._finish_init()

        # Shake after entrance to signal danger (same as glass_messagebox Critical)
        QTimer.singleShot(260, self._shake)

    def _build_ui(self, lab_name: str, pcs_count: int):
        self.setStyleSheet(self.BASE_QSS + """
            QLabel#DeleteIconBg {
                background: #fef2f2;
                border-radius: 22px;
                font-size: 20px;
            }
            QLabel#ConfirmDeleteTitle {
                font-size: 15px;
                font-weight: 700;
                color: #0f172a;
            }
            QLabel#ConfirmDeleteSubtitle {
                font-size: 12px;
                color: #475569;
            }
            QFrame#WarnBox {
                background: #fef2f2;
                border: 1px solid #fecaca;
                border-radius: 8px;
            }
            QLabel#WarnText {
                color: #b91c1c;
                font-size: 11px;
                font-weight: 600;
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(0)

        # ── Header ────────────────────────────────────────────
        hdr = QHBoxLayout()
        hdr.setSpacing(14)

        # Red-tinted icon circle
        icon_lbl = QLabel("🗑️")
        icon_lbl.setObjectName("DeleteIconBg")
        icon_lbl.setFixedSize(44, 44)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 18))

        # Title + subtitle stacked
        title_col = QVBoxLayout()
        title_col.setSpacing(4)

        title = QLabel("Delete Laboratory?")
        title.setObjectName("ConfirmDeleteTitle")

        subtitle_text = (
            f"<span style='font-weight:600; color:#dc2626;'>{lab_name}</span> "
            f"contains <span style='font-weight:600;'>{pcs_count}</span> workstation(s)."
        )
        subtitle = QLabel(subtitle_text)
        subtitle.setObjectName("ConfirmDeleteSubtitle")
        subtitle.setTextFormat(Qt.RichText)
        subtitle.setWordWrap(True)

        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        self.close_btn = CloseButton()
        self.close_btn.setObjectName("CloseBtn")
        self.close_btn.clicked.connect(self.reject)

        hdr.addWidget(icon_lbl)
        hdr.addLayout(title_col, 1)
        hdr.addWidget(self.close_btn)
        root.addLayout(hdr)

        root.addSpacing(14)
        root.addWidget(self._divider())
        root.addSpacing(14)

        # ── Warning badge ─────────────────────────────────────
        warn_box = QFrame()
        warn_box.setObjectName("WarnBox")
        wlay = QHBoxLayout(warn_box)
        wlay.setContentsMargins(12, 10, 12, 10)
        wlay.setSpacing(8)

        warn_icon = QLabel("⚠")
        warn_icon.setFixedWidth(16)
        warn_icon.setAlignment(Qt.AlignCenter)
        warn_icon.setStyleSheet(
            "color: #dc2626; font-weight: 700; font-size: 13px; background: transparent;"
        )

        warn_text = QLabel("This action is permanent and cannot be undone.")
        warn_text.setObjectName("WarnText")
        warn_text.setWordWrap(True)

        wlay.addWidget(warn_icon)
        wlay.addWidget(warn_text, 1)
        root.addWidget(warn_box)

        root.addStretch()
        root.addWidget(self._divider())
        root.addSpacing(12)

        # ── Buttons ───────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("CancelBtn")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedHeight(36)
        cancel_btn.setFixedWidth(110)
        cancel_btn.clicked.connect(self.reject)

        delete_btn = QPushButton("Delete Lab")
        delete_btn.setObjectName("DeleteBtn")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setFixedHeight(36)
        delete_btn.setFixedWidth(120)
        delete_btn.clicked.connect(self._confirm)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(delete_btn)
        root.addLayout(btn_row)

    # ── Shake animation ───────────────────────────────────────
    def _shake(self):
        sp = self.pos()
        self._shake_anim = QPropertyAnimation(self, b"pos")
        self._shake_anim.setDuration(300)
        self._shake_anim.setKeyValueAt(0.00, sp)
        self._shake_anim.setKeyValueAt(0.15, QPoint(sp.x() - 7, sp.y()))
        self._shake_anim.setKeyValueAt(0.35, QPoint(sp.x() + 7, sp.y()))
        self._shake_anim.setKeyValueAt(0.55, QPoint(sp.x() - 4, sp.y()))
        self._shake_anim.setKeyValueAt(0.75, QPoint(sp.x() + 2, sp.y()))
        self._shake_anim.setKeyValueAt(1.00, sp)
        self._shake_anim.start()

    # ── Unchanged functionality ───────────────────────────────
    def _confirm(self):
        self._dismiss(accepted=True)