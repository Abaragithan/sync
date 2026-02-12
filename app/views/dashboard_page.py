from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QMessageBox, QDialog, QSizePolicy, QGridLayout, QCheckBox,
    QGraphicsOpacityEffect
)
from PySide6.QtCore import Signal, Qt, QPropertyAnimation, QEasingCurve, QTimer, QPoint, QRect, Property
from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QLinearGradient, QFont

from .create_lab_dialog import CreateLabDialog


# ────────────────────────────────────────────────
#   Enhanced ThemeToggle with rich animations
# ────────────────────────────────────────────────
class ThemeToggle(QPushButton):
    """Elegant theme toggle with animated moon/sun and sliding background"""
    
    # Define custom properties for animation
    def _get_circle_position(self):
        return self._circle_position
    
    def _set_circle_position(self, pos):
        self._circle_position = pos
        self.update()
    
    def _get_rotation(self):
        return self._rotation
    
    def _set_rotation(self, rot):
        self._rotation = rot
        self.update()
    
    def _get_pulse_opacity(self):
        return self._pulse_opacity
    
    def _set_pulse_opacity(self, opacity):
        self._pulse_opacity = opacity
        self.update()
    
    def _get_sparkle_opacity(self):
        return self._sparkle_opacity_val
    
    def _set_sparkle_opacity(self, opacity):
        self._sparkle_opacity_val = opacity
        self.update()
    
    # Register properties with Qt
    circle_position = Property(float, _get_circle_position, _set_circle_position)
    rotation = Property(float, _get_rotation, _set_rotation)
    pulse_opacity = Property(float, _get_pulse_opacity, _set_pulse_opacity)
    sparkle_opacity = Property(float, _get_sparkle_opacity, _set_sparkle_opacity)
   
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(100, 40)  # Increased width for better text spacing
        self.setCursor(Qt.PointingHandCursor)
        self._dark_theme = True
        
        # Animation properties
        self._circle_position = 0.0  # 0 = left (dark), 1 = right (light)
        self._rotation = 0
        self._pulse_opacity = 1.0
        self._sparkle_opacity_val = 0.0
        self._sparkle_points = []
        
        # Circle position animation
        self._animation = QPropertyAnimation(self, b"circle_position")
        self._animation.setDuration(500)
        self._animation.setEasingCurve(QEasingCurve.OutBack)
        
        # Rotation animation
        self._rotation_anim = QPropertyAnimation(self, b"rotation")
        self._rotation_anim.setDuration(600)
        self._rotation_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # Pulse animation
        self._pulse_anim = QPropertyAnimation(self, b"pulse_opacity")
        self._pulse_anim.setDuration(300)
        self._pulse_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # Sparkle animation
        self._sparkle_anim = QPropertyAnimation(self, b"sparkle_opacity")
        self._sparkle_anim.setDuration(800)
        self._sparkle_anim.setEasingCurve(QEasingCurve.OutQuad)
        
        self.update_style()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        rect = self.rect()
        
        # Background with gradient
        if self._dark_theme:
            # Night sky gradient
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
            gradient.setColorAt(0, QColor(8, 20, 36))    # Deep blue-black
            gradient.setColorAt(1, QColor(20, 35, 55))   # Dark blue
            bg_color = gradient
            border_color = QColor(60, 90, 130)
            text_color = QColor(220, 240, 255)
        else:
            # Day sky gradient
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
            gradient.setColorAt(0, QColor(255, 200, 100))  # Warm yellow
            gradient.setColorAt(1, QColor(255, 160, 60))   # Orange
            bg_color = gradient
            border_color = QColor(255, 140, 40)
            text_color = QColor(80, 50, 20)
        
        # Draw background with rounded rectangle
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1.5))
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 20, 20)
        
        # Draw sparkles if in dark mode and animating
        if self._dark_theme and self.sparkle_opacity > 0.01:
            painter.save()
            painter.setOpacity(self.sparkle_opacity)
            painter.setBrush(QColor(255, 255, 200, 180))
            painter.setPen(Qt.NoPen)
            
            for x, y in self._sparkle_points:
                size = 2 + (x * y) % 3
                painter.drawEllipse(int(x), int(y), int(size), int(size))
            painter.restore()
        
        # Draw text FIRST (so it appears behind the circle)
        painter.save()
        painter.setOpacity(self.pulse_opacity)
        
        font = QFont("Segoe UI", 9, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QPen(text_color))
        
        # Draw text on the left side, positioned higher
        text_rect = QRect(12, 0, rect.width() - 20, rect.height() - 4)
        
        if self._dark_theme:
            painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, "           DARK")
        else:
            painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, "LIGHT      ")
        
        painter.restore()
        
        # Draw the sliding circle ON TOP of text
        circle_size = 32
        circle_y = (rect.height() - circle_size) // 2
        circle_x = int(4 + (self._circle_position * (rect.width() - circle_size - 8)))
        
        # Circle shadow
        painter.setBrush(QColor(0, 0, 0, 40))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(circle_x + 1, circle_y + 2, circle_size, circle_size)
        
        # Main circle with gradient
        circle_gradient = QLinearGradient(circle_x, circle_y, 
                                          circle_x + circle_size, 
                                          circle_y + circle_size)
        
        if self._dark_theme:
            circle_gradient.setColorAt(0, QColor(230, 245, 255))  # Light blue-white
            circle_gradient.setColorAt(1, QColor(200, 225, 255))  # Soft blue
            circle_color = QBrush(circle_gradient)
            circle_border = QColor(180, 210, 255)
        else:
            circle_gradient.setColorAt(0, QColor(255, 255, 220))  # Light yellow
            circle_gradient.setColorAt(1, QColor(255, 200, 80))   # Golden
            circle_color = QBrush(circle_gradient)
            circle_border = QColor(255, 170, 50)
        
        painter.setBrush(circle_color)
        painter.setPen(QPen(circle_border, 1.2))
        painter.drawEllipse(circle_x, circle_y, circle_size, circle_size)
        
        # Draw icons with rotation
        painter.save()
        painter.translate(circle_x + circle_size // 2, circle_y + circle_size // 2)
        
        if self._dark_theme:
            # Moon icon with rotation effect
            painter.rotate(self._rotation * 0.3)
            
            # Moon glow
            painter.setBrush(QColor(255, 255, 220, 30))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(-10, -10, 20, 20)
            
            # Main moon
            painter.setPen(QPen(QColor(255, 255, 200), 1.2))
            painter.setBrush(QColor(255, 255, 220))
            painter.drawEllipse(-8, -8, 16, 16)
            
            # Moon craters
            painter.setBrush(QColor(220, 220, 200))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(-5, -4, 5, 5)
            painter.drawEllipse(0, -2, 4, 4)
            painter.drawEllipse(3, 2, 3, 3)
            
            # Tiny stars
            painter.setBrush(QColor(255, 255, 200))
            painter.drawEllipse(-12, -8, 2, 2)
            painter.drawEllipse(10, -5, 2, 2)
            
        else:
            # Sun icon with rays
            painter.rotate(self._rotation)
            
            # Sun glow
            painter.setBrush(QColor(255, 200, 50, 40))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(-12, -12, 24, 24)
            
            # Sun core
            painter.setPen(QPen(QColor(255, 140, 0), 1.2))
            painter.setBrush(QColor(255, 220, 80))
            painter.drawEllipse(-7, -7, 14, 14)
            
            # Sun rays
            painter.setPen(QPen(QColor(255, 180, 60), 2))
            for i in range(8):
                painter.save()
                painter.rotate(i * 45)
                painter.drawLine(10, 0, 16, 0)
                
                # Smaller rays between main rays
                if i % 2 == 0:
                    painter.rotate(22.5)
                    painter.drawLine(12, 0, 15, 0)
                painter.restore()
        
        painter.restore()
        
        # Pulse overlay effect
        if self.pulse_opacity < 0.95:
            alpha = int(60 * (1 - self.pulse_opacity))
            painter.setBrush(QColor(255, 255, 255, alpha))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 20, 20)
    
    def update_style(self):
        """Update button style"""
        self.update()
    
    def nextCheckState(self):
        super().nextCheckState()
        
        # Start animations
        target_pos = 1.0 if self.isChecked() else 0.0
        
        # Circle slide animation
        self._animation.stop()
        self._animation.setStartValue(self.circle_position)
        self._animation.setEndValue(target_pos)
        self._animation.start()
        
        # Rotation animation
        self._rotation_anim.stop()
        self._rotation_anim.setStartValue(0)
        self._rotation_anim.setEndValue(360)
        self._rotation_anim.start()
        
        # Pulse animation
        self._pulse_anim.stop()
        self._pulse_anim.setStartValue(0.6)
        self._pulse_anim.setEndValue(1.0)
        self._pulse_anim.start()
        
        self._dark_theme = not self.isChecked()
        
        # Sparkle effect for dark mode
        if self._dark_theme:
            QTimer.singleShot(100, self._create_sparkles)
        else:
            self.sparkle_opacity = 0.0
    
    def _create_sparkles(self):
        """Create sparkling stars animation for dark mode transition"""
        import random
        self._sparkle_points = []
        for _ in range(15):
            x = random.randint(10, self.width() - 20)
            y = random.randint(5, self.height() - 15)
            self._sparkle_points.append((x, y))
        
        self._sparkle_anim.stop()
        self._sparkle_anim.setStartValue(0.8)
        self._sparkle_anim.setEndValue(0.0)
        self._sparkle_anim.start()
    
    def resizeEvent(self, event):
        """Regenerate sparkle points when widget is resized"""
        super().resizeEvent(event)
        if hasattr(self, '_sparkle_points') and self._dark_theme:
            import random
            self._sparkle_points = []
            for _ in range(15):
                x = random.randint(10, self.width() - 20)
                y = random.randint(5, self.height() - 15)
                self._sparkle_points.append((x, y))


