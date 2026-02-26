from __future__ import annotations

import ipaddress

from PySide6.QtCore import (
    Signal, Qt, QPropertyAnimation, QEasingCurve, QTimer,
    Property, QPointF, QDateTime
)
from PySide6.QtGui import QPainter, QBrush, QColor, QPen
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QMessageBox, QDialog, QSizePolicy,
    QGridLayout, QGraphicsDropShadowEffect
)

from .dialogs.confirm_delete_dialog import ConfirmDeleteDialog
from .dialogs.create_lab_dialog import CreateLabDialog
from .dialogs.glass_messagebox import show_glass_message


# ─────────────────────────────────────────────────────────────
#  HoverCard
#  IMPORTANT: Never apply a second QGraphicsEffect to this widget
#  or its children — Qt only allows ONE effect per widget and
#  setting another will delete the shadow, causing the C++ crash.
# ─────────────────────────────────────────────────────────────
class HoverCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)

        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setOffset(0, 2)
        self._shadow.setBlurRadius(10)
        self._shadow.setColor(QColor(0, 0, 0, 35))
        self.setGraphicsEffect(self._shadow)

        self._blur_anim = QPropertyAnimation(self._shadow, b"blurRadius")
        self._blur_anim.setDuration(200)
        self._blur_anim.setEasingCurve(QEasingCurve.OutCubic)

        self._offset_anim = QPropertyAnimation(self._shadow, b"offset")
        self._offset_anim.setDuration(200)
        self._offset_anim.setEasingCurve(QEasingCurve.OutCubic)

    def _shadow_alive(self) -> bool:
        """Guard: check the C++ object is still valid before touching it."""
        try:
            self._shadow.blurRadius()
            return True
        except RuntimeError:
            return False

    def enterEvent(self, event):
        if self._shadow_alive():
            self._blur_anim.stop()
            self._blur_anim.setStartValue(self._shadow.blurRadius())
            self._blur_anim.setEndValue(22)
            self._blur_anim.start()

            self._offset_anim.stop()
            self._offset_anim.setStartValue(self._shadow.offset())
            self._offset_anim.setEndValue(QPointF(0, 6))
            self._offset_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._shadow_alive():
            self._blur_anim.stop()
            self._blur_anim.setStartValue(self._shadow.blurRadius())
            self._blur_anim.setEndValue(10)
            self._blur_anim.start()

            self._offset_anim.stop()
            self._offset_anim.setStartValue(self._shadow.offset())
            self._offset_anim.setEndValue(QPointF(0, 2))
            self._offset_anim.start()
        super().leaveEvent(event)


# ─────────────────────────────────────────────────────────────
#  TrashButton
# ─────────────────────────────────────────────────────────────
class TrashButton(QPushButton):
    def _get_lid_angle(self): return self._lid_angle
    def _set_lid_angle(self, a):
        self._lid_angle = a
        self.update()

    def _get_bin_scale(self): return self._bin_scale
    def _set_bin_scale(self, s):
        self._bin_scale = s
        self.update()

    lid_angle = Property(float, _get_lid_angle, _set_lid_angle)
    bin_scale  = Property(float, _get_bin_scale, _set_bin_scale)

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
        self._click_anim.setDuration(130)
        self._click_anim.setEasingCurve(QEasingCurve.OutCubic)

        self.setFixedSize(32, 32)
        self.setFlat(True)

    def enterEvent(self, e):
        super().enterEvent(e)
        self._hover_anim.stop()
        self._hover_anim.setStartValue(self._lid_angle)
        self._hover_anim.setEndValue(28.0)
        self._hover_anim.start()

    def leaveEvent(self, e):
        super().leaveEvent(e)
        self._hover_anim.stop()
        self._hover_anim.setStartValue(self._lid_angle)
        self._hover_anim.setEndValue(0.0)
        self._hover_anim.start()

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        self._click_anim.stop()
        self._click_anim.setStartValue(self._bin_scale)
        self._click_anim.setEndValue(0.88)
        self._click_anim.start()

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self._click_anim.stop()
        self._click_anim.setStartValue(self._bin_scale)
        self._click_anim.setEndValue(1.0)
        self._click_anim.start()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        from PySide6.QtCore import QRect
        w, h   = self.width(), self.height()
        cx, cy = w // 2, h // 2

        bin_color = QColor(220, 75, 75)
        lid_color = QColor(195, 55, 55)
        outline   = QColor(0, 0, 0, 30)
        detail    = QColor(255, 255, 255, 110)

        if self.underMouse():
            bin_color = bin_color.lighter(112)
            lid_color = lid_color.lighter(112)

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
        painter.translate(cx, cy - 4)
        painter.rotate(self._lid_angle)
        painter.translate(-cx, -(cy - 4))

        lid = QRect(cx - 10, cy - 10, 20, 6)
        painter.setBrush(QBrush(lid_color))
        painter.setPen(QPen(outline, 1))
        painter.drawRoundedRect(lid, 2, 2)

        painter.setBrush(QBrush(lid_color.lighter(120)))
        painter.setPen(Qt.NoPen)
        handle = QRect(cx - 3, cy - 12, 6, 3)
        painter.drawRoundedRect(handle, 1, 1)
        painter.restore()


