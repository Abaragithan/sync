# views/software_page.py
"""
Software Manager page.

Dynamically swaps in the correct action form (from action_forms.py)
whenever the user changes OS or action. Each form is instantiated once
and cached so state is preserved if the user switches back.

Payload flow:
  form.payload_ready  →  _on_payload_ready()  →  inventory_manager / Ansible
                                               →  view_status_requested (navigate away)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox,
    QFrame, QStackedWidget, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

from views.action_forms import get_form


# ── button style tokens ───────────────────────────────────────────────────────
_BTN_IDLE = ""          # inherit from global QSS
_BTN_ACTIVE = (
    "background-color: #1a6fd4;"
    "color: white;"
    "font-weight: 700;"
    "border: 2px solid #5aaaff;"
    "border-radius: 6px;"
)

# ── human-readable action labels ──────────────────────────────────────────────
_ACTIONS = [
    ("install", "Install"),
    ("remove",  "Remove"),
    ("update",  "Update"),
]


class SoftwarePage(QWidget):
    view_status_requested = Signal()
    back_to_lab = Signal()

    def __init__(self, inventory_manager, state):
        super().__init__()
        self.inventory_manager = inventory_manager
        self.state = state

        # Cache: (os_key, action_key) -> form widget already added to stack
        self._form_cache: dict[tuple[str, str], QWidget] = {}

        self._build_ui()

    # ─────────────────────────────────────────────────────────────────────────
    #  UI construction
    # ─────────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(60, 40, 60, 40)
        root.setSpacing(0)

        # ── Top bar ──────────────────────────────────────────────────────────
        top_bar = QHBoxLayout()
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self.back_to_lab.emit)
        top_bar.addWidget(self.back_btn)
        top_bar.addStretch()
        root.addLayout(top_bar)

        root.addStretch(2)

        # ── Title ────────────────────────────────────────────────────────────
        title = QLabel("Software Manager")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: 800;")
        root.addWidget(title)

        subtitle = QLabel("Configure and push software actions to selected PCs")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: gray; margin-bottom: 4px;")
        root.addWidget(subtitle)

        root.addSpacing(32)

        # ── Card ─────────────────────────────────────────────────────────────
        card = QFrame()
        card.setObjectName("SoftwareCard")
        card.setMaximumWidth(640)
        card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(20)
        card_layout.setContentsMargins(32, 28, 32, 28)

        # ── OS row ───────────────────────────────────────────────────────────
        os_row = QHBoxLayout()
        os_lbl = QLabel("Operating System")
        os_lbl.setStyleSheet("font-weight: 600;")
        self.os_combo = QComboBox()
        self.os_combo.addItems(["Windows", "Linux"])
        self.os_combo.setCurrentText(
            "Windows" if self.state.target_os == "windows" else "Linux"
        )
        self.os_combo.currentTextChanged.connect(self._on_os_changed)
        os_row.addWidget(os_lbl)
        os_row.addStretch()
        os_row.addWidget(self.os_combo)
        card_layout.addLayout(os_row)

        # ── Action selector row ───────────────────────────────────────────────
        action_row = QHBoxLayout()
        action_row.setSpacing(8)
        self._action_buttons: dict[str, QPushButton] = {}
        for key, label in _ACTIONS:
            btn = QPushButton(label)
            btn.clicked.connect(lambda _=False, k=key: self._on_action_changed(k))
            action_row.addWidget(btn)
            self._action_buttons[key] = btn
        card_layout.addLayout(action_row)

        # Thin separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #2a2a2a;")
        card_layout.addWidget(sep)

        # ── Dynamic form area ─────────────────────────────────────────────────
        self.form_stack = QStackedWidget()
        card_layout.addWidget(self.form_stack)

        # Centre card
        centre = QHBoxLayout()
        centre.addStretch()
        centre.addWidget(card)
        centre.addStretch()
        root.addLayout(centre)

        root.addStretch(3)

    # ─────────────────────────────────────────────────────────────────────────
    #  Event handlers
    # ─────────────────────────────────────────────────────────────────────────

    def _on_os_changed(self, text: str):
        self.state.target_os = text.lower()
        self._swap_form()

    def _on_action_changed(self, action: str):
        self.state.action = action
        self._swap_form()

    # ─────────────────────────────────────────────────────────────────────────
    #  Form management
    # ─────────────────────────────────────────────────────────────────────────

    def _current_key(self) -> tuple[str, str]:
        return (self.state.target_os, self.state.action)

    def _swap_form(self):
        """Show the correct form for the current (os, action) pair."""
        # Highlight active action button
        for key, btn in self._action_buttons.items():
            btn.setStyleSheet(_BTN_ACTIVE if key == self.state.action else _BTN_IDLE)

        key = self._current_key()

        if key not in self._form_cache:
            form = get_form(*key)
            if form is None:
                form = _NoFormPlaceholder(self.state.target_os, self.state.action)
            form.payload_ready.connect(self._on_payload_ready)
            self.form_stack.addWidget(form)
            self._form_cache[key] = form

        self.form_stack.setCurrentWidget(self._form_cache[key])

    # ─────────────────────────────────────────────────────────────────────────
    #  Payload handler
    # ─────────────────────────────────────────────────────────────────────────

    def _on_payload_ready(self, form_payload: dict):
        if not self.state.selected_targets:
            print("[SoftwarePage] No PCs selected – aborting.")
            return

        payload = {
            "lab":     self.state.current_lab,
            "targets": self.state.selected_targets,
            **form_payload,          # os, action, and form-specific fields
        }

        print("[SoftwarePage] Dispatching payload:", payload)
        # TODO: hand off to inventory_manager / Ansible runner here
        self.view_status_requested.emit()

    # ─────────────────────────────────────────────────────────────────────────
    #  Lifecycle
    # ─────────────────────────────────────────────────────────────────────────

    def on_page_show(self):
        """Called by MainWindow each time this page is navigated to."""
        # Sync OS combo without triggering a redundant swap
        self.os_combo.blockSignals(True)
        self.os_combo.setCurrentText(
            "Windows" if self.state.target_os == "windows" else "Linux"
        )
        self.os_combo.blockSignals(False)

        # Reset the cached form for the current key so stale input is cleared
        key = self._current_key()
        if key in self._form_cache:
            self._form_cache[key].reset()

        self._swap_form()

        print("[SoftwarePage] Opened for targets:", self.state.selected_targets)


# ─────────────────────────────────────────────────────────────────────────────
#  Fallback widget (should never appear in normal use)
# ─────────────────────────────────────────────────────────────────────────────

class _NoFormPlaceholder(QWidget):
    payload_ready = Signal(dict)   # never emitted – keeps duck-typing happy

    def __init__(self, os_name: str, action: str):
        super().__init__()
        lbl = QLabel(f'No form available for "{os_name} / {action}".')
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("color: #888;")
        QVBoxLayout(self).addWidget(lbl)

    def reset(self):
        pass