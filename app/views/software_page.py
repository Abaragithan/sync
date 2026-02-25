from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QStackedWidget, QSizePolicy, QScrollArea, QRadioButton, QButtonGroup,
    QApplication, QFileDialog,
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor, QPalette

from views.action_forms import get_form
from core.ansible_worker import AnsibleWorker

import os

# ── progress step registry ──────────────────────────────────────────────────
_STEPS = [
    ("select_pcs", "Select PCs"),
    ("configure",  "Configure"),
    ("executing",  "Executing"),
    ("done",       "Done"),
]
_STEP_INDEX = {key: i for i, (key, _) in enumerate(_STEPS)}

_ACTIONS = [("install", "Install"), ("remove", "Remove"), ("update", "Update")]

# ── per-theme colour tokens ──────────────────────────────────────────────────
DARK = {
    "chrome_bg": "#1a1d27", "chrome_bdr": "#252836",
    "pill_done": "#1d4ed8", "pill_active": "#3d7aed",
    "pill_fail": "#dc2626", "pill_idle": "#2a2d3a",
    "pill_text": "#ffffff", "pill_muted": "#64748b",
    "line_done": "#3d7aed", "line_idle": "#2a2d3a",
    "log_bg": "#111318", "log_header": "#141720", "log_border": "#2d3148",
    "log_text": "#dde3ed", "log_error": "#fca5a5", "log_dim": "#8896a8",
    "scrollbar": "#2a2d3a", "scroll_hdl": "#3d4460",
    "btn_idle_bg": "#1a1d27", "btn_idle_bdr": "#252836", "btn_idle_fg": "#94a3b8",
    "radio_bg": "#1a1d27", "radio_bdr": "#252836", "radio_fg": "#64748b",
    "radio_chk_bg": "#3d7aed", "radio_chk_fg": "#ffffff",
    "radio_hov_bdr": "#3d7aed", "radio_hov_fg": "#e2e8f0",
    "act_idle_bg": "#1a1d27", "act_idle_bdr": "#252836", "act_idle_fg": "#64748b",
    "act_active_bg": "#3d7aed", "act_active_bdr": "#5aaaff", "act_active_fg": "#ffffff",
    "div_color": "#252836",
    "badge_ok_fg": "#86efac", "badge_ok_bg": "#14532d", "badge_ok_bdr": "#166534",
    "badge_fail_fg": "#fca5a5", "badge_fail_bg": "#7f1d1d", "badge_fail_bdr": "#991b1b",
    "abar_bg": "#141720", "abar_bdr": "#1e2130",
    "abar_btn_bg": "#2a2d3a", "abar_btn_bdr": "#252836", "abar_btn_fg": "#e2e8f0",
    "back_bg": "transparent", "back_bdr": "#252836", "back_fg": "#64748b",
    "lbl_muted": "#64748b", "lbl_title": "#e2e8f0", "lbl_sub": "#64748b",
    "vline": "#252836",
}
LIGHT = {
    "chrome_bg": "#ffffff", "chrome_bdr": "#e2e8f0",
    "pill_done": "#1d4ed8", "pill_active": "#2563eb",
    "pill_fail": "#dc2626", "pill_idle": "#cbd5e1",
    "pill_text": "#ffffff", "pill_muted": "#94a3b8",
    "line_done": "#2563eb", "line_idle": "#e2e8f0",
    "log_bg": "#f8fafc", "log_header": "#f1f5f9", "log_border": "#e2e8f0",
    "log_text": "#1e293b", "log_error": "#b91c1c", "log_dim": "#94a3b8",
    "scrollbar": "#e2e8f0", "scroll_hdl": "#94a3b8",
    "btn_idle_bg": "#ffffff", "btn_idle_bdr": "#e2e8f0", "btn_idle_fg": "#64748b",
    "radio_bg": "#ffffff", "radio_bdr": "#cbd5e1", "radio_fg": "#64748b",
    "radio_chk_bg": "#2563eb", "radio_chk_fg": "#ffffff",
    "radio_hov_bdr": "#2563eb", "radio_hov_fg": "#0f172a",
    "act_idle_bg": "#ffffff", "act_idle_bdr": "#cbd5e1", "act_idle_fg": "#64748b",
    "act_active_bg": "#2563eb", "act_active_bdr": "#1d4ed8", "act_active_fg": "#ffffff",
    "div_color": "#e2e8f0",
    "badge_ok_fg": "#14532d", "badge_ok_bg": "#dcfce7", "badge_ok_bdr": "#15803d",
    "badge_fail_fg": "#991b1b", "badge_fail_bg": "#fee2e2", "badge_fail_bdr": "#dc2626",
    "abar_bg": "#f1f5f9", "abar_bdr": "#e2e8f0",
    "abar_btn_bg": "#ffffff", "abar_btn_bdr": "#e2e8f0", "abar_btn_fg": "#334155",
    "back_bg": "transparent", "back_bdr": "#e2e8f0", "back_fg": "#94a3b8",
    "lbl_muted": "#64748b", "lbl_title": "#0f172a", "lbl_sub": "#64748b",
    "vline": "#e2e8f0",
}


