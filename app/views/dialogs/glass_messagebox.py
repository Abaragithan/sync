from __future__ import annotations

from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QTimer, QPoint, Property
)
from PySide6.QtWidgets import (
    QDialog, QLabel, QPushButton, QHBoxLayout, QVBoxLayout,
    QMessageBox, QWidget, QApplication, QFrame, QMainWindow,
    QGraphicsDropShadowEffect
)
from PySide6.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush, QPainterPath
)


# ──────────────────────────────────────────────────────────────
#  Dim overlay
# ──────────────────────────────────────────────────────────────
class _DimOverlay(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self._alpha = 0
        self.setGeometry(parent.rect())
        self.raise_()
        self.show()

        self._anim = QPropertyAnimation(self, b"dim_alpha")
        self._anim.setDuration(180)
        self._anim.setStartValue(0)
        self._anim.setEndValue(160)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.start()

    def _get_alpha(self): return self._alpha
    def _set_alpha(self, v):
        self._alpha = v
        self.update()
    dim_alpha = Property(int, _get_alpha, _set_alpha)

    def fade_out(self, done_cb=None):
        self._anim2 = QPropertyAnimation(self, b"dim_alpha")
        self._anim2.setDuration(150)
        self._anim2.setStartValue(self._alpha)
        self._anim2.setEndValue(0)
        self._anim2.setEasingCurve(QEasingCurve.InCubic)
        if done_cb:
            self._anim2.finished.connect(done_cb)
        self._anim2.start()

    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(0, 0, 0, self._alpha))
        p.end()


