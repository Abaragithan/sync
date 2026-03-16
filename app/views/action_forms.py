# views/action_forms.py
"""
Dynamic action forms – theme-transparent.

Form matrix
-----------
OS       | Action   | Form class
---------|----------|------------------
Windows  | install  | WinInstallForm   – chocolatey + file picker fallback
Windows  | remove   | WinRemoveForm    – chocolatey + display name fallback
Windows  | update   | WinUpdateForm    – chocolatey update + Windows Update
Linux    | install  | LinuxInstallForm – package name(s) + flags + cache
Linux    | remove   | LinuxRemoveForm  – package name(s) + purge + autoremove
Linux    | update   | LinuxUpdateForm  – packages OR dist-upgrade + cache
"""

import os as _os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QCheckBox, QComboBox,
    QFileDialog, QSizePolicy, QListWidget, QListWidgetItem,
)
from PySide6.QtCore import Signal, Qt, QTimer


# ── helpers ───────────────────────────────────────────────────────────────────

def _section(text: str) -> QLabel:
    lbl = QLabel(text.upper())
    lbl.setObjectName("SubText")
    lbl.setStyleSheet(
        "font-size: 10px; font-weight: 700; letter-spacing: 1.1px; margin-bottom: 1px;"
    )
    return lbl


def _field(placeholder: str = "", read_only: bool = False) -> QLineEdit:
    w = QLineEdit()
    w.setPlaceholderText(placeholder)
    w.setReadOnly(read_only)
    w.setStyleSheet("border-radius: 6px; padding: 8px 10px; font-size: 13px;")
    return w


