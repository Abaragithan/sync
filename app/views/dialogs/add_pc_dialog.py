from __future__ import annotations
import re

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox, QSizePolicy, QWidget
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QPoint, Property
from PySide6.QtGui import QColor, QFont, QPainter, QMouseEvent, QEnterEvent, QPen, QBrush
from PySide6.QtWidgets import QGraphicsDropShadowEffect

_IPV4_REGEX = re.compile(
    r"^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"
    r"(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$"
)


class _DimOverlay(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self._alpha = 0
        self.setGeometry(parent.rect())
        self.raise_(); self.show()
        self._anim = QPropertyAnimation(self, b"dim_alpha")
        self._anim.setDuration(180)
        self._anim.setStartValue(0)
        self._anim.setEndValue(160)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.start()

    def _get_alpha(self): return self._alpha
    def _set_alpha(self, v): self._alpha = v; self.update()
    dim_alpha = Property(int, _get_alpha, _set_alpha)

    def fade_out(self, done_cb=None):
        self._anim2 = QPropertyAnimation(self, b"dim_alpha")
        self._anim2.setDuration(150)
        self._anim2.setStartValue(self._alpha)
        self._anim2.setEndValue(0)
        self._anim2.setEasingCurve(QEasingCurve.InCubic)
        if done_cb: self._anim2.finished.connect(done_cb)
        self._anim2.start()

    def paintEvent(self, _):
        p = QPainter(self); p.fillRect(self.rect(), QColor(0, 0, 0, self._alpha)); p.end()


class CloseButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(32, 32)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self._hovered = False

    def enterEvent(self, event: QEnterEvent):
        self._hovered = True; self.update(); super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False; self.update(); super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(239, 68, 68, 30)) if self._hovered else Qt.transparent)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(4, 4, 24, 24)
        painter.setPen(QPen(QColor(239, 68, 68) if self._hovered else QColor(156, 163, 175),
                           2.5 if self._hovered else 2))
        m = 11
        painter.drawLine(m, m, 32 - m, 32 - m)
        painter.drawLine(32 - m, m, m, 32 - m)


