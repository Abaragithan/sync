from PySide6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel, QHBoxLayout,
                               QPushButton, QFrame, QSizePolicy, QScrollArea, QSpacerItem)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QPalette, QColor, QLinearGradient
from typing import List

class DashboardWidget(QWidget):
    quick_deploy_requested = Signal(str)

    def __init__(self, inventory_manager):
        super().__init__()
        self.inventory_manager = inventory_manager
        self.labs = self.inventory_manager.get_all_labs()
        self.stat_values = {}
        self.lab_widgets = {}
        self.setup_ui()
        self.update_stats()

    def setup_ui(self):
        # Set black background for the entire widget
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create scroll area with black background
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #000000;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #1a1a1a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #3b82f6;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

        # Container widget with black background
        container = QWidget()
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        container.setStyleSheet("background-color: #000000;")
        scroll_area.setWidget(container)
        
        # Container layout
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setSpacing(30)

        # ========== HEADER SECTION ==========
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        header_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        
        # Main title
        title = QLabel("Dashboard Overview")
        title.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: transparent;
            }
        """)
        
        # Subtitle
        subtitle = QLabel("Monitor all computer labs at a glance")
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #94a3b8;
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: transparent;
            }
        """)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        container_layout.addWidget(header_frame)

        # ========== STATISTICS CARDS ==========
        stats_container = QFrame()
        stats_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        stats_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        stats_layout = QHBoxLayout(stats_container)
        stats_layout.setSpacing(20)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setAlignment(Qt.AlignLeft)

        # Stat cards
        stat_cards = [
            ("🏢", "Total Labs", "#3b82f6", "total_labs"),
            ("💻", "Total PCs", "#10b981", "total_pcs"),
            ("🪟", "Windows", "#0ea5e9", "windows"),
            ("🐧", "Linux", "#f59e0b", "linux")
        ]
        
        for icon, title_text, color, key in stat_cards:
            card = self.create_stat_card(icon, title_text, color, key)
            stats_layout.addWidget(card)
        
        stats_layout.addStretch()
        container_layout.addWidget(stats_container)

        # ========== LABS SECTION ==========
        labs_section = QFrame()
        labs_section.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        labs_section.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        labs_layout = QVBoxLayout(labs_section)
        labs_layout.setContentsMargins(0, 0, 0, 0)
        labs_layout.setSpacing(20)
        
        # Section header
        section_header = QHBoxLayout()
        section_header.setContentsMargins(0, 0, 0, 0)
        section_header.setSpacing(10)
        
        labs_title = QLabel("Computer Labs")
        labs_title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: transparent;
            }
        """)
        
        labs_count = QLabel(f"({len(self.labs)} labs)")
        labs_count.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #94a3b8;
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: transparent;
            }
        """)
        
        section_header.addWidget(labs_title)
        section_header.addWidget(labs_count)
        section_header.addStretch()
        labs_layout.addLayout(section_header)

        if self.labs:
            # Create grid for lab cards
            grid_widget = QWidget()
            grid_widget.setStyleSheet("background-color: transparent;")
            grid_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            
            grid_layout = QGridLayout(grid_widget)
            grid_layout.setSpacing(25)
            grid_layout.setContentsMargins(0, 0, 0, 0)
            grid_layout.setAlignment(Qt.AlignCenter)
            
            # Use 3 columns for better layout
            max_columns = 3
            
            for i, lab in enumerate(self.labs):
                row = i // max_columns
                col = i % max_columns
                
                card = self.create_lab_card(lab)
                grid_layout.addWidget(card, row, col)
            
            labs_layout.addWidget(grid_widget)
        else:
            # No labs message
            no_labs_frame = QFrame()
            no_labs_frame.setStyleSheet("""
                QFrame {
                    background-color: #0a0a0a;
                    border-radius: 12px;
                    border: 2px dashed #1a1a1a;
                }
            """)
            no_labs_frame.setFixedHeight(200)
            
            no_labs_layout = QVBoxLayout(no_labs_frame)
            no_labs_layout.setAlignment(Qt.AlignCenter)
            
            no_labs_icon = QLabel("🏢")
            no_labs_icon.setStyleSheet("font-size: 48px; background-color: transparent;")
            no_labs_icon.setAlignment(Qt.AlignCenter)
            
            no_labs_text = QLabel("No Labs Configured")
            no_labs_text.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    color: #94a3b8;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    margin-top: 10px;
                    background-color: transparent;
                }
            """)
            no_labs_text.setAlignment(Qt.AlignCenter)
            
            no_labs_hint = QLabel("Add labs through inventory management")
            no_labs_hint.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #64748b;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    background-color: transparent;
                }
            """)
            no_labs_hint.setAlignment(Qt.AlignCenter)
            
            no_labs_layout.addWidget(no_labs_icon)
            no_labs_layout.addWidget(no_labs_text)
            no_labs_layout.addWidget(no_labs_hint)
            labs_layout.addWidget(no_labs_frame)

        container_layout.addWidget(labs_section)
        container_layout.addStretch()
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)

    def create_stat_card(self, icon, title_text, color, key):
        """Create a beautiful stat card with black theme"""
        card = QFrame()
        # FIXED: Made stat cards larger so text doesn't get cut off
        card.setFixedSize(280, 150)  # WAS: 260, 140
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #0a0a0a;
                border-radius: 16px;
                border: none;
            }}
            QFrame:hover {{
                border: 2px solid {color};
                background-color: #0f0f0f;
            }}
        """)
        
        layout = QVBoxLayout(card)
        # FIXED: Increased top/bottom padding for better text fitting
        layout.setContentsMargins(25, 25, 25, 25)  # WAS: 25, 20, 25, 20
        layout.setSpacing(10)  # WAS: 15
        
        # Top row with icon and title
        top_row = QHBoxLayout()
        top_row.setSpacing(15)
        top_row.setContentsMargins(0, 0, 0, 0)
        
        # Icon with background
        icon_frame = QFrame()
        # FIXED: Made icon smaller to fit better
        icon_frame.setFixedSize(44, 44)  # WAS: 48, 48
        icon_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color}15;
                border-radius: 12px;
                border: 1px solid {color}30;
            }}
        """)
        icon_layout = QVBoxLayout(icon_frame)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 22px;  # WAS: 24px
                color: {color};
                background-color: transparent;
            }}
        """)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_label)
        
        title_label = QLabel(title_text)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;  # Good size
                color: #cbd5e1;
                font-weight: 500;
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: transparent;
            }
        """)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        top_row.addWidget(icon_frame)
        top_row.addWidget(title_label)
        top_row.addStretch()
        layout.addLayout(top_row)
        
        # Value
        value_label = QLabel("0")
        value_label.setObjectName(f"stat_{key}")
        value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 36px;  # WAS: 40px - Reduced to fit better
                font-weight: bold;
                color: {color};
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 0;
                margin: 0;
                background-color: transparent;
            }}
        """)
        value_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(value_label)
        layout.addStretch()
        
        # Store reference
        self.stat_values[key] = value_label
        
        return card

    def create_lab_card(self, lab_name):
        """Create a beautiful lab card with properly aligned text"""
        card = QFrame()
        # FIXED: Made lab cards larger to prevent text cutoff
        card.setFixedSize(400, 280)  # WAS: 380, 260 - Increased height more
        card.setStyleSheet("""
            QFrame {
                background-color: #0a0a0a;
                border-radius: 16px;
                border: none;
            }
            QFrame:hover {
                border: 2px solid #3b82f6;
                background-color: #0f0f0f;
            }
        """)
        
        layout = QVBoxLayout(card)
        # FIXED: Increased bottom margin for button space
        layout.setContentsMargins(20, 20, 20, 20)  # WAS: 25, 25, 25, 20
        layout.setSpacing(15)
        
        # Header
        header = QHBoxLayout()
        header.setSpacing(15)
        header.setContentsMargins(0, 0, 0, 0)
        
        # Lab icon with background
        icon_frame = QFrame()
        # FIXED: Made icon smaller to fit better
        icon_frame.setFixedSize(50, 50)  # WAS: 56, 56
        icon_frame.setStyleSheet("""
            QFrame {
                background-color: #3b82f615;
                border-radius: 14px;
                border: 1px solid #3b82f630;
            }
        """)
        icon_layout = QVBoxLayout(icon_frame)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        lab_icon = QLabel("🏢")
        lab_icon.setStyleSheet("""
            QLabel {
                font-size: 24px;  # WAS: 28px - Reduced
                color: #3b82f6;
                background-color: transparent;
            }
        """)
        lab_icon.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(lab_icon)
        
        # Lab name
        lab_title = QLabel(lab_name)
        lab_title.setStyleSheet("""
            QLabel {
                font-size: 20px;  # WAS: 22px - Reduced
                font-weight: bold;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: transparent;
                padding: 5px 0;
            }
        """)
        lab_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        header.addWidget(icon_frame)
        header.addWidget(lab_title)
        header.addStretch()
        layout.addLayout(header)
        
        # Stats section
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #050505;
                border-radius: 12px;
                border: nonea;
            }
        """)
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setContentsMargins(15, 15, 15, 15)
        stats_layout.setSpacing(12)  # WAS: 15
        
        # Total PCs
        total_layout = QHBoxLayout()
        total_layout.setSpacing(10)
        
        total_icon = QLabel("💻")
        total_icon.setStyleSheet("""
            QLabel {
                font-size: 18px;  # WAS: 20px - Reduced
                color: #ffffff;
                background-color: transparent;
            }
        """)
        
        total_label = QLabel("Total PCs:")
        total_label.setStyleSheet("""
            QLabel {
                font-size: 15px;  # WAS: 16px - Reduced
                color: #94a3b8;
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: transparent;
                font-weight: 500;
            }
        """)
        
        total_value = QLabel("0")
        total_value.setStyleSheet("""
            QLabel {
                font-size: 22px;  # WAS: 24px - Reduced
                font-weight: bold;
                color: #10b981;
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: transparent;
            }
        """)
        total_value.setAlignment(Qt.AlignRight)
        
        total_layout.addWidget(total_icon)
        total_layout.addWidget(total_label)
        total_layout.addStretch()
        total_layout.addWidget(total_value)
        stats_layout.addLayout(total_layout)
        
        # OS Distribution
        os_layout = QHBoxLayout()
        os_layout.setSpacing(25)  # WAS: 30 - Reduced
        
        # Windows section
        windows_section = QVBoxLayout()
        windows_section.setSpacing(5)
        
        windows_header = QHBoxLayout()
        windows_header.setSpacing(8)
        
        
        windows_icon = QLabel("🪟")
        windows_icon.setStyleSheet("""
            QLabel {
                font-size: 16px;  # WAS: 18px - Reduced
                color: #0ea5e9; 
                background-color: transparent;
            }
        """)
        
        windows_title = QLabel("Windows")
        windows_title.setStyleSheet("""
            QLabel {
                font-size: 13px;  # WAS: 14px - Reduced
                color: #94a3b8;
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: transparent;
                font-weight: 500;
            }
        """)
        
        windows_value = QLabel("0")
        windows_value.setStyleSheet("""
            QLabel {
                font-size: 18px;  # WAS: 20px - Reduced
                font-weight: bold;
                color: #0ea5e9;
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: transparent;
            }
        """)
        windows_value.setAlignment(Qt.AlignCenter)
        
        windows_header.addWidget(windows_icon)
        windows_header.addWidget(windows_title)
        windows_header.addStretch()
        
        windows_section.addLayout(windows_header)
        windows_section.addWidget(windows_value)
        
        # Linux section
        linux_section = QVBoxLayout()
        linux_section.setSpacing(5)
        
        linux_header = QHBoxLayout()
        linux_header.setSpacing(8)
        
        linux_icon = QLabel("🐧")
        linux_icon.setStyleSheet("""
            QLabel {
                font-size: 16px;  # WAS: 18px - Reduced
                color: #f59e0b; 
                background-color: transparent;
            }
        """)
        
        linux_title = QLabel("Linux")
        linux_title.setStyleSheet("""
            QLabel {
                font-size: 13px;  # WAS: 14px - Reduced
                color: #94a3b8;
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: transparent;
                font-weight: 500;
            }
        """)
        
        linux_value = QLabel("0")
        linux_value.setStyleSheet("""
            QLabel {
                font-size: 18px;  # WAS: 20px - Reduced
                font-weight: bold;
                color: #f59e0b;
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: transparent;
            }
        """)
        linux_value.setAlignment(Qt.AlignCenter)
        
        linux_header.addWidget(linux_icon)
        linux_header.addWidget(linux_title)
        linux_header.addStretch()
        
        linux_section.addLayout(linux_header)
        linux_section.addWidget(linux_value)
        
        os_layout.addLayout(windows_section)
        os_layout.addLayout(linux_section)
        stats_layout.addLayout(os_layout)
        
        layout.addWidget(stats_frame)
        
        # Quick Deploy Button - FIXED: Made button shorter to fit better
        deploy_btn = QPushButton("🚀 Quick Deploy All")
        deploy_btn.setFixedHeight(40)  # WAS: 44 - Reduced
        deploy_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #1d4ed8);
                border: none;
                border-radius: 10px;
                color: white;
                font-weight: 600;
                font-size: 14px;  # WAS: 15px - Reduced
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #1e40af);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1d4ed8, stop:1 #1e3a8a);
            }
        """)
        deploy_btn.clicked.connect(lambda: self.quick_deploy_requested.emit(lab_name))
        layout.addWidget(deploy_btn)
        
        # Store references
        self.lab_widgets[lab_name] = {
            'total': total_value,
            'windows': windows_value,
            'linux': linux_value,
            'card': card
        }
        
        return card

    def update_stats(self):
        """Update all dashboard statistics"""
        # Calculate totals
        total_labs = len(self.labs)
        total_pcs = sum(len(self.inventory_manager.get_pcs_for_lab(lab)) for lab in self.labs)
        windows_pcs = sum(len([pc for pc in self.inventory_manager.get_pcs_for_lab(lab) 
                              if pc["os"] == "windows"]) for lab in self.labs)
        linux_pcs = total_pcs - windows_pcs
        
        # Update stat cards
        if 'total_labs' in self.stat_values:
            self.stat_values['total_labs'].setText(str(total_labs))
        if 'total_pcs' in self.stat_values:
            self.stat_values['total_pcs'].setText(str(total_pcs))
        if 'windows' in self.stat_values:
            self.stat_values['windows'].setText(str(windows_pcs))
        if 'linux' in self.stat_values:
            self.stat_values['linux'].setText(str(linux_pcs))
        
        # Update lab cards
        for lab in self.labs:
            pcs = self.inventory_manager.get_pcs_for_lab(lab)
            total = len(pcs)
            windows_count = len([pc for pc in pcs if pc["os"] == "windows"])
            linux_count = total - windows_count
            
            if lab in self.lab_widgets:
                self.lab_widgets[lab]['total'].setText(str(total))
                self.lab_widgets[lab]['windows'].setText(str(windows_count))
                self.lab_widgets[lab]['linux'].setText(str(linux_count))