def _hint(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("SubText")
    lbl.setStyleSheet("font-size: 10px; letter-spacing: 0.2px; margin-top: -4px;")
    lbl.setWordWrap(True)
    return lbl


class ValidationError(Exception):
    pass


# ── Local Chocolatey package list ─────────────────────────────────────────────

CHOCO_PACKAGES = [
    # Browsers
    ("googlechrome",            "Google Chrome",                "Browser"),
    ("firefox",                 "Mozilla Firefox",              "Browser"),
    ("microsoft-edge",          "Microsoft Edge",               "Browser"),
    ("opera",                   "Opera Browser",                "Browser"),
    ("brave",                   "Brave Browser",                "Browser"),
    ("tor-browser",             "Tor Browser",                  "Browser"),
    # Media
    ("vlc",                     "VLC Media Player",             "Media"),
    ("spotify",                 "Spotify",                      "Media"),
    ("itunes",                  "iTunes",                       "Media"),
    ("k-litecodecpackfull",     "K-Lite Codec Pack Full",       "Media"),
    ("audacity",                "Audacity",                     "Media"),
    ("handbrake",               "HandBrake",                    "Media"),
    ("obs-studio",              "OBS Studio",                   "Media"),
    ("foobar2000",              "foobar2000",                   "Media"),
    ("mpv",                     "MPV Player",                   "Media"),
    ("mpc-hc",                  "MPC-HC",                       "Media"),
    # Developer Tools
    ("vscode",                  "Visual Studio Code",           "Dev"),
    ("git",                     "Git",                          "Dev"),
    ("nodejs",                  "Node.js",                      "Dev"),
    ("python",                  "Python",                       "Dev"),
    ("python3",                 "Python 3",                     "Dev"),
    ("jdk8",                    "Java JDK 8",                   "Dev"),
    ("jdk11",                   "Java JDK 11",                  "Dev"),
    ("jdk17",                   "Java JDK 17",                  "Dev"),
    ("notepadplusplus",         "Notepad++",                    "Dev"),
    ("sublimetext4",            "Sublime Text 4",               "Dev"),
    ("intellijidea-community",  "IntelliJ IDEA Community",      "Dev"),
    ("pycharm-community",       "PyCharm Community",            "Dev"),
    ("eclipse",                 "Eclipse IDE",                  "Dev"),
    ("netbeans",                "NetBeans IDE",                 "Dev"),
    ("androidstudio",           "Android Studio",               "Dev"),
    ("postman",                 "Postman",                      "Dev"),
    ("insomnia-rest-api-client","Insomnia",                     "Dev"),
    ("docker-desktop",          "Docker Desktop",               "Dev"),
    ("vagrant",                 "Vagrant",                      "Dev"),
    ("virtualbox",              "VirtualBox",                   "Dev"),
    ("vmwareworkstation",       "VMware Workstation",           "Dev"),
    ("putty",                   "PuTTY",                        "Dev"),
    ("winscp",                  "WinSCP",                       "Dev"),
    ("filezilla",               "FileZilla",                    "Dev"),
    ("curl",                    "cURL",                         "Dev"),
    ("wget",                    "Wget",                         "Dev"),
    ("wireshark",               "Wireshark",                    "Dev"),
    ("nmap",                    "Nmap",                         "Dev"),
    ("powershell-core",         "PowerShell Core",              "Dev"),
    ("cmder",                   "Cmder",                        "Dev"),
    ("hyper",                   "Hyper Terminal",               "Dev"),
    ("windirstat",              "WinDirStat",                   "Dev"),
    ("sysinternals",            "Sysinternals Suite",           "Dev"),
    ("mysql",                   "MySQL",                        "Dev"),
    ("mysql.workbench",         "MySQL Workbench",              "Dev"),
    ("postgresql",              "PostgreSQL",                   "Dev"),
    ("mongodb",                 "MongoDB",                      "Dev"),
    ("robo3t",                  "Robo 3T",                      "Dev"),
    ("redis",                   "Redis",                        "Dev"),
    ("dbeaver",                 "DBeaver",                      "Dev"),
    ("heidisql",                "HeidiSQL",                     "Dev"),
    # Communication
    ("zoom",                    "Zoom",                         "Communication"),
    ("slack",                   "Slack",                        "Communication"),
    ("microsoft-teams",         "Microsoft Teams",              "Communication"),
    ("discord",                 "Discord",                      "Communication"),
    ("skype",                   "Skype",                        "Communication"),
    ("telegram",                "Telegram",                     "Communication"),
    ("signal",                  "Signal",                       "Communication"),
    ("whatsapp",                "WhatsApp",                     "Communication"),
    # Office & Productivity
    ("libreoffice-fresh",       "LibreOffice",                  "Office"),
    ("openoffice",              "Apache OpenOffice",            "Office"),
    ("onlyoffice",              "ONLYOFFICE",                   "Office"),
    ("foxitreader",             "Foxit Reader",                 "Office"),
    ("adobereader",             "Adobe Acrobat Reader",         "Office"),
    ("sumatrapdf",              "Sumatra PDF",                  "Office"),
    ("calibre",                 "Calibre",                      "Office"),
    ("obsidian",                "Obsidian",                     "Office"),
    ("notion",                  "Notion",                       "Office"),
    ("evernote",                "Evernote",                     "Office"),
    ("todoist",                 "Todoist",                      "Office"),
    # Utilities
    ("7zip",                    "7-Zip",                        "Utility"),
    ("winrar",                  "WinRAR",                       "Utility"),
    ("peazip",                  "PeaZip",                       "Utility"),
    ("ccleaner",                "CCleaner",                     "Utility"),
    ("bleachbit",               "BleachBit",                    "Utility"),
    ("revo-uninstaller",        "Revo Uninstaller",             "Utility"),
    ("geek-uninstaller",        "Geek Uninstaller",             "Utility"),
    ("crystaldiskinfo",         "CrystalDiskInfo",              "Utility"),
    ("hwinfo",                  "HWiNFO",                       "Utility"),
    ("cpu-z",                   "CPU-Z",                        "Utility"),
    ("gpu-z",                   "GPU-Z",                        "Utility"),
    ("speccy",                  "Speccy",                       "Utility"),
    ("autoruns",                "Autoruns",                     "Utility"),
    ("procexp",                 "Process Explorer",             "Utility"),
    ("everything",              "Everything Search",            "Utility"),
    ("powertoys",               "Microsoft PowerToys",          "Utility"),
    ("greenshot",               "Greenshot",                    "Utility"),
    ("lightshot",               "Lightshot",                    "Utility"),
    ("sharex",                  "ShareX",                       "Utility"),
    ("teamviewer",              "TeamViewer",                   "Utility"),
    ("anydesk",                 "AnyDesk",                      "Utility"),
    ("parsec",                  "Parsec",                       "Utility"),
    ("veracrypt",               "VeraCrypt",                    "Utility"),
    ("keepass",                 "KeePass",                      "Utility"),
    ("bitwarden",               "Bitwarden",                    "Utility"),
    ("malwarebytes",            "Malwarebytes",                 "Utility"),
    ("avastfreeantivirus",      "Avast Free Antivirus",         "Utility"),
    ("glasswire",               "GlassWire",                    "Utility"),
    ("windscribe",              "Windscribe VPN",               "Utility"),
    ("protonvpn",               "ProtonVPN",                    "Utility"),
    ("openvpn",                 "OpenVPN",                      "Utility"),
    # Design & Creative
    ("gimp",                    "GIMP",                         "Design"),
    ("inkscape",                "Inkscape",                     "Design"),
    ("krita",                   "Krita",                        "Design"),
    ("blender",                 "Blender",                      "Design"),
    ("figma",                   "Figma",                        "Design"),
    ("darktable",               "Darktable",                    "Design"),
    ("rawtherapee",             "RawTherapee",                  "Design"),
    # Gaming
    ("steam",                   "Steam",                        "Gaming"),
    ("epicgameslauncher",       "Epic Games Launcher",          "Gaming"),
    ("goggalaxy",               "GOG Galaxy",                   "Gaming"),
    ("origin",                  "EA Origin",                    "Gaming"),
    # Science & Education
    ("r.project",               "R Project",                    "Science"),
    ("rstudio",                 "RStudio",                      "Science"),
    ("anaconda3",               "Anaconda",                     "Science"),
    ("miniconda3",              "Miniconda",                    "Science"),
    ("julia",                   "Julia",                        "Science"),
    ("octave",                  "GNU Octave",                   "Science"),
    ("scilab",                  "Scilab",                       "Science"),
    # Runtime
    ("dotnet",                  ".NET SDK",                     "Runtime"),
    ("dotnet-runtime",          ".NET Runtime",                 "Runtime"),
    ("dotnetfx",                ".NET Framework",               "Runtime"),
    ("vcredist140",             "Visual C++ Redistributable",   "Runtime"),
    ("directx",                 "DirectX",                      "Runtime"),
    # Version Control
    ("github-desktop",          "GitHub Desktop",               "VCS"),
    ("gitkraken",               "GitKraken",                    "VCS"),
    ("sourcetree",              "Sourcetree",                   "VCS"),
    ("tortoisegit",             "TortoiseGit",                  "VCS"),
    ("tortoisesvn",             "TortoiseSVN",                  "VCS"),
    # Network
    ("advanced-ip-scanner",     "Advanced IP Scanner",          "Network"),
    ("angry-ip-scanner",        "Angry IP Scanner",             "Network"),
    ("mremoteng",               "mRemoteNG",                    "Network"),
    ("mobaxterm",               "MobaXterm",                    "Network"),
]


# ── Chocolatey autocomplete field (local list) ────────────────────────────────

class ChocoSearchField(QWidget):
    """
    A QLineEdit with instant local search dropdown for Chocolatey packages.
    Supports multiple packages separated by spaces.
    """

    def __init__(self, placeholder: str = "e.g.  vlc  notepadplusplus  7zip"):
        super().__init__()
        self._debounce = QTimer()
        self._debounce.setSingleShot(True)
        self._debounce.timeout.connect(self._do_search)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.input.setStyleSheet("border-radius: 6px; padding: 8px 10px; font-size: 13px;")
        self.input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.input)

        self._dropdown = QListWidget()
        self._dropdown.setStyleSheet("""
            QListWidget {
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                background: #ffffff;
                font-size: 13px;
                padding: 2px;
            }
            QListWidget::item {
                padding: 6px 10px;
                border-radius: 4px;
                color: #0f172a;
            }
            QListWidget::item:hover {
                background: #eff6ff;
                color: #2563eb;
            }
            QListWidget::item:selected {
                background: #2563eb;
                color: #ffffff;
            }
        """)
        self._dropdown.setFixedHeight(0)
        self._dropdown.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self._dropdown)

        self.input.installEventFilter(self)
        self._dropdown.installEventFilter(self)

    def text(self) -> str:
        return self.input.text()

    def setText(self, text: str):
        self.input.setText(text)

    def clear(self):
        self.input.clear()
        self._hide_dropdown()

    def _on_text_changed(self, text: str):
        last_word = text.split()[-1] if text.strip() else ""
        if len(last_word) >= 1:
            self._debounce.start(150)
        else:
            self._hide_dropdown()

    def _do_search(self):
        text = self.input.text().strip()
        last_word = text.split()[-1] if text else ""
        if not last_word:
            self._hide_dropdown()
            return

        query = last_word.lower()
        typed_words = set(text.lower().split())
        matches = []

        for pkg_id, pkg_title, pkg_cat in CHOCO_PACKAGES:
            if pkg_id.lower() in typed_words and pkg_id.lower() != query:
                continue
            if query in pkg_id.lower() or query in pkg_title.lower():
                matches.append((pkg_id, pkg_title, pkg_cat))
            if len(matches) >= 8:
                break

        self._dropdown.clear()
        if not matches:
            self._hide_dropdown()
            return

        for pkg_id, pkg_title, pkg_cat in matches:
            item = QListWidgetItem(f"{pkg_id}  —  {pkg_title}  [{pkg_cat}]")
            item.setData(Qt.UserRole, pkg_id)
            self._dropdown.addItem(item)

        row_h = 34
        self._dropdown.setFixedHeight(min(len(matches), 6) * row_h + 8)

    def _on_item_clicked(self, item: QListWidgetItem):
        pkg_id = item.data(Qt.UserRole)
        current = self.input.text()
        words = current.split()
        if words:
            words[-1] = pkg_id
        else:
            words = [pkg_id]
        self.input.setText(" ".join(words) + " ")
        self.input.setFocus()
        self._hide_dropdown()

    def _hide_dropdown(self):
        self._dropdown.clear()
        self._dropdown.setFixedHeight(0)

    def eventFilter(self, obj, event):
        from PySide6.QtCore import QEvent
        if obj is self.input and event.type() == QEvent.KeyPress:
            key = event.key()
            if key == Qt.Key_Down:
                if self._dropdown.count() > 0:
                    self._dropdown.setFocus()
                    self._dropdown.setCurrentRow(0)
                return True
            elif key == Qt.Key_Escape:
                self._hide_dropdown()
                return True
        if obj is self._dropdown and event.type() == QEvent.KeyPress:
            key = event.key()
            if key in (Qt.Key_Return, Qt.Key_Enter):
                item = self._dropdown.currentItem()
                if item:
                    self._on_item_clicked(item)
                return True
            elif key == Qt.Key_Escape:
                self._hide_dropdown()
                self.input.setFocus()
                return True
        return super().eventFilter(obj, event)


