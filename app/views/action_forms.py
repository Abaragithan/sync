# views/action_forms.py
"""
Dynamic action forms – theme-transparent.

All widgets deliberately carry NO colour styling so they inherit cleanly
from the global DARK_QSS / LIGHT_QSS.  Only structural properties
(spacing, padding, border-radius) are set inline.

Form matrix
-----------
OS       | Action   | Form class
---------|----------|------------------
Windows  | install  | WinInstallForm   – file picker + silent args + reboot
Windows  | remove   | WinRemoveForm    – display name + optional GUID + reboot
Windows  | update   | WinUpdateForm    – category combo + optional KB + reboot
Linux    | install  | LinuxInstallForm – package name(s) + flags + cache
Linux    | remove   | LinuxRemoveForm  – package name(s) + purge + autoremove
Linux    | update   | LinuxUpdateForm  – packages OR dist-upgrade + cache
"""

import os as _os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QCheckBox, QComboBox,
    QFileDialog, QSizePolicy,
)
from PySide6.QtCore import Signal, Qt


# ── helpers ───────────────────────────────────────────────────────────────────

def _section(text: str) -> QLabel:
    """Small caps section label – inherits colour from global QSS SubText."""
    lbl = QLabel(text.upper())
    lbl.setObjectName("SubText")
    lbl.setStyleSheet(
        "font-size: 10px; font-weight: 700; letter-spacing: 1.1px; margin-bottom: 1px;"
    )
    return lbl


def _field(placeholder: str = "", read_only: bool = False) -> QLineEdit:
    """Standard input – NO colour override, inherits QLineEdit rule from QSS."""
    w = QLineEdit()
    w.setPlaceholderText(placeholder)
    w.setReadOnly(read_only)
    # only structural styling – colours come from global QSS QLineEdit rule
    w.setStyleSheet("border-radius: 6px; padding: 8px 10px; font-size: 13px;")
    return w


class ValidationError(Exception):
    pass


# ── base form ─────────────────────────────────────────────────────────────────

class _BaseForm(QWidget):
    payload_ready    = Signal(dict)
    validation_error = Signal(str)

    def __init__(self):
        super().__init__()
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(12)
        self._layout.setContentsMargins(0, 0, 0, 0)
        # transparent so parent panel background shows through
        self.setAttribute(Qt.WA_TranslucentBackground, False)

    def _add(self, label: str, widget: QWidget) -> QWidget:
        self._layout.addWidget(_section(label))
        self._layout.addWidget(widget)
        return widget

    def _add_row(self, label: str, *widgets) -> None:
        self._layout.addWidget(_section(label))
        row = QHBoxLayout()
        row.setSpacing(8)
        for w in widgets:
            row.addWidget(w)
        self._layout.addLayout(row)

    def _add_check(self, label: str) -> QCheckBox:
        cb = QCheckBox(label)
        # no inline colour – inherits from global QSS QCheckBox
        self._layout.addWidget(cb)
        return cb

    def _add_combo(self, label: str, items: list) -> QComboBox:
        cb = QComboBox()
        cb.addItems(items)
        # structural only
        cb.setStyleSheet("border-radius: 6px; padding: 5px 8px; font-size: 13px;")
        self._add(label, cb)
        return cb

    def submit(self):
        try:
            self.payload_ready.emit(self._collect())
        except ValidationError as e:
            self.validation_error.emit(str(e))

    def reset(self):
        pass

    def _collect(self) -> dict:
        raise NotImplementedError


# ── Windows forms ─────────────────────────────────────────────────────────────

class WinInstallForm(_BaseForm):
    def __init__(self):
        super().__init__()
        self.file_input = _field("No file selected…", read_only=True)
        browse_btn = QPushButton("Browse…")
        browse_btn.setObjectName("SecondaryBtn")
        browse_btn.setFixedWidth(90)
        browse_btn.clicked.connect(self._browse)
        self._add_row("Installer File  (.exe / .msi)", self.file_input, browse_btn)

        self.args_input = _field("/S  /quiet  /norestart")
        self._add("Silent Install Arguments  (optional)", self.args_input)

        self.reboot_cb = self._add_check("Reboot targets after installation")
        self._layout.addStretch()

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Installer", _os.path.expanduser("~"),
            "Installers (*.exe *.msi);;All Files (*)"
        )
        if path:
            self.file_input.setText(path)

    def reset(self):
        self.file_input.clear()
        self.args_input.clear()
        self.reboot_cb.setChecked(False)

    def _collect(self) -> dict:
        f = self.file_input.text().strip()
        if not f:
            raise ValidationError("No installer file selected.")
        return {
            "os": "windows", "action": "install",
            "file": f,
            "args": self.args_input.text().strip(),
            "reboot": self.reboot_cb.isChecked(),
        }


class WinRemoveForm(_BaseForm):
    def __init__(self):
        super().__init__()
        self.name_input = _field("e.g.  VLC media player")
        self._add("Application Display Name", self.name_input)

        self.guid_input = _field("{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}")
        self._add("Product GUID  (optional – improves accuracy)", self.guid_input)

        self.reboot_cb = self._add_check("Reboot targets after removal")
        self._layout.addStretch()

    def reset(self):
        self.name_input.clear()
        self.guid_input.clear()
        self.reboot_cb.setChecked(False)

    def _collect(self) -> dict:
        n = self.name_input.text().strip()
        if not n:
            raise ValidationError("Application display name is required.")
        return {
            "os": "windows", "action": "remove",
            "name": n,
            "guid": self.guid_input.text().strip(),
            "reboot": self.reboot_cb.isChecked(),
        }


