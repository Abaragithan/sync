# views/software_page.py
"""
Software Manager – two-panel layout with step progress bar.

Theme integration
-----------------
This page sets NO background/color on its root QWidget so the global
QSS (DARK_QSS / LIGHT_QSS) flows through naturally.  Only elements
that need explicit scoped styling (the custom-painted progress bar,
the log panel terminal area) carry their own colours, and those read
from the two helper dicts DARK and LIGHT so swapping themes is one
call to apply_theme().

Progress steps
--------------
  1  Select PCs  – pre-completed on page open
  2  Configure   – active while user fills form
  3  Executing   – active while ansible runs
  4  Done        – blue on success, red on failure (no yellow anywhere)

Log colours
-----------
Dark  : all text is #e2e8f0 (near-white). Only errors use a soft red.
Light : all text is #1e293b (near-black). Only errors use a dark red.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QStackedWidget,
    QSizePolicy, QScrollArea, QRadioButton,
    QButtonGroup, QApplication,
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor, QPalette

from views.action_forms import get_form

# ── progress step registry ────────────────────────────────────────────────────
_STEPS = [
    ("select_pcs", "Select PCs"),
    ("configure",  "Configure"),
    ("executing",  "Executing"),
    ("done",       "Done"),
]
_STEP_INDEX = {key: i for i, (_, _l) in enumerate(_STEPS) for key, _l in [(_STEPS[i][0], _STEPS[i][1])]}
# rebuild cleanly
_STEP_INDEX = {key: i for i, (key, _) in enumerate(_STEPS)}

_ACTIONS = [("install", "Install"), ("remove", "Remove"), ("update", "Update")]

# ── per-theme colour tokens used ONLY in custom-painted / terminal widgets ────
# Everything else inherits from the global QSS.
DARK = {
    "chrome_bg":    "#1a1d27",
    "chrome_bdr":   "#252836",
    "pill_done":    "#1d4ed8",   # blue – completed step
    "pill_active":  "#3d7aed",   # blue – current step
    "pill_fail":    "#dc2626",   # red  – failed step
    "pill_idle":    "#2a2d3a",   # grey – future step
    "pill_text":    "#ffffff",
    "pill_muted":   "#64748b",
    "line_done":    "#3d7aed",
    "line_idle":    "#2a2d3a",
    "log_bg":       "#111318",
    "log_header":   "#141720",
    "log_border":   "#2d3148",
    "log_text":     "#dde3ed",   # all log lines: near-white
    "log_error":    "#fca5a5",   # soft red for errors only
    "log_dim":      "#8896a8",
    "scrollbar":    "#2a2d3a",
    "scroll_hdl":   "#3d4460",
    "btn_idle_bg":  "#1a1d27",
    "btn_idle_bdr": "#252836",
    "btn_idle_fg":  "#94a3b8",
    "radio_bg":     "#1a1d27",
    "radio_bdr":    "#252836",
    "radio_fg":     "#64748b",
    "radio_chk_bg": "#3d7aed",
    "radio_chk_fg": "#ffffff",
    "radio_hov_bdr":"#3d7aed",
    "radio_hov_fg": "#e2e8f0",
    "act_idle_bg":  "#1a1d27",
    "act_idle_bdr": "#252836",
    "act_idle_fg":  "#64748b",
    "act_active_bg":"#3d7aed",
    "act_active_bdr":"#5aaaff",
    "act_active_fg":"#ffffff",
    "div_color":    "#252836",
    "exec_bg":      "#3d7aed",
    "exec_fg":      "#ffffff",
    "badge_ok_fg":  "#86efac",
    "badge_ok_bg":  "#14532d",
    "badge_ok_bdr": "#166534",
    "badge_fail_fg":"#fca5a5",
    "badge_fail_bg":"#7f1d1d",
    "badge_fail_bdr":"#991b1b",
    "abar_bg":      "#141720",
    "abar_bdr":     "#1e2130",
    "abar_btn_bg":  "#2a2d3a",
    "abar_btn_bdr": "#252836",
    "abar_btn_fg":  "#e2e8f0",
    "back_bg":      "transparent",
    "back_bdr":     "#252836",
    "back_fg":      "#64748b",
    "lbl_muted":    "#64748b",
    "lbl_title":    "#e2e8f0",
    "lbl_sub":      "#64748b",
    "vline":        "#252836",
}

LIGHT = {
    "chrome_bg":    "#ffffff",
    "chrome_bdr":   "#e2e8f0",
    "pill_done":    "#1d4ed8",   # blue
    "pill_active":  "#2563eb",
    "pill_fail":    "#dc2626",
    "pill_idle":    "#cbd5e1",
    "pill_text":    "#ffffff",
    "pill_muted":   "#94a3b8",
    "line_done":    "#2563eb",
    "line_idle":    "#e2e8f0",
    "log_bg":       "#f8fafc",
    "log_header":   "#f1f5f9",
    "log_border":   "#e2e8f0",
    "log_text":     "#1e293b",   # all log lines: near-black
    "log_error":    "#b91c1c",   # dark red for errors
    "log_dim":      "#94a3b8",
    "scrollbar":    "#e2e8f0",
    "scroll_hdl":   "#94a3b8",
    "btn_idle_bg":  "#ffffff",
    "btn_idle_bdr": "#e2e8f0",
    "btn_idle_fg":  "#64748b",
    "radio_bg":     "#ffffff",
    "radio_bdr":    "#cbd5e1",
    "radio_fg":     "#64748b",
    "radio_chk_bg": "#2563eb",
    "radio_chk_fg": "#ffffff",
    "radio_hov_bdr":"#2563eb",
    "radio_hov_fg": "#0f172a",
    "act_idle_bg":  "#ffffff",
    "act_idle_bdr": "#cbd5e1",
    "act_idle_fg":  "#64748b",
    "act_active_bg":"#2563eb",
    "act_active_bdr":"#1d4ed8",
    "act_active_fg":"#ffffff",
    "div_color":    "#e2e8f0",
    "exec_bg":      "#2563eb",
    "exec_fg":      "#ffffff",
    "badge_ok_fg":  "#14532d",
    "badge_ok_bg":  "#dcfce7",
    "badge_ok_bdr": "#15803d",
    "badge_fail_fg":"#991b1b",
    "badge_fail_bg":"#fee2e2",
    "badge_fail_bdr":"#dc2626",
    "abar_bg":      "#f1f5f9",
    "abar_bdr":     "#e2e8f0",
    "abar_btn_bg":  "#ffffff",
    "abar_btn_bdr": "#e2e8f0",
    "abar_btn_fg":  "#334155",
    "back_bg":      "transparent",
    "back_bdr":     "#e2e8f0",
    "back_fg":      "#94a3b8",
    "lbl_muted":    "#64748b",
    "lbl_title":    "#0f172a",
    "lbl_sub":      "#64748b",
    "vline":        "#e2e8f0",
}


def _is_dark() -> bool:
    """Detect active theme by sampling the application palette."""
    app = QApplication.instance()
    if app is None:
        return True
    bg = app.palette().color(QPalette.Window)
    return bg.lightness() < 128


def _t() -> dict:
    """Return the correct token dict for the current theme."""
    return DARK if _is_dark() else LIGHT


# =============================================================================
#  StepProgressBar  – custom-painted, no circles/dots
# =============================================================================

class StepProgressBar(QWidget):
    """
    Fedora-style step pills connected by thin lines.
    Completed = blue, Active = blue (brighter), Idle = grey.
    On failure: active step turns red.  No yellow anywhere.
    The numbered circle indicator is removed – label only.
    """

    def __init__(self, steps: list[tuple[str, str]], parent=None):
        super().__init__(parent)
        self._steps  = steps
        self._active = 0
        self._failed = False
        self.setFixedHeight(64)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def set_step(self, key: str, failed: bool = False):
        self._active = _STEP_INDEX.get(key, 0)
        self._failed = failed
        self.update()

    def paintEvent(self, _event):
        from PySide6.QtGui import QPainter, QBrush, QFontMetrics
        from PySide6.QtCore import QRectF

        t = _t()
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        W = self.width()
        H = self.height()
        n = len(self._steps)

        pill_w  = 116
        pill_h  = 30
        line_h  = 2
        spacing = (W - n * pill_w) / (n + 1)
        y_pill  = (H - pill_h) / 2
        y_line  = H / 2

        for i, (key, label) in enumerate(self._steps):
            x = spacing + i * (pill_w + spacing)

            # connector line before this pill
            if i > 0:
                prev_x = spacing + (i - 1) * (pill_w + spacing) + pill_w
                from PySide6.QtCore import QRectF as R
                line_rect = R(prev_x, y_line - line_h / 2, x - prev_x, line_h)
                # line is "done" colour if this step is reached
                line_col = t["line_done"] if i <= self._active else t["line_idle"]
                p.fillRect(line_rect, QColor(line_col))

            # pill colour
            if i < self._active:
                # completed – solid blue
                col = t["pill_done"]
            elif i == self._active:
                col = t["pill_fail"] if self._failed else t["pill_active"]
            else:
                col = t["pill_idle"]

            from PySide6.QtCore import QRectF as RF
            rect = RF(x, y_pill, pill_w, pill_h)
            p.setBrush(QBrush(QColor(col)))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(rect, pill_h / 2, pill_h / 2)

            # step label text only – no numbered circle
            fnt = p.font()
            fnt.setPixelSize(12)
            fnt.setBold(i == self._active)
            p.setFont(fnt)
            if i <= self._active:
                p.setPen(QColor(t["pill_text"]))
            else:
                p.setPen(QColor(t["pill_muted"]))
            p.drawText(rect, Qt.AlignCenter, label)

        p.end()


# =============================================================================
#  LogPanel  – terminal-style, theme-aware, minimal colours
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

        # header
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

        # scroll area
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

        # bottom action bar
        self._action_bar = QFrame()
        self._action_bar.setFixedHeight(50)
        self._action_bar.setStyleSheet(
            f"background: {t['abar_bg']}; border-radius: 0 0 8px 8px;"
            f" border-top: 1px solid {t['abar_bdr']};"
        )
        arow = QHBoxLayout(self._action_bar)
        arow.setContentsMargins(12, 0, 12, 0)
        arow.setSpacing(8)
        self.retry_btn    = QPushButton("↺  Retry")
        self.new_task_btn = QPushButton("＋  New Task")
        self.export_btn   = QPushButton("↓  Export Log")
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
        """Call after the global theme changes to re-style this panel."""
        # Rebuild styles in place – faster than destroying/recreating widgets
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
        # re-colour existing log labels
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

    # ── public API ─────────────────────────────────────────────────────────────

    def clear(self):
        while self._inner_layout.count() > 1:
            item = self._inner_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.status_badge.hide()
        self._action_bar.hide()

    def append_line(self, text: str, style: str = "normal"):
        """
        style: "normal" | "error" | "dim"
        All "normal" lines are the same neutral colour (white/black per theme).
        "error" lines get a soft red. "dim" lines get muted grey.
        No other colours – no green, no blue, no amber.
        """
        t = _t()
        is_error = style == "error"
        is_dim   = style == "dim"
        colour = t["log_error"] if is_error else (t["log_dim"] if is_dim else t["log_text"])

        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lbl.setProperty("log_error", is_error)
        lbl.setProperty("log_dim", is_dim)
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
            self.status_badge.setText("✓  SUCCESS")
            self.status_badge.setStyleSheet(
                f"color: {t['badge_ok_fg']}; background: {t['badge_ok_bg']};"
                f" border: 1px solid {t['badge_ok_bdr']};"
                " font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 10px;"
            )
        else:
            self.status_badge.setText("✗  FAILED")
            self.status_badge.setStyleSheet(
                f"color: {t['badge_fail_fg']}; background: {t['badge_fail_bg']};"
                f" border: 1px solid {t['badge_fail_bdr']};"
                " font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 10px;"
            )
        self.status_badge.show()
        self._action_bar.show()


# =============================================================================
#  SoftwarePage
# =============================================================================

class SoftwarePage(QWidget):
    view_status_requested = Signal()
    back_to_lab           = Signal()

    def __init__(self, inventory_manager, state):
        super().__init__()
        self.inventory_manager = inventory_manager
        self.state             = state
        self._form_cache: dict[tuple[str, str], QWidget] = {}
        self._sim_timer: QTimer | None = None

        self._build_ui()

    # =========================================================================
    #  UI construction  –  no hardcoded colours on QWidget/QFrame/QLabel;
    #  those inherit from global QSS.  Only custom-drawn and terminal widgets
    #  get explicit colours via _t().
    # =========================================================================

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── chrome: back button + progress bar ───────────────────────────────
        self._chrome = QFrame()
        self._chrome.setFixedHeight(112)
        # chrome styled in apply_theme
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

        # ── main two-panel area ───────────────────────────────────────────────
        content_area = QWidget()
        content_layout = QHBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # LEFT: scrollable config form
        left_scroll = QScrollArea()
        left_scroll.setObjectName("SWFormScroll")
        self._left_scroll = left_scroll
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_scroll.setObjectName("LeftScroll")   # styled via QSS scroll rules

        left_panel = QWidget()
        left_panel.setObjectName("SWFormPanel")
        self._left_panel = left_panel
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(36, 28, 36, 28)
        left_layout.setSpacing(20)

        # title (inherits theme colour via QSS QLabel rule)
        self._title_lbl = QLabel("Software Manager")
        self._title_lbl.setStyleSheet("font-size: 20px; font-weight: 800;")
        left_layout.addWidget(self._title_lbl)

        self._sub_lbl = QLabel("Configure the action to deploy to selected PCs")
        self._sub_lbl.setObjectName("SubText")   # grey via QSS
        left_layout.addWidget(self._sub_lbl)

        # divider
        self._divider = QFrame()
        self._divider.setFrameShape(QFrame.HLine)
        left_layout.addWidget(self._divider)

        # OS section label
        os_lbl = QLabel("OPERATING SYSTEM")
        os_lbl.setObjectName("SubText")
        os_lbl.setStyleSheet("font-size: 10px; font-weight: 700; letter-spacing: 1.2px;")
        left_layout.addWidget(os_lbl)

        # OS radio buttons
        os_row = QHBoxLayout()
        os_row.setSpacing(8)
        self._os_group = QButtonGroup(self)
        self._win_radio = self._make_radio("🪟  Windows")
        self._lin_radio = self._make_radio("🐧  Linux")
        self._os_group.addButton(self._win_radio, 0)
        self._os_group.addButton(self._lin_radio, 1)
        os_row.addWidget(self._win_radio)
        os_row.addWidget(self._lin_radio)
        os_row.addStretch()
        left_layout.addLayout(os_row)

        self._win_radio.setChecked(self.state.target_os == "windows")
        self._lin_radio.setChecked(self.state.target_os == "linux")
        self._os_group.buttonClicked.connect(self._on_os_radio_clicked)

        # Action buttons section label
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

        # dynamic form
        self.form_stack = QStackedWidget()
        left_layout.addWidget(self.form_stack)

        # execute button
        self.execute_btn = QPushButton("Execute  →")
        self.execute_btn.setObjectName("PrimaryBtn")
        self.execute_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.execute_btn.clicked.connect(self._on_execute_clicked)
        left_layout.addWidget(self.execute_btn)
        left_layout.addStretch()

        left_scroll.setWidget(left_panel)

        # vertical divider
        self._vline = QFrame()
        self._vline.setFrameShape(QFrame.VLine)
        self._vline.setFixedWidth(1)

        # RIGHT: log panel
        right_wrapper = QWidget()
        rw_layout = QVBoxLayout(right_wrapper)
        rw_layout.setContentsMargins(0, 20, 20, 20)
        self.log_panel = LogPanel()
        rw_layout.addWidget(self.log_panel)

        self.log_panel.retry_btn.clicked.connect(self._on_retry)
        self.log_panel.new_task_btn.clicked.connect(self._on_new_task)
        self.log_panel.export_btn.clicked.connect(self._on_export_log)

        # stretch 2:3 – log gets ~60%, form gets ~40%
        content_layout.addWidget(left_scroll, 2)
        content_layout.addWidget(self._vline)
        content_layout.addWidget(right_wrapper, 3)
        root.addWidget(content_area, 1)

        # apply theme-dependent styles to chrome + dividers
        self.apply_theme()

    # =========================================================================
    #  Theme application
    # =========================================================================

    def apply_theme(self):
        """
        Called once on build and again whenever the global theme changes.
        Updates only the parts that can't inherit from QSS.
        """
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
                background: {t['radio_bg']};
                border: 1px solid {t['radio_bdr']};
                border-radius: 18px;
                color: {t['radio_fg']};
                padding: 7px 20px;
                font-size: 13px;
                font-weight: 600;
                spacing: 0px;
            }}
            QRadioButton::indicator {{ width: 0; height: 0; }}
            QRadioButton:checked {{
                background: {t['radio_chk_bg']};
                border-color: {t['radio_chk_bg']};
                color: {t['radio_chk_fg']};
            }}
            QRadioButton:hover:!checked {{
                border-color: {t['radio_hov_bdr']};
                color: {t['radio_hov_fg']};
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
    #  Form management
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
    #  Event handlers
    # =========================================================================

    def _on_os_radio_clicked(self, btn: QRadioButton):
        self.state.target_os = "windows" if btn is self._win_radio else "linux"
        self._swap_form()

    def _on_action_changed(self, action: str):
        self.state.action = action
        self._swap_form()

    def _on_execute_clicked(self):
        if not self.state.selected_targets:
            self.log_panel.append_line("⚠  No PCs selected – go back and choose targets.", "error")
            return
        self.progress_bar.set_step("executing")
        self.execute_btn.setEnabled(False)
        self.execute_btn.setText("Executing…")
        form = self._form_cache.get(self._current_key())
        if form:
            form.submit()

    def _on_payload_ready(self, form_payload: dict):
        payload = {
            "lab":     self.state.current_lab,
            "targets": self.state.selected_targets,
            **form_payload,
        }
        self.log_panel.clear()
        self._start_execution_log(payload)

    def _on_validation_error(self, msg: str):
        self.progress_bar.set_step("configure")
        self.execute_btn.setEnabled(True)
        self.execute_btn.setText("Execute  →")
        self.log_panel.append_line(f"✗  {msg}", "error")

    # =========================================================================
    #  Simulated Ansible log  (replace timer + _log_lines with real subprocess)
    # =========================================================================

    def _start_execution_log(self, payload: dict):
        os_name = payload.get("os", "?")
        action  = payload.get("action", "?")
        targets = payload.get("targets", [])

        self._log_lines: list[tuple[str, str]] = [
            ("normal", f"PLAY [SYNC – {action.upper()} on {os_name.upper()}] {'*' * 30}"),
            ("dim",    ""),
            ("normal", f"TASK [Gathering Facts] {'*' * 34}"),
        ]
        for t in targets:
            self._log_lines.append(("normal", f"ok: [{t}]"))

        if action == "install" and os_name == "windows":
            fname = payload.get("file", "installer.exe").split("/")[-1].split("\\")[-1]
            self._log_lines += [
                ("dim",    ""),
                ("normal", f"TASK [Copy installer to targets] {'*' * 24}"),
            ]
            for t in targets:
                self._log_lines.append(("normal", f"changed: [{t}] – {fname} → C:\\Windows\\Temp\\"))
            self._log_lines += [
                ("dim",    ""),
                ("normal", f"TASK [Run installer silently] {'*' * 26}"),
            ]
            for t in targets:
                self._log_lines.append(("normal", f"changed: [{t}] – exit code 0"))

        elif action == "install" and os_name == "linux":
            pkgs = payload.get("packages", "package")
            self._log_lines += [
                ("dim",    ""),
                ("normal", f"TASK [apt/dnf – install packages] {'*' * 22}"),
            ]
            for t in targets:
                self._log_lines.append(("normal", f"changed: [{t}] – {pkgs}"))

        elif action == "remove":
            self._log_lines += [
                ("dim",    ""),
                ("normal", f"TASK [Remove software] {'*' * 33}"),
            ]
            for t in targets:
                self._log_lines.append(("normal", f"changed: [{t}]"))

        elif action == "update":
            self._log_lines += [
                ("dim",    ""),
                ("normal", f"TASK [Apply updates] {'*' * 35}"),
            ]
            for t in targets:
                self._log_lines.append(("normal", f"changed: [{t}] – updates applied"))

        self._log_lines += [
            ("dim",    ""),
            ("normal", f"PLAY RECAP {'*' * 44}"),
        ]
        for t in targets:
            self._log_lines.append(
                ("normal", f"{t:<28} : ok=3   changed=2   unreachable=0   failed=0")
            )
        self._log_lines += [
            ("dim",    ""),
            ("normal", "Playbook completed successfully."),
            ("_DONE_OK", ""),
        ]

        self._log_line_idx = 0
        self._sim_timer = QTimer(self)
        self._sim_timer.timeout.connect(self._tick_log)
        self._sim_timer.start(85)

    def _tick_log(self):
        if self._log_line_idx >= len(self._log_lines):
            if self._sim_timer:
                self._sim_timer.stop()
            return
        style, text = self._log_lines[self._log_line_idx]
        self._log_line_idx += 1
        if style == "_DONE_OK":
            self._on_execution_finished(ok=True)
        else:
            self.log_panel.append_line(text, style)

    def _on_execution_finished(self, ok: bool):
        if self._sim_timer:
            self._sim_timer.stop()
        self.progress_bar.set_step("done", failed=not ok)
        self.log_panel.set_status(ok)
        self.execute_btn.setEnabled(True)
        self.execute_btn.setText("Execute  →")

    # =========================================================================
    #  Log action bar
    # =========================================================================

    def _on_retry(self):
        form = self._form_cache.get(self._current_key())
        if form:
            self.progress_bar.set_step("executing")
            self.execute_btn.setEnabled(False)
            self.execute_btn.setText("Executing…")
            form.submit()

    def _on_new_task(self):
        key = self._current_key()
        if key in self._form_cache:
            self._form_cache[key].reset()
        self.log_panel.clear()
        self.progress_bar.set_step("configure")
        self.execute_btn.setEnabled(True)
        self.execute_btn.setText("Execute  →")

    def _on_export_log(self):
        from PySide6.QtWidgets import QFileDialog
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
    #  Lifecycle
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

        # re-apply theme in case it changed since last visit
        self.apply_theme()

        self.log_panel.clear()
        n = len(self.state.selected_targets)
        target_str = f"{n} PC{'s' if n != 1 else ''} selected" if n else "No PCs selected"
        self.log_panel.append_line(
            f"Lab: {self.state.current_lab or '?'}  ·  {target_str}", "dim"
        )
        self.log_panel.append_line("Waiting for execution…", "dim")

        self.progress_bar.set_step("configure")
        self.execute_btn.setEnabled(True)
        self.execute_btn.setText("Execute  →")
        self._swap_form()

        print("[SoftwarePage] Opened for targets:", self.state.selected_targets)


# ── fallback form ─────────────────────────────────────────────────────────────

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