# ── base form ─────────────────────────────────────────────────────────────────

class _BaseForm(QWidget):
    payload_ready    = Signal(dict)
    validation_error = Signal(str)

    def __init__(self):
        super().__init__()
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(12)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

    def _add(self, label: str, widget: QWidget) -> QWidget:
        self._layout.addWidget(_section(label))
        self._layout.addWidget(widget)
        return widget

    def _add_with_hint(self, label: str, widget: QWidget, hint: str) -> QWidget:
        self._layout.addWidget(_section(label))
        self._layout.addWidget(widget)
        self._layout.addWidget(_hint(hint))
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
        self._layout.addWidget(cb)
        return cb

    def _add_combo(self, label: str, items: list) -> QComboBox:
        cb = QComboBox()
        cb.addItems(items)
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

        self.choco_input = ChocoSearchField("e.g.  vlc  notepadplusplus  7zip  git")
        self._add("Chocolatey Package Name(s)  (recommended)", self.choco_input)

        or_lbl = QLabel("── or install from a local file ──")
        or_lbl.setObjectName("SubText")
        or_lbl.setStyleSheet("font-size: 10px; letter-spacing: 0.5px; margin: 4px 0;")
        or_lbl.setAlignment(Qt.AlignCenter)
        self._layout.addWidget(or_lbl)

        self.file_input = _field("No file selected…", read_only=True)
        browse_btn = QPushButton("Browse…")
        browse_btn.setObjectName("SecondaryBtn")
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(self._browse)
        self._add_row("Installer File  (.exe / .msi)", self.file_input, browse_btn)

        self.args_input = _field("/S  /quiet  /norestart")
        self._add("Silent Install Arguments  (optional – for local file only)", self.args_input)

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
        self.choco_input.clear()
        self.file_input.clear()
        self.args_input.clear()
        self.reboot_cb.setChecked(False)

    def _collect(self) -> dict:
        choco = self.choco_input.text().strip()
        f     = self.file_input.text().strip()
        if not choco and not f:
            raise ValidationError("Enter a Chocolatey package name or select a local installer file.")
        return {
            "os": "windows", "action": "install",
            "choco_package": choco,
            "file":          f,
            "args":          self.args_input.text().strip(),
            "reboot":        self.reboot_cb.isChecked(),
        }


