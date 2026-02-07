import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout

from core.inventory_manager import InventoryManager
from core.app_state import AppState
from ui.theme import get_qss

from views.welcome_page import WelcomePage
from views.lab_page import LabPage
from views.software_page import SoftwarePage
from views.lab_edit_page import LabEditPage
from views.dashboard_page import DashboardPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SYNC")
        self.setMinimumSize(1000, 700)

        self.inventory_manager = InventoryManager()
        self.state = AppState()
        self.state.load()

        # -------- Stack --------
        self.stack = QStackedWidget()

        # 1. Initialize All Pages
        self.welcome = WelcomePage()
        self.dashboard = DashboardPage(self.inventory_manager)
        self.lab = LabPage(self.inventory_manager, self.state)
        self.software = SoftwarePage(self.inventory_manager, self.state)
        self.lab_edit = LabEditPage(self.inventory_manager)

        # 2. Add to Stack (Order Matters!)
        self.stack.addWidget(self.welcome)   # Index 0
        self.stack.addWidget(self.dashboard) # Index 1
        self.stack.addWidget(self.lab)       # Index 2
        self.stack.addWidget(self.software)  # Index 3
        self.stack.addWidget(self.lab_edit)  # Index 4

        # -------- Navigation --------
        
        # Welcome (0) -> Dashboard (1)
        self.welcome.go_deployment.connect(lambda: self.stack.setCurrentIndex(1))

        # Dashboard (1) -> Welcome (0) (Back Button)
        self.dashboard.back_requested.connect(lambda: self.stack.setCurrentIndex(0))

        # Dashboard (1) -> Lab (2) via handler
        self.dashboard.lab_selected.connect(self._handle_lab_selection)

        # Lab (2) -> Dashboard (1) (Back Button)
        self.lab.back_requested.connect(lambda: self.stack.setCurrentIndex(1))

        # Dashboard (1) -> Lab Edit (4)
        self.dashboard.edit_lab_requested.connect(self._go_lab_edit)

        # Lab (2) -> Software (3)
        self.lab.next_to_software.connect(self._go_software)

        # Software (3) -> Lab (2)
        self.software.back_to_lab.connect(lambda: self.stack.setCurrentIndex(2))

        # Lab (2) <-> Lab Edit (4)
        self.lab.edit_lab_requested.connect(self._go_lab_edit)
        self.lab_edit.back_btn.clicked.connect(self._back_from_lab_edit)

        # Theme toggle (LabPage -> App stylesheet)
        self.lab.theme_toggled.connect(self._apply_theme)


        # -------- Central widget --------
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.stack)
        self.setCentralWidget(w)

    def _go_software(self):
        self.stack.setCurrentIndex(3)
        self.software.on_page_show()

    def _go_lab_edit(self, lab_name: str):
        print(f"[NAV] Edit lab requested: {lab_name}")
        self.lab_edit.load_lab(lab_name)
        self.stack.setCurrentIndex(4)

    def _back_from_lab_edit(self):
        # Force LabPage to refresh from inventory
        self.lab._render_lab()
        self.stack.setCurrentIndex(2)

    def _handle_lab_selection(self, lab_name: str):
        """
        Called when user clicks 'Open' on the Dashboard.
        """
        # Use the existing method _on_lab_changed to load data
        self.lab._on_lab_changed(lab_name)
        
        # Switch to Lab Page (Index 2)
        self.stack.setCurrentIndex(2)


    def _apply_theme(self, theme: str):
        theme = (theme or "dark").lower()
        self.state.theme = theme
        self.state.save()
        QApplication.instance().setStyleSheet(get_qss(theme))



def main():
    app = QApplication(sys.argv)
    from ui.theme import get_qss
   # app.setStyleSheet(get_qss("dark"))  # or state.theme
    win = MainWindow()
    app.setStyleSheet(get_qss(win.state.theme))
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()