from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QMessageBox, QDialog, QSizePolicy, QGridLayout, QCheckBox,
    QGraphicsOpacityEffect
)
from PySide6.QtCore import Signal, Qt, QPropertyAnimation, QEasingCurve, QTimer

from .create_lab_dialog import CreateLabDialog


# ────────────────────────────────────────────────
#   ThemeToggle class exactly as you provided
# ────────────────────────────────────────────────
class ThemeToggle(QPushButton):
    """Elegant theme toggle with moon/sun symbols"""
   
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(80, 34)
        self.setCursor(Qt.PointingHandCursor)
        self._dark_theme = True
        self.update_style()
       
    def update_style(self):
        """Update button style based on theme"""
        if self._dark_theme:
            self.setText("🌙 Dark")
            bg_color = "#1a2634"
            text_color = "#ecf0f1"
            hover_color = "#2c3e50"
            border_color = "#34495e"
        else:
            self.setText("☀️ Light")
            bg_color = "#f8f9fa"
            text_color = "#2c3e50"
            hover_color = "#e9ecef"
            border_color = "#dee2e6"
       
        self.setStyleSheet(f"""
            ThemeToggle {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
                padding: 0px 12px;
                text-align: left;
            }}
           
            ThemeToggle:hover {{
                background-color: {hover_color};
                border: 1px solid #3498db;
            }}
           
            ThemeToggle:pressed {{
                padding-top: 1px;
                padding-bottom: 0px;
            }}
        """)
   
    def nextCheckState(self):
        super().nextCheckState()
        self._dark_theme = not self.isChecked()
        self.update_style()
       
        # Subtle pulse animation
        self._pulse_animation()
   
    def _pulse_animation(self):
        """Subtle pulse effect when toggling"""
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
       
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(200)
        anim.setStartValue(0.8)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()


