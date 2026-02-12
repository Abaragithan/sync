from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QMessageBox, QDialog, QSizePolicy, QGridLayout,
    QProgressBar, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Signal, Qt, QPropertyAnimation, QEasingCurve, QTimer, QRect, Property, QPointF
from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QLinearGradient, QFont

from .create_lab_dialog import CreateLabDialog


# ────────────────────────────────────────────────
#   ThemeToggle (UNCHANGED - DO NOT EDIT)
# ────────────────────────────────────────────────
class ThemeToggle(QPushButton):
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

    circle_position = Property(float, _get_circle_position, _set_circle_position)
    rotation = Property(float, _get_rotation, _set_rotation)
    pulse_opacity = Property(float, _get_pulse_opacity, _set_pulse_opacity)
    sparkle_opacity = Property(float, _get_sparkle_opacity, _set_sparkle_opacity)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(90, 44)
        self.setCursor(Qt.PointingHandCursor)
        self._dark_theme = False

        self._circle_position = 0.0
        self._rotation = 0
        self._pulse_opacity = 1.0
        self._sparkle_opacity_val = 0.0
        self._sparkle_points = []

        self._animation = QPropertyAnimation(self, b"circle_position")
        self._animation.setDuration(500)
        self._animation.setEasingCurve(QEasingCurve.OutBack)

        self._rotation_anim = QPropertyAnimation(self, b"rotation")
        self._rotation_anim.setDuration(600)
        self._rotation_anim.setEasingCurve(QEasingCurve.OutCubic)

        self._pulse_anim = QPropertyAnimation(self, b"pulse_opacity")
        self._pulse_anim.setDuration(300)
        self._pulse_anim.setEasingCurve(QEasingCurve.OutCubic)

        self._sparkle_anim = QPropertyAnimation(self, b"sparkle_opacity")
        self._sparkle_anim.setDuration(800)
        self._sparkle_anim.setEasingCurve(QEasingCurve.OutQuad)

        self.update_style()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        rect = self.rect()

        if self._dark_theme:
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
            gradient.setColorAt(0, QColor(8, 20, 36))
            gradient.setColorAt(1, QColor(20, 35, 55))
            bg_color = gradient
            border_color = QColor(60, 90, 130)
            text_color = QColor(220, 240, 255)
        else:
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
            gradient.setColorAt(0, QColor(255, 230, 100))
            gradient.setColorAt(1, QColor(255, 210, 60))
            bg_color = gradient
            border_color = QColor(255, 200, 50)
            text_color = QColor(80, 60, 20)

        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1.2))
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 22, 22)

        if self._dark_theme and self.sparkle_opacity > 0.01:
            painter.save()
            painter.setOpacity(self.sparkle_opacity)
            painter.setBrush(QColor(255, 255, 200, 180))
            painter.setPen(Qt.NoPen)
            for x, y in self._sparkle_points:
                size = 2 + (x * y) % 3
                painter.drawEllipse(int(x), int(y), int(size), int(size))
            painter.restore()

        painter.save()
        painter.setOpacity(self.pulse_opacity)
        font = QFont("Segoe UI", 8, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QPen(text_color))
        text_rect = QRect(10, 0, rect.width() - 20, rect.height())

        if self._dark_theme:
            painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignRight, "DARK")
        else:
            painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, "LIGHT")
        painter.restore()

        circle_size = 34
        circle_y = (rect.height() - circle_size) // 2
        circle_x = int(4 + (self._circle_position * (rect.width() - circle_size - 8)))

        painter.setBrush(QColor(0, 0, 0, 30))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(circle_x + 1, circle_y + 2, circle_size, circle_size)

        circle_gradient = QLinearGradient(circle_x, circle_y, circle_x + circle_size, circle_y + circle_size)

        if self._dark_theme:
            circle_gradient.setColorAt(0, QColor(230, 245, 255))
            circle_gradient.setColorAt(1, QColor(200, 225, 255))
            circle_color = QBrush(circle_gradient)
            circle_border = QColor(180, 210, 255)
        else:
            circle_gradient.setColorAt(0, QColor(255, 255, 220))
            circle_gradient.setColorAt(1, QColor(255, 230, 100))
            circle_color = QBrush(circle_gradient)
            circle_border = QColor(255, 210, 80)

        painter.setBrush(circle_color)
        painter.setPen(QPen(circle_border, 1.2))
        painter.drawEllipse(circle_x, circle_y, circle_size, circle_size)

        painter.save()
        painter.translate(circle_x + circle_size // 2, circle_y + circle_size // 2)

        if self._dark_theme:
            painter.rotate(self._rotation * 0.3)
            painter.setBrush(QColor(255, 255, 220, 40))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(-10, -10, 20, 20)
            painter.setPen(QPen(QColor(255, 255, 210), 1.2))
            painter.setBrush(QColor(255, 255, 230))
            painter.drawEllipse(-8, -8, 16, 16)
            painter.setBrush(QColor(230, 230, 210))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(-5, -4, 5, 5)
            painter.drawEllipse(0, -2, 4, 4)
            painter.drawEllipse(3, 2, 3, 3)
            painter.setBrush(QColor(255, 255, 220))
            painter.drawEllipse(-14, -10, 2, 2)
            painter.drawEllipse(12, -8, 2, 2)
            painter.drawEllipse(-15, 5, 2, 2)
        else:
            painter.rotate(self._rotation)
            painter.setBrush(QColor(255, 230, 80, 50))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(-12, -12, 24, 24)
            painter.setPen(QPen(QColor(255, 180, 0), 1.2))
            painter.setBrush(QColor(255, 240, 100))
            painter.drawEllipse(-8, -8, 16, 16)
            painter.setPen(QPen(QColor(255, 220, 80), 2))
            for i in range(8):
                painter.save()
                painter.rotate(i * 45)
                painter.drawLine(12, 0, 18, 0)
                painter.restore()

        painter.restore()

        if self.pulse_opacity < 0.95:
            alpha = int(50 * (1 - self.pulse_opacity))
            painter.setBrush(QColor(255, 255, 255, alpha))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 22, 22)

    def update_style(self):
        self.update()

    def nextCheckState(self):
        super().nextCheckState()
        self._dark_theme = not self.isChecked()
        target_pos = 1.0 if self.isChecked() else 0.0

        self._animation.stop()
        self._animation.setStartValue(self.circle_position)
        self._animation.setEndValue(target_pos)
        self._animation.start()

        self._rotation_anim.stop()
        self._rotation_anim.setStartValue(0)
        self._rotation_anim.setEndValue(360)
        self._rotation_anim.start()

        self._pulse_anim.stop()
        self._pulse_anim.setStartValue(0.7)
        self._pulse_anim.setEndValue(1.0)
        self._pulse_anim.start()

        if self._dark_theme:
            QTimer.singleShot(150, self._create_sparkles)
        else:
            self.sparkle_opacity = 0.0

    def _create_sparkles(self):
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
        super().resizeEvent(event)
        if hasattr(self, '_sparkle_points') and self._dark_theme:
            import random
            self._sparkle_points = []
            for _ in range(15):
                x = random.randint(10, self.width() - 20)
                y = random.randint(5, self.height() - 15)
                self._sparkle_points.append((x, y))