class WinRemoveForm(_BaseForm):
    def __init__(self):
        super().__init__()

        self.choco_input = ChocoSearchField("e.g.  vlc  notepadplusplus  7zip  git")
        self._add("Chocolatey Package Name(s)  (recommended)", self.choco_input)

        or_lbl = QLabel("── or remove by display name ──")
        or_lbl.setObjectName("SubText")
        or_lbl.setStyleSheet("font-size: 10px; letter-spacing: 0.5px; margin: 4px 0;")
        or_lbl.setAlignment(Qt.AlignCenter)
        self._layout.addWidget(or_lbl)

        self.name_input = _field("e.g.  VLC media player")
        self._add_with_hint(
            "Application Display Name  (fallback)",
            self.name_input,
            "Used only when no Chocolatey name is given. Must match the name shown in Add/Remove Programs.",
        )

        self.reboot_cb = self._add_check("Reboot targets after removal")
        self._layout.addStretch()

    def reset(self):
        self.choco_input.clear()
        self.name_input.clear()
        self.reboot_cb.setChecked(False)

    def _collect(self) -> dict:
        choco = self.choco_input.text().strip()
        name  = self.name_input.text().strip()
        if not choco and not name:
            raise ValidationError("Enter a Chocolatey package name or an application display name.")
        return {
            "os": "windows", "action": "remove",
            "choco_package": choco,
            "app_name":      name,
            "reboot":        self.reboot_cb.isChecked(),
        }