class DashboardPage(QWidget):
    lab_selected = Signal(str)
    edit_lab_requested = Signal(str)
    back_requested = Signal()

    # Theme toggle signal
    theme_toggled = Signal(str)

    def __init__(self, inventory_manager, state=None):
        super().__init__()
        self.inventory_manager = inventory_manager
        self.state = state  # optional, but recommended
        self._build_ui()
        self.refresh_labs()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # --- Header ---
        header_layout = QHBoxLayout()

        self.title = QLabel("Lab Management")
        self.title.setObjectName("PageTitle")
        header_layout.addWidget(self.title)

        header_layout.addStretch()

        # Using your ThemeToggle instead of QCheckBox
        self.theme_switch = ThemeToggle(self)

        # Set initial state
        current_theme = getattr(self.state, "theme", "dark") if self.state else "dark"
        is_light = current_theme == "light"
        self.theme_switch.setChecked(is_light)
        self.theme_switch._dark_theme = not is_light   # sync internal flag
        self.theme_switch.update_style()

        # Connect the toggled signal (QPushButton style)
        self.theme_switch.toggled.connect(self._toggle_theme)

        header_layout.addWidget(self.theme_switch)

        self.create_btn = QPushButton("Create New Lab")
        self.create_btn.setObjectName("PrimaryBtn")
        self.create_btn.setCursor(Qt.PointingHandCursor)
        self.create_btn.clicked.connect(self._open_create_dialog)
        header_layout.addWidget(self.create_btn)

        layout.addLayout(header_layout)

        # --- Scroll Area for Lab Grid ---
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.scroll_widget = QWidget()

        self.scroll_layout = QGridLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(16)
        self.scroll_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.scroll.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll)

        # --- Status Label (Footer) ---
        self.status_lbl = QLabel("Select a lab to manage or create a new one.")
        self.status_lbl.setObjectName("SubText")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_lbl)

    def _toggle_theme(self, checked):
        new_theme = "light" if checked else "dark"
        if self.state:
            self.state.theme = new_theme
        self.theme_toggled.emit(new_theme)

    def refresh_labs(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        labs = self.inventory_manager.get_all_labs()

        if not labs:
            self.status_lbl.setText("No labs found. Create one to get started.")
            return

        self.status_lbl.setText(f"Found {len(labs)} lab(s).")

        for i, lab_name in enumerate(labs):
            card = self._create_lab_card(lab_name)
            self.scroll_layout.addWidget(card, i // 2, i % 2)

    def _create_lab_card(self, lab_name: str) -> QFrame:
        card = QFrame()
        card.setObjectName("DashboardCard")

        card.setMinimumWidth(300)
        card.setMinimumHeight(200)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        main_layout = QVBoxLayout(card)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(10)

        name_lbl = QLabel(lab_name)
        name_lbl.setObjectName("CardTitle")
        main_layout.addWidget(name_lbl)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #334155; max-height: 1px; margin-top: 5px;")
        main_layout.addWidget(line)

        pcs = self.inventory_manager.get_pcs_for_lab(lab_name)
        layout_data = self.inventory_manager.get_lab_layout(lab_name)

        ip_range = "N/A"
        if pcs:
            ip_list = sorted([pc['ip'] for pc in pcs])
            ip_range = f"{ip_list[0]} - {ip_list[-1]}"

        layout_str = "N/A"
        if layout_data:
            layout_str = f"{layout_data.get('sections', 0)} Sections, {layout_data.get('rows', 0)} Rows, {layout_data.get('cols', 0)} Cols"

        lbl_pcs = QLabel(f"Total PCs: {len(pcs)}")
        lbl_pcs.setObjectName("CardSubtitle")

        lbl_layout = QLabel(f"Structure: {layout_str}")
        lbl_layout.setObjectName("CardSubtitle")

        lbl_ip = QLabel(f"IP Range: {ip_range}")
        lbl_ip.setObjectName("CardSubtitle")

        main_layout.addWidget(lbl_pcs)
        main_layout.addWidget(lbl_layout)
        main_layout.addWidget(lbl_ip)

        main_layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        del_btn = QPushButton("Delete")
        del_btn.setObjectName("DangerBtn")
        del_btn.setFixedWidth(90)
        del_btn.setFixedHeight(38)
        del_btn.clicked.connect(lambda checked, name=lab_name: self._confirm_delete(name))

        edit_btn = QPushButton("Edit")
        edit_btn.setObjectName("SecondaryBtn")
        edit_btn.setFixedWidth(90)
        edit_btn.setFixedHeight(38)
        edit_btn.clicked.connect(lambda: self.edit_lab_requested.emit(lab_name))

        open_btn = QPushButton("Open Lab")
        open_btn.setObjectName("SecondaryBtn")
        open_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        open_btn.setFixedHeight(38)
        open_btn.clicked.connect(lambda: self.lab_selected.emit(lab_name))

        btn_layout.addWidget(del_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(open_btn)

        main_layout.addLayout(btn_layout)
        return card

    def _open_create_dialog(self):
        try:
            dlg = CreateLabDialog(self)
            if dlg.exec() != QDialog.Accepted:
                return

            data = dlg.get_data()
            layout = data["layout"]
            ips = data["ips"]

            pcs = []
            idx = 0
            for sec in range(1, layout["sections"] + 1):
                for r in range(1, layout["rows"] + 1):
                    for c in range(1, layout["cols"] + 1):
                        pcs.append({
                            "name": f"PC-{idx+1:03d}",
                            "ip": ips[idx],
                            "section": sec,
                            "row": r,
                            "col": c
                        })
                        idx += 1

            self.inventory_manager.add_lab_with_layout(data["lab_name"], layout, pcs)
            self.refresh_labs()
            QMessageBox.information(self, "Success", f"Lab '{data['lab_name']}' created.")

        except NameError:
            QMessageBox.critical(self, "Error", "CreateLabDialog not found in imports.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create lab: {str(e)}")

    def _confirm_delete(self, lab_name: str):
        reply = QMessageBox.question(
            self,
            "Delete Lab",
            f"Are you sure you want to delete '{lab_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.inventory_manager.delete_lab(lab_name):
                self.refresh_labs()
            else:
                QMessageBox.warning(self, "Error", "Could not delete lab.")