class DashboardPage(QWidget):
    lab_selected = Signal(str)
    edit_lab_requested = Signal(str)
    back_requested = Signal()
    theme_toggled = Signal(str)

    def __init__(self, inventory_manager, state=None):
        super().__init__()
        self.inventory_manager = inventory_manager
        self.state = state
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

        # Enhanced ThemeToggle with rich animations
        self.theme_switch = ThemeToggle(self)

        # Set initial state
        current_theme = getattr(self.state, "theme", "dark") if self.state else "dark"
        is_light = current_theme == "light"
        self.theme_switch.setChecked(is_light)
        self.theme_switch._dark_theme = not is_light
        self.theme_switch.setProperty("circle_position", 1.0 if is_light else 0.0)
        self.theme_switch.update()

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
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

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
        # Clear existing widgets
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
        card.setMinimumWidth(320)
        card.setMinimumHeight(220)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        main_layout = QVBoxLayout(card)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(10)

        # Lab name
        name_lbl = QLabel(lab_name)
        name_lbl.setObjectName("CardTitle")
        name_lbl.setWordWrap(True)
        main_layout.addWidget(name_lbl)

        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #334155; max-height: 1px; margin: 8px 0;")
        main_layout.addWidget(line)

        # Lab details
        pcs = self.inventory_manager.get_pcs_for_lab(lab_name)
        layout_data = self.inventory_manager.get_lab_layout(lab_name)

        # IP Range
        ip_range = "N/A"
        if pcs:
            ip_list = sorted([pc['ip'] for pc in pcs if pc.get('ip')])
            if ip_list:
                ip_range = f"{ip_list[0]} - {ip_list[-1]}"

        # Layout structure
        layout_str = "Standard Layout"
        if layout_data:
            layout_str = f"{layout_data.get('sections', 0)} Sections, {layout_data.get('rows', 0)} Rows, {layout_data.get('cols', 0)} Cols"

        # Stats
        lbl_pcs = QLabel(f"🖥️  Total PCs: {len(pcs)}")
        lbl_pcs.setObjectName("CardSubtitle")
        
        lbl_layout = QLabel(f"📐  Structure: {layout_str}")
        lbl_layout.setObjectName("CardSubtitle")
        lbl_layout.setWordWrap(True)
        
        lbl_ip = QLabel(f"🌐  IP Range: {ip_range}")
        lbl_ip.setObjectName("CardSubtitle")
        lbl_ip.setWordWrap(True)

        main_layout.addWidget(lbl_pcs)
        main_layout.addWidget(lbl_layout)
        main_layout.addWidget(lbl_ip)

        main_layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("DangerBtn")
        delete_btn.setFixedWidth(90)
        delete_btn.setFixedHeight(38)
        delete_btn.clicked.connect(lambda checked, name=lab_name: self._confirm_delete(name))

        edit_btn = QPushButton("Edit")
        edit_btn.setObjectName("SecondaryBtn")
        edit_btn.setFixedWidth(90)
        edit_btn.setFixedHeight(38)
        edit_btn.clicked.connect(lambda: self.edit_lab_requested.emit(lab_name))

        open_btn = QPushButton("Open Lab")
        open_btn.setObjectName("PrimaryBtn")
        open_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        open_btn.setFixedHeight(38)
        open_btn.clicked.connect(lambda: self.lab_selected.emit(lab_name))

        btn_layout.addWidget(delete_btn)
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
                            "col": c,
                            "os": "windows"
                        })
                        idx += 1

            self.inventory_manager.add_lab_with_layout(data["lab_name"], layout, pcs)
            self.refresh_labs()
            QMessageBox.information(self, "Success", f"Lab '{data['lab_name']}' created successfully.")

        except NameError:
            QMessageBox.critical(self, "Error", "CreateLabDialog not found in imports.")
        except KeyError as e:
            QMessageBox.critical(self, "Error", f"Missing data: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create lab: {str(e)}")

    def _confirm_delete(self, lab_name: str):
        reply = QMessageBox.question(
            self,
            "Delete Lab",
            f"Are you sure you want to delete '{lab_name}'?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.inventory_manager.delete_lab(lab_name):
                self.refresh_labs()
                QMessageBox.information(self, "Success", f"Lab '{lab_name}' deleted successfully.")
            else:
                QMessageBox.warning(self, "Error", f"Could not delete lab '{lab_name}'.")