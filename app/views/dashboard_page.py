from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QMessageBox, QDialog, QSizePolicy, QGridLayout,
    QGraphicsDropShadowEffect, QGraphicsOpacityEffect
)
from PySide6.QtCore import (
    Signal, Qt, QPropertyAnimation, QEasingCurve, QTimer, QRect, Property, QPointF
)
from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QLinearGradient, QFont

from .dialogs.confirm_delete_dialog import ConfirmDeleteDialog
from .dialogs.create_lab_dialog import CreateLabDialog
import ipaddress


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
#   TrashButton (Animated Dustbin Icon)
# ────────────────────────────────────────────────
class TrashButton(QPushButton):
    def _get_lid_angle(self):
        return self._lid_angle

    def _set_lid_angle(self, angle):
        self._lid_angle = angle
        self.update()

    def _get_bin_scale(self):
        return self._bin_scale

    def _set_bin_scale(self, scale):
        self._bin_scale = scale
        self.update()

    lid_angle = Property(float, _get_lid_angle, _set_lid_angle)
    bin_scale = Property(float, _get_bin_scale, _set_bin_scale)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TrashButton")
        self.setCursor(Qt.PointingHandCursor)

        self._lid_angle = 0.0
        self._bin_scale = 1.0

        # Hover: lid opens/closes
        self._hover_anim = QPropertyAnimation(self, b"lid_angle")
        self._hover_anim.setDuration(180)
        self._hover_anim.setEasingCurve(QEasingCurve.OutBack)

        # Click: small scale "pop"
        self._click_anim = QPropertyAnimation(self, b"bin_scale")
        self._click_anim.setDuration(140)
        self._click_anim.setEasingCurve(QEasingCurve.OutCubic)

        # Make it feel like an icon button
        self.setFixedSize(32, 32)
        self.setFlat(True)

    def enterEvent(self, event):
        super().enterEvent(event)
        self._hover_anim.stop()
        self._hover_anim.setStartValue(self._lid_angle)
        self._hover_anim.setEndValue(28.0)
        self._hover_anim.start()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._hover_anim.stop()
        self._hover_anim.setStartValue(self._lid_angle)
        self._hover_anim.setEndValue(0.0)
        self._hover_anim.start()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self._click_anim.stop()
        self._click_anim.setStartValue(self._bin_scale)
        self._click_anim.setEndValue(0.88)
        self._click_anim.start()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self._click_anim.stop()
        self._click_anim.setStartValue(self._bin_scale)
        self._click_anim.setEndValue(1.0)
        self._click_anim.start()

    def paintEvent(self, event):
        # IMPORTANT: allows stylesheet hover background (if you add QSS)
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        w = self.width()
        h = self.height()
        cx = w // 2
        cy = h // 2

        # Theme detection from property (set from DashboardPage)
        is_dark = (self.property("theme") != "light")

        if is_dark:
            bin_color = QColor(220, 80, 80)
            lid_color = QColor(200, 70, 70)
            outline = QColor(0, 0, 0, 50)
            detail = QColor(255, 255, 255, 90)
        else:
            bin_color = QColor(200, 60, 60)
            lid_color = QColor(180, 50, 50)
            outline = QColor(0, 0, 0, 35)
            detail = QColor(255, 255, 255, 120)

        if self.underMouse():
            bin_color = bin_color.lighter(115)
            lid_color = lid_color.lighter(115)

        # Scale animation
        painter.translate(cx, cy)
        painter.scale(self._bin_scale, self._bin_scale)
        painter.translate(-cx, -cy)

        # Body
        body = QRect(cx - 8, cy - 2, 16, 12)
        painter.setBrush(QBrush(bin_color))
        painter.setPen(QPen(outline, 1))
        painter.drawRoundedRect(body, 2, 2)

        # Body details
        painter.setPen(QPen(detail, 1))
        painter.drawLine(cx - 4, cy + 2, cx - 1, cy + 2)
        painter.drawLine(cx + 1, cy + 2, cx + 4, cy + 2)

        # Lid (rotates around hinge)
        painter.save()
        hinge_x = cx
        hinge_y = cy - 4
        painter.translate(hinge_x, hinge_y)
        painter.rotate(self._lid_angle)
        painter.translate(-hinge_x, -hinge_y)

        lid = QRect(cx - 10, cy - 10, 20, 6)
        painter.setBrush(QBrush(lid_color))
        painter.setPen(QPen(outline, 1))
        painter.drawRoundedRect(lid, 2, 2)

        # Handle
        painter.setBrush(QBrush(lid_color.lighter(120)))
        painter.setPen(Qt.NoPen)
        handle = QRect(cx - 3, cy - 12, 6, 3)
        painter.drawRoundedRect(handle, 1, 1)

        painter.restore()


