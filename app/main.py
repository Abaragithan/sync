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
from views.operation_status_page import OperationStatusPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SYNC")
        self.setMinimumSize(1000, 700)

        self.inventory_manager = InventoryManager()
        self.state = AppState()
        self.state.load()

        self.stack = QStackedWidget()

        # Initialize pages ONCE
        self.welcome = WelcomePage()
        self.dashboard = DashboardPage(self.inventory_manager, self.state)
        self.lab = LabPage(self.inventory_manager, self.state)
        self.software = SoftwarePage(self.inventory_manager, self.state)
        self.lab_edit = LabEditPage(self.inventory_manager, self.state)
        self.status_page = OperationStatusPage(self.inventory_manager, self.state)

        # Stack order
        self.stack.addWidget(self.welcome)
        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.lab)
        self.stack.addWidget(self.software)
        self.stack.addWidget(self.lab_edit)
        self.stack.addWidget(self.status_page)

        # -------- Navigation --------

        self.welcome.go_deployment.connect(lambda: self.stack.setCurrentWidget(self.dashboard))

        self.dashboard.back_requested.connect(lambda: self.stack.setCurrentWidget(self.welcome))
        self.dashboard.lab_selected.connect(self._handle_lab_selection)
        self.dashboard.edit_lab_requested.connect(self._go_lab_edit)

        self.lab.back_requested.connect(lambda: self.stack.setCurrentWidget(self.dashboard))
        self.lab.next_to_software.connect(self._go_software)
        self.lab.edit_lab_requested.connect(self._go_lab_edit)

        self.software.back_to_lab.connect(lambda: self.stack.setCurrentWidget(self.lab))
        self.software.view_status_requested.connect(self._go_status_page)

        self.lab_edit.back_btn.clicked.connect(self._back_from_lab_edit)

        self.status_page.back_to_software.connect(
            lambda: self.stack.setCurrentWidget(self.software)
        )

        # Central widget
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.stack)
        self.setCentralWidget(w)

    # ---------------- Navigation ----------------

    def _go_software(self):
        self.software.on_page_show()
        self.stack.setCurrentWidget(self.software)

    def _go_lab_edit(self, lab_name: str):
        self.lab_edit.load_lab(lab_name)
        self.stack.setCurrentWidget(self.lab_edit)

    def _back_from_lab_edit(self):
        self.lab._render_lab()
        self.stack.setCurrentWidget(self.lab)

    def _handle_lab_selection(self, lab_name: str):
        self.lab._on_lab_changed(lab_name)
        self.stack.setCurrentWidget(self.lab)

    
    def _go_status_page(self):
        self.status_page.load_pcs()
        self.stack.setCurrentWidget(self.status_page)


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    app.setStyleSheet(get_qss(win.state.theme))
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()