class AddPcDialog(QDialog):
    def __init__(self, parent=None, default_name: str = "", default_ip: str = ""):
        super().__init__(parent)
        self.setObjectName("AddPcDialog")
        self.setWindowTitle("Add PC")
        self.setModal(True)

        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self._drag_position: QPoint | None = None
        self.setFixedSize(480, 300)
        self.setWindowOpacity(0.0)

        self._default_name = default_name.strip()
        self._default_ip   = default_ip.strip()

        # Dim overlay
        self._overlay: _DimOverlay | None = None
        if parent:
            self._overlay = _DimOverlay(parent)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28); shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)

        self._build_ui()
        QTimer.singleShot(0, self._animate_in)

    # ── Dragging ──────────────────────────────────────────────
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_position = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_position is not None:
            delta = event.globalPosition().toPoint() - self._drag_position
            self.move(self.pos() + delta)
            self._drag_position = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_position = None

    # ── Paint ─────────────────────────────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(252, 252, 252)))
        painter.drawRoundedRect(r, 12, 12)
        painter.setPen(QPen(QColor(0, 0, 0, 28), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(r.adjusted(1, 1, -1, -1), 11, 11)
        painter.end()
        super().paintEvent(event)

    # ── UI ────────────────────────────────────────────────────
    def _build_ui(self):
        self.setStyleSheet("""
            QLabel { background: transparent; color: #1a1a1a; }
            QLabel#DialogTitle { font-size: 15px; font-weight: 700; color: #0f172a; }
            QLabel#DialogHint  { font-size: 12px; color: #64748b; }
            QLabel#FieldLabel  { font-size: 11px; font-weight: 600; color: #64748b; }
            QFrame#Divider {
                background: #edf0f5; border: none;
                min-height: 1px; max-height: 1px;
            }
            QLineEdit {
                background: #f8fafc; border: 1px solid #e2e8f0;
                border-radius: 8px; padding: 0 12px; color: #0f172a;
                font-size: 13px; font-family: 'Consolas', monospace;
                selection-background-color: #bfdbfe;
            }
            QLineEdit:focus { border: 1px solid #3b82f6; background: #fff; }
            QLineEdit:hover { border: 1px solid #94a3b8; }
            QPushButton#CancelBtn {
                background: #f1f4f9; border: 1px solid #e2e8f0;
                border-radius: 8px; color: #475569;
                font-size: 13px; font-weight: 600;
            }
            QPushButton#CancelBtn:hover { background: #e8ecf4; border-color: #c8cdd8; color: #1e293b; }
            QPushButton#CancelBtn:pressed { background: #dde2ec; }
            QPushButton#PrimaryBtn {
                background: #2563eb; border: none; border-radius: 8px;
                color: white; font-size: 13px; font-weight: 700;
            }
            QPushButton#PrimaryBtn:hover   { background: #1d4ed8; }
            QPushButton#PrimaryBtn:pressed { background: #1e40af; }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 22)
        root.setSpacing(16)

        # Header
        hdr = QHBoxLayout()
        hdr.setSpacing(10)

        icon = QLabel("➕")
        icon.setFixedSize(32, 32)
        icon.setAlignment(Qt.AlignCenter)
        icon.setFont(QFont("Segoe UI Emoji", 16))

        title = QLabel("Add New PC")
        title.setObjectName("DialogTitle")

        self.close_btn = CloseButton()
        self.close_btn.clicked.connect(self.reject)

        hdr.addWidget(icon)
        hdr.addWidget(title, 1)
        hdr.addWidget(self.close_btn)
        root.addLayout(hdr)

        div = QFrame(); div.setObjectName("Divider"); root.addWidget(div)

        # Fields
        def field_row(label_text, widget):
            row = QHBoxLayout(); row.setSpacing(12)
            lbl = QLabel(label_text); lbl.setObjectName("FieldLabel")
            lbl.setFixedWidth(110); lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row.addWidget(lbl); row.addWidget(widget, 1)
            return row

        fields = QVBoxLayout(); fields.setSpacing(12)

        self.name_edit = QLineEdit()
        self.name_edit.setObjectName("AddPcInput")
        self.name_edit.setPlaceholderText("e.g. PC-106")
        self.name_edit.setText(self._default_name)
        self.name_edit.setFixedHeight(38)
        fields.addLayout(field_row("PC NAME", self.name_edit))

        self.ip_edit = QLineEdit()
        self.ip_edit.setObjectName("AddPcInput")
        self.ip_edit.setPlaceholderText("e.g. 192.168.1.100")
        self.ip_edit.setText(self._default_ip)
        self.ip_edit.setFixedHeight(38)
        fields.addLayout(field_row("IP ADDRESS", self.ip_edit))

        root.addLayout(fields)

        hint = QLabel("Enter a valid PC name and IPv4 address.")
        hint.setObjectName("DialogHint")
        root.addWidget(hint)

        root.addStretch()

        div2 = QFrame(); div2.setObjectName("Divider"); root.addWidget(div2)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10); btn_row.setContentsMargins(0, 6, 0, 0)
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("CancelBtn")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedHeight(36); cancel_btn.setFixedWidth(110)
        cancel_btn.clicked.connect(self.reject)

        add_btn = QPushButton("Add PC")
        add_btn.setObjectName("PrimaryBtn")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedHeight(36); add_btn.setFixedWidth(110)
        add_btn.clicked.connect(self._add)

        btn_row.addWidget(cancel_btn); btn_row.addWidget(add_btn)
        root.addLayout(btn_row)

    # ── Animation ─────────────────────────────────────────────
    def _animate_in(self):
        self._center_on_parent()
        self._start_pos = self.pos()
        start = QPoint(self._start_pos.x(), self._start_pos.y() - 12)
        self.move(start); self.setWindowOpacity(0.0)

        self._op_anim = QPropertyAnimation(self, b"windowOpacity")
        self._op_anim.setDuration(200); self._op_anim.setStartValue(0.0)
        self._op_anim.setEndValue(1.0); self._op_anim.setEasingCurve(QEasingCurve.OutCubic)

        self._pos_anim = QPropertyAnimation(self, b"pos")
        self._pos_anim.setDuration(220); self._pos_anim.setStartValue(start)
        self._pos_anim.setEndValue(self._start_pos); self._pos_anim.setEasingCurve(QEasingCurve.OutCubic)

        self._op_anim.start(); self._pos_anim.start()

    def _center_on_parent(self):
        if not self.parent(): return
        pg = self.parent().geometry()
        self.move(pg.x() + pg.width() // 2 - self.width() // 2,
                  pg.y() + pg.height() // 2 - self.height() // 2)

    def showEvent(self, event):
        super().showEvent(event)
        self._center_on_parent()
        if self._overlay and self.parent():
            self._overlay.setGeometry(self.parent().rect())
            self._overlay.raise_(); self.raise_()

    def _dismiss(self, accepted: bool):
        for name in ("_op_anim", "_pos_anim"):
            obj = getattr(self, name, None)
            if obj:
                try: obj.stop()
                except Exception: pass
        self._exit_anim = QPropertyAnimation(self, b"windowOpacity")
        self._exit_anim.setDuration(130)
        self._exit_anim.setStartValue(self.windowOpacity())
        self._exit_anim.setEndValue(0.0)
        self._exit_anim.setEasingCurve(QEasingCurve.InCubic)
        def _finish():
            if self._overlay:
                self._overlay.fade_out(done_cb=lambda: (
                    self._overlay.deleteLater(),
                    self.accept() if accepted else super(AddPcDialog, self).reject()
                ))
            else:
                self.accept() if accepted else super(AddPcDialog, self).reject()
        self._exit_anim.finished.connect(_finish)
        self._exit_anim.start()

    def reject(self):
        self._dismiss(accepted=False)

    # ── Functionality (unchanged) ─────────────────────────────
    def _add(self):
        name = self.name_edit.text().strip()
        ip   = self.ip_edit.text().strip()
        if not name:
            from .glass_messagebox import show_glass_message
            show_glass_message(self, "Invalid Input", "Please enter a PC name.", icon=QMessageBox.Warning)
            return
        if not ip:
            from .glass_messagebox import show_glass_message
            show_glass_message(self, "Invalid Input", "Please enter an IP address.", icon=QMessageBox.Warning)
            return
        if not _IPV4_REGEX.match(ip):
            from .glass_messagebox import show_glass_message
            show_glass_message(self, "Invalid IP", "Please enter a valid IPv4 address.", icon=QMessageBox.Warning)
            return
        self._dismiss(accepted=True)

    def values(self):
        return self.name_edit.text().strip(), self.ip_edit.text().strip()