# ──────────────────────────────────────────────────────────────
#  Light GTK-style Dialog
# ──────────────────────────────────────────────────────────────
class RibbonMessageBox(QDialog):
    """
    Light-theme GTK/Adwaita-style message dialog.
    Clean rounded corners, no decorative bars, fits light desktop UIs.
    """

    _TYPE_CFG = {
        QMessageBox.Information: {
            "icon":      "ℹ",
            "icon_fg":   QColor(255, 255, 255),
            "icon_bg":   QColor(53,  132, 228),
            "btn":       QColor(53,  132, 228),
            "btn_hover": QColor(36,  110, 200),
        },
        QMessageBox.Warning: {
            "icon":      "⚠",
            "icon_fg":   QColor(255, 255, 255),
            "icon_bg":   QColor(198, 128,   0),
            "btn":       QColor(198, 128,   0),
            "btn_hover": QColor(160, 100,   0),
        },
        QMessageBox.Question: {
            "icon":      "?",
            "icon_fg":   QColor(255, 255, 255),
            "icon_bg":   QColor(53,  132, 228),
            "btn":       QColor(53,  132, 228),
            "btn_hover": QColor(36,  110, 200),
        },
        QMessageBox.Critical: {
            "icon":      "✕",
            "icon_fg":   QColor(255, 255, 255),
            "icon_bg":   QColor(192,  28,  40),
            "btn":       QColor(192,  28,  40),
            "btn_hover": QColor(155,  20,  30),
        },
    }

    def __init__(
        self,
        parent: QWidget,
        title: str,
        text: str,
        icon: QMessageBox.Icon = QMessageBox.Information,
        buttons: QMessageBox.StandardButtons = QMessageBox.Ok,
    ):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self.resize(400, 170)

        self._icon_type  = icon
        self._clicked    = QMessageBox.NoButton
        self._cfg        = self._TYPE_CFG.get(icon, self._TYPE_CFG[QMessageBox.Information])
        self._start_pos: QPoint | None = None
        self.setWindowOpacity(0.0)

        # Dim overlay
        self._overlay: _DimOverlay | None = None
        if parent:
            self._overlay = _DimOverlay(parent)

        # Drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)

        # ── Root layout ───────────────────────────
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Content area
        content = QHBoxLayout()
        content.setContentsMargins(22, 22, 22, 14)
        content.setSpacing(14)
        content.setAlignment(Qt.AlignTop)

        # Icon circle
        self._icon_lbl = QLabel(self._cfg["icon"])
        self._icon_lbl.setFixedSize(40, 40)
        self._icon_lbl.setAlignment(Qt.AlignCenter)
        self._icon_lbl.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self._icon_lbl.setObjectName("IconCircle")
        content.addWidget(self._icon_lbl, 0, Qt.AlignTop)

        # Text block
        txt_block = QVBoxLayout()
        txt_block.setSpacing(4)

        self._title_lbl = QLabel(title)
        self._title_lbl.setWordWrap(True)
        self._title_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self._title_lbl.setObjectName("TitleLbl")

        self._body_lbl = QLabel(text)
        self._body_lbl.setWordWrap(True)
        self._body_lbl.setFont(QFont("Segoe UI", 10))
        self._body_lbl.setObjectName("BodyLbl")

        txt_block.addWidget(self._title_lbl)
        txt_block.addWidget(self._body_lbl)
        content.addLayout(txt_block, 1)
        root.addLayout(content)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("Separator")
        root.addWidget(sep)

        # Button row
        btn_area = QHBoxLayout()
        btn_area.setContentsMargins(14, 10, 14, 14)
        btn_area.setSpacing(8)
        btn_area.addStretch()

        self._btn_widgets: list[QPushButton] = []
        for i, std_btn in enumerate(self._expand_buttons(buttons)):
            btn = QPushButton(self._std_btn_text(std_btn))
            btn.setFixedHeight(32)
            btn.setMinimumWidth(86)
            btn.setFont(QFont("Segoe UI", 10))
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, b=std_btn: self._on_clicked(b))
            btn.setProperty("primary", i == 0)
            btn_area.addWidget(btn)
            self._btn_widgets.append(btn)

        root.addLayout(btn_area)

        self._apply_styles()
        QTimer.singleShot(0, self._animate_in)

        if icon == QMessageBox.Critical:
            QTimer.singleShot(120, self._start_shake)

    # ─────────────────────────────────────────
    #  Paint — light surface, rounded, NO top bar
    # ─────────────────────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        r = self.rect()

        # White card background
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(252, 252, 252)))
        painter.drawRoundedRect(r, 12, 12)

        # Thin light border
        painter.setPen(QPen(QColor(0, 0, 0, 28), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(r.adjusted(1, 1, -1, -1), 11, 11)

        painter.end()
        super().paintEvent(event)

    # ─────────────────────────────────────────
    #  Styles
    # ─────────────────────────────────────────
    def _apply_styles(self):
        cfg     = self._cfg
        ic_bg   = cfg["icon_bg"]
        ic_fg   = cfg["icon_fg"]
        btn_c   = cfg["btn"]
        btn_h   = cfg["btn_hover"]

        def rgb(c: QColor): return f"rgb({c.red()},{c.green()},{c.blue()})"

        self.setStyleSheet(f"""
            RibbonMessageBox {{
                background: transparent;
            }}

            QLabel#IconCircle {{
                background: {rgb(ic_bg)};
                color: {rgb(ic_fg)};
                border-radius: 20px;
                font-weight: 700;
            }}

            QLabel#TitleLbl {{
                color: #1a1a1a;
                background: transparent;
                font-weight: 700;
            }}

            QLabel#BodyLbl {{
                color: #555555;
                background: transparent;
            }}

            QFrame#Separator {{
                background: #e0e0e0;
                border: none;
                max-height: 1px;
                min-height: 1px;
            }}

            QPushButton {{
                background: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 4px 14px;
                color: #2a2a2a;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: #e4e4e4;
                border-color: #b8b8b8;
            }}
            QPushButton:pressed {{
                background: #d8d8d8;
            }}

            QPushButton[primary="true"] {{
                background: {rgb(btn_c)};
                border: 1px solid {rgb(btn_c)};
                border-radius: 6px;
                color: white;
                font-weight: 600;
            }}
            QPushButton[primary="true"]:hover {{
                background: {rgb(btn_h)};
                border-color: {rgb(btn_h)};
            }}
            QPushButton[primary="true"]:pressed {{
                background: {rgb(btn_h)};
            }}
        """)

    # ─────────────────────────────────────────
    #  Animations
    # ─────────────────────────────────────────
    def _animate_in(self):
        if self._start_pos is None:
            self._center_on_parent()
            self._start_pos = self.pos()

        start = QPoint(self._start_pos.x(), self._start_pos.y() - 10)
        self.move(start)
        self.setWindowOpacity(0.0)

        self._op_anim = QPropertyAnimation(self, b"windowOpacity")
        self._op_anim.setDuration(180)
        self._op_anim.setStartValue(0.0)
        self._op_anim.setEndValue(1.0)
        self._op_anim.setEasingCurve(QEasingCurve.OutCubic)

        self._pos_anim = QPropertyAnimation(self, b"pos")
        self._pos_anim.setDuration(200)
        self._pos_anim.setStartValue(start)
        self._pos_anim.setEndValue(self._start_pos)
        self._pos_anim.setEasingCurve(QEasingCurve.OutCubic)

        self._op_anim.start()
        self._pos_anim.start()

    def _start_shake(self):
        sp = self.pos()
        self._shake = QPropertyAnimation(self, b"pos")
        self._shake.setDuration(300)
        self._shake.setKeyValueAt(0.00, sp)
        self._shake.setKeyValueAt(0.15, QPoint(sp.x() - 8, sp.y()))
        self._shake.setKeyValueAt(0.35, QPoint(sp.x() + 8, sp.y()))
        self._shake.setKeyValueAt(0.55, QPoint(sp.x() - 5, sp.y()))
        self._shake.setKeyValueAt(0.75, QPoint(sp.x() + 3, sp.y()))
        self._shake.setKeyValueAt(1.00, sp)
        self._shake.start()

    # ─────────────────────────────────────────
    #  Positioning / dismiss
    # ─────────────────────────────────────────
    def showEvent(self, event):
        super().showEvent(event)
        self._center_on_parent()
        if self._overlay and self.parent():
            self._overlay.setGeometry(self.parent().rect())
            self._overlay.raise_()
            self.raise_()

    def _center_on_parent(self):
        if not self.parent():
            return
        pg = self.parent().geometry()
        self.move(
            pg.x() + pg.width()  // 2 - self.width()  // 2,
            pg.y() + pg.height() // 2 - self.height() // 2,
        )

    def _stop_effects(self):
        for name in ("_op_anim", "_pos_anim", "_shake", "_exit_anim"):
            obj = getattr(self, name, None)
            if obj:
                try: obj.stop()
                except Exception: pass

    def _dismiss(self):
        self._stop_effects()
        self._exit_anim = QPropertyAnimation(self, b"windowOpacity")
        self._exit_anim.setDuration(130)
        self._exit_anim.setStartValue(self.windowOpacity())
        self._exit_anim.setEndValue(0.0)
        self._exit_anim.setEasingCurve(QEasingCurve.InCubic)

        def _finish():
            if self._overlay:
                self._overlay.fade_out(done_cb=lambda: (
                    self._overlay.deleteLater(),
                    self.accept()
                ))
            else:
                self.accept()

        self._exit_anim.finished.connect(_finish)
        self._exit_anim.start()

    def _on_clicked(self, btn):
        self._clicked = btn
        self._dismiss()

    def reject(self):
        self._clicked = QMessageBox.Cancel
        self._stop_effects()
        if self._overlay:
            self._overlay.fade_out(done_cb=lambda: (
                self._overlay.deleteLater(),
                super(RibbonMessageBox, self).reject()
            ))
        else:
            super().reject()

    def clicked_button(self):
        return self._clicked

    @staticmethod
    def _expand_buttons(buttons):
        order = [
            QMessageBox.Ok, QMessageBox.Yes, QMessageBox.No,
            QMessageBox.Cancel, QMessageBox.Close
        ]
        return [b for b in order if buttons & b] or [QMessageBox.Ok]

    @staticmethod
    def _std_btn_text(b):
        return {
            QMessageBox.Ok:     "OK",
            QMessageBox.Yes:    "Yes",
            QMessageBox.No:     "No",
            QMessageBox.Cancel: "Cancel",
            QMessageBox.Close:  "Close",
        }.get(b, "OK")


# ──────────────────────────────────────────────────────────────
#  Public helper
# ──────────────────────────────────────────────────────────────
def show_glass_message(
    parent,
    title: str,
    text: str,
    icon=QMessageBox.Information,
    buttons=QMessageBox.Ok,
) -> QMessageBox.StandardButton:
    """
    Show a light-theme native-style dialog with dimmed backdrop.
    Returns the clicked QMessageBox.StandardButton.

    Examples:
        show_glass_message(self, "Lab Created",
                           "Lab 'CUL' was created with 42 workstations.")

        show_glass_message(self, "Low Disk Space",
                           "Less than 2 GB free on the server.",
                           icon=QMessageBox.Warning)

        result = show_glass_message(
            self, "Delete Lab?",
            "All workstation configs will be permanently removed.",
            icon=QMessageBox.Question,
            buttons=QMessageBox.Yes | QMessageBox.No,
        )
        if result == QMessageBox.Yes:
            self.delete_lab()

        show_glass_message(self, "Sync Failed",
                           "Cannot reach the Ansible controller.",
                           icon=QMessageBox.Critical)
    """
    dlg = RibbonMessageBox(
        parent=parent, title=title, text=text, icon=icon, buttons=buttons
    )
    dlg.exec()
    return dlg.clicked_button()


__all__ = ["RibbonMessageBox", "show_glass_message"]


# ──────────────────────────────────────────────────────────────
#  Demo
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    win = QMainWindow()
    win.setWindowTitle("SYNC Lab Manager — Dialog Demo")
    win.resize(960, 620)

    central = QWidget()
    win.setCentralWidget(central)
    layout = QVBoxLayout(central)
    layout.setAlignment(Qt.AlignCenter)
    layout.setSpacing(10)
    central.setStyleSheet("background: #f0f2f5;")   # light app bg

    scenarios = [
        (
            "ℹ  Information",
            "Lab Created",
            "Lab 'CUL' has been created with 42 workstations\nand IP range 10.10.20.1 – 10.10.20.42.",
            QMessageBox.Information,
            QMessageBox.Ok,
        ),
        (
            "⚠  Warning",
            "Low Disk Space",
            "The server has less than 2 GB of free disk space.\nConsider removing old snapshots.",
            QMessageBox.Warning,
            QMessageBox.Ok | QMessageBox.Cancel,
        ),
        (
            "?  Question",
            "Delete Lab 'CSL 1 & 2'?",
            "All 99 workstation configurations will be permanently\nremoved. This action cannot be undone.",
            QMessageBox.Question,
            QMessageBox.Yes | QMessageBox.No,
        ),
        (
            "✕  Critical",
            "Sync Failed",
            "Unable to reach the remote Ansible controller.\nCheck your network connection and try again.",
            QMessageBox.Critical,
            QMessageBox.Close,
        ),
    ]

    for label, title, text, icon, btns in scenarios:
        btn = QPushButton(label)
        btn.setFixedSize(220, 36)
        btn.setFont(QFont("Segoe UI", 10))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #d0d4da;
                border-radius: 7px;
                color: #333;
            }
            QPushButton:hover {
                background: #f5f5f5;
                border-color: #b0b4ba;
            }
        """)
        btn.clicked.connect(
            lambda _, t=title, tx=text, ic=icon, b=btns:
                show_glass_message(win, t, tx, ic, b)
        )
        layout.addWidget(btn)

    win.show()
    sys.exit(app.exec())