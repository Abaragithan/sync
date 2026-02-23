# views/action_forms.py
"""
Dynamic action forms for the Software Manager page.
Each form is a self-contained QWidget that emits `payload_ready: Signal(dict)`
when the user clicks Execute, carrying everything the caller needs to build
an Ansible task.

Form matrix
-----------
OS       | Action   | Form class
---------|----------|------------------
Windows  | install  | WinInstallForm   – file picker (.exe/.msi) + optional silent args
Windows  | remove   | WinRemoveForm    – app display name + optional product GUID
Windows  | update   | WinUpdateForm    – Windows Update category selector + KB filter
Linux    | install  | LinuxInstallForm – package name(s) + optional extra apt/dnf flags
Linux    | remove   | LinuxRemoveForm  – package name(s) + purge toggle
Linux    | update   | LinuxUpdateForm  – specific packages OR full dist-upgrade toggle
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QCheckBox, QComboBox,
    QFileDialog, QFrame, QSizePolicy
)
from PySide6.QtCore import Signal, Qt


# ─────────────────────────────────────────────
#  Shared helpers
# ─────────────────────────────────────────────

def _section(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet("font-size: 11px; font-weight: 600; color: #888; letter-spacing: 1px; text-transform: uppercase;")
    return lbl


def _input(placeholder: str = "", read_only: bool = False) -> QLineEdit:
    w = QLineEdit()
    w.setPlaceholderText(placeholder)
    w.setReadOnly(read_only)
    return w


def _execute_button() -> QPushButton:
    btn = QPushButton("Execute")
    btn.setObjectName("PrimaryBtn")
    btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    return btn


def _divider() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet("color: #333;")
    return line


class _BaseForm(QWidget):
    """Base class: provides `payload_ready` signal and layout helpers."""
    payload_ready = Signal(dict)

    def __init__(self):
        super().__init__()
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(14)
        self._layout.setContentsMargins(0, 0, 0, 0)

    def _add(self, label_text: str, widget: QWidget) -> QWidget:
        self._layout.addWidget(_section(label_text))
        self._layout.addWidget(widget)
        return widget

    def _add_row(self, label_text: str, *widgets) -> None:
        self._layout.addWidget(_section(label_text))
        row = QHBoxLayout()
        row.setSpacing(8)
        for w in widgets:
            row.addWidget(w)
        self._layout.addLayout(row)

    def _add_check(self, label_text: str) -> QCheckBox:
        cb = QCheckBox(label_text)
        self._layout.addWidget(cb)
        return cb

    def _add_execute(self) -> QPushButton:
        self._layout.addSpacing(4)
        self._layout.addWidget(_divider())
        btn = _execute_button()
        btn.clicked.connect(self._on_execute)
        self._layout.addWidget(btn)
        return btn

    def _on_execute(self):
        raise NotImplementedError

    def reset(self):
        """Override to clear fields when page is re-opened."""
        pass


# ─────────────────────────────────────────────
#  Windows forms
# ─────────────────────────────────────────────

class WinInstallForm(_BaseForm):
    """
    Windows → Install
    Lets the user pick a local .exe/.msi to be copied to target PCs via Ansible,
    plus optional silent-install arguments.
    """

    def __init__(self):
        super().__init__()

        # File picker row
        self.file_input = _input("Select .exe or .msi installer…", read_only=True)
        browse_btn = QPushButton("Browse…")
        browse_btn.setFixedWidth(90)
        browse_btn.clicked.connect(self._browse)
        self._add_row("Installer File", self.file_input, browse_btn)

        # Silent args
        self.args_input = _input('e.g. /S /quiet /norestart')
        self._add("Silent Install Arguments (optional)", self.args_input)

        # Reboot option
        self.reboot_cb = self._add_check("Reboot targets after installation")

        self._add_execute()

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Installer", os.path.expanduser("~"),
            "Installers (*.exe *.msi);;All Files (*)"
        )
        if path:
            self.file_input.setText(path)

    def reset(self):
        self.file_input.clear()
        self.args_input.clear()
        self.reboot_cb.setChecked(False)

    def _on_execute(self):
        self.payload_ready.emit({
            "os": "windows",
            "action": "install",
            "file": self.file_input.text().strip(),
            "args": self.args_input.text().strip(),
            "reboot": self.reboot_cb.isChecked(),
        })


class WinRemoveForm(_BaseForm):
    """
    Windows → Remove
    Uninstalls by display name (used with win_package / win_feature).
    Optionally accepts a product GUID for precision.
    """

    def __init__(self):
        super().__init__()

        self.name_input = _input("e.g. VLC media player")
        self._add("Application Display Name", self.name_input)

        self.guid_input = _input("e.g. {XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}")
        self._add("Product GUID (optional – improves accuracy)", self.guid_input)

        self.reboot_cb = self._add_check("Reboot targets after removal")

        self._add_execute()

    def reset(self):
        self.name_input.clear()
        self.guid_input.clear()
        self.reboot_cb.setChecked(False)

    def _on_execute(self):
        self.payload_ready.emit({
            "os": "windows",
            "action": "remove",
            "name": self.name_input.text().strip(),
            "guid": self.guid_input.text().strip(),
            "reboot": self.reboot_cb.isChecked(),
        })


class WinUpdateForm(_BaseForm):
    """
    Windows → Update
    Runs Windows Update via Ansible's `win_updates` module.
    User can filter by category or by specific KB article.
    """

    _CATEGORIES = [
        "All",
        "SecurityUpdates",
        "CriticalUpdates",
        "UpdateRollups",
        "DefinitionUpdates",
        "Drivers",
        "FeaturePacks",
        "ServicePacks",
        "Updates",
    ]

    def __init__(self):
        super().__init__()

        self.category_combo = QComboBox()
        self.category_combo.addItems(self._CATEGORIES)
        self._layout.addWidget(_section("Update Category"))
        self._layout.addWidget(self.category_combo)

        self.kb_input = _input("e.g. KB5034441 (leave blank for all in category)")
        self._add("Specific KB Article (optional)", self.kb_input)

        self.reboot_cb = self._add_check("Allow automatic reboot if required")
        self.reboot_cb.setChecked(True)

        self._add_execute()

    def reset(self):
        self.category_combo.setCurrentIndex(0)
        self.kb_input.clear()
        self.reboot_cb.setChecked(True)

    def _on_execute(self):
        self.payload_ready.emit({
            "os": "windows",
            "action": "update",
            "category": self.category_combo.currentText(),
            "kb": self.kb_input.text().strip(),
            "reboot": self.reboot_cb.isChecked(),
        })


# ─────────────────────────────────────────────
#  Linux forms
# ─────────────────────────────────────────────

class LinuxInstallForm(_BaseForm):
    """
    Linux → Install
    Installs one or more packages via apt/dnf (manager auto-detected by Ansible).
    Supports extra flags like --no-install-recommends.
    """

    def __init__(self):
        super().__init__()

        self.pkg_input = _input("e.g.  vlc  git  python3-pip")
        self._add("Package Name(s)", self.pkg_input)

        self.flags_input = _input("e.g. --no-install-recommends")
        self._add("Extra Package Manager Flags (optional)", self.flags_input)

        self.update_cache_cb = self._add_check("Update package cache before installing")
        self.update_cache_cb.setChecked(True)

        self._add_execute()

    def reset(self):
        self.pkg_input.clear()
        self.flags_input.clear()
        self.update_cache_cb.setChecked(True)

    def _on_execute(self):
        self.payload_ready.emit({
            "os": "linux",
            "action": "install",
            "packages": self.pkg_input.text().strip(),
            "flags": self.flags_input.text().strip(),
            "update_cache": self.update_cache_cb.isChecked(),
        })


class LinuxRemoveForm(_BaseForm):
    """
    Linux → Remove
    Removes packages. Purge toggle also deletes config files (apt --purge).
    """

    def __init__(self):
        super().__init__()

        self.pkg_input = _input("e.g.  vlc  git")
        self._add("Package Name(s)", self.pkg_input)

        self.purge_cb = self._add_check("Purge configuration files (--purge)")
        self.autoremove_cb = self._add_check("Run autoremove after removal")
        self.autoremove_cb.setChecked(True)

        self._add_execute()

    def reset(self):
        self.pkg_input.clear()
        self.purge_cb.setChecked(False)
        self.autoremove_cb.setChecked(True)

    def _on_execute(self):
        self.payload_ready.emit({
            "os": "linux",
            "action": "remove",
            "packages": self.pkg_input.text().strip(),
            "purge": self.purge_cb.isChecked(),
            "autoremove": self.autoremove_cb.isChecked(),
        })


class LinuxUpdateForm(_BaseForm):
    """
    Linux → Update
    Either updates specific packages or runs a full dist-upgrade.
    Dist-upgrade mode disables the package name field.
    """

    def __init__(self):
        super().__init__()

        self.dist_upgrade_cb = QCheckBox("Full dist-upgrade (update everything)")
        self.dist_upgrade_cb.toggled.connect(self._toggle_dist_upgrade)
        self._layout.addWidget(self.dist_upgrade_cb)

        self.pkg_input = _input("e.g.  firefox  libc6  (leave blank = all installed)")
        self._add("Specific Package(s) to Update (optional)", self.pkg_input)

        self.update_cache_cb = self._add_check("Update package cache first")
        self.update_cache_cb.setChecked(True)

        self._add_execute()

    def _toggle_dist_upgrade(self, checked: bool):
        self.pkg_input.setEnabled(not checked)
        self.pkg_input.setPlaceholderText(
            "Disabled – all packages will be upgraded" if checked
            else "e.g.  firefox  libc6  (leave blank = all installed)"
        )

    def reset(self):
        self.dist_upgrade_cb.setChecked(False)
        self.pkg_input.clear()
        self.pkg_input.setEnabled(True)
        self.update_cache_cb.setChecked(True)

    def _on_execute(self):
        self.payload_ready.emit({
            "os": "linux",
            "action": "update",
            "dist_upgrade": self.dist_upgrade_cb.isChecked(),
            "packages": self.pkg_input.text().strip(),
            "update_cache": self.update_cache_cb.isChecked(),
        })


# ─────────────────────────────────────────────
#  Registry / factory
# ─────────────────────────────────────────────

# Maps (os, action) → form class
_FORM_REGISTRY: dict[tuple[str, str], type[_BaseForm]] = {
    ("windows", "install"): WinInstallForm,
    ("windows", "remove"):  WinRemoveForm,
    ("windows", "update"):  WinUpdateForm,
    ("linux",   "install"): LinuxInstallForm,
    ("linux",   "remove"):  LinuxRemoveForm,
    ("linux",   "update"):  LinuxUpdateForm,
}


def get_form(os_name: str, action: str) -> _BaseForm | None:
    """
    Return the appropriate form instance for the given OS + action combo,
    or None if no form is registered.
    """
    cls = _FORM_REGISTRY.get((os_name.lower(), action.lower()))
    return cls() if cls else None