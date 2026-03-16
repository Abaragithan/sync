# views/software_widgets.py
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QSizePolicy, QTextEdit,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QTextCursor

from views.software_theme import _t, _STEPS, _STEP_INDEX


# =============================================================================
# StepProgressBar
# =============================================================================
class StepProgressBar(QWidget):
    def __init__(self, steps: list[tuple[str, str]], parent=None):
        super().__init__(parent)
        self._steps = steps
        self._active = 0
        self._failed = False
        self.setFixedHeight(64)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def set_step(self, key: str, failed: bool = False):
        self._active = _STEP_INDEX.get(key, 0)
        self._failed = failed
        self.update()

    def paintEvent(self, _event):
        from PySide6.QtGui import QPainter, QBrush
        from PySide6.QtCore import QRectF
        t = _t()
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W, H = self.width(), self.height()
        n = len(self._steps)
        pill_w, pill_h, line_h = 116, 30, 2
        spacing = (W - n * pill_w) / (n + 1)
        y_pill = (H - pill_h) / 2
        y_line = H / 2

        for i, (key, label) in enumerate(self._steps):
            x = spacing + i * (pill_w + spacing)
            if i > 0:
                prev_x = spacing + (i - 1) * (pill_w + spacing) + pill_w
                line_rect = QRectF(prev_x, y_line - line_h / 2, x - prev_x, line_h)
                line_col = t["line_done"] if i <= self._active else t["line_idle"]
                p.fillRect(line_rect, QColor(line_col))

            if i < self._active:
                col = t["pill_done"]
            elif i == self._active:
                col = t["pill_fail"] if self._failed else t["pill_active"]
            else:
                col = t["pill_idle"]

            rect = QRectF(x, y_pill, pill_w, pill_h)
            p.setBrush(QBrush(QColor(col)))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(rect, pill_h / 2, pill_h / 2)

            fnt = p.font()
            fnt.setPixelSize(12)
            fnt.setBold(i == self._active)
            p.setFont(fnt)
            p.setPen(QColor(t["pill_text"] if i <= self._active else t["pill_muted"]))
            p.drawText(rect, Qt.AlignCenter, label)
        p.end()


# =============================================================================
# LogPanel
# =============================================================================
class LogPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._build()

    def _build(self):
        t = _t()
        self.setStyleSheet(
            f"background: {t['log_bg']}; border-radius: 8px;"
            f" border: 1px solid {t['log_border']};"
        )
        self._header = QFrame()
        self._header.setFixedHeight(36)
        self._header.setStyleSheet(
            f"background: {t['log_header']}; border-radius: 8px 8px 0 0;"
            f" border-bottom: 1px solid {t['log_border']};"
        )
        hrow = QHBoxLayout(self._header)
        hrow.setContentsMargins(14, 0, 14, 0)
        self._title_lbl = QLabel("Execution Log")
        self._title_lbl.setStyleSheet(
            f"color: {t['lbl_muted']}; font-size: 12px; font-weight: 600;"
            " letter-spacing: 0.5px; background: transparent; border: none;"
        )
        hrow.addWidget(self._title_lbl)
        hrow.addStretch()
        self.status_badge = QLabel("")
        self.status_badge.setStyleSheet(
            "font-size: 11px; font-weight: 700; padding: 3px 10px;"
            " border-radius: 10px; background: transparent; border: none;"
        )
        self.status_badge.hide()
        hrow.addWidget(self.status_badge)
        self._layout.addWidget(self._header)

        self._log_view = QTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.setLineWrapMode(QTextEdit.WidgetWidth)
        self._log_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._log_view.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )
        self._log_view.setStyleSheet(
            f"QTextEdit {{"
            f" background: transparent;"
            f" color: {t['log_text']};"
            f" border: none;"
            f" padding: 10px 14px;"
            f" selection-background-color: #bfdbfe;"
            f"}}"
            f"QScrollBar:vertical {{ background: {t['scrollbar']}; width: 5px; border-radius: 2px; }}"
            f"QScrollBar::handle:vertical {{ background: {t['scroll_hdl']}; border-radius: 2px; }}"
            f"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}"
        )
        self._layout.addWidget(self._log_view)

        self._action_bar = QFrame()
        self._action_bar.setFixedHeight(50)
        self._action_bar.setStyleSheet(
            f"background: {t['abar_bg']}; border-radius: 0 0 8px 8px;"
            f" border-top: 1px solid {t['abar_bdr']};"
        )
        arow = QHBoxLayout(self._action_bar)
        arow.setContentsMargins(12, 0, 12, 0)
        arow.setSpacing(8)
        self.retry_btn = QPushButton("↺ Retry")
        self.new_task_btn = QPushButton("+ New Task")
        self.export_btn = QPushButton("↓ Export Log")
        btn_style = (
            f"background: {t['abar_btn_bg']}; border: 1px solid {t['abar_btn_bdr']};"
            f" color: {t['abar_btn_fg']}; border-radius: 6px; padding: 5px 12px; font-size: 12px;"
        )
        for btn in (self.retry_btn, self.new_task_btn, self.export_btn):
            btn.setStyleSheet(btn_style)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            arow.addWidget(btn)
        self._action_bar.hide()
        self._layout.addWidget(self._action_bar)

    def clear(self):
        self._log_view.clear()
        self.status_badge.hide()
        self._action_bar.hide()

    def append_line(self, text: str, style: str = "normal"):
        t = _t()
        is_error = style == "error"
        is_dim   = style == "dim"
        is_success = style == "success"
        colour = (
            t["log_error"] if is_error else
            t["log_dim"] if is_dim else
            t["log_success"] if is_success else
            t["log_text"]
        )
        cursor = self._log_view.textCursor()
        cursor.movePosition(QTextCursor.End)
        self._log_view.setTextCursor(cursor)
        self._log_view.setTextColor(QColor(colour))
        self._log_view.insertPlainText(text + "\n")
        self._log_view.moveCursor(QTextCursor.End)

    def get_plain_text(self) -> str:
        return self._log_view.toPlainText()

    def set_status(self, ok: bool):
        t = _t()
        if ok:
            self.status_badge.setText("✓ SUCCESS")
            self.status_badge.setStyleSheet(
                f"color: {t['badge_ok_fg']}; background: {t['badge_ok_bg']};"
                f" border: 1px solid {t['badge_ok_bdr']};"
                " font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 10px;"
            )
        else:
            self.status_badge.setText("✗ FAILED")
            self.status_badge.setStyleSheet(
                f"color: {t['badge_fail_fg']}; background: {t['badge_fail_bg']};"
                f" border: 1px solid {t['badge_fail_bdr']};"
                " font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 10px;"
            )
        self.status_badge.show()
        self._action_bar.show()