# ────────────────────────────────────────────────
#   DashboardPage (Max 2 columns + Stats Panel)
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
        self.create_btn.clicked.connect(self._open_create_dialog)
        btn_row.addWidget(self.create_btn)

        layout.addLayout(btn_row)

        # ─── Scroll + Grid
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setObjectName("DashboardScroll")

        self.scroll_widget = QWidget()
        self.scroll_widget.setObjectName("DashboardScrollWidget")

        self.grid_layout = QGridLayout(self.scroll_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setHorizontalSpacing(20)
        self.grid_layout.setVerticalSpacing(20)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # ✅ Always max 2 columns
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

    def _toggle_theme(self, checked):
        new_theme = "light" if checked else "dark"
        if self.state:
            self.state.theme = new_theme
        self.theme_toggled.emit(new_theme)
        self.refresh_labs()

    # ─── Row widget: Label + Value
    def _info_row(self, label_text: str, value_text: str) -> QWidget:
        row = QWidget()
        row.setObjectName("LabInfoRow")

        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(12)

        lbl = QLabel(label_text)
        lbl.setObjectName("LabInfoLabel")
        lbl.setFixedWidth(110)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        val = QLabel(value_text)
        val.setObjectName("LabInfoValue")
        val.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        val.setWordWrap(False)

        h.addWidget(lbl)
        h.addWidget(val, 1)
        return row

    # ✅ UPDATED: only button design changed, no functionality touched
    def _create_lab_card(self, lab_name: str) -> QFrame:
        card = HoverCard()
        card.setObjectName("LabCard")
        card.setFrameShape(QFrame.StyledPanel)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card.setMinimumHeight(190)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(10)

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
            config = f"{layout_data.get('sections', 1)}S/{layout_data.get('rows', 1)}R/{layout_data.get('cols', 1)}C"
        else:
            config = "1S/1R/1C"

        ip_range = "N/A"
        if pcs:
            ips = [pc.get("ip") for pc in pcs if pc.get("ip")]
            if ips:
                ip_objs = sorted(ipaddress.ip_address(ip) for ip in ips)
                ip_range = f"{ip_objs[0]} – {ip_objs[-1]}"

        layout.addWidget(self._info_row("Workstations:", str(count)))
        layout.addWidget(self._info_row("Layout:", config))
        layout.addWidget(self._info_row("IP Range:", ip_range))

        layout.addStretch()

        # Actions (same signals, only UI sizes + custom trash icon)
        actions = QHBoxLayout()
        actions.setSpacing(8)

        edit_btn = QPushButton("Edit")
        edit_btn.setObjectName("EditButton")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setFixedHeight(32)
        edit_btn.setFixedWidth(78)
        edit_btn.clicked.connect(lambda: self.edit_lab_requested.emit(lab_name))
        actions.addWidget(edit_btn)

        open_btn = QPushButton("Open")
        open_btn.setObjectName("OpenButton")
        open_btn.setCursor(Qt.PointingHandCursor)
        open_btn.setFixedHeight(36)
        open_btn.setFixedWidth(92)
        open_btn.clicked.connect(lambda: self.lab_selected.emit(lab_name))
        actions.addWidget(open_btn)

        actions.addStretch()

        trash_btn = TrashButton()
        # pass theme so the icon colors match light/dark
        trash_btn.setProperty("theme", getattr(self.state, "theme", "dark") if self.state else "dark")
        trash_btn.clicked.connect(lambda: self._confirm_delete(lab_name))
        actions.addWidget(trash_btn)

        layout.addLayout(actions)
        return card

    # ────────────────────────────────────────────────
    #   Stats Panel (fills extra empty area)
    # ────────────────────────────────────────────────
    def _create_stats_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("StatsPanel")
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        panel.setMinimumHeight(180)

        outer = QVBoxLayout(panel)
        outer.setContentsMargins(18, 16, 18, 16)
        outer.setSpacing(12)

        top = QHBoxLayout()
        title = QLabel("Dashboard Overview")
        title.setObjectName("StatsTitle")
        top.addWidget(title)

        top.addStretch()

        subtitle = QLabel("Quick summary of your labs")
        subtitle.setObjectName("StatsSubTitle")
        top.addWidget(subtitle)

        outer.addLayout(top)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)
        grid.setContentsMargins(0, 0, 0, 0)

        labs = self.inventory_manager.get_all_labs()
        total_labs = len(labs)

        total_pcs = 0
        all_ips = []
        for lab in labs:
            pcs = self.inventory_manager.get_pcs_for_lab(lab) or []
            total_pcs += len(pcs)
            for pc in pcs:
                ip = pc.get("ip")
                if ip:
                    all_ips.append(ip)

        unique_ips = len(set(all_ips))

        from PySide6.QtCore import QDateTime
        updated_text = QDateTime.currentDateTime().toString("dd MMM yyyy, hh:mm AP")

        chips = [
            ("Total Labs", str(total_labs)),
            ("Total Workstations", str(total_pcs)),
            ("Unique IPs", str(unique_ips)),
            ("Last Updated", updated_text),
        ]

        for i, (label, value) in enumerate(chips):
            chip = QFrame()
            chip.setObjectName("StatChip")

            v = QVBoxLayout(chip)
            v.setContentsMargins(14, 12, 14, 12)
            v.setSpacing(6)

            val = QLabel(value)
            val.setObjectName("StatValue")

            labl = QLabel(label)
            labl.setObjectName("StatLabel")

            v.addWidget(val)
            v.addWidget(labl)

            r = i // 2
            c = i % 2
            grid.addWidget(chip, r, c)

        outer.addLayout(grid)

        eff = QGraphicsOpacityEffect(panel)
        panel.setGraphicsEffect(eff)
        eff.setOpacity(0.0)

        fade = QPropertyAnimation(eff, b"opacity")
        fade.setDuration(260)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.OutCubic)

        QTimer.singleShot(0, fade.start)
        return panel

    def _animate_cards_in(self, cards: list[QWidget]):
        if not cards:
            return

        def start():
            for idx, w in enumerate(cards):
                base_pos = w.pos()
                w.move(base_pos.x(), base_pos.y() + 12)

                pos_anim = QPropertyAnimation(w, b"pos", self)
                pos_anim.setDuration(260)
                pos_anim.setStartValue(w.pos())
                pos_anim.setEndValue(base_pos)
                pos_anim.setEasingCurve(QEasingCurve.OutCubic)

                QTimer.singleShot(idx * 70, pos_anim.start)

        QTimer.singleShot(0, start)

    def refresh_labs(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        labs = self.inventory_manager.get_all_labs()

        if not labs:
            empty = QFrame()
            empty.setObjectName("EmptyState")
            empty.setMinimumHeight(320)
            box = QVBoxLayout(empty)
            box.setAlignment(Qt.AlignCenter)
            box.setSpacing(10)

            icon = QLabel("📁")
            icon.setObjectName("EmptyIcon")
            title = QLabel("No labs yet")
            title.setObjectName("EmptyTitle")
            desc = QLabel("Click “+ New Lab” to create your first laboratory")
            desc.setObjectName("EmptyDesc")

            box.addWidget(icon, 0, Qt.AlignCenter)
            box.addWidget(title, 0, Qt.AlignCenter)
            box.addWidget(desc, 0, Qt.AlignCenter)

            self.grid_layout.addWidget(empty, 0, 0, 1, 2)
            return

        cards = []
        for i, lab_name in enumerate(labs):
            card = self._create_lab_card(lab_name)
            row = i // 2
            col = i % 2
            self.grid_layout.addWidget(card, row, col)
            cards.append(card)

        stats_row = (len(labs) + 1) // 2
        stats = self._create_stats_panel()
        self.grid_layout.addWidget(stats, stats_row, 0, 1, 2)

        self._animate_cards_in(cards)

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
        dlg = ConfirmDeleteDialog(self, lab_name=lab_name, pcs_count=len(pcs))

        if dlg.exec() == QDialog.Accepted:
            if self.inventory_manager.delete_lab(lab_name):
                self.refresh_labs()
                QMessageBox.information(self, "Deleted", f"Lab '{lab_name}' has been deleted.")
            else:
                QMessageBox.critical(self, "Error", f"Failed to delete lab '{lab_name}'.")
