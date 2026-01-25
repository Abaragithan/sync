from PySide6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QSizePolicy
from PySide6.QtCore import Qt

from core.inventory_manager import InventoryManager
from .dashboard_widget import DashboardWidget
from .software_widget import SoftwareWidget
from .client_widget import ClientWidget
from .reports_widget import ReportsWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gemini Central Deployer v2.0")
        self.setMinimumSize(1000, 700)  # Set minimum size
        
        # Center on screen with initial size
        screen_geometry = self.screen().availableGeometry()
        initial_width = min(1200, screen_geometry.width() - 100)
        initial_height = min(800, screen_geometry.height() - 100)
        self.resize(initial_width, initial_height)
        
        self.inventory_manager = InventoryManager()

        # Create tab widget with size policy
        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #333;
                background-color: #1a1a1a;
            }
            QTabBar::tab {
                background-color: #2a2a2a;
                color: #aaa;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #1a1a1a;
                color: white;
                border-bottom: 2px solid #007acc;
            }
            QTabBar::tab:hover {
                background-color: #333;
            }
        """)

        # Create widgets
        self.dashboard = DashboardWidget(self.inventory_manager)
        self.software = SoftwareWidget(self.inventory_manager)
        self.client = ClientWidget(self.inventory_manager)
        self.reports = ReportsWidget(self.inventory_manager)

        # Add tabs
        self.tabs.addTab(self.dashboard, "📊 Dashboard")
        self.tabs.addTab(self.software, "📦 Software")
        self.tabs.addTab(self.client, "💻 Client")
        self.tabs.addTab(self.reports, "📋 Reports")

        # Connect signals
        self.client.deployment_requested.connect(self.software.handle_deployment)
        self.client.targets_updated.connect(
            lambda targets, action: self.software.update_targets_display(targets, action)
        )
        self.dashboard.quick_deploy_requested.connect(self.handle_quick_deploy)

        # Set central widget
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tabs)
        self.setCentralWidget(central_widget)

    def handle_quick_deploy(self, lab: str):
        """Handle quick deploy from dashboard"""
        self.tabs.setCurrentIndex(2)  # Switch to Client tab
        self.client.select_all_pcs_for_lab(lab)