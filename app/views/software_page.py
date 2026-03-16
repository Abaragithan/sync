# views/software_page.py
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QStackedWidget, QSizePolicy, QScrollArea, QRadioButton, QButtonGroup,
    QFileDialog,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPalette

from views.action_forms import get_form
from views.software_theme import _t, _STEPS, _ACTIONS
from views.software_widgets import StepProgressBar, LogPanel
from views.software_controller import SoftwareController

import os


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
        self._build_ui()
        self._controller = SoftwareController(
            log_panel=self.log_panel,
            progress_bar=self.progress_bar,
            execute_btn=self.execute_btn,
            state=self.state,
        )

    # =========================================================================
    # UI construction
    # =========================================================================
    def _build_ui(self):
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#f8fafc"))
        self.setPalette(palette)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._chrome = QFrame()
        self._chrome.setFixedHeight(112)
        self._chrome.setAutoFillBackground(True)
        chrome_layout = QVBoxLayout(self._chrome)
        chrome_layout.setContentsMargins(24, 10, 24, 10)
        chrome_layout.setSpacing(6)
        btn_row = QHBoxLayout()
        self.back_btn = QPushButton("← Back")
        self.back_btn.setFixedWidth(90)
        self.back_btn.setObjectName("BackBtn")
        self.back_btn.clicked.connect(self.back_to_lab.emit)
        btn_row.addWidget(self.back_btn)
        btn_row.addStretch()
        chrome_layout.addLayout(btn_row)
        self.progress_bar = StepProgressBar(_STEPS)
        chrome_layout.addWidget(self.progress_bar)
        root.addWidget(self._chrome)

        content_area = QWidget()
        content_area.setAutoFillBackground(True)
        content_layout = QHBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        left_scroll = QScrollArea()
        left_scroll.setObjectName("SWFormScroll")
        self._left_scroll = left_scroll
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_scroll.setAutoFillBackground(True)
        left_panel = QWidget()
        left_panel.setObjectName("SWFormPanel")
        left_panel.setAutoFillBackground(True)
        self._left_panel = left_panel
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(36, 28, 36, 28)
        left_layout.setSpacing(20)

        self._title_lbl = QLabel("Software Manager")
        self._title_lbl.setStyleSheet("font-size: 20px; font-weight: 800; color: #0f172a;")
        left_layout.addWidget(self._title_lbl)

        self._sub_lbl = QLabel("Configure the action to deploy to selected PCs")
        self._sub_lbl.setObjectName("SubText")
        self._sub_lbl.setStyleSheet("color: #64748b;")
        left_layout.addWidget(self._sub_lbl)

        self._divider = QFrame()
        self._divider.setFrameShape(QFrame.HLine)
        self._divider.setStyleSheet("color: #e2e8f0; background: #e2e8f0;")
        left_layout.addWidget(self._divider)

        os_lbl = QLabel("OPERATING SYSTEM")
        os_lbl.setObjectName("SubText")
        os_lbl.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 700; letter-spacing: 1.2px;")
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
        action_lbl.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 700; letter-spacing: 1.2px;")
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
        self.execute_btn.setStyleSheet(
            "QPushButton#PrimaryBtn {"
            "   background: #2563eb; color: white; border: none;"
            "   border-radius: 8px; padding: 12px 24px;"
            "   font-size: 14px; font-weight: 700;"
            "}"
            "QPushButton#PrimaryBtn:hover { background: #1d4ed8; }"
            "QPushButton#PrimaryBtn:pressed { background: #1e40af; }"
            "QPushButton#PrimaryBtn:disabled { background: #cbd5e1; color: #64748b; }"
        )
        self.execute_btn.clicked.connect(self._on_execute_clicked)
        left_layout.addWidget(self.execute_btn)
        left_layout.addStretch()

        left_scroll.setWidget(left_panel)

        self._vline = QFrame()
        self._vline.setFrameShape(QFrame.VLine)
        self._vline.setFixedWidth(1)
        self._vline.setStyleSheet("color: #e2e8f0; background: #e2e8f0;")

        right_wrapper = QWidget()
        right_wrapper.setAutoFillBackground(True)
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
            f"QScrollArea {{ background: {t['log_bg']}; }}"
            f"QScrollBar:vertical {{ background: {t['scrollbar']}; width: 6px; border-radius: 3px; }}"
            f"QScrollBar::handle:vertical {{ background: {t['scroll_hdl']}; border-radius: 3px; }}"
            f"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}"
        )
        self._left_panel.setStyleSheet(f"background: {t['log_bg']};")
        self._apply_radio_style(self._win_radio)
        self._apply_radio_style(self._lin_radio)
        self._refresh_action_btns()
        self.log_panel.setStyleSheet(
            f"background: {t['log_bg']}; border-radius: 8px;"
            f" border: 1px solid {t['log_border']};"
        )
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
        self._controller.run(payload)

    def _on_validation_error(self, msg: str):
        self.progress_bar.set_step("configure")
        self.execute_btn.setEnabled(True)
        self.execute_btn.setText("Execute →")
        self.log_panel.append_line(f"✗ {msg}", "error")

    def _on_retry(self):
        self._controller.retry()

    def _on_new_task(self):
        key = self._current_key()
        if key in self._form_cache:
            self._form_cache[key].reset()
        self.log_panel.clear()
        self.progress_bar.set_step("configure")
        self.execute_btn.setEnabled(True)
        self.execute_btn.setText("Execute →")

    def _on_export_log(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Log", "ansible_log.txt", "Text Files (*.txt)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.log_panel.get_plain_text())
        except OSError as e:
            self.log_panel.append_line(f"Export failed: {e}", "error")

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
    from PySide6.QtCore import Signal
    payload_ready    = Signal(dict)
    validation_error = Signal(str)

    def __init__(self, os_name, action):
        super().__init__()
        lbl = QLabel(f'No form defined for "{os_name} / {action}".')
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setObjectName("SubText")
        lbl.setStyleSheet("color: #64748b;")
        QVBoxLayout(self).addWidget(lbl)

    def submit(self):
        self.validation_error.emit("No form available for this combination.")

    def reset(self):
        pass