# ─────────────────────────────────────────────────────────────
#  DashboardPage
# ─────────────────────────────────────────────────────────────
class DashboardPage(QWidget):
    lab_selected        = Signal(str)
    edit_lab_requested  = Signal(str)
    back_requested      = Signal()

    def __init__(self, inventory_manager, state=None):
        super().__init__()
        self.inventory_manager = inventory_manager
        self.state             = state
        self._stats_panel      = None
        self.setObjectName("DashboardPage")
        self._build_ui()
        self.refresh_labs()

    # ── UI skeleton ───────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header bar
        header_bar = QFrame()
        header_bar.setObjectName("HeaderBar")
        header_bar.setFixedHeight(60)

        hb = QHBoxLayout(header_bar)
        hb.setContentsMargins(28, 0, 28, 0)

        brand = QLabel("SYNC Lab Manager")
        brand.setObjectName("Brand")
        hb.addWidget(brand)
        hb.addStretch()

        # Simple text button with refresh symbol
        self.refresh_btn = QPushButton("↻  Refresh")
        self.refresh_btn.setObjectName("CreateButton")
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.setFixedHeight(34)
        self.refresh_btn.setFixedWidth(120)
        self.refresh_btn.clicked.connect(self._handle_refresh)
        hb.addWidget(self.refresh_btn)

        self.create_btn = QPushButton("＋  New Lab")
        self.create_btn.setObjectName("CreateButton")
        self.create_btn.setCursor(Qt.PointingHandCursor)
        self.create_btn.clicked.connect(self._open_create_dialog)
        hb.addWidget(self.create_btn)

        root.addWidget(header_bar)

        divider = QFrame()
        divider.setObjectName("HeaderDivider")
        divider.setFixedHeight(1)
        root.addWidget(divider)

        # Scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setObjectName("DashboardScroll")

        self.scroll_widget = QWidget()
        self.scroll_widget.setObjectName("DashboardScrollWidget")

        self.content_layout = QVBoxLayout(self.scroll_widget)
        self.content_layout.setContentsMargins(28, 24, 28, 28)
        self.content_layout.setSpacing(18)

        self.section_lbl = QLabel("All Laboratories")
        self.section_lbl.setObjectName("SectionLabel")
        self.content_layout.addWidget(self.section_lbl)

        # Card grid
        self.grid_container = QWidget()
        self.grid_container.setObjectName("GridContainer")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setHorizontalSpacing(18)
        self.grid_layout.setVerticalSpacing(18)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid_layout.setColumnStretch(0, 1)
        self.grid_layout.setColumnStretch(1, 1)
        self.content_layout.addWidget(self.grid_container)

        # Trailing stretch (stats panel inserted before this)
        self.content_layout.addStretch()

        self.scroll.setWidget(self.scroll_widget)
        root.addWidget(self.scroll, 1)

    # ── Info row ──────────────────────────────────────────────
    def _info_row(self, label_text: str, value_text: str) -> QWidget:
        row = QWidget()
        row.setObjectName("LabInfoRow")
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)

        lbl = QLabel(label_text)
        lbl.setObjectName("LabInfoLabel")
        lbl.setFixedWidth(106)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        val = QLabel(value_text)
        val.setObjectName("LabInfoValue")
        val.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        h.addWidget(lbl)
        h.addWidget(val, 1)
        return row

    # ── Lab card ──────────────────────────────────────────────
    def _create_lab_card(self, lab_name: str) -> HoverCard:
        card = HoverCard()
        card.setObjectName("LabCard")
        card.setFrameShape(QFrame.StyledPanel)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card.setMinimumHeight(185)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 16)
        layout.setSpacing(8)

        # Header
        hdr = QHBoxLayout()
        dot = QLabel("●")
        dot.setObjectName("CardDot")
        name_lbl = QLabel(lab_name)
        name_lbl.setObjectName("LabName")
        hdr.addWidget(dot)
        hdr.addWidget(name_lbl)
        hdr.addStretch()
        layout.addLayout(hdr)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("CardSep")
        layout.addWidget(sep)
        layout.addSpacing(2)

        # Data — always read fresh from inventory
        pcs         = self.inventory_manager.get_pcs_for_lab(lab_name)
        count       = len(pcs)
        layout_data = self.inventory_manager.get_lab_layout(lab_name)
        config      = (
            f"{layout_data.get('sections', 1)}S/"
            f"{layout_data.get('rows', 1)}R/"
            f"{layout_data.get('cols', 1)}C"
        ) if layout_data else "1S/1R/1C"

        ip_range = "N/A"
        ips = [pc.get("ip") for pc in pcs if pc.get("ip")]
        if ips:
            ip_objs  = sorted(ipaddress.ip_address(ip) for ip in ips)
            ip_range = f"{ip_objs[0]} – {ip_objs[-1]}"

        layout.addWidget(self._info_row("Workstations:", str(count)))
        layout.addWidget(self._info_row("Layout:", config))
        layout.addWidget(self._info_row("IP Range:", ip_range))
        layout.addStretch()

        # Buttons
        actions = QHBoxLayout()
        actions.setSpacing(8)

        edit_btn = QPushButton("Edit")
        edit_btn.setObjectName("EditButton")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setFixedHeight(30)
        edit_btn.setFixedWidth(72)
        # ✅ FIX: use _handle_edit so refresh happens after editing
        edit_btn.clicked.connect(lambda: self._handle_edit(lab_name))
        actions.addWidget(edit_btn)

        open_btn = QPushButton("Open")
        open_btn.setObjectName("OpenButton")
        open_btn.setCursor(Qt.PointingHandCursor)
        open_btn.setFixedHeight(30)
        open_btn.setFixedWidth(80)
        open_btn.clicked.connect(lambda: self.lab_selected.emit(lab_name))
        actions.addWidget(open_btn)

        actions.addStretch()

        trash_btn = TrashButton()
        trash_btn.clicked.connect(lambda: self._confirm_delete(lab_name))
        actions.addWidget(trash_btn)

        layout.addLayout(actions)
        return card

    # ── Stats panel ───────────────────────────────────────────
    def _create_stats_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("StatsPanel")
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        outer = QVBoxLayout(panel)
        outer.setContentsMargins(20, 16, 20, 16)
        outer.setSpacing(14)

        top = QHBoxLayout()
        title = QLabel("Overview")
        title.setObjectName("StatsTitle")
        top.addWidget(title)
        top.addStretch()
        sub = QLabel(QDateTime.currentDateTime().toString("dd MMM yyyy  •  hh:mm AP"))
        sub.setObjectName("StatsSubTitle")
        top.addWidget(sub)
        outer.addLayout(top)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        grid.setContentsMargins(0, 0, 0, 0)

        labs      = self.inventory_manager.get_all_labs()
        total_pcs = 0
        all_ips   = []
        for lab in labs:
            pcs = self.inventory_manager.get_pcs_for_lab(lab) or []
            total_pcs += len(pcs)
            all_ips.extend(pc.get("ip") for pc in pcs if pc.get("ip"))

        chips = [
            ("🏫", str(len(labs)),         "Total Labs"),
            ("🖥️", str(total_pcs),          "Total Workstations"),
            ("🌐", str(len(set(all_ips))),  "Unique IPs"),
        ]

        for i, (emoji, value, label) in enumerate(chips):
            chip = QFrame()
            chip.setObjectName("StatChip")
            v = QVBoxLayout(chip)
            v.setContentsMargins(16, 12, 16, 12)
            v.setSpacing(4)

            top_row = QHBoxLayout()
            top_row.setSpacing(8)
            em_lbl = QLabel(emoji)
            em_lbl.setObjectName("ChipEmoji")
            val_lbl = QLabel(value)
            val_lbl.setObjectName("StatValue")
            top_row.addWidget(em_lbl)
            top_row.addWidget(val_lbl)
            top_row.addStretch()

            lbl = QLabel(label)
            lbl.setObjectName("StatLabel")

            v.addLayout(top_row)
            v.addWidget(lbl)
            grid.addWidget(chip, 0, i)
            grid.setColumnStretch(i, 1)

        outer.addLayout(grid)
        return panel

    # ── Card entrance animation ───────────────────────────────
    # ✅ FIX: uses windowOpacity instead of QGraphicsOpacityEffect
    #         so the HoverCard's shadow is NEVER replaced/deleted.
    def _animate_cards_in(self, cards: list[HoverCard]):
        if not cards:
            return

        def start():
            for idx, card in enumerate(cards):
                base = card.pos()
                card.move(base.x(), base.y() + 14)
                card.setWindowOpacity(0.0)

                op = QPropertyAnimation(card, b"windowOpacity")
                op.setDuration(260)
                op.setStartValue(0.0)
                op.setEndValue(1.0)
                op.setEasingCurve(QEasingCurve.OutCubic)

                pos = QPropertyAnimation(card, b"pos")
                pos.setDuration(280)
                pos.setStartValue(card.pos())
                pos.setEndValue(base)
                pos.setEasingCurve(QEasingCurve.OutCubic)

                QTimer.singleShot(idx * 60, op.start)
                QTimer.singleShot(idx * 60, pos.start)

        QTimer.singleShot(0, start)

    # ── Refresh ───────────────────────────────────────────────
    def refresh_labs(self):
        # Clear cards
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        # Remove old stats panel
        if self._stats_panel is not None:
            self.content_layout.removeWidget(self._stats_panel)
            self._stats_panel.deleteLater()
            self._stats_panel = None

        labs = self.inventory_manager.get_all_labs()

        if not labs:
            empty = QFrame()
            empty.setObjectName("EmptyState")
            empty.setMinimumHeight(300)
            box = QVBoxLayout(empty)
            box.setAlignment(Qt.AlignCenter)
            box.setSpacing(12)

            icon  = QLabel("📁")
            icon.setObjectName("EmptyIcon")
            title = QLabel("No laboratories yet")
            title.setObjectName("EmptyTitle")
            desc  = QLabel('Click  "＋ New Lab"  to create your first laboratory.')
            desc.setObjectName("EmptyDesc")

            box.addWidget(icon,  0, Qt.AlignCenter)
            box.addWidget(title, 0, Qt.AlignCenter)
            box.addWidget(desc,  0, Qt.AlignCenter)
            self.grid_layout.addWidget(empty, 0, 0, 1, 2)
            return

        cards = []
        for i, lab_name in enumerate(labs):
            card = self._create_lab_card(lab_name)
            self.grid_layout.addWidget(card, i // 2, i % 2)
            cards.append(card)

        # Insert stats panel before trailing stretch
        self._stats_panel = self._create_stats_panel()
        self.content_layout.insertWidget(
            self.content_layout.count() - 1,
            self._stats_panel
        )

        self._animate_cards_in(cards)

    # ── ✅ FIX: edit + immediate refresh ──────────────────────
    def _handle_edit(self, lab_name: str):
        """Emit edit signal then refresh so changes show immediately."""
        self.edit_lab_requested.emit(lab_name)
        # If your edit dialog is modal (exec()), delay=0 is fine.
        # 300ms gives non-modal dialogs time to write before refresh.
        QTimer.singleShot(300, self.refresh_labs)

    # ── ✅ NEW: Refresh button handler ────────────────────────
    def _handle_refresh(self):
        """Handle refresh button click."""
        self.refresh_labs()
        
        # Optional: Show a brief message that refresh is complete
        # Uncomment if you want feedback
        # show_glass_message(
        #     self, "Refreshed", "Dashboard updated successfully.",
        #     QMessageBox.Information, timeout=1500
        # )

    # ── Create lab ────────────────────────────────────────────
    def _open_create_dialog(self):
        try:
            dlg = CreateLabDialog(self)
            if dlg.exec() != QDialog.Accepted:
                return
            data = dlg.get_data()
            self.inventory_manager.add_lab_with_layout(
                data["lab_name"],
                data["layout"],
                data["ips"],
            )
            self.refresh_labs()
            show_glass_message(
                self, "Lab Created",
                f"Lab '{data['lab_name']}' has been created successfully.",
                QMessageBox.Information,
            )
        except Exception as e:
            show_glass_message(self, "Error", str(e), QMessageBox.Critical)

    # ── Delete lab ────────────────────────────────────────────
    def _confirm_delete(self, lab_name: str):
        pcs = self.inventory_manager.get_pcs_for_lab(lab_name)
        dlg = ConfirmDeleteDialog(self, lab_name=lab_name, pcs_count=len(pcs))

        if dlg.exec() == QDialog.Accepted:
            if self.inventory_manager.delete_lab(lab_name):
                self.refresh_labs()
                show_glass_message(
                    self, "Lab Deleted",
                    f"Lab '{lab_name}' has been removed.",
                    QMessageBox.Information,
                )
            else:
                show_glass_message(
                    self, "Delete Failed",
                    f"Could not delete lab '{lab_name}'.",
                    QMessageBox.Critical,
                )