import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout

from core.inventory_manager import InventoryManager
from core.app_state import AppState
from ui.theme import APP_QSS

from views.welcome_page import WelcomePage
from views.lab_page import LabPage
from views.software_page import SoftwarePage
from views.lab_edit_page import LabEditPage   # ✅ NEW (only addition)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SYNC")
        self.setMinimumSize(1000, 700)

        self.inventory_manager = InventoryManager()
        self.state = AppState()

        # -------- Stack --------
        self.stack = QStackedWidget()

        self.welcome = WelcomePage()
        self.lab = LabPage(self.inventory_manager, self.state)
        self.software = SoftwarePage(self.inventory_manager, self.state)

        # ✅ NEW: Lab Edit page
        self.lab_edit = LabEditPage(self.inventory_manager)

        # Order matters
        self.stack.addWidget(self.welcome)   # index 0
        self.stack.addWidget(self.lab)       # index 1
        self.stack.addWidget(self.software)  # index 2
        self.stack.addWidget(self.lab_edit)  # index 3

        # -------- Navigation --------
        self.welcome.go_deployment.connect(lambda: self.stack.setCurrentIndex(1))

        self.lab.next_to_software.connect(self._go_software)
        self.software.back_to_lab.connect(lambda: self.stack.setCurrentIndex(1))

        # ✏ Edit lab navigation (ONLY new wiring)
        self.lab.edit_lab_requested.connect(self._go_lab_edit)
        self.lab_edit.back_btn.clicked.connect(self._back_from_lab_edit)

        # -------- Central widget --------
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.stack)
        self.setCentralWidget(w)

    def _go_software(self):
        self.stack.setCurrentIndex(2)
        self.software.on_page_show()

    def _go_lab_edit(self, lab_name: str):
        print(f"[NAV] Edit lab requested: {lab_name}")
        self.lab_edit.load_lab(lab_name)
        self.stack.setCurrentIndex(3)

    def _back_from_lab_edit(self):
        # Force LabPage to refresh from inventory
        self.lab._render_lab()
        self.stack.setCurrentIndex(1)



def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_QSS)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