class WinUpdateForm(_BaseForm):
    _CATS = [
        "All", "SecurityUpdates", "CriticalUpdates", "UpdateRollups",
        "DefinitionUpdates", "Drivers", "FeaturePacks", "ServicePacks", "Updates",
    ]

    def __init__(self):
        super().__init__()
        self.cat_combo = self._add_combo("Update Category", self._CATS)
        self.kb_input  = _field("KB5034441  (blank = all in category)")
        self._add("Specific KB Article  (optional)", self.kb_input)
        self.reboot_cb = self._add_check("Allow automatic reboot if required")
        self.reboot_cb.setChecked(True)
        self._layout.addStretch()

    def reset(self):
        self.cat_combo.setCurrentIndex(0)
        self.kb_input.clear()
        self.reboot_cb.setChecked(True)

    def _collect(self) -> dict:
        return {
            "os": "windows", "action": "update",
            "category": self.cat_combo.currentText(),
            "kb":       self.kb_input.text().strip(),
            "reboot":   self.reboot_cb.isChecked(),
        }


# ── Linux forms ───────────────────────────────────────────────────────────────

class LinuxInstallForm(_BaseForm):
    def __init__(self):
        super().__init__()
        self.pkg_input   = _field("vlc  git  python3-pip")
        self._add("Package Name(s)", self.pkg_input)
        self.flags_input = _field("--no-install-recommends")
        self._add("Extra Flags  (optional)", self.flags_input)
        self.cache_cb = self._add_check("Update package cache before installing")
        self.cache_cb.setChecked(True)
        self._layout.addStretch()

    def reset(self):
        self.pkg_input.clear()
        self.flags_input.clear()
        self.cache_cb.setChecked(True)

    def _collect(self) -> dict:
        p = self.pkg_input.text().strip()
        if not p:
            raise ValidationError("At least one package name is required.")
        return {
            "os": "linux", "action": "install",
            "packages":     p,
            "flags":        self.flags_input.text().strip(),
            "update_cache": self.cache_cb.isChecked(),
        }


class LinuxRemoveForm(_BaseForm):
    def __init__(self):
        super().__init__()
        self.pkg_input     = _field("vlc  git")
        self._add("Package Name(s)", self.pkg_input)
        self.purge_cb      = self._add_check("Purge configuration files  (--purge)")
        self.autoremove_cb = self._add_check("Run autoremove after removal")
        self.autoremove_cb.setChecked(True)
        self._layout.addStretch()

    def reset(self):
        self.pkg_input.clear()
        self.purge_cb.setChecked(False)
        self.autoremove_cb.setChecked(True)

    def _collect(self) -> dict:
        p = self.pkg_input.text().strip()
        if not p:
            raise ValidationError("At least one package name is required.")
        return {
            "os": "linux", "action": "remove",
            "packages":   p,
            "purge":      self.purge_cb.isChecked(),
            "autoremove": self.autoremove_cb.isChecked(),
        }


class LinuxUpdateForm(_BaseForm):
    def __init__(self):
        super().__init__()
        self.dist_upgrade_cb = QCheckBox("Full dist-upgrade  (update all packages)")
        self.dist_upgrade_cb.toggled.connect(self._toggle_dist)
        self._layout.addWidget(self.dist_upgrade_cb)

        self.pkg_input = _field("firefox  libc6   (blank = all installed)")
        self._add("Specific Package(s)  (optional)", self.pkg_input)

        self.cache_cb = self._add_check("Update package cache first")
        self.cache_cb.setChecked(True)
        self._layout.addStretch()

    def _toggle_dist(self, checked: bool):
        self.pkg_input.setEnabled(not checked)
        self.pkg_input.setPlaceholderText(
            "Disabled – all packages will be upgraded" if checked
            else "firefox  libc6   (blank = all installed)"
        )

    def reset(self):
        self.dist_upgrade_cb.setChecked(False)
        self.pkg_input.clear()
        self.pkg_input.setEnabled(True)
        self.cache_cb.setChecked(True)

    def _collect(self) -> dict:
        return {
            "os": "linux", "action": "update",
            "dist_upgrade": self.dist_upgrade_cb.isChecked(),
            "packages":     self.pkg_input.text().strip(),
            "update_cache": self.cache_cb.isChecked(),
        }


# ── factory ───────────────────────────────────────────────────────────────────

_REGISTRY = {
    ("windows", "install"): WinInstallForm,
    ("windows", "remove"):  WinRemoveForm,
    ("windows", "update"):  WinUpdateForm,
    ("linux",   "install"): LinuxInstallForm,
    ("linux",   "remove"):  LinuxRemoveForm,
    ("linux",   "update"):  LinuxUpdateForm,
}


def get_form(os_name: str, action: str):
    cls = _REGISTRY.get((os_name.lower(), action.lower()))
    return cls() if cls else None