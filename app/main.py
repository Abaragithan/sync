import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout

from core.inventory_manager import InventoryManager
from core.app_state import AppState
from ui.theme import APP_QSS

from views.welcome_page import WelcomePage
from views.lab_page import LabPage
from views.software_page import SoftwarePage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SYNC")
        self.setMinimumSize(1000, 700)

        self.inventory_manager = InventoryManager()
        self.state = AppState()

        self.stack = QStackedWidget()
        self.welcome = WelcomePage()
        self.lab = LabPage(self.inventory_manager, self.state)
        self.software = SoftwarePage(self.inventory_manager, self.state)

        self.stack.addWidget(self.welcome)   
        self.stack.addWidget(self.lab)       
        self.stack.addWidget(self.software)  

        self.welcome.go_deployment.connect(lambda: self.stack.setCurrentIndex(1))
        self.lab.next_to_software.connect(self._go_software)
        self.software.back_to_lab.connect(lambda: self.stack.setCurrentIndex(1))

        
        self.lab.edit_lab_requested.connect(self._go_lab_edit)

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
      

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_QSS)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