def _is_dark() -> bool:
    app = QApplication.instance()
    if app is None:
        return True
    return app.palette().color(QPalette.Window).lightness() < 128


def _t() -> dict:
    return DARK if _is_dark() else LIGHT


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

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background: transparent; }}"
            f"QScrollBar:vertical {{ background: {t['scrollbar']}; width: 5px; border-radius: 2px; }}"
            f"QScrollBar::handle:vertical {{ background: {t['scroll_hdl']}; border-radius: 2px; }}"
            f"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}"
        )
        self._inner = QWidget()
        self._inner.setStyleSheet("background: transparent;")
        self._inner_layout = QVBoxLayout(self._inner)
        self._inner_layout.setContentsMargins(14, 10, 14, 10)
        self._inner_layout.setSpacing(1)
        self._inner_layout.addStretch()
        self._scroll.setWidget(self._inner)
        self._layout.addWidget(self._scroll)

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

    def apply_theme(self):
        t = _t()
        self.setStyleSheet(
            f"background: {t['log_bg']}; border-radius: 8px;"
            f" border: 1px solid {t['log_border']};"
        )
        self._header.setStyleSheet(
            f"background: {t['log_header']}; border-radius: 8px 8px 0 0;"
            f" border-bottom: 1px solid {t['log_border']};"
        )
        self._title_lbl.setStyleSheet(
            f"color: {t['lbl_muted']}; font-size: 12px; font-weight: 600;"
            " letter-spacing: 0.5px; background: transparent; border: none;"
        )
        self._scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background: transparent; }}"
            f"QScrollBar:vertical {{ background: {t['scrollbar']}; width: 5px; border-radius: 2px; }}"
            f"QScrollBar::handle:vertical {{ background: {t['scroll_hdl']}; border-radius: 2px; }}"
            f"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}"
        )
        self._action_bar.setStyleSheet(
            f"background: {t['abar_bg']}; border-radius: 0 0 8px 8px;"
            f" border-top: 1px solid {t['abar_bdr']};"
        )
        btn_style = (
            f"background: {t['abar_btn_bg']}; border: 1px solid {t['abar_btn_bdr']};"
            f" color: {t['abar_btn_fg']}; border-radius: 6px; padding: 5px 12px; font-size: 12px;"
        )
        for btn in (self.retry_btn, self.new_task_btn, self.export_btn):
            btn.setStyleSheet(btn_style)
        for i in range(self._inner_layout.count()):
            item = self._inner_layout.itemAt(i)
            if item and item.widget():
                w = item.widget()
                is_error = w.property("log_error")
                colour = t["log_error"] if is_error else (
                    t["log_dim"] if w.property("log_dim") else t["log_text"]
                )
                w.setStyleSheet(
                    f"color: {colour}; font-family: 'Consolas', 'Courier New', monospace;"
                    " font-size: 12px; background: transparent; border: none;"
                )

    def clear(self):
        while self._inner_layout.count() > 1:
            item = self._inner_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.status_badge.hide()
        self._action_bar.hide()

    def append_line(self, text: str, style: str = "normal"):
        t = _t()
        is_error = style == "error"
        is_dim   = style == "dim"
        colour   = t["log_error"] if is_error else (t["log_dim"] if is_dim else t["log_text"])
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lbl.setProperty("log_error", is_error)
        lbl.setProperty("log_dim",   is_dim)
        lbl.setStyleSheet(
            f"color: {colour}; font-family: 'Consolas', 'Courier New', monospace;"
            " font-size: 12px; background: transparent; border: none;"
        )
        self._inner_layout.insertWidget(self._inner_layout.count() - 1, lbl)
        QTimer.singleShot(30, lambda: self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        ))

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