# ────────────────────────────────────────────────
#   HoverCard (Smooth Hover Animation)
# ────────────────────────────────────────────────
class HoverCard(QFrame):
    """Card with smooth hover: shadow blur + slight lift"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)

        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setOffset(0, 8)
        self._shadow.setBlurRadius(18)
        self._shadow.setColor(QColor(0, 0, 0, 140))
        self.setGraphicsEffect(self._shadow)

        self._blur_anim = QPropertyAnimation(self._shadow, b"blurRadius")
        self._blur_anim.setDuration(180)
        self._blur_anim.setEasingCurve(QEasingCurve.OutCubic)

        self._offset_anim = QPropertyAnimation(self._shadow, b"offset")
        self._offset_anim.setDuration(180)
        self._offset_anim.setEasingCurve(QEasingCurve.OutCubic)

    def enterEvent(self, event):
        self._blur_anim.stop()
        self._blur_anim.setStartValue(self._shadow.blurRadius())
        self._blur_anim.setEndValue(34)
        self._blur_anim.start()

        self._offset_anim.stop()
        self._offset_anim.setStartValue(self._shadow.offset())
        self._offset_anim.setEndValue(QPointF(0, 3))
        self._offset_anim.start()

        super().enterEvent(event)

    def leaveEvent(self, event):
        self._blur_anim.stop()
        self._blur_anim.setStartValue(self._shadow.blurRadius())
        self._blur_anim.setEndValue(18)
        self._blur_anim.start()

        self._offset_anim.stop()
        self._offset_anim.setStartValue(self._shadow.offset())
        self._offset_anim.setEndValue(QPointF(0, 8))
        self._offset_anim.start()

        super().leaveEvent(event)


# ────────────────────────────────────────────────
#   DashboardPage
# ────────────────────────────────────────────────
class DashboardPage(QWidget):
    lab_selected = Signal(str)
    edit_lab_requested = Signal(str)
    back_requested = Signal()
    theme_toggled = Signal(str)

    def __init__(self, inventory_manager, state=None):
        super().__init__()
        self.inventory_manager = inventory_manager
        self.state = state
        self.setObjectName("DashboardPage")
        self._build_ui()
        self.refresh_labs()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # ─── Header
        header = QHBoxLayout()
        header.setSpacing(12)

        brand = QLabel("SYNC Lab Manager")
        brand.setObjectName("Brand")
        header.addWidget(brand)

        header.addStretch()
        header.addWidget(self._create_theme_toggle())
        layout.addLayout(header)

        # ─── New Lab Button
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.create_btn = QPushButton("+ New Lab")
        self.create_btn.setObjectName("CreateButton")
        self.create_btn.setCursor(Qt.PointingHandCursor)
        self.create_btn.setFixedHeight(40)
        self.create_btn.setFixedWidth(140)
        self.create_btn.clicked.connect(self._open_create_dialog)
        btn_row.addWidget(self.create_btn)

        layout.addLayout(btn_row)

        # ─── Labs Grid
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout(self.scroll_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setHorizontalSpacing(16)
        self.grid_layout.setVerticalSpacing(16)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.grid_layout.setColumnStretch(0, 1)
        self.grid_layout.setColumnStretch(1, 1)

        self.scroll.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll, 1)

    def _create_theme_toggle(self):
        self.theme_switch = ThemeToggle(self)
        current_theme = getattr(self.state, "theme", "dark") if self.state else "dark"
        is_light = current_theme == "light"
        self.theme_switch.setChecked(is_light)
        self.theme_switch._dark_theme = not is_light
        self.theme_switch.setProperty("circle_position", 1.0 if is_light else 0.0)
        self.theme_switch.update()
        self.theme_switch.toggled.connect(self._toggle_theme)
        return self.theme_switch

    def _info_row(self, label_text: str, value_text: str) -> QWidget:
        row = QWidget()
        row.setObjectName("LabInfoRow")

        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)

        lbl = QLabel(label_text)
        lbl.setObjectName("LabInfoLabel")
        lbl.setFixedWidth(110)

        val = QLabel(value_text)
        val.setObjectName("LabInfoValue")
        val.setWordWrap(False)

        h.addWidget(lbl)
        h.addWidget(val, 1, Qt.AlignLeft)
        h.addStretch()
        return row

    def _create_lab_card(self, lab_name: str) -> QFrame:
        card = HoverCard()
        card.setObjectName("LabCard")
        card.setFrameShape(QFrame.StyledPanel)
        card.setFrameShadow(QFrame.Raised)

        card.setMinimumWidth(380)
        card.setMinimumHeight(180)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(8)

        # Header
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)

        name = QLabel(lab_name)
        name.setObjectName("LabName")
        header.addWidget(name)
        header.addStretch()
        layout.addLayout(header)

        # Data
        pcs = self.inventory_manager.get_pcs_for_lab(lab_name)
        count = len(pcs)

        layout_data = self.inventory_manager.get_lab_layout(lab_name)
        if layout_data:
            config = f"{layout_data.get('sections', 1)}Sections/{layout_data.get('rows', 1)}Rows/{layout_data.get('cols', 1)}Columns"
        else:
            config = "1Sections/1Rows/1Columns"

        if pcs:
            ips = sorted([pc.get("ip") for pc in pcs if pc.get("ip")])
            if ips:
                ip_range = f"{ips[0].split('.')[-1]}–{ips[-1].split('.')[-1]}"
            else:
                ip_range = "N/A"
        else:
            ip_range = "N/A"

        layout.addWidget(self._info_row("Workstations:", str(count)))
        layout.addWidget(self._info_row("Layout:", config))
        layout.addWidget(self._info_row("IP Range:", ip_range))

        layout.addSpacing(6)

        # Actions (buttons expand equally to fit card)
        actions = QHBoxLayout()
        actions.setSpacing(10)

        edit_btn = QPushButton("Edit")
        edit_btn.setObjectName("EditButton")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        edit_btn.clicked.connect(lambda: self.edit_lab_requested.emit(lab_name))
        actions.addWidget(edit_btn)

        open_btn = QPushButton("Open")
        open_btn.setObjectName("OpenButton")
        open_btn.setCursor(Qt.PointingHandCursor)
        open_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        open_btn.clicked.connect(lambda: self.lab_selected.emit(lab_name))
        actions.addWidget(open_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("DeleteButton")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        delete_btn.clicked.connect(lambda: self._confirm_delete(lab_name))
        actions.addWidget(delete_btn)

        layout.addLayout(actions)
        return card

    def _create_empty_state(self) -> QFrame:
        container = QFrame()
        container.setObjectName("EmptyState")
        container.setMinimumHeight(300)

        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)

        icon = QLabel("📁")
        icon.setStyleSheet("font-size: 48px;")
        layout.addWidget(icon)

        title = QLabel("No labs yet")
        title.setObjectName("EmptyTitle")
        layout.addWidget(title)

        desc = QLabel("Create your first lab to get started")
        desc.setObjectName("EmptyDesc")
        layout.addWidget(desc)

        return container

    def _toggle_theme(self, checked):
        new_theme = "light" if checked else "dark"
        if self.state:
            self.state.theme = new_theme
        self.theme_toggled.emit(new_theme)
        self.refresh_labs()

    def refresh_labs(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        labs = self.inventory_manager.get_all_labs()

        if not labs:
            empty = self._create_empty_state()
            self.grid_layout.addWidget(empty, 0, 0, 1, 2)
            return

        for i, lab_name in enumerate(labs):
            card = self._create_lab_card(lab_name)
            row = i // 2
            col = i % 2
            self.grid_layout.addWidget(card, row, col)

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
            QMessageBox.information(self, "Success", f"Lab '{data['lab_name']}' created")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _confirm_delete(self, lab_name: str):
        pcs = self.inventory_manager.get_pcs_for_lab(lab_name)
        reply = QMessageBox.question(
            self,
            "Delete Lab",
            f"Delete {lab_name}? ({len(pcs)} workstations)",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.inventory_manager.delete_lab(lab_name):
                self.refresh_labs()
