# views/operation_status_page.py
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QPalette

from .widgets.pc_card import PcCard


class OperationStatusPage(QWidget):
    back_to_software = Signal()

    def __init__(self, inventory_manager, state):
        super().__init__()
        self.inventory_manager = inventory_manager
        self.state = state
        self._results: dict[str, bool] = {}
        self._build_ui()

    # =========================================================================
    # UI construction
    # =========================================================================
    def _build_ui(self):
        # Same background pattern as SoftwarePage
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#f8fafc"))
        self.setPalette(palette)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        # ── Header ────────────────────────────────────────────────────────
        header = QHBoxLayout()

        self.back_btn = QPushButton("← Back")
        self.back_btn.setFixedSize(90, 38)
        self.back_btn.setObjectName("BackBtn")   # global QSS handles style
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.clicked.connect(self.back_to_software.emit)
        header.addWidget(self.back_btn)

        title_col = QVBoxLayout()
        title_col.setSpacing(4)
        title_lbl = QLabel("Operation Results")
        title_lbl.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title_lbl.setStyleSheet("color: #0f172a; background: transparent;")
        self._sub_lbl = QLabel("Showing results for last execution")
        self._sub_lbl.setStyleSheet("color: #64748b; font-size: 13px; background: transparent;")
        title_col.addWidget(title_lbl)
        title_col.addWidget(self._sub_lbl)
        header.addLayout(title_col, 1)

        root.addLayout(header)

        # ── Legend ────────────────────────────────────────────────────────
        legend = QHBoxLayout()
        legend.setSpacing(20)
        legend.addStretch()
        for color, text in [("#22c55e", "Success"), ("#ef4444", "Failed"), ("#9F9F9F", "Not targeted")]:
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 16px; background: transparent;")
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
            legend.addWidget(dot)
            legend.addWidget(lbl)
        legend.addStretch()
        root.addLayout(legend)

        # ── Scroll area with PC grid ──────────────────────────────────────
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { background: #f1f5f9; width: 8px; border-radius: 4px; }
            QScrollBar::handle:vertical { background: #cbd5e1; border-radius: 4px; min-height: 30px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        self._wrap = QWidget()
        self._wrap.setStyleSheet("background: transparent;")
        self._wrap_layout = QHBoxLayout(self._wrap)
        self._wrap_layout.setSpacing(16)
        self._wrap_layout.setContentsMargins(0, 0, 0, 0)
        self._wrap_layout.setAlignment(Qt.AlignHCenter)

        self._scroll.setWidget(self._wrap)
        root.addWidget(self._scroll, 1)

        # ── Summary footer ────────────────────────────────────────────────
        self._footer = QFrame()
        self._footer.setStyleSheet("""
            QFrame {
                background: #ffffff; border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        footer_layout = QHBoxLayout(self._footer)
        footer_layout.setContentsMargins(20, 12, 20, 12)

        self._success_lbl = QLabel("✓  0 succeeded")
        self._success_lbl.setStyleSheet("color: #15803d; font-size: 14px; font-weight: 700; background: transparent;")
        self._failed_lbl  = QLabel("✗  0 failed")
        self._failed_lbl.setStyleSheet("color: #dc2626; font-size: 14px; font-weight: 700; background: transparent;")
        self._skipped_lbl = QLabel("—  0 not targeted")
        self._skipped_lbl.setStyleSheet("color: #94a3b8; font-size: 14px; font-weight: 600; background: transparent;")

        footer_layout.addStretch()
        footer_layout.addWidget(self._success_lbl)
        footer_layout.addSpacing(32)
        footer_layout.addWidget(self._failed_lbl)
        footer_layout.addSpacing(32)
        footer_layout.addWidget(self._skipped_lbl)
        footer_layout.addStretch()

        root.addWidget(self._footer)

    # =========================================================================
    # Public API — called before showing this page
    # =========================================================================
    def load_results(self, results: dict[str, bool]):
        """
        results: { ip: True/False }  True = success, False = failed
        All other PCs in the lab are shown in normal grey.
        """
        self._results = results
        self._render()

    # =========================================================================
    # Rendering
    # =========================================================================
    def _render(self):
        # Clear existing widgets
        while self._wrap_layout.count():
            item = self._wrap_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        lab = self.state.current_lab
        if not lab:
            return

        layout   = self.inventory_manager.get_lab_layout(lab)
        all_pcs  = self.inventory_manager.get_pcs_for_lab(lab)
        targeted = set(self._results.keys())

        if not layout or not all_pcs:
            return

        n_success = sum(1 for v in self._results.values() if v)
        n_failed  = sum(1 for v in self._results.values() if not v)
        n_skipped = len(all_pcs) - len(targeted)

        self._success_lbl.setText(f"✓  {n_success} succeeded")
        self._failed_lbl.setText(f"✗  {n_failed} failed")
        self._skipped_lbl.setText(f"—  {n_skipped} not targeted")

        action  = self.state.action.upper()
        os_name = self.state.target_os.upper()
        self._sub_lbl.setText(
            f"{action} / {os_name}  ·  "
            f"{len(targeted)} targeted  ·  Lab: {lab}"
        )

        self._wrap_layout.addStretch(1)

        # Build section frames matching lab layout
        for s in range(layout["sections"]):
            frame = QFrame()
            frame.setStyleSheet("""
                QFrame {
                    background: #ffffff;
                    border: 1px solid #e2e8f0;
                    border-radius: 12px;
                }
            """)
            v = QVBoxLayout(frame)
            v.setContentsMargins(10, 10, 10, 10)
            v.setSpacing(12)
            v.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

            sec_lbl = QLabel(f"Section {s + 1}")
            sec_lbl.setStyleSheet(
                "color: #0f172a; font-size: 16px; font-weight: 700;"
                " padding: 8px 0px; background: transparent;"
            )
            v.addWidget(sec_lbl)

            grid = QGridLayout()
            grid.setHorizontalSpacing(5)
            grid.setVerticalSpacing(15)
            grid.setContentsMargins(12, 12, 12, 12)
            v.addLayout(grid)

            # Add PC cards for this section
            for pc in all_pcs:
                if pc["section"] != s + 1:
                    continue

                card = PcCard(pc["name"], pc["ip"])
                card.setFixedSize(60, 60)

                ip = pc["ip"]
                if ip in self._results:
                    if self._results[ip]:
                        card.set_status_online()   # green = success
                    else:
                        card.set_status_offline()  # red   = failed
                # else: stays normal grey = not targeted

                r = pc["row"] - 1
                c = pc["col"] - 1
                grid.addWidget(card, r, c, alignment=Qt.AlignCenter)

            self._wrap_layout.addWidget(frame)

        self._wrap_layout.addStretch(1)