"""
_dialog_base.py
Shared infrastructure for all SYNC Lab Manager dialogs.
Import from here so every dialog has an identical look.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QPoint, Property
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QEnterEvent, QMouseEvent
from PySide6.QtWidgets import (
    QDialog, QFrame, QWidget, QPushButton, QGraphicsDropShadowEffect
)


# ─────────────────────────────────────────────────────────────
#  Dim overlay  (identical to glass_messagebox)
# ─────────────────────────────────────────────────────────────
class DimOverlay(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self._alpha = 0
        self.setGeometry(parent.rect())
        self.raise_()
        self.show()

        self._anim = QPropertyAnimation(self, b"dim_alpha")
        self._anim.setDuration(180)
        self._anim.setStartValue(0)
        self._anim.setEndValue(160)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.start()

    def _get_alpha(self): return self._alpha
    def _set_alpha(self, v):
        self._alpha = v
        self.update()
    dim_alpha = Property(int, _get_alpha, _set_alpha)

    def fade_out(self, done_cb=None):
        self._anim2 = QPropertyAnimation(self, b"dim_alpha")
        self._anim2.setDuration(150)
        self._anim2.setStartValue(self._alpha)
        self._anim2.setEndValue(0)
        self._anim2.setEasingCurve(QEasingCurve.InCubic)
        if done_cb:
            self._anim2.finished.connect(done_cb)
        self._anim2.start()

    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(0, 0, 0, self._alpha))
        p.end()


# ─────────────────────────────────────────────────────────────
#  CloseButton  (shared across all dialogs)
# ─────────────────────────────────────────────────────────────
class CloseButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(32, 32)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self._hovered = False

    def enterEvent(self, event: QEnterEvent):
        self._hovered = True; self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False; self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(239, 68, 68, 28)) if self._hovered else Qt.transparent)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(4, 4, 24, 24)
        c = QColor(239, 68, 68) if self._hovered else QColor(156, 163, 175)
        painter.setPen(QPen(c, 2.5 if self._hovered else 2.0))
        m = 11
        painter.drawLine(m, m, 32 - m, 32 - m)
        painter.drawLine(32 - m, m, m, 32 - m)


# ─────────────────────────────────────────────────────────────
#  BaseDialog  — white card, rounded 12px, dim overlay, animate-in/out
# ─────────────────────────────────────────────────────────────
class BaseDialog(QDialog):
    """
    Base for all SYNC dialogs.
    Subclasses call super().__init__(parent) then build their own UI.
    Call self._finish_init() at the end of __init__ to start the overlay + animation.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setModal(True)
        self.setWindowOpacity(0.0)

        self._drag_pos: QPoint | None = None
        self._start_pos: QPoint | None = None
        self._overlay: DimOverlay | None = None

    def _finish_init(self):
        """Call after _build_ui() is complete."""
        # Drop shadow on the whole dialog window
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 55))
        self.setGraphicsEffect(shadow)

        # Dim overlay on parent
        if self.parent():
            self._overlay = DimOverlay(self.parent())

        QTimer.singleShot(0, self._animate_in)

    # ── Dragging ──────────────────────────────────────────────
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_pos is not None:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_pos = None

    # ── Paint: white card + thin border + 12px radius ─────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(252, 252, 252)))
        painter.drawRoundedRect(r, 12, 12)
        painter.setPen(QPen(QColor(0, 0, 0, 22), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(r.adjusted(1, 1, -1, -1), 11, 11)
        painter.end()
        super().paintEvent(event)

    # ── Positioning ───────────────────────────────────────────
    def _center_on_parent(self):
        if not self.parent():
            return
        pg = self.parent().geometry()
        self.move(
            pg.x() + pg.width()  // 2 - self.width()  // 2,
            pg.y() + pg.height() // 2 - self.height() // 2,
        )

    def showEvent(self, event):
        super().showEvent(event)
        self._center_on_parent()
        if self._overlay and self.parent():
            self._overlay.setGeometry(self.parent().rect())
            self._overlay.raise_()
            self.raise_()

    # ── Animate in ────────────────────────────────────────────
    def _animate_in(self):
        self._center_on_parent()
        self._start_pos = self.pos()

        start = QPoint(self._start_pos.x(), self._start_pos.y() - 12)
        self.move(start)
        self.setWindowOpacity(0.0)

        self._op_in = QPropertyAnimation(self, b"windowOpacity")
        self._op_in.setDuration(200)
        self._op_in.setStartValue(0.0)
        self._op_in.setEndValue(1.0)
        self._op_in.setEasingCurve(QEasingCurve.OutCubic)

        self._pos_in = QPropertyAnimation(self, b"pos")
        self._pos_in.setDuration(220)
        self._pos_in.setStartValue(start)
        self._pos_in.setEndValue(self._start_pos)
        self._pos_in.setEasingCurve(QEasingCurve.OutCubic)

        self._op_in.start()
        self._pos_in.start()

    # ── Dismiss with fade-out ─────────────────────────────────
    def _dismiss(self, accepted: bool):
        for attr in ("_op_in", "_pos_in"):
            obj = getattr(self, attr, None)
            if obj:
                try: obj.stop()
                except Exception: pass

        self._op_out = QPropertyAnimation(self, b"windowOpacity")
        self._op_out.setDuration(140)
        self._op_out.setStartValue(self.windowOpacity())
        self._op_out.setEndValue(0.0)
        self._op_out.setEasingCurve(QEasingCurve.InCubic)

        def _done():
            if self._overlay:
                self._overlay.fade_out(done_cb=lambda: (
                    self._overlay.deleteLater(),
                    self.accept() if accepted else super(BaseDialog, self).reject()
                ))
            else:
                self.accept() if accepted else super(BaseDialog, self).reject()

        self._op_out.finished.connect(_done)
        self._op_out.start()

    def reject(self):
        self._dismiss(accepted=False)

    # ── Shared stylesheet ─────────────────────────────────────
    BLUE   = "#2563eb"
    BLUE_H = "#1d4ed8"
    BLUE_P = "#1e40af"
    RED    = "#dc2626"
    RED_H  = "#b91c1c"
    RED_P  = "#991b1b"

    BASE_QSS = f"""
        QLabel {{
            background: transparent;
            color: #0f172a;
        }}
        QLabel#DialogTitle {{
            font-size: 15px;
            font-weight: 700;
            color: #0f172a;
        }}
        QLabel#DialogSubtitle {{
            font-size: 12px;
            color: #64748b;
        }}
        QLabel#FieldLabel {{
            font-size: 11px;
            font-weight: 600;
            color: #64748b;
            letter-spacing: 0.4px;
        }}
        QLabel#FieldValueGray {{
            background: #f4f6f9;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            color: #1e293b;
            font-size: 13px;
            font-weight: 600;
            padding: 0px 10px;
        }}
        QLabel#FieldValueBlue {{
            background: #eff6ff;
            border: 1px solid #dbeafe;
            border-radius: 8px;
            color: {BLUE};
            font-size: 13px;
            font-weight: 600;
            font-family: 'Consolas', monospace;
            padding: 0px 10px;
        }}
        QFrame#Divider {{
            background: #edf0f5;
            border: none;
            min-height: 1px;
            max-height: 1px;
        }}
        QLineEdit {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 0px 12px;
            color: #0f172a;
            font-size: 13px;
            font-family: 'Consolas', monospace;
            min-height: 38px;
        }}
        QLineEdit:focus {{
            border: 1px solid {BLUE};
            background: #ffffff;
        }}
        QLineEdit:hover {{
            border: 1px solid #94a3b8;
        }}
        QPushButton#CancelBtn {{
            background: #f4f6f9;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            color: #475569;
            font-size: 13px;
            font-weight: 600;
        }}
        QPushButton#CancelBtn:hover {{
            background: #eaecf2;
            border-color: #c8ccd6;
            color: #1e293b;
        }}
        QPushButton#CancelBtn:pressed {{
            background: #dde0e8;
        }}
        QPushButton#PrimaryBtn {{
            background: {BLUE};
            border: none;
            border-radius: 8px;
            color: white;
            font-size: 13px;
            font-weight: 700;
        }}
        QPushButton#PrimaryBtn:hover {{
            background: {BLUE_H};
        }}
        QPushButton#PrimaryBtn:pressed {{
            background: {BLUE_P};
        }}
        QPushButton#PrimaryBtn:disabled {{
            background: #93c5fd;
        }}
        QPushButton#DeleteBtn {{
            background: {RED};
            border: none;
            border-radius: 8px;
            color: white;
            font-size: 13px;
            font-weight: 700;
        }}
        QPushButton#DeleteBtn:hover {{
            background: {RED_H};
        }}
        QPushButton#DeleteBtn:pressed {{
            background: {RED_P};
        }}
        QPushButton#CloseBtn {{
            background: transparent;
            border: none;
        }}
    """

    def _divider(self) -> QFrame:
        d = QFrame()
        d.setObjectName("Divider")
        return d
    