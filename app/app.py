import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QTextStream

# Add app/ to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow
from core.config import INVENTORY_FILE  # Import to ensure data dir exists

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load dark theme from resources/
    resources_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
    styles_path = os.path.join(resources_dir, "styles.qss")
    if os.path.exists(styles_path):
        file = QFile(styles_path)
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)
        app.setStyleSheet(stream.readAll())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())