class WinUpdateForm(_BaseForm):
    def __init__(self):
        super().__init__()

        # ── Chocolatey update (primary) ──
        self.upgrade_all_cb = QCheckBox("Upgrade ALL Chocolatey packages on the PC")
        self.upgrade_all_cb.toggled.connect(self._toggle_upgrade_all)
        self._layout.addWidget(self.upgrade_all_cb)

        self.choco_input = ChocoSearchField("e.g.  vlc  notepadplusplus  git")
        self._add_with_hint(
            "Chocolatey Package Name(s)  (specific packages)",
            self.choco_input,
            "Leave blank and tick above to upgrade everything.",
        )

        self.reboot_cb = self._add_check("Reboot targets after update if required")
        self._layout.addStretch()

    def _toggle_upgrade_all(self, checked: bool):
        self.choco_input.setEnabled(not checked)
        self.choco_input.input.setPlaceholderText(
            "Disabled – all packages will be upgraded" if checked
            else "e.g.  vlc  notepadplusplus  git"
        )

    def reset(self):
        self.upgrade_all_cb.setChecked(False)
        self.choco_input.clear()
        self.choco_input.setEnabled(True)
        self.reboot_cb.setChecked(False)

    def _collect(self) -> dict:
        upgrade_all = self.upgrade_all_cb.isChecked()
        choco       = self.choco_input.text().strip()
        if not upgrade_all and not choco:
            raise ValidationError("Enter a package name or tick 'Upgrade ALL'.")
        return {
            "os":           "windows",
            "action":       "update",
            "choco_package": "all" if upgrade_all else choco,
            "upgrade_all":  upgrade_all,
            "reboot":       self.reboot_cb.isChecked(),
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