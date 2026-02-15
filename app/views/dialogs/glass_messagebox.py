from __future__ import annotations

import math
import random

from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QRect, Property, QPoint
from PySide6.QtWidgets import (
    QDialog, QFrame, QLabel, QPushButton, QHBoxLayout, QVBoxLayout,
    QMessageBox, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QPen, QBrush, QFont, QPainterPath


class RibbonMessageBox(QDialog):
    """
    Glass message dialog:
    - Information: ribbons + confetti (celebration)
    - Warning / Question: NO confetti (only glass + entrance animation)
    - Critical: glitch + shake
    """

    def __init__(
        self,
        parent,
        title: str,
        text: str,
        icon: QMessageBox.Icon = QMessageBox.Information,
        buttons: QMessageBox.StandardButtons = QMessageBox.Ok,
        theme: str = "dark",
    ):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)

        # Window size
        self.resize(520, 240)

        self._theme = (theme or "dark").lower()
        self._icon_type = icon
        self._clicked = QMessageBox.NoButton

        # FX state
        self._particles: list[dict] = []
        self._glitch_offset = 0
        self._ribbon_angle = 0.0

        # Entrance anchor
        self._start_pos: QPoint | None = None
        self.setWindowOpacity(0.0)

        # Card container (transparent, we paint glass)
        self.card = QFrame(self)
        self.card.setObjectName("RibbonCard")
        self.card.setGeometry(40, 26, 440, 190)
        self.card.setStyleSheet("QFrame#RibbonCard{ background: transparent; border: none; }")
        self.card.setAttribute(Qt.WA_TranslucentBackground, True)

        # Shadow
        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(26)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 75))
        self.card.setGraphicsEffect(shadow)

        # Layout
        layout = QVBoxLayout(self.card)
        layout.setContentsMargins(26, 22, 26, 18)
        layout.setSpacing(12)

        # Icon + Title
        top = QHBoxLayout()
        top.setSpacing(12)

        self.icon_lbl = QLabel(self._get_icon_emoji())
        self.icon_lbl.setFont(QFont("Segoe UI Emoji", 36))
        self.icon_lbl.setFixedSize(58, 58)
        self.icon_lbl.setAlignment(Qt.AlignCenter)

        self.title_lbl = QLabel(title)
        self.title_lbl.setWordWrap(True)
        self.title_lbl.setFont(QFont("Segoe UI", 18, QFont.Bold))

        top.addWidget(self.icon_lbl, 0, Qt.AlignTop)
        top.addWidget(self.title_lbl, 1, Qt.AlignVCenter)
        layout.addLayout(top)

        # Message
        self.text_lbl = QLabel(text)
        self.text_lbl.setWordWrap(True)
        self.text_lbl.setAlignment(Qt.AlignCenter)
        self.text_lbl.setFont(QFont("Segoe UI", 12))
        layout.addWidget(self.text_lbl)

        layout.addStretch()

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        self._btn_widgets: list[QPushButton] = []
        for std_btn in self._expand_buttons(buttons):
            btn = QPushButton(self._std_btn_text(std_btn))
            btn.setFixedHeight(38)
            btn.setMinimumWidth(100)
            btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, b=std_btn: self._on_clicked(b))
            btn_row.addWidget(btn)
            self._btn_widgets.append(btn)

        layout.addLayout(btn_row)

        self._apply_styles()

        # ✅ Confetti only for Information
        self._create_particles()

        # Start animations
        self._start_effects()

    # ------------------------------
    # Icon emoji
    # ------------------------------
    def _get_icon_emoji(self) -> str:
        if self._icon_type == QMessageBox.Critical:
            return "💥"
        if self._icon_type == QMessageBox.Warning:
            return "⚠️"
        if self._icon_type == QMessageBox.Question:
            return "❓"
        return "🎉"

    # ------------------------------
    # Particles
    # ------------------------------
    def _create_particles(self):
        """Create confetti/glitch particles once (no random inside paint)."""
        self._particles.clear()

        # ✅ Confetti only for Information
        if self._icon_type == QMessageBox.Information:
            for _ in range(40):
                self._particles.append({
                    "x": random.randint(0, self.width()),
                    "y": random.randint(-150, -20),
                    "speed": random.uniform(2.2, 6.0),
                    "size": random.randint(4, 10),
                    "color": QColor(
                        random.randint(200, 255),
                        random.randint(150, 255),
                        random.randint(120, 255),
                        205
                    ),
                    "rotation": random.uniform(0, 360),
                    "rot_speed": random.uniform(-3.0, 3.0),
                    "shape": random.choice(["rect", "circle"]),  # ✅ no flicker
                })

        elif self._icon_type == QMessageBox.Critical:
            for _ in range(16):
                self._particles.append({
                    "x": random.randint(0, self.width()),
                    "y": random.randint(0, self.height()),
                    "offset_x": random.randint(-10, 10),
                    "offset_y": random.randint(-5, 5),
                    "alpha": 255,
                    "life": 100
                })

    # ------------------------------
    # Effects
    # ------------------------------
    def _start_effects(self):
        """Start animations based on icon type."""
        if self._icon_type == QMessageBox.Information:
            # Ribbon rotation
            self._ribbon_anim = QPropertyAnimation(self, b"ribbon_angle")
            self._ribbon_anim.setDuration(2600)
            self._ribbon_anim.setStartValue(0.0)
            self._ribbon_anim.setEndValue(360.0)
            self._ribbon_anim.setLoopCount(-1)
            self._ribbon_anim.start()

            # Confetti timer
            self._confetti_timer = QTimer(self)
            self._confetti_timer.timeout.connect(self._update_confetti)
            self._confetti_timer.start(30)

            QTimer.singleShot(0, self._animate_in)

        elif self._icon_type in (QMessageBox.Warning, QMessageBox.Question):
            # ✅ Alerts: only entrance animation (no confetti)
            QTimer.singleShot(0, self._animate_in)

        elif self._icon_type == QMessageBox.Critical:
            # Glitch timer
            self._glitch_timer = QTimer(self)
            self._glitch_timer.timeout.connect(self._update_glitch)
            self._glitch_timer.start(80)

            QTimer.singleShot(0, self._animate_in)
            QTimer.singleShot(70, self._start_shake)

        else:
            QTimer.singleShot(0, self._animate_in)

    def _animate_in(self):
        if self._start_pos is None:
            self._center_on_parent()
            self._start_pos = self.pos()

        start = QPoint(self._start_pos.x(), self._start_pos.y() - 14)
        end = self._start_pos

        self.move(start)
        self.setWindowOpacity(0.0)

        self._entrance_op = QPropertyAnimation(self, b"windowOpacity")
        self._entrance_op.setDuration(220)
        self._entrance_op.setStartValue(0.0)
        self._entrance_op.setEndValue(1.0)
        self._entrance_op.setEasingCurve(QEasingCurve.OutCubic)

        self._entrance_pos = QPropertyAnimation(self, b"pos")
        self._entrance_pos.setDuration(260)
        self._entrance_pos.setStartValue(start)
        self._entrance_pos.setEndValue(end)
        self._entrance_pos.setEasingCurve(QEasingCurve.OutBack)

        self._entrance_op.start()
        self._entrance_pos.start()

    def _start_shake(self):
        start_pos = self.pos()
        self._shake_anim = QPropertyAnimation(self, b"pos")
        self._shake_anim.setDuration(380)
        self._shake_anim.setLoopCount(2)
        self._shake_anim.setEasingCurve(QEasingCurve.OutQuad)

        self._shake_anim.setKeyValueAt(0.0, start_pos)
        self._shake_anim.setKeyValueAt(0.25, QPoint(start_pos.x() - 10, start_pos.y()))
        self._shake_anim.setKeyValueAt(0.5, QPoint(start_pos.x() + 10, start_pos.y()))
        self._shake_anim.setKeyValueAt(0.75, QPoint(start_pos.x() - 6, start_pos.y()))
        self._shake_anim.setKeyValueAt(1.0, start_pos)
        self._shake_anim.start()

    def _update_confetti(self):
        for p in self._particles:
            p["y"] += p["speed"]
            p["rotation"] = (p["rotation"] + p["rot_speed"]) % 360.0
            if p["y"] > self.height() + 90:
                p["y"] = random.randint(-150, -20)
                p["x"] = random.randint(0, self.width())
                p["speed"] = random.uniform(2.2, 6.0)
        self.update()

    def _update_glitch(self):
        self._glitch_offset = random.randint(-6, 6)
        self.update()
        QTimer.singleShot(50, lambda: setattr(self, "_glitch_offset", 0))

    # Ribbon property for animation
    def _get_ribbon_angle(self):
        return self._ribbon_angle

    def _set_ribbon_angle(self, angle):
        self._ribbon_angle = angle
        self.update()

    ribbon_angle = Property(float, _get_ribbon_angle, _set_ribbon_angle)

    # ------------------------------
    # Painting
    # ------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Dim background
        painter.fillRect(self.rect(), QColor(0, 0, 0, 70))

        # ✅ Only success/info has celebration effects
        if self._icon_type == QMessageBox.Information:
            self._draw_ribbons(painter)
            self._draw_confetti(painter)

        # Optional glitch shift
        if self._glitch_offset != 0:
            painter.save()
            painter.translate(self._glitch_offset, 0)

        # Glass card paint
        card_rect = self.card.geometry()
        self._paint_glass_card(painter, card_rect)

        if self._glitch_offset != 0:
            painter.restore()

        painter.end()
        super().paintEvent(event)

    def _paint_glass_card(self, painter: QPainter, card_rect: QRect):
        is_light = (self._theme == "light")
        grad = QLinearGradient(card_rect.topLeft(), card_rect.bottomRight())

        if is_light:
            grad.setColorAt(0, QColor(255, 255, 255, 195))
            grad.setColorAt(1, QColor(240, 245, 255, 210))
            border_color = QColor(60, 120, 255, 80)
            glow_color = QColor(100, 150, 255, 30)
            top_highlight = QColor(255, 255, 255, 120)
        else:
            grad.setColorAt(0, QColor(25, 28, 40, 175))
            grad.setColorAt(1, QColor(16, 18, 28, 200))
            border_color = QColor(110, 170, 255, 90)
            glow_color = QColor(80, 140, 255, 28)
            top_highlight = QColor(255, 255, 255, 35)

        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(border_color, 2))
        painter.drawRoundedRect(card_rect, 22, 22)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(glow_color))
        painter.drawRoundedRect(card_rect.adjusted(5, 5, -5, -5), 16, 16)

        painter.setPen(QPen(top_highlight, 1))
        painter.drawLine(
            card_rect.left() + 18, card_rect.top() + 6,
            card_rect.right() - 18, card_rect.top() + 6
        )

    def _draw_ribbons(self, painter: QPainter):
        center_x = self.width() // 2
        center_y = 26

        painter.save()
        painter.translate(center_x, center_y)

        ribbon_colors = [
            QColor(255, 215, 0, 170),
            QColor(255, 100, 100, 170),
            QColor(100, 200, 255, 170),
            QColor(255, 150, 255, 170),
        ]

        for i, color in enumerate(ribbon_colors):
            angle = self._ribbon_angle + (i * 90)
            painter.save()
            painter.rotate(angle)

            path = QPainterPath()
            path.moveTo(0, 0)
            for t in range(0, 121, 10):
                x = t * 2
                y = 34 * math.sin(math.radians(t * 2 + angle))
                path.lineTo(x, y)

            painter.setPen(QPen(color, 9, Qt.SolidLine, Qt.RoundCap))
            painter.drawPath(path)
            painter.restore()

        painter.restore()

    def _draw_confetti(self, painter: QPainter):
        for p in self._particles:
            painter.save()
            painter.translate(p["x"], p["y"])
            painter.rotate(p["rotation"])

            painter.setBrush(QBrush(p["color"]))
            painter.setPen(Qt.NoPen)

            s = p["size"]
            if p["shape"] == "rect":
                painter.drawRect(-s // 2, -s // 2, s, max(2, s // 2))
            else:
                painter.drawEllipse(-s // 2, -s // 2, s, s)

            painter.restore()

    # ------------------------------
    # Styles / positioning
    # ------------------------------
    def _apply_styles(self):
        if self._theme == "light":
            self.setStyleSheet("""
                QLabel { background: transparent; color: rgba(15, 23, 42, 235); }
                QPushButton {
                    background: rgba(255, 255, 255, 210);
                    border: 1px solid rgba(70, 130, 255, 70);
                    border-radius: 12px;
                    padding: 8px 18px;
                    font-weight: 800;
                    color: rgba(15, 23, 42, 235);
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 235);
                    border: 1px solid rgba(70, 130, 255, 130);
                }
                QPushButton:pressed { background: rgba(240, 240, 255, 240); }
            """)
        else:
            self.setStyleSheet("""
                QLabel { background: transparent; color: rgba(226, 232, 240, 235); }
                QPushButton {
                    background: rgba(40, 40, 50, 180);
                    border: 1px solid rgba(100, 150, 255, 80);
                    border-radius: 12px;
                    padding: 8px 18px;
                    font-weight: 800;
                    color: rgba(226, 232, 240, 235);
                }
                QPushButton:hover {
                    background: rgba(60, 60, 80, 200);
                    border: 1px solid rgba(120, 180, 255, 150);
                }
                QPushButton:pressed { background: rgba(80, 80, 120, 220); }
            """)

    def showEvent(self, event):
        super().showEvent(event)
        self._center_on_parent()

    def _center_on_parent(self):
        if not self.parent():
            return
        parent_geo = self.parent().geometry()
        self.move(
            parent_geo.center().x() - self.width() // 2,
            parent_geo.center().y() - self.height() // 2
        )

    # ------------------------------
    # Close / click
    # ------------------------------
    def _stop_effects(self):
        for name in ("_ribbon_anim", "_confetti_timer", "_glitch_timer", "_shake_anim",
                     "_entrance_op", "_entrance_pos", "_exit_anim"):
            obj = getattr(self, name, None)
            if obj is None:
                continue
            try:
                obj.stop()
            except Exception:
                pass

    def _on_clicked(self, btn):
        self._clicked = btn
        self._stop_effects()

        self._exit_anim = QPropertyAnimation(self, b"windowOpacity")
        self._exit_anim.setDuration(170)
        self._exit_anim.setStartValue(self.windowOpacity())
        self._exit_anim.setEndValue(0.0)
        self._exit_anim.setEasingCurve(QEasingCurve.InCubic)
        self._exit_anim.finished.connect(self.accept)
        self._exit_anim.start()

    def reject(self):
        self._clicked = QMessageBox.Cancel
        self._stop_effects()
        super().reject()

    def clicked_button(self):
        return self._clicked

    @staticmethod
    def _expand_buttons(buttons):
        order = [QMessageBox.Ok, QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel, QMessageBox.Close]
        return [b for b in order if buttons & b] or [QMessageBox.Ok]

    @staticmethod
    def _std_btn_text(b):
        return {
            QMessageBox.Ok: "OK",
            QMessageBox.Yes: "Yes",
            QMessageBox.No: "No",
            QMessageBox.Cancel: "Cancel",
            QMessageBox.Close: "Close",
        }.get(b, "OK")


def show_glass_message(parent, title, text, icon=QMessageBox.Information, buttons=QMessageBox.Ok):
    """
    Helper wrapper.
    - Reads theme from parent.state.theme if available
    - Returns clicked QMessageBox.StandardButton
    """
    theme = "dark"
    if hasattr(parent, "state") and getattr(parent.state, "theme", None):
        theme = parent.state.theme

    dlg = RibbonMessageBox(
        parent=parent,
        title=title,
        text=text,
        icon=icon,
        buttons=buttons,
        theme=theme,
    )
    dlg.exec()
    return dlg.clicked_button()


__all__ = ["RibbonMessageBox", "show_glass_message"]
