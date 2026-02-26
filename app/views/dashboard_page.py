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
from .dialogs.glass_messagebox import show_glass_message

import ipaddress


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
#   TrashButton (Animated Dustbin Icon - Light Mode Only)
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

        self._hover_anim = QPropertyAnimation(self, b"lid_angle")
        self._hover_anim.setDuration(180)
        self._hover_anim.setEasingCurve(QEasingCurve.OutBack)

        self._click_anim = QPropertyAnimation(self, b"bin_scale")
        self._click_anim.setDuration(140)
        self._click_anim.setEasingCurve(QEasingCurve.OutCubic)

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
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        w = self.width()
        h = self.height()
        cx = w // 2
        cy = h // 2

        bin_color = QColor(200, 60, 60)
        lid_color = QColor(180, 50, 50)
        outline = QColor(0, 0, 0, 35)
        detail = QColor(255, 255, 255, 120)

        if self.underMouse():
            bin_color = bin_color.lighter(115)
            lid_color = lid_color.lighter(115)

        painter.translate(cx, cy)
        painter.scale(self._bin_scale, self._bin_scale)
        painter.translate(-cx, -cy)

        body = QRect(cx - 8, cy - 2, 16, 12)
        painter.setBrush(QBrush(bin_color))
        painter.setPen(QPen(outline, 1))
        painter.drawRoundedRect(body, 2, 2)

        painter.setPen(QPen(detail, 1))
        painter.drawLine(cx - 4, cy + 2, cx - 1, cy + 2)
        painter.drawLine(cx + 1, cy + 2, cx + 4, cy + 2)

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

        painter.setBrush(QBrush(lid_color.lighter(120)))
        painter.setPen(Qt.NoPen)
        handle = QRect(cx - 3, cy - 12, 6, 3)
        painter.drawRoundedRect(handle, 1, 1)

        painter.restore()


# ────────────────────────────────────────────────
#   DashboardPage
# ────────────────────────────────────────────────
class DashboardPage(QWidget):
    lab_selected = Signal(str)
    edit_lab_requested = Signal(str)
    back_requested = Signal()

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

        self.grid_layout.setColumnStretch(0, 1)
        self.grid_layout.setColumnStretch(1, 1)

        self.scroll.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll, 1)

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

    def _create_lab_card(self, lab_name: str) -> QFrame:
        card = HoverCard()
        card.setObjectName("LabCard")
        card.setFrameShape(QFrame.StyledPanel)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card.setMinimumHeight(190)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)

        name = QLabel(lab_name)
        name.setObjectName("LabName")
        header.addWidget(name)
        header.addStretch()
        layout.addLayout(header)

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
        trash_btn.clicked.connect(lambda: self._confirm_delete(lab_name))
        actions.addWidget(trash_btn)

        layout.addLayout(actions)
        return card

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
            desc = QLabel('Click "+ New Lab" to create your first laboratory')
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

    # ── ONLY THIS METHOD CHANGED ──────────────────────────────────────────
    # Removed the manual pcs-building loop (which was section-first and passed
    # dicts). Now passes raw IP strings directly to inventory_manager, which
    # assigns section/row/col using row-first ordering via build_pcs_from_ips().
    def _open_create_dialog(self):
        try:
            dlg = CreateLabDialog(self)
            if dlg.exec() != QDialog.Accepted:
                return

            data = dlg.get_data()

            # data["ips"] is a plain list of IP strings e.g. ["10.0.0.1", ...]
            # inventory_manager.add_lab_with_layout() calls build_pcs_from_ips()
            # internally, which assigns IPs row-first across all sections:
            #   Row 1 of S1 → Row 1 of S2 → Row 1 of S3 → Row 2 of S1 → ...
            self.inventory_manager.add_lab_with_layout(
                data["lab_name"],
                data["layout"],
                data["ips"],
            )

            self.refresh_labs()
            show_glass_message(self, "Success", f"Lab '{data['lab_name']}' created", QMessageBox.Information)

        except Exception as e:
            show_glass_message(self, "Error", str(e), QMessageBox.Critical)
    # ─────────────────────────────────────────────────────────────────────

    def _confirm_delete(self, lab_name: str):
        pcs = self.inventory_manager.get_pcs_for_lab(lab_name)
        dlg = ConfirmDeleteDialog(self, lab_name=lab_name, pcs_count=len(pcs))

        if dlg.exec() == QDialog.Accepted:
            if self.inventory_manager.delete_lab(lab_name):
                self.refresh_labs()
                show_glass_message(self, "Deleted", f"Lab '{lab_name}' has been deleted.", QMessageBox.Information)
            else:
                show_glass_message(self, "Error", f"Failed to delete lab '{lab_name}'.", QMessageBox.Critical)