# =============================================================================
# SoftwarePage
# =============================================================================
class SoftwarePage(QWidget):
    view_status_requested = Signal()
    back_to_lab = Signal()

    def __init__(self, inventory_manager, state):
        super().__init__()
        self.inventory_manager = inventory_manager
        self.state = state
        self._form_cache: dict[tuple[str, str], QWidget] = {}
        self._worker: AnsibleWorker | None = None   # ← real worker, replaces sim timer
        self._last_payload: dict | None = None       # ← stored for Retry
        self._build_ui()

    # =========================================================================
    # UI construction
    # =========================================================================
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # chrome
        self._chrome = QFrame()
        self._chrome.setFixedHeight(112)
        chrome_layout = QVBoxLayout(self._chrome)
        chrome_layout.setContentsMargins(24, 10, 24, 10)
        chrome_layout.setSpacing(6)
        btn_row = QHBoxLayout()
        self.back_btn = QPushButton("← Back")
        self.back_btn.setFixedWidth(80)
        self.back_btn.setObjectName("BackBtn")
        self.back_btn.clicked.connect(self.back_to_lab.emit)
        btn_row.addWidget(self.back_btn)
        btn_row.addStretch()
        chrome_layout.addLayout(btn_row)
        self.progress_bar = StepProgressBar(_STEPS)
        chrome_layout.addWidget(self.progress_bar)
        root.addWidget(self._chrome)

        # two-panel content
        content_area = QWidget()
        content_layout = QHBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # LEFT scroll
        left_scroll = QScrollArea()
        left_scroll.setObjectName("SWFormScroll")
        self._left_scroll = left_scroll
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_panel = QWidget()
        left_panel.setObjectName("SWFormPanel")
        self._left_panel = left_panel
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(36, 28, 36, 28)
        left_layout.setSpacing(20)

        self._title_lbl = QLabel("Software Manager")
        self._title_lbl.setStyleSheet("font-size: 20px; font-weight: 800;")
        left_layout.addWidget(self._title_lbl)

        self._sub_lbl = QLabel("Configure the action to deploy to selected PCs")
        self._sub_lbl.setObjectName("SubText")
        left_layout.addWidget(self._sub_lbl)

        self._divider = QFrame()
        self._divider.setFrameShape(QFrame.HLine)
        left_layout.addWidget(self._divider)

        os_lbl = QLabel("OPERATING SYSTEM")
        os_lbl.setObjectName("SubText")
        os_lbl.setStyleSheet("font-size: 10px; font-weight: 700; letter-spacing: 1.2px;")
        left_layout.addWidget(os_lbl)

        os_row = QHBoxLayout()
        os_row.setSpacing(8)
        self._os_group = QButtonGroup(self)
        self._win_radio = self._make_radio("🪟 Windows")
        self._lin_radio = self._make_radio("🐧 Linux")
        self._os_group.addButton(self._win_radio, 0)
        self._os_group.addButton(self._lin_radio, 1)
        os_row.addWidget(self._win_radio)
        os_row.addWidget(self._lin_radio)
        os_row.addStretch()
        left_layout.addLayout(os_row)
        self._win_radio.setChecked(self.state.target_os == "windows")
        self._lin_radio.setChecked(self.state.target_os == "linux")
        self._os_group.buttonClicked.connect(self._on_os_radio_clicked)

        action_lbl = QLabel("ACTION")
        action_lbl.setObjectName("SubText")
        action_lbl.setStyleSheet("font-size: 10px; font-weight: 700; letter-spacing: 1.2px;")
        left_layout.addWidget(action_lbl)

        action_row = QHBoxLayout()
        action_row.setSpacing(8)
        self._action_buttons: dict[str, QPushButton] = {}
        for key, label in _ACTIONS:
            btn = QPushButton(label)
            btn.clicked.connect(lambda _=False, k=key: self._on_action_changed(k))
            action_row.addWidget(btn)
            self._action_buttons[key] = btn
        action_row.addStretch()
        left_layout.addLayout(action_row)

        self.form_stack = QStackedWidget()
        left_layout.addWidget(self.form_stack)

        self.execute_btn = QPushButton("Execute →")
        self.execute_btn.setObjectName("PrimaryBtn")
        self.execute_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.execute_btn.clicked.connect(self._on_execute_clicked)
        left_layout.addWidget(self.execute_btn)
        left_layout.addStretch()

        left_scroll.setWidget(left_panel)

        self._vline = QFrame()
        self._vline.setFrameShape(QFrame.VLine)
        self._vline.setFixedWidth(1)

        right_wrapper = QWidget()
        rw_layout = QVBoxLayout(right_wrapper)
        rw_layout.setContentsMargins(0, 20, 20, 20)
        self.log_panel = LogPanel()
        rw_layout.addWidget(self.log_panel)
        self.log_panel.retry_btn.clicked.connect(self._on_retry)
        self.log_panel.new_task_btn.clicked.connect(self._on_new_task)
        self.log_panel.export_btn.clicked.connect(self._on_export_log)

        content_layout.addWidget(left_scroll, 2)
        content_layout.addWidget(self._vline)
        content_layout.addWidget(right_wrapper, 3)
        root.addWidget(content_area, 1)

        self.apply_theme()

    # =========================================================================
    # Theme
    # =========================================================================
    def apply_theme(self):
        t = _t()
        self._chrome.setStyleSheet(
            f"QFrame {{ background-color: {t['chrome_bg']};"
            f" border-bottom: 1px solid {t['chrome_bdr']}; }}"
        )
        self._left_scroll.setStyleSheet(
            f"QScrollBar:vertical {{ background: {t['scrollbar']}; width: 6px; border-radius: 3px; }}"
            f"QScrollBar::handle:vertical {{ background: {t['scroll_hdl']}; border-radius: 3px; }}"
            f"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}"
        )
        self._divider.setStyleSheet(
            f"color: {t['div_color']}; background: {t['div_color']};"
        )
        self._vline.setStyleSheet(
            f"color: {t['vline']}; background: {t['vline']};"
        )
        self._apply_radio_style(self._win_radio)
        self._apply_radio_style(self._lin_radio)
        self._refresh_action_btns()
        self.log_panel.apply_theme()
        self.progress_bar.update()

    def _apply_radio_style(self, rb: QRadioButton):
        t = _t()
        rb.setStyleSheet(f"""
            QRadioButton {{
                background: {t['radio_bg']}; border: 1px solid {t['radio_bdr']};
                border-radius: 18px; color: {t['radio_fg']};
                padding: 7px 20px; font-size: 13px; font-weight: 600; spacing: 0px;
            }}
            QRadioButton::indicator {{ width: 0; height: 0; }}
            QRadioButton:checked {{
                background: {t['radio_chk_bg']}; border-color: {t['radio_chk_bg']};
                color: {t['radio_chk_fg']};
            }}
            QRadioButton:hover:!checked {{
                border-color: {t['radio_hov_bdr']}; color: {t['radio_hov_fg']};
            }}
        """)

    def _make_radio(self, label: str) -> QRadioButton:
        rb = QRadioButton(label)
        self._apply_radio_style(rb)
        return rb

    def _action_btn_style(self, active: bool) -> str:
        t = _t()
        if active:
            return (
                f"background: {t['act_active_bg']}; color: {t['act_active_fg']};"
                f" font-weight: 700; border: 2px solid {t['act_active_bdr']};"
                " border-radius: 6px; padding: 8px 20px; font-size: 13px;"
            )
        return (
            f"background: {t['act_idle_bg']}; color: {t['act_idle_fg']};"
            f" font-weight: 500; border: 1px solid {t['act_idle_bdr']};"
            " border-radius: 6px; padding: 8px 20px; font-size: 13px;"
        )

    def _refresh_action_btns(self):
        for key, btn in self._action_buttons.items():
            btn.setStyleSheet(self._action_btn_style(key == self.state.action))

    # =========================================================================
    # Form management
    # =========================================================================
    def _current_key(self) -> tuple[str, str]:
        return (self.state.target_os, self.state.action)

    def _swap_form(self):
        self._refresh_action_btns()
        key = self._current_key()
        if key not in self._form_cache:
            form = get_form(*key)
            if form is None:
                form = _NoForm(*key)
            form.payload_ready.connect(self._on_payload_ready)
            form.validation_error.connect(self._on_validation_error)
            self.form_stack.addWidget(form)
            self._form_cache[key] = form
        self.form_stack.setCurrentWidget(self._form_cache[key])

    # =========================================================================
    # Event handlers
    # =========================================================================
    def _on_os_radio_clicked(self, btn: QRadioButton):
        self.state.target_os = "windows" if btn is self._win_radio else "linux"
        self._swap_form()

    def _on_action_changed(self, action: str):
        self.state.action = action
        self._swap_form()

    def _on_execute_clicked(self):
        if not self.state.selected_targets:
            self.log_panel.append_line(
                "⚠ No PCs selected – go back and choose targets.", "error"
            )
            return
        self.progress_bar.set_step("executing")
        self.execute_btn.setEnabled(False)
        self.execute_btn.setText("Executing...")
        form = self._form_cache.get(self._current_key())
        if form:
            form.submit()

    def _on_payload_ready(self, form_payload: dict):
        payload = {
            "lab":     self.state.current_lab,
            "targets": self.state.selected_targets,
            **form_payload,
        }
        self._last_payload = payload          # save for Retry
        self.log_panel.clear()
        self._run_ansible(payload)

    def _on_validation_error(self, msg: str):
        self.progress_bar.set_step("configure")
        self.execute_btn.setEnabled(True)
        self.execute_btn.setText("Execute →")
        self.log_panel.append_line(f"✗ {msg}", "error")

    # =========================================================================
    # Real Ansible execution
    # =========================================================================
    def _run_ansible(self, payload: dict):
        """
        Builds the exact Docker command your README documents, using sync-ansible:latest.

        Windows install:
          docker run --rm
            -v $PWD:/app  -v ~/.ssh:/root/.ssh:ro
            -w /app/ansible  sync-ansible:latest
            ansible-playbook -i inventory/hosts.ini playbooks/master_deploy_v2.yml
            -e "target_host=windows_clients file_name=X app_state=present"

        Linux install/remove/update: same but adds --vault-password-file=/vault_pass
        and mounts ~/.ansible_vault_pass.

        The playbook var  target_host  tells Ansible which group to run against.
        For targeted IPs we write a temporary inventory file so the user's
        selection (not the whole group) is used.
        """
        os_name = payload.get("os", self.state.target_os)   # "windows" | "linux"
        action  = payload.get("action", self.state.action)  # "install" | "remove" | "update"
        targets = payload.get("targets", self.state.selected_targets)

        # ── locate project root  (app/views/ → ../../) ──────────────────────
        here         = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(here, "..", ".."))
        ssh_dir      = os.path.expanduser("~/.ssh")
        vault_pass   = os.path.expanduser("~/.ansible_vault_pass")
        sw_repo      = os.path.join(project_root, "software_repo")

        # ── map action → Ansible app_state ──────────────────────────────────
        app_state_map = {"install": "present", "remove": "absent", "update": "latest"}
        app_state = app_state_map.get(action, "present")

        # ── build extra-vars ─────────────────────────────────────────────────
        # target_host is the Ansible group; we ALSO pass a per-run temp inventory
        # so only the user-selected IPs are targeted.
        target_host = "windows_clients" if os_name == "windows" else "linux_clients"
        extra: dict[str, str] = {
            "app_state":   app_state,
            "target_host": target_host,
        }

        if action == "install" and os_name == "windows":
            file_path = payload.get("file", "").strip()
            if not file_path:
                self.log_panel.append_line("✗ No installer file specified.", "error")
                self._on_execution_finished(ok=False)
                return
            file_name = os.path.basename(file_path)
            extra["file_name"] = file_name
            # Copy installer into software_repo so Docker can reach it
            self._ensure_in_repo(file_path, sw_repo)
            if payload.get("args", "").strip():
                extra["custom_install_args"] = payload["args"].strip()

        elif action == "install" and os_name == "linux":
            pkgs = payload.get("packages", "").strip()
            if not pkgs:
                self.log_panel.append_line("✗ No packages specified.", "error")
                self._on_execution_finished(ok=False)
                return
            extra["package_name"] = pkgs

        elif action == "remove" and os_name == "windows":
            app_name = payload.get("app_name", "").strip()
            if not app_name:
                self.log_panel.append_line("✗ No application name specified.", "error")
                self._on_execution_finished(ok=False)
                return
            extra["app_name"] = app_name

        elif action == "remove" and os_name == "linux":
            pkgs = payload.get("packages", "").strip()
            if not pkgs:
                self.log_panel.append_line("✗ No packages specified.", "error")
                self._on_execution_finished(ok=False)
                return
            extra["package_name"] = pkgs

        # update needs no extra vars beyond app_state / target_host

        # ── write a temporary inventory for the selected IPs only ────────────
        # This lives inside the project's ansible/inventory/ folder so Docker
        # can see it via the -v $PWD:/app mount.
        tmp_inv = self._write_temp_inventory(
            project_root, targets, os_name, target_host
        )
        if tmp_inv is None:
            self.log_panel.append_line("✗ Could not write temporary inventory.", "error")
            self._on_execution_finished(ok=False)
            return

        # Inventory path relative to /app/ansible (the Docker workdir)
        inv_rel = os.path.relpath(
            tmp_inv,
            os.path.join(project_root, "ansible")
        )

        # ── serialise extra-vars string ──────────────────────────────────────
        ev_str = " ".join(f"{k}={v}" for k, v in extra.items())

        # ── log header ───────────────────────────────────────────────────────
        self.log_panel.append_line(
            f"▶ ansible-playbook  [{action.upper()} / {os_name.upper()}]"
            f"  →  {len(targets)} host(s)", "dim"
        )
        self.log_panel.append_line(f"  Hosts : {', '.join(targets)}", "dim")
        self.log_panel.append_line(f"  Vars  : {ev_str}", "dim")
        self.log_panel.append_line("", "dim")

        # ── build Docker command (mirrors README exactly) ────────────────────
        #
        # docker run --rm
        #   -v "$PWD:/app"
        #   -v "$HOME/.ssh:/root/.ssh:ro"
        #   [-v "$HOME/.ansible_vault_pass:/vault_pass:ro"]   # linux only
        #   -v "software_repo:/app/software_repo"             # windows install only
        #   -w /app/ansible
        #   sync-ansible:latest
        #   ansible-playbook
        #     -i <inv_rel>
        #     playbooks/master_deploy.yml
        #     -e "<ev_str>"
        #     [--vault-password-file=/vault_pass]             # linux only
        #
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{project_root}:/app",
            "-v", f"{ssh_dir}:/root/.ssh:ro",
        ]

        # Mount software_repo for Windows installs so the playbook can copy the file
        if action == "install" and os_name == "windows":
            cmd += ["-v", f"{sw_repo}:/app/software_repo"]

        # Mount vault password for Linux targets
        if os_name == "linux" and os.path.exists(vault_pass):
            cmd += ["-v", f"{vault_pass}:/vault_pass:ro"]

        cmd += [
            "-w", "/app/ansible",
            "sync-ansible:latest",
            "ansible-playbook",
            "-i", inv_rel,
            "playbooks/master_deploy_v2.yml",
            "-e", ev_str,
        ]

        if os_name == "linux" and os.path.exists(vault_pass):
            cmd += ["--vault-password-file=/vault_pass"]

        # ── launch worker ────────────────────────────────────────────────────
        if self._worker and self._worker.isRunning():
            self.log_panel.append_line(
                "⚠ A task is already running. Wait for it to finish.", "error"
            )
            return

        self._worker = AnsibleWorker(cmd)
        self._worker.output_received.connect(self._on_ansible_line)
        self._worker.finished.connect(
            lambda ok: self._on_execution_finished(ok, tmp_inv)
        )
        self._worker.start()

    # ── helpers ──────────────────────────────────────────────────────────────
    @staticmethod
    def _write_temp_inventory(
        project_root: str,
        targets: list[str],
        os_name: str,
        group: str,
    ) -> str | None:
        """
        Write a minimal INI inventory containing only the selected IPs.
        Copies connection vars from the real hosts.ini so SSH / vault settings
        are preserved, then adds the selected IPs under the right group.

        Returns the absolute path to the temp file, or None on error.
        """
        import shutil, tempfile, configparser

        ansible_dir  = os.path.join(project_root, "ansible")
        real_inv     = os.path.join(ansible_dir, "inventory", "hosts.ini")
        tmp_dir      = os.path.join(ansible_dir, "inventory")
        tmp_path     = os.path.join(tmp_dir, "_sync_tmp_inventory.ini")

        # Read the real inventory for [group:vars] section
        group_vars_lines: list[str] = []
        if os.path.exists(real_inv):
            with open(real_inv, "r") as f:
                in_vars = False
                for line in f:
                    stripped = line.strip()
                    if stripped == f"[{group}:vars]":
                        in_vars = True
                        group_vars_lines.append(line)
                        continue
                    if in_vars:
                        if stripped.startswith("[") and not stripped.startswith(f"[{group}"):
                            in_vars = False
                        else:
                            group_vars_lines.append(line)

        try:
            with open(tmp_path, "w") as f:
                f.write(f"[{group}]\n")
                for ip in targets:
                    f.write(f"{ip}\n")
                f.write("\n")
                for line in group_vars_lines:
                    f.write(line)
            return tmp_path
        except OSError as e:
            print(f"[SoftwarePage] Failed to write temp inventory: {e}")
            return None

    @staticmethod
    def _ensure_in_repo(src_path: str, repo_dir: str):
        """Copy installer into software_repo if it isn't already there."""
        import shutil
        os.makedirs(repo_dir, exist_ok=True)
        dst = os.path.join(repo_dir, os.path.basename(src_path))
        if not os.path.exists(dst):
            try:
                shutil.copy2(src_path, dst)
            except OSError as e:
                print(f"[SoftwarePage] Could not copy installer to repo: {e}")

    def _on_ansible_line(self, line: str):
        """Classify each output line and forward to log panel."""
        low = line.lower()
        # Ansible fatal / error → red
        if any(kw in low for kw in ("fatal:", "error", "failed!", "unreachable")):
            self.log_panel.append_line(line, "error")
        # Blank / separator → dim
        elif line.strip() == "" or line.strip().startswith("*"):
            self.log_panel.append_line(line, "dim")
        else:
            self.log_panel.append_line(line, "normal")

    def _on_execution_finished(self, ok: bool, tmp_inv: str | None = None):
        """Called by AnsibleWorker.finished signal."""
        # Clean up temporary inventory file
        if tmp_inv and os.path.exists(tmp_inv):
            try:
                os.remove(tmp_inv)
            except OSError:
                pass
        self.progress_bar.set_step("done", failed=not ok)
        self.log_panel.set_status(ok)
        self.execute_btn.setEnabled(True)
        self.execute_btn.setText("Execute →")
        self._worker = None

    # =========================================================================
    # Log action bar
    # =========================================================================
    def _on_retry(self):
        if self._last_payload is None:
            return
        self.progress_bar.set_step("executing")
        self.execute_btn.setEnabled(False)
        self.execute_btn.setText("Executing...")
        self.log_panel.clear()
        self._run_ansible(self._last_payload)

    def _on_new_task(self):
        key = self._current_key()
        if key in self._form_cache:
            self._form_cache[key].reset()
        self.log_panel.clear()
        self._last_payload = None
        self.progress_bar.set_step("configure")
        self.execute_btn.setEnabled(True)
        self.execute_btn.setText("Execute →")

    def _on_export_log(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Log", "ansible_log.txt", "Text Files (*.txt)"
        )
        if not path:
            return
        lines = []
        layout = self.log_panel._inner_layout
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item and item.widget():
                lines.append(item.widget().text())
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
        except OSError as e:
            self.log_panel.append_line(f"Export failed: {e}", "error")

    # =========================================================================
    # Lifecycle
    # =========================================================================
    def on_page_show(self):
        key = self._current_key()
        if key in self._form_cache:
            self._form_cache[key].reset()
        self._win_radio.blockSignals(True)
        self._lin_radio.blockSignals(True)
        self._win_radio.setChecked(self.state.target_os == "windows")
        self._lin_radio.setChecked(self.state.target_os == "linux")
        self._win_radio.blockSignals(False)
        self._lin_radio.blockSignals(False)
        self.apply_theme()
        self.log_panel.clear()
        n = len(self.state.selected_targets)
        target_str = f"{n} PC{'s' if n != 1 else ''} selected" if n else "No PCs selected"
        self.log_panel.append_line(
            f"Lab: {self.state.current_lab or '?'} · {target_str}", "dim"
        )
        self.log_panel.append_line("Waiting for execution...", "dim")
        self.progress_bar.set_step("configure")
        self.execute_btn.setEnabled(True)
        self.execute_btn.setText("Execute →")
        self._swap_form()
        print("[SoftwarePage] Opened for targets:", self.state.selected_targets)


# ── fallback form ──────────────────────────────────────────────────────────
class _NoForm(QWidget):
    payload_ready    = Signal(dict)
    validation_error = Signal(str)

    def __init__(self, os_name, action):
        super().__init__()
        lbl = QLabel(f'No form defined for "{os_name} / {action}".')
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setObjectName("SubText")
        QVBoxLayout(self).addWidget(lbl)

    def submit(self):
        self.validation_error.emit("No form available for this combination.")

    def reset